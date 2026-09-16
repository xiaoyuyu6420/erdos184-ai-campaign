#!/usr/bin/env python3
"""R2 裸区战役 v3：位掩码 + 禁止值预计算（F-prune）。

对固定 N 判定「是否存在 valid (K+1)-集合 mod N」（K=7 即 n=8）：
  A = {0} ∪ B, B ⊂ [1, N-1], |B| = K（a₀=0 规范化）。
  DFS 按 升序 插入元素；子集和集合用 N 位大整数位掩码跟踪。
  每个节点预计算「禁止值掩码」F(C)：
    x ∈ F(C) ⟺ 存在 R ⊆ C 使 x + Σ_R ∈ sums_{≤|R|+2}(C∖R)
             （即把 x 插为最大元素后，max 元素属于 Q 的碰撞已可见 —— sound 剪枝）
  叶子处做完整 MC 判据检查（完备性由叶检查保证：P 侧需要较大元素的碰撞不被
  F-prune 捕获，但会被叶检查捕获）。
  零输出 ⟺ 该 N 无 valid (K+1)-集。

自测：--selftest 对 K ∈ {2,3,4} 与暴力全枚举双向比对。
"""
import sys, os, json, time, argparse
from itertools import combinations
from collections import Counter
from multiprocessing import Pool, cpu_count

# ---------------- 精确判据（位掩码） ----------------

def sums_upto_mask(elems, budget, N):
    full = (1 << N) - 1
    reach = 1
    exact = 1
    for _ in range(budget):
        nx = 0
        for e in elems:
            nx |= ((exact << e) & full) | (exact >> (N - e)) if e else exact
        reach |= nx
        exact = nx
    return reach

class Ctx:
    __slots__ = ('N', 'cache')
    def __init__(self, N):
        self.N = N
        self.cache = {}
    def reach(self, elems, budget):
        key = (elems, budget)
        r = self.cache.get(key)
        if r is None:
            r = sums_upto_mask(elems, budget, self.N)
            self.cache[key] = r
        return r

def rot_right(mask, s, N):
    s %= N
    if s == 0:
        return mask
    full = (1 << N) - 1
    return ((mask >> s) | (mask << (N - s))) & full

def forbidden_mask(B, N, ctx):
    """x ∈ F ⟺ 插入 x（作为当前最大元素）后立即出现可见碰撞。"""
    m = len(B)
    F = 0
    for rmask in range(1 << m):
        rsum = 0
        comp = []
        for i in range(m):
            if (rmask >> i) & 1:
                rsum += B[i]
            else:
                comp.append(B[i])
        budget = bin(rmask).count('1') + 2
        rm = ctx.reach(tuple(comp), budget)
        F |= rot_right(rm, rsum, N)
    return F

def mc_violation(B, N, ctx):
    """引理 A 完整检查：返回第一个违规 Q，无则 None。"""
    m = len(B)
    rng = range(m)
    for q in range(1, m + 1):
        budget = q + 1
        for Q in combinations(rng, q):
            Qs = set(Q)
            elems = tuple(B[i] for i in rng if i not in Qs)
            delta = sum(B[i] for i in Q) % N
            if (ctx.reach(elems, budget) >> delta) & 1:
                return Q
    return None

# ---------------- 独立复核（原始 multiset 定义） ----------------

def make_multisets(k, s):
    def rec(start, rem):
        if rem == 0:
            yield ()
            return
        for i in range(start, k):
            for rest in rec(i, rem - 1):
                yield (i,) + rest
    return list(rec(0, s))

class Direct:
    """按 K 缓存的原始定义检查器（A = (0,)+B 共 K+1 元，多重集大小 = K+1）。"""
    def __init__(self, K):
        self.K = K
        self.ms = make_multisets(K + 1, K + 1)
    def valid(self, B, N):
        A = (0,) + tuple(B)
        p = sum(A) % N
        ones = tuple(range(self.K + 1))
        for ms in self.ms:
            s = 0
            for i in ms:
                s += A[i]
            if s % N == p and ms != ones:
                return False
        return True

# ---------------- 枚举 ----------------

class CapExceeded(Exception):
    pass

def search_from(N, b1, K, deadline, direct):
    full = (1 << N) - 1
    B = [b1]
    mask = 1 | (1 << b1)
    ctx = Ctx(N)
    nodes = leaves = 0
    qhist = Counter()
    sols = []
    CHECK = 8192

    def rec(start):
        nonlocal nodes, leaves, mask
        nodes += 1
        if nodes % CHECK == 0 and time.time() > deadline:
            raise CapExceeded
        m = len(B)
        if m == K:
            leaves += 1
            Q = mc_violation(B, N, ctx)
            if Q is None:
                sols.append(tuple(B))
            else:
                qhist[len(Q)] += 1
            return
        F = forbidden_mask(B, N, ctx)
        hi = N - (K - m) + 1   # b ≤ N-K+m（留足更高元素空间）
        for b in range(start, N - K + m + 1):
            nb = ((mask << b) & full) | (mask >> (N - b))
            if nb & mask:
                continue          # dissociation 前缀剪枝
            if (F >> b) & 1:
                continue          # F-prune：插入即碰撞
            B.append(b)
            mask |= nb
            rec(b + 1)
            B.pop()
            mask ^= nb

    try:
        rec(b1 + 1)
        return {'leaves': leaves, 'nodes': nodes, 'sols': sols,
                'qhist': dict(qhist), 'capped': False}
    except CapExceeded:
        return {'leaves': leaves, 'nodes': nodes, 'sols': sols,
                'qhist': dict(qhist), 'capped': True}

def worker(job):
    N, b1, K, deadline = job
    r = search_from(N, b1, K, deadline, None)
    r['sols'] = [list(s) for s in r['sols']]
    return r

# ---------------- 自测 ----------------

def selftest():
    ok = True
    for K in (2, 3, 4):
        d = Direct(K)
        for N in (6, 9, 12, 13, 16, 17, 29, 31):
            # 暴力：全部 K-子集
            brute_valid = set()
            for B in combinations(range(1, N), K):
                if d.valid(B, N):
                    brute_valid.add(B)
            # 枚举器（b1 分治）
            enum = set()
            for b1 in range(1, N - K + 2):
                r = search_from(N, b1, K, time.time() + 60, d)
                for s in r['sols']:
                    enum.add(tuple(s))
                if r['capped']:
                    print(f"  selftest CAP at K={K} N={N} b1={b1}")
            miss = brute_valid - enum
            false = enum - brute_valid
            # 枚举器输出应全过原始定义（false 已含此检查）
            if miss or false:
                ok = False
                print(f"  SELFTEST FAIL K={K} N={N}: missed={sorted(miss)} false={sorted(false)}")
            else:
                print(f"  selftest OK K={K} N={N}: dissociated+valid sets = {len(brute_valid)}", flush=True)
    print("SELFTEST", "PASS" if ok else "FAIL", flush=True)
    return ok

# ---------------- 主流程 ----------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--start', type=int, default=128)
    ap.add_argument('--end', type=int, default=247)
    ap.add_argument('--per-n-seconds', type=int, default=900)
    ap.add_argument('--workers', type=int, default=max(1, cpu_count() or 4))
    ap.add_argument('--results', default='r2_logs/results.jsonl')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()

    if a.selftest:
        sys.exit(0 if selftest() else 1)

    os.makedirs(os.path.dirname(a.results) or '.', exist_ok=True)
    done = {}
    if os.path.exists(a.results):
        with open(a.results) as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    if rec.get('status') == 'complete':
                        done[rec['N']] = rec
                except Exception:
                    pass

    print(f"campaign N∈[{a.start},{a.end}] workers={a.workers} "
          f"per_n={a.per_n_seconds}s already_done={sorted(done)}", flush=True)

    direct = Direct(7)
    with open(a.results, 'a', buffering=1) as out, Pool(a.workers) as pool:
        for N in range(a.start, a.end + 1):
            if N in done:
                print(f"N={N}: complete (cached), skip", flush=True)
                continue
            t0 = time.time()
            deadline = t0 + a.per_n_seconds
            jobs = [(N, b1, 7, deadline) for b1 in range(1, N - 5)]
            leaves = nodes = 0
            sols = []
            qh = Counter()
            capped = False
            for r in pool.imap_unordered(worker, jobs,
                                         chunksize=max(1, len(jobs) // (a.workers * 4) or 1)):
                leaves += r['leaves']
                nodes += r['nodes']
                qh.update(r['qhist'])
                sols += r['sols']
                capped = capped or r['capped']
            secs = time.time() - t0
            confirmed = []
            for B in sols:
                if direct.valid(tuple(B), N):
                    confirmed.append(B)
                else:
                    print(f"!! MC 正例未过原始复核（判据 bug）N={N} B={B}", flush=True)
            status = 'complete' if not capped else 'incomplete'
            rec = {'N': N, 'status': status, 'dissociated_sets': leaves,
                   'nodes': nodes, 'seconds': round(secs, 1),
                   'valid_sets': confirmed,
                   'valid_sets_unconfirmed': len(sols) - len(confirmed),
                   'qkill_hist': {str(k): v for k, v in sorted(qh.items())}}
            out.write(json.dumps(rec) + '\n')
            if confirmed:
                print(f"!!!!! COUNTEREXAMPLE n=8 N={N}: {confirmed}", flush=True)
            print(f"N={N}: {status} diss={leaves} nodes={nodes} secs={secs:.1f} "
                  f"valid={len(confirmed)} qkill={dict(qh)}", flush=True)

if __name__ == '__main__':
    main()
