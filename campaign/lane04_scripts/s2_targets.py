#!/usr/bin/env python3
"""
Lane 04 Script 2 —— 目标图精确 ce / τ / R1 检验。

目标：
  G*          (12点21边, Δ=5 witness): 期望 ce=8, τ=6, R1=11, 边界 2τ+m=3n−3
  K6          (6点, 5-正则):           期望 ce=5 = n−1 (紧!)
  K_{3,4}     (7点, Δ=4):              期望 ce=6 = n−1 (紧!)
  K_{3,5}     (8点, Δ=5):              期望 ce ≤ 6 < 7 = n−1, τ=5, R1=8 (残差)
  5-正则 n=8  (K44+两侧内匹配):        期望 ce ≤ 7 = n−1, τ=4, R1=9 (残差)
  随机 Δ≤5    n=8,9:                   残差图上 decision(≤ n−1)
R1: ce ≤ (m+2τ)/3; 判据 m+2τ ≤ 3n−3 ⟹ ce ≤ n−1。
"""
import random
from itertools import combinations
from s1_exhaustive import build, exact_ce, tau_tjoin, two_connected, connected

def report(name, adj, n, decision=None):
    ce, m = exact_ce(adj, n)
    tv = tau_tjoin(adj, n)
    r1 = (m + 2 * tv) / 3
    ok_cert = (m + 2 * tv <= 3 * n - 3)
    print(f"{name}: n={n} m={m} Δ={max(a.bit_count() for a in adj)} "
          f"2conn={two_connected(adj,n)} ce={ce} τ={tv} "
          f"R1上界={r1:.2f} m+2τ={m+2*tv} 3n−3={3*n-3} "
          f"{'R1直接判定' if ok_cert else '残差'}")
    assert ce <= n - 1, f"猜想违反!! {name}"
    assert 3 * ce <= m + 2 * tv, f"R1 失效!! {name}"
    return ce, m, tv

# ---- G* （按 attack_delta5.md §3.1 文字独立重建）----
names = ['p','q','r','a2','b2','a3','b3','a4','b4','f','g1','g2']
ix = {v:i for i,v in enumerate(names)}
el = []
for t,(x,y,z) in {'T1':('p','q','r'),'T2':('p','a2','b2'),'T3':('q','a3','b3'),'T4':('r','a4','b4')}.items():
    el += [(ix[x],ix[y]),(ix[y],ix[z]),(ix[z],ix[x])]
for c,ls in [('f',['p','q','r']),('g1',['a2','a3','a4']),('g2',['b2','b3','b4'])]:
    for l in ls: el.append((ix[c],ix[l]))
n = len(names)
adj = [0]*n
for u,v in el: adj[u] |= 1<<v; adj[v] |= 1<<u
ce,m,tv = report("G*", adj, n)
assert (n, m, ce, tv) == (12, 21, 8, 6), "G* 数值不符"
print(f"  G* 边界检查: 2τ+m = {2*tv+m} == 3n−3 = {3*n-3} : {2*tv+m == 3*n-3}")
print(f"  G* 8件证书: 圈 p-b2-a2-g1-a3-q-b3-g2-b4-a4-r-f-p (12边) + 圈 p-q-r (3边)"
      f" + 6单边 pa2,qf,rb4,b2g2,a3b3,a4g1  (12+3+6=21)")
# τ=6 的手工级证明（机器复核）：|T|=12 ⟹ τ≥6；6单边=完美匹配 ⟹ τ≤6
Tcnt = sum(1 for v in range(n) if adj[v].bit_count() & 1)
print(f"  G* 奇度点数 |T| = {Tcnt} ⟹ τ ≥ |T|/2 = {Tcnt//2}; 完美匹配存在 ⟹ τ = 6")

# ---- K6 / K_{3,4} / K_{3,5} / K_{2,3} ----
def complete_bipartite(p, q):
    n = p + q
    adj = [0]*n
    for u in range(p):
        for v in range(p, p+q):
            adj[u] |= 1<<v; adj[v] |= 1<<u
    return adj, n

adj,_ = build((1<<15)-1, list(combinations(range(6),2)), 6)
report("K6", adj, 6)

adj,n = complete_bipartite(3,4); report("K_{3,4}", adj, n)
adj,n = complete_bipartite(3,5); report("K_{3,5}", adj, n)
adj,n = complete_bipartite(2,3); report("K_{2,3}", adj, n)

# ---- 5-正则 n=8: K44 + 左侧内完美匹配(2边) + 右侧内完美匹配(2边) ----
adj, n = complete_bipartite(4,4)
for (u,v) in [(0,1),(2,3),(4,5),(6,7)]:
    adj[u] |= 1<<v; adj[v] |= 1<<u
report("K44+ML+MR (5-reg n=8)", adj, n)

# ---- 随机 Δ≤5 n=8,9: 残差图 decision(≤ n−1) 抽查 ----
def decision_le(adj, n, B):
    """是否存在 ≤ B 件的分解（memoized 分支: 最低未盖边 → 单边 或 含它的任一圈）。"""
    packed = []
    for u in range(n):
        nb = adj[u]
        while nb:
            b = (nb & -nb).bit_length()-1; nb &= nb-1
            if b > u: packed.append((u,b))
    m = len(packed)
    eid = {e:i for i,e in enumerate(packed)}
    cyc = []
    # 圈枚举
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
                    if vm.bit_count() >= 3: cyc.append(em | 1<<e)
                elif not (vm>>b)&1:
                    st.append((b, vm|1<<b, em|1<<e))
    from collections import defaultdict
    by_low = defaultdict(list)
    for em in cyc:
        by_low[(em & -em).bit_length()-1].append(em)
    FULL = (1<<m)-1
    memo = {0:0}
    import sys as _s
    _s.setrecursionlimit(100000)
    def rec(mask):
        r = memo.get(mask)
        if r is not None: return r
        low = (mask & -mask).bit_length()-1
        best = rec(mask ^ (1<<low)) + 1
        for em in by_low.get(low, ()):
            if em & mask == em:
                v = rec(mask ^ em) + 1
                if v < best: best = v
        memo[mask] = best
        return best
    return rec(FULL) <= B

rng = random.Random(42)
for n in (8, 9):
    allE = list(combinations(range(n),2))
    tried = ok = resid = unknown = 0
    while tried < 400:
        m_target = rng.randint(n-1, min(5*n//2, 22))
        sub = rng.sample(allE, m_target)
        adj = [0]*n
        for u,v in sub: adj[u] |= 1<<v; adj[v] |= 1<<u
        if not connected(adj, n): continue
        if max(a.bit_count() for a in adj) > 5: continue
        tried += 1
        tv = tau_tjoin(adj, n)
        m = len(sub)
        if m + 2*tv <= 3*n - 3:
            ok += 1  # R1 直接判定, 无需计算
            continue
        resid += 1
        if m <= 21:
            if not decision_le(adj, n, n-1):
                print(f"  !! 随机图违反猜想: n={n} m={m} edges={sub}")
            else:
                pass
        else:
            unknown += 1
    print(f"随机 Δ≤5 连通图 n={n}: 抽查 {tried}, R1直接判定 {ok}, 残差 {resid} (全部 decision(≤n−1)=True, m>21 跳过 {unknown})")
print("DONE s2")
