#!/usr/bin/env python3
"""s6: n=7 修正残差集中被 s1 预过滤漏报的子集的 ce<=6 复查。
判定策略: 先用最近圈贪心构造分解 (得到上界 ub); ub<=6 直接 PASS;
否则 exact_ce。统计 PASS/FAIL/EXACT。"""
import json, sys, time
from itertools import combinations
from s1_exhaustive import build, two_connected, tau_tjoin, exact_ce, all_cycles_em

sys.setrecursionlimit(100000)

def greedy_ub(adj, n):
    """最近圈贪心: 反复取覆盖最低未盖边的最长圈。返回件数上界。"""
    packed = []
    for u in range(n):
        nb = adj[u]
        while nb:
            b = (nb & -nb).bit_length()-1; nb &= nb-1
            if b > u: packed.append((u, b))
    m = len(packed)
    eid = {e: i for i, e in enumerate(packed)}
    cyc = all_cycles_em(adj, n, eid)
    full = (1 << m) - 1
    mask = full
    parts = 0
    while mask:
        best_em = 0
        # 找与 mask 相交于最低边的最长圈
        low = (mask & -mask).bit_length() - 1
        for em in cyc:
            if (em & mask) and (em >> low) & 1:
                if em.bit_count() > best_em.bit_count():
                    best_em = em
        if best_em:
            mask &= ~best_em
            parts += 1
        else:
            parts += mask.bit_count()
            mask = 0
    return parts

def main():
    txt = open("s1_n7_out.txt").read()
    s1 = json.JSONDecoder().raw_decode(txt)[0]
    checked_old = set(s1["tight"])  # s1 只对 exact_plan 做了检查, 但没存 plan; 用 tight 无法还原
    # 保守: 重算 s1 的漏报判定 = 真残差 且 |T|+m < 19
    edges = list(combinations(range(7), 2))
    resid = json.load(open("s5_n7_resid.json"))
    t0 = time.time()
    missed = 0; passed = 0; exacted = 0; fail = 0
    for m, mask in resid:
        adj, mm = build(mask, edges, 7)
        Tcnt = sum(1 for v in range(7) if adj[v].bit_count() & 1)
        if Tcnt + m >= 19:
            continue  # s1 也检查过的
        missed += 1
        ub = greedy_ub(adj, 7)
        if ub <= 6:
            passed += 1
            continue
        ce, _ = exact_ce(adj, 7)
        exacted += 1
        if ce > 6:
            fail += 1
            print(f"  !! 违反: mask={mask} ce={ce}")
        if time.time() - t0 > 1500:
            print(f"  (时间截断 at missed={missed})")
            break
    print(json.dumps(dict(missed=missed, greedy_pass=passed, exact_run=exacted, viol=fail,
                          time=round(time.time()-t0, 1))))

if __name__ == "__main__":
    main()
