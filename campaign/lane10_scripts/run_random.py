"""
lane10 random sampling: random graphs n = 7..9, canonical + sampled-worst greedy
vs exact ce.  Also: the K_10 / Petersen question (does T(5)=complement of
Petersen decompose into 3 Ham cycles -> greedy-worst(K_10) >= 10 = n).
"""
import sys, os, time, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from peel_lib import *

OUT = []
def P(s=""):
    OUT.append(s)
    print(s, flush=True)

P("=" * 72)
P("D. RANDOM GRAPHS: exact ce vs greedy (canonical & 300 sampled tie-breaks)")
P("=" * 72)
rng = random.Random(184)
for n, ps, cnt in ((7, (0.3, 0.5, 0.7), 400), (8, (0.3, 0.5), 300), (9, (0.3, 0.5), 150)):
    m = n * (n - 1) // 2
    for p in ps:
        rows = []
        t0 = time.time()
        for _ in range(cnt):
            E = 0
            for idx in range(m):
                if rng.random() < p:
                    E |= 1 << idx
            if E == 0 or is_forest(n, E):
                continue
            cyc = enumerate_cycles(n) if n <= 7 else enumerate_graph_cycles(n, E)
            ce, _ = make_ce(n, cyc)
            gs = GreedySolver(n, cyc)
            gs.cap = 500_000
            try:
                w = gs.W(E)
            except RecursionError:
                w = gs.W_sample(E, 300, rng)
            b = gs.B(E)
            rows.append((E, ce(E), w, b))
        if rows:
            mg = max(w - c for _, c, w, _ in rows)
            mr = max(w / c for _, c, w, _ in rows if c)
            mwn1 = sum(1 for _, c, w, _ in rows if w > n - 1)
            wcex = sum(1 for _, c, w, _ in rows if w > c)
            P(f"n={n},p={p}: {len(rows)} graphs, max(W-ce)={mg}, max W/ce={mr:.2f}, "
              f"#W>n-1={mwn1}/{len(rows)}, #W>ce={wcex}/{len(rows)}, {time.time()-t0:.0f}s")

P()
P("=" * 72)
P("E. K_10 / Petersen: does T(5) (complement of Petersen) = 3 edge-disjoint")
P("   Hamilton cycles?  If yes, greedy-worst(K_10) >= 3 + W(Petersen) = 10 = n.")
P("=" * 72)

PETERSEN_EDGES = ([(0,1),(1,2),(2,3),(3,4),(4,0)] +
                  [(5,7),(7,9),(9,6),(6,8),(8,5)] +
                  [(i, i+5) for i in range(5)])
n = 10
Peten = mask_from_edges(n, PETERSEN_EDGES)
K10 = K_n(n)
T5 = K10 & ~Peten

# enumerate Ham cycles of T5 via graph-restricted DFS (search for 3 covering T5)
cycT = enumerate_graph_cycles(n, T5)
hams = [C for (l, C) in cycT if l == 10]
P(f"T(5): edges={popcount(T5)}, Hamilton cycles contained: {len(hams)}")

# DFS for 3 edge-disjoint Ham cycles covering T5
best = []
def dfs(rem, chosen):
    if len(chosen) == 3:
        if rem == 0:
            best.append(list(chosen))
        return
    if len(best) > 0:
        return
    # pick the Ham cycles containing the lowest remaining edge
    low = (rem & -rem).bit_length() - 1
    for C in hams:
        if C & rem == C and (C >> low) & 1:
            chosen.append(C)
            dfs(rem & ~C, chosen)
            chosen.pop()
            if best:
                return

dfs(T5, [])
if best:
    triple = best[0]
    P("T(5) = 3 edge-disjoint Ham cycles: YES")
    cycv = []
    for C in triple:
        # recover vertex list for readability
        edges = set(edges_of(n, C))
        adjd = {}
        for a, b in edges:
            adjd.setdefault(a, []).append(b)
            adjd.setdefault(b, []).append(a)
        v = sorted(adjd)[0]; prev = None; walk = [v]
        for _ in range(10):
            nxt = [x for x in adjd[v] if x != prev][0]
            prev, v = v, nxt
            walk.append(v)
        cycv.append(walk[:-1])
    pc, lf, ok, log = verify_run(n, K10, cycv)
    P(f"   resulting greedy run on K_10: ok={ok}, pieces={pc+lf} (n=10, ce=9)")
    cycP = enumerate_graph_cycles(n, Peten)
    ceP, _ = make_ce(n, cycP)
    gsP = GreedySolver(n, cycP)
    P(f"   Petersen: ce={ceP(Peten)}, B={gsP.B(Peten)}, W={gsP.W(Peten)}")
else:
    P("T(5) = 3 edge-disjoint Ham cycles: NO (within search space)")

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
          "RESULTS_random.txt"), "w") as f:
    f.write("\n".join(OUT) + "\n")
print("\nsaved RESULTS_random.txt")
