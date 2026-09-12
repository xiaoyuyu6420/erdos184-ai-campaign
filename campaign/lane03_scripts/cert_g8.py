"""G_8 = K_2∨K_{1,7} 双证书：save=13 的最优边不相交圈族 + 11 部件分解（逐边核对）。"""
import sys
from ce_solver import edge_index, enumerate_edges, all_simple_cycles, graph_to_adj
sys.setrecursionlimit(1 << 20)

n = 10
eidx = edge_index(n)
E = {(0,1)} | {(0, 2+j) for j in range(8)} | {(1, 2+j) for j in range(8)} | {(2, 3+j) for j in range(7)}
adj = graph_to_adj(n, sorted(E))
m = len(E)
FULL = 0
for (u,v) in E: FULL |= 1 << eidx[(min(u,v),max(u,v))]

cycles = all_simple_cycles(n, adj, eidx)
cyc = sorted(cycles, key=lambda c: (-(c[1]-1), c[1]))
em = [c[0] for c in cyc]; sv = [c[1]-1 for c in cyc]
memo = {}
def dfs(i, rem):
    if i == len(cyc) or rem == 0: return (0, [])
    key = (rem, i)
    v = memo.get(key)
    if v: return v
    b1 = dfs(i+1, rem)
    best = b1
    if em[i] & rem == em[i]:
        s2, p2 = dfs(i+1, rem & ~em[i])
        cand = (sv[i] + s2, [i] + p2)
        if cand > best: best = cand
    memo[key] = best
    return best
save, pick = dfs(0, FULL)
print(f"最优 packing: save = {save} (目标 13), {len(pick)} 个圈")
used = 0
for i in pick:
    msk = em[i]
    used |= msk
    # 解码圈顶点序列
    es = [e for e,(bit) in enumerate_edges(n).__iter__()] # placeholder
    elist = []
    for (u,v) in enumerate_edges(n):
        if msk >> eidx[(u,v)] & 1: elist.append((u,v))
    print(f"  圈长 {len(elist)}: {elist}")
singles = []
for (u,v) in enumerate_edges(n):
    if (FULL >> eidx[(u,v)] & 1) and not (used >> eidx[(u,v)] & 1):
        singles.append((u,v))
# 覆盖核对：packing 边 ∪ 单边 = 全边集, 两两不交
allcov = used | sum(1 << eidx[(u,v)] for (u,v) in singles)
parts = len(pick) + len(singles)
print(f"分解: {len(pick)} 圈 + {len(singles)} 单边 = {parts} 部件; 覆盖核对: {'OK' if allcov == FULL else 'FAIL'} (m={m})")
assert save == 13 and parts == 11 and allcov == FULL
print("G_8 证书全部核对通过: save=13, ce = 24-13 = 11")
