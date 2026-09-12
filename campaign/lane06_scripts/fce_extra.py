#!/usr/bin/env python3
"""
lane06 closing-round numerics (second pass).

New instances / verifications beyond fce_torus.py:
  1. K_{3,7}   (g=2): reproduce claimed EXACT f_ce = 10 = n-1+1.
  2. K_{3,8}   (g=2): new.  Campaign lower bound (4/3)m = 32/3 -> ceil = 11 = n-1+1.
  3. K_{3,9}   (g=2): new.  Campaign lower bound ceil(12) = 12 = n-1+1.
  4. K_{3,10}  (g=2): explicit 14-object decomposition (certificate check, no search),
                     matched with lower bound ceil(40/3) = 14  => f_ce = 14 by pinch.
  5. K_{4,6}   (g=2, EULERIAN: degrees 6 and 4): genus(K_{4,6}) = ceil(2*4/4) = 2 (Ringel).
                     Tests looseness of the Eulerian bound n+2g-4 = 18.

Genus data (Ringel, Map Color Theorem 1974): genus(K_{a,b}) = ceil((a-2)(b-2)/4).
"""
import time
from collections import defaultdict
from fce_torus import complete_bipartite, solve


def verify_decomposition(name, edges, objects, expect_cycle_or_single=True):
    """Independent certificate check: objects partition edges; each object is
    a simple cycle (all degrees 2, connected) or a single edge."""
    E = set(tuple(sorted(e)) for e in edges)
    covered = set()
    for obj in objects:
        o = [tuple(sorted(e)) for e in obj]
        assert len(set(o)) == len(o), "repeated edge within object"
        for e in o:
            assert e in E, f"object edge {e} not in graph"
            assert e not in covered, f"edge {e} covered twice"
            covered.add(e)
        if len(o) == 1:
            continue
        deg = defaultdict(int)
        adj = defaultdict(set)
        for (a, b) in o:
            deg[a] += 1
            deg[b] += 1
            adj[a].add(b)
            adj[b].add(a)
        assert all(d == 2 for d in deg.values()), "object not 2-regular -> not a cycle"
        # connectivity
        start = next(iter(adj))
        seen, stack = {start}, [start]
        while stack:
            x = stack.pop()
            for w in adj[x]:
                if w not in seen:
                    seen.add(w)
                    stack.append(w)
        assert len(seen) == len(deg), "cycle object disconnected"
    assert covered == E, f"uncovered edges: {len(E - covered)}"
    print(f"   certificate OK: {len(objects)} objects, all simple cycles / single edges, "
          f"partition of all {len(E)} edges")


def k310_construction():
    """K_{3,10}: split the size-10 side into parts {3,3,2,2}; each K_{3,3} -> one C6
    + 3 singles (4 objects), each K_{3,2} -> one C4 + 2 singles (3 objects).
    Total 4+4+3+3 = 14 objects."""
    left = [0, 1, 2]
    parts = [[3, 4, 5], [6, 7, 8], [9, 10], [11, 12]]
    edges = [(u, v) for u in left for v in range(3, 13)]
    objects = []
    for part in parts:
        sub = [(u, v) for u in left for v in part]
        subset = set(tuple(sorted(e)) for e in sub)
        if len(part) == 3:
            cyc = [(part[0], 0), (0, part[1]), (part[1], 1), (1, part[2]), (part[2], 2), (2, part[0])]
        else:  # len 2
            cyc = [(part[0], 0), (0, part[1]), (part[1], 1), (1, part[0])]
        cyc = [tuple(sorted(e)) for e in cyc]
        assert set(cyc) <= subset, "constructed cycle uses foreign edges"
        objects.append(set(cyc))
        rest = subset - set(cyc)
        for e in sorted(rest):
            objects.append({e})
    return edges, objects


if __name__ == "__main__":
    print("lane06 extra instances (genus 2 via Ringel: genus(K_{a,b})=ceil((a-2)(b-2)/4))\n")
    for (a, b, tcap) in [(3, 7, 300), (3, 8, 300), (3, 9, 300), (4, 6, 120)]:
        edges = complete_bipartite(a, b)
        n, m, best, stats = solve(edges, f"K_{{{a},{b}}}", time_cap=tcap)
        status = "EXACT" if not stats["capped"] else "UPPER(capped)"
        lb = -(-4 * b // 3)  # ceil(4m/3), campaign-certified K_{3,m} lower bound
        deg = defaultdict(int)
        for (u, v) in edges:
            deg[u] += 1
            deg[v] += 1
        eul = all(d % 2 == 0 for d in deg.values())
        print(f"== K_{{{a},{b}}} == n={n} e={m} genus={-(-(a-2)*(b-2)//4)} Eulerian={eul}")
        print(f"   f_ce = {best['cnt']}  [{status}]  nodes={stats['nodes']}  time<={tcap}s")
        print(f"   n-1 = {n-1} ; campaign LB ceil(4m/3) = {lb} ; "
              f"excess over n-1 >= {max(0, lb - (n-1))}")
        if best["witness"]:
            tot = sum(len(o) for o in best["witness"])
            assert tot == m
            seen = set()
            ok = True
            for o in best["witness"]:
                for e2 in o:
                    fe = frozenset(e2)
                    assert fe not in seen
                    seen.add(fe)
            print(f"   witness verified: {len(best['witness'])} edge-disjoint objects")
        print()
    # K_{3,10}: certificate pinch, no search
    print("== K_{3,10} ==  genus = ceil(8*... ) = ceil((1)(8)/4) = 2 ; n=13 e=30")
    edges, objects = k310_construction()
    verify_decomposition("K_{3,10}", edges, objects)
    print(f"   construction: 14 objects ; campaign LB ceil(40/3) = 14  => f_ce = 14 = n-1+2 (pinch)")
    print()
