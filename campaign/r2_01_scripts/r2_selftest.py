#!/usr/bin/env python3
"""r2_selftest.py — 核心构造自检（含人工锚点）。"""
import sys, itertools
sys.path.insert(0, "/Users/munich/Desktop/数学/front184/campaign/r2_01_scripts")
from r2_core import *

def test_phi_on_rook():
    # B = K_{3,3}: left {0,1,2}, right {3,4,5}, 完全二部
    B_adj = {0: {3,4,5}, 1: {3,4,5}, 2: {3,4,5},
             3: {0,1,2}, 4: {0,1,2}, 5: {0,1,2}}
    verts, idx, LE, N = line_graph_of_B(B_adj)
    # L(K_{3,3}) = 3x3 rook graph, 9 顶点 4-正则
    adjL = make_graph(N, LE)
    assert all(len(adjL[v]) == 4 for v in range(N)), "L(B) 应 4-正则"
    # 穷举 K_{3,3} 全部 6 个完美匹配 × 定向，构造 Φ，验证 2-因子且无三角形
    import itertools as it
    perms = list(it.permutations([3,4,5]))
    seen_lens = set()
    for p in perms:
        M = {frozenset((u, p[u])): (u, p[u]) for u in [0,1,2]}
        # 手工构造 phi（复用 construct_phi 但注入 M 不便，直接重算）
        # 用 construct_phi 的默认匹配 + 默认定向
        phi_adj, M2, m = construct_phi(B_adj, 3, 3)
        assert all(len(phi_adj[e]) == 2 for e in phi_adj)
        comps = phi_components(phi_adj)
        lens = sorted(len(c) for c in comps)
        seen_lens.add(tuple(lens))
        assert all(L >= 4 for L in lens), f"Φ 有 <4 分量: {lens}"
        break  # construct_phi 匹配固定，定向固定；穷举见下
    # 穷举所有 (匹配, 定向) 组合
    cnt = 0
    for p in perms:
        for orient_bits in range(8):  # 3 条匹配边各两个方向
            # 重新实现定向逻辑：M 边 e=(u,p[u])，尾= u or p[u]
            M = {frozenset((u, p[u])): (u, p[u]) for u in [0,1,2]}
            tails = {}
            bits = [(orient_bits >> k) & 1 for k in range(3)]
            for k, u in enumerate([0,1,2]):
                e = frozenset((u, p[u]))
                # bit=0: 尾=左 u；bit=1: 尾=右 p[u]
                tails[u] = (bits[k] == 0)
                tails[p[u]] = (bits[k] == 1)
            phi_pairs = []
            for x in range(6):
                nb = sorted(B_adj[x])
                me = None
                for e, (a, b) in M.items():
                    if x in (a, b):
                        me = e
                others = [frozenset((x, y)) for y in nb if frozenset((x, y)) != me]
                o1, o2 = others
                if tails[x]:
                    phi_pairs += [(me, o1), (me, o2)]
                else:
                    phi_pairs += [(o1, o2)]
            phi_adj = defaultdict(set)
            for a, b in phi_pairs:
                phi_adj[a].add(b)
                phi_adj[b].add(a)
            assert all(len(v) == 2 for v in phi_adj.values()), "度 !=2"
            comps = phi_components(phi_adj)
            lens = sorted(len(c) for c in comps)
            assert all(L >= 4 for L in lens), f"FAIL: 定向组合 {orient_bits}, 排列 {p}, 分量 {lens}"
            seen_lens.add(tuple(lens))
            cnt += 1
    print(f"[rook] K3,3 全部 {cnt} 个 (匹配,定向) 组合: Φ 均为 2-因子且分量长>=4；分量型集合 {sorted(seen_lens)}")

def test_star_small():
    # n=5: K5（唯一 4-正则）；n=6: K6-PM（八面体，唯一 4-正则）；n=7: 补 2-正则两类
    K5 = set(itertools.combinations(range(5), 2))
    F, how = pipeline_star(5, frozenset(K5), "K5")
    assert max(cycles_of_factor(F)) >= 4
    print(f"[K5] 2-因子圈长 {cycles_of_factor(F)} (route={how})")
    pm = {(i, i+3) for i in range(3)}  # K6-PM（八面体）：唯一 4-正则 n=6
    n = 6
    K6 = set(itertools.combinations(range(n), 2))
    G = K6 - pm
    adj = make_graph(n, G)
    assert all(len(adj[v]) == 4 for v in range(n)), "K6-PM 应 4-正则"
    F, how = pipeline_star(n, frozenset(G), "K6-PM")
    assert max(cycles_of_factor(F)) >= 4
    print(f"[K6-PM(八面体)] 2-因子圈长 {cycles_of_factor(F)} (route={how})")
    # n=7 4-正则两类：K7-C7, K7-(C4+C3)
    K7 = set(itertools.combinations(range(7), 2))
    c7 = {(min(i,(i+1)%7), max(i,(i+1)%7)) for i in range(7)}
    c4c3 = {(0,1),(1,2),(2,3),(0,3)} | {(4,5),(5,6),(4,6)}
    for name, H2 in [("K7-C7", c7), ("K7-(C4+C3)", c4c3)]:
        G = K7 - H2
        adj = make_graph(7, G)
        assert all(len(adj[v]) == 4 for v in range(7))
        F, how = pipeline_star(7, frozenset(G), name)
        assert max(cycles_of_factor(F)) >= 4
        print(f"[{name}] 2-因子圈长 {cycles_of_factor(F)} (route={how})")

def test_pipeline_6reg_anchors():
    # 6-正则锚点：K7（n=7, 6-正则）；K8-PM（n=8, 6-正则）
    K7 = set(itertools.combinations(range(7), 2))
    pieces, info = pipeline_6reg(7, frozenset(K7), "K7")
    print(f"[K7] pieces={len(pieces)} (n-1=6) route={info['route']} factor_pieces={info['factor_pieces']}")
    pm = {(i, i+4) for i in range(4)}
    K8 = set(itertools.combinations(range(8), 2))
    G8 = frozenset(K8 - pm)
    pieces, info = pipeline_6reg(8, G8, "K8-PM")
    print(f"[K8-PM] pieces={len(pieces)} (n-1=7) route={info['route']} factor_pieces={info['factor_pieces']}")
    # K_{3,3,3}（n=9, 6-正则）
    E = set()
    A, B, C = [0,1,2], [3,4,5], [6,7,8]
    for X, Y in itertools.combinations([A,B,C], 2):
        for u in X:
            for v in Y:
                E.add((min(u,v), max(u,v)))
    pieces, info = pipeline_6reg(9, frozenset(E), "K333")
    print(f"[K333] pieces={len(pieces)} (n-1=8) route={info['route']} factor_pieces={info['factor_pieces']}")

def test_ce_solver_anchor():
    # 精确 ce 求解器锚点（与 Lane05 独立的实现，锚定人工值）
    from r2_ce import exact_ce
    assert exact_ce(5, frozenset((4, i) for i in range(4))) == 4, "星 K1,4=4"
    # 附加：轮 W5（C4+中心连全部）= 2 件（两个梯形圈? 实际：外圈4边+2辐条 与 2辐条+2外边? 手算难，仅打印）
    W5 = set(itertools.combinations([0,1,2,3],2)) - {(0,2),(1,3)}
    W5 |= {(4,0),(4,1),(4,2),(4,3)}
    print("  W5 ce =", exact_ce(5, frozenset(W5)))
    E = {(u, v) for u in range(2) for v in range(2, 5)}
    assert exact_ce(5, frozenset((min(u,v), max(u,v)) for u,v in E)) == 3, "K2,3=3"
    E = {(u, v) for u in range(3) for v in range(3, 6)}
    assert exact_ce(6, frozenset((min(u,v), max(u,v)) for u,v in E)) == 4, "K3,3=4"
    E2 = set(itertools.combinations([0,1,2],2)) | {(u,v) for u in range(3) for v in range(3,7)}
    assert exact_ce(7, frozenset((min(u,v),max(u,v)) for u,v in E2)) == 7, "K3∪K3,4=7"
    print("[ce] 人工锚点全过: K1,4=4, K2,3=3, K3,3=4, K3∪K3,4=7")

if __name__ == "__main__":
    test_ce_solver_anchor()
    test_phi_on_rook()
    test_star_small()
    test_pipeline_6reg_anchors()
    print("ALL SELFTESTS PASSED")
