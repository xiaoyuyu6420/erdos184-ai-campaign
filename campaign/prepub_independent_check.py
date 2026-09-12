#!/usr/bin/env python3
"""PREPUB 独立复核求解器（与各 lane 脚本完全独立实现）。

ce(G) = 把 E(G) 划分为最少个数的 parts，每 part 是单边或某简单圈的边集。
算法：最小未覆盖边分支；含该边的件 = 单边，或该边 + 一条避开它的简单 u-v 路。
自检锚点 + 各 A 级声称的独立复算。
"""
import sys
from itertools import combinations

sys.setrecursionlimit(100000)

def build_complete(n):
    return list(combinations(range(n), 2))

def build_bipartite(a, b):
    return [(x, y) for x in range(a) for y in range(a, a + b)]

def build_k3_plus_k34():
    # lane_05 反例：3 侧三角形 + K_{3,4}（同一 7 点集，非不交并）
    tri = [(0, 1), (0, 2), (1, 2)]
    bip = [(x, y) for x in range(3) for y in range(3, 7)]
    return tri + bip

def build_petersen():
    edges = []
    for i in range(5):
        edges.append((i, (i + 1) % 5))          # 外圈
        edges.append((5 + i, 5 + (i + 2) % 5))  # 内五角星
        edges.append((i, 5 + i))                # 辐条
    return edges

def paths_between(u, v, adj, banned, used, n):
    """u 到 v 的全部简单路（边集 bitmask of used-graph）。"""
    results = []
    banned_edge = next(iter(used))
    def dfs(cur, visited, emask):
        if cur == v and emask > 0:
            results.append(emask)
            return
        for (x, y, idx) in adj.get(cur, []):
            if idx == banned_edge:
                continue
            nxt = y
            if nxt in visited:
                continue
            visited.add(nxt)
            dfs(nxt, visited, emask | (1 << idx))
            visited.remove(nxt)
    dfs(u, {u}, 0)
    return results

def ce_exact(n, edges, ub=None):
    """精确 ce：分支定界。"""
    m = len(edges)
    emap = edges
    adj = {}
    for idx, (u, v) in enumerate(emap):
        adj.setdefault(u, []).append((u, v, idx))
        adj.setdefault(v, []).append((v, u, idx))
    full = (1 << m) - 1

    # 预计算：对每条边 idx，含它的所有圈（该边 + 简单路）
    cycles_through = {}
    for idx, (u, v) in enumerate(emap):
        pths = paths_between(u, v, adj, None, {idx}, n)
        cands = []
        for p in pths:
            mask = p | (1 << idx)
            # 排除 2-圈（u,v 平行边不存在于简单图，路长>=2 保证圈长>=3）
            if bin(mask).count("1") >= 3:
                cands.append(mask)
        cycles_through[idx] = cands

    best = [ub if ub is not None else m]  # 全单边平凡可行

    def greedy_ub(mask):
        # 贪心上界：反复取最长圈，否则单边
        cnt = 0
        while mask:
            bestlen, bestc = 0, 0
            for i0 in range(m):
                if not (mask >> i0 & 1):
                    continue
                for c in cycles_through[i0]:
                    if c & mask == c:
                        L = bin(c).count("1")
                        if L > bestlen:
                            bestlen, bestc = L, c
            if bestc:
                mask &= ~bestc
            else:
                cnt += bin(mask).count("1")
                break
            cnt += 1
        return cnt

    def lower_bound(mask):
        # LB: ⌈|E(mask)| / n⌉ 与 ⌈odd/2⌉ 的 max（子图内度数）
        e = bin(mask).count("1")
        lb = (e + n - 1) // n
        deg = {}
        for i in range(m):
            if mask >> i & 1:
                u, v = emap[i]
                deg[u] = deg.get(u, 0) + 1
                deg[v] = deg.get(v, 0) + 1
        odd = sum(1 for d in deg.values() if d % 2 == 1)
        lb = max(lb, (odd + 1) // 2, 1 if e else 0)
        return lb

    def solve(mask, cnt):
        if cnt + lower_bound(mask) >= best[0]:
            return
        if mask == 0:
            if cnt < best[0]:
                best[0] = cnt
            return
        g = greedy_ub(mask)
        if cnt + g < best[0]:
            best[0] = cnt + g
        # 最小未覆盖边
        i0 = (mask & -mask).bit_length() - 1
        # 选项 1：单边
        solve(mask & ~(1 << i0), cnt + 1)
        # 选项 2：含 i0 的圈
        for c in cycles_through[i0]:
            if c & mask == c:
                solve(mask & ~c, cnt + 1)

    solve(full, 0)
    return best[0]

def check():
    ok = True
    def expect(name, got, want):
        nonlocal ok
        flag = "OK " if got == want else "FAIL"
        if got != want:
            ok = False
        print(f"  [{flag}] {name}: got {got}, expect {want}")

    print("== 自检锚点 ==")
    expect("C4 (2x2 grid cycle)", ce_exact(4, [(0,1),(1,2),(2,3),(0,3)]), 1)
    expect("K_{2,3}", ce_exact(5, build_bipartite(2,3)), 3)
    expect("bowtie(2 三角共点)", ce_exact(5, [(0,1),(1,2),(0,2),(0,3),(3,4),(0,4)]), 2)

    print("== A1: 完全图 ce（lane_07/09 仲裁）==")
    for n, want in [(4,3),(5,2),(6,5),(7,3),(8,7)]:
        want_str = want
        got = ce_exact(n, build_complete(n))
        expect(f"ce(K_{n})", got, want_str)

    print("== A3: 反例 K_3+K_{3,4} ==")
    expect("ce(K3+K34)", ce_exact(7, build_k3_plus_k34()), 7)

    print("== lane09 V4: Petersen ==")
    expect("ce(Petersen)", ce_exact(10, build_petersen(), ub=8), 7)

    print("== lane06/08: K_{3,q} ==")
    expect("ce(K_{3,4})", ce_exact(7, build_bipartite(3,4)), 6)
    expect("ce(K_{3,5})", ce_exact(8, build_bipartite(3,5)), 7)

    print("== lane05 白名单：K_{3,6} ==")
    expect("ce(K_{3,6})", ce_exact(9, build_bipartite(3,6)), 8)

    print("\nRESULT:", "ALL PASS" if ok else "FAILURES PRESENT")
    return ok

if __name__ == "__main__":
    sys.exit(0 if check() else 1)
