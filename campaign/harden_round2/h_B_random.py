#!/usr/bin/env python3
"""h_B_random.py — B 任务：随机大样本（n=15,18,21,24 各 ≥2000 个 6-正则图）。

采样：networkx.random_regular_graph(6, n, seed=SEED_BASE + n*100000 + i)
      —— Steger–Wormald 交换算法（networkx 3.6.1 文档：d=O(n^{1/3}) 时渐近均匀）。
每图：decompose_six_regular 构造件数 ≤ n−2（n≡0 mod 3）的证书，落盘供 h_verify.py 独立复核。
分片 + checkpoint：每个 (n, shard) 写一个 jsonl + .done；重跑自动跳过已完成分片。

用法:
  python3 h_B_random.py --count 2000 --shard 200 --procs 8 [--nlist 15,18,21,24]
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

SEED_BASE = 20260914


def sample_graph(n, i):
    """固定种子采样（种子公式写死在报告/记录里）。"""
    seed = SEED_BASE + n * 100000 + i
    G = nx.random_regular_graph(6, n, seed=seed)
    return G, seed


def run_shard(args):
    n, shard, start, count, outdir = args
    path = os.path.join(outdir, f"B_n{n}_s{shard}.jsonl")
    done = path + ".done"
    if os.path.exists(done):
        with open(done) as f:
            return json.load(f)
    t0 = time.time()
    n_ok = 0
    n_fail = 0
    hist = {}
    route_hist = {}
    maxp = 0
    minp = None
    with open(path, "w") as f:
        for i in range(start, start + count):
            try:
                G, seed = sample_graph(n, i)
            except Exception as e:
                n_fail += 1
                f.write(json.dumps({"tag": f"B_n{n}#{i}", "n": n, "seed": None,
                                    "sample_error": str(e)}) + "\n")
                continue
            edges = sorted(HC.norm(u, v) for u, v in G.edges())
            if len(edges) != 3 * n or not all(len(a) == 6 for a in HC.build_adj(n, edges)):
                n_fail += 1
                f.write(json.dumps({"tag": f"B_n{n}#{i}", "n": n, "seed": seed,
                                    "sample_error": "非 6-正则简单图（采样器异常）"}) + "\n")
                continue
            rng = random.Random(SEED_BASE ^ (n * 7919 + i))
            pieces, info = HC.decompose_six_regular(n, edges, rng, f"B_n{n}#{i}")
            rec = HC.certificate(n, edges, pieces, n - 2, info["route"], f"B_n{n}#{i}")
            rec["seed"] = seed
            rec["reg"] = 6
            assert rec["npieces"] <= n - 2, "件数超界（嫌疑反例）"
            f.write(json.dumps(rec) + "\n")
            n_ok += 1
            hist[str(rec["npieces"])] = hist.get(str(rec["npieces"]), 0) + 1
            rt = info["route"].split("(")[0]
            route_hist[rt] = route_hist.get(rt, 0) + 1
            maxp = max(maxp, rec["npieces"])
            minp = rec["npieces"] if minp is None else min(minp, rec["npieces"])
    res = {"n": n, "shard": shard, "start": start, "count": count, "ok": n_ok, "fail": n_fail,
           "pieces_hist": hist, "route_hist": route_hist, "min": minp, "max": maxp,
           "elapsed_s": round(time.time() - t0, 2), "file": path}
    with open(done, "w") as f:
        json.dump(res, f)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=2000)
    ap.add_argument("--shard", type=int, default=200)
    ap.add_argument("--procs", type=int, default=8)
    ap.add_argument("--nlist", default="15,18,21,24")
    ap.add_argument("--outdir", default="data")
    args = ap.parse_args()
    ns = [int(x) for x in args.nlist.split(",")]
    tasks = []
    for n in ns:
        nsh = (args.count + args.shard - 1) // args.shard
        for s in range(nsh):
            start = s * args.shard
            cnt = min(args.shard, args.count - start)
            tasks.append((n, s, start, cnt, args.outdir))
    print(f"[B] 分片任务 {len(tasks)} 个（ns={ns}, 每 n {args.count} 图）", flush=True)
    t0 = time.time()
    results = []
    with mp.Pool(args.procs) as pool:
        for res in pool.imap_unordered(run_shard, tasks):
            results.append(res)
            print(f"  [B] 完成 n={res['n']} shard={res['shard']} ok={res['ok']} "
                  f"fail={res['fail']} max={res['max']} {res['elapsed_s']}s", flush=True)
    agg = {}
    for n in ns:
        rs = [r for r in results if r["n"] == n]
        hist = {}
        routes = {}
        ok = fail = 0
        for r in rs:
            ok += r["ok"]
            fail += r["fail"]
            for k, v in r["pieces_hist"].items():
                hist[k] = hist.get(k, 0) + v
            for k, v in r["route_hist"].items():
                routes[k] = routes.get(k, 0) + v
        agg[n] = {"graphs": ok, "fail": fail, "bound": n - 2,
                  "pieces_hist": dict(sorted(hist.items(), key=lambda kv: int(kv[0]))),
                  "max_pieces": max((r["max"] for r in rs if r["max"]), default=None),
                  "min_pieces": min((r["min"] for r in rs if r["min"] is not None), default=None),
                  "route_hist": routes}
        print(f"[B] n={n}: {ok} 图全过（≤ {n-2} 件），fail={fail}，"
              f"件数 min/max={agg[n]['min_pieces']}/{agg[n]['max_pieces']}", flush=True)
    with open(os.path.join(args.outdir, "B_summary.json"), "w") as f:
        json.dump({"count_per_n": args.count, "shard": args.shard, "seed_base": SEED_BASE,
                   "ns": agg, "total_elapsed_s": round(time.time() - t0, 1)}, f, indent=1)
    print(f"[B] 总用时 {time.time()-t0:.1f}s，摘要 -> {args.outdir}/B_summary.json", flush=True)


if __name__ == "__main__":
    main()
