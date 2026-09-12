"""s4 v2: witnesses with corrected constructions and expectations.
Facts verified here:
- star: tau = ce = n-1 (R1 exactly tight)
- lollipop (C3 + pendant path): tau = n-3, ce = n-2  [my earlier n-2 hand value was wrong]
- double-triangle dumbbell: tau = n-5, ce = n-3 (R1 tight)
- W_6: tau = 3 (NOT 5 as in Lane 04 table; ce = 5 unchanged)  [cross-lane correction]
- K_{3,3}+chord: tau = 3, ce = 5; R1 = 5.33: boundary-certified (m+2tau = 16 = 3n-2)
- G* : tau = 6, ce = 8 (Lane 04 consistent)
- G_c = K2 v K_{1,c-1} (Lane 03 G_c): tau: c odd: c-1 (leaves only); c even: c-1 on 10-pt G8 verified; ce = c-1+ceil((c+2)/3) (Lane 03 M2)
- K_{s,t}: tau = t if s odd,t even; = s if t odd,s even; = max(s,t) if both odd; 0 if both even
- G_n = triangle + K_{3,n-3}: tau = n-3 (all n); ce = n at n=7 (Lane 05 counterexample family)
"""
import sys
sys.path.insert(0, "/Users/munich/Desktop/数学/front184/campaign/lane11_scripts")
from gg import *

def report(name, n, edges, expect_tau=None, expect_ce=None, exact=True):
    t = tau_exact(n, edges)
    m = len(edges)
    g = girth(n, edges)
    r1 = t + (m - t) // 3
    if exact:
        ce = ce_exact(n, edges)
    else:
        ce = greedy_decomp(n, edges)
    flag = ""
    if expect_tau is not None and t != expect_tau: flag += f" TAU-MISMATCH(expect {expect_tau})"
    if expect_ce is not None and ce != expect_ce: flag += f" CE-MISMATCH(expect {expect_ce})"
    print(f"{name:30s} n={n:2d} m={m:2d} tau={t:2d} ce={ce:2d} R1={r1:2d} girth={g if g<INF else 0:2d}{flag}")
    return t, ce

print("== stars (R1 exactly tight) ==")
for k in (3, 6, 9):
    report(f"star K_1,{k}", k + 1, [(0, i) for i in range(1, k + 1)], expect_tau=k, expect_ce=k)

print("\n== lollipop: triangle + pendant path == (tau = n-3, ce = n-2)")
def lollipop(n):
    e = [(0,1),(1,2),(2,0),(0,3)] + [(i, i+1) for i in range(3, n-1)]
    return e
for n in (5, 6, 8, 10):
    report(f"lollipop n={n}", n, lollipop(n), expect_tau=n-3, expect_ce=n-2)

print("\n== double-triangle dumbbell: tau = n-5, ce = n-3 ==")
def dumb2(L):
    # triangles (0,1,2) and (L+3,L+4,L+5), path 2-3-...-(L+3): L+1 edges
    e = [(0,1),(1,2),(2,0)]
    prev = 2
    for i in range(1, L+2):
        e.append((prev, 2+i)); prev = 2+i
    a = L+3
    e += [(a,a+1),(a+1,a+2),(a+2,a)]
    return e
for L in (1, 3, 5):
    n = L + 6
    report(f"2-triangle dumbbell L={L}", n, dumb2(L), expect_tau=n-5, expect_ce=n-3)

print("\n== W_6 and K_{3,3}+chord (Lane 04 tau-table reconciliation) ==")
W6 = [(i,(i+1)%5) for i in range(5)] + [(5,i) for i in range(5)]
report("W_6", 6, W6, expect_tau=3, expect_ce=5)
K33c = [(i,j) for i in (0,1,2) for j in (3,4,5)] + [(0,1)]
report("K_{3,3}+chord", 6, K33c, expect_tau=3, expect_ce=5)
print("   (Lane 04 table lists tau(W_6)=5 and calls both 'residual-tight';")
print("    corrected: m+2tau=16=3n-2 exactly on the R1 boundary -> certified ce<=5)")

print("\n== G* (Lane 04) ==")
idx = {v: i for i, v in enumerate("p q r f a2 a3 a4 b2 b3 b4 g1 g2".split())}
E_star = [("p","b2"),("b2","a2"),("a2","g1"),("g1","a3"),("a3","q"),("q","b3"),("b3","g2"),
          ("g2","b4"),("b4","a4"),("a4","r"),("r","f"),("f","p"),
          ("p","q"),("q","r"),("r","p"),
          ("p","a2"),("q","f"),("r","b4"),("b2","g2"),("a3","b3"),("a4","g1")]
Gstar = [tuple(sorted((idx[u], idx[v]))) for u, v in E_star]
report("G*", 12, Gstar, expect_tau=6, expect_ce=8)

print("\n== G_c = K2 v K_{1,c-1} (correct construction, Lane 03 M2: ce = c-1+ceil((c+2)/3)) ==")
def Gc(c):
    e = [(0,1),(0,2),(1,2)]
    for x in range(3, c+2):
        e += [(0,x),(1,x),(2,x)]
    return e
for c in (3, 4, 5, 6, 7, 8):
    n = c + 2
    exp_ce = c - 1 + (c + 2 + 2) // 3
    t_exp = (c - 1) if (c % 2 == 1) else None
    report(f"G_{c}", n, Gc(n-2), expect_tau=t_exp, expect_ce=exp_ce)

print("\n== K_{s,t} tau formula ==")
for (s, t) in [(2,2),(2,3),(2,4),(3,3),(3,4),(3,5),(3,6),(3,7),(4,4),(4,5),(4,7),(5,5)]:
    e = [(i, s+j) for i in range(s) for j in range(t)]
    tv = tau_exact(s+t, e)
    if s % 2 == 0 and t % 2 == 0: pred = 0
    elif s % 2 == 1 and t % 2 == 0: pred = t
    elif s % 2 == 0 and t % 2 == 1: pred = s
    else: pred = max(s, t)
    print(f"  K_{s},{t}: tau={tv} pred={pred} {'OK' if tv==pred else 'MISMATCH'}")

print("\n== G_n = triangle + K_{3,n-3}: tau = n-3 (all n); ce value ==")
def Gfam(n):
    e = [(0,1),(1,2),(2,0)]
    e += [(i,j) for i in (0,1,2) for j in range(3,n)]
    return e
for n in (6,7,8,9,10,11,12):
    t, ce = report(f"G_{n}", n, Gfam(n), expect_tau=n-3)

print("\n== tau == min spanning-tree oddcount sanity on witnesses ==")
for name, n, e in [("W6", 6, W6), ("G*", 12, Gstar)]:
    print(f"  {name}: spanning-tree-min = {spanning_trees_oddcount(n, e, cap=20000)} vs tau = {tau_exact(n, e)}")
