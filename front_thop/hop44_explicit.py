#!/usr/bin/env python3
"""
(4,4) 类显式构造器 (纯模式, 无搜索) —— 对应报告中的定理 T1 的构造性证明.

标签层分解方案:
  [偶] K_n 有 1-factorization F_1..F_{n-1} (标准轮换构造, n 偶).
       2K_n = 每个匹配 2 份. 匹配对 (F_{2i-1}, F_{2i}) 两轮 (第一份/第二份).
       对 (P,Q): 并是偶圈(>=4)的并; 循环边序配对 (e1,e3),(e2,e4),...
       末段按 6-圈模式收尾.
  [奇] 2K_n = 差圈 C_d x2 份 (d=1..(n-1)/2, C_d 的边 e_i={i,i+d}).
       圈对 (C_d, C_d') 用平移 a: e_i 配 e_{i+a}, a 避开 {0, d, -d'} (同差时
       即避开 {0,±d}), n>=5 可行. 圈两两配对: 共 n-1 个圈 (偶数).
相位提升: 每对标签第 k 次同桌用相位 k mod 2 -> 4 条人边全覆盖.
"""
from verifier import verify
from hop44 import verify2_independent


# ---------- 偶数 n: 1-factorization ----------

def factorization(n):
    """标准轮换 1-factorization of K_n, n 偶. 返回匹配列表 (每匹配 = 边列表)."""
    # 顶点 Z_{n-1} U {inf}; 轮换法
    matchings = []
    for r in range(n - 1):
        m = [(n - 1, r)]
        for k in range(1, n // 2):
            m.append(((r + k) % (n - 1), (r - k) % (n - 1)))
        matchings.append(sorted(tuple(sorted(mm)) for mm in m))
    return matchings


def circle_pair_groups(P, Q):
    """两个无公共边的匹配 P,Q; 并是偶圈并. 返回重组后的组列表 (每组 2 条不交边)."""
    adj = {}
    for (u, v) in P + Q:
        adj.setdefault(u, []).append(v)
        adj.setdefault(v, []).append(u)
    seen = set()
    groups = []
    for start in adj:
        if start in seen:
            continue
        # 走圈
        cycle = [start]
        prev, cur = None, start
        while True:
            nxts = [x for x in adj[cur] if x != prev]
            nxt = nxts[0]
            if nxt == start:
                break
            cycle.append(nxt)
            seen.add(nxt)
            prev, cur = cur, nxt
        seen.add(start)
        L = len(cycle)
        es = [(cycle[i], cycle[(i + 1) % L]) for i in range(L)]
        # 配对: L≡0 mod4 -> (e0,e2),(e1,e3),(e4,e6),...
        #        L≡2 mod4 -> 前 L-6 按 4-模式, 末 6 条 (e_{L-6},e_{L-4}),(e_{L-5},e_{L-3}),(e_{L-2},e_{L-1})
        #   检查末 6 模式: e_{L-6}={a,a+1},e_{L-4}={a+2,a+3} 不交; e_{L-5}={a+1,a+2},e_{L-3}={a+3,a+4} 不交;
        #   e_{L-2}={a+4,a+5}, e_{L-1}={a+5,a+0}? 共享 a+5 ✗!
        # 改用 6-圈模式 (相对段起点): (f0,f2),(f1,f4),(f3,f5): f4={4,5},f3={3,4}? 共享 ✗
        # 正确 6 模式 (验证): (f0,f2),(f1,f3)?? f1={1,2},f3={3,4} 不交 ✓, f0={0,1},f2={2,3} ✓ -> 剩 f4={4,5},f5={5,0} 共享 ✗
        # 用 (f0,f2),(f1,f4),(f3,f5): f1={1,2},f4={4,5} ✓; f3={3,4},f5={5,0} ✓; f0={0,1},f2={2,3} ✓  全部不交 ✓
        pairs = []
        if L % 4 == 0:
            for j in range(0, L, 4):
                pairs.append((es[j], es[j + 2]))
                pairs.append((es[j + 1], es[j + 3]))
        else:  # L ≡ 2 mod 4, L >= 6
            for j in range(0, L - 6, 4):
                pairs.append((es[j], es[j + 2]))
                pairs.append((es[j + 1], es[j + 3]))
            b = L - 6
            pairs.append((es[b], es[b + 2]))
            pairs.append((es[b + 1], es[b + 4]))
            pairs.append((es[b + 3], es[b + 5]))
        for (x, y) in pairs:
            if set(x) & set(y):
                raise RuntimeError(f"圈重组共点: {x} {y} cycle={cycle}")
            groups.append((tuple(sorted(x)), tuple(sorted(y))))
    return groups


def explicit_groups_even(n):
    facs = factorization(n)
    groups = []
    # 第一份: (F0,F1),(F2,F3),...; 第二份: (F1,F2),(F3,F4),...,(F_{n-2},F_{n-1})
    # 需覆盖 2(n-1) 个匹配副本各一次 -> 第一份用 (0,1),(2,3)..(n-2,n-1)? n-1 奇!
    # n 偶 -> n-1 奇: 第一份配 (0,1),(2,3),...,(n-4,n-3) 共 (n-2)/2 对, 剩 F_{n-2},F_{n-1}
    # 第二份配 (F_{n-2},F_{n-1}) 及错位对 (F1,F2),(F3,F4),...,(F_{n-4},F_{n-3})
    # 覆盖检查: 第一份 {F0..F_{n-3}}, 第二份 {F1..F_{n-1}} -> F0 只一次 ✗ 每个 factor 应 2 次.
    # 改: 第一份 (F0,F1),(F2,F3),...,(F_{n-2},F_{n-1}) 用 n/2 对 (n 偶 -> n-1 奇, 最后配 (F_{n-2},F_{n-1}))
    #     即 (F0,F1),(F2,F3),...,(F_{n-3},F_{n-2}) + (F_{n-1} ?) n-1 奇数个配不完.
    # 干脆: 副本1 配对 (F0,F1),(F2,F3),...,(F_{n-3},F_{n-2}) + (F_{n-1} 无伴!)
    # 解决: 两个副本统一排成环: 对 i=0..n-2: 副本A(F_i) 与 副本B(F_{(i+1) mod (n-1)}) 配对
    #   -> 每个 F 恰在 2 个对里 (一次作A一次作B) ✓ 总 n-1 对 ✓
    for i in range(n - 1):
        P, Q = facs[i], facs[(i + 1) % (n - 1)]
        # P,Q 不同 factor -> 无公共边; 并是 2-正则 n 点图 = 偶圈并 ✓
        groups.extend(circle_pair_groups(P, Q))
    return groups


# ---------- 奇数 n: 差圈 ----------

def explicit_groups_odd(n):
    """2K_n = 差圈 C_d x2. 圈配对: (C_d^A, C_d^B) 同差, 平移 a 避开 {0, ±d}."""
    groups = []
    half = (n - 1) // 2
    for d in range(1, half + 1):
        # 选 a: 最小正整数 ∉ {0, d, n-d} mod n
        a = next(t for t in range(1, n) if t not in (d, (n - d) % n))
        for i in range(n):
            e1 = ((i) % n, (i + d) % n)
            e2 = ((i + a) % n, (i + a + d) % n)
            if set(e1) & set(e2):
                raise RuntimeError(f"奇构造共点: n={n} d={d} a={a} i={i}")
            groups.append((tuple(sorted(e1)), tuple(sorted(e2))))
    return groups


def groups_to_seating(n, groups):
    seen = {}
    nights = []
    for (e1, e2) in groups:
        tables = []
        used = set()
        for (u, v) in (e1, e2):
            key = (min(u, v), max(u, v))
            c = seen.get(key, 0)
            if c > 1:
                raise RuntimeError(f"标签对 {key} 同桌 >2 次")
            alpha = c % 2
            seen[key] = c + 1
            a, b = min(u, v), max(u, v)
            tables.append([2 * a, 2 * a + 1, 2 * b + alpha, 2 * b + 1 - alpha])
            used.update((u, v))
        for p in range(n):
            if p not in used:
                tables.append([2 * p, 2 * p + 1])
        nights.append(tables)
    # 完整性检查: 每标签对恰 2 次
    bad = [k for k, c in seen.items() if c != 2]
    if bad:
        raise RuntimeError(f"标签对次数 != 2: {bad[:5]}")
    return nights


if __name__ == "__main__":
    print("=== T1 显式构造 (纯模式) 双验证器终审 ===")
    results = {}
    for n in range(4, 31):
        if n % 2 == 0:
            groups = explicit_groups_even(n)
        else:
            groups = explicit_groups_odd(n)
        seating = groups_to_seating(n, groups)
        assert len(groups) == n * (n - 1) // 2, f"组数 {len(groups)} != {n*(n-1)//2}"
        ok1, msg1 = verify(n, [2, 2], seating)
        ok2, errs2 = verify2_independent(n, [2, 2], seating)
        tag = "PASS" if (ok1 and ok2) else "FAIL"
        results[n] = tag
        print(f"n={n} (s={n-4}, gamma={len(seating)}): V1={ok1} V2={ok2} [{tag}]")
        if not (ok1 and ok2):
            print("   ", msg1)
            for e in errs2[:3]:
                print("    V2:", e)
    print("\n汇总:", results)
