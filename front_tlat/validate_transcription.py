"""validate_transcription.py — 转录验证：Latin 性 + 论文测试向量 + Δ-统计量"""
import sys
sys.path.insert(0, '/Users/munich/Desktop/数学/front_tlat')
from latpack import *

print("=" * 70)
print("A. Latin 性检验")
for fam, ns in [('G', [18, 22, 26, 30, 34, 38, 42, 50, 62, 82, 102, 202]),
                ('H', [16, 20, 24, 28, 32, 36, 40, 44, 52, 64, 84, 104, 204]),
                ('X', [28, 32, 36, 40, 44, 56, 72, 92, 112, 212])]:
    for n in ns:
        check_latin(fam, n)
    print(f"  {fam}: Latin OK for n in {ns}")
print("  方阵本身同时核对了 |delta|<=4 与中心代表元唯一性（由定义直接成立）")

print("=" * 70)
print("B. 论文显式 transversal 测试向量")
for (fam, n, t), T in sorted(PAPER_TS.items()):
    ok, msg = is_transversal(fam, n, T)
    print(f"  {fam}_{n} #{t}: {'PASS' if ok else 'FAIL: ' + msg}")
    assert ok, msg

print("=" * 70)
print("C. 论文声称的 disjoint 对（小 n 构造失败的证据）")
for (fam, ns) in [('G', [22, 26, 30, 34]), ('H', [20, 24, 28])]:
    for n in ns:
        T1, T2 = PAPER_TS[(fam, n, 1)], PAPER_TS[(fam, n, 2)]
        inter = set(T1) & set(T2)
        assert not inter, (fam, n, inter)
        print(f"  {fam}_{n}: T1 ∩ T2 = ∅  ✓ (构造在阈值以下确有 disjoint 对)")
# X_28 / X_32 三条: 交为空
for n in (28, 32):
    ts = [set(PAPER_TS[('X', n, i)]) for i in (1, 2, 3)]
    common = ts[0] & ts[1] & ts[2]
    print(f"  X_{n}: 三条 transversal 的公共 entry 数 = {len(common)} (论文声称 0)")
    assert len(common) == 0

print("=" * 70)
print("D. Δ-统计量与引理声称的一致性")
for fam, k, claim in [('G', 9, 'n=38: 每 transversal 含 >=2 个 Delta=3 特殊格'),
                      ('G', 12, 'n=50'), ('H', 9, 'n=36'), ('H', 12, 'n=48'), ('X', 7, 'n=28'), ('X', 9, 'n=36')]:
    n = {'G': lambda: 4 * k + 2, 'H': lambda: 4 * k, 'X': lambda: 4 * k}[fam]()
    L = make_square(fam, n)
    d = FAMILIES[fam][0]
    # Delta 范围
    allv = [d(r, c, n) for r in range(n) for c in range(n)]
    rng = (min(allv), max(allv))
    # 特殊格指认
    sp = SPECIALS[fam]
    for (r, c, s) in sp:
        assert L[r][c] == s, (fam, n, r, c, s, L[r][c])
    if fam in ('G', 'H'):
        d3 = [(r, c) for r in range(n) for c in range(n) if d(r, c, n) == 3]
        assert sorted(d3) == sorted((r, c) for r, c, s in sp), (fam, n, d3)
        print(f"  {fam}_{n}: Δ∈{rng}; Δ=3 的格子恰为 {sorted(d3)} ✓")
    else:
        # X: 行 2,6,9 的行最大 Δ 唯一且为特殊格
        st = row_stats(fam, n)
        for r in (2, 6, 9):
            mx, mn, nmx, nmn, mxcols, mncols = st[r]
            assert nmx == 1 and mxcols == [sp[(2, 6, 9).index(r)][1]], (r, st[r])
        print(f"  {fam}_{n}: Δ∈{rng}; 行2/6/9 的行最大 Δ 格唯一 = {sp} ✓")

# 行 min/max 求和 vs 引理数值
print("-" * 70)
print("  行最大 Δ 之和 / 行最小 Δ 之和（引理 7/8/9 的两条关键和）")
for fam, kmin, kmax in [('G', 9, 13), ('H', 9, 13), ('X', 7, 13)]:
    for k in range(kmin, kmax + 1):
        n = 4 * k + 2 if fam == 'G' else 4 * k
        st = row_stats(fam, n)
        smax = sum(s[0] for s in st)
        smin = sum(s[1] for s in st)
        print(f"    {fam}_{n}: sum_max={smax}, sum_min={smin}, n/2={n/2}")
print("DONE all validations passed")
