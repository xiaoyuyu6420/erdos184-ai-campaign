"""build_H.py — H_n τ₃ (含 (1,1,5),(6,5,14), 缺 (11,9,23)) 的参数化分块构造
架构 (k >= K0):
  patch   行 0..14            : 小列池 (偶 {0..14}, 奇 {1..17}), 一次求解后硬编码
  Q 块    偶行 [16, 2k-4]     : 恒等列 (参数: 符号斜率/起点)
  D 块    奇行 15+4t          : 列 4k-22-2t, 符号 4k-5+2t mod 4k      [已证自洽]
  E 块    奇行 17+4u          : 列 γ-2u,      符号 17+γ+2u mod 4k      [已证自洽]
  P 块    偶行 2k-2+2i        : 奇列 (参数化配对)
  tail    行 4k-21..4k-1      : 恒等
所有块参数 {γ, P列配对σ, Q变体} 由搜索确定; 全自动独立验证。
"""
import sys
sys.path.insert(0, '/Users/munich/Desktop/数学/front_tlat')
from latpack import symbol as sym_of, SPECIALS, FAMILIES, is_transversal

def walecki(N):
    """长 N 的 graceful 排列 (差分两两不同): 0, N-1, 1, N-2, ..."""
    out = []
    lo, hi = 0, N - 1
    while lo <= hi:
        out.append(lo); lo += 1
        if lo > hi: break
        out.append(hi); hi -= 1
    return out

def build_H3(k, gamma_E, p_variant, q_variant):
    """返回 colmap (row->col) 或 None (结构冲突). p_variant/q_variant: 整数参数."""
    n = 4 * k
    M = k - 10
    if M < 2: return None
    col = {}
    # --- D 块
    for t in range(M + 1):
        col[15 + 4 * t] = (4 * k - 22 - 2 * t) % n
    # --- E 块
    for u in range(M + 1):
        col[17 + 4 * u] = (gamma_E - 2 * u) % n
    # --- tail 恒等
    for r in range(4 * k - 21, 4 * k):
        col[r] = r
    # --- Q 块: 偶行 16..2k-4 恒等
    for j in range(M + 2, k - 1):          # j: 0..k-11  -> 行 16+2j, 最大 2k-6?? 修正 below
        pass
    qrows = list(range(16, 2 * k - 4 + 1, 2))   # k-9 个
    if q_variant == 0:     # 恒等
        for q in qrows: col[q] = q
    elif q_variant == 1:   # 反序
        for j, q in enumerate(qrows): col[q] = qrows[-1 - j]
    elif q_variant == 2:   # walecki 索引
        perm = walecki(len(qrows))
        for j, q in enumerate(qrows): col[q] = qrows[perm[j]]
    # --- P 块: 偶行 2k-2..4k-22 -> 奇列池
    prows = list(range(2 * k - 2, 4 * k - 22 + 1, 2))   # k-9 个
    # P 可用奇列 = 全部奇列 - patch 候选(<=17) - tail 恒等奇列 - E 列 - B/A 列
    used_odd = set()
    for r in range(4 * k - 21, 4 * k):
        if r % 2 == 1: used_odd.add(r)
    for u in range(M + 1): used_odd.add((gamma_E - 2 * u) % n)
    # patch 用列(见下) 先留: patch 奇列 ⊆ {1..17}; A/B: {9,13,17,1,5}
    p_pool = [c for c in range(19, 4 * k - 21, 2) if c % n not in used_odd and c <= 4 * k - 23]
    if len(p_pool) < len(prows): return None
    if p_variant == 0:      # 顺序
        assign = p_pool[:len(prows)]
    elif p_variant == 1:    # 反序
        assign = p_pool[:len(prows)][::-1]
    elif p_variant == 2:    # 隔取
        assign = p_pool[::2][:len(prows)]
        if len(assign) < len(prows): return None
    elif p_variant == 3:    # 前半+后半
        h = len(prows) // 2
        assign = p_pool[:h] + p_pool[-(len(prows) - h):]
    for i, p in enumerate(prows): col[p] = assign[i] % n
    return col

def finish_patch(k, col, verbose=False):
    """给定块, 用回溯解 patch 行 0..14 (含特殊格约束). 返回完整 colmap 或 None."""
    n = 4 * k
    d = FAMILIES['H'][0]
    sp = SPECIALS['H']
    # 禁止列/符号 (已被块占用)
    used_c = set(col.values())
    used_s = set((r + c + d(r, c, n)) % n for r, c in col.items())
    prows = [r for r in range(15) if r not in col]
    allow = {}
    for r in prows:
        cc = []
        for c in range(n):
            if c in used_c: continue
            s = (r + c + d(r, c, n)) % n
            if s in used_s: continue
            # 类约束: A 行 (0,5,10) 需 Δ=4; C 行 (4,9,14) 需 Δ=0 且 c∉1 mod4;
            # 行 11 需 Δ=0 且 c∉{9,10,11,12}; B 行 1,6 需特殊格; 其余 Δ=0
            dl = d(r, c, n)
            if r in (0, 5, 10):
                if dl != 4: continue
                if not (c % 4 == 1 and c - 4 * r // 5 != 1): continue
            elif r in (1, 6, 11):
                if r == 1:
                    if (r, c, s) != sp[0]: continue
                elif r == 6:
                    if (r, c, s) != sp[1]: continue
                else:
                    if dl != 0 or c in (9, 10, 11, 12): continue
            elif r in (4, 9, 14):
                if dl != 0 or c % 4 == 1: continue
            else:
                if dl != 0: continue
            cc.append(c)
        allow[r] = cc
    order = sorted(prows, key=lambda r: len(allow[r]))
    sol = {}
    def dfs(i):
        if i == len(order): return True
        r = order[i]
        for c in allow[r]:
            s = (r + c + d(r, c, n)) % n
            if c in used_c or s in used_s: continue
            col[r] = c; used_c.add(c); used_s.add(s)
            if dfs(i + 1): return True
            del col[r]; used_c.discard(c); used_s.discard(s)
        return False
    ok = dfs(0)
    return col if ok else None

def verify_H3(k, col):
    n = 4 * k
    T = [(r, c, sym_of('H', r, c, n)) for r, c in sorted(col.items())]
    ok, msg = is_transversal('H', n, T)
    if not ok: return False, msg
    Tset = set(T)
    if SPECIALS['H'][0] not in Tset or SPECIALS['H'][1] not in Tset: return False, "缺特殊格"
    if SPECIALS['H'][2] in Tset: return False, "含 sp3"
    return True, "OK"

if __name__ == '__main__':
    import itertools, time
    t0 = time.time()
    winners = []
    for gamma_E, pv, qv in itertools.product(
            [4 * k_ - 23 for k_ in [24]] , range(4), range(3)):
        pass
    # 参数扫描: gamma_E 的候选与 k 解耦 — gamma_E 是公式 4k + c0 形式, 扫 c0
    for c0 in range(-50, 21, 2):
        for pv in range(4):
            for qv in range(3):
                good = True
                for k in (24, 25, 40):
                    col = build_H3(k, 4 * k + c0, pv, qv)
                    if col is None: good = False; break
                    col = finish_patch(k, col)
                    if col is None: good = False; break
                    ok, msg = verify_H3(k, col)
                    if not ok: good = False; break
                if good:
                    winners.append((c0, pv, qv))
                    print(f"WINNER c0={c0} pv={pv} qv={qv}  ({time.time()-t0:.1f}s)")
    print("total winners:", len(winners))
