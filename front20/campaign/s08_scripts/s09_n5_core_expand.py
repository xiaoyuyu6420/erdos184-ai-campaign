#!/usr/bin/env python3
"""
S09 A1' 侦察：n=5 N=9 核心扩容枚举（C₆-vs-2C₃ 机理 @ 核-3 花）

机理（n=5、N=9）：T-差 = 核-3 花数差 = 影子图 E_Y（rest 6 点）PM 数差。
核心对（m=6）：F₀ = {012∪e : e ∈ C₆} vs G₀ = {012∪e : e ∈ 2C₃}，
T = 12 vs 0，但 level-2 裸露 E 的边 ⟹ 核心自身不同剖面，
扩容 X/Y 须补偿剖面差：profkey(F₀∪X) == profkey(G₀∪Y)。
匹配用 dict ⟹ 复杂度 O(C(120,w) × profkey)。w ≥ 1 全扫。

命中后 gadget 三关过滤（自由元 ≥ 1、(H4) levels ≤ 3、T(G)=0）
——注意此处命中本身就是 n=5 N=9 分裂对（μ(5)=9 直接达成），
gadget 过滤只是附加情报（n=6 谱系）。

用法：python3 s09_n5_core_expand.py <w> [<w> ...]
"""
import itertools
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np

from s09_toolkit import (T_ordered, flowers_unordered, free_points,
                         check_H4, bitset)

N, n = 9, 5
Y0 = frozenset({0, 1, 2})
REST = [3, 4, 5, 6, 7, 8]

# 影子图：C₆ = 圈 3-4-5-6-7-8-3；2C₃ = {345}{678}
E_F = [frozenset(e) for e in [(3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 3)]]
E_G = [frozenset(e) for e in [(3, 4), (4, 5), (5, 3), (6, 7), (7, 8), (8, 6)]]
F0 = [Y0 | e for e in E_F]
G0 = [Y0 | e for e in E_G]

MEMBERS = list(itertools.combinations(range(N), n))
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
    print(f"核心对: T={T1c} vs {T2c}; 自身同剖面="
          f"{profkey(F0s) == profkey(G0s)}（False 预期）")
    assert T1c != T2c

    pool = [mm for mm in MEMBERS
            if frozenset(mm) not in set(F0s) | set(G0s)]
    for w in ws:
        t0 = time.time()
        ncomb = 1
        k = 1
        for j in range(w):
            k = k * (len(pool) - j) // (j + 1)
        print(f"\n#### w={w} (m={6+w}): C({len(pool)},{w}) = {k:,} 组合 ####",
              flush=True)
        combos = itertools.combinations(range(len(pool)), w)
        keyF_by = {}
        nF1 = 0
        for c in combos:
            X = [pool[i] for i in c]
            kf = profkey(F0s + [frozenset(S) for S in X])
            keyF_by.setdefault(kf, []).append(c)
            nF1 += 1
        print(f"  X 侧键 {nF1:,} 建立 ({time.time()-t0:.0f}s)", flush=True)
        found_split, found_gadget = [], []
        tested = 0
        for d in itertools.combinations(range(len(pool)), w):
            Y = [pool[i] for i in d]
            kg = profkey(G0s + [frozenset(S) for S in Y])
            tested += 1
            for c in keyF_by.get(kg, ()):
                F1 = F0s + [frozenset(pool[i]) for i in c]
                F2 = G0s + [frozenset(pool[i]) for i in d]
                t1, t2 = T_ordered(F1), T_ordered(F2)
                if t1 != t2:
                    found_split.append((F1, t1, F2, t2))
                    if not flowers_unordered(F2):
                        fr = free_points(F1, F2, list(range(N)))
                        if fr:
                            ok, Z = check_H4(F1, F2, list(range(N)), 4)  # 定理 C 口径 levels <= n0-1 = 4
                            if ok:
                                found_gadget.append((F1, F2, fr))
        print(f"  tested={tested:,} splits={len(found_split)} "
              f"gadget-qualified={len(found_gadget)} ({time.time()-t0:.0f}s)")
        for F1, F2, fr in found_gadget[:3]:
            print(f"  *** SPLIT+gadget-qualified *** frees={fr}")
            print(f"    F1 = {sorted(map(sorted, F1))}")
            print(f"    F2 = {sorted(map(sorted, F2))}")
        for F1, t1, F2, t2 in found_split[:2]:
            print(f"  样例分裂对: T={t1} vs {t2}")
            print(f"    F1 = {sorted(map(sorted, F1))}")
            print(f"    F2 = {sorted(map(sorted, F2))}")
        if not found_split:
            print(f"  RESULT: w={w} 零分裂")


if __name__ == "__main__":
    main()
