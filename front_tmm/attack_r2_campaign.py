#!/usr/bin/env python3
"""R2 裸区战役驱动：对每个 N ∈ [start, end] 调用 C 内核 r2search（K=7）做
「是否存在 valid 8-集合 mod N」的精确判定。

- 结果写 r2_logs/results.jsonl（resumable：status=complete 的 N 跳过）
- 每个 SOL 用原始 multiset 定义独立复核后才写入（防内核/判据 bug 自欺）
- N ≤ 247 出现复核通过的 SOL = Conjecture 1 的 n=8 反例（大声报告）
- N=248 为阳性锚点（应找到超递增集 (1,3,7,15,31,63,127) 及其伸缩）
"""
import sys, os, json, time, argparse, subprocess
from multiprocessing import cpu_count

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from attack_r2_search import Direct

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--start', type=int, default=128)
    ap.add_argument('--end', type=int, default=248)
    ap.add_argument('--per-n-seconds', type=int, default=1800)
    ap.add_argument('--threads', type=int, default=max(1, (cpu_count() or 4)))
    ap.add_argument('--results', default='r2_logs/results.jsonl')
    ap.add_argument('--bin', default='r2search')
    a = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    binpath = os.path.join(here, a.bin)
    respath = os.path.join(here, a.results)
    os.makedirs(os.path.dirname(respath), exist_ok=True)

    done = {}
    if os.path.exists(respath):
        with open(respath) as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    if rec.get('status') == 'complete':
                        done[rec['N']] = rec
                except Exception:
                    pass

    d = Direct(7)
    super_t = (1, 3, 7, 15, 31, 63, 127)
    print(f"campaign N∈[{a.start},{a.end}] threads={a.threads} "
          f"per_n={a.per_n_seconds}s done={sorted(done)}", flush=True)

    with open(respath, 'a', buffering=1) as out:
        for N in range(a.start, a.end + 1):
            if N in done:
                print(f"N={N}: complete (cached), skip", flush=True)
                continue
            t0 = time.time()
            p = subprocess.run([binpath, str(N), str(a.threads), str(a.per_n_seconds)],
                               capture_output=True, text=True)
            secs = time.time() - t0
            c_sols, nodes, leaves, capped = [], 0, 0, False
            for line in p.stdout.splitlines():
                if line.startswith('SOL'):
                    c_sols.append(tuple(int(x) for x in line.split()[1:]))
                elif line.startswith('STATS'):
                    _, nd, lv, cp = line.split()
                    nodes, leaves, capped = int(nd), int(lv), bool(int(cp))
            confirmed = [B for B in c_sols if d.valid(B, N)]
            false_pos = len(c_sols) - len(confirmed)
            if false_pos:
                print(f"!! {false_pos} 个内核正例未过原始复核 N={N}", flush=True)
            status = 'complete' if not capped else 'incomplete'
            rec = {'N': N, 'status': status, 'nodes': nodes, 'leaves': leaves,
                   'seconds': round(secs, 1), 'valid_sets': [list(B) for B in confirmed],
                   'false_positives': false_pos,
                   'superincreasing_present': (list(super_t) in [list(B) for B in confirmed])}
            out.write(json.dumps(rec) + '\n')
            if confirmed and N <= 247:
                print(f"!!!!! COUNTEREXAMPLE n=8 N={N}: {confirmed}", flush=True)
            if N == 248:
                print(f"anchor N=248: valid={len(confirmed)} "
                      f"superincreasing_present={rec['superincreasing_present']}", flush=True)
            print(f"N={N}: {status} nodes={nodes} leaves={leaves} secs={secs:.1f} "
                  f"valid={len(confirmed)}", flush=True)

if __name__ == '__main__':
    main()
