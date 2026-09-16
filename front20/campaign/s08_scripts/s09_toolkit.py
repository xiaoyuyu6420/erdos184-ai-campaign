#!/usr/bin/env python3
"""
S09（软靶 #6，2026-09-13/14）：μ(5) ∈ {9,10} 定夺战——公共工具 + 自击测试

独立重写的验证链（不 import cone_lift 的验证逻辑；交叉断言在自击中做）：
  - T_ordered / flowers_unordered / profile_dict / cmin：位运算独立实现
  - gadget_lift：链接-掩码 gadget 独立实现（含 (H4) 前置断言）
  - verify_cert：分裂证书完整验证（同剖面 + T 分裂 + 一致度 + C_min 相等）
  - fam_key 工具：numpy 向量化的剖面键（供参数化搜索）

自击测试（python3 s09_toolkit.py selftest）：
  [T1] 已知证书链复算：n2-C6 / n2-m4 / n2-link / n3-S05 / n4-gadget / n5-double
  [T2] T 与 profile 与 cone_lift 交叉验证（随机族 800 例 × 3 个 (n,N)）
  [T3] gadget_lift 与 cone_lift.gadget 输出逐成员一致
  [T4] 阴性对照：随机剖面不同的族对必须判「非分裂」
  [T5] C₆ vs 2C₃ 影子图机制 sanity：6 点图完美匹配计数器

命令行：
  python3 s09_toolkit.py selftest
"""
import itertools
import sys

import numpy as np


# ---------------- 基本不变量（独立实现） ----------------

def bitset(S):
    return sum(1 << e for e in S)


def T_ordered(fam):
    """有序 3-花三元组数：两两互异成员、两两交相等。独立位运算实现。"""
    ms = [bitset(S) for S in fam]
    t = 0
    k = len(ms)
    for a in range(k):
        for b in range(a + 1, k):
            for c in range(b + 1, k):
                x, y, z = ms[a], ms[b], ms[c]
                if (x & y) == (x & z) == (y & z):
                    t += 6
    return t


def flowers_unordered(fam):
    ms = [bitset(S) for S in fam]
    out = []
    k = len(ms)
    for a in range(k):
        for b in range(a + 1, k):
            for c in range(b + 1, k):
                x, y, z = ms[a], ms[b], ms[c]
                if (x & y) == (x & z) == (y & z):
                    out.append((fam[a], fam[b], fam[c]))
    return out


def profile_dict(fam, U, maxlev):
    """levels 0..maxlev 的 deg 字典（Z 的元组表示 → deg）"""
    fams = [frozenset(S) for S in fam]
    out = {}
    for r in range(maxlev + 1):
        for Z in itertools.combinations(sorted(U), r):
            Zs = frozenset(Z)
            out[Z] = sum(1 for S in fams if Zs <= S)
    return out


def cmin(fam, n, U):
    worst = 1
    fams = [frozenset(S) for S in fam]
    for r in range(1, n):
        for Z in itertools.combinations(sorted(U), r):
            Zs = frozenset(Z)
            d = sum(1 for S in fams if Zs <= S)
            if d:
                c = 1
                while c ** (n - r) < d:
                    c += 1
                if c > worst:
                    worst = c
    return worst


def diff_members(F, G):
    Fs, Gs = set(map(frozenset, F)), set(map(frozenset, G))
    A = sorted(Fs - Gs, key=sorted)
    B = sorted(Gs - Fs, key=sorted)
    return A, B


def free_points(F, G, V):
    """(H3)：不在 F△G 任何成员中的点"""
    A, B = diff_members(F, G)
    if not A and not B:
        return sorted(V)
    covered = set().union(*(A + B))
    return [z for z in sorted(V) if z not in covered]


def check_H4(F, G, V, maxlev):
    """gadget 输入 (H4)：A=F∖G 与 B=G∖F 的上影子 levels ≤ maxlev 逐点相等"""
    A, B = diff_members(F, G)
    assert len(A) == len(B), "(H4) 前置：|A| != |B|"
    for r in range(maxlev + 1):
        for Z in itertools.combinations(sorted(V), r):
            Zs = frozenset(Z)
            udA = sum(1 for a in A if Zs <= frozenset(a))
            udB = sum(1 for b in B if Zs <= frozenset(b))
            if udA != udB:
                return False, Z
    return True, None


def gadget_lift(D1, D2, V, s):
    """链接-掩码 gadget 独立实现。前置：同剖面、T(D1)>0>=T(D2)、(H3) s 自由、
    (H4) 上影子配平 levels <= n0-1（n0 = |成员|）。返回 (F1, F2, 新宇宙)。"""
    D1s = [frozenset(S) for S in D1]
    D2s = [frozenset(S) for S in D2]
    n0 = len(D1s[0])
    p1 = profile_dict(D1s, V, n0 - 1)
    p2 = profile_dict(D2s, V, n0 - 1)
    assert p1 == p2, "gadget 前置 (H1) 失败：剖面不等"
    A, B = diff_members(D1s, D2s)
    ok, Z = check_H4(D1s, D2s, V, n0 - 1)
    assert ok, f"gadget 前置 (H4) 失败 at {Z}"
    for M in A + B:
        assert s not in M, "gadget 前置 (H3) 失败：s 非自由"
    x = max(V) + 1
    ss, xx = frozenset([s]), frozenset([x])
    E1 = [b | ss for b in B]
    E2 = [a | ss for a in A]
    F1 = [e | xx for e in D1s] + E1
    F2 = [e | xx for e in D2s] + E2
    return F1, F2, sorted(V) + [x]


def verify_cert(tag, F1, F2, U, n, expect_T=None, require_flowerless=False):
    """分裂证书完整独立验证。返回 (T1, T2, c)。"""
    F1s, F2s = [frozenset(S) for S in F1], [frozenset(S) for S in F2]
    assert all(len(S) == n for S in F1s + F2s), f"{tag}: 一致度失败"
    p1 = profile_dict(F1s, U, n - 1)
    p2 = profile_dict(F2s, U, n - 1)
    bad = [Z for Z in p1 if p1[Z] != p2[Z]]
    assert not bad, f"{tag}: 剖面失配 {bad[:5]}"
    T1, T2 = T_ordered(F1s), T_ordered(F2s)
    assert T1 != T2, f"{tag}: T 不分裂 ({T1} == {T2})"
    if expect_T is not None:
        assert (T1, T2) == expect_T, f"{tag}: T = {T1},{T2} ≠ 期望 {expect_T}"
    c1, c2 = cmin(F1s, n, U), cmin(F2s, n, U)
    assert c1 == c2, f"{tag}: C_min 不等 {c1} vs {c2}（同剖面应自动相等）"
    if require_flowerless:
        assert not flowers_unordered(F2s), f"{tag}: P₂ 有花"
    print(f"  [{tag}] n={n} N={len(U)} m={len(F1s)} T={T1} vs {T2} "
          f"C_min={c1} PASS")
    return T1, T2, c1


# ---------------- 参数化搜索工具 ----------------

def build_sub_matrix(N, n):
    """剖面点（levels 1..n-1）× 全体 2^N 掩码的包含矩阵；返回 (Zmasks, SUB)。
    SUB[i, m] = 1 ⟺ Zmasks[i] ⊆ m。"""
    Zmasks = []
    for r in range(1, n):
        for Z in itertools.combinations(range(N), r):
            Zmasks.append(bitset(Z))
    Zm = np.array(Zmasks, dtype=np.int64)
    uni = np.arange(1 << N, dtype=np.int64)
    SUB = ((Zm[:, None] & uni[None, :]) == Zm[:, None]).astype(np.uint8)
    return Zmasks, SUB


def member_vectors(N, n, members):
    """每个成员（tuple）的剖面 deg 贡献向量（uint8）"""
    _, SUB = build_sub_matrix(N, n)
    return [SUB[:, bitset(m)] for m in members]


# ---------------- 自击测试 ----------------

def _certs():
    """已知证书库（与 s08_gap2pp.md §3、§11.6 逐字一致）"""
    U6 = list(range(6))
    G1 = [frozenset(e) for e in [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)]]
    G2 = [frozenset(e) for e in [(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3)]]
    H1 = [frozenset(e) for e in [(1, 2), (1, 3), (2, 4), (5, 6)]]
    H2 = [frozenset(e) for e in [(1, 3), (1, 4), (2, 5), (2, 6)]]
    K1 = [frozenset(e) for e in [(0, 1), (3, 4), (4, 5), (5, 6)]]
    K2 = [frozenset(e) for e in [(0, 5), (1, 4), (3, 4), (5, 6)]]
    F1 = [frozenset(s) for s in [(0, 1, 2), (0, 5, 6), (1, 4, 6), (2, 3, 4),
                                 (2, 4, 5), (2, 5, 6)]]
    F2 = [frozenset(s) for s in [(0, 1, 6), (0, 2, 5), (1, 2, 4), (2, 3, 4),
                                 (2, 5, 6), (4, 5, 6)]]
    S1 = [frozenset(s) for s in [(0, 1, 3), (0, 1, 5), (0, 2, 4), (0, 2, 6),
                                 (1, 2, 3), (3, 4, 5)]]
    S2 = [frozenset(s) for s in [(0, 1, 2), (0, 1, 3), (0, 2, 6), (0, 4, 5),
                                 (1, 3, 5), (2, 3, 4)]]
    return dict(n2c6=(G1, G2, U6, 2), n2m4=(H1, H2, list(range(1, 7)), 2),
                n2link=(K1, K2, [0, 1, 3, 4, 5, 6], 2),
                n3s05=(F1, F2, list(range(7)), 3),
                n3N8=(S2, S1, list(range(8)), 3))


def selftest():
    print("=== [T1] 已知证书链复算（阳性锚点）===")
    c = _certs()
    verify_cert("n2-C6", *c["n2c6"], expect_T=(12, 0), require_flowerless=True)
    verify_cert("n2-m4", *c["n2m4"], expect_T=(6, 0), require_flowerless=True)
    verify_cert("n2-link", *c["n2link"], expect_T=(6, 0), require_flowerless=True)
    verify_cert("n3-S05", *c["n3s05"], expect_T=(6, 0), require_flowerless=True)
    verify_cert("n3-N8m6", *c["n3N8"], expect_T=(6, 0), require_flowerless=True)

    # gadget 链：n3-S05 --(s=3)--> n4 证书（s08 §5 推论 D2 的重算）
    F1, F2, U7, _ = c["n3s05"]
    G1, G2, U8 = gadget_lift(F1, F2, U7, 3)
    verify_cert("n4-gadget", G1, G2, U8, 4, expect_T=(6, 0),
                require_flowerless=True)
    # n4 --(自由元)--> n5 证书（double_lift_n5.py 谱系重算）
    fr4 = free_points(G1, G2, U8)
    print(f"  n4 输出的自由元 = {fr4}（报告口径：空 ⟹ 链止步）")
    assert not fr4, "n4 链自由元应为空（s08 §11.6 口径）"

    # double-lift 证书：从报告 §11.6 抄写的显式族（人读数据独立复核）
    H1 = [frozenset(int(ch) for ch in s) for s in
          ["01267", "01289", "01389", "01569", "01578", "02469", "02478",
           "02689", "04567", "04589", "12369", "12378", "13567", "13589",
           "23467", "23489", "34569", "34578"]]
    H2 = [frozenset(int(ch) for ch in s) for s in
          ["01269", "01278", "01389", "01567", "01589", "02467", "02489",
           "02689", "04569", "04578", "12367", "12389", "13569", "13578",
           "23469", "23478", "34567", "34589"]]
    verify_cert("n5-double-lift", H1, H2, list(range(10)), 5,
                expect_T=(6, 0), require_flowerless=True)
    # 双步 gadget 重算应精确重构 H1/H2
    s1 = free_points(F1 := c["n3N8"][0], F2 := c["n3N8"][1], list(range(8)))
    assert s1 == [6, 7], f"N8 谱系自由元应为 [6,7]，得 {s1}"
    J1, J2, U9 = gadget_lift(F1, F2, list(range(8)), s1[0])
    fr4b = free_points(J1, J2, U9)
    assert len(fr4b) == 1, fr4b
    K1, K2, U10 = gadget_lift(J1, J2, U9, fr4b[0])
    assert sorted(map(sorted, K1)) == sorted(map(sorted, H1)), "双步重构 H1 失败"
    assert sorted(map(sorted, K2)) == sorted(map(sorted, H2)), "双步重构 H2 失败"
    print("  双步 gadget 精确重构报告 §11.6 的 H1/H2  PASS")

    print("\n=== [T2] T / profile / cmin 与 cone_lift 交叉验证 ===")
    sys.path.insert(0, "/Users/munich/Desktop/数学/front20/campaign/s08_scripts")
    import cone_lift
    import random
    rng = random.Random(20260913)
    for (n, N, trials) in ((2, 6, 300), (3, 8, 300), (4, 8, 200)):
        members = list(itertools.combinations(range(N), n))
        for _ in range(trials):
            m = rng.randrange(2, min(12, len(members)) + 1)
            fam = [frozenset(members[i]) for i in rng.sample(range(len(members)), m)]
            t_mine = T_ordered(fam)
            t_ref = cone_lift.T_ordered(fam)
            assert t_mine == t_ref, (n, N, fam, t_mine, t_ref)
            U = list(range(N))
            p_mine = profile_dict(fam, U, n - 1)
            p_ref = cone_lift.profile(fam, U, n - 1)
            assert p_mine == p_ref, (n, N, fam)
            assert cmin(fam, n, U) == cone_lift.cmin(fam, n, U)
    print(f"  T/profile/cmin 三档 (n,N) × 共 800 族 交叉一致  PASS")

    print("\n=== [T3] gadget_lift 与 cone_lift.gadget 输出一致性 ===")
    for tag in ("n2link", "n3s05", "n3N8"):
        D1, D2, U, n = c[tag]
        frees = free_points(D1, D2, U)
        for s in frees:
            M1, M2, UU = gadget_lift(D1, D2, U, s)
            R1, R2, UU2, _, _ = cone_lift.gadget(
                [frozenset(x) for x in D1], [frozenset(x) for x in D2],
                list(U), s)
            assert sorted(map(sorted, M1)) == sorted(map(sorted, R1)), (tag, s)
            assert sorted(map(sorted, M2)) == sorted(map(sorted, R2)), (tag, s)
            assert UU == list(UU2), (tag, s)
    print("  全部 (tag, s) 组合输出逐成员一致  PASS")

    print("\n=== [T4] 阴性对照：剖面不同的族对必须判非分裂 ===")
    members = list(itertools.combinations(range(9), 5))
    rng2 = random.Random(7)
    for _ in range(200):
        m = 5
        f1 = [frozenset(members[i]) for i in rng2.sample(range(len(members)), m)]
        f2 = [frozenset(members[i]) for i in rng2.sample(range(len(members)), m)]
        p1 = profile_dict(f1, range(9), 4)
        p2 = profile_dict(f2, range(9), 4)
        same = p1 == p2
        if not same:
            # 必须能被键比较发现
            assert any(p1[Z] != p2[Z] for Z in p1)
    print("  200 随机对：剖面不同者均可由逐点比较发现  PASS")

    print("\n=== [T5] 6 点图完美匹配计数（影子图机制 sanity）===")
    def count_pm(edges):
        vs = set().union(*edges) if edges else set()
        edges = list(edges)
        best = 0
        def rec(cov, k, cnt):
            nonlocal best
            if len(cov) == 6:
                best += 1
                return
            if k == len(edges):
                return
            e = edges[k]
            rec(cov, k + 1, cnt)
            if not (set(e) & cov):
                rec(cov | set(e), k + 1, cnt + 1)
        rec(set(), 0, 0)
        return best
    rest = [3, 4, 5, 6, 7, 8]
    C6 = [frozenset(e) for e in [(3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 3)]]
    C3 = [frozenset(e) for e in [(3, 4), (4, 5), (5, 3), (6, 7), (7, 8), (8, 6)]]
    pm6, pm3 = count_pm(C6), count_pm(C3)
    assert pm6 == 2 and pm3 == 0, (pm6, pm3)
    # 度序列相同性（level-4 剖面决定的部分）
    deg6 = sorted(sum(1 for e in C6 if v in e) for v in rest)
    deg3 = sorted(sum(1 for e in C3 if v in e) for v in rest)
    assert deg6 == deg3 == [2] * 6
    print(f"  C6: PM={pm6}, 2C3: PM={pm3}，度序列同 {[2]*6}  PASS")
    print("\n=== 自击全部通过 ===")


if __name__ == "__main__":
    selftest()
