"""
lane10: longest-cycle peeling greedy analysis library.

Conventions:
  A graph on vertex set {0..n-1} is represented by an int bitmask over the
  C(n,2) possible edges. Edge (i,j), i<j, gets bit index
      idx = i*(2n-i-1)//2 + (j-i-1).

Definitions (matching the campaign statement "反复取图中最长圈拿出来、余项进单边"):
  A (longest-first) greedy RUN on G is a sequence of cycles C_1..C_p with
  C_i a longest cycle of G_{i-1} := G - E(C_1) - ... - E(C_{i-1}), ending when
  the remainder is acyclic.  pieces(run) = p + (#remaining edges).
  W(G) = max pieces over all runs ("greedy-worst", adversarial tie-breaking).
  B(G) = min pieces over all runs ("greedy-best").
  ce(G) = min pieces over ALL decompositions into edge-disjoint cycles+singles.
"""
from itertools import combinations, permutations
import random

# ---------------------------------------------------------------- masks

def edge_index_table(n):
    EI = {}
    k = 0
    for i in range(n):
        for j in range(i + 1, n):
            EI[(i, j)] = k
            k += 1
    return EI

def popcount(x):
    return bin(x).count("1")

def edges_of(n, E):
    EI = edge_index_table(n)
    out = []
    for (i, j), idx in EI.items():
        if E >> idx & 1:
            out.append((i, j))
    return out

def mask_from_edges(n, edge_list):
    EI = edge_index_table(n)
    m = 0
    for a, b in edge_list:
        if a > b:
            a, b = b, a
        m |= 1 << EI[(a, b)]
    return m

def mask_from_cycles(n, cycles):
    """cycles: list of vertex lists."""
    E = 0
    for cyc in cycles:
        E |= cycle_mask(n, cyc)
    return E

def cycle_mask(n, cyc):
    EI = edge_index_table(n)
    m = 0
    k = len(cyc)
    for t in range(k):
        a, b = cyc[t], cyc[(t + 1) % k]
        if a > b:
            a, b = b, a
        m |= 1 << EI[(a, b)]
    return m

# ---------------------------------------------------------------- cycles of K_n

def enumerate_cycles(n):
    """All simple cycles of K_n as list of (length, mask).  n <= 9-ish."""
    EI = edge_index_table(n)
    out = []
    verts = list(range(n))
    for k in range(3, n + 1):
        for subset in combinations(verts, k):
            s0 = subset[0]
            seen = set()
            for perm in permutations(subset[1:]):
                cyc = (s0,) + perm
                rev = (s0,) + tuple(reversed(perm))
                key = min(cyc, rev)
                if key in seen:
                    continue
                seen.add(key)
                m = 0
                for t in range(k):
                    a, b = cyc[t], cyc[(t + 1) % k]
                    if a > b:
                        a, b = b, a
                    m |= 1 << EI[(a, b)]
                out.append((k, m))
    return out

# ---------------------------------------------------------------- forest test

def enumerate_graph_cycles(n, E):
    """All simple cycles CONTAINED IN graph E (mask), as list of (length, mask).
    Dedup by edge-set mask.  Efficient for sparse/medium graphs."""
    adj = {}
    EI = edge_index_table(n)
    for (i, j), idx in EI.items():
        if E >> idx & 1:
            adj.setdefault(i, set()).add(j)
            adj.setdefault(j, set()).add(i)
    found = {}

    def dfs(start, cur, visited, mask, depth):
        for w in adj.get(cur, ()):
            if w == start and depth >= 3:
                found[mask] = depth
            elif w not in visited and w > start:
                visited.add(w)
                a, b = min(cur, w), max(cur, w)
                dfs(start, w, visited, mask | (1 << EI[(a, b)]), depth + 1)
                visited.discard(w)

    for v in range(n):
        if v in adj:
            dfs(v, v, {v}, 0, 1)
    return sorted((l, m) for m, l in found.items())

def is_forest(n, E):
    """Union-find over set bits; forest iff acyclic."""
    if E == 0:
        return True
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    e = 0
    for (i, j), idx in edge_index_table(n).items():
        if E >> idx & 1:
            e += 1
            ri, rj = find(i), find(j)
            if ri == rj:
                return False
            parent[ri] = rj
    return True

# ---------------------------------------------------------------- exact ce

def make_ce(n, cycles):
    """Exact ce via recursion + memo, restricted to cycles through the
    lowest-numbered remaining edge (valid: in any decomposition that edge is
    either a single edge or lies on a cycle through it)."""
    EI = edge_index_table(n)
    through = {idx: [] for idx in range(len(EI))}
    for l, C in cycles:
        # pick any bit of C as representative; store for every edge of C
        mm = C
        while mm:
            b = (mm & -mm).bit_length() - 1
            through[b].append(C)
            mm &= mm - 1
    memo = {}

    def ce(E):
        if E == 0:
            return 0
        r = memo.get(E)
        if r is not None:
            return r
        if is_forest(n, E):
            r = popcount(E)
        else:
            e = (E & -E).bit_length() - 1
            r = popcount(E)
            for C in through[e]:
                if C & E == C:
                    v = 1 + ce(E & ~C)
                    if v < r:
                        r = v
        memo[E] = r
        return r

    return ce, memo

# ---------------------------------------------------------------- exact greedy worst/best

class GreedySolver:
    def __init__(self, n, cycles):
        self.n = n
        self.cycles_desc = sorted(cycles, key=lambda t: -t[0])
        self.by_len = {}
        for l, C in cycles:
            self.by_len.setdefault(l, []).append(C)
        self.memoW = {}
        self.memoB = {}
        self.nodes = 0
        self.cap = None  # node cap for exact search; None = unlimited

    def longest_cycles(self, E):
        """All longest cycles contained in E.  Returns (L, [masks])."""
        for l in sorted(self.by_len.keys(), reverse=True):
            cands = [C for C in self.by_len[l] if C & E == C]
            if cands:
                return l, cands
        return 0, []

    def _bounded(self):
        return self.cap is not None and self.nodes > self.cap

    def W(self, E):
        """greedy-worst: max pieces (exact, memoized).  Raises TimeoutError-ish
        flag if node cap exceeded (partial results kept)."""
        self.nodes += 1
        if self._bounded():
            raise RecursionError("node cap")
        r = self.memoW.get(E)
        if r is not None:
            return r
        if E == 0 or is_forest(self.n, E):
            r = popcount(E)
        else:
            L, cands = self.longest_cycles(E)
            r = 0
            for C in cands:
                v = 1 + self.W(E & ~C)
                if v > r:
                    r = v
        self.memoW[E] = r
        return r

    def B(self, E):
        self.nodes += 1
        if self._bounded():
            raise RecursionError("node cap")
        r = self.memoB.get(E)
        if r is not None:
            return r
        if E == 0 or is_forest(self.n, E):
            r = popcount(E)
        else:
            L, cands = self.longest_cycles(E)
            r = 10 ** 9
            for C in cands:
                v = 1 + self.B(E & ~C)
                if v < r:
                    r = v
        self.memoB[E] = r
        return r

    def W_sample(self, E, R, rng):
        """Lower bound on W via R random adversarial runs."""
        best = 0

        def run(E):
            pieces = 0
            while E and not is_forest(self.n, E):
                L, cands = self.longest_cycles(E)
                C = rng.choice(cands)
                pieces += 1
                E &= ~C
            return pieces + popcount(E)

        for _ in range(R):
            v = run(E)
            if v > best:
                best = v
        return best

# ---------------------------------------------------------------- graph builders

def K_n(n):
    E = 0
    EI = edge_index_table(n)
    for idx in EI.values():
        E |= 1 << idx
    return E

def K_ab(a, b):
    n = a + b
    EI = edge_index_table(n)
    E = 0
    for i in range(a):
        for j in range(a, a + b):
            E |= 1 << EI[(i, j)]
    return E

def sun(b):
    """K_3 v I_b : triangle on {0,1,2} joined to independent {3..b+2}
    (this is 'K_3 u K_{3,b}' as an edge-union on the shared 3-part)."""
    n = b + 3
    EI = edge_index_table(n)
    E = 0
    for i, j in ((0, 1), (0, 2), (1, 2)):
        E |= 1 << EI[(i, j)]
    for i in range(3):
        for j in range(3, n):
            E |= 1 << EI[(i, j)]
    return E

def disjoint_union(masks_list, offset_base=0):
    """Union of graphs given as (n_i, E_i); vertices of block t are shifted by
    sum of previous sizes."""
    E = 0
    shift = 0
    for (ni, Ei) in masks_list:
        EI = edge_index_table(ni)
        for (i, j), idx in EI.items():
            if Ei >> idx & 1:
                a, b = i + shift, j + shift
                if a > b:
                    a, b = b, a
                E |= 1 << edge_index_table(100)[(a, b)]  # cap n<=100
        shift += ni
    return E, shift

def union_mask(n_total, masks_shifted):
    m = 0
    for E in masks_shifted:
        m |= E
    return m

def shift_mask(ni, Ei, shift, n_total):
    """Copy mask Ei (on ni vertices) shifted by `shift`, into an n_total-vertex
    mask.  Uses edge_index_table(n_total) so that the result is consistent with
    every other routine on n_total vertices."""
    EI = edge_index_table(ni)
    EIbig = edge_index_table(n_total)
    out = 0
    for (i, j), idx in EI.items():
        if Ei >> idx & 1:
            a, b = i + shift, j + shift
            if a > b:
                a, b = b, a
            out |= 1 << EIbig[(a, b)]
    return out

# ---------------------------------------------------------------- certificate verifier

def verify_run(n, start_E, cycle_vertex_lists, verbose=False):
    """Independently re-check a claimed greedy run:
       each listed cycle must (a) be contained in the current graph,
       (b) be a LONGEST cycle of the current graph (no longer cycle contained),
       and the remainder must be a forest.
    Returns (pieces, leftover_edges, ok, log)."""
    cyc_masks = [(len(c), cycle_mask(n, c)) for c in cycle_vertex_lists]
    E = start_E
    pieces = 0
    log = []
    all_cycles = enumerate_cycles(n) if n <= 10 else None
    ok = True
    for (l, C) in cyc_masks:
        if C & E != C:
            ok = False
            log.append(f"FAIL: cycle {C:060b} not contained in current graph")
            break
        # longest check: no cycle of length > l contained
        if all_cycles is not None:
            longer = [cl for (cl, C2) in all_cycles if cl > l and C2 & E == C2]
            if longer:
                ok = False
                log.append(f"FAIL: a cycle of length {max(longer)} exists > {l}")
                break
        E &= ~C
        pieces += 1
        if verbose:
            log.append(f"peel length {l}: ok, remaining edges {popcount(E)}")
    left = popcount(E)
    if not is_forest(n, E):
        ok = False
        log.append("FAIL: remainder not a forest")
    log.append(f"pieces = {pieces} + leftover {left} = {pieces + left}")
    return pieces, left, ok, log

# ---------------------------------------------------------------- explicit constructions
#
# Core construction (used everywhere).  Let parts A={a_0..a_{m-1}}, B={b_0..b_{m-1}}
# of K_{m,m} (possibly shifted vertex offsets).  M_t := {a_i b_{i+t mod m}} are the
# m perfect matchings.  For each t, M_{2t} u M_{2t+1} is a 2-regular spanning
# bipartite subgraph; the map a_i -> b_{i+2t} -> a_{i-1} shows it is a SINGLE
# Hamilton cycle (orbit i -> i-1 hits all of Z_m).  Hence:
#   m even : K_{m,m} = M_0uM_1 + M_2uM_3 + ... + M_{m-2}uM_{m-1}  (m/2 Ham cycles)
#   m = 2k+1     : M_0uM_1 + ... + M_{2k-2}uM_{2k-1} (k Ham cycles) + M_{2k} (matching)
# All constructions below are edge-disjoint by construction and the pieces are
# single cycles by the orbit argument -- no external citation needed.

def matching_pair_cycle(m, t, off_a=0, off_b=None):
    """Vertex list of the Hamilton cycle M_{2t} u M_{2t+1} of K_{m,m}:
    walk a_i -M_{2t}-> b_{i+2t} -M_{2t+1}-> a_{i-1}."""
    if off_b is None:
        off_b = m
    cyc = []
    i = 0
    for _ in range(m):
        cyc.append(off_a + i)
        cyc.append(off_b + (i + 2 * t) % m)
        i = (i - 1) % m
    return cyc

def cross_ham_decomp(m, off_a=0, off_b=None):
    """m/2 edge-disjoint Hamilton cycles decomposing K_{m,m} (m even)."""
    assert m % 2 == 0
    return [matching_pair_cycle(m, t, off_a, off_b) for t in range(m // 2)]

def k_partial_cross_kcycles(k, m, off_a=0, off_b=None):
    """k edge-disjoint Hamilton cycles of K_{m,m} using matchings M_0..M_{2k-1}
    (m = 2k+1 odd here): drains every b-vertex to exactly its M_{2k} edge."""
    assert m == 2 * k + 1
    return [matching_pair_cycle(m, t, off_a, off_b) for t in range(k)]

def sun_greedy_path(b):
    """The forced greedy path on K_3 v I_b: one 6-cycle (all 3 a's + 3 b's),
    then triangle, then remainder.  Returns cycle vertex lists for the
    canonical forced prefix (b >= 4)."""
    a1, a2, a3 = 0, 1, 2
    b1, b2, b3 = 3, 4, 5
    c6 = [a1, b1, a2, b2, a3, b3]
    tri = [a1, a2, a3]
    return [c6, tri]
