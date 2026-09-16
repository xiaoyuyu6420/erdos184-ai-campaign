"""mc.py — min-conflicts 搜索器（增量 O(1) 计数, 支持行级 δ-目标约束）
用于在 H_n / G_n 的 type-类内找 transversal。状态 = 行->列; 目标 = 符号两两不同。
"""
import sys, random
sys.path.insert(0, '/Users/munich/Desktop/数学/front_tlat')
from latpack import symbol, SPECIALS, FAMILIES

def solve_mc(fam, n, targets, rng, max_steps=None, seed_tries=60):
    """targets: row -> set(允许 delta)。返回 col 列表或 None。
    min-conflicts: 重复符号的两行交换列（保持约束）, 增量计数。"""
    d = FAMILIES[fam][0]
    if max_steps is None: max_steps = 300 * n
    # 每行允许列（按 delta 目标过滤）; 行按约束强度排序初始化
    allow = {}
    for r in range(n):
        t = targets[r]
        cols = [c for c in range(n) if d(r, c, n) in t]
        allow[r] = cols
        if not cols: return None
    symtab = [[(r + c + d(r, c, n)) % n for c in allow[r]] for r in range(n)]

    for attempt in range(seed_tries):
        cur = [-1] * n
        used_c = [False] * n
        cnt = [0] * n            # 符号出现次数
        rows_of = {}             # symbol -> list of rows (动态)
        # 初始化: 约束最强的行先放（随机可行列）
        order = sorted(range(n), key=lambda r: (len(allow[r]), rng.random()))
        conflict = True
        for r in order:
            # 找一个不撞列的列; 优先不撞符号
            best = None
            cand = allow[r]
            idx = rng.randrange(len(cand))
            for off in range(len(cand)):
                c = cand[(idx + off) % len(cand)]
                if not used_c[c]:
                    best = c
                    if cnt[symtab[r][allow[r].index(c)]] == 0:
                        break
            if best is None: break
            ii = allow[r].index(best)
            s = symtab[r][ii]
            cur[r] = best; used_c[best] = True
            cnt[s] += 1
            rows_of.setdefault(s, []).append(r)
        if any(v == -1 for v in cur):
            continue
        # min-conflicts 主循环
        for step in range(max_steps):
            bad = [s for s, rr in rows_of.items() if len(rr) >= 2]
            if not bad:
                return cur
            s = rng.choice(bad)
            rr = rows_of[s]
            i1, i2 = rng.sample(range(len(rr)), 2) if len(rr) >= 2 else (0, 0)
            r1, r2 = rr[i1], rr[i2]
            c1, c2 = cur[r1], cur[r2]
            # 交换后符号
            s1n = symtab[r1][allow[r1].index(c2)]
            s2n = symtab[r2][allow[r2].index(c1)]
            # 评分: 交换前后冲突变化
            before = (cnt[s] - 1) + (cnt[s1n] if s1n != s else cnt[s]-1) + (cnt[s2n] if s2n != s else cnt[s]-1)
            # 简化: 直接算交换后 bad 增量
            def delta_cost():
                cost = 0
                cnt[s] -= 2
                cnt[s1n] += 1; cnt[s2n] += 1
                for ss in {s, s1n, s2n}:
                    if cnt[ss] >= 2: cost += cnt[ss] - 1
                cnt[s1n] -= 1; cnt[s2n] -= 1
                cnt[s] += 2
                return cost
            if delta_cost() <= 1 or rng.random() < 0.02:
                # 执行交换
                cur[r1], cur[r2] = c2, c1
                rows_of[s].remove(r1); rows_of[s].remove(r2)
                if not rows_of[s]: del rows_of[s]
                cnt[s] -= 2
                for sn in (s1n, s2n):
                    cnt[sn] += 1
                    rows_of.setdefault(sn, []).append(r1 if sn == s1n else r2)
        # fallthrough: 重试
    return None

def targets_H(k, miss):
    n = 4 * k
    t = {}
    for r in range(n):
        if r in (0, 5, 10): t[r] = {4}
        elif r in (1, 6, 11):
            t[r] = {0} if r == (1, 6, 11)[miss] else {3}
        elif r in (4, 9, 14): t[r] = {0}
        elif 15 <= r < 4 * k - 21 and r % 4 == 3: t[r] = {2}
        elif 15 <= r < 4 * k - 21 and r % 4 == 1: t[r] = {0}
        else: t[r] = {0}
    return t

def targets_G(k, miss, deficit):
    n = 4 * k + 2
    t = {}
    for r in range(n):
        if r in (0, 5, 10): t[r] = {4}
        elif r in (1, 6, 11):
            t[r] = {0} if r == (1, 6, 11)[miss] else {3}
        elif r in (4, 9, 14): t[r] = {0}
        elif r == 15: t[r] = {2}
        elif r == 16: t[r] = {1}
        elif r == 17: t[r] = {0}
        elif 18 <= r < 3 * k - 9 and r % 3 == 0: t[r] = {2}
        else: t[r] = {0}
    for (r, vals) in deficit: t[r] = set(vals)
    assert sum(max(v) for v in t.values()) == 2 * k + 1
    return t

def targets_G_sigma(k):
    """G_n 三特殊型 σ: 含全部三个特殊格, 行 15→Δ0, 行16→Δ0, 行17→Δ−2.
    Σ = 2k+6 − 5 = 2k+1 ✓; 构造性避开 (16,12,29) 与 (15,12,28)."""
    n = 4 * k + 2
    t = {}
    for r in range(n):
        if r in (0, 5, 10): t[r] = {4}
        elif r in (1, 6, 11): t[r] = {3}
        elif r in (4, 9, 14): t[r] = {0}
        elif r == 15: t[r] = {0}
        elif r == 16: t[r] = {0}
        elif r == 17: t[r] = {-2}
        elif 18 <= r < 3 * k - 9 and r % 3 == 0: t[r] = {2}
        else: t[r] = {0}
    return t

def targets_G2(k, miss):
    """模式 G (2026-09-15 攻击棒): 松弛型 targets, 构造性排除全部 δ=1 格.
    行 15 → {0,2} (避开 (15,12),(15,13) 的 δ=1); 行 16 → {0} (避开 (16,12,29));
    行 17 与周期区 r≡2 (mod 3) 行 → {0,−2} (松弛). Σ 上界 2k+2, Δ-引理强制实际 Σ=2k+1.
    所有单值行合法格 ≥ k−2 ≥ 3 (k≥9), 无鸽笼."""
    n = 4 * k + 2
    t = {}
    for r in range(n):
        if r in (0, 5, 10): t[r] = {4}
        elif r in (1, 6, 11): t[r] = {0} if r == (1, 6, 11)[miss] else {3}
        elif r in (4, 9, 14): t[r] = {0}
        elif r == 15: t[r] = {0, 2}
        elif r == 16: t[r] = {0}
        elif r == 17: t[r] = {0, -2}
        elif 18 <= r < 3 * k - 9 and r % 3 == 0: t[r] = {2}
        elif 18 <= r < 3 * k - 9 and r % 3 == 2: t[r] = {0, -2}
        else: t[r] = {0}
    return t

def targets_G3(k, miss):
    """模式 H (2026-09-15 攻击棒): 全单值零松弛, Σ = 2k+1 精确.
    miss 行 → {−1} (恰 3 格, 各条 miss 行互异故无鸽笼); 行 16 → {0} (排除 (16,12,29));
    行 15 → {2} (排除 (15,12,28),(15,13,29)); 其余同基础模式. 三个 δ=1 格全表排除."""
    n = 4 * k + 2
    t = {}
    for r in range(n):
        if r in (0, 5, 10): t[r] = {4}
        elif r in (1, 6, 11):
            t[r] = {-1} if r == (1, 6, 11)[miss] else {3}
        elif r in (4, 9, 14): t[r] = {0}
        elif r == 15: t[r] = {2}
        elif r == 16: t[r] = {0}
        elif r == 17: t[r] = {0}
        elif 18 <= r < 3 * k - 9 and r % 3 == 0: t[r] = {2}
        else: t[r] = {0}
    assert sum(max(v) for v in t.values()) == 2 * k + 1, 'budget'
    return t
