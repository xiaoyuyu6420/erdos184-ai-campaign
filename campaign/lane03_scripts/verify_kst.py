"""
verify_kst.py — 验证完全二部图 K_{s,t} 的 ce 值与猜想公式。

待验证命题（见 lane_03_constant.md）:
  定理 N (本 lane 证明): ce(K_{3,t}) = ceil(4t/3)
  引理 P (本 lane 证明): ce(K_{2,t}) = t/2 (t 偶), (t+3)/2 (t 奇)
  猜想 E'(偶偶): ce(K_{s,t}) = t/2                    (s,t 均偶, s<=t)  [依赖设计定理, GAP]
  猜想 E'(偶奇): ce(K_{s,t}) = floor(t/2) + s          (s 偶 t 奇)
  猜想 E'(奇):   ce(K_{s,t}) = ceil(t(3s-1)/(2s))      (s 奇, s<=t)
"""
import sys
from ce_solver import ce, edge_index, complete_bipartite

def pred_E(s, t):
    """猜想 E' 的公式值（约定 s <= t）。"""
    if s % 2 == 1:
        num = t * (3 * s - 1)
        return (num + 2 * s - 1) // (2 * s)   # ceil
    if t % 2 == 0:
        return t // 2
    return t // 2 + s

def main(max_n):
    print(f"{'图':<12} {'n':>3} {'ce':>4} {'猜想E''':>8} {'匹配':>5}")
    rows = []
    for s in range(2, max_n):          # s = 小侧
        for t in range(s, max_n + 1 - s):
            n, adj, _ = complete_bipartite(s, t)
            val = ce(n, adj)
            pred = pred_E(s, t)
            ok = "OK" if val == pred else "DIFF"
            rows.append((s, t, n, val, pred, ok))
            print(f"K_{s,t}{'':<6} {n:>3} {val:>4} {pred:>8} {ok:>5}")
    # 定理 N 专项
    print("\n定理 N: ce(K_{3,t}) = ceil(4t/3)")
    for s, t, n, val, pred, ok in rows:
        if s == 3:
            expected = (4 * t + 2) // 3
            print(f"  K_3,{t}: ce={val}, ceil(4t/3)={expected}, {'OK' if val == expected else 'DIFF!!'}")

if __name__ == '__main__':
    mx = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    main(mx)
