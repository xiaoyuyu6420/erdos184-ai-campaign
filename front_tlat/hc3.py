"""hc3.py — 忠实实现论文 Procedure 2 (Shor # 爬山), 增量 O(1) 维护.
支持 R (必含 entries) 与行级 δ-目标约束 (F 的紧凑形式).
"""
import sys, random
sys.path.insert(0, '/Users/munich/Desktop/数学/front_tlat')
from latpack import FAMILIES

class ShorHC:
    def __init__(self, fam, n, targets, R=(), rng=None):
        self.fam, self.n = fam, n
        self.d = FAMILIES[fam][0]
        self.targets = targets           # row -> set(允许 delta)
        self.R = dict(((r, c), s) for (r, c, s) in R)   # row -> col (必须用)
        self.Rcol = set(c for (r, c) in self.R)
        self.rng = rng or random.Random()
        # Linv 不再预存 (O(n^2) 内存), 用 _col_for 算术求逆

    def _col_for(self, r, s):
        """行 r 中符号 s 的列 (限定 δ ∈ targets[r]); 找不到返回 None."""
        n = self.n
        for delta in self.targets[r]:
            c = (s - r - delta) % n
            if self.d(r, c, n) == delta:
                return c
        return None

    def _sym(self, r, c):
        return (r + c + self.d(r, c, self.n)) % self.n

    def _init(self):
        rng = self.rng
        n = self.n
        fixed = dict(self.R)
        # 类感知贪心: 洗牌列池, 行按约束强度分配首个合法列
        pool = list(range(n))
        rng.shuffle(pool)
        # O(1) 移除的池: swap-pop; 扫描用位置指针循环
        pos = 0
        P = [-1] * n
        # 行分组
        rows = [r for r in range(n) if r not in fixed]
        rng.shuffle(rows)
        rows.sort(key=lambda r: sum(1 for c in (0, 1, 2, 3) if self._legal(r, c, fixed)))
        for r in rows:
            found = -1
            L = len(pool)
            start = rng.randrange(L)
            for off in range(L):
                idx = (start + off) % L
                c = pool[idx]
                if self._legal(r, c, fixed):
                    found = idx; break
            if found < 0:
                # 线性兜底
                for idx, c in enumerate(pool):
                    if self._legal(r, c, fixed):
                        found = idx; break
            if found < 0: return False
            c = pool[found]
            pool[found] = pool[-1]; pool.pop()
            P[r] = c
        for r, c in fixed.items():
            P[r] = c
        self.P = P
        self.Pinv = [0] * n
        for r in range(n): self.Pinv[P[r]] = r
        self.cnt = [0] * n
        self.rows_of = {}
        for r in range(n):
            s = self._sym(r, P[r])
            self.cnt[s] += 1
            self.rows_of.setdefault(s, []).append(r)
        self.U = set(s for s in range(n) if self.cnt[s] == 0)
        return True

    def _legal(self, r, c, fixed):
        n = self.n
        if c in fixed.values(): return False
        return self.d(r, c, n) in self.targets[r]

    def _pool_has_legal(self, r, pool, fixed):
        fv = set(fixed.values())
        t = self.targets[r]
        d = self.d
        for c in pool:
            if c not in fv and d(r, c, n) in t: return True
        return False

    def _apply_swap(self, r1, r2):
        """交换 r1, r2 的列, 增量更新. 注: endgame 交换不查 targets (保证收敛力,
        论文 Procedure 2 同款); type 有效性由外层独立验证器 (campaign 协议) 保证.
        2026-09-15 曾试加检查导致收敛崩溃, 已回退."""
        c1, c2 = self.P[r1], self.P[r2]
        s1, s2 = self._sym(r1, c1), self._sym(r2, c2)
        s1n, s2n = self._sym(r1, c2), self._sym(r2, c1)
        for s_old, s_new, rr, cc in ((s1, s1n, r1, c2), (s2, s2n, r2, c1)):
            lst = self.rows_of[s_old]
            lst.remove(rr)
            if not lst: del self.rows_of[s_old]
            self.cnt[s_old] -= 1
            if self.cnt[s_old] == 0: self.U.add(s_old)
            self.cnt[s_new] += 1
            if self.cnt[s_new] == 1: self.U.discard(s_new)
            self.rows_of.setdefault(s_new, []).append(rr)
        self.P[r1], self.P[r2] = c2, c1
        self.Pinv[c2], self.Pinv[c1] = r1, r2

    def _E(self):
        return [r for s, rr in self.rows_of.items() if len(rr) >= 2 for r in rr]

    def run(self, max_restarts=50, budget=30.0, verbose=False):
        import time
        t0 = time.time()
        n = self.n
        for attempt in range(max_restarts):
            if not self._init():
                continue
            # Phase 1: w < n-2
            stall = 0
            while self.w() < n - 2:
                E = self._E()
                if not E or not self.U: break
                r = self.rng.choice(E)
                s = self.rng.choice(tuple(self.U))
                c = self._col_for(r, s)
                if c is None or c in self.Rcol:
                    stall += 1
                    if stall > 60 * n: break
                    continue
                r2 = self.Pinv[c]
                if r2 != r and self.d(r, c, n) in self.targets[r] \
                   and self.d(r2, self.P[r], n) in self.targets[r2]:
                    self._apply_swap(r, r2)
                    stall = 0
                else:
                    stall += 1
                if stall > 60 * n: break
                if time.time() - t0 > budget: return None
            # Phase 2: endgame (论文逻辑 + 定向喂符号 + 踢扰动)
            patience = 1000 * n + 2000
            kicks = 0
            while self.w() < n:
                if time.time() - t0 > budget: return None
                w0 = self.w()
                if w0 == n - 1:
                    E = self._E()
                    if not E: break
                    r = self.rng.choice(E)
                    r2 = self.rng.randrange(n)
                    if r2 != r:
                        self._apply_swap(r, r2)
                elif w0 == n - 2:
                    E = sorted(set(self._E()))
                    progressed = False
                    for i in range(len(E)):
                        for j in range(i + 1, len(E)):
                            if time.time() - t0 > budget: return None
                            self._apply_swap(E[i], E[j])
                            if self.w() == n:
                                return self.P
                            if self.w() > w0:
                                progressed = True
                            self._apply_swap(E[i], E[j])
                    # 定向喂符号 (无论 sweep 是否进展都尝试)
                    moved = False
                    E2 = sorted(set(self._E()))
                    if E2 and self.U:
                        for _try in range(10):
                            r = self.rng.choice(E2)
                            s = self.rng.choice(tuple(self.U))
                            c = self._col_for(r, s)
                            if c is None or c in self.Rcol: continue
                            r2 = self.Pinv[c]
                            if r2 == r: continue
                            if self.d(r, c, n) in self.targets[r] and \
                               self.d(r2, self.P[r], n) in self.targets[r2]:
                                self._apply_swap(r, r2)
                                moved = True
                                break
                    if not moved:
                        for _try in range(10):
                            r1, r2 = self.rng.sample(range(n), 2)
                            if self.d(r1, self.P[r2], n) in self.targets[r1] and \
                               self.d(r2, self.P[r1], n) in self.targets[r2]:
                                self._apply_swap(r1, r2)
                                moved = True
                                break
                    if not moved: break
                else:
                    E = self._E()
                    if not E: break
                    r = self.rng.choice(E)
                    r2 = self.rng.randrange(n)
                    if r2 != r:
                        self._apply_swap(r, r2)
                patience -= 1
                if patience < 0 or (patience % (200 * n) == 0 and self.w() <= n - 2 and kicks < 6):
                    # 踢扰动: 随机合法交换若干次后回 phase 1
                    for _k in range(40):
                        r1, r2 = self.rng.sample(range(n), 2)
                        if self.d(r1, self.P[r2], n) in self.targets[r1] and \
                           self.d(r2, self.P[r1], n) in self.targets[r2]:
                            self._apply_swap(r1, r2)
                    kicks += 1
                    break
                if patience < 0: break
            if self.w() == n:
                return self.P
        return None

    def w(self):
        return len(self.rows_of)
