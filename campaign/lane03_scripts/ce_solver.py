"""
ce_solver.py — 计算 ce(G)：把 n 点简单图 G 的边集分解为边不相交的圈与单边所需的最少部件数。

关键恒等式（lane 文档 §0）：若分解为 c 条圈 + e 条单边，则
    ce(G) = c + e = m - max over 边不相交圈族 D of sum(|C|-1)  = m - max_save(G)
其中 m = |E(G)|。每条长 l 的圈"节省" l-1 个部件。

圈枚举：canonical（圈的最小顶点为起点，限制 v1 < vk 消旋转/反射重复）。
packing：DFS + memo(on 剩余边 mask) + 后缀和乐观剪枝。n<=12 均可用。
"""
import sys
from functools import lru_cache

def edge_index(n):
    """返回 (u,v)->bit 的映射表；边按字典序编号 0..C(n,2)-1。"""
    idx = {}
    k = 0
    for u in range(n):
        for v in range(u + 1, n):
            idx[(u, v)] = k
            k += 1
    return idx

def enumerate_edges(n):
    return [(u, v) for u in range(n) for v in range(u + 1, n)]

def all_simple_cycles(n, adj_mask, eidx):
    """枚举全部简单圈，返回 [(edge_bitmask, length), ...]（canonical 去重）。"""
    cycles = []
    for s in range(n):
        # 路径 s -> v1 -> ... -> vk -> s，全部 vi > s，且 v1 < vk（消反射）
        def dfs(path, used_e, cur):
            # 尝试闭合：cur 与 s 相邻
            if len(path) >= 3 and (adj_mask[cur] >> s & 1) and path[1] < cur:
                close_ei = eidx[(s, cur)]
                if not (used_e >> close_ei & 1):
                    cycles.append((used_e | (1 << close_ei), len(path)))
            for w in range(s + 1, n):
                if w in path_set:
                    continue
                if not (adj_mask[cur] >> w & 1):
                    continue
                ei = eidx[(min(cur, w), max(cur, w))]
                if used_e >> ei & 1:
                    continue
                path.append(w); path_set.add(w)
                dfs(path, used_e | (1 << ei), w)
                path.pop(); path_set.remove(w)
        path_set = {s}
        dfs([s], 0, s)
    return cycles

def max_save(n, edge_mask_full, cycles, memo_cap=None):
    """边不相交圈族的最大 sum(len-1)。"""
    # 按节省/长度收益排序：长圈优先（节省大）
    cyc = sorted(cycles, key=lambda c: (-(c[1] - 1), c[1]))
    m = len(cyc)
    em = [c[0] for c in cyc]
    sv = [c[1] - 1 for c in cyc]
    # 后缀乐观和（忽略冲突）
    suffix = [0] * (m + 1)
    for i in range(m - 1, -1, -1):
        suffix[i] = suffix[i + 1] + sv[i]
    sys.setrecursionlimit(1 << 20)
    memo = {}
    FULL = edge_mask_full

    def dfs(i, rem):
        if i == m or rem == 0:
            return 0
        key = rem * (m + 1) + i
        v = memo.get(key)
        if v is not None:
            return v
        best = dfs(i + 1, rem)  # 不取圈 i
        if em[i] & rem == em[i]:  # 圈 i 的全部边仍可用
            cand = sv[i] + dfs(i + 1, rem & ~em[i])
            if cand > best:
                best = cand
        memo[key] = best
        return best

    return dfs(0, FULL)

def ce(n, adj_mask, eidx=None, edge_mask=None):
    """精确 ce(G)。adj_mask: 长度 n 的邻接 bitmask（顶点侧）。"""
    if eidx is None:
        eidx = edge_index(n)
    if edge_mask is None:
        edge_mask = 0
        for u in range(n):
            am = adj_mask[u]
            for v in range(u + 1, n):
                if am >> v & 1:
                    edge_mask |= 1 << eidx[(u, v)]
    if edge_mask == 0:
        return 0
    cycles = all_simple_cycles(n, adj_mask, eidx)
    cycles = [c for c in cycles if c[0] & edge_mask == c[0]]
    return bin(edge_mask).count('1') - max_save(n, edge_mask, cycles)

def greedy_save_ub(n, adj_mask, eidx, tries=3):
    """快速贪心：返回 save 的一个下界（<=最优），故 m - greedy 是 ce 的上界，用于剪枝。"""
    import random
    best = 0
    live = 0
    for u in range(n):
        am = adj_mask[u]
        for v in range(u + 1, n):
            if am >> v & 1:
                live |= 1 << eidx[(u, v)]
    rng = random.Random(12345)
    for t in range(tries):
        rem = live
        save = 0
        while True:
            # 从随机点 DFS 找一个圈（在 rem 内）
            cyc = find_cycle(n, adj_mask, eidx, rem, rng)
            if cyc is None:
                break
            rem &= ~cyc
            save += bin(cyc).count('1') - 1  # cyc 是圈边 mask，长度 = popcount
        if save > best:
            best = save
    return best

def find_cycle(n, adj_mask, eidx, rem, rng):
    """在 rem 边集中找一个圈，返回其边 mask；无圈返回 None。"""
    # 现用边邻接
    adj = [0] * n
    for u in range(n):
        for v in range(u + 1, n):
            ei = eidx[(u, v)]
            if rem >> ei & 1:
                adj[u] |= 1 << v
                adj[v] |= 1 << u
    # DFS 找回边
    color = [0] * n
    parent = [-1] * n
    order = list(range(n))
    rng.shuffle(order)
    for s in order:
        if color[s] or bin(adj[s]).count('1') == 0:
            continue
        # 迭代 DFS
        stack = [s]
        color[s] = 1
        par = {s: -1}
        while stack:
            u = stack[-1]
            nbrs = [w for w in range(n) if adj[u] >> w & 1]
            rng.shuffle(nbrs)
            advanced = False
            for w in nbrs:
                if w == par.get(u, -1):
                    continue
                if w in par:
                    # 找到圈：提取路径 u..w
                    cyc_vertices = []
                    x = u
                    while x != -1 and x != w:
                        cyc_vertices.append(x)
                        x = par[x]
                    if x != w:
                        continue
                    cyc_vertices.append(w)
                    mask = 0
                    for i in range(len(cyc_vertices)):
                        a = cyc_vertices[i]
                        b = cyc_vertices[(i + 1) % len(cyc_vertices)]
                        mask |= 1 << eidx[(min(a, b), max(a, b))]
                    if len(cyc_vertices) >= 3:
                        return mask
                    continue
                par[w] = u
                color[w] = 1
                stack.append(w)
                advanced = True
                break
            if not advanced:
                stack.pop()
        # 清 color
    return None

def graph_to_adj(n, edge_list):
    adj = [0] * n
    for (u, v) in edge_list:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj

def complete_bipartite(s, t):
    """K_{s,t}: 顶点 0..s-1 为小侧, s..s+t-1 为大侧。返回 (n, adj, edge_list)。"""
    n = s + t
    el = [(u, v) for u in range(s) for v in range(s, n)]
    return n, graph_to_adj(n, el), el

if __name__ == '__main__':
    # ---- 单元测试：手推值 ----
    eidx8 = edge_index(12)
    tests = []
    # K_3 = 1 (三角形)
    tests.append(("K_3", 3, graph_to_adj(3, [(0,1),(1,2),(0,2)]), 1))
    # K_4 = 3 (3 个 4-圈 or H 圈+2 对角)
    tests.append(("K_4", 4, graph_to_adj(4, [(i,j) for i in range(4) for j in range(i+1,4)]), 3))
    # K_5 = 2 (Walecki 2 个 Hamilton 圈)
    tests.append(("K_5", 5, graph_to_adj(5, [(i,j) for i in range(5) for j in range(i+1,5)]), 2))
    # K_6 = ? (Walecki: (n-2)/2 H圈 + 完美匹配 n/2 边 = 2+3 = 5)
    tests.append(("K_6", 6, graph_to_adj(6, [(i,j) for i in range(6) for j in range(i+1,6)]), 5))
    # K_{2,3} = 3
    n, adj, _ = complete_bipartite(2, 3)
    tests.append(("K_{2,3}", n, adj, 3))
    # K_{3,3} = 4
    n, adj, _ = complete_bipartite(3, 3)
    tests.append(("K_{3,3}", n, adj, 4))
    # K_{2,4} = 2
    n, adj, _ = complete_bipartite(2, 4)
    tests.append(("K_{2,4}", n, adj, 2))
    # K_{3,4} = 6 (手推)
    n, adj, _ = complete_bipartite(3, 4)
    tests.append(("K_{3,4}", n, adj, 6))
    # K_{3,5} = 7 (手推)
    n, adj, _ = complete_bipartite(3, 5)
    tests.append(("K_{3,5}", n, adj, 7))
    # K_{2,5} = 4 (手推: 2 个 4-圈 + 2 单边)
    n, adj, _ = complete_bipartite(2, 5)
    tests.append(("K_{2,5}", n, adj, 4))
    ok = True
    for name, n, adj, expect in tests:
        got = ce(n, adj)
        status = "OK " if got == expect else "FAIL"
        if got != expect:
            ok = False
        print(f"[{status}] {name}: ce = {got} (期望 {expect})")
    print("ALL PASS" if ok else "SOME FAILED")
