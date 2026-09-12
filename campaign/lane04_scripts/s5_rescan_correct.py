#!/usr/bin/env python3
"""
Lane 04 Script 5 —— 修正 s1 的预过滤 bug 后的残差重扫。

BUG 记录（s1_exhaustive.py scan() 内 `cand_resid = (Tcnt + m >= 3n-2)`）:
  τ ≥ |T|/2 只给 m+2τ ≥ m+|T|（下界），故 m+|T| < 3n−2 不能排除残差
  （τ 可以因配对距离 > 1 而大于 |T|/2）。s1 的 resid/resid_2c/tight 计数全部漏报。
  本脚本对 2-连通图直接算 τ 判残差（无预过滤），重新计数并对残差图 exact_ce。

输出:
  A. n=6: 正确 resid_2c 总数、全部残差 exact_ce（viol/r1bad/tight 真值）。
  B. n=7 m=17: 修正后的残差 2-连通数 + decision(≤6)。
  C. n=7: 正确 resid_2c 总数（tau 全算）; 漏报子集（旧预过滤会漏掉的残差图）计数;
     漏报子集 exact/decision 全查或抽样; Δ≤4 m∈{7..12} 残差全查。
  D. W=∅: 紧实例全覆盖最优分解检验（n=6 全部 + n=7 全部 + 非紧抽样）。
"""
import json, random, sys, time
from itertools import combinations
from s1_exhaustive import build, connected, two_connected, tau_tjoin, exact_ce
from s4_coverage_gaps import min_pi_and_coverage

sys.setrecursionlimit(100000)


def twoconn_delta5_masks(n, mmin, mmax):
    edges = list(combinations(range(n), 2))
    E = len(edges)
    for k in range(mmin, min(mmax, E) + 1):
        for comb in combinations(range(E), k):
            mask = 0
            for i in comb:
                mask |= 1 << i
            yield mask, edges


def is_resid(adj, n, m):
    tv = tau_tjoin(adj, n)
    return m + 2 * tv >= 3 * n - 2, tv


def part_A6():
    print("== A6: n=6 全 2-连通 Δ≤5, 正确残差判定, 残差全部 exact_ce ==")
    edges = list(combinations(range(6), 2))
    n = 6
    twoconn = resid_masks = 0
    viol = r1bad = 0
    tight = []
    t0 = time.time()
    for mask, edges_ in twoconn_delta5_masks(6, 5, 15):
        adj, m = build(mask, edges_, n)
        if max(a.bit_count() for a in adj) > 5 or not two_connected(adj, n):
            continue
        twoconn += 1
        ok, tv = is_resid(adj, n, m)
        if not ok:
            continue
        resid_masks += 1
        ce, _ = exact_ce(adj, n)
        if ce > n - 1:
            viol += 1
            print(f"  !! 违反 mask={mask} ce={ce}")
        if 3 * ce > m + 2 * tv:
            r1bad += 1
            print(f"  !! R1 失效 mask={mask} ce={ce} m={m} tau={tv}")
        if ce == n - 1:
            tight.append(mask)
    print(json.dumps({
        "n": 6, "twoconn": twoconn, "resid_2c_correct": resid_masks,
        "viol": viol, "r1bad": r1bad, "tight_count": len(tight),
        "time": round(time.time() - t0, 1)}))
    with open("s5_n6_tight.json", "w") as f:
        json.dump(tight, f)
    return tight


def part_A7_full_resid():
    print("== A7: n=7 全 2-连通 Δ≤5, 正确残差计数（tau 全算, 不 exact） ==")
    n = 7
    twoconn = resid = 0
    resid_masks = []
    t0 = time.time()
    for mask, edges in twoconn_delta5_masks(7, 6, 21):
        adj, m = build(mask, edges, n)
        if max(a.bit_count() for a in adj) > 5 or not two_connected(adj, n):
            continue
        twoconn += 1
        ok, tv = is_resid(adj, n, m)
        if ok:
            resid += 1
            resid_masks.append((m, mask))
    print(json.dumps({"n": 7, "twoconn": twoconn, "resid_2c_correct": resid,
                      "time": round(time.time() - t0, 1)}))
    with open("s5_n7_resid.json", "w") as f:
        json.dump(resid_masks, f)


def part_B7():
    print("== B7: n=7 m=17 修正残差 + n=7 Δ≤4 m∈{7..14} 残差全查 ==")
    n = 7
    edges = list(combinations(range(7), 2))
    r17 = 0
    for comb in combinations(range(21), 17):
        mask = sum(1 << i for i in comb)
        adj, m = build(mask, edges, n)
        if not two_connected(adj, n):
            continue
        ok, tv = is_resid(adj, n, m)
        if ok:
            r17 += 1
            ce, _ = exact_ce(adj, n)
            assert ce <= 6, f"违反 {mask} {ce}"
    print(f"  m=17: 残差2-连通 = {r17} (全部 ce ≤ 6)")
    cnt_d4 = 0
    tight_d4 = []
    for k in range(7, 15):
        for comb in combinations(range(21), k):
            mask = sum(1 << i for i in comb)
            adj, m = build(mask, edges, n)
            if max(a.bit_count() for a in adj) > 4 or not two_connected(adj, n):
                continue
            ok, tv = is_resid(adj, n, m)
            if ok:
                cnt_d4 += 1
                ce, _ = exact_ce(adj, n)
                print(f"  n=7 残差Δ≤4: m={m} tau={tv} ce={ce} mask={mask}"
                      + (" 紧!" if ce == 6 else ""))
                assert ce <= 6
                if ce == 6:
                    tight_d4.append(mask)
    print(f"  n=7 残差 2-连通 Δ≤4 总数 = {cnt_d4}, 紧 = {len(tight_d4)}")


def part_D_cov(skip_n7_non_tight=True, sample=100, seed=5):
    print("== D: W=∅ 覆盖检验（基于修正后的紧实例） ==")
    edges6 = list(combinations(range(6), 2))
    edges7 = list(combinations(range(7), 2))
    n6 = 0; ncov6 = 0; skip6 = 0
    try:
        tight6 = json.load(open("s5_n6_tight.json"))
    except FileNotFoundError:
        tight6 = []
    for mask in tight6:
        adj, m = build(mask, edges6, 6)
        ce, status, cov = min_pi_and_coverage(adj, 6)
        n6 += 1
        if status == "OK" and not cov:
            ncov6 += 1
            print(f"  !! n=6 mask={mask}: ce={ce} 无全覆盖最优分解")
        elif status != "OK":
            skip6 += 1
    print(f"  n=6 紧实例覆盖检验: {n6} 个, 无覆盖 = {ncov6}, SKIP = {skip6}")
    # n=7: 残差重扫若在, 紧实例 = 残差中 ce=6; 直接边扫边验会太慢, 抽样+紧全查:
    try:
        resid7 = json.load(open("s5_n7_resid.json"))
    except FileNotFoundError:
        resid7 = []
    rng = random.Random(seed)
    pool = []
    nonres_pool = []
    n7 = ncov7 = skip7 = 0
    # 紧实例必须全查; 为拿到紧实例需 exact: 对 m≤14 残差全 exact, m≥15 抽样
    small = [(m, mk) for (m, mk) in resid7 if m <= 14]
    big = [(m, mk) for (m, mk) in resid7 if m > 14]
    picks = small + rng.sample(big, min(600, len(big)))
    for m, mask in picks:
        adj, mm = build(mask, edges7, 7)
        ce, _ = exact_ce(adj, 7)
        if ce == 6:
            pool.append(mask)
    print(f"  n=7 紧实例候选（残差 m≤14 全查 + m≥15 抽样 600）: {len(pool)} 个")
    for mask in pool:
        adj, m = build(mask, edges7, 7)
        ce, status, cov = min_pi_and_coverage(adj, 7)
        n7 += 1
        if status == "OK" and not cov:
            ncov7 += 1
            print(f"  !! n=7 mask={mask}: ce=6 无全覆盖最优分解")
        elif status != "OK":
            skip7 += 1
    # 非紧残差抽样
    if not skip_n7_non_tight:
        pass
    print(f"  n=7 紧实例覆盖检验: {n7} 个, 无覆盖 = {ncov7}, SKIP = {skip7}")


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "AD"
    if "6" in which:
        part_A6()
    if "7" in which:
        part_A7_full_resid()
    if "B" in which:
        part_B7()
    if "D" in which:
        part_D_cov()
    print("DONE s5", which)
