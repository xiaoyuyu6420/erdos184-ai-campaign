#!/usr/bin/env python3
"""lane05 侦察第一波：关键白名单族的精确 ce。
包含 K_{a,b}（Δ≤6）、完全三部、正则图（经补图构造）、以及 benchmark。"""
import time, itertools
from ce_exact import ce_dp, ce_branch, cycles_bitmask

def complete_bip(a, b):
    edges = [(i, a + j) for i in range(a) for j in range(b)]
    n = a + b
    return n, edges

def complete_tripart(a, b, c):
    parts = [list(range(a)), list(range(a, a + b)), list(range(a + b, a + b + c))]
    edges = []
    for i, p in enumerate(parts):
        for q in parts[i + 1:]:
            for u in p:
                for v in q:
                    edges.append((u, v))
    return a + b + c, edges

def complement(n, edges_h):
    alle = set(itertools.combinations(range(n), 2))
    eh = {(min(u, v), max(u, v)) for u, v in edges_h}
    return sorted(alle - eh)

def cycle_graph(n, offset=0):
    return [(offset + i, offset + (i + 1) % n) for i in range(n)]

def regular_via_complement(n, comp_cycles):
    """K_n 去掉若干不交圈 comp_cycles（每项为长度>=3 的列表）。"""
    eh = []
    for L in comp_cycles:
        eh += cycle_graph(L, sum(comp_cycles[:comp_cycles.index(L)]))
    # 更简单：直接逐段
    eh = []
    off = 0
    for L in comp_cycles:
        eh += cycle_graph(L, off)
        off += L
    return n, complement(n, eh)

def report(name, n, edges, check=True):
    m = 0
    for i in range(len(edges)):
        m |= 1 << i
    t0 = time.time()
    v = ce_dp(n, edges, m)
    dt = time.time() - t0
    deg = [0] * n
    for u, w in edges:
        deg[u] += 1; deg[w] += 1
    delta = max(deg)
    ce2 = ce_branch(n, edges, m) if check and dt < 30 else None
    ok = "" if ce2 is None else (" [x2=%s]" % ("OK" if ce2 == v else "MISMATCH!"))
    print(f"{name:24s} n={n} m={len(edges)} Δ={delta} ce={v} ce/n={v/n:.3f} ce-(n-1)={v-(n-1)} t={dt:.2f}s{ok}", flush=True)
    return v

if __name__ == '__main__':
    print("== benchmark ==")
    report("K_7", 7, list(itertools.combinations(range(7), 2)))
    print("== 完全二部 Δ≤6（n≤9 侦察范围）==")
    for a in range(1, 7):
        for b in range(a, 7):
            if a + b <= 9 and b <= 6:
                n, e = complete_bip(a, b)
                report(f"K_{a},{b}", n, e)
    print("== 完全三部（n≤9, Δ≤6）==")
    for a in range(1, 4):
        for b in range(a, 4):
            for c in range(b, 4):
                n, e = complete_tripart(a, b, c)
                deg = [0] * n
                for u, w in e:
                    deg[u] += 1; deg[w] += 1
                if max(deg) <= 6:
                    report(f"K_{a},{b},{c}", n, e)
    print("== 6-正则 n=7,8,9（K_n − 2-正则）==")
    report("K_7 (6-reg)", 7, list(itertools.combinations(range(7), 2)))
    for parts8 in [[8], [5, 3], [4, 4]]:
        n, e = regular_via_complement(8, parts8)
        report(f"6-reg n=8 = K8−C{parts8}", n, e)
    for parts9 in [[9], [6, 3], [5, 4], [3, 3, 3]]:
        n, e = regular_via_complement(9, parts9)
        report(f"6-reg n=9 = K9−C{parts9}", n, e)
    print("== witness G* 复算（与 notes 对账）==")
    # G*: p=0,q=1,r=2,a2=3,b2=4,a3=5,b3=6,a4=7,b4=8,f=9,g1=10,g2=11
    t1 = [(0,1),(1,2),(0,2)]
    t2 = [(0,3),(3,4),(0,4)]
    t3 = [(1,5),(5,6),(1,6)]
    t4 = [(2,7),(7,8),(2,8)]
    stars = [(9,0),(9,1),(9,2),(10,3),(10,5),(10,7),(11,4),(11,6),(11,8)]
    report("G*(Δ=5 witness)", 12, t1 + t2 + t3 + t4 + stars, check=True)
