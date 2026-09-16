#!/usr/bin/env python3
"""
通用两级搜索引擎 (小实例):
  第 1 级: 粗分解搜索: 4K_n -> gamma 块 [s 孤点 + C_{m1} ⊔ ... ⊔ C_{mt}],
           每条标签边恰用 4 次. 回溯 + 剪枝.
  第 2 级: 相位求解: 每圈每标签 1 bit, 约束 = 每标签对 4 次邻接事件覆盖
           Z_2^2 (4 条人边各一次). 回溯.
  输出 seating -> 双验证器终审.
"""
import sys
from itertools import combinations
from verifier import verify
from hop44 import verify2_independent

sys.setrecursionlimit(100000)


def gen_cycles(points, k):
    """点集 points 中取 k 个的所有循环圈 (规范化: 最小点开头, 去旋转; 保留两个方向).
    返回 (cycle_tuple, edge_set)."""
    out = []
    pts = sorted(points)
    for combo in combinations(pts, k):
        rest = combo[1:]
        # 固定 combo[0] 开头, rest 的所有排列会重复 -> 用规范: 两个方向各取一种
        # 通过全排列生成再规范化 (k 小, 可接受)
        from itertools import permutations
        seen = set()
        for perm in permutations(rest):
            cyc = (combo[0],) + perm
            # 规范化方向: 与其反向中字典序较小者
            rev = (cyc[0],) + tuple(reversed(cyc[1:]))
            key = min(cyc, rev)
            if key in seen:
                continue
            seen.add(key)
            if k == 2:
                # C_2 圈 = 标签对之间的 2 条平行边 (去+回)
                edges = [tuple(sorted((combo[0], rest[0])))] * 2
            else:
                edges = [tuple(sorted((cyc[i], cyc[(i + 1) % k]))) for i in range(k)]
            out.append((cyc, edges))
    return out


def all_blocks(n, m_list, gen_deadline=None):
    """生成所有块: (frozen 边多重集, 圈列表, 孤点列表). 边集用 frozenset 的 tuple.
    gen_deadline: 可选 wall-clock 期限, 超时抛 TimeoutError (保护生成阶段)."""
    import time as _time
    s = n - sum(m_list)
    labels = list(range(n))
    from itertools import combinations as comb
    # 选孤点
    for solo in comb(labels, s):
        rest = [x for x in labels if x not in solo]
        # rest 分成大小 m_list 的组; 同大小相邻组用字典序递增去重 (不丢异大小划分)
        blocks = []
        ml = sorted(m_list)

        def partition(pool, sizes, cur):
            if gen_deadline is not None and _time.time() > gen_deadline:
                raise TimeoutError("block generation budget exhausted")
            if not sizes:
                blocks.append(list(cur))
                return
            k = sizes[0]
            from itertools import combinations as cb
            same_prev = bool(cur) and len(cur[-1]) == k
            for c in cb(pool, k):
                if same_prev and sorted(c) <= list(cur[-1]):
                    continue  # 同大小组: 字典序严格递增, 去置换重复
                rem = [x for x in pool if x not in c]
                partition(rem, sizes[1:], cur + [c])
        partition(rest, ml, [])
        for parts in blocks:
            # 每部分生成圈
            cycle_opts = []
            for c in parts:
                opts = gen_cycles(list(c), len(c))
                cycle_opts.append(opts)
            # 组合 (圈数 t 小)
            def combos(idx, cur):
                if idx == len(cycle_opts):
                    yield list(cur)
                    return
                for (cyc, edges) in cycle_opts[idx]:
                    cur.append((cyc, edges))
                    yield from combos(idx + 1, cur)
                    cur.pop()
            for cset in combos(0, []):
                edges_all = []
                for (_, es) in cset:
                    edges_all.extend(sorted(tuple(sorted(e))) for e in es)
                yield (tuple(edges_all), tuple((cyc, tuple(sorted(es))) for cyc, es in cset), solo)


def solve(n, m_list, max_blocks=None, verbose=False, node_limit=3_000_000, time_limit=600.0):
    import time as _time
    t_start = _time.time()
    m = sum(m_list)
    gamma = 2 * n * (n - 1) // m
    all_edges = []
    for u in range(n):
        for v in range(u + 1, n):
            all_edges.append((u, v))
    use = {e: 0 for e in all_edges}
    # 预生成全部块 (去重 by 边多重集); 生成阶段限时 = 总预算的一半
    seen_block = {}
    try:
        for (edges, cset, solo) in all_blocks(n, m_list, gen_deadline=t_start + time_limit / 2):
            key = tuple(sorted((tuple(e) for e in edges)))
            if key not in seen_block:
                seen_block[key] = (key, cset, solo)
    except TimeoutError:
        if verbose:
            print("  [生成阶段预算耗尽]")
        return None
    block_list = sorted(seen_block.values(), key=lambda b: b[0])
    # 边 -> 包含它的块索引 (用于 MRV)
    edge_blocks = {e: [] for e in all_edges}
    for bi, (key, _, _) in enumerate(block_list):
        for e in set(key):
            edge_blocks[e].append(bi)
    if verbose:
        print(f"  候选块总数: {len(block_list)}, gamma={gamma}")

    sol_blocks = []
    nodes = [0]

    def ok_block(key):
        cnt = {}
        for e in key:
            cnt[e] = cnt.get(e, 0) + 1
        for e, c in cnt.items():
            if use[e] + c > 4:
                return False
        return True

    def commit(key, delta):
        cnt = {}
        for e in key:
            cnt[e] = cnt.get(e, 0) + 1
        for e, c in cnt.items():
            use[e] += c * delta

    def feasible():
        r = gamma - len(sol_blocks)
        for e, u in use.items():
            if 4 - u > 2 * r or u > 4:
                return False
        return True

    def dfs(start_idx):
        nodes[0] += 1
        if nodes[0] > node_limit or _time.time() - t_start > time_limit:
            raise TimeoutError("search budget exhausted")
        if len(sol_blocks) == gamma:
            return all(u == 4 for u in use.values())
        if not feasible():
            return False
        r = gamma - len(sol_blocks)
        total_need = sum(4 - u for u in use.values())
        if total_need != r * m:
            return False
        # 完备剪枝: 每个 need>0 的边必须能被某个未来块 (索引 >= start_idx 且不超容) 覆盖
        for e in all_edges:
            need = 4 - use[e]
            if need <= 0:
                continue
            if not any(ok_block(block_list[bi][0]) for bi in edge_blocks[e] if bi >= start_idx):
                return False
        # 块序非降 (对称破除); 不强制下一块覆盖特定边 (MRV 下一块式剪枝不完备, 已弃用)
        for bi in range(start_idx, len(block_list)):
            key, cset, solo = block_list[bi]
            if not ok_block(key):
                continue
            commit(key, +1)
            sol_blocks.append((key, cset, solo))
            if dfs(bi):
                return True
            sol_blocks.pop()
            commit(key, -1)
        return False

    try:
        found = dfs(0)
    except TimeoutError:
        if verbose:
            print(f"  [预算耗尽 nodes={nodes[0]}]")
        return None
    if not found:
        return None
    return sol_blocks


def phase_solve(n, m_list, sol_blocks, time_limit=120.0):
    """相位求解. 变量: (块id, 圈id, 圈内位置) -> bit.
    约束: 每标签对 (u,v): 其 4 次共同邻接事件 (块,圈,u 前后关系) 的
    (1-eps_u, eps_v) 组合覆盖 Z_2^2. time_limit: 回溯预算 (秒)."""
    import time as _time
    _t0 = _time.time()
    # 收集邻接事件: 对每对标签, list of (var_u, var_v) 要求 (1-a, b) 全域
    events = {}  # (u,v) -> [(var_u, var_v), ...]
    var_of = {}
    nvars = 0
    for bi, (key, cset, solo) in enumerate(sol_blocks):
        for ci, (cyc, es) in enumerate(cset):
            for pos in range(len(cyc)):
                var_of[(bi, ci, pos)] = nvars
                nvars += 1
    for bi, (key, cset, solo) in enumerate(sol_blocks):
        for ci, (cyc, es) in enumerate(cset):
            L = len(cyc)
            for pos in range(L):
                u = cyc[pos]
                v = cyc[(pos + 1) % L]
                uv = (min(u, v), max(u, v))
                vu = var_of[(bi, ci, pos)]
                vv = var_of[(bi, ci, (pos + 1) % L)]
                events.setdefault(uv, []).append((vu, vv, u, v))
    assign = [0] * nvars

    def compatible(uv, elist):
        """检查已赋值部分: 人边像 (min侧, max侧) 不重复.
        事件 u->v 的边 = (u^{1-e_u}, v^{e_v}); 换算到 (min,max) 坐标:
        u<v: (1-a, b);  u>v: (b, 1-a)."""
        seen = set()
        for (vu, vv, u, v) in elist:
            a = assign[vu]
            b = assign[vv]
            pair = (1 - a, b) if u < v else (b, 1 - a)
            if pair in seen:
                return False
            seen.add(pair)
        return True

    # 简单回溯: 按约束组聚类变量排序
    order = []
    seenv = set()
    for uv, elist in sorted(events.items()):
        for (vu, vv, u, v) in elist:
            if vu not in seenv:
                seenv.add(vu)
                order.append(vu)
            if vv not in seenv:
                seenv.add(vv)
                order.append(vv)
    for i in range(nvars):
        if i not in seenv:
            order.append(i)

    inv_order = {v: i for i, v in enumerate(order)}
    # 约束在 order 前缀下的完整性: 当组内变量全赋值时检查

    def bt(k):
        if k == len(order):
            return True
        if _time.time() - _t0 > time_limit:
            raise TimeoutError("phase budget exhausted")
        var = order[k]
        for val in (0, 1):
            assign[var] = val
            good = True
            for uv, elist in events.items():
                # 检查该约束是否所有变量已赋 (在 order 中位置 <= k)
                all_done = True
                for (vu, vv, u, v) in elist:
                    if inv_order[vu] > k or inv_order[vv] > k:
                        all_done = False
                        break
                if all_done and not compatible(uv, elist):
                    good = False
                    break
            if good and bt(k + 1):
                return True
        assign[var] = 0
        return False

    if not bt(0):
        return None

    def bit(bi, ci, pos):
        return assign[var_of[(bi, ci, pos)]]

    # 生成 seating
    nights = []
    for bi, (key, cset, solo) in enumerate(sol_blocks):
        tables = []
        used = set()
        for ci, (cyc, es) in enumerate(cset):
            L = len(cyc)
            table = []
            for pos in range(L):
                p = cyc[pos]
                e = bit(bi, ci, pos)
                table.extend([2 * p + e, 2 * p + 1 - e])
            tables.append(table)
            used.update(cyc)
        for p in solo:
            tables.append([2 * p, 2 * p + 1])
            used.add(p)
        nights.append(tables)
    return nights


def run_case(n, m_list, label=""):
    print(f"=== 搜索 HOP(2^<{n-sum(m_list)}>, {m_list}), n={n} {label} ===")
    sol = solve(n, m_list, verbose=True)
    if sol is None:
        print("  粗分解: 未找到 (搜索空间内无解或超时)")
        return False
    print(f"  粗分解找到: {len(sol)} 块")
    seating = phase_solve(n, m_list, sol)
    if seating is None:
        print("  相位求解失败")
        return False
    ok1, msg1 = verify(n, m_list, seating)
    ok2, errs2 = verify2_independent(n, m_list, seating)
    tag = "PASS" if (ok1 and ok2) else "FAIL"
    print(f"  V1={ok1} V2={ok2} [{tag}] {msg1[-1] if ok1 else msg1}")
    if not ok2:
        for e in errs2[:5]:
            print("   V2:", e)
    return ok1 and ok2


if __name__ == "__main__":
    import time
    cases = [
        (6, [3, 3], "(6,6) n=6, n≡6 mod 12 类"),
        (6, [2, 3], "(2,3) n=6, n≡6 mod 10 类"),
        (6, [2, 2, 2], "(2,2,2) n=6 (复核 T1' 路径)"),
    ]
    for (n, ml, lab) in cases:
        t0 = time.time()
        ok = run_case(n, ml, lab)
        print(f"  用时 {time.time()-t0:.1f}s -> {'SOLVED' if ok else 'FAILED'}\n")
