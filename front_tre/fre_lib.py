#!/usr/bin/env python3
"""
front_tre 验证库：arXiv:2509.01901 Conjecture 6.4 (f_re ≤ n-1 for (2k+1)-regular graphs)

核心对象：
  - f_re(G): 把 G 分解为 2-正则子图与单边的最小块数（原文 §1 定义）
  - p(G):    最小奇宇称生成子图的边数（min T-join, T=V），仅对全奇度图 = 分解归约中的 F
  - ℓ(G):    边不交圈打包的最大总长；对奇正则图 ℓ = m - p
  - f_re_exact(G): 用子集 DP 精确计算 f_re（m ≤ 20 可行）

理论依据（详见 attack_tre.md）：
  定理 R（分解归约）: f_re(G) = min_{F: deg_F ≡ deg_G (mod 2)} ( |E(F)| + Δ(G-F)/2 )
  推论（奇正则）:     p(G) ≤ f_re(G) ≤ p(G) + k
  推论（立方）:       f_re(G) = p(G) + 1 = m - ℓ(G) + 1

所有实现自包含，仅依赖 numpy/networkx/scipy。
"""
import itertools
from collections import deque


class Graph:
    """简单图：n 顶点 (0..n-1)，边列表。"""
    def __init__(self, n, edges, name=""):
        self.n = n
        self.edges = [tuple(e) for e in edges]
        self.m = len(self.edges)
        self.name = name
        self.adj = [set() for _ in range(n)]
        for u, v in self.edges:
            assert u != v and 0 <= u < n and 0 <= v < n
            self.adj[u].add(v)
            self.adj[v].add(u)
        self.deg = [len(a) for a in self.adj]
        # 顶点的边掩码（位 i = 第 i 条边）
        self.vmask = [0] * n
        for i, (u, v) in enumerate(self.edges):
            self.vmask[u] |= 1 << i
            self.vmask[v] |= 1 << i

    def is_regular(self):
        return len(set(self.deg)) == 1

    def is_connected(self):
        if self.n == 0:
            return True
        seen = {0}
        dq = deque([0])
        while dq:
            u = dq.popleft()
            for v in self.adj[u]:
                if v not in seen:
                    seen.add(v)
                    dq.append(v)
        return len(seen) == self.n

    def bridges(self):
        """Tarjan 桥。返回边下标集合。"""
        n, adj = self.n, self.adj
        disc = [-1] * n
        low = [0] * n
        timer = [0]
        br = set()
        import sys
        sys.setrecursionlimit(10000)
        eid = {}
        for i, (u, v) in enumerate(self.edges):
            eid[(u, v)] = i; eid[(v, u)] = i
        def dfs2(u, pe):
            disc[u] = low[u] = timer[0]; timer[0] += 1
            for v in adj[u]:
                if disc[v] == -1:
                    dfs2(v, eid[(u, v)])
                    low[u] = min(low[u], low[v])
                    if low[v] > disc[u]:
                        br.add(eid[(u, v)])
                elif eid[(u, v)] != pe:
                    low[u] = min(low[u], disc[v])
        for s in range(n):
            if disc[s] == -1:
                dfs2(s, -1)
        return br

    def components(self):
        comp = [-1] * self.n
        c = 0
        for s in range(self.n):
            if comp[s] == -1:
                dq = deque([s]); comp[s] = c
                while dq:
                    u = dq.popleft()
                    for v in self.adj[u]:
                        if comp[v] == -1:
                            comp[v] = c; dq.append(v)
                c += 1
        return c, comp

    def dist_matrix(self):
        INF = float('inf')
        D = [[INF] * self.n for _ in range(self.n)]
        for s in range(self.n):
            D[s][s] = 0
            dq = deque([s])
            while dq:
                u = dq.popleft()
                for v in self.adj[u]:
                    if D[s][v] == INF:
                        D[s][v] = D[s][u] + 1
                        dq.append(v)
        return D


def min_tjoin(g, T):
    """最小 T-join（精确）：度量闭包 + T 上最小权完美匹配（蛮力枚举配对）。
    经典归约（Edmonds；见 Korte–Vygen《Combinatorial Optimization》T-join 一章）。
    返回 (最小边数, 配对列表)。要求 |T| 偶。"""
    T = sorted(T)
    assert len(T) % 2 == 0
    if not T:
        return 0, []
    D = g.dist_matrix()
    best = [None, None]  # (cost, pairing)
    k = len(T)
    used = [False] * k
    def pair(i, cost, acc):
        # 跳过已配对点；i == k 表示全部配完
        while i < k and used[i]:
            i += 1
        if i == k:
            if best[0] is None or cost < best[0]:
                best[0] = cost
                best[1] = list(acc)
            return
        if best[0] is not None and cost >= best[0]:
            return
        u = T[i]
        used[i] = True
        for j in range(i + 1, k):
            if not used[j]:
                v = T[j]
                d = D[u][v]
                if cost + d < (best[0] if best[0] is not None else float('inf')):
                    used[j] = True
                    acc.append((u, v))
                    pair(i + 1, cost + d, acc)
                    acc.pop()
                    used[j] = False
        used[i] = False
    pair(0, 0, [])
    return best[0], best[1]


def p_odd(g):
    """最小奇宇称生成子图边数（要求 g 全奇度）。= min T-join, T = V。"""
    assert all(d % 2 == 1 for d in g.deg), "p_odd 需要全奇度图"
    val, _ = min_tjoin(g, range(g.n))
    return val


def ell_from_p(g):
    """奇正则图：ℓ = m - p。"""
    return g.m - p_odd(g)


def parity_join_exists(g, T):
    """检查 T-join 存在（每个分量含偶数个 T 点）——调试用。"""
    _, comp = g.components()
    cnt = {}
    for v in T:
        cnt[comp[v]] = cnt.get(comp[v], 0) + 1
    return all(c % 2 == 0 for c in cnt.values())


def f_re_exact(g):
    """精确 f_re：枚举全部 H ⊆ E（H 偶图），f_re = min ( m-|H| + Δ(G-H)/2 )。
    由定理 R：F = G-H 满足 deg_F ≡ deg_G (mod 2)。m ≤ 20 可行。
    返回 (最优值, 最优 H 掩码)。"""
    m, n = g.m, g.n
    assert m <= 20, "子集 DP 需要 m ≤ 20"
    # 每条边的列：对每个顶点的度贡献
    # deg[v][S] 用 DP：sz/par/deg 数组
    N = 1 << m
    par = [0] * N        # 度奇偶掩码（位 v = 顶点 v 度的奇偶）
    sz = [0] * N
    # deg DP 用 numpy：degA[S] = int8 数组长度 n
    import numpy as np
    col = np.zeros((n, m), dtype=np.int8)
    for i, (u, v) in enumerate(g.edges):
        col[u][i] = 1
        col[v][i] = 1
    dG = np.array(g.deg, dtype=np.int16)
    degA = np.zeros((N, n), dtype=np.int8)
    # 标准 DP：degA[S] = degA[S \ {lowbit}] + col[lowbit]
    lowbit = [0] * N
    for S in range(1, N):
        lb = (S & -S)
        lowbit[S] = lb.bit_length() - 1
        i = lowbit[S]
        degA[S] = degA[S ^ lb] + col[:, i]
        sz[S] = sz[S ^ lb] + 1
        par[S] = par[S ^ lb] ^ ((1 << g.edges[i][0]) | (1 << g.edges[i][1]))
    best = (float('inf'), 0)
    for S in range(N):
        if par[S] == 0:  # H = 边集 S 是偶图（deg_H ≡ 0），F = G-S 满足 deg_F ≡ deg_G (mod 2)
            maxH = int(degA[S].astype(np.int16).max())
            val = (m - sz[S]) + maxH // 2  # |F| + Δ(H)/2, H = G - F
            if val < best[0]:
                best = (val, S)
    return best


def f_re_setcover(g):
    """独立交叉验证：精确覆盖分支定界。块 = 全部 2-正则子图 + 全部单边。m ≤ 14 推荐。"""
    m = g.m
    # 枚举所有 2-正则边子集：子集枚举（m ≤ 14）
    sets = []
    N = 1 << m
    for S in range(1, N):
        # 检查每个顶点度 ∈ {0, 2}
        ok = True
        for v in range(g.n):
            d = bin(S & g.vmask[v]).count('1')
            if d not in (0, 2):
                ok = False
                break
        if ok and bin(S).count('1') >= 3:
            sets.append(S)
    sets += [1 << i for i in range(m)]
    sets = sorted(set(sets), key=lambda s: -bin(s).count('1'))
    full = (1 << m) - 1
    # 每条边被哪些集合覆盖
    cov = {i: [] for i in range(m)}
    for si, S in enumerate(sets):
        mm = S
        while mm:
            lb = (mm & -mm)
            cov[lb.bit_length() - 1].append(si)
            mm ^= lb
    best = [m]  # 全单边
    def bb(uncovered, cnt):
        if cnt >= best[0]:
            return
        if uncovered == 0:
            best[0] = cnt
            return
        # 选未覆盖边中覆盖集最少的
        e = min((e for e in range(m) if uncovered >> e & 1),
                key=lambda e: len(cov[e]))
        for si in cov[e]:
            S = sets[si]
            # 分解 = 划分：块必须完全落在未覆盖部分内（禁止重复覆盖）
            if (S & uncovered) == S:
                bb(uncovered & ~S, cnt + 1)
    bb(full, 0)
    return best[0]


def max_cycle_packing_ILP(g):
    """ℓ(G) 直接 ILP（交叉验证用）：max Σ|C| s.t. 边不交。"""
    import networkx as nx
    import numpy as np
    from scipy.optimize import milp, LinearConstraint, Bounds
    G = nx.Graph()
    G.add_nodes_from(range(g.n))
    G.add_edges_from(g.edges)
    cycles = [c for c in nx.simple_cycles(G) if len(c) >= 3]
    eid = {tuple(sorted(e)): i for i, e in enumerate(g.edges)}
    obj = np.array([len(c) for c in cycles], dtype=float)
    A = np.zeros((g.m, len(cycles)))
    for j, c in enumerate(cycles):
        for i in range(len(c)):
            u, v = c[i], c[(i + 1) % len(c)]
            A[eid[tuple(sorted((u, v)))], j] = 1
    res = milp(c=-obj, constraints=LinearConstraint(A, 0, 1),
               integrality=np.ones(len(cycles)),
               bounds=Bounds(0, 1))
    assert res.success
    return int(round(-res.fun))


def from_edges(n, edges, name=""):
    return Graph(n, edges, name)


def complete_graph(n):
    return Graph(n, [(i, j) for i in range(n) for j in range(i + 1, n)], f"K_{n}")


def path_graph(n):
    return Graph(n, [(i, i + 1) for i in range(n - 1)], f"P_{n}")


def star(n):
    return Graph(n, [(0, i) for i in range(1, n)], f"K_1,{n-1}")


def cycle_graph(n):
    return Graph(n, [(i, (i + 1) % n) for i in range(n)], f"C_{n}")


def petersen():
    edges = []
    for i in range(5):
        edges.append((i, (i + 1) % 5))          # 外圈 5-圈
        edges.append((5 + i, 5 + (i + 2) % 5))  # 内圈 5-圈（步长 2 的星多边形）
        edges.append((i, 5 + i))                # 5 条辐条
    return Graph(10, edges, "Petersen")
