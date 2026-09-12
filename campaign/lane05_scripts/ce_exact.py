#!/usr/bin/env python3
"""
lane05 / Δ≤6 数值侦察：精确 ce(G) 计算（最小圈+单边分解数）。
方法：位掩码枚举全部简单圈 → 子集 DP（f[mask] = min 件数分解 mask 的边集）。
独立校验：分支定界 DFS（与 DP 独立的第二种算法）。
"""
import sys
from functools import lru_cache
from itertools import combinations

def cycles_bitmask(n, edges):
    """枚举所有简单圈（点集互异，长≥3），返回 bitmask 列表（边集掩码）。
    edges: dict mask->(u,v) 或 list[(u,v)]。"""
    adj = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        adj[u].append((v, 1 << i))
        adj[v].append((u, 1 << i))
    emask_of_vpair = {}
    for i, (u, v) in enumerate(edges):
        emask_of_vpair[(min(u, v), max(u, v))] = 1 << i
    cycles = []
    # 枚举：从每个点出发的不回头路（限制起点为最小点防止重复）
    def dfs(start, cur, visited, emask):
        for (nxt, eb) in adj[cur]:
            if eb & emask:
                continue
            if nxt == start and len(visited) >= 3:
                cycles.append(emask | eb)
                continue
            if nxt in visited or nxt < start:
                continue
            visited.add(nxt)
            dfs(start, nxt, visited, emask | eb)
            visited.remove(nxt)
    for s in range(n):
        dfs(s, s, {s}, 0)
    # 去重（同一个边集只会被枚举两次：两个方向），用集合
    return list(set(cycles))

def ce_dp(n, edges, all_edge_mask):
    """DP 精确 ce。返回最小件数。"""
    if all_edge_mask == 0:
        return 0
    cyc = cycles_bitmask(n, edges)
    pieces = cyc + [1 << i for i in range(len(edges))]  # 圈 + 单边
    # 排序加速：优先大 piece
    pieces.sort(key=lambda x: -bin(x).count('1'))
    INF = 1 << 29
    f = {0: 0}
    # 迭代：对每个 mask，剥一个 piece。用 BFS 全子集。
    # 更稳：f 全量数组（m ≤ 27 → 2^27 太大），改 dict 只存可达。
    import heapq
    # 用「递归+记忆化」按需计算
    best = [INF]
    from functools import lru_cache
    sys.setrecursionlimit(100000)
    memo = {}
    def solve(mask):
        if mask == 0:
            return 0
        if mask in memo:
            return memo[mask]
        low = mask & (-mask)
        res = INF
        for p in pieces:
            if (p & low) and (p & ~mask == 0):  # 覆盖最低边且 p 必须是 mask 子集（划分语义）
                r = solve(mask & ~p)
                if r + 1 < res:
                    res = r + 1
        memo[mask] = res
        return res
    return solve(all_edge_mask)

def ce_branch(n, edges, all_edge_mask, budget=None):
    """独立校验：分支定界。若给定 budget 可判定 ≤budget 是否可行。"""
    if all_edge_mask == 0:
        return 0
    cyc = cycles_bitmask(n, edges)
    pieces = cyc + [1 << i for i in range(len(edges))]
    pieces.sort(key=lambda x: -bin(x).count('1'))
    sys.setrecursionlimit(100000)
    best = [1000]
    def dfs(mask, used):
        if mask == 0:
            if used < best[0]:
                best[0] = used
            return
        if used + 1 >= best[0]:
            return
        low = mask & (-mask)
        for p in pieces:
            if (p & low) and (p & ~mask == 0):  # 同修复：piece ⊆ mask
                dfs(mask & ~p, used + 1)
    dfs(all_edge_mask, 0)
    return best[0]

if __name__ == '__main__':
    # 自检：K_3 (n=3) ce=1；C_4 ce=1；路径 P_4 ce=3；witness G* ce=8
    tests = [
        (3, [(0,1),(1,2),(0,2)], 1),
        (4, [(0,1),(1,2),(2,3),(3,0)], 1),
        (4, [(0,1),(1,2),(2,3)], 3),
        # 手工核算：K_{2,3}（n=5, m=6）：2 个 3 度点 ⟹ ≥2 单边（1 单边剩 5 边非偶圈和）+ 4-圈 = 3；
        # 2 件需 savings=4 而最大 savings=3（一个 4-圈）⟹ ce=3
        (5, [(0,2),(0,3),(0,4),(1,2),(1,3),(1,4)], 3),
        # 手工核算：K_{3,3}（n=6, m=9）：6 个 3 度点 ⟹ ≥3 单边；3 单边+6-圈=4 件；
        # ≤3 件需 savings≥6：须两个 4-圈+1 单边，但 K_{3,3} 边不交 4-圈 packing=1（逐对核查）⟹ ce=4
        (6, [(0,3),(0,4),(0,5),(1,3),(1,4),(1,5),(2,3),(2,4),(2,5)], 4),
    ]
    for n, e, want in tests:
        m = 0
        for i in range(len(e)):
            m |= 1 << i
        got = ce_dp(n, e, m)
        got2 = ce_branch(n, e, m)
        status = "OK" if (got == want and got2 == want) else "FAIL"
        print(f"selftest n={n} edges={len(e)} ce_dp={got} ce_branch={got2} want={want} [{status}]")
