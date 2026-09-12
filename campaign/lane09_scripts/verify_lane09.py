#!/usr/bin/env python3
"""
Lane 09 (block decomposition) verification script.

Verifies, by exact computation (DP over edge bitmasks):
  V1. Block additivity:      ce(G) == sum of ce(B) over blocks B          (Theorem A)
  V2. Counting identity:     sum_B (|V(B)|-1) == n - c(G) - iso(G)        (Lemma 2)
  V3. Cactus formula:        ce(G) == (n-1) - sum over cycle blocks (|C|-2) (Theorem E)
  V4. Known exact values:    C_n -> 1, trees -> n-1, K4 -> 3, K_{2,3} -> 3,
                             bowtie (two triangles at a cut vertex) -> 2,
                             K5 -> 2, Petersen -> 7
  V5. Parity lower bound:    ce(G) >= ceil(odd(G)/2) for every tested G   (Lemma F)

Random families: trees, cacti, block graphs (2-connected blocks glued at cut
vertices), G(n,p). ce computed exactly; blocks via the standard lowpoint
biconnected-components algorithm. Pure stdlib.
"""
import random
import sys

sys.setrecursionlimit(100000)

# ---------------------------------------------------------------- basics

def enumerate_cycles(n, edges):
    """All simple cycles as frozensets of edge indices (dedup by edge set)."""
    inc = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        inc[u].append(i)
        inc[v].append(i)
    cycles = set()

    def dfs(v, start, used, visited):
        for e in inc[v]:
            if e in used:
                continue
            a, b = edges[e]
            x = b if a == v else a
            if x == start:
                if len(used) >= 2:
                    cycles.add(frozenset(used | {e}))
            elif x not in visited:
                dfs(x, start, used | {e}, visited | {x})

    for s in range(n):
        dfs(s, s, frozenset(), {s})
    return list(cycles)


def ce_exact(n, edges):
    """Exact ce = min #parts (edge-disjoint cycles + single edges) partitioning E.

    DP: OPT(S) = min( |S| ,  min over cycles C subseteq S of 1 + OPT(S \\ C) ).
    Correctness: any optimal decomposition either uses no cycle (=> |S| singletons)
    or some cycle part C, and the rest is a decomposition of S\\C.
    """
    m = len(edges)
    if m == 0:
        return 0
    cmasks = [sum(1 << e for e in c) for c in enumerate_cycles(n, edges)]
    memo = {}

    def f(S):
        if S == 0:
            return 0
        r = memo.get(S)
        if r is not None:
            return r
        best = bin(S).count("1")
        for cm in cmasks:
            if cm & S == cm:
                val = 1 + f(S ^ cm)
                if val < best:
                    best = val
        memo[S] = best
        return best

    return f((1 << m) - 1)


def biconnected_blocks(n, edges):
    """Standard lowpoint algorithm. Returns list of (vertexset, edge-index tuple).
    Blocks are bridges (K2) or maximal 2-connected subgraphs. Isolated vertices ignored."""
    inc = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        inc[u].append((v, i))
        inc[v].append((u, i))
    disc = [-1] * n
    low = [0] * n
    t = [0]
    estack = []
    blocks = []

    def dfs(u, pe):
        disc[u] = low[u] = t[0]
        t[0] += 1
        for v, e in inc[u]:
            if e == pe:
                continue
            if disc[v] != -1:
                if disc[v] < disc[u]:
                    estack.append(e)
                    if disc[v] < low[u]:
                        low[u] = disc[v]
            else:
                estack.append(e)
                dfs(v, e)
                if low[v] < low[u]:
                    low[u] = low[v]
                if low[v] >= disc[u]:
                    cur = []
                    while True:
                        f = estack.pop()
                        cur.append(f)
                        if f == e:
                            break
                    vs = set()
                    for f in cur:
                        vs |= set(edges[f])
                    blocks.append((frozenset(vs), tuple(cur)))

    for s in range(n):
        if disc[s] == -1:
            dfs(s, -1)
    return blocks


def graph_stats(n, edges):
    """(num components, num isolated vertices, num odd-degree vertices)."""
    deg = [0] * n
    for u, v in edges:
        deg[u] += 1
        deg[v] += 1
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for u, v in edges:
        ra, rb = find(u), find(v)
        if ra != rb:
            parent[ra] = rb
    comps = len({find(v) for v in range(n)})
    iso = sum(1 for d in deg if d == 0)
    odd = sum(1 for d in deg if d % 2 == 1)
    return comps, iso, odd


# ---------------------------------------------------------------- generators

def gen_tree(n, rng):
    return [(rng.randrange(v), v) for v in range(1, n)]


def _norm(a, b):
    return (a, b) if a < b else (b, a)


def gen_cactus(n, rng):
    edges = []
    seen = set()
    nxt = 1
    while nxt < n:
        u = rng.randrange(nxt)
        room = n - nxt
        if room >= 2 and rng.random() < 0.6:
            k = min(rng.choice([3, 4]), room + 1)
            verts = [u] + list(range(nxt, nxt + k - 1))
            for i in range(k):
                e = _norm(verts[i], verts[(i + 1) % k])
                if e not in seen:
                    seen.add(e)
                    edges.append(e)
            nxt += k - 1
        else:
            e = _norm(u, nxt)
            seen.add(e)
            edges.append(e)
            nxt += 1
    return edges


def gen_block_graph(n, rng):
    """Chain/tree of 2-connected blocks (cycle + random chords) glued at cut vertices,
    plus occasional bridges."""
    edges = []
    nxt = 1
    while nxt < n:
        u = rng.randrange(nxt)
        room = n - nxt
        if room >= 2 and rng.random() < 0.7:
            k = min(rng.choice([3, 4, 5]), room + 1)
            verts = [u] + list(range(nxt, nxt + k - 1))
            for i in range(k):
                edges.append(_norm(verts[i], verts[(i + 1) % k]))
            for i in range(k):
                for j in range(i + 2, k):
                    if i == 0 and j == k - 1:
                        continue
                    if rng.random() < 0.3:
                        edges.append(_norm(verts[i], verts[j]))
            nxt += k - 1
        else:
            edges.append(_norm(u, nxt))
            nxt += 1
    return edges


def gen_gnp(n, p, rng):
    return [(u, v) for u in range(n) for v in range(u + 1, n) if rng.random() < p]


# ---------------------------------------------------------------- checks

failures = []
checked = {"V1": 0, "V2": 0, "V3": 0, "V5": 0}


def verify_graph(name, n, edges, cactus=False):
    comps, iso, odd = graph_stats(n, edges)
    blocks = biconnected_blocks(n, edges)

    # V2 counting identity:  sum_B (|V(B)|-1) == n - c(G)   (isolated-vertex
    # components contribute 0 = n_j - 1 automatically)
    lhs2 = sum(len(vs) - 1 for vs, _ in blocks)
    rhs2 = n - comps
    if lhs2 != rhs2:
        failures.append(f"V2 FAIL {name}: sum(|V(B)|-1)={lhs2} != n-c-iso={rhs2}")
    checked["V2"] += 1

    # V1 block additivity
    ce_g = ce_exact(n, edges)
    ce_sum = sum(ce_exact(n, [edges[i] for i in ed]) for _, ed in blocks)
    if ce_g != ce_sum:
        failures.append(f"V1 FAIL {name}: ce(G)={ce_g} != sum ce(B)={ce_sum}")
    checked["V1"] += 1

    # V5 parity lower bound  ce >= ceil(odd/2)
    if (ce_g + (-odd)) > ce_g:  # always true; keep linter quiet
        pass
    if ce_g < -(-odd // 2):
        failures.append(f"V5 FAIL {name}: ce={ce_g} < ceil(odd/2)={-(-odd // 2)} (odd={odd})")
    checked["V5"] += 1

    # V3 cactus formula
    if cactus:
        n_cycles = sum(1 for vs, ed in blocks if len(ed) >= 3)
        pred = (n - comps if comps >= 1 else n) - 1 - sum(
            len(ed) - 2 for vs, ed in blocks if len(ed) >= 3
        )
        # formula stated for connected cactus; generators are connected
        pred = n - 1 - sum(len(ed) - 2 for _, ed in blocks if len(ed) >= 3)
        if ce_g != pred:
            failures.append(f"V3 FAIL {name}: ce={ce_g} != n-1-sum(|C|-2)={pred}")
        if ce_g != len(blocks):
            failures.append(f"V3b FAIL {name}: ce={ce_g} != #blocks={len(blocks)}")
        checked["V3"] += 1
    return ce_g


def main():
    rng = random.Random(20260911)

    # ---------- V4 known exact values ----------
    known = []
    for nn in range(3, 9):
        c = [(i, (i + 1) % nn) for i in range(nn)]
        val = ce_exact(nn, c)
        if val != 1:
            failures.append(f"V4 FAIL C_{nn}: ce={val} != 1")
    known.append("C_n (3<=n<=8): ce=1 OK")

    for nn in [4, 6, 8]:
        t = gen_tree(nn, rng)
        val = ce_exact(nn, t)
        if val != nn - 1:
            failures.append(f"V4 FAIL tree n={nn}: ce={val} != {nn-1}")
    known.append("trees: ce=n-1 OK")

    k4 = [(i, j) for i in range(4) for j in range(i + 1, 4)]
    if ce_exact(4, k4) != 3:
        failures.append(f"V4 FAIL K4: ce={ce_exact(4, k4)} != 3")
    known.append("K4: ce=3 (=n-1, tight 2-connected example) OK")

    k23 = [(0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4)]
    if ce_exact(5, k23) != 3:
        failures.append(f"V4 FAIL K_(2,3): ce={ce_exact(5, k23)} != 3")
    known.append("K_(2,3): ce=3 (> cyclomatic number 2) OK")

    bowtie = [(0, 1), (1, 2), (2, 0), (0, 3), (3, 4), (4, 0)]
    if ce_exact(5, bowtie) != 2:
        failures.append(f"V4 FAIL bowtie: ce={ce_exact(5, bowtie)} != 2")
    known.append("bowtie (2 triangles at cut vertex): ce=2 = 1+1, no cut discount OK")

    k5 = [(i, j) for i in range(5) for j in range(i + 1, 5)]
    if ce_exact(5, k5) != 2:
        failures.append(f"V4 FAIL K5: ce={ce_exact(5, k5)} != 2")
    known.append("K5: ce=2 ((n-1)/2, Hamilton decomposition) OK")

    petersen = [(i, (i + 1) % 5) for i in range(5)] + \
               [(i, i + 5) for i in range(5)] + \
               [(5, 7), (7, 9), (9, 6), (6, 8), (8, 5)]
    ce_p = ce_exact(10, petersen)
    if ce_p != 7:
        failures.append(f"V4 FAIL Petersen: ce={ce_p} != 7")
    known.append("Petersen: ce=7 (construction: two 5-cycles + 5 spokes; parity lb 5) OK")

    k6 = [(i, j) for i in range(6) for j in range(i + 1, 6)]
    ce_k6 = ce_exact(6, k6)
    known.append(f"K6: ce={ce_k6} (Hamilton cycles + perfect matching => expect 5 = n-1)")
    if ce_k6 != 5:
        failures.append(f"V4 FAIL K6: ce={ce_k6} != 5")

    # ---------- random families ----------
    fams = [
        ("tree", lambda n: gen_tree(n, rng), False),
        ("cactus", lambda n: gen_cactus(n, rng), True),
        ("blockgraph", lambda n: gen_block_graph(n, rng), False),
        ("gnp", lambda n: gen_gnp(n, rng.choice([0.2, 0.3, 0.4]), rng), False),
    ]
    counts = {}
    for trial in range(300):
        fname, gen, cactus = fams[trial % len(fams)]
        n = rng.randint(2, 9)
        edges = gen(n)
        # keep m small for the DP
        if len(edges) > 13:
            edges = edges[:13]
        val = verify_graph(f"{fname}#{trial}", n, edges, cactus=cactus)
        counts[fname] = counts.get(fname, 0) + 1

    print("== V4 known values ==")
    for line in known:
        print("  " + line)
    print("== random families ==")
    for fname, cnt in counts.items():
        print(f"  {fname}: {cnt} graphs verified")
    print(f"== checks passed ==  V1={checked['V1']} V2={checked['V2']} "
          f"V3={checked['V3']} V5={checked['V5']}")
    if failures:
        print("FAILURES:")
        for f in failures:
            print("  " + f)
        sys.exit(1)
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
