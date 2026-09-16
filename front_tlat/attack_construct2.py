"""attack_construct2.py — H_n (miss=2) 闭式骨架 v2: 符号层常数表.
周期区 4 类仿射公式 (mod 4 列段 / mod 8 符号段互异 → 双射自动),
剩余 36 列 (每 mod4 段头 4-5 + 尾 4-5) 恰好给 patch+tail 36 行, DFS 求常数表.
"""
import sys, itertools
sys.path.insert(0, '/Users/munich/Desktop/数学/front_tlat')
from latpack import delta_H, symbol as sym, SPECIALS, is_transversal

def build(k, a, pt):
    """a = (a0,a1,a2,a3); pt = dict row -> ('head', q, u) | ('tail', q, w) | ('const', c).
    返回完整 colmap 或 None."""
    n = 4 * k
    col = {}
    # 周期区
    for r in range(15, 4 * k - 21):
        j = r % 4
        c = r + a[j]
        if not (0 <= c < n): return None
        col[r] = c
    used_c = set(col.values())
    used_s = set((r + c + delta_H(r, c, n)) % n for r, c in col.items())
    # patch+tail
    for r in list(range(15)) + list(range(4 * k - 21, 4 * k)):
        tag = pt.get(r)
        if tag is None: return None
        if tag[0] == 'const':
            c = tag[1]
        elif tag[0] == 'head':
            q, u = tag[1], tag[2]
            c = 4 * u + q
        else:
            q, w = tag[1], tag[2]
            c = 4 * k - 4 * (1 + w) + q
        if not (0 <= c < n) or c in used_c: return None
        d = delta_H(r, c, n)
        s = (r + c + d) % n
        if s in used_s: return None
        col[r] = c
        used_c.add(c); used_s.add(s)
    return col

def validate(k, a, pt, miss=2):
    """完整验证: 零松弛(逐行行最大 delta) + 双射 + latin + type."""
    n = 4 * k
    col = build(k, a, pt)
    if col is None: return None
    if len(col) != n or len(set(col.values())) != n: return None
    T = []
    for r in range(n):
        c = col[r]
        d = delta_H(r, c, n)
        # 零松弛检查 (targets_H(k, miss) 的行最大)
        if r in (0, 5, 10):
            if d != 4: return None
        elif r in (1, 6, 11):
            if r == (1, 6, 11)[miss]:
                if d != 0 or c in (9, 10, 11, 12): return None
            else:
                if (r, c) not in {(1, 1), (6, 5)}: return None
        elif r in (4, 9, 14):
            if d != 0: return None
        elif 15 <= r < 4 * k - 21 and r % 4 == 3:
            if d != 2: return None
        elif 15 <= r < 4 * k - 21 and r % 4 == 1:
            if d != 0: return None
        else:
            if d != 0: return None
        T.append((r, c, (r + c + d) % n))
    if len(set(x[1] for x in T)) != n: return None
    if len(set(x[2] for x in T)) != n: return None
    ok, msg = is_transversal('H', n, T)
    if not ok: return None
    Tset = set(T)
    inc = sum(1 for e in SPECIALS['H'] if e in Tset)
    if inc != 2: return None
    return col

def candidates_head_tail(k, a):
    """每 mod4 段的剩余列 (head u / tail w 索引), 依赖 a."""
    res = []   # list of ('head', q, u) / ('tail', q, w)
    for j in range(4):
        t_min, t_max = (3, k - 7) if j == 3 else (4, k - 6)
        q = (j + a[j]) % 4
        eps = (j + a[j] - q) // 4          # j+a_j = 4 eps + q
        n_head = t_min + eps               # u ∈ [0, t_min+eps-1]
        n_tail = k - 1 - (t_max + eps)     # w ∈ [0, n_tail-1]
        for u in range(n_head):
            res.append(('head', q, u))
        for w in range(n_tail):
            res.append(('tail', q, w))
    return res

def solve_pt(k, a, miss=2):
    """DFS patch+tail 36 行 (符号层列索引). 返回 pt dict 或 None."""
    n = 4 * k
    cand = candidates_head_tail(k, a)
    col0 = build_partial_periodic(k, a)
    used_c = set(col0.values())
    used_s = set((r + c + delta_H(r, c, n)) % n for r, c in col0.items())
    prows = list(range(15)) + list(range(4 * k - 21, 4 * k))
    def col_of(tag):
        if tag[0] == 'head': return 4 * tag[2] + tag[1]
        return 4 * k - 4 * (1 + tag[2]) + tag[1]
    allow = {}
    for r in prows:
        cc = []
        for tag in cand:
            c = col_of(tag)
            if c in used_c: continue
            d = delta_H(r, c, n)
            if r in (0, 5, 10):
                if d != 4: continue
            elif r in (1, 6, 11):
                if r == (1, 6, 11)[miss]:
                    if d != 0 or c in (9, 10, 11, 12): continue
                else:
                    if (r, c) not in {(1, 1), (6, 5)}: continue
            elif r in (4, 9, 14):
                if d != 0: continue
            else:
                if d != 0: continue
            s = (r + c + d) % n
            if s in used_s: continue
            cc.append(tag)
        allow[r] = cc
    order = sorted(prows, key=lambda r: len(allow[r]))
    pt = {}
    budget = [200000]
    def dfs(i):
        if i == len(order): return True
        if budget[0] <= 0: return False
        r = order[i]
        for tag in allow[r]:
            budget[0] -= 1
            if budget[0] <= 0: return False
            c = col_of(tag)
            d = delta_H(r, c, n)
            s = (r + c + d) % n
            if c in used_c or s in used_s: continue
            pt[r] = tag; used_c.add(c); used_s.add(s)
            if dfs(i + 1): return True
            del pt[r]; used_c.discard(c); used_s.discard(s)
        return False
    return pt if dfs(0) else None

def build_partial_periodic(k, a):
    n = 4 * k
    col = {}
    for r in range(15, 4 * k - 21):
        c = r + a[r % 4]
        col[r] = c
    return col

def mod_ok(a):
    cols = set((j + a[j]) % 4 for j in range(4))
    syms = set((2 * j + (a[3] + 2 if j == 3 else a[j])) % 8 for j in range(4))
    # j=3: s = 2r + a3 + 2, 2r = 8t+6 → s ≡ 6 + a3 + 2 = a3 + 8 ≡ a3 (mod 8)
    return len(cols) == 4 and len(syms) == 4 and all(-13 <= x <= 7 for x in a)

if __name__ == '__main__':
    import time
    t0 = time.time()
    winners = []
    tested = 0
    for a in itertools.product(range(-13, 8, 1), repeat=4):
        if not mod_ok(a): continue
        tested += 1
        if tested % 100 == 0:
            print(f'... {tested} combos tested ({time.time()-t0:.0f}s)', flush=True)
        # k=32 (偶, 周期区非空, wrap 深度大) 与 k=33 (奇) 先探
        pt = None
        ok_ks = []
        for k in (32, 33):
            pt = solve_pt(k, a)
            if pt is None: break
            if validate(k, a, pt) is None: break
            ok_ks.append(k)
        if len(ok_ks) == 2:
            # 用 k=32 的表验证一批 k
            pt32 = pt
            good = True
            for k in (12, 20, 40, 41, 50, 64, 65, 66, 100):
                if validate(k, a, pt32) is None: good = False; break
            if good:
                winners.append((a, pt32))
                print(f'WINNER a={a} ({time.time()-t0:.0f}s)', flush=True)
    print(f'tested {tested} combos, winners: {len(winners)}', flush=True)
