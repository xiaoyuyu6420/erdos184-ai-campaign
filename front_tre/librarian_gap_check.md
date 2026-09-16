# 片引理 GAP 新颖性/覆盖核查报告（Librarian，2026-09-14）

**核查对象**：`/Users/munich/Desktop/数学/front_tre/attack_tre.md` §片引理——连通无桥 subcubic 图（n ≥ 3）的最大偶子图边数 p2(X) ≥ n/2 + 3/2（= 攻击报告中的唯一 GAP，卡在"删点后 X₁ 奇阶单块 +1 构造"）。

## 红绿灯总览

| # | 待查项 | 灯 | 结论 |
|---|---|---|---|
| 1 | 片引理（无桥 subcubic 最大偶子图下界） | **红（已被覆盖，直接引用）** | 是 Choi–Kim–Kostochka–Park–West 2019 定理 1.3 的即时特例（且弱于它） |
| 2 | 等价/更强定理 | 红 | 同上（CKKPW 全家桶）；Botler–Jiménez–Sambinelli 系是相邻问题（3-分解猜想），不覆盖但同谱系 |
| 3 | n=16 极小无完美匹配立方图 | 红（已知） | Chartrand–Goldsmith–Schuster 1979（Colloq. Math. 41(2)，Corollary 2a）+ MathWorld GraphData {"Cubic",{16,104}} |
| 4 | 是否有人在攻 2509.01901 Conjecture 6.4 | 绿（无人跟进） | Semantic Scholar 0 引用 + OpenAlex cited_by 0 + 作者主页仍标 preprint、无同主题后续 |

---

## 1. 新颖性判定（核心：片引理）

**红——已被覆盖。** 片引理是已发表定理的即时推论：

> **I. Choi, R. Kim, A. V. Kostochka, B. Park, D. B. West, *Largest 2-regular subgraphs in 3-regular graphs*, Graphs and Combinatorics 35(4) (2019) 805–813.** DOI: 10.1007/s00373-019-02021-6；arXiv:1903.08795（2018-09-18 版本全文在 https://dwest.web.illinois.edu/pubs/2reg.pdf ，本核查已逐页读取）。

其 **Theorem 1.3 / 2.3**（原文引述）：

> "If G is a subcubic n-vertex multigraph with c cut-edges and 1-deficit d, then **f2(G) ≥ n − max{0, (d+c−1)/2}**, and this bound is sharp."

其中 1-deficit d = 3n − 2m，f2(G) = 最大 2-正则子图的顶点数。

**换算两步，片引理即得：**

(a) **p2 = f2（subcubic 图上）**：偶子图各点度 ∈ {0,2} ⟹ 是顶点不交圈的并，边数 = 顶点数；2-正则子图反之亦然。故按边数的最大偶子图 = 按顶点数的最大 2-正则子图。

(b) **应用（X 连通无桥 subcubic，故 c = 0）**：
- X 为圈（全度 2）：p2 = n ≥ n/2 + 3/2；
- X 立方（d = 0）：Petersen 定理 ⟹ 2-因子 ⟹ p2 = n；
- 其余情形（有度 3 点，d ≥ 1）：m ≥ n+1（Σdeg ≥ 2n+1 且为偶 ⟹ 2m ≥ 2n+2），故
  **p2(X) = f2(X) ≥ n − (d−1)/2 = m − n/2 + 1/2 ≥ n/2 + 3/2**。∎

附赠强化版（比片引理强，随 m 增大）：非圈非立方的连通无桥 subcubic 图满足 **p2(X) ≥ m − n/2 + 1/2**。

注意：报告 GAP 所在的"残缺情形"（X − v 为奇阶连通无桥单块、需 +1）正是 CKKPW 自己标注的困难核心——原文 §2："**The difficult case is when c = 0 and d > 0**"——他们用 Edmonds 加权匹配（经 O–West）+ Plesník 定理 + Tutte 集合解决。报告的两条补法（拆点提升/奇阶强化）被反例封死与此完全吻合：这一步本质需要重活，CKKPW 已经干了。

**是否降档考虑**：无。CKKPW 陈述是多重图级别（简单图 a fortiori）、c=0 精确对应无桥、界严格更强、并给出等式刻画（Thm 1.6）。判定"红"。

## 2. GAP 段替换建议（可直接粘贴）

将 `attack_tre.md` §片引理的归纳证明 + GAP 声明整段替换为：

> **片引理 Φ（已闭合；归功于 CKKPW）**
> **引理 A**（Choi–Kim–Kostochka–Park–West, Graphs Combin. 35 (2019) 805–813, Thm 1.3）：subcubic n 点多重图有 c 条割边、1-deficit d = 3n−2m，则 f2(G) ≥ n − max{0, (d+c−1)/2}，f2 = 最大 2-正则子图顶点数；等式情形（Thm 1.6，连通时）当且仅当删去全部割边后每个分量是单点、balloon、或其 G 族（2-连通立方二部多重图删一点后逐点"爆炸"所得）。
> **引理 B（换算）**：subcubic 图上 p2 = f2（偶子图度 ∈ {0,2} ⟹ 顶点不交圈并且边数=顶点数；反向显然）。
> **片引理证明**：X 连通无桥 subcubic ⟹ c = 0。若 X 全度 2 则 X 为圈，p2 = n；若 X 立方则 Petersen 给 2-因子，p2 = n；否则 d ≥ 1 且 m ≥ n+1，p2 ≥ n − (d−1)/2 = m − n/2 + 1/2 ≥ n/2 + 3/2。∎
> 推论形式 Φ(X) ≥ b/2 + 3/2 的换算照原报告不变（全偶子图对任何规范合法）。

**引用条目**：
I. Choi, R. Kim, A. V. Kostochka, B. Park, D. B. West, Largest 2-regular subgraphs in 3-regular graphs, **Graphs and Combinatorics 35(4) (2019) 805–813**, DOI 10.1007/s00373-019-02021-6, arXiv:1903.08795.

**连锁效应**：
- 定理 D 由"条件性完全证明"升级为**无条件**（在报告内部自称完全证明的定理 A/C/拼装引理成立的前提下）；
- §9.1.b 的"临界图结构"计划**不必从零做**：Thm 1.6 已给出全等式刻画（单点 / balloon / G 族）。报告中实测的紧例 K_{2,3} 正是 G 族最小成员（K_{3,3} 删一点，d = 3，f2 = n − 1 = 4）；
- §9.1.a 的猜想（"p2 ≥ (n+3)/2 极可能是已知结果"）**证实**，出处即上；
- 遗留清单 ②（bridgeless subcubic 圈打包已知界）= CKKPW Thm 1.3 + Corollary 1.2（cubic 简单图 f2 ≥ min{n, ⌈5(n+2)/6⌉}；无环多重图 ⌈3(n+2)/4⌉）。

## 3. 其余三项结论

### 3.1 n=16 极小无完美匹配立方图 —— 已知
- **MathWorld "Petersen's Theorem"**（https://mathworld.wolfram.com/PetersensTheorem.html ）："every cubic graph with 0, 1, or 2 bridges has a perfect matching. The graph above shows the **smallest counterexample for 3 bridges, namely a connected cubic graph on 16 vertices** having no perfect matchings. This graph is implemented in the Wolfram Language as GraphData[{"Cubic", {16, 104}}]." —— 与报告"3×细分K4 + 三桥中心点"结构一致（唯一 16 点无 PM 连通立方图）。
- **正式出处**（经 MathOverflow #98385 中 Peter Heinig 的注释指认）：G. Chartrand, D. L. Goldsmith, S. Schuster, *A sufficient condition for graphs with 1-factors*, **Colloquium Mathematicum 41(2) (1979)**，Corollary 2a（p. 343）陈述最小性，p. 341 有图。MO 链接：https://mathoverflow.net/questions/98385/
- 相邻补充：**Errera (1922)**——连通立方图的桥若全在一条路上则有完美匹配（MathWorld 同页引述）。这恰是报告 §7"PM-free ⟹ 三桥必须聚于一点"观察的文献对应物（Errera 的逆否 + Petersen 的 ≤2 桥定理）。
- 该图仍活跃：Haemers（2026 预印本，Tilburg）"On perfect matchings, edge-colourings and eigenvalues"再次使用这张 16 点无 PM 立方图（谱方向）。https://repository.tilburguniversity.edu/bitstreams/59e3aaca-6d26-4b0a-ae4e-0a3755791dc6/download
- 报告遗留清单 ①（Petersen 1-因子定理多重图版出处）：CKKPW §1 的现代表述可直接引："every cubic multigraph with at most two cut-edges has a 2-factor and (equivalently) a 1-factor"，归 Petersen 1891（Acta Math. 15, 193–220）。**Lovász–Plummer 书内定理编号未核实**（本书不可及，见覆盖面声明）。

### 3.2 靶子论文跟进（查重）—— 无人跟进
- **Semantic Scholar** citations API（arXiv:2509.01901）：返回空，0 篇引用（2026-09-14 查询）。
- **OpenAlex** W4416169864："Tight Bounds for Cycle-Edge Decompositions and Covers"，publication_year 2025，**cited_by_count = 0**。
- **作者主页**（https://www.alexanderclow.com/publications ，2026 年状态）：该文仍列在 "Submitted Papers"（preprint），作者 2025–2026 的其他论文均为别的方向（oriented chromatic number、quasi-kernels、cops & robbers、Lovász 反例、odd wheels），**无同主题后续**。
- arXiv 仅 v1（2025-09-02）/ v2（2025-09-07）。
- 相邻领域动态（非直接跟进）：subcubic 分解领域 2026-08 出现 arXiv:2608.25385（证明 3-Decomposition Conjecture，用到 Botler–Jiménez–Sambinelli–Wakabayashi 的极小反例结构定理）——说明该领域活跃，但对象是"生成树+匹配+2-正则子图"分解（Hoffmann-Ostenhof–Kaiser–Ozeki 意义下等价的 2DC/3DC 猜想），**不是** f_re 猜想。

### 3.3 Botler–Jiménez–Sambinelli 系与 Kaneko 线（谱系定位）
- Botler–Jiménez–Sambinelli–Wakabayashi：2-Decomposition / 3-Decomposition Conjecture 系列（cubic 图分解为生成树+匹配+2-正则子图）；与 f_re 同属"圈-边分解"大谱系（Erdős–Gallai ⟶ Pyber ⟶ Bucić–Montgomery ⟶ 2509.01901），但问题不同，未覆盖片引理。
- Kaneko：可考的最近结果是 A. Kaneko, *A necessary and sufficient condition for the existence of a path factor…*, JCTB 88 (2003) 195–218（路因子，非圈打包）。报告 §9.1.a 的"Kaneko 类"猜测**未找到**对应片引理的 Kaneko 定理；实际应答者是 CKKPW。
- Erdős–Pósa / Thompson–Wollan 线（"cubic 图不交圈覆盖 ≥ n/6 顶点"级别）：仅在配额耗尽的内置搜索的模型自述中出现，**无链接未核实**，且远弱于 CKKPW，不影响判定；引用请勿使用。

## 4. 问题谱系（一页纸）

**问题**：图能被拆成多少个"圈 + 单边"块？（Erdős–Gallai 1968 猜想 O(n) 块；覆盖版由 Pyber 1985 证：n−1 个；分解版最好界 O(n log* n)，Bucić–Montgomery 2023。）

- **1965–1972**：Edmonds 匹配多面体 / Plesník（(t−1)-边连通 t-正则图有避开指定 t−1 条边的 1-因子）——CKKPW 证明的两个引擎。
- **1891**：Petersen（立方多重图 ≤2 割边 ⟹ 1-因子 = 2-因子；无桥 1-因子定理）。
- **1922**：Errera（桥在一条单路上 ⟹ 有完美匹配）。
- **1979**：Chartrand–Goldsmith–Schuster：≤2 桥定理的推广与 16 点极小反例（Colloq. Math. 41(2)）。
- **1998**：Hanson–Loten–Toft：(2r+1)-正则图 ≤ 2^r 条割边 ⟹ 有 2-因子。
- **2010/2015**：O–West 两篇（balloon 概念；割边与奇正则图匹配/Chinese postman）。
- **2018–2019**：Kostochka–Raspaud–Toft–West–Zirlin（arXiv:1806.05347：(2r+1)-正则 ≤ 2^r − 3(k−1) 割边 ⟹ 2k-因子；**对报告 §6 的 k ≥ 2 情形直接有用**）；**Choi–Kim–Kostochka–Park–West：f2 精确极小值定理（本文红牌来源）**。
- **2019–2026**：Botler–Jiménez–Sambinelli(+Wakabayashi) 2DC/3DC 系列；2023 Bucić–Montgomery O(n log* n)；**2025-09 Akbari–Aloni–Beikmohammadi–Clow（靶子 2509.01901）+ Conjecture 6.4（(2k+1)-正则 f_re ≤ n−1）**；2026-08 arXiv:2608.25385 证 3DC。
- **已知变体**：最大偶子图（= 圈打包，subcubic 时顶点不交）；2-因子存在性（割边数阈值型）；balloon 结构；2-匹配/完美 2-匹配。
- **相邻开放问题**：f_re 猜想的 k ≥ 2 情形（报告 §6 已指出桥分解路线失效，需 Tutte 障碍归纳——KRTWZ 的割边-因子阈值是可用的第一性工具）；3-connected cubic 图周长（Bondy–Simonovits / Jackson n^0.69 线，与片引理无关）。

## 5. 覆盖面声明

**查了的**（全部带时间戳 2026-09-14）：
- 靶子确认：arXiv:2509.01901 abs 页（标题/作者/日期）；本地源码核对行号（front184/2509.01901_src，报告已完成）。
- 片引理：tavily（advanced）检索 "maximum even subgraph / largest Eulerian subgraph + subcubic + bridgeless"、"packing vertex-disjoint cycles + subcubic + 2-regular subgraph"、CKKPW 发表版；**直接读取 CKKPW 全文 PDF 9 页**（dwest.web.illinois.edu/pubs/2reg.pdf，curl + pypdf），定理 1.1/1.2/1.3/1.6、证明骨架、参考文献逐条过目。
- n=16 图：MathWorld Petersen's Theorem 页；MathOverflow #98385（含 Chartrand–Goldsmith–Schuster 1979 出处指认）；Haemers 2026 预印本。
- 查重：Semantic Scholar citations API（空）；OpenAlex API（cited_by 0）；Clow 个人主页；arXiv abs 页版本历史。
- 谱系：Botler–Jiménez–Sambinelli–Wakabayashi 系列（tavily）；Kaneko 定理定位（tavily）；KRTWZ arXiv:1806.05347（CKKPW 参考文献 [7]）。
- 报告遗留 ③（"2-connected subcubic 周长 ≥ (n+3)/2"）：tavily 检索 circumference + 2-connected + subcubic，**未找到直接来源**；现有文献集中于 3-connected/cubic 的渐近周长（Bondy–Simonovits 1980、Jackson）。该命题真伪未验证，建议改用 CKKPW Thm 1.6 结构刻画替代此路线。

**没查/查不了的**：
- 内置 WebSearch 配额耗尽（官方报错"reset 2026-09-29"），仅首查询得到一次无结果响应；后续全部走 tavily。
- Google Scholar、MathSciNet：bot 屏蔽/订阅墙，不可及。
- DBLP：Anubis 反爬拦截；发表版信息改由 SNU Pure（Elsevier）页面核实（卷期页码 DOI 齐全）。
- arXiv API au:Clow 检索：网络返回空（失败），作者跟进情况以 Clow 主页 + 两个引文库为准。
- 俄语/中文文献未专门检索（语言壁垒声明）；OEIS 未查（本项无数列需求；16 点图已有 GraphData 编号）。
- Lovász–Plummer《Matching Theory》书内定理编号未核实。

**对攻击报告的两点复核提示（下游动作）**：
1. 摘要/§5 中"机器验证 p2 − n/2 ≥ 2 恒成立（n ≤ 14）"与 K_{2,3}（n=5，p2=4，p2−n/2=1.5）矛盾——K_{2,3} 恰是片引理紧例（= n/2+3/2），CKKPW 等式刻画也确认 G 族取等。建议复核 sweep3 的枚举范围（是否 n≥6 或统计口径不同）并改表述为"p2 ≥ n/2+3/2 恒成立，紧例 K_{2,3} 型"。
2. 定理 D 升级为无条件后，报告"结论强度：部分进展"一栏与 §8 Lean 陈述中的 hlemma 假设应同步更新（hlemma 现在是引理 A+B 的推论，不再是 sorry）。
