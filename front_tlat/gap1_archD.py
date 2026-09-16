"""gap1_archD.py — H_n (miss=2) 显式构造: 均匀分段 Arch D.

结构 (k >= K0):
  周期区行 15..4k-22, 行类 j = r mod 4, T0=(4,4,4,3), T2=(k-5,k-5,k-5,k-6).
  seg1: t in [T0_j, T)  列 c = r + a_j     (e_j = floor((j+a_j)/4), Q_j = (j+a_j) mod 4)
  seg2: t in [T, T2_j)  列 c = r + a_j + d_j (d_j in ±1..±3, 偶类 j=1,3 取 ±2)
  列: 类 Q_j 内 u 区间 [T0+e, T+e) ∪ [T+e, T2+e) 无缝 (anti-poison: 中列必被周期用掉)
  符号: sigma^1_j = 2j+a_j+δ_j, sigma^2_j = sigma^1_j + d_j (mod 8), 8 类全互异
        → 跨段/跨类符号碰撞不可能 (8(t-t') ≡ σ'-σ mod 4k 而 σ'≢σ mod 8)
  边界 34 行 (patch 0..14 去掉行1,6 + tail 4k-21..4k-1) ← 34 空余列, 符号落空余符号集.
  精确匹配: 位掩 DFS + MRV. 全部通过 is_transversal 独立验证.
"""
import sys, time
sys.path.insert(0, '/Users/munich/Desktop/数学/front_tlat')
sys.setrecursionlimit(100000)
from latpack import delta_H, is_transversal, SPECIALS

T0 = (4, 4, 4, 3)
T2OFF = (-5, -5, -5, -6)          # T2_j = k + T2OFF[j]
SIG1 = lambda a: tuple((2 * j + a[j] + (2 if j == 3 else 0)) % 8 for j in range(4))

def build_period(k, a, d, T):
    """返回 (used_c set, used_s set) 或 None (任何碰撞/非法)."""
    n = 4 * k
    used_c, used_s = set(), set()
    for j in range(4):
        dj = d[j]
        dl = 2 if j == 3 else 0
        aj = a[j]
        ap = aj + dj
        if (j == 1 or j == 3) and dj % 2:  # 偶性
            return None
        for t in list(range(T0[j], T)) + list(range(T, k + T2OFF[j])):
            r = 4 * t + j
            c = r + (aj if t < T else ap)
            if not (0 <= c < n):
                return None
            if j == 3 and c % 2:  return None
            if j == 1 and c % 2 == 0: return None
            s = (r + c + dl) % n
            if s in used_s or c in used_c: return None
            used_c.add(c); used_s.add(s)
    return used_c, used_s

def boundary_solve(k, used_c, used_s, node_cap=40000):
    """34 行精确匹配 (节点上限防爆炸). 返回 col dict (不含行1,6) 或 None."""
    n = 4 * k
    left_c = [c for c in range(n) if c not in used_c and c not in (1, 5)]
    left_s = sorted(s for s in range(n) if s not in used_s and s not in (5, 14))
    if len(left_c) != 34 or len(left_s) != 34: return None
    cidx = {c: i for i, c in enumerate(left_c)}
    sidx = {s: i for i, s in enumerate(left_s)}
    rows = [r for r in range(15) if r not in (1, 6)] + list(range(4 * k - 21, 4 * k))
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
            if s in sidx:
                lst.append((cidx[c], c, sidx[s]))
        if not lst: return None
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
        return sol if dfs(0, 0, 0) else None
    except TimeoutError:
        return None

def full_verify(k, col):
    """独立验证: transversal + type (含 sp0,sp1 缺 sp2)."""
    n = 4 * k
    T = [(r, col[r], (r + col[r] + delta_H(r, col[r], n)) % n) for r in range(n)]
    ok, msg = is_transversal('H', n, T)
    if not ok: return False, msg
    Ts = set(T)
    sp = SPECIALS['H']
    if sp[0] not in Ts or sp[1] not in Ts: return False, 'miss special 0/1'
    if sp[2] in Ts: return False, 'contains sp2'
    return True, 'OK'

def search_k(k, e_grid, t0, tcap, verbose=True):
    """e_grid: 可迭代的 e 四元组. 返回 (a, d, T, col) 或 None."""
    n = 4 * k
    combos = 0
    for e in e_grid:
        # a_j 窗口 [4e_j - j, 4e_j + 3 - j], 奇偶约束
        wins = []
        for j in range(4):
            lo, hi = 4 * e[j] - j, 4 * e[j] + 3 - j
            vals = [x for x in range(max(lo, -13), min(hi, 7) + 1)
                    if (x - j) % 4 == (x % 4) or True]
            if j == 1: vals = [x for x in vals if x % 2 == 0]
            if j == 3: vals = [x for x in vals if x % 2 == 1]
            if j == 3: vals = [x for x in vals if x >= -7]   # B_3 >= 0
            wins.append(vals)
        for a0 in wins[0]:
            for a1 in wins[1]:
                for a2 in wins[2]:
                    for a3 in wins[3]:
                        a = (a0, a1, a2, a3)
                        s1 = SIG1(a)
                        if len(set(s1)) < 4: continue
                        # d 候选: |d|<=3, j=1,3 取 ±2; sigma^2 全异且异于 s1
                        dopts = []
                        for j in range(4):
                            if j in (1, 3): dopts.append([2, -2])
                            else: dopts.append([1, -1, 2, -2, 3, -3])
                        for d0 in dopts[0]:
                            for d1 in dopts[1]:
                                for d2 in dopts[2]:
                                    for d3 in dopts[3]:
                                        d = (d0, d1, d2, d3)
                                        s2 = tuple((s1[j] + d[j]) % 8 for j in range(4))
                                        if len(set(s2 + s1)) < 8: continue
                                        for T in range(k // 2 - 5, k // 2 + 5):
                                            combos += 1
                                            if combos % 20000 == 0 and time.time() - t0 > tcap:
                                                print(f'  k={k}: tcap {combos} combos', flush=True)
                                                return None
                                            res = build_period(k, a, d, T)
                                            if res is None: continue
                                            uc, us = res
                                            if len(uc) != 4 * k - 36: continue
                                            if 1 in uc or 5 in uc: continue
                                            if 5 in us or 14 in us: continue
                                            # len(us)==4k-36 由 build 无碰撞保证
                                            col = boundary_solve(k, uc, us)
                                            if col is None: continue
                                            full = dict(col); full[1] = 1; full[6] = 5
                                            ok, msg = full_verify(k, full)
                                            if ok:
                                                print(f'  k={k}: WINNER a={a} d={d} T={T} '
                                                      f'({combos} combos, {time.time()-t0:.0f}s)', flush=True)
                                                return (a, d, T, full)
                                            elif verbose:
                                                print(f'  k={k}: match found but verify FAIL: {msg}', flush=True)
    print(f'  k={k}: exhausted {combos} combos ({time.time()-t0:.0f}s)', flush=True)
    return None

if __name__ == '__main__':
    import itertools
    t0 = time.time()
    K = int(sys.argv[1]) if len(sys.argv) > 1 else 32
    TCAP = float(sys.argv[2]) if len(sys.argv) > 2 else 1500.0
    # e 分层: 由小到大
    e_layers = [
        [(0, 0, 0, 0)],
        [e for e in itertools.product([-1, 0, 1], repeat=4)],
        [e for e in itertools.product([-2, -1, 0, 1, 2], repeat=4)],
    ]
    seen = set()
    for layer in e_layers:
        grid = [e for e in layer if e not in seen]
        seen.update(grid)
        print(f'== k={K} e-layer |{-2}..2|={len(grid)} ==', flush=True)
        r = search_k(K, grid, t0, TCAP)
        if r:
            a, d, T, col = r
            import json
            json.dump({'k': K, 'a': a, 'd': d, 'T': T, 'col': col},
                      open(f'/Users/munich/Desktop/数学/front_tlat/gap1_H{4*K}.json', 'w'))
            print(f'k={K} SOLVED, saved gap1_H{4*K}.json', flush=True)
            break
    print(f'total {time.time()-t0:.0f}s', flush=True)
