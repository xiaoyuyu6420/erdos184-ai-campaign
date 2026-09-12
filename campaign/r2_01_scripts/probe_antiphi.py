#!/usr/bin/env python3
"""probe_antiphi.py — 命题 6（反 Φ 分解）的数值验证：
若 W = L(B)（B = 3-正则二部简单图），M 为 B 的完美匹配、任一定向，
则 E(Φ(M)) 与 E(Φ(−M))（定向翻转版）恰划分 E(W)，且两者都是无三角形 2-因子
（所有圈长 >= 4）⟹ W 可分解为两个无三角形 2-因子。
验证方式：构造 Φ(M)（复用 r2_core.phi_route_from_pair 的构造核），取
PhiMinus = E(W) \\ E(Phi)，独立校验：(a) 划分完整；(b) PhiMinus 是支撑 2-因子；
(c) PhiMinus 所有圈长 >= 4；(d) Phi 本身所有圈长 >= 4（复证）。
覆盖：s=3..6 全部标记 B（穷举）+ 随机大 B。
用法: python3 probe_antiphi.py exhaustive [S_max] | random [count_per_s]"""
import sys, time, random
sys.path.insert(0, "/Users/munich/Desktop/数学/front184/campaign/r2_01_scripts")
from r2_core import (all_cubic_bipartite, line_graph_of_B, make_graph,
                     verify_two_factor, cycles_of_factor, edge_components,
                     construct_phi, incidence_graph, random_cubic_bipartite)

def check_antiphi(B_adj, tag):
    """对 L(B) 验证反 Φ 分解。返回圈长向量统计。"""
    verts, idx, LE, nL = line_graph_of_B(B_adj)
    # B 的二部划分与完美匹配（construct_phi 内部用 Kuhn；此处直接复用其输出）
    # 构造 B_adj 的规范形式：construct_phi 需要左右编号（左 0..nA-1, 右 nA..）
    color = {}
    for x0 in B_adj:
        if x0 not in color:
            color[x0] = 0
            stack = [x0]
            while stack:
                x = stack.pop()
                for y in B_adj[x]:
                    if y not in color:
                        color[y] = 1 - color[x]
                        stack.append(y)
    Ls = sorted(x for x in color if color[x] == 0)
    Rs = sorted(x for x in color if color[x] == 1)
    assert len(Ls) == len(Rs)
    remap = {}
    for new, old in enumerate(Ls + Rs):
        remap[old] = new
    nA = len(Ls)
    B_std = {remap[x]: {remap[y] for y in B_adj[x]} for x in B_adj}
    # W = L(B_std)：idx/LE 与 construct_phi 使用同一套（重映射后）标签
    verts, idx, LE, nL = line_graph_of_B(B_std)
    # Φ 构造（含独立校验）：phi_pairs 即 Φ 的邻接（以 B 边 frozenset 为节点）
    phi_adj, M, m = construct_phi(B_std, nA, nA)
    for e in phi_adj:
        assert len(phi_adj[e]) == 2, f"[{tag}] Φ 度 != 2"
    # B 边 ↔ W 点
    B_edges = {frozenset((u, v)) for u in B_std for v in B_std[u]}
    assert len(B_edges) == nL
    # Φ 边集（W 的边 = 共享 B 端点的 B 边对）
    PhiW = set()
    for a in phi_adj:
        for b in phi_adj[a]:
            i, j = idx[a], idx[b]
            PhiW.add((min(i, j), max(i, j)))
    # 独立校验 1：Φ ⊆ E(W) 且是支撑 2-因子
    ok, msg = verify_two_factor(nL, LE, frozenset(PhiW))
    assert ok, f"[{tag}] Φ 校验失败: {msg}"
    cyc = cycles_of_factor(frozenset(PhiW))
    assert min(cyc) >= 4, f"[{tag}] Φ 有 <4 圈: {cyc}"
    # 反 Φ = E(W) \ Φ
    PhiMinus = set(LE) - PhiW
    ok, msg = verify_two_factor(nL, LE, frozenset(PhiMinus))
    assert ok, f"[{tag}] Φ(−M) 校验失败: {msg}"
    cycm = cycles_of_factor(frozenset(PhiMinus))
    assert min(cycm) >= 4, f"[{tag}] Φ(−M) 有 <4 圈: {cycm}"
    # 独立校验 2：划分完整（Φ ∪ Φ− = E(W)，已由集合减法保证；再验证边数）
    assert len(PhiW) + len(PhiMinus) == len(LE)
    return (tuple(sorted(cyc)), tuple(sorted(cycm)))

def run_exhaustive(smax):
    t0 = time.time()
    total = 0
    split_stat = {}
    for s in range(3, smax + 1):
        Bs = all_cubic_bipartite(s)
        cnt = 0
        for bi, B_adj in enumerate(Bs):
            c1, c2 = check_antiphi(B_adj, f"anti_s{s}#{bi}")
            split_stat[(len(c1), len(c2))] = split_stat.get((len(c1), len(c2)), 0) + 1
            cnt += 1
        total += cnt
        print(f"[exh] s={s}: {cnt} 个 B 全过  累计 {total}  {time.time()-t0:.0f}s", flush=True)
    print(f"[exh] 总计 {total} 个 L(B)：Φ(M) ⊔ Φ(−M) 全部为无三角形 2-因子分解")
    print(f"[exh] (Φ 分量数, Φ− 分量数) 分布: {dict(sorted(split_stat.items()))}")

def run_random(count):
    rng = random.Random(20260913)
    t0 = time.time()
    total = 0
    for s in range(8, 41):
        for i in range(count):
            B_adj = random_cubic_bipartite(s, rng)
            check_antiphi(B_adj, f"anti_rand_s{s}#{i}")
            total += 1
        print(f"[rand] s={s}: 累计 {total} 全过  {time.time()-t0:.0f}s", flush=True)

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "exhaustive"
    if mode == "exhaustive":
        run_exhaustive(int(sys.argv[2]) if len(sys.argv) > 2 else 6)
    else:
        run_random(int(sys.argv[2]) if len(sys.argv) > 2 else 20)
