#!/usr/bin/env python3
"""s8: n=7 m=17 残差图的 ce<=6 封闭判定（时间盒）。"""
import json, sys, time
from itertools import combinations
from s1_exhaustive import build, two_connected, tau_tjoin, all_cycles_em
from collections import defaultdict
sys.setrecursionlimit(100000)

def decision_le(adj, n, B):
    packed = []
    for u in range(n):
        nb = adj[u]
        while nb:
            b = (nb & -nb).bit_length()-1; nb &= nb-1
            if b > u: packed.append((u,b))
    m = len(packed)
    eid = {e:i for i,e in enumerate(packed)}
    cyc = set()
    for s in range(n):
        st = [(s, 1<<s, 0)]
        while st:
            v, vm, em = st.pop()
            nb = adj[v]
            while nb:
                b = (nb & -nb).bit_length()-1; nb &= nb-1
                if b < s: continue
                e = eid[(v,b) if v<b else (b,v)]
                if (em>>e)&1: continue
                if b == s:
                    if vm.bit_count() >= 3: cyc.add(em | 1<<e)
                elif not (vm>>b)&1:
                    st.append((b, vm|1<<b, em|1<<e))
    by_low = defaultdict(list)
    for em in cyc:
        by_low[(em & -em).bit_length()-1].append(em)
    memo = {0: 0}
    def rec(mask):
        r = memo.get(mask)
        if r is not None: return r
        low = (mask & -mask).bit_length()-1
        best = B + 1  # 剪枝: 超过 B 不再细究
        single = rec(mask ^ (1 << low)) + 1
        if single < best: best = single
        for em in by_low.get(low, ()):
            if em & mask == em:
                v = rec(mask ^ em) + 1
                if v < best: best = v
        memo[mask] = best
        return best
    return rec((1 << m) - 1) <= B

edges = list(combinations(range(7), 2))
t0 = time.time(); TLIMIT = 1100
done = passed = failed = 0
fails = []
easy = hard = 0
for comb in combinations(range(21), 17):
    if time.time() - t0 > TLIMIT:
        print(f"(时间盒触发 at done={done})")
        break
    mask = sum(1 << i for i in comb)
    adj, m = build(mask, edges, 7)
    if not two_connected(adj, 7): continue
    tv = tau_tjoin(adj, 7)
    if m + 2*tv < 19: continue
    done += 1
    ok = decision_le(adj, 7, 6)
    if ok: passed += 1
    else:
        failed += 1; fails.append(mask)
        print(f"  !! decision(≤6)=False: mask={mask}")
print(json.dumps(dict(resid_m17_done=done, passed=passed, failed=failed,
                      time=round(time.time()-t0,1))))
