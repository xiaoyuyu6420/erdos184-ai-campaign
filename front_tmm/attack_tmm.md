# 攻击报告：minimum modulus 全局最优性猜想（arXiv:2607.08366, Conjecture 1）

**二号攻击手** | 2026-09-12 | 侦察报告：reports/soft-targets-2026-09-12.md 候选 2

---

## 结论强度（三选一）

**部分进展（精确障碍分析 + 新引理组 + 竞争状态修正）**。未证明、未反例。

- 猜想陈述逐字核对无误；Lean 仓库零 sorry 独立复核属实；
- **竞争修正（重要）**：侦察说「零竞争」不准确——作者仓库里已包含 **M. Inal (2026)** 定理的完整 Lean 形式化：*有限阿贝尔群中承载 valid n-元组的最小阶 = 2^(n−1)*（AbelianMin.lean，464 行，0 sorry）。这收掉了「群层面」的最优性，但**循环群的 Conjecture 1（下界 2^n − 2^m ≈ 2·2^(n−1)）仍开放且无人跟进**。攻击窗口仍在，但任何「N ≥ 2^(n−1) 型」成果都已有归属，不可再产出。
- 本轮新增：判据 W（碰撞的规范形，§4.1）、循环群层避让定理（§4.3，新）、n = 8 障碍的精确定量形式（§5）。

---

## 1. 猜想（逐字核对，arXiv:2607.08366v2）

**定义**（论文 §2）。固定 n ≥ 2。集合 A = {a₀ < … < a_{n−1}} ⊂ ℤ_N 是 **valid mod N**，若 size-n 多重集的重数向量 k ∈ ℤ≥0ⁿ（Σkᵢ = n）满足 Σkᵢaᵢ ≡ p := Σᵢaᵢ (mod N) 时必有 k = (1,1,…,1)。

**Conjecture 1**（逐字）："For every n ≥ 2 and every N < 2^n − 2^⌊log₂ n⌋, no set of n residues is valid mod N; that is, the super-increasing set attains the least valid modulus over all size-n sets."

**已证并 Lean 化（论文 Main Theorem）**：超递增集 A = {2^k − 1 : 0 ≤ k < n} 在 N* = 2^n − 2^⌊log₂ n⌋ 处 valid（Theorem A），且对每个 2 ≤ N′ < N* invalid（Theorem B）。松弛恰好 1（Corollary 1：surplus = 2j − popcount(j)，在 j = 1 取最小 1）。**注意已证部分全部针对固定集合**；全局量词（∀A）未被任何已知论证触及，论文原话："a set-free argument would need a different mechanism. Even an exponential lower bound N ≥ c^n valid for all sets appears to be open"（§8，此句写于 Inal 之前/独立，现已被 Inal 的 2^(n−1) 部分超越）。

前 12 个 N*：2, 6, 12, 28, 60, 124, 248, 504, 1016, 2040, 4088, 8184。

---

## 2. Lean 仓库状态（独立核实）

clone：`/Users/munich/Desktop/数学/front_tmm/min-modulus`（本地副本，未动远端）。

| 文件 | 行数 | 内容 |
|---|---|---|
| `MinModulus/UniqueSums.lean` | 943 | 论文主定理：`theorem nmin_eq (hn : 2 ≤ n) : IsLeast {N | 2 ≤ N ∧ Valid n N} (2^n - 2^Nat.log 2 n)`，Valid 对超递增集 `a i = 2^i − 1` 硬编码 |
| `MinModulus/AbelianMin.lean` | 464 | **Inal 2026**：群最小阶 m_ab(n) = 2^(n−1)；`card_ge`（valid ⟹ 2^(n−1) ≤ |G|）、`ssum_injective`（valid ⟹ 差集 dissociated）、极解分类 `equality_addEquiv` |
| `MinModulus/ElemAbelian2.lean` | 252 | (ℤ₂)^k 秩论证：`elementaryAbelianTwoGroups_optimal` |
| `scripts/check_axioms.lean` | — | axiom 审计脚本 |

**sorry 计数**：`grep -rn "sorry" --include="*.lean"` = **1 处，且是审计脚本注释**（"sorryAx must be absent"）。实际 sorry = **0** ✓，与侦察一致。无 `axiom` 声明、无 `native_decide`。仓库文档声称仅用 propext / Classical.choice / Quot.sound（本机无 Lean 工具链，未能重跑审计与编译——标注 `[UNVERIFIED-compile]`，工具链要求 leanprover/lean4:v4.32.0）。

**覆盖范围**：形式化 = 固定集合双向 + 群层面最优（Inal）。Conjecture 1（∀A 的循环群下界）**不在形式化覆盖内**，与论文 §7 陈述一致。

---

## 3. 问题重构（本轮完成的归约）

### 3.1 平移规范化

**引理 0（平移不变）**。对任意 t：A valid mod N ⟺ A + t valid mod N（多重集 k 的和偏移 |k|·t，目标偏移 n·t，碰撞关系保持）。
证：Σkᵢ(aᵢ+t) − Σaᵢ − nt = Σkᵢaᵢ − Σaᵢ。∎

因此 WLOG a₀ = 0（取 t = −a₀）。

### 3.2 判据 W（碰撞规范形）

**引理 1（差形式）**。A invalid mod N ⟺ ∃ c ∈ ℤⁿ∖{0}：Σcᵢ = 0，Σcᵢaᵢ ≡ 0 (mod N)，minᵢ cᵢ ≥ −1。
证：（⟸）k := c + 1 ≥ 0，|k| = n，Σkᵢaᵢ = p + Σcᵢaᵢ ≡ p，k ≠ 1。（⟹）取 c = k − 1，由 kᵢ ≥ 0 得 cᵢ ≥ −1。∎

（澄清：碰撞向量恒可定向为「k − ones」，故不存在「两个任意多重集碰撞差方向不定」的问题——一切碰撞都对着 all-ones 归一。）

**引理 1′（多重集–子集形式，a₀ = 0 下）**。A invalid ⟺ 存在 (P, Q)：
- P：取值于 {a₁,…,a_{n−1}} 的有限多重集（无 0 拷贝）；
- Q ⊆ {a₀,…,a_{n−1}} 子集；
- supp(P) ∩ Q = ∅；|P| = |Q| ≥ 1；Σ_P ≡ Σ_Q (mod N)。

证：（⟹）由引理 1 的 c，取 P = {aᵢ 重数 max(cᵢ,0)}_{i≥1}，Q = {aᵢ : cᵢ = −1}（含 i = 0 至多一次）。平衡 Σcᵢ = 0 给 |P| = |supp 正部| 重数和 = Σcᵢ⁺ = Σcᵢ⁻ = |Q|。支撑不交由 cᵢ 符号唯一。Σ_P − Σ_Q = Σᵢ≥1 cᵢaᵢ ≡ 0（a₀ 项系数 c₀ 不入和但入平衡）。（⟸）由 (P,Q) 构造 c：cᵢ = P 重数（i ≥ 1，i ∈ supp P），c₀ = |Q| − |P| + (−1_{a₀∈Q} 的补偿)…… 直接：c₀ := |Q∖{0}| − |P|，cᵢ = −1 (i ∈ Q∖{0})，c₀ += −1 若 a₀ ∈ Q。逐项验证 Σc = 0、min ≥ −1、同余。∎（完整逐项验证见验证脚本 witness_PQ 一致性检查。）

**用途**：把猜想化为「等大小多重集-子集碰撞的存在性」，比论文 §7 的 CP 模型（k-向量枚举）变量更少，可直接做 ILP/CP 模型升级。

### 3.3 推论包（valid 集合的强制性质；a₀ = 0 下）

**引理 2**。设 A valid mod N。则：
(a) **零和自由**：无非空子集 T ⊆ {1,…,n−1} 使 Σ_T ≡ 0。〔P = ∅, Q = T，|P| = 0 ≠ |T| ≥ 1 违反等大小？——不：用 c = |T|·e₀ − 1_T：c₀ = |T| ≥ 0 ≥ −1 ✓，Σc = 0 ✓，Σcᵢaᵢ = −Σ_T ≡ 0 ✓ witness。〕
(b) **子集类和单射**（T ~ T △ {a₀}）：⟹ **N ≥ 2^{n−1}**。〔子集和碰撞 Σ_T ≡ Σ_{T′} 经不交支撑规范化给出 P、Q 且 |P| − |Q| = |T| − |T′| 经 e₀-padding 总可平衡（0 拷贝任意多），唯一例外 T′ = T ∪ {a₀}（平凡，c = 0）。故 2^{n−1} 个类和两两不同。〕
   **归属标注**：此即 Inal 定理（valid ⟹ 差集 dissociated ⟹ 2^{n−1} 子集和 ≤ |G|）在循环群的特例，已 Lean 形式化（AbelianMin.lean `card_ge`、`ssum_injective`）。本轮独立重推确认，**不作为新成果**。
(c) **阶下界**：ord(aᵢ) ≥ n + 1（i ≥ 1）。〔j·aᵢ ≡ 0 给 c = j·eᵢ：Σc = j ≠ 0 不平衡——修正：给 c = (n−1)e₀ + j·eᵢ 型需再平衡；直接：j·aᵢ ≡ 0, j ≤ n：多重集 {aᵢ^j} + (n−j)·a₀ vs 全部补 0…… 构造 k = j·eᵢ + (n−j)·e₀：|k| = n，Σkᵢaᵢ = j·aᵢ ≡ 0；若 j·aᵢ ≡ 0 ≡ ? 需要 ≡ p：p ≠ 0（否则 c = (n−1)e₀ − Σ_{i≥1} eᵢ：Σc = 0，Σcᵢaᵢ = −p ≡ 0 witness）。所以 j·aᵢ ≡ 0 不直接碰撞。**改证**：p ≠ 0 ✓（前述）；j·aᵢ ≡ p 对 2 ≤ j ≤ n？k = j·eᵢ + (n−j)·e₀ 碰撞 ⟹ invalid。故 p ∉ {j·aᵢ : 2 ≤ j ≤ n}。ord 下界另一证：aᵢ ≡ p − (j−1)aᵢ 不给 ord。**诚实修正**：(c) 的 ord ≥ n+1 断言在本轮未完全闭合，仅证得 p ∉ {j·aᵢ}。降级为 open 小问题。〕
(d) 每层单射：对每个 s，size-s 子集和 S_s 内部无碰撞（碰撞给等大小 P=Q′ 型 witness），且 |S_s/类| = C(n−1, s)（类代表 = 不含 a₀ 的子集）。

---

## 4. 新定理：层倍数避让

### 4.1 陈述

**定理 3**。设 A valid mod N，a₀ = 0。对 s ≥ 1 与类和 x ∈ S_s（x = Σ_{i∈T} aᵢ，T 代表，|T| = s，x ≢ 0）：若 2x ≡ Σ_{T′} (mod N) 且 T′ ∌ a₀（|T′| = s′），则 **s′ ≤ 2s − 2**。

即：valid ⟹ 2·S_s∖{0} ∩ S_{[2s−1, n−1]} = ∅（顶层避让）。

**证明**。设 2Σ_T ≡ Σ_{T′}，s′ ≥ 2s − 1。构造
  c = 2·1_{T∖T′} + 1_{T∩T′} − 1_{T′∖T} + m·e₀，m := s′ − 2s。
逐项核对：
- min cᵢ ≥ −1：负部仅 T′∖T 处 −1；c₀ = m = s′ − 2s ≥ −1 ✓。
- Σcᵢ = 2|T∖T′| + |T∩T′| − |T′∖T| + m。算：2(s − |T∩T′|) + |T∩T′| − (s′ − |T∩T′|) + s′ − 2s = 2s − 2|T∩T′| + |T∩T′| − s′ + |T∩T′| + s′ − 2s = 0 ✓。
- Σcᵢaᵢ = 2Σ_T − Σ_{T′}（交处 2−1+1 = 2·1 净额恰为 2Σ_T − Σ_{T′} 的规范形）≡ 0 ✓；e₀ 项 = 0（a₀ = 0）✓。
- c ≠ 0：若 c = 0 则 T∖T′ = ∅ 与 |T∩T′| 项、T′∖T = ∅ → T = T′ → 2Σ_T ≡ Σ_T → Σ_T ≡ 0 矛盾 ✓。
由判据 W（引理 1）得碰撞，与 valid 矛盾。∎

### 4.2 计数推论与自我纠错记录

**推论 4**。valid ⟹ N ≥ 2^{n−1} + ½·C(n−1, ⌊n/2⌋)（逐层：S_{<2s−1} ∪ S_{≥2s−1} ∪ 2S_s 两两不相交于最大 s 处）。
n = 8：N ≥ 128 + 17 = **145**（vs 目标 248）。j ≥ 3 变体（j·S_s 避开 S_{≥ js−1}）同型，增量不改变渐近阶。

**纠错记录（防下一棒重踩）**：本轮中途曾误推「valid ⟹ 2·𝒮° ∩ 𝒮 = ∅（全局）⟹ N ≥ ~0.75·2^n」。错误原因：把「|P| = |Q| 等大小自动成立」用错了场景——平衡约束只在 |T′| ≥ 2|T| − 1（+a₀ ∈ T′ 时再 +1）时可满足，**层间自由碰撞**（如 2·S_1 与 S_2 在小 |T| 处、以及 2x ≡ Σ_{T′} with s′ < 2s−1）不受约束。穷举验证器亦曾因多重集枚举的非降序去重条件写反而集体误报「反例」，修正后（非降 index 序列规范枚举）通过。两个错误都已定位并修复，正确结果以本节与验证脚本为准。

### 4.3 为什么这仍不够（量化）

层避让计数的天花板：Σ_{s} C(n−1,s) = 2^{n−1} 已全计入，2S_s 的增量 ≤ ½·max_s C(n−1,s) = O(2^n/√n)（×2 映射纤维 ≤ 2 且层间可合并）。**所有「子集结构」类论证的总和封顶在 2^{n−1} + O(2^n/√n)**。

---

## 5. n = 8（第一个开放 n）的精确障碍

目标：N ∈ [2, 247] 全 invalid（任意 8-集合）。

| 工具 | 覆盖 | 剩余 |
|---|---|---|
| Inal/引理 2b（dissociated ⟹ 2^{n−1}） | N < 128 | — |
| 定理 3 推论 4（层避让） | N < 145 | — |
| 论文 Theorem B 机制 | 0（仅固定超递增集） | — |
| **剩余裸区** | — | **N ∈ [145, 247]，共 103 个模数** |

**裸区的本质**：需要证明「ℤ_N 中 N ≤ 247 时，任何 dissociated 7-元组 + 平移 0 必有非平凡重数碰撞」。已知：
- (ℤ₂)⁷ 中 dissociated 7-元组 valid 存在（Inal 极解 (0, e₁,…,e₇)）——群最小阶 2^7 = 128 **在非循环群达到**；
- 循环群 ℤ_128 的极化 dissociated 集（如 {1,2,4,…,64}）必 invalid（猜想断言至多到 N = 247 都无 valid），失败机制是「阶约束 + 倍数碰撞」（例：n = 4, N = 8, A = {0,1,2,4}：多重集 {1,2,2,2} 碰撞 {0,1,2,4}，和同为 7；witness c = (−1,0,2,−1)）。
- **[GAP-1]**：把「非 2-挠的代价」定量化到 2^n − 2^m 精确式，本轮未找到机制。所有尝试的死点：(i) 鸽笼/柯西计数差因子 n（需 N < 2^n/n 才起效）；(ii) 特征和（p-系数 = (1/N)Σ_ζ ζ^{−p}Πᵢ(1−ζ^{(n+1)aᵢ})/(1−ζ^{aᵢ})）在一般 A 下逐 ζ 无界（(n+1)^n 爆炸，零因子 ζ^{(n+1)aᵢ}=1≠ζ^{aᵢ} 帮忙但不足）；(iii) 论文 Theorem A/B 的数字和机制本质依赖二进制贪心唯一性，一般集合无此结构（作者已声明）。

**反例评估**：n ≤ 7 CP 已证；作者 GPU 搜索至 n ≤ 13 无反例且极小解全部 canonicalize 到超递增集；本轮 n ≤ 5 修正穷举确认（见 §7）。猜想为假的概率评估：低。**主战场在证明侧**。

---

## 6. Lean 接续（陈述已备，待工具链）

本机无 elan/lean（需 leanprover/lean4:v4.32.0），未能编译。以下为接续作者框架的目标陈述（需先在 UniqueSums.lean 的 `Valid` 之外引入一般集合版本）：

```lean
/-- 一般集合的 validity（作者仓库的 `Valid n N` 仅覆盖超递增集）。 -/
def ValidGen {n N : ℕ} (A : Fin n → ZMod N) : Prop :=
  ∀ k : Fin n → ℕ, (∑ i, k i = n) →
    (∑ i, k i • A i = ∑ i, A i) → ∀ i, k i = 1

/-- 引理 1（判据 W，差形式）。A invalid ↔ 存在平衡、下界 −1 的非零零模向量。 -/
theorem invalid_iff_witness {n N : ℕ} (hn : 2 ≤ n) (A : Fin n → ZMod N)
    (hinj : Function.Injective A) :
    ¬ ValidGen A ↔ ∃ c : Fin n → ℤ, (∑ i, c i = 0) ∧ c ≠ 0 ∧
      ∀ i, c i ≥ -1 ∧ ((∑ i, c i * (A i : ℤ)) : ℤ) % N = 0

/-- 引理 2b（循环群 2^(n-1) 下界；Inal 定理的循环特例，仓库 AbelianMin.card_ge 的群版本已含）。 -/
theorem card_ge_cyclic {n N : ℕ} (hn : 2 ≤ n) (A : Fin n → ZMod N)
    (hval : ValidGen A) : 2^(n-1) ≤ N

/-- 定理 3（层倍数避让，本轮新）。 -/
theorem layer_double_avoid {n N : ℕ} (hn : 2 ≤ n) (A : Fin n → ZMod N)
    (hval : ValidGen A) :
    ∀ (T T' : Finset (Fin n)), 0 ∉ T' → T.card ≥ 1 →
      (∑ i in T, A i) ≠ 0 →
      ((2 * ∑ i in T, A i : ZMod N) = ∑ i in T', A i) →
      2 * T.card ≤ T'.card + 2

/-- Conjecture 1（主目标，未证）。 -/
theorem conjecture1 {n N : ℕ} (hn : 2 ≤ n) (A : Fin n → ZMod N)
    (hinj : Function.Injective A) (hN : N < 2^n - 2^(Nat.log 2 n)) :
    ¬ ValidGen A
```

（`layer_double_avoid` 陈述中的 `2*T.card ≤ T'.card + 2` 对应正文 s′ ≤ 2s − 2 加 a₀ ∈ T′ 情形的常数吸收；形式化时以正文证明为准微调。）

---

## 7. 验证（轻量，防自欺）

脚本：`/Users/munich/Desktop/数学/front_tmm/verify_tmm.py`（穷举 n ≤ 5 全部 (A, N) 对 + n = 6,7 结构抽查）。
- 核对 Conjecture 1 在 n ≤ 5 无反例（N < N* 全 invalid，任意 A）；
- 核对 L1（valid ⟹ N ≥ 2^{n−1}）、定理 3 层避让在所有 valid (A, N) 上无一违反；
- n = 6,7：超递增集在 N* 处 valid、N*−1 处给出显式 witness；
- 运行结果见附录（§9）。

---

## 8. 遗留与下一步

1. **主缺口 [GAP-1]**：定量化「循环群非 2-挠的代价」。建议方向：研究 ℤ_N 中 dissociated 集的 h-重数自由阈值（N ≤ 2^n 量级时重数碰撞的必然性），这是加法组合型问题；或对 𝒮 的 Frobenius/覆盖结构做逐 N 分析。
2. **n = 8 CP 再战（需 Experimenter）**：用判据 W′（多重集-子集等大小碰撞）替换论文 §7 的 k-枚举模型，目标 N ∈ [145, 247] 的 103 个模数；变量数显著减少。
3. **Lean 接续**：按 §6 陈述实现（优先 `invalid_iff_witness` 与 `layer_double_avoid`，均短证明）；接续作者仓库形成 PR 是天然发表配套。
4. **竞争盯梢**：Inal (2026) + Fonollosa 配套论文 2607.09949 是同一生态；若作者扩展其仓库至 Conjecture 1，窗口收窄。
5. 修正确认的小开放问题：valid 时 ord(aᵢ) 的精确下界（§3.3(c) 降级记录）。

---

## 9. 附录：验证器输出（已完成）

`verify_tmm.py` 实跑结果（穷举 n ≤ 5 全部 (A,N) + n = 6,7 结构抽查）：

```
n=2: Ncrit=2,  minValidN=2,  Conjecture(OK), L1bad=0, checked=1
n=3: Ncrit=6,  minValidN=6,  Conjecture(OK), L1bad=0, checked=17
n=4: Ncrit=12, minValidN=12, Conjecture(OK), L1bad=0, checked=805
n=5: Ncrit=28, minValidN=28, Conjecture(OK), L1bad=0, checked=377114
n=6: Ncrit=60,  superincr valid@Ncrit=True, invalid below=True, witness@59=(1,3,4,5,5,5)
n=7: Ncrit=124, superincr valid@Ncrit=True, invalid below=True, witness@123=(1,3,4,5,6,6,6)
定理 3 精确复查（仅 a₀=0 规范化集合，仅禁区 s′ ≥ 2s−1）：valid (A,N) checked: 82, violations: 0
```

要点：
- Conjecture 1 在 n ≤ 5 **全穷举确认**（377,114 对，无一反例），minValidN 精确等于 N*；
- L1（valid ⟹ N ≥ 2^{n−1}）零违反；
- 定理 3 在精确陈述下零违反。**注意**：初版验证器的 `check_L2` 检查的是被废弃的全局强命题（2x 不落任何层），其「违反」实例（超递增集 (0,1,3,7) mod 12：x=8, s=2 → 层 2，s′=2 ≤ 2s−2 允许）全部落在定理允许区，恰好实锤 §4.2 的纠错记录；另有部分实例的 A 未规范化（如 (1,2,4,8)），平移改变碰撞关系（2x ≡ y ↦ 2x−y ≡ 2s−s′），前提不适用。
- n = 6,7 超递增集在 N* 处 valid、N*−1 处有显式 witness，与论文 §7 一致。

---

## 文件清单

- 论文：`/Users/munich/Desktop/数学/front_tmm/2607.08366.pdf`（+ paper_clean.txt 提取文本）
- 仓库：`/Users/munich/Desktop/数学/front_tmm/min-modulus/`（jarfo/min-modulus 本地克隆）
  - 主分支：保持作者原状（零 sorry）
  - 本地分支 `attack/witness-criterion`（commit 1113ce9a，**未推远端**）：`MinModulus/Attack.lean` 陈述骨架（含 sorry 占位，勿合入主干）
- 验证器：`/Users/munich/Desktop/数学/front_tmm/verify_tmm.py`
- 本报告：`/Users/munich/Desktop/数学/front_tmm/attack_tmm.md`
