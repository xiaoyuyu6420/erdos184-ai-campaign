#!/usr/bin/env python3
"""
S-08 数值验证 6（收尾轮）：[7] m=6 分裂类的 gadget 输入筛选

对 [7] 上全部 m=6 分裂类（同剖面、T 异）逐一检验链接-掩码 gadget 的前置条件：
 (H3) 存在自由元 s：s 不属于任何差半成员（差半 = F△G 的成员）；
 (H4) 上影子配平：ud_A(Z) = ud_B(Z) 对一切 |Z| ≤ n−2 = 1（n=3 时 levels 0,1；
      level 0 由 |A| = |B| 自动；即 A、B 的顶点度向量相等）。
满足者可作 gadget 输入升到 n=4（N=8），产出新证书并检查输出自由元。

用法：python3 gadget_input_filter.py
"""
import itertools
import numpy as np
from split_dimension import build_env, scan, unrank, show, spread_cmin


def main():
    members, stats, splits = scan(7, 6)
    M = len(members)
    print(f"[7] m=6: classes={stats['classes']:,} splits={stats['splits']}", flush=True)

    ok_h3 = 0
    ok_h3h4 = 0
    samples = []
    for ts, i_min, i_max in splits:
        f1 = show(members, M, 6, i_min)
        f2 = show(members, M, 6, i_max)
        S1 = set(map(frozenset, f1))
        S2 = set(map(frozenset, f2))
        A = S1 - S2
        B = S2 - S1
        if len(A) != len(B):
            continue          # 不可能（level-0），防御
        # (H3)
        covered = set().union(*(A | B)) if (A | B) else set()
        frees = set(range(7)) - covered
        if not frees:
            continue
        ok_h3 += 1
        # (H4)：顶点度（levels ≤ 1）
        def ud(famset):
            deg = [0] * 7
            for S in famset:
                for v in S:
                    deg[v] += 1
            return deg
        if ud(A) != ud(B):
            continue
        ok_h3h4 += 1
        if len(samples) < 5:
            samples.append((sorted(map(sorted, A)), sorted(map(sorted, B)),
                            sorted(frees), ts))
    print(f"(H3) satisfiable: {ok_h3} / {stats['splits']}", flush=True)
    print(f"(H3)+(H4) satisfiable: {ok_h3h4} / {stats['splits']}", flush=True)
    for A, B, frees, ts in samples:
        print(f"  sample A={A} B={B} frees={frees} T-spec={ts}")


if __name__ == "__main__":
    main()
