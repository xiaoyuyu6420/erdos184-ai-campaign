#!/usr/bin/env python3
"""
S-08 数值验证 8（收尾轮）：双步 gadget —— n=5 分裂证书（μ(5) ≤ 10）

谱系：N=8 m=6 的 n=3 分裂对（自由元预算 2，60,480 个类，全 2-spread）
  --gadget(s=6)--> n=4、N=9？不：N = 8+1 = 9？—— 实测宇宙 V∪{x} = {0..7}+8？
  （以脚本输出为准）--gadget(s=frees4[0])--> n=5 分裂证书。

实测结果：n=5、N=10、m=18，T = 6 vs 0（强分裂），双侧 C_min = 2（2-spread），
  levels ≤ 4 剖面逐点相等（verify_pair 断言全过）。

用法：python3 double_lift_n5.py
"""
from cone_lift import gadget, verify_pair

# N=8 m=6 扫描（split_dimension.scan(8,6)：32,468,436 族）的最优样例
# （自由元 = {6,7}，C_min = 2，T-spec [0,6]；report 自动输出）
S1 = [frozenset(s) for s in [(0,1,3),(0,1,5),(0,2,4),(0,2,6),(1,2,3),(3,4,5)]]
S2 = [frozenset(s) for s in [(0,1,2),(0,1,3),(0,2,6),(0,4,5),(1,3,5),(2,3,4)]]


def main():
    # T 定向：有花侧（T=6）放 D₁
    from cone_lift import T_ordered
    D1, D2 = (S2, S1) if T_ordered(S2) > T_ordered(S1) else (S1, S2)
    A = [e for e in D1 if e not in D2]
    B = [e for e in D2 if e not in D1]
    covered = set().union(*(A + B))
    frees = [z for z in range(8) if z not in covered]
    assert len(frees) == 2, frees
    print(f"input (n=3,N=8,m=6): frees={frees}")

    s1 = frees[0]
    G1, G2, U8, _, _ = gadget(D1, D2, list(range(8)), s1)
    A4 = [e for e in G1 if e not in G2]
    B4 = [e for e in G2 if e not in G1]
    frees4 = [z for z in U8 if z not in set().union(*(A4 + B4))]
    print(f"lift 1 (n=4): m={len(G1)}, frees4={frees4}")
    assert frees4, "自由元预算耗尽（不应发生：输入预算 2）"

    s2 = frees4[0]
    H1, H2, U9, _, _ = gadget(G1, G2, U8, s2)
    print(f"lift 2 (n=5): m={len(H1)}, N={len(U9)}")
    verify_pair("n5-double-gadget", H1, H2, U9, 5)
    print("H1 =", sorted(map(sorted, H1)))
    print("H2 =", sorted(map(sorted, H2)))
    print("\n⟹ μ(5) ≤ 10（叠加 μ(5) ≥ 9 与 N=9 的 m=4 清场 ⟹ μ(5) ∈ {9,10}）")


if __name__ == "__main__":
    main()
