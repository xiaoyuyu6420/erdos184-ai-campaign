#!/usr/bin/env python3
"""
S-08 数值验证 5（收尾轮）：n=5 的参数化直搜（N=10, m=4）——μ(5) 判定

覆盖论证：若 4-族 F 满足 T(F) > 0，则 F 含核-Y 花三元组，核 |Y| = c 满足
  激活带 c ≥ (3n−N)/2 ⟹ c ∈ {3,4}（N=10）。同一剖面类内任何族 G 满足
  deg_G(Y) = deg_F(Y) ≥ 3（同一个 Y，逐点）⟹ G 也有 ≥ 3 个成员包含 Y
  ⟹ G ∈ {Y∪Q₁, Y∪Q₂, Y∪Q₃, D'}（D' 可再含 Y ⟹ 覆盖 deg(Y)=4 情形）。
  点对称 ⟹ 核-3 类归一 Y = {0,1,2}、核-4 类归一 Y = {0,1,2,3}。
  F₁ 侧：核-3（105 种瓣完美匹配 × D ∈ C(10,5)）+ 核-4（C(6,3) × C(10,5)）；
  F₂ 侧：Q-三重 C(21,3) × D' ∈ C(10,5)；键命中且 T 异 ⟹ 分裂。

用法：python3 n5_param_search.py [N]   （默认 10）
"""
import itertools
import sys
import numpy as np


def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    n, m = 5, 4
    U = list(range(N))
    Zmasks = []
    for r in range(1, n):
        for Z in itertools.combinations(range(N), r):
            Zmasks.append(sum(1 << e for e in Z))
    nZ = len(Zmasks)
    Zm = np.array(Zmasks, dtype=np.uint16)
    # SUB[i, m] = 1 ⟺ Zmasks[i] ⊆ m
    SUB = (((Zm[:, None] & np.arange(1 << N, dtype=np.uint16)[None, :])
            == Zm[:, None])).astype(np.uint8)
    print(f"[n=5 N={N} m=4] profile points = {nZ}", flush=True)

    def fam_key(fam_masks):
        deg = SUB[:, fam_masks[0]].astype(np.uint8)
        for fm in fam_masks[1:]:
            deg += SUB[:, fm]
        return deg.tobytes()

    def T_of(fam_masks):
        t = 0
        v0, v1, v2, v3 = fam_masks
        for a, b, c in ((0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)):
            x, y, z = fam_masks[a], fam_masks[b], fam_masks[c]
            t += (x & y) == (x & z) == (y & z)
        return 6 * t

    def masks(Ss):
        return [sum(1 << e for e in S) for S in Ss]

    f1_db = {}
    f1_count = 0
    D_all = list(itertools.combinations(U, 5))

    # ---------- F₁ 侧：核-3 花，Y = {0,1,2} ----------
    Y3 = {0, 1, 2}
    rest = [x for x in U if x not in Y3]
    ppairs = list(itertools.combinations(rest, 2))
    n_match = 0
    for match in itertools.combinations(ppairs, 3):
        pts = [p for pr in match for p in pr]
        if len(set(pts)) != 6:
            continue
        n_match += 1
        cands = [frozenset(Y3 | set(pr)) for pr in match]
        for Dc in D_all:
            D = frozenset(Dc)
            fam = cands + [D]
            if len(set(fam)) != 4:
                continue
            fm = masks(fam)
            T = T_of(fm)
            if T == 0:
                continue
            f1_db[fam_key(fm)] = (T, fam)
            f1_count += 1
    print(f"  F1 core-3: matches={n_match}, instances={f1_count}, "
          f"distinct profiles={len(f1_db)}", flush=True)

    # ---------- F₁ 侧：核-4 花，Y = {0,1,2,3} ----------
    Y4 = {0, 1, 2, 3}
    singles = [x for x in U if x not in Y4]
    c4 = 0
    for tri in itertools.combinations(singles, 3):
        cands = [frozenset(Y4 | {x}) for x in tri]
        for Dc in D_all:
            D = frozenset(Dc)
            fam = cands + [D]
            if len(set(fam)) != 4:
                continue
            fm = masks(fam)
            T = T_of(fm)
            if T == 0:
                continue
            k = fam_key(fm)
            if k not in f1_db:
                f1_db[k] = (T, fam)
            c4 += 1
    print(f"  F1 core-4: instances={c4}; F1 total distinct profiles={len(f1_db)}",
          flush=True)

    # ---------- F₂ 侧：全部 Q-三重 × D'（核-3 形状）----------
    Qsets = [frozenset(pr) for pr in itertools.combinations(rest, 2)]
    splits = []
    tested = 0
    for Qtri in itertools.combinations(Qsets, 3):
        cands = [frozenset(Y3 | q) for q in Qtri]
        cm = masks(cands)
        for Dc in D_all:
            D = frozenset(Dc)
            fam = cands + [D]
            if len(set(fam)) != 4:
                continue
            fm = cm + [sum(1 << e for e in D)]
            T2 = T_of(fm)
            tested += 1
            key = fam_key(fm)
            hit = f1_db.get(key)
            if hit is not None and hit[0] != T2:
                splits.append((hit[1], hit[0], fam, T2))
                print(f"  *** SPLIT *** T={hit[0]} vs {T2}")
                print(f"    F1 = {sorted(map(sorted, hit[1]))}")
                print(f"    F2 = {sorted(map(sorted, fam))}")
    print(f"  F2 core-3 side tested {tested:,}", flush=True)

    # ---------- F₂ 侧：核-4 形状（3 个 Y4∪{x} + D'）----------
    tested4 = 0
    for tri in itertools.combinations(singles, 3):
        cands = [frozenset(Y4 | {x}) for x in tri]
        cm = masks(cands)
        for Dc in D_all:
            D = frozenset(Dc)
            fam = cands + [D]
            if len(set(fam)) != 4:
                continue
            fm = cm + [sum(1 << e for e in D)]
            T2 = T_of(fm)
            tested4 += 1
            key = fam_key(fm)
            hit = f1_db.get(key)
            if hit is not None and hit[0] != T2:
                splits.append((hit[1], hit[0], fam, T2))
                print(f"  *** SPLIT *** T={hit[0]} vs {T2}")
                print(f"    F1 = {sorted(map(sorted, hit[1]))}")
                print(f"    F2 = {sorted(map(sorted, fam))}")
    print(f"  F2 core-4 side tested {tested4:,}", flush=True)
    print(f"  SPLITS = {len(splits)}", flush=True)
    if not splits:
        print(f"RESULT: n=5 N={N} m=4 参数化覆盖零分裂 ⟹ N={N} 的 m≤4 层无证书",
              flush=True)


if __name__ == "__main__":
    main()
