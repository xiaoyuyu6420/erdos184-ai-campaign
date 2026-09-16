#!/usr/bin/env python3
"""
S-08 数值验证 3：[7] 上 3-一致族的剖面分裂穷举 + ν(3) + 分裂维数统计

任务：
 (a) (n=3, U=[7])：m = 3..8 全穷举，按真链接剖面（deg1[7] + deg2[21]，m 由
     组内一致）分组，报告：族数、碰撞类数、T-分裂类数、|spec|/振幅统计；
     每个分裂类给出代表对与 2-spread 状态（S-05 遗留 2 的 m=8 校准 + 最小 m）。
 (b) ν(3)：m=4 已手证排除（任意 N，S-08 命题 E）；m=5 在 N=7,8,9 扫描 ⟹ 定夺
     ν(3) ∈ {5,6}。
 (c) 每个分裂对报告「差半并的元素覆盖数」——剩余自由元 = N − 覆盖数，
     即链接-掩码 gadget 可继续的步数（S-08 构造接口）。

用法：python3 split_dimension.py [all|u7|nu]
"""
import itertools
import sys
import numpy as np
from math import comb
from collections import defaultdict


def build_env(N, n=3):
    members = list(itertools.combinations(range(N), n))
    M = len(members)
    mvec = [sum(1 << e for e in m) for m in members]
    fedges = []
    for (i, si), (j, sj), (k, sk) in itertools.combinations(
            ((i, mvec[i]) for i in range(M)), 3):
        if (si & sj) == (si & sk) == (sj & sk):
            fedges.append((i, j, k))
    return members, mvec, fedges


def spread_cmin(fam_sets, N, n=3):
    worst = 1
    for r in range(1, n):
        for Z in itertools.combinations(range(N), r):
            Zs = frozenset(Z)
            d = sum(1 for S in fam_sets if Zs <= S)
            if d:
                c = 1
                while c ** (n - r) < d:
                    c += 1
                worst = max(worst, c)
    return worst


def scan(N, m):
    """穷举 |F| = m 的全部族；返回统计与分裂记录"""
    members, mvec, fedges = build_env(N)
    M = len(members)
    total = comb(M, m)
    nlane = (M + 63) // 64
    assert nlane <= 2, "本实现支持 M ≤ 128"
    pairs = list(itertools.combinations(range(N), 2))

    def lanes(mask):
        return (mask & ((1 << 63) - 1), mask >> 63)

    # deg1/deg2 掩码
    deg1_masks = [lanes(sum(1 << i for i, mm in enumerate(members) if v in mm))
                  for v in range(N)]
    deg2_masks = [lanes(sum(1 << i for i, mm in enumerate(members)
                            if frozenset(p) <= frozenset(mm))) for p in pairs]
    edge_masks = [lanes((1 << i) | (1 << j) | (1 << k)) for (i, j, k) in fedges]

    bc = np.bitwise_count
    K1, K2, T = [], [], []
    nkeys1 = (N + 7) // 8
    nkeys2 = (len(pairs) + 7) // 8
    k1_parts = [np.zeros(0, dtype=np.uint64) for _ in range(nkeys1)]
    k2_parts = [np.zeros(0, dtype=np.uint64) for _ in range(nkeys2)]
    tparts = []
    gen = itertools.combinations(range(M), m)
    CH = 2_000_000
    done = 0
    while done < total:
        cnt = min(CH, total - done)
        chunk = np.fromiter(itertools.chain.from_iterable(itertools.islice(gen, cnt)),
                            dtype=np.uint64, count=cnt * m).reshape(cnt, m)
        lo = np.zeros(cnt, dtype=np.uint64)
        hi = np.zeros(cnt, dtype=np.uint64)
        b_lo = np.array([(1 << i) if i < 63 else 0 for i in range(M)], dtype=np.uint64)
        b_hi = np.array([(1 << (i - 63)) if i >= 63 else 0 for i in range(M)], dtype=np.uint64)
        for j in range(m):
            cj = chunk[:, j]
            lo |= np.where(cj < 63, b_lo[cj], np.uint64(0))
            hi |= np.where(cj >= 63, b_hi[cj], np.uint64(0))
        t = np.zeros(cnt, dtype=np.int64)
        for el, eh in edge_masks:
            t += ((bc(lo & np.uint64(el)) + bc(hi & np.uint64(eh))) == 3).astype(np.int64)
        tparts.append(6 * t)
        d1 = {}
        d2 = {}
        for v in range(N):
            zl, zh = deg1_masks[v]
            d1[v] = bc(lo & np.uint64(zl)) + bc(hi & np.uint64(zh))
        for pi, (zl, zh) in enumerate(deg2_masks):
            d2[pi] = bc(lo & np.uint64(zl)) + bc(hi & np.uint64(zh))
        for part in range(nkeys1):
            k = np.zeros(cnt, dtype=np.uint64)
            for j in range(8):
                v = part * 8 + j
                if v < N:
                    k |= d1[v].astype(np.uint64) << (8 * j)
            k1_parts[part] = np.concatenate([k1_parts[part], k]) if done else k
        for part in range(nkeys2):
            k = np.zeros(cnt, dtype=np.uint64)
            for j in range(8):
                pi = part * 8 + j
                if pi < len(pairs):
                    k |= d2[pi].astype(np.uint64) << (8 * j)
            k2_parts[part] = np.concatenate([k2_parts[part], k]) if done else k
        done += cnt
    T = np.concatenate(tparts)
    keys = k1_parts + k2_parts
    # lexsort：最后一个键为主键。需要剖面为主、T 为次 ⟹ T 放最前、k1 放最后
    order = np.lexsort((T,) + tuple(reversed(keys)))
    sT = T[order]
    Ks = [k[order] for k in keys]
    diff = np.zeros(total, dtype=bool)
    diff[1:] = np.any([Ks[t][1:] != Ks[t][:-1] for t in range(len(Ks))], axis=0)
    bnd = np.flatnonzero(diff)  # diff[t]=True ⟹ 第 t 行开新组
    starts = np.concatenate(([0], bnd))
    mn = np.minimum.reduceat(sT, starts)
    mx = np.maximum.reduceat(sT, starts)
    issplit = mn != mx
    splits = []
    for gi in np.flatnonzero(issplit):
        s0 = int(starts[gi])
        s1 = int(starts[gi + 1]) if gi + 1 < len(starts) else total
        seg = sT[s0:s1]
        tset = sorted(set(int(x) for x in seg))
        i_min = int(order[s0 + int(np.argmin(seg))])
        i_max = int(order[s0 + int(np.argmax(seg))])
        splits.append((tset, i_min, i_max))
    stats = dict(total=int(total), classes=int(len(starts)), splits=int(len(splits)))
    return members, stats, splits


def unrank(M, m, k):
    """第 k 个（字典序）C(M,m) 组合的下标集；O(m·M)"""
    from math import comb
    out = []
    e = -1
    j = m
    while j > 0:
        for v in range(e + 1, M):
            c = comb(M - v - 1, j - 1)
            if k < c:
                out.append(v)
                e = v
                j -= 1
                break
            k -= c
    return out


def show(members, M, m, rank):
    idxs = unrank(M, m, rank)
    return sorted(sorted(members[i]) for i in idxs)


def report(N, m, members, stats, splits, max_show=2):
    print(f"--- [N={N}] m={m}: 族数={stats['total']}, 剖面类={stats['classes']}, "
          f"T-分裂类={stats['splits']}", flush=True)
    if not splits:
        return
    specs = sorted(len(ts) for ts, _, _ in splits)
    amps = sorted(ts[-1] - ts[0] for ts, _, _ in splits)
    # 聚合：2-spread 状态 / 自由元 / C_min
    by_cmin = defaultdict(int)
    by_free = defaultdict(int)
    spread_splits = 0
    min_cmin = 99
    best = None
    M = len(members)
    for ts, i_min, i_max in splits:
        f1 = show(members, M, m, i_min)
        f2 = show(members, M, m, i_max)
        s1 = [frozenset(S) for S in f1]
        s2 = [frozenset(S) for S in f2]
        c1 = spread_cmin(s1, N)
        c2 = spread_cmin(s2, N)
        assert c1 == c2, "同剖面 ⟹ 同 C_min 应自动成立"
        by_cmin[c1] += 1
        min_cmin = min(min_cmin, c1)
        if c1 <= 2:
            spread_splits += 1
        S1s = set(map(frozenset, f1)); S2s = set(map(frozenset, f2))
        diff_mem = S1s.symmetric_difference(S2s)
        d_els = set().union(*diff_mem) if diff_mem else set()
        fr = len(set(range(N)) - d_els)
        by_free[fr] += 1
        if best is None or (c1, -fr) < (best[0], -best[1]):
            best = (c1, fr, f1, f2, ts)
    print(f"    |spec|: max={specs[-1]}; 最大振幅={amps[-1]}")
    print(f"    分裂类 C_min 分布: {dict(sorted(by_cmin.items()))}; 最小 C_min = {min_cmin}")
    print(f"    2-spread 分裂类 (C_min≤2): {spread_splits}")
    print(f"    自由元分布: {dict(sorted(by_free.items()))}")
    c1, fr, f1, f2, ts = best
    print(f"    最优样例: C_min={c1}, 自由元={fr}, T={ts}")
    print(f"      F = {f1}")
    print(f"      G = {f2}")


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "u7"):
        print("======== (a) [7] 全穷举 m=3..8 ========")
        for m in range(3, 9):
            members, stats, splits = scan(7, m)
            report(7, m, members, stats, splits)
    if which in ("all", "nu"):
        print("======== (b) ν(3)：m=5 @ N=8,9 ========")
        for N in (8, 9):
            members, stats, splits = scan(N, 5)
            report(N, 5, members, stats, splits)


if __name__ == "__main__":
    main()
