#!/usr/bin/env python3
"""n=8,9 定向候选：反例 K3∪K_{3,4} 的自然外推（去边降度版）与混合结构。"""
from ce_exact import ce_dp, ce_branch
from itertools import combinations

def ce_of(name, n, edges, check=True):
    deg = [0]*n
    for u,v in edges: deg[u]+=1; deg[v]+=1
    mask = (1 << len(edges)) - 1
    v = ce_dp(n, edges, mask)
    v2 = ce_branch(n, edges, mask) if check else v
    ok = "OK" if v2 == v else "MISMATCH!"
    print(f"{name:38s} n={n} m={len(edges)} Δ={max(deg)} ce={v} (n-1={n-1}) [{ok}]", flush=True)
    return v

# 反例 G7 = K3(0,1,2) + K_{3,4}(b=3..6)
G7 = [(0,1),(1,2),(0,2)] + [(a,b) for a in range(3) for b in range(3,7)]

print("== n=8：反例外推（加第 5 个 b 点、去边把 a 侧压到 Δ≤6）==")
# 新 b 点 = 7，连 a1,a2（不加 a3，控制度数）
for drop in [(0,1),(0,2),(1,2)]:
    e = [x for x in G7 if x != drop] + [(0,7),(1,7)]
    ce_of(f"G8 = G7 −{drop} + b5~a1,a2", 8, e)
# 变体：b5 连 a1、a3
for drop in [(0,1),(1,2)]:
    e = [x for x in G7 if x != drop] + [(0,7),(2,7)]
    ce_of(f"G8 = G7 −{drop} + b5~a1,a3", 8, e)

print("== n=8：K3 + K_{3,5} 型整体（Δ=7）去两条星边 ==")
base = [(0,1),(1,2),(0,2)] + [(a,b) for a in range(3) for b in range(3,8)]  # m=18
for drop in combinations([(a,b) for a in range(3) for b in range(3,8)], 2):
    dset = set(drop)
    # 只试「去掉同一 a 点的两条边」的对称代表（a 点度 7→5）
    if len({u for u,v in drop}) != 1:
        continue
    e = [x for x in base if x not in dset]
    ce_of(f"K3+K35 −{sorted(drop)}", 8, e)
    break  # 一个代表即可（对称性）

print("== n=8：两个 K3+K_{3,2} 共享 a 三角形（b 侧 4 点）变形 ==")
# a={0,1,2} 三角形，b={3..7} 5 点各连恰好 2 个 a 点（3 度 b 点）
# b 度 3 ⟹ 5 个奇点集中 + a 侧度 = 2 + deg_a
import itertools
for pat in [[(0,1),(0,1),(0,1),(1,2),(1,2)], [(0,1),(0,1),(0,2),(0,2),(1,2)]]:
    e = [(0,1),(1,2),(0,2)]
    ok = True
    for i, (x, y) in enumerate(pat):
        e.append((x, 3+i)); e.append((y, 3+i))
    deg = [0]*8
    for u,v in e: deg[u]+=1; deg[v]+=1
    if max(deg) <= 6:
        ce_of(f"ΔK3 + 5×P2 模式{pat}", 8, e)
