"""Lane 11 graph tools: tau (min T-join), ce (exact decomposition), ledgers.
Unit weights, simple graphs. Anchors: K_{3,3} tau=3 ce=4; K4 tau=2 ce=2; star K_{1,k}: tau=ce=k.
"""
import itertools
from collections import deque

INF = 10**9


def edges_of(n, mask, elist):
    return [elist[i] for i in range(len(elist)) if (mask >> i) & 1]


def degrees(n, edges):
    d = [0] * n
    for u, v in edges:
        d[u] += 1
        d[v] += 1
    return d


def components(n, edges):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for u, v in edges:
        a, b = find(u), find(v)
        if a != b:
            parent[a] = b
    comps = {}
    for v in range(n):
        comps.setdefault(find(v), []).append(v)
    return list(comps.values())


def connected(n, edges):
    return len(components(n, edges)) <= 1


def _bfs_from(n, edges, srcs):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    D = {}
    for s in srcs:
        dist = [-1] * n
        dist[s] = 0
        q = deque([s])
        while q:
            x = q.popleft()
            for y in adj[x]:
                if dist[y] < 0:
                    dist[y] = dist[x] + 1
                    q.append(y)
        D[s] = dist
    return D


def tau_exact(n, edges):
    """tau = sum over components of min T-join (metric matching DP on odd vertices)."""
    if not edges:
        return 0
    d = degrees(n, edges)
    total = 0
    for comp in components(n, edges):
        cs = set(comp)
        T = [v for v in comp if d[v] % 2 == 1]
        if not T:
            continue
        sub = [(u, v) for (u, v) in edges if u in cs]
        D = _bfs_from(n, sub, T)
        k = len(T)
        full = (1 << k) - 1
        dp = [INF] * (1 << k)
        dp[0] = 0
        for mask in range(1 << k):
            if dp[mask] >= INF or mask == full:
                continue
            i = 0
            while (mask >> i) & 1:
                i += 1
            base = dp[mask]
            Ti = T[i]
            for j in range(k):
                if j != i and not ((mask >> j) & 1):
                    c = base + D[Ti][T[j]]
                    m2 = mask | (1 << i) | (1 << j)
                    if c < dp[m2]:
                        dp[m2] = c
        if dp[full] >= INF:
            return INF
        total += dp[full]
    return total


def tau_brute(n, edges):
    """subset enumeration; for validation, m <= 14."""
    d = degrees(n, edges)
    Tmask = tuple(x % 2 for x in d)
    m = len(edges)
    best = INF
    for S in range(1 << m):
        par = [0] * n
        x = S
        i = 0
        while x:
            if x & 1:
                u, v = edges[i]
                par[u] ^= 1
                par[v] ^= 1
            x >>= 1
            i += 1
        if tuple(par) == Tmask:
            c = bin(S).count("1")
            if c < best:
                best = c
    return best


def tau_join_edges(n, edges):
    """return one min T-join edge set (list of edge index tuples via metric matching paths)."""
    d = degrees(n, edges)
    eidx = {e: i for i, e in enumerate(edges)}
    from collections import Counter
    F = Counter()
    for comp in components(n, edges):
        cs = set(comp)
        T = [v for v in comp if d[v] % 2 == 1]
        if not T:
            continue
        sub = [(u, v) for (u, v) in edges if u in cs]
        # DP with parent reconstruction
        D = _bfs_from(n, sub, T)
        # shortest path reconstruction between two vertices
        def spath(a, b):
            # BFS from a within sub
            dist = {a: 0}
            prev = {}
            q = deque([a])
            adj = [[] for _ in range(n)]
            for u, v in sub:
                adj[u].append(v)
                adj[v].append(u)
            while q:
                x = q.popleft()
                for y in adj[x]:
                    if y not in dist:
                        dist[y] = dist[x] + 1
                        prev[y] = x
                        q.append(y)
            path = [b]
            while path[-1] != a:
                path.append(prev[path[-1]])
            return list(zip(path[1:], path[:-1]))
        k = len(T)
        full = (1 << k) - 1
        dp = [INF] * (1 << k)
        par = [-1] * (1 << k)  # (i, j) pair used
        dp[0] = 0
        for mask in range(1 << k):
            if dp[mask] >= INF:
                continue
            i = 0
            while (mask >> i) & 1:
                i += 1
            base = dp[mask]
            for j in range(k):
                if j != i and not ((mask >> j) & 1):
                    c = base + D[T[i]][T[j]]
                    m2 = mask | (1 << i) | (1 << j)
                    if c < dp[m2]:
                        dp[m2] = c
                        par[m2] = (i, j)
        mask = full
        while mask:
            i, j = par[mask]
            for (a, b) in spath(T[i], T[j]):
                F[tuple(sorted((a, b)))] ^= 1
            mask ^= (1 << i) | (1 << j)
    return [e for e, c in F.items() if c]


def all_cycles_masks(n, edges):
    """all simple cycles as edge-index frozensets (each once)."""
    adj = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        adj[u].append((v, i))
        adj[v].append((u, i))
    res = set()
    for s in range(n):
        visited = [False] * n
        path = []
        pathedges = []

        def dfs(v):
            visited[v] = True
            path.append(v)
            for (w, i) in adj[v]:
                if w == s and len(path) >= 3:
                    res.add(frozenset(pathedges + [i]))
                elif not visited[w] and w > s:
                    pathedges.append(i)
                    dfs(w)
                    pathedges.pop()
            path.pop()
            visited[v] = False

        dfs(s)
    return [set(c) for c in res]


def ce_exact(n, edges):
    """exact minimum decomposition into cycles + single edges (partition semantics)."""
    m = len(edges)
    if m == 0:
        return 0
    cycm = []
    for c in all_cycles_masks(n, edges):
        x = 0
        for i in c:
            x |= 1 << i
        cycm.append(x)
    cycm = sorted(set(cycm))
    memo = {}
    full = (1 << m) - 1

    import sys
    sys.setrecursionlimit(100000)

    def f(mask):
        if mask == 0:
            return 0
        if mask in memo:
            return memo[mask]
        low = (mask & -mask).bit_length() - 1
        best = 1 + f(mask ^ (1 << low))
        for c in cycm:
            if (c >> low) & 1 and (c & ~mask) == 0:
                v = 1 + f(mask ^ c)
                if v < best:
                    best = v
        memo[mask] = best
        return best

    return f(full)


def girth(n, edges):
    """min cycle length, INF if forest."""
    g = INF
    adj = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        adj[u].append((v, i))
        adj[v].append((u, i))
    for s in range(n):
        dist = [-1] * n
        par_e = [-1] * n
        dist[s] = 0
        q = deque([s])
        while q:
            x = q.popleft()
            for (w, i) in adj[x]:
                if dist[w] < 0:
                    dist[w] = dist[x] + 1
                    par_e[w] = i
                    q.append(w)
                elif i != par_e[x] and dist[w] >= dist[x]:
                    g = min(g, dist[x] + dist[w] + 1)
    return g


def greedy_decomp(n, edges, restarts=8):
    """upper-bound certificate: remove cycles (shortest-first), singles = rest. Returns piece count."""
    best = len(edges)
    for t in range(restarts):
        E = set(map(tuple, edges))
        ncyc = 0
        while True:
            C = _shortest_cycle(n, E)
            if C is None:
                break
            E -= C
            ncyc += 1
        best = min(best, ncyc + len(E))
    return best


def _shortest_cycle(n, E):
    """shortest cycle as a set of edges, via per-edge deletion BFS. None if forest."""
    Elist = list(E)
    best = None
    bestcyc = None
    for i, (u0, v0) in enumerate(Elist):
        # BFS from u0 to v0 avoiding edge i
        adj = [[] for _ in range(n)]
        for j, (u, v) in enumerate(Elist):
            if j == i:
                continue
            adj[u].append((v, j))
            adj[v].append((u, j))
        prevv = [-1] * n
        prevE = [-1] * n
        dist = [-1] * n
        dist[u0] = 0
        q = deque([u0])
        while q:
            x = q.popleft()
            for (y, j) in adj[x]:
                if dist[y] < 0:
                    dist[y] = dist[x] + 1
                    prevv[y] = x
                    prevE[y] = j
                    q.append(y)
        if dist[v0] >= 0:
            L = dist[v0] + 1
            if best is None or L < best:
                best = L
                cyc = {Elist[i]}
                y = v0
                while y != u0:
                    cyc.add(Elist[prevE[y]])
                    y = prevv[y]
                bestcyc = cyc
    return bestcyc


def spanning_trees_oddcount(n, edges, cap=200):
    """min oddcount over enumerated spanning trees (small graphs only); T = G's odd vertices."""
    m = len(edges)
    if not connected(n, edges):
        return None
    d = degrees(n, edges)
    Tset_ref = [[v % 2 for v in d]]
    best = [INF]
    cnt = [0]

    def rec(avail_mask, compcount):
        # count components of (V, avail edges)
        if cnt[0] > cap:
            return
        cur_edges = [edges[i] for i in range(m) if (avail_mask >> i) & 1]
        comps = components(n, cur_edges)
        if len(comps) == 1:
            cnt[0] += 1
            oc = oddcount(n, cur_edges, Tset_ref[0])
            if oc < best[0]:
                best[0] = oc
            return
        # pick lowest edge not in avail? choose an edge connecting two comps
        for i in range(m):
            if (avail_mask >> i) & 1:
                continue
            u, v = edges[i]
            cu = next(c for c in comps if u in c)
            cv = next(c for c in comps if v in c)
            if cu is not cv:
                cnt[0] += 1
                rec(avail_mask | (1 << i), compcount)
        return

    rec(0, 0)
    return best[0] if cnt[0] <= cap else None


def oddcount(n, tree_edges, Tset=None):
    """T-join of a forest (unique) for parity pattern Tset (list of 0/1 per vertex).
    Defaults to the forest's own degree parities. Returns #edges in the unique T-join."""
    if Tset is None:
        Tset = [v % 2 for v in degrees(n, tree_edges)]
    adj = [[] for _ in range(n)]
    for i, (u, v) in enumerate(tree_edges):
        adj[u].append((v, i))
        adj[v].append((u, i))
    cnt = [0] * len(tree_edges)  # parity of T below
    deg = list(degrees(n, tree_edges))
    Tpar = list(Tset)
    removed = [False] * n
    dead = [False] * len(tree_edges)
    q = deque(v for v in range(n) if deg[v] <= 1)
    while q:
        x = q.popleft()
        if removed[x]:
            continue
        removed[x] = True
        for (w, i) in adj[x]:
            if dead[i]:
                continue
            dead[i] = True
            cnt[i] ^= Tpar[x]
            deg[w] -= 1
            Tpar[w] ^= Tpar[x]
            if deg[w] == 1:
                q.append(w)
    return sum(cnt)


def ledger_values(n, edges):
    m = len(edges)
    t = tau_exact(n, edges)
    g = girth(n, edges)
    r1 = t + (m - t) // 3
    lg = t + (m - t) // g if g < INF else m  # forest: tau = m
    return {"n": n, "m": m, "tau": t, "girth": g, "R1": r1, "gledger": lg}
