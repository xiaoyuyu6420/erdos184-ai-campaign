"""validate2.py — 完整验证（锚定向量 + Δ统计闭式 + 特殊格指认 + 互斥性检查）"""
import sys
sys.path.insert(0, '/Users/munich/Desktop/数学/front_tlat')
from latpack import *

ANCHORS = [('G',26,1), ('H',20,1), ('H',20,2), ('H',28,1), ('H',28,2),
           ('X',28,1), ('X',28,2), ('X',28,3), ('X',32,1), ('X',32,2), ('X',32,3)]

print("== B'. 锚定向量（与我的方阵逐 entry 一致的那部分）==")
for key in ANCHORS:
    T = PAPER_TS[key]
    ok, msg = is_transversal(key[0], key[1], T)
    print(f"  {key}: {'PASS' if ok else 'FAIL ' + msg}")
    assert ok

print("== C'. 论文声称的 disjoint 对（在自洽向量范围内）==")
for fam, n in [('H', 20), ('H', 28)]:
    T1, T2 = PAPER_TS[(fam,n,1)], PAPER_TS[(fam,n,2)]
    assert not (set(T1) & set(T2))
    print(f"  {fam}_{n}: T1∩T2=∅ ✓")
ts = [set(PAPER_TS[('X',28,i)]) for i in (1,2,3)]
print(f"  X_28 三条公共 entry: {ts[0]&ts[1]&ts[2]} (应为空)")
assert not (ts[0]&ts[1]&ts[2])
ts = [set(PAPER_TS[('X',32,i)]) for i in (1,2,3)]
print(f"  X_32 三条公共 entry: {ts[0]&ts[1]&ts[2]} (应为空)")
assert not (ts[0]&ts[1]&ts[2])
# X_28 三条各自包含哪些特殊格
spX = SPECIALS['X']
for i in (1,2,3):
    T = set(PAPER_TS[('X',28,i)])
    print(f"  X_28 T{i} 含特殊格: {[e for e in spX if e in T]}")

print("== D'. 分段规则互斥性（不同规则若同时命中必须给同值）==")
def conflicts(fam, n):
    d = FAMILIES[fam][0]
    bad = []
    # 暴力：对每个格子，删除单条规则重算，若值改变说明该规则是唯一命中——
    # 更直接：重新实现每条规则并收集所有命中的 (rule_id, delta)
    return bad  # 在下方以逐规则方式检查 G/H/X

import latpack
def rule_hits_G(r, c, n):
    k = (n-2)//4; a, b = r, c
    hits = []
    if a in (0,5,10) and b%4==1 and b>a+1: hits.append((1,4))
    if (a,b) in {(5,3),(10,3),(10,7)}: hits.append((2,4))
    if (a,b) in {(1,2),(6,6),(11,10)}: hits.append((3,3))
    if (a,b) in {(0,3),(0,4),(5,7),(5,8),(10,11),(10,12),(15,12),(15,13),(16,12)}: hits.append((4,1))
    if (a,b) in {(1,3),(1,4),(1,5),(6,7),(6,8),(6,9),(11,11),(11,12),(11,13),(16,13)}: hits.append((5,-1))
    if (a,b) in {(4,2),(4,5),(9,6),(9,9),(14,10),(14,13)}: hits.append((6,-3))
    if a in (4,9,14) and b%4==1 and b>a+1: hits.append((7,-4))
    if (a,b) in {(9,3),(14,3),(14,7)}: hits.append((8,-4))
    if a==15 and b%2==0 and b!=12: hits.append((9,2))
    if a==17 and b%2==0: hits.append((10,-2))
    if 18<=a<3*k-9 and a%3==0 and b%2==0: hits.append((11,2))
    if 18<=a<3*k-9 and a%3==2 and b%2==0: hits.append((12,-2))
    return hits

def rule_hits_H(r, c, n):
    k = n//4; a, b = r, c
    hits = []
    if a in (0,5,10) and b%4==1 and b-4*a//5!=1: hits.append((1,4))
    if (a,b) in {(1,1),(6,5),(11,9)}: hits.append((2,3))
    if a in (0,5,10) and 1<=b-4*a//5<=4: hits.append((3,1))
    if a in (1,6,11) and 2<=b-4*(a-1)//5<=4: hits.append((4,-1))
    if a in (4,9,14) and b%4==1: hits.append((5,-4))
    if 15<=a<4*k-21 and a%4==3 and b%2==0: hits.append((6,2))
    if 15<=a<4*k-21 and a%4==1 and b%2==0: hits.append((7,-2))
    return hits

def rule_hits_X(r, c, n):
    k = n//4; a, b = r, c
    hits = []
    if a in (0,4) and (b-a) in (1,5,8): hits.append((1,3))
    if a in (0,1) and 10<b and b%2==1: hits.append((2,2))
    if a in (4,5) and b%2==1 and b not in (5,7,9,11,13): hits.append((3,2))
    if a in (1,5) and (b-a) in (3,6,8): hits.append((4,2))
    if a==8 and b%2==1 and b!=13: hits.append((5,2))
    if 11<=a<3*k-10 and a%3==2 and b%2==1: hits.append((6,2))
    if a in (1,5) and (b-a) in (0,1,2,5): hits.append((7,1))
    if (a,b) in {(0,4),(2,3),(4,8),(6,7),(8,13),(8,14),(9,13)}: hits.append((8,1))
    if a in (2,6) and (b-a) in (0,4,7): hits.append((9,-1))
    if a in (3,7) and (b-a) in (1,2,5,6): hits.append((10,-1))
    if (a,b)==(9,14): hits.append((10.5,-1))
    if 11<=a<3*k-10 and a%3==1 and b%2==1: hits.append((11,-2))
    if a in (2,3) and b%2==1 and b!=9 and (a,b) not in {(2,3),(2,7),(3,5)}: hits.append((12,-2))
    if a in (6,7) and b%2==1 and b!=13 and (a,b) not in {(6,7),(6,11),(7,9)}: hits.append((13,-2))
    if a==10 and b%2==1: hits.append((14,-2))
    if a in (2,6) and (b-a) in (2,6): hits.append((15,-2))
    return hits

HITS = {'G': rule_hits_G, 'H': rule_hits_H, 'X': rule_hits_X}
for fam, ns in [('G',[22,30,38,50,102]), ('H',[20,24,32,36,44,100]), ('X',[28,32,36,40,100])]:
    nmax = max(ns)
    for n in ns:
        for r in range(n):
            for c in range(n):
                hits = HITS[fam](r,c,n)
                vals = set(v for _,v in hits)
                assert len(vals) <= 1, (fam,n,r,c,hits)
        print(f"  {fam}_{n}: 所有格子多规则命中时值一致 ✓")

print("== D''. Δ-统计闭式比对（作者由他们方阵算出的和，必须匹配我的方阵）==")
print("  G_n (4k+2): 理论 Σmin = -2k 恰确; Σmax(原始) = 2k+6; ≤1特殊时 Σmax ≤ 2k")
for k in range(9, 26):
    n = 4*k+2
    st = row_stats('G', n)
    smin = sum(s[1] for s in st); smax = sum(s[0] for s in st)
    assert smin == -2*k, (n, smin)
    assert smax == 2*k+6, (n, smax)
    # k-8 行的行最大 = 2 (行15 + 周期区 a≡0 mod 3 行 k-9 个)
    nrows2 = sum(1 for s in st if s[0] == 2)
    assert nrows2 == k-8, (n, nrows2)
    assert sum(1 for s in st if s[0]==4) == 3
    assert sum(1 for s in st if s[0]==3) == 3
    # 行 4,9,14 的行最大 = 0（有 -3/-4 格但其余格为 0）
    for r in (4, 9, 14):
        assert st[r][0] == 0 and st[r][1] == -4, (n, r, st[r])
    # 行 1,6,11 去掉特殊格后行最大 = 0
    for r in (1, 6, 11):
        mxcols_wo = [c for c in st[r][4] if (r, c) not in {(1,2),(6,6),(11,10)}]
        d = FAMILIES['G'][0]
        assert all(d(r, c, n) <= 0 for c in range(n) if c not in st[r][4]), (n, r)
print("  G_n: 全部吻合 (k=9..25)")
print("  H_n (4k): 理论 Σmin = -2k+3; Σmax(原始)=2k+3; ≤1特殊时 Σmax ≤ 2k-3")
for k in range(9, 26):
    n = 4*k
    st = row_stats('H', n)
    smin = sum(s[1] for s in st); smax = sum(s[0] for s in st)
    assert smin == -2*k+3, (n, smin)
    assert smax == 2*k+3, (n, smax)
    assert sum(1 for s in st if s[0]==2) == k-9, (n,)
    assert sum(1 for s in st if s[1]==-2) == k-9
    assert sum(1 for s in st if s[0]==4) == 3
    assert sum(1 for s in st if s[0]==3) == 3
print("  H_n: 全部吻合 (k=9..25)")
print("  X_n (4k,k>=7): Σmin = -2k+3; Σmax = 2k+1; 行2/6/9 行最大唯一")
for k in range(7, 26):
    n = 4*k
    st = row_stats('X', n)
    smin = sum(s[1] for s in st); smax = sum(s[0] for s in st)
    assert smin == -2*k+3, (n, smin)
    assert smax == 2*k+1, (n, smax)
    sp = SPECIALS['X']
    for ri, r in enumerate((2,6,9)):
        mx, mn, nmx, nmn, mxcols, mncols = st[r]
        assert nmx == 1 and mxcols == [sp[ri][1]] and mx == 1, (n, r, st[r])
    assert sum(1 for s in st if s[0]==2) == k-4, (n,)
print("  X_n: 全部吻合 (k=7..25)")

print("== E. 特殊格 Δ 值核验 ==")
for fam, ns in [('G',[38,42,50]), ('H',[36,40,48]), ('X',[28,32,36])]:
    d = FAMILIES[fam][0]
    for n in ns:
        for (r,c,s) in SPECIALS[fam]:
            v = d(r,c,n)
            expect = 3 if fam in 'GH' else 1
            assert v == expect, (fam,n,r,c,v)
print("  特殊格 Δ 值全部正确 (G/H: Δ=3; X: Δ=1=行最大)")
print("ALL VALIDATION PASSED")
