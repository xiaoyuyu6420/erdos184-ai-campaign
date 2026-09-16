"""frontier_fix_r3.py — 第三棒的 G_18006 有界并行补证 (与第四棒的 fix_frontier.py 互不干扰:
独立 seed 空间 + 独立输出文件 frontier_G18006_r3.json).
只跑实测能出活的模式 (G3/m0 与 SIG), 每 attempt 预算 200s, 每条成功即存.
收满 6 条即枚举三元组; 有空三集 → verdict PASS 并写 verdict 行.
"""
import sys, time, json, random, itertools
sys.path.insert(0, '/Users/munich/Desktop/数学/front_tlat')
from hc3 import ShorHC
from mc import targets_G3, targets_G_sigma
from latpack import is_transversal, symbol as sym

N = 18006
K = (N - 2) // 4
BUDGET = 200.0
WANT = 6
SEED0 = 313370000  # 独立 seed 空间

def search_T(tg, seed):
    rng = random.Random(seed)
    hc = ShorHC('G', N, tg, rng=rng)
    P = hc.run(max_restarts=10, budget=BUDGET)
    if P is None: return None
    T = [(r, P[r], sym('G', r, P[r], N)) for r in range(N)]
    ok, msg = is_transversal('G', N, T)
    return P if ok else None

def main():
    found = []
    t0 = time.time()
    attempt = 0
    while len(found) < WANT and time.time() - t0 < 2400:  # 硬上限 40 分钟
        mode = ('m0', 'SIG')[attempt % 2]
        tg = targets_G_sigma(K) if mode == 'SIG' else targets_G3(K, 0)
        seed = SEED0 + 7919 * attempt
        ta = time.time()
        P = search_T(tg, seed)
        dt = time.time() - ta
        tag = f'G_18006 r3 {mode} seed={seed}'
        if P is None:
            print(f'  {tag}: failed ({dt:.0f}s)', flush=True)
        else:
            print(f'  {tag}: OK ({dt:.0f}s)  [{len(found)+1}/{WANT}]', flush=True)
            found.append(P)
            json.dump({'n': N, 'modes': ['G3/m0' if i % 2 == 0 else 'SIG' for i in range(len(found))],
                       'cols': found}, open('/Users/munich/Desktop/数学/front_tlat/frontier_G18006_r3.json', 'w'))
        attempt += 1
    print(f'G_18006 r3: collected {len(found)} ({time.time()-t0:.0f}s)', flush=True)
    if len(found) >= 3:
        sets = [set((r, P[r], sym('G', r, P[r], N)) for r in range(N)) for P in found]
        for i, j, l in itertools.combinations(range(len(sets)), 3):
            if not (sets[i] & sets[j] & sets[l]):
                print(f'VERDICT: G_18006 PASS triple=({i},{j},{l}) |T1∩T2∩T3|=0 — cert in frontier_G18006_r3.json', flush=True)
                return
        print(f'VERDICT: no empty triple among {len(found)} (需要更多/异构证书)', flush=True)

if __name__ == '__main__':
    main()
