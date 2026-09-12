"""s3: exact ce vs ledgers.
- n<=6: all graphs: ce <= R1 = tau+(m-tau)//3; ce <= gledger; forest => ce=m=tau; ce <= ceil(3n/2)
- n=7 : m<=14 all exact; residual (m+2tau>=19) with m>=15: random 8000 exact
- tight instances ce = n-1 / ce = n at n=7 catalog
"""
import itertools, sys, random
sys.path.insert(0, "/Users/munich/Desktop/数学/front184/campaign/lane11_scripts")
from gg import *

random.seed(7)
bad = {"R1": [], "GL": [], "forest": [], "s11": [], "half": []}
slack_r1 = {}
tight6 = []
tight7 = []
count = 0

for n in range(1, 8):
    elist = list(itertools.combinations(range(n), 2))
    M = len(elist)
    fullmax = 1 << M
    for mask in range(1 << M):
        edges = edges_of(n, mask, elist)
        m = len(edges)
        if m == 0:
            continue
        if n == 7 and m > 14:
            continue
        if n == 7 and random.random() < 0.7:
            continue  # subsample n=7 m<=14
        count += 1
        t = tau_exact(n, edges)
        g = girth(n, edges)
        ce = ce_exact(n, edges)
        r1 = t + (m - t) // 3
        gl = (t + (m - t) // g) if g < INF else m
        if ce > r1:
            bad["R1"].append((n, edges, ce, r1))
        if ce > gl:
            bad["GL"].append((n, edges, ce, gl))
        # forest check
        iscyclic = g < INF
        if not iscyclic and (ce != m or t != m):
            bad["forest"].append((n, edges, ce, t, m))
        if ce > (3 * n + 1) // 2:
            bad["s11"].append((n, edges, ce))
        Tcnt = sum(1 for x in degrees(n, edges) if x % 2)
        if 2 * t < Tcnt:
            bad["half"].append((n, edges, t, Tcnt))
        s = r1 - ce
        slack_r1[s] = slack_r1.get(s, 0) + 1
        if n == 6 and ce == 5:
            tight6.append((mask, m, t))
        if n == 7 and ce == 7:
            tight7.append((mask, m, t))
        if n == 7 and ce == 6:
            tight7.append((mask, m, t))

print(f"checked {count} graphs")
for k, v in bad.items():
    print(f"  viol {k}: {len(v)}", v[:3])
print("R1-ce slack histogram:", dict(sorted(slack_r1.items())))
print(f"n=6 tight ce=5: {len(tight6)}; n=7 ce in {{6,7}}: {len(tight7)}")

# anchor: K3 u K_{3,4} (the n=7 counterexample): triangle 0,1,2 + bipartite to 3..6
G7 = [(0,1),(1,2),(2,0)] + [(i,j) for i in (0,1,2) for j in (3,4,5,6)]
print("G7 = K3 u K_{3,4}: tau =", tau_exact(7, G7), " ce =", ce_exact(7, G7), " (expect 4, 7)")

import json
with open("/Users/munich/Desktop/数学/front184/campaign/lane11_scripts/s3_out.json", "w") as f:
    json.dump({
        "checked": count,
        "viol": {k: len(v) for k, v in bad.items()},
        "slack_hist": slack_r1,
        "tight6_count": len(tight6),
        "tight7_count": len(tight7),
    }, f, indent=1)
print("saved s3_out.json")
