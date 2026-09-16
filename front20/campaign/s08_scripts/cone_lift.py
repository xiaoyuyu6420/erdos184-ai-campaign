#!/usr/bin/env python3
"""
S-08 数值验证 1：GAP-2″ 的构造体系（链接-掩码 gadget + 不交并组合）

【机制 1：链接-掩码 gadget（n-1 → n，单步）】
  输入：(n-1)-一致分裂对 (D₁,D₂)（同剖面、T(D₁)>0=T(D₂)），V = 宇宙（|V| = n+3），
        自由元 s ∈ V（s 不属于任何 D₁△D₂ 成员），新枢轴 x ∉ V。
  A := D₁∖D₂, B := D₂∖D₁（|A| = |B| 由剖面 level-0 保证）
  E₁ := {b∪{s} : b ∈ B},  E₂ := {a∪{s} : a ∈ A}     （n-一致）
  F_i := {x∪e : e ∈ D_i} ∪ E_i                       （n-一致，宇宙 V∪{x}，N = n+4）
  剖面恒等式：对 Z ∋ x：deg_F(Z) = deg_D(Z∖{x})（level ≤ n−2，相等）；
              对 Z ∌ x：deg_F(Z) = deg_D(Z) + deg_E(Z)，
              level ≤ n−2 处 deg_D 相等且 deg_E 相等（条件 C1：ud_A ≡ ud_B），
              level n−1 处 D-差 = 成员差（tautology）与 E-差恰好抵消。
  T 恒等式：混合三元组（两类成员混住）不可能成花 ⟹ T(F_i) = T(D_i) + T(E_i)，
              T(E₁) = T(B) = 0、T(E₂) = T(A) = 0（B ⊆ D₂、A ⊆ D₁ 无花子族）
              ⟹ F₁' 含花、F₂' 无花，强分裂保持。
  已验证可走 n=2 → 3（重构 S-05 [7] 证书）→ 4（N = 8 = n+4）。
  （n=5 起自由元耗尽，单步 gadget 停止；不交并接管已被 N3 定理否决，见 D 节。）

【机制 2：不交并组合（n₁ + n₂ → n₁+n₂）——已判死刑（S-08 收尾轮勘误）】
  (F₁ ⊔ G₁, F₂ ⊔ G₂)（宇宙不交并）：levels ≤ max(n₁,n₂)−1 内剖面逐点相加相等，
  但组合一致度 n = n₁+n₂ 的验证口径升至 levels ≤ n−1，组件成员 Z（|Z| = nᵢ）
  的隶属指示裸露 ⟹ 组件不同必失配。
  N3 定理：levels ≤ n−1 剖面相等 ⟹ A₁ = A₂、B₁ = B₂ ⟹ 族相同 ⟹ T 差 = 0。
  即不交组件组合永不分裂（证明见报告 §6；本脚本 D 节为演示 + 佐证）。
  T-并公式本身仍真：T(X⊔Y) = T(X)+T(Y)+6|Y|dp(X)+6|X|dp(Y)（E 节抽查）。
"""
import itertools
from functools import reduce


def T_ordered(fam):
    return sum(1 for A, B, C in itertools.permutations(fam, 3)
               if A & B == A & C == B & C)


def flowers_unordered(fam):
    return [(A, B, C) for A, B, C in itertools.combinations(fam, 3)
            if A & B == A & C == B & C]


def deg(fam, Z):
    Zs = frozenset(Z)
    return sum(1 for S in fam if Zs <= S)


def profile(fam, U, maxlev):
    return {Z: deg(fam, Z) for r in range(maxlev + 1)
            for Z in itertools.combinations(sorted(U), r)}


def cmin(fam, n, U):
    worst = 1
    for r in range(1, n):
        for Z in itertools.combinations(sorted(U), r):
            d = deg(fam, Z)
            if d:
                c = 1
                while c ** (n - r) < d:
                    c += 1
                if c > worst:
                    worst = c
    return worst


def disjoint_pairs(fam):
    return sum(1 for A, B in itertools.combinations(fam, 2) if not A & B)


def base_pairs():
    """n=2 与 n=3 的直接证书（宇宙 = 各对的精确支撑点集）

    勘误（S-08 收尾轮）：旧版把 H 对/K 对的宇宙误声明为 U6 = [0..5]，
    而这些对的边含点 6 ⟹ 含点 6 的剖面点被漏验，且 dunion 以 max(U)+1
    平移时点 6 与下一组件碰撞 ⟹ union-n5 假性失配 14 点（旧 §6 N3 的
    「不交并泄漏」实为该实现 bug；机制本身健全）。本版宇宙 = 精确支撑。
    """
    U6 = list(range(6))
    # n=2 #1: C6 vs 2C3（支撑 {0..5}）
    G1 = [frozenset(e) for e in [(0,1),(1,2),(2,3),(3,4),(4,5),(5,0)]]
    G2 = [frozenset(e) for e in [(0,1),(1,2),(2,0),(3,4),(4,5),(5,3)]]
    # n=2 #2: m=4 对（支撑 {1..6}）
    H1 = [frozenset(e) for e in [(1,2),(1,3),(2,4),(5,6)]]
    H2 = [frozenset(e) for e in [(1,3),(1,4),(2,5),(2,6)]]
    # n=2 #3: [7] 证书的链接对（支撑 {0,1,3,4,5,6}）
    K1 = [frozenset(e) for e in [(0,1),(3,4),(4,5),(5,6)]]
    K2 = [frozenset(e) for e in [(0,5),(1,4),(3,4),(5,6)]]
    # n=3: S-05 证书（支撑 {0..6}）
    F1 = [frozenset(s) for s in [(0,1,2),(0,5,6),(1,4,6),(2,3,4),(2,4,5),(2,5,6)]]
    F2 = [frozenset(s) for s in [(0,1,6),(0,2,5),(1,2,4),(2,3,4),(2,5,6),(4,5,6)]]
    return [(G1,G2,U6,2,"n2-C6"), (H1,H2,list(range(1,7)),2,"n2-m4"),
            (K1,K2,[0,1,3,4,5,6],2,"n2-link"), (F1,F2,list(range(7)),3,"n3-S05")]


def verify_pair(tag, P1, P2, U, n, strong=True):
    """完整验证：同剖面 + T 分裂 + 强分裂（P₂ 无花）"""
    p1, p2 = profile(P1, U, n - 1), profile(P2, U, n - 1)
    assert p1 == p2, f"{tag}: 剖面不等"
    assert all(len(S) == n for S in P1 + P2), f"{tag}: 一致度"
    T1, T2 = T_ordered(P1), T_ordered(P2)
    assert T1 > T2 >= 0, f"{tag}: T 不分裂 ({T1},{T2})"
    fl2 = flowers_unordered(P2)
    c1, c2 = cmin(P1, n, U), cmin(P2, n, U)
    assert c1 == c2, f"{tag}: C_min 不等"
    assert not fl2, f"{tag}: P₂ 有花"
    print(f"  [{tag}] n={n} N={len(U)} m={len(P1)} T={T1} vs {T2} "
          f"C_min={c1} P₂无花=True  PASS")
    return T1, T2, c1


def gadget(D1, D2, V, s):
    """链接-掩码单步：n-1 → n。返回 (F1, F2, 新宇宙, 新 A, 新 B)"""
    x = max(V) + 1
    A = [e for e in D1 if e not in D2]
    B = [e for e in D2 if e not in D1]
    assert len(A) == len(B), "|A| != |B|（level-0 应保证）"
    ss = frozenset([s])
    xx = frozenset([x])
    E1 = [b | ss for b in B]
    E2 = [a | ss for a in A]
    F1 = [e | xx for e in D1] + E1
    F2 = [e | xx for e in D2] + E2
    # 前置条件：C1（ud_A ≡ ud_B，levels ≤ n-2 = |e|-1）与 C2（s 自由）
    n = len(D1[0]) + 1
    for r in range(0, n - 1):
        for Z in itertools.combinations(sorted(V), r):
            Zs = frozenset(Z)
            udA = sum(1 for a in A if Zs <= a)
            udB = sum(1 for b in B if Zs <= b)
            assert udA == udB, ("C1 fails", Z, udA, udB)
    for M in A + B:
        assert s not in M, "C2 fails: s 非自由"
    return F1, F2, sorted(V) + [x], A, B


def dunion(P1, P2, U1, Q1, Q2, U2):
    """不交并：返回 (F1⊔Q1, F2⊔Q2, 宇宙并, 偏移映射后)"""
    off = max(U1) + 1
    shift = lambda S: frozenset(x + off for x in S)
    Q1s = [shift(S) for S in Q1]
    Q2s = [shift(S) for S in Q2]
    return P1 + Q1s, P2 + Q2s, sorted(set(U1) | {x + off for x in U2})


def main():
    print("=== A. 基础证书（n=2 三对 + n=3 S-05）===")
    cert0 = {}
    for P1, P2, U, n, tag in base_pairs():
        T1, T2, c = verify_pair(tag, P1, P2, U, n)
        cert0[tag] = (P1, P2, U, n)
    # S-05 证书规模
    print("  （n=2、n=3 均 2-spread：C_min = 2，N = n+4，m ∈ {4,6}）")

    print("\n=== B. gadget 重构检验：n2-link --(x=2,s=6)--> 应重构 S-05 [7] 证书 ===")
    K1, K2, _, _ = cert0["n2-link"]
    # [7] 证书 = gadget(D=链接对, x=2, s=6)，V = {0,1,3,4,5,6}
    V = [0, 1, 3, 4, 5, 6]
    F1r, F2r, U7, A, B = gadget(K1, K2, V, 6)
    # gadget 枢轴为 x=7；S-05 证书枢轴为 2：在重标签 7↦2 下应精确重合
    rel = {7: 2, 2: 7}
    ren = lambda S: frozenset(rel.get(z, z) for z in S)
    F1r = [ren(S) for S in F1r]
    F2r = [ren(S) for S in F2r]
    F1 = [frozenset(s) for s in [(0,1,2),(0,5,6),(1,4,6),(2,3,4),(2,4,5),(2,5,6)]]
    F2 = [frozenset(s) for s in [(0,1,6),(0,2,5),(1,2,4),(2,3,4),(2,5,6),(4,5,6)]]
    assert sorted(map(sorted, F1r)) == sorted(map(sorted, F1)), "gadget 未重构 F1"
    assert sorted(map(sorted, F2r)) == sorted(map(sorted, F2)), "gadget 未重构 F2"
    print("  gadget(x=2, s=6) 精确重构 S-05 证书  PASS")
    verify_pair("n3-gadget", F1r, F2r, list(range(7)), 3)

    print("\n=== C. gadget 再走一步：n=3 → n=4（s=3 为最后自由元）===")
    G1, G2, U8, A4in, B4in = gadget(F1, F2, list(range(7)), 3)
    verify_pair("n4-gadget", G1, G2, U8, 4)
    A4out = [e for e in G1 if e not in G2]
    B4out = [e for e in G2 if e not in G1]
    frees = [z for z in U8 if all(z not in M for M in A4out + B4out)]
    print(f"  n=4 证书的剩余自由元: {frees}（为空 ⟹ 单步 gadget 链在此止步；n≥5 需自由元预算 ≥ 2 的谱系，见报告 §11.6）")
    print("  F1(n=4) =", sorted(sorted(S) for S in G1))
    print("  F2(n=4) =", sorted(sorted(S) for S in G2))

    print("\n=== D. 不交并组合：机制死刑的精确定位（勘误：旧版声称 union 接管 n≥5，实为失效）===")
    # 旧版（含标签 bug：n=2 各对宇宙误声明为 [0..5] 而边含点 6）在此断言失败。
    # 修复标签后依然失败——失配点是机制性的：Z = 某侧组件成员（|Z| = 组件一致度）
    # 在 level >= 组件一致度处裸露「组件成员隶属」，两侧组件不同则必失配。
    # N3 定理（本报告 §6）：F_i = A_i ⊔ B_i（宇宙不交、组件一致 a,b，a+b = n）
    #   的 levels<=n-1 剖面相等 ⟹ A₁ = A₂ 且 B₁ = B₂ ⟹ T(F₁) = T(F₂)：
    #   不交组件组合永不分裂。以下演示 + 佐证。
    certs = {2: cert0["n2-m4"][:3], 3: cert0["n3-S05"][:3], 4: (G1, G2, U8)}

    def compose(n):
        a, b = (n % 3) // 2, n // 3
        if n % 3 == 1:
            a, b = 2, (n - 4) // 3
        assert 2 * a + 3 * b == n
        P1, P2, U = [], [], []
        for _ in range(a):
            p1, p2, u = certs[2]
            if not P1:
                P1, P2, U = list(p1), list(p2), list(u)
            else:
                P1, P2, U = dunion(P1, P2, U, p1, p2, u)
        for _ in range(b):
            p1, p2, u = certs[3]
            if not P1:
                P1, P2, U = list(p1), list(p2), list(u)
            else:
                P1, P2, U = dunion(P1, P2, U, p1, p2, u)
        return P1, P2, U

    for n in [5, 6, 7, 8, 9, 10, 11, 13]:
        P1, P2, U = compose(n)
        # 演示性验证：失配点集中出现在 levels ≤ 组件一致度（2,3），检查到
        # levels ≤ 6 已足够展示（levels 7+ 的全扫描在 n=13 时约 40 亿点，无意义）。
        lev = min(n - 1, 6)
        p1 = profile(P1, U, lev)
        p2 = profile(P2, U, lev)
        bad = [Z for Z in p1 if p1[Z] != p2[Z]]
        same_fam = sorted(map(sorted, P1)) == sorted(map(sorted, P2))
        print(f"  union-n{n}: N={len(U)} (levels<={lev}) 失配剖面点={len(bad)} "
              f"族相同={same_fam}（族不同 ⟹ 必有失配 ⟹ 不分裂）")
        assert bad or same_fam, "N3 定理被违反！"
    print("  ⟹ 不交并机制对 GAP-2″ 死刑（N3 定理）：组件成员在 level = 组件一致度")
    print("    处的隶属指示不可掩蔽；μ(n) n≥5 上界不由此产生（旧 docstring 勘误）。")

    print("\n=== E. T-并公式抽查（union-n5 上）===")
    P1, P2, U = compose(5)
    f1c, f2c, u3 = certs[3]
    h1, h2, u2 = certs[2]
    dp = disjoint_pairs
    pred1 = T_ordered(f1c) + T_ordered(h1) + 6*len(h1)*dp(f1c) + 6*len(f1c)*dp(h1)
    pred2 = T_ordered(f2c) + T_ordered(h2) + 6*len(h2)*dp(f2c) + 6*len(f2c)*dp(h2)
    real1, real2 = T_ordered(P1), T_ordered(P2)
    print(f"  T(F₁⊔H₁) 公式={pred1} 实算={real1}；T(F₂⊔H₂) 公式={pred2} 实算={real2}")
    assert pred1 == real1 and pred2 == real2

    print("\n全部通过：n=2..4 精确证书（N=n+4）；n≥5 的不交并接管已由 N3 定理否决（D 节）。")


if __name__ == "__main__":
    main()
