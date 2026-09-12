"""
lane10 exact solver: exhaustive small graphs + exact complete-graph values.

Facts used:
  * states reachable from G by cycle-removal are exactly G - H for Eulerian H,
    so the memo stays inside 2^{m-n+c} states.
  * ce via the fixed-lowest-edge recursion (exact).
  * W / B via longest-cycle branching (exact).
"""
import sys, os, time, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from peel_lib import *

OUT = []
def P(s=""):
    OUT.append(s)
    print(s, flush=True)

# ---------------------------------------------------------------- A: exhaustive n <= 6
P("=" * 72)
P("A. EXHAUSTIVE: all graphs on n <= 6 vertices")
P("=" * 72)
import itertools
for n in (4, 5, 6):
    m = n * (n - 1) // 2
    cyc = enumerate_cycles(n)
    ce, ce_memo = make_ce(n, cyc)
    gs = GreedySolver(n, cyc)
    stats = dict(gap=0, worst=0, ratio=0.0, worstg=None, gapg=None, fails=0,
                 w_gt_ce=0)
    t0 = time.time()
    for E in range(1 << m):
        c = ce(E)
        # W with node guard: reuse memo; exhaustive over subgraphs of K_n is
        # at most 2^m states, fine for n<=6
        w = gs.W(E)
        if w - c > stats["gap"]:
            stats["gap"] = w - c
            stats["gapg"] = E
        if w > stats["worst"]:
            stats["worst"] = w
            stats["worstg"] = E
        if c and w / c > stats["ratio"]:
            stats["ratio"] = w / c
        if w > n - 1:
            stats["fails"] += 1
        if w > c:
            stats["w_gt_ce"] += 1
    P(f"n={n}: graphs={1<<m}, max W = {stats['worst']} (graph {stats['worstg']:0{m}b}), "
      f"max(W-ce) = {stats['gap']}, max W/ce = {stats['ratio']:.3f}, "
      f"#W>n-1 = {stats['fails']}, #W>ce = {stats['w_gt_ce']}, "
      f"{time.time()-t0:.1f}s")
    for tag, key in (("max-W", 'worstg'), ("max-gap", 'gapg')):
        E = stats[key]
        if E is None:
            continue
        c = ce(E); w = gs.W(E)
        P(f"    [{tag}] n={n} W={w} ce={c} edges={sorted(edges_of(n,E))}")

# ---------------------------------------------------------------- B: complete graphs
P()
P("=" * 72)
P("B. EXACT values on K_n (n<=8) and key structured graphs")
P("=" * 72)

import random as _rnd
def report(name, n, E, w_cap=2_000_000):
    cyc = enumerate_cycles(n) if n <= 7 else enumerate_graph_cycles(n, E)
    ce, _ = make_ce(n, cyc)
    c = ce(E)
    gs = GreedySolver(n, cyc)
    gs.cap = w_cap
    try:
        w = gs.W(E)
        wtxt = str(w)
    except RecursionError:
        rng = _rnd.Random(20260911)
        ws = gs.W_sample(E, 4000, rng)
        w = None
        wtxt = f">= {ws} (sampled 4000, exact cap {w_cap})"
    b = gs.B(E)
    P(f"{name}: n={n}, ce={c}, B(greedy-best)={b}, W(greedy-worst)={wtxt}")
    return c, w, b

for n in (4, 5, 6, 7):
    report(f"K_{n}", n, K_n(n))

# K_8 exact: reachable states 2^{21}; try with a node cap first
n = 8
cyc8 = enumerate_cycles(n)
gs8 = GreedySolver(n, cyc8)
gs8.cap = 3_000_000
t0 = time.time()
try:
    w = gs8.W(K_n(8))
    P(f"K_8: W = {w} exactly  ({gs8.nodes} nodes, {time.time()-t0:.0f}s)")
    P(f"     Theorem-A ceiling for n=8: {(8/2)*__import__('math').log(7/3) + 7*8/6:.2f} -> <= 12")
except RecursionError:
    P(f"K_8: W >= sampled value; exact exceeded {gs8.nodes} nodes ({time.time()-t0:.0f}s)")

# ---------------------------------------------------------------- C: structured graphs
P()
P("=" * 72)
P("C. Structured families (exact where state space permits)")
P("=" * 72)

PETERSEN_EDGES = ([(0,1),(1,2),(2,3),(3,4),(4,0)] +
                  [(5,7),(7,9),(9,6),(6,8),(8,5)] +
                  [(i, i+5) for i in range(5)])
report("Petersen", 10, mask_from_edges(10, PETERSEN_EDGES))
report("K_{3,3}", 6, K_ab(3,3))
report("K_{3,4}", 7, K_ab(3,4))
report("K_{3,5}", 8, K_ab(3,5))
report("K_{3,6}", 9, K_ab(3,6))
report("sun(3)=K_3vI_3", 6, sun(3))
report("sun(4)=K_3vI_4", 7, sun(4))
report("sun(5)=K_3vI_5", 8, sun(5))
report("K_{5,5}", 10, K_ab(5,5))
report("K_{5,6}", 11, K_ab(5,6), w_cap=400_000)

# K_{2k+1,2k+2}: W should be exactly 5k+2 for every tie-break (C7 certificate);
# cross-check W == B here for k=1,2
for k in (1, 2):
    n = 4*k+3
    E = K_ab(2*k+1, 2*k+2)
    report(f"K_{{{2*k+1},{2*k+2}}}", n, E)

# windmill / friendship graph F_c (c triangles through one vertex)
def friendship(c):
    n = 2*c + 1
    edges = []
    for t in range(c):
        edges += [(0, 1+2*t), (0, 2+2*t), (1+2*t, 2+2*t)]
    return n, mask_from_edges(n, edges)
for c in (2, 3, 4):
    n, E = friendship(c)
    report(f"friendship(c={c})", n, E)

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
          "RESULTS_exact.txt"), "w") as f:
    f.write("\n".join(OUT) + "\n")
print("\nsaved RESULTS_exact.txt")
