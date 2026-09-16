# CHANGES：draft_en.tex → draft_v2/main.tex 重写记录

日期：2026-09-15。
输入：五份材料全部读完；骨架的定理集合未动（只修了三处陈述级笔误，见 §二）。
产出：`main.tex`（tectonic 编译通过，PDF 已生成，无错误、无未解析引用，仅剩 2 处 <5pt 的轻微 overfull，肉眼不可见）。

---

## 一、相对骨架的结构变化

1. **§6 大幅扩写为「反例 + 六正则问题的解决」**。
   - 新增：引理 0（Petersen 2-因子分解自足版）、**引理 1（刚性引理：所有 2-因子皆为三角形之并的 4-正则图必为 L(B)）**、**命题 6（Φ(σ) ⊔ Φ(−σ) 划分 + 双无三角形）**、**定理 2′（6-正则 n≡0 mod 3 ⟹ ce ≤ n−2）**、**定理 3（AABC25 Conjecture 6.2 逐字成立，三分解决策写全）**、系（全部 6-正则 ⟹ ≤ n−1；**even + Δ≤6 ⟹ ≤ n−1**）。
   - 全部数学内容照搬 `campaign/r2_01_aabc25_struct.md`（四稿），含 KS95 降级定位、BH97/Hartvigsen 对照、「P_n 非 even 图不作紧性 witness」的三稿修订。
   - 骨架的 `cor:6reg`（瓶颈归约，写的是 open conjecture）按四稿升级为已解决；骨架 open problems 里「Six-regular bottleneck」一条相应删除。
2. **新增 §7「Odd degrees: the cubic case of Conjecture 6.4」**（来自 `front_tre/attack_tre.md`）。评估结论：**并入，作为独立一节**。理由：完整证明（依赖已发表定理，引用封口干净）、与 §6 是同一篇 AABC25 的姊妹猜想、计算完备验证可展示。注意点已在正文处理：f_re 与 ce 是**不同不变量**，§7 开头显式定义并说明 f_re ≤ ce，避免与全文的 ce 混淆。贡献边界照抄 tre 报告的诚实声明（归约链 + 桥分解 + 拼装 + 计算验证是本项目贡献；片引理引 CKKPW 2019 Thm 1.3）。
3. **Open problems 更新**：删「Six-regular bottleneck」；新增三个来自战役的问题——6-正则的 n−3 残余问题（四稿注记 A）、「每个 4-正则图有完全无三角形 2-因子」（加强命题 +，含 BH97/Hartvigsen 定位）、奇正则 k≥2（Tutte 集结构）。「Δ≤5/6」一条改写：even 情形已闭合，剩余 = 非 even 的长 T-join 危险区。
4. **新增 Appendix A（Proof status and computational verification）**：汇总全部计算验证，数字与下述记录严格一致。每个定理的 `\proofsrc` 指针保留骨架格式（Proof status: …），新定理按任务要求标注 *full proof in campaign records*。
5. **引言重写为动机叙事**：预算审计的视角（n−1 在哪些族恰好成立、在哪里破、破的原因是什么）；六正则的「卡在哪、钥匙是哪一步」（刚性引理 + 反 Φ 构造）写在引言里。禁用词已扫描（comprehensive/delve/crucially/furthermore/it is worth noting/leverage/robust/novel 均未用于正文；"No novelty is claimed" 是诚实免责，保留）。
6. Acknowledgments 保留骨架的 AI 协作声明框架，追加第二轮加固（独立证明复审 PASS、数值加宽、文献复核发现 KS95 并因此降级命题 6、AABC25 v2 更正），口径与 `email_final_v2.txt` 一致。「未投递、求验证」立场**未写进正文**（按项目基准留给 cover letter）；`\thanks` 只保留中性的 draft + 验证状态说明。

## 二、修正的数学/事实问题（骨架 → v2，均建议人核）

1. **`lem:tjoin` 的无条件 5n/3 尾巴（最重要的一处修正）**：骨架写 "τ ≤ n−1 always, so ce ≤ ⌊(5n−2)/3⌋ unconditionally"——这对一般图不可能成立（等于直接解决 O(n) 猜想；该式只有在 m ≤ 3n 时才由 (m+2τ)/3 得出，对应 Δ≤6 与 degeneracy 两个应用场景，骨架 §6 定理 D 的 5n/3−2/3 正是这么来的）。已改为「该判据适用于一切 m = 3n+O(1) 的图族」。**⚠️ 需人核 lane_04 Thm 1.2 / lane_08 Lem 3.1 原文，确认原意是否就是限定 m。**
2. **`thm:deg2` 等号条款**：骨架 "equality ce = n−1 iff forest" 不准确（c ≥ 2 的森林 ce = n−c < n−1）；已改为 "iff G is a tree"。上界链 n − c − s(G) 本身未动。
3. **`thm:counterex` 陈述笔误**："all **nine** edges a_i b_j" → "all **twelve**"（3×4 = 12，m = 3+12 = 15 才与陈述自洽）。
4. **`thm:counterex` 证明概要微论证**：骨架 "(4,7) 用 eight b-ends among seven edges" 经我复推是**正确的**（7-圈用过全部 7 个顶点 ⟹ 含全部 4 个 b_j ⟹ 需 8 个 b 端 > 7 条边各至多贡献 1 个 b 端）；(5,6) 的论证也已复推成立（b 端恰为 8 ⟹ 6-圈纯二部过 3 个 b、5-圈需 2 个未被碰过的 b，只剩 1 个）。已按此重写，删除我第一版压缩时写错的过渡句。
5. **AABC25 引用编号全部修正（对照本地 `2509.01901_src/main.tex` 逐一核对）**：骨架写 "Theorem 1.9 = even Δ""Theorem 1.4 = Δ≤4""Problem 5.1 = Δ≤5"，实际（共享计数器、按 section 编号）：**Theorem 1.3 = Δ≤4；Theorem 1.5 = Even Delta；Problem 6.1 = Δ≤5 / 6-正则 / 8-正则；Conjecture 6.2 / 6.3 / 6.4**（Conjecture 6.4 = (2k+1)-正则 f_re ≤ n−1，与 tre 报告一致；冲突裁决按约定以战役记录 + 本地源为准）。
6. **AAFJLS04 标题修正**：骨架 "Graphs and decompositions: cycles with all degrees odd" 是错的；按 AABC25 的 main.bbl 和战役记录改为 **"Graphs and digraphs with all 2-factors isomorphic"**（JCTB 92 (2004) 395–404）。
7. **Erdős n−1 归属精确化**（按 erdosproblems.com/184 核对）：O(n) 猜想出自 Erdős–Gallai（该网页记为 EGP66 = Erdős–Goodman–Pósa 1966，BM22 同样引此文）；Er71 的 n−1 建议是**覆盖版**（Pyber 证明的就是它）；分解版 n−1 被 K_{3,n−3} 否证。骨架的对应 \TODO 已解决。
8. **tre 报告内部口径问题**：其摘要「cubic n ≤ 18 全量 55,458 张」中 9,588 实为 **n ≤ 12 全部连通奇正则图（k=1..5，非全是 cubic）**；cubic 侧全量数为 n=14/16/18 的 509/4,060/41,301。论文 Appendix A 已按行分开陈述，未使用 55,458 合数。**⚠️ 建议人核 `front_tre/results.jsonl` 确认 9,588 的构成。**

## 三、文献落实（骨架全部 \TODO 的处置）

网络受限（arXiv 直连 TLS 失败、WebSearch 配额耗尽），核对路径为：**项目内已下载的论文源文件逐字核对**（`2211.07689_src/`、`2509.01901_src/`、`campaign/lane07_scripts/{cfs_src,cklot_src}/`）+ erdosproblems.com/184 + 一次 tavily 检索。

| 骨架 \TODO 项 | 处置 | 依据 |
|---|---|---|
| EG（O(n log n) + 猜想出处） | 拆为 EG59（Acta Hungar. 10, 337–356）+ EGP66（Canad. J. Math. 18, 106–112，猜想记录处） | BM22 本地源参考文献逐字核对 |
| E71 | "Some unsolved problems in graph theory…"（Oxford 1969 会议集，Academic Press，97–109） | BM22 本地源 |
| E83 | "On some of my conjectures…", **Congr. Numer. 39 (1983), 3–19** | BM22 本地源（BM22 只写 "volume 39"；Congr. Numer. 是标准展开）⚠️ 刊名展开建议人核 |
| Py85 | **"An Erdős–Gallai conjecture", Combinatorica 5 (1985), 67–79** | BM22 本地源 |
| CFS14 | "Cycle packing", Random Structures Algorithms **45** (2014), 608–626 | 本地 `cfs_src/` 源文件 |
| BM22 标题 | **"Towards the Erdős–Gallai cycle decomposition conjecture"**，arXiv:2211.07689 | 本地源 \title |
| AABC25 | 作者四人（Akbari, Aloni, Beikmohammadi, Clow）+ 标题 "Tight bounds for cycle–edge decompositions and covers"，注明引用 v2 编号 | 本地源 \author/\title |
| CKLOT20 | 第五作者 **Treglown**（本地源确认）；改为已发表版 **Mem. Amer. Math. Soc. 244 (2016), no. 1152** | 本地源核对作者；卷号凭公开记录 ⚠️ 建议人核 |
| Wal | 改引 **Lucas 1883**（BM22 引 Walecki 的方式）+ BM08 | BM22 本地源 |
| HNS17 | **I. Heinrich, M. V. Natale, M. Streicher, "Hajós' cycle conjecture for small graphs"**, arXiv:1705.08724 | tavily 检索 arXiv 页核实 |
| 新增 | KS95（JCTB 63, 170–184）、BH97（SIAM JDM 10, 309–317）、CKKPW19（Graphs Combin. 35, 805–813）、CGS79（Colloq. Math. 41, fasc. 2）、Hartvigsen24（preprint） | 均按战役记录；CGS79 未写页码（记录只给到 fasc. 2 / Cor. 2a）|

## 四、数字溯源（Appendix A 各数字来自哪里）

- **K_4/K_5/K_6/K_7/K_8 精确值、K_8 的 3.3×10⁷ 搜索、反例四路验证**：骨架 \proofsrc（lane_09 / lane_05 / prepub_independent_check.py），原样保留。
- **725 个 2-degenerate、630 个 3-degenerate、3,324 圈（K_{3,14}+e）、794,530 圈（K_{5,11}）、1,273 个 n=6 反例、n≤6 全量**：骨架原数字，保留。
- **六正则全部数字**：`r2_01_aabc25_struct.md` §4 + `HARDEN_SUMMARY.md` §2——299,265（1/24/2,040/297,200）、832,944 = 48+3,456+829,440（s≤5 全参数）、1,183,920（两轮累计）、30,016（n=9 全量，四类 280/5,040/4,536/20,160，件数 ≤7=n−2、精确 ce=3）、21/266/7,849 类（n=10/11/12，max 件数 8/8/10，n=10 全类 ce=3，n=12 恰 5 类达 n−2=10）、8,000 随机（max 11/12/13/13）、对抗 s=7/s=8 各 1,500/600、18,279 证书 + 负对照 5/5 + sha256 三遍一致、890,100（标注为 600s 截断的标记图侦察，非全量）、残差风险边界 s≥7。**与 harden_round2 逐项一致，未做任何换算。**
- **cubic/奇正则数字**：`attack_tre.md` §5——9,588（口径见 §二.8）、509/4,060/41,301、60,077（min 2p₂−n = 3，唯一紧例 K_{2,3}）、n=16 极小 PM-free 唯一（归属 CGS79/Errera，按 tre §7 降级为「枚举确认唯一性 + 结构刻画」）、5-正则构造族 5 张（n=36..146）。

## 五、拿不准 / 需要人核的清单（按优先级）

1. `lem:tjoin` 的修正（§二.1）是否符合 lane_04 原意——这是唯一一处我**改动了引理内容**的地方。
2. tre 的 9,588 构成（§二.8）。
3. CKLOT 的 Mem. Amer. Math. Soc. 卷号 no. 1152 / 年份 2016（多次网络尝试均失败，凭公开记录写入）。
4. E83 的 "Congr. Numer." 展开名。
5. 论文署名沿用骨架的 "The Front184 Collaboration"——对外署名方式需要你拍板（email_final_v2 的口径是独立开发者 + AI 系统）。
6. 完整证明仍以 campaign records 指针形式存在（正文是 sketch，§6/§7 新定理的 sketch 已经把关键步骤写全）；若真的要投 arXiv，Appendix A–D（完整证明）需要实际写出。当前状态是「骨架要求的 v2 完整论文」，不是「可立即提交的终稿」。
7. 平面/degeneracy 新颖性的免责声明改成了正文散文（"a literature search in September 2026 found no prior work, though we have not re-verified this against the full literature"），保留了骨架 TODO 的实质，措辞是否合意请过目。

## 六、编译状态

- tectonic（Mac，等价 pdflatex 流程）清洁编译，无 error、无未解析引用/标签；All cite keys、labels 均已核对（无孤儿引用）。
- 仅剩 2 处 overfull <5pt（Appendix A 一条 item 内），肉眼不可见；正文禁用词扫描通过；"moreover" 仅 3 处且均为句中连接，非连环。
- 定理编号由 LaTeX 自动按 section 连续编号，无手写编号。
