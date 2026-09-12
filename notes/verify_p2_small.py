#!/usr/bin/env python3
"""
独立复核 attack_delta5.md P2：even 且 Δ≤5 ⟹ ce(G) ≤ 2⌊n/3⌋ ≤ n−1。
  n = 3..6：对全部偶图（Δ≤5）精确计算 ce（位掩码 DP）。
  n = 7  ：全部偶图（Δ≤5 ⟹ 实际 Δ≤4, m≤14）做「能否 ≤4 件分解」的
           有界精确搜索（记忆化 DFS）；找不出 ≤4 件的记为反例（应为 0）。
偶图枚举：固定顶点 0 为校验点，{1..n-1} 内部边任取，0-i 边由奇偶性唯一确定。
"""
from itertools import combinations

def enumerate_even_graphs(n):
    """所有偶图（labelled），返回边集 frozenset 列表。"""
    others = list(range(1, n))
    inner = list(combinations(others, 2))
    out = []
    for bits in range(1 << len(inner)):
        edges = set()
        deg = [0]*n
        for k, (u, v) in enumerate(inner):
            if (bits >> k) & 1:
                edges.add((u, v)); deg[u] += 1; deg[v] += 1
        for i in others:
            if deg[i] % 2 == 1:
                e = (0, i) if i != 0 else None
                edges.add((0, i)); deg[0] += 1; deg[i] += 1
        out.append(frozenset(edges))
    return out

def cycles_of(n, edges):
    eset = sorted(edges); eid = {e: i for i, e in enumerate(eset)}
    adj = {v: set() for v in range(n)}
    for (u, v) in eset:
        adj[u].add(v); adj[v].add(u)
    cyc = set()
    for start in range(n):
        stack = [(start, [start], 0)]
        while stack:
            v, path, em = stack.pop()
            for w in sorted(adj[v]):
                if w < start: continue
                e = tuple(sorted((v, w)))
                if (em >> eid[e]) & 1: continue
                if w == start and len(path) >= 3:
                    cyc.add(em | (1 << eid[e]))
                elif w not in path:
                    stack.append((w, path + [w], em | (1 << eid[e])))
    return eset, eid, sorted(cyc)

def exact_ce(n, edges):
    eset, eid, cyc = cycles_of(n, edges)
    M = len(eset); FULL = (1 << M) - 1
    if M == 0: return 0
    cbe = [[] for _ in range(M)]
    for cm in cyc:
        for i in range(M):
            if (cm >> i) & 1: cbe[i].append(cm)
    INF = 99
    dp = [INF]*(1 << M); dp[0] = 0
    for mask in range(1, 1 << M):
        low = (mask & -mask).bit_length()-1
        best = dp[mask ^ (1 << low)] + 1
        for cm in cbe[low]:
            if cm & mask == cm:
                v = dp[mask ^ cm] + 1
                if v < best: best = v
        dp[mask] = best
    return dp[FULL]

def can_decompose_within(n, edges, budget):
    """能否把 edges 划分成 ≤ budget 个 圈/单边（精确判定）。"""
    eset, eid, cyc = cycles_of(n, edges)
    M = len(eset); FULL = (1 << M) - 1
    cbe = [[] for _ in range(M)]
    for cm in cyc:
        for i in range(M):
            if (cm >> i) & 1: cbe[i].append(cm)
    from functools import lru_cache
    import sys
    sys.setrecursionlimit(100000)
    memo = {}
    def rec(mask, budget):
        if mask == 0: return True
        if budget == 0: return False
        key = (mask, budget)
        if key in memo: return memo[key]
        low = (mask & -mask).bit_length()-1
        ans = rec(mask ^ (1 << low), budget-1)  # 单边
        if not ans:
            for cm in cbe[low]:
                if cm & mask == cm and rec(mask ^ cm, budget-1):
                    ans = True; break
        memo[key] = ans
        return ans
    return rec(FULL, budget)

print("n  #even(Δ≤5)  max ce  bound 2⌊n/3⌋  违反数")
total_bad = 0
for n in range(3, 7):
    gs = enumerate_even_graphs(n)
    bad = []; mx = 0
    B = 2*(n//3)
    for g in gs:
        if max((sum(1 for e in g if v in e) for v in range(n)), default=0) > 5:
            continue  # Δ≤5 假设
        ce = exact_ce(n, g)
        mx = max(mx, ce)
        if not (ce <= B and B <= n-1):
            bad.append((g, ce))
    total_bad += len(bad)
    print(f"{n}  {len(gs)}        {mx}       {B}          {len(bad)}")

# n = 7：有界判定（bound = 4）
n = 7
B = 2*(n//3)
gs = enumerate_even_graphs(n)
cnt = 0; bad = []
for g in gs:
    degs = [sum(1 for e in g if v in e) for v in range(n)]
    if max(degs) > 5:  # Δ≤5（偶 ⟹ 实际 Δ≤4）
        continue
    cnt += 1
    if not can_decompose_within(n, g, B):
        bad.append(g)
print(f"{n}  {cnt}        (有界搜索)  {B}          {len(bad)}")
total_bad += len(bad)
if bad:
    for g in bad[:3]:
        print("  反例边集:", sorted(g))
        print("  精确 ce =", exact_ce(7, g))
print("\nP2 小图穷举总判决:", "PASS（无反例）" if total_bad == 0 else f"FAIL（{total_bad} 个反例）")
print("顺带核对 2⌊n/3⌋ ≤ n−1 (n≥3):", all(2*(n//3) <= n-1 for n in range(3, 30)))
