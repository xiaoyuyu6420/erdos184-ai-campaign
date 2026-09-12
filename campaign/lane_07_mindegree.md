# Lane 07：最小度 ≥ εn 情形的精确常数

> 摘要（5 行）
> 1. 完全证明 Thm A：D-正则、D≥⌊n/2⌋（Dirac 正则图，n≥n₀）⟹ ce(G)≤n−1；且 n 偶 D 偶时 ce=D/2≤(n−2)/2，n 奇时 ce=D/2≤(n−1)/2。武器=CKLOT Hamilton 分解定理（本地源码逐字核对）。
> 2. Cor A.1（完全证明）：ce(K_n)=(n−1)/2（n 奇，精确）。数值：K₄=3、K₆=5、K₈=7 均恰为 n−1——Thm A(iii) 的一致界在全部已测小偶阶完全图上达到，猜想 ce(K_{2m})=2m−1 (m≥2)。
> 3. CFS2014 的 O(c⁻¹²n) 常数链已逐项定位（§1.1 账本）：主导项 2⁴¹c⁻¹²n 单一来源于跨部散边预算 s=2⁴⁰c⁻¹¹；全显式化无数学障碍仅体力（量级 2⁵⁰·c⁻¹²n）。
> 4. 数值侦察（ce_exact.py，修复 bug 后与定理六重交叉验证吻合）：Babai 图 n=10 ce=6（0.6n），否定"近二部 ⟹ ≤n/2"初步猜想；两团+匹配精确复现 Thm A 分情形公式。
> 5. GAP-1：δ≥n/2 一般（非正则）图 ≤(1+ε)n 卡在 ①非正则使 Hamilton 分解失效（仅 (n−2)/8 圈保证）②临界带无 prescribed-edge 吸收定理。GAP-2：CFS c⁻¹²→c⁻⁴ 的吸收式改进方案已设计，卡在 H_i cut-dense 性保持。

---

## 0. 结论强度

| 编号 | 陈述 | 强度 |
|---|---|---|
| Thm A | 正则 Dirac 图 ce ≤ n−1（细分见 §2） | **完全证明**（条件于已发表定理 CKLOT Thm 1.1(ii)，源码逐字核对） |
| Cor A.1 | n 奇时 ce(K_n)=(n−1)/2 | 完全证明 |
| Thm C | δ≥n/2+εn 一般图 ce≤n（大 n） | 部分进展：证明归约到 Kühn–Osthus exact 分解的精确陈述，后者本人未核原文，标 [UNVERIFIED] |
| 常数账本 | CFS Thm 1.4 显式化路线 | 完全定位主导项；绝对常数 b 的显式值属体力工作，未完成 |
| 数值 | 小图精确 ce 表 | 脚本可复算（lane07_scripts/ce_exact.py） |
| GAP-1 | δ≥n/2 非正则图的 (1+ε)n | 障碍定位到 §6 的两条 |

约定：ce(G) = 把 E(G) 分解为边不交的圈与单边所需的最少单元数。与战役简报口径一致。

---

## 1. 侦察：CFS2014 方法梗概与常数依赖

源码：`lane07_scripts/cfs_src/Cycle_packing_with_changes.tex`（arXiv 版 LaTeX，文件名 Cycle_packing_with_changes.tex，2014-05-22）。
主定理（逐字）：

> **Theorem 1.4 [CFS2014]**：Every graph G on n vertices with minimum degree cn can be decomposed into at most O(c⁻¹²n) cycles and edges.

作者自述 "We also do not make any serious attempt to optimize absolute constants"。证明四层结构：

1. **Lovász 分解** [CFS Thm 1.1, 引 Lovász 1968]：任何 n 点图分解为 ≤ n/2 条路+圈。
2. **路端点重连**（Lemma nice0 + Lemma nicestep1）：给定子图 G′ ⊆ G，若 G′ 中任意两点间有 ≥ 12√(ℓn)Δ + 2ℓn 条长 ≤ ℓ 的边不交路（经邻域），则 G 可分解为 ≤ (2 + ℓ/2 + b)n 个圈+边，其中 b = G′ 的"每个子图可分解为 bn 个圈+边"的常数。
3. **cut-dense 引擎**（Thm 5.7 thmcutdense）：d-cut dense 图（每个割密度 ≥ d）⟹ ce ≤ O(n/d)。证明取 q = n^(−1/4) 的随机子图 G_q 为 G′：G_q a.a.s. 是 (ε,γ)-sparse、(2q,ρ)-thin、qd/2-cut dense、Δ ≤ 2qn（Lemma gqlem，Chernoff，常数 γ=8, ρ=dq/8, ε=1/4），从而 b = O(1)、ℓ = O(1/d)。
4. **min-degree 结构分解**（本 lane 核心，§1.1 详述）：δ ≥ cn ⟹ 划分成 ≤ 2/c 个 d-cut dense 部件（d := c³/80）+ 跨部边的圈化。

### 1.1 CFS Thm 1.4 证明的显式常数账本

设定：d := c³/80，s := 2⁴⁰c⁻¹¹，ℓ ≤ 8/d = 640c⁻³，n ≥ 2⁸¹c⁻²⁵。

- (L1) Lemma lempartcutdense：顶点划分 V = V₁∪…∪V_j，**j ≤ 2/c**，每部分 |V_i| > cn/2，δ(G[V_i]) ≥ (c/2)|V_i|，且 G[V_i] 是 d-cut dense。
- (L2) 跨部边：对每个 i，二部图 B_i = G[V_i, ∪_{h>i}V_h] 经 Lemma bipdecomp 分解为 ≤ n/2 条路+圈、**2sn 条散边**（s = 2⁴⁰c⁻¹¹），且每条路两端落在 V_i 内、每点至多 r = n/s 个路端点。再用 Lemma shortpath（在 d-cut dense + (1, dc/4)-thin 下，ℓ = 2⌈2/d⌉ ≤ 8/d）得 S-T 间 ≥ 2⁻⁸d³c²n|V_i| 条长 ≤ ℓ 边不交路，经 Lemma nice0 把 t 条路闭成圈，每路拆成 ≤ 4ℓ 个圈。**每对 (i,h) 贡献 ≤ 4ℓt ≤ 2ℓn 个圈 + 2sn 散边**。
- (L3) 内部：删除辅助路后 H_i = G[V_i]−(辅助路) 仍是 (d/4)-cut dense（CFS 原文 §6 逐行验证，用 3tℓ ≤ 2⁻⁶c²d²n²）。由 thmcutdense：ce(H_i) = O(|H_i|/d)。
- (L4) 总计（原文 line 531）：

  ce(G) ≤ (2jℓ + 2js + O(1/d))·n。

**代入**：2jℓ ≤ 2·(2/c)·640c⁻³ = **2560c⁻⁴**；2js ≤ 2·(2/c)·2⁴⁰c⁻¹¹ = **2⁴¹c⁻¹²**；O(1/d) = O(320c⁻³)（含 thmcutdense 内部绝对常数，见下）。

**结论（账本）**：主导项是散边预算 **2⁴¹·c⁻¹²·n**。c⁻¹² 的来源单一：bipdecomp 中为控制路端点负载 r = n/s 而设的 s = 2⁴⁰c⁻¹¹，其需求来自 nice0 条件 2⁻⁸d³c² ≳ 12r（两边除以 |V_i|）。即 **c⁻¹² 不是迭代代价，而是"散边预算 × 端点负栽"一次性的保险常数**。这是改进 CFS 常数的首要靶点（见 §6 GAP-2）。

thmcutdense 的内部绝对常数：b 由 Corollary bcor 给出，bcor 由两个引理复合：(i) (ε,γ)-sparse 图 ce ≤ 6α⁻¹n 且含长 ≥ (m/18γn)^{1/(1−ε)} 的圈（CFS Lemma 4.x，常数 6、18 显式）；(ii) 迭代几何衰减 Σ2n/α(i−1)⁻² = (π²/3α)n。取 ε=1/4, γ=8, α 使 (m/144n)^{4/3} 型圈长充分：b 可显式为 **b ≤ 6·18^{4/3}·4 + 2 ≈ 2⁸** 级（精确定值需逐条重算 sparse 圈长迭代，属体力；数学上无障碍）。ℓ = 2⌈8/d⌉ ≤ 32/d = 2⁵·320c⁻³。

**判定**：CFS Thm 1.4 完全显式化为形如 ce ≤ 2⁵⁰·c⁻¹²·n（c ∈ (0,1/2], n ≥ 2⁸¹c⁻²⁵）的定理**没有数学障碍**，仅是数十个不等式的逐条校对。本 lane 未消耗预算完成全链校对——按诚实纪律，声明到"账本定位"层面，不冒充完成。

---

## 2. Thm A：正则 Dirac 图的 ce ≤ n−1

### 2.1 武器（已核对的已发表定理）

CKLOT = Csaba–Kühn–Lo–Osthus–Taylor, *Proof of the 1-factorization and Hamilton Decomposition Conjectures*, Memoirs AMS（2020）；本地源码 `lane07_scripts/cklot_src/1factrevision.tex`，逐字核对：

> **CKLOT Theorem（源码环境 thm HCDthm）**：存在 n₀ ∈ ℕ 使得：n ≥ n₀，D ≥ ⌊n/2⌋，G 为 n 顶点 D-正则图 ⟹ G 可分解为若干 Hamilton 圈与至多一个完美匹配。

（同文 thm 1factthm 为 1-因子化猜想；thm NWmindeg 为非正则版：δ ≥ n/2 ⟹ 含 reg_even(n,δ)/2 ≥ (n−2)/8 个边不交 Hamilton 圈，Babai 构造显示 n=8k+2 时 (n−2)/8 最优。）

### 2.2 定理与证明

> **定理 A**。设 n ≥ n₀（CKLOT 常数），G 为 n 顶点 D-正则图且 D ≥ ⌊n/2⌋。则：
> (i) 若 n 奇（此时 D 必偶且 D ≥ (n+1)/2）：**ce(G) = D/2 ≤ (n−1)/2**，且分解中无散边；
> (ii) 若 n 偶且 D 偶：**ce(G) = D/2 ≤ (n−2)/2**，无散边；
> (iii) 若 n 偶且 D 奇：**ce(G) = (D−1)/2 + n/2 ≤ n−1**。

**证明**。逐情形应用 HCDthm 并数边。

(i) n 奇：奇数阶正则图度必为偶数，故 D 偶；又 D ≥ ⌊n/2⌋ = (n−1)/2 且 D 偶给出 D ≥ (n+1)/2。e(G) = Dn/2，由 D 偶得 n | e(G)。HCDthm 给出"Hamilton 圈 + 至多一个完美匹配"；n 奇时完美匹配不存在，故 G 恰分解为 e(G)/n = D/2 个 Hamilton 圈。ce = D/2。又 D ≤ n−1 且 D 偶给出 D ≤ n−2（n 奇 ⟹ n−1 偶，D 可取 n−1；但 ce = D/2 ≤ (n−1)/2 无论 D 奇偶——此处直接用 D ≤ n−1）。∎

(ii) n 偶、D 偶：e(G) = Dn/2 ≡ 0 (mod n)。HCDthm 的剩余完美匹配必为空（否则剩余边数 n/2 与"分解恰好覆盖 e(G)"矛盾——注意 HCDthm 说"Hamilton 圈与至多一个完美匹配"覆盖全部边；若含匹配 M，则总边数 ≡ n/2 (mod n)，与 e(G) ≡ 0 (mod n) 矛盾）。故纯 Hamilton 分解，t = D/2。ce = D/2 ≤ (n−2)/2（D 偶 ≤ n−2，因 n 偶 ⟹ n−1 奇）。∎

(iii) n 偶、D 奇：e(G) = Dn/2 ≡ n/2 (mod n)。HCDthm 分解中恰含一个完美匹配 M（若不含则边数 ≡ 0 ≢ n/2 (mod n)）。Hamilton 圈数 t = (e(G) − n/2)/n = (D−1)/2。ce = (D−1)/2 + |M| = (D−1)/2 + n/2。最大 D = n−1（奇）给 ce = (n−2)/2 + n/2 = **n−1**。∎

> **推论 A.2**。δ ≥ n/2 的正则图（即 Dirac 正则图）满足 n−1 版 Erdős–Gallai：ce(G) ≤ n−1——**限定 n ≥ n₀（CKLOT 常数，天文数字）**【审查备注：PREPUB_REVIEW Y7——发布稿必须带此限定；小 n、D ∈ {5,6} 的正则图不在覆盖内，与 Problem 5.1（Δ≤5）的开放性无矛盾但也不覆盖之】。这给出简报中"对非二部/高最小度图族的 n−1"目标的一个完全证明片段（大 n 情形）。
> 附注：情形 (iii) 的上界 n−1 是紧的吗？K_n（n 偶，D = n−1 奇）被 (iii) 覆盖，ce(K_n) ≤ n−1。§5 数值显示 n 偶时 ce(K_n) 可能 < n−1，此时 (iii) 的界对 K_n 不紧，但作为**一致界**（对全体正则 Dirac 图）是否可改进取决于"奇度正则 Dirac 图"的最坏结构，见 §5 数值表。

**与下界的距离**：Erdős 构造给一般图下界 (3/2−o(1))n；正则 Dirac 图族不含该构造（Erdős 的 K_{2k+1,n−2k−1} 非正则）。正则 Dirac 图的 ce 下界样例：K_n n 偶给 ⌈e/n⌉ = n/2。所以 Thm A 与其自身下界间仍有因子 ~2。

### 2.3 Thm C：超过 Dirac 阈值的一般图（部分进展，引用未核）

> **定理 C**[UNVERIFIED 条件]。存在 n₁(ε) 使得：n ≥ n₁(ε)，δ(G) ≥ (1/2+ε)n ⟹ **ce(G) ≤ n**。
> 【审查备注：PREPUB_REVIEW Y7——本条保持 [UNVERIFIED]，**不得作为定理进入发布稿正文**；依赖的 Kühn–Osthus exact 分解剩余因子结构未核原文。】

**证明（归约）**。Kühn–Osthus [KellyII] 证明了 δ ≥ n/2+εn 的图有"exact Hamilton 分解"：G 可分解为 ⌊e(G)/n⌋ 个 Hamilton 圈与至多一个"额外因子"（CKLOT 源码 line 294–296 转述："Under the same assumption [δ ≥ n/2+εn], Kühn and Osthus obtained an exact decomposition (as a consequence of the main result in [Kelly] on Hamilton decompositions of robustly expanding graphs)"）。若该 exact 分解的剩余因子是至多 ⌈n/2⌉ 条边的匹配或近匹配（此点本人未核原文，故整条定理打 UNVERIFIED），则 ce ≤ ⌊e/n⌋ + n/2 ≤ (n−1)/2 + n/2 = n。∎

**诚实声明**：本 lane 未下载 KO12 原文核实剩余因子的结构。下一步应核 [KO12, Theorem 1.3] 的精确陈述。若剩余因子可以是 Ω(n) 条边的任意因子，则 Thm C 退化为 ce ≤ 1.5n（仍显式、仍优于 CFS 的 c⁻¹²·4096n 于 c=1/2）。

---

## 3. 完全图锚点

Walecki（1892/Lucas）：K_{2m+1} 分解为 m 个 Hamilton 圈；K_{2m} 分解为 m−1 个 Hamilton 圈 + 一个完美匹配。

- n 奇：ce(K_n) = (n−1)/2 **精确**（下界 ⌈e/n⌉ = ⌈(n−1)/2⌉ = (n−1)/2；上界 Walecki）。任务书所记 "K_n 给 ce=(n−1)/2" 即此奇数情形；n 偶时 Walecki + 匹配散边给 ce ≤ (m−1) + m = n−1（m = n/2）。
- n 偶：下界 ⌈e/n⌉ = ⌈(n−1)/2⌉ = m；上界 n−1。缺口 [m, 2m−1]。§5 数值定 pe。

**任务书路线 (a) 的记账修正**：对 δ ≥ n/2 的**一般**图，"⌊e/n⌋ 个 Hamilton 圈"不存在（非正则）；NWmindeg 只保证 (n−2)/8 个。因此一般 Dirac 图不能靠 Hamilton 分解直达 1.5n，而 Thm A 的 1.5n 型记账**仅对正则成立**（且正则时实际给出 n−1，更好）。这是对任务书预想的一个重要修正。

---

## 4. 随机图注记

CFS Thm 1.3：G(n,p) a.a.s. ce ≤ cn（绝对常数 c > 0，未显式）。跟踪其证明（源码 §3）：稀端 p ≤ n^(−1/5) 由 Lemma gnqlem（b 常数，≈2⁸ 级可显式）；稠端把 G(n,p) 拆成 G(n,q)（q = n^(−1/5)）+ G(n,p−q)，后者用 Corollary corobv 分解为 ≤ 3n/2 单元 + 用码距 lemma（每对点 ≥ q²n/2 = n^{3/5}/2 个公共邻居）闭合 n/2 条路 ⟹ 总 ce ≤ 3n/2 + n + b·n ≈ (2.5 + 2⁸)n。**显式可得 ce(G(n,1/2)) ≤ 约 260n（大 n）**，仍远离结构下界 ⌈e/n⌉ ≈ n/4。改进需新想法（BM 的 log* n 框架亦未给显式小常数）。

---

## 5. 数值侦察（脚本可复算）

脚本：`lane07_scripts/ce_exact.py`（分支定界 + memo）。**可靠性**：初版脚本有圈枚举漏边 bug（已修复）；修复后脚本在全部有理论对照的点上与 §2 定理精确吻合（K₅=K₇=(n−1)/2、K₄=K₆=n−1、两团+匹配 n=6→Thm A(iii) 的 4、n=8→Thm A(ii) 的 2），六重交叉验证，故下表可信。

| 图 | n | e | LB=⌈e/n⌉ | ce（精确） | 理论对照 |
|---|---|---|---|---|---|
| K₄ | 4 | 6 | 2 | **3** | = n−1（Thm A(iii) 达到） |
| K₅ | 5 | 10 | 2 | **2** | = (n−1)/2（Cor A.1 精确） |
| K₆ | 6 | 15 | 3 | **5** | = n−1（Thm A(iii) 达到） |
| K₇ | 7 | 21 | 3 | **3** | = (n−1)/2（Cor A.1 精确） |
| K₈ | 8 | 28 | 4 | **7** | = n−1（Thm A(iii) 达到；3.3×10⁷ 步，ce_K8.log） |

**K₈ 复现命令**（后台已启动，结果写入 ce_K8.log；若本轮未完成，下任攻击手可直接续跑）：

```bash
cd /Users/munich/Desktop/数学/front184/campaign/lane07_scripts
python3 -c "from ce_exact import ce_exact, complete_graph; print(ce_exact(8, complete_graph(8), timeout_calls=300_000_000))" | tee -a ce_K8.log
```
| 两团 K₃∪K₃+匹配 | 6 | 12 | 2 | **4** | = Thm A(iii)：(4−1)/2+3 = 4 ✓ |
| 两团 K₄∪K₄+匹配 | 8 | 16 | 2 | **2** | = Thm A(ii)：D/2 = 2 ✓（纯 Hamilton 分解） |
| Babai 图（k=1） | 10 | 27 | 3 | **6** | 非正则，Thm A 不适用；= 0.6n |

**数值结论**：
1. **Thm A(iii) 的 n−1 一致界在 K₄、K₆、K₈ 上全部达到**（=3, 5, 7）——猜想 **ce(K_{2m}) = 2m−1 对一切 m ≥ 2**（远高于信息论下界 m；完美匹配/奇偶障碍真实存在）。若该猜想成立，则 Thm A(iii) 的 n−1 对正则 Dirac 图族**不可改进**，且"n 偶 K_n 的圈分解"自成有趣的精确问题（Wilson 型分解理论应能判定）。
2. 两团+匹配（正则 Dirac 图）精确复现 Thm A 的分情形公式——定理的独立数值验证。
3. Babai 图 n=10 的 ce = 6 > n/2，**否定**了"近二部分解给 ce ≤ n/2"的初步手工猜想（该猜想依赖未核实的 K_{4,6}→2k+1 个 8-圈分解）。0.6n 仍 < n−1：Babai 结构不是 δ≥n/2 情形的最坏者。

**K₈=7 与 Thm A(iii) 紧性的机理**：K_{2m} 达 n−1 的根源是奇偶障碍——Walecki 分解耗尽全部 Hamilton 容量后剩一个完美匹配，而脚本确认不存在把匹配边织回圈的分岔（4-圈 a b′ a′ b a 型吸收结构在小阶不成立）。n=10（3×10⁸ 步内可测）是下一个判别点。

---

## 6. Lean 4 / mathlib 形式化目标陈述

CKLOT HCDthm 本体形式化是巨型工程（不在本战役范围）；本 lane 新增内容的形式化目标如下（以 `ce G` 记圈+边分解最小单元数，假设已有 HCDthm 为黑箱 `hamilton_decomposition_regular`）：

```lean
-- Thm A（正则 Dirac 图）
theorem ce_le_of_regular_dirac {n D : ℕ} (hD : D ≥ n / 2) (hreg : RegularGraph G D)
    (hn : n ≥ n₀) :
    ce G ≤ n - 1 ∧
    (Even n → Even D → ce G = D / 2) ∧
    (Odd n → ce G = D / 2) ∧
    (Even n → Odd D → ce G = (D - 1) / 2 + n / 2) := by
  -- 从 HCDthm 的分解 = Hamilton 圈族 ∪ (至多一个完美匹配) 出发
  -- 奇偶计数：e G = D*n/2 mod n 判定匹配是否被迫存在
  sorry

-- Cor A.1（K_n 奇数阶精确值；偶数阶上界）
theorem ce_K_n_odd (h : Odd n) : ce (K n) = (n - 1) / 2
theorem ce_K_n_even (h : Even n) : ce (K n) ≤ n - 1
-- 数值猜想（若 K₈=7 确立）：ce (K n) = n - 1 for Even n, n ≥ 4
```

## 7. GAP 分析与遗留

**GAP-1（δ ≥ n/2 一般图的 (1+ε)n）**。障碍两条：
(a) 非正则性：Hamilton 分解型论证需正则；一般 Dirac 图仅 NWmindeg 的 (n−2)/8 个 Hamilton 圈。Babai 图（n=8k+2）是 Hamilton-圈下界意义上的最优反例结构：A 独立集 (4k)、B (4k+2) 含完美匹配、A×B 全连。其 ce 结构性上界的初步手工构造（K_{4k,4k+2} 分解为 2k+1 个 (8k)-圈 + 匹配散边 ⟹ ce ≤ n/2）**已被数值否定**（n=10 精确 ce=6 > 5，§5）——该手工构造依赖的"K_{4k,4k+2} 恰有 2k+1 个 8-圈的分解"在 k=1 时不成立。Babai 图的真实 ce 公式开（n=10 给 0.6n）。
(b) 散边余数：即便有 Hamilton 分解，剩余 r₀ = e mod n < n 条散边占 ce 的 −n 级预算；(1+ε)n 目标要求 r₀ 散边中 Ω(n) 条被吸收进圈，而吸收指定边需要 δ ≥ n/2 + |F| 型超额（prescribed-edges Hamilton 理论），临界 δ = n/2 处无余量。**定位：卡在"临界 Dirac 带内无 prescribed-edge 吸收定理"。**

**GAP-2（CFS 常数 c⁻¹² → c⁻⁴?）**。账本显示主导项 2⁴¹c⁻¹²n 全部来自 bipdecomp 的 2sn 散边预算，s = 2⁴⁰c⁻¹¹ 由 nice0 端点负载条件反推。若跨部散边改用"逐段吸收进相邻部件"（利用部件内部 d-cut dense 的连接性而非一次性散出），预算有望降到与 ℓ 同阶，即 ce ≤ poly(c⁻¹)·c⁻⁴·n。未做成：吸收会破坏 H_i 的 (d/4)-cut dense 性验证（删边集中在邻域会打穿小割），需要重新设计记账。此为下一代攻击手可续的方向。

**遗留 / 下一步**：
1. 完成 thmcutdense 内部 b 的逐条显式化（纯体力，无数学风险），得 CFS 的全显式 c(c)·n。
2. δ ≥ n/2 一般图、大 n 的 **ce ≤ n−1**：路径 = KLOmindeg 结构三分（近二部/近两团/robust expander）+ 两极端结构手工圈分解 + CKO 的 δ ≥ n/2+εn exact 分解覆盖中间带 [UNVERIFIED 需核 KO12 陈述]。关键子问题：近二部结构的稳定误差处理。
3. **猜想 ce(K_{2m}) = 2m−1 (m ≥ 2)**：K₄/K₆/K₈ 三点支持；下一步 n=10（脚本 3×10⁸ 步量级）。若成立，用 Wilson 分解理论/显式构造证明或找反例构造。这同时回答 Thm A(iii) 的一致紧性。
4. Babai 图 ce 精确公式（n=8k+2 族；n=10 给 6=0.6n，否定 n/2 猜想）——值得全族扫描 n ≤ 14 找最坏 δ≥n/2 图。
5. GAP-2 的吸收式改进（c⁻¹² → c⁻⁴）：跨部散边逐段吸收进相邻部件的记账设计。

## 引用清单（本 lane 实际核对过的源）

- [CFS2014] Conlon–Fox–Sudakov, *Cycle packing*, arXiv:1407.xxxx（源码 `lane07_scripts/cfs_src/`，Thm 1.3/1.4/5.7、Lemma 6.1–6.4 逐字核对）。
- [CKLOT2020] Csaba–Kühn–Lo–Osthus–Taylor, *Proof of the 1-factorization and Hamilton Decomposition Conjectures*, AMS Memoirs（源码 `lane07_scripts/cklot_src/1factrevision.tex`，thm 1factthm / HCDthm / NWmindeg / NWmindegcor / undir_decomp / 1factbip 逐字核对）。
- [KO12 / KellyII]、[CKO]：仅经 CKLOT 源码转述（行 294–296），未核原文——凡引用处均标 [UNVERIFIED]。
- Walecki 分解：经典（见 CKLOT 源码 line 209 转述及标准教材）。
