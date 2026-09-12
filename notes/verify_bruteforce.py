import itertools

def edge_masks(n):
    edges = list(itertools.combinations(range(n), 2))
    return edges, {e: 1 << i for i, e in enumerate(edges)}

def connected_set(S, adjm):
    S = list(S)
    seen = {S[0]}; stack=[S[0]]
    while stack:
        v = stack.pop()
        for w in S:
            if w not in seen and (adjm[v]>>w)&1:
                seen.add(w); stack.append(w)
    return len(seen)==len(S)

def partitions(lst, k):
    if len(lst) == k:
        yield [(x,) for x in lst]
        return
    if k == 1:
        if lst: yield [tuple(lst)]
        return
    if len(lst) < k: return
    first, rest = lst[0], lst[1:]
    for p in partitions(rest, k-1):
        yield [(first,)] + p
    for p in partitions(rest, k):
        yield [ (first,) + p[0] ] + p[1:]
        for i in range(1, len(p)):
            yield p[:i] + [ (first,) + p[i] ] + p[i+1:]

def all_simple_cycles_full(n, adjm, emap):
    seen = set()
    for r in range(3, n+1):
        for W in itertools.combinations(range(n), r):
            for perm in itertools.permutations(W):
                if perm[0] != min(perm): continue
                if perm[1] > perm[-1]: continue
                k = len(perm)
                if all((adjm[perm[i]]>>perm[(i+1)%k])&1 for i in range(k)):
                    mask = 0
                    for i in range(k):
                        u, v = perm[i], perm[(i+1)%k]
                        mask |= emap[tuple(sorted((u,v)))]
                    seen.add(mask)
    return sorted(seen)

def has_K5_minor(n, adjm):
    if n < 5: return False
    for r in range(5, n+1):
        for S in itertools.combinations(range(n), r):
            S = list(S)
            if sum(1 for v in S if sum(((adjm[v]>>w)&1) for w in S) >= 4) < 5: continue
            for part in partitions(S, 5):
                if all(connected_set(b, adjm) for b in part) and \
                   all(any((adjm[u]>>v)&1 for u in part[i] for v in part[j])
                       for i, j in itertools.combinations(range(5), 2)):
                    return True
    return False

def has_K33_minor(n, adjm):
    if n < 6: return False
    for S in itertools.combinations(range(n), 6):
        vs = list(S)
        for L in itertools.combinations(vs, 3):
            R = [v for v in vs if v not in L]
            if all((adjm[u]>>v)&1 for u in L for v in R): return True
    return False

def is_planar(n, adjm):
    if n < 5: return True
    return not has_K5_minor(n, adjm) and not has_K33_minor(n, adjm)

def has_K4_minor(n, adjm):
    if n < 4: return False
    for r in range(4, n+1):
        for S in itertools.combinations(range(n), r):
            if sum(sum(((adjm[v]>>w)&1) for w in S) for v in S)//2 < 6: continue
            for part in partitions(list(S), 4):
                if all(connected_set(b, adjm) for b in part) and \
                   all(any((adjm[u]>>v)&1 for u in part[i] for v in part[j])
                       for i, j in itertools.combinations(range(4), 2)):
                    return True
    return False

def has_K23_minor(n, adjm):
    if n < 5: return False
    for r in range(5, n+1):
        for S in itertools.combinations(range(n), r):
            for part in partitions(list(S), 5):
                if not all(connected_set(b, adjm) for b in part): continue
                for two in itertools.combinations(range(5), 2):
                    L = [part[i] for i in two]
                    R = [part[i] for i in range(5) if i not in two]
                    if all(any((adjm[u]>>v)&1 for u in l for v in r) for l in L for r in R):
                        return True
    return False

def is_outerplanar(n, adjm):
    return not has_K4_minor(n, adjm) and not has_K23_minor(n, adjm)

def f_ce(n, adjm, emap, allE, cycles):
    cyc_by_edge = {}
    for c in cycles:
        m = c
        while m:
            b = m & -m
            cyc_by_edge.setdefault(b, []).append(c)
            m ^= b
    memo = {0:0}
    def rec(S):
        if S in memo: return memo[S]
        low = S & -S
        best = 1 + rec(S ^ low)
        for c in cyc_by_edge.get(low, []):
            if c & S == c:
                r = 1 + rec(S ^ c)
                if r < best: best = r
        memo[S] = best
        return best
    return rec(allE)

# ---------- unit tests ----------
if __name__ == '__main__':
    edges, emap = edge_masks(4)
    adjm=[0]*4
    for u,v in edges: adjm[u]|=1<<v; adjm[v]|=1<<u
    cyc = all_simple_cycles_full(4, adjm, emap)
    assert len(cyc) == 7, f"K4 cycles {len(cyc)} != 7"
    assert f_ce(4, adjm, emap, 63, cyc) == 3, "K4 f_ce != 3"
    # octahedron = K_{2,2,2} on 6 vertices
    edges6, emap6 = edge_masks(6)
    adj6=[0]*6
    parts=[[0,3],[1,4],[2,5]]
    octE=set()
    for i in range(3):
        for j in range(3):
            if i!=j:
                for a in parts[i]:
                    for b in parts[j]:
                        octE.add(tuple(sorted((a,b))))
    for u,v in octE: adj6[u]|=1<<v; adj6[v]|=1<<u
    assert len(octE)==12
    assert is_planar(6, adj6), "octahedron should be planar"
    oct_cyc = all_simple_cycles_full(6, adj6, emap6)
    f_oct = f_ce(6, adj6, emap6, sum(emap6[e] for e in octE), oct_cyc)
    print("octahedron f_ce =", f_oct, "(expect 2)")
    # triangles of octahedron: partition into 4 edge-disjoint triangles?
    tris = [c for c in oct_cyc if bin(c).count('1')==3]
    found = None
    for combo in itertools.combinations(tris, 4):
        m = 0
        for c in combo: 
            if m & c: break
            m |= c
        else:
            if m == sum(emap6[e] for e in octE): found = combo; break
    print("octahedron: 4 edge-disjoint triangles covering all edges:", "YES" if found else "NO")
    # K23 is not outerplanar, K4 is not outerplanar, C4+chord is outerplanar
    adj=[0]*5
    for u,v in [(0,3),(0,4),(1,3),(1,4),(2,3),(2,4)]: adj[u]|=1<<v; adj[v]|=1<<u
    assert not is_outerplanar(5, adj), "K23 should not be outerplanar"
    adj=[0]*4
    for u,v in [(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]: adj[u]|=1<<v; adj[v]|=1<<u
    assert not is_outerplanar(4, adj), "K4 should not be outerplanar"
    adj=[0]*4
    for u,v in [(0,1),(1,2),(2,3),(3,0),(0,2)]: adj[u]|=1<<v; adj[v]|=1<<u
    assert is_outerplanar(4, adj), "C4+chord should be outerplanar"
    print("unit tests OK")

def run(nmax):
    for n in range(3, nmax+1):
        edges, emap = edge_masks(n)
        st = dict(planar=0, fmax=0, P_viol=[], Q_viol=[], B_viol=[],
                  euler_maxplanar={}, max_planar_f={},
                  out2c_noncycle_max=(0,None))
        for edges_mask in range(1 << len(edges)):
            adjm=[0]*n; e=0
            m = edges_mask
            while m:
                b=m&-m; i=b.bit_length()-1
                u,v=edges[i]; adjm[u]|=1<<v; adjm[v]|=1<<u
                e+=1; m^=b
            if e > 3*n-6: continue
            if not is_planar(n, adjm): continue
            st['planar'] += 1
            cyc = all_simple_cycles_full(n, adjm, emap)
            f = f_ce(n, adjm, emap, edges_mask, cyc)
            has_cycle = bool(cyc)
            if f > st['fmax']: st['fmax'] = f
            if f > n-1: st['P_viol'].append((edges_mask,e,f))
            if has_cycle and f > n-2: st['Q_viol'].append((edges_mask,e,f))
            degs = [bin(adjm[v]).count('1') for v in range(n)]
            euler = all(d%2==0 for d in degs)
            if euler and has_cycle and f > n-2:
                st['B_viol'].append((edges_mask,e,f))
            if euler and e == 3*n-6:
                st['euler_maxplanar'][f] = st['euler_maxplanar'].get(f,0)+1
            if e == 3*n-6:
                st['max_planar_f'][f] = st['max_planar_f'].get(f,0)+1
            if is_outerplanar(n, adjm):
                two_c = all(bin(adjm[v]).count('1') >= 2 for v in range(n))
                if two_c and has_cycle and e > n and f > st['out2c_noncycle_max'][0]:
                    st['out2c_noncycle_max'] = (f, (e,))
        print(f"n={n}: planar={st['planar']} max_f_ce={st['fmax']} "
              f"P_viol={len(st['P_viol'])} Q_viol={len(st['Q_viol'])} B_viol={len(st['B_viol'])}")
        print(f"   eulerian maximal planar f_ce histogram: {st['euler_maxplanar']}  (n-2={n-2})")
        print(f"   all maximal planar f_ce histogram: {st['max_planar_f']}")
        print(f"   2-conn outerplanar non-cycle max f_ce: {st['out2c_noncycle_max']} (bound n-2={n-2})")
        if st['B_viol']:
            print("   !!! Theorem B counterexample candidates:", st['B_viol'][:5])
run(6)
