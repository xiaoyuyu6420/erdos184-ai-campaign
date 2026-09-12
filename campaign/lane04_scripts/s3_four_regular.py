#!/usr/bin/env python3
"""
Lane 04 Script 3 —— 4-正则图的最小圈分解数 vs n/2 − 1（猜想 C2 检验）。

C2（lane 文档 §4 猜想2）: 每个 2-连通 4-正则图（偶阶 n ≥ 6）的 exact_ce ≤ n/2 − 1。
动机: 5-正则 G 有完美匹配 F 时 G−F 是 4-正则偶图, ce(G) ≤ n/2 + mindecomp(G−F)
      ≤ n/2 + n/2 − 1 = n−1。紧例: K_{2,2,2}（八面体, n=6）mindecomp = 2 = n/2−1。

n=6: 全枚举(15 labeled); n=7: 全枚举(825 labeled, 奇阶对照); n=8: 随机样本。
"""
import random
from itertools import combinations
from s1_exhaustive import exact_ce, two_connected, build

def enum_regular(n, d):
    allE = [(u,v) for u in range(n) for v in range(u+1,n)]
    E = len(allE)
    deg = [0]*n
    sols = []
    def bt(i, mask):
        if i == E:
            if all(x == d for x in deg):
                sols.append(mask)
            return
        u, v = allE[i]
        for x in range(n):
            if d - deg[x] > E - i:
                return
        bt(i+1, mask)
        if deg[u] < d and deg[v] < d:
            deg[u] += 1; deg[v] += 1
            bt(i+1, mask | (1 << i))
            deg[u] -= 1; deg[v] -= 1
    bt(0, 0)
    return sols, allE

def check(n, sample=0, seed=1, label=""):
    sols, allE = enum_regular(n, 4)
    rng = random.Random(seed)
    if sample and len(sols) > sample:
        picks = rng.sample(sols, sample)
        how = f"抽样 {sample}/{len(sols)}"
    else:
        picks = sols
        how = f"全枚举 {len(sols)}"
    worst = -1; bad = 0; not2c = 0; tight = 0
    for mask in picks:
        adj, m = build(mask, allE, n)
        if not two_connected(adj, n):
            not2c += 1
            continue
        ce, m = exact_ce(adj, n)
        bound = n//2 - 1
        if ce > bound:
            bad += 1
            print(f"  !! C2 失败: n={n} mask={mask} exact_ce={ce} > n/2−1={bound}")
        if ce == bound:
            tight += 1
        if ce > worst: worst = ce
    print(f"n={n} 4-正则 [{how}] 非2连通(跳过)={not2c} C2违反={bad} "
          f"恰达 n/2−1 的={tight} max-exact_ce={worst} (n/2−1={n//2-1}) [{label}]")
    return bad

if __name__ == '__main__':
    total = 0
    total += check(6, label="全枚举")
    total += check(7, label="奇阶对照")
    total += check(8, sample=1500, seed=8, label="随机样本")
    print("TOTAL C2 violations (2-connected):", total)
