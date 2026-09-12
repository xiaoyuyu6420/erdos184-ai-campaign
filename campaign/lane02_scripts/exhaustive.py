"""
exhaustive.py -- exhaustive computation of c(H) over ALL Eulerian simple graphs
on n vertices, for n = 3..8 (labeled; sup over labeled = sup over unlabeled).

Bijection used: even (all-even-degree) graphs on n labeled vertices correspond
bijectively to arbitrary graphs on the FIRST n-1 vertices (edges incident to
vertex n-1 are forced by parity; handshake parity makes it consistent).
Hence exactly 2^((n-1)(n-2)/2) even labeled graphs:
    n=3: 2    n=4: 8    n=5: 64    n=6: 1024    n=7: 32768    n=8: 2097152

For each graph: exact minimum cycle decomposition c(H) (components split,
per-component cache), Hajos check c(H) <= floor((n-1)/2).
Outputs out/exhaustive.json.
"""
import json, sys, time
from math import ceil
from lib_cycles import min_cycle_decomp


def run_n(n):
    t0 = time.time()
    k = n - 1
    # canonical edge table of K_n
    can = [(u, v) for u in range(n) for v in range(u + 1, n)]
    idx = {e: i for i, e in enumerate(can)}
    base = [(u, v) for u in range(k) for v in range(u + 1, k)]
    base_idx = [idx[e] for e in base]
    lastrow_idx = [idx[(u, k)] for u in range(k)]

    stats = {"n": n, "count": 0, "max_c": 0, "max_ratio": 0.0,
             "achieved_bound": 0, "violations": [], "achievers": [],
             "max_c_core": 0, "core_achiever": None, "c_histogram": {},
             "counting_tight": 0, "solved_fresh": 0}
    cache = {}
    full = (1 << n) - 1

    for mask in range(1 << len(base)):
        adj = [0] * n
        emask = 0
        mm = mask
        while mm:
            b = mm & -mm
            mm ^= b
            u, v = base[b.bit_length() - 1]
            adj[u] |= 1 << v
            adj[v] |= 1 << u
        lastmask = 0
        for u in range(k):
            if bin(adj[u]).count("1") & 1:
                adj[u] |= 1 << k
                adj[k] |= 1 << u
                lastmask |= 1 << u
        # canonical edge-index bitmask for the whole graph
        emask = 0
        mm = mask
        while mm:
            b = mm & -mm
            mm ^= b
            emask |= 1 << base_idx[b.bit_length() - 1]
        lm = lastmask
        while lm:
            b = lm & -lm
            lm ^= b
            emask |= 1 << lastrow_idx[b.bit_length() - 1]

        # components (nontrivial only)
        comps = []
        seen = 0
        while seen != full:
            rest = (~seen) & full
            v0 = (rest & -rest).bit_length() - 1
            comp = 0
            frontier = 1 << v0
            while frontier:
                comp |= frontier
                nxt = 0
                f = frontier
                while f:
                    bb = f & -f
                    f ^= bb
                    nxt |= adj[bb.bit_length() - 1]
                frontier = nxt & ~comp
            seen |= comp
            if bin(comp).count("1") > 1:
                comps.append(comp)

        total_c = 0
        mtotal = 0
        has_d2 = False
        core_flag = False
        comp_masks = []
        for cv in comps:
            # component edge bitmask over canonical indices
            cem = 0
            mm = emask
            while mm:
                b = mm & -mm
                mm ^= b
                u, v = can[b.bit_length() - 1]
                if (cv >> u) & 1:
                    cem |= b
            du = {}
            mm = cem
            while mm:
                b = mm & -mm
                mm ^= b
                u, v = can[b.bit_length() - 1]
                du[u] = du.get(u, 0) + 1
                du[v] = du.get(v, 0) + 1
            mtotal += bin(cem).count("1")
            if 2 in du.values():
                has_d2 = True
            if any(x >= 4 for x in du.values()):
                core_flag = True
            key = cem
            if key in cache:
                c = cache[key]
            else:
                cn = max(v for v in range(n) if (cv >> v) & 1) + 1
                ce = [can[i] for i in bits(cem)]
                c, _, proven = min_cycle_decomp(cn, ce)
                assert proven, "node limit exceeded"
                cache[key] = c
                stats["solved_fresh"] += 1
            total_c += c
            comp_masks.append((cem, c))

        stats["count"] += 1
        bound = (n - 1) // 2
        stats["c_histogram"][total_c] = stats["c_histogram"].get(total_c, 0) + 1
        if total_c > bound:
            stats["violations"].append(
                {"n": n, "edges": [can[i] for i in bits(emask)],
                 "c": total_c})
        if total_c > stats["max_c"]:
            stats["max_c"] = total_c
            stats["achievers"] = [{"n": n, "c": total_c, "ratio": total_c / n,
                                   "edges": [can[i] for i in bits(emask)]}]
        elif total_c == stats["max_c"] and len(stats["achievers"]) < 8:
            stats["achievers"].append(
                {"n": n, "c": total_c, "ratio": total_c / n,
                 "edges": [can[i] for i in bits(emask)]})
        stats["max_ratio"] = max(stats["max_ratio"], total_c / n)
        if total_c == bound:
            stats["achieved_bound"] += 1
        if total_c and total_c == ceil(mtotal / n):
            stats["counting_tight"] += 1
        if core_flag and not has_d2 and total_c > stats["max_c_core"]:
            stats["max_c_core"] = total_c
            stats["core_achiever"] = {
                "n": n, "c": total_c,
                "edges": [can[i] for i in bits(emask)]}
    stats["time_s"] = round(time.time() - t0, 1)
    return stats


def bits(mask):
    while mask:
        b = mask & -mask
        mask ^= b
        yield b.bit_length() - 1


if __name__ == "__main__":
    ns = [int(x) for x in sys.argv[1:]] or [3, 4, 5, 6, 7]
    out = {"summary": []}
    for n in ns:
        s = run_n(n)
        out["summary"] = [x for x in out["summary"] if x["n"] != n] + [s]
        print(f"n={n}: graphs={s['count']} distinct_solved={s['solved_fresh']} "
              f"max_c={s['max_c']} max_ratio={s['max_ratio']:.4f} "
              f"floor((n-1)/2)={(n-1)//2} achieved_bound={s['achieved_bound']} "
              f"VIOLATIONS={len(s['violations'])} counting_tight={s['counting_tight']} "
              f"max_c_core(delta>=4)={s['max_c_core']} time={s['time_s']}s",
              flush=True)
        for a in s["achievers"][:6]:
            print(f"    achiever c={a['c']}/{a['n']}: {a['edges']}")
        if s["violations"]:
            print("    *** VIOLATIONS FOUND ***", s["violations"][:3])
        json.dump(out, open("out/exhaustive.json", "w"), indent=1)
    print("saved out/exhaustive.json")
