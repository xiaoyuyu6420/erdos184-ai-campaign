#!/usr/bin/env python3
"""
Lane 04 Script 4 —— 收尾缺口四件套。

A. n=7 m=17 全枚举: 残差2-连通计数 + decision(≤6)（补齐 s1 的 m≤16 exact + m=17 抽样）。
B. 残差类中的 Δ≤4 图统计（R1 对 2-连通 Δ≤4 的覆盖缺口到底有多大）:
   n=6: m≥12 才可能残差（数学论证见 lane 文档 §3.4）; n=7: m∈{13,14}（补图枚举）。
C. W=∅ 覆盖检验: 残差图是否存在 Π = ce 且圈覆盖所有点的最优分解。
   （W = 不在任何圈件上的点集；存在 ⟺ ce_cov = ce。）
D. 紧实例（ce = n−1）形态统计: n=6 全部 138 个 + n=7 全部 105 个（s1 输出 mask 解码）。
"""
import json, random, sys, time
from itertools import combinations
from s1_exhaustive import build, connected, two_connected, tau_tjoin, exact_ce

sys.setrecursionlimit(100000)


def all_cycles_of(adj, n, eid):
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


def packing_structure(adj, n):
    """返回 (m, by_low 圈索引, eid) 供 DFS 枚举分解。"""
    packed = []
    for u in range(n):
        nb = adj[u]
        while nb:
            b = (nb & -nb).bit_length() - 1
            nb &= nb - 1
            if b > u:
                packed.append((u, b))
    eid = {e: i for i, e in enumerate(packed)}
    cyc = all_cycles_of(adj, n, eid)
    by_low = {}
    for em in cyc:
        by_low.setdefault((em & -em).bit_length() - 1, []).append(em)
    return len(packed), by_low, eid, packed


def min_pi_and_coverage(adj, n, node_cap=400000, time_cap=8.0):
    """DFS 枚举全部最优（Π = ce）分解, 检查是否存在圈覆盖全部点的。
    返回 (ce, status, cov_yes)  status ∈ OK/SKIP_CAP。"""
    ce, m = exact_ce(adj, n)
    m2, by_low, eid, packed = packing_structure(adj, n)
    t0 = time.time()
    nodes = [0]
    found_cov = [False]
    FULLV = (1 << n) - 1

    def dfs(mask, parts, vm_cov):
        # mask: 未处理边; parts: 已用件数; vm_cov: 已被圈覆盖的点
        if parts > ce:
            return
        if nodes[0] > node_cap or time.time() - t0 > time_cap:
            raise TimeoutError
        nodes[0] += 1
        if mask == 0:
            if parts == ce and vm_cov == FULLV:
                found_cov[0] = True
            return
        # 剪枝: 剩余每件至少 1 边, 至少还需 mask 边数 - 最优圈省边……
        # 简单下界: 剩余边数 rem, 每圈最多省 |C|-1 ≥ 2 边 → parts + rem - 2*maxcirc ≤ ce
        rem = mask.bit_count()
        if parts + rem - 2 * (max((em.bit_count() for lst in by_low.values() for em in lst), default=3)) > ce:
            return
        low = (mask & -mask).bit_length() - 1
        # 分支1: low 边作单边件
        dfs(mask ^ (1 << low), parts + 1, vm_cov)
        if found_cov[0]:
            return
        # 分支2+: low 边进某个圈
        for em in by_low.get(low, ()):
            if em & mask == em:
                vm = 0
                ee = em
                while ee:
                    b = (ee & -ee).bit_length() - 1
                    ee &= ee - 1
                    u, v = packed[b]
                    vm |= (1 << u) | (1 << v)
                dfs(mask ^ em, parts + 1, vm_cov | vm)
                if found_cov[0]:
                    return

    try:
        dfs((1 << m) - 1, 0, 0)
        status = "OK"
    except TimeoutError:
        status = "SKIP"
    return ce, status, found_cov[0]


def part_A():
    print("== Part A: n=7, m=17 全枚举（补齐 s1 的 exact 覆盖） ==")
    edges = list(combinations(range(7), 2))
    tot = resid = r2c = viol = 0
    for comb in combinations(range(21), 17):
        mask = sum(1 << i for i in comb)
        adj, m = build(mask, edges, 7)
        if not two_connected(adj, 7):
            continue
        tot += 1
        Tcnt = sum(1 for v in range(7) if adj[v].bit_count() & 1)
        if Tcnt + m < 3 * 7 - 2:
            continue
        tv = tau_tjoin(adj, 7)
        if m + 2 * tv >= 3 * 7 - 2:
            resid += 1
            r2c += 1
            ce, _ = exact_ce(adj, 7)
            if ce > 6:
                viol += 1
                print(f"  !! 违反: mask={mask} ce={ce}")
    print(f"  m=17: 2-连通 Δ≤5 = {tot}, 残差2-连通 = {r2c}, ce>6 违反 = {viol}")
    return r2c, viol


def part_B():
    print("== Part B: 残差类中 Δ≤4 的图（R1 覆盖 Δ≤4 的缺口大小） ==")
    # n=6: 残差需 m+2τ ≥ 16, τ ≤ 3 ⟹ m ≥ 10 数学上 m≥12(见文档); 枚举 m ∈ {10,11,12} Δ≤4 验证
    edges6 = list(combinations(range(6), 2))
    cnt6 = 0
    for m in (10, 11, 12):
        for comb in combinations(range(15), m):
            mask = sum(1 << i for i in comb)
            adj, mm = build(mask, edges6, 6)
            if max(a.bit_count() for a in adj) > 4:
                continue
            if not two_connected(adj, 6):
                continue
            tv = tau_tjoin(adj, 6)
            if mm + 2 * tv >= 16:
                cnt6 += 1
                ce, _ = exact_ce(adj, 6)
                print(f"  n=6 残差 Δ≤4: m={mm} τ={tv} ce={ce} mask={mask}")
    print(f"  n=6 残差 2-连通 Δ≤4 总数 = {cnt6}")
    # n=7: 残差需 m+2τ ≥ 19, τ ≤ ⌊|T|/2⌋ ≤ 3 (Δ≤4 时 |T| ≤ 7 偶 ⟹ ≤ 6 ⟹ τ ≤ 3) ⟹ m ≥ 13
    # Δ≤4 ⟹ m ≤ 14. 补图枚举: m=13 ⟹ 补 8 边; m=14 ⟹ 补 7 边; 补图最小度 ≥ 7-1-4 = 2
    edges7 = list(combinations(range(7), 2))
    cnt7 = 0
    tight7 = []
    for mb in (7, 8):
        for comb in combinations(range(21), mb):
            cmask = sum(1 << i for i in comb)
            mask = ((1 << 21) - 1) ^ cmask
            adj, m = build(mask, edges7, 7)
            if max(a.bit_count() for a in adj) > 4:
                continue
            if not two_connected(adj, 7):
                continue
            tv = tau_tjoin(adj, 7)
            if m + 2 * tv >= 19:
                cnt7 += 1
                ce, _ = exact_ce(adj, 7)
                tag = " 紧!" if ce == 6 else ""
                if ce == 6:
                    tight7.append(mask)
                print(f"  n=7 残差 Δ≤4: m={m} τ={tv} ce={ce} mask={mask}{tag}")
                assert ce <= 6
    print(f"  n=7 残差 2-连通 Δ≤4 总数 = {cnt7}, 其中 ce=6=n−1 的 = {len(tight7)}")
    return cnt6, cnt7


def part_C(samples_n7=150, seed=11):
    print("== Part C: W=∅ 覆盖检验（存在 Π=ce 且全圈覆盖的最优分解?） ==")
    edges6 = list(combinations(range(6), 2))
    edges7 = list(combinations(range(7), 2))
    # n=6: 全部残差2-连通
    r2c6 = []
    for mask in range(1, 1 << 15):
        adj, m = build(mask, edges6, 6)
        if max(a.bit_count() for a in adj) > 5 or not two_connected(adj, 6):
            continue
        Tcnt = sum(1 for v in range(6) if adj[v].bit_count() & 1)
        if Tcnt + m < 16:
            continue
        tv = tau_tjoin(adj, 6)
        if m + 2 * tv >= 16:
            r2c6.append(mask)
    print(f"  n=6 残差2-连通 Δ≤5 = {len(r2c6)}, 全查覆盖…")
    no_cov = skip = ok = 0
    for mask in r2c6:
        adj, m = build(mask, edges6, 6)
        ce, status, cov = min_pi_and_coverage(adj, 6)
        if status == "OK":
            ok += 1
            if not cov:
                no_cov += 1
                print(f"  !! n=6 mask={mask}: ce={ce} 但不存在全覆盖最优分解")
        else:
            skip += 1
    print(f"  n=6: OK={ok} (无覆盖最优分解的图 = {no_cov}), SKIP={skip}")
    # n=7: 抽样残差2-连通（含 s1 输出的全部 105 个紧 mask）
    txt = open("s1_n7_out.txt").read()
    s1 = json.JSONDecoder().raw_decode(txt)[0]
    tight7 = s1["tight"]
    rng = random.Random(seed)
    extra = []
    tries = 0
    while len(extra) < samples_n7 and tries < 200000:
        tries += 1
        k = rng.randint(12, 17)
        mask = sum(1 << i for i in rng.sample(range(21), k))
        adj, m = build(mask, edges7, 7)
        if max(a.bit_count() for a in adj) > 5 or not two_connected(adj, 7):
            continue
        Tcnt = sum(1 for v in range(7) if adj[v].bit_count() & 1)
        if Tcnt + m < 19:
            continue
        tv = tau_tjoin(adj, 7)
        if m + 2 * tv >= 19 and mask not in tight7:
            extra.append(mask)
    pool = tight7 + extra
    no7 = skip7 = ok7 = 0
    for mask in pool:
        adj, m = build(mask, edges7, 7)
        ce, status, cov = min_pi_and_coverage(adj, 7)
        if status == "OK":
            ok7 += 1
            if not cov:
                no7 += 1
                print(f"  !! n=7 mask={mask}: ce={ce} 但不存在全覆盖最优分解")
        else:
            skip7 += 1
    print(f"  n=7: 查 {len(pool)} (紧 {len(tight7)} + 抽样 {len(extra)}), OK={ok7} "
          f"(无覆盖最优分解 = {no7}), SKIP={skip7}")
    return no_cov + no7, skip + skip7


def part_D():
    print("== Part D: 紧实例形态 ==")
    edges6 = list(combinations(range(6), 2))
    def load_s1(path):
        txt = open(path).read()
        dec = json.JSONDecoder()
        obj, _ = dec.raw_decode(txt)
        return obj
    s1 = load_s1("s1_n7_out.txt")
    edges7 = list(combinations(range(7), 2))

    def shape(mask, edges, n):
        adj, m = build(mask, edges, n)
        degs = tuple(sorted(a.bit_count() for a in adj))
        return m, degs, adj

    from collections import Counter
    c6 = Counter()
    for mask in range(1, 1 << 15):
        adj, m = build(mask, edges6, 6)
        if max(a.bit_count() for a in adj) > 5 or not two_connected(adj, 6):
            continue
        Tcnt = sum(1 for v in range(6) if adj[v].bit_count() & 1)
        if Tcnt + m < 16:
            continue
        tv = tau_tjoin(adj, 6)
        if m + 2 * tv >= 16:
            ce, _ = exact_ce(adj, 6)
            if ce == 5:
                c6[(m, shape(mask, edges6, 6)[1])] += 1
    print(f"  n=6 紧实例 (ce=5): {sum(c6.values())} 个, 按 (m, 度序列):")
    for k, v in c6.most_common():
        print(f"    m={k[0]} degseq={k[1]}: {v}")
    c7 = Counter()
    for mask in s1["tight"]:
        m, degs, adj = shape(mask, edges7, 7)
        c7[(m, degs)] += 1
    print(f"  n=7 紧实例 (ce=6): {sum(c7.values())} 个, 按 (m, 度序列):")
    for k, v in c7.most_common():
        print(f"    m={k[0]} degseq={k[1]}: {v}")


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "ABCD"
    if "A" in which:
        part_A()
    if "B" in which:
        part_B()
    if "C" in which:
        part_C()
    if "D" in which:
        part_D()
    print("DONE s4", which)
