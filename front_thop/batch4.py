#!/usr/bin/env python3
"""最后一轮: 大预算粗分解 + 相位局部搜索."""
import time
import search as S
from phase_local import phase_local
from verifier import verify
from hop44 import verify2_independent

targets = [
    (10, [2, 7], "[2,7] n=10, n≡10 mod 18 类"),
    (10, [4, 5], "[4,5] n=10, n≡10 mod 18 类"),
    (10, [5, 5], "[5,5] n=10, n≡10 mod 20 类"),
    (10, [2, 2, 2], "(2,2,2) n=10, n≡10 mod 12 类"),
    (8,  [2, 2, 3], "[2,2,3] n=8, n≡8 mod 14 类"),
]

for (n, ml, note) in targets:
    t0 = time.time()
    sol = S.solve(n, ml, verbose=False, time_limit=280)
    if sol is None:
        print(f"[--] {ml}@n={n} 粗分解 NOFIND ({time.time()-t0:.0f}s) #{note}", flush=True)
        continue
    print(f"粗分解 OK ({time.time()-t0:.0f}s)", flush=True)
    seating = phase_local(n, ml, sol, max_seconds=110)
    if seating is None:
        seating = S.phase_solve(n, ml, sol, time_limit=110)
    if seating is None:
        print(f"[??] {ml}@n={n} 相位失败 ({time.time()-t0:.0f}s)", flush=True)
        continue
    ok1, _ = verify(n, ml, seating)
    ok2, _ = verify2_independent(n, ml, seating)
    print(f"[{'++' if ok1 and ok2 else '??'}] {ml}@n={n} gamma={len(seating)} V1={ok1} V2={ok2} ({time.time()-t0:.0f}s) #{note}", flush=True)
print("BATCH4 DONE")
