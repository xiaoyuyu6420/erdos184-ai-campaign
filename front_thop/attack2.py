#!/usr/bin/env python3
"""NOFIND 实例二次攻坚: 随机重启 + 真 MRV (候选块最少的 need 边优先)."""
import sys, time, random
sys.setrecursionlimit(100000)
from search import all_blocks
from verifier import verify
from hop44 import verify2_independent
import search as S


def attack2(n, m_list, restarts=6, time_per=75.0, seed0=42):
    m = sum(m_list)
    gamma = 2 * n * (n - 1) // m
    all_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    seen_block = {}
    for (edges, cset, solo) in all_blocks(n, m_list):
        key = tuple(sorted((tuple(e) for e in edges)))
        if key not in seen_block:
            seen_block[key] = (key, cset, solo)
    base_list = sorted(seen_block.values(), key=lambda b: b[0])

    rng = random.Random(seed0)
    state = {"use": {e: 0 for e in all_edges}, "sol": [], "nodes": 0,
             "deadline": 0.0, "bl": base_list, "eb": None}

    def ok_block(key):
        cnt = {}
        for e in key:
            cnt[e] = cnt.get(e, 0) + 1
        return all(state["use"][e] + c <= 4 for e, c in cnt.items())

    def dfs(start_idx):
        state["nodes"] += 1
        if state["nodes"] % 256 == 0 and time.time() > state["deadline"]:
            raise TimeoutError
        sol = state["sol"]; use = state["use"]
        if len(sol) == gamma:
            return all(u == 4 for u in use.values())
        r = gamma - len(sol)
        total_need = sum(4 - u for u in use.values())
        if total_need != r * m:
            return False
        for e, u in use.items():
            if 4 - u > 2 * r or u > 4:
                return False
        bl = state["bl"]; eb = state["eb"]
        # 完备剪枝: 每个 need>0 边必须有未来候选块 (不强制下一块覆盖特定边)
        for e in all_edges:
            if 4 - use[e] <= 0:
                continue
            if not any(ok_block(bl[bi][0]) for bi in eb[e] if bi >= start_idx):
                return False
        # 块序非降 (对称破除)
        for bi in range(start_idx, len(bl)):
            key, cset, solo = bl[bi]
            if not ok_block(key):
                continue
            cnt = {}
            for e in key:
                cnt[e] = cnt.get(e, 0) + 1
            for e, c in cnt.items():
                use[e] += c
            sol.append((key, cset, solo))
            if dfs(bi):
                return True
            sol.pop()
            for e, c in cnt.items():
                use[e] -= c
        return False

    for attempt in range(restarts):
        order = list(range(len(base_list)))
        if attempt > 0:
            rng.shuffle(order)
        state["bl"] = [base_list[i] for i in order]
        eb = {e: [] for e in all_edges}
        for bi, (key, _, _) in enumerate(state["bl"]):
            for e in set(key):
                eb[e].append(bi)
        state["eb"] = eb
        state["use"] = {e: 0 for e in all_edges}
        state["sol"] = []
        state["nodes"] = 0
        state["deadline"] = time.time() + time_per
        try:
            if dfs(0):
                return list(state["sol"])
        except TimeoutError:
            pass
    return None


if __name__ == "__main__":
    targets = [
        (8, [2, 5], "[2,5] n=8, n≡8 mod 14"),
        (8, [3, 4], "[3,4] n=8, n≡8 mod 14"),
        (8, [2, 2, 3], "[2,2,3] n=8"),
        (8, [2, 2, 4], "[2,2,4] n=8"),
    ]
    for (n, ml, note) in targets:
        t0 = time.time()
        sol = attack2(n, ml, restarts=6, time_per=75.0)
        if sol is None:
            print(f"[--] {ml}@n={n} 二次攻坚仍 NOFIND ({time.time()-t0:.0f}s) #{note}", flush=True)
            continue
        seating = S.phase_solve(n, ml, sol)
        if seating is None:
            print(f"[??] {ml}@n={n} PHASE-FAIL", flush=True)
            continue
        ok1, _ = verify(n, ml, seating)
        ok2, _ = verify2_independent(n, ml, seating)
        status = "PASS" if (ok1 and ok2) else "FAIL"
        print(f"[{'++' if ok1 and ok2 else '??'}] {ml}@n={n} gamma={2*n*(n-1)//sum(ml)} {status} ({time.time()-t0:.0f}s) #{note}", flush=True)
