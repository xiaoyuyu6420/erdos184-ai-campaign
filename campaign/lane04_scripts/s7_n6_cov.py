#!/usr/bin/env python3
"""s7: n=6 修正紧实例 258 个的 W=∅ 覆盖全查。"""
import json, sys
from itertools import combinations
from s1_exhaustive import build
from s4_coverage_gaps import min_pi_and_coverage

sys.setrecursionlimit(100000)
edges = list(combinations(range(6), 2))
tight = json.load(open("s5_n6_tight.json"))
ok = ncov = skip = 0
for mask in tight:
    adj, m = build(mask, edges, 6)
    ce, status, cov = min_pi_and_coverage(adj, 6, node_cap=200000, time_cap=5.0)
    if status == "OK":
        ok += 1
        if not cov:
            ncov += 1
            print(f"!! n=6 mask={mask}: ce={ce} 无全覆盖最优分解")
    else:
        skip += 1
print(json.dumps(dict(n=6, checked=len(tight), OK=ok, no_cover=ncov, SKIP=skip)))
