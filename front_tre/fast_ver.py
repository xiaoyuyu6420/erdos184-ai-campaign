#!/usr/bin/env python3
"""向量化加速版（与 fre_lib 中已锚定版本交叉验证后用于全量扫描）：
  - f_re_exact_fast: 子集 DP 全向量化（m ≤ 20）
  - p_odd_fast: 度量闭包 + networkx 最大权匹配（Edmonds 花算法，精确）
"""
import sys
sys.path.insert(0, '/Users/munich/Desktop/数学/front_tre')
import numpy as np
import networkx as nx
from fre_lib import Graph, min_tjoin


def f_re_exact_fast(g):
    """精确 f_re（定理 R 的 DP 实现，向量化）。
    f_re = min over 偶子图 H⊆G of ( m-|H| + Δ(H)/2 )。"""
    m, n = g.m, g.n
    assert m <= 22  # n=14 cubic 有 m=21；2^22*14 int8 ≈ 59MB 可承受
    N = 1 << m
    col = np.zeros((m, n), dtype=np.int8)
    for i, (u, v) in enumerate(g.edges):
        col[i][u] = 1
        col[i][v] = 1
    degA = np.zeros((N, n), dtype=np.int8)
    par = np.zeros(N, dtype=np.int64)
    epar = np.array([ (1 << u) | (1 << v) for u, v in g.edges], dtype=np.int64)
    for i in range(m):
        step = 1 << i
        # 所有含位 i 的 S: S = hi*2^(i+1) + step + r, r < step
        idx = (np.arange(N // (step << 1), dtype=np.int64) * (step << 1) + step)[:, None] + \
              np.arange(step, dtype=np.int64)[None, :]
        idx = idx.reshape(-1)
        degA[idx] += col[i]
        par[idx] ^= epar[i]
    sz = np.zeros(N, dtype=np.int16)
    for i in range(m):
        step = 1 << i
        idx = (np.arange(N // (step << 1), dtype=np.int64) * (step << 1) + step)[:, None] + \
              np.arange(step, dtype=np.int64)[None, :]
        sz[idx.reshape(-1)] += 1
    maxH = degA.astype(np.int16).max(axis=1)
    cand = np.nonzero(par == 0)[0]
    vals = (m - sz[cand]).astype(np.int32) + (maxH[cand].astype(np.int32) // 2)
    j = int(np.argmin(vals))
    return int(vals[j]), int(cand[j])


def p_odd_fast(g):
    """最小奇宇称生成子图边数 = min T-join (T=V) = 度量闭包最小权完美匹配。"""
    D = g.dist_matrix()
    H = nx.Graph()
    for u in range(g.n):
        for v in range(u + 1, g.n):
            if D[u][v] != float('inf'):
                H.add_edge(u, v, weight=-D[u][v])  # 取负做最大权
    M = nx.max_weight_matching(H, maxcardinality=True)
    assert len(M) == g.n // 2, "完美匹配不存在（不应发生：连通偶阶图的全点 T-join 总存在）"
    return sum(D[u][v] for u, v in M)


def parse_geng_line(line):
    """解析 geng graph6 行 → (n, 边列表)。"""
    s = line.strip()
    n = ord(s[0]) - 63
    if n > 62:
        n = ((ord(s[0]) - 63) << 12) + ((ord(s[1]) - 63) << 6) + (ord(s[2]) - 63)
        bits = s[3:]
    else:
        bits = s[1:]
    data = [ord(c) - 63 for c in bits]
    k = 0
    edges = []
    for j in range(1, n):
        for i in range(j):
            if data[k // 6] >> (5 - k % 6) & 1:
                edges.append((i, j))
            k += 1
    return n, edges


if __name__ == '__main__':
    """交叉验证：快速版 vs 已锚定蛮力版。"""
    from fre_lib import complete_graph, petersen, cycle_graph, path_graph, star, p_odd, f_re_exact
    import random
    sys.setrecursionlimit(100000)

    def dbl_sub_k4():
        e = [(0,1),(0,2),(1,2),(1,3),(2,3),(3,4),(4,0)]
        f = [(5+u, 5+v) for (u,v) in [(0,1),(0,2),(1,2),(1,3),(2,3),(3,4),(4,0)]]
        return Graph(10, e + f + [(4,9)], "double-subdiv-K4")

    ok = True
    tests = [complete_graph(4), petersen(), complete_graph(6), dbl_sub_k4()]
    # 随机 5-正则 n=8 图（全部 3 个）
    import subprocess, itertools
    out = subprocess.run(['geng', '-c', '-d5', '-D5', '8'], capture_output=True, text=True).stdout
    cnt = 0
    for line in out.splitlines():
        n, edges = parse_geng_line(line)
        tests.append(Graph(n, edges, f"geng5reg8-{cnt}")); cnt += 1
    for g in tests:
        a = p_odd(g); b = p_odd_fast(g)
        if a != b:
            ok = False
            print(f"[FAIL] p {g.name}: brute {a} vs fast {b}")
        if g.m <= 16:
            c = f_re_exact(g)[0]; d = f_re_exact_fast(g)[0]
            if c != d:
                ok = False
                print(f"[FAIL] f_re {g.name}: slow {c} vs fast {d}")
    # geng 随机 5-正则 n=12 抽 40 张做 p 交叉验证
    out = subprocess.run(['geng', '-c', '-d5', '-D5', '12'], capture_output=True, text=True).stdout
    lines = out.splitlines()
    random.seed(20260913)
    for line in random.sample(lines, 40):
        n, edges = parse_geng_line(line)
        g = Graph(n, edges)
        a = p_odd(g); b = p_odd_fast(g)
        if a != b:
            ok = False
            print(f"[FAIL] p (5reg12): brute {a} vs fast {b}")
    print("=== 快速版交叉验证", "全部通过 ===" if ok else "存在失败 !!! ===")
    sys.exit(0 if ok else 1)
