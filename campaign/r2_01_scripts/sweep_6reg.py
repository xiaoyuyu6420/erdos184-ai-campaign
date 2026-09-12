#!/usr/bin/env python3
"""sweep_6reg.py — 定理2（6-正则 n≡0 mod 3 ⟹ ce ≤ n-1）与定理3（三 2-因子分解）
的构造性证明流水线数值验证 + 精确 ce 侦察。
覆盖：
  (1) n=8: 唯一类 K8-PM；n=9: 全部标记 6-正则图（= 全部标记 2-正则的补图）；
  (2) n=10: 全部标记 3-正则图的补图（回溯枚举）；
  (3) n=12,15,18: 对抗族（三角形因子 ∪ L(B)，B 穷举 3-正则二部）+ 随机样本；
  (4) 精确 ce（独立求解器）用于小类交叉核对。
用法: python3 sweep_6reg.py [section]"""
import sys, time, random, itertools
sys.path.insert(0, "/Users/munich/Desktop/数学/front184/campaign/r2_01_scripts")
from r2_core import *
from r2_ce import exact_ce

def enumerate_k_regular(n, d, cap=50_000_000):
    """回溯枚举全部标记 d-正则简单图（n 顶点）。生成器。带前向剪枝。"""
    all_edges = [(i, j) for i in range(n) for j in range(i+1, n)]
    m = len(all_edges)
    degs = [0]*n
    chosen = []
    cnt = [0]
    def can_finish(idx):
        # 前向检查：每点还缺的度 <= 其剩余可选边数
        for x in range(n):
            if degs[x] > d:
                return False
            rem = sum(1 for k in range(idx, m) if x in all_edges[k])
            if d - degs[x] > rem:
                return False
        return True
    def rec2(idx):
        cnt[0] += 1
        if cnt[0] > cap:
            raise RuntimeError("cap")
        if idx == m:
            if all(x == d for x in degs):
                yield frozenset(chosen)
            return
        u, v = all_edges[idx]
        if degs[u] < d and degs[v] < d:
            degs[u] += 1; degs[v] += 1
            chosen.append((u, v))
            if can_finish(idx+1):
                yield from rec2(idx+1)
            chosen.pop()
            degs[u] -= 1; degs[v] -= 1
        degs_plus = degs  # 跳过分支
        if can_finish(idx+1):
            yield from rec2(idx+1)
    yield from rec2(0)

def sec_small():
    """n=8 唯一类；n=9 全部标记 6-正则（补 2-正则）；n=10 全部标记（补 3-正则）。"""
    rng = random.Random(7)
    # n=8
    K8 = set(itertools.combinations(range(8), 2))
    pm = [(i, i+4) for i in range(4)]
    G = frozenset(K8 - set((min(a,b), max(a,b)) for a,b in pm))
    pieces, info = pipeline_6reg(8, G, "K8-PM")
    print(f"[n=8] K8-PM: pieces={len(pieces)} <= 7 ok, route={info['route']}")
    ce = exact_ce(8, G, kmax=8)
    print(f"[n=8] K8-PM: exact ce = {ce}")
    # n=9：枚举全部标记 2-正则图（圈划分），取补
    n = 9
    parts = [((9,),), ]  # 用 composition 枚举
    def two_regular_graphs(n):
        # 全部标记 2-正则 = 全部圈划分的标记实现
        def compositions():
            # 划分为 >=3 的部分
            res = []
            def rec(rem, cur):
                if rem == 0:
                    res.append(tuple(cur))
                    return
                for k in range(3, rem+1):
                    rec(rem-k, cur+[k])
            rec(n, [])
            return res
        for comp in compositions():
            # 把 n 个标记点分给各圈（有序？无序）
            verts = list(range(n))
            for perm in itertools.permutations(verts):
                pos = 0
                cycles = []
                ok = True
                for L in comp:
                    cyc = perm[pos:pos+L]
                    cycles.append(cyc)
                    pos += L
                # 规范化：每圈取最小元定向、圈间排序，去重
                canon = []
                for cyc in cycles:
                    i = cyc.index(min(cyc))
                    r = tuple(cyc[i:]) + tuple(cyc[:i])
                    rr = (r[0],) + tuple(reversed(r[1:]))
                    canon.append(min(r, rr))
                if canon == sorted(canon) and len(set(canon)) == len(comp):
                    E = set()
                    for cyc in cycles:
                        for a, b in zip(cyc, cyc[1:]+cyc[:1]):
                            E.add((min(a,b), max(a,b)))
                    yield frozenset(E)
    K9 = set(itertools.combinations(range(9), 2))
    seen_classes = {}
    seen_H2 = set()
    cnt = 0
    t0 = time.time()
    for H2 in two_regular_graphs(9):
        if H2 in seen_H2:
            continue
        seen_H2.add(H2)
        G = frozenset(K9 - H2)
        adj = make_graph(9, G)
        assert all(len(adj[v]) == 6 for v in range(9))
        pieces, info = pipeline_6reg(9, G, f"n9#{cnt}")
        assert len(pieces) <= 8
        # 用圈长向量近似分类
        key = tuple(sorted(cycles_of_factor(H2)))
        seen_classes.setdefault(key, [G, 0, len(pieces)])
        seen_classes[key][1] += 1
        cnt += 1
        if cnt % 5000 == 0:
            print(f"  [n=9] 已测 {cnt} 个去重标记图  {time.time()-t0:.0f}s", flush=True)
    print(f"[n=9] 全部 {cnt} 个标记 6-正则图通过流水线 (pieces <= n-1 = 8)")
    for key, (G, c, np_) in sorted(seen_classes.items()):
        ce = exact_ce(9, G, kmax=9)
        print(f"  类 complement(2-factor={key}): {c} 个标记图, 流水线 pieces={np_}, exact ce={ce}")
    print(f"[n=9] 耗时 {time.time()-t0:.0f}s")

def sec_n10(cap_time=600):
    """n=10: 全部标记 3-正则图的补图。"""
    t0 = time.time()
    cnt = 0
    ce_samples = {}
    rng = random.Random(11)
    for Gc in enumerate_k_regular(10, 3, cap=50_000_000):
        if time.time() - t0 > cap_time:
            print(f"[n=10] 时间到，已测 {cnt} 个；中止（诚实声明非全量）")
            break
        G = frozenset((i, j) for i in range(10) for j in range(i+1, 10)) - Gc
        adj = make_graph(10, G)
        if any(len(adj[v]) != 6 for v in range(10)):
            continue
        pieces, info = pipeline_6reg(10, G, f"n10#{cnt}")
        assert len(pieces) <= 9
        key = tuple(sorted(cycles_of_factor(Gc)))
        if key not in ce_samples:
            ce_samples[key] = [G, exact_ce(10, G, kmax=10)]
        cnt += 1
        if cnt % 2000 == 0:
            print(f"  [n=10] 已测 {cnt}  {time.time()-t0:.0f}s", flush=True)
    print(f"[n=10] 共测 {cnt} 个标记 6-正则图全过")
    for key, (G, ce) in sorted(ce_samples.items()):
        print(f"  补图2-因子型 {key}: 代表 exact ce = {ce}")

def adversarial2(n, B_adj, tag):
    """G = star(L) ∪ star(R) ∪ F₂：字面包含关联图为 B 的三角形因子对。
    F₂ = K_n - (两个星形因子) 中的任一 2-因子（剩余图 7-正则）。"""
    verts, idx, LE, n = line_graph_of_B(B_adj)
    side = {}
    for i, e in enumerate(verts):
        for x in e:
            side.setdefault(x, set()).add(i)
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
    Ls = [x for x in color if color[x] == 0]
    Rs = [x for x in color if color[x] == 1]
    def star_edges(vs):
        E = set()
        for x in vs:
            ids = sorted(side[x])
            for p in range(3):
                for q in range(p+1, 3):
                    E.add((ids[p], ids[q]))
        return E
    F = star_edges(Ls)
    Fp = star_edges(Rs)
    assert not (F & Fp) and len(F) == n and len(Fp) == n
    K = {(i, j) for i in range(n) for j in range(i+1, n)}
    A = frozenset(K - F - Fp)
    adjA = make_graph(n, A)
    assert all(len(adjA[v]) == n - 5 for v in range(n)), "剩余图应 (n-5)-正则"
    F2 = find_two_factor(n, A)
    assert F2 is not None, f"[{tag}] 剩余 7-正则图找不到 2-因子"
    G = frozenset(F | Fp | set(F2))
    adj = make_graph(n, G)
    assert all(len(adj[v]) == 6 for v in range(n)), "对抗图应 6-正则"
    pieces, info = pipeline_6reg(n, G, tag)
    assert len(pieces) <= n - 1
    return info


def sec_adversarial(smax=5):
    t0 = time.time()
    tot = 0
    for s in range(3, smax+1):
        Bs = all_cubic_bipartite(s)
        n = 3*s
        for bi, B_adj in enumerate(Bs):
            info = adversarial2(n, B_adj, f"adv_s{s}#{bi}")
            tot += 1
        print(f"  [adv] s={s} (n={n}): {len(Bs)} 个全过  {time.time()-t0:.0f}s", flush=True)
    print(f"[adv] 对抗族总计 {tot} 个 6-正则图全过（三角形因子∪L(B)，强迫危险结构）")

def sec_random(ns=(12, 15, 18), per=200):
    rng = random.Random(20260912)
    for n in ns:
        t0 = time.time()
        okc = 0
        routes = {}
        for i in range(per):
            G = random_regular(n, 6, rng)
            if G is None:
                continue
            pieces, info = pipeline_6reg(n, G, f"rand6_n{n}#{i}")
            assert len(pieces) <= n-1
            r = info["route"].split("(")[0]
            routes[r] = routes.get(r, 0) + 1
            okc += 1
        print(f"[rand] n={n}: {okc}/{per} 全过  routes={routes}  {time.time()-t0:.0f}s", flush=True)

if __name__ == "__main__":
    sec = sys.argv[1] if len(sys.argv) > 1 else "all"
    if sec in ("all", "small"):
        sec_small()
    if sec in ("all", "n10"):
        sec_n10()
    if sec in ("all", "adv"):
        sec_adversarial(int(sys.argv[2]) if len(sys.argv) > 2 else 5)
    if sec in ("all", "rand"):
        sec_random()
