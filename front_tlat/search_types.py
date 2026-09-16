"""search_types.py — 在刚性约束下搜索 H_n / G_n 的 type-transversal

刚性框架（由 Δ-预算分析得出）:
  H_n (n=4k, k>=9), 2-特殊型 τ (含恰好两个特殊格): ΣΔ=2k, 条件最大和=2k → 松弛 0
    每行必须取"条件最大 Δ"格:
      rows 0,5,10: Δ=4 格 (b≡1 mod 4, b≠4a/5+1)
      两个特殊行: 特殊格 (Δ=3); 被跳过的特殊行: Δ=0 格
      rows 4,9,14: Δ=0 格 (b not≡1 mod 4)
      rows a≡3 mod 4, 15<=a<4k-21: Δ=2 格 (b even)
      rows a≡1 mod 4, 15<=a<4k-21: Δ=0 格 (b odd)
      其余行: Δ=0 格
  G_n (n=4k+2, k>=9), 2-特殊型: ΣΔ=2k+1, 条件最大和=2k+3 → 松弛 2
    条件最大格同上 G 版; 松弛 2 用指定亏缺模式实现。
"""
import sys, json, random
sys.path.insert(0, '/Users/munich/Desktop/数学/front_tlat')
from latpack import *

def H_targets(k, miss):
    """miss ∈ {0,1,2}: 跳过哪个特殊格. 返回 per-row 允许 Δ 集合."""
    n = 4 * k
    t = {}
    for r in range(n):
        if r in (0, 5, 10):
            t[r] = {4}
        elif r in (1, 6, 11):
            if r == (1, 6, 11)[miss]: t[r] = {0}
            else: t[r] = {3}
        elif r in (4, 9, 14):
            t[r] = {0}
        elif 15 <= r < 4 * k - 21 and r % 4 == 3:
            t[r] = {2}
        elif 15 <= r < 4 * k - 21 and r % 4 == 1:
            t[r] = {0}
        else:
            t[r] = {0}
    return t

def G_targets(k, miss, deficit):
    """deficit: list of (row, allowed_delta_set) 覆盖默认条件最大目标.
    默认条件最大: 同 H 结构但 G 规则; 总亏缺须恰 2."""
    n = 4 * k + 2
    t = {}
    for r in range(n):
        if r in (0, 5, 10):
            t[r] = {4}
        elif r in (1, 6, 11):
            if r == (1, 6, 11)[miss]: t[r] = {0}
            else: t[r] = {3}
        elif r in (2, 3, 7, 8, 12, 13):
            t[r] = {0}
        elif r in (4, 9, 14):
            t[r] = {0}
        elif r == 15:
            t[r] = {2}
        elif r == 16:
            t[r] = {1}
        elif r == 17:
            t[r] = {0}
        elif 18 <= r < 3 * k - 9 and r % 3 == 0:
            t[r] = {2}
        elif 18 <= r < 3 * k - 9 and r % 3 == 1:
            t[r] = {0}
        elif 18 <= r < 3 * k - 9 and r % 3 == 2:
            t[r] = {0}
        else:   # r >= 3k-9
            t[r] = {0}
    # 应用亏缺模式
    for (r, vals) in deficit:
        t[r] = set(vals)
    # 一致性检查: 目标和 = 2k+1
    total = sum(max(v) for v in t.values())
    assert total == 2 * k + 1, (total, 2 * k + 1)
    return t

def F_from_targets(fam, n, t):
    d = FAMILIES[fam][0]
    F = set()
    for r in range(n):
        for c in range(n):
            if d(r, c, n) not in t[r]:
                F.add((r, c, symbol(fam, r, c, n)))
    return F

def search_one(fam, n, t, seed=0, budget=25):
    d = FAMILIES[fam][0]
    R = set()
    for (r, c, s) in SPECIALS[fam]:
        if d(r, c, n) not in t[r]:
            R.add((r, c, s))
    F = F_from_targets(fam, n, t)
    hc = HC(fam, n, R=R, F=F, rng=random.Random(seed))
    P = hc.run(max_restarts=60, budget=budget)
    if P is None: return None
    T = P_to_T(fam, n, P)
    ok, msg = is_transversal(fam, n, T)
    assert ok, msg
    return T

def verify_type(fam, n, T, miss):
    sp = SPECIALS[fam]
    cnt = sum(1 for e in sp if e in set(T))
    assert cnt == 2 and sp[miss] not in set(T), (fam, n, miss, cnt)
    return True

if __name__ == '__main__':
    out = {}
    print("==== H_n: 三种 2-特殊型 (k=9..14) ====")
    for k in range(9, 15):
        n = 4 * k
        for miss in (0, 1, 2):
            t = H_targets(k, miss)
            best = None
            for seed in range(8):
                T = search_one('H', n, t, seed=seed)
                if T: break
            if T is None:
                print(f"  H_{n} τ{miss+1}: SEARCH FAILED")
                continue
            verify_type('H', n, T, miss)
            out[f'H_{n}_tau{miss+1}'] = T
            print(f"  H_{n} τ{miss+1}: found (seed={seed})")
    print("==== G_n: 三种 2-特殊型, 亏缺模式 B (k=9..14) ====")
    # 模式 B: 行16 → {0} (避开 (16,12,29)), 行15 → {1} (取 (15,12)/(15,13))
    for k in range(9, 15):
        n = 4 * k + 2
        for miss in (0, 1, 2):
            t = G_targets(k, miss, deficit=[(16, {0}), (15, {1})])
            T = None
            for seed in range(8):
                T = search_one('G', n, t, seed=seed)
                if T: break
            if T is None:
                print(f"  G_{n} τ{miss+1} patB: SEARCH FAILED")
                continue
            verify_type('G', n, T, miss)
            assert (16, 12, 29) not in set(T)
            out[f'G_{n}_tau{miss+1}_B'] = T
            print(f"  G_{n} τ{miss+1} patB: found (seed={seed})")
    with open('/Users/munich/Desktop/数学/front_tlat/solutions_raw.json', 'w') as f:
        json.dump(out, f)
    print("saved solutions_raw.json:", len(out), "transversals")
