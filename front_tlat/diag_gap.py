"""diag_gap.py — 诊断 G 族 30 个缺口点的「交集 |∩|=1」: 交集到底是哪个 entry?
跑 k=9 (n=38) 与 k=66 (n=266), 多 seed 打印交集.
"""
import sys, random
sys.path.insert(0, '/Users/munich/Desktop/数学/front_tlat')
from hc3 import ShorHC
from mc import targets_G
from latpack import symbol as sym, SPECIALS, is_transversal

def search_one(fam, n, targets, seed, budget=240):
    rng = random.Random(seed)
    hc = ShorHC(fam, n, targets, rng=rng)
    P = hc.run(max_restarts=10, budget=budget)
    if P is None: return None
    T = tuple((r, P[r], sym(fam, r, P[r], n)) for r in range(n))
    ok, msg = is_transversal(fam, n, list(T))
    if not ok: return None
    return T

def diag(k, seeds=(1000*9+17, 999983+9)):
    n = 4 * k + 2
    for sd_base in seeds:
        Ts = []
        for miss in (0, 1, 2):
            tg = targets_G(k, miss, deficit=[(16, {0}), (15, {1})])
            T = None
            for sd in range(6):
                T = search_one('G', n, tg, seed=1000*k + 17*miss + sd, budget=60)
                if T: break
            if T is None:
                print(f'k={k} m{miss}: SEARCH FAILED'); return
            sp = SPECIALS['G']
            inc = sum(1 for e in sp if e in set(T))
            Ts.append(set(T))
            print(f'k={k} m{miss}: found, specials inc={inc}')
        inter = Ts[0] & Ts[1] & Ts[2]
        print(f'k={k} seed_base={sd_base}: |T1∩T2∩T3| = {len(inter)}  -> {sorted(inter)}')

if __name__ == '__main__':
    diag(9)
    diag(66)
