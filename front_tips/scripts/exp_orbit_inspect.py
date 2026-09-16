#!/usr/bin/env python3
"""
实验3：轨道结构可视化。对固定 (d, kappa)，打印每个实现水平 m 的近区 z 值。
理论预测（定理E）：固定 m 的解集是若干条「单位轨道」的并，z 沿轨道几何增长
（比值 >= (1+√2)^2 ≈ 5.83）。观察：每个 m 的 z 值个数少、且相邻比值大。
"""
import math
import numpy as np
from exp_level_census import sf_list_upto


def orbit_dump(d: int, kappa: int, zcap_factor=4):
    Zmax = zcap_factor * d * d
    N = Zmax + 2 * d + 1
    sf = np.array(sf_list_upto(N), dtype=np.int64)
    z = np.arange(d + 1, Zmax + 1, dtype=np.int64)
    a, b = sf[z - d], sf[z + d]
    g = np.gcd(a, b)
    k1 = a * b // (g * g)
    par = z & 1
    rows = []
    for mm in range(1, d):
        cc = int(sf[d * d - mm * mm])
        zv, kv = z[par == (mm & 1)], k1[par == (mm & 1)]
        gg = np.gcd(kv, cc)
        hit = zv[(kv * cc // (gg * gg)) == kappa]
        if len(hit):
            rows.append((mm, hit.tolist()))
    print(f"=== d={d}, kappa={kappa}, zcap={zcap_factor}d^2={Zmax}: "
          f"{len(rows)} 个实现水平")
    for mm, zs in rows:
        gaps = [f"x{zs[i+1]/zs[i]:.2f}" for i in range(len(zs)-1)]
        print(f"  m={mm:4d}: z = {zs}  相邻比值 {gaps if gaps else '(单点)'}")


if __name__ == "__main__":
    # 自击：与 census 主路径一致性（d=16 已在实验2对账过；此处复验 d=24）
    import exp_level_census as E
    got = E.census(24, [2002], verbose=False, return_set=True)[2002][3]
    dump = orbit_dump(24, 2002)
    print(f"自击: census(24,2002) 实现水平 = {got}，与 orbit_dump 一致性见上表")
    orbit_dump(256, 2002)
    orbit_dump(256, 1)
    # 帽敏感性：同一 d、不同帽，看远区是否快速添水平
    for f in (4, 9, 16):
        orbit_dump(128, 2002, zcap_factor=f)
