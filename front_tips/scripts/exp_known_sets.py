#!/usr/bin/env python3
"""
实验1：已知整距离点集（KK2008 两枚七点 + front213 六点）的「水平结构」剖析。

对点集 P、最小距离对 (p,q)（距离 d）：
  每个其它点 x 有整数水平 m_x = |xp|-|xq| （|m_x| <= d-1，无三点共线保证）
  与 z_x = |xp|+|xq|。
理论预测（本次攻击推导）：
  (i)  特征条件：sf((z^2-d^2)(d^2-m^2)) = kappa（集合特征）对每点成立；
  (ii) 在「除 |pq| 外全部距离 > 4d^2」的远散布假设下，每对中心对称双曲弧
       {(m,+),(-m,-)} / {(m,-),(-m,+)} 至多 1 点，从而 n <= 3 + 2*rho，
       rho = #不同的 |m|。
已知点集不满足远散布假设，因此可观察 (ii) 的占用是否被打破（镜子对等）。

纯矩阵算术（无需坐标），完全可复算。
"""
import math
from math import isqrt

MATRIX_1 = [  # KK2008 七点, 直径 22270, 特征 2002
    [0, 22270, 22098, 16637, 9248, 8908, 8636],
    [22270, 0, 21488, 11397, 15138, 20698, 13746],
    [22098, 21488, 0, 10795, 14450, 13430, 20066],
    [16637, 11397, 10795, 0, 7395, 11135, 11049],
    [9248, 15138, 14450, 7395, 0, 5780, 5916],
    [8908, 20698, 13430, 11135, 5780, 0, 10744],
    [8636, 13746, 20066, 11049, 5916, 10744, 0],
]
MATRIX_2 = [  # KK2008 七点, 直径 66810, 特征 2002
    [0, 66810, 66555, 66294, 49928, 41238, 40290],
    [66810, 0, 32385, 64464, 32258, 25908, 52020],
    [66555, 32385, 0, 34191, 16637, 33147, 33405],
    [66294, 64464, 34191, 0, 34322, 53244, 26724],
    [49928, 32258, 16637, 34322, 0, 20066, 20698],
    [41238, 25908, 33147, 53244, 20066, 0, 32232],
    [40290, 52020, 33405, 26724, 20698, 32232, 0],
]
# front213 发现的 D=174 六点（results/hexagon_D174.json，特征 2002）：
# 底边 v1=(0,0), v2=(174,0)，其余 4 点由整坐标 u=2Dx, w=√(T/κ) 给出，
# 距离^2 = (Δu^2 + κΔw^2)/(2D)^2。此处从 JSON 精确重建距离矩阵。
def build_matrix_hex174():
    import json
    D, kappa = 174, 2002
    rec = json.load(open("/Users/munich/Desktop/数学/lab/front213/results/hexagon_D174.json"))
    assert rec["D"] == D and rec["k"] == kappa
    L = 2 * D
    pts = [(0, 0), (L * D, 0)]  # 缩放坐标 (Lx, L·y/√κ)：v2 的 Lx = L·D
    pts += [(rec["u"][i], rec["w_signed"][i]) for i in range(4)]
    n = len(pts)
    M = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            du = pts[i][0] - pts[j][0]
            dw = pts[i][1] - pts[j][1]
            dist2 = (du * du + kappa * dw * dw) // (L * L)
            r = isqrt(dist2)
            assert r * r == dist2, f"非整距离: {i},{j}, {dist2}"
            M[i][j] = M[j][i] = r
    return M


MATRIX_HEX = build_matrix_hex174()


def sf(n: int) -> int:
    """平方核（squarefree kernel / squarefree part 的无符号版本）。n>=1"""
    assert n > 0
    r, m = 1, n
    p = 2
    while p * p <= m:
        cnt = 0
        while m % p == 0:
            m //= p
            cnt ^= 1
        if cnt:
            r *= p
        p = 3 if p == 2 else p + 2
    if m > 1:
        r *= m
    return r


def char_of_triangle(a: int, b: int, c: int) -> int:
    """三角形 (a,b,c) 的特征 = sf((a+b+c)(a+b-c)(a-b+c)(-a+b+c))"""
    f1, f2, f3, f4 = a + b + c, a + b - c, a - b + c, -a + b + c
    for f in (f1, f2, f3, f4):
        assert f > 0, "退化三角形"
    return sf(f1 * f2 * f3 * f4)


def analyze(M, name, expect_kappa=None):
    n = len(M)
    # 全对距离整性 + 一致性
    for i in range(n):
        for j in range(i + 1, n):
            assert M[i][j] == M[j][i] > 0
    # 所有三角形的特征
    kappas = set()
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                kappas.add(char_of_triangle(M[i][j], M[i][k], M[j][k]))
    assert len(kappas) == 1, f"{name}: 特征不唯一: {kappas}"
    kappa = kappas.pop()
    # 最小距离对
    d, pair = min((M[i][j], (i, j)) for i in range(n) for j in range(i + 1, n))
    # 次小距离
    dists = sorted(M[i][j] for i in range(n) for j in range(i + 1, n))
    M2 = dists[1]
    p, q = pair
    print(f"=== {name}: n={n}, kappa={kappa} (期望 {expect_kappa}), "
          f"最小距离 d={d} (点对 {pair}), 次小 M2={M2}")
    if expect_kappa is not None:
        assert kappa == expect_kappa
    # 水平结构
    rows = []
    for x in range(n):
        if x in (p, q):
            continue
        r, s = M[x][p], M[x][q]
        m, z = r - s, r + s
        T = (z * z - d * d) * (d * d - m * m)
        k = sf(T)
        rows.append((x, r, s, m, z, k))
        ok = "OK" if k == kappa else "**违背特征条件**"
        print(f"  点{x}: r=|xp|={r}, s=|xq|={s}, m={m:+d}, z={z}, "
              f"|m|={abs(m)}, sf((z^2-d^2)(d^2-m^2))={k} {ok}")
        assert k == kappa, "理论(i)失败"
        assert abs(m) <= d - 1, "水平越界（应被无三点共线排除）"
    rho = len({abs(m) for (_, _, _, m, _, _) in rows})
    mult = {}
    for (_, _, _, m, _, _) in rows:
        mult[abs(m)] = mult.get(abs(m), 0) + 1
    print(f"  rho(#不同|m|) = {rho};  各|m|重数 {dict(sorted(mult.items()))}")
    print(f"  界 n<=3+2rho: {n} <= {3+2*rho} -> {n <= 3+2*rho}; "
          f"线性界 n<=2d+1: {n} <= {2*d+1} -> {2*d+1}")
    print(f"  远散布假设(其余距离>4d^2): M2={M2} vs 4d^2={4*d*d} -> "
          f"{'成立' if M2 > 4*d*d else '不成立(引理6.1假设失效区间)'}")
    return d, M2, kappa, rho


if __name__ == "__main__":
    analyze(MATRIX_1, "KK2008-heptagon-22270", expect_kappa=2002)
    analyze(MATRIX_2, "KK2008-heptagon-66810", expect_kappa=2002)
    analyze(MATRIX_HEX, "front213-hexagon-D174", expect_kappa=2002)
    # 自击：sf 与 char 的健全性
    assert sf(1) == 1 and sf(8) == 2 and sf(12) == 3 and sf(2002) == 2002
    assert char_of_triangle(3, 4, 5) == 1 and char_of_triangle(6, 5, 5) == 1
    # (6,5,5) 镜子对距离 = sqrt(T)/d = 48/6 = 8，整风筝、特征 1（正文反例用）
    print("自击测试通过: sf/char_of_triangle")
