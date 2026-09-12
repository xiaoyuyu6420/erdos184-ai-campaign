#!/usr/bin/env python3
"""
lane06: skewness (min #deleted edges making the graph ABSTRACTLY planar) of toroidal grids
C_m x C_m.  This certifies the "handle-stripping wall": on the torus (g=1) the number of
edges one must pay to reduce to the planar case grows like sqrt(n) (grids), so no
bound  f_ce(G) <= n-1+f(g)  can be reached by planarization with f(g) independent of n.

Upper bound sk <= m: delete one full row (m edges) -> ladder strip C_m x P_{m-1}, planar.
Lower bound: exhaustive search over deletion sets of size < m (m = 3,4,5 below), using
networkx.check_planarity (Boyer-Myrvold).  Also tests abstract planarity of the patch
C_3 x C_3 and C_4 x C_4 (used in the general sk >= m-3 argument, see lane note).
"""
import itertools
import networkx as nx


def torus_grid(m):
    G = nx.Graph()
    for i in range(m):
        for j in range(m):
            u = i * m + j
            G.add_edge(u, ((i + 1) % m) * m + j)
            G.add_edge(u, i * m + (j + 1) % m)
    return G


def sk_by_search(m, kmax=None):
    """exhaustive minimal planarizing edge set size, up to kmax (default m-1)."""
    G = torus_grid(m)
    edges = list(G.edges())
    if kmax is None:
        kmax = m - 1
    for k in range(0, kmax + 1):
        for F in itertools.combinations(edges, k):
            H = G.copy()
            H.remove_edges_from(F)
            is_planar, _ = nx.check_planarity(H)
            if is_planar:
                return k, F
    return None, None


if __name__ == "__main__":
    for m in (3, 4):
        G = torus_grid(m)
        p, _ = nx.check_planarity(G)
        print(f"C_{m}xC_{m}: n={G.number_of_nodes()} e={G.number_of_edges()} abstractly planar? {bool(p)}")
    # patch planarity (C_3xC_3 and C_4xC_4 as abstract graphs)
    for m in (3, 4):
        P = nx.cartesian_product(nx.cycle_graph(m), nx.cycle_graph(m))
        P = nx.convert_node_labels_to_integers(P)
        p, _ = nx.check_planarity(P)
        print(f"patch C_{m}xC_{m} abstractly planar? {bool(p)}")
    print()
    for m in (3, 4, 5):
        k, F = sk_by_search(m)
        print(f"sk(C_{m}xC_{m}) = {k}   (m = {m};  search exhausted sizes 0..{m-1})")
    # explicit upper-bound certificate: delete row 0
    for m in (3, 4, 5, 6):
        G = torus_grid(m)
        F = [((0 * m + j), ((1 % m) * m + j)) for j in range(m)]
        H = G.copy()
        H.remove_edges_from(F)
        p, _ = nx.check_planarity(H)
        print(f"delete row 0 ({m} edges) of C_{m}xC_{m}: planar? {bool(p)}")
