#!/usr/bin/env python3
"""h_A_exact.py — 两个互相独立的精确 ce 求解器（ce = 把 E(G) 划分为圈与单边的最少件数）。

求解器 1（BB）：迭代加深 DFS + 状态 memo（按"最低未覆盖边"分支；件为单边或简单圈；
                要求逐件边不交（划分））。自研 mask 状态搜索。
求解器 2（MILP）：exact-cover ILP，用 scipy.optimize.milp (HiGHS) 精确求解（对偶界=最优证明）。

两者共享的仅有"枚举全部简单圈"这一准备步骤；搜索/优化引擎完全不同。

锚点（取自上游 r2_01 报告公布的独立求解器数值，本文件不 import 其代码，仅对照取值）：
  K_{1,4}=4, K_{2,3}=3, K_{3,3}=4, K_3 ∪ K_{3,4}=7, K7=3, K8−PM=3, n=9 四个 6-正则类=3。
"""
import sys
import itertools
import time


def norm(u, v):
    return (u, v) if u < v else (v, u)


def build_adj(n, edges):
    adj = [[] for _ in range(n)]
    for (u, v) in edges:
        adj[u].append(v)
        adj[v].append(u)
    for a in adj:
        a.sort()
    return adj


def enum_all_cycles(n, adj):
    """枚举全部简单圈（长度 ≥3），每个圈为规范化边 tuple（最小顶点为起点）。"""
    cycles = set()

    def rec(s, v, path, pset):
        for w in adj[v]:
            if w == s:
                if len(path) >= 3:
                    cycles.add(tuple(sorted(norm(path[i], path[(i + 1) % len(path)])
                                          for i in range(len(path)))))
            elif w > s and w not in pset:
                path.append(w)
                pset.add(w)
                rec(s, w, path, pset)
                path.pop()
                pset.discard(w)

    for s in range(n):
        rec(s, s, [s], {s})
    return [list(c) for c in cycles]


def _prepare(n, edges):
    E = sorted(set(norm(u, v) for (u, v) in edges))
    eidx = {e: i for i, e in enumerate(E)}
    m = len(E)
    adj = build_adj(n, E)
    cyc = enum_all_cycles(n, adj)
    pieces = []
    for c in cyc:
        mask = 0
        for e in c:
            mask |= 1 << eidx[e]
        pieces.append((mask, len(c), c))
    for i in range(m):
        pieces.append((1 << i, 1, [E[i]]))
    return E, m, pieces


def exact_ce_bb(n, edges, ub=None, node_limit=20_000_000):
    """迭代加深 DFS + memo。返回 (ce, 见证件列表)。找不到（超 node_limit）返回 (None, reason)。"""
    E, m, pieces = _prepare(n, edges)
    full = (1 << m) - 1
    Lmax = max(sz for _, sz, _ in pieces)
    # 按边索引候选件（大小降序）
    by_edge = [[] for _ in range(m)]
    for idx, (mask, sz, _) in enumerate(pieces):
        for i in range(m):
            if (mask >> i) & 1:
                by_edge[i].append(idx)
    for i in range(m):
        by_edge[i].sort(key=lambda idx: -pieces[idx][1])
    memo = {}
    state = {"nodes": 0}

    def dfs(mask, k):
        state["nodes"] += 1
        if state["nodes"] > node_limit:
            raise RuntimeError("node_limit")
        if mask == full:
            return []
        if k == 0:
            return None
        key = (mask, k)
        if key in memo:
            return None
        rem = m - bin(mask).count("1")
        if rem > k * Lmax or rem < k:          # 件数预算剪枝
            memo[key] = None
            return None
        low = (~mask) & full
        e = (low & -low).bit_length() - 1     # 最低未覆盖边
        for idx in by_edge[e]:
            pm, sz, _ = pieces[idx]
            if pm & mask:                      # 与已覆盖重叠 -> 不是划分
                continue
            r = dfs(mask | pm, k - 1)
            if r is not None:
                return [idx] + r
        memo[key] = None
        return None

    lb = max(1, -(-m // Lmax))
    kmax = ub if ub is not None else m
    for k in range(lb, kmax + 1):
        try:
            r = dfs(0, k)
        except RuntimeError:
            return None, f"node_limit@{k} (lb={lb})"
        if r is not None:
            wit = [pieces[idx][2] for idx in r]
            return k, wit
    return None, f"no<= {kmax}"


def _milp_data(n, edges, k=None):
    """构造 exact-cover ILP 数据。k 给定时：加 Σx = k 行 + 按"每件大小 ≥ m−(k−1)Lmax"过滤。
    返回 (E, m, pieces, A, lb, ub)。"""
    import numpy as np
    import scipy.sparse as sp
    E, m, pieces = _prepare(n, edges)
    Lmax = max(sz for _, sz, _ in pieces)
    if k is not None:
        lo = max(1, m - (k - 1) * Lmax)   # k 件时每件的必要大小下界
        pieces = [p for p in pieces if p[1] >= lo]
    rows, cols, vals = [], [], []
    for ci, (mask, sz, c) in enumerate(pieces):
        for e in c:
            rows.append(E.index(e))
            cols.append(ci)
            vals.append(1)
    A = sp.csc_matrix((vals, (rows, cols)), shape=(m, len(pieces)))
    lb = np.ones(m)
    ub = np.ones(m)
    if k is not None:
        A = sp.vstack([A, sp.csc_matrix(np.ones((1, len(pieces))))]).tocsc()
        lb = np.concatenate([lb, [k]])
        ub = np.concatenate([ub, [k]])
    return E, m, pieces, A, lb, ub


def lp_bound(n, edges, time_limit=60.0):
    """exact-cover 的 LP 松弛最优值（下界；min Σx s.t. Ax=1, 0≤x≤1）。
    x≤1 是合法附加约束（整数解的 x 本就 ≤1），故仍是 IP 的松弛。"""
    import numpy as np
    from scipy.optimize import milp, LinearConstraint, Bounds
    E, m, pieces, A, lb, ub = _milp_data(n, edges, k=None)
    res = milp(c=np.ones(len(pieces)),
               constraints=LinearConstraint(A, lb, ub),
               integrality=np.zeros(len(pieces)),
               bounds=Bounds(0, 1),
               options={"time_limit": time_limit, "presolve": True})
    if res.status != 0:
        return None, f"lp status={res.status} msg={res.message}"
    return float(res.fun), "lp ok"


def milp_exact_ce(n, edges, ub, time_limit=60.0):
    """独立精确求解：对 k = lb, lb+1, ..., ub 依次问 HiGHS"恰好 k 件精确覆盖是否可行"。
    返回 (ce, 见证, 说明)。超时/未定如实标注；每个被证明不可行的 k 都记录。"""
    import numpy as np
    from scipy.optimize import milp, LinearConstraint, Bounds
    E0, m0, pieces0 = _prepare(n, edges)
    Lmax = max(sz for _, sz, _ in pieces0)
    lb = max(1, -(-m0 // Lmax))
    notes = []
    for k in range(lb, ub + 1):
        E, m, pieces, A, clb, cub = _milp_data(n, edges, k=k)
        res = milp(c=np.zeros(len(pieces)),
                   constraints=LinearConstraint(A, clb, cub),
                   integrality=np.ones(len(pieces)),
                   bounds=Bounds(0, 1),
                   options={"time_limit": time_limit, "presolve": True})
        if res.status == 0:
            x = np.round(res.x).astype(int)
            wit = [pieces[i][2] for i in range(len(pieces)) if x[i] == 1]
            if len(wit) != k or sum(len(p) for p in wit) != m0:
                notes.append(f"k={k}: 返回解不合规（内部检查拦截：{len(wit)} 件，边上数 {sum(len(p) for p in wit)}≠{m0}）")
                return None, None, "; ".join(notes)
            notes.append(f"k={k}: 可行（更小的各 k 已由 HiGHS 证不可行）")
            return k, wit, "; ".join(notes)
        if res.status == 2:
            notes.append(f"k={k}: 不可行(证明)")
            continue
        notes.append(f"k={k}: 未定 status={res.status}({res.message}) -> 停止")
        return None, None, "; ".join(notes)
    notes.append(f"k={ub}: 未找到可行解（异常，上界应可达）")
    return None, None, "; ".join(notes)


# ---------------------------------------------------------------- 校验（件合法性）
def check_pieces(n, edges, pieces):
    """独立小工具：件划分 + 每件是圈或单边。（主校验器在 h_verify.py，另写。）"""
    E = set(norm(u, v) for (u, v) in edges)
    seen = set()
    for p in pieces:
        pe = [norm(u, v) for (u, v) in p]
        assert all(e in E for e in pe), "件含非图边"
        for e in pe:
            assert e not in seen, "件之间重叠"
            seen.add(e)
        if len(pe) == 1:
            continue
        adj = {}
        for u, v in pe:
            adj.setdefault(u, []).append(v)
            adj.setdefault(v, []).append(u)
        assert all(len(a) == 2 for a in adj.values()), "件不是圈（度≠2）"
        assert len(adj) == len(pe), "件不是圈（点数≠边数）"
    assert seen == E, "件未覆盖全部边"
    return len(pieces)


def _mk(n, pairs):
    return [norm(u, v) for u, v in pairs]


def anchors(verbose=True):
    """对照上游公布的独立求解器数值（只取数值，不 import 上游代码）。"""
    cases = []
    cases.append(("K_{1,4}", 5, _mk(5, [(0, i) for i in range(1, 5)]), 4))
    cases.append(("K_{2,3}", 5, _mk(5, [(u, v) for u in range(2) for v in range(2, 5)]), 3))
    cases.append(("K_{3,3}", 6, _mk(6, [(u, v) for u in range(3) for v in range(3, 6)]), 4))
    k3 = _mk(7, [(0, 1), (1, 2), (0, 2)])
    k34 = _mk(7, [(u, v) for u in range(3, 6) for v in range(3, 7)])
    cases.append(("K3 u K_{3,4}", 7, k3 + k34, 7))
    cases.append(("K7", 7, _mk(7, [(u, v) for u in range(7) for v in range(u + 1, 7)]), 3))
    k8pm = [e for e in _mk(8, [(u, v) for u in range(8) for v in range(u + 1, 8)])
            if e not in {(i, i + 4) for i in range(4)}]
    cases.append(("K8-PM", 8, k8pm, 3))
    # n=9 的 4 个 6-正则类（补 2-因子型）
    K9 = set(itertools.combinations(range(9), 2))
    for comp in ([9], [6, 3], [5, 4], [3, 3, 3]):
        pos = 0
        E2 = set()
        for L in comp:
            cyc = list(range(pos, pos + L))
            pos += L
            for i in range(L):
                E2.add(norm(cyc[i], cyc[(i + 1) % L]))
        cases.append((f"n9 comp={comp}", 9, sorted(K9 - E2), 3))
    ok = True
    for name, n, edges, expect in cases:
        t0 = time.time()
        ce1, wit1 = exact_ce_bb(n, edges)
        c1 = check_pieces(n, edges, wit1) if wit1 else -1
        ce2, wit2, info2 = milp_exact_ce(n, edges, ub=ce1 if ce1 else expect)
        c2 = check_pieces(n, edges, wit2) if wit2 else -1
        lbp, inf = lp_bound(n, edges)
        good = (ce1 == expect == c1 == c2) and (ce2 == expect)
        ok &= good
        if verbose or not good:
            print(f"[anchor] {name:16s} expect={expect} BB={ce1} MILP={ce2} 见证={c1}/{c2} "
                  f"LP下界={lbp} {'OK' if good else '*** 不一致 ***'} ({time.time()-t0:.2f}s)")
            if not good:
                print(f"         MILP 说明: {info2} | LP: {inf}")
    print("[anchor] 全部一致" if ok else "[anchor] 存在不一致，需排查")
    return ok


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "anchors":
        ok = anchors()
        sys.exit(0 if ok else 1)
    print(__doc__)
