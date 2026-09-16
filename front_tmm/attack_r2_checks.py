#!/usr/bin/env python3
"""R2 攻击的一致性检查（防自欺）：
(1) 引理 A（MC 预算判据）⟺ 原始 multiset-valid 定义：n=2..4 全穷举 + n=5..7 随机抽样；
(2) 定理 B（二倍记账下界）：N ≥ 2^(n-1) + (n-2)（N 偶）/ 2^(n-1) + (n-1)（N 奇）
    在全部遇到的 valid (A,N) 上零违反（含超递增锚点 n=5..8）；
(3) 定理 3-s1（2*b_i ≢ b_j, i≠j≥1）在全部 valid (A,N) 上零违反；
(4) T-02 推论 4 的「+½C(n-1,⌊n/2⌋)」增量审计：数 valid 集的 |COMP| 是否达到该值
    （预期：达不到 → 145 无依据的实证旁证）。
"""
import random
from itertools import combinations

# ---------- 复用 verify_tmm.py 的原始定义（独立拷贝，避免其顶层主循环） ----------
def multisets(n, s):
    def rec(start, rem):
        if rem == 0:
            yield ()
            return
        for i in range(start, n):
            for rest in rec(i, rem - 1):
                yield (i,) + rest
    return rec(0, s)

MULTI_CACHE = {}
def multisets_cached(n, s):
    if (n, s) not in MULTI_CACHE:
        MULTI_CACHE[(n, s)] = list(multisets(n, s))
    return MULTI_CACHE[(n, s)]

def is_valid(A, N, n):
    p = sum(A) % N
    ones = tuple(range(n))
    for ms in multisets_cached(n, n):
        s = 0
        for i in ms:
            s += A[i]
        if s % N == p and ms != ones:
            return False
    return True

# ---------- 引理 A：MC 预算判据 ----------
def sums_upto(elems, k, N):
    """elems 中可重复取 ≤k 个数的全部和（mod N），含空和 0。"""
    reach = {0}; exact = {0}
    for _ in range(k):
        exact = {(s + e) % N for s in exact for e in elems}
        reach |= exact
    return reach

def mc_valid(B, N):
    """A=(0,)+B valid mod N ⟺ 每个非空 Q⊆B：Σ_Q ∉ sums_{≤|Q|+1}(B∖Q)。"""
    m = len(B)
    for q in range(1, m + 1):
        budget = q + 1
        for Q in combinations(range(m), q):
            Qs = set(Q)
            elems = tuple(B[i] for i in range(m) if i not in Qs)
            delta = sum(B[i] for i in Q) % N
            if delta in sums_upto(elems, budget, N):
                return False
    return True

def floordig2(n):
    return n.bit_length() - 1

def main():
    random.seed(20260913)
    print("== (1) MC 判据 ⟺ 原始定义 ==", flush=True)
    mismatch = tested = 0
    valid_found = []   # (n, N, A)
    for n in range(2, 5):
        Ncrit = 2**n - 2**floordig2(n)
        for N in range(2, Ncrit + 3):          # 多扫两个 N 以捕捉 valid 正例
            for A in combinations(range(N), n):
                v1 = is_valid(A, N, n)
                # MC 判据要求 a0=0 规范化（平移不变，引理 0）
                B = tuple(sorted((a - A[0]) % N for a in A[1:]))
                v2 = mc_valid(B, N)
                tested += 1
                if v1 != v2:
                    mismatch += 1
                    if mismatch <= 5:
                        print(f"  MISMATCH n={n} N={N} A={A} raw={v1} mc={v2}", flush=True)
                if v1:
                    valid_found.append((n, N, (0,) + B))
    for n in (5, 6, 7):
        Ncrit = 2**n - 2**floordig2(n)
        for _ in range(300 if n < 7 else 80):
            N = random.randint(max(n, 2), Ncrit + 2)
            A = tuple(sorted(random.sample(range(N), n)))
            v1 = is_valid(A, N, n)
            B = tuple(sorted((a - A[0]) % N for a in A[1:]))
            v2 = mc_valid(B, N)
            tested += 1
            if v1 != v2:
                mismatch += 1
                if mismatch <= 5:
                    print(f"  MISMATCH(sample) n={n} N={N} A={A} raw={v1} mc={v2}", flush=True)
            if v1:
                valid_found.append((n, N, (0,) + B))
    print(f"  tested={tested}, mismatch={mismatch}", flush=True)

    # 超递增锚点 n=5..8：论文已证 valid@Ncrit —— MC 判据必须复现
    print("== 超递增锚点（论文 Theorem A）==", flush=True)
    for n in range(5, 9):
        Ncrit = 2**n - 2**floordig2(n)
        A = tuple(2**k - 1 for k in range(n))
        v_raw = is_valid(A, Ncrit, n)
        v_mc = mc_valid(A[1:], Ncrit)
        print(f"  n={n} Ncrit={Ncrit} raw_valid={v_raw} mc_valid={v_mc}", flush=True)
        if v_raw:
            valid_found.append((n, Ncrit, A))

    print("== (2) 定理 B 下界（even: 2^(n-1)+n-2 / odd: 2^(n-1)+n-1）==", flush=True)
    tb_bad = 0
    for (n, N, A) in valid_found:
        need = 2**(n - 1) + (n - 2 if N % 2 == 0 else n - 1)
        if N < need:
            tb_bad += 1
            print(f"  THEOREM-B VIOLATION n={n} N={N} A={A}", flush=True)
    print(f"  valid sets checked={len(valid_found)}, violations={tb_bad}", flush=True)

    print("== (3) 定理 3-s1（2*b_i ≠ b_j）on valid sets ==", flush=True)
    s1_bad = 0
    for (n, N, A) in valid_found:
        for i in range(1, n):
            for j in range(1, n):
                if i != j and (2 * A[i]) % N == A[j] % N:
                    s1_bad += 1
                    print(f"  S1 VIOLATION n={n} N={N} A={A} i={i} j={j}", flush=True)
    print(f"  violations={s1_bad}", flush=True)

    print("== (4) T-02 推论4 增量审计：valid 集的 |COMP| vs ½C(n-1,⌊n/2⌋) ==", flush=True)
    import math
    under = over = 0
    for (n, N, A) in valid_found:
        comp_size = N - 2**(n - 1)
        claim = 0.5 * math.comb(n - 1, n // 2)
        if comp_size >= claim:
            over += 1
        else:
            under += 1
    print(f"  valid sets with |COMP| ≥ ½C(n-1,⌊n/2⌋): {over};  < : {under}", flush=True)
    print("  （注：此审计只说明 145 计数与 n≤5 数据相容，不构成对其推导的辩护；")
    print("    反驳在正文：2S_s 的像可合法落入低层槽位，增量无法全额计入。）", flush=True)

if __name__ == "__main__":
    main()
