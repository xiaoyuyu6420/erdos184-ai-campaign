#!/usr/bin/env python3
"""
S09 校准终章（修正版）：金标准轨道像与参数化检出键的逐键对齐

对齐对象 = **剖面键**（levels 1..2 的 deg 向量，与 s09_param_hunt.hunt 同一
键函数）。理论侧：金标准分裂类 (F_hi, F_lo) 经全部 σ（σ(y₀)=0，6!=720 个）
的像族 F_lo^σ 的剖面键集合；参数化侧：hunt 检出 hits 的 F 侧族剖面键集合。
两者应逐键相等。

用法：python3 s09_calib_align.py
"""
import itertools
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import split_dimension
from s09_toolkit import T_ordered, bitset
from s09_param_hunt import hunt


def build_profkey_fn(N, n):
    Zmasks = [bitset(Z) for r in range(1, n)
              for Z in itertools.combinations(range(N), r)]
    Zm = np.array(Zmasks, dtype=np.int64)
    uni = np.arange(1 << N, dtype=np.int64)
    SUB = ((Zm[:, None] & uni[None, :]) == Zm[:, None]).astype(np.uint8)

    def profkey(fam):
        k = np.zeros(len(Zmasks), dtype=np.uint8)
        for S in fam:
            k += SUB[:, bitset(S)]
        return k.tobytes()

    return profkey


def main():
    t0 = time.time()
    profkey = build_profkey_fn(7, 3)
    members, stats, splits = split_dimension.scan(7, 6)
    M = len(members)
    assert stats["splits"] == 5040

    def fam_of_rank(r):
        return [frozenset(members[i]) for i in split_dimension.unrank(M, 6, r)]

    # 对每个分裂类：核 y₀ 唯一（已验证 |K_hi|=1 对全部 5040 类）
    # 全部 5040 类同轨道 ⟹ 任取一类的像键集合即全体。取前 3 类分别验证
    # （同一轨道 ⟹ 像键集合应相同；顺带检验「单轨道」论断）。
    sig_by = {}
    for idx in range(3):
        tset, rmin, rmax = splits[idx]
        F_hi, F_lo = fam_of_rank(rmax), fam_of_rank(rmin)
        for A, B, C in itertools.combinations(F_hi, 3):
            if A & B == A & C == B & C and len(A & B) == 1:
                y0 = next(iter(A & B))
                break
        others = [x for x in range(7) if x != y0]
        tgt = [x for x in range(7) if x != 0]
        keys = set()
        for p in itertools.permutations(tgt):
            sigma = {y0: 0, **dict(zip(others, p))}
            F_ls = [frozenset(sigma[e] for e in S) for S in F_lo]
            keys.add(profkey(F_ls))
        sig_by[idx] = keys
        print(f"类#{idx}: y₀={y0}, 像键数={len(keys)}")
    assert sig_by[0] == sig_by[1] == sig_by[2], "前 3 类像键集不同 ⟹ 非单轨道？"
    keys_theory = sig_by[0]
    print(f"理论像键集合: {len(keys_theory)} 个（3 个代表类一致 ⟹ 单轨道佐证）")

    # 参数化检出键
    nF, nG, hits, f1_db = hunt(3, 7, 6, (0,), "align")
    keys_param = set()
    for F1, T1, F2, T2, _k in hits:
        keys_param.add(profkey(F1))
    print(f"参数化检出键: {len(keys_param)}")

    if keys_theory == keys_param:
        print("ALIGN: 逐键相等  PASS")
    else:
        d1, d2 = keys_theory - keys_param, keys_param - keys_theory
        print(f"ALIGN MISMATCH: 仅理论 {len(d1)}, 仅参数化 {len(d2)}")
        raise SystemExit(1)
    print(f"({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
