"""
lib_cycles.py -- core library for lane 02 (Eulerian cycle decomposition).

Graph representation:
    n                  : number of vertices, vertices are 0..n-1
    adj                : list of int bitmasks, adj[u] has bit v set iff uv is an edge
    edges              : list of (u, v) with u < v, index = position
    cycle              : bitmask over edge indices (a simple cycle's edge set)

c(H) = minimum number of edge-disjoint simple cycles partitioning E(H)
       (H Eulerian => such a decomposition exists; multigraph 2-cycles never occur
        since inputs are simple graphs).

Everything is exact (branch & bound with admissible lower bounds), no heuristics
affecting correctness: greedy only supplies an initial upper bound; the IDA*
(iterative deepening) search proves optimality or the caller is warned.
"""
from math import ceil
import sys

sys.setrecursionlimit(100000)


# ---------------------------------------------------------------- basic

def edges_from_adj(n, adj):
    E = []
    for u in range(n):
        m = adj[u] >> (u + 1)
        v = u + 1
        while m:
            if m & 1:
                E.append((u, v))
            v += 1
            m >>= 1
    return E


def adj_from_edges(n, edges):
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj


def degrees(n, adj):
    return [bin(a).count("1") for a in adj]


def is_eulerian(n, adj):
    return all(d % 2 == 0 for d in degrees(n, adj))


def components(n, adj):
    """connected components as vertex bitmasks (isolated vertices included)."""
    allv = (1 << n) - 1
    seen = 0
    comps = []
    while seen != allv:
        rest = (~seen) & allv
        v0 = (rest & -rest).bit_length() - 1
        comp = 0
        frontier = 1 << v0
        while frontier:
            comp |= frontier
            nxt = 0
            f = frontier
            while f:
                b = f & -f
                f ^= b
                nxt |= adj[b.bit_length() - 1]
            frontier = nxt & ~comp
        seen |= comp
        comps.append(comp)
    return comps


def subgraph_edges(n, edges, vmask):
    return [(u, v) for (u, v) in edges if (vmask >> u) & 1 and (vmask >> v) & 1]


# ------------------------------------------------- cycle enumeration

def enumerate_cycles(n, edges):
    """All simple cycles of the graph, as edge-index bitmasks (deduplicated).

    Rule: every cycle is generated exactly once from its smallest vertex s,
    travelling only through vertices > s, then closing back to s.
    """
    eind = {}
    for i, (u, v) in enumerate(edges):
        eind[(u, v)] = i
    adj = adj_from_edges(n, edges)
    cycles = set()

    def dfs(start, v, visited, path, edge_mask):
        a = adj[v]
        while a:
            b = a & -a
            a ^= b
            w = b.bit_length() - 1
            if w == start and len(path) >= 3:
                close = eind[(min(v, start), max(v, start))]
                cycles.add(edge_mask | (1 << close))
            elif w > start and not (visited >> w) & 1:
                dfs(start, w, visited | (1 << w), path + [w],
                    edge_mask | (1 << eind[(min(v, w), max(v, w))]))

    for s in range(n):
        dfs(s, s, 1 << s, [s], 0)
    return sorted(cycles)


# ------------------------------------------------- exact min decomposition

class _Timeout(Exception):
    pass


def min_cycle_decomp(n, edges, node_limit=20_000_000):
    """Exact c(H) for a simple Eulerian graph given by (n, edges).

    Returns (c, cycles_as_edge_masks, proven_optimal).
    For disconnected graphs it recurses on components (min = sum of mins).
    """
    if not edges:
        return 0, [], True
    adj = adj_from_edges(n, edges)
    comps = components(n, adj)
    nontrivial = []
    for cv in comps:
        ce = subgraph_edges(n, edges, cv)
        if ce:
            nontrivial.append((cv, ce))
    if len(nontrivial) > 1:
        total, allc, ok = 0, [], True
        for cv, ce in nontrivial:
            # renumber component vertices to 0..sz-1 (avoids phantom vertices)
            vs = sorted(v for v in range(n) if (cv >> v) & 1)
            remap = {v: i for i, v in enumerate(vs)}
            ce2 = [(remap[u], remap[v]) for (u, v) in ce]
            cn = len(vs)
            c, cc, okc = min_cycle_decomp(cn, ce2, node_limit)
            total += c
            allc += cc
            ok = ok and okc
        return total, allc, ok

    m = len(edges)
    full = (1 << m) - 1
    cyc = enumerate_cycles(n, edges)
    if not cyc:
        # non-Eulerian input: no decomposition; signal with m "phantom" edges
        return None, [], True
    lens = [bin(c).count("1") for c in cyc]
    maxlen = max(lens)

    # edge -> cycles containing it
    through = [[] for _ in range(m)]
    for ci, cm in enumerate(cyc):
        mm = cm
        while mm:
            b = mm & -mm
            mm ^= b
            through[b.bit_length() - 1].append(ci)

    # greedy upper bound (valid: remainder of Eulerian graph stays Eulerian)
    unc = full
    ub_cycles = []
    by_len = sorted(range(len(cyc)), key=lambda ci: -lens[ci])
    while unc:
        pick = None
        for ci in by_len:
            if cyc[ci] & unc == cyc[ci]:
                pick = ci
                break
        assert pick is not None, "remainder of Eulerian graph must contain a cycle"
        unc &= ~cyc[pick]
        ub_cycles.append(pick)
    ub = len(ub_cycles)

    # trivial lower bounds
    lb = max(1, (m + maxlen - 1) // maxlen)
    if lb > ub:  # cannot happen (greedy is a valid decomposition), guard anyway
        lb = ub

    nodes = 0

    def search(uncovered, budget):
        nonlocal nodes
        if uncovered == 0:
            return []
        if budget <= 0:
            return None
        nodes += 1
        if nodes > node_limit:
            raise _Timeout
        # admissible lower bound 1: edges / maxlen
        cnt = bin(uncovered).count("1")
        if (cnt + maxlen - 1) // maxlen > budget:
            return None
        # admissible lower bound 2: max_v ceil(deg_uncovered(v)/2)
        d = [0] * n
        mm = uncovered
        while mm:
            b = mm & -mm
            mm ^= b
            u, v = edges[b.bit_length() - 1]
            d[u] += 1
            d[v] += 1
        if max((x + 1) // 2 for x in d) > budget:
            return None
        # rarest uncovered edge
        best_e, best_cands = -1, None
        mm = uncovered
        while mm:
            b = mm & -mm
            mm ^= b
            e = b.bit_length() - 1
            cands = [ci for ci in through[e] if cyc[ci] & uncovered == cyc[ci]]
            if not cands:
                return None
            if best_cands is None or len(cands) < len(best_cands):
                best_e, best_cands = e, cands
                if len(cands) == 1:
                    break
        for ci in sorted(best_cands, key=lambda c: -lens[c]):
            r = search(uncovered & ~cyc[ci], budget - 1)
            if r is not None:
                return [ci] + r
        return None

    for k in range(lb, ub + 1):
        try:
            r = search(full, k)
        except _Timeout:
            return len(ub_cycles), [cyc[ci] for ci in ub_cycles], False
        if r is not None:
            return len(r), [cyc[ci] for ci in r], True
    return ub, [cyc[ci] for ci in ub_cycles], True


# ------------------------------------------------- families / constructions

def friendship(k):
    """k triangles sharing one common vertex 0.  n = 2k+1."""
    n = 2 * k + 1
    E = []
    for i in range(k):
        a, b = 1 + 2 * i, 2 + 2 * i
        E += [(0, a), (0, b), (a, b)]
    return n, E


def complete_odd(m):
    """K_{2m+1}."""
    n = 2 * m + 1
    return n, [(u, v) for u in range(n) for v in range(u + 1, n)]


def octahedron():
    """K_{2,2,2}: 6 vertices, 4-regular."""
    vs = [(0, 3), (1, 4), (2, 5)]  # antipodal pairs
    bad = set()
    for a, b in vs:
        bad.add((min(a, b), max(a, b)))
    n = 6
    return n, [(u, v) for u in range(n) for v in range(u + 1, n)
               if (u, v) not in bad]


def complete_even_minus_matching(m):
    """K_{2m} minus a perfect matching."""
    n = 2 * m
    bad = {(2 * i, 2 * i + 1) for i in range(m)}
    return n, [(u, v) for u in range(n) for v in range(u + 1, n)
               if (u, v) not in bad]


def bouquet(k, n0, E0):
    """k copies of a rooted family (with root vertex 0) sharing vertex 0."""
    n = 1 + k * (n0 - 1)
    E = []
    for j in range(k):
        off = j * (n0 - 1)
        mp = {0: 0}
        for v in range(1, n0):
            mp[v] = off + v
        E += [(mp[u], mp[v]) for (u, v) in E0]
    return n, E


def walecki_odd(m):
    """Walecki Hamiltonian decomposition of K_{2m+1} (cycle edge sets).

    Vertices: 0..2m-1 on a cycle role plus 'inf' = 2m.
    Base Hamiltonian path P = [0, 1, 2m-1, 2, 2m-2, ..., m-1, m+1, m] on Z_{2m};
    cycle i (0 <= i < m) = shifted path (endpoints i, i+m) plus both edges to inf.
    Returns (n, edges, list_of_edge_index_lists) and validity flags.
    """
    n = 2 * m + 1
    inf = 2 * m
    E = [(u, v) for u in range(n) for v in range(u + 1, n)]
    idx = {e: i for i, e in enumerate(E)}

    def shift(x, i):
        return (x + i) % (2 * m)

    seq = [0]
    for i in range(1, m):
        seq += [i, 2 * m - i]
    seq += [m]
    assert len(seq) == 2 * m

    cycles = []
    for i in range(m):
        path = [shift(x, i) for x in seq]
        cyc_edges = [(path[0], inf)]
        for a, b in zip(path, path[1:]):
            cyc_edges.append((min(a, b), max(a, b)))
        cyc_edges.append((path[-1], inf))
        cycles.append(sorted(idx[e] for e in cyc_edges))
    return n, E, cycles


def walecki_even_minus_matching(m):
    """Walecki decomposition of K_{2m} - M into m-1 Hamiltonian cycles."""
    n = 2 * m
    M = {(2 * i, 2 * i + 1) for i in range(m)}
    E = [(u, v) for u in range(n) for v in range(u + 1, n) if (u, v) not in M]
    idx = {e: i for i, e in enumerate(E)}

    def shift(x, i):
        return (x + i) % (2 * m)

    seq = [0]
    for i in range(1, m):
        seq += [i, 2 * m - i]
    seq += [m]
    cycles = []
    for i in range(m - 1):
        path = [shift(x, i) for x in seq]
        cyc_edges = [(min(a, b), max(a, b)) for a, b in zip(path, path[1:])]
        cycles.append(sorted(idx[e] for e in cyc_edges))
    return n, E, cycles


def verify_cycle_family(n, E, cycles):
    """Check: each cycle is a genuine simple cycle; they are edge-disjoint."""
    adj = adj_from_edges(n, E)
    used = set()
    for cyc in cycles:
        # rebuild vertex walk: match edges
        ces = [E[i] for i in cyc]
        if len(set(ces)) != len(ces):
            return False, "repeated edge in one cycle"
        for u, v in ces:
            if not ((adj[u] >> v) & 1):
                return False, "non-edge used"
        if len(set(ces)) < 3:
            return False, "cycle too short"
        # connectivity of the cycle as a graph
        deg = {}
        for u, v in ces:
            deg[u] = deg.get(u, 0) + 1
            deg[v] = deg.get(v, 0) + 1
        if any(d != 2 for d in deg.values()):
            return False, "not 2-regular on its vertex set"
        # connected?
        start = ces[0][0]
        seen = {start}
        stack = [start]
        while stack:
            x = stack.pop()
            for u, v in ces:
                for y in (u, v):
                    if y == x and (u if x == v else v) not in seen:
                        w = u if x == v else v
                        seen.add(w)
                        stack.append(w)
        if len(seen) != len(deg):
            return False, "cycle disconnected"
        for i in cyc:
            if i in used:
                return False, "edge reused across cycles"
            used.add(i)
    return True, "ok"


# ------------------------------------------------- suppression core

def suppress_core(n, edges):
    """Iteratively suppress degree-2 vertices (multigraph-safe).

    Returns (n_core, edges_core_multigraph, n_suppressed).
    Parallel edges are kept (u, v) duplicates; u < v everywhere.
    """
    E = list(edges)
    alive = set(range(n))
    changed = True
    supp = 0
    while changed:
        changed = False
        deg = {}
        for u, v in E:
            deg[u] = deg.get(u, 0) + 1
            deg[v] = deg.get(v, 0) + 1
        for v in sorted(alive):
            if deg.get(v, 0) == 2:
                inc = [(u, w) for (u, w) in E if u == v or w == v]
                a, b = [], []
                for (u, w) in inc:
                    (a if u == v else b).append(w)
                if len(a) != 1 or len(b) != 1:
                    continue  # parallel loop-degenerate; skip (cannot happen from simple)
                x, y = a[0], b[0]
                if x == y:
                    continue  # would create a loop; skip
                E = [(u, w) for (u, w) in E if u != v and w != v]
                E.append((min(x, y), max(x, y)))
                alive.discard(v)
                supp += 1
                changed = True
                break
    return len(alive), sorted(E), supp


# ------------------------------------------------- random graphs

import random as _rnd


def random_eulerian(n, p=0.5, tries=20000, rng=None):
    rng = rng or _rnd
    for _ in range(tries):
        adj = [0] * n
        for u in range(n):
            for v in range(u + 1, n):
                if rng.random() < p:
                    adj[u] |= 1 << v
                    adj[v] |= 1 << u
        if is_eulerian(n, adj) and any(adj):
            return n, edges_from_adj(n, adj)
    return None


def random_regular(d, n, tries=4000, rng=None):
    """random simple d-regular graph (configuration model + rejection)."""
    rng = rng or _rnd
    if (d * n) % 2 or d >= n:
        return None
    for _ in range(tries):
        stubs = [v for v in range(n) for _ in range(d)]
        rng.shuffle(stubs)
        E = set()
        ok = True
        for i in range(0, len(stubs), 2):
            u, v = stubs[i], stubs[i + 1]
            if u == v:
                ok = False
                break
            e = (min(u, v), max(u, v))
            if e in E:
                ok = False
                break
            E.add(e)
        if ok:
            return n, sorted(E)
    return None


def subdivide_each_edge_once(n, edges):
    """subdivide every edge once: n' = n + m, degrees preserved, c preserved."""
    E = []
    nn = n
    for (u, v) in edges:
        w = nn
        nn += 1
        E.append((min(u, w), max(u, w)))
        E.append((min(w, v), max(w, v)))
    return nn, E
