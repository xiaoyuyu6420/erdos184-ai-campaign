"""solver2.py — 精确回溯求解器（在刚性目标类内找 transversal）
行按允许列数升序（MRV），位掩码维护已用列/符号。解具有确定性（列优先序），
便于跨 n 对比提取参数模式。
"""
import sys
sys.path.insert(0, '/Users/munich/Desktop/数学/front_tlat')
from latpack import symbol, SPECIALS, FAMILIES

def allowed_cols(fam, n, t):
    """t: row -> set of allowed delta values. 返回 row -> sorted list of columns."""
    d = FAMILIES[fam][0]
    out = []
    for r in range(n):
        cols = [c for c in range(n) if d(r, c, n) in t[r]]
        out.append(cols)
    return out

def solve(fam, n, t, node_budget=8_000_000, want=1):
    """返回最多 want 个解（每个是 row->col 列表）。"""
    d = FAMILIES[fam][0]
    allow = allowed_cols(fam, n, t)
    order = sorted(range(n), key=lambda r: (len(allow[r]), r))
    solutions = []
    used_c = [False] * n
    used_s = [False] * n
    cur = [-1] * n
    nodes = 0

    def sym(r, c):
        return (r + c + d(r, c, n)) % n

    def dfs(idx):
        nonlocal nodes
        if len(solutions) >= want: return
        if idx == n:
            solutions.append(list(cur)); return
        if nodes >= node_budget: return
        # MRV 动态选行: 剩余行中可行列数最少
        best_r, best_cols = -1, None
        for j in range(idx, n):
            r = order[j]
            feas = [c for c in allow[r] if not used_c[c] and not used_s[sym(r, c)]]
            if best_cols is None or len(feas) < len(best_cols):
                best_r, best_cols = r, feas
                if not feas: break
        if not best_cols: return
        # 把 best_r 提到 idx 位
        i = order.index(best_r)
        order[idx], order[i] = order[i], order[idx]
        r = best_r
        nodes += 1
        for c in best_cols:
            s = sym(r, c)
            used_c[c] = used_s[s] = True
            cur[r] = c
            dfs(idx + 1)
            used_c[c] = used_s[s] = False
            cur[r] = -1
            if len(solutions) >= want or nodes >= node_budget: break
        order[idx], order[i] = order[i], order[idx]  # 恢复

    dfs(0)
    return solutions

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
    total = sum(max(v) for v in t.values())
    assert total == 2 * k + 1, (total,)
    return t

def to_T(fam, n, cvec):
    return [(r, cvec[r], symbol(fam, r, cvec[r], n)) for r in range(n)]
