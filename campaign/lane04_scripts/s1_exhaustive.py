#!/usr/bin/env python3
"""
Lane 04 数值侦察 Script 1 —— Δ≤5 图穷举 (n ≤ 7) + R1 判据（奇偶台账）扫描。

R1（lane_04_delta5_savings.md §1 的主定理，本脚本同时是它的机器自检）：
    ce(G) ≤ (m + 2τ)/3,   τ = min T-join (T = 奇度点集, 单位权)
    判据: m + 2τ ≤ 3n − 3  ⟹  ce(G) ≤ n − 1。
residual := m + 2τ ≥ 3n − 2 （R1 不能直接判定 n−1 的图，即本 lane 的"残差前沿"）。

输出：
  - 各 n：connected/Δ≤5 计数、2-连通计数、residual 计数（按 2-连通分层）
  - exact-ce 子集上：猜想违反数（预期 0）、R1 有效性 assert、
    2-连通 ce=n−1 紧实例清单、sup ce/(n−1)
  - τ 的实现自检（对若干小图与暴力子集枚举对照）

用法: python3 s1_exhaustive.py <n> [--exact-cap M] [--sample K]
"""
import sys, random, json, time
from itertools import combinations


def bits(x):
    while x:
        b = (x & -x).bit_length() - 1
        x &= x - 1
        yield b


def build(mask, edges, n):
    adj = [0] * n
    m = 0
    for i in bits(mask):
        u, v = edges[i]
        adj[u] |= 1 << v
        adj[v] |= 1 << u
        m += 1
    return adj, m


def connected(adj, n, skip=-1):
    target = 0
    for v in range(n):
        if v != skip:
            target |= 1 << v
    if target == 0:
        return True
    start = (target & -target).bit_length() - 1
    seen = 1 << start
    st = [start]
    while st:
        x = st.pop()
        nb = adj[x] & target & ~seen
        while nb:
            b = (nb & -nb).bit_length() - 1
            nb &= nb - 1
            seen |= 1 << b
            st.append(b)
    return seen == target


def two_connected(adj, n):
    if n < 3:
        return False
    if not connected(adj, n):
        return False
    for v in range(n):
        if not connected(adj, n, skip=v):
            return False
    return True


def tau_tjoin(adj, n):
    """min T-join (单位权) = T 上最短路度量的最小权完美匹配 (Held-Karp)。"""
    T = [v for v in range(n) if adj[v].bit_count() & 1]
    t = len(T)
    if t == 0:
        return 0
    assert t % 2 == 0
    dist = {}
    for s in T:
        D = [-1] * n
        D[s] = 0
        q = [s]
        for x in q:
            nb = adj[x]
            while nb:
                b = (nb & -nb).bit_length() - 1
                nb &= nb - 1
                if D[b] < 0:
                    D[b] = D[x] + 1
                    q.append(b)
        for v in T:
            if v != s:
                dist[(s, v)] = D[v]
    idx = {v: i for i, v in enumerate(T)}
    FULL = (1 << t) - 1
    INF = 10 ** 9
    dp = [INF] * (1 << t)
    dp[0] = 0
    for S in range(1, FULL + 1):
        i = (S & -S).bit_length() - 1
        v = T[i]
        rest = S ^ (1 << i)
        best = INF
        R = rest
        while R:
            j = (R & -R).bit_length() - 1
            R &= R - 1
            c = dist[(v, T[j])] + dp[rest ^ (1 << j)]
            if c < best:
                best = c
        dp[S] = best
    return dp[FULL]


def tau_brute(adj, n, edges, mask, cap=8):
    """暴力 min T-join：枚举图中大小 ≤ cap 的边子集（仅小图自检用）。"""
    T = frozenset(v for v in range(n) if adj[v].bit_count() & 1)
    if not T:
        return 0
    present = list(bits(mask))
    for k in range(0, min(cap, len(present)) + 1):
        for sub in combinations(present, k):
            deg = [0] * n
            for i in sub:
                u, v = edges[i]
                deg[u] += 1
                deg[v] += 1
            if all((deg[v] & 1) == (1 if v in T else 0) for v in range(n)):
                return k
    return None


def all_cycles_em(adj, n, eid):
    cyc = set()
    for s in range(n):
        st = [(s, 1 << s, 0)]
        while st:
            v, vm, em = st.pop()
            nb = adj[v]
            while nb:
                b = (nb & -nb).bit_length() - 1
                nb &= nb - 1
                if b < s:
                    continue
                e = eid[(v, b) if v < b else (b, v)]
                if (em >> e) & 1:
                    continue
                if b == s:
                    if vm.bit_count() >= 3:
                        cyc.add(em | (1 << e))
                elif not (vm >> b) & 1:
                    st.append((b, vm | (1 << b), em | (1 << e)))
    return list(cyc)


def exact_ce(adj, n, edges=None):
    """位掩码 DP 精确 ce（所有简单圈 + 最低边分支）。边重打包为 0..m-1。"""
    m = sum(a.bit_count() for a in adj) // 2
    packed = []
    for u in range(n):
        nb = adj[u]
        while nb:
            b = (nb & -nb).bit_length() - 1
            nb &= nb - 1
            if b > u:
                packed.append((u, b))
    assert len(packed) == m
    eid = {e: i for i, e in enumerate(packed)}
    cyc = all_cycles_em(adj, n, eid)
    by_low = {}
    for em in cyc:
        low = (em & -em).bit_length() - 1
        by_low.setdefault(low, []).append(em)
    INF = 10 ** 9
    size = 1 << m
    dp = [INF] * size
    dp[0] = 0
    for mask in range(1, size):
        low = (mask & -mask).bit_length() - 1
        best = dp[mask ^ (1 << low)] + 1
        lst = by_low.get(low)
        if lst:
            for em in lst:
                if em & mask == em:
                    v = dp[mask ^ em] + 1
                    if v < best:
                        best = v
        dp[mask] = best
    return dp[size - 1], m


def scan(n, sample_residual=400, exact_mcap=16, seed=7, tlimit=None):
    t0 = time.time()
    edges = list(combinations(range(n), 2))
    E = len(edges)
    rng = random.Random(seed)
    S = dict(n=n, conn=0, twoconn=0, resid=0, resid_2c=0, conn_d5=0)
    resid2c = []
    for mask in range(1, 1 << E):
        adj, m = build(mask, edges, n)
        if m < n - 1:
            continue
        big = False
        for v in range(n):
            if adj[v].bit_count() > 5:
                big = True
                break
        if big:
            continue
        if not connected(adj, n):
            continue
        S['conn_d5'] += 1
        # 廉价残差预过滤: τ ≥ |T|/2 ⟹ 非残差当且仅当 |T|+m < 3n−2
        Tcnt = sum(1 for v in range(n) if adj[v].bit_count() & 1)
        cand_resid = (Tcnt + m >= 3 * n - 2)
        t2 = two_connected(adj, n)
        if t2:
            S['twoconn'] += 1
        if cand_resid:
            tv = tau_tjoin(adj, n)
            if m + 2 * tv >= 3 * n - 2:
                S['resid'] += 1
                if t2:
                    S['resid_2c'] += 1
                    resid2c.append((m, mask))
    # ---- exact-ce 阶段 ----
    resid2c.sort()
    exact_plan = [mk for (m, mk) in resid2c if m <= exact_mcap]
    if len(resid2c) > len(exact_plan):
        extra = rng.sample([mk for (m, mk) in resid2c if m > exact_mcap],
                           min(sample_residual, len(resid2c) - len(exact_plan)))
        exact_plan += extra
    S['exact_plan'] = len(exact_plan)
    S['viol'] = 0
    S['r1bad'] = 0
    S['tight'] = []
    S['maxratio'] = 0.0
    S['maxce'] = -1
    S['ce_hist'] = {}
    for mask in exact_plan:
        adj, m = build(mask, edges, n)
        ce, m = exact_ce(adj, n, edges)
        tv = tau_tjoin(adj, n)
        if ce > n - 1:
            S['viol'] += 1
            print(f"  !! 猜想违反: n={n} mask={mask} ce={ce} m={m}")
        if 3 * ce > m + 2 * tv:
            S['r1bad'] += 1
            print(f"  !! R1 失效: n={n} mask={mask} ce={ce} m={m} tau={tv}")
        if ce == n - 1:
            S['tight'].append(mask)
        S['ce_hist'][ce] = S['ce_hist'].get(ce, 0) + 1
        if ce > S['maxce']:
            S['maxce'] = ce
        r = ce / (n - 1)
        if r > S['maxratio']:
            S['maxratio'] = r
    S['time'] = round(time.time() - t0, 1)
    return S, resid2c


def selfcheck_tau(nmax=6, trials=200, seed=1):
    """τ 实现 vs 暴力：随机连通图 m≤12 上对照。"""
    rng = random.Random(seed)
    bad = 0
    for _ in range(trials):
        n = rng.randint(3, nmax)
        edges = list(combinations(range(n), 2))
        m = len(edges)
        mask = 0
        while True:
            mask = rng.getrandbits(m)
            adj, mm = build(mask, edges, n)
            if connected(adj, n) and all(adj[v].bit_count() <= 5 for v in range(n)) and mm <= 12:
                break
        a = tau_tjoin(adj, n)
        b = tau_brute(adj, n, edges, mask, cap=7)
        if b is not None and a != b:
            bad += 1
            print(f"  !! tau 不一致 n={n} mask={mask}: DP={a} brute={b}")
    print(f"tau selfcheck: {trials} trials, {bad} mismatches")
    return bad


if __name__ == '__main__':
    n = int(sys.argv[1])
    cap = int(sys.argv[2]) if len(sys.argv) > 2 else 16
    samp = int(sys.argv[3]) if len(sys.argv) > 3 else 400
    if n <= 6:
        selfcheck_tau()
    S, resid2c = scan(n, sample_residual=samp, exact_mcap=cap)
    print(json.dumps(S, ensure_ascii=False, indent=1))
    print(f"resid_2c 总数={len(resid2c)}, 按最小 m 的前 10: {[m for m,_ in resid2c[:10]]}")
