"""campaign.py — Conjecture 3 独立验证战役
范围: H 族 n=4k (k=9..500), G 族 n=4k+2 (k=9..500) 全类型;
     越过论文前沿 (n>10000) 的采样点至 n≈20006。
每个 n: 三条 type-transversal (各缺一个特殊格), 独立三重验证, 检查公共交集为空。
断点续跑: campaign_state.json。
"""
import sys, time, random, json, os, subprocess
sys.setrecursionlimit(300000)
sys.path.insert(0, '/Users/munich/Desktop/数学/front_tlat')
from hc3 import ShorHC
from mc import targets_H, targets_G, targets_G3
from latpack import is_transversal, symbol as sym, SPECIALS

STATE_F = '/Users/munich/Desktop/数学/front_tlat/campaign_state.json'
LOG_F = '/Users/munich/Desktop/数学/front_tlat/campaign_log.txt'

def log(msg):
    with open(LOG_F, 'a') as f:
        f.write(msg + '\n')

def swap_used_gb():
    out = subprocess.run(['sysctl', 'vm.swapusage'], capture_output=True, text=True).stdout
    toks = out.replace('=', ' ').split()
    for i, tok in enumerate(toks):
        if tok == 'used':
            return float(toks[i + 1].rstrip('Mm')) / 1024.0   # MB -> GB
    return -1

def wait_swap_ok(threshold=12.0, max_wait_s=3600):
    """swap used > threshold GB 时等待 (资源纪律: >12.5GB 降档)."""
    waited = 0
    while swap_used_gb() > threshold and waited < max_wait_s:
        if waited % 600 == 0:
            log(f'[swap guard] used={swap_used_gb()}GB — 等待中 ({waited}s)')
        time.sleep(30)
        waited += 30
    return swap_used_gb() <= threshold

def load_state():
    if os.path.exists(STATE_F):
        return json.load(open(STATE_F))
    return {'done': []}

def save_state(st):
    json.dump(st, open(STATE_F, 'w'))

def search_one(fam, n, targets, seed, budget=240):
    rng = random.Random(seed)
    hc = ShorHC(fam, n, targets, rng=rng)
    P = hc.run(max_restarts=10, budget=budget)
    if P is None: return None
    T = tuple((r, P[r], sym(fam, r, P[r], n)) for r in range(n))
    ok, msg = is_transversal(fam, n, list(T))
    if not ok: return None
    return T

def do_family(fam, ks, budget_small=60, budget_big=240):
    st = load_state()
    for k in ks:
        n = 4 * k if fam == 'H' else 4 * k + 2
        key = f'{fam}_{n}'
        if key in st['done']:
            continue
        if n > 3000:
            if not wait_swap_ok():
                log(f'{key}: swap 等待超时, 中止战役 (可续跑)')
                return
        t0 = time.time()
        Ts = []
        ok_all = True
        for miss in (0, 1, 2):
            if fam == 'H':
                tg = targets_H(k, miss)
            else:
                # 模式 H (targets_G3): 全单值零松弛 Σ=2k+1, 三个 δ=1 格构造性排除
                tg = targets_G3(k, miss)
            T = None
            for sd in range(6):
                T = search_one(fam, n, tg, seed=1000 * k + 17 * miss + sd,
                               budget=budget_big if n > 3000 else budget_small)
                if T: break
            if T is None:
                log(f'{key} m{miss+1}: SEARCH FAILED')
                ok_all = False
                break
            spset = SPECIALS[fam]
            inc = sum(1 for e in spset if e in T)
            if inc != 2 or spset[miss] in set(T):
                log(f'{key} m{miss+1}: TYPE CHECK FAILED inc={inc}')
                ok_all = False
                break
            # 逐行 delta 合法性 (targets 未污染 — Phase 2 无检查交换的防御)
            from latpack import FAMILIES
            dfun = FAMILIES[fam][0]
            viol = [r for (r, c, s) in T if dfun(r, c, n) not in tg[r]]
            if viol:
                log(f'{key} m{miss+1}: TARGETS VIOLATED rows={viol[:5]}')
                ok_all = False
                break
            Ts.append(set(T))
        if not ok_all:
            continue
        inter = Ts[0] & Ts[1] & Ts[2]
        tag = ''
        if fam == 'G':
            if (16, 12, 29) in inter:
                log(f'{key}: 交集含 (16,12,29) — 异常')
                continue
        if inter:
            # 换种子重跑一次三类以打破交集
            Ts2 = []
            for miss in (0, 1, 2):
                tg = targets_H(k, miss) if fam == 'H' else targets_G3(k, miss)
                T = search_one(fam, n, tg, seed=999983 + k + miss, budget=budget_big)
                if T is None:
                    log(f'{key}: 重跑失败')
                    ok_all = False
                    break
                Ts2.append(set(T))
            if not ok_all: continue
            inter = Ts2[0] & Ts2[1] & Ts2[2]
            tag = '(重跑)'
        dt = time.time() - t0
        if not inter:
            log(f'{key}: PASS |T1∩T2∩T3|=0 {tag} ({dt:.1f}s)')
            st['done'].append(key)
            save_state(st)
        else:
            log(f'{key}: 交集非空 |∩|={len(inter)} {tag} — 需人工处理 ({dt:.1f}s)')
    print('family done:', fam, flush=True)

if __name__ == '__main__':
    swap = subprocess.run(['sysctl', 'vm.swapusage'], capture_output=True, text=True).stdout.strip()
    log(f'=== campaign start {time.strftime("%F %T")} | {swap} ===')
    # 全覆盖范围 k=9..500 (n 到 2000/2002)
    do_family('H', range(9, 501))
    do_family('G', range(9, 501))
    # 越过论文前沿的采样
    do_family('H', [2501, 3000, 3501, 4000, 4501, 5001])     # n=10004..20004
    do_family('G', [2501, 3000, 3501, 4000, 4501, 5001])     # n=10006..20006
    log('=== campaign complete ===')
    print('CAMPAIGN COMPLETE', flush=True)
