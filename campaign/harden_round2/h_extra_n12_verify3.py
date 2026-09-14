#!/usr/bin/env python3
"""h_extra_n12_verify3.py — 对 n=12 中构造件数 = n−2 的 5 个类：
  1) BB 找 3 件分解（件必为 Hamilton 圈）→ 写出证书 JSONL；
  2) 调 h_verify.py（独立 networkx 实现）复核证书；
  3) MILP（HiGHS）交叉：k=3 可行性（time_limit 120s）。
注意：36 条边 / 每件 ≤ 12 条 → 3 是平凡下界；故"合法 3 件分解"+"下界 3"即 ce = 3 的完整证明，
BB 只负责找见证，证明力来自独立校验器。"""
import json
import sys
import time
import os
import subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import h_A_exact as X

TAGS = ['n12#1335', 'n12#3974', 'n12#4472', 'n12#5130', 'n12#5482']


def main():
    rows = {}
    for line in open('data/A_n12.jsonl'):
        r = json.loads(line)
        if r['tag'] in TAGS:
            rows[r['tag']] = r
    certs = []
    out = {}
    for tag in TAGS:
        r = rows[tag]
        edges = [tuple(e) for e in r['edges']]
        t0 = time.time()
        ce, wit = X.exact_ce_bb(12, edges, ub=3, node_limit=5_000_000)
        res = {"construct_pieces": r['npieces'], "bb": ce, "s": round(time.time() - t0, 1)}
        print(f"[{tag}] BB={ce} {res['s']}s", flush=True)
        if ce is not None:
            assert X.check_pieces(12, edges, wit) == ce
            certs.append({"tag": tag + "-ce3", "n": 12, "bound": 3, "reg": 6,
                          "route": "bb-ce3", "npieces": len(wit),
                          "edges": [list(e) for e in edges],
                          "pieces": [[list(e) for e in p] for p in wit]})
        out[tag] = res
    with open('data/extra_n12_ce3_certs.jsonl', 'w') as f:
        for c in certs:
            f.write(json.dumps(c) + "\n")
    print(f"证书 {len(certs)} 条 -> data/extra_n12_ce3_certs.jsonl", flush=True)
    # 独立复核（h_verify.py，子进程）
    r = subprocess.run([sys.executable, 'h_verify.py', 'data/extra_n12_ce3_certs.jsonl'],
                       capture_output=True, text=True)
    print(r.stdout[-600:], flush=True)
    out['_verify_failures'] = '"total_failures": 0' in r.stdout
    # MILP 交叉：k=3 可行性
    for tag in TAGS:
        r0 = rows[tag]
        edges = [tuple(e) for e in r0['edges']]
        t0 = time.time()
        c, w, note = X.milp_exact_ce(12, edges, ub=3, time_limit=120)
        out[tag]['milp_k3'] = c
        out[tag]['milp_note'] = note
        out[tag]['milp_s'] = round(time.time() - t0, 1)
        print(f"[{tag}] MILP k≤3: {c} ({note}) {out[tag]['milp_s']}s", flush=True)
    with open('data/extra_n12_ce3.json', 'w') as f:
        json.dump(out, f, indent=1)
    print("完成 -> data/extra_n12_ce3.json", flush=True)


if __name__ == "__main__":
    main()
