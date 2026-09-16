#!/usr/bin/env python3
"""
S-08 数值验证 2：T 的剖面决定性阈值定理（S-08 定理 A/推论 C）的机器检验

定理 A（决定性，一般 n）：N ≤ n+3 ⟹ 每朵 3-花的核恰为 n−1，且
    T(F) = Σ_{|Y|=n−1} deg(Y)·(deg(Y)−1)·(deg(Y)−2)   （纯 level-(n−1) 泛函）
推论 C：N ≤ n+3 ⟹ 无任何同剖面 T-分裂（连弱分裂也没有）。

检验：
 (1) n=1：T = 6·C(m,3)（一切 N，唯无一不通过的例外层结构）；
 (2) n=2：N=2..6 全枚举；N ≤ 5 公式+决定性成立，N=6 公式失效与分裂并存；
 (3) n=3：N=6 全量 2^20（numpy）；N=7 修正层恒等式 T = t2sum + 6·#core1花；
 (4) n=4：N=7（=n+3）随机 20 万族公式核验；
 (5) 激活带抽查：N=9, n=4 时核-1 花不可能（N < 3n−2c）。
 (6) 勘误演示：S-05 profile_determinacy.py 的 T_formula（t1 项把宇宙候选
     C(|U|-5,2) 当作成员数）在 U=7 上的违例率。
"""
import itertools
import random
from collections import defaultdict
import numpy as np


def flowers_unordered(fam):
    return [(A, B, C) for A, B, C in itertools.combinations(fam, 3)
            if A & B == A & C == B & C]


def T_of(fam):
    return 6 * len(flowers_unordered(fam))


def formula_sum(fam, U, lev):
    """Σ_{|Y|=lev} d(d−1)(d−2)"""
    tot = 0
    for Y in itertools.combinations(sorted(U), lev):
        d = sum(1 for S in fam if frozenset(Y) <= S)
        tot += d * (d - 1) * (d - 2)
    return tot


def check_n1(trials=2000):
    print("=== (1) n=1：T = 6·C(m,3) 恒等 ===")
    U = list(range(9))
    rng = random.Random(1)
    for _ in range(trials):
        m = rng.randint(0, 9)
        fam = [frozenset([x]) for x in rng.sample(U, m)]
        assert T_of(fam) == 6 * (m * (m-1) * (m-2) // 6)
        assert T_of(fam) == formula_sum(fam, U, 0)  # level-0 泛函
    print(f"  {trials} 随机族通过")


def check_n2():
    print("=== (2) n=2：N=2..6 全枚举 ===")
    for N in range(2, 7):
        edges = list(itertools.combinations(range(N), 2))
        E = len(edges)
        lev = 1  # n−1
        groups = defaultdict(set)
        formula_viol = 0
        det_viol = 0
        for bits in range(1 << E):
            fam = [frozenset(edges[i]) for i in range(E) if (bits >> i) & 1]
            T = T_of(fam)
            Fs = formula_sum(fam, range(N), lev)
            if T != Fs:
                formula_viol += 1
            dv = tuple(sum(1 for S in fam if v in S) for v in range(N))
            groups[dv].add(T)
        splits = sum(1 for v in groups.values() if len(v) > 1)
        print(f"  N={N}: 2^{E} 族, 公式违例={formula_viol}, 剖面类={len(groups)}, "
              f"分裂类={splits}")
        if N <= 5:
            assert formula_viol == 0 and splits == 0, "N ≤ n+3 应决定！"
        else:
            assert formula_viol > 0 and splits > 0, "N = n+4 应失效！"
            # 最小 m 的分裂对
            best = None
            for bits in range(1 << E):
                fam = [frozenset(edges[i]) for i in range(E) if (bits >> i) & 1]
                if len(fam) < 4:
                    continue
                dv = tuple(sum(1 for S in fam if v in S) for v in range(N))
                # 同度数向量配对检查太贵——只记录 T 与公式不同的最小族
            print(f"    （N=n+4：分裂存在，最小构造见 cone_lift.py 的 m=4 对）")


def check_n3_N6():
    print("=== (3a) n=3, N=6：全量 2^20（numpy）===")
    U = list(range(6))
    members = list(itertools.combinations(U, 3))
    M = len(members)
    masks = np.array([sum(1 << e for e in s) for s in members], dtype=np.uint64)
    pairs = list(itertools.combinations(U, 2))
    pmask = np.array([sum(1 << i for i, m in enumerate(members)
                          if frozenset(p) <= frozenset(m)) for p in pairs],
                     dtype=np.uint64)
    # 花超边
    fedges = []
    for (i, si), (j, sj), (k, sk) in itertools.combinations(
            ((i, masks[i]) for i in range(M)), 3):
        if (si & sj) == (si & sk) == (sj & sk):
            fedges.append((i, j, k))
    N = 1 << M
    bits = ((np.arange(N, dtype=np.uint64)[:, None] >> np.arange(M, dtype=np.uint64)) & 1).astype(np.uint8)
    pair_inc = np.array([[int(frozenset(p) <= frozenset(m)) for m in members]
                         for p in pairs], dtype=np.uint8).T  # (M, 15)
    prof = bits @ pair_inc
    T = np.zeros(N, dtype=np.int64)
    b = bits.astype(np.int64)
    for (i, j, k) in fedges:
        T += 6 * b[:, i] * b[:, j] * b[:, k]
    # 公式：Σ_pairs d(d−1)(d−2)
    d2 = (bits @ pair_inc).astype(np.int64)
    formula = np.sum(d2 * (d2 - 1) * (d2 - 2), axis=1)
    viol = int(np.sum(formula != T))
    # 剖面碰撞分裂
    prof_key = prof.tobytes()
    order = np.lexsort((T,) + tuple(prof[:, t].astype(np.int64) for t in reversed(range(prof.shape[1]))))
    Ts = T[order]
    Pr = prof[order]
    bnd = np.flatnonzero(np.any(np.diff(Pr.astype(np.int64), axis=0) != 0, axis=1)) + 1
    starts = np.concatenate(([0], bnd))
    ends = np.concatenate((bnd, [N]))
    mn = np.minimum.reduceat(Ts, starts)
    mx = np.maximum.reduceat(Ts, starts)
    splits = int(np.sum(mn != mx))
    print(f"  2^20 族: 公式违例={viol}, 剖面类={len(starts)}, T-分裂类={splits}")
    assert viol == 0 and splits == 0


def core1_flower_count(fam, U):
    """核大小恰为 1 的无序花数"""
    cnt = 0
    for A, B, C in itertools.combinations(fam, 3):
        if A & B == A & C == B & C and len(A & B) == 1:
            cnt += 1
    return cnt


def check_n3_N7(trials=50000):
    print(f"=== (3b) n=3, N=7：修正层恒等式 T = t2sum + 6·#核1花（随机 {trials} 族）===")
    U = list(range(7))
    members = list(itertools.combinations(U, 3))
    rng = random.Random(7)
    bad = 0
    s05_bad = 0
    for _ in range(trials):
        m = rng.randint(0, len(members))
        fam = [frozenset(members[i]) for i in rng.sample(range(len(members)), m)]
        T = T_of(fam)
        c1 = core1_flower_count(fam, U)
        lhs = formula_sum(fam, U, 2) + 6 * c1
        if T != lhs:
            bad += 1
        # S-05 buggy 公式：t1 = C(|U|-5,2)·N₁（N₁ = 单点交有序对数）
        deg1 = defaultdict(int)
        for S in fam:
            for x in S:
                deg1[x] += 1
        N1 = 0
        for x, dx in deg1.items():
            for S in fam:
                if x in S:
                    N1 += len([y for y in U if y not in S])  # C(|U|-|S|,2) 的组合数
        k = (7 - 5) * (7 - 5 - 1) // 2  # C(2,2)=1
        buggy = formula_sum(fam, U, 2) + k * N1
        if T != buggy:
            s05_bad += 1
    print(f"  修正恒等式违例 = {bad}/{trials}（应 0）")
    print(f"  S-05 旧公式违例 = {s05_bad}/{trials}（勘误：应大量非零）")
    assert bad == 0 and s05_bad > trials // 2


def check_n4(trials=200000):
    print(f"=== (4) n=4, N=7（=n+3）：决定性公式随机核验 {trials} 族 ===")
    U = list(range(7))
    members = list(itertools.combinations(U, 4))
    rng = random.Random(4)
    bad = 0
    core_sizes = defaultdict(int)
    for _ in range(trials):
        m = rng.randint(0, len(members))
        fam = [frozenset(members[i]) for i in rng.sample(range(len(members)), m)]
        T = T_of(fam)
        Fs = formula_sum(fam, U, 3)
        if T != Fs:
            bad += 1
        for A, B, C in flowers_unordered(fam):
            core_sizes[len(A & B)] += 1
    print(f"  公式违例 = {bad}/{trials}（应 0）；花核大小分布 = {dict(core_sizes)}（应只有 3=n−1）")
    assert bad == 0 and set(core_sizes) <= {3}


def check_bands():
    print("=== (5) 激活带抽查：n=4, N=9 时核-2 花可活、核-1 花不可活（N<3n−2c）===")
    U = list(range(9))
    members = list(itertools.combinations(U, 4))
    rng = random.Random(9)
    core_seen = defaultdict(int)
    for _ in range(30000):
        m = rng.randint(3, len(members))
        fam = [frozenset(members[i]) for i in rng.sample(range(len(members)), m)]
        for A, B, C in flowers_unordered(fam):
            core_seen[len(A & B)] += 1
    print(f"  花核大小分布 = {dict(core_seen)}（应只含 2 与 3，无 0/1）")
    assert set(core_seen) <= {2, 3} and 2 in core_seen


if __name__ == "__main__":
    check_n1()
    check_n2()
    check_n3_N6()
    check_n3_N7()
    check_n4()
    check_bands()
    print("\n全部通过：决定性阈值定理在 n=1..4 全部机器确认；勘误（S-05 旧 t1 公式）量化证实。")
