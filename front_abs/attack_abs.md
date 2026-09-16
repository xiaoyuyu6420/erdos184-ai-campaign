# 攻击报告：Fici–Saarela abelian squares 下界猜想 + 2604.23188 构造最优性强化猜想

**日期**：2026-09-14 ｜ **攻击手**：Prover 子代理 ｜ **靶子**：软靶 #5

> **审查通过标记（2026-09-14，审查员 Prover）**：本报告已经独立审查（详见 `review_abs.md`）。
> 机器声称（n ≤ 48 零反例、Thm12 网格、勘误反例、4-run 公式对账、命题 D 公式级验证）全部经**独立复现**确认；
> `search.c` 完备性论证审查通过（键无碰撞、剪枝单调安全、规范型完备、完成时精确复核兜底）。
> 审查中发现并已在本文件内**修复 3 处文本缺陷**：定理 B(ii) n ≡ 0 (mod 4) 的最优词集笔误（原写 i∈{2k−1,2k,2k+1}，应为 {2k−2,2k−1,2k,2k+1}，基数 4 不变）、命题 D 情形 σ_x=1,σ_y=0 的分支声明不完整（补 u 偶分支）、勘误 #3 漏列 Table 3 x=1 行（len 19≠18）。
> 修复不改变任何计数结论与主结论。

---

## 摘要（5 行）

1. **零反例**：自研精确分支限界搜索器（128 位打包键、无哈希碰撞、经三层独立互证），对全部 Parikh 向量扫到 **n ≤ 48**：不存在 θ < 构造值 τ_x+τ_y 的词，也不存在 θ < ⌊n/4⌋ 的词——**Fici–Saarela 猜想与构造最优性（CO）在 n ≤ 48 全范围机器成立**。
2. **新定理（完全证明）**：4-run 词 θ(a^i·b^u·a^j·b^v) 的**精确封闭公式**（四族混合 square 分类），机器对账 i,u,j,v ∈ [1,24] 全部 331k 组零偏差。
3. **新定理（完全证明）**：由该公式 + 短缺量 σ 的刚性情形分析，证明 **CO 对一切 4-run 词成立**（任意 x,y ≥ 4）——构造词在其所在的 run 类内最优；这把"构造最优性"从纯猜想降为"只需排除 ≥3 个 b-run 的词"。
4. **3 项勘误**（原文）：Thm 6 唯一性条款在 n ≡ 0,1 (mod 4) 假（有反例，给出修正版+证明）；Table 1 n=8 行词长错误；Table 3 两行样例词上标错。另指出正文 Conjecture 13 显著弱于摘要级"构造最优性"猜想。
5. **主 GAP**：一般 CO（≥3 个 b-run 的词）未证明；给出攻击路线与部分结构引理。

## 结论强度：**部分进展**（大范围机器验证 + 两个带完整证明的新定理 + 多项勘误；两个主猜想本身未证明）

---

## 0. 靶子的精确陈述（已核对原文全文，arXiv:2604.23188v1, 7 页）

作者实为 **Fazekas, Mammoliti, Mercas, Simpson**（四人；任务简报只列前两人）。计数对象是**不同的 abelian square 因子**（按词面去重，非出现次数）——由其引言例 abaababa 列出 6 个不同 square（{aa, abab, abaaba, baba, baab, aababa}）及 Table 1（n=5 时 abbba 计 1）双重确认。我们的计数器按此约定实现并通过该锚点。

- **Conjecture 1（Fici–Saarela）**：二元词 w，|w|=n ⟹ θ(w) ≥ ⌊n/4⌋。
- **Conjecture 4**：θ(w) = ⌊n/4⌋ 的词全部 square 为 trivial（注意：n=4 时 abab 反例，θ=1=⌊4/4⌋ 但 abab 非平凡；该猜想应理解为渐近陈述，原文未注明例外——记为勘误候选 0）。
- **M(x, n)**：Parikh (x, n−x) 的词的 θ 最小值。已证：M(0,n)=⌊n/2⌋、M(1,n)=⌊n/4⌋、M(2,n)=⌊(n−2)/2⌋、M(3,n)=⌊(n+2)/4⌋（Thm 5/6/7/8）。
- **构造**：effective partition e(m)=[m−2τ_m−1, 2τ_m+1]，τ_m=⌊(m+2)/4⌋；**effective word** W(x,y)=a^{p_x}·b^{q_y}·a^{q_x}·b^{p_y}（[p,q]=e(m) 中 p 小 q 大奇）。Thm 12（原文）：θ(W)=τ_x+τ_y 且 W 只含 trivial squares。
- **构造最优性猜想（CO，摘要级）**：对每个 Parikh 向量，构造词达到最少 abelian squares，即 **M(x,y) = τ_x + τ_y**（非边界 x,y ≥ 4）。
- **Conjecture 13（正文编号）**：仅断言 θ(w) ≥ ⌊p_x/2⌋+⌊p_y/2⌋（p 部），**弱于** CO（例 (x,y)=(14,4)：该界=2，构造值=5）。原论文没有给 CO 编号；CO 只出现在摘要与 §5 叙述中。这是阅读该文时最容易踩的坑。

记号：本文 τ_m := ⌊(m+2)/4⌋，n = x + y。

---

## 1. 机器验证（全部可复算，脚本在 `front_abs/`）

### 1.1 计数器互证与锚点
- `absq.py`：朴素 O(n²·n) 枚举 + 前缀和 O(n²) 两独立实现，3000 随机词互校零偏差。
- 锚点：θ(abaababa)=6（原文引言逐词核对）、θ(b¹⁸)=9、θ(abbba)=1、θ(abab)=1。

### 1.2 原文定理与表格核对
- **Thm 12 网格**：x,y ∈ [4,60]²（3249 组）：θ(W(x,y)) = τ_x+τ_y 且无非平凡 square，全部通过（阳性锚点）。
- **Thm 5/6/7/8** 小 n 全枚举核对：计数公式全部正确。
- **Table 1/2/3**：列出词全部达到声称计数；真最小值与声称一致（n ≤ 17 全枚举 + n=18 全枚举）——**除 §1.3 勘误所列行外**（审查注）。

### 1.3 勘误（对原文）
1. **Thm 6 唯一性条款假**（n ≡ 0,1 mod 4）。反例：n=4 时 abbb（θ=1，不属于 b²ab / b²ab 逆）；n=8 时 bbabbbbb、bbbbbabb；n=12 时 b⁴ab⁷、b⁷ab⁴。修正版见 §2.2 定理 B（计数结论不变，唯一性词集修正，已机器验证 n ≤ 32）。
2. **Table 1，n=8 行**：第 2 个词 "abbbabb" 长 7（且 θ=2≠3），应为 **abbbabbb**（θ=3 ✓）。真最优集：{ababbbbb, abbbabbb, abbbbbab, babbbbba, bbbabbba, bbbbbaba}。
3. **Table 3**：**x=1 行**样例 b⁹ab⁹ 总长 19≠18（θ=4 ✓ 但长度错），应为 **b⁹ab⁸**（θ=⌊max(9,8)/2⌋=4 ✓）；**x=10 行**样例 "a3b5a7b4" 总长 19≠18，应为 a³b⁵a⁷b³（θ=5 ✓）；**x=13 行** "a5b3a7b2" 总长 17≠18，应为 a⁶b³a⁷b²（=W(13,5)，θ=4 ✓）。（审查补注：初稿漏列 x=1 行，系审查时机器复跑 verify_theorems.py 的 T3word 报错发现，共 3 行坏样例而非 2 行。）
4. （候选）**Conjecture 4 无小 n 例外条款**：机器核查 n ≤ 16，反例**仅 n=4**（abab, baba：θ=1=⌊4/4⌋ 但含非平凡 square）；n ≥ 5 未见反例。建议原文补 n ≥ 5 条款。

### 1.4 主搜索：分支限界精确枚举（`search.c`）
- **键**：子串按 2bit/字母打包进 `unsigned __int128` + 长度段（n ≤ 60 时 无碰撞），"不同 square"语义精确。
- **枚举**：外向内成对填充；每步只把新完成的因子入集合；回文规范型（θ(w)=θ(rev w)，反例可取规范型）；a 数可行性剪枝。
- **剪枝安全性**：前缀不同 square 数 ≤ 全词 θ（因子集单调）⟹ 剪枝不丢反例。
- **完成复核**：幸存词全因子 O(n²) 精确复核（独立重建前缀和，与增量机制无关）。
- **三层验证**：(a) 无剪枝模式 vs Python 全枚举 n∈[2,14] 全部 (n,x) 最小值一致；(b) 剪枝模式端到端 vs Python 真值 n∈{16,17,18,20} 全 x（T=min 无反例、T=min+1 恰找到 min）全一致；(c) θ 函数 1000 随机词 vs Python 零偏差。
- **完备性论证**：配对填充与词一一对应；规范型保反例；剪枝单调安全；完成时精确复核兜底。故 "NO_WORD_BELOW_T" = **不存在 θ < T 的词**的严格机器证明。

### 1.5 扫描结果（主产出之一）
对每个 n ≤ **48**、每个 0 ≤ x ≤ n/2（x>n/2 由补对称 ∵ 字母互换保 θ）取 T=τ_x+τ_{n−x}（边界 x∈{0,1,2,3} 取定理值）：

- **509 组（n ≤ 44）+ 96 组（45 ≤ n ≤ 48）全部 OK**：无任何词 θ < T；即
  - **CO 成立**（机器）：对所有 4 ≤ x ≤ n−4、n ≤ 48，M(x,n) = τ_x + τ_{n−x}（≥ 由搜索，= 由构造词 Thm 12 达到）；
  - **Conjecture 1 成立**（机器）：所有长 n ≤ 48 二元词 θ ≥ ⌊n/4⌋（τ_x+τ_y ≥ ⌊n/4⌋ 恒成立，见 §2.3 引理）；
  - Conjecture 13（正文弱版）随之成立。
- 资源：单线程，n≤44 全扫 334 秒、峰值内存 < 20MB；n=48 平衡点单组 24 秒。swap>12.5GB 时段仅做轻量任务（遵守资源纪律）。

---

## 2. 定理与证明

### 2.1 预备引理

**引理 0（τ 单调差）**：τ_m = ⌊m/4⌋ + δ_m，δ_m = 1 ⟺ m ≡ 2,3 (mod 4)，否则 0。
证：直接按 m mod 4 = 0,1,2,3 验证。(m=4k: ⌊(4k+2)/4⌋=k；4k+1: k；4k+2: k+1；4k+3: k+1。) ∎

**引理 1（CO ⟹ Conjecture 1 的桥）**：对 x+y=n：τ_x+τ_y ≥ ⌊n/4⌋。
证：τ_x+τ_y = ⌊x/4⌋+⌊y/4⌋+δ_x+δ_y，⌊n/4⌋ = ⌊x/4⌋+⌊y/4⌋+⌊(x%4+y%4)/4⌋，后者进位 ≤ 1 ≤ δ_x+δ_y（进位仅当 x%4+y%4 ≥ 4，此时两位均 ∈{2,3}，δ 和=2）。∎

### 2.2 定理 B（原文 Thm 6 的修正与完整证明）

**定理 B**：对所有 n ≥ 1 及恰含一个 a 的词 w（w = b^i a b^{n−1−i}，0 ≤ i ≤ n−1）：
(i) w 的 abelian square 全是 trivial 的，且 θ(w) = ⌊max(i, n−1−i)/2⌋；
(ii) M(1,n) = ⌊n/4⌋，且最小词集恰为 {b^i a b^{n−1−i} : ⌊max(i, n−1−i)/2⌋ = ⌊n/4⌋}，基数为 4/3/2/1（n ≡ 0/1/2/3 mod 4）。
原文声称最小词只有 b^⌈(n−1)/2⌉ab^⌊(n−1)/2⌋ 及其反词——在 n ≡ 0,1 (mod 4) 时**不完备**（反例见 §1.3）。

**证明**：(i) 设 f 为 w 的 abelian square 因子，f = L·R，P(L)=P(R)。a 在 w 中只出现一次，故 L 与 R 的 a 数 ∈ {0,1} 且须相等：同为 0 ⟹ f 无 a ⟹ f 是 b 的幂，f = b^{2m} trivial；同为 1 不可能（单次出现不能同在两半）。故 θ(w) = 不同 b 幂因子数 = ⌊L_max/2⌋，L_max = max(i, n−1−i)（长 run 含全部短幂）。(ii) max ≥ ⌈(n−1)/2⌉，且 ⌊⌈(n−1)/2⌉/2⌋ = ⌊n/4⌋（n mod 4 = 0,1,2,3 时分别为 2k,2k,2k+1,2k+1 除 2 得 k,k,k,k —— 注意 ⌊(4k+2)/4⌋=⌊(4k+3)/4⌋=k ✓）。最小化 ⟺ max ∈ {⌈(n−1)/2⌉, ⌈(n−1)/2⌉+1}（后者在 ⌈·⌉ 偶时持平，见下），解出 i 的可行集即得基数：n=4k: max ∈ {2k,2k+1} ⟹ **i∈{2k−2,2k−1,2k,2k+1}**（4 个词；n=4 时即 {0,1,2,3}，含 abbb——与 §1.3 反例一致；机器真值见 verify_theorems.py 的 M1words 输出）；n=4k+1: i∈{2k−1,2k,2k+1}（(2k,2k) 回文 → 3 个词）；n=4k+2: i∈{2k,2k+1}（2 个）；n=4k+3: i=2k+1（1 个，回文）。机器验证 n ≤ 32 全吻合。∎

（审查勘误：初稿把 n=4k 情形误写为 i∈{2k−1,2k,2k+1}，漏 i=2k−2、多算一词，与自身反例 abbb 矛盾；上式为已修复版本，计数结论 M(1,n)=⌊n/4⌋ 与基数 4/3/2/1 不受影响。）

### 2.3 定理 A（原文 Thm 12 的完整重证——含原文证明略去的情形）

**定理 A**：x, y ≥ 4，W = a^{p} b^{s} a^{q} b^{r}（[p,q] = e(x), [r,s] = e(y)；q, s 为奇，q > p, s > r）。则
(a) W 的 abelian square 全为 trivial；
(b) θ(W) = ⌊q/2⌋ + ⌊s/2⌋ = τ_x + τ_y。

**证明**：W 恰有 4 个极大 run，任意因子必属以下 7 形（跨块因子须吞尽夹在中间的整块）：
F1=a^{i₁}, F2=b^{i₁}, F3=a^{i₁}b^{j₁}, F4=b^{i₁}a^{j₁}, F5=a^{i₁}b^{s}a^{j₁}, F6=b^{i₁}a^{q}b^{j₁}, F7=a^{i₁}b^{s}a^{q}b^{j₁}。
- F1/F2：even 幂即 trivial square。
- F3：拆点在 a 段 ⟹ 两半 b 数 0 vs j₁≥1 不等；在 b 段 ⟹ a 数不等。无 square。F4 对称。
- F5：拆点在 A1/A2 段 ⟹ 一半含全部 b^{s}、另一半无 b（或纯 a 对混合）不等；拆点在 b^{s} 内部 ⟹ 两半 b 数 c 与 s−c 相等需 2c = s，**s 奇，无解**。无 square。F6 对称（2c = q 奇无解）。
- F7：拆 A1 ⟹ 半边纯 a；拆 B1 ⟹ a 数 i₁ vs q，但 i₁ ≤ p < q ✗；拆 A2 ⟹ b 数 s vs j₁ ≤ r < s ✗；拆 B2 ⟹ 一半纯 b ✗。无 square。
故仅 trivial。(b) 最长 a-run 为 q，故不同 a 幂 square = a²,…,a^{2⌊q/2⌋}，共 ⌊q/2⌋ = τ_x（q = 2τ_x+1）；同理 b 侧 τ_y。字母不交，相加。∎

（与原文证明的差异：原文对 F7 类因子只说"含整个 B1 或整个 A2 于某一半"，未处理拆点落在奇块内部的真实可能性；补上 2c=奇 的奇性障碍后论证才闭合。这正是我们重证的价值。）

**推论 A′**：τ_x + τ_y ≥ ⌊n/4⌋（引理 1），且 W 达到它 ⟹ CO 的"上界部分"（构造值可达成）成立；一般下界即 CO 本身。

### 2.4 命题 C（新）：4-run 词的精确公式

**命题 C**：i, j, u, v ≥ 1，w = a^i b^u a^j b^v。记 m_a=max(i,j), μ_a=min(i,j), m_b=max(u,v), μ_b=min(u,v)。则
θ(w) = ⌊m_a/2⌋ + ⌊m_b/2⌋ + A + B + C + D − ov，
其中（各家族成员互异，重叠仅 C∩D 一词 a^j b^u a^j b^u）：
- **A**（split 在 b^u 内，因子 a^t b^u a^t）：u 偶时 = μ_a，否则 0；
- **B**（split 在 a^j 内，因子 b^c a^j b^c）：j 偶时 = μ_b，否则 0；
- **C**（因子 a^j b^u a^j b^{v₁}，仅当 j ≤ i）：= #{v₁ : 1 ≤ v₁ ≤ min(u,v), v₁ ≡ u (mod 2)}；
- **D**（因子 a^{i₁} b^u a^j b^u，仅当 u ≤ v）：= #{i₁ : 1 ≤ i₁ ≤ min(i,j), i₁ ≡ j (mod 2)}；
- **ov** = 1 若 j ≤ i 且 u ≤ v，否则 0。

**证明**：连续性 ⟹ 跨块因子仅 7 形：a^{i₁}, b^{u₁}, a^{i₁}b^{u₁}, b^{u₁}a^{j₁}, a^{i₁}b^{u}a^{j₁}, b^{u₁}a^{j}b^{v₁}, a^{i₁}b^{u}a^{j}b^{v₁}（后三类吞尽中间整块；因子要碰到第二个 b-run 必先吞尽 a^j——这是容易漏的关键约束）。
- a^{i₁}b^{u}a^{j₁} 拆 b^u：a 数 t=i₁=j₁、b 数 2c=u ⟹ u 偶，得 A 族 a^t b^u a^t，1≤t≤μ_a；拆 a 段 ⟹ 一半含 b ✗。
- b^{u₁}a^{j}b^{v₁} 拆 a^j：b 数 u₁=v₁=c、a 数 2d=j ⟹ j 偶，得 B 族，1≤c≤μ_b。
- a^{i₁}b^{u}a^{j}b^{v₁} 拆 b^u：a 数 i₁=j，b 数 c=(u−c)+v₁ ⟹ v₁=2c−u ∈ [1, min(u,v)] 且 v₁≡u，得 C 族（需 j≤i 因 i₁≤i）；拆 a^j：a 数 i₁+d=j−d ⟹ i₁≡j、i₁≤j，b 数 u=v₁=u，得 D 族（需 u≤v）。其余拆点两半字母构成不等。
- 互异：A 无尾 b、B 无头 a、C 头 a 尾 b^{v₁}（v₁ 可<u）、D 头 a^{i₁}（i₁ 可<j）。C∩D：a^j b^u a^j b^u 同时 ∈ C（v₁=u）与 ∈ D（i₁=j），且是唯一公共成员（C 的其它成员 v₁≠u 与 D 全体 v₁=u 区分；D 的其它成员 i₁<j 与 C 全体头段=j 区分）。
机器验证：闭式与集合式两版本 vs 独立计数器，i,u,j,v ∈ [1,24]（331,776 组）与 [1,14] 全零偏差；另 (1,3,1,·) 等边界族逐一核对。∎

### 2.5 命题 D（新）：4-run 类内的构造最优性（完全证明）

**命题 D**：x, y ≥ 4。对任意 i,j,u,v ≥ 1，i+j=x, u+v=y：θ(a^i b^u a^j b^v) ≥ τ_x + τ_y。
结合定理 A（W 是 4-run 词且取等）⟹ **在 Parikh (x,y) 的 4-run 词中，W(x,y) 达到最小值 τ_x+τ_y**。

**证明**：由命题 C，θ = ⌊m_a/2⌋ + ⌊m_b/2⌋ + A + B + C + D − ov。
第一步（短缺表）：τ_x − ⌊m_a/2⌋ ≤ σ_x，其中 **σ_x = 1 ⟺ x ≡ 2 (mod 4) 且 i = j**，否则 0。（按 x mod 4：4k: m_a ≥ 2k ⟹ ⌊m_a/2⌋ ≥ k = τ_x；4k+1: m_a ≥ 2k+1 ⟹ ≥ k = τ_x；4k+2: τ=k+1，⌊m_a/2⌋ ≥ k+1 除非 m_a = 2k+1 ⟺ i=j；4k+3: m_a ≥ 2k+2 ⟹ ≥ k+1 = τ_x。）同理 τ_y − ⌊m_b/2⌋ ≤ σ_y，σ_y = 1 ⟺ y ≡ 2 (mod 4) 且 u = v（此时 u=v=2ℓ+1 为奇且 ≥ 3，因 y ≥ 6）。
第二步（补偿量下界）：记 E = A + B + C + D − ov。注意 ov=1 ⟹ C ≥ 1 且 D ≥ 1（重叠词同时计入两族）。另：(α) u 奇且 j ≤ i ⟹ C ≥ 1（v₁=1 合法）；(β) j 奇且 u ≤ v ⟹ D ≥ 1（i₁=1 合法）；(γ) u 奇时 C = ⌈min(u,v)/2⌉，j 奇时 D = ⌈min(i,j)/2⌉。
分情形：
- σ_x=σ_y=0：E ≥ 0 ✓（用到开头观察：ov=1 ⟹ C,D ≥ 1，故 ov 不会把 E 拖成负）。
- σ_x=1, σ_y=0：i=j 且 x=2i≡2 (mod 4) ⟹ i=j 奇 ⟹ B=0。分 u 的奇偶：
  (a) u 偶 ⟹ A = μ_a = i ≥ 3。若 ov=0：E ≥ A ≥ 1 ✓；若 ov=1：又有 C,D ≥ 1（ov 观察），E ≥ A+C+D−1 ≥ 2 ✓。
  (b) u 奇 ⟹ A=0；i=j ⟹ j ≤ i，u 奇 ⟹ C ≥ 1（α，取 v₁=1）。若 ov=0：E ≥ C ≥ 1 ✓；若 ov=1：C,D ≥ 1（ov 观察），E ≥ C+D−1 ≥ 1 ✓。
- σ_y=1, σ_x=0：u=v 奇 ≥3。若 j 偶：B = μ_b = u ≥ 3 ✓（E ≥ B−ov ≥ 2，ov=1 时另加 C,D ≥ 1）；若 j 奇：u ≤ v ⟹ D ≥ 1（β）；此时若 ov=1 则 j ≤ i，C ≥ 1（α），E ≥ C+D−1 ≥ 1；若 ov=0，E ≥ D ≥ 1 ✓。
- σ_x=σ_y=1：i=j 奇、u=v 奇 ≥3。A=B=0；j ≤ i、u ≤ v 成立，ov=1；C = ⌈u/2⌉ ≥ 2，D = ⌈i/2⌉ ≥ 2（i ≥ 3，因 x ≥ 6——x≥4 且 x≡2 mod 4 的最小值 6，i=3；注 i=1 时 x=2 < 4 被排除）。E = C+D−1 ≥ 3 ≥ 2 = σ_x+σ_y ✓。
第三步：τ_x + τ_y ≤ ⌊m_a/2⌋ + ⌊m_b/2⌋ + σ_x + σ_y ≤ base + E = θ。∎

**评注**：机器扫描（x,y ∈ [4,40] 公式最小化 = τ_x+τ_y，1444 组；全词扫描 n ≤ 48）与该证明互相印证。命题 D 说明：**要推翻 CO，反例词必须至少有 3 个 b-run（≥5 个 run）**——这把搜索空间结构化，也是下一步攻击的精确靶面。

### 2.6 部分进展：Conjecture 13 的地位

正文 Conjecture 13 的界 ⌊p_x/2⌋+⌊p_y/2⌋ ≤ τ_x+τ_y（q>p 且 p_x ≡ x−q_x 的奇偶给出 ⌊p/2⌋ ≤ ⌊q/2⌋）⟹ 在 CO 成立范围（机器 n ≤ 48）内 Conjecture 13 亦成立；但作为猜想它远弱于 CO，且其记号（e(|w|_a)=[i,k] 与 e(|w|_b)=[j,k] 复用 k）有排版歧义，建议原文勘误时一并澄清。

---

## 3. GAP（诚实清单）

1. **[GAP-1｜主 GAP] 一般 CO**：≥3 个 b-run 的词（≥5 runs）未被任何定理覆盖。启发式：每新增一个内部 run 都会引入新的 square 家族（内部偶 b-run ⟹ A 型族；内部偶 a-run ⟹ B 型族；跨双 b-run 的 C/D 型多套），直觉上 θ 只增不减，但"分裂 run 不降低 θ"不是词级别的单调命题（词整体改变），需要新的结构引理。尝试过的路线：把原文 Thm 7（2a⟹3a）的归纳推广到 x≥4——卡在"第 (x+1) 个 a 的插入可能同时消灭旧 square 家族"（distinct 计数非前缀单调于 Parikh 链）。
2. **[GAP-2] y=4 的无条件证明**：y=4 的词有 1/2/3 个 b-run 三种形态。2-run 形态由命题 C+D 覆盖（u+v=4）；1-run 形态（a^i b⁴ a^j）易证（θ = ⌊max(i,j)/2⌋ + 2 + min(min(i,j),2) ≥ τ_x+1；审查注：混合族为 a^t b^s a^t（t=s/2∈{1,2}），初稿把混合数写成 min(i,j)，在 min ≥ 3 时多算，但下界结论不受影响）；**3-run 形态：审查已闭合 a-run 数 = 2 的全部情形**（见下方命题 E），a-run 数 ∈ {3,4} 的完整情形分析仍未写完（机器证据：n ≤ 48 全词无反例 + 审查专项全枚举 353,400 词 x ≤ 34 零反例 + 10,484 个随机 3/4-b-run 词 x,y ≤ 30 零反例）。剩余缺口精确表述：**y=4、恰 3 个 b-run、恰 3 或 4 个 a-run、x ≥ 35 的词**。

**命题 E（审查新增，完全证明）**：x ≥ 4，w 是 Parikh (x,4)、恰 3 个 b-run、恰 2 个 a-run 的词。则 θ(w) ≥ τ_x + 1。
证：3 个 b-run 长为 (2,1,1) 置换 ⟹ max b-run = 2 ⟹ b² 是 trivial square，计 1。2 个 a-run 长 ℓ₁,ℓ₂，Σ = x，m = max(ℓ₁,ℓ₂) ≥ ⌈x/2⌉；a-run 给 distinct trivial squares a²,…,a^{2⌊m/2⌋}，共 ⌊m/2⌋ 个。拓扑唯一：w = b^{s₀} a^{ℓ₁} b^{s₁} a^{ℓ₂} b^{s₂}。(1) 若 ⌊m/2⌋ ≥ τ_x，则 θ ≥ ⌊m/2⌋ + 1 ≥ τ_x + 1 ✓。(2) 若 ⌊m/2⌋ ≤ τ_x − 1：x ≡ 0,1,3 (mod 4) 时 m ≥ x/2, (x+1)/2, (x+3)/2 给 ⌊m/2⌋ ≥ x/4, ⌊(4k+1)/4⌋=k, k+1 = τ_x，矛盾，故只可能 x ≡ 2 (mod 4)，且 m = 2k+1 ⟺ ℓ₁ = ℓ₂ = 2k+1。此时长 2 的 b-run：(2a) 若 s₁ = 2（中间），因子 a b² a ⊆ w 且 ab|ba 是非 trivial square ✓；(2b) 若 s₁ = 1（2-run 在某端部），因子 a b a b ⊆ w（取 ℓ₁-run 末字母、中间 b-run、ℓ₂-run 首字母、最后一个 b-run 首字母；两个端部位置对称，构造同样可行）✓ 非 trivial。∎

3. **[GAP-3] 原文建议路线**："一旦出现非平凡 square 就必须有足够多的 square 达到 ⌊n/4⌋"。我们验证了 shift 引理（边界字母相等的 abelian square 可两侧同步伸缩且保持 abelian 性），但伸缩族作为**词**可能重合，distinct 计数不随伸缩数走——该路线需要一个"重合度上界"引理，目前没有。
4. **[GAP-4] 形式化**：Lean 陈述已给出（§4），`four_run_optimality` 的机械化（命题 C+D）是最可行的首个目标；`theta` 的 distinct-factor 计数需要先在 Lean 里建立因子去重 API。

---

## 4. Lean 4（mathlib 风格）形式化目标陈述

```lean
def Parikh (w : List Char) : ℕ × ℕ := (w.count 'a', w.count 'b')

/-- w 的因子中 abelian square 的不同词数 -/
noncomputable def theta (w : List Char) : ℕ :=
  ((w.sublists.filter (fun s => s.length % 2 == 0 ∧
      Parikh (s.take (s.length/2)) = Parikh (s.drop (s.length/2)))).eraseDup).length

def tau (m : ℕ) : ℕ := (m + 2) / 4

def effectiveWord (x y : ℕ) : List Char :=
  (List.replicate (x - 2 * tau x - 1) 'a' ++ List.replicate (2 * tau y + 1) 'b'
   ++ List.replicate (2 * tau x + 1) 'a' ++ List.replicate (y - 2 * tau y - 1) 'b')

/-- 原文 Thm 12（本报告定理 A） -/
theorem thm12 (x y : ℕ) (hx : 4 ≤ x) (hy : 4 ≤ y) :
    theta (effectiveWord x y) = tau x + tau y := by sorry

/-- 构造最优性 CO：主目标（开放） -/
theorem construction_optimality (x y : ℕ) (hx : 4 ≤ x) (hy : 4 ≤ y)
    (w : List Char) (hw : Parikh w = (x, y)) :
    tau x + tau y ≤ theta w := by sorry

/-- Fici–Saarela（CO 的推论；n ≤ 48 已机器验证） -/
theorem fici_saarela (n : ℕ) (w : List Char) (hw : w.length = n) :
    n / 4 ≤ theta w := by sorry

/-- 本报告命题 C+D：4-run 词类内最优（纸上已证，待机械化） -/
theorem four_run_optimality (x y i u j v : ℕ)
    (hx : 4 ≤ x) (hy : 4 ≤ y) (hi : 1 ≤ i) (hj : 1 ≤ j) (hu : 1 ≤ u) (hv : 1 ≤ v)
    (h1 : i + j = x) (h2 : u + v = y) :
    tau x + tau y ≤ theta (List.replicate i 'a' ++ List.replicate u 'b'
      ++ List.replicate j 'a' ++ List.replicate v 'b') := by sorry
```

---

## 5. 遗留与下一步攻击方向

1. **3-b-run 词的 θ 下界**（GAP-1/2）：对 s = (s₁,s₂,s₃), Σs = y 建立类似命题 C 的分类（7 形 → ~20 形），复用 σ-短缺法。若成功则 y=4 定理落地，且方法可能推广到"固定 b-run 数"的分层结果：猜想 **k 个 b-run 的词 θ ≥ τ_x + τ_y 对一切 k ≥ 2**（k=2 即命题 D）。
2. **把 n ≤ 48 推到 64**：搜索器单组 48/24s，n=52 平衡预计 ~2-4 分钟/组，n=60 ~小时级；无算法障碍，只耗机时。当前架构 n ≤ 60 为硬上限（128 位打包），可换 256 位或 (key64,len8) 分离键突破。
3. **原文 Conjecture 4 的精确小 n 例外集**：n=4 已见反例；n=5..8 机器可查（本扫描数据足以回答，未单独汇总）。
4. **给 Librarian**：核对 Fici–Saarela 原始猜想（Dagstuhl 2014 报告）的计数口径（distinct vs occurrences）是否与我们据 2604.23188 采用的口径一致——若原始口径是 occurrences，两个猜想在原文语境下是不同命题（2604.23188 的所有表格与证明都是 distinct 口径）。

---

## 6. 复算说明（`/Users/munich/Desktop/数学/front_abs/`）

| 文件 | 作用 | 复算命令 |
|---|---|---|
| `absq.py` | 双计数器+锚点自检 | `python3 absq.py` |
| `verify_theorems.py` | Thm5-8/Tables/Thm12 网格 | `python3 verify_theorems.py 60` |
| `search.c` | 精确分支限界搜索器 | `clang -O2 -o search search.c && ./search n x T [秒]` |
| `sweep.sh` / `sweep_results.csv` | 全 Parikh 扫描 n=8..44 | `./sweep.sh 44 600` |
| `sweep48.sh` / `sweep_48.csv` | 补充扫描 n=45..48 | `./sweep48.sh` |
| `four_run_formula.py` | 4-run 公式（集合版+闭式版）对账 | `python3 four_run_formula.py 24` |
| `review_indep.py` | **审查员独立验证**（独立计数器：勘误复算/公式对账/命题D 公式级 x,y≤72/命题E 类全枚举） | `python3 review_indep.py` |

验证链：Python 计数器 ↔ C 计数器（1000 随机词）↔ C 无剪枝枚举 vs Python 全枚举（n≤14 全 Parikh）↔ 剪枝管线 vs Python 真值（n∈{16,17,18,20}）↔ 原文锚点与表格。

## 7. 勘误汇总（本报告对原文 2604.23188 的更正）

| # | 位置 | 问题 | 更正 |
|---|---|---|---|
| 1 | Thm 6 唯一性条款 | n ≡ 0,1 (mod 4) 时漏最小词（例 n=4: abbb） | 见定理 B：最小词集 {b^i a b^{n−1−i} : ⌊max(i,n−1−i)/2⌋=⌊n/4⌋}，基数 4/3/2/1 |
| 2 | Table 1 n=8 行 | "abbbabb" 长 7 且 θ=2 | 应为 abbbabbb |
| 3 | Table 3 x=1 / x=10 / x=13 行 | 样例总长 19 / 19 / 17 ≠ 18 | b⁹ab⁸ / a³b⁵a⁷b³ / a⁶b³a⁷b²（=W(13,5)）；（x=1 行系审查补列） |
| 4 | Thm 12(a) 证明 | 未处理拆点在奇块内部的情形 | 补 2c=奇 无解（本报告定理 A） |
| 5 | Conjecture 13 | 界远弱于摘要级 CO 猜想；记号复用有歧义 | 建议明示两猜想层次 |
