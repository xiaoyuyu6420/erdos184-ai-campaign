#!/usr/bin/env python3
"""
S09 主武器：参数化覆盖搜索（μ(5) 定夺）

【覆盖定理（搜索完备性的依据，m 给定）】
设 (F,G) 为 N 元宇宙上 n-一致 m-族对，prof(F) = prof(G)（levels 1..n-1），
T(F) > T(G) >= 0。则：
  (i)  激活带（s08 定理 A(a)）：F 的每朵花核 c 满足 c >= (3n-N)/2。
  (ii) 核-(n-1) 层纯剖面（s08 定理 A(b)）：同剖面对的核-(n-1) 花数相等。
结合 T(F)-T(G) = 6·(核c花(F) - 核c花(G)) 的按核分解 ⟹
  T(F) > T(G) ⟹ F 含核 c = n-2 的花（c ≥ (3n-N)/2 由 (i)）。
取 F 的核-(n-2) 花 (S1,S2,S3)，核 Y₀，经点置换归一 Y₀ = Yref ⟹
  F  ∈ DomF := {m-族 ⊇ 某 Yref-花三元组}（花瓣两两不交），
  G  ∈ DomG := {m-族 : deg_G(Yref) ≥ 3}（剖面逐点：deg_G(Y₀)=deg_F(Y₀) ≥ 3）。
枚举 DomF 全实例建「剖面键 → T 值集合」字典，枚举 DomG 全实例查字典：
  键相同且 T(G) ∉ T 值集合 ⟺ 分裂对（覆盖一切分裂对）。∎

 DomF 中花三元组形状：
  n=3, c=1: Y₀={0}, rest 6 点完美匹配（15 种）；
  n=4, c=2: Y₀={0,1}, rest 6 点完美匹配（15 种）；
  n=5, c=3: Y₀={0,1,2}, rest 6 点完美匹配（15 种）。
 DomG 的 3 个含 Y₀ 成员在 rest 上取任意 2-集三重（C(15,3)=455 种）。

【校准（金标准）】n=3 N=7 m=6 全穷举（general_scan + split_dimension 双实现）
  = 5040 分裂类 ⟹ 本搜索器在该参数下必须命中恰 5040 个 distinct 剖面键。

【命中后的过滤器（gadget 输入资格，A2 路线）】
  (F3) 自由元 = N - |∪(F△G 成员)| ≥ 1
  (F4) 上影子配平：A=F∖G 与 B=G∖F levels ≤ n-2 逐点相等
  (F2) T(G) = 0（无花侧）
  三条全过 ⟹ gadget_lift(s=自由元) ⟹ (n+1, N+1) 分裂证书。

用法：
  python3 s09_param_hunt.py calib3        # n=3 N=7 m=6 校准（期望 5040）
  python3 s09_param_hunt.py n5m5          # n=5 N=9 m=5 主搜索（A1）
  python3 s09_param_hunt.py n4 <m>        # n=4 N=8 m=X 猎场（A2）
  python3 s09_param_hunt.py n5m5b <k>     # n=5 N=9 m=5 分块续跑（k=块号）
"""
import itertools
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s09_toolkit import (T_ordered, flowers_unordered, profile_dict, cmin,
                         gadget_lift, verify_cert, free_points, check_H4,
                         bitset)


def perfect_matchings(rest):
    """rest（6 点）上的全部完美匹配（15 种），每个 = 3 个 frozenset 2-集"""
    rest = list(rest)
    out = []
    a = rest[0]
    for b in rest[1:]:
        rem = [x for x in rest if x not in (a, b)]
        # 去重：固定剩余 4 点中最小点 c 所在的边（每匹配恰被枚举一次）
        c = min(rem)
        for d in rem:
            if d <= c:
                continue
            rem2 = [x for x in rem if x not in (c, d)]
            e, f = rem2
            out.append((frozenset((a, b)), frozenset((c, d)), frozenset((e, f))))
    return out


def pairs_on(rest):
    return [frozenset(p) for p in itertools.combinations(rest, 2)]


def hunt(n, N, m, yref, tag, filter_gadget=False):
    """
    参数化覆盖搜索（干净版）。
    yref: 归一花核（tuple），rest = U ∖ yref 须为 6 点。
    DomF = {m-族 ⊇ 某 Yref-花三元组}（15 完美匹配 × C(|M|-3, m-3)）
    DomG = {m-族 : 3 个含 Yref 成员（rest 上 2-集任取三重）+ (m-3) 任意}
    命中 = 剖面键相同且 T ∉ F 侧 T 值集合 ⟺ 分裂对。
    返回 (nF, nG, hits, f1_db)；hits 元组 (F1, T1, F2, T2, key)。
    """
    t0 = time.time()
    U = list(range(N))
    Y0 = frozenset(yref)
    rest = [x for x in U if x not in Y0]
    assert len(rest) == 6
    members = list(itertools.combinations(U, n))
    midx = {mm: i for i, mm in enumerate(members)}
    # 剖面键向量（levels 1..n-1）
    Zmasks = [bitset(Z) for r in range(1, n)
              for Z in itertools.combinations(U, r)]
    Zm = np.array(Zmasks, dtype=np.int64)
    uni = np.arange(1 << N, dtype=np.int64)
    SUB = ((Zm[:, None] & uni[None, :]) == Zm[:, None]).astype(np.uint8)
    vec = [SUB[:, bitset(mm)] for mm in members]
    mbit = [bitset(mm) for mm in members]
    nP = len(Zmasks)
    print(f"[{tag}] n={n} N={N} m={m}: |members|={len(members)}, "
          f"profile points={nP}", flush=True)

    def fam_of(ids):
        return [frozenset(members[i]) for i in ids]

    def T_of(ms):
        t = 0
        k = len(ms)
        for a in range(k):
            for b in range(a + 1, k):
                for c in range(b + 1, k):
                    x, y, z = ms[a], ms[b], ms[c]
                    if (x & y) == (x & z) == (y & z):
                        t += 1
        return 6 * t

    # ---------- DomF ----------
    PM = perfect_matchings(rest)
    triples = []
    for mt in PM:
        tri = tuple(sorted((Y0 | p) for p in mt))
        triples.append([midx[tuple(sorted(s))] for s in tri])
    f1_db = {}
    nF = 0
    for tri in triples:
        triset = set(tri)
        rest_ids = [i for i in range(len(members)) if i not in triset]
        ms_base = [mbit[i] for i in tri]
        for extra in itertools.combinations(rest_ids, m - 3):
            ids = tri + list(extra)
            ms = ms_base + [mbit[i] for i in extra]
            nF += 1
            T = T_of(ms)
            if T == 0:
                continue
            kv = vec[ids[0]].copy()
            for i in ids[1:]:
                kv += vec[i]
            f1_db.setdefault(kv.tobytes(), {}).setdefault(T, ids)
    print(f"[{tag}] DomF instances={nF:,}, T>0 distinct keys={len(f1_db):,} "
          f"({time.time()-t0:.1f}s)", flush=True)

    # ---------- DomG ----------
    Psets = pairs_on(rest)
    g3_triples = [tuple(sorted((Y0 | p) for p in comb))
                  for comb in itertools.combinations(Psets, 3)]
    hits, hit_keys, gadget_qualified = [], set(), []
    nG = 0
    for gtri in g3_triples:
        ids3 = [midx[tuple(sorted(s))] for s in gtri]
        triset = set(ids3)
        rest_ids = [i for i in range(len(members)) if i not in triset]
        ms3 = [mbit[i] for i in ids3]
        v3 = vec[ids3[0]] + vec[ids3[1]] + vec[ids3[2]]
        for extra in itertools.combinations(rest_ids, m - 3):
            ms = ms3 + [mbit[i] for i in extra]
            nG += 1
            T = T_of(ms)
            kv = v3.copy()
            for i in extra:
                kv += vec[i]
            slot = f1_db.get(kv.tobytes())
            if slot is not None and T not in slot:
                if kv.tobytes() not in hit_keys:
                    hit_keys.add(kv.tobytes())
                    for tval, fids in slot.items():
                        hits.append((fam_of(fids), tval, fam_of(sorted(ids3 + list(extra))), T, kv.tobytes()))
                        break
                    if filter_gadget:
                        F1, T1, F2, T2, _ = hits[-1]
                        qualify(F1, F2, U, n, gadget_qualified, tag)
    print(f"[{tag}] DomG instances={nG:,}, distinct split keys={len(hit_keys)}, "
          f"hits={len(hits)} ({time.time()-t0:.1f}s)", flush=True)
    return nF, nG, hits, f1_db


def qualify(F1, F2, U, n, sink, tag):
    """gadget 输入资格过滤：(F3) 自由元≥1、(F4) 上影子配平、(F2) T(G)=0"""
    F1s, F2s = [frozenset(s) for s in F1], [frozenset(s) for s in F2]
    if flowers_unordered(F2s):
        return False
    fr = free_points(F1s, F2s, U)
    if not fr:
        return False
    ok, Z = check_H4(F1s, F2s, U, n - 1)  # 定理 C 口径：levels <= n0-1
    if not ok:
        return False
    sink.append((F1s, F2s, tuple(U), n, tuple(fr)))
    print(f"  *** GADGET-QUALIFIED *** frees={fr}", flush=True)
    print(f"    F1 = {sorted(map(sorted, F1s))}")
    print(f"    F2 = {sorted(map(sorted, F2s))}")
    return True


def distinct_split_keys(f1_db, hits):
    """分裂 distinct 键数：需要重扫 DomG 收集命中键。"""
    raise NotImplementedError


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "calib3"
    if mode == "calib3":
        # 金标准：n=3 N=7 m=6 全穷举 5040 分裂类
        n, N, m, yref = 3, 7, 6, (0,)
        nF, nG, hits, f1_db = hunt(n, N, m, yref, "calib3")
        # distinct 命中键 = 重新以键计数 hits 的 F 侧（每 hit 一个键，
        # 但同键多 hit 可能；重新计算）
        keyset = set()
        for F1, T1, F2, T2, k in hits:
            keyset.add(tuple(sorted(tuple(sorted(S)) for S in F1)))
        print(f"[calib3] distinct F-side split families = {len(keyset)}")
        # 与金标准口径（分裂类 = 剖面类）对齐：分裂类数 = distinct 剖面键
        # （一个剖面类一个键）。期望 5040。
        print(f"CALIBRATION: expect 5040 split classes; "
              f"got {len(keyset)} distinct split families (F-side).")
    elif mode == "n5m5":
        n, N, m, yref = 5, 9, 5, (0, 1, 2)
        nF, nG, hits, f1_db = hunt(n, N, m, yref, "n5m5", filter_gadget=False)
        keyset = {tuple(sorted(tuple(sorted(S)) for S in F1)) for F1, _, _, _ in hits}
        print(f"[n5m5] distinct split families (F-side) = {len(keyset)}")
        if not hits:
            print("RESULT: n=5 N=9 m=5 参数化覆盖零分裂（m=5 层清场）")
    elif mode == "n4":
        m = int(sys.argv[2])
        n, N, yref = 4, 8, (0, 1)
        nF, nG, hits, f1_db = hunt(n, N, m, yref, f"n4-m{m}",
                                   filter_gadget=True)
        keyset = {tuple(sorted(tuple(sorted(S)) for S in F1)) for F1, _, _, _ in hits}
        print(f"[n4-m{m}] distinct split families (F-side) = {len(keyset)}")
        if not hits:
            print(f"RESULT: n=4 N=8 m={m} 参数化覆盖零分裂")
    else:
        raise SystemExit(f"unknown mode {mode}")


if __name__ == "__main__":
    main()
