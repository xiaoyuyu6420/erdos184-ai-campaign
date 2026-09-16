#!/usr/bin/env python3
"""
S-08 数值验证 4（收尾轮）：通用 (n, N, m) 分裂直搜——两遍法

第一遍：穷举 C(M, m) 个族（M = C(N,n)），向量化计算
  - T = 6 × #花三元组（成员掩码位运算）
  - 粗键 = levels 1,2 的 deg 打包（N + C(N,2) 字节 ⟹ uint64 列）
第二遍：粗键同组内 T 有极差的组 ⟹ 组内精确比较全剖面（levels 1..n-1）
  ⟹ 真分裂（全剖面同、T 异）与假分裂（仅粗键同）分别计数。

用途：
 (a) n=5, N=9, m=4：μ(5) = 9 判定（§10.1(a) 直搜）。
 (b) n=3, N=9, m=4：命题 E2 的核-0 缺口机器封死（核-0 花需 N ≥ 9）。

用法：python3 general_scan.py <n> <N> <m>
"""
import itertools
import sys
import numpy as np


def build_env(N, n):
    members = list(itertools.combinations(range(N), n))
    M = len(members)
    mvec = [sum(1 << e for e in mem) for mem in members]
    fedges = []
    for (i, si), (j, sj), (k, sk) in itertools.combinations(
            ((i, mvec[i]) for i in range(M)), 3):
        if (si & sj) == (si & sk) == (sj & sk):
            fedges.append((i, j, k))
    return members, mvec, fedges


def exact_profile_key(fam_mask_bits, Zbits, n):
    """fam: tuple of member bitmasks (python ints)；返回 levels 1..n-1 全 deg 字节串"""
    out = bytearray()
    for zb in Zbits:
        out.append(sum(1 for mb in fam_mask_bits if zb & mb == zb))
    return bytes(out)


def scan_general(N, n, m, exact_on_candidate=True):
    members, mvec, fedges = build_env(N, n)
    M = len(members)
    total = __import__("math").comb(M, m)
    print(f"[n={n} N={N} m={m}] M={M} members, {len(fedges)} flower-edges, "
          f"{total:,} families", flush=True)

    # levels 1..n-1 的 Z 及其位掩码
    Zs, Zbits = [], []
    for r in range(1, n):
        for Z in itertools.combinations(range(N), r):
            Zs.append(Z)
            Zbits.append(sum(1 << e for e in Z))
    nZ = len(Zs)
    n12 = N + N * (N - 1) // 2          # levels 1,2 点数（粗键）
    if n == 3:
        n12 = nZ                        # n=3 时粗键即全键
    assert n12 <= nZ
    ncols = (n12 + 7) // 8

    # 常量数组
    Zb12 = np.array([sum(1 << e for e in Z) for Z in Zs[:n12]], dtype=np.uint64)
    mvec_arr = np.array(mvec, dtype=np.uint64)

    gen = itertools.combinations(range(M), m)
    CH = 1_000_000
    kcols = [np.zeros(0, dtype=np.uint64) for _ in range(ncols)]
    Tall = np.zeros(0, dtype=np.int64)
    rank0 = 0
    done = 0
    while done < total:
        cnt = min(CH, total - done)
        chunk = np.fromiter(itertools.chain.from_iterable(
            itertools.islice(gen, cnt)), dtype=np.int64, count=cnt * m
        ).reshape(cnt, m)
        # T：C(m,3) 个成员三元组逐一检查（m 小，至多 C(4,3) = 4 或 C(5,3) = 10 项）
        vecs = [mvec_arr[chunk[:, j]] for j in range(m)]       # m 个 (cnt,) uint64
        t = np.zeros(cnt, dtype=np.int64)
        for (i1, i2, i3) in itertools.combinations(range(m), 3):
            s1, s2, s3 = vecs[i1], vecs[i2], vecs[i3]
            t += (((s1 & s2) == (s1 & s3)) & ((s1 & s2) == (s2 & s3))).astype(np.int64)
        # 粗键 deg 打包
        mats = [((vecs[j][:, None] & Zb12[None, :]) == Zb12[None, :]).astype(np.uint8)
                for j in range(m)]
        deg = np.zeros((cnt, n12), dtype=np.uint8)
        for j in range(m):
            deg += mats[j]
        # 打包为 ncols 列 uint64（每字节一 deg）
        newcols = [np.zeros(cnt, dtype=np.uint64) for _ in range(ncols)]
        for p in range(ncols):
            for off in range(8):
                idx = p * 8 + off
                if idx < n12:
                    newcols[p] |= deg[:, idx].astype(np.uint64) << np.uint64(8 * off)
        if done == 0:
            kcols = newcols
        else:
            kcols = [np.concatenate([kcols[p], newcols[p]]) for p in range(ncols)]
        Tall = np.concatenate([Tall, 6 * t])
        done += cnt
        if done % 2_000_000 < CH:
            print(f"  ... {done:,}/{total:,}", flush=True)

    # 分组：全粗键相同 = 各列皆同
    order = np.lexsort(tuple(reversed(kcols)))
    Ks = [k[order] for k in kcols]
    sT = Tall[order]
    same = np.ones(len(sT), dtype=bool)
    same[0] = False
    same[1:] = np.all([Ks[p][1:] == Ks[p][:-1] for p in range(ncols)], axis=0)
    starts = np.flatnonzero(~same)
    seg_ends = np.append(starts[1:], len(sT))
    gmin = np.minimum.reduceat(sT, starts)
    gmax = np.maximum.reduceat(sT, starts)
    cand = np.flatnonzero(gmin != gmax)
    print(f"  classes(coarse)={len(starts):,}, candidate T-split(coarse)={len(cand)}",
          flush=True)

    real_splits = []
    if exact_on_candidate and n > 3:
        from math import comb
        for gi in cand:
            s0, s1 = int(starts[gi]), int(seg_ends[gi])
            fams = []
            for row in range(s0, s1):
                rank = int(order[row])
                fams.append((unrank(M, m, rank), sT[row], rank))
            for (f1, t1, r1), (f2, t2, r2) in itertools.combinations(fams, 2):
                if t1 == t2:
                    continue
                mb1 = [sum(1 << e for e in members[i]) for i in f1]
                mb2 = [sum(1 << e for e in members[i]) for i in f2]
                if exact_profile_key(mb1, Zbits, n) == exact_profile_key(mb2, Zbits, n):
                    real_splits.append((f1, t1, f2, t2, r1, r2))
        print(f"  REAL splits (exact profile) = {len(real_splits)}", flush=True)
    elif n == 3:
        for gi in cand:
            s0, s1 = int(starts[gi]), int(seg_ends[gi])
            real_splits.append((unrank(M, m, int(order[s0])), int(sT[s0]),
                                unrank(M, m, int(order[s0 + 1])), int(sT[s0 + 1]),
                                int(order[s0]), int(order[s0 + 1])))
        print(f"  splits (exact, n=3 coarse==full) = {len(real_splits)}", flush=True)
    return members, dict(total=total, classes=len(starts),
                         splits=len(real_splits)), real_splits


def unrank(M, m, k):
    out, e, j = [], -1, m
    while j > 0:
        for v in range(e + 1, M):
            c = comb(M - v - 1, j - 1)
            if k < c:
                out.append(v); e = v; j -= 1
                break
            k -= c
    return out


from math import comb  # noqa: E402  (unrank 依赖)


def spread_cmin_general(fam_idx, members, N, n):
    worst = 1
    for r in range(1, n):
        for Z in itertools.combinations(range(N), r):
            Zs = frozenset(Z)
            d = sum(1 for i in fam_idx if Zs <= frozenset(members[i]))
            if d:
                c = 1
                while c ** (n - r) < d:
                    c += 1
                worst = max(worst, c)
    return worst


def main():
    n, N, m = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    members, stats, splits = scan_general(N, n, m)
    print(f"=== RESULT n={n} N={N} m={m}: families={stats['total']:,} "
          f"classes={stats['classes']:,} splits={stats['splits']}", flush=True)
    shown = 0
    for f1, t1, f2, t2, r1, r2 in splits[:5]:
        c1 = spread_cmin_general(f1, members, N, n)
        c2 = spread_cmin_general(f2, members, N, n)
        print(f"  SPLIT T={t1} vs {t2}  C_min={c1}/{c2}")
        print(f"    F1 = {sorted(sorted(members[i]) for i in f1)}")
        print(f"    F2 = {sorted(sorted(members[i]) for i in f2)}")
        shown += 1
    if stats["splits"] > shown:
        print(f"  ... {stats['splits'] - shown} more")


if __name__ == "__main__":
    main()
