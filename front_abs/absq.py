"""Abelian square 计数器：两个独立实现 + 自检。

约定（与 arXiv:2604.23188 一致）：
- abelian square: 因子 w[i..i+2p-1]，前半与后半 Parikh 向量相等（等价地，长度相等且
  a 数相等；二元情形这是充要条件）。
- theta(w) = w 中不同 abelian square 因子的个数（按字面词去重，与位置无关）。
- trivial abelian square: a^{2i} 或 b^{2i}, i>=1。
"""

from itertools import combinations


# ---------- 实现一：朴素枚举所有因子，逐一检查 ----------
def theta_naive(w):
    n = len(w)
    sq = set()
    for i in range(n):
        for L in range(2, n - i + 1, 2):  # 偶长因子
            half = L // 2
            left = w[i:i + half]
            right = w[i + half:i + L]
            if sorted(left) == sorted(right):
                sq.add(w[i:i + L])
    return len(sq)


def squares_naive(w):
    """返回不同 abelian square 因子集合（调试用）。"""
    n = len(w)
    sq = set()
    for i in range(n):
        for L in range(2, n - i + 1, 2):
            half = L // 2
            if sorted(w[i:i + half]) == sorted(w[i + half:i + L]):
                sq.add(w[i:i + L])
    return sq


# ---------- 实现二：前缀和 O(n^2)，逐因子 O(1) 判定 ----------
def theta_prefix(w):
    n = len(w)
    # pa[i] = 前 i 个字母中 a 的个数
    pa = [0] * (n + 1)
    for i, c in enumerate(w):
        pa[i + 1] = pa[i] + (1 if c == 'a' else 0)
    sq = set()
    for i in range(n):                      # 起点
        for half in range(1, (n - i) // 2 + 1):  # 半长
            j = i + half                   # 中点
            ca_l = pa[j] - pa[i]
            ca_r = pa[j + half] - pa[j]
            if ca_l == ca_r:               # 等长 + 等a数 <=> Parikh 相等
                sq.add(w[i:j + half])
    return len(sq)


theta = theta_prefix  # 主入口


def is_abelian_square(w, i, L):
    half = L // 2
    return sorted(w[i:i + half]) == sorted(w[i + half:i + L])


def trivial_count_in_word(w):
    """w 中不同 trivial abelian square 个数（a^{2i}/b^{2i} 因子）。"""
    tr = set()
    for c in 'ab':
        run = 0
        for ch in w + '#':
            if ch == c:
                run += 1
            else:
                for m in range(1, run // 2 + 1):
                    tr.add(c * (2 * m))
                run = 0
    return len(tr)


# ---------- effective partition 与构造词 ----------
def t_of(m):
    """t_m = floor((m+2)/4)，构造词族在 Parikh (x,y) 的声称值 t_x+t_y。"""
    return (m + 2) // 4


def effective_partition(m):
    """e(m) = [p, q]: p+q=m, q>p, q 奇, q 最小。论文 Thm 10 公式。要求 m>=4。"""
    assert m >= 4
    p = m - 2 * t_of(m) - 1
    q = 2 * t_of(m) + 1
    assert p + q == m and q > p and q % 2 == 1
    return (p, q)


def effective_word(x, y):
    """W(x,y) = a^{p_x} b^{q_y} a^{q_x} b^{p_y}，[p_x,q_x]=e(x), [k,i]=e(y) => i=q_y, k=p_y."""
    px, qx = effective_partition(x)
    py, qy = effective_partition(y)
    return 'a' * px + 'b' * qy + 'a' * qx + 'b' * py


# ---------- 自检（先自击再上阵） ----------
def _selftest():
    # 手工核实的锚点
    assert squares_naive("abaababa") == {'aa', 'abab', 'abaaba', 'baba', 'baab', 'aababa'}, \
        squares_naive("abaababa")
    assert theta_naive("abaababa") == 6
    assert theta_naive("b" * 18) == 9
    assert theta_naive("abbba") == 1 and squares_naive("abbba") == {'bb'}
    assert theta_naive("abab") == 1 and squares_naive("abab") == {'abab'}
    assert theta_naive("") == 0 and theta_naive("a") == 0
    assert theta_naive("aa") == 1 and theta_naive("aaa") == 1 and theta_naive("aaaa") == 2
    # 随机词两实现互校
    import random
    random.seed(20260913)
    for _ in range(3000):
        n = random.randint(0, 60)
        w = ''.join(random.choice('ab') for _ in range(n))
        a, b = theta_naive(w), theta_prefix(w)
        assert a == b, (w, a, b)
    # 边界/退化
    for w in ['a' * 7, 'b' * 13, 'ab' * 9, 'a' * 3 + 'b' * 3]:
        assert theta_naive(w) == theta_prefix(w)
    # effective_partition 抽查：论文例子 e(10)=[3,7]
    assert effective_partition(10) == (3, 7)
    assert effective_partition(9) == (4, 5)
    assert effective_partition(4) == (1, 3)
    assert effective_partition(14) == (5, 9)
    print("selftest OK")


if __name__ == '__main__':
    _selftest()
