"""
lane10 certificates v2: independently verify explicit adversarial greedy runs.

Each certificate is a list of cycles; verify_run re-checks legality
(containment + longest + forest remainder) and counts pieces.
Constructions use the matching-pair decomposition (peel_lib), which was
itself sanity-checked for edge-disjointness, coverage and single-cycle-ness.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from peel_lib import *

OUT = []
def P(s=""):
    OUT.append(s)
    print(s)

P("=" * 72)
P("CERTIFICATES v2: explicit greedy runs (independently re-verified)")
P("=" * 72)

# ------------------------------------------------------- C2: K_8 -> 8 pieces
P("\n[C2] K_8: peel the 2 cross Ham cycles of K_{4,4} (parts {0..3},{4..7}),")
P("     remainder = K_4 u K_4, then triangles:  2 + 3 + 3 = 8 pieces  (n=8, ce=7)")
n = 8
K8 = K_n(n)
cross = cross_ham_decomp(4)          # 2 Ham cycles covering all 16 cross edges
path = [list(c) for c in cross] + [[0, 1, 2, 3], [4, 5, 6, 7]]
pc, lf, ok, log = verify_run(n, K8, path, verbose=True)
for s in log: P("   " + s)
P(f"   RESULT: ok={ok}, total pieces = {pc + lf}  (claim: W(K_8) >= 8 = n > 7 = n-1 = ce)")

# ------------------------------------------------------- C3: K_{2^k} recursion
P("\n[C3] K_{2^k} recursion: cross K_{2^{k-1},2^{k-1}} = 2^{k-2} Ham cycles,")
P("     then recurse on the two K_{2^{k-1}} blocks.  pieces(2^k) = 2^{k-2} + 2 pieces(2^{k-1}).")

def k2k_path(k):
    N = 2 ** k
    if k == 2:
        return [[0, 1, 2, 3]]           # Ham cycle of K_4; leaves 2 singles
    m = N // 2
    path = [list(c) for c in cross_ham_decomp(m, 0, m)]
    path += [[v for v in c] for c in k2k_path(k - 1)]
    path += [[v + m for v in c] for c in k2k_path(k - 1)]
    return path

for k in (3, 4, 5, 6):
    N = 2 ** k
    path = k2k_path(k)
    pc, lf, ok, log = verify_run(N, K_n(N), path)
    theory = N * (k + 1) // 4
    P(f"   K_{N}: {len(path)} cycles + {lf} singles, ok={ok}, pieces={pc+lf}, "
      f"formula N(k+1)/4 = {theory}, match={pc+lf == theory}")
P("   => W(K_{2^k}) >= 2^k (k+1)/4  i.e.  (1/(4 ln2)) n ln n (1+o(1)) = 0.3607 n ln n")

# ------------------------------------------------------- C4: K_{3,4} forced
P("\n[C4] K_{3,4}: circumference 6; after ANY 6-cycle remainder is a forest:")
P("     every greedy run = 1 cycle + 6 singles = 7 pieces  (n=7, ce=6=n-1)")
n = 7
K34 = K_ab(3, 4)
cyc = enumerate_cycles(n)
sixes = [C for (l, C) in cyc if l == 6 and C & K34 == C]
allf = all(is_forest(n, K34 & ~C) for C in sixes)
has7 = any(l >= 7 and C & K34 == C for (l, C) in cyc)
P(f"   #6-cycles contained in K_{{3,4}}: {len(sixes)}; all leave forests: {allf}; "
  f"7-cycle exists: {has7}")
path = [[0, 3, 1, 4, 2, 5]]
pc, lf, ok, log = verify_run(n, K34, path)
P(f"   certificate run ok={ok}: pieces = {pc+lf}  (forced for every tie-break)")

# ------------------------------------------------------- C5: sun(4)
P("\n[C5] sun(4) = K_3 v I_4 = K_3 u K_{3,4} (edge-union on shared 3-part), n=7:")
P("     6-cycle forced; then 4-cycle forced (join creates 4-cycles a,a',b,b'');")
P("     then forest.  pieces = 1+1+5 = 7 = n.  ce(sun4) computed exactly elsewhere.")
n = 7
S4 = sun(4)
C6 = [0, 3, 1, 4, 2, 5]
C4 = [0, 1, 6, 2]                    # 0-1 (triangle edge), 1-6, 6-2, 2-0
pc, lf, ok, log = verify_run(n, S4, [C6, C4], verbose=True)
for s in log: P("   " + s)
# check: every 6-cycle leaves a 4-cycle (so 2nd peel is forced to be a 4-cycle)
s6 = [C for (l, C) in cyc if l == 6 and C & S4 == C]
allhave4 = True
tri = cycle_mask(n, [0, 1, 2])
for C in s6:
    rem = S4 & ~C
    if not any(l >= 4 and C2 & rem == C2 for (l, C2) in cyc):
        allhave4 = False
# every (6-cycle, 4-cycle) pair leaves a forest
allf2 = True
for C in s6:
    rem = S4 & ~C
    for (l, C2) in cyc:
        if l == 4 and C2 & rem == C2 and not is_forest(n, rem & ~C2):
            allf2 = False
P(f"   #6-cycles: {len(s6)}; every 6-cycle leaves a >=4-cycle: {allhave4}; "
  f"every (6C,4C) pair leaves forest: {allf2}")

# ------------------------------------------------------- C6: amplification (K_16 blocks)
P("\n[C6] Amplifier: g disjoint copies of K_16 -> W = 20g, ce(K_16)=15 => ce = 15g,")
P("     n = 16g:  greedy = 1.25 n > n,  gap = 20g - 15g = 5g = n/3.2 = Theta(n)")
for g in (2, 3):
    n = 16 * g
    E = 0
    path = []
    for t in range(g):
        E |= shift_mask(16, K_n(16), 16 * t, n)
        for c in k2k_path(4):
            path.append([v + 16 * t for v in c])
    pc, lf, ok, log = verify_run(n, E, path)
    P(f"   g={g}: n={n}, ok={ok}, greedy pieces={pc+lf} = {(pc+lf)/n:.3f}n, "
      f"ce={15*g} (block additivity), gap={pc+lf-15*g} = {(pc+lf-15*g)/n:.3f}n")

# ------------------------------------------------------- C7: K_{2k+1,2k+2} adversary
P("\n[C7] K_{2k+1,2k+2}: k edge-disjoint 4k+2-cycles (matching pairs M_0uM_1,...)")
P("     drain the fixed (2k+1)-set of big vertices to degree 1; smalls to degree 2;")
P("     only one fresh big remains -> forest.  pieces = k + 4k+2 = 5k+2.")
for k in (1, 2, 3):
    a, N = 2 * k + 1, 2 * k + 2
    n = a + N
    E = K_ab(a, N)
    path = k_partial_cross_kcycles(k, a, 0, a)
    pc, lf, ok, log = verify_run(n, E, path)
    P(f"   k={k}: n={n}, m={(2*k+1)*(2*k+2)}, ok={ok}, pieces={pc+lf} vs 5k+2={5*k+2}: "
      f"{pc+lf == 5*k+2}")

# ------------------------------------------------------- C8: K_7 friendly
P("\n[C8] K_7 (odd): friendly = 3 edge-disjoint Ham cycles = 3 pieces = ce(K_7).")
n = 7
ham = [[0, 1, 2, 3, 4, 5, 6],
       [0, 2, 4, 6, 1, 3, 5],
       [0, 3, 6, 2, 5, 1, 4]]
pc, lf, ok, log = verify_run(n, K_n(7), ham)
P(f"   ok={ok}, pieces={pc+lf}")

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
          "RESULTS_certificates.txt"), "w") as f:
    f.write("\n".join(OUT) + "\n")
print("\nsaved RESULTS_certificates.txt")
