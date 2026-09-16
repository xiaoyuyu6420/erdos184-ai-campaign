#!/usr/bin/env python3
"""阳性锚点自检：验证库各件工具在已知图上的行为。
纪律：每件工具先自击再上阵。"""
import sys
sys.path.insert(0, '/Users/munich/Desktop/数学/front_tre')
from fre_lib import *

ok = True
def check(desc, got, want):
    global ok
    tag = "PASS" if got == want else "FAIL"
    if got != want:
        ok = False
    print(f"[{tag}] {desc}: got {got}, want {want}")

# ---- 锚点 1: 最小 T-join ----
# P_4: T={0,3}: 最短路径 0-1-2-3, 3 条边
check("min_tjoin(P4, {0,3})", min_tjoin(path_graph(4), [0, 3])[0], 3)
# C_6: T={0,1}: dist=1
check("min_tjoin(C6, {0,1})", min_tjoin(cycle_graph(6), [0, 1])[0], 1)
# C_6: T=V: 全部 6 点需奇度: 完美匹配, 3 条边
check("min_tjoin(C6, V)", min_tjoin(cycle_graph(6), range(6))[0], 3)
# 星 K_1,3: T=V: 全部 3 条边
check("min_tjoin(K13, V)", min_tjoin(star(4), range(4))[0], 3)

# ---- 锚点 2: p_odd ----
check("p(K4)=2 (完美匹配)", p_odd(complete_graph(4)), 2)
check("p(Petersen)=5 (完美匹配)", p_odd(petersen()), 5)
check("p(K6)=3", p_odd(complete_graph(6)), 3)
check("p(K33)=3", p_odd(Graph(6, [(i, 3 + j) for i in range(3) for j in range(3)], "K33")), 3)

# ---- 锚点 3: ℓ 与 ILP 交叉验证 ----
# 注: ℓ(K6) = 12: 两个边不交哈密顿圈(12 边)后剩 3 边匹配; ILP 与 m-p 双向印证
for g, want in [(complete_graph(4), 4), (petersen(), 10), (complete_graph(6), 12)]:
    check(f"ell(K4/Petersen/K6 via m-p) {g.name}", g.m - p_odd(g), want)
for g in [complete_graph(4), petersen(), complete_graph(6)]:
    check(f"ell ILP {g.name}", max_cycle_packing_ILP(g), g.m - p_odd(g))

# 桥图: 双三角铃(两三角由一边相连)加延长成 3-正则不可行, 用 5-正则小图? 改用:
# 两个 K_4 各去掉一边, 缺口点两两相连 -> 3-正则 6 点 (有桥? 无, 有 2-边割)
# 造立方带桥图: 两个"K4 细分端点"结构, n=10
# side: K4 {a,b,c,d}, 细分边 da -> d-x-a; x 带桥
def dbl_sub_k4():
    # 顶点: 0..4 = a,b,c,d,x | 5..9 = a',b',c',d',x'
    e = [(0,1),(0,2),(1,2),(1,3),(2,3),(3,4),(4,0)]   # K4-abcd 去 da 加 x
    f = [(5+u, 5+v) for (u,v) in [(0,1),(0,2),(1,2),(1,3),(2,3),(3,4),(4,0)]]
    return Graph(10, e + f + [(4,9)], "double-subdiv-K4")
g = dbl_sub_k4()
check("double-subdiv-K4 cubic", sorted(set(g.deg)), [3])
check("double-subdiv-K4 connected", g.is_connected(), True)
pm = g.m - p_odd(g)  # ℓ
check("double-subdiv-K4 ℓ >= n/2+2=7", pm >= 7, True)
print(f"  (实际 ℓ = {pm}, n=10)")

# ---- 锚点 4: f_re 精确 DP vs 集合覆盖 B&B ----
for g in [path_graph(4), star(4), complete_graph(4), cycle_graph(5), petersen(), complete_graph(6), dbl_sub_k4()]:
    a = f_re_exact(g)[0]
    b = f_re_setcover(g)
    check(f"f_re DP == setcover ({g.name}, n={g.n})", a, b)
    print(f"    f_re({g.name}) = {a}")

# ---- 锚点 5: 定理 R 的上界一致性: f_re ≤ p + k (奇正则) ----
for g, k in [(complete_graph(4), 1), (petersen(), 1), (complete_graph(6), 2), (dbl_sub_k4(), 1)]:
    check(f"f_re ≤ p+k ({g.name})", f_re_exact(g)[0] <= p_odd(g) + k, True)

# ---- 锚点 6: 立方 f_re = p + 1 ----
for g in [complete_graph(4), petersen(), dbl_sub_k4()]:
    check(f"f_re == p+1 (cubic {g.name})", f_re_exact(g)[0], p_odd(g) + 1)

# ---- 锚点 7: K_6 的 f_re = 5 = n-1 (紧例) ----
check("f_re(K6) = 5 = n-1", f_re_exact(complete_graph(6))[0], 5)
# K_4: f_re = 3 = n-1
check("f_re(K4) = 3 = n-1", f_re_exact(complete_graph(4))[0], 3)

print("\n=== 全部锚点", "通过 ===" if ok else "存在失败 !!! ===")
sys.exit(0 if ok else 1)
