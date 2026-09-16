"""4-run 词 w = a^i b^u a^j b^v (i,j,u,v >= 1) 的 abelian square 完全分类公式（修正版）。

因子连续性 => 跨块因子只有 7 种形状（见报告推导）。混合 abelian square 恰为：

A. u 偶：a^t b^u a^t，1 <= t <= min(i,j)                       [split 在 b^u 内]
B. j 偶：b^c a^j b^c，1 <= c <= min(u,v)                       [split 在 a^j 内]
C. j <= i：a^j b^u a^j b^{v1}，v1 ∈ [1, min(v, u)]，v1 ≡ u (mod 2)
     [split 在 b^u 内：v1 = 2c - u, c ∈ [(u+1)/2, u] => v1 <= u]
D. u <= v：a^{i1} b^u a^j b^u，i1 ∈ [1, min(i,j)]，i1 ≡ j (mod 2)
     [split 在 a^j 内：v1 = u]
重叠：C ∩ D = {a^j b^u a^j b^u}，非空 ⟺ j <= i 且 u <= v。
"""


def theta_four_run(i, u, j, v):
    sq = set()
    for m in range(1, max(i, j) // 2 + 1):
        sq.add('a' * (2 * m))
    for m in range(1, max(u, v) // 2 + 1):
        sq.add('b' * (2 * m))
    if u % 2 == 0:
        for t in range(1, min(i, j) + 1):
            sq.add('a' * t + 'b' * u + 'a' * t)
    if j % 2 == 0:
        for c in range(1, min(u, v) + 1):
            sq.add('b' * c + 'a' * j + 'b' * c)
    if j <= i:
        for v1 in range(1, min(v, u) + 1):
            if v1 % 2 == u % 2:
                sq.add('a' * j + 'b' * u + 'a' * j + 'b' * v1)
    if u <= v:
        for i1 in range(1, min(i, j) + 1):
            if i1 % 2 == j % 2:
                sq.add('a' * i1 + 'b' * u + 'a' * j + 'b' * u)
    return len(sq)


def theta_four_run_count(i, u, j, v):
    """闭式计数版（集合版的对数校验）。"""
    cnt = max(i, j) // 2 + max(u, v) // 2
    if u % 2 == 0:
        cnt += min(i, j)
    if j % 2 == 0:
        cnt += min(u, v)
    c_cnt = len([v1 for v1 in range(1, min(v, u) + 1) if v1 % 2 == u % 2]) if j <= i else 0
    d_cnt = len([i1 for i1 in range(1, min(i, j) + 1) if i1 % 2 == j % 2]) if u <= v else 0
    ov = 1 if (j <= i and u <= v) else 0
    return cnt + c_cnt + d_cnt - ov


if __name__ == '__main__':
    import sys
    sys.path.insert(0, '.')
    from absq import theta_prefix
    lim = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    bad = bad2 = 0
    for i in range(1, lim + 1):
        for u in range(1, lim + 1):
            for j in range(1, lim + 1):
                for v in range(1, lim + 1):
                    g = theta_prefix('a' * i + 'b' * u + 'a' * j + 'b' * v)
                    f = theta_four_run(i, u, j, v)
                    c = theta_four_run_count(i, u, j, v)
                    if f != g:
                        bad += 1
                        if bad <= 5:
                            print('SET MISMATCH', (i, u, j, v), f, g)
                    if c != g:
                        bad2 += 1
                        if bad2 <= 5:
                            print('COUNT MISMATCH', (i, u, j, v), c, g)
    print(f'4-run 公式(集合版/闭式版) vs 计数器 i,u,j,v∈[1,{lim}]:',
          f'集合版 {"OK" if bad == 0 else str(bad)+" bad"}, 闭式版 {"OK" if bad2 == 0 else str(bad2)+" bad"}')
