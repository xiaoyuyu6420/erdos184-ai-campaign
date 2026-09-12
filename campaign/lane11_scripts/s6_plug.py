"""s6: verify the path-plug lemma numerically.
Plug move: F parity subgraph, J = G-F with cycle C; P path in F (k edges) with endpoints x,y on C;
A = longer arc of C between x,y, B = shorter arc (b edges).
Move: F' = (F \\ P) u B ; new cycle P u A ; predicted gain = k - b  (positive iff k > b).
We construct explicit decompositions and verify piece counts against prediction, and ce via DP.
"""
import sys
sys.path.insert(0, "/Users/munich/Desktop/数学/front184/campaign/lane11_scripts")
from gg import *

def plug_certificate(n, edges, F, P, C, A, B):
    """construct decomposition after plug; return piece count (upper bound on ce)."""
    Pset = set(map(tuple, P)); Bset = set(map(tuple, B)); Cset = set(map(tuple, C)); Aset = set(map(tuple, A))
    Fset = set(map(tuple, F))
    Fp = Fset - Pset
    for x in B:
        Fp.add(tuple(x))
    # sanity: F' parity == original parity
    def par(S):
        d = degrees(n, list(S))
        return tuple(x % 2 for x in d)
    assert par(Fp) == par(Fset), "plug broke parity"
    # pieces: |F'| singles + cycle P u A + greedy cycles of J' = G - F' - (P u A)
    Jp = [x for x in edges if tuple(x) not in Fp and tuple(x) not in (Pset | Aset)]
    npieces = len(Fp) + 1 + greedy_decomp(n, Jp)
    return npieces

print("== example 1: 4-cycle x-a-y-b-x + long path x-p1-...-pk-y (k>=3) ==")
def plug_graph(k):
    # vertices: 0=x, 1=a, 2=y, 3=b, path 4..3+k
    e = [(0,1),(1,2),(2,3),(3,0)]
    prev = 0
    for i in range(1, k+1):
        e.append((prev, 3+i)); prev = 3+i
    e.append((prev, 2))
    return e
for k in (3, 5, 7):
    n = 4 + k
    e = plug_graph(k)
    m = len(e)
    t = tau_exact(n, e)
    r1 = t + (m - t)//3
    ce = ce_exact(n, e)
    # P = the x..y path: edges (0,4),(4,5),...,(2+k? ) : build list
    P = [(0,4)] + [(3+i, 4+i) for i in range(1, k)] + [(3+k, 2)]
    C = [(0,1),(1,2),(2,3),(3,0)]
    A = [(1,2),(2,3),(3,0),(0,1)][0:2]  # arc x-a-y = 2 edges: A = {(0,1),(1,2)}; B = {(2,3),(3,0)}
    A = [(0,1),(1,2)]; B = [(2,3),(3,0)]
    cert = plug_certificate(n, e, tau_join_edges(n, e), P, C, A, B)
    pred_gain = k - 2
    print(f"  k={k}: n={n} m={m} tau={t} R1={r1} ce={ce} plug_cert={cert} predicted_gain={pred_gain} "
          f"R1-cert={r1-cert} {'OK' if cert <= r1 - pred_gain + 1 else 'CHECK'}")

print("\n== example 2: lollipop (plug impossible: leaf not on any cycle) => R1 tight ==")
for n in (8, 10):
    e = [(0,1),(1,2),(2,0),(0,3)] + [(i, i+1) for i in range(3, n-1)]
    m = len(e); t = tau_exact(n, e); r1 = t + (m-t)//3
    ce = ce_exact(n, e)
    print(f"  n={n}: tau={t} R1={r1} ce={ce} R1==ce: {r1==ce}")

print("\n== example 3: G_8 window escape via plugs/long cycles ==")
def Gc(c):
    e = [(0,1),(0,2),(1,2)]
    for x in range(3, c+2):
        e += [(0,x),(1,x),(2,x)]
    return e
n = 10
e = Gc(8)
m = len(e); t = tau_exact(n, e); r1 = t + (m-t)//3
ce = ce_exact(n, e)
# free-F long-cycle bound T-H: ce <= |F| + 1 + (m-|F|-L)/3 with F = tau-join, L = longest cycle in G-F
# estimate L by greedy: use girth ledgers + a found 6-cycle existence; just report R1 vs ce vs M3 bound with L=6
L = 6
m3 = t + 1 + (m - t - L + 2)//3
print(f"  G_8: tau={t} R1={r1} ce={ce} M3-red(L=6,F=R) bound={m3}")
