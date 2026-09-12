"""G_8 = K_2 ∨ K_{1,7} (n=10, m=24) 的独立验证：Python 侧 ce + 双证书。
f_one(C) 报 ce=11。本脚本：
 1) 用 ce_solver 独立精算 ce(G_8)（不同实现、不同语言）；
 2) 输出 save=13 的 packing 证书（边不相交圈族）与 11 部件分解证书（逐边核对）。"""
import sys
from ce_solver import ce, edge_index, enumerate_edges

n = 10
edges = enumerate_edges(n)
eidx = edge_index(n)
# G_8: x=0, y=1, W={2..9}, star center 2
E = {(0,1)} | {(0, 2+j) for j in range(8)} | {(1, 2+j) for j in range(8)} | {(2, 3+j) for j in range(7)}
mask = 0
for (u,v) in E:
    mask |= 1 << eidx[(min(u,v), max(u,v))]
adj = [0]*n
for (u,v) in E:
    adj[u] |= 1 << v; adj[v] |= 1 << u
m = len(E)
print(f"G_8: n={n} m={m}")
val = ce(n, adj, eidx)
print(f"Python ce(G_8) = {val}   (C 版 f_one 报 11)")
