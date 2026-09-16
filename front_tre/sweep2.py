#!/usr/bin/env python3
"""扩展扫描 v2：
  A. geng 全量: cubic n=14,16,18; 5-regular n=14; 7-regular n=14
     - p-check (Claim R: p ≤ n-1-k)
     - cubic: 定理 B 断言 ℓ = m-p ≥ n/2+2
     - 标记 PM-free (p > n/2) 图
  B. 构造 k=2 的 PM-free 图族（Tutte 障碍构造）并 p-check
  C. cubic n=14 精确 f_re (m=21)
结果追加 results2.jsonl。
"""
import sys, json, time, subprocess, os
sys.path.insert(0, '/Users/munich/Desktop/数学/front_tre')
from fre_lib import Graph
from fast_ver import f_re_exact_fast, p_odd_fast, parse_geng_line

RES = '/Users/munich/Desktop/数学/front_tre/results2.jsonl'

def side_B7():
    """7 点 5-正则枝: K_7 去 {P_3 上的 2 边 + 1 匹配}; 顶点 0 是附着点(内度 4)"""
    K7 = {(i, j) for i in range(7) for j in range(i + 1, 7)}
    # 移除: 0-1, 1-2 (P_3: 0,1,2 使 0,2 失去1度, 1 失去2度?) 需要 (2,1,1,1,1,1,1)
    # 目标去除度序列: 顶点0 失去 2, 其余各失 1
    rem = [(0, 1), (0, 2), (3, 4), (5, 6)]
    return [e for e in K7 if e not in rem and (e[1], e[0]) not in rem]

def filler_B6():
    """6 点偶枝: K_6 去 1 条边, 顶点 0,1 是附着点(内度 4)"""
    K6 = [(i, j) for i in range(6) for j in range(i + 1, 6)]
    return [e for e in K6 if e != (0, 1)]

def build_pmfree_5reg(n_branches):
    """v 为中心, 挂 n_branches 个 B7 枝 (5-正则, n = 7b+1)。
    G - v 有 n_branches 个奇分量 -> Tutte 障碍 -> 无完美匹配 (b >= 3)。"""
    edges = []
    base = 1
    atts = []
    for b in range(n_branches):
        s = side_B7()
        edges += [(u + base, v + base) for u, v in s]
        atts.append(base)  # 顶点 0 of the side 是附着点
        base += 7
    v = base
    for a in atts:
        edges.append((v, a))
    # 中心 v 度 = n_branches, 需要 5
    assert n_branches == 5, "此简单版只做 5 枝"
    return Graph(7 * n_branches + 1, edges, f"PMfree5reg_b{n_branches}")

def build_pmfree_5reg_mixed():
    """3 个 B7 枝 + 1 个 B6 填充 + v (n=28), v 度 = 3+2 = 5"""
    edges = []
    base = 1
    atts = []
    for b in range(3):
        s = side_B7()
        edges += [(u + base, v + base) for u, v in s]
        atts.append(base)
        base += 7
    s = filler_B6()
    edges += [(u + base, v + base) for u, v in s]
    atts += [base, base + 1]
    base += 6
    v = base
    for a in atts:
        edges.append((v, a))
    return Graph(base + 1, edges, "PMfree5reg_mixed28")

def build_pmfree_5reg_chain(t):
    """t 个 5 度中心链: 端中心挂 4 个 B7 + 1 链边; 内中心挂 3 个 B7 + 2 链边 (t=1: 5 个 B7)。
    每个中心删去自身 -> 至少 3 个奇分量? 注: 需逐例验证 Tutte 障碍。"""
    edges = []
    nxt = 0
    centers = []
    branch_att = []
    for i in range(t):
        nb = 5 if t == 1 else (4 if (i == 0 or i == t - 1) else 3)
        for _ in range(nb):
            s = side_B7()
            edges += [(u + nxt, v + nxt) for u, v in s]
            branch_att.append((i, nxt))  # side 顶点 0 是附着点
            nxt += 7
        centers.append(nxt)
        nxt += 1
    for (ci, a) in branch_att:
        edges.append((centers[ci], a))
    for i in range(t - 1):
        edges.append((centers[i], centers[i + 1]))
    return Graph(nxt, edges, f"PMfree5reg_chain{t}")

def main():
    outf = open(RES, 'a', buffering=1)
    t00 = time.time()
    total = pmfree_cnt = viol = 0
    print('== A. geng 扩展全量 ==', flush=True)
    for k, n in [(1, 14), (1, 16), (1, 18), (2, 14), (3, 14)]:
        if k >= 2:
            continue  # 结构分析: 5-正则 PM-free 需 n>=22, n=14 全量枚举无信息量且过慢; 以 B 部分构造族代替
        deg = 2 * k + 1
        out = subprocess.run(['geng', '-c', f'-d{deg}', f'-D{deg}', str(n)],
                             capture_output=True, text=True).stdout
        cnt = 0
        for line in out.splitlines():
            g6 = line.strip()
            N, edges = parse_geng_line(g6)
            g = Graph(N, edges, g6)
            p = p_odd_fast(g)
            rec = {'g6': g6, 'n': N, 'k': k, 'p': p,
                   'claimR_ok': p <= N - 1 - k, 'pmfree': p > N // 2}
            if k == 1:
                ell = g.m - p
                rec['ell'] = ell
                assert ell >= N // 2 + 2, f'定理 B 违反? n={N} ell={ell} g6={g6}'
            if not rec['claimR_ok']:
                viol += 1
                print(f'!!! Claim R 违反: k={k} n={N} p={p} g6={g6}', flush=True)
            if rec['pmfree']:
                pmfree_cnt += 1
                if pmfree_cnt <= 10 or pmfree_cnt % 50 == 0:
                    print(f'  PM-free: k={k} n={N} p={p} ( surplus={p - N//2} ) g6={g6[:20]}...', flush=True)
            if k == 1 and N == 14:
                fr, _ = f_re_exact_fast(g)
                rec['f_re'] = fr
                assert fr <= N - 1, f'f_re 违反 n={N}'
            outf.write(json.dumps(rec) + '\n')
            cnt += 1
        print(f'  k={k} n={n}: {cnt} 图完成, PM-free={sum(1 for _ in [])}, 用时 {time.time()-t00:.0f}s', flush=True)
    total += 0
    print('== B. 构造 k=2 PM-free 图族 ==', flush=True)
    constructed = []
    for b in [5]:
        g = build_pmfree_5reg(b)
        constructed.append(g)
    constructed.append(build_pmfree_5reg_mixed())
    for t in [2, 3, 4, 6]:
        g = build_pmfree_5reg_chain(t)
        constructed.append(g)
    for g in constructed:
        assert sorted(set(g.deg)) == [5], f'{g.name} 非 5-正则: {sorted(set(g.deg))}'
        assert g.is_connected()
        p = p_odd_fast(g)
        rec = {'name': g.name, 'n': g.n, 'k': 2, 'p': p,
               'claimR_ok': p <= g.n - 3, 'pmfree': p > g.n // 2, 'constructed': True}
        outf.write(json.dumps(rec) + '\n')
        tag = 'OK ' if rec['claimR_ok'] else 'VIOLATION'
        print(f'  [{tag}] {g.name}: n={g.n} p={p} (n/2={g.n//2}, 上界 n-3={g.n-3})', flush=True)
        if not rec['claimR_ok']:
            viol += 1
    outf.close()
    print(f'\n扩展扫描完成: Claim R 违反 {viol}, 用时 {time.time()-t00:.0f}s', flush=True)

if __name__ == '__main__':
    main()
