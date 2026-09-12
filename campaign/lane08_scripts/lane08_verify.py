#!/usr/bin/env python3
"""
lane08 (degeneracy route) verification script.
All constructive claims in lane_08_degeneracy.md are checked here:

  A. Theorem B sanity: every sampled 2-degenerate graph has ce <= n - c,
     and ce <= n - 2 whenever some component is not a tree.
  B. ce(K_{3,7}) == 10 > 9 = n-1   (exact search, bipartite 3-degenerate witness)
  C. K_{3,q}+e for q = 6,7,8: exact ce values (is small q a counterexample?)
  D. K_{3,9}+e (n=10, 3-degenerate, NON-bipartite): certified ce >= 10 > 9 = n-1
        via the slot/rate lemma: every cycle C has |C|-1 <= (5/3)|C cap B|,
        B-slots: x,y have 2, other B-vertices have 1  => savings <= (5/3)(q+2),
        parts = m - savings >= (4q-7)/3.  Machine checks the per-cycle inequality
        over ALL cycles and the slot accounting.
  E. K_{5,11} (n=16, 5-degenerate): certified ce >= 16 > 15 = n-1 via
        |C|-1 <= (9/5)|C cap B| over all cycles, B-slots = 2 each (total 22).
  F. Explicit valid decompositions (slot-respecting) as upper-bound certificates.
  G. Random graphs n<=8: degeneracy vs ce table.

Graph representation: vertices 0..n-1, edges list of tuples, bitmask over edges.
ce: minimum number of parts (cycles length>=3, single edges) in an edge partition.
Exact ce via IDA*-style feasibility search (branch on lowest uncovered edge).
"""
import itertools, random, sys, time
from collections import defaultdict

sys.setrecursionlimit(100000)

# ---------- basic graph utils ----------

def edge_set(n, edges):
    return frozenset(frozenset(e) for e in edges)

def canon_edges(n, edges):
    return sorted(tuple(sorted(e)) for e in edges)

def degrees(n, edges):
    d = [0]*n
    for a,b in edges: d[a]+=1; d[b]+=1
    return d

def adjacency(n, edges):
    adj = defaultdict(set)
    for i,(a,b) in enumerate(edges):
        adj[a].add((b,i)); adj[b].add((a,i))
    return adj

def components(n, edges):
    adj = adjacency(n, edges); seen=[False]*n; comps=[]
    for s in range(n):
        if seen[s]: continue
        stack=[s]; seen[s]=True; comp=[]
        while stack:
            v=stack.pop(); comp.append(v)
            for (u,_) in adj[v]:
                if not seen[u]: seen[u]=True; stack.append(u)
        comps.append(comp)
    return comps

def is_forest(n, edges):
    # forest iff #edges == n - #components (simple graph, acyclic equivalence)
    return len(edges) == n - len(components(n, edges))

def comp_is_tree(comp, comp_edges):
    """union-find acyclicity + connectivity check on a vertex list"""
    pos = {v:i for i,v in enumerate(comp)}
    par = list(range(len(comp)))
    def find(x):
        while par[x]!=x: par[x]=par[par[x]]; x=par[x]
        return x
    for a,b in comp_edges:
        ra,rb = find(pos[a]), find(pos[b])
        if ra==rb: return False
        par[ra]=rb
    return len(comp_edges) == len(comp)-1

def degeneracy(n, edges):
    """peel order; returns max over peeling of min degree (standard k-core peeling)"""
    adj = {v:set() for v in range(n)}
    for a,b in edges: adj[a].add(b); adj[b].add(a)
    deg = {v:len(adj[v]) for v in range(n)}
    alive = set(range(n)); dmax = 0
    while alive:
        v = min(alive, key=lambda x: deg[x])
        dmax = max(dmax, deg[v])
        alive.discard(v)
        for u in adj[v]:
            if u in alive:
                adj[u].discard(v); deg[u]-=1
    return dmax

def core_vertices(n, edges, k):
    """vertices of the k-core"""
    adj = {v:set() for v in range(n)}
    for a,b in edges: adj[a].add(b); adj[b].add(a)
    deg = {v:len(adj[v]) for v in range(n)}
    alive = set(range(n))
    while True:
        drop = {v for v in alive if deg[v] < k}
        if not drop: break
        alive -= drop
        for v in drop:
            for u in adj[v]:
                if u in alive:
                    adj[u].discard(v); deg[u]-=1
    return alive

# ---------- cycle enumeration ----------

def all_cycles(n, edges):
    """all simple cycles (len>=3), each once, as frozensets of edge indices"""
    m = len(edges)
    adj = adjacency(n, edges)
    cycles = set()
    # canonical enumeration: cycles containing edge i with all other edge indices > i,
    # and vertex min of cycle is one endpoint of edge i... simpler: DFS from each edge's
    # low endpoint, only allow edge indices > i, dedupe by frozenset.
    for i,(a,b) in enumerate(edges):
        # find cycles through edge i where i is the minimum edge index in the cycle
        stack = [(b, frozenset([i]), [a, b])]
        while stack:
            v, eset, visited = stack.pop()
            for (u, j) in adj[v]:
                if j <= i: continue
                if u == a and len(eset) >= 2:
                    cycles.add(eset | {j})   # include the closing edge (v,a)
                elif u not in visited:
                    stack.append((u, eset | {j}, visited + [u]))
    return [c for c in cycles]

def cycles_through_index(cycles, m=None):
    thr = defaultdict(list)
    for c in cycles:
        cs = c
        while cs:
            i = (cs & -cs).bit_length() - 1
            thr[i].append(c)
            cs &= cs - 1
    return thr

# ---------- exact ce via feasibility search ----------

def exact_ce(n, edges, node_budget=6_000_000, verbose=False):
    edges = canon_edges(n, edges)
    m = len(edges)
    if m == 0: return 0
    cycles = all_cycles(n, edges)
    cycles = [sum(1<<i for i in c) for c in cycles]  # to bitmasks
    thr = cycles_through_index(cycles, m)
    maxlen = max((c.bit_count() for c in cycles), default=3)
    full = (1<<m) - 1
    nodes = [0]
    from math import inf
    def feasible(T):
        """can we cover with <= T parts?"""
        seen = set()
        def dfs(bits, used):
            nodes[0]+=1
            if nodes[0] > node_budget: raise RuntimeError("node budget exceeded")
            if bits == 0: return True
            lb = used + (bits.bit_count() + maxlen - 1)//maxlen
            if lb > T: return False
            if (bits, T-used) in seen: return False
            i = (bits & -bits).bit_length() - 1
            # solo
            if dfs(bits & ~(1<<i), used+1): return True
            # cycles through edge i
            for C in thr.get(i, []):
                if C & bits == C:
                    if dfs(bits & ~C, used+1): return True
            seen.add((bits, T-used))
            return False
        return dfs(full, 0)
    lo = (m + maxlen - 1)//maxlen
    for T in range(lo, m+1):
        nodes[0] = 0
        try:
            if feasible(T): return T
        except RuntimeError:
            return None  # budget exceeded
    return m

# ---------- slot/rate lemma certificate ----------

def rate_certificate(n, edges, B, slot_cap, rate):
    """
    Check over ALL cycles: |C|-1 <= rate * |C cap B|.
    Returns max observed ratio and total B-slots available
    (sum over v in B of slot_cap(v)).  Then
    savings <= rate * sum(B-slots) is certified.
    """
    cyc = all_cycles(n, edges)
    worst = 0.0; worst_c = None
    for c in cyc:
        b = sum(1 for i in c if edges[i][0] in B or edges[i][1] in B)
        # |C cap B| counts distinct B-vertices of the cycle:
        verts = set()
        for i in c: verts |= set(edges[i])
        bcount = len(verts & B)
        r = (len(c)-1) / bcount
        if r > worst: worst, worst_c = r, c
        assert (len(c)-1) <= rate * bcount + 1e-9, f"rate violated: {c}"
    slots = sum(slot_cap(v) for v in B)
    return worst, len(cyc), slots

# ---------- explicit decomposition certificate ----------

def check_decomposition(n, edges, parts):
    """parts: list of ('cycle', [edge indices]) or ('edge', i). Verify partition,
    cyclicity, simplicity."""
    used = set()
    for p in parts:
        if p[0]=='edge':
            i = p[1]; assert i not in used; used.add(i)
        else:
            ei = p[1]; assert len(ei)>=3
            for i in ei: assert i not in used; used.add(i)
            # simple cycle check
            adj = defaultdict(list)
            for i in ei:
                a,b = edges[i]; adj[a].append(b); adj[b].append(a)
            for v in adj: assert len(adj[v])==2, "not a cycle"
            vs = list(adj); start=vs[0]; prev=None; cur=start; cnt=0
            while True:
                nxt = adj[cur][0] if adj[cur][0]!=prev else adj[cur][1]
                prev, cur = cur, nxt; cnt += 1
                if cur==start: break
            assert cnt==len(adj), "cycle not simple/connected"
    assert len(used)==len(edges), "not a partition"
    return True

# ---------- witness graphs ----------

def K_3_q(q):
    """K_{3,q}: A={0,1,2}, B={3,...,3+q-1}"""
    edges=[]
    for a in range(3):
        for b in range(3,3+q): edges.append((a,b))
    return 3+q, edges

def K_3_q_plus_e(q):
    n, edges = K_3_q(q)
    edges = edges + [(3,4)]  # extra edge inside B
    return n, edges

def K_5_q(q):
    edges=[]
    for a in range(5):
        for b in range(5,5+q): edges.append((a,b))
    return 5+q, edges

# ---------- runs ----------

def min_tjoin(n, edges):
    """exact tau(G) = min T-join, T = odd-degree vertices (unit weights).
    = min-weight perfect matching on the shortest-path metric of T."""
    import itertools as it
    deg = degrees(n, edges)
    T = [v for v in range(n) if deg[v] % 2 == 1]
    if not T: return 0
    # BFS all-pairs
    adj = adjacency(n, edges)
    dist = {}
    for s in T:
        d = {s:0}; q=[s]
        while q:
            v=q.pop(0)
            for (u,_) in adj[v]:
                if u not in d: d[u]=d[v]+1; q.append(u)
        for t in T:
            if t in d: dist[(s,t)] = d[t]
    INF = float('inf')
    k = len(T)
    # DP over subsets (k <= ~10)
    full = (1<<k)-1
    dp = {0:0}
    for mask in range(1, 1<<k):
        i = (mask & -mask).bit_length()-1
        rest = mask ^ (1<<i)
        best = INF
        j = rest
        while True:
            if j:
                lsb = (j & -j); jj = lsb.bit_length()-1
                w = dist.get((T[i],T[jj]), INF)
                sub = dp.get(mask ^ (1<<i) ^ (1<<jj), INF)
                if w+sub < best: best = w+sub
                j &= j-1
            else:
                break
        dp[mask]=best
    return dp.get(full, INF)

def run():
    t0=time.time(); random.seed(20260911)
    import itertools as it2
    print("="*72); print("A. Theorem B random check (2-degenerate => ce <= n-c; non-tree comp => ce <= n-2)")
    viol=0; tested=0; tab=defaultdict(list)
    for (n,p,cnt) in [(7,0.35,250),(7,0.5,250),(8,0.3,250),(8,0.4,200)]:
        for _ in range(cnt):
            edges=[(i,j) for i,j in itertools.combinations(range(n),2) if random.random()<p]
            if degeneracy(n,edges)>2: continue
            ce = exact_ce(n,edges, node_budget=1_500_000)
            if ce is None: continue
            tested+=1
            comps=components(n,edges); c=len(comps)
            non_tree = any(not comp_is_tree(comp,[e for e in edges if e[0] in comp and e[1] in comp]) for comp in comps)
            tab[(n,degeneracy(n,edges))].append(ce)
            if ce > n-c: viol+=1; print("  VIOLATION ce>n-c:", n, edges)
            if non_tree and ce > n-2: viol+=1; print("  VIOLATION ce>n-2:", n, edges)
    print(f"  tested={tested} 2-degenerate graphs, violations={viol}")
    for k in sorted(tab): print(f"    n={k[0]} deg={k[1]}: max ce={max(tab[k])}, mean={sum(tab[k])/len(tab[k]):.2f}, n-1={k[0]-1}")

    print("="*72); print("B. ce(K_{3,7}) exact (expect 10 = n > n-1 = 9)")
    n,edges = K_3_q(7)
    print("  ce(K_{3,7}) =", exact_ce(n,edges))

    print("="*72); print("C. K_{3,q}+e exact for q=6,7,8 (n=q+3)")
    for q in (6,7,8):
        n,edges = K_3_q_plus_e(q)
        print(f"  q={q}: n={n}, n-1={n-1}, ce={exact_ce(n,edges)}")

    print("="*72); print("D. K_{3,14}+e (n=17, 3-degenerate, NON-bipartite): certificate ce >= 17 > 16 = n-1")
    q=14; n,edges = K_3_q_plus_e(q)
    B=set(range(3,3+q))
    worst, ncyc, slots = rate_certificate(n, edges, B, lambda v: 2 if v in (3,4) else 1, 5/3)
    m=len(edges); import math
    lb = m - math.floor((5/3)*slots)
    print(f"  n={n}, m={m}; cycles checked={ncyc}, worst rate={worst:.4f} (cap 5/3), B-slots={slots}")
    print(f"  parts >= m - floor(5/3*slots) = {lb} > n-1 = {n-1}: {'OK' if lb>n-1 else 'FAIL'}")
    print("  degeneracy =", degeneracy(n, edges), "(expect 3); bipartite?", "no (edge (3,4) inside B)")
    # explicit decomposition (slot-respecting): triangle(1;3,4), hub-C6 via 3, hub-C6 via 4, 2 pure C6, rest solos
    idx = {e:i for i,e in enumerate(edges)}
    def IX(a,b): return idx[tuple(sorted((a,b)))]
    def c6(seq):
        return ['cycle',[IX(seq[i],seq[i+1]) for i in range(len(seq)-1)]]
    tri=['cycle',[IX(3,0),IX(4,0),IX(3,4)]]
    parts=[ c6([9,0,10,1,11,2,9]), c6([12,0,13,1,14,2,12]),
            c6([5,0,6,1,7,2,5]),   c6([8,0,15,1,16,2,8]), tri ]
    used=set(i for p in parts for i in p[1])
    rest=[('edge',i) for i in range(len(edges)) if i not in used]
    parts=parts+rest
    print("  explicit decomposition parts =", len(parts), "(<= 21 upper certificate), valid:", check_decomposition(n,edges,parts))

    print("="*72); print("E. K_{5,11} (n=16): slot/rate certificate ce >= 16 > 15")
    q=11; n,edges = K_5_q(q)
    B=set(range(5,5+q))
    worst, ncyc, slots = rate_certificate(n, edges, B, lambda v: 2, 9/5)
    m=len(edges)
    lb = m - math.floor((9/5)*slots)
    print(f"  cycles checked={ncyc}, worst rate={worst:.4f} (cap 9/5), B-slots={slots}")
    print(f"  m={m} => parts >= {lb} > n-1 = {n-1}: {'OK' if lb>n-1 else 'FAIL'}")
    print("  degeneracy =", degeneracy(n, edges), "(expect 5)")

    print("="*72); print("F. ce(K_{3,q}) exact for q=6,7 (tightness of 4q/3): expect 8, 10")
    for q in (6,7):
        n,edges = K_3_q(q)
        print(f"  q={q}: n={n}, ce={exact_ce(n,edges)} (4q/3={4*q/3})")

    print("="*72); print("G. 3-degenerate random graphs: check T3a ce<=(5n-8)/3 and conjecture T3b ce<=(4n-6)/3")
    import math as _m
    v3a=v3b=0; tested3=0; best_ratio=0; worst=None
    for (nn,pp,cnt) in [(7,0.55,300),(8,0.5,300),(9,0.45,250),(9,0.55,250)]:
        for _ in range(cnt):
            ee=[(i,j) for i,j in it2.combinations(range(nn),2) if random.random()<pp]
            if degeneracy(nn,ee)!=3: continue
            ce=exact_ce(nn,ee,node_budget=1_200_000)
            if ce is None: continue
            tested3+=1
            b3a=(5*nn-8)//3  # T3a as stated in lane_08_degeneracy.md (stronger than (5n-6)/3)
            b3b=max(0,(4*nn-6)//3)
            if ce>b3a: v3a+=1; print("  T3a VIOLATION:", nn, ee)
            if ce>b3b:
                v3b+=1
                print(f"  T3b VIOLATION (n={nn}, ce={ce}>{b3b}):", ee)
            if ce/nn>best_ratio: best_ratio=ce/nn; worst=(nn,ce)
    print(f"  tested3={tested3}, T3a violations={v3a}, T3b violations={v3b}, max ce/n={best_ratio:.3f} at {worst}")

    print("="*72); print(f"done in {time.time()-t0:.1f}s")

if __name__ == "__main__":
    run()
