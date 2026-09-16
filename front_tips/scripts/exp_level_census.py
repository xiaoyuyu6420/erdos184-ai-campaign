#!/usr/bin/env python3
"""
实验2：特征约束下的「实现水平」普查（census）。

背景（攻击推导的归约）：无三点共线整距离点集，最小距离对 (p,q)，d=min 距离，
远散布假设（除 |pq| 外所有距离 > 4d^2）下 n <= 3 + 2*rho，其中
  rho = #{ m in (0,d) : 存在点 x, | |xp|-|xq| | = m }。
每个水平 m 上的点满足 Pell 型特征约束 (z^2-d^2)(d^2-m^2) = kappa * 平方数
（z = |xp|+|xq|, z ≡ m mod 2）。本实验在「近区」z <= 4d^2 内数：
  rho_cap(d,kappa) = #{ m : 存在 z <= 4d^2 满足特征等式 }
并对照 d 与 log^2(d)。另数含「最小距离约束 r,s >= d」的版本。

纯 numpy 单进程；最大筛域 ~4.2e6（int64），内存 < 200 MB，单线程。
自击：①恒等式 ②小 d 双路对账（census 路径 vs 纯暴力路径）③植入测试。
"""
import math
import numpy as np


def sf_list_upto(N: int):
    """sfl[z] = z 的平方核（z=0..N），O(N) 线性筛。"""
    sfl = [0] * (N + 1)
    if N >= 1:
        sfl[1] = 1
    spf = [0] * (N + 1)
    for z in range(2, N + 1):
        if spf[z] == 0:
            for w in range(z, N + 1, z):
                if spf[w] == 0:
                    spf[w] = z
    for z in range(2, N + 1):
        p = spf[z]
        w = z // p
        sfl[z] = sfl[w // p] if w % p == 0 else p * sfl[w]
    return sfl


def sf_int(n: int) -> int:
    r, m = 1, n
    p = 2
    while p * p <= m:
        c = 0
        while m % p == 0:
            m //= p
            c ^= 1
        if c:
            r *= p
        p = 3 if p == 2 else p + 2
    if m > 1:
        r *= m
    return r


def census(d: int, kappas, verbose=True, return_set=False):
    """近区 z<=4d^2 的实现水平普查。返回 {kappa: (rho, rho_rs, pairs[, set])}。"""
    Zmax = 4 * d * d
    N = Zmax + 2 * d + 1
    sfl = sf_list_upto(N)
    sf = np.array(sfl, dtype=np.int64)
    z = np.arange(d + 1, Zmax + 1, dtype=np.int64)          # z > d（三角不等式）
    a = sf[z - d]
    b = sf[z + d]
    g = np.gcd(a, b)
    k1 = a * b // (g * g)                                    # sf(z^2-d^2)
    m = np.arange(1, d, dtype=np.int64)                      # 1..d-1
    c2 = sf[d * d - m * m]                                   # sf(d^2-m^2)
    parity = z & 1
    cls_cache = {}
    for par in (0, 1):
        sel = parity == par
        cls_cache[par] = (z[sel], k1[sel])
    out = {}
    for kappa in kappas:
        rho = rho_rs = pairs = 0
        realized = []
        for mi in range(len(m)):
            mm = int(m[mi])
            zv, kv = cls_cache[mm & 1]
            cc = int(c2[mi])
            gg = np.gcd(kv, cc)
            hit = (kv * cc // (gg * gg)) == kappa
            cnt = int(hit.sum())
            pairs += cnt
            if cnt:
                rho += 1
                realized.append(mm)
                if int(zv[hit].min()) >= 2 * d + abs(mm):   # r,s >= d（最小距离约束）
                    rho_rs += 1
        out[kappa] = (rho, rho_rs, pairs, realized) if return_set else (rho, rho_rs, pairs)
        if verbose:
            lg2d = math.log(d) ** 2
            print(f"d={d:5d} kappa={kappa:5d}: rho_cap={rho:6d}  rho_cap(rs>=d)={rho_rs:6d}  "
                  f"#(m,z)对={pairs:9d} | log^2 d={lg2d:7.1f}  d/log^2d={d/lg2d:6.2f}")
    return out


def brute(d: int, kappa):
    """纯暴力路径（无筛、无向量化、无 gcd 恒等式——直接 sf 乘积）。"""
    realized = set()
    for mm in range(1, d):
        c2 = sf_int(d * d - mm * mm)
        for z in range(d + 1, 4 * d * d + 1):
            if (z - mm) % 2:
                continue
            if sf_int(sf_int((z - d) * (z + d)) * c2) == kappa:
                realized.add(mm)
                break
    return realized


if __name__ == "__main__":
    # ---- 自击 1：恒等式 sf(ab) = sf(a)sf(b)/gcd(a,b)^2（a,b 无平方因子）
    for A, B in [(6, 35), (2, 3), (10, 21), (1, 1), (30, 210), (5777, 3)]:
        assert sf_int(A) * sf_int(B) // math.gcd(sf_int(A), sf_int(B)) ** 2 == sf_int(A * B)
    print("自击1 通过: sf(ab)=sf(a)sf(b)/gcd^2（a,b 无平方因子）")

    # ---- 自击 2：小 d 双路对账 —— census 路径 vs 纯暴力路径，逐集合相等
    for d in (10, 12, 16):
        for kappa in (1, 2002, 30030):
            got = census(d, [kappa], verbose=False, return_set=True)[kappa][3]
            ref = brute(d, kappa)
            assert set(got) == ref, f"对账失败 d={d} kappa={kappa}: {got} vs {ref}"
    print("自击2 通过: census 路径与纯暴力路径在小 d 逐集合一致（d=10,12,16 × κ∈{1,2002,30030}）")

    # ---- 自击 3：植入测试 —— 构造 (d0,m0,z0) 的解定义 kappa0，census 必须实现 m0
    d0, m0, z0 = 48, 25, 97   # z0 ≡ m0 ≡ 1 (mod 2), z0 > d0
    k0 = sf_int(sf_int((z0 - d0) * (z0 + d0)) * sf_int(d0 * d0 - m0 * m0))
    got = census(d0, [k0], verbose=False, return_set=True)[k0][3]
    assert m0 in got, f"植入失败: m0={m0} 未被找回, got={got}"
    print(f"自击3 通过: 植入 (d,m,z)=({d0},{m0},{z0}) -> kappa0={k0}, m0 被 census 找回")

    # ---- 主实验
    print("=== 主实验：近区 z<=4d^2 实现水平普查 ===")
    for d in (64, 128, 256, 512, 1024):
        census(d, [1, 2002])
