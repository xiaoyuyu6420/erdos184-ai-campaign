#!/usr/bin/env python3
"""
S09 重炮：参数化覆盖搜索的 numpy 签名版（n=5 N=9 m=6 完备清场用）

原理与 s09_param_hunt.hunt 相同（覆盖定理见其 docstring），但全部向量化：
  F 侧（15 PM × C(M-3, m-3) D 组合）：签名 → (T 集合) 排序数组。
  G 侧（455 P 三重 × D 表）：每轮 30 万实例签名 searchsorted 命中。
  签名 = key·r mod 2^k（key = levels 1..n-1 的 deg 向量，uint8），
  双签名 32+64 位独立随机 ⟹ 假阳性 ~0（命中即真键匹配）。

  T 的向量化按成员来源分解（P = 3 个花/含核成员、D = m-3 个任意成员）：
  C(m,3) 个三元组按 {P,D}^3 模式分组，逐模式 numpy 位运算。

  G 实例分裂 ⟺ 键命中 F 签名 且 T(G) ∉ T 集合(键)。

自校准锚点（必须先跑）：
  python3 s09_hunt_fast.py calib      # n3N7m6 → 720 键（阳性）+ n5N9m5 → 0（阴性）
  python3 s09_hunt_fast.py n5m6       # 主战场：n=5 N=9 m=6
"""
import itertools
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s09_toolkit import T_ordered, bitset, profile_dict
from s09_param_hunt import perfect_matchings, pairs_on


def build_env(N, n, yref):
    U = list(range(N))
    Y0 = frozenset(yref)
    rest = [x for x in U if x not in Y0]
    assert len(rest) >= 6
    members = list(itertools.combinations(U, n))
    M = len(members)
    mbits = np.array([bitset(mm) for mm in members], dtype=np.uint16)
    Zmasks = [bitset(Z) for r in range(1, n)
              for Z in itertools.combinations(U, r)]
    Zm = np.array(Zmasks, dtype=np.int64)
    uni = np.arange(1 << N, dtype=np.int64)
    SUB = ((Zm[:, None] & uni[None, :]) == Zm[:, None]).astype(np.uint8)
    nP = len(Zmasks)
    # 成员键向量矩阵 M × nP
    V = SUB[:, mbits].T.copy()          # 行 = 成员
    # D 组合表（从 M-3 个非花成员中取 m-3）
    # 由调用方传入 triset（3 个花/P 成员 id）
    return U, Y0, rest, members, mbits, V, nP


def build_D_table(base_ids, M, m):
    """D 组合表：从 [M]∖base_ids 中取 m-3 的全部组合，返回 (rows, Dids)"""
    others = np.array([i for i in range(M) if i not in set(base_ids)],
                      dtype=np.int64)
    k = m - 3
    if k == 2:
        it = itertools.combinations(others.tolist(), 2)
    elif k == 3:
        it = itertools.combinations(others.tolist(), 3)
    else:
        raise ValueError("仅支持 m-3 ∈ {2,3}")
    Dids = np.fromiter(itertools.chain.from_iterable(it),
                       dtype=np.int64, count=-1)
    nD = len(Dids) // k
    return Dids.reshape(nD, k), others


def T_vec(ms_list):
    """ms_list: list of 同形状 uint16 数组 ⟹ 有序花计数 ×6"""
    t = np.zeros(len(ms_list[0]), dtype=np.int64)
    k = len(ms_list)
    for a in range(k):
        for b in range(a + 1, k):
            for c in range(b + 1, k):
                x, y, z = ms_list[a], ms_list[b], ms_list[c]
                ab, ac, bc = x & y, x & z, y & z
                t += ((ab == ac) & (ab == bc))
    return 6 * t


def hunt_fast(n, N, m, yref, tag, seed=20260914):
    t0 = time.time()
    U, Y0, rest, members, mbits, V, nP = build_env(N, n, yref)
    assert len(rest) >= 6, "rest 须 >= 6（花三重瓣并 6 点）"
    M = len(members)
    # DomF 花三重：rest 中取 6 点的完美匹配（rest > 6 时含自由 rest 点）
    PM = []
    for six in itertools.combinations(rest, 6):
        PM.extend(perfect_matchings(six))
    Psets = pairs_on(rest)
    rng = np.random.default_rng(seed)
    r32 = rng.integers(0, 2**32, size=nP, dtype=np.uint64)
    r64 = rng.integers(0, 2**32, size=nP, dtype=np.uint64)

    def keysigs(id_rows):
        """id_rows: (rows, m) int64 ⟹ (keymat, sig32, sig64)
        keymat 按需构建；sig = key·r mod 2^k（uint 溢出 wrap）"""
        rows = len(id_rows)
        key = V[id_rows[:, 0]].copy()
        for j in range(1, m):
            key += V[id_rows[:, j]]
        s32 = (key.astype(np.uint64) * r32).sum(axis=1, dtype=np.uint64)
        s64 = (key.astype(np.uint64) * r64).sum(axis=1, dtype=np.uint64)
        return key, s32.astype(np.uint32), s64

    # ---------- F 侧 ----------
    kD = m - 3
    f_parts32, f_parts64, f_partsT = [], [], []
    f_partsPM, f_partsDR = [], []
    nF = 0
    for mt in PM:
        tri = tuple(sorted((Y0 | p) for p in mt))
        base_ids = [i for i, mm in enumerate(members)
                    if tuple(sorted(mm)) in set(map(tuple, map(sorted, tri)))]
        assert len(base_ids) == 3
        Dids, others = build_D_table(base_ids, M, m)
        nD = len(Dids)
        # 键 = 3P + D
        pkey = V[base_ids[0]] + V[base_ids[1]] + V[base_ids[2]]
        dk = V[Dids[:, 0]].copy()
        for j in range(1, kD):
            dk += V[Dids[:, j]]
        key = np.empty((nD, nP), dtype=np.uint8)
        key[:] = pkey
        key += dk
        # T 向量化（P=base 3 成员 + D 3/2 成员）
        p0, p1, p2 = (np.full(nD, int(mbits[base_ids[0]]), dtype=np.uint16),
                      np.full(nD, int(mbits[base_ids[1]]), dtype=np.uint16),
                      np.full(nD, int(mbits[base_ids[2]]), dtype=np.uint16))
        d0, d1 = mbits[Dids[:, 0]], mbits[Dids[:, 1]]
        if kD == 3:
            d2 = mbits[Dids[:, 2]]
            ms = [p0, p1, p2, d0, d1, d2]
        else:
            ms = [p0, p1, p2, d0, d1]
        T = T_vec(ms)
        keep = T > 0
        key, Tk = key[keep], T[keep]
        s32 = (key.astype(np.uint64) * r32).sum(axis=1, dtype=np.uint64)
        s64 = (key.astype(np.uint64) * r64).sum(axis=1, dtype=np.uint64)
        f_parts32.append(s32.astype(np.uint32))
        f_parts64.append(s64)
        f_partsT.append(Tk)
        f_partsPM.append(np.full(int(keep.sum()), len(f_parts32) - 1,
                                 dtype=np.int32))
        f_partsDR.append(np.flatnonzero(keep).astype(np.int32))
        nF += int(keep.sum())
        print(f"[{tag}] F: PM done, cum F(T>0)={nF:,} ({time.time()-t0:.0f}s)",
              flush=True)
    fs32 = np.concatenate(f_parts32)
    fs64 = np.concatenate(f_parts64)
    fT = np.concatenate(f_partsT)
    fPM = np.concatenate(f_partsPM)
    fDR = np.concatenate(f_partsDR)
    order = np.lexsort((fPM, fDR, fs64, fs32))
    fs32, fs64, fT = fs32[order], fs64[order], fT[order]
    fPM, fDR = fPM[order], fDR[order]
    del f_parts32, f_parts64, f_partsT, f_partsPM, f_partsDR
    print(f"[{tag}] F side: {nF:,} T>0 instances, sorted ({time.time()-t0:.0f}s)",
          flush=True)
    # F 的 per-键 T 范围 + 多样键（组内 T 全同的键只需比对 min/max；
    # T 多样键的完整集合存 dict）
    same = (np.diff(fs32) == 0) & (np.diff(fs64) == 0)
    starts = np.flatnonzero(~np.concatenate(([True], same)))
    ends = np.append(starts[1:], len(fs32))
    tmin = np.minimum.reduceat(fT, starts)
    tmax = np.maximum.reduceat(fT, starts)
    multi = tmin != tmax
    multi_T = {}
    for gi in np.flatnonzero(multi):
        multi_T[(int(fs32[starts[gi]]), int(fs64[starts[gi]]))] = \
            sorted(set(int(x) for x in fT[starts[gi]:ends[gi]]))
    nkeysF = len(starts)
    print(f"[{tag}] F distinct keys={nkeysF:,}, "
          f"T-diverse keys={int(multi.sum()):,} ({time.time()-t0:.0f}s)",
          flush=True)

    # ---------- G 侧 ----------
    split_keys = []          # 命中的签名（用于解码）
    g_triples = []
    for comb in itertools.combinations(Psets, 3):
        gtri = tuple(sorted((Y0 | p) for p in comb))
        gtri_set = set(gtri)
        ids = tuple(i for i, mm in enumerate(members)
                    if frozenset(mm) in gtri_set)
        assert len(ids) == 3
        g_triples.append(ids)
    # D 表：base = 任一 P 三重（D 表对全部 P 三重同构：M-3 个成员中取 kD）
    # 但各 P 三重的补集不同 ⟹ D 表各自构建（同尺寸）
    nG_total = 0
    hits = []
    for gi_, pids in enumerate(g_triples):
        Dids, _ = build_D_table(list(pids), M, m)
        nD = len(Dids)
        pkey = V[pids[0]] + V[pids[1]] + V[pids[2]]
        dk = V[Dids[:, 0]].copy()
        for j in range(1, kD):
            dk += V[Dids[:, j]]
        key = dk + pkey
        g32 = ((key.astype(np.uint64) * r32).sum(axis=1, dtype=np.uint64)
               ).astype(np.uint32)
        g64 = (key.astype(np.uint64) * r64).sum(axis=1, dtype=np.uint64)
        nG_total += nD
        # searchsorted 命中
        lo = np.searchsorted(fs32, g32, side="left")
        hi = np.searchsorted(fs32, g32, side="right")
        cand = np.flatnonzero(hi > lo)
        if len(cand) == 0:
            continue
        # 64 位 + T 检查（命中数通常少，Python 逐个）
        starts64 = fs64  # 组内连续
        starts_arr = starts
        for ci in cand:
            l, h = int(lo[ci]), int(hi[ci])
            s64g = int(g64[ci])
            # 在 [l, h) 中找 s64 相等的行
            w = np.flatnonzero(fs64[l:h] == np.uint64(s64g))
            if len(w) == 0:
                continue
            r0 = l + int(w[0])
            grp = int(np.searchsorted(starts_arr, r0, side="right")) - 1
            # 键匹配 ⟹ 比较 T（组 [starts[grp], ends[grp]) = 同键全部行）
            Tg = int(T_vec([np.full(1, int(mbits[pids[0]]), dtype=np.uint16),
                            np.full(1, int(mbits[pids[1]]), dtype=np.uint16),
                            np.full(1, int(mbits[pids[2]]), dtype=np.uint16),
                            mbits[Dids[ci, 0:1]], mbits[Dids[ci, 1:2]],
                            mbits[Dids[ci, 2:3]]])[0]) if kD == 3 else \
                int(T_vec([np.full(1, int(mbits[pids[0]]), dtype=np.uint16),
                           np.full(1, int(mbits[pids[1]]), dtype=np.uint16),
                           np.full(1, int(mbits[pids[2]]), dtype=np.uint16),
                           mbits[Dids[ci, 0:1]], mbits[Dids[ci, 1:2]]])[0])
            if tmin[grp] != tmax[grp]:
                Ts = multi_T[(int(g32[ci]), s64g)]
            else:
                Ts = [int(tmin[grp])]
            if Tg not in Ts:
                hits.append((tuple(pids), tuple(int(x) for x in Dids[ci]),
                             Ts, Tg, (int(g32[ci]), s64g)))
                print(f"  *** SPLIT HIT *** T(F)∈{Ts} vs T(G)={Tg}", flush=True)
                # 回溯 F 侧同键实例（组内 64 位匹配行）
                for wj in w:
                    rj = l + int(wj)
                    pm_i, dr_i = int(fPM[rj]), int(fDR[rj])
                    F1 = reconstruct_F(pm_i, dr_i, PM, Y0, members, M, m, n)
                    F2 = [frozenset(members[i])
                          for i in list(pids) + list(Dids[ci])]
                    if profile_dict(F1, range(N), n - 1) == \
                       profile_dict(F2, range(N), n - 1) and \
                       T_ordered(F1) != Tg:
                        print(f"    F1 = {sorted(map(sorted, F1))}")
                        print(f"    F2 = {sorted(map(sorted, F2))}")
                        break
        if (gi_ + 1) % 50 == 0:
            print(f"[{tag}] G: {gi_+1}/455 P-triples, {nG_total:,} instances, "
                  f"hits={len(hits)} ({time.time()-t0:.0f}s)", flush=True)
    print(f"[{tag}] G total={nG_total:,} instances, hits={len(hits)} "
          f"({time.time()-t0:.0f}s)", flush=True)
    return nF, nG_total, hits


def reconstruct_F(pm_i, d_row, PM, Y0, members, M, m, n):
    """F 侧实例 = 第 pm_i 个完美匹配的三成员 + 其 D 表第 d_row 行组合"""
    mt = PM[pm_i]
    tri = [Y0 | p for p in mt]
    base_ids = [i for i, mm in enumerate(members)
                if frozenset(mm) in set(tri)]
    Dids, _ = build_D_table(base_ids, M, m)
    ids = base_ids + [int(x) for x in Dids[d_row]]
    return [frozenset(members[i]) for i in ids]


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "calib"
    if mode == "calib":
        print("=== 阳性锚点：n=3 N=7 m=6（期望 720 distinct split keys）===")
        nF, nG, hits = hunt_fast(3, 7, 6, (0,), "calib-fast")
        keys = {(h[4]) for h in hits}
        print(f"hits={len(hits)}, distinct sigs={len(keys)} （期望 720）")
        print("\n=== 阴性锚点：n=5 N=9 m=5（期望 0）===")
        nF, nG, hits5 = hunt_fast(5, 9, 5, (0, 1, 2), "n5m5-fast")
        assert not hits5, "n5m5 应零分裂（与慢速版一致）"
        print("n5m5 零分裂 ✓")
    elif mode == "n5m6":
        nF, nG, hits = hunt_fast(5, 9, 6, (0, 1, 2), "n5m6")
        if not hits:
            print("RESULT: n=5 N=9 m=6 参数化覆盖零分裂（m ≤ 6 全清场）")
    else:
        raise SystemExit(f"unknown mode {mode}")


if __name__ == "__main__":
    main()
