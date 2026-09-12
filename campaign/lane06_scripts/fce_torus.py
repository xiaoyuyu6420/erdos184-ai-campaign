#!/usr/bin/env python3
"""
lane06 (genus graphs) numeric recon: exact f_ce for small TOROIDAL (orientable genus 1) graphs.

f_ce(G) = minimum number of objects (edge-disjoint simple cycles + single edges)
          partitioning E(G).  Erdos #184 currency (same convention as notes/attack_planar.md).

Method: DFS branch-and-bound over "which object covers the smallest uncovered edge":
  either that edge is a single-edge object, or it lies in a simple cycle (enumerate all
  simple cycles through it in the current remaining graph). Prune with lower bound
  ceil(rem / n) (each object has <= n edges) plus "forest remainder" exact closure.
Node/time caps: when hit we report an upper bound (first-improvement witness), NOT exact.

Every claimed value is reproducible: this script prints a witness decomposition
(objects as edge lists) for each graph.

Genus-1 status of the instances is classical literature data (not computed here):
  K_{3,m} for m<=6, K_{4,4}, K_7, Petersen, Heawood, Pappus, C_m x C_m  -- all toroidal.
  (Ringel, "Map Color Theorem"; White & Binet citations in lane_06_genus.md.)
"""

import time
from collections import defaultdict

NODE_CAP = 3_000_000
TIME_CAP = 90  # seconds per instance


def complete_bipartite(a, b):
    return [(i, a + j) for i in range(a) for j in range(b)]


def complete_graph(k):
    return [(i, j) for i in range(k) for j in range(i + 1, k) if (i, j) != (0, 0)]


def cartesian_cycle_product(m, n):
    # C_m x C_n  (toroidal grid), vertices (i,j) -> i*n+j
    edges = set()
    for i in range(m):
        for j in range(n):
            u = i * n + j
            edges.add(tuple(sorted((u, ((i + 1) % m) * n + j))))
            edges.add(tuple(sorted((u, i * n + (j + 1) % n))))
    return sorted(edges)


def petersen():
    edges = []
    for i in range(5):
        edges.append(tuple(sorted((i, (i + 1) % 5))))        # outer cycle
        edges.append(tuple(sorted((i, i + 5))))              # spokes
        edges.append(tuple(sorted((i + 5, (i + 2) % 5 + 5))))  # inner star
    return sorted(set(edges))


def lcf(n, jumps):
    # LCF notation: vertex i gets chord to (i + jumps[i % len(jumps)]) mod n
    edges = [(i, (i + 1) % n) for i in range(n)]
    seen = set()
    for i in range(n):
        j = (i + jumps[i % len(jumps)]) % n
        if i != j and (i, j) not in seen and (j, i) not in seen:
            seen.add((i, j))
            edges.append((i, j))
    return sorted(edges)


def cycles_through_edge(rem, e, n):
    """All simple cycles of rem containing edge e=(u,v), as frozensets of tuple-edges."""
    u, v = e
    rest = rem - {e}
    adj = defaultdict(list)
    for (a, b) in rest:
        adj[a].append(b)
        adj[b].append(a)
    out = []
    path = [v]
    used = {v}

    def dfs():
        last = path[-1]
        if last == u:
            if len(path) >= 3:
                cyc = {tuple(sorted((path[i], path[i + 1]))) for i in range(len(path) - 1)}
                cyc.add(e)
                out.append(frozenset(cyc))
            return
        if len(path) >= n:
            return
        for w in adj[last]:
            if w not in used:
                used.add(w)
                path.append(w)
                dfs()
                path.pop()
                used.remove(w)

    dfs()
    return out


def has_any_cycle(rem, n):
    adj = defaultdict(set)
    for (a, b) in rem:
        adj[a].add(b)
        adj[b].add(a)
    seen = set()

    for s in adj:
        if s in seen:
            continue
        # iterative DFS with parent tracking
        stack = [(s, None)]
        parent = {s: None}
        while stack:
            x, p = stack.pop()
            seen.add(x)
            for w in adj[x]:
                if w == p:
                    continue
                if w in parent:
                    return True
                parent[w] = x
                stack.append((w, x))
        # note: parent-detection on undirected DFS with pop-stack can false-positive?
        # No: we mark parent only on first visit; w in parent means already visited ->
        # back edge (cycle) unless w == p (the edge we came by).  Sound for simple graphs.
    return False


def solve(edges, name, node_cap=NODE_CAP, time_cap=TIME_CAP):
    E = sorted(tuple(sorted(e)) for e in edges)
    n = len({x for e in E for x in e})
    m = len(E)
    adj_full = defaultdict(set)
    for (a, b) in E:
        adj_full[a].add(b)
        adj_full[b].add(a)

    best = {"cnt": m + 1, "witness": None}
    stats = {"nodes": 0, "t0": time.time(), "capped": False}

    def dfs(rem, cnt, objects):
        stats["nodes"] += 1
        if stats["nodes"] > node_cap or time.time() - stats["t0"] > time_cap:
            stats["capped"] = True
            return
        if not rem:
            if cnt < best["cnt"]:
                best["cnt"] = cnt
                best["witness"] = [sorted(tuple(sorted(x)) for x in obj) for obj in objects]
            return
        # closure: forest remainder -> all singles forced
        if not has_any_cycle(rem, n):
            if cnt + len(rem) < best["cnt"]:
                best["cnt"] = cnt + len(rem)
                best["witness"] = [sorted(tuple(sorted(x)) for x in obj) for obj in objects] + \
                                  [[e] for e in sorted(rem)]
            return
        # lower bound: each object <= n edges
        if cnt + (len(rem) + n - 1) // n >= best["cnt"]:
            return
        e = min(rem)
        # option 1: e is a single edge
        objects.append({e})
        dfs(rem - {e}, cnt + 1, objects)
        objects.pop()
        if stats["capped"]:
            return
        # option 2: e in some cycle
        for cyc in cycles_through_edge(rem, e, n):
            if cyc <= rem:
                objects.append(cyc)
                dfs(rem - cyc, cnt + 1, objects)
                objects.pop()
                if stats["capped"]:
                    return

    dfs(frozenset(E), 0, [])
    return n, m, best, stats


def report(name, edges, genus_note):
    n, m, best, stats = solve(edges, name)
    deg = defaultdict(int)
    for (a, b) in edges:
        deg[a] += 1
        deg[b] += 1
    eulerian = all(d % 2 == 0 for d in deg.values())
    peel_bound = (m + 2 * (n - 1)) / 3            # L6.1:  e/3 + 2(n-1)/3
    eul_bound = m // 3 if eulerian else None      # L6.2:  floor(e/3) cycles
    status = "EXACT" if not stats["capped"] else "UPPER(capped)"
    print(f"== {name} ==  n={n} e={m}  [{genus_note}]  Eulerian={eulerian}")
    print(f"   f_ce = {best['cnt']}   [{status}]  nodes={stats['nodes']}")
    print(f"   n-1 = {n-1} | L6.1 peel bound {(m + 2*(n-1))//3 if (m+2*(n-1))%3==0 else round(peel_bound,2)}"
          f" | " + (f"L6.2 floor(e/3)={eul_bound}" if eulerian else "L6.2 n/a"))
    if best["witness"]:
        tot = sum(len(o) for o in best["witness"])
        assert tot == m, "witness does not cover all edges!"
        seen = set()
        for o in best["witness"]:
            for e2 in o:
                fe = frozenset(e2)
                assert fe not in seen, "witness repeats an edge!"
                seen.add(fe)
        print(f"   witness verified: {len(best['witness'])} edge-disjoint objects covering {tot} edges")
    print()
    return n, m, best["cnt"], status


if __name__ == "__main__":
    print("Exact / capped f_ce for small toroidal (orientable genus 1) graphs.\n")
    report("K_{3,3}", complete_bipartite(3, 3), "torus, genus(K_{3,m})=ceil((m-2)/4)=1")
    report("K_{3,4}", complete_bipartite(3, 4), "torus")
    report("K_{3,5}", complete_bipartite(3, 5), "torus")
    report("K_{3,6}", complete_bipartite(3, 6), "torus (campaign: >= (4/3)(n-3)=8)")
    report("K_{4,4}", complete_bipartite(4, 4), "torus; decomposes into 2 Hamilton cycles")
    report("K_7", complete_graph(7), "torus triangulation, 6-regular (Eulerian); Walecki: 3 Ham. cycles")
    report("Petersen", petersen(), "genus 1")
    report("Heawood", lcf(14, [5, -5]), "torus, cubic girth 6 (LCF[5,-5]^7)")
    report("Pappus", lcf(18, [5, 7, -7, 7, -7, -5]), "torus per literature, cubic girth 6")
    report("C3xC3", cartesian_cycle_product(3, 3), "torus grid, 4-regular Eulerian")
    report("C4xC4", cartesian_cycle_product(4, 4), "torus grid, 4-regular Eulerian")
