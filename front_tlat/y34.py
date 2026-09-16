"""Y_34 (式12) 实现 + Lemma 10 验证 + 三条论文 transversal 验证"""
import sys
sys.path.insert(0, '.')
from latpack import is_transversal, row_stats

def delta_Y(r, c, n=34):
    a, b = r, c
    if a in (0,4,8) and (b-a) in (4,7,10): return 3
    if a in (0,4,8) and b%2==1 and (b-a) not in range(1,12): return 2
    if (a,b) in {(0,2),(4,6),(8,10),(1,0),(5,4),(9,8)}: return 2
    if a in (1,2,5,6,9,10) and b%2==0 and (b-a) not in range(-2,10): return 1
    if a in (0,2,4,6,8,10) and (b-a) == (1 if (a//2)%2==0 else -1): return 1
    if a in (1,2,5,6,9,10) and b%2==1 and (b-a) not in range(-1,11): return -1
    if a in (2,6,10) and (b-a)==0: return -1
    if a in (1,5,9) and (b-a) in (0,1): return -1
    if a in (3,7,11) and (b-a)==-2: return -1
    if a in (3,7,11) and b%2==0 and (b-a) not in range(-1,8): return -2
    if a in (3,7,11) and (b-a) in (1,4,7): return -3
    return 0

n = 34
L = [[(r+c+delta_Y(r,c))%n for c in range(n)] for r in range(n)]
for r in range(n): assert sorted(L[r])==list(range(n)), f"row {r}"
for c in range(n): assert sorted(L[r][c] for r in range(n))==list(range(n)), f"col {c}"
print("Y_34: Latin OK")
vals=[delta_Y(r,c) for r in range(n) for c in range(n)]
print("Delta range:", min(vals), max(vals), "(论文: -3..3)")
sp=[(1,0,3),(5,4,11),(9,8,19)]
for (r,c,s) in sp: assert L[r][c]==s, (r,c,s,L[r][c])
st=row_stats.__wrapped__('Y',34) if hasattr(row_stats,'__wrapped__') else None
# 手动行统计
mxs=[]; mns=[]
for r in range(n):
    v=[delta_Y(r,c) for c in range(n)]
    mxs.append(max(v)); mns.append(min(v))
print("Σmax =", sum(mxs), "(论文: 18=n/2+1)   Σmin =", sum(mns), "(论文: -15)")
assert sum(mxs)==18 and sum(mns)==-15
for (r,c,s) in sp:
    v=[delta_Y(r,cc) for cc in range(n)]
    assert v.count(max(v))==1 and v[c]==max(v), (r,"max不唯一")
print("行 1/5/9 的行最大 Δ 格唯一 =", sp)
T1=[(0,10,13),(1,20,22),(2,1,4),(3,27,30),(4,14,21),(5,4,11),(6,16,23),(7,29,2),(8,15,26),(9,8,19),(10,26,3),(11,33,10),(12,3,15),(13,28,7),(14,0,14),(15,13,28),(16,17,33),(17,12,29),(18,21,5),(19,24,9),(20,11,31),(21,30,17),(22,2,24),(23,23,12),(24,18,8),(25,25,16),(26,6,32),(27,7,0),(28,31,25),(29,32,27),(30,5,1),(31,9,6),(32,22,20),(33,19,18)]
T2=[(0,7,10),(1,0,3),(2,32,1),(3,6,9),(4,14,21),(5,28,0),(6,5,12),(7,15,22),(8,12,23),(9,8,19),(10,4,15),(11,27,4),(12,21,33),(13,18,31),(14,26,6),(15,13,28),(16,31,13),(17,1,18),(18,11,29),(19,22,7),(20,16,2),(21,33,20),(22,17,5),(23,9,32),(24,2,26),(25,20,11),(26,24,16),(27,3,30),(28,23,17),(29,19,14),(30,29,25),(31,30,27),(32,10,8),(33,25,24)]
T3=[(0,10,13),(1,0,3),(2,16,19),(3,25,28),(4,8,15),(5,4,11),(6,2,9),(7,31,4),(8,18,29),(9,32,8),(10,30,7),(11,5,16),(12,14,26),(13,11,24),(14,7,21),(15,12,27),(16,19,1),(17,23,6),(18,21,5),(19,17,2),(20,24,10),(21,13,0),(22,3,25),(23,28,17),(24,9,33),(25,6,31),(26,22,14),(27,29,22),(28,26,20),(29,1,30),(30,27,23),(31,15,12),(32,20,18),(33,33,32)]
for i,T in enumerate((T1,T2,T3),1):
    ok,msg=is_transversal('Y',34,T) if False else (None,None)
    # 手动独立验证
    rows={t[0] for t in T}; cols={t[1] for t in T}; syms={t[2] for t in T}
    assert len(T)==34 and len(rows)==34 and len(cols)==34 and len(syms)==34, f"T{i} 结构"
    bad=[(r,c,s) for (r,c,s) in T if (r+c+delta_Y(r,c))%34!=s]
    assert not bad, (i,bad)
    print(f"Y_34 T{i}: transversal PASS")
I12=set(T1)&set(T2); I13=set(T1)&set(T3); I=set(T1)&set(T2)&set(T3)
print(f"T1∩T2∩T3 = {I} (应为空);  |T1∩T2|={len(I12)}, |T1∩T3|={len(I13)}")
assert not I
spset=set(sp)
for i,T in enumerate((T1,T2,T3),1):
    print(f"  T{i} 含特殊格: {[e for e in sp if e in set(T)]}")
print("Y_34 全部验证通过")
