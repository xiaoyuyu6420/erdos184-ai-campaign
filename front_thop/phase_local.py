#!/usr/bin/env python3
"""相位层局部搜索 (WalkSAT 风格): 约束 = 每标签对 4 事件像覆盖 Z_2^2.
随机初始化 + 迭代: 挑违反约束, 翻转其变量之一使违反度下降."""
import random, time
import search as S


def build_events(n, m_list, sol_blocks):
    events = {}
    var_of = {}
    nvars = 0
    for bi, (key, cset, solo) in enumerate(sol_blocks):
        for ci, (cyc, es) in enumerate(cset):
            for pos in range(len(cyc)):
                var_of[(bi, ci, pos)] = nvars
                nvars += 1
    for bi, (key, cset, solo) in enumerate(sol_blocks):
        for ci, (cyc, es) in enumerate(cset):
            L = len(cyc)
            for pos in range(L):
                u, v = cyc[pos], cyc[(pos + 1) % L]
                uv = (min(u, v), max(u, v))
                events.setdefault(uv, []).append((var_of[(bi, ci, pos)], var_of[(bi, ci, (pos + 1) % L)], u, v))
    return events, var_of, nvars


def viol_of(elist, assign):
    """该标签对约束的违反度 = 缺失像数 = 4 - |像集| (每事件像 (1-a,b) 或 (b,1-a))."""
    seen = set()
    for (vu, vv, u, v) in elist:
        a, b = assign[vu], assign[vv]
        seen.add((1 - a, b) if u < v else (b, 1 - a))
    return 4 - len(seen)


def phase_local(n, m_list, sol_blocks, max_seconds=120.0, seed=1):
    events, var_of, nvars = build_events(n, m_list, sol_blocks)
    elists = list(events.values())
    rng = random.Random(seed)
    assign = [rng.randint(0, 1) for _ in range(nvars)]
    t0 = time.time()

    def total_viol():
        return sum(viol_of(el, assign) for el in elists)

    cur = total_viol()
    while cur > 0 and time.time() - t0 < max_seconds:
        # 挑一个违反的约束
        bad = [el for el in elists if viol_of(el, assign) > 0]
        if not bad:
            break
        el = rng.choice(bad) if len(bad) > 1 or viol_of(bad[0], assign) > 0 else bad[0]
        # 尝试翻转该约束涉及的所有变量, 取使总违反最小的
        cands = []
        for (vu, vv, u, v) in el:
            cands.extend([vu, vv])
        best_d, best_var = None, None
        for var in set(cands):
            assign[var] ^= 1
            d = total_viol() - cur
            assign[var] ^= 1
            if best_d is None or d < best_d:
                best_d, best_var = d, var
        if best_var is None:
            break
        assign[best_var] ^= 1
        cur += best_d
        # 平原逃逸: 偶发随机翻转
        if best_d >= 0 and rng.random() < 0.3:
            var = rng.randrange(nvars)
            assign[var] ^= 1
            cur = total_viol()
    if cur == 0:
        # 从 assign 生成 seating
        def bit(bi, ci, pos):
            return assign[var_of[(bi, ci, pos)]]
        nights = []
        for bi, (key, cset, solo) in enumerate(sol_blocks):
            tables = []
            used = set()
            for ci, (cyc, es) in enumerate(cset):
                table = []
                for pos in range(len(cyc)):
                    p = cyc[pos]
                    e = bit(bi, ci, pos)
                    table.extend([2 * p + e, 2 * p + 1 - e])
                tables.append(table)
                used.update(cyc)
            for p in solo:
                tables.append([2 * p, 2 * p + 1])
                used.add(p)
            nights.append(tables)
        return nights
    return None


if __name__ == "__main__":
    import time as _t
    from verifier import verify
    from hop44 import verify2_independent
    # 目标: 粗分解已找到但相位超时的实例
    targets = [
        (10, [2, 3], "(2,3) n=10, n≡0 mod 10"),
    ]
    for (n, ml, note) in targets:
        t0 = _t.time()
        sol = S.solve(n, ml, verbose=False, time_limit=110)
        if sol is None:
            print(f"[--] {ml}@n={n} 粗分解 NOFIND")
            continue
        print(f"粗分解 OK ({_t.time()-t0:.0f}s), 相位局部搜索…")
        seating = phase_local(n, ml, sol, max_seconds=110)
        if seating is None:
            print(f"[??] {ml}@n={n} 相位局部搜索失败")
            continue
        ok1, _ = verify(n, ml, seating)
        ok2, _ = verify2_independent(n, ml, seating)
        print(f"[{'++' if ok1 and ok2 else '??'}] {ml}@n={n} gamma={len(seating)} V1={ok1} V2={ok2} ({_t.time()-t0:.0f}s) #{note}")
