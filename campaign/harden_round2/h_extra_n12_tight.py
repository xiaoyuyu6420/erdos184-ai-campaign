#!/usr/bin/env python3
"""h_extra_n12_tight.py — 尽力而为：对 A_n12 中构造件数达 n−2 = 10 的类，尝试精确 ce。

对每个目标类：
  1) BB（迭代加深 + memo，node_limit 5e6/每个 k）；
  2) MILP：先 min Σx 直接求（time_limit 300s），再 k=3..9 可行性（每个 60s）直到定值。
结果如实落盘（含"未定"状态）。"""
import json
import sys
import time
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import h_A_exact as X

TAGS = ['n12#1335', 'n12#3974', 'n12#4472', 'n12#5130', 'n12#5482']


def main():
    rows = {}
    for line in open('data/A_n12.jsonl'):
        r = json.loads(line)
        if r['tag'] in TAGS:
            rows[r['tag']] = r
    out = {}
    for tag in TAGS:
        r = rows[tag]
        edges = [tuple(e) for e in r['edges']]
        ub = r['npieces']
        t0 = time.time()
        ce, wit = X.exact_ce_bb(12, edges, ub=ub, node_limit=5_000_000)
        res = {"npieces_construct": ub, "ce_bb": ce,
               "bb_s": round(time.time() - t0, 1)}
        print(f"[{tag}] 构造件数={ub} BB={ce} ({res['bb_s']}s)", flush=True)
        if ce is None:
            # k=3..9 可行性（MILP）
            kres = []
            for k in range(3, ub):
                t1 = time.time()
                c, w, note = X.milp_exact_ce(12, edges, ub=k, time_limit=60)
                kres.append({"k": k, "ce": c, "note": note, "s": round(time.time() - t1, 1)})
                print(f"[{tag}]   MILP k≤{k}: {c} ({note}) {kres[-1]['s']}s", flush=True)
                if c is not None:
                    res["ce_milp"] = c
                    break
            res["milp_trials"] = kres
        out[tag] = res
    with open('data/extra_n12_tight.json', 'w') as f:
        json.dump(out, f, indent=1)
    print("完成 -> data/extra_n12_tight.json", flush=True)


if __name__ == "__main__":
    main()
