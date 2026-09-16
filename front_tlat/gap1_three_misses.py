"""gap1_three_misses.py — 给定 Arch E 模式 (a, ap, rho, E, h), 对 miss∈{0,1,2}
各解边界 34 行 (miss 行 δ=0, 另两行取特殊格), 独立验证 + 三交集检查.
"""
import sys, json, time, itertools
sys.path.insert(0, '/Users/munich/Desktop/数学/front_tlat')
sys.setrecursionlimit(100000)
from latpack import delta_H, is_transversal, SPECIALS

T0 = (4, 4, 4, 3)
T2OFF = (-5, -5, -5, -6)

def period_cols_syms(k, a, ap, T1):
    n = 4 * k
    used_c, used_s, cmap = set(), set(), {}
    for j in range(4):
        dl = 2 if j == 3 else 0
        for (lo, hi, off) in ((T0[j], T1[j], a[j]), (T1[j], k + T2OFF[j], ap[j])):
            for t in range(lo, hi):
                r = 4 * t + j
                c = r + off
                cmap[r] = c
                used_c.add(c); used_s.add((r + c + dl) % n)
    return cmap, used_c, used_s

def boundary_solve_miss(k, used_c, used_s, miss, node_cap=600000):
    """miss∈{0,1,2}: 缺第 miss 个特殊格; 另两 B 行固定特殊列."""
    n = 4 * k
    sp = SPECIALS['H']   # [(1,1,5),(6,5,14),(11,9,23)]
    fixed = {sp[i][0]: sp[i][1] for i in range(3) if i != miss}
    missrow = sp[miss][0]
    left_c = [c for c in range(n) if c not in used_c and c not in set(fixed.values())]
    left_s = sorted(s for s in range(n) if s not in used_s
                    and s not in {sp[i][2] for i in range(3)})
    if len(left_c) != 34 or len(left_s) != 34:
        return None, f'left sizes {len(left_c)},{len(left_s)}'
    cidx = {c: i for i, c in enumerate(left_c)}
    sidx = {s: i for i, s in enumerate(left_s)}
    rows = [r for r in range(15) if r not in fixed and r != missrow] \
        + list(range(4 * k - 21, 4 * k))
    legal = {}
    for r in rows:
        lst = []
        for c in left_c:
            d = delta_H(r, c, n)
            if r in (0, 5, 10):
                if d != 4: continue
            else:
                if d != 0: continue
            s = (r + c + d) % n
            if s in sidx: lst.append((cidx[c], c, sidx[s]))
        if not lst:
            return None, f'row {r} starved'
        legal[r] = lst
    order = sorted(rows, key=lambda r: len(legal[r]))
    sol = {}
    nodes = [0]
    def dfs(i, cmask, smask):
        if i == len(order): return True
        nodes[0] += 1
        if nodes[0] > node_cap: raise TimeoutError
        r = order[i]
        for (ci, c, si) in legal[r]:
            if cmask >> ci & 1: continue
            if smask >> si & 1: continue
            sol[r] = c
            if dfs(i + 1, cmask | (1 << ci), smask | (1 << si)): return True
            del sol[r]
        return False
    try:
        return (sol if dfs(0, 0, 0) else None), f'{nodes[0]} nodes'
    except TimeoutError:
        return None, f'timeout at {nodes[0]}'

def full_T(k, a, ap, T1, boundary, miss):
    n = 4 * k
    cmap, _, _ = period_cols_syms(k, a, ap, T1)
    cmap.update(boundary)
    sp = SPECIALS['H']
    for i in range(3):
        if i != miss:
            cmap[sp[i][0]] = sp[i][1]
    T = [(r, cmap[r], (r + cmap[r] + delta_H(r, cmap[r], n)) % n) for r in range(n)]
    assert len(cmap) == n
    return T

def main():
    w = json.load(open('/Users/munich/Desktop/数学/front_tlat/gap1_H128.json'))
    a, ap, E = tuple(w['a']), tuple(w['ap']), tuple(w['E'])
    h = [t1 - 16 for t1 in w['T1']]
    print(f"pattern a={a} ap={ap} E={E} h={h}", flush=True)
    Ts = []
    for miss, k in [(m, K) for m in (0, 1, 2) for K in ([32] )]:
        T1 = [k // 2 + hj for hj in h]
        cmap, uc, us = period_cols_syms(k, a, ap, T1)
        assert len(uc) == 4 * k - 36, len(uc)
        b, info = boundary_solve_miss(k, uc, us, miss)
        print(f'k={k} miss={miss}: {"OK" if b is not None else "FAIL"} ({info})', flush=True)
        if b is None: return
        T = full_T(k, a, ap, T1, b, miss)
        ok, msg = is_transversal('H', 4 * k, T)
        sp = SPECIALS['H']; Tsset = set(T)
        inc = [e for e in sp if e in Tsset]
        print(f'  transversal: {ok} {msg}; specials in: {inc}; missing sp{miss}: {sp[miss] not in Tsset}', flush=True)
        assert ok and len(inc) == 2 and sp[miss] not in Tsset
        Ts.append(set(T))
    inter = Ts[0] & Ts[1] & Ts[2]
    print(f'triple intersection: {len(inter)} {sorted(inter)[:5]}', flush=True)
    if not inter:
        print('TRIPLE EMPTY — H_n 无 pinned entry 完全证书 (k=32 模式)', flush=True)
        json.dump({'k': 32, 'a': list(a), 'ap': list(ap), 'E': list(E), 'h': h},
                  open('/Users/munich/Desktop/数学/front_tlat/gap1_H32_three.json', 'w'))

if __name__ == '__main__':
    main()
