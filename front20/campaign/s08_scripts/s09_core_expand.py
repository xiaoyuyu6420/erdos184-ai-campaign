#!/usr/bin/env python3
"""
S09 A2 加速器：核心扩容枚举（n=4 N=8，C₆-vs-2C₃ 机理专用）

机理：n=4 N=8 的 T-差 = 核-2 花数差 = 影子图 PM 数差。6-边影子图 C₆(PM=2)
vs 2C₃(PM=0) 同度序列 ⟹ 核心对（m=6）：
  F₀ = {0145,0156,0167,0172,0123,0134}（E = C₆ on rest {2..7}，T=12）
  G₀ = {0145,0152,0126,0167,0173,0135}？
  （以代码内显式定义为准：F₀ 的影子 = 6-圈，G₀ 的影子 = 两个三角形）

扩容：F = F₀ ∪ X、G = G₀ ∪ Y（|X| = |Y| = w，w = m − 6），要求：
  (P) levels ≤ 3 剖面逐点相等 ⟺ 差半 (F₀△G₀ ∪ X△Y) 上影子配平 levels ≤ 3
  枚举 X, Y ∈ C(64, w)（w ≤ 2 实用；w=1: 4096 对秒级；w=2: ~4M 对分钟级）。
命中后过滤 gadget 三关：自由元 ≥ 1、(H4) levels ≤ 2、T(G) = 0 ⟹ 提升验证。

用法：python3 s09_core_expand.py <w> [<w> ...]    # w = 扩容宽度
"""
import itertools
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np

from s09_toolkit import (T_ordered, flowers_unordered, profile_dict,
                         gadget_lift, verify_cert, free_points, check_H4,
                         bitset)

N, n = 8, 4
Y0 = frozenset({0, 1})
REST = [2, 3, 4, 5, 6, 7]

# 影子图：C₆ = 圈 2-3-4-5-6-7-2；2C₃ = {234}{567} 两个三角形
E_F = [frozenset(e) for e in [(2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 2)]]
E_G = [frozenset(e) for e in [(2, 3), (3, 4), (4, 2), (5, 6), (6, 7), (7, 5)]]
F0 = [Y0 | e for e in E_F]
G0 = [Y0 | e for e in E_G]

MEMBERS = list(itertools.combinations(range(N), n))
MIDX = {mm: i for i, mm in enumerate(MEMBERS)}
ZMASKS = [bitset(Z) for r in range(1, n)
          for Z in itertools.combinations(range(N), r)]
Zm = np.array(ZMASKS, dtype=np.int64)
UNI = np.arange(1 << N, dtype=np.int64)
SUB = ((Zm[:, None] & UNI[None, :]) == Zm[:, None]).astype(np.uint8)
VEC = {mm: SUB[:, bitset(mm)] for mm in MEMBERS}


def profkey(fam):
    k = np.zeros(len(ZMASKS), dtype=np.uint8)
    for S in fam:
        k += VEC[tuple(sorted(S))]
    return k.tobytes()


def main():
    ws = [int(a) for a in sys.argv[1:]] or [1]
    F0s, G0s = [frozenset(S) for S in F0], [frozenset(S) for S in G0]
    T1c, T2c = T_ordered(F0s), T_ordered(G0s)
    print(f"核心对: T(F₀)={T1c}, T(G₀)={T2c}, 同剖面="
          f"{profkey(F0s) == profkey(G0s)}")
    assert T1c != T2c, "核心对必须分裂"
    key0 = profkey(F0s)
    same0 = key0 == profkey(G0s)
    print(f"核心对自身同剖面 = {same0}（False 是预期：扩容 X/Y 须补偿核心差）")

    pool = [mm for mm in MEMBERS if frozenset(mm) not in set(F0s) | set(G0s)]
    for w in ws:
        t0 = time.time()
        print(f"\n#### w={w} (m={6+w}): {len(pool):,}C{w}² 候选对 ####",
              flush=True)
        combos = list(itertools.combinations(range(len(pool)), w))
        found_split, found_gadget = [], []
        tested = 0
        # X 侧键 → 组合索引（dict 匹配，O(1) 查询）
        keyF_by = {}
        for ci, c in enumerate(combos):
            X = [pool[i] for i in c]
            kf = profkey(F0s + [frozenset(S) for S in X])
            keyF_by.setdefault(kf, []).append(ci)
        for cj, d in enumerate(combos):
            Y = [pool[i] for i in d]
            kg = profkey(G0s + [frozenset(S) for S in Y])
            tested += 1
            for ci in keyF_by.get(kg, ()):
                X = [pool[i] for i in combos[ci]]
                F1 = F0s + [frozenset(S) for S in X]
                F2 = G0s + [frozenset(S) for S in Y]
                t1, t2 = T_ordered(F1), T_ordered(F2)
                if t1 != t2:
                    found_split.append((tuple(sorted(map(sorted, F1))),
                                        t1,
                                        tuple(sorted(map(sorted, F2))),
                                        t2))
                    # gadget 三关
                    if not flowers_unordered(F2):
                        fr = free_points(F1, F2, list(range(N)))
                        if fr:
                            ok, Z = check_H4(F1, F2, list(range(N)), 3)  # 定理 C 口径
                            if ok:
                                found_gadget.append((F1, F2, fr))
        print(f"  tested={tested:,} splits={len(found_split)} "
              f"gadget-qualified={len(found_gadget)} ({time.time()-t0:.0f}s)")
        for F1, F2, fr in found_gadget[:2]:
            print(f"  *** GADGET INPUT *** frees={fr}")
            G1, G2, U9 = gadget_lift(F1, F2, list(range(N)), fr[0])
            verify_cert("n5-N9-from-core-expand", G1, G2, U9, 5)
            print(f"  F1 = {sorted(map(sorted, F1))}")
            print(f"  F2 = {sorted(map(sorted, F2))}")
        if found_split and not found_gadget:
            s = found_split[0]
            print(f"  样例分裂对（不合格 gadget）: T={s[1]} vs {s[3]}")
            print(f"    F1 = {s[0]}")
            print(f"    F2 = {s[2]}")
        if not found_split:
            print(f"  RESULT: w={w} 核心扩容零分裂")


if __name__ == "__main__":
    main()
