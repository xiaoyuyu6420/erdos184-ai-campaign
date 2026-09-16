#!/usr/bin/env python3
"""第三轮精简批量: 修复 phase 超时后, 攻剩余高价值目标."""
import time
import search as S
from verifier import verify
from hop44 import verify2_independent


def attack(n, m_list, search_budget=120):
    sol = S.solve(n, m_list, verbose=False, time_limit=search_budget)
    if sol is None:
        return "NOFIND", None
    try:
        seating = S.phase_solve(n, m_list, sol, time_limit=90.0)
    except TimeoutError:
        return "PHASE-TIMEOUT", None
    if seating is None:
        return "PHASE-FAIL", None
    ok1, _ = verify(n, m_list, seating)
    ok2, _ = verify2_independent(n, m_list, seating)
    return ("PASS" if (ok1 and ok2) else "FAIL"), seating


if __name__ == "__main__":
    targets = [
        (10, [2, 3],   "(2,3) n=10, n≡0 mod 10 类"),
        (8,  [2, 2, 3], "[2,2,3] n=8, n≡8 mod 14"),
        (10, [2, 2, 2], "(2,2,2) n=10, n≡10 mod 12"),
        (10, [2, 4],   "(2,4) n=10, n≡10 mod 12"),
        (10, [2, 7],   "[2,7] n=10, n≡10 mod 18"),
        (10, [4, 5],   "[4,5] n=10, n≡10 mod 18"),
        (10, [2, 2, 5], "[2,2,5] n=10, n≡10 mod 18"),
        (10, [3, 3, 3], "[3,3,3] n=10"),
        (10, [5, 5],   "[5,5] n=10"),
        (10, [3, 6],   "[3,6] n=10"),
        (10, [2, 3, 4], "[2,3,4] n=10"),
        (10, [2, 2, 6], "[2,2,6] n=10"),
        (10, [2, 3, 5], "[2,3,5] n=10"),
        (10, [2, 4, 4], "[2,4,4] n=10"),
        (10, [3, 3, 4], "[3,3,4] n=10"),
        (10, [2, 2, 2, 4], "[2,2,2,4] n=10"),
        (10, [2, 2, 3, 3], "[2,2,3,3] n=10"),
        (10, [2, 2, 2, 3], "[2,2,2,3] n=10"),
    ]
    results = {}
    for (n, ml, note) in targets:
        t0 = time.time()
        try:
            status, _ = attack(n, ml)
        except Exception as ex:
            status = f"ERR:{type(ex).__name__}"
        dt = time.time() - t0
        results[f"{ml}@{n}"] = status
        flag = "++" if status == "PASS" else ("--" if status == "NOFIND" else "??")
        print(f"[{flag}] {ml}@n={n} gamma={2*n*(n-1)//sum(ml)} {status} ({dt:.0f}s)  # {note}", flush=True)
    print("\n汇总:")
    pass_n = sum(1 for v in results.values() if v == "PASS")
    print(f"  PASS {pass_n} / {len(results)}")
    for k, v in results.items():
        if v != "PASS":
            print(f"  非PASS: {k}: {v}")
