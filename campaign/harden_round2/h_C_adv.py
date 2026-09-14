#!/usr/bin/env python3
"""h_C_adv.py — C 任务：对抗族加宽（L(B) 星型族）。

构造（与上游 sweep_star_B.py 同思路、本文件独立实现）：
  B = 随机 3-正则二部简单图（s + s 点，配置模型拒绝采样；种子落盘）
  W = L(B)（3s 点 4-正则）= star(L) ⊔ star(R)（两个三角形因子；本文件由 B 显式构造）
  对每个 B 取 3 个 (完美匹配, 定向) 组合，验证 Φ(σ)/Φ(−σ) 划分 E(W)、两者无三角形（圈长 ≥4）；
  F₂ = 剩余 (n−5)-正则图 R = K_n − W 的任一 2-因子（偶度 → 2-因子分解取一；
       奇度 → blossom 完美匹配后取偶度子图的 2-因子分解之一）
  G = W ⊔ F₂（断言 6-正则）→ 件数 = comps(Φσ) + comps(Φ−σ) + comps(F₂) ≤ n−2。

用法: python3 h_C_adv.py --s 7 --count 500 --procs 8
分片 + checkpoint：每个 (s, shard) 一个 jsonl + .done。
"""
import os
import sys
import json
import time
import random
import argparse
import multiprocessing as mp

import networkx as nx

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import h_common as HC

SEED_C = 777001


def random_cubic_bipartite(s, rng):
    """配置模型 + 拒绝采样：3-正则二部简单图（左侧 0..s-1，右侧 s..2s-1）。"""
    while True:
        left = [i for i in range(s) for _ in range(3)]          # 左部 stub
        right = [j for j in range(s) for _ in range(3)]         # 右部 stub（内部编号）
        rng.shuffle(right)
        seen = set()
        ok = True
        for i, jr in zip(left, right):
            if (i, jr) in seen:                                  # 重边即拒绝
                ok = False
                break
            seen.add((i, jr))
        if ok:
            return sorted((i, s + jr) for (i, jr) in seen)


def build_W(s, Bedges):
    """由 B 显式构造 W = L(B)：顶点 = B 的边；三角形 = B 的顶点星。"""
    nb = {v: [] for v in range(2 * s)}
    for (i, j) in Bedges:
        nb[i].append(j)
        nb[j].append(i)
    for v in nb:
        nb[v].sort()
    pos = {a: {b: k for k, b in enumerate(nb[a])} for a in range(s)}

    def eid(a, b):          # B 边 (a,b), a<s 的左点编号
        return 3 * a + pos[a][b]

    S_tris = [sorted(eid(a, b) for b in nb[a]) for a in range(s)]
    T_tris = [sorted(eid(a, b) for a in nb[b]) for b in range(s, 2 * s)]
    n = 3 * s
    assert sorted(x for t in S_tris for x in t) == list(range(n))
    assert sorted(x for t in T_tris for x in t) == list(range(n))
    S, T = [], []
    for tris, acc in ((S_tris, S), (T_tris, T)):
        for t in tris:
            for p in range(3):
                for q in range(p + 1, 3):
                    acc.append(HC.norm(t[p], t[q]))
    S = sorted(set(S))
    T = sorted(set(T))
    assert not (set(S) & set(T)) and len(S) == len(T) == n
    assert all(len(a) == 4 for a in HC.build_adj(n, S + T))
    return n, S, T


def two_factor_of_R(n, Redges):
    """R = (n−5)-正则；返回 R 的一个支撑 2-因子（边列表）。"""
    d = n - 5
    adjR = HC.build_adj(n, Redges)
    assert all(len(a) == d for a in adjR), "R 应为 (n−5)-正则"
    if d % 2 == 0:
        F = HC.two_factorize(n, adjR, d // 2)[0]
        return F
    # d 奇数：blossom 求完美匹配 M -> R' = R − M 为偶度 -> 2-因子分解
    GR = nx.Graph()
    GR.add_nodes_from(range(n))
    GR.add_edges_from(Redges)
    M = nx.algorithms.matching.max_weight_matching(GR, maxcardinality=True)
    assert 2 * len(M) == n, f"完美匹配不存在（{len(M)} 条）"
    Mset = set(HC.norm(u, v) for (u, v) in M)
    R2 = [e for e in Redges if e not in Mset]
    adjR2 = HC.build_adj(n, R2)
    assert all(len(a) == d - 1 for a in adjR2)
    F = HC.two_factorize(n, adjR2, (d - 1) // 2)[0]
    return F


def run_B(s, bidx, out, combos=3):
    """处理一个 B，返回记录条数与统计。"""
    rng = random.Random(SEED_C + 1000003 * s + bidx)
    Bedges = random_cubic_bipartite(s, rng)
    assert len(Bedges) == 3 * s
    n, S, T = build_W(s, Bedges)
    W = sorted(set(S) | set(T))
    # R = K_n − W 与其 2-因子 F₂
    K = set()
    for u in range(n):
        for v in range(u + 1, n):
            K.add((u, v))
    R = sorted(K - set(W))
    F2 = two_factor_of_R(n, R)
    cF2 = HC.cycles_of_two_factor(n, F2)
    G = sorted(set(W) | set(F2))
    assert all(len(a) == 6 for a in HC.build_adj(n, G)), "G 应 6-正则"
    recs = []
    for ci in range(combos):
        shuf = (ci > 0)
        rng2 = random.Random(SEED_C + 7 * 1000003 * s + 13 * bidx + ci)
        phi, phim = HC.phi_decompose(n, S, T, rng2, shuffle_matching=shuf)
        cphi = HC.cycles_of_two_factor(n, sorted(phi))       # 顶点序列
        cphim = HC.cycles_of_two_factor(n, sorted(phim))
        assert all(len(c) >= 4 for c in cphi) and all(len(c) >= 4 for c in cphim), \
            "Φ 因子含三角形（嫌疑反例）"
        ephi = HC.cycle_edges_of(n, cphi)                    # 边列表
        ephim = HC.cycle_edges_of(n, cphim)
        pieces = ephi + ephim + HC.cycle_edges_of(n, cF2)
        assert len(pieces) <= n - 2, "件数超界（嫌疑反例）"
        rec = {
            "tag": f"C_s{s}#{bidx}c{ci}", "n": n, "bound": n - 2, "reg": 6,
            "route": f"adv_s{s}", "npieces": len(pieces),
            "edges": [list(e) for e in G],
            "pieces": [[list(e) for e in p] for p in pieces],
            "W_edges": [list(e) for e in W],
            "phi_pieces": [[list(e) for e in p] for p in ephi],
            "phim_pieces": [[list(e) for e in p] for p in ephim],
            "f2_pieces": [[list(e) for e in p] for p in HC.cycle_edges_of(n, cF2)],
            "comps": {"phi": len(cphi), "phim": len(cphim), "f2": len(cF2)},
            "comp_eq": len(cphi) == len(cphim),
            "shuffled_matching": shuf,
        }
        recs.append(rec)
    return recs


def run_shard(args):
    s, shard, start, count, outdir, combos = args
    path = os.path.join(outdir, f"C_s{s}_s{shard}.jsonl")
    done = path + ".done"
    if os.path.exists(done):
        with open(done) as f:
            return json.load(f)
    t0 = time.time()
    ok = 0
    fail = 0
    hist = {}
    comp_eq_true = 0
    phi_hist = {}
    with open(path, "w") as f:
        for b in range(start, start + count):
            try:
                recs = run_B(s, b, path, combos=combos)
            except AssertionError as e:
                fail += 1
                f.write(json.dumps({"tag": f"C_s{s}#{b}", "sample_error": str(e)}) + "\n")
                print(f"*** 反例嫌疑 s={s} B#{b}: {e}", flush=True)
                continue
            for rec in recs:
                f.write(json.dumps(rec) + "\n")
                ok += 1
                hist[str(rec["npieces"])] = hist.get(str(rec["npieces"]), 0) + 1
                phi_hist[str(rec["comps"]["phi"])] = phi_hist.get(str(rec["comps"]["phi"]), 0) + 1
                if rec["comp_eq"]:
                    comp_eq_true += 1
    res = {"s": s, "shard": shard, "start": start, "count": count, "records_ok": ok,
           "B_fail": fail, "pieces_hist": hist, "phi_comp_hist": phi_hist,
           "comp_eq_true": comp_eq_true, "elapsed_s": round(time.time() - t0, 2), "file": path}
    with open(done, "w") as f:
        json.dump(res, f)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--s", type=int, required=True)
    ap.add_argument("--count", type=int, required=True)
    ap.add_argument("--shard", type=int, default=50)
    ap.add_argument("--procs", type=int, default=8)
    ap.add_argument("--combos", type=int, default=3)
    ap.add_argument("--outdir", default="data")
    args = ap.parse_args()
    tasks = []
    nsh = (args.count + args.shard - 1) // args.shard
    for sh in range(nsh):
        start = sh * args.shard
        cnt = min(args.shard, args.count - start)
        tasks.append((args.s, sh, start, cnt, args.outdir, args.combos))
    print(f"[C s={args.s}] {len(tasks)} 分片，{args.count} 个 B × {args.combos} (匹配,定向) 组合", flush=True)
    t0 = time.time()
    results = []
    with mp.Pool(args.procs) as pool:
        for res in pool.imap_unordered(run_shard, tasks):
            results.append(res)
            print(f"  [C] s={res['s']} shard={res['shard']} records={res['records_ok']} "
                  f"fail={res['B_fail']} {res['elapsed_s']}s", flush=True)
    tot = sum(r["records_ok"] for r in results)
    fails = sum(r["B_fail"] for r in results)
    hist = {}
    ph = {}
    ceq = 0
    for r in results:
        for k, v in r["pieces_hist"].items():
            hist[k] = hist.get(k, 0) + v
        for k, v in r["phi_comp_hist"].items():
            ph[k] = ph.get(k, 0) + v
        ceq += r["comp_eq_true"]
    out = {"s": args.s, "B_count": args.count, "combos": args.combos,
           "records_ok": tot, "B_fail": fails, "pieces_hist": hist,
           "phi_comp_hist": ph, "comp_eq_all": ceq == tot,
           "comp_eq_true": ceq, "elapsed_s": round(time.time() - t0, 1)}
    with open(os.path.join(args.outdir, f"C_s{args.s}_summary.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"[C s={args.s}] 记录 {tot} 全过（≤ {3*args.s-2} 件）；B 失败 {fails}；"
          f"#comp(Φ)=#comp(Φ−) 在 {ceq}/{tot} 条上成立；件数直方图 {hist}", flush=True)


if __name__ == "__main__":
    main()
