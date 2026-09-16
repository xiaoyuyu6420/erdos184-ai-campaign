#!/usr/bin/env python3
"""
(4,4) 类攻击管线: HOP(2^<s>, 4, 4), n = s+4.

模型 (自建, 见报告):
  HOP(2^<s>,4,4) 可解 <= 2K_n (每条 K_n 边取 2 副本) 的边能配成
  n(n-1)/2 组, 每组 2 条边端点不相交  [即线图补图 L_bar 有完美匹配]
  + 相位提升 (每标签对的两次事件分配互补内部序, 无耦合, 总可行).

方法:
  n>=8: Dirac (deg = (n-2)(n-3) >= N/2 = n(n-1)/2 当 n>=8) 保证存在.
  n=4..7: blossom 算法 (networkx) 显式求出.
输出: seating -> verifier 终审.
"""
import networkx as nx
from verifier import verify


def build_line_complement(n):
    """2K_n 边副本图, 顶点 = 2*eid + copy; 连边 iff 端点集不相交."""
    edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    eid = {e: i for i, e in enumerate(edges)}
    # 预计算每条边的"冲突边"(共享端点)
    conflicts = {i: set() for i in range(len(edges))}
    for i, (u, v) in enumerate(edges):
        for j, (x, y) in enumerate(edges):
            if i < j and len({u, v, x, y}) < 4:
                conflicts[i].add(j)
                conflicts[j].add(i)
    G = nx.Graph()
    N = 2 * len(edges)
    G.add_nodes_from(range(N))
    for i in range(len(edges)):
        j_set = conflicts[i]
        for j in range(i + 1, len(edges)):  # 严格 j>i; 同边副本共端点, 不连
            if j in j_set:
                continue
            for c1 in (0, 1):
                for c2 in (0, 1):
                    a, b = 2 * i + c1, 2 * j + c2
                    if a < b:
                        G.add_edge(a, b)
    return G, edges, eid


def match_44(n):
    """返回组的列表: 每组 = ((u,v),(w,x)) 标签边对, 端点互异; 若不存在返回 None."""
    G, edges, eid = build_line_complement(n)
    M = nx.max_weight_matching(G, maxcardinality=True)
    if len(M) * 2 != G.number_of_nodes():
        return None
    groups = []
    for a, b in M:
        i, j = a // 2, b // 2
        groups.append((edges[i], edges[j]))
    return groups


def groups_to_seating(n, groups):
    """相位提升 + seating 生成.
    每组一晚: 桌1 = 标签 (u,v), 桌2 = (w,x); 其余 n-4 对坐双人桌.
    每对标签的两次事件分配互补相位 a=0 / a=1."""
    seen_count = {}
    nights = []
    for (e1, e2) in groups:
        tables = []
        for (u, v) in (e1, e2):
            key = (min(u, v), max(u, v))
            c = seen_count.get(key, 0)
            alpha = c % 2  # 第 0/2/4... 次 a=0, 第 1/3... 次 a=1
            seen_count[key] = c + 1
            if c > 1:
                raise RuntimeError(f"标签对 {key} 同桌超过 2 次!")
            a, b = (u, v) if u < v else (v, u)
            tables.append([2 * a, 2 * a + 1, 2 * b + alpha, 2 * b + 1 - alpha])
        used = set()
        for (u, v) in (e1, e2):
            used.update((u, v))
        for p in range(n):
            if p not in used:
                tables.append([2 * p, 2 * p + 1])
        nights.append(tables)
    return nights


def verify2_independent(n, m_list, seating):
    """独立第二验证器: 邻接矩阵法 (不同实现路径).
    M[a][b] = a,b 全程邻座次数. 要求: 非配偶对恰 1, 配偶对恰 gamma 次, 对称, 对角 0."""
    m = sum(m_list)
    partner = {}
    for i in range(n):
        partner[2 * i] = 2 * i + 1
        partner[2 * i + 1] = 2 * i
    M = [[0] * (2 * n) for _ in range(2 * n)]
    for night in seating:
        for table in night:
            L = len(table)
            if L == 2:
                a, b = table
                M[a][b] += 1
                M[b][a] += 1
                continue
            for pos in range(L):
                a = table[pos]
                for q in (table[(pos - 1) % L], table[(pos + 1) % L]):
                    if q != a:
                        M[a][q] += 1
    gamma = len(seating)
    errs = []
    for a in range(2 * n):
        if M[a][a] != 0:
            errs.append(f"对角 M[{a}][{a}]={M[a][a]}")
        for b in range(a + 1, 2 * n):
            if M[a][b] != M[b][a]:
                errs.append(f"不对称 M[{a}][{b}]={M[a][b]} vs {M[b][a]}")
            if partner[a] == b:
                if M[a][b] != gamma:
                    errs.append(f"配偶对 ({a},{b}) 邻座 {M[a][b]} 次 != {gamma} 晚")
            else:
                if M[a][b] != 1:
                    errs.append(f"非配偶对 ({a},{b}) 邻座 {M[a][b]} 次 != 1")
        row = sum(M[a])
        if not (gamma <= row <= 2 * gamma):
            errs.append(f"人{a} 行和 {row} 越界 [{gamma},{2*gamma}]")
    # 每晚人员唯一性 + 桌规格 (与 v1 不同写法)
    for k, night in enumerate(seating):
        allp = [p for t in night for p in t]
        if sorted(allp) != list(range(2 * n)):
            errs.append(f"night{k} 覆盖错误")
        sizes = sorted(len(t) for t in night)
        if sizes != sorted([2] * (n - m) + [2 * mi for mi in m_list]):
            errs.append(f"night{k} 桌型 {sizes}")
    return (len(errs) == 0), errs


if __name__ == "__main__":
    print("=== (4,4) 类: L_bar(2K_n) 完美匹配 -> seating 双验证器终审 ===")
    results = {}
    for n in range(4, 17):
        groups = match_44(n)
        if groups is None:
            print(f"n={n}: L_bar 无完美匹配 (最大匹配 < N/2)")
            results[n] = "NO-MATCH"
            continue
        seating = groups_to_seating(n, groups)
        ok1, msg1 = verify(n, [2, 2], seating)
        ok2, errs2 = verify2_independent(n, [2, 2], seating)
        tag = "PASS" if (ok1 and ok2) else "FAIL"
        results[n] = tag
        print(f"n={n} (s={n-4}, gamma={len(seating)}): "
              f"V1={ok1} V2={ok2} [{tag}]  {msg1[-1] if ok1 else msg1}")
        if not ok2:
            for e in errs2[:5]:
                print("     V2:", e)
    print("\n汇总:", results)
