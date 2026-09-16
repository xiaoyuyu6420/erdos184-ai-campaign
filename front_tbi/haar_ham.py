#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cyclic Haar graph H(m;S) = B(m; {}, S, {}) Hamiltonicity harness.

Definition (Bonvicini-Pisanski-Zitnik 2510.23420):
  B(m;R,S,T): V = {u_0..u_{m-1}} ∪ {v_0..v_{m-1}},
    edges u_i-u_{i+j} (j∈R), v_i-v_{i+j} (j∈T), u_i-v_{i+j} (j∈S),
    R=-R, T=-T, 0∉R∪T, 0∈S.
  H(m;S) = B(m;{},S,{}).  Connected ⟺ gcd(m,S)=1 (with 0∈S).

This file:
  - builds H(m;S) two independent ways (for cross-validation),
  - Verifier V1: check a claimed Hamiltonian cycle given as vertex sequence,
  - Verifier V2: independent implementation (edge-set based),
  - Hamiltonian cycle SEARCH: 2-factor (union of 2 perfect matchings) + cycle
    splicing; heuristic => outputs are evidence, not proofs. All found cycles
    are checked by BOTH verifiers.
  - self-test anchors (Petersen non-Ham by brute force; Lemma-E instances).

Resource discipline: pure python, single thread, tiny memory.
"""
import sys, math, random
from collections import deque

# ----------------------------------------------------------------------------
# Graph construction
# ----------------------------------------------------------------------------
def haar_edges(m, S):
    """Independent construction #1: iterate over vertices, lookup spokes.
    Returns dict vertex -> sorted tuple of neighbors.
    Vertices: u_i = i, v_i = m + i   (i in Z_m)."""
    S = sorted(set(x % m for x in S))
    assert 0 in S
    adj = {i: [] for i in range(2 * m)}
    for i in range(m):                      # u_i = i
        for s in S:
            w = m + ((i + s) % m)           # v_{i+s}
            adj[i].append(w)
    for i in range(m):                      # v_i = m+i : edge u_j-v_i iff i-j ∈ S
        sset = set(S)
        for j in range(m):
            if (i - j) % m in sset:
                adj[m + i].append(j)
    for k in adj:
        adj[k] = tuple(sorted(adj[k]))
    return adj

def haar_edges_alt(m, S):
    """Independent construction #2: iterate over connection set, emit edges into a set."""
    S = sorted(set(x % m for x in S))
    E = set()
    for s in S:
        for i in range(m):
            a, b = i, m + ((i + s) % m)
            E.add((min(a, b), max(a, b)))
    adj = {i: [] for i in range(2 * m)}
    for (a, b) in E:
        adj[a].append(b)
        adj[b].append(a)
    for k in adj:
        adj[k] = tuple(sorted(adj[k]))
    return adj

def is_connected(adj):
    n = len(adj)
    seen = {0}
    dq = deque([0])
    while dq:
        x = dq.popleft()
        for y in adj[x]:
            if y not in seen:
                seen.add(y)
                dq.append(y)
    return len(seen) == n

# ----------------------------------------------------------------------------
# Verifiers (two independent implementations)
# ----------------------------------------------------------------------------
def verify_cycle_v1(adj, cyc):
    """cyc: list of vertices, claimed Hamiltonian cycle (cyc[0] adjacent to cyc[-1])."""
    n = len(adj)
    if len(cyc) != n:
        return False, "length %d != %d" % (len(cyc), n)
    if len(set(cyc)) != n:
        return False, "repeated vertex"
    s = set(adj and range(n))
    if set(cyc) != s:
        return False, "not the full vertex set"
    for k in range(n):
        a, b = cyc[k], cyc[(k + 1) % n]
        if b not in adj[a]:
            return False, "bad edge %d-%d at pos %d" % (a, b, k)
    return True, "OK"

def verify_cycle_v2(m, S, cyc):
    """Independent: rebuild edges by brute set, check degree-2 + connected + size."""
    n = 2 * m
    if len(cyc) != n or len(set(cyc)) != n:
        return False, "not a permutation of all vertices"
    idx = {x: k for k, x in enumerate(cyc)}
    E = set()
    Sset = set(x % m for x in S)
    for k in range(n):
        a, b = cyc[k], cyc[(k + 1) % n]
        E.add((min(a, b), max(a, b)))
    # check each edge is genuinely an edge of H by direct definition
    for (a, b) in E:
        ua, ub = (a < m), (b < m)
        if ua == ub:
            return False, "edge %d-%d not bipartite" % (a, b)
        u, v = (a, b) if ua else (b, a)
        if ((v - m) - u) % m not in Sset:
            return False, "edge %d-%d not a spoke of S" % (a, b)
    # degree 2 at every vertex
    deg = {x: 0 for x in range(n)}
    for (a, b) in E:
        deg[a] += 1
        deg[b] += 1
    if any(d != 2 for d in deg.values()):
        return False, "degree != 2 somewhere"
    # connected via one endpoint chase
    nxt = {}
    for (a, b) in E:
        nxt.setdefault(a, []).append(b)
        nxt.setdefault(b, []).append(a)
    start = cyc[0]
    prev, cur, cnt = -1, start, 1
    while True:
        a, b = nxt[cur]
        step = b if a == prev else a
        prev, cur = cur, step
        if cur == start:
            break
        cnt += 1
        if cnt > n:
            return False, "runaway"
    return (cnt == n), "cycle covers %d of %d" % (cnt, n)

# ----------------------------------------------------------------------------
# Hamiltonian cycle search (heuristic): 2-factor via 2 perfect matchings + splice
# ----------------------------------------------------------------------------
def perfect_matching(m, S, banned=None, rng=None, deadline=None, shuffle_pref=False):
    """Hopcroft-Karp-lite: greedy + augmenting paths. Bipartition: U=[0,m), V=[m,2m)."""
    import time
    t0 = time.time()
    S = sorted(set(x % m for x in S))
    matchV = {}   # v -> u
    matchU = {}   # u -> v
    if banned:
        bad = set(banned)
    else:
        bad = set()
    order = list(range(m))
    if rng:
        rng.shuffle(order)
    def adj_u(i):
        types = list(S)
        if shuffle_pref and rng is not None:
            rng.shuffle(types)
        for s in types:
            w = m + ((i + s) % m)
            if (min(i, w), max(i, w)) not in bad:
                yield w
    def try_assign(u, seen):
        # iterative DFS (Hopcroft-Karp style single-phase would be faster; this is fine)
        stack = [(u, iter(adj_u(u)))]
        path = []
        while stack:
            node, it = stack[-1]
            advanced = False
            for w in it:
                if w in seen:
                    continue
                seen.add(w)
                if w not in matchV:
                    # augment along path
                    matchV[w] = node
                    matchU[node] = w
                    for (pu, pw) in reversed(path):
                        matchV[pw] = pu
                        matchU[pu] = pw
                    return True
                else:
                    path.append((node, w))
                    stack.append((matchV[w], iter(adj_u(matchV[w]))))
                    advanced = True
                    break
            if not advanced:
                stack.pop()
                if path:
                    path.pop()
        return False
    for u in order:
        if u in matchU:
            continue
        try_assign(u, set())
        if deadline and time.time() - t0 > deadline:
            return None
    if len(matchU) != m:
        return None
    return matchU

def find_two_factor(m, S, rng, tries=8):
    """Union of two edge-disjoint perfect matchings = spanning 2-regular subgraph.
    Second matching uses shuffled spoke preferences for structural diversity."""
    for t in range(tries):
        M1 = perfect_matching(m, S, rng=rng, shuffle_pref=bool(t % 2))
        if M1 is None:
            continue
        banned = set((min(u, w), max(u, w)) for u, w in M1.items())
        M2 = perfect_matching(m, S, banned=banned, rng=rng, shuffle_pref=True)
        if M2 is None:
            continue
        # 2-factor as adjacency (each vertex degree 2)
        tf = {i: set() for i in range(2 * m)}
        ok = True
        for u, w in list(M1.items()) + list(M2.items()):
            a, b = min(u, w), max(u, w)
            if b in tf[a]:
                ok = False
                break
            tf[a].add(b)
            tf[b].add(a)
        if ok and all(len(tf[x]) == 2 for x in tf):
            return {x: tuple(sorted(y)) for x, y in tf.items()}
    return None

def cycles_of_2factor(tf):
    seen = set()
    cycs = []
    for start in tf:
        if start in seen:
            continue
        c = [start]
        seen.add(start)
        prev, cur = None, start
        while True:
            a, b = tf[cur]
            nxt = b if a == prev else a
            if nxt == start:
                break
            c.append(nxt)
            seen.add(nxt)
            prev, cur = cur, nxt
        cycs.append(c)
    return cycs

def splice(m, S, tf, rng, max_rounds=100000):
    """Merge cycles of the 2-factor using systematic 2-opt swaps through spokes.
    Returns a Hamiltonian cycle (list) or None if stuck."""
    aset = set(x % m for x in S)
    Slist = sorted(aset)
    def has_edge(a, b):
        if (a < m) == (b < m):
            return False
        if a > b:
            a, b = b, a
        return ((b - m) - a) % m in aset
    def spoke_partner(a, s):
        # vertex reached from a via a spoke of type s (a = u_i or v_j)
        if a < m:
            return m + ((a + s) % m)
        return (a - m - s) % m
    cycs = cycles_of_2factor(tf)
    pos = {}
    for ci, c in enumerate(cycs):
        for k, x in enumerate(c):
            pos[x] = (ci, k)
    while len(cycs) > 1:
        merged = False
        C1 = cycs[0]
        for a in C1:
            ca = pos[a][0]
            for s in Slist:
                w = spoke_partner(a, s)
                cw = pos[w][0]
                if cw == ca:
                    continue
                # remove 2-factor edges (a,a1) and (w,w1); add spokes (a,w),(a1,w1)
                for a1 in tf[a]:
                    for w1 in tf[w]:
                        if has_edge(a1, w1):
                            # build merged cycle:
                            # P1: C1 path from a1 ... to a (drop edge a-a1)
                            # P2: C2 path from w ... to w1 (drop edge w-w1)
                            # new cycle: a1 ->(P1)-> a -> w ->(P2)-> w1 -> a1
                            C2 = cycs[cw]
                            k1 = pos[a][1]; k2 = pos[w][1]
                            j1 = [k for k in (pos[a1][1],) ][0]
                            P1 = None
                            # rotate C1 to start at a1, ending at a
                            r1 = C1[j1:] + C1[:j1]
                            if r1[0] == a1 and r1[-1] == a:
                                P1 = r1
                            else:
                                r1 = [a1] + C1[j1+1:] + C1[:j1]  # fallback (should not trigger)
                                P1 = r1
                            r2 = C2[k2:] + C2[:k2]
                            if r2[0] == w and r2[-1] == w1:
                                P2 = r2
                            else:
                                r2 = [w] + C2[k2+1:] + C2[:k2]
                                P2 = r2
                            NC = P1 + P2
                            # replace cycs[0] and cycs[cw] by NC
                            cycs[0] = NC
                            del cycs[cw]
                            pos = {}
                            for ci, c in enumerate(cycs):
                                for k, x in enumerate(c):
                                    pos[x] = (ci, k)
                            merged = True
                            break
                    if merged: break
                if merged: break
            if merged: break
        if not merged:
            return None
    return cycs[0]

def search_ham(m, S, seed=1, time_budget=120.0):
    import time
    t0 = time.time()
    rng = random.Random(seed)
    attempt = 0
    while time.time() - t0 < time_budget:
        attempt += 1
        tf = find_two_factor(m, S, rng)
        if tf is None:
            continue
        cyc = splice(m, S, tf, rng)
        if cyc is not None:
            # rotate to canonical start (vertex 0) and orient
            k = cyc.index(0)
            cyc = cyc[k:] + cyc[:k]
            return cyc, attempt, time.time() - t0
    return None, attempt, time.time() - t0

# ----------------------------------------------------------------------------
# Brute force Hamiltonicity (tiny graphs only) -- ground truth for anchors
# ----------------------------------------------------------------------------
def brute_force_hamiltonian(m, S, limit=14):
    if 2 * m > limit:
        raise ValueError("too big for brute force")
    adj = haar_edges(m, S)
    n = 2 * m
    start = 0
    path = [start]
    used = {start}
    def dfs(cur):
        if len(path) == n:
            return start in adj[cur]
        # Warnsdorff ordering
        cand = [w for w in adj[cur] if w not in used]
        cand.sort(key=lambda w: sum(1 for z in adj[w] if z not in used))
        for w in cand:
            used.add(w)
            path.append(w)
            if dfs(w):
                return True
            path.pop()
            used.remove(w)
        return False
    return (path if dfs(start) else None)

# ----------------------------------------------------------------------------
# Self tests
# ----------------------------------------------------------------------------
def self_test():
    rng = random.Random(42)
    print("== SELF TEST ==")
    ok = True
    # T1: two constructions agree
    for (m, S) in [(5, [0, 1, 2]), (6, [0, 1, 3]), (7, [0, 2, 3, 6]), (12, [0, 3, 4, 8])]:
        A = haar_edges(m, S)
        B = haar_edges_alt(m, S)
        agree = all(sorted(A[x]) == sorted(B[x]) for x in A)
        print("  constructions agree on H(%d,%s): %s" % (m, S, agree))
        ok &= agree
    # T2: degrees = |S|, count edges = m*|S|
    m, S = 9, [0, 1, 4]
    A = haar_edges(m, S)
    deg_ok = all(len(A[x]) == len(set(S)) for x in A)
    print("  regular degree check H(9,%s): %s" % (S, deg_ok))
    ok &= deg_ok
    # T3: verifier accepts genuine cycle, rejects corrupted
    m, S = 7, [0, 1, 3]
    cyc = brute_force_hamiltonian(m, S)
    assert cyc is not None
    v1 = verify_cycle_v1(haar_edges(m, S), cyc)
    v2 = verify_cycle_v2(m, S, cyc)
    print("  verifier accept genuine: V1=%s V2=%s" % (v1[0], v2[0]))
    ok &= v1[0] and v2[0]
    bad = list(cyc)
    bad[2], bad[3] = bad[3], bad[2]
    v1b = verify_cycle_v1(haar_edges(m, S), bad)
    v2b = verify_cycle_v2(m, S, bad)
    print("  verifier rejects corrupted: V1=%s V2=%s" % (not v1b[0], not v2b[0]))
    ok &= (not v1b[0]) and (not v2b[0])
    # T4: Petersen graph B(5,{1,4},{0},{2,3}) is NOT Hamiltonian (Alspach); brute force agrees
    #     (brute force on the full bicirculant: reuse haar-style builder generalized inline)
    pet_adj = bicirculant_adj(5, [1, 4], [0], [2, 3])
    pf = brute_force_bicirc(pet_adj)
    print("  Petersen B(5,{±1},{0},{±2}) brute-force Hamiltonian: %s (expect False)" % (pf is not None))
    ok &= (pf is None)
    # T5: Lemma E instance: H(15,{0,5,6}) has unit difference 6 => Hamiltonian
    cyc = brute_force_hamiltonian(15, [0, 5, 6], limit=40)
    print("  H(15,{0,5,6}) brute-force Hamiltonian: %s (expect True)" % (cyc is not None))
    ok &= (cyc is not None)
    # T6: 2-spoke Lemma E cycle formula check: gcd(m, s-t)=1 => explicit cycle
    m, s, t = 21, 3, 7
    cycE = lemma_E_cycle(m, s, t)
    v1 = verify_cycle_v1(haar_edges(m, [0, s, t]), cycE) if cycE else (False, "none")
    print("  lemma_E_cycle(21, s=3, t=7): %s" % (v1,))
    ok &= v1[0]
    # T7: search pipeline on a mid-size easy instance
    cyc, att, dt = search_ham(120, [0, 1, 7, 30], seed=7, time_budget=20)
    if cyc:
        v1 = verify_cycle_v1(haar_edges(120, [0, 1, 7, 30]), cyc)
        v2 = verify_cycle_v2(120, [0, 1, 7, 30], cyc)
        print("  search H(120,{0,1,7,30}): found att=%d %.1fs V1=%s V2=%s" % (att, dt, v1[0], v2[0]))
        ok &= v1[0] and v2[0]
    else:
        print("  search H(120,{0,1,7,30}): NOT FOUND (unexpected)")
        ok = False
    print("== SELF TEST %s ==" % ("PASSED" if ok else "FAILED"))
    return ok

def bicirculant_adj(m, R, S, T):
    adj = {i: set() for i in range(2 * m)}
    Rs, Ts, Ss = set(x % m for x in R), set(x % m for x in T), set(x % m for x in S)
    for i in range(m):
        for r in Rs:
            j = (i + r) % m
            adj[i].add(j); adj[j].add(i)
        for t in Ts:
            j = m + ((i + t) % m)
            adj[m + i].add(j); adj[j].add(m + i)
        for s in Ss:
            j = m + ((i + s) % m)
            adj[i].add(j); adj[j].add(i)
    return {x: tuple(sorted(y)) for x, y in adj.items()}

def brute_force_bicirc(adj, limit=14):
    n = len(adj)
    if n > limit:
        raise ValueError("too big")
    start = 0
    path = [start]
    used = {start}
    def dfs(cur):
        if len(path) == n:
            return start in adj[cur]
        cand = [w for w in adj[cur] if w not in used]
        cand.sort(key=lambda w: sum(1 for z in adj[w] if z not in used))
        for w in cand:
            used.add(w); path.append(w)
            if dfs(w):
                return True
            path.pop(); used.remove(w)
        return False
    return path if dfs(start) else None

def lemma_E_cycle(m, s, t):
    """If gcd(m, s-t) = 1: cycle u_x, v_{x+s}, u_{x+(s-t)}, v_{x+(s-t)+s}, ...
    Spokes used: type s and type t. Vertices u_i = i, v_i = m+i."""
    if math.gcd(m, s - t) != 1:
        return None
    cyc = []
    x = 0
    for _ in range(m):
        cyc.append(x)          # u_x
        cyc.append(m + ((x + s) % m))  # v_{x+s}
        x = (x + s - t) % m
    return cyc

# ----------------------------------------------------------------------------
# Hard-instance analysis helpers
# ----------------------------------------------------------------------------
def is_hard(m, S):
    """The 'beyond-elementary-tools' predicate:
    0 in S, gcd(m,S)=1 (connected), |S|>=2,
    all pairwise differences non-coprime to m (blocks 2-spoke Lemma-E cycles)."""
    S = sorted(set(x % m for x in S))
    if 0 not in S or math.gcd(m, *S) != 1:
        return False
    n = len(S)
    for i in range(n):
        for j in range(i + 1, n):
            if math.gcd(m, S[i] - S[j]) == 1:
                return False
    return True

def sum_free_hard(m, S):
    """Additionally all pairwise sums non-coprime to m."""
    S = sorted(set(x % m for x in S))
    n = len(S)
    for i in range(n):
        for j in range(i, n):
            if math.gcd(m, S[i] + S[j]) == 1:
                return False
    return True

# ----------------------------------------------------------------------------
if __name__ == "__main__":
    sys.setrecursionlimit(100000)
    good = self_test()
    sys.exit(0 if good else 1)
