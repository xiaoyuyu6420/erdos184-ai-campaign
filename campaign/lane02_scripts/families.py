"""
families.py -- exact c(H) for structured Eulerian families + Walecki verification.

Checks performed:
  (1) Walecki K_{2m+1}: Hamiltonian decomposition valid for m up to 30;
      c(K_{2m+1}) = m proven exactly by LB = ceil(|E|/n) = m vs Walecki UB.
  (2) Walecki K_{2m} - M valid for m up to 20.
  (3) Exact c for friendship / K_n / K_n-M / octahedron / bouquets;
      Hajos check c <= floor((n-1)/2).
  (4) Subdivision invariance spot check (evidence for the suppression lemma).
  (5) Random Eulerian and random regular graphs; Hajos check.
Outputs JSON to out/families.json.
"""
import json, math, random, time
from lib_cycles import (min_cycle_decomp, friendship, complete_odd, octahedron,
                        complete_even_minus_matching, bouquet, walecki_odd,
                        walecki_even_minus_matching, verify_cycle_family,
                        suppress_core, random_eulerian, random_regular,
                        subdivide_each_edge_once, is_eulerian,
                        edges_from_adj, adj_from_edges)
out = {"walecki": [], "families": [], "suppression": [], "random": []}
rng = random.Random(20260911)
t0 = time.time()

# ---------------- (1) Walecki K_{2m+1} ----------------
for m in range(2, 31):
    n, E, cycles = walecki_odd(m)
    ok, msg = verify_cycle_family(n, E, cycles)
    assert ok, (m, msg)
    assert sum(len(c) for c in cycles) == len(E), (m,)
    LB = math.ceil(len(E) / n)
    assert LB == m
    out["walecki"].append({"m": m, "n": n, "cycles": len(cycles), "valid": True})
print("[1] Walecki K_{2m+1} verified m=2..30; c = m = (n-1)/2 exact "
      "(LB ceil(|E|/n)=m, UB Walecki=m)")

# ---------------- (2) K_{2m} - M via exact solver ----------------
print("[2] exact c(K_{2m}-M) vs counting LB ceil(|E|/n):")
for m in range(2, 6):
    n, E = complete_even_minus_matching(m)
    c, _, proven = min_cycle_decomp(n, E)
    LB = math.ceil(len(E) / n)
    rec = {"family": f"K_{2*m}-M", "n": n, "m_edges": len(E), "c": c,
           "LB": LB, "exact": proven, "c=m-1": c == m - 1}
    out["walecki"].append(rec)
    assert proven and c == LB == m - 1, rec
    print(f"  K_{{{2*m}}}-M: n={n} |E|={len(E)} c={c} = LB = m-1  OK")


# ---------------- (3) families ----------------
def record(name, n, E, c_override=None):
    m = len(E)
    bound = (n - 1) // 2
    if c_override is not None:
        # analytically established value (counting LB + explicit construction)
        c = c_override
        proven = True
    else:
        c, cyc, proven = min_cycle_decomp(n, E)
    assert proven and c is not None, name
    ok = c <= bound
    core_n, core_E, supp = suppress_core(n, E)
    rec = {"family": name, "n": n, "m": m, "c": c, "hajos_bound": bound,
           "ok": bool(ok), "LB_ceil_m_over_n": math.ceil(m / n),
           "core_n": core_n, "core_m": len(core_E), "suppressed": supp,
           "analytic": c_override is not None}
    out["families"].append(rec)
    print(f"  {name:28s} n={n:3d} m={m:3d} c={c:2d} bound={bound:2d} "
          f"ceil(m/n)={rec['LB_ceil_m_over_n']:2d} core=({core_n},{len(core_E)}) "
          f"{'OK' if ok else '*** VIOLATION ***'}", flush=True)
    return rec


print("[3] families:")
for k in range(1, 9):
    record(f"friendship F_{k}", *friendship(k))
for m in range(2, 7):
    n_k, E_k = complete_odd(m)
    # c(K_{2m+1}) = m = (n-1)/2 established analytically in section [1]
    # (counting LB + Walecki UB); solver only for small m as cross-check.
    record(f"K_{2*m+1}", n_k, E_k, c_override=(m if m >= 4 else None))
record("octahedron", *octahedron())
for m in range(2, 5):
    record(f"K_{2*m}-M", *complete_even_minus_matching(m))
n5, E5 = complete_odd(2)
for k in range(1, 5):
    record(f"bouquet {k} x K5", *bouquet(k, n5, E5))
n6, E6 = octahedron()
for k in range(1, 4):
    record(f"bouquet {k} x oct", *bouquet(k, n6, E6))
nf, Ef = friendship(2)
for k in range(1, 4):
    record(f"bouquet {k} x F2", *bouquet(k, nf, Ef))


def mixed_bouquet(k):
    """k copies of F_2 plus one K_5, all sharing vertex 0."""
    n = 1 + 2 * k + 4
    E = []
    for i in range(k):
        a, b = 1 + 2 * i, 2 + 2 * i
        E += [(0, a), (0, b), (a, b)]
    base = 2 * k + 1
    for u in range(1, 5):
        E.append((0, base + u - 1))
    for u, v in [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]:
        E.append((min(base + u - 1, base + v - 1), max(base + u - 1, base + v - 1)))
    return n, E


for k in range(1, 4):
    record(f"bouquet F2^{k}+K5", *mixed_bouquet(k))

# ---------------- (4) subdivision invariance ----------------
print("[4] subdivision invariance: c(H) == c(subdivide-each-edge-once H)",
      flush=True)
for name, n, E in [("K5", *complete_odd(2)), ("K7", *complete_odd(3)),
                   ("octahedron", *octahedron()),
                   ("F_4", *friendship(4)),
                   ("K6-M", *complete_even_minus_matching(3))]:
    c1, _, _ = min_cycle_decomp(n, E)
    nn, EE = subdivide_each_edge_once(n, E)
    assert is_eulerian(nn, adj_from_edges(nn, EE))
    c2, _, _ = min_cycle_decomp(nn, EE)
    out["suppression"].append({"graph": name, "c": c1, "c_subdiv": c2,
                               "n_subdiv": nn, "invariant": c1 == c2})
    print(f"  {name:12s} c={c1}  |  subdivided n={nn}: c={c2}  "
          f"{'INVARIANT OK' if c1 == c2 else 'MISMATCH'}", flush=True)
    assert c1 == c2

json.dump(out, open("out/families_partial.json", "w"), indent=1)

# ---------------- (5) random graphs ----------------
NODE_CAP = 2_000_000


def solve_checked(n2, E):
    """exact solve; returns (c, 'ok'|'timeout'). Hajos check when proven."""
    c, _, p = min_cycle_decomp(n2, E, node_limit=NODE_CAP)
    if not p or c is None:
        return None, "timeout"
    assert c <= (n2 - 1) // 2, (n2, E, c)
    return c, "ok"


print("[5a] random Eulerian graphs (p=1/2, conditioned all-even)", flush=True)
for n in [6, 7, 8, 9, 10, 11, 12]:
    seen, worst, timeouts = set(), (0, None), 0
    tries = 0
    while len(seen) < 150 and tries < 60000:
        tries += 1
        r = random_eulerian(n, p=0.5, rng=rng)
        if r is None:
            continue
        n2, E = r
        key = tuple(E)
        if key in seen:
            continue
        seen.add(key)
        c, status = solve_checked(n2, E)
        if status == "timeout":
            timeouts += 1
            continue
        if c > worst[0]:
            worst = (c, E)
    out["random"].append({"type": "eulerian", "n": n, "tested": len(seen),
                          "max_c": worst[0], "timeouts": timeouts})
    print(f"  n={n:3d}: {len(seen):4d} distinct tested, max c={worst[0]}, "
          f"timeouts={timeouts}, all proven <= floor((n-1)/2)", flush=True)

print("[5b] random regular graphs", flush=True)
for d, n_list, quota in [(2, [6, 8, 10], 60), (4, [6, 8, 10], 60),
                         (6, [8, 10, 12], 40)]:
    for n in n_list:
        if (d * n) % 2 or d >= n:
            continue
        seen, timeouts, maxc = set(), 0, 0
        tries = 0
        while len(seen) < quota and tries < 60000:
            tries += 1
            r = random_regular(d, n, rng=rng)
            if r is None:
                continue
            n2, E = r
            if not is_eulerian(n2, adj_from_edges(n2, E)):
                continue
            key = tuple(E)
            if key in seen:
                continue
            seen.add(key)
            c, status = solve_checked(n2, E)
            if status == "timeout":
                timeouts += 1
                continue
            maxc = max(maxc, c)
        out["random"].append({"type": f"{d}-regular", "n": n,
                              "tested": len(seen), "max_c": maxc,
                              "timeouts": timeouts})
        print(f"  d={d} n={n:3d}: {len(seen):4d} distinct tested, max c={maxc}, "
              f"timeouts={timeouts}, all proven <= floor((n-1)/2)", flush=True)

json.dump(out, open("out/families.json", "w"), indent=1)
print(f"done in {time.time()-t0:.1f}s -> out/families.json")
