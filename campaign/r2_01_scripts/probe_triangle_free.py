#!/usr/bin/env python3
"""probe_triangle_free.py — 加强命题侦察（非证明，仅数值侦察）：
(+) 每个 4-正则简单图有【完全无三角形】的 2-因子（所有圈长 >= 4）？
比引理 1（存在含 >=4 圈的 2-因子）强。Φ 构造在 L(B) 情形给出的恰是无三角形 2-因子。
本脚本：随机 4-正则图 + 随机 3-正则二部 B 的 L(B) 上，回溯搜索无三角形 2-因子；
若找不到（搜索穷尽）即为 (+) 的反例候选。
用法: python3 probe_triangle_free.py [n_max] [per]"""
import sys, random, itertools
sys.path.insert(0, "/Users/munich/Desktop/数学/front184/campaign/r2_01_scripts")
from r2_core import (make_graph, line_graph_of_B, edge_components,
                     cycles_of_factor, random_cubic_bipartite, all_cubic_bipartite)

def triangle_free_two_factor(n, edges, node_budget=3_000_000):
    """回溯搜索所有圈长 >=4 的支撑 2-因子。返回边集 / None(不存在) / 'timeout'。"""
    adj = make_graph(n, edges)
    inc = {}
    for u, v in edges:
        inc.setdefault(u, []).append((u, v))
        inc.setdefault(v, []).append((u, v))
    chosen = {}
    used = set()
    budget = [node_budget]
    def feasible():
        for v in range(n):
            c = chosen.get(v, 0)
            if c > 2:
                return False
            rem = sum(1 for e in inc.get(v, []) if e not in used)
            if c + rem < 2:
                return False
        return True
    def rec():
        budget[0] -= 1
        if budget[0] < 0:
            raise TimeoutError
        v = None
        for x in range(n):
            if chosen.get(x, 0) != 2:
                v = x
                break
        if v is None:
            cyc = cycles_of_factor(frozenset(used))
            if min(cyc) >= 4:
                return True
            return False
        need = 2 - chosen.get(v, 0)
        opts = [e for e in inc.get(v, []) if e not in used]
        if len(opts) < need:
            return False
        for cb in itertools.combinations(opts, need):
            # 三角形剪枝：新边加入不应造成未完成三角形也行，这里仅最终检查
            for e in cb:
                used.add(e)
                chosen[e[0]] = chosen.get(e[0], 0) + 1
                chosen[e[1]] = chosen.get(e[1], 0) + 1
            if feasible() and rec():
                return True
            for e in cb:
                used.discard(e)
                chosen[e[0]] -= 1
                chosen[e[1]] -= 1
        return False
    try:
        if rec():
            return frozenset(used)
        return None
    except TimeoutError:
        return "timeout"

def main():
    n_max = int(sys.argv[1]) if len(sys.argv) > 1 else 16
    per = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    rng = random.Random(20260913)
    print(f"[probe(+) 无三角形 2-因子] 随机 4-正则 n=6..{n_max} x {per}")
    for n in range(6, n_max + 1, 2):
        stat = {}
        for i in range(per):
            # 随机 4-正则：配置模型
            while True:
                stubs = [v for v in range(n) for _ in range(4)]
                rng.shuffle(stubs)
                E = set(); ok = True
                for j in range(0, 4 * n, 2):
                    e = (min(stubs[j], stubs[j+1]), max(stubs[j], stubs[j+1]))
                    if e[0] == e[1] or e in E:
                        ok = False; break
                    E.add(e)
                if ok:
                    break
            r = triangle_free_two_factor(n, E)
            stat[r is None and "REJECT(反例!)" or (r == "timeout" and "timeout" or "ok")] = stat.get(
                r is None and "REJECT(反例!)" or (r == "timeout" and "timeout" or "ok"), 0) + 1
        print(f"  n={n}: {stat}")
    print(f"[probe] 危险类 L(B)（引理1 的 L(B) 上 (+) 是否也成立）: s=3..5 穷举")
    for s in range(3, 6):
        stat = {}
        for B_adj in all_cubic_bipartite(s):
            verts, idx, LE, nL = line_graph_of_B(B_adj)
            r = triangle_free_two_factor(nL, LE, node_budget=5_000_000)
            key = r is None and "REJECT" or (r == "timeout" and "timeout" or "ok")
            stat[key] = stat.get(key, 0) + 1
        print(f"  s={s} (n={3*s}): {stat}")

if __name__ == "__main__":
    main()
