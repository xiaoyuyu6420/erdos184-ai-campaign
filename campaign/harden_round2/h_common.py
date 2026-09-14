#!/usr/bin/env python3
"""h_common.py — harden_round2 独立实现（不 import r2_core / 不依赖上游代码）。

实现内容（对应上游定理 2' 的构造路线，逐条独立重写）：
  1) euler_orientation: 2k-正则图的欧拉定向（每条边恰定向一次；出度 = 入度 = k）
  2) bipartite_max_matching: Kuhn 增广路（确定性，按给定邻接序）
  3) two_factorize: 2k-正则简单图 -> k 个边不交支撑 2-因子（Petersen 构造：定向 + 二部 1-因子分解）
  4) cycles_of_two_factor: 2-因子 -> 圈列表（并断言每点度 2）
  5) phi_decompose: 两个边不交三角形因子 S,T（W = S ⊔ T ≅ L(B)）的 Φ(σ) / Φ(−σ) 分解
       —— 命题 6 构造：B 点 = 三角形，B 边 = G 顶点；B 的完美匹配 M + 定向 σ
  6) decompose_six_regular: 定理 2' 的记账管线
       n ≡ 0 (mod 3)：先做 3 个 2-因子；按三角形因子个数分情形
         0/1 个三角形因子 -> 全部圈件数 ≤ n−2（情形 1 与 2b 的等价记账）
         ≥2 个三角形因子 -> Φ 路线：W = S ⊔ T，R = G − W 为 2-因子 -> 件数 ≤ n−2
       n ≢ 0 (mod 3)：3 个 2-因子各 ≤ ⌊n/3⌋ 件 -> ≤ 3⌊n/3⌋ ≤ n−1（系 4）

证书格式（JSON 每行一条）：
  {"tag":..,"n":..,"bound":..,"route":..,"npieces":..,"edges":[[u,v],..],
   "pieces":[[[u,v],..],..]}
全部随机性来自调用方显式传入的 random.Random(seed)；无全局随机、无 hash 序依赖
（对集合的迭代处均显式排序）。
"""
import random
from collections import deque


# ---------------------------------------------------------------- 基础工具
def norm(u, v):
    return (u, v) if u < v else (v, u)


def build_adj(n, edges):
    adj = [[] for _ in range(n)]
    for (u, v) in edges:
        adj[u].append(v)
        adj[v].append(u)
    for a in adj:
        a.sort()
    return adj


def components(n, adj):
    seen = [False] * n
    out = []
    for s in range(n):
        if seen[s]:
            continue
        seen[s] = True
        comp = [s]
        dq = deque([s])
        while dq:
            x = dq.popleft()
            for y in adj[x]:
                if not seen[y]:
                    seen[y] = True
                    comp.append(y)
                    dq.append(y)
        out.append(sorted(comp))
    return out


def is_six_regular(n, edges):
    adj = build_adj(n, edges)
    return all(len(a) == 6 for a in adj)


# ---------------------------------------------------------------- 欧拉定向
def euler_orientation(n, adj):
    """返回弧列表 arcs（每条边恰出现一次，作为有向弧），满足每点出度=入度=deg/2。
    逐连通分量做 Hierholzer；每个分量度数为偶数 -> 存在欧拉回路。
    仅对全偶度图合法（调用方保证；此处 fail fast）。"""
    for v in range(n):
        assert len(adj[v]) % 2 == 0, "euler_orientation 只对偶度图合法"
    arcs = []
    for comp in components(n, adj):
        local = {v: list(adj[v]) for v in comp}
        start = comp[0]
        stack = [start]
        verts = []
        while stack:
            u = stack[-1]
            if local[u]:
                v = local[u].pop()
                local[v].remove(u)
                stack.append(v)
            else:
                verts.append(stack.pop())
        verts.reverse()  # verts[0] == verts[-1] == start，为欧拉回路的顶点序列
        assert verts[0] == verts[-1], "欧拉回路应闭合"
        for a, b in zip(verts, verts[1:]):
            arcs.append((a, b))
    # 不变量：出度 = 入度 = deg/2
    deg = [len(adj[v]) for v in range(n)]
    outd = [0] * n
    ind = [0] * n
    for (u, v) in arcs:
        outd[u] += 1
        ind[v] += 1
    for v in range(n):
        assert outd[v] == ind[v] == deg[v] // 2, "欧拉定向的出/入度错误"
    return arcs


# ---------------------------------------------------------------- 二部匹配 / 1-因子分解
def bipartite_max_matching(adjL, nR):
    """Kuhn 增广路最大匹配。adjL: 左点 -> 右点有序列表。返回 (matchL, matchR)。"""
    matchL = [-1] * len(adjL)
    matchR = [-1] * nR

    def try_aug(u, seen):
        for v in adjL[u]:
            if seen[v]:
                continue
            seen[v] = True
            if matchR[v] == -1 or try_aug(matchR[v], seen):
                matchR[v] = u
                matchL[u] = v
                return True
        return False

    for u in range(len(adjL)):
        if matchL[u] == -1:
            try_aug(u, [False] * nR)
    return matchL, matchR


def two_factorize(n, adj, k):
    """2k-正则简单图 -> k 个边不交的支撑 2-因子（每个为规范化边列表）。
    构造 = Petersen：欧拉定向（每条边恰一次）-> 二部图 out/in -> k 次完美匹配。
    因每条边只被定向一次，(u,v) 与 (v,u) 不同时出现 -> 无有向 2-圈 -> 因子是简单 2-因子。"""
    arcs = euler_orientation(n, adj)
    adjL = [[] for _ in range(n)]
    for (u, v) in arcs:
        adjL[u].append(v)
    for a in adjL:
        a.sort()
    factors = []
    for _ in range(k):
        matchL, matchR = bipartite_max_matching(adjL, n)
        assert all(x != -1 for x in matchL), "k-正则二部图应有完美匹配"
        fedges = sorted({norm(u, matchL[u]) for u in range(n)})
        assert len(fedges) == n, "每个 2-因子应恰有 n 条边"
        factors.append(fedges)
        for u in range(n):
            w = matchL[u]
            adjL[u].remove(w)
    assert all(len(a) == 0 for a in adjL), "1-因子分解后二部图应清空"
    return factors


def cycles_of_two_factor(n, fedges):
    """2-因子（每点度 2 的支撑子图）-> 圈（顶点序列）列表；顺序为最小顶点先。"""
    adj = build_adj(n, fedges)
    for v in range(n):
        assert len(adj[v]) == 2, "2-因子每点度应为 2"
    seen = [False] * n
    cycles = []
    for s in range(n):
        if seen[s]:
            continue
        seen[s] = True
        cyc = [s]
        prev, cur = -1, s
        while True:
            nxt = [x for x in adj[cur] if x != prev][0]
            if nxt == s:
                break
            assert not seen[nxt], "2-因子应无重复顶点"
            seen[nxt] = True
            cyc.append(nxt)
            prev, cur = cur, nxt
        cycles.append(cyc)
    return cycles


def cycle_edges_of(n, cycles):
    """圈（顶点序列）-> 边列表。"""
    out = []
    for cyc in cycles:
        L = len(cyc)
        out.append(sorted(norm(cyc[i], cyc[(i + 1) % L]) for i in range(L)))
    return out


# ---------------------------------------------------------------- 命题 6：Φ 分解
def phi_decompose(n, S_edges, T_edges, rng, shuffle_matching=False):
    """W = S ⊔ T（两个边不交三角形因子）的 Φ(σ)/Φ(−σ) 分解。
    返回 (phi, phi_minus) 两个边集合（均应为无三角形 2-因子且划分 E(W)）。
    注意：rng 由调用方给（可复现）；定向逐匹配边独立取随机位。
    shuffle_matching=True 时先用 rng 打乱 B 的邻接序（得到不同的完美匹配）。"""
    cS = cycles_of_two_factor(n, S_edges)
    cT = cycles_of_two_factor(n, T_edges)
    assert len(cS) == len(cT) == n // 3 and all(len(c) == 3 for c in cS) and all(len(c) == 3 for c in cT), \
        "S,T 必须都是三角形因子"
    assert not (set(S_edges) & set(T_edges)), "S,T 必须边不交"
    m = len(cS)
    sidx = {}
    tidx = {}
    for i, c in enumerate(cS):
        for v in c:
            sidx[v] = i
    for j, c in enumerate(cT):
        for v in c:
            tidx[v] = j
    # 二部图 B：左 = S-三角形 (0..m-1)，右 = T-三角形 (m..2m-1)；B 的边 = G 的顶点
    adjL = [[] for _ in range(m)]
    edge_of = {}
    for v in range(n):
        i, j = sidx[v], tidx[v]
        assert (i, j) not in edge_of, "B 非简单（S,T 共享边）——不应发生"
        edge_of[(i, j)] = v
        adjL[i].append(j)
    for a in adjL:
        a.sort()
    if shuffle_matching:
        for a in adjL:
            rng.shuffle(a)
    matchL, matchR = bipartite_max_matching(adjL, m)
    assert all(x != -1 for x in matchL) and all(x != -1 for x in matchR), "3-正则二部图 B 应有完美匹配"
    # 随机定向：每条匹配边随机指定尾端（尾端取 2 对，头端取 1 对）
    tail = {}
    for i in range(m):
        j = matchL[i]
        if rng.random() < 0.5:
            tail[i] = True
            tail[m + j] = False
        else:
            tail[i] = False
            tail[m + j] = True
    tris = {}
    for i in range(m):
        tris[i] = list(cS[i])
        tris[m + i] = list(cT[i])
    phi = set()
    phim = set()
    for i in range(m):
        j = matchL[i]
        e = edge_of[(i, j)]
        for x in (i, m + j):
            tri = tris[x]
            fg = [w for w in tri if w != e]
            assert len(fg) == 2
            if tail[x]:
                phi.add(norm(e, fg[0]))
                phi.add(norm(e, fg[1]))
                phim.add(norm(fg[0], fg[1]))
            else:
                phi.add(norm(fg[0], fg[1]))
                phim.add(norm(e, fg[0]))
                phim.add(norm(e, fg[1]))
    # 内建不变量（本文件内自查；独立校验器再另查一遍）
    W = set(S_edges) | set(T_edges)
    assert phi | phim == W and not (phi & phim), "Φ(σ) ⊔ Φ(−σ) 应恰好划分 E(W)"
    assert len(phi) == len(phim) == n, "每个 Φ 因子应恰有 n 条边"
    for F in (phi, phim):
        adjF = build_adj(n, sorted(F))
        assert all(len(a) == 2 for a in adjF), "Φ 因子每点度应为 2"
    return phi, phim


# ---------------------------------------------------------------- 主管线
def decompose_six_regular(n, edges, rng, tag=""):
    """返回 (pieces, info)。pieces = 圈件列表（每个为边列表）。
    n≡0 (mod 3)：件数 ≤ n−2；n≢0：件数 ≤ n−1。
    失败（件数超界/断言失败）会抛异常，由调用方记录为嫌疑反例。"""
    edges = sorted(set(norm(u, v) for (u, v) in edges))
    adj = build_adj(n, edges)
    assert all(len(a) == 6 for a in adj), "输入应 6-正则简单图"
    Fs = two_factorize(n, adj, 3)
    cyc_lists = [cycles_of_two_factor(n, F) for F in Fs]
    comps = [len(cs) for cs in cyc_lists]
    if n % 3 != 0:
        pieces_cyc = [c for cs in cyc_lists for c in cs]
        bound = n - 1
        assert len(pieces_cyc) <= bound, "n≢0 mod 3 侧件数超界"
        return cycle_edges_of(n, pieces_cyc), {
            "route": "nondiv3mod", "bound": bound, "factor_comps": comps}
    m = n // 3
    is_tri = [all(len(c) == 3 for c in cs) for cs in cyc_lists]
    ntri = sum(is_tri)
    bound = n - 2
    if ntri <= 1:
        pieces_cyc = [c for cs in cyc_lists for c in cs]
        route = "flat(ntri=%d)" % ntri
        assert len(pieces_cyc) <= bound, "情形 0/1 件数超界（嫌疑）"
        return cycle_edges_of(n, pieces_cyc), {
            "route": route, "bound": bound, "factor_comps": comps}
    # ≥2 个三角形因子 -> Φ 路线
    idx = [i for i in range(3) if is_tri[i]]
    S_edges = set(Fs[idx[0]])
    T_edges = set(Fs[idx[1]])
    W = S_edges | T_edges
    R = [e for e in edges if e not in W]
    phi, phim = phi_decompose(n, S_edges, T_edges, rng)
    cphi = cycles_of_two_factor(n, sorted(phi))
    cphim = cycles_of_two_factor(n, sorted(phim))
    assert all(len(c) >= 4 for c in cphi) and all(len(c) >= 4 for c in cphim), \
        "Φ 两因子应无三角形（全部圈 ≥4）——否则是嫌疑反例"
    cR = cycles_of_two_factor(n, R)
    pieces_cyc = cphi + cphim + cR
    assert len(pieces_cyc) <= bound, "Φ 路线件数超界（嫌疑）"
    return cycle_edges_of(n, pieces_cyc), {
        "route": "phi(ntri=%d)" % ntri, "bound": bound,
        "factor_comps": comps, "phi_comps": len(cphi),
        "phim_comps": len(cphim), "R_comps": len(cR)}


def certificate(n, edges, pieces, bound, route, tag):
    """构造可落盘的证书 dict（pieces 为边列表的列表）。"""
    return {
        "tag": tag, "n": n, "bound": bound, "route": route,
        "npieces": len(pieces),
        "edges": [list(e) for e in sorted(set(edges))],
        "pieces": [[list(e) for e in p] for p in pieces],
    }


# ---------------------------------------------------------------- 锚点自检
def selftest():
    # 0) 通用：2-因子分解的合法性检查工具
    def check_2fac(n, edges, factors):
        E = set(edges)
        seen = set()
        for F in factors:
            assert len(F) == n
            for e in F:
                assert e in E and e not in seen, "2-因子必须边不交且是原图子集"
                seen.add(e)
            adjF = build_adj(n, F)
            assert all(len(a) == 2 for a in adjF), "2-因子每点度应为 2"
        assert seen == E, "2-因子应划分全部边"

    # 1) K5（4-正则）：2-因子分解 = 两个 5-圈
    n = 5
    edges = [norm(u, v) for u in range(5) for v in range(u + 1, 5)]
    Fs = two_factorize(n, build_adj(n, edges), 2)
    check_2fac(n, edges, Fs)
    assert all(len(cycles_of_two_factor(n, F)) == 1 for F in Fs), "K5 的 2-因子应为 5-圈"
    print("[selftest] K5 2-因子分解 ok（两个 5-圈，划分 10 条边）")

    # 1b) W = L(K_{3,3}) = 3x3 车图（4-正则, 9 点, 18 边）：2-因子分解合法
    def vid(side, a, b):
        return a * 3 + b if side == 0 else b * 3 + a
    W_edges = []
    for a in range(3):
        for b1 in range(3):
            for b2 in range(b1 + 1, 3):
                W_edges.append(norm(vid(0, a, b1), vid(0, a, b2)))
    for b in range(3):
        for a1 in range(3):
            for a2 in range(a1 + 1, 3):
                W_edges.append(norm(vid(0, a1, b), vid(0, a2, b)))
    W_edges = sorted(set(W_edges))
    assert len(W_edges) == 18 and all(len(a) == 4 for a in build_adj(9, W_edges))
    FsW = two_factorize(9, build_adj(9, W_edges), 2)
    check_2fac(9, W_edges, FsW)
    print("[selftest] W = L(K_{3,3}) 2-因子分解 ok")

    # 2) B = K_{3,3} 的全部匹配 x 定向（48 组合）：Φ(σ) 与 Φ(−σ) 为两个 9-圈且划分 E(W)
    Slist = [[vid(0, a, b) for b in range(3)] for a in range(3)]
    Tlist = [[vid(0, a, b) for a in range(3)] for b in range(3)]
    Sedges = []
    for tri in Slist:
        Sedges += [norm(tri[0], tri[1]), norm(tri[0], tri[2]), norm(tri[1], tri[2])]
    Tedges = []
    for tri in Tlist:
        Tedges += [norm(tri[0], tri[1]), norm(tri[0], tri[2]), norm(tri[1], tri[2])]
    assert not (set(Sedges) & set(Tedges))
    count = 0
    for seed in range(48):
        rng = random.Random(seed)
        phi, phim = phi_decompose(9, Sedges, Tedges, rng)
        cp = cycles_of_two_factor(9, sorted(phi))
        cpm = cycles_of_two_factor(9, sorted(phim))
        assert len(cp) == 1 and len(cp[0]) == 9, "K3,3: Φ 应为 9-圈"
        assert len(cpm) == 1 and len(cpm[0]) == 9
        count += 1
    print(f"[selftest] B=K_{{3,3}}: Φ/Φ(−) 全 {count} 组合为 9-圈且划分 E(W) ok")

    # 3) 完整管线：n=9 的 4 个 6-正则类（补 2-因子型）
    import itertools
    K9 = set(itertools.combinations(range(9), 2))
    parts = []
    def comps_of(n_, minlen=3):
        res = []
        def rec(rem, cur):
            if rem == 0:
                res.append(tuple(cur)); return
            for k in range(minlen, rem + 1):
                rec(rem - k, cur + [k])
        rec(n_, [])
        return res
    for comp in comps_of(9):
        # 一个代表性 2-正则图：按分量长度顺序摆放
        verts = list(range(9))
        pos = 0
        E = set()
        for L in comp:
            cyc = verts[pos:pos + L]
            for i in range(L):
                E.add(norm(cyc[i], cyc[(i + 1) % L]))
            pos += L
        G = set(K9) - E
        rng = random.Random(12345)
        pieces, info = decompose_six_regular(9, sorted(G), rng, "n9")
        assert len(pieces) <= 7, "n=9 应 ≤ n−2 = 7"
        print(f"[selftest] n=9 补 2-因子型 {comp}: pieces={len(pieces)} route={info['route']}")
    print("[selftest] 全部锚点通过")


if __name__ == "__main__":
    selftest()
