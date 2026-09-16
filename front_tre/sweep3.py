#!/usr/bin/env python3
"""扩展扫描 v3（本棒）：
  A. cubic n=14,16,18 全量：Claim R (p<=n-2) + 定理B (ell>=n/2+2) + PM-free 标记
     n=14 另算精确 f_re（m=21，DP 上限已放到 22）
  B. PM-free 图的块分析：p == sum(q(C_i)) + B? 与片节省 Phi = n_i - q_i >= ?
  C. 片引理 Phi 机器验证：全部连通无桥 subcubic 图 n<=14，
     验证 P0: p2(G) >= n/2 + 3/2（真值口径：2*p2 >= n+3），
     另统计强版 p2 >= n/2+2（2*p2 >= n+4）违反数与真值余量 min(2*p2-n) 及其 argmin；
     n=3 的 C3 与 n=5 的 K_{2,3} 是 P0 已知紧例（p2-n/2=3/2）。
     [2026-09-14 修复] 旧版用 N//2 整数除法：奇数 n 时实际只验了 P0（⌊n/2⌋+2 = n/2+3/2），
     且标签 min(p2-N//2) 虚高 0.5，导致报告误称「p2-n/2 >= 2 恒成立」。
     其中 p2 = 最大偶子图边数 = m - min T-join (T=奇度点集)
  D. k=2 构造族（上一棒 sweep2 的 B 部分，修正后）：5-正则 PM-free 候选的 Claim R 检查
结果追加 results3.jsonl。
"""
import sys, json, time, subprocess, os
sys.path.insert(0, '/Users/munich/Desktop/数学/front_tre')
import networkx as nx
from fre_lib import Graph
from fast_ver import f_re_exact_fast, parse_geng_line

RES = '/Users/munich/Desktop/数学/front_tre/results3.jsonl'


def tjoin_fast(g, T):
    """min T-join: 度量闭包 + networkx 最大权匹配（精确）。|T| 须偶。"""
    T = sorted(T)
    assert len(T) % 2 == 0, f"|T|={len(T)} 奇"
    if not T:
        return 0
    D = g.dist_matrix()
    H = nx.Graph()
    for i in range(len(T)):
        for j in range(i + 1, len(T)):
            u, v = T[i], T[j]
            if D[u][v] != float('inf'):
                H.add_edge(i, j, weight=-D[u][v])
    M = nx.max_weight_matching(H, maxcardinality=True)
    assert len(M) == len(T) // 2, "完美匹配不存在：连通图上 T 各分量偶数个点时必存在"
    return sum(D[T[i]][T[j]] for i, j in M)


def p_odd2(g):
    return tjoin_fast(g, range(g.n))


def blocks_with_bridges(g):
    """删桥后的连通片 + 每点桥数。返回 (片列表, 桥数)。
    片 = (n_i, b: dict 点->桥数)。"""
    br = g.bridges()
    bset = set(br)
    # 删桥
    adj = [set() for _ in range(g.n)]
    for i, (u, v) in enumerate(g.edges):
        if i not in bset:
            adj[u].add(v)
            adj[v].add(u)
    comp = [-1] * g.n
    c = 0
    for s in range(g.n):
        if comp[s] == -1:
            dq = [s]
            comp[s] = c
            while dq:
                u = dq.pop()
                for v in adj[u]:
                    if comp[v] == -1:
                        comp[v] = c
                        dq.append(v)
            c += 1
    bdeg = [0] * g.n
    for i in br:
        u, v = g.edges[i]
        bdeg[u] += 1
        bdeg[v] += 1
    pieces = []
    for ci in range(c):
        nodes = [v for v in range(g.n) if comp[v] == ci]
        b = {v: bdeg[v] for v in nodes}
        pieces.append((len(nodes), b, nodes))
    return pieces, len(br)


def q_block(g, nodes, b):
    """块上规范 T-join: T = {b_v 偶}。块须连通。"""
    T = [v for v in nodes if b[v] % 2 == 0]
    return tjoin_fast(g, T)


def p2_subcubic(g):
    """最大偶子图边数（圈打包）= m - min T-join, T = 奇度点。要求图 subcubic 无桥时该值即圈打包。"""
    T = [v for v in range(g.n) if g.deg[v] % 2 == 1]
    return g.m - tjoin_fast(g, T)


def main():
    outf = open(RES, 'a', buffering=1)
    t00 = time.time()
    viol_R = viol_B = viol_f = viol_phi = 0

    print('== A. cubic n=14,16,18 全量 ==', flush=True)
    for n in [14, 16, 18]:
        out = subprocess.run(['geng', '-c', '-d3', '-D3', str(n)],
                             capture_output=True, text=True).stdout
        cnt = pmfree_cnt = 0
        for line in out.splitlines():
            g6 = line.strip()
            N, edges = parse_geng_line(g6)
            g = Graph(N, edges, g6)
            p = p_odd2(g)
            rec = {'g6': g6, 'n': N, 'k': 1, 'p': p,
                   'claimR_ok': p <= N - 2, 'pmfree': p > N // 2}
            ell = g.m - p
            rec['ell'] = ell
            if ell < N // 2 + 2:
                viol_B += 1
                print(f'!!! 定理B违反: n={N} ell={ell} g6={g6}', flush=True)
            if not rec['claimR_ok']:
                viol_R += 1
                print(f'!!! Claim R 违反: n={N} p={p} g6={g6}', flush=True)
            if rec['pmfree']:
                pmfree_cnt += 1
                # 块分析: p == sum q + B?
                pieces, B = blocks_with_bridges(g)
                qs = []
                for (ni, b, nodes) in pieces:
                    q = q_block(g, nodes, b)
                    qs.append(q)
                    # 片引理 Phi >= ?
                    phi = ni - q
                    rec.setdefault('phis', []).append({'n': ni, 'q': q, 'bsum': sum(b.values()), 'phi': phi})
                tot = sum(qs) + B
                if tot != p:
                    print(f'!!! 块拼装不符: p={p} sum q + B={tot} g6={g6}', flush=True)
                rec['sum_phi'] = sum(ni - q for (ni, _, _), q in zip(pieces, qs))
                rec['B'] = B
                # 目标: sum Phi >= B + 2  <=>  p <= n - 2
                if rec['sum_phi'] < B + 2:
                    viol_phi += 1
                    print(f'!!! Phi 下界违反: sum_phi={rec["sum_phi"]} B={B} g6={g6}', flush=True)
            if n == 14:
                fr, _ = f_re_exact_fast(g)
                rec['f_re'] = fr
                rec['fre_ok'] = fr <= N - 1
                if fr > N - 1:
                    viol_f += 1
                    print(f'!!! 猜想违反: n={N} f_re={fr} g6={g6}', flush=True)
            outf.write(json.dumps(rec) + '\n')
            cnt += 1
            if cnt % 5000 == 0:
                print(f'  n={n}: {cnt} done, pmfree={pmfree_cnt}, {time.time()-t00:.0f}s', flush=True)
        print(f'  n={n} 完成: {cnt} 图, PM-free={pmfree_cnt}, {time.time()-t00:.0f}s', flush=True)

    run_piece_lemma_sweep(range(4, 15), outf, t00)
    run_k2_family(outf)

    outf.close()
    print(f'\n全部完成: ClaimR违 {viol_R}, 定理B违 {viol_B}, f_re违 {viol_f}, Phi违 {viol_phi}, 用时 {time.time()-t00:.0f}s', flush=True)


def run_piece_lemma_sweep(ns, outf, t00=None):
    """片引理扫描（真值口径）。ns: n 范围；outf: 追加写 jsonl。
    P0: 2*p2 >= n+3；强版: 2*p2 >= n+4；真值余量 = 2*p2 - n。"""
    t0 = time.time() if t00 is None else t00
    print('== C. 片引理: 无桥 subcubic 全量, P0: 2*p2>=n+3, 强版: 2*p2>=n+4 ==', flush=True)
    for n in ns:
        out = subprocess.run(['geng', '-c', '-D3', str(n)],
                             capture_output=True, text=True).stdout
        nb = viol_p0 = viol_strong = 0
        mn = 10**9
        argmin = ''
        for line in out.splitlines():
            g6 = line.strip()
            N, edges = parse_geng_line(g6)
            g = Graph(N, edges)
            if g.bridges():
                continue
            nb += 1
            p2 = p2_subcubic(g)
            margin2 = 2 * p2 - N   # = 2*(p2 - n/2)，整数无舍入
            if margin2 < mn:
                mn, argmin = margin2, g6
            if margin2 < 3:   # P0 违反: p2 < n/2+3/2
                viol_p0 += 1
                print(f'!!! P0 违反: n={N} p2={p2} 需2*p2>={N+3}', flush=True)
            if margin2 < 4:   # 强版违反: p2 < n/2+2（K_2,3 型紧例落此处）
                viol_strong += 1
            if N % 2 == 0 and margin2 < 4:
                print(f'!!! 强版(偶n)违反: n={N} p2={p2} g6={g6}', flush=True)
        print(f'  n={n}: 无桥subcubic {nb} 张, P0违反 {viol_p0}, 强版违反 {viol_strong}, '
              f'min(2*p2-n) = {mn} (即 p2-n/2 >= {mn/2:g}), argmin g6={argmin}, {time.time()-t0:.0f}s', flush=True)
        outf.write(json.dumps({'subcubic_n': n, 'count': nb, 'viol_p0': viol_p0,
                               'viol_strong': viol_strong, 'min_margin2': mn,
                               'argmin_g6': argmin}) + '\n')


def run_k2_family(outf):
    """D. k=2 构造族（上一棒 sweep2 的 B 部分，修正后）：5-正则 PM-free 候选的 Claim R 检查。"""
    print('== D. k=2 构造族 ==', flush=True)
    def side_B7():
        K7 = {(i, j) for i in range(7) for j in range(i + 1, 7)}
        rem = [(0, 1), (0, 2), (3, 4), (5, 6)]
        return [e for e in K7 if e not in rem and (e[1], e[0]) not in rem]

    def build_pmfree_5reg_chain(t):
        edges = []
        nxt = 0
        centers = []
        branch_att = []
        for i in range(t):
            nb = 5 if t == 1 else (4 if (i == 0 or i == t - 1) else 3)
            for _ in range(nb):
                s = side_B7()
                edges += [(u + nxt, v + nxt) for u, v in s]
                branch_att.append((i, nxt))
                nxt += 7
            centers.append(nxt)
            nxt += 1
        for (ci, a) in branch_att:
            edges.append((centers[ci], a))
        for i in range(t - 1):
            edges.append((centers[i], centers[i + 1]))
        return Graph(nxt, edges, f"PMfree5reg_chain{t}")

    for t in [1, 2, 3, 4, 6]:
        g = build_pmfree_5reg_chain(t)
        assert sorted(set(g.deg)) == [5], f'{g.name} 非5-正则: {sorted(set(g.deg))}'
        assert g.is_connected()
        p = p_odd2(g)
        ok = p <= g.n - 3
        rec = {'name': g.name, 'n': g.n, 'k': 2, 'p': p, 'claimR_ok': ok,
               'pmfree': p > g.n // 2, 'constructed': True}
        outf.write(json.dumps(rec) + '\n')
        print(f'  [{"OK" if ok else "VIOL"}] {g.name}: n={g.n} p={p} (上界 n-3={g.n-3}, PM-free={p > g.n//2})', flush=True)


if __name__ == '__main__':
    main()
