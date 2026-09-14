#!/usr/bin/env python3
"""h_A_enum.py — A 任务：同构意义下的全类枚举（geng 代表元，补图法转 6-正则）。

用法:
  python3 h_A_enum.py --n 10 --g6 data/geng_10_d3.g6 --out data/A_n10.jsonl [--exact] [--limit K]

流程（每个同构类，geng 每行一个代表元）：
  graph6 -> G（k-正则）-> 补图 -> 6-正则简单图 -> decompose_six_regular 构造 ≤ n−2（或 n−1）件证书
  --exact（仅小 n）：BB 精确 ce + MILP 独立精确 + LP 下界；记录 slack = bound − ce
断点续跑：out 已存在时按 tag 跳过已处理类。反例嫌疑（断言失败）单独落 violations 文件并大声打印。
"""
import sys
import json
import time
import random
import argparse
import os

import networkx as nx

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import h_common as HC
import h_A_exact as X


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--g6", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--exact", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--milp-tl", type=float, default=60.0)
    args = ap.parse_args()

    n = args.n
    bound = (n - 2) if n % 3 == 0 else (n - 1)
    done = set()
    if os.path.exists(args.out):
        with open(args.out) as f:
            for line in f:
                try:
                    done.add(json.loads(line)["tag"])
                except Exception:
                    pass
        print(f"[A n={n}] 续跑：已有 {len(done)} 条记录", flush=True)
    fo = open(args.out, "a")
    vio = open(args.out + ".violations", "a")
    summary = {"n": n, "bound": bound, "classes": 0, "processed": 0,
               "pieces_hist": {}, "route_hist": {}, "violations": 0,
               "min_pieces": None, "max_pieces": None, "elapsed_s": 0.0,
               "npieces_le_nminus2": 0, "nminus2": n - 2}
    exact_rows = []
    t0 = time.time()
    idx = -1
    with open(args.g6) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            idx += 1
            summary["classes"] = idx + 1
            tag = f"n{n}#{idx}"
            if tag in done:
                continue
            Gk = nx.from_graph6_bytes(line.encode())
            if Gk.number_of_nodes() != n:
                print(f"*** 顶点数异常 {tag}", flush=True)
                continue
            Gc = nx.complement(Gk)
            edges = sorted(HC.norm(u, v) for u, v in Gc.edges())
            adj = HC.build_adj(n, edges)
            assert all(len(a) == 6 for a in adj), f"{tag}: 补图不是 6-正则"
            rng = random.Random(1000003 * n + idx)
            try:
                pieces, info = HC.decompose_six_regular(n, edges, rng, tag)
            except AssertionError as e:
                summary["violations"] += 1
                rec = {"tag": tag, "n": n, "edges": [list(e) for e in edges], "err": str(e)}
                vio.write(json.dumps(rec) + "\n")
                vio.flush()
                print(f"*** 反例嫌疑 {tag}: {e}（已落盘 {args.out}.violations）", flush=True)
                continue
            cert = HC.certificate(n, edges, pieces, bound, info["route"], tag)
            rec = {"tag": tag, "n": n, "bound": bound, "route": info["route"],
                   "npieces": len(pieces),
                   "edges": [list(e) for e in edges],
                   "pieces": [[list(e) for e in p] for p in pieces],
                   "factor_comps": info.get("factor_comps"),
                   "reg": 6}
            if args.exact:
                ce_bb, wit = X.exact_ce_bb(n, edges, ub=len(pieces))
                cw = X.check_pieces(n, edges, wit) if wit else -1
                assert cw == ce_bb, f"{tag}: BB 见证校验失败"
                ce_milp, wit2, info2 = X.milp_exact_ce(n, edges, ub=ce_bb, time_limit=args.milp_tl)
                if wit2:
                    cw2 = X.check_pieces(n, edges, wit2)
                    assert cw2 == ce_milp, f"{tag}: MILP 见证校验失败"
                lpb, _ = X.lp_bound(n, edges)
                rec["exact"] = {"ce_bb": ce_bb, "ce_milp": ce_milp, "lp_lb": lpb,
                                "slack": bound - ce_bb, "milp_note": info2}
                exact_rows.append((tag, ce_bb, ce_milp, lpb))
                if ce_milp is not None and ce_milp != ce_bb:
                    print(f"*** BB/MILP 不一致 {tag}: {ce_bb} vs {ce_milp}（嫌疑）", flush=True)
            fo.write(json.dumps(rec) + "\n")
            fo.flush()
            summary["processed"] += 1
            if len(pieces) <= n - 2:
                summary["npieces_le_nminus2"] += 1
            h = summary["pieces_hist"]
            h[str(len(pieces))] = h.get(str(len(pieces)), 0) + 1
            rt = info["route"].split("(")[0]
            summary["route_hist"][rt] = summary["route_hist"].get(rt, 0) + 1
            pmin = summary["min_pieces"]
            summary["min_pieces"] = len(pieces) if pmin is None else min(pmin, len(pieces))
            pmax = summary["max_pieces"]
            summary["max_pieces"] = len(pieces) if pmax is None else max(pmax, len(pieces))
            if summary["processed"] % 500 == 0:
                print(f"  [A n={n}] {summary['processed']} 类已处理 {time.time()-t0:.0f}s", flush=True)
            if args.limit and summary["processed"] >= args.limit:
                break
    summary["elapsed_s"] = time.time() - t0
    if exact_rows:
        summary["exact_ce_hist"] = {}
        summary["exact_milp_fail"] = 0
        for tag, cb, cm, lpb in exact_rows:
            summary["exact_ce_hist"][str(cb)] = summary["exact_ce_hist"].get(str(cb), 0) + 1
            if cm is None:
                summary["exact_milp_fail"] += 1
        summary["exact_rows"] = [{"tag": t, "ce_bb": b, "ce_milp": m, "lp_lb": l} for t, b, m, l in exact_rows]
    fo.close()
    vio.close()
    with open(args.out + ".summary.json", "w") as f:
        json.dump(summary, f, indent=1)
    print(f"[A n={n}] 完成：类 {summary['classes']}，处理 {summary['processed']}，"
          f"件数 min/max = {summary['min_pieces']}/{summary['max_pieces']}，"
          f"直方图 {summary['pieces_hist']}，路线 {summary['route_hist']}，"
          f"违反 {summary['violations']}，用时 {summary['elapsed_s']:.1f}s", flush=True)


if __name__ == "__main__":
    main()
