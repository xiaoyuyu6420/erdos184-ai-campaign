#!/usr/bin/env python3
"""
T1' 定理验证: 全 4 人桌 HOP(2^<s>, 4^<t>), n = s+2t 偶且 t | n/2.
构造: K_n 1-factorization (n-1 个匹配, 每匹配 n/2 边), 每匹配切成 n/(2t) 块,
每块 t 条边 = 一晚 t 张 4 人桌; 每匹配 2 份 -> 每标签对恰 2 块 -> 相位互补.
"""
from verifier import verify
from hop44 import verify2_independent
from hop44_explicit import factorization


def groups_to_seating_general(n, groups):
    """每组 = 任意条标签边 (每条 = 一张 4 人桌); 每对标签全程恰 2 次出现."""
    seen = {}
    nights = []
    for grp in groups:
        tables = []
        used = set()
        for (u, v) in grp:
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
    bad = [k for k, c in seen.items() if c != 2]
    if bad:
        raise RuntimeError(f"标签对次数 != 2: {bad[:5]}")
    return nights


def groups_uniform4(n, t):
    facs = factorization(n)
    groups = []
    for F in facs:
        for rep in range(2):  # 2 份副本
            for j in range(0, len(F), t):  # n/2 边按 t 切块
                groups.append(tuple(sorted(F[j:j + t])))
    return groups


if __name__ == "__main__":
    print("=== T1': HOP(2^<s>, 4^<t>), n 偶, t | n/2 ===")
    results = {}
    for (n, t) in [(6, 3), (8, 2), (8, 4), (10, 5), (12, 2), (12, 3), (12, 4), (12, 6),
                   (14, 7), (16, 2), (16, 4), (16, 8), (18, 3), (18, 9), (20, 4), (20, 10),
                   (6, 1), (8, 1), (10, 1)]:
        if n % 2 != 0 or (n // 2) % t != 0:
            continue
        m_list = [2] * t
        groups = groups_uniform4(n, t)
        gamma_expected = n * (n - 1) // t  # m = 2t, gamma = 2n(n-1)/m
        assert len(groups) == gamma_expected, f"组数 {len(groups)} != {gamma_expected}"
        seating = groups_to_seating_general(n, groups)
        ok1, msg1 = verify(n, m_list, seating)
        ok2, errs2 = verify2_independent(n, m_list, seating)
        tag = "PASS" if (ok1 and ok2) else "FAIL"
        results[(n, t)] = tag
        print(f"n={n} t={t} (s={n-2*t}, m={2*t}, gamma={len(seating)}): "
              f"V1={ok1} V2={ok2} [{tag}]")
        if not (ok1 and ok2):
            print("   ", msg1[:3])
            for e in errs2[:3]:
                print("    V2:", e)
    print("\n汇总:", results)
