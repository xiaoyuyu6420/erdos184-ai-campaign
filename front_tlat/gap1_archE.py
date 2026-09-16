"""gap1_archE.py — H_n (miss=2) 显式构造: 跨类配对 Arch E (通用化 Arch D).

周期区行 15..4k-22, 行类 j=r mod 4, T0=(4,4,4,3), T2_j=k+T2OFF[j].
seg1-j: t∈[T0_j, T1_j), 列 c=r+a_j      (e_j=floor((j+a_j)/4), Q_j=(j+a_j) mod 4)
seg2-i: t∈[T1_i, T2_i), 列 c=r+ap_i
配对 ρ (bijection): seg2-i 填充列类 Q_{ρ(i)} 的顶部:
   ap_i ≡ Q_{ρ(i)} − i (mod 4);  E_i = floor((i+ap_i)/4)
   邻接: T1_{ρ(i)} + e_{ρ(i)} = T1_i + E_i   (列 u 区间无缝 → 无中列毒化)
   循环一致: ρ 的每个圈上 Σ(e − E) = 0.
符号: σ1_j = 2j+a_j+δ_j, σ2_i = 2i+ap_i+δ_i (mod 8), 8 类全异 → 无符号碰撞 (对任何 k).
边界 34 行 = patch(0..14\{1,6}) + tail(4k-21..4k-1) ← 34 空余列, 位掩 DFS 精确匹配.
"""
import sys, time, itertools
sys.path.insert(0, '/Users/munich/Desktop/数学/front_tlat')
sys.setrecursionlimit(100000)
from latpack import delta_H, is_transversal, SPECIALS

T0 = (4, 4, 4, 3)
T2OFF = (-5, -5, -5, -6)

def SIG(a, ap, T1=None):
    s1 = tuple((2 * j + a[j] + (2 if j == 3 else 0)) % 8 for j in range(4))
    s2 = tuple((2 * i + ap[i] + (2 if i == 3 else 0)) % 8 for i in range(4))
    return s1, s2

def build_period(k, a, ap, T1):
    n = 4 * k
    used_c, used_s = set(), set()
    for j in range(4):
        dl = 2 if j == 3 else 0
        for (lo, hi, off) in ((T0[j], T1[j], a[j]), (T1[j], k + T2OFF[j], ap[j])):
            for t in range(lo, hi):
                r = 4 * t + j
                c = r + off
                if not (0 <= c < n): return None
                if j == 3 and c % 2: return None
                if j == 1 and c % 2 == 0: return None
                s = (r + c + dl) % n
                if s in used_s or c in used_c: return None
                used_c.add(c); used_s.add(s)
    return used_c, used_s

def boundary_solve(k, used_c, used_s, node_cap=60000):
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
            if s in sidx: lst.append((cidx[c], c, sidx[s]))
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
    n = 4 * k
    T = [(r, col[r], (r + col[r] + delta_H(r, col[r], n)) % n) for r in range(n)]
    ok, msg = is_transversal('H', n, T)
    if not ok: return False, msg
    Ts = set(T); sp = SPECIALS['H']
    if sp[0] not in Ts or sp[1] not in Ts: return False, 'miss special 0/1'
    if sp[2] in Ts: return False, 'contains sp2'
    return True, 'OK'

def cycles_of(rho):
    n = len(rho); seen = [False] * n; cyc = []
    for i in range(n):
        if not seen[i]:
            c = []; j = i
            while not seen[j]:
                seen[j] = True; c.append(j); j = rho[j]
            cyc.append(c)
    return cyc

def search_k(k, e_grid, t_start, tcap, stats=None, verbose=True):
    n = 4 * k
    combos = 0
    RHOS = list(itertools.permutations(range(4)))
    for e in e_grid:
        wins = []
        for j in range(4):
            lo, hi = 4 * e[j] - j, 4 * e[j] + 3 - j
            vals = [x for x in range(max(lo, -13), min(hi, 7) + 1)]
            if j == 1: vals = [x for x in vals if x % 2 == 0]
            if j == 3: vals = [x for x in vals if x % 2 == 1 and x >= -7]
            wins.append(vals)
        for a in itertools.product(*wins):
            s1 = tuple((2 * j + a[j] + (2 if j == 3 else 0)) % 8 for j in range(4))
            if len(set(s1)) < 4: continue
            Q = tuple((j + a[j]) % 4 for j in range(4))
            if len(set(Q)) < 4: continue
            for rho in RHOS:
                # ap_i 残差与奇偶可行性
                resid = [(Q[rho[i]] - i) % 4 for i in range(4)]
                if resid[1] % 2: continue      # ap_1 偶
                if resid[3] % 2 == 0: continue # ap_3 奇
                # E 逐圈一致: 圈上 Σ E = Σ e (邻接式绕圈求和)
                cyc = cycles_of(rho)
                E = [None] * 4
                def gen_E(ci):
                    if ci == len(cyc):
                        yield tuple(E); return
                    c = cyc[ci]
                    m = len(c)
                    se = sum(e[x] for x in c)
                    for Ev in itertools.product(range(-3, 4), repeat=m - 1):
                        for pos, i in enumerate(c[:m - 1]):
                            E[i] = Ev[pos]
                        last = se - sum(Ev)
                        if -3 <= last <= 3:
                            E[c[m - 1]] = last
                            yield from gen_E(ci + 1)
                        for i in c[:m - 1]:
                            E[i] = None
                        E[c[m - 1]] = None
                for Et in gen_E(0):
                    # ap_i 唯一: 窗口 [4E_i − i, 4E_i + 3 − i] 中 ≡ resid[i] (mod 4)
                    ap = []
                    okk = True
                    for i in range(4):
                        cand = [x for x in range(4 * Et[i] - i, 4 * Et[i] + 4 - i) if x % 4 == resid[i]]
                        if len(cand) != 1 or not (-14 <= cand[0] <= 8): okk = False; break
                        ap.append(cand[0])
                    if not okk: continue
                    ap = tuple(ap)
                    s2 = tuple((2 * i + ap[i] + (2 if i == 3 else 0)) % 8 for i in range(4))
                    if len(set(s1 + s2)) < 8: continue
                    # T1: 每圈一个自由变量, 传播
                    bases = []
                    okcyc = True
                    t1 = [None] * 4
                    for c in cyc:
                        got = []
                        for base in range(k // 2 - 6, k // 2 + 6):
                            t1[c[0]] = base
                            good = True
                            for p in range(len(c)):
                                nxt = c[(p + 1) % len(c)]
                                if nxt == c[0]:
                                    continue
                                val = t1[c[p]] + Et[c[p]] - e[nxt]
                                if not (T0[nxt] + 1 <= val <= k + T2OFF[nxt] - 1 and
                                        k // 2 - 7 <= val <= k // 2 + 7):
                                    good = False; break
                                t1[nxt] = val
                            if good: got.append(tuple(t1))
                        if not got: okcyc = False; break
                        bases.append(got)
                    if not okcyc: continue
                    for combo in itertools.product(*bases):
                        T1 = [None] * 4
                        for c, g in zip(cyc, combo):
                            for i in c: T1[i] = g[i]
                        combos += 1
                        if stats is not None: stats[0] = combos
                        if combos % 5000 == 0:
                            if time.time() - t_start > tcap:
                                print(f'  tcap at {combos} combos', flush=True)
                                return None
                        res = build_period(k, a, ap, T1)
                        if res is None: continue
                        uc, us = res
                        if len(uc) != 4 * k - 36: continue
                        if 1 in uc or 5 in uc: continue
                        if 5 in us or 14 in us or 23 in us: continue  # 三特殊符号全避开 → 一模式三证书
                        col = boundary_solve(k, uc, us)
                        if col is None: continue
                        # 补全周期区列映射 + 特殊格行
                        full = {}
                        for j in range(4):
                            for (lo, hi, off) in ((T0[j], T1[j], a[j]),
                                                  (T1[j], k + T2OFF[j], ap[j])):
                                for t in range(lo, hi):
                                    full[4 * t + j] = 4 * t + j + off
                        full.update(col); full[1] = 1; full[6] = 5
                        ok, msg = full_verify(k, full)
                        if ok:
                            print(f'  WINNER a={a} ap={ap} rho={rho} E={Et} T1={T1} '
                                  f'({combos} combos, {time.time()-t_start:.0f}s)', flush=True)
                            return (a, ap, rho, Et, T1, full)
    print(f'  exhausted {combos} combos ({time.time()-t_start:.0f}s)', flush=True)
    return None

if __name__ == '__main__':
    K = int(sys.argv[1]) if len(sys.argv) > 1 else 32
    TCAP = float(sys.argv[2]) if len(sys.argv) > 2 else 2400.0
    t0 = time.time()
    e_grid = [e for e in itertools.product([-2, -1, 0, 1, 2, 3], repeat=4)]
    r = search_k(K, e_grid, t0, TCAP)
    if r:
        a, ap, rho, Et, t1, col = r
        import json
        json.dump({'k': K, 'a': list(a), 'ap': list(ap), 'rho': list(rho),
                   'E': list(Et), 'T1': t1, 'col': col},
                  open(f'/Users/munich/Desktop/数学/front_tlat/gap1_H{4*K}_v2.json', 'w'))
        print(f'k={K} SOLVED, saved gap1_H{4*K}_v2.json', flush=True)
    print(f'total {time.time()-t0:.0f}s', flush=True)
