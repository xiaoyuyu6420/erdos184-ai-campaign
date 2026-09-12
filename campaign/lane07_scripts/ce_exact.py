#!/usr/bin/env python3
"""Exact minimal cycle-decomposition size ce(G) for small graphs.

ce(G) = min number of (edge-disjoint cycles + single edges) partitioning E(G).
Method: recursive branch & bound. Take the lowest-index remaining edge e={u,v}.
Branch 1: every simple cycle containing e in the remaining graph.
Branch 2: e is a single edge.
Memoize on remaining-edge bitmask. Lower-bound pruning: ceil(|rest|/n_vertices).
"""
import sys
from collections import defaultdict

sys.setrecursionlimit(100000)


def enumerate_cycles_containing(nv, adj, rest, e):
    """All simple cycles containing edge e=(u,v), using only edges in rest.
    Returns list of edge-bitmasks (each includes e)."""
    u, v = e
    # walk from v back to u, never reusing an edge, never revisiting a vertex except at u
    cycles = []
    start = (v, 1 << v, 0)  # current vertex, visited-vertex mask, edge mask
    stack = [start]
    while stack:
        cur, vmask, emask = stack.pop()
        for w in adj[cur]:
            bit = 1 << edge_id(cur, w)
            if not (rest & bit):
                continue
            if w == u:
                cycles.append(emask | bit | (1 << edge_id(u, v)))
            elif not (vmask >> w) & 1:
                stack.append((w, vmask | (1 << w), emask | bit))
    return cycles


N_GLOBAL = 0
_id = {}


def edge_id(a, b):
    if a > b:
        a, b = b, a
    return _id[(a, b)]


def build_ids(nv):
    global _id
    _id = {}
    k = 0
    for a in range(nv):
        for b in range(a + 1, nv):
            _id[(a, b)] = k
            k += 1


def ce_exact(nv, edges, timeout_calls=30_000_000):
    """edges: list of (a,b). Returns exact ce value."""
    build_ids(nv)
    full = 0
    for (a, b) in edges:
        full |= 1 << edge_id(a, b)
    adj = [[] for _ in range(nv)]
    for (a, b) in edges:
        adj[a].append(b)
        adj[b].append(a)
    all_eids = [edge_id(a, b) for (a, b) in edges]

    memo = {}
    calls = [0]

    def lower(rest):
        # each unit covers <= nv edges
        return (bin(rest).count("1") + nv - 1) // nv

    def rec(rest):
        calls[0] += 1
        if calls[0] > timeout_calls:
            raise TimeoutError
        if rest == 0:
            return 0
        if rest in memo:
            return memo[rest]
        # lowest remaining edge
        eid = (rest & -rest).bit_length() - 1
        u, v = None, None
        for (a, b), i in _id.items():
            if i == eid:
                u, v = a, b
                break
        rest_no = rest & ~(1 << eid)
        best = 1 + rec(rest_no)  # e as single edge
        for cmask in enumerate_cycles_containing(nv, adj, rest, (u, v)):
            if cmask == (1 << eid):
                continue
            val = 1 + rec(rest & ~cmask)
            if val < best:
                best = val
        memo[rest] = best
        return best

    try:
        val = rec(full)
        return val, calls[0]
    except TimeoutError:
        return None, calls[0]


def ce_greedy_longest(nv, edges, rounds=2000):
    """Greedy: repeatedly extract a longest cycle; heuristic upper bound."""
    import itertools
    best = None
    rng = random.Random(42)
    for _ in range(rounds):
        rest = set(edges)
        cnt = 0
        while True:
            # find longest cycle in rest via permutation sampling + BFS fallback
            bestcyc = None
            verts = sorted({x for e in rest for x in e})
            if len(verts) <= 8:
                for perm in itertools.permutations(verts):
                    cyc = []
                    ok = True
                    for i in range(len(perm)):
                        e = (perm[i], perm[(i + 1) % len(perm)])
                        e = (min(e), max(e))
                        if e not in rest:
                            ok = False
                            break
                        cyc.append(e)
                    if ok and (bestcyc is None or len(cyc) > len(bestcyc)):
                        bestcyc = cyc
            else:
                # random double-tree / BFS cycles: try random Hamiltonian-ish cycles
                for _try in range(400):
                    perm = verts[:]
                    rng.shuffle(perm)
                    cyc = []
                    for i in range(len(perm)):
                        e = (perm[i], perm[(i + 1) % len(perm)])
                        e = (min(e), max(e))
                        if e in rest:
                            cyc.append(e)
                        else:
                            cyc = []
                            break
                    if cyc and (bestcyc is None or len(cyc) > len(bestcyc)):
                        bestcyc = cyc
                if bestcyc is None:
                    # shortest-cycle via BFS
                    bl = 99
                    for s in verts:
                        adjm = defaultdict(list)
                        for (a, b) in rest:
                            adjm[a].append(b)
                            adjm[b].append(a)
                        for tgt in adjm[s]:
                            # BFS shortest s->tgt avoiding edge once
                            from collections import deque
                            dq = deque([(s, [s])])
                            seen = {s}
                            found = None
                            while dq:
                                x, path = dq.popleft()
                                if len(path) - 1 > bl:
                                    break
                                for y in adjm[x]:
                                    if y == tgt and len(path) >= 2:
                                        cand = path[1:]  # cycle edges
                                        if found is None or len(cand) < len(found):
                                            found = cand
                                    elif y not in seen:
                                        seen.add(y)
                                        dq.append((y, path + [y]))
                            if found:
                                cyc = []
                                ok = True
                                p = [s] + found + [tgt] if found[-1] != tgt else [s] + found
                                # simpler: build from found path
                                break
                        if cyc:
                            break
                    if not cyc:
                        break
            if not bestcyc:
                cnt += len(rest)
                break
            cnt += 1
            rest -= set(bestcyc)
        best = cnt if best is None else min(best, cnt)
    return best


def complete_graph(nv):
    return [(a, b) for a in range(nv) for b in range(a + 1, nv)]


def two_cliques_plus_matching(half):
    """G = K_{m} + K_{m} (m=half) + perfect matching between the two halves.
    n=2m, delta = m-? : vertices have deg (m-1)+1 = m = n/2. Dirac graph."""
    m = half
    edges = complete_graph(m) + [(a + m, b + m) for (a, b) in complete_graph(m)]
    edges += [(i, i + m) for i in range(m)]
    return 2 * m, edges


def babai(k):
    """Babai/CKLOT extremal graph: A independent (4k), B (4k+2) with perfect
    matching, all A-B edges. n=8k+2, delta=n/2."""
    A = list(range(4 * k))
    B = list(range(4 * k, 8 * k + 2))
    edges = [(a, b) for a in A for b in B]
    edges += [(B[i], B[i + 1]) for i in range(0, len(B), 2)]
    return 8 * k + 2, edges


if __name__ == "__main__":
    import random
    print("=== exact ce(K_n) ===")
    for n in range(4, 9):
        v, c = ce_exact(n, complete_graph(n), timeout_calls=20_000_000)
        lb = ((n * (n - 1) // 2) + n - 1) // n
        walecki = (n - 1) // 2 if n % 2 == 1 else (n - 2) // 2 + n // 2
        print(f"K_{n}: ce = {v}  (LP lower bound {lb}, Walecki-ub {walecki}, calls {c})")
    print("=== exact ce: two cliques + matching (n even, delta=n/2) ===")
    for m in (3, 4):
        if m % 2 == 1:
            n, ed = two_cliques_plus_matching(m)
            v, c = ce_exact(n, ed, timeout_calls=20_000_000)
            print(f"n={n}: ce = {v} (calls {c})")
    print("=== exact ce: Babai graphs (n=8k+2, delta=n/2) ===")
    for k in (1,):
        n, ed = babai(k)
        v, c = ce_exact(n, ed, timeout_calls=20_000_000)
        print(f"n={n}: ce = {v} (calls {c})")
