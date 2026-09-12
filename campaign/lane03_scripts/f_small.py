"""
f_small.py — 全枚举 n 点简单图，计算 f(n) = max ce(G)（n<=6 Python 精确）。
输出 f(n)、witness 图（边表）、f(n)/n 与 3n/2 的对照。
"""
import sys
from ce_solver import ce, edge_index, enumerate_edges, graph_to_adj

def run(n):
    eidx = edge_index(n)
    edges = enumerate_edges(n)
    E = len(edges)
    f_best = 0
    witnesses = []
    total = 1 << E
    for mask in range(total):
        adj = [0] * n
        m = 0
        for i, (u, v) in enumerate(edges):
            if mask >> i & 1:
                adj[u] |= 1 << v
                adj[v] |= 1 << u
                m += 1
        if m < f_best or m == 0:
            continue  # ce <= m < f_best
        val = ce(n, adj, eidx)
        if val > f_best:
            f_best = val
            witnesses = [(m, mask)]
        elif val == f_best:
            witnesses.append((m, mask))
    return f_best, witnesses

if __name__ == '__main__':
    for n in range(1, 7):
        f, ws = run(n)
        print(f"n={n}: f(n)={f}  f/n={f/n:.3f}  ceil(3n/2)={(3*n+1)//2}  witnesses={len(ws)}  示例边表:")
        # 打印最多 3 个 witness
        eidx = edge_index(n)
        edges = enumerate_edges(n)
        for m, mask in ws[:3]:
            el = [edges[i] for i in range(len(edges)) if mask >> i & 1]
            print(f"    m={m}: {el}")
