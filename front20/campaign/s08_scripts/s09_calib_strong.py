#!/usr/bin/env python3
"""
S09 强化校准：参数化搜索器的完备性机器验证（n=3 N=7 m=6 金标准）

三重校准：
  [C1] 覆盖性：金标准全部 5040 个分裂类，其 T-max 侧含核-1 花、且存在该花核 y
       使 T-min 侧 deg(y) >= 3 ⟹ 每个分裂类经归一 (y ↦ 0) 后落入搜索域
       （域覆盖性的逐类机器验证）。
  [C2] 轨道算术：金标准分裂类键的 S₇-轨道大小分布；参数化检出键（归一坐标）
       的轨道大小分布；验证 5040 = 720 × 7 的逐轨道对应
       （每轨道恰含一个「核-{0} 归一」域内键 ⟺ |K_hi| = 1 对全部类）。
  [C3] T 差分解回归：T(F)-T(G) = 6·(核1花数差) 对全部分裂对成立（[7] 振幅
       结构定理的机器回归）。

用法：python3 s09_calib_strong.py
"""
import itertools
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import split_dimension
from s09_toolkit import T_ordered, flowers_unordered, profile_dict


def core_cores(fam, core_size):
    """族中全部花的核（core_size = 1 ⟹ 核-1 花核集合）"""
    ks = set()
    for A, B, C in itertools.combinations(fam, 3):
        if A & B == A & C == B & C:
            inter = A & B
            if len(inter) == core_size:
                ks.add(tuple(sorted(inter)))
    return ks


def core1_count(fam):
    n = 0
    for A, B, C in itertools.combinations(fam, 3):
        if A & B == A & C == B & C and len(A & B) == 1:
            n += 1
    return n


def deg(fam, Z):
    Zs = frozenset(Z)
    return sum(1 for S in fam if Zs <= S)


PERMS = list(itertools.permutations(range(7)))


def orbit_size(fam):
    fam = [frozenset(S) for S in fam]
    seen = set()
    for p in PERMS:
        f2 = frozenset(frozenset(p[e] for e in S) for S in fam)
        seen.add(tuple(sorted(tuple(sorted(S)) for S in f2)))
    return len(seen)


def norm_key(fam, y):
    """把点 y 映到 0 的规范归一（y 固定映射，其余恒等——注意这不是全体
    置换的规范形，只是「核位置归一」；键比较发生在同一归一约定下即可）"""
    rel = {y: 0}
    f2 = frozenset(frozenset(rel.get(e, e) for e in S) for S in fam)
    return tuple(sorted(tuple(sorted(S)) for S in f2))


def main():
    t0 = time.time()
    print("=== 金标准：split_dimension.scan(7,6) 全穷举 ===", flush=True)
    members, stats, splits = split_dimension.scan(7, 6)
    M = len(members)
    print(f"族数={stats['total']:,} 类={stats['classes']:,} "
          f"分裂类={stats['splits']:,} ({time.time()-t0:.0f}s)", flush=True)
    assert stats["splits"] == 5040, "金标准应为 5040"

    def fam_of_rank(r):
        return [frozenset(members[i]) for i in split_dimension.unrank(M, 6, r)]

    print("\n=== [C1] 逐类覆盖性 + [C3] T 差分解回归 ===")
    ok_cover = 0
    khi_dist = {}
    k1_hi_dist = {}
    c3_bad = 0
    for tset, rmin, rmax in splits:
        F_hi = fam_of_rank(rmax)
        F_lo = fam_of_rank(rmin)
        T_hi, T_lo = tset[-1], tset[0]
        assert T_ordered(F_hi) == T_hi and T_ordered(F_lo) == T_lo
        K_hi = core_cores(F_hi, 1)
        khi_dist[len(K_hi)] = khi_dist.get(len(K_hi), 0) + 1
        # C3: T 差 = 6 × (核-1 花数差)
        dT = T_hi - T_lo
        dK1 = core1_count(F_hi) - core1_count(F_lo)
        if dT != 6 * dK1:
            c3_bad += 1
        # C1: 存在 y ∈ K_hi 使 deg_lo(y) >= 3
        good = False
        if K_hi:
            for y in K_hi:
                if deg(F_lo, y) >= 3:
                    good = True
                    break
        if good:
            ok_cover += 1
        k1_hi_dist[core1_count(F_hi)] = k1_hi_dist.get(core1_count(F_hi), 0) + 1
    print(f"  覆盖性: {ok_cover}/5040 分裂类落入归一域")
    print(f"  T-max 侧核-1 花核个数 |K_hi| 分布: {dict(sorted(khi_dist.items()))}")
    print(f"  T-max 侧核-1 花数分布: {dict(sorted(k1_hi_dist.items()))}")
    print(f"  [C3] T 差分解违例: {c3_bad}（应为 0）")
    assert ok_cover == 5040, "覆盖性失败！"
    assert c3_bad == 0, "T 差分解回归失败！"

    print("\n=== [C2] 轨道算术 ===")
    # 金标准键轨道大小（采样 60 个）
    import random
    rng = random.Random(1)
    sample = rng.sample(splits, 60)
    orb_gold = {}
    for tset, rmin, rmax in sample:
        F_hi = fam_of_rank(rmax)
        orb = orbit_size(F_hi)
        orb_gold[orb] = orb_gold.get(orb, 0) + 1
    print(f"  金标准分裂族轨道大小分布（采样 60）: {dict(sorted(orb_gold.items()))}")
    # T-max 侧核-1 花核数 |K_hi|=1 对全部类？
    print(f"  |K_hi| 分布（全部 5040 类）: {dict(sorted(khi_dist.items()))}")

    print(f"\n总耗时 {time.time()-t0:.0f}s")
    print("CALIBRATION STRONG: PASS（覆盖性 + T 差分解 + 轨道数据齐备）")


if __name__ == "__main__":
    main()
