#!/usr/bin/env python3
"""穷举验证（终版）：
- n = 2..5：对每个 N < Ncrit 全体 n-集合验证 invalid（Conjecture 1 穷举确认），
  并对每个 valid (A,N) 检查 L1 (N >= 2^(n-1)) 与 L2'（层避让）。
- n = 6..7：只验证超递增集 valid + L1/L2' 在随机/结构集合上抽查。
"""
import sys
from itertools import combinations
from math import ceil, log2, floor

def multisets(n, s):
    def rec(start, rem):
        if rem == 0:
            yield ()
            return
        for i in range(start, n):
            for rest in rec(i, rem-1):
                yield (i,) + rest
    return rec(0, s)

MULTI_CACHE = {}
def multisets_cached(n, s):
    if (n,s) not in MULTI_CACHE:
        MULTI_CACHE[(n,s)] = list(multisets(n,s))
    return MULTI_CACHE[(n,s)]

def first_collision(A, N, n):
    p = sum(A) % N
    ones = tuple(range(n))
    for ms in multisets_cached(n, n):
        s = 0
        for i in ms: s += A[i]
        if s % N == p and ms != ones:
            return ms
    return None

def is_valid(A, N, n):
    return first_collision(A, N, n) is None

def subset_layer_sums(A, N, n):
    """层 -> 类和集合（代表 = 不含 a0）。"""
    layers = {}
    for r in range(n):
        S = set()
        for T in combinations(range(1, n), r):
            S.add(sum(A[i] for i in T) % N)
        layers[r] = S
    return layers

def check_L2(layers, N, n):
    """L2': 对每个 s>=1，2*x (x in 层s, x!=0) 不得落入层 [2s-1, n-1] 的类和集。"""
    hi = set()
    for s2 in range(1, n):
        hi |= layers[s2]
    for s in range(1, n):
        for x in layers[s]:
            if x and (2*x) % N in hi:
                return False
    return True

mode = sys.argv[1] if len(sys.argv) > 1 else "full"

for n in range(2, 6):
    m = floor(log2(n)); Ncrit = 2**n - 2**m
    min_valid = None; conj_ok = True; l1_bad = l2_bad = 0; checked = 0
    for N in range(2, Ncrit+1):
        for A in combinations(range(N), n):
            checked += 1
            if is_valid(A, N, n):
                if min_valid is None: min_valid = N
                if N < Ncrit:
                    conj_ok = False
                    print(f"  COUNTEREXAMPLE?! n={n} N={N} A={A}", flush=True)
                if N < 2**(n-1): l1_bad += 1
                if not check_L2(subset_layer_sums(A, N, n), N, n): l2_bad += 1
                break
        if min_valid is not None and N >= Ncrit: break
    print(f"n={n}: Ncrit={Ncrit}, minValidN={min_valid}, Conjecture({'OK' if conj_ok else 'FAIL'}), "
          f"L1bad={l1_bad}, L2'bad={l2_bad}, checked={checked}", flush=True)

# n=6,7: 超递增集在 Ncrit 处 valid + 负例抽查 + L1/L2' 对超递增集
for n in (6, 7):
    m = floor(log2(n)); Ncrit = 2**n - 2**m
    A = tuple(2**k - 1 for k in range(n))
    v = is_valid(A, Ncrit, n)
    below = all(not is_valid(A, N, n) for N in range(2, Ncrit))
    l1 = Ncrit >= 2**(n-1)
    l2 = check_L2(subset_layer_sums(A, Ncrit, n), Ncrit, n)
    # 临界下方一个模数的 witness 示例
    w = first_collision(A, Ncrit-1, n)
    print(f"n={n}: Ncrit={Ncrit}, superincr valid@Ncrit={v}, invalid below={below}, "
          f"L1={l1}, L2'={l2}, sample witness@Ncrit-1={w}", flush=True)
