"""shape.py — GAP-1 形状发现: 找 H_n miss=2 type-transversal 的解结构.
输出 (r -> c-r) 差分按行段/mod4 分组, 找正则模式以提炼闭式构造.
"""
import sys, random
sys.path.insert(0, '/Users/munich/Desktop/数学/front_tlat')
from hc3 import ShorHC
from mc import targets_H
from latpack import symbol as sym, SPECIALS, is_transversal

def find(k, seed):
    n = 4 * k
    tg = targets_H(k, 2)
    rng = random.Random(seed)
    hc = ShorHC('H', n, tg, rng=rng)
    P = hc.run(max_restarts=10, budget=30)
    return P

def show(k, col):
    n = 4 * k
    print(f'--- k={k} n={n} ---')
    T = [(r, col[r], sym('H', r, col[r], n)) for r in range(n)]
    ok, msg = is_transversal('H', n, T)
    print('valid:', ok, msg)
    sp = SPECIALS['H']
    print('specials included:', [s for s in sp if (s[0], s[1], s[2]) in set(T)], '(miss=2 means sp index 2 excluded)')
    # 分段打印
    def seg(r):
        if r < 15: return 'patch'
        if r < 4 * k - 21: return 'peri'
        return 'tail'
    from collections import defaultdict
    rows = defaultdict(list)
    for r in range(n):
        rows[(seg(r), r % 4)].append(col[r] - r)
    for key in sorted(rows):
        diffs = rows[key]
        # 压缩显示: 只显示 unique 值和频次
        uniq = {}
        for d in diffs: uniq[d] = uniq.get(d, 0) + 1
        top = sorted(uniq.items(), key=lambda x: -x[1])[:6]
        print(f'{key[0]:5s} r%4={key[1]}: n={len(diffs):3d} diff(c-r) top: {top}')

if __name__ == '__main__':
    for k in (10, 12, 16):
        col = find(k, seed=42)
        if col:
            show(k, col)
        else:
            print(f'k={k}: no solution found')
