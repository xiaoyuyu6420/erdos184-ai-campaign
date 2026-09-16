#!/usr/bin/env python3
"""批量攻击 Problem 2 (m<=10) 的最小 open 实例."""
import time
from search import solve, phase_solve
from verifier import verify
from hop44 import verify2_independent


def attack(n, m_list, budget=240):
    t0 = time.time()
    try:
        sol = solve(n, m_list, verbose=False, time_limit=budget)
    except Exception as ex:
        sol = None
    if sol is None:
        return ("NOFIND", time.time() - t0, None)
    seating = phase_solve(n, m_list, sol)
    if seating is None:
        return ("PHASE-FAIL", time.time() - t0, None)
    ok1, _ = verify(n, m_list, seating)
    ok2, _ = verify2_independent(n, m_list, seating)
    return ("PASS" if (ok1 and ok2) else "FAIL", time.time() - t0, seating)


if __name__ == "__main__":
    targets = [
        # (n, m_list, 备注)
        (6,  [2, 4], "(2,4) n=6, n≡6 mod 12 类"),
        (8,  [2, 6], "[2,6] n=8, n≡8 mod 16 类"),
        (8,  [3, 5], "[3,5] n=8"),
        (8,  [4, 4], "[4,4] n=8"),
        (8,  [2, 2, 4], "[2,2,4] n=8"),
        (8,  [2, 3, 3], "[2,3,3] n=8"),
        (8,  [2, 5], "[2,5] n=8, n≡8 mod 14 类"),
        (8,  [3, 4], "[3,4] n=8, n≡8 mod 14 类"),
        (8,  [2, 2, 3], "[2,2,3] n=8"),
        (10, [2, 2, 2, 2, 2], "[2^5] n=10 (T1' 应解, 复核)"),
        (10, [4, 6], "[4,6] n=10, n≡10 mod 20 类"),
        (10, [5, 5], "[5,5] n=10"),
        (10, [2, 2, 6], "[2,2,6] n=10"),
        (10, [2, 3, 5], "[2,3,5] n=10"),
        (10, [2, 4, 4], "[2,4,4] n=10"),
        (10, [3, 3, 4], "[3,3,4] n=10"),
        (10, [2, 2, 2, 4], "[2,2,2,4] n=10"),
        (10, [2, 2, 3, 3], "[2,2,3,3] n=10"),
        (10, [3, 3], "(3,3) n=10, n≡10 mod 12 类"),
        (10, [2, 2, 2], "(2,2,2) n=10, n≡10 mod 12 类"),
        (10, [2, 4], "(2,4) n=10, n≡10 mod 12 类"),
    ]
    results = {}
    for (n, ml, note) in targets:
        status, dt, _ = attack(n, ml)
        results[f"{ml}@n={n}"] = status
        flag = "++" if status == "PASS" else ("--" if status == "NOFIND" else "??")
        print(f"[{flag}] {ml}@n={n} gamma={2*n*(n-1)//sum(ml)} {status} ({dt:.1f}s)  # {note}")
    print("\n汇总:")
    for k, v in results.items():
        print(f"  {k}: {v}")
