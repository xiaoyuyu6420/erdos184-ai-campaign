"""attack_construct.py — GAP-1 主攻: H_n (miss=2) type-transversal 的闭式骨架构造.

骨架 (周期区行 15 <= r < 4k-22, 全部「行最大 delta 格」= T2 零松弛):
  r=4t+3: c = r + a3,  s = 2r + a3 + 2   (需 c 偶: a3 奇)
  r=4t+1: c = r + a1,  s = 2r + a1       (需 c 奇: a1 偶)
  r=4t  : c = r + a0,  s = 2r + a0       (自由)
  r=4t+2: c = r + a2,  s = 2r + a2       (自由)
要求: 列 mod 4 类互异、符号 mod 8 类互异、区间覆盖恰好。
patch(0..14) + tail(4k-21..4k-1) 共 36 行: 列取 小端常数 const_c 或 4k-K 常数,
符号随之 (对一般 k 一致, 由符号化回溯求解)。
"""
import sys, itertools
sys.path.insert(0, '/Users/munich/Desktop/数学/front_tlat')
from latpack import delta_H, symbol as sym, SPECIALS, is_transversal

def build_periodic(k, a):
    """周期区骨架. a = (a0, a1, a2, a3) 行 mod 4 = 0,1,2,3 的列偏移. 返回 dict r->c 或 None."""
    n = 4 * k
    col = {}
    for r in range(15, 4 * k - 21):
        j = r % 4
        c = r + a[j]
        if not (0 <= c < n):
            return None
        col[r] = c
    return col

def check_periodic(k, a):
    """检查周期区骨架: 行约束 (delta=行最大) + 列双射 + 符号双射."""
    n = 4 * k
    col = build_periodic(k, a)
    if col is None: return None
    used_c, used_s = set(), set()
    for r, c in col.items():
        d = delta_H(r, c, n)
        j = r % 4
        # 零松弛检查: 行最大 delta
        if j == 3 and d != 2: return None
        if j == 1 and d != 0: return None   # 行最大 0 (奇列)
        if c in used_c: return None
        used_c.add(c)
        s = (r + c + d) % n
        if s in used_s: return None
        used_s.add(s)
    return col

def solve_patch_tail(k, a, miss=2, keep_small=16):
    """给定周期区偏移, 符号化回溯 patch+tail 36 行.
    候选列: 小端 [0, keep_small) 与大端 [4k-36-?, 4k) 未被周期区占用的.
    返回 dict r->c 或 None."""
    n = 4 * k
    colp = check_periodic(k, a)
    if colp is None: return None
    used_c = set(colp.keys()) and set(colp.values())
    used_s = set((r + c + delta_H(r, c, n)) % n for r, c in colp.items())
    prows = list(range(15)) + list(range(4 * k - 21, 4 * k))
    cand = [c for c in range(n) if c not in used_c]
    sp = SPECIALS['H']
    allow = {}
    for r in prows:
        cc = []
        for c in cand:
            d = delta_H(r, c, n)
            ok = True
            # 零松弛: 行最大 delta 检查 (同 targets_H(k, miss))
            if r in (0, 5, 10):
                if d != 4: ok = False
            elif r in (1, 6, 11):
                if r == (1, 6, 11)[miss]:
                    if d != 0 or c in (9, 10, 11, 12): ok = False
                else:
                    if (r, c) not in {(1, 1), (6, 5)}: ok = False
            elif r in (4, 9, 14):
                if d != 0: ok = False
            else:
                if d != 0: ok = False
            if ok:
                s = (r + c + d) % n
                if s not in used_s: cc.append(c)
        allow[r] = cc
    order = sorted(prows, key=lambda r: len(allow[r]))
    sol = {}
    used_c2, used_s2 = set(used_c), set(used_s)
    def dfs(i):
        if i == len(order): return True
        r = order[i]
        for c in allow[r]:
            d = delta_H(r, c, n)
            s = (r + c + d) % n
            if c in used_c2 or s in used_s2: continue
            sol[r] = c; used_c2.add(c); used_s2.add(s)
            if dfs(i + 1): return True
            del sol[r]; used_c2.discard(c); used_s2.discard(s)
        return False
    return sol if dfs(0) else None

def full_check(k, a, miss=2):
    n = 4 * k
    colp = check_periodic(k, a)
    if colp is None: return None, 'periodic failed'
    pt = solve_patch_tail(k, a, miss)
    if pt is None: return None, 'patch/tail failed'
    col = dict(colp); col.update(pt)
    if len(set(col.values())) != n: return None, 'col not bij'
    T = [(r, col[r], sym('H', r, col[r], n)) for r in range(n)]
    ok, msg = is_transversal('H', n, T)
    if not ok: return None, f'invalid: {msg}'
    Tset = set(T)
    inc = [s for s in SPECIALS['H'] if s in Tset]
    if len(inc) != 2: return None, f'specials inc={len(inc)}'
    return col, 'OK'

if __name__ == '__main__':
    # 参数扫描: a0..a3 小偏移
    winners = []
    for a in itertools.product((-2, 0, 2, 4, 6), repeat=4):
        a = tuple(x if j != 3 else x + (1 if x % 2 == 0 else 0) for j, x in enumerate(a))
        # a3 必须奇, a1 必须偶
        if a[3] % 2 == 0: continue
        if a[1] % 2 != 0: continue
        good_ks = []
        for k in (10, 11, 12, 13):
            col, msg = full_check(k, a)
            if col is None: break
            good_ks.append(k)
        if len(good_ks) == 4:
            winners.append(a)
            print('WINNER a =', a, flush=True)
    print('total winners:', len(winners))
