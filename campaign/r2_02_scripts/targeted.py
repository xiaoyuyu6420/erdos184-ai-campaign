#!/usr/bin/env python3
"""
targeted.py — R2-02 targeted computations.

1. Independent (Python, different algorithm structure) exact ce implementation;
   cross-validate against the C solver cecli on random 3-degenerate graphs.
2. K_{3,q}: exact ce and tau for q = 2..9  -> Theorem A numeric certificates
   (tau(K_{3,q}) = q; m + 2tau = 5q vs 4n-6).
3. Split graphs K_3 v I_k: exact ce  -> extremal family for psi(n)=floor((4n-7)/3).
4. Wheel family C_L + hub, and the core wheel (C6 + evens-triangle + hub):
   witnesses that deg-3 k=0 interior peels can have Delta = 3.
5. 3-trees (stacked) up to n=12: max ce.
6. phi / psi / beta tables.
"""
import itertools, random, subprocess, sys, functools
from fractions import Fraction

CECLI = "./cecli"

# ---------- exact ce: independent implementation (iterative, dict memo,
# cycle enumeration by simple paths; different code path from scan.c) ----------
def graph_edges(n, adj):
    return [(u, v) for u in range(n) for v in range(u + 1, n) if (adj[u] >> v) & 1]

def ce_exact(n, adj):
    """min pieces partition of E into simple cycles + single edges (exact)."""
    edges = graph_edges(n, adj)
    m = len(edges)
    if m == 0:
        return 0
    eidx = {}
    for i, (u, v) in enumerate(edges):
        eidx[(u, v)] = eidx[(v, u)] = i
    nbr = {v: [x for x in range(n) if (adj[v] >> x) & 1] for v in range(n)}

    def cycles_through(e, mask):
        u, v = edges[e]
        out = []
        stack = [(v, 1 << v, 0)]
        while stack:
            cur, visited, pmask = stack.pop()
            for x in nbr[cur]:
                ei = eidx[(cur, x)]
                if not (mask >> ei) & 1:
                    continue
                if x == u:
                    out.append(pmask | (1 << ei) | (1 << e))
                elif not (visited >> x) & 1:
                    stack.append((x, visited | (1 << x), pmask | (1 << ei)))
        return out

    memo = {0: 0}

    def solve(mask):
        if mask in memo:
            return memo[mask]
        e = (mask & -mask).bit_length() - 1
        best = 1 + solve(mask & ~(1 << e))
        for c in cycles_through(e, mask):
            val = 1 + solve(mask & ~c)
            if val < best:
                best = val
        memo[mask] = best
        return best

    return solve((1 << m) - 1)

def tau_exact(n, adj):
    """min T-join via metric closure + exact matching DP."""
    import heapq
    d = [[10**6] * n for _ in range(n)]
    for i in range(n):
        d[i][i] = 0
    for u in range(n):
        for v in range(n):
            if (adj[u] >> v) & 1:
                d[u][v] = 1
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if d[i][k] + d[k][j] < d[i][j]:
                    d[i][j] = d[i][k] + d[k][j]
    T = [v for v in range(n) if bin(adj[v]).count("1") % 2 == 1]
    t = len(T)
    if t == 0:
        return 0
    full = (1 << t) - 1
    dp = [10**6] * (full + 1)
    dp[0] = 0
    for S in range(1, full + 1):
        i = (S & -S).bit_length() - 1
        best = 10**6
        for j in range(t):
            if j == i or not (S >> j) & 1:
                continue
            v = d[T[i]][T[j]] + dp[S ^ (1 << i) ^ (1 << j)]
            best = min(best, v)
        dp[S] = best
    return dp[full]

def cecli_call(n, adj):
    edges = graph_edges(n, adj)
    inp = f"{n} {len(edges)}\n" + "\n".join(f"{u} {v}" for u, v in edges)
    out = subprocess.run([CECLI], input=inp, capture_output=True, text=True).stdout
    kv = dict(p.split("=") for p in out.split())
    return int(kv["ce"]), int(kv["tau"]), int(kv["degen"])

# ---------- builders ----------
def K33_like(a, b):  # K_{a,b}
    n = a + b
    adj = [0] * n
    for i in range(a):
        for j in range(a, a + b):
            adj[i] |= 1 << j
            adj[j] |= 1 << i
    return n, adj

def split_graph(k):  # K_3 v I_k ; A = {0,1,2}, B = 3..k+2
    n = 3 + k
    adj = [0] * n
    for i in range(3):
        for j in range(3):
            if i != j:
                adj[i] |= 1 << j
    for b in range(3, n):
        for a in range(3):
            adj[b] |= 1 << a
            adj[a] |= 1 << b
    return n, adj

def wheel(L, hubset):  # cycle C_L on 0..L-1 + ONE hub at vertex L adjacent to hubset
    n = L + 1
    adj = [0] * n
    for i in range(L):
        j = (i + 1) % L
        adj[i] |= 1 << j
        adj[j] |= 1 << i
    for h in hubset:
        adj[L] |= 1 << h
        adj[h] |= 1 << L
    return n, adj

def core_wheel6():
    """C6 (0..5) + hub 6 adjacent to 1,3,5 + triangle 2-4-6 among evens... as
    designed: hub v adjacent to {1,3,5}; triangle {2,4,6}: edges 24,46,62."""
    n = 7
    adj = [0] * n
    for i in range(6):
        j = (i + 1) % 6
        adj[i] |= 1 << j
        adj[j] |= 1 << i
    for h in (1, 3, 5):
        adj[6] |= 1 << h
        adj[h] |= 1 << 6
    for a, b in ((2, 4), (4, 6), (6, 2)):
        adj[a] |= 1 << b
        adj[b] |= 1 << a
    return n, adj

def degeneracy_of(n, adj):
    a = list(adj)
    alive = [True] * n
    k = 0
    rem = n
    while rem:
        found = -1
        for v in range(n):
            if alive[v] and bin(a[v]).count("1") <= k:
                found = v
                break
        if found < 0:
            k += 1
            continue
        alive[found] = False
        rem -= 1
        for u in range(n):
            if alive[u] and (a[found] >> u) & 1:
                a[u] &= ~(1 << found)
                a[found] &= ~(1 << u)
    return k

def is_pure_core(n, adj):
    if min(bin(adj[v]).count("1") for v in range(n)) < 3:
        return False
    for v in range(n):
        if bin(adj[v]).count("1") != 3:
            continue
        nb = [x for x in range(n) if (adj[v] >> x) & 1]
        if (adj[nb[0]] >> nb[1]) & 1 or (adj[nb[0]] >> nb[2]) & 1 or (adj[nb[1]] >> nb[2]) & 1:
            return False
    return True

# ---------- 1. cross-validation ----------
def cross_validate(trials=300, seed=20260912):
    rng = random.Random(seed)
    bad = 0
    for t in range(trials):
        # random 3-degenerate graph: reverse peel construction
        n = rng.randint(3, 9)
        adj = [0] * n
        order = list(range(n))
        rng.shuffle(order)
        placed = []
        for v in order:
            pool = placed[:]
            rng.shuffle(pool)
            S = pool[: rng.randint(0, min(3, len(pool)))]
            for u in S:
                adj[v] |= 1 << u
                adj[u] |= 1 << v
            placed.append(v)
        if degeneracy_of(n, adj) > 3:
            continue
        cp, tp, dp = cecli_call(n, adj)
        cm = ce_exact(n, adj)
        tm = tau_exact(n, adj)
        if (cp, tp) != (cm, tm):
            bad += 1
            print(f"  MISMATCH n={n} adj={adj}: C=({cp},{tp}) py=({cm},{tm})")
    print(f"[1] cross-validation: {trials} random 3-degenerate graphs, {bad} mismatches")
    return bad

# ---------- 2. K_{3,q} ----------
def table_k3q(qmax=9):
    print("[2] K_{3,q}: exact ce, tau;  m+2tau vs 4n-6 and 4n-4")
    print(f"{'q':>3} {'n':>3} {'m':>3} {'ce':>3} {'ceil(4q/3)':>10} {'tau':>4} {'m+2tau':>7} {'4n-6':>5} {'viol?':>6}")
    for q in range(2, qmax + 1):
        n, adj = K33_like(3, q)
        m = 3 * q
        ce, tau, dg = cecli_call(n, adj)
        assert dg <= 3, (q, dg)
        assert ce == ce_exact(n, adj)
        viol = m + 2 * tau - (4 * n - 6)
        print(f"{q:>3} {n:>3} {m:>3} {ce:>3} {-(-4*q//3):>10} {tau:>4} {m+2*tau:>7} {4*n-6:>5} {'+'+str(viol) if viol>0 else 'no':>6}")

# ---------- 3. split graphs ----------
def table_split(kmax=9):
    print("[3] split graphs K_3 v I_k: n = k+3, m = 3k+3")
    print(f"{'k':>3} {'n':>3} {'m':>3} {'ce':>3} {'psi(n)':>7} {'phi(n)':>7} {'degen':>5} {'pure?':>5}")
    for k in range(1, kmax + 1):
        n, adj = split_graph(k)
        m = 3 * k + 3
        ce, tau, dg = cecli_call(n, adj)
        psi = (4 * n - 7) // 3
        print(f"{k:>3} {n:>3} {m:>3} {ce:>3} {psi:>7} {(4*n-6)//3:>7} {dg:>5} {str(is_pure_core(n,adj)):>5}")

# ---------- 4. wheel witnesses ----------
def wheel_checks():
    print("[4] wheel witnesses: deg-3 k=0 interior peel with Delta=3")
    for L in (6, 7, 8):
        n, adj = wheel(L, (1, 3, 5))  # 1,3,5 pairwise non-adjacent on C_L (L>=6)
        ce, tau, dg = cecli_call(n, adj)
        # G - hub
        adj2 = [a & ~((1 << (n - 1))) for a in adj[: n - 1]]
        adj2[n - 2] = 0
        ce2, _, _ = cecli_call(n - 1, adj2)
        print(f"  C{L}+hub: n={n} ce={ce} ce(C{L})={ce2} Delta={ce-ce2}  (beta({n})={((4*n-6)//3)-((4*(n-1)-6)//3)})")
    n, adj = core_wheel6()
    ce, tau, dg = cecli_call(n, adj)
    adj2 = [a & ~(1 << 6) for a in adj[:6]]
    ce2, _, _ = cecli_call(6, adj2)
    print(f"  core-wheel(C6+evens-tri+hub): n={n} ce={ce} ce(G-hub)={ce2} Delta={ce-ce2} pure={is_pure_core(n,adj)} degen={dg}")

# ---------- 5. 3-trees ----------
def all_3trees(maxn=12):
    """generate unlabeled 3-trees by stacking; canonicalize via brute perm for n<=10,
    skip isomorphism at 11,12 (upper bound set anyway)."""
    def canon_key(n, adj):
        best = None
        for perm in itertools.permutations(range(n)):
            rows = []
            pos = [0] * n
            for i, p in enumerate(perm):
                pos[p] = i
            for i in range(n):
                r = 0
                for x in range(n):
                    if (adj[perm[i]] >> x) & 1:
                        r |= 1 << pos[x]
                rows.append(r)
            key = tuple(rows)
            if best is None or key < best:
                best = key
        return best
    levels = {4: [tuple([(0b1110, 0b1101, 0b1011, 0b0111)])]}
    # represent graph as tuple of adjacency masks
    start = (0b1110, 0b1101, 0b1011, 0b0111)
    levels = {4: {start}}
    results = {}
    for n in range(4, maxn + 1):
        cur = set()
        if n == 4:
            cur = {start}
        else:
            for g in levels[n - 1]:
                pn = n - 1
                # faces = triangles
                tris = [(a, b, c) for a in range(pn) for b in range(a + 1, pn) for c in range(b + 1, pn)
                        if (g[a] >> b) & 1 and (g[a] >> c) & 1 and (g[b] >> c) & 1]
                for (a, b, c) in tris:
                    adj = list(g) + [0]
                    for u in (a, b, c):
                        adj[u] |= 1 << pn
                        adj[pn] |= 1 << u
                    key = canon_key(n, tuple(adj)) if n <= 10 else tuple(adj)
                    cur.add(key)
        # canonical keys are already canonical forms (rows) -> rebuild adj from key
        levels[n] = cur
        best_ce = 0
        cnt = len(cur)
        for key in cur:
            if n <= 10:
                adj = [0] * n
                for i in range(n):
                    for j in range(n):
                        if (key[i] >> j) & 1:
                            adj[i] |= 1 << j
            else:
                adj = list(key)
            ce, _, _ = cecli_call(n, adj)
            if ce > best_ce:
                best_ce = ce
        results[n] = (cnt, best_ce)
        print(f"[5] 3-trees n={n}: count={cnt} max_ce={best_ce} psi={(4*n-7)//3} phi={(4*n-6)//3} n-1={n-1}")
    return results

# ---------- 6. tables ----------
def tables():
    print("[6] n: phi=floor((4n-6)/3), psi=floor((4n-7)/3), beta=phi(n)-phi(n-1)")
    for n in range(1, 16):
        phi = (4 * n - 6) // 3 if n >= 3 else (0 if n <= 1 else 1)
        psi = (4 * n - 7) // 3
        print(f"  n={n:>2} phi={phi:>3} psi={psi:>3} beta={phi-((4*(n-1)-6)//3 if n-1>=3 else (0 if n-1<=1 else 1)):>2}")

# ---------- 7. R2-02 session additions ----------
def split_graph_k(k):  # alias with explicit k (K_3 v I_k)
    return split_graph(k)

def witness_p4_dissolve():
    """G = (K5 - xy) + z(p,q,r) + v(x,y,z): 3-degenerate, N(v) independent,
    ALL THREE pair-dissolves G - v + pair have degeneracy 4 (P4 fails)."""
    # vertices: x=0 y=1 p=2 q=3 r=4 z=5 v=6 ; K5-xy on {0,1,2,3,4}; 5~{2,3,4}; 6~{0,1,5}
    edges = []
    V5 = [0, 1, 2, 3, 4]
    for i in range(5):
        for j in range(i + 1, 5):
            if {i, j} == {0, 1}:
                continue
            edges.append((i, j))
    edges += [(5, 2), (5, 3), (5, 4)]
    edges += [(6, 0), (6, 1), (6, 5)]
    n = 7
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    dg = degeneracy_of(n, adj)
    ce, tau, _ = cecli_call(n, adj)
    print(f"[7] P4-dissolve witness: n=7 m={len(edges)} degen={dg} (want 3), ce={ce} (phi(7)=7)")
    nb_v = [x for x in range(n) if (adj[6] >> x) & 1]
    assert nb_v == [0, 1, 5] and not ((adj[0] >> 1) & 1) and not ((adj[0] >> 5) & 1) and not ((adj[1] >> 5) & 1), "N(v) not independent"
    for (a, b) in ((0, 1), (0, 5), (1, 5)):
        adj2 = list(adj)
        adj2[6] = 0
        for x in range(6):
            adj2[x] &= ~(1 << 6)
        adj2[a] |= 1 << b
        adj2[b] |= 1 << a
        dg2 = degeneracy_of(n, adj2)  # note: v still counted, isolated; check induced on 0..5
        dg2 = degeneracy_of(6, adj2[:6])
        print(f"     dissolve pair ({a},{b}): degen(G-v+pair) = {dg2} (want 4)")
    return dg == 3

def witness_k5e_v():
    """G = K5-e + v joined to the two non-adjacent vertices x,y and one more z:
    the naive 'deg-3 dissolve keeps 3-degeneracy' fails here too via pair (x,y)."""
    edges = []
    for i in range(5):
        for j in range(i + 1, 5):
            if {i, j} == {0, 1}:
                continue
            edges.append((i, j))
    edges += [(5, 0), (5, 1), (5, 2)]  # v=5, z=2
    n = 6
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    ce, tau, dg = cecli_call(n, adj)
    adj2 = list(adj)
    adj2[5] = 0
    for x in range(5):
        adj2[x] &= ~(1 << 5)
    adj2[0] |= 1 << 1
    adj2[1] |= 1 << 0
    dg2 = degeneracy_of(5, adj2)
    print(f"[7b] K5-e + v(x,y,z): n=6 degen={dg} (want 3) ce={ce} phi(6)=6 ; dissolve xy: degen={dg2} (want 4)")

def split_table(kmax=8):
    print("[8] split graphs K_3 v I_k: n=k+3, m=3k+3; formula ce = k + ceil(k/3) + 1; tau = k")
    import math
    ok = True
    for k in range(1, kmax + 1):
        n, adj = split_graph_k(k)
        m = 3 * k + 3
        ce, tau, dg = cecli_call(n, adj)
        pred = k + math.ceil(k / 3) + 1
        phi = (4 * n - 6) // 3
        ok &= (ce == pred) and (tau == k) and (dg == 3)
        print(f"  k={k} n={n} m={m}: ce={ce} pred={pred} tau={tau} degen={dg} phi(n)={phi} tight={'YES' if ce==phi else 'phi-1'}")
    print(f"  ALL MATCH formula: {ok}")

def gpfail_witness_ce():
    print("[9] GPFAIL witnesses from scan_wit.txt: exact ce vs phi(n)")
    cases = [
        (7, [(0,3),(0,4),(0,5),(0,6),(1,3),(1,4),(1,5),(2,4),(2,5),(2,6),(3,6)]),
        (8, [(0,3),(0,4),(0,5),(1,4),(1,5),(1,6),(2,5),(2,6),(2,7),(3,6),(3,7),(4,7)]),
    ]
    for n, edges in cases:
        adj = [0] * n
        for u, v in edges:
            adj[u] |= 1 << v
            adj[v] |= 1 << u
        ce, tau, dg = cecli_call(n, adj)
        phi = (4 * n - 6) // 3
        print(f"  n={n} m={len(edges)}: ce={ce} phi={phi} slack={phi-ce} degen={dg} pure={is_pure_core(n,adj)}")

def random_dissolve_scan(trials=3000, seed=7):
    """how often does a 3-degenerate G with independent-N deg-3 vertex have ALL pair-dissolves 4-degenerate?"""
    import random as _r
    rng = _r.Random(seed)
    bad = 0
    for _ in range(trials):
        n = rng.randint(5, 9)
        adj = [0] * n
        order = list(range(n))
        rng.shuffle(order)
        placed = []
        for v in order:
            pool = placed[:]
            rng.shuffle(pool)
            S = pool[: rng.randint(0, min(3, len(pool)))]
            for u in S:
                adj[v] |= 1 << u
                adj[u] |= 1 << v
        if degeneracy_of(n, adj) > 3:
            continue
        for v in range(n):
            nb = [x for x in range(n) if (adj[v] >> x) & 1]
            if len(nb) != 3:
                continue
            if (adj[nb[0]] >> nb[1]) & 1 or (adj[nb[0]] >> nb[2]) & 1 or (adj[nb[1]] >> nb[2]) & 1:
                continue  # not independent
            alldis = True
            for i in range(3):
                a, b = nb[i], nb[(i + 1) % 3]
                adj2 = [adj[x] & ~(1 << v) for x in range(n)]
                adj2[v] = 0
                adj2[a] |= 1 << b
                adj2[b] |= 1 << a
                if degeneracy_of(n, adj2) <= 3:
                    alldis = False
                    break
            if alldis:
                bad += 1
    print(f"[10] random 3-degenerate graphs with a deg-3 independent-N vertex whose ALL pair-dissolves break 3-degeneracy: {bad}/{trials}")

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "cv"):
        cross_validate()
    if which in ("all", "k3q"):
        table_k3q()
    if which in ("all", "split"):
        table_split()
    if which in ("all", "wheel"):
        wheel_checks()
    if which in ("all", "trees"):
        all_3trees(9)
    if which in ("all", "tables"):
        tables()
    if which in ("all", "r2"):
        witness_p4_dissolve()
        witness_k5e_v()
        split_table()
        gpfail_witness_ce()
        random_dissolve_scan()
