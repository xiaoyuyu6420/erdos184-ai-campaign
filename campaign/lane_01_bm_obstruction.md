# Lane 01: 解剖 Bucić–Montgomery——log* 墙的精确定位

> 1. **log* 的唯一来源**：单步引理 Lemma (lem:density, main.tex line 1020) 的剩余平均度映射 d ↦ O(log²⁷⁴ d)，迭代 log* n 次（thm:logstar 证明, lines 1039–1049）。除摘要/记号外，全文 log* 仅出现于该最终迭代（lines 1033, 1042, 1049）；第 2–5 章的全部机器不含 log*。
> 2. **log²⁷⁴ 的精确谱系**（已逐行核算）：次线性扩张比 eps/log²n（Def, line 479）→ 撒水批数 ℓ≈log⁴ (line 726) → 失败率 e^(−u·τ/log²²) → well-core 损耗 1/log²⁶ (line 827) → F-预算 1/log²⁷ (line 843) → 三分 k=2¹⁷log⁴² (line 892) → 鲁棒性需求 s ≥ log¹³⁵ (line 674) → 二次切分删除 4sr·log r = r·log²⁷⁴ r (line 978)。链条各级的 slack ≤ 3 个 log-幂；**274 ≈ 2×135+4 是硬算出来的，不是浪费出来的**。
> 3. **两行归约**：splitting-into-expanders 取 s=0 时把任意图**精确**切分为 (eps,0)-expander 且 Σ|G_i| ≤ 2n（line 568, 570）⟹ **EG ⟺ "每个 (eps,0)-expander 分解为 O(r) 个圈+边"**。BM 对 s ≥ log²⁷³r 的 expander 得 3r 圈 + 2¹¹r·log¹⁰r 边（Lemma, line 962）。墙 = (i) 鲁棒化价格 4sr·log r（BM 自认主瓶颈，line 1063）+ (ii) 骨架闭环价格 r·log¹⁰r。
> 4. **相变定位**（本 lane 新结果，已形式化）：剩余度映射 f 的迭代深度决定一切。f = 固定 polylog ⟹ Θ(n log* n)；f(d)=2^((log d)^θ), θ∈(0,1) ⟹ O(n·log log log n)；f(d)=log* d ⟹ O(n)。**BM 恰好卡在 2^{O(log log r)} 那一格**；跨过"polylog → 次多项式"一格立即得 O(n log log log n)。【**PREPUB_REVIEW R1 撤回注**：上式的深度计算正确并保留，但"跨过一格 = 进展"的解读方向反了——O(n log log log n) **弱于** BM 现有 O(n log* n)（log* n = o(log log log n)），不是优越格；见 lane_12 命题 12.2 与 MERGE_1 修正 1。】
> 5. **三路评估**：(a) 改迭代结构 = 形式化死路（迭代对给定单步引理已最优，唯一改进通道就是单步引理本身）；(b) 层数常数化 = 前线，含两个子墙（鲁棒化价格 / 骨架循环依赖），s=0 版难度 = EG 本体；(c) 绕开 expansion = 目前无立足点（Eulerian/Hajós 重组撞同一面墙）。

---

## 结论强度

- **完全证明**：3 个形式化命题（迭代深度 meta-lemma；EG ⟺ EG-for-expanders 归约；相变命题）——证明附下，逐步可查。
- **完全证明（按行号引用）**：BM 证明树与 log²⁷⁴ 谱系表——基于对 arXiv:2211.07689 源码（本地 `/Users/munich/Desktop/数学/front184/2211.07689_src/main.tex`，2023-11-13 打包版本）的逐行精读。
- **部分进展（架构条件命题）**："骨架困境"命题（第四节 D）：在 Lovász-路径 + 储备库闭环架构内，剩余度必为 polylog 型。证明给出但依赖架构假设，明确标注。
- **数值/文献缺口**：未做 2022 后文献核查（简报已确认 BM 仍为最优）；Krivelevich 2019 精确陈述未引用。

**编号约定**：BM 源码定理环境共享一个计数器；下文编号（如"Lemma 22"）由我按出现顺序推算，未经编译验证（本机无 LaTeX）。**以 label + 行号为准**，推算编号仅供对照（thm:logstar = "Theorem 2" 已由论文自身小节标题 line 1010 证实）。

---

## 一、BM 证明骨架（逐行解剖）

### 1.1 证明树

```
Thm 2 (thm:logstar, line 198)  O(n log* n)
│
└─【迭代】lines 1039–1049:  d_{i+1} ≤ C·log²⁷⁴(d_i)，ℓ ≈ log* n 步后 d_ℓ = O(1)
   总代价 ≤ Cn·ℓ + O(n) 边
   │
   └─ Lem 22 (lem:density, line 1020)【单步】
      n 顶点、平均度 d ≥ 2 ⟹ ≤ 13n 圈 + 剩余子图平均度 O(log²⁷⁴ d)
      │
      ├─ (A) 极大边不交长圈 ≥ d（line 1024）：≤ n/2 圈；此后无圈 ≥ d
      ├─ (B) Lem 10 (splitting-into-expanders, line 570)，s=0, eps=2⁻⁵：
      │       精确切分为 (2⁻⁵,0)-expander，Σ|G_i| ≤ 2n
      ├─ (C) Lem 21 (lem:onelongcycle, line 988)：(eps,0)-expander 含
      │       Ω(r/log⁴r) 圈 ⟹ 每片 |G_i| = O(d·log⁴d)
      └─ (D) Thm 20 (thm:decompexander-explicit, line 974)：
              每片 → ≤ 6r 圈 + O(r·log²⁷⁴r) 边
              │
              ├─ (D1) Lem 10 再切，s = log²⁷³r：删除 ≤ 4sr·log r = 4r·log²⁷⁴r 边
              │        ⟵ s 的下界来自 (D2) 要求 s ≥ log²⁷³ (line 962)
              ├─ (D2) Lem 19 (lem:decompexander, line 962)：
              │        (eps, s≥log²⁷³r)-expander → ≤ 3r 圈 + 2¹¹r·log¹⁰r 剩余边
              │        │
              │        ├─ Lem 11 (lem:partitionedgesintoexpanders, line 624)，k=3：
              │        │   三片边不交 (eps/4, s')-expander，s' = √(s·eps)/(24 log r) ≳ log¹³⁵r
              │        ├─ Lem 16 (lem:sparseconnect, line 923)：骨架 G_i' ⊆ G_i，
              │        │   ≤ 2⁹r·log¹⁰r 边，(log⁷r, 2)-path connected through V_i
              │        │   ├─ Thm 12 (thm:pathconnect, line 673)：through V 的路长 ≤ 4log⁵r
              │        │   └─ Lem 9 (lem:template, line 432)：模板 Δ(H) ≤ 2⁸log⁵r
              │        │       骨架 = 路长 × 模板边数 = 4log⁵r × 2⁷r·log⁵r = 2⁹r·log¹⁰r (line 930)
              │        └─ Cor 18 (cor:lovasz, line 947)：H_i 分解为端点度 ≤ 2 的路径
              │            经 G_i' 闭环 → 覆盖骨架之外全部边；剩余 = 骨架本身
              │
              └─ (D3) 小 expander（< n₀ 顶点）整块计入剩余（line 980）
```

### 1.2 三个任务问题的直接回答

- **log* 出现在哪一层递归**：只在最外层（thm:logstar 证明，lines 1039–1049）。第 2–5 章（工具层）与第 6 章前四小节完全不含 log*。line 1042–1047 显式使用了"迭代到第 i 层时 log^{[i]}n 仍 ≥ 300C"，即 log* 深度被显式消费的唯一位置。
- **每层递归付出什么**：≤ 13n 个圈（= n/2 长圈 + 12n 来自 Σ|G_i| ≤ 2n 的小 expander 分解，line 1026），换得剩余边数从 nd/2 降到 n·O(log²⁷⁴d)/2——即每层把边的规模压掉一个 log-塔层，但圈代价恒为 Θ(n)，与 d 无关。
- **哪一步依赖"递归深度可以取对数"**：严格说，没有任何一步"依赖对数深度"——依赖的是**单步剩余映射是固定的 log-塔复合**。log* 深度是该映射的迭代深度，是输出而非输入（形式化见命题 A）。这意味着：改迭代层（路径 a）没有独立收益，见第三节。

---

## 二、log²⁷⁴ 的谱系表（根到叶，全部行号已核对）

| # | 位置 (label / 行号) | 内容 | 产生的 log-指数 | 必要性核算 |
|---|---|---|---|---|
| 0 | Def (defn:robust-sublinear-expansion) / 479 | 扩张比 eps·|U|/log²n | **比值 1/log²n = 全链条之根** | KSS 规范；注意切分引理对比值形式**不敏感**（见 2.1），故此根是"记号选择 + KSS 传统"，改 1/log n 只把 274 压到 ~180，log* 不变 |
| 1 | Lem (lem:expandintorandom) / 718–812 | 撒水 ℓ = log⁴n 批；p ≈ 1/(15ℓ) (726–729) | 4 | 必要 ℓ ≥ 2⁷log³n/eps（line 808: (1+eps/2⁶log²n)^ℓ ≥ 2n/3）；slack ×log |
| 2 | Prop (prop:red-blue-expansion-robust-both) / 521–562 | 星叶 d = log⁴n（=1/p，撒水需 p·d ≥ 1/15）；Δ = 2log⁹n | 9 | 9 = 4 + 4 + slack（Δ ≥ 2d） |
| 3 | McDiarmid 应用 / 783 | 失败率 e^(−Ω(|W|/log²²n)) | 22 | 22 = 4(p) + 2×9(Δ²) |
| 4 | Prop (prop:well-expanding-core) / 825–835 | well-expanding 阈值 τ = log²⁴n；核损耗 1/log²⁶n | 24, 26 | 并查界需 e^(−uτ/log²²) ≪ e^(3u log n) ⟹ τ ≥ log²¹；26 = 24+2（line 832 的 +1 与 ≤3|U'|τ）|
| 5 | Lem (lem:expandintorandom2) / 841–875 | F-预算 \|F\| ≤ \|U\|/log²⁷n | 27 | 26 + 1 slack |
| 6 | Thm (thm:pathconnect) 证明 / 890–904 | k = 2¹⁷log⁴²n；F-预算 2¹⁷\|U\|log¹⁵n | 42 = 15+27 | line 899: 2¹⁷·log¹⁵/k = 1/log²⁷ ⟺ k = 2¹⁷log⁴² ✓ |
| 7 | Thm (thm:pathconnect) / 673 | 需 s ≥ log¹³⁵n | **135** | 135 = 84 + 50 + 1：s'² = s·eps/(64k²log²n) ≥ 4log⁴⁸ ⟺ s ≥ 256k²log⁵⁰/eps，k² = 2³⁴log⁸⁴ ⟹ s ≳ log¹³⁴ ✓（切分约束 s ≥ 2¹²eps⁻¹k²log⁴ ≈ log⁸⁸ 非主导，line 625）|
| 8 | Lem (lem:partitionedgesintoexpanders) / 624–660 | k 片切分，s' = √(s·eps)/(8k log n) | s 损耗 √s 级 | eps 仅降 4 倍（"高效切分"，line 622）|
| 9 | Lem (lem:decompexander) / 962 | 需 s ≥ log²⁷³r（k=3: s' = √(s·eps)/(24 log r) ≥ log¹³⁵）| **273** | 273 = 2×135 + 3：s ≥ (24 log r)²·log²⁷⁰/eps = 2^≈14.5·log²⁷² ✓ |
| 10 | Thm (thm:decompexander-explicit) / 974–983 | 切分删除 4sr·log r，s = log²⁷³r | **274 = 273+1** | **主导项**；BM 自认主瓶颈（line 1063）|
| 11 | Lem (lem:sparseconnect) / 923–934 | 骨架 ≤ 2⁹r·log¹⁰r 边 | **10 = 5+5** | 路长 4log⁵（= log⁴ℓ × log）× 模板 Δ=2⁸log⁵（= 预算 log⁴ + 1 slack；预算 log⁴ = (ℓ_H·log n)²·const，ℓ_H = ¼log²，line 462 已核算 2¹⁰/16²·log⁴ = 4log⁴ ✓）|
| 12 | Lem (lem:density) / 1020–1027 | f(d) = O(log²⁷⁴d) | 274 | 10 ≪ 274：骨架被 (D1) 主导 |
| 13 | Thm 2 证明 / 1039–1049 | 迭代 ℓ ≈ log* n | log* | line 1042–1047 |

**要点**：每一级的 log-指数相对其必要性只有 ≤ 3 个幂的松弛。把比值 1/log²n 换成 1/log n、收紧 ℓ 到 log³、τ 到 log²¹ 等，只把 274 压到 ~200 上下——**多项式 log 的"形状"不变，log* 不变**。这不是常数浪费问题，是结构问题。

### 2.1 一个容易被忽视的事实：切分引理对扩张比不敏感

Lemma 10 (splitting-into-expanders) 的归纳证明（lines 574–609）只用到：(i) 非 expander 时存在失败集 U；(ii) n₁ = |U|+|N(U)| ≤ ⅔n(1+eps/log²n) < ¾n。把定义中的 1/log²n 换成 1/log n 甚至**常数 eps**，逐字成立（bookkeeping 只会更松）。BM 选择 1/log²n 是 KSS 规范（"每个图都含这种 expander"的保证水平，line 489），不是切分的限制。**含义**：链条根部的"比值"不是墙；墙在比值往下每一级的**鲁棒性购买价与骨架尺寸**。

---

## 三、形式化命题（本 lane 的可验证产出）

### 命题 A（迭代深度 meta-lemma）

设分解算子 Φ 满足：每个 n 顶点、平均度 d ≥ 2 的图可分解为 ≤ a·n 个圈+边，以及一个剩余子图，其平均度 ≤ f(d)（f: ℕ→ℝ₊）。令 K(n) = min{ i : f^i(n) ≤ 2 }（f^i 为 i 次迭代）。则每个 n 顶点图可分解为 ≤ a·n·(K(n)+1) + n 个圈+边。

**证明**：归纳。G₀ = G，G_{i+1} = Φ(G_i) 的剩余图，d_i = 平均度。若 d_i ≥ 2 则 |E(G_{i+1})| ≤ n·f(d_i)/2（顶点数 ≤ n）。到第 K(n) 层剩余平均度 ≤ 2，剩余边数 ≤ n。每层圈+边 ≤ a·n。总计 ≤ a·n·K(n) + n。∎（这正是 BM lines 1039–1049 所做的事，抽象化。）

**推论 A1**：f(d) = log^c d（任意固定 c, C）⟹ K(n) = log* n + O(1)，总代价 Θ(n·log* n)。任何**固定的** log-塔复合 f = log∘log∘…∘log（j 层）同理给 K = ⌈log* n / j⌉ = Θ(log* n)——**j 再大只省常数因子**。

**推论 A2**：总代价 O(n) ⟺ K(n) = O(1)。特别地 f(d) = log* d 给 K ≤ 3（n → log* n ≤ 6 → log* 6 ≤ 3 → done），故**"剩余平均度 ≤ log* d + O(1)"的单步引理即证 EG**。

**推论 A3（相变命题）**：设 f 如下，则 K(n) 渐近为——
- f(d) = 2^{C log log d}（即 polylog）：K = Θ(log* n)。（证：x_i = log f^i(n) 满足 x_{i+1} ≤ 2 log x_i，每步降一个 log*-层。）
- f(d) = 2^{(log d)^θ}, θ ∈ (0,1)：K = Θ(log log log n)。（证：x_{i+1} = x_i^θ，x_k ≤ 2 ⟺ θ^k·log log n ≤ 1。）
- f(d) = d^{1−δ}：K = Θ(log log n)。（CFS 2014 所在格。）

**解释**：从 polylog 到 2^{(log d)^θ} 有一个**相变**：迭代深度从 log* n 突降到 log log log n。BM 的 f(d) = Θ(log²⁷⁴d) = 2^{274 log log d} 恰好停在相变线之前。

### 命题 B（EG ⟺ EG-for-(eps,0)-expanders）

若存在 eps₀ ∈ (0,1] 与 c，使每个 (eps₀, 0)-expander（按 Def line 476，比值 eps₀|U|/log²n）分解为 ≤ c·r 个圈+边，则每个 n 顶点图分解为 ≤ 2cn 个圈+边。反之显然。

**证明**：对任意图 G 取 eps = min(eps₀, 2⁻⁵)，用 Lemma 10（line 570）取 s = 0：由 line 568 的明确陈述（"Setting s = 0 … obtains a full decomposition"），删 0 条边、精确切分为 (eps,0)-expander G_1,…,G_r，Σ|G_i| ≤ 2n。每片用假设分解，总计 ≤ c·Σ|G_i| ≤ 2cn。（eps₀-扩张 ⟹ eps-扩张，定义同形。空片平凡。）∎

**推论 B1**：BM 管线的剩余项若从 O(r·log²⁷⁴r) 降到 O(r)，则 EG 直接得证——log²⁷⁴ 剩余就是整个问题的余量。
**推论 B2**：命题 B 对"哪个 eps"不敏感、且由 2.1 对比值形式也不敏感。所以问题唯一地等价于：**把 (·,0)-expander 全分解**。BM 能做到 (eps, log²⁷³r)-expander 的 3r 圈 + 2¹¹r·log¹⁰r 边（Lemma line 962）。

### 命题 C（骨架困境；架构条件命题，非无条件定理）

**架构假设**：分解具有如下形态——(i) 把 E(G) 划分为" Lovász 路径部分"𝒫 与"储备库部分"ℛ，𝒫 中路径端点度 ≤ 2 且内部顶点避开对应的随机类 V；(ii) 每条路径经 ℛ 中过 V 的路闭环；(iii) ℛ 必须对**先验未知、对抗选取的**端点度 ≤ 2 的路径族通用（因 𝒫 依赖 ℛ，存在循环依赖：𝒫 = 分解(G − ℛ)，而 ℛ 的选择需先于 𝒫）。则剩余边 ≥ |ℛ| − Σ_{Q∈𝒬} len(Q)，且：

- **稀储备库支**：|ℛ| = o(n·polylog 不可达)。通用路由需含 n/2 条边不交路连接对抗性的远距离对；而在平均度 d、阶 r 的图中最远对距离 ≥ log r / log(d+1)（Moore 界），故 |ℛ| ≥ (n/2)·log r/log d 型下界（对存在足够多远对的图——常数度类 expander 即是，[此步对任意 (eps,0)-expander 未证，标 GAP]）。
- **胖储备库支**：|ℛ| = Θ(|E|) 时剩余 = |ℛ| − O(n·路由长) ≈ c·|E|，剩余度 f(d) ≥ c·d：迭代无进展。

**结论（架构内）**：f 要么 polylog 型（稀支），要么线性型（胖支），没有中间格。相变格 2^{(log d)^θ} 在此架构内不可达。

**诚实标注**：[GAP: "对抗性远对匹配在任意 (eps,0)-expander 中存在 n/2 条"未证；命题仅在架构假设下成立，且假设 (iii) 的循环依赖是否可破（"边用边消耗"式同时路由+分解）正是路径 (b) 的核心开放点。] 反向自检：BM 用稀支（骨架 2¹¹r log¹⁰r），BM 自己在 line 1063 指认的主瓶颈是胖支的变形（二次切分删除 4sr log r）——两者是同一困境的两次收费。

---

## 四、log* 墙的最终表述

**墙 = 单步引理（Lemma line 1020）的剩余映射 f(d) = log²⁷⁴d 停在相变线前。** f 由两项费用构成，均已定位到行：

1. **鲁棒化价格**（主导）：路径连通机器（Thm line 673 及其全部前置，Prop lines 503/521/825/841，Lem lines 624/718）处处需要 s = polylog(r) 的鲁棒性，而 (eps,0)-expander 没有它；用 Lemma 10（line 570）购买鲁棒性 s 的价格是 4sr·log r 条删除边。**鲁棒性无法从次线性扩张免费导出**：叶顶点论证——单点 U 的扩张保证 eps/log²n < 1 为空，一条被删边即可杀死 N(U)，故鲁棒性必须来自度/密度（red-blue 二分，line 503），而次线性比值下 red-blue 给出的鲁棒预算 ≤ eps/log²n = o(1)。这不是 proof 技巧缺口，是定义层面的鸿沟。
2. **骨架闭环价格**：2¹¹r·log¹⁰r（line 930）。log¹⁰ = 嵌入路长(4log⁵) × 模板度(2⁸log⁵)；模板度 ≥ ℓ²（Aharoni–Haxell 极大匹配阻塞预算 (ℓ·log n)²·k，line 418/424 的二次耦合）× 撒水稳健性。**即使鲁棒化免费，log¹⁰ 仍把 f 钉在 polylog ⟹ 仍 log\***。

**去掉 log* 需要什么**：把 f 从"固定 log-塔"变为"自指型"。具体阶梯：
- O(n log log log n)：expander 分解剩余 L(r) = r·2^{(log r)^θ}（θ<1 固定）且鲁棒化价格同阶；【PREPUB_REVIEW R1：该格为退化方向，弱于 O(n log* n)，不作目标——见 lane_12 命题 12.2、MERGE_1 修正 1】；
- **O(n)（=EG）**：L(r) = r·log* r 型（命题 A 推论 A2），即鲁棒化与骨架合计 O(r·log* r)；L(r) = O(r) 时单步即 EG（命题 B1）。

---

## 五、三条突破路径评估

### (a) 改 BM 的迭代结构

- **已知最近距离**：距离为 0，但方向为负——命题 A 证明迭代对给定单步引理已闭环最优；BM 的 k+1 次迭代权衡（line 1063 自述：O(kn) 圈 + n·log^{[k]}n 边）在 k 上是线性的，无 sub-log* 甜点。
- **还缺的引理形态**：无。任何迭代层改进都严格归约为单步改进，即路径 (b)。
- **难度评估**：★☆☆☆☆（作为独立方向：死路，形式化封死）。**建议全战役不再在迭代层投入**。

### (b) 找"层数常数化"的结构引理

即单步引理的剩余从 r·log²⁷⁴r 降格。含两个子墙：

- **(b1) 鲁棒化价格**：s 从 log²⁷³ → 小常数，删除价 4sr·log r → o(r·polylog)。
  - 最近距离：BM line 1063 自认此为主瓶颈；除 Lemma 10 的通价外**无任何更便宜的鲁棒化结果存在**（我未在 BM 内或简报文献中见到）。
  - 缺的引理形态："每个 (eps,0)-expander 可通过删除 o(r·polylog r) 条边变为 spanning (eps', s)-expander，s = polylog(r) 或更小"（自鲁棒化引理）。注意引理 B 证明此价不能是零（叶顶点障碍），但 Ω(?)–O(sn log n) 之间完全空白——连"鲁棒化价格的下界是什么形状"都无人知道。
  - 难度：█████（很难）。这是 BM 明示的正面攻击点，但叶顶点/薄割障碍说明需要密度侧新思想（如 red-blue 的量化改进：在 min degree ≥ D₀ 的片内，鲁棒预算 ~ D₀/log²——若切分能保证片的 min degree = polylog 且不被 red-blue 浪费，预算可到 polylog；BM 的切分确实给 min degree > s 的片，问题是购买价）。
- **(b2) 骨架价格 / 循环依赖**：2¹¹r log¹⁰r → 次多项式，或破"先骨架后路径"的循环。
  - 最近距离：骨架尺寸的每一因子都有行号级定位（line 930）；二次耦合 (ℓ log n)² 在 Aharoni–Haxell 应用（line 417–428）的极大匹配阻塞处，属方法内生。
  - 缺的引理形态：**"边用边消耗"的同时路由-分解定理**：给定 (eps,s)-expander 与随机 V-三分，同时产出路径分解与闭环路，使闭环路全部被圈消费、剩余 o(r·polylog)。（命题 C 说明这是唯一出口：稀储备库的通用性代价与胖储备库的浪费代价必居其一，除非循环依赖被破。）或者：对"端点度 ≤ 2 且全局散布"的路径族专用的稀疏通用路由网络（Lovász 端点散布性当前未被利用）。
  - 难度：█████。注意即使 (b1) 完全解决，(b2) 不动则 f 仍 polylog、仍 log*——**两墙必须同破**。
- **参照点（已知已解决的外围）**：min degree ≥ εn：GGKO 2021（(3/2+o(1))n，最优，line 193/1060）；min degree polylog 的 expander：除 BM 的 log¹⁰-剩余外无。GGKO 的 absorption 机器从 εn 降到 polylog 无人知晓如何做。

### (c) 绕开 expansion 路线 entirely

- **已知最近距离**：无一般图上的非 expansion 管线。候选重组全部撞墙：
  - Eulerian 归约（EG ⟺ Eulerian 图 O(n) 圈分解，BM line 171–180；简报 line 17）：与 Hajós 猜想同生；本战役二部 lane 已证 3n/2 上界 ⟺ Hajós 二部特例，说明该路线的"最浅"格也未破。
  - covering（Pyber n−1，已解）→ packing 的转移：无工具（精确覆盖选择问题）。
  - 随机图/高 min degree/低 Δ：各有专线（CFS、GGKO、Δ≤4 本战役），general 图的中间密度带（平均度 polylog、Δ 大）恰是 expansion 管线的领地。
- **缺的引理形态**：任何"对中间密度带一般图直接产出 O(n) 圈+边"的机制。
- **难度评估**：█████+（无立足点）。诚实结论：60 年来所有非 expansion 尝试停留在特殊族；expansion 是唯一有完整（尽管漏水的）管线的路线。

**综合判断**：战役的正面对抗点是 (b1)+(b2) 的**中间格**——即使不指望 EG，证出"剩余 L(r) = r·2^{(log r)^θ}"（任一固定 θ<1）即得 O(n log log log n)。【**PREPUB_REVIEW R1 撤回**：原稿此处"这是 1985 年以来该问题上界的第一步非常数改进阶梯，且相变命题 A3 保证它严格优于 log*"系方向性错误——log* n = o(log log log n)，O(n log log log n) 弱于 BM 现有 O(n log* n)，不是进展阶梯；撤回该解读与衍生"中期目标"，深度计算 Θ(log log log n) 本身正确保留。见 lane_12 命题 12.2 与 MERGE_1 修正 1。】建议后续 lane 以"自鲁棒化引理的下界/上界"与"骨架循环依赖的形式化"为两个可独立推进的子问题。

---

## 六、Lean 4 陈述（供后续形式化；本机未装 Lean，仅给目标陈述）

```lean
-- 剩余平均度单步引理的抽象
def AvgDeg (G : SimpleGraph ℕ) : ℝ := 2 * G.edgeFinset.card / G.vertexFinset.card

structure OneStepDecomp (f : ℕ → ℕ) (a : ℕ) : Prop where
  step : ∀ (n d : ℕ), 2 ≤ d → d ≤ n → ∀ (G : SimpleGraph ℕ),
    G.vertexFinset.card = n → AvgDeg G = d →
    ∃ (C : Finset (SimpleGraph ℕ)) (L : SimpleGraph ℕ),
      (∀ H ∈ C, H.IsCycle) ∧ EdgeDisjoint' (G := G) C L ∧
      C.card + L.edgeFinset.card ≤ a * n ∧ AvgDeg L ≤ f d

theorem iteration_depth (f : ℕ → ℕ) (a : ℕ) (h : OneStepDecomp f a)
    (K : ℕ → ℕ) (hK : ∀ n, 2 ≤ f n → K (f n) = K n - 1) :
    ∀ (G : SimpleGraph ℕ), decomposesInto G
      (a * n * (K n + 1) + n) objects := by sorry

-- 推论 A2/A3 的目标：相变
example : ∀ θ : ℝ, 0 < θ → θ < 1 →
  (iterDepth (fun d => 2 ^ ((Real.log d) ^ θ)) = fun n => logloglog n) := by sorry
example : iterDepth (fun d => 274 ^ (Real.log d)) = fun n => logstar n := by sorry

-- 命题 B：归约
theorem EG_of_expander_case (eps₀ : ℝ) (hε : 0 < eps₀) (c : ℕ)
    (h : ∀ (H : SimpleGraph ℕ), IsSublinearExpander H (min eps₀ (2⁻⁵)) 0 →
      ∃ decomp, decomp.card ≤ c * H.vertexFinset.card) :
    ∀ (G : SimpleGraph ℕ) [Fintype G.vertexFinset],
    ∃ decomp, decomp.card ≤ 2 * c * G.vertexFinset.card := by sorry
```

（`IsSublinearExpander H eps s`：∀ U F, 1 ≤ |U| ≤ 2n/3 → |F| ≤ s|U| → |N_{G−F}(U)| ≥ eps|U|/(log n)²。）

---

## 七、自我反例攻击记录

1. **命题 A 边界**：f 在 d < 2 无定义/取 0——已用 K(n) 的 min 定义吸收；f 非单调时 K 仍良定（取 min 迭代数），推论 A1 对单调塔成立，非单调 f 无 BM 实例，不影响。
2. **命题 B**：切分片可含 <4 顶点平凡片——空/单边 expander 分解平凡，计入 O(Σ|G_i|) ✓。eps₀ > 2⁻⁵ 时取 min ✓（扩张定义随 eps 单调）。
3. **骨架困境（命题 C）**：我曾构过"k=4 切分、储备库即切片、零剩余"的假突破——检查发现未消费储备库边 ~|E|/3 全部漏账（f(d) ≈ d/3，迭代无进展），已作为"胖储备库支"写进命题 C。这正是 BM 必须造**稀**骨架的原因（对照 line 274–283 的设计叙述）。
4. **274 可否靠收紧常数击穿**：否——谱系表第 4 列逐项核算，各级 slack ≤ 3 个 log-幂；且切分引理对比值不敏感（2.1），说明多项式指数本身是自由参数，log* 才是不变量。
5. **编号风险**：定理编号为计数器推算，未经编译；结论不依赖编号，全部结论锚定 label+行号。

## 八、遗留与建议

1. [GAP→任务] 把命题 C 的远对匹配 GAP 补成定理或找到反例："(eps,0)-expander 中存在 Ω(n) 条端点相异、距离 ≥ c·log r/log D 的顶点对匹配"——若真，则 BM 架构内 polylog 剩余是**无条件**下界，路径 (b2) 可正式关闭，火力集中 (b1)。
2. [GAP→任务] 鲁棒化价格的第一个非平凡结果：常数 s（如 s=2）的自鲁棒化，删除 O(r·polyloglog r)？哪怕 s = log^{o(1)}r 也把 274 → 273·o(1)+骨架，首次把 f 推到相变线附近需要的是**次多项式**而非更小常数指数——见相变命题 A3，任何固定指数改进都不改 log*。
3. [文献] 2022 后无新上界（简报确认）；GGKO absorption 机制能否 min-degree polylog 化，值得一条独立 lane 评估（本 lane 未做，防污染未读其他产出）。
4. 本 lane 三个命题（A/A3、B、C）均已按"陈述→证明"给出，可直接进入审查。

## 文件与出处

- BM 源码：`/Users/munich/Desktop/数学/front184/2211.07689_src/main.tex`（gzip 单文件解出；原始包留存于同目录 `paper.tgz`）
- 简报：`/Users/munich/Desktop/数学/front184/campaign/CAMPAIGN.md`
- 引用核对状态：BM 内部引用（Aharoni–Haxell 2000、Lovász 1968、Krivelevich 2019、Tomon 2022、GGKO 2021、CFS 2014、KSS）均以论文引文形式采信，未逐一下载核查 [UNVERIFIED-间接]；行号级内容为本次直接精读所得。
