"""定理 M2 构造证书生成器: 对任意 c 生成 E + d*C1 + e*D 分解并逐边核对。
用法: python3 cert_gc.py c1 c2 ...  (缺省 5..12)
输出: 每个圈的边表 + 单边表 + 覆盖/部件数核对。"""
import sys, math
from ce_solver import edge_index, enumerate_edges

def edges_of_cycle(c, cyc_type, vs):
    """返回圈型对应的叶子-边使用 (用 (u,v) 顶点对); x=0,y=1,w1=2, 叶=v"""
    x, y, w1 = 0, 1, 2
    if cyc_type == 'E':   # x-y-w1-x
        return [(x,y), (y,w1), (w1,x)]
    if cyc_type == 'C1':  # y-w_i-w_1-w_j-y
        i, j = vs
        return [(y,i), (i,w1), (w1,j), (j,y)]
    if cyc_type == 'D':   # x-w_i-w_1-w_j-y-w_k-x
        i, j, k = vs
        return [(x,i), (i,w1), (w1,j), (j,y), (y,k), (k,x)]

for c in [int(a) for a in (sys.argv[1:] or ['5','6','7','8','9','10','11','12'])]:
    n = c + 2
    eidx = edge_index(n)
    kappa = math.ceil((c+2)/3)
    d, e = 3*kappa - c - 2, c + 1 - 2*kappa
    leaves = list(range(2+1, 2+1 + (c-1)))   # w_2..w_c = 顶点 3..c+1
    fam = [('E', None)]
    idx = 0
    for _ in range(d):
        fam.append(('C1', (leaves[idx], leaves[idx+1]))); idx += 2
    for _ in range(e):
        fam.append(('D', tuple(leaves[idx:idx+3]))); idx += 3
    all_edges = {(0,1)} | {(0, 1+i) for i in range(1, c+1)} | {(1, 1+i) for i in range(1, c+1)} | {(2, 1+j) for j in range(2, c+1)}
    used = set()
    print(f'--- c={c} (n={n}, m={3*c}): kappa={kappa}, d={d}, e={e} ---')
    for t, vs in fam:
        el = edges_of_cycle(c, t, vs)
        ce = {(min(u,v), max(u,v)) for u,v in el}
        assert not (ce & used), f'边冲突! {t} {vs}'
        used |= ce
        print(f'  {t}: {sorted(ce)}')
    singles = sorted(all_edges - used)
    assert not (used - all_edges), '用了不存在的边'
    parts = len(fam) + len(singles)
    formula = c - 1 + kappa
    print(f'  单边 {len(singles)} 条: {singles}')
    print(f'  部件 = {len(fam)} 圈 + {len(singles)} 单边 = {parts}; 公式 c-1+ceil((c+2)/3) = {formula}: {"✓" if parts == formula else "✗✗"}')
    assert parts == formula
print('全部构造证书核对通过')
