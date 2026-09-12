"""s1: validate tau_exact vs tau_brute; ce anchors; oddcount/tree tools."""
import random, sys, itertools
sys.path.insert(0, "/Users/munich/Desktop/数学/front184/campaign/lane11_scripts")
from gg import *

random.seed(11)
bad = 0
tested = 0
for n in range(1, 8):
    elist = list(itertools.combinations(range(n), 2))
    trials = 400 if n <= 6 else 1500
    for _ in range(trials):
        m = len(elist)
        mask = random.getrandbits(m)
        edges = edges_of(n, mask, elist)
        if len(edges) > 13:
            continue
        a = tau_exact(n, edges)
        b = tau_brute(n, edges)
        tested += 1
        if a != b:
            bad += 1
            print("MISMATCH", n, edges, a, b)
print(f"tau validation: tested={tested} mismatches={bad}")

# ce anchors
def star(k):
    return [(0, i) for i in range(1, k + 1)]

assert ce_exact(4, [(0,1),(1,2),(2,3),(3,0)]) == 1, "C4"
assert ce_exact(4, [(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]) == 3, "K4"  # C4 + 2 singles; no 2-piece split exists
assert ce_exact(6, [(i,j) for i in (0,1,2) for j in (3,4,5)]) == 4, "K33"
assert ce_exact(4, star(3)) == 3, "K13"
assert tau_exact(6, [(i,j) for i in (0,1,2) for j in (3,4,5)]) == 3, "tau K33"
assert tau_exact(4, [(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]) == 2, "tau K4"
assert tau_exact(4, star(3)) == 3, "tau star"
# path P4: T = {0,3}: tau = 3 = m
assert tau_exact(4, [(0,1),(1,2),(2,3)]) == 3, "tau P4"
# forest: tau = m
assert tau_exact(5, [(0,1),(0,2),(3,4)]) == 3, "tau forest"
print("ce/tau anchors OK")

# spanning-tree oddcount = tau on small graphs (exhaustive tree enumeration, capped)
import math
ok = 0; fail = 0
for n in range(2, 7):
    elist = list(itertools.combinations(range(n), 2))
    for _ in range(300):
        mask = random.getrandbits(len(elist))
        edges = edges_of(n, mask, elist)
        if not connected(n, edges):
            continue
        t = tau_exact(n, edges)
        st = spanning_trees_oddcount(n, edges, cap=3000)
        if st is None:
            continue
        if st == t:
            ok += 1
        else:
            fail += 1
            print("TREE-MISMATCH", n, edges, t, st)
print(f"tau == min spanning-tree oddcount: ok={ok} fail={fail}")
