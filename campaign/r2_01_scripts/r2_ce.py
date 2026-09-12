#!/usr/bin/env python3
"""r2_ce.py — 精确 ce（最少 圈+单边 分解件数）。独立实现（与 lane05 不同方法）：
迭代加深 + 最低未覆盖边分支 + 下界剪枝。仅用于 n <= 12 的小图。"""
import itertools, sys
from collections import defaultdict

def _cycles_through_edge(u, v, adj, forbidden_edge):
    """图中经过边 (u,v) 的全部简单圈（边集 frozenset 列表）。DFS。"""
    cycles = []
    # 路径 u -> ... -> v，不用边 (u,v)
    def dfs(cur, path_edges, visited):
        if cur == v:
            if len(path_edges) >= 2:
                cycles.append(frozenset(path_edges))
            return
        for w in adj[cur]:
            if w in visited:
                continue
            e = (min(cur, w), max(cur, w))
            if e == forbidden_edge:
                continue
            visited.add(w)
            path_edges.append(e)
            dfs(w, path_edges, visited)
            path_edges.pop()
            visited.discard(w)
    dfs(u, [(u, v)], {u})
    return cycles

def _all_cycles_through_lowest(rem_edges):
    adj = defaultdict(list)
    for u, v in rem_edges:
        adj[u].append(v)
        adj[v].append(u)
    e = min(rem_edges)
    return e, _cycles_through_edge(e[0], e[1], adj, e)

def feasible(n, edges, k):
    """<=k 件可行性。"""
    edges = frozenset(edges)
    if not edges:
        return True
    m = len(edges)
    nn = max(3, n)
    def rec(rem, k):
        if not rem:
            return True
        if k <= 0:
            return False
        import math
        if math.ceil(len(rem) / nn) > k:
            return False
        e, cycs = _all_cycles_through_lowest(rem)
        seen = set()
        # 先试大圈（更快降深度）
        for c in sorted(cycs, key=len, reverse=True):
            if c in seen:
                continue
            seen.add(c)
            if rec(rem - c, k - 1):
                return True
        if k >= 1:
            if rec(rem - {e}, k - 1):
                return True
        return False
    return rec(edges, k)

def exact_ce(n, edges, kmax=None):
    edges = frozenset((min(u, v), max(u, v)) for u, v in edges)
    if not edges:
        return 0
    if kmax is None:
        kmax = len(edges)
    import math
    lo = math.ceil(len(edges) / max(n, 3))
    for k in range(lo, kmax + 1):
        if feasible(n, edges, k):
            return k
    return None
