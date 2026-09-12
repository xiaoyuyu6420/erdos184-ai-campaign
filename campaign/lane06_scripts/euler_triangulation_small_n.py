#!/usr/bin/env python3
"""
lane06 closing check: do Eulerian planar triangulations exist for n = 4..8?

Corollary L6.2' claims f_ce <= n-4 for Eulerian planar triangulations (n >= 8) and the
draft's exclusion of n = 7 used a faulty face-count argument (face count of a
triangulation is f = 2n-4, always even, so parity of f excludes nothing).
Correct check: brute-force enumerate all n-vertex graphs with e = 3n-6 edges,
test planarity (networkx/Boyer-Myrvold) + connectivity => maximal planar,
then test all degrees even.

Expected known: n=4 none (K4 has odd degrees), n=5 none (wheel W5), n=6 the
octahedron (Eulerian, f_ce = 2 = n-4), n=7 ??? (draft claims none), n=8 ???
"""
import itertools
from collections import defaultdict
import networkx as nx


def all_edges(n):
    return list(itertools.combinations(range(n), 2))


def is_eulerian_triangulation(edge_set, n):
    if len(edge_set) != 3 * n - 6:
        return False
    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from(edge_set)
    if not nx.is_connected(G):
        return False
    planar, _ = nx.check_planarity(G)
    if not planar:
        return False
    return all(d % 2 == 0 for _, d in G.degree())


if __name__ == "__main__":
    import sys
    NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 7   # n=8 would be C(28,18)=1.3e7 checks
    for n in range(4, NMAX + 1):
        E = all_edges(n)
        target = 3 * n - 6
        found = []
        for comb in itertools.combinations(E, target):
            if is_eulerian_triangulation(comb, n):
                found.append(comb)
        print(f"n={n}: e={target}, scanned C({len(E)},{target}) = "
              f"{sum(1 for _ in itertools.combinations(E, target))} subsets; "
              f"Eulerian planar triangulations found: {len(found)}", flush=True)
        for f in found[:3]:
            G = nx.Graph()
            G.add_nodes_from(range(n))
            G.add_edges_from(f)
            print(f"   example deg seq: {sorted(d for _, d in G.degree())}", flush=True)
