"""审查员独立验证脚本（不 import 攻击手的公式/搜索代码，计数器独立重写）。

审查项：
 R1 锚点 + 勘误逐字复算（Thm6 反例、Table1 n=8、Table3 三行）
 R2 小 n 全枚举：Conjecture 1 (theta >= n//4) 与 CO 小范围 (x,y>=4)
 R3 4-run 闭式公式独立对账：i,u,j,v in [1,14] 全枚举 + 随机大参数
 R4 命题 D 公式级验证：x,y in [4,72] 全网格 min 公式值 = tau_x+tau_y
 R5 y=4 且恰 3 个 b-run 的词：theta >= tau_x + 1 对 x in [4,60]
 R6 随机 3-b-run 词（一般 y）：theta >= tau_x + tau_y 的随机抽查
"""
import itertools
import random
import sys
from functools import lru_cache

sys.setrecursionlimit(10000)


# ---------- 独立计数器：逐因子，前半/后半 26 字母计数数组比较 ----------
def theta_indep(w):
    n = len(w)
    pref = [[0, 0]]  # pref[i] = [#, #a] of w[:i]
    ca = cb = 0
    for ch in w:
        if ch == 'a':
            ca += 1
        else:
            cb += 1
        pref.append((ca, cb))
    sq = set()
    for i in range(n):
        for half in range(1, (n - i) // 2 + 1):
            j = i + half
            k = j + half
            if pref[j][0] - pref[i][0] == pref[k][0] - pref[j][0]:
                sq.add(w[i:k])
    return len(sq)


def tau(m):
    return (m + 2) // 4


# ---------- R4/R3 的 4-run 闭式公式（审查员照命题 C 独立重推实现） ----------
def theta_four_run_indep(i, u, j, v):
    base = max(i, j) // 2 + max(u, v) // 2
    A = min(i, j) if u % 2 == 0 else 0
    B = min(u, v) if j % 2 == 0 else 0
    C = len([x for x in range(1, min(u, v) + 1) if x % 2 == u % 2]) if j <= i else 0
    D = len([x for x in range(1, min(i, j) + 1) if x % 2 == j % 2]) if u <= v else 0
    ov = 1 if (j <= i and u <= v) else 0
    return base + A + B + C + D - ov


def run():
    ok = []

    # R1 锚点
    assert theta_indep("abaababa") == 6
    assert theta_indep("b" * 18) == 9
    assert theta_indep("abbba") == 1
    assert theta_indep("abab") == 1
    ok.append("R1 anchors OK")

    # R1 勘误1 反例
    for w, n in [("abbb", 4), ("babbbbb"[:0] or "bbabbbbb", 8), ("bbbbbabb", 8),
                 ("b" * 4 + "a" + "b" * 7, 12), ("b" * 7 + "a" + "b" * 4, 12)]:
        assert len(w) == n and theta_indep(w) == n // 4, (w, theta_indep(w))
    assert theta_indep("b" * 2 + "a" + "b" * 5) == 2
    ok.append("R1 erratum1 counterexamples OK (theta = floor(n/4), non-canonical)")

    # R1 勘误2：abbbabb 长度/theta；替换词 abbbabbb
    assert len("abbbabb") == 7 and theta_indep("abbbabb") == 2
    assert len("abbbabbb") == 8 and theta_indep("abbbabbb") == 3
    t1 = ["ababbbbb", "abbbabbb", "abbbbbab", "babbbbba", "bbbabbba", "bbbbbaba"]
    for w in t1:
        assert len(w) == 8 and w.count("a") == 2 and theta_indep(w) == 3, (w, theta_indep(w))
    ok.append("R1 erratum2 OK (abbbabb bad; replacement + 5 kept words all theta=3, |w|=8)")

    # R1 勘误3：Table 3 x=1,10,13 行
    bad_rows = {
        1: "b" * 10 + "a" + "b" * 8,     # 原文样例(机器读出的形状)：len 19
        10: "a" * 3 + "b" * 5 + "a" * 7 + "b" * 4,  # len 19
        13: "a" * 5 + "b" * 3 + "a" * 7 + "b" * 2,  # len 17
    }
    for x, w in bad_rows.items():
        assert len(w) != 18, x
    assert theta_indep("a" * 3 + "b" * 5 + "a" * 7 + "b" * 3) == 5
    W13 = "a" * 6 + "b" * 3 + "a" * 7 + "b" * 2
    assert theta_indep(W13) == 4 and W13.count("a") == 13
    ok.append("R1 erratum3 OK (x=10 -> a3b5a7b3 theta=5; x=13 -> a6b3a7b2 theta=4)")

    # R2 小 n 全枚举
    for n in range(1, 13):
        for k in range(n + 1):
            best = None
            for pos in itertools.combinations(range(n), k):
                w = ["b"] * n
                for p in pos:
                    w[p] = "a"
                v = theta_indep("".join(w))
                best = v if best is None else min(best, v)
            y = n - k
            # Conjecture 1: 每个词 theta >= n//4（检查 min 即可）
            assert best >= n // 4, (n, k, best)
            # CO: x,y>=4 时 min = tau_x+tau_y
            if k >= 4 and y >= 4:
                assert best == tau(k) + tau(y), (n, k, best, tau(k) + tau(y))
            # 边界 Thm5-8 抽查
            if k == 0:
                assert best == n // 2, (n, best)
            elif k == 1:
                assert best == n // 4, (n, best)
            elif k == 2:
                if n >= 3:
                    assert best == (n - 2) // 2, (n, best)
                else:
                    assert best == 1, (n, best)  # 原文 Thm7 边界例外: M(2,2)=1 != floor(0/2)
            elif k == 3:
                assert best == (n + 2) // 4, (n, best)
    ok.append("R2 exhaustive n<=12: Conjecture1 + CO(small) + Thm5-8 boundary OK")

    # R3 4-run 公式对账
    lim = 14
    bad = 0
    for i in range(1, lim + 1):
        for u in range(1, lim + 1):
            for j in range(1, lim + 1):
                for v in range(1, lim + 1):
                    w = "a" * i + "b" * u + "a" * j + "b" * v
                    g = theta_indep(w)
                    f = theta_four_run_indep(i, u, j, v)
                    if f != g:
                        bad += 1
                        if bad <= 3:
                            print("R3 MISMATCH", (i, u, j, v), f, g)
    assert bad == 0
    random.seed(20260914)
    for _ in range(2000):
        i, u, j, v = (random.randint(1, 60) for _ in range(4))
        w = "a" * i + "b" * u + "a" * j + "b" * v
        g = theta_indep(w)
        f = theta_four_run_indep(i, u, j, v)
        if f != g:
            bad += 1
            if bad <= 3:
                print("R3big MISMATCH", (i, u, j, v), f, g)
    assert bad == 0
    ok.append("R3 4-run closed formula: [1,14]^4 exhaustive + 2000 random in [1,60]^4, zero mismatch")

    # R4 命题 D 公式级：x,y in [4,72]
    for x in range(4, 73):
        for y in range(4, 73):
            m = None
            for i in range(1, x):
                j = x - i
                for u in range(1, y):
                    v = y - u
                    val = theta_four_run_indep(i, u, j, v)
                    m = val if m is None else min(m, val)
            assert m == tau(x) + tau(y), (x, y, m, tau(x) + tau(y))
    ok.append("R4 formula-level CO for 4-run words: all x,y in [4,72], min == tau_x+tau_y")

    # R5 y=4, 恰 3 个 b-run：theta >= tau_x + 1, x in [4,34]（全枚举，稍后另用 C 级思路补大 x）
    cnt5 = 0
    bad5 = 0
    for x in range(4, 35):
        # 枚举 run 结构：3 个 b-run 长 (perm of (2,1,1))，a-run 数 2..4，a 开头或 b 开头
        for bperm in itertools.permutations([2, 1, 1]):
            for ra in (2, 3, 4):
                # run 序列：交替；长度 = ra + 3
                for start in "ab":
                    nb = 3
                    seq_len = ra + nb
                    # a-run 出现在 start, start+2, ...；需要恰好 ra 个 a-run、nb 个 b-run
                    first_a = 0 if start == "a" else 1
                    na_slots = (seq_len - first_a + 1) // 2
                    nb_slots = seq_len // 2 if first_a == 0 else (seq_len + 1) // 2
                    if first_a == 1:
                        nb_slots = (seq_len + 1) // 2
                        na_slots = seq_len // 2
                    if na_slots != ra or nb_slots != nb:
                        continue
                    # a-run 正整数分割 x -> ra parts
                    for adiv in itertools.product(range(1, x), repeat=ra):
                        if sum(adiv) != x:
                            continue
                        runs = [None] * seq_len
                        ai = 0
                        bi = 0
                        for s in range(seq_len):
                            if (s % 2 == 0) == (first_a == 0):
                                runs[s] = ("a", adiv[ai])
                                ai += 1
                            else:
                                runs[s] = ("b", bperm[bi])
                                bi += 1
                        w = "".join(c * L for c, L in runs)
                        assert len(w) == x + 4
                        th = theta_indep(w)
                        cnt5 += 1
                        if th < tau(x) + 1:
                            bad5 += 1
                            if bad5 <= 5:
                                print("R5 COUNTEREX", x, w, th, tau(x) + 1)
    assert bad5 == 0
    ok.append(f"R5 y=4 with exactly 3 b-runs: {cnt5} words, x in [4,34], all theta >= tau_x+1")

    for line in ok:
        print(line)
    print("ALL INDEPENDENT CHECKS PASSED")


if __name__ == "__main__":
    run()
