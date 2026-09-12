"""s5: window hunt + certificates + correlation data.
Window W11 := {G connected : m + 2*tau > 4.5*n} (R1 fails to give 3n/2).
Predictions:
- n<=7 empty (s2 exhaustive, 0 hits)
- n=8: empty (case analysis); n=9: empty (parity: |T|=8 needs complement odd-count 1, impossible)
- n=10: needs all-odd no-PM; |T|=8 case impossible (T-independent => m<=17<28)
- K_{3,n-3}: window from n>=32 (m+2tau = 5n-15 > 4.5n), saved by bipartite girth ledger
- G_n = triangle + K_{3,n-3}: window from n>=25 (m+2tau = 5n-12 > 4.5n), saved by short-side 6-cycles
Checks here:
A) random sampling n=8..12: any window hits? classify triangle-ful / girth
B) K_{3,29} (n=32): window membership + bipartite ledger <= 1.5n
C) G_n n=25..30: window membership + constructive certificate ce <= 1.5n (tau-join singles + greedy cycles of G-F)
D) correlation: n=7 random graphs (tau, ce) + n=8 (tau, R1, greedy) -> tau-ce relation
"""
import sys, random, json, itertools
sys.path.insert(0, "/Users/munich/Desktop/数学/front184/campaign/lane11_scripts")
from gg import *

random.seed(2026)
out = {}

print("A) random sampling for window hits")
hits = {}
for n in (8, 9, 10, 11, 12):
    elist = list(itertools.combinations(range(n), 2))
    M = len(elist)
    H = 0
    wh = []
    for _ in range(4000):
        mask = random.getrandbits(M)
        edges = edges_of(n, mask, elist)
        m = len(edges)
        if m < 3 or m > 3 * n or not connected(n, edges):
            continue
        t = tau_exact(n, edges)
        if m + 2 * t > 4.5 * n:
            g = girth(n, edges)
            tri = 1 if any(True for _ in ()) else (1 if g == 3 else 0)
            wh.append((m, t, tri, mask))
    hits[n] = wh
    print(f"  n={n}: sampled 4000, window hits = {len(wh)}", wh[:3])
out["A_random_hits"] = {str(k): v[:10] for k, v in hits.items()}

print("\nB) K_{3,29}: window + bipartite ledger (n=32)")
n = 32
e = [(i, 3+j) for i in range(3) for j in range(29)]
m = len(e)
t = tau_exact(n, e)
g = girth(n, e)
gl = t + (m - t) // g
print(f"  m={m} tau={t} m+2tau={m+2*t} vs 4.5n={4.5*n}  -> window: {m+2*t > 4.5*n}")
print(f"  girth={g} gledger={gl} vs 1.5n={1.5*n} -> certified: {gl <= 1.5*n}")
out["B_k3_29"] = {"m": m, "tau": t, "window": m + 2*t > 4.5*n, "gledger": gl}

print("\nC) G_n triangle-ful window + certificate (n=25..30)")
def Gfam_big(nn):
    e = [(0,1),(1,2),(2,0)]
    e += [(i,j) for i in (0,1,2) for j in range(3,nn)]
    return e
resC = []
for nn in (24, 25, 26, 28, 30):
    e = Gfam_big(nn)
    m = len(e)
    t = tau_exact(nn, e)
    win = m + 2*t > 4.5*nn
    # certificate: F = tau-join singles; greedy cycles on G-F
    F = tau_join_edges(nn, e)
    Fset = set(map(tuple, F))
    rest = [x for x in e if tuple(x) not in Fset]
    pieces = len(F) + greedy_decomp(nn, rest)
    gl = t + (m - t) // girth(nn, e)
    print(f"  n={nn}: m={m} tau={t} m+2tau={m+2*t} win={win} | cert pieces={pieces} (<= {1.5*nn}: {pieces <= 1.5*nn}) | gledger={gl}")
    resC.append({"n": nn, "m": m, "tau": t, "window": win, "cert": pieces, "ok": pieces <= 1.5*nn})
out["C_Gn"] = resC

print("\nD) tau-ce correlation, n=7 random (exact ce)")
data = []
elist = list(itertools.combinations(range(7), 2))
for _ in range(2500):
    mask = random.getrandbits(21)
    edges = edges_of(7, mask, elist)
    m = len(edges)
    if m < 2 or not connected(7, edges):
        continue
    t = tau_exact(7, edges)
    ce = ce_exact(7, edges)
    data.append((m, t, ce))
# bucket by m: mean tau, mean ce, mean R1-ce slack
from collections import defaultdict
buckets = defaultdict(list)
for (m, t, ce) in data:
    buckets[m].append((t, ce))
print("  m | count | mean tau | max tau | mean ce | max ce | mean (R1-ce)")
for m in sorted(buckets):
    b = buckets[m]
    mt = sum(x[0] for x in b)/len(b)
    mc = sum(x[1] for x in b)/len(b)
    r1s = sum(t + (m-t)//3 - ce for (t, ce) in b)/len(b)
    print(f"  {m:2d} | {len(b):5d} | {mt:6.2f} | {max(x[0] for x in b):7d} | {mc:6.2f} | {max(x[1] for x in b):6d} | {r1s:6.2f}")
out["D_corr_n7"] = {str(m): {"cnt": len(b), "mean_tau": sum(x[0] for x in b)/len(b),
                              "mean_ce": sum(x[1] for x in b)/len(b)} for m, b in sorted(buckets.items())}

with open("/Users/munich/Desktop/数学/front184/campaign/lane11_scripts/s5_out.json", "w") as f:
    json.dump(out, f, indent=1, default=str)
print("\nsaved s5_out.json")
