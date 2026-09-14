# BH97 全文核查 + 竞争态势复查（Librarian，2026-09-14）

任务：① 拿到 Bertram–Horák 1997（BH97）全文或精确内容，判断其是否隐含 "L(B) 型全 YES" 刻画或与 Φ 构造等价的构造；② 竞争态势复查；③ 核对 AABC25 对 Abreu et al. 2004 的表述。

**一句话结论**：BH97 全文仍未拿到（拿到的是史无前例精度的转述级信息：Plummer 2007 综述 Theorem 6.9 逐字转述 + BH97 自己提出的 Conjecture 6.10 + 其余 8 条参考文献全文列表）；但**核查过程中发现了一个比 BH97 更直接的新颖性威胁——Kouider–Sabidussi 1995 (JCTB 63:170–184) 的摘要含 "3-正则图有完美匹配 ⟺ 其线图有 triangle-free 2-factorisation" 的等价观察，按字面即覆盖命题 6**。建议：命题 6 新颖性**降级**（引 KS95），引理 1 的困难情形也需按 KS95 转述；主定理（ce ≤ n−2 / AABC25 Problem+Conjecture 解决）新颖性不受影响。竞争态势：**无抢占风险**（AABC25 有 v2 但数学内容与 v1 相同、被引 0；未检索到任何新文献触及 6-正则 ce 或 Conjecture 6.2）。

---

## 任务 1：BH97 全文获取（结果：否，但拿到高精度替代材料）

### 1.1 逐路径尝试记录

| # | 路径 | 结果 |
|---|---|---|
| 1 | SIAM 官方页 https://epubs.siam.org/doi/10.1137/S089548019427144X （tavily-extract 全文抓取） | **成功（页面级）**：摘要、关键词、MSC、**全部 8 条参考文献**、Cited-By 列表。正文 PDF（/doi/pdf/…、/doi/epdf/…）curl 直连 HTTP=000、代理 403、tavily-extract "Failed to fetch"。 |
| 2 | Unpaywall/OpenAlex：`api.openalex.org/works/https://doi.org/10.1137/S089548019427144X` | OA status = **closed**，`pdf_url: null`，`any_repository_has_fulltext: false`。 |
| 3 | Semantic Scholar API（paperId 8118a5e80e7cd83c35429d6de01770d9aa9a4668） | `openAccessPdf.status = CLOSED`；abstract 被出版商 elide；只有 tldr。10 篇施引列表已取（逐篇核查见 1.3）。 |
| 4 | 作者主页 / 学位论文（P. Horák: Miami→UW Tacoma；E. Bertram） | **未命中**：无可见的个人 preprint/技术报告列表副本；DBLP 与站点均被 bot 保护（Anubis/Cloudflare），未能枚举 Bertram 的 1994 年条目与其学位论文。※未做：馆际互借（本会话不可用）、直接联系作者。 |
| 5 | 引用文献精确定理陈述：Plummer 综述 | **成功（关键）**：见 1.2，Theorem 6.9 + Conjecture 6.10 逐字。 |
| 6 | Hartvigsen–Li 系列（IPCO 2007 / SIAM J Optim 2011 / Math Prog 2012） | 施引存在（参考文献表确认），正文付费墙；Hartvigsen 自己的工作站 preprints 只挂了 2024 年新稿（无 BH97 提及，见 2.4）。 |
| 7 | Heinrich–Liu–Zhang 1998 (JCTB 72:197–207)，施引之一 | 正文未取到；但 scispace 摘要片段给出其转述（见 1.3）。 |
| 8 | CORE / scholar.archive.org / CiteSeerX / Wayback | 全部失败：CORE 需 API key；scholar.archive.org 反爬；CiteSeerX 已下线（只剩 Wayback 404 页）；Wayback CDX 对 SIAM/ScienceDirect 目标 URL **无任何 PDF 快照**（仅 landing page 的 403 记录）。 |
| 9 | ScienceDirect / ACM DL（含作者副本、ResearchGate、academia.edu） | 全部 403/Cloudflare/captcha。ResearchGate 只泄出零碎摘要句。scispace 的 PDF 直链返回 HTTP 202 空体（拒绝下载）。 |
| 10 | zbMATH Open（免费，可能有长评审） | **命中但无增益**：Zbl 0867.05054 只有 "Summary:" 级文字，与官方摘要逐字相同，无独立评审内容。 |

### 1.2 已有原文/转述（引用原文）

**(a) 官方摘要（三源一致，本次第四源确认）** —— SIAM 页 https://epubs.siam.org/doi/10.1137/S089548019427144X 与 ACM DL https://dl.acm.org/doi/10.5555/252265.252294 与 zbMATH Zbl 0867.05054：

> "There is a polynomial algorithm which finds a decomposition of any given 4-regular graph into two triangle-free 2-factors or shows that such a decomposition does not exist."

SIAM 关键词：decomposition, triangle-free, 2-factor, polynomial algorithm；MSC 05C70 / 05C85 / 68R10。

**(b) Plummer 综述（2007）逐字转述【本次最重要原文级收获】** —— M. D. Plummer, *Graph factors and factorization: 1985–2003: A survey*, Discrete Math. 307 (2007) 791–821，第 812 页 §6（PDF 镜像已下载：http://ftp.eecs.umich.edu/~pettie/matching/Plummer-f-factor-survey.pdf ，31 页）：

> "Theorem 6.9 (Bertram and Horák [33]). There is a polynomial algorithm which finds a factorization of any given 4-regular graph into two triangle-free 2-factors or else shows that such a factorization does not exist."

紧接着：

> "On the other hand, the same two authors pose the following:
> **Conjecture 6.10.** The problems of (a) recognizing which 2n-regular graphs decompose into two triangle-free n-factors, and (b) recognizing which 2n-regular graphs decompose into n triangle-free 2-factors are both NP-complete for all n ⩾ 3."

**这两条联合起来回答编排者的核心问题**：BH97 是**纯判定算法**，没有给出 YES 实例的刻画；而且作者自己把 "2n-正则（n≥3）能否分解为 n 个无三角形 2-因子" 作为**猜想 NP-完全**登记——一个已掌握 YES/NO 刻画的工作不会这样写。故 "BH97 隐含 L(B) 全 YES 刻画" 的担心**没有证据支持**。

**(c) BH97 全部参考文献（SIAM 页）**：Cornuéjols 1988 (General factors)；Dolinski–Tarsi 1992 (H-decomposition is NPC)；Edmonds–Johnson 1970；Cornuéjols–Hartvigsen 1986 (An extension of matching theory)；Hell–Kirkpatrick–Kratochvíl–Kříž 1988 (On restricted two-factors)；**Kouider–Sabidussi 1995 (JCTB 63:170–184)**；Lovász–Plummer, Matching Theory；Tutte 1952。
→ 技术路线 = 匹配/一般因子（Edmonds–Johnson、Cornuéjols–Hartvigsen、Cornuéjols）+ restricted 2-factor 复杂度框架（Hell et al.）；**KS95 是其直接前置**。

**(d) 正文片段（低可靠度，搜索引擎缓存的付费 PDF 预览）**：tavily 结果曾显示 SIAM PDF 首页开头为 "Introduction. A 2-factor of a graph G is a subgraph F of G such that any vertex of G is of degree 2 in F. Hell et al. [5] proved that given a set L of …"（与引言以 Hell et al. 的受限 2-因子为背景一致；仅作旁证，无法复核）。

### 1.3 BH97 的 10 篇施引逐一核查（无一篇转述其定理细节）

OpenAlex 9 篇 / S2 10 篇（去重）：Plummer 2007 综述（**唯一给出精确定理转述者**）；Plummer 2013 *Factors and Factorization*（Handbook of Graph Theory 章节，未取到）；Hartvigsen–Li 2007 (IPCO) / 2011 (SIAM J. Optim. 21:1027–1045) / 2012 (Math. Prog. 138)；Babenko 2010 (even factor)；Heinrich–Liu–Zhang 1998 (JCTB 72:197–207)；Johnson–Mendell–Norris–Plantholt–Tipnis 2021 (Discrete Math. Lett. 6:32–37，OA)。
- Johnson et al. 2021（OA 全文已读）只写："Bertram and Horak showed that the problem of determining whether a 4-regular graph can be decomposed into two triangle-free 2-regular graphs can be solved in polynomial time." 无判据细节。
- HLZ 1998 的 scispace 摘要片段（只能读到一句）："gave sufficient conditions for decomposing 4-regular graphs into triangle-free 2-factors. In this paper, the main result (Theorem 4.1) characterizes all …"（归属对象被截断，不能确定指 BH97 还是 KS95；标注为**未定**）。
- 结论：**没有任何施引文献给出 BH97 的 YES/NO 判据或算法内部构造**。

### 1.4 对编排者四个子问题（a）–（d）的答复

- (a) 算法输入输出：输入任意 4-正则图，输出两个无三角形 2-因子的分解，或判定不存在（1.2(a)(b)，原文级）。
- (b) YES/NO 判据：**未见于任何可达来源**；BH97 自己把高次情形登记为猜想 NP-完全（1.2(b)），说明其 4-正则算法是特例性判定程序而非结构性刻画。**也没拿到算法细节（多项式归约到哪个匹配问题）**。
- (c) 是否讨论 L(B)/line graph 类：**无法确认**（全文未取到）。但间接证据强：BH97 引用 KS95 [6]，而 KS95 的核心观察正是 line graph 版本（见 2.1）。
- (d) 是否含与 "每条匹配边端点二选一" 等价的构造：**无法确认**。**替代性风险**：KS95 的等价观察若按其摘要字面成立，则其证明必然含 "从 3-正则图的完美匹配构造线图的无三角形 2-因子分解" 的构造，与 Φ 高度可能同源（详见 2.1）。

### 1.5 建议的后续获取路径（按性价比排序）

1. **馆际互借/图书馆扫描**：SIAM J. Discrete Math. 10(2):309–317（9 页）；国内高校馆多半有 SIAM 回溯库；亦可请求 SIAM 单篇 $42（若值得）。
2. **联系作者**：P. Horák（ORCID 0000-0003-4157-8813，曾在 University of Miami，后 UW Tacoma）；同时问 KS95 的 Kouider（Paris-Sud）或 Sabidussi（Montréal）。KS95 是更关键的全文（JCTB 63:170–184，Bronze OA 但站点反爬）。
3. **MathSciNet 评审**（MR1457724 一类的评审文字常有定理逐字转述）——本次无订阅权限。
4. **HLZ 1998 全文**（JCTB 72:197–207）：其引言同时引 BH97 与 KS95，最可能给出两者的一句话精确定位；Bronze OA。
5. **Plummer 2013 Handbook 章节**与 **Yu–Liu《Graph Factors and Matching Extensions》(2009)** 的 2-因子分解节（可能重述 BH97/KS95 的定理）。

---

## 任务 1 的意外收获/真实威胁：Kouider–Sabidussi 1995（KS95）

### 2.1 摘要（两个来源 + S2 tldr，三处一致）

M. Kouider, G. Sabidussi, *Factorizations of 4-regular graphs and Petersen's theorem*, JCTB 63 (1995) 170–184, DOI 10.1006/jctb.1995.1014：

> "On the basis of the observation that **a 3-regular graph has a perfect matching if and only if its line graph has a triangle-free 2-factorisation**, we show that a connected 4-regular graph has a triangle-free 2-factorisation, provided it has no more than two cut-vertices belonging to a triangle."

来源：① ScienceDirect 落地页片段 https://www.sciencedirect.com/science/article/pii/S0095895685710143 ；② ACM DL 摘要片段 https://dl.acm.org/doi/abs/10.1006/jctb.1995.1014 ；③ S2 tldr（paperId b9e5f2c3fa0e2ea03438d1b6d24ba3125a051a74）为同句第二半。全文未取到（403/captcha；Wayback 无 PDF；S2 标注 BRONZE 但被反爬挡住）。

### 2.2 为什么这直接威胁命题 6

命题 6：B 为 **3-正则二部**简单图 ⟹ W ≅ L(B) 可分解为两个无三角形 2-因子（Φ(σ) ⊔ Φ(−σ)）。
- 3-正则二部图必有完美匹配（Hall）——这是标准事实，无需新颖性；
- KS95 的观察原文是 **iff**，其正向（"完美匹配 ⟹ 线图有无三角形 2-因子化"）对任意 3-正则图成立，**二部性甚至不是必需假设**；
- 因此 **命题 6 的存在性断言 = KS95 观察的直接特例**（Σ 二部情形）。计数推论（每因子 ≤ 1+⌊(n−4)/3⌋ 件）由无三角形性自动得到，也不是新东西。
- 我们的 Φ(σ)⊔Φ(−σ) 是否与 KS95 的构造相同：**无法确认**（KS95 全文未读），但风险应按"很可能"处理。

### 2.3 引理 1 的处境（连带影响）

引理 1 的困难情形（"每个 2-因子都是三角形因子"）被本稿证明归约为 G ≅ L(B)、B 三正则**二部**；随后用 Φ 造出无三角形 2-因子导出矛盾。
- 归约本身（"两个边不交三角形因子的并 ⟹ 线图结构"）在本轮检索中**未找到先例**，可主张为新；
- 但"在 L(B) 上造出无三角形 2-因子"这一步**可由 KS95 观察替代**，不再构成新颖性；
- 结果：引理 1 的**陈述**未见先例（未找到任何文献陈述"每个 4-正则图有含 ≥4 阶圈的 2-因子"，见 4.3），但其**证明的关键引擎**要改记为 [KS95]。

### 2.4 顺带发现的两条"最近工作"（供 §7.3 (+) 命题与相关工作使用）

- **Hartvigsen, *Finding Triangle-free 2-factors in General Graphs*, preprint 2024-02-25**（作者主页 PDF 已下载 105 页）："we present a polynomial-time algorithm for the problem of finding a triangle-free 2-factor **as well as a characterization of the graphs that have such a 2-factor** and related min-max and augmenting path theorems." 全文 **0 次** 出现 Bertram/Horák/Kouider，"4-regular" 0 次 → 不含 4-正则推论。**意义**：(+) 猜想（每个 4-正则图有完全无三角形 2-因子）在他的刻画下应是"可判定"的——建议 r2_01 §7.3 把该猜想与 Hartvigsen 的刻画对照（可能直接得证或给出反例工厂），这是比 BH97 更该读的文献。
- **2026 年新综述**：J. van den Heuvel 等, *2-Factors in Graphs*, Electron. J. Combin. 33(2) (2026) #P2.40（= arXiv:2510.11486v2, 2026-05-07；OA PDF 已下载）：**不提及** Bertram/Horák/Kouider/triangle-free/4-regular/6-regular/ce —— 即 r2_01 §8 待核查的 arXiv:2510.11486 **不含**我们的引理 1/命题 6 的相关内容（[UNVERIFIED] 可结案为"无覆盖"）。

---

## 任务 2：竞争态势复查

### 3.1 arXiv:2509.01901（AABC25）

- **有 v2**：v1 2025-09-02，**v2 2025-09-07**（arXiv abs 页与 e-print tarball 双向确认；v1 tar=17848B，v2 tar=19474B）。⚠️ r2_01 §7.2/§8 的"仍为 v1"记录**错误**，需更正。
- v1→v2 差异（逐行 diff）：摘要与引言重写（把"Beikmohammadi 猜想：≤ n−1"改为"Erdős–Gallai 猜想：O(n)"；补 Pyber/Bucić–Montgomery 等背景；致谢新增"v1 发布后 Bertille Granet 与 Matija Bucić 提醒 Erdős–Gallai 猜想"）；email/date 变动。**Problem 6.1 与 Conjecture 6.2 的数学内容不变**（Problem 仅措辞从"Show Conjecture 1.2 holds if…"改为"Show that if G has max degree 5, or is 6-regular, or 8-regular, then G can be decomposed into at most n−1 cycles and edges"）。
- **重要**：本地 `front184/2509.01901_src/main.tex` 与 arXiv v2 **逐字节相同**（tar md5 均为 fa00e83d8db2d73d616dd0b158b809ae）——即 r2_01 引用的 main.tex:781–794 本来就是 v2 行号，引文无误；只是"版本状态"叙述错了。
- Conjecture 6.2 逐字（v2）："Every 6-regular graph is decomposable into three 2-factors, where one of these 2-factors has a component with at least 4 vertices."
- **被引**：Semantic Scholar `citationCount = 0`、citations 列表为空（API 复核）；OpenAlex W4416169864（DOI 10.48550/arxiv.2509.01901）`cited_by_count = 0`。

### 3.2 是否有人解决 6-正则 ce ≤ n−1 / Conjecture 6.2 / 引理 1？（窗口 2025-09 → 今）

- **未检索到**任何新文献解决这三者之一。检索覆盖：OpenAlex 引用网络（0）、S2 引用网络（0）、tavily 对 "cycle-edge decomposition"/"cycles and edges"+regular 的 2025–2026 检索（命中的只有 Erdős–Gallai 主线的通用 O(n)/log* 进展：Bucić–Montgomery 2023、EMS Magazine 2025 综述 "Cycles and expansion in graphs"、arXiv:2607.26049 等，均不触及正则图的 n−1 界）。
- 竞争者画像：AABC25 作者群（Akbari/Aloni/Beikmohammadi/Clow，SFU）在 v2 致谢显示他们正被同行提醒 Erdős–Gallai 文献——说明该方向活跃，但其目标是最一般的 O(n) 猜想，**没有人把 6-正则 n−1 当靶子**（该问题目前只存在于他们的 Problem 6.1）。
- ⚠️ 覆盖面缺口：arXiv 官方 API 搜索端点本次持续 429（rate limit），"2026 年新预印本"扫描靠 tavily/网页检索完成；Google Scholar 不可达。见 §5 覆盖面声明。

### 3.3 AABC25 对 Abreu–Aldred–Funk–Jackson–Labbate–Sheehan 2004 的表述核对

AAFJLS 2004（JCTB 92(2):395–404；勘误 JCTB 99(1):271–273, 2009）摘要原文（scispace PDF 全文首段 + ScienceDirect 摘要，双源一致）：

> "We show that a **digraph** which contains a directed 2-factor and has minimum **in-degree and out-degree at least four** has two non-isomorphic directed 2-factors. As a corollary we deduce that every graph which contains a 2-factor and has **minimum degree at least eight** has two non-isomorphic 2-factors."

AABC25 v2 正文："…if 6-regular graphs decomposing into three 2-factors is replaced with 8-regular graphs decomposing into four 2-factors, then the result follows by a theorem Abreu, Aldred, Funk, Jackson, Labbate, and Sheehan regarding the existence of non-isomorphic 2-factors in graphs with minimum degree at least 8."
→ **表述准确**（δ≥8 覆盖 8-正则；6-正则不被覆盖；有向版为 δ±≥4）。r2_01 §8 的相关描述（"主定理（有向版）… 度 6 情形不被覆盖"）与原文一致，**维持现状**。

---

## 4. 新颖性判定与建议措辞

### 4.1 三档判定

**部分已知（Partially known），且比 r2_01 现有定位更不利一档。** 理由：
- 命题 6 的**存在性断言**（L(B) 两无三角形 2-因子分解）按 KS95 摘要字面是 1995 年已知观察的直接特例——尽管我们无法读 KS95 全文去比对构造是否即 Φ，但"陈述被覆盖"这一点由摘要级证据即成立（两独立来源 + S2 tldr）。
- 引理 1 的**陈述**未找到先例（新），但其证明的关键步骤要改引 KS95。
- 主定理（ce ≤ n−2）、AABC25 Problem 6.1/Conjecture 6.2 的解决、even+Δ≤6 ⟹ ce ≤ n−1：**未找到任何先例或近似工作**（BH97 不涉 ce 界；其 10 篇施引无一涉 ce 界；2025-09 后无人触及）。
- BH97 本身：**没有被其覆盖**的证据——它是判定算法、作者自己猜想高次 NP-完全、且不涉 ce 界。

### 4.2 对 r2_01 §7.1/§8 的明确建议：**降级（改措辞），不减工作量**

具体建议：

1. **§7.1 第一条**（"核心新引理（引理 1，自足证明）… 本次新增命题 6（反 Φ 分解）"）改为：
   > **引理 1（核心）**：每个 4-正则简单图都有含 ≥4 阶圈的 2-因子。其证明分两步：(i) **结构归约（本稿新增）**：若某 4-正则图的每个 2-因子都是三角形因子，则 G ≅ L(B)、B 为 3-正则二部图（B 必含完美匹配）；(ii) 对 L(B) 构造两个无三角形 2-因子（Φ(σ) ⊔ Φ(−σ)）导出矛盾。第 (ii) 步与 **Kouider–Sabidussi (1995)** 的已知观察"3-正则图有完美匹配 ⟺ 其线图有无三角形 2-因子化"在断言上重合：本稿给出该观察在二部情形下的**显式自足构造与计数推论**，不主张其存在性断言的首创性。
2. **§7.1 第二条/§7 摘要点 2**（"命题 6（反 Φ 分解）"）改称"命题 6（KS95 观察的显式构造版）"，并在 §8 增两条引用：
   - [KS95] M. Kouider, G. Sabidussi, *Factorizations of 4-regular graphs and Petersen's theorem*, J. Combin. Theory Ser. B **63** (1995) 170–184, DOI 10.1006/jctb.1995.1014。关键观察（摘要）："a 3-regular graph has a perfect matching if and only if its line graph has a triangle-free 2-factorisation"；推论：连通 4-正则图若含 ≤2 个属于三角形的割点则有无三角形 2-因子化。**全文未获取**（ScienceDirect 反爬），定位基于摘要（两源）——投稿前建议补全文核对。
   - [BH97] 条目**升级为**：不仅"多项式判定算法"，还应写明 **BH97 作者本人（经 Plummer 2007, Theorem 6.9/Conjecture 6.10 转述）把 "2n-正则（n≥3）分解为 n 个无三角形 2-因子的识别问题" 登记为猜想 NP-完全**——用于论证"BH97 不构成对 L(B) 类或 ce 界的覆盖"。
3. **摘要/§5 的"核心新引理"语气**统一改为"新的结构归约 + 显式构造 + 完整计数后果"；主定理与 AABC25 解决的"首创性"表述**维持甚至可加强**（可写明：据 OpenAlex/S2，AABC25 截至 2026-09-14 被引 0，且其 Problem 6.1/Conjecture 6.2 与我们完成的结果逐字对应）。
4. **新增一条审稿人预案**（放入 §7 或 rebuttal 素材）："为什么不用 BH97 的算法？" 答复要点：BH97 判定的是"两个无三角形 2-因子"的存在性（存在 NO 实例，等于无完美匹配的三正则图的线图），不含任何 ce 计数或 6-正则推论；且其作者自己认为 n≥3 情形是高复杂度问题。引 Plummer Theorem 6.9 + Conjecture 6.10 为证。
5. **§8 版本状态更正**：把"arXiv:2509.01901 … 本次联网复核仍为 v1"改为"v2（2025-09-07）；v2 仅重写摘要/引言（改挂 Erdős–Gallai 猜想），Problem 6.1 与 Conjecture 6.2 数学内容与 v1 相同；本地 main.tex 与 v2 逐字节相同"。

### 4.3 未找到先例的两条（覆盖面见 §5）

- "每个 4-正则简单图有含 ≥4 阶圈的 2-因子"（引理 1 的陈述）——**未找到任何文献陈述**；
- "4-正则图的每个 2-因子都是三角形因子 ⟹ G ≅ L(B)（B 三正则）"这一结构归约——**未找到先例**。

---

## 5. 问题谱系（一页纸）

**起源**：Petersen 1891 —— 2k-正则图可分解为 k 个 2-因子（本稿引理 0 的经典原型）。**三角禁用的变体**由此分叉。

**主线 A：无三角形 2-因子 / 分解**
- 1986 Cornuéjols–Hartvigsen（匹配理论的扩展）、1988 Cornuéjols（general factors）——技术工具箱。
- 1988 Hell–Kirkpatrick–Kratochvíl–Kříž, *On restricted two-factors*（SIAM JDM 1:472–484）——受限 2-因子的复杂度框架；BH97 引言的背景。
- **1995 Kouider–Sabidussi（JCTB 63:170–184）**——① 观察：3-正则图有完美匹配 ⟺ 其线图有无三角形 2-因子化；② 定理：连通 4-正则图若 ≤2 个割点属于三角形，则有无三角形 2-因子化（充分条件）。**这是本稿命题 6 的最直接先行工作。**
- **1997 Bertram–Horák（SIAM JDM 10:309–317）**——任意 4-正则图的两无三角形 2-因子分解的多项式判定算法（NO 实例存在）；作者登记 Conjecture：2n-正则（n≥3）识别问题 NP-完全。
- 1998 Heinrich–Liu–Zhang（JCTB 72:197–207）——无 Petersen minor 的简单图的 triangle-free circuit decomposition 刻画；1998 前后 Heinrich–Liu–Yu——4-正则图有 triangle-free Euler tour ⟺ K5-free 且 (K5−e)-free（此定理被 2021 DML 论文用作工具）。
- 2007–2012 Hartvigsen–Li——子三次图的 triangle-free simple 2-matchings 多面体与算法（IPCO'07、SIAM J. Optim. 21:1027–1045、Math. Prog. 138）。
- 2024 Hartvigsen——一般图 triangle-free 2-因子的多项式算法 + **完整刻画**（preprint，作者主页）。**这是 (+) 猜想的直接对照物。**

**主线 B：cycle-edge 分解（ce）与覆盖**
- 1966 Erdős–Gallai 猜想：O(n) 条圈与边分解；Lovász 1968：⌈n/2⌉ 圈与路径；Pyber 1985：n−1 覆盖；Conlon–Fox–Sudakov 2014（O(n loglog n)）；Bucić–Montgomery 2023（O(n log* n)）；Bonamy–Perrett（Δ≤5 的 Gallai 路径猜想）；EMS Magazine 2025 综述（Montgomery 等）。
- 2025 AABC25（arXiv:2509.01901，v2）——Δ≤4 ⟹ ce ≤ n−1；爪-free 的 2-正则分解版；Problem 6.1（Δ=5 / 6-正则 / 8-正则的 ce ≤ n−1）与 Conjecture 6.2（6-正则 ⟹ 三个 2-因子分解，其一含 ≥4 点分量）。
- 2025 Lane 05（本 campaign）——even + Δ≤6 ⟹ ce ≤ 3⌊n/3⌋。
- **本稿**——6-正则 ⟹ ce ≤ n−2；AABC25 Problem 6.1 / Conjecture 6.2 解决。

**相邻开放问题**：Hajós 猜想（Eulerian 图 ≤(n−1)/2 圈分解）；Oberwolfach；2-factor-isomorphic 图（Abreu 等系列：δ≥8 / 有向 δ±≥4 有两个不同构 2-因子；4-正则 2-factor-isomorphic 的无限族；二部伪 2-factor-isomorphic 猜想 2023 反例）；Petersen minor 与 triangle-free circuit decomposition；snarks/odd 2-factored。

---

## 6. 覆盖面声明

**查了**：OpenAlex API（work 查询、cites: 过滤、title.search、locations）；Semantic Scholar Graph API（paper/abstract/tldr/citations，BH97、KS95、HLZ98、AAFJLS04、AABC25）；Crossref/zbMATH Open API（Zbl 0867.05054）；SIAM 官方页（tavily-extract 全文）；Plummer 2007 综述 PDF 镜像（全文 31 页，本地 /tmp/plummer_survey.pdf）；Hartvigsen 2024 preprint PDF（105 页，本地 /tmp/hartvigsen24.pdf）；EJC 2026 "2-Factors in Graphs" PDF；arXiv abs 页与 e-print（2509.01901 v1/v2 均下载并与本地 main.tex 逐字节比对；2510.11486 版本史）；Wayback CDX（SIAM/ScienceDirect 目标）；tavily 检索约 12 轮（含 scispace、ResearchGate、dmlett、Springer、Lirias 等镜像与转述）。

**没查到/失败**：
- **BH97 与 KS95 的全文**（两篇都是付费/反爬，Wayback 无 PDF 快照，CORE 需 key，scholar.archive.org 反爬，CiteSeerX 已死，scispace/ResearchGate 拒绝直取）；
- MathSciNet 评审文字（无订阅）；Plummer 2013 Handbook 章节；Yu–Liu (2009) 书；HLZ 1998 正文；Hartvigsen–Li 2007/2011/2012 正文；
- DBLP 与作者主页被 bot 保护，**Bertram 的学位论文路径未走通**（未做馆际互借、未发作者邮件——留给编排者决策）；
- **arXiv 官方 API 搜索端点本次持续 429**（rate limit），2026 新预印本扫描改由网页检索完成，可能有遗漏；Google Scholar 不可达（无法核独立被引数）；
- 语言壁垒：只检索英文文献（俄语/中文文献未查）；未使用 Sci-Hub（按任务约束）。

**可靠性分级**：BH97 摘要=官方原文级（4 源）；Plummer Theorem 6.9/Conjecture 6.10=同行评审综述原文级（PDF 已下载，页码 812）；KS95 摘要=出版商元数据级（2 源 + S2），**全文未读，其"iff"表述与"triangle-free 2-factorisation"的精确定义有待全文核实**；HLZ 摘要片段=搜索引擎片段级（低）；SIAM PDF 首页片段=缓存级（低）。

---

## 7. 竞争态势一句话

**无抢占风险**：AABC25 v2 只是换背景框架（数学不变）、至今被引 0，2025-09 以来没有任何新文献触及 6-正则 ce ≤ n−1、AABC25 Conjecture 6.2 或引理 1——真正的风险不在别人抢先，而在于我们自己的新颖性措辞必须按 KS95 降级。

---

## 附：报告内所有可点击来源

- BH97（SIAM）：https://epubs.siam.org/doi/10.1137/S089548019427144X ｜ACM：https://dl.acm.org/doi/10.5555/252265.252294 ｜zbMATH：https://zbmath.org/1013282 ｜S2：https://www.semanticscholar.org/paper/8118a5e80e7cd83c35429d6de01770d9aa9a4668 ｜OpenAlex：https://openalex.org/W2058677112
- Plummer 综述 PDF（镜像）：http://ftp.eecs.umich.edu/~pettie/matching/Plummer-f-factor-survey.pdf ｜DOI：https://doi.org/10.1016/j.disc.2005.11.059
- KS95：https://www.sciencedirect.com/science/article/pii/S0095895685710143 ｜https://dl.acm.org/doi/abs/10.1006/jctb.1995.1014 ｜S2：paperId b9e5f2c3fa0e2ea03438d1b6d24ba3125a051a74
- HLZ 1998：https://doi.org/10.1006/jctb.1997.1808 ｜片段镜像：https://scispace.com/pdf/triangle-free-circuit-decompositions-and-petersen-minor-4o3v032pzm.pdf
- Hartvigsen 2024：https://david-hartvigsen.net/wp-content/uploads/2024/03/Tri-free-2-matchings-2-25-24.pdf
- EJC 2026 综述：https://www.combinatorics.org/ojs/index.php/eljc/article/download/v33i2p40/pdf ｜arXiv:2510.11486
- AABC25：https://arxiv.org/abs/2509.01901 （v2 2025-09-07）｜OpenAlex：https://openalex.org/W4416169864
- AAFJLS 2004：https://doi.org/10.1016/j.jctb.2004.09.004 ｜勘误：https://doi.org/10.1016/j.jctb.2008.09.001
- Johnson et al. 2021（BH97 转述 "polynomial time"）：https://www.dmlett.com/archive/v6/DML21_v6_pp32-37.pdf
- 本地文件：BH97/KS95 未取到的全文（无）；Plummer 综述 PDF=/tmp/plummer_survey.pdf、Hartvigsen=/tmp/hartvigsen24.pdf、EJC=/tmp/ejc_2factors.pdf、AABC25 v1/v2 源=/tmp/aabc_v1/、/tmp/aabc_v2/（本会话临时目录）
