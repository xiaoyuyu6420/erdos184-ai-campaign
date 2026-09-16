"""fix_frontier.py — 补齐 G_18006 / G_20006 两个前沿缺口 (第三棒 m1 SEARCH FAILED).

策略: 证书引理只要求任意三条 transversal 三交集为空, type 无关.
故对每个 n 用多模式 (G3 / G2 / sigma) × 多种子收集 transversal,
每条过独立三重验证 (is_transversal), 再枚举三元组找空交集.
找到的 transversal 以列向量存盘 (可复算: symbol 由 latpack 重算).
"""
import sys, time, json, random, itertools
sys.path.insert(0, '/Users/munich/Desktop/数学/front_tlat')
from hc3 import ShorHC
from mc import targets_G3, targets_G2, targets_G_sigma
from latpack import is_transversal, symbol as sym

def search_T(fam, n, tg, seed, budget):
    rng = random.Random(seed)
    hc = ShorHC(fam, n, tg, rng=rng)
    P = hc.run(max_restarts=10, budget=budget)
    if P is None:
        return None
    T = [(r, P[r], sym(fam, r, P[r], n)) for r in range(n)]
    ok, msg = is_transversal(fam, n, T)
    if not ok:
        print(f'  [REJECT] seed={seed} {msg}', flush=True)
        return None
    return P

def collect(n, want, budget, seed_base):
    k = (n - 2) // 4
    # m0 优先 (实测最稳), 模式索引进 seed 防同轮相关
    modes = [('G3', 0), ('G3', 0), ('G3', 0), ('G3', 1), ('G3', 2), ('G2', 0), ('SIG', None)]
    found = []
    round_ = 0
    while len(found) < want and round_ < 3:
        for mi, (mname, miss) in enumerate(modes):
            if len(found) >= want:
                break
            if mname == 'G3':
                tg = targets_G3(k, miss)
            elif mname == 'G2':
                tg = targets_G2(k, miss)
            else:
                tg = targets_G_sigma(k)
            seed = seed_base + 7919 * round_ + 31 * len(found) + 101 * mi
            t0 = time.time()
            P = search_T('G', n, tg, seed, budget)
            dt = time.time() - t0
            tag = f'G_{n} {mname}' + (f'/m{miss}' if miss is not None else '') + f' seed={seed}'
            if P is None:
                print(f'  {tag}: failed ({dt:.0f}s)', flush=True)
            else:
                print(f'  {tag}: OK ({dt:.0f}s)', flush=True)
                found.append(P)
        round_ += 1
    return found

def triple_empty(n, Ps):
    """枚举三元组, 返回空交集三元组的下标或 None."""
    sets = [set((r, P[r], sym('G', r, P[r], n)) for r in range(n)) for P in Ps]
    for i, j, l in itertools.combinations(range(len(Ps)), 3):
        if not (sets[i] & sets[j] & sets[l]):
            return (i, j, l)
    return None

def main():
    ns = [int(x) for x in sys.argv[1:]] or [18006, 20006]
    budget = 300.0
    for n in ns:
        print(f'=== G_{n} frontier fix start ===', flush=True)
        t0 = time.time()
        store = f'/Users/munich/Desktop/数学/front_tlat/frontier_G{n}_cols.jsonl'
        Ps = []
        import os
        if os.path.exists(store):   # 断点续传
            for line in open(store):
                line = line.strip()
                if line:
                    Ps.append(json.loads(line)['P'])
            print(f'  resumed {len(Ps)} from store', flush=True)
        while len(Ps) < 5:
            k = (n - 2) // 4
            mnames = [('G3', 0), ('G3', 0), ('SIG', None), ('G3', 0), ('SIG', None),
                      ('G3', 1), ('G3', 2), ('G2', 0)]
            mi = len(Ps) % len(mnames)
            mname, miss = mnames[mi]
            if mname == 'G3':
                tg = targets_G3(k, miss)
            elif mname == 'G2':
                tg = targets_G2(k, miss)
            else:
                tg = targets_G_sigma(k)
            seed = 880000000 + n * 1000 + 7919 * len(Ps) + 57 * mi
            P = search_T('G', n, tg, seed, budget)
            tag = f'G_{n} {mname}' + (f'/m{miss}' if miss is not None else '') + f' seed={seed}'
            if P is None:
                print(f'  {tag}: failed', flush=True)
                seed += 1
                P = search_T('G', n, tg, seed, budget)
            if P is not None:
                print(f'  {tag}: OK #{len(Ps)+1}', flush=True)
                Ps.append(P)
                with open(store, 'a') as f:
                    f.write(json.dumps({'P': P}) + '\n')
        trip = triple_empty(n, Ps)
        if trip is None and len(Ps) >= 3:
            trip = triple_empty(n, Ps)   # 便宜, 再保险
        if trip is not None:
            json.dump({'n': n, 'triples': trip, 'cols': Ps},
                      open(f'/Users/munich/Desktop/数学/front_tlat/frontier_G{n}.json', 'w'))
            print(f'G_{n}: PASS triple={trip} |T1∩T2∩T3|=0 — certificate saved ({time.time()-t0:.0f}s)', flush=True)
        else:
            print(f'G_{n}: no empty triple among {len(Ps)} — 需更多条 ({time.time()-t0:.0f}s)', flush=True)
            while trip is None and len(Ps) < 9:
                k = (n - 2) // 4
                mname, miss = ('SIG', None) if len(Ps) % 2 else ('G3', 0)
                tg = targets_G_sigma(k) if mname == 'SIG' else targets_G3(k, miss)
                seed = 990000000 + n * 1000 + 137 * len(Ps)
                P = search_T('G', n, tg, seed, budget)
                if P is not None:
                    print(f'  extra {mname} seed={seed}: OK #{len(Ps)+1}', flush=True)
                    Ps.append(P)
                    with open(store, 'a') as f:
                        f.write(json.dumps({'P': P}) + '\n')
                    trip = triple_empty(n, Ps)
            if trip is not None:
                json.dump({'n': n, 'triples': trip, 'cols': Ps},
                          open(f'/Users/munich/Desktop/数学/front_tlat/frontier_G{n}.json', 'w'))
                print(f'G_{n}: PASS triple={trip} (extended)', flush=True)
            else:
                print(f'G_{n}: STILL NO EMPTY TRIPLE among {len(Ps)}', flush=True)
    print('FRONTIER FIX COMPLETE', flush=True)

if __name__ == '__main__':
    main()
