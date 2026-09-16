#!/usr/bin/env python3
"""
S09 A2 猎场：n=4 N=8 分裂对 → gadget → n=5 N=9 证书（μ(5)=9 冲刺）

理论链：
  [T 差定位] n=4、N=8：核-3 花数 = Σ C(d_Y,3) 纯 level-3 剖面（定理 A(b)），
    核 ≤ 1 花被激活带排除（3n−2c ≤ N ⟹ c ≥ 2）⟹ 同剖面对的 T-差全部来自
    核-2 花数。分裂对存在 ⟺ 存在 (F,G) 同剖面、某 2-集 Y 的影子图
    E_Y(F) 与 E_Y(G)（rest 6 点、边 = {Q: Y∪Q ∈ F}）完美匹配数不同。
  [覆盖] 分裂对 (F,G)、T(F)>T(G) ⟹ F 含核-2 花 ⟹ 归一 Y₀={0,1}：
    F ∈ DomF（15 完美匹配 on rest × 任意额外成员）、G ∈ DomG（deg≥3 at Y₀）。
  [gadget 资格] (F3) 自由元 ≥ 1、(F4) 上影子配平 levels ≤ 2、(F2) T(G)=0
    ⟹ s09_toolkit.gadget_lift(s=自由元) ⟹ (n=5, N=9) 分裂证书。
    证书经 verify_cert 完整独立验证（μ(5)=9 则达成）。

用法：python3 s09_n4N8_hunt.py <m> [<m> ...]   # m ∈ {4,...}，逐层扫描
"""
import itertools
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s09_toolkit import (T_ordered, flowers_unordered, profile_dict, cmin,
                         gadget_lift, verify_cert, free_points, check_H4)
from s09_param_hunt import hunt


def check_cert(F1, T1, F2, T2):
    """命中对的快速独立复检（剖面对 + T 值）。"""
    U = list(range(8))
    p1 = profile_dict(F1, U, 3)
    p2 = profile_dict(F2, U, 3)
    assert p1 == p2, "命中对剖面失配（实现 bug）"
    assert T_ordered(F1) == T1 and T_ordered(F2) == T2
    return True


def main():
    ms = [int(a) for a in sys.argv[1:]] or [4, 5, 6]
    any_hit = False
    for m in ms:
        print(f"\n######## n=4 N=8 m={m} ########")
        nF, nG, hits, f1_db = hunt(4, 8, m, (0, 1), f"n4-m{m}",
                                   filter_gadget=True)
        # 命中统计与 gadget 尝试（qualify 已在 hunt 内打印合格者；
        # 这里对全部 hit 再做一次完整三关过滤 + gadget 提升尝试）
        fq = 0
        tried = set()
        for F1, T1, F2, T2, k in hits:
            check_cert(F1, T1, F2, T2)
            F1s, F2s = [frozenset(s) for s in F1], [frozenset(s) for s in F2]
            sig = (tuple(sorted(map(sorted, F1s))), tuple(sorted(map(sorted, F2s))))
            if sig in tried:
                continue
            tried.add(sig)
            if flowers_unordered(F2s):
                continue
            fr = free_points(F1s, F2s, list(range(8)))
            if not fr:
                continue
            ok, Z = check_H4(F1s, F2s, list(range(8)), 3)  # 定理 C 口径：levels <= n0-1
            if not ok:
                continue
            fq += 1
            if fq <= 3:
                print(f"  [gadget input] T={T1} vs {T2} frees={fr}")
                G1, G2, U9 = gadget_lift(F1s, F2s, list(range(8)), fr[0])
                verify_cert(f"n5-N9-from-n4-m{m}", G1, G2, U9, 5)
                print(f"  F1 = {sorted(map(sorted, F1s))}")
                print(f"  F2 = {sorted(map(sorted, F2s))}")
        print(f"[n4-m{m}] gadget-qualified pairs = {fq}")
        if hits:
            any_hit = True
        # 内存卫生
        del f1_db, hits
        sw = os.popen("sysctl -n vm.swapusage").read().strip()
        print(f"  [watermark] {sw}")
    if not any_hit:
        print(f"\nRESULT: n=4 N=8 m ∈ {ms} 参数化覆盖零分裂（该 m 层清场）")
    else:
        print(f"\nRESULT: n=4 N=8 存在分裂对（谱系情报）；gadget 合格者见上")


if __name__ == "__main__":
    main()
