#!/usr/bin/env python3
"""lane05 批量枚举：n 顶点、Δ≤6 图中 ce 的最大值（sup ce/n 曲线）。
两层过滤：贪心上界（可分解证书）剪枝 + 精确 DP（划分语义，已修复 p⊆mask bug）。
用法：python3 enumerate_lane05.py n_min edge_min n_max
"""
import sys, time
from itertools import combinations
from ce_exact import cycles_bitmask, ce_dp

def max_deg_ok(n, edges, cap=6):
    deg = [0] * n
    for u, v in edges:
        deg[u] += 1
        deg[v] += 1
        if deg[u] > cap or deg[v] > cap:
            return False
    return True

def greedy_ce(n, edges):
    """贪心上界：反复剥最长圈，最后剩森林按单边计。返回件数（可行解 ⟹ 上界）。"""
    eset = set(edges)
    adj = {v: set() for v in range(n)}
    for u, v in eset:
        adj[u].add(v); adj[v].add(u)
    pieces = 0
    # 剥圈
    while True:
        # 找一个圈（DFS）
        cyc = None
        for s in range(n):
            if not adj[s]:
                continue
            # BFS 找圈
            parent = {s: None}
            stack = [s]
            while stack and cyc is None:
                x = stack.pop()
                for y in adj[x]:
                    if y not in parent:
                        parent[y] = x
                        stack.append(y)
                    elif parent[x] != y:
                        # 找到圈：回溯路径 x..s 与 y..s
                        def path_to(a, b):
                            p = []
                            while a != b:
                                p.append(a)
                                a = parent[a]
                            p.append(b)
                            return p
                        px = path_to(x, s)
                        py = path_to(y, s)
                        # 公共后缀去掉
                        sx = set(px)
                        cyc = [x]
                        prev = x
                        cur = parent[x]
                        while cur is not None and cur != y:
                            cyc.append(cur)
                            cur = parent[cur]
                        break
                if cyc:
                    break
            if cyc:
                break
        if cyc is None:
            break
        # 剥掉这个圈：按 cyc 序列删边
        L = len(cyc)
        for i in range(L):
            u, v = cyc[i], cyc[(i + 1) % L]
            if (min(u, v), max(u, v)) in eset or (u, v) in eset:
                a, b = (u, v) if (u, v) in eset else (min(u, v), max(u, v))
                eset.discard((u, v)); eset.discard((min(u, v), max(u, v)))
                adj[u].discard(v); adj[v].discard(u)
        pieces += 1
    pieces += len(eset)  # 剩余森林 ⟹ 每条边单出（粗上界）
    return pieces

def odd_count(n, edges):
    deg = [0] * n
    for u, v in edges:
        deg[u] += 1; deg[v] += 1
    return sum(1 for d in deg if d % 2 == 1), deg

def connected(n, edges):
    if not edges:
        return False
    adj = {i: set() for i in range(n)}
    for u, v in edges:
        adj[u].add(v); adj[v].add(u)
    seen = {0}
    stack = [0]
    while stack:
        x = stack.pop()
        for y in adj[x]:
            if y not in seen:
                seen.add(y); stack.append(y)
    return len(seen) == n

def enumerate_max(n, m_min, m_max=None, verbose_every=20000, seed_best=0, desc=True):
    """枚举 n 点、边数∈[m_min, m_max]、Δ≤6、连通图，返回 (max_ce, witness_edges, stats)。
    desc=True 时从高边数往下扫（ce 大的图更可能在高 m 处）。"""
    alle = list(combinations(range(n), 2))
    if m_max is None:
        m_max = len(alle)
    best = seed_best
    best_e = None
    t0 = time.time()
    cnt = cnt_exact = 0
    ms = range(min(m_max, len(alle)), m_min - 1, -1) if desc else range(m_min, min(m_max, len(alle)) + 1)
    for m in ms:
        for comb in combinations(alle, m):
            edges = list(comb)
            cnt += 1
            if cnt % verbose_every == 0:
                print(f"  [n={n} m={m}] scanned={cnt} exact={cnt_exact} best={best} "
                      f"t={time.time()-t0:.0f}s", flush=True)
            if not connected(n, edges):
                continue
            ub = greedy_ce(n, edges)
            if ub <= best:
                continue
            cnt_exact += 1
            mask = 0
            for i in range(m):
                mask |= 1 << i
            v = ce_dp(n, edges, mask)
            if v > best:
                best = v
                best_e = edges
                print(f"  ** new best n={n} m={m} ce={v} (n-1={n-1}) edges={edges}", flush=True)
    return best, best_e, cnt, cnt_exact

if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    m_min = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    m_max = int(sys.argv[3]) if len(sys.argv) > 3 else None
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    b, e, c, cx = enumerate_max(n, m_min, m_max, seed_best=seed)
    print(f"RESULT n={n}: max_ce={b} witness_m={len(e) if e else None}")
