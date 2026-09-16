#!/usr/bin/env python3
"""
S-08 数值验证 2：广义 σ-交换锥搜索 —— n=3 → n=4 的关键一跳

背景：普通锥与固定公共元交换锥都需要"全体成员共元"，而 n=3 的分裂证书
（S-05 [7] 对）没有公共元，且 n=3 上不存在共元分裂对（可证：共元 3-一致对
= 2-一致对的锥，锥剖面在 level-2 读出边集 ⟹ 相等 ⟹ 族相等）。

广义构造：σ_i: F_i → U，σ_i(S) ∈ S；f_i(S) = (S ∖ {σ_i(S)}) ∪ {w₁,w₂}
  —— 4-一致，宇宙 [7]⊔{w₁,w₂}（9 元）。
剖面恒等式：deg_{G_i}(Z) = #{S ∈ F_i : (Z∖W) ⊆ S, σ_i(S) ∉ (Z∖W)}
  = deg_{F_i}(Z') − #{S ⊇ Z': σ_i(S) ∈ Z'}    (Z' = Z∖W, |Z'| ≤ 2)
  = 0                                          (|Z'| = 3，泄漏自动消灭)
故剖面相等 ⟺ 配平条件 (R1)：对一切 |Z'| ≤ 2：
  #{S ∈ F₁ ⊇ Z': σ₁(S) ∈ Z'} = #{S ∈ F₂ ⊇ Z': σ₂(S) ∈ Z'}

搜索：3^10 ≈ 59k 个 σ 赋值，过滤 (R1)；再查
  (R2) 基花 {012,234,256}（核 {2}）提升后仍是花；
  (R3) G₂ 无花（暴力）；
  (R4) C_min(G_i) 与公共元（供后续迭代）。
"""
import itertools
from collections import defaultdict

F1 = [frozenset(s) for s in [(0,1,2),(0,5,6),(1,4,6),(2,3,4),(2,4,5),(2,5,6)]]
F2 = [frozenset(s) for s in [(0,1,6),(0,2,5),(1,2,4),(2,3,4),(2,5,6),(4,5,6)]]
U7 = list(range(7))
COMMON = [frozenset(s) for s in [(2,3,4),(2,5,6)]]
FLOWER = [frozenset(s) for s in [(0,1,2),(2,3,4),(2,5,6)]]   # 核 {2}
W = {7, 8}


def corrections(fam, sigma):
    """corr[Z'] = #{S ⊇ Z': σ(S) ∈ Z'}，|Z'| ≤ 2"""
    corr = defaultdict(int)
    for r in range(1, 3):
        for Z in itertools.combinations(U7, r):
            Zs = frozenset(Z)
            c = 0
            for S in fam:
                if Zs <= S and sigma[S] in Zs:
                    c += 1
            corr[Zs] = c
    return corr


def lifted(fam, sigma):
    Ws = frozenset(W)
    return [(S - {sigma[S]}) | Ws for S in fam]


def T_ordered(fam):
    return sum(1 for A, B, C in itertools.permutations(fam, 3)
               if A & B == A & C == B & C)


def flowers_unordered(fam):
    return [(A, B, C) for A, B, C in itertools.combinations(fam, 3)
            if A & B == A & C == B & C]


def cmin(fam, n, U):
    worst = 1
    for r in range(1, n):
        for Z in itertools.combinations(sorted(U), r):
            Zs = frozenset(Z)
            d = sum(1 for S in fam if Zs <= S)
            if d:
                c = 1
                while c ** (n - r) < d:
                    c += 1
                if c > worst:
                    worst = c
    return worst


def main():
    allmembers = F1 + [S for S in F2 if S not in F1]   # 10 个（公共 2 个在后）
    cands = 0
    winners = []
    for combo in itertools.product(*[sorted(S) for S in allmembers]):
        sigma = {S: combo[i] for i, S in enumerate(allmembers)}
        # (R1) 配平
        c1, c2 = corrections(F1, sigma), corrections(F2, sigma)
        if c1 != c2:
            continue
        cands += 1
        # (R2) 基花提升
        if not all(sigma[S] != 2 for S in FLOWER):
            continue
        if cands > 200000:   # 安全阀
            break
        G1 = lifted(F1, sigma)
        G2 = lifted(F2, sigma)
        fl2 = flowers_unordered(G2)
        fl1 = flowers_unordered(G1)
        # (R3) G₂ 无花
        if fl2:
            continue
        # (R4)
        U9 = U7 + [7, 8]
        cm1, cm2 = cmin(G1, 4, U9), cmin(G2, 4, U9)
        winners.append((sigma, T_ordered(G1), len(fl1), cm1, cm2))
        if len(winners) >= 5:
            break

    print(f"满足 (R1) 的 σ 数：{cands}")
    print(f"满足 (R1)+(R2)+(R3) 的胜者数：{len(winners)}")
    for sigma, T1, nfl, cm1, cm2 in winners[:5]:
        print("  σ =", {tuple(sorted(S)): sigma[S] for S in allmembers})
        print(f"    T(G₁) = {T1}（{nfl} 朵无序花）, T(G₂) = 0, C_min = {cm1},{cm2}")
    if winners:
        sigma = winners[0][0]
        G1 = lifted(F1, sigma)
        G2 = lifted(F2, sigma)
        common = set.intersection(*[set(S) for S in G1])
        print("  G₁ 公共元 =", sorted(common), "（供后续 σ≡公共元 迭代）")
        print("  G₁ =", sorted(sorted(S) for S in G1))
        print("  G₂ =", sorted(sorted(S) for S in G2))
        with open("/tmp/s08_sigma_winner.txt", "w") as f:
            f.write(repr({tuple(sorted(S)): sigma[S] for S in allmembers}))
    else:
        print("！！单删 σ 无解——需要双删方案或 C_min=3 回退路线")


if __name__ == "__main__":
    main()
