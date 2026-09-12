#!/usr/bin/env python3
"""
r2_core.py — R2-01 AABC25 六正则猜想结构攻击：核心构造 + 独立校验器。

数学内容（对应报告 campaign/r2_01_aabc25_struct.md）：
  引理0  Petersen 2-因子分解：2k-正则图分解为 k 个边不交支撑 2-因子（此处用剥层法+搜索实现）。
  引理1  (★) 每个 4-正则简单图有含 >=4 阶圈的 2-因子。
         构造路线：任取 2-因子 F；F 非三角形则完成；否则 H = F ∪ F'（两个三角形因子），
         H ≅ L(B)（B = 关联图，3-正则二部简单），取 B 的完美匹配 M 并定向，
         构造 Φ(M)：L(B) 中在 M-尾点把匹配边与另两边连，在 M-头点把两边此连。
         Φ 是 2-因子且无三角形（所有分量长 >=4）。
  定理2  6-正则、n≡0 (mod 3) ⟹ ce(G) <= n-1。
  定理3  = AABC25 Conjecture：6-正则图分解为三个 2-因子，其一含 >=4 点分量。

图表示：n 个顶点 0..n-1；边集 set of (u,v), u<v。
"""

import random
import itertools
from collections import defaultdict

# ---------------------------------------------------------------- 基础工具

def edges_of(n, adj):
    E = set()
    for u in range(n):
        for v in adj[u]:
            if u < v:
                E.add((u, v))
    return E

def make_graph(n, edges):
    adj = defaultdict(set)
    for u, v in edges:
        assert u != v, "简单图，禁自环"
        if (u, v) not in edges and (v, u) not in edges:
            pass
        a, b = (u, v) if u < v else (v, u)
        adj[a].add(b)
        adj[b].add(a)
    return adj

def deg(adj, v):
    return len(adj[v])

def components(vertices, adj_pairs):
    """adj_pairs: dict v -> set of neighbors（子图内）。返回分量列表。"""
    seen = set()
    comps = []
    for s in vertices:
        if s in seen:
            continue
        stack, comp = [s], []
        seen.add(s)
        while stack:
            x = stack.pop()
            comp.append(x)
            for y in adj_pairs[x]:
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
        comps.append(sorted(comp))
    return comps

def edge_components(edge_set):
    """把边集拆成连通分量（边集）。返回 [component_edges,...]。"""
    vat = defaultdict(set)
    verts = set()
    for u, v in edge_set:
        vat[u].add(v)
        vat[v].add(u)
        verts.add(u)
        verts.add(v)
    seen = set()
    out = []
    for s in sorted(verts):
        if s in seen:
            continue
        stack, ce = [s], []
        seen.add(s)
        while stack:
            x = stack.pop()
            for y in vat[x]:
                e = (x, y) if x < y else (y, x)
                if e not in ce:
                    ce.append(e)
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
        out.append(frozenset(ce))
    return out

def is_simple_cycle_edges(edge_set):
    """边集是否构成一个简单圈（所有涉及点度恰 2、连通、|V|>=3）。"""
    if not edge_set:
        return False
    vat = defaultdict(set)
    for u, v in edge_set:
        vat[u].add(v)
        vat[v].add(u)
    if any(len(nb) != 2 for nb in vat.values()):
        return False
    comps = edge_components(set(edge_set))
    return len(comps) == 1 and len(vat) >= 3

# ---------------------------------------------------------------- 独立校验器（不依赖构造逻辑）

def verify_two_factor(n, full_edges, F):
    """F 是否为 (n, full_edges) 图的支撑 2-因子。"""
    F = set(F)
    if not F <= set(full_edges):
        return False, "F 含非原图边"
    d = defaultdict(int)
    for u, v in F:
        d[u] += 1
        d[v] += 1
    if any(d[v] != 2 for v in range(n)):
        return False, "存在点度 != 2"
    return True, "ok"

def cycles_of_factor(F):
    """2-因子的圈长列表。"""
    return sorted(len(c) for c in edge_components(set(F)))

def verify_decomposition(n, full_edges, pieces):
    """pieces: list of edge-set（圈边集或单边）。校验：划分 E(G)，每件单边或简单圈。"""
    allp = []
    for p in pieces:
        allp.extend(p)
    if len(allp) != len(set(allp)):
        return False, "边重复"
    if set(allp) != set(full_edges):
        return False, "未恰好覆盖 E(G)"
    for p in pieces:
        if len(p) == 1:
            continue
        if not is_simple_cycle_edges(p):
            return False, "存在既非单边又非圈的件"
    return True, "ok"

# ---------------------------------------------------------------- 搜索：2-因子 / 三角形因子

def find_two_factor(n, edges, rng=None, node_budget=2_000_000):
    """回溯搜索支撑 2-因子；返回边集或 None。"""
    adj = make_graph(n, edges)
    inc = defaultdict(list)
    for e in edges:
        u, v = e
        inc[u].append(e)
        inc[v].append(e)
    chosen = defaultdict(int)   # 点 -> 已选度
    used = set()
    budget = [node_budget]

    # 每个点需要度 2；处理顺序：候选最少的点优先
    def candidates():
        best, bestv = None, None
        for v in range(n):
            if chosen[v] >= 2:
                continue
            avail = (2 - chosen[v])
            opts = len(inc[v])
            key = (chosen[v], opts)
            if best is None or key < best:
                best, bestv = key, v
        return bestv

    def feasible():
        for v in range(n):
            if chosen[v] > 2:
                return False
            rem = sum(1 for e in inc[v] if e not in used)
            if chosen[v] + rem < 2:
                return False
        return True

    def rec():
        budget[0] -= 1
        if budget[0] < 0:
            raise RuntimeError("node budget exhausted")
        v = None
        for x in range(n):
            if chosen[x] != 2:
                v = x
                break
        if v is None:
            return True
        need = 2 - chosen[v]
        opts = [e for e in inc[v] if e not in used]
        if len(opts) < need:
            return False
        # 只在 need==2 时枚举组合；need==1 时枚举单边
        combos = itertools.combinations(opts, need)
        for cb in combos:
            for e in cb:
                used.add(e)
                u, w = e
                chosen[u] += 1
                chosen[w] += 1
            if feasible() and rec():
                return True
            for e in cb:
                u, w = e
                used.discard(e)
                chosen[u] -= 1
                chosen[w] -= 1
        return False

    if rec():
        return frozenset(used)
    return None

def find_triangle_factor(n, edges):
    """精确覆盖：用三角形覆盖全部顶点。返回 [triangle_edge_sets] 或 None。"""
    tri_list = []
    eset = set(edges)
    adj = make_graph(n, edges)
    for u, v, w in itertools.combinations(range(n), 3):
        if (u, v) in eset and (v, w) in eset and (u, w) in eset:
            tri_list.append((u, v, w))
    used = set()

    def rec():
        if len(used) == n:
            return []
        v = min(x for x in range(n) if x not in used)
        for (a, b, c) in tri_list:
            if v in (a, b, c) and not ({a, b, c} & used):
                used.update((a, b, c))
                r = rec()
                if r is not None:
                    r.append(frozenset([(min(a,b),max(a,b)), (min(b,c),max(b,c)), (min(a,c),max(a,c))]))
                    return r
                used.difference_update((a, b, c))
        return None

    r = rec()
    return r

# ---------------------------------------------------------------- 二部图匹配（Kuhn）

def bipartite_matching(left, adjLR):
    """adjLR: left vertex -> iterable of right vertices。返回 matchL dict left->right 或 None。"""
    matchR = {}
    def try_k(u, seen):
        for v in adjLR[u]:
            if v in seen:
                continue
            seen.add(v)
            if v not in matchR or try_k(matchR[v], seen):
                matchR[v] = u
                return True
        return False
    matchL = {}
    for u in left:
        if not try_k(u, set()):
            return None
    matchL = {u: v for v, u in matchR.items()}
    return matchL

def matchR_inv(matchR, u):
    for v, w in matchR.items():
        if w == u:
            return v
    return None

# ---------------------------------------------------------------- L(B) 机器（引理 1 的构造）

def incidence_graph(trisA, trisB, n):
    """两个边不交三角形因子 -> 关联图 B（二部 3-正则简单）。
    顶点编码：A 侧 i（i<len(trisA)），B 侧 len(trisA)+j。
    返回 (B_adj, vmap)；vmap: 顶点 v of G -> (i, j)。"""
    locA = {}
    for i, t in enumerate(trisA):
        for v in tri_vertices(t):
            locA[v] = i
    locB = {}
    for j, t in enumerate(trisB):
        for v in tri_vertices(t):
            locB[v] = j
    B_adj = defaultdict(set)
    vmap = {}
    for v in range(n):
        i, j = locA[v], locB[v]
        B_adj[i].add(len(trisA) + j)
        B_adj[len(trisA) + j].add(i)
        vmap[v] = (i, j)
    return dict(B_adj), vmap, len(trisA), len(trisB)

def tri_vertices(t_edge_set):
    vat = defaultdict(set)
    for u, v in t_edge_set:
        vat[u].add(v)
        vat[v].add(u)
    assert len(vat) == 3
    return tuple(sorted(vat))

def construct_phi(B_adj, nA, nB, orient=None, rng=None):
    """B：3-正则二部（左 0..nA-1，右 nA..nA+nB-1）。
    取完美匹配 M，定向（默认左->右），构造 Φ。
    返回 (phi_adj (L(B)顶点=B边的 dict), M, ok_flags)。"""
    left = list(range(nA))
    adjLR = {u: set(B_adj[u]) for u in left}
    m = bipartite_matching(left, adjLR)
    assert m is not None, "3-正则二部图必有完美匹配（Hall）"
    M = {}
    for u in left:
        w = m[u]
        M[frozenset((u, w))] = (u, w)   # 尾=u, 头=w
    # Φ：L(B) 顶点 = B 的边 e={x,y}；Φ 邻接只允许同端点的 B 边之间
    # 尾点 x：matched(x) 与 x 处另两条边各连一条；头点 y：另两条边互连
    tail = {}   # B顶点 -> True 若它是其匹配边的尾
    for e, (u, w) in M.items():
        tail[u] = True
        tail[w] = False
    # 每个 B 顶点处选定的 Φ 邻接对
    phi_pairs = []
    for x in list(range(nA + nB)):
        nb = [y for y in B_adj[x]]
        assert len(nb) == 3
        e = frozenset((x, m.get(x, None)) ) if x in m else None
        # 找 x 的匹配边
        if x < nA:
            ex = (x, m[x])
        else:
            ex = None
            for u, w in M.values():
                if w == x:
                    ex = (u, w)
        me = frozenset(ex)
        others = [frozenset((x, y)) for y in nb if frozenset((x, y)) != me]
        assert len(others) == 2
        o1, o2 = others
        if tail.get(x, False):
            phi_pairs.append((me, o1))
            phi_pairs.append((me, o2))
        else:
            phi_pairs.append((o1, o2))
    phi_adj = defaultdict(set)
    for a, b in phi_pairs:
        phi_adj[a].add(b)
        phi_adj[b].add(a)
    return phi_adj, M, m

def phi_components(phi_adj):
    """Φ 的分量：顶点 = B 边（frozenset），邻接 = phi_adj。"""
    verts = list(phi_adj.keys())
    seen = set()
    out = []
    for s in verts:
        if s in seen:
            continue
        stack, comp = [s], []
        seen.add(s)
        while stack:
            x = stack.pop()
            comp.append(x)
            for y in phi_adj[x]:
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
        out.append(comp)
    return out

# ---------------------------------------------------------------- 主定理构造性证明流水线

def phi_route_from_pair(n, H_edges, trisF, trisFp, name="H"):
    """pipeline_star 的 Φ 分支：给定两个边不交三角形因子，执行
    incidence -> B -> perfect matching -> 定向 -> Φ -> 全部独立校验。
    返回 (Phi_edge_set, info)。"""
    trisF = [frozenset(c) for c in trisF]
    trisFp = [frozenset(c) for c in trisFp]
    B_adj, vmap, nA, nB = incidence_graph(trisF, trisFp, n)
    for u in B_adj:
        assert len(B_adj[u]) == 3, f"[{name}] B 非 3-正则"
    B_edges = set()
    for u in B_adj:
        for w in B_adj[u]:
            B_edges.add(frozenset((u, w)))
    assert len(B_edges) == n, f"[{name}] |E(B)| != |V(H)|"
    vmap2 = {}
    for v, (i, j) in vmap.items():
        vmap2[v] = frozenset((i, nA + j))
    assert set(vmap2.values()) == B_edges, f"[{name}] vmap 与 B 边不一致"
    phi_adj, M, m = construct_phi(B_adj, nA, nB)
    for e in B_edges:
        assert len(phi_adj[e]) == 2, f"[{name}] Φ 度 != 2"
    inv = {e: v for v, e in vmap2.items()}
    H_adj = make_graph(n, H_edges)
    for e in B_edges:
        for f in phi_adj[e]:
            ve, vf = inv[e], inv[f]
            assert vf in H_adj[ve], f"[{name}] Φ 邻接不是 H 边"
    comps = phi_components(phi_adj)
    lens = [len(c) for c in comps]
    assert all(L >= 4 for L in lens), f"[{name}] Φ 存在 <4 长分量: {sorted(lens)}"
    Phi = set()
    for e in B_edges:
        for f in phi_adj[e]:
            ve, vf = inv[e], inv[f]
            Phi.add((min(ve, vf), max(ve, vf)))
    ok, msg = verify_two_factor(n, H_edges, Phi)
    assert ok, f"[{name}] Φ 校验失败: {msg}"
    return frozenset(Phi), {"B": B_adj, "components": sorted(lens)}

def pipeline_star(H_n, H_edges, name="H"):
    """引理1：返回 H 的含 >=4 圈的 2-因子（边集），并全程独立校验。"""
    F = find_two_factor(H_n, H_edges)
    assert F is not None, f"[{name}] 4-正则图应有 2-因子"
    ok, msg = verify_two_factor(H_n, H_edges, F)
    assert ok, f"[{name}] F 校验失败: {msg}"
    cyc = cycles_of_factor(F)
    if max(cyc) >= 4:
        return F, "first-factor"
    # F 是三角形因子；F' = H - F 也是 2-因子
    trisF = edge_components(set(F))
    Fp = frozenset(H_edges) - set(F)
    ok, msg = verify_two_factor(H_n, H_edges, Fp)
    assert ok, f"[{name}] F' 校验失败: {msg}"
    cycp = cycles_of_factor(Fp)
    if max(cycp) >= 4:
        return Fp, "second-factor"
    # 两个都是三角形因子 -> L(B) 构造
    trisFp = edge_components(set(Fp))
    B_adj, vmap, nA, nB = incidence_graph(trisF, trisFp, H_n)
    # B 简单性（核心证明步骤：两三角形至多交一点）
    for u in B_adj:
        assert len(B_adj[u]) == 3, f"[{name}] B 非 3-正则"
    # B 边 = L(B) 顶点
    B_edges = set()
    for u in B_adj:
        for w in B_adj[u]:
            B_edges.add(frozenset((u, w)))
    assert len(B_edges) == H_n, f"[{name}] |E(B)| != |V(H)|"
    # vmap: H 顶点 -> B 边
    vmap2 = {}
    for v, (i, j) in vmap.items():
        vmap2[v] = frozenset((i, nA + j))
    # 一致性：B 边集合 = vmap2 值集合
    assert set(vmap2.values()) == B_edges, f"[{name}] vmap 与 B 边不一致"
    phi_adj, M, m = construct_phi(B_adj, nA, nB)
    # 校验 Φ 度数
    for e in B_edges:
        assert len(phi_adj[e]) == 2, f"[{name}] Φ 度 != 2"
    # 校验 Φ 的每条邻接对应 H 的真边：B 边 e,f 相邻（共享端点）⟺ vmap2^{-1} 两 H 点相邻
    inv = {e: v for v, e in vmap2.items()}
    H_adj = make_graph(H_n, H_edges)
    for e in B_edges:
        for f in phi_adj[e]:
            ve, vf = inv[e], inv[f]
            assert vf in H_adj[ve], f"[{name}] Φ 邻接不是 H 边"
    comps = phi_components(phi_adj)
    lens = [len(c) for c in comps]
    assert all(L >= 4 for L in lens), f"[{name}] Φ 存在 <4 长分量: {sorted(lens)}"
    Phi = set()
    for e in B_edges:
        for f in phi_adj[e]:
            ve, vf = inv[e], inv[f]
            Phi.add((min(ve, vf), max(ve, vf)))
    ok, msg = verify_two_factor(H_n, H_edges, Phi)
    assert ok, f"[{name}] Φ 校验失败: {msg}"
    return frozenset(Phi), "phi-construction"

def pipeline_6reg(n, G_edges, name="G"):
    """定理2/3 构造性证明：返回 (pieces, info)。全程校验。"""
    m = len(G_edges)
    assert all(len(make_graph(n, G_edges)[v]) == 6 for v in range(n)), f"[{name}] 非 6-正则"
    # 三个 2-因子分解
    E = set(G_edges)
    factors = []
    for it in range(3):
        degs = defaultdict(int)
        for u, v in E:
            degs[u] += 1
            degs[v] += 1
        k = degs[0]
        assert all(d == 6 - 2 * it for d in degs.values()), f"[{name}] 第{it}步非 {6-2*it}-正则"
        F = find_two_factor(n, E)
        assert F is not None, f"[{name}] 2-因子搜索失败 (iter {it})"
        ok, msg = verify_two_factor(n, E, F)
        assert ok, f"[{name}] 2-因子校验失败: {msg}"
        factors.append(set(F))
        E -= set(F)
    F0, F1, F2 = map(frozenset, factors)
    info = {"route": None}
    if max(cycles_of_factor(F0)) >= 4:
        # 路线 A：F0 直接有 >=4 圈
        pieces = [set(c) for c in edge_components(set(F0))] + \
                 [set(c) for c in edge_components(F1)] + \
                 [set(c) for c in edge_components(F2)]
        info["route"] = "A(first factor non-triangular)"
        info["factor_pieces"] = [len(edge_components(F0)), len(edge_components(F1)), len(edge_components(F2))]
    else:
        # F0 是三角形因子；H = G - F0 是 4-正则
        H_edges = frozenset(G_edges) - set(F0)
        S, how = pipeline_star(n, H_edges, name=name + "/H")
        T = H_edges - set(S)
        ok, msg = verify_two_factor(n, H_edges, T)
        assert ok, f"[{name}] T 校验失败: {msg}"
        pieces = [set(c) for c in edge_components(set(F0))] + \
                 [set(c) for c in edge_components(set(S))] + \
                 [set(c) for c in edge_components(T)]
        info["route"] = f"B(triangle factor; H-star via {how})"
        info["factor_pieces"] = [len(edge_components(F0)), len(edge_components(S)), len(edge_components(T))]
    ok, msg = verify_decomposition(n, G_edges, pieces)
    assert ok, f"[{name}] 分解校验失败: {msg}"
    info["pieces"] = len(pieces)
    info["n_minus_1"] = n - 1
    assert len(pieces) <= n - 1, f"[{name}] 件数 {len(pieces)} > n-1"
    return pieces, info

# ---------------------------------------------------------------- 随机图生成

def random_regular(n, d, rng, swaps=4000):
    """循环图起点 + 度保持交换 MCMC（稠密正则图配置模型拒绝率过高，不可用）。"""
    assert (n * d) % 2 == 0 and d < n
    k = d // 2
    if d % 2 == 0:
        E = {(i, (i + s) % n) if i < (i + s) % n else ((i + s) % n, i)
             for i in range(n) for s in range(1, k + 1)}
    else:
        E = {(i, (i + s) % n) if i < (i + s) % n else ((i + s) % n, i)
             for i in range(n) for s in range(1, k + 1)}
        E |= {(i, (i + n // 2) % n) for i in range(n // 2)}  # 完美匹配（n 偶）
    E = list(E)
    assert all(0 <= u < n and 0 <= v < n and u != v for u, v in E)
    adj0 = make_graph(n, set(E))
    assert all(len(adj0[v]) == d for v in range(n)), "起点构造非正则"
    acc = 0
    tries = 0
    while acc < swaps and tries < swaps * 10:
        tries += 1
        i, j = rng.randrange(len(E)), rng.randrange(len(E))
        if i == j:
            continue
        a, b = E[i]
        c, e = E[j]
        if len({a, b, c, e}) < 4:
            continue
        if rng.random() < 0.5:
            n1, n2 = (a, c), (b, e)
        else:
            n1, n2 = (a, e), (b, c)
        n1 = (min(n1), max(n1))
        n2 = (min(n2), max(n2))
        if n1 == n2 or n1 in set(E) - {E[i], E[j]} or n2 in set(E) - {E[i], E[j]}:
            continue
        E[i], E[j] = n1, n2
        acc += 1
    Eset = frozenset(E)
    adj = make_graph(n, Eset)
    if all(len(adj[v]) == d for v in range(n)):
        return Eset
    return None

def random_cubic_bipartite(s, rng):
    """s+s 顶点 3-正则二部随机（配置模型）。返回 B_adj (left 0..s-1, right s..2s-1)。"""
    while True:
        stubsL = [v for v in range(s) for _ in range(3)]
        stubsR = [v + s for v in range(s) for _ in range(3)]
        rng.shuffle(stubsR)
        E = set()
        ok = True
        for i in range(3 * s):
            u, v = stubsL[i], stubsR[i]
            e = frozenset((u, v))
            if e in E:
                ok = False
                break
            E.add(e)
        if not ok:
            continue
        adj = defaultdict(set)
        for e in E:
            u, v = tuple(e)
            adj[u].add(v)
            adj[v].add(u)
        return dict(adj)

# ---------------------------------------------------------------- L(B) 全族生成（危险类穷举）

def all_cubic_bipartite(s, cap=400_000_000):
    """枚举全部 s+s 顶点 3-正则简单二部图（标记版，邻接表 dict）。左 0..s-1 右 s..2s-1。"""
    res = []
    # 回溯：逐个左点选 3 个右邻居，维护右度 <=3
    choice = []
    rdeg = [0] * s
    cnt = [0]
    def rec(i):
        cnt[0] += 1
        if cnt[0] > cap:
            raise RuntimeError("cap")
        if i == s:
            adj = defaultdict(set)
            for u, nb in enumerate(choice):
                for v in nb:
                    adj[u].add(v + s)
                    adj[v + s].add(u)
            res.append(dict(adj))
            return
        for cb in itertools.combinations(range(s), 3):
            if any(rdeg[v] >= 3 for v in cb):
                continue
            for v in cb:
                rdeg[v] += 1
            choice.append(cb)
            rec(i + 1)
            choice.pop()
            for v in cb:
                rdeg[v] -= 1
    rec(0)
    return res

def line_graph_of_B(B_adj):
    """L(B)：顶点 = B 边（frozenset），相邻 = 共享端点。返回 (verts list, index map, edge set of L)。"""
    B_edges = set()
    for u in B_adj:
        for v in B_adj[u]:
            B_edges.add(frozenset((u, v)))
    verts = list(B_edges)
    idx = {e: i for i, e in enumerate(verts)}
    LE = set()
    for i, e in enumerate(verts):
        for j, f in enumerate(verts):
            if i < j and (e & f):
                LE.add((i, j))
    return verts, idx, LE, len(verts)

def brute_long_two_factor(n, edges, max_nodes=4_000_000):
    """独立于构造：回溯搜索一个含 >=4 圈的 2-因子（不使用 L(B)/Φ 逻辑）。
    枚举 2-因子，遇到含 >=4 圈即返回；超过 node 预算仍未找到则返回 None。"""
    found = []
    result = [None]
    # 复用 find_two_factor 的骨架，但需要枚举多个解
    adj = make_graph(n, edges)
    inc = defaultdict(list)
    for e in edges:
        u, v = e
        inc[u].append(e)
        inc[v].append(e)
    chosen = defaultdict(int)
    used = set()
    budget = [max_nodes]
    def feasible():
        for v in range(n):
            if chosen[v] > 2:
                return False
            rem = sum(1 for e in inc[v] if e not in used)
            if chosen[v] + rem < 2:
                return False
        return True
    def rec():
        budget[0] -= 1
        if budget[0] < 0:
            raise TimeoutError
        v = None
        for x in range(n):
            if chosen[x] != 2:
                v = x
                break
        if v is None:
            cyc = cycles_of_factor(frozenset(used))
            if max(cyc) >= 4:
                result[0] = frozenset(used)
                return True
            return False
        need = 2 - chosen[v]
        opts = [e for e in inc[v] if e not in used]
        if len(opts) < need:
            return False
        for cb in itertools.combinations(opts, need):
            for e in cb:
                used.add(e)
                u, w = e
                chosen[u] += 1
                chosen[w] += 1
            if feasible() and rec():
                return True
            for e in cb:
                u, w = e
                used.discard(e)
                chosen[u] -= 1
                chosen[w] -= 1
        return False
    try:
        rec()
    except TimeoutError:
        return "timeout"
    return result[0]
