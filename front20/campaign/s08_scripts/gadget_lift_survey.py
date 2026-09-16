#!/usr/bin/env python3
"""
S-08 数值验证 7（收尾轮）：[7] m=6 分裂类 → gadget 提升 → n=4 自由元普查

流程：
 1. [7] m=6 全穷举得 5040 个分裂类（split_dimension.scan）。
 2. 对每个分裂类检验 (H3)（自由元存在）与 (H4)（差半顶点度相等）。
 3. 对通过者取自由元跑 cone_lift.gadget 提升到 n=4（C1 断言在函数内自动检验
    levels 0..n₀−1 = 0..2 的上影子配平）。
 4. 统计 n=4 输出的自由元分布。

预期结果（收尾轮实测）：(H3)+(H4) 5040/5040 通过；n=4 输出自由元 5040/5040
为 0——与命题 D′ 恒等式一致（输出自由元 = 输入自由元 − 1，输入恒 1）。

用法：python3 gadget_lift_survey.py
"""
from collections import Counter
from split_dimension import scan, show
from cone_lift import gadget


def main():
    members, stats, splits = scan(7, 6)
    M = len(members)
    print(f"[7] m=6: classes={stats['classes']:,} splits={stats['splits']}", flush=True)

    ok_h3 = ok_h3h4 = success = fail = 0
    free_counter = Counter()
    for ts, i_min, i_max in splits:
        S1 = [frozenset(s) for s in show(members, M, 6, i_min)]
        S2 = [frozenset(s) for s in show(members, M, 6, i_max)]
        A = [e for e in S1 if e not in S2]
        B = [e for e in S2 if e not in S1]
        covered = set().union(*(A + B))
        frees = [z for z in range(7) if z not in covered]
        if frees:
            ok_h3 += 1

            def ud(fam):
                deg = [0] * 7
                for S in fam:
                    for v in S:
                        deg[v] += 1
                return deg
            if ud(A) == ud(B):
                ok_h3h4 += 1
                try:
                    G1, G2, U8, _, _ = gadget(S1, S2, list(range(7)), frees[0])
                    success += 1
                    A4 = [e for e in G1 if e not in G2]
                    B4 = [e for e in G2 if e not in G1]
                    cov4 = set().union(*(A4 + B4))
                    frees4 = [z for z in U8 if z not in cov4]
                    free_counter[len(frees4)] += 1
                except AssertionError:
                    fail += 1
    print(f"(H3): {ok_h3}/{stats['splits']};  (H3)+(H4): {ok_h3h4}/{stats['splits']}",
          flush=True)
    print(f"gadget success={success}, C1-assert-fail={fail}", flush=True)
    print(f"n=4 output free-element distribution: {dict(sorted(free_counter.items()))}",
          flush=True)


if __name__ == "__main__":
    main()
