"""mc2.py — min-conflicts 搜索器 v2（列隶属用集合, 增量计数正确）"""
import sys, random
sys.path.insert(0, '/Users/munich/Desktop/数学/front_tlat')
from latpack import symbol, SPECIALS, FAMILIES

def solve_mc(fam, n, targets, rng, max_steps=None, seed_tries=40):
    d = FAMILIES[fam][0]
    if max_steps is None: max_steps = 300 * n
    allow = {}
    for r in range(n):
        t = targets[r]
        cols = [c for c in range(n) if d(r, c, n) in t]
        if not cols: return None
        allow[r] = cols
    # 预计算: sym_of[r][c] 及 col->idx
    symat = {}
    for r in range(n):
        symat[r] = {c: (r + c + d(r, c, n)) % n for c in allow[r]}

    for attempt in range(seed_tries):
        cur = [-1] * n
        used_c = set()
        cnt = [0] * n
        rows_of = {}
        order = sorted(range(n), key=lambda r: (len(allow[r]), rng.random()))
        ok_init = True
        for r in order:
            cand = allow[r]
            idx = rng.randrange(len(cand))
            best = None
            for off in range(len(cand)):
                c = cand[(idx + off) % len(cand)]
                if c in used_c: continue
                s = symat[r][c]
                if best is None: best = c
                if cnt[s] == 0:
                    best = c; break
            if best is None: ok_init = False; break
            s = symat[r][best]
            cur[r] = best; used_c.add(best)
            cnt[s] += 1
            rows_of.setdefault(s, []).append(r)
        if not ok_init: continue

        for step in range(max_steps):
            bad = [s for s, rr in rows_of.items() if len(rr) >= 2]
            if not bad:
                return cur
            s = rng.choice(bad)
            rr = rows_of[s]
            r1, r2 = rng.sample(rr, 2)
            c1, c2 = cur[r1], cur[r2]
            if c2 not in symat[r1] or c1 not in symat[r2]:
                continue
            s1n = symat[r1][c2]
            s2n = symat[r2][c1]
            # 交换后各符号计数
            def cost_after():
                cost = 0
                cnt[s] -= 2; cnt[s1n] += 1; cnt[s2n] += 1
                for ss in (s, s1n, s2n):
                    if cnt[ss] >= 2: cost += cnt[ss] - 1
                cnt[s1n] -= 1; cnt[s2n] -= 1; cnt[s] += 2
                return cost
            before = sum(cnt[ss] - 1 for ss in {s, s1n, s2n} if cnt[ss] >= 2)
            if cost_after() <= before or rng.random() < 0.03:
                cur[r1], cur[r2] = c2, c1
                rr.remove(r1); rr.remove(r2)
                if not rr: del rows_of[s]
                cnt[s] -= 2
                for sn, rnew in ((s1n, r1), (s2n, r2)):
                    cnt[sn] += 1
                    rows_of.setdefault(sn, []).append(rnew)
    return None
