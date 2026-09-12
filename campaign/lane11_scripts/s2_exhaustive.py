"""s2: exhaustive n<=7 sweep for tau-structure conjectures + ledger checks.
T-B (S(n)): non-tree => tau <= n-2
A':  m >= n+3 => tau <= n-3        (connected)
L :  delta>=3, n>=6 => tau <= n-3
tau >= |T|/2; forest: tau = m = ce
R1: ce <= tau + (m-tau)//3 ; girth ledger: ce <= tau + (m-tau)//g
window: m + 2*tau > 1.5*3*n i.e. m+2tau > 4.5n (count per n)
"""
import itertools, sys, random
sys.path.insert(0, "/Users/munich/Desktop/数学/front184/campaign/lane11_scripts")
from gg import *

viol = {"TB": [], "Ap": [], "L": [], "half": [], "forest": [], "R1": [], "GL": []}
win = {n: [] for n in range(1, 8)}
maxtau = {}  # (n,m) -> max tau
tau_at_max = {}
residual_n7 = []
random.seed(11)

for n in range(1, 8):
    elist = list(itertools.combinations(range(n), 2))
    M = len(elist)
    for mask in range(1 << M):
        edges = edges_of(n, mask, elist)
        m = len(edges)
        if m == 0:
            continue
        d = degrees(n, edges)
        if max(d) == 0:
            continue
        conn = connected(n, edges)
        t = tau_exact(n, edges)
        Tcnt = sum(1 for x in d if x % 2 == 1)
        key = (n, m)
        if t > maxtau.get(key, -1):
            maxtau[key] = t
        # tau >= |T|/2
        if 2 * t < Tcnt:
            viol["half"].append((n, edges, t, Tcnt))
        if conn:
            istree = (m == n - 1)
            # T-B
            if not istree and t > n - 2:
                viol["TB"].append((n, edges, t))
            # A'
            if m >= n + 2 and t > n - 3:   # m>=n+3 in integers: m-n >= 3
                pass
            if m - n >= 3 and t > n - 3:
                viol["Ap"].append((n, edges, t))
            # L
            if n >= 6 and min(d) >= 3 and t > n - 3:
                viol["L"].append((n, edges, t))
            # window (3n/2 frontier): m <= 3n and m+2tau > 4.5n
            if m <= 3 * n and 2 * (m + 2 * t) > 9 * n:
                win[n].append((m, t, mask))
        else:
            # forest check (disconnected forest): tau = m
            if t != m:
                viol["forest"].append((n, edges, t, m))
        if m == n - 1 and conn and (t != m):
            viol["forest"].append((n, edges, t, m))
        # residual class at n=7 (m+2tau >= 3n-2)
        if n == 7 and conn and m + 2 * t >= 19:
            residual_n7.append((mask, m, t))

print("violations:")
for k, v in viol.items():
    print(f"  {k}: {len(v)}", v[:3])
for n in range(1, 8):
    print(f"window n={n}: {len(win[n])}", win[n][:4])
print(f"n=7 residual (m+2tau>=19): {len(residual_n7)}")

# max tau table for phase diagram (print selected)
print("\nmax tau per (n,m), n=7, m in 10..21:")
row = []
for m in range(10, 22):
    row.append(f"m={m}:{maxtau.get((7,m),'-')}")
print("  " + "  ".join(row))
row = []
for m in range(4, 16):
    row.append(f"m={m}:{maxtau.get((6,m),'-')}")
print("n=6: " + "  ".join(row))

import json
with open("/Users/munich/Desktop/数学/front184/campaign/lane11_scripts/s2_out.json", "w") as f:
    json.dump({
        "viol_counts": {k: len(v) for k, v in viol.items()},
        "win": {str(n): win[n][:20] for n in win},
        "maxtau_n7": {m: maxtau.get((7, m)) for m in range(1, 22)},
        "maxtau_n6": {m: maxtau.get((6, m)) for m in range(1, 16)},
        "maxtau_n5": {m: maxtau.get((5, m)) for m in range(1, 11)},
        "residual_n7_count": len(residual_n7),
    }, f, indent=1)
print("saved s2_out.json")
