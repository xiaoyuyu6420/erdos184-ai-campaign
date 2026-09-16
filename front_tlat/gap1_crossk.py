"""gap1_crossk.py — 用 k=32 winner 的常数模式 (a, ap, rho, E, h) 跨 k 验证.
T1_j = k//2 + h_j 不变; 周期区重算; 边界 34 行重新 DFS; 全部独立验证.
"""
import sys, json, time
sys.path.insert(0, '/Users/munich/Desktop/数学/front_tlat')
sys.setrecursionlimit(100000)
import gap1_archE as G

def main():
    w = json.load(open('/Users/munich/Desktop/数学/front_tlat/gap1_H128.json'))
    a, ap, rho, E = tuple(w['a']), tuple(w['ap']), tuple(w['rho']), tuple(w['E'])
    h = [t1 - 32 // 2 for t1 in w['T1']]
    print(f"pattern: a={a} ap={ap} rho={rho} E={E} h={h}", flush=True)
    for k in [33, 40, 41, 50, 64, 65, 100, 101]:
        n = 4 * k
        T1 = [k // 2 + hj for hj in h]
        t0 = time.time()
        res = G.build_period(k, a, ap, T1)
        if res is None:
            print(f'k={k}: period build FAIL', flush=True)
            continue
        uc, us = res
        if len(uc) != 4 * k - 36 or 1 in uc or 5 in uc or 5 in us or 14 in us:
            print(f'k={k}: set check FAIL (|uc|={len(uc)})', flush=True)
            continue
        col = G.boundary_solve(k, uc, us, node_cap=400000)
        if col is None:
            print(f'k={k}: boundary FAIL ({time.time()-t0:.0f}s)', flush=True)
            continue
        full = dict(col); full[1] = 1; full[6] = 5
        ok, msg = G.full_verify(k, full)
        print(f'k={k}: {"VERIFIED" if ok else "VERIFY FAIL: " + msg} ({time.time()-t0:.0f}s)', flush=True)
        if ok:
            json.dump({'k': k, 'a': list(a), 'ap': list(ap), 'rho': list(rho),
                       'E': list(E), 'T1': T1, 'col': full},
                      open(f'/Users/munich/Desktop/数学/front_tlat/gap1_H{4*k}.json', 'w'))

if __name__ == '__main__':
    main()
