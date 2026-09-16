"""验证 2604.23188 的定理与表格。

1. Thm 12: theta(W(x,y)) == t_x + t_y，且 W 中全部为 trivial（对网格 (x,y) 全查）。
2. Thm 5/6/7/8: M(0,n), M(1,n), M(2,n), M(3,n) 公式 vs 全枚举（小 n）。
3. Tables 1-3：论文列出的词是否达到声称计数；且声称计数是否等于真最小值。
"""
import itertools
from absq import theta_naive, theta_prefix, effective_word, t_of, trivial_count_in_word


def all_words_with_k_a(n, k):
    for pos in itertools.combinations(range(n), k):
        w = ['b'] * n
        for p in pos:
            w[p] = 'a'
        yield ''.join(w)


def M_exact(n, k):
    """全枚举：Parikh (k, n-k) 下 theta 的真最小值 + 全部最小词。"""
    best, words = None, []
    for w in all_words_with_k_a(n, k):
        v = theta_prefix(w)
        if best is None or v < best:
            best, words = v, [w]
        elif v == best:
            words.append(w)
    return best, words


def check_thm12(xmax, ymax):
    bad = []
    for x in range(4, xmax + 1):
        for y in range(4, ymax + 1):
            W = effective_word(x, y)
            v = theta_prefix(W)
            expect = t_of(x) + t_of(y)
            triv = trivial_count_in_word(W)
            nontriv = v - triv
            if v != expect or nontriv != 0:
                bad.append((x, y, W, v, expect, nontriv))
    return bad


def check_thm_small():
    """Thm 5/6/7/8 小 n 全枚举核对。"""
    errs = []
    # M(1,n) = floor(n/4), 最优词 b^ceil ab^floor 及 reverse
    for n in range(1, 19):
        best, words = M_exact(n, 1)
        f = n // 4
        if best != f:
            errs.append(('M1', n, best, f))
        canon = {'b' * ((n + 1) // 2 - (0 if n % 2 else 0)) + 'a' + 'b' * (n // 2)}
        # 直接构造 b^ceil((n-1)/2) a b^floor((n-1)/2)
        c1 = 'b' * ((n - 1 + 1) // 2) + 'a' + 'b' * ((n - 1) // 2)
        c1 = 'b' * ((n - 1) // 2 + (n - 1) % 2) + 'a' + 'b' * ((n - 1) // 2)
        expect_set = {c1, c1[::-1]}
        if set(words) != expect_set:
            errs.append(('M1words', n, sorted(set(words)), sorted(expect_set)))
    # M(2,n) = floor((n-2)/2)
    for n in range(3, 19):
        best, _ = M_exact(n, 2)
        f = (n - 2) // 2
        if best != f:
            errs.append(('M2', n, best, f))
    # M(3,n) = floor((n+2)/4)
    for n in range(4, 19):
        best, _ = M_exact(n, 3)
        f = (n + 2) // 4
        if best != f:
            errs.append(('M3', n, best, f))
    # M(0,n) = floor(n/2)
    for n in range(1, 13):
        best, _ = M_exact(n, 0)
        if best != n // 2:
            errs.append(('M0', n, best, n // 2))
    return errs


TABLE1 = [  # (n, claimed, words)
    (2, 1, ['aa']),
    (3, 0, ['aba']),
    (4, 1, ['abab', 'baba']),
    (5, 1, ['abbba']),
    (6, 2, ['ababbb', 'abbbab', 'babbba', 'bbbaba']),
    (7, 2, ['abbbabb', 'abbbbba', 'bbabbba']),
    (8, 3, ['ababbbbb', 'abbbabb', 'abbbbbab', 'babbbbba', 'bbbabbba', 'bbbbbaba']),
    (9, 3, ['abbbbbabb', 'abbbbbbba', 'bbabbbbba']),
    (10, 4, ['ababbbbbbb', 'abbbabbbbb', 'abbbbbabbb', 'abbbbbbbab',
             'babbbbbbba', 'bbbabbbbba', 'bbbbbabbba', 'bbbbbbbaba']),
    (11, 4, ['abbbbbabbbb', 'abbbbbbbabb', 'abbbbbbbbba', 'bbabbbbbbba', 'bbbbabbbbba']),
]
TABLE2 = [
    (5, 1, ['baaab']),
    (6, 2, ['aaabbb', 'aabbba', 'ababab', 'abbbaa', 'baaabb', 'bababa', 'bbaaab', 'bbbaaa']),
    (7, 2, ['baaabbb', 'bababab', 'bbaaabb', 'bbbaaab']),
    (8, 2, ['bbaaabbb', 'bbbaaabb']),
    (9, 2, ['bbbaaabbb']),
    (10, 3, ['bbaaabbbbb', 'bbbaaabbbb', 'bbbbaaabbb', 'bbbbbaaabb']),
    (11, 3, ['bbbaaabbbbb', 'bbbbaaabbbb', 'bbbbbaaabbb']),
    (12, 3, ['bbbbaaabbbbb', 'bbbbbaaabbbb']),
    (13, 3, ['bbbbbaaabbbbb']),
    (14, 4, ['bbbbaaabbbbbbb', 'bbbbbaaabbbbbb', 'bbbbbbaaabbbbb', 'bbbbbbbaaabbbb']),
    (15, 4, ['bbbbbaaabbbbbbb', 'bbbbbbaaabbbbbb', 'bbbbbbbaaabbbbb']),
    (16, 4, ['bbbbbbaaabbbbbbb', 'bbbbbbbaaabbbbbb']),
    (17, 4, ['bbbbbbbaaabbbbbbb']),
]


def check_tables():
    errs = []
    for n, claimed, words in TABLE1 + TABLE2:
        k = 2 if (n, claimed, words) in TABLE1 else 3
        best, allmin = M_exact(n, k)
        if best != claimed:
            errs.append(('tableMin', n, k, best, claimed))
        for w in words:
            v = theta_prefix(w)
            if v != claimed:
                errs.append(('tableWord', n, k, w, v, claimed))
            if len(w) != n or w.count('a') != k:
                errs.append(('tableShape', n, k, w, len(w), w.count('a')))
        # 论文没列全所有最优词（表格只是列举），所以只查列出的达到即可
    return errs


def check_table3():
    """Table 3: n=18 各 x 的最小值 + 样例词。"""
    samples = {0: ('b' * 18, 9), 1: ('b' * 9 + 'ab' + 'b' * 8, 4),
               2: ('a' + 'b' * 15 + 'a' + 'b', 8),
               3: ('b' * 6 + 'aaa' + 'b' * 9, 5),
               4: ('a' + 'b' * 7 + 'aaa' + 'b' * 7, 5),
               5: ('aa' + 'b' * 7 + 'aaa' + 'b' * 6, 4),
               6: ('a' + 'b' * 7 + 'aaaaa' + 'b' * 5, 5),
               7: ('aa' + 'b' * 7 + 'aaaaa' + 'b' * 4, 5),
               8: ('aaa' + 'b' * 7 + 'aaaaa' + 'b' * 3, 5),
               9: ('aaaa' + 'b' * 5 + 'aaaaa' + 'b' * 4, 4),
               10: ('aaa' + 'b' * 5 + 'aaaaaaa' + 'b' * 4, 5),
               11: ('aaaa' + 'b' * 5 + 'aaaaaaa' + 'bb', 5),
               12: ('aaaaa' + 'b' * 5 + 'aaaaaaa' + 'b', 5),
               13: ('aaaaa' + 'bbb' + 'aaaaaaa' + 'bb', 4),
               14: ('aaaaaaa' + 'bbb' + 'aaaaaaa' + 'b', 5),
               15: ('aaaaaaaaa' + 'bbb' + 'aaaaaa', 5),
               16: ('aaaaaaaaaaaaaaa' + 'b' + 'ab', 8),
               17: ('aaaaaaaaa' + 'b' + 'aaaaaaaa', 4),
               18: ('a' * 18, 9)}
    errs = []
    for x in range(0, 19):
        best, _ = M_exact(18, x)
        w, claimed = samples[x]
        vw = theta_prefix(w)
        ok_shape = (len(w) == 18 and w.count('a') == x)
        if best != claimed:
            errs.append(('T3min', x, best, claimed))
        if vw != claimed or not ok_shape:
            errs.append(('T3word', x, w, vw, claimed, ok_shape))
    return errs


if __name__ == '__main__':
    import sys
    xmax = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    bad = check_thm12(xmax, xmax)
    print(f"Thm12 grid x,y in [4,{xmax}]: {'ALL OK' if not bad else bad[:10]}")
    errs = check_thm_small()
    print("Thm 5/6/7/8 small-n:", "ALL OK" if not errs else errs[:10])
    errs = check_tables()
    print("Tables 1-2:", "ALL OK" if not errs else errs[:20])
    errs = check_table3()
    print("Table 3 (n=18):", "ALL OK" if not errs else errs[:20])
