#!/usr/bin/env python3
"""sweep_star_B.py — 引理1(★) 的数值验证。
危险类参数化：若 (★) 有反例，则 G 必为 L(B)（B = 3-正则二部简单图）。
本扫描：(a) 穷举所有 s+s 顶点（s=3..S_max）的标记 3-正则二部 B，对每个 L(B)
  双路验证：构造性 pipeline_star（内含逐项校验）+ 独立暴力搜索 brute_long_two_factor；
(b) 随机大 B（s=8..40）构造性验证。
用法: python3 sweep_star_B.py exhaustive [S_max] | random [count_per_s]"""
import sys, time, random
sys.path.insert(0, "/Users/munich/Desktop/数学/front184/campaign/r2_01_scripts")
from r2_core import *

def phi_forced_check(B_adj, tag):
    """强制走 Φ 路线：L(B) 的两个三角形因子 = B 左侧/右侧的星形。
    提取该三角形因子对，调用 r2_core.phi_route_from_pair（pipeline_star 的 else 分支）。"""
    from r2_core import phi_route_from_pair
    verts, idx, LE, nL = line_graph_of_B(B_adj)
    # 二部侧划分：BFS 二着色
    color = {}
    for x0 in B_adj:
        if x0 in color:
            continue
        color[x0] = 0
        stack = [x0]
        while stack:
            x = stack.pop()
            for y in B_adj[x]:
                if y not in color:
                    color[y] = 1 - color[x]
                    stack.append(y)
    Lverts = [x for x in color if color[x] == 0]
    Rverts = [x for x in color if color[x] == 1]
    assert len(Lverts) == len(Rverts)
    # 星形三角形（L(B) 顶点 = verts 的 id）
    def star_tris(vs):
        out = []
        for x in vs:
            ids = []
            for i, e in enumerate(verts):
                if x in e:
                    ids.append(i)
            assert len(ids) == 3
            te = set()
            for p, q in ((0,1),(1,2),(0,2)):
                a, b = sorted((ids[p], ids[q]))
                te.add((a, b))
            out.append(frozenset(te))
        return out
    trisF, trisFp = star_tris(Lverts), star_tris(Rverts)
    Phi, info = phi_route_from_pair(nL, frozenset(LE), trisF, trisFp, tag)
    assert max(cycles_of_factor(Phi)) >= 4
    return sorted(info["components"])

def check_LB(verts, LE, nL, tag, do_brute=True):
    """对 L(B) 双路验证 (★)。"""
    F, how = pipeline_star(nL, frozenset(LE), tag)
    assert max(cycles_of_factor(F)) >= 4, f"[{tag}] 构造路失败"
    if do_brute:
        B = brute_long_two_factor(nL, LE, max_nodes=1_500_000)
        if B == "timeout":
            return how, "brute-timeout"
        assert B is not None, f"[{tag}] 暴力路找不到 >=4 圈 2-因子 —— 可能是反例!"
    return how, "brute-ok"

def run_exhaustive(smax):
    total = 0
    route_stat = {}
    for s in range(3, smax + 1):
        t0 = time.time()
        Bs = all_cubic_bipartite(s)
        n_ok = 0
        for bi, B_adj in enumerate(Bs):
            verts, idx, LE, nL = line_graph_of_B(B_adj)
            adjL = make_graph(nL, LE)
            assert all(len(adjL[v]) == 4 for v in range(nL)), "L(B) 应 4-正则"
            how, bs = check_LB(verts, LE, nL, f"L(B_s{s}#{bi})", do_brute=(nL <= 30))
            route_stat[how] = route_stat.get(how, 0) + 1
            comps = phi_forced_check(B_adj, f"phi_s{s}#{bi}")   # 强制 Φ 路线
            n_ok += 1
        total += n_ok
        print(f"[exh] s={s} ({nL} 点 L(B)): {n_ok} 个 B 全过  耗时 {time.time()-t0:.1f}s  累计 {total}", flush=True)
    print(f"[exh] 总计 {total} 个 L(B) 图，全部支持 (★)；路线统计 {route_stat}")

def run_random(count):
    rng = random.Random(20260912)
    total = 0
    for s in range(8, 41):
        t0 = time.time()
        for i in range(count):
            B_adj = random_cubic_bipartite(s, rng)
            # 大图：直接强制 Φ 路线（构造 + 逐项独立校验），避免朴素 2-因子搜索爆炸
            comps = phi_forced_check(B_adj, f"rand_s{s}#{i}")
            assert all(L >= 4 for L in comps)
            total += 1
        print(f"[rand] s={s} (n={2*s}): {count} 个全过(Φ强制路线)  耗时 {time.time()-t0:.1f}s  累计 {total}", flush=True)

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "exhaustive"
    if mode == "exhaustive":
        smax = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        run_exhaustive(smax)
    else:
        run_random(int(sys.argv[2]) if len(sys.argv) > 2 else 100)
