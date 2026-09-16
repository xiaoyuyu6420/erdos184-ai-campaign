#!/usr/bin/env python3
"""全量扫描：n ≤ 12 的全部连通 (2k+1)-正则图（geng 枚举，完备）。
对每张图：
  p     = 最小奇宇称生成子图边数（fast, networkx 花算法）
  断言 R: p ≤ n-1-k （Claim R，Conjecture 6.4 的充分条件）
  ℓ     = m - p；立方情形断言 ℓ ≥ n/2 + 2（定理 B）
  f_re  = 精确值（fast DP, m ≤ 20 时）；断言 f_re ≤ n-1
结果追加写 results.jsonl，可断点续跑。
"""
import sys, json, time, subprocess, os, random
sys.path.insert(0, '/Users/munich/Desktop/数学/front_tre')
from fre_lib import Graph
from fast_ver import f_re_exact_fast, p_odd_fast, parse_geng_line

RES = '/Users/munich/Desktop/数学/front_tre/results.jsonl'

def done_set():
    if not os.path.exists(RES):
        return set()
    with open(RES) as f:
        return {json.loads(l)['g6'] for l in f if l.strip()}

def main():
    done = done_set()
    outf = open(RES, 'a', buffering=1)
    total = viol_R = viol_f = 0
    t00 = time.time()
    stats = {}
    for k, n_list in [(1, [4, 6, 8, 10, 12]), (2, [6, 8, 10, 12]),
                      (3, [8, 10, 12]), (4, [10, 12]), (5, [12])]:
        for n in n_list:
            if 2 * k + 1 >= n and not (n == 0):
                pass
            deg = 2 * k + 1
            if deg >= n:
                continue
            out = subprocess.run(['geng', '-c', f'-d{deg}', f'-D{deg}', str(n)],
                                 capture_output=True, text=True).stdout
            for line in out.splitlines():
                g6 = line.strip()
                if g6 in done:
                    continue
                N, edges = parse_geng_line(g6)
                g = Graph(N, edges, g6)
                assert sorted(set(g.deg)) == [deg] and g.is_connected()
                p = p_odd_fast(g)
                rec = {'g6': g6, 'n': N, 'k': k, 'p': p,
                       'claimR_ok': p <= N - 1 - k,
                       'surplus': p - (N // 2)}
                if not rec['claimR_ok']:
                    viol_R += 1
                    print(f'!!! Claim R 违反: k={k} n={N} p={p} 上界={N-1-k} g6={g6}')
                # 立方：定理 B 断言
                if k == 1:
                    ell = g.m - p
                    rec['ell'] = ell
                    assert ell >= N // 2 + 2, f'定理 B 违反? n={N} ell={ell}'
                # 精确 f_re（m ≤ 20）
                if g.m <= 20:
                    fr, _ = f_re_exact_fast(g)
                    rec['f_re'] = fr
                    rec['fre_ok'] = fr <= N - 1
                    if fr > N - 1:
                        viol_f += 1
                        print(f'!!! 猜想违反: k={k} n={N} f_re={fr} g6={g6}')
                outf.write(json.dumps(rec) + '\n')
                total += 1
                if total % 1000 == 0:
                    import subprocess as sp
                    sw = sp.run(['sysctl', '-n', 'vm.swapusage'], capture_output=True, text=True).stdout.strip()
                    print(f'  ... {total} done, {time.time()-t00:.0f}s, {sw}', flush=True)
    outf.close()
    print(f'\n扫描完成: 新增 {total} 张, Claim R 违反 {viol_R}, f_re 违反 {viol_f}, 用时 {time.time()-t00:.0f}s')

if __name__ == '__main__':
    main()
