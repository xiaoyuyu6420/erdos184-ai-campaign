# verify_english_pack —— 英文对外材料对抗性终审（Verifier，2026-09-14）

审查对象（只读）：
- `repo-publish/results/aabc25-conjecture-6.2/proof.md`（135 行）
- `repo-publish/results/aabc25-conjecture-6.2/README.md`（70 行）
- `repo-publish/README.md`（52 行）

对照底稿：`campaign/r2_01_aabc25_struct.md`（四稿）、`campaign/harden_round2/harden_numeric.md`、`campaign/harden_round2/bh97_landscape.md`、`2509.01901_src/main.tex`、`campaign/lane_05_delta6.md`、`campaign/harden_round2/{verify_round2_proof.md,verify_fixes.md}`、`email_final.txt`、`campaign/article_draft_zh.md`、`campaign/PREPUB_REVIEW.md`。
立场：默认有错。所有数学与数字结论均由**本轮自写实现**独立复算，不复用上游代码。

---

## 判定

**FAIL** —— 数学内容（证明与全部被核数字）经本轮独立重算**全部成立、零反例**；但英文材料作为"作者第一眼读到的东西"存在 **5 条必须改的硬伤**（3 条数字/归因事实错误 + 1 条复现命令不可运行 + 1 条发布前置条件未满足）。修完即可放行，无需改动任何定理陈述或证明。

严重度口径（按材料性质微调）：CRITICAL = 数学陈述或结论为假；MAJOR = 可被读者当场证伪的事实/数字/归因错误、或使"怎么自己验证"落空的缺陷；MINOR = 表述精度与读感。

---

## 发现清单

### F1【MAJOR·数字错误】`results/aabc25-conjecture-6.2/README.md:37` —— "all s ≤ 5 cases (829,440 combinations)" 的 829,440 是 **s=5 单项**，s ≤ 5 合计是 **832,944**

证据（本轮自写枚举 + DP，两次独立算法）：

| s | 标记 3-正则二部 B 数 | Σ#完美匹配 | 组合数 = Σ#PM·2^s |
|---|---|---|---|
| 3 | 1 | 6 | 48 |
| 4 | 24 | 216 | 3,456 |
| 5 | 2,040 | 25,920 | **829,440** |
| 3–5 合计 | 2,065 | — | **832,944** |

- 829,440 ≡ 0 (mod 32)，而 832,944 ≡ 16 (mod 32)：829,440 只能是 s=5 段的整数倍形式，不可能等于含 s=3,4 的合计。
- 全表口径自洽性：1,183,920 = 832,944（s ≤ 5）+ 350,976（s=6 抽样 = 64 × 5,484，300 个 B，平均 18.28 个匹配）。若按 README 的写法（s ≤ 5 = 829,440），则 s=6 抽样须为 354,480 而 s=3,4 的 3,504 组合被排除在总数之外——但 s=3（48）与 s=4（3,456）确在 `verify_r2_01.md:41` 的攻击清单内且已跑，排除不成立。
- 该错标同时存在于 `email_final.txt:9`（"all matchings and orientations for s ≤ 5, 829,440 combinations"），且四稿 §4 行 5 把它登记为"832,944 vs 829,440，3,504 之差，待核"——**本轮结论：两个数都对，是口径（s=5 单项 vs s ≤ 5 合计）被误标，不是第一轮实现 bug**（`verify_fixes.md:42` 的"疑为一轮实现的匹配计数偏差"应改写）。
- 我另用自写 Φ 扫描器（见重验记录 R2）在 s=5 上跑满 829,440 组合、零反例，等于把"829,440 属于 s=5"这一口径坐实。

建议改法（二选一，推荐 a）：
(a) `all s ≤ 5 cases (832,944 combinations: s = 3, 4, 5 contributing 48 / 3,456 / 829,440) + sampled s = 6 (1,183,920 combinations in total)`；
(b) 保留 829,440 但改标签为 `the s = 5 case (829,440 combinations; s = 3, 4 add 3,504 more, 832,944 in total)`。

### F2【MAJOR·归因错误】`results/aabc25-conjecture-6.2/README.md:3` —— "Since n ≢ 0 (mod 3) was already handled in the template paper"

证据：`main.tex:316–318` 只有**条件式**观察——"if G is a 6-regular graph **which can be decomposed into three 2-factors, where at least one of these 2-factors has at least one components with at least 4 vertices**, then G can be decomposed into at most n−1 cycles and edge"，紧接着 `main.tex:318` 问 "Is it possible every 6-regular graph admits such a decomposition?"。全文（grep 6-regular / divisible / mod 3）没有任何"n ≢ 0 (mod 3) 已被处理"的陈述；该分支是本材料自己由 Petersen（引理 1）+ 该条件观察一步得到的（四稿 §0、系 4 归给 `campaign/lane_05_delta6.md` 定理 A(ii)）。在同一份 README 里，第 19 行又说 n ≡ 0 (mod 3) 是 "the last open case"，两句并列时读者会认为前一句是别人论文的既有结果——而这正是收件人最会当场纠正的一类错。

建议改法：`Since the case n ≢ 0 (mod 3) needs no triangle factor (no 2-factor can be a union of triangles), the template paper's reduction applied to any Petersen 2-factorisation already closes it; together with Theorem 4 this gives ce(G) ≤ n − 1 for every 6-regular simple graph.`

### F3【MAJOR·交叉引用悬空】`results/aabc25-conjecture-6.2/README.md:19, 23, 61` —— 引用了 proof.md 中不存在的编号

- `:23` "…has a 2-factor containing a cycle of length at least 4 (**Lemma 3** below)"：proof.md 中是 **Lemma 2**（proof.md:18），README 内也没有 Lemma 3。
- `:61` "the existence statement of our **Proposition 6**"：proof.md 中是 **Proposition 3**（proof.md:20）。
- `:19` "our **Theorem A** pushes the same accounting … to n − 2"：proof.md 中是 **Theorem 4**（n−2 那一条），全文无 Theorem A。

这三处像是从中文稿（引理 1 / 命题 6）或更早草稿继承的编号。README 是"Read this first"的入口，读者按图索骥会立刻发现引用不存在。**不影响数学，但直接影响第一印象**。
建议改法：三处改为 `Lemma 2` / `Proposition 3` / `Theorem 4`（或统一写成"the 4-regular lemma"之类不依赖编号的称呼）。

### F4【MAJOR·复现命令不可运行】`results/aabc25-conjecture-6.2/README.md:45–54` —— 三个"second-round" 命令没一个按写法做事

本轮在仓库内实测（`/opt/homebrew/Caskroom/miniconda/base/bin/python3`，Python 3.13.12 + networkx 3.6.1）：

| README 写法 | 实测结果 |
|---|---|
| `python3 h_A_enum.py` | `error: the following arguments are required: --n, --g6, --out`（三个参数均 required=True，且需要先用 geng 生成 `data/geng_*_d*.g6`）→ 报错退出 |
| `python3 h_verify.py` | 打印 `{"total_records": 0, "total_failures": 0}`、exit 0 → **静默空转**，看起来像"校验通过" |
| `python3 h_A_exact.py` | 只打印自身 docstring（锚点运行需 `h_A_exact.py anchors`）→ 什么都没算 |

另：默认 `python3`（Homebrew 3.14.3）未装 networkx，照 README 原样敲 `python3 r2_selftest.py` 会 `ModuleNotFoundError`；README:45 只笼统写了 "Python 3, networkx"，未说明所用解释器/依赖（campaign 记录的运行环境是 miniconda 3.13.12 + networkx 3.6.1 + nauty 2.9.3）。
建议改法：把 harden_numeric.md §8 的完整命令列表抄进来（含三行 `geng -d3 -D3 10 / -d4 -D4 11 / -d5 -D5 12 -q > data/…`、`h_A_enum.py --n 10 --g6 data/geng_10_d3.g6 --out data/A_n10.jsonl --exact`、`h_A_exact.py anchors`、以及带全部数据文件参数的 `h_verify.py` 行），并加一句"需 Python+networkx+geng（nauty）"。现在的注释 "see harden_numeric.md for the full command list" 不能替代——页面承诺的就是"how to re-run it"。

### F5【MAJOR·发布前置条件】`results/…/proof.md:133,135` 与 `results/…/README.md:15,56` 指向的 `campaign/harden_round2/*`、更新后的四稿尚未在公开仓库中

证据（本轮 `gh api repos/xiaoyuyu6420/erdos184-ai-campaign/...`）：远端 `campaign/` 30 项**不含** `harden_round2/`；其 `r2_01_aabc25_struct.md` 仍是三稿（`verify_fixes.md:23` 同结论）；远端 HEAD `pushed_at = 2026-09-12`，无 `results/`。因此：
- `proof.md:133`（bh97_landscape）、`proof.md:135`（r2_01_scripts ✓ 存在、harden_round2 ✗ 不存在）、`README.md:15`（harden_round2 ✗）、`README.md:56`（harden_numeric / verify_r2_01：后者 ✓）目前都会 404；
- `email_final.txt:13-14` 的 "The complete proof, verification scripts, and review records are available at ⟨repo⟩" 在推送前是**事实性不实**（`verify_fixes.md` F-A 已判 MAJOR）。
- `proof.md:131` 更明确写着 "This corollary depends on that internal report（lane_05_delta6.md），not only on this document" —— 该文件存在 ✓，但同一句依赖链上的 harden_round2 必须一起推。

建议：推送四稿 + 整个 `harden_round2/` + `repo-publish/{README.md,results/}` 之后再发信；或先改邮件措辞。**这条不是文本错，是发布顺序问题，但英文页的可用性依赖它。**

### F6【MINOR】`proof.md:135` "covers cubic bipartite B with up to 18 vertices (s ≤ 6)"

s ≤ 6 对应 B 只有 2s ≤ **12** 个顶点；18 是 L(B) 的点数（3s）。四稿原文 "s ≤ 6（n ≤ 18）" 中的 n 指 4-正则图 L(B) 的阶，翻译时被挪到 B 头上。建议：`covers cubic bipartite B with at most 12 vertices, i.e. 4-regular graphs L(B) on up to 18 vertices (s ≤ 6)`。`README.md:56` 同类表述（"B with 2s vertices; exhaustive search covers s ≤ 6 (graphs up to 18 vertices)"）建议同样写清 "18 vertices of L(B)"。

### F7【MINOR】`proof.md:77` "Φ omits one pair at every x"

尾部点 Φ 只取 1 对、**omit 两对**（只举了 `{e_x,f_x}` 一个 witness）；结论只需"至少缺一对"，witness 本身也正确，但"one pair"字面读作"恰缺一对"与事实不符。建议：`Φ omits at least one pair at every x`。

### F8【MINOR】`proof.md:120`（推论 6 的括号）表述打结

原文："…this is Theorem 4 (ce ≤ n−2 ≤ n−1; for n = 3m ≥ 9; the smaller 6-regular graphs on n ≡ 0 (mod 3) vertices are excluded by n ≥ 7, so nothing remains)."
建议：`For n ≡ 0 (mod 3): 6-regular simple graphs have n ≥ 7, hence n ≥ 9, so Theorem 4 gives ce ≤ n − 2 ≤ n − 1.`（逻辑本身正确，只是读起来像绕口令。）

### F9【MINOR·证据等级】`README.md:60` "It contains no characterisation of the YES instances" / `proof.md:133` "prove no characterization of the YES instances"

这是对**未读全文**论文内容的正面断言，而同一份 README:66 又承认 "Neither paper was read in full"。landscape 的谨慎写法是"未见于任何可达来源"。另外 "prove no characterization" 更是把"没找到刻画"说成"证明了没有刻画"（实际证据是 Plummer 转述的 Theorem 6.9 + BH97 作者自己把高次识别问题登记为猜想 NP-完全）。建议统一改为 `we found no characterisation of the YES instances in any source we could access; the authors conjectured …`。注意 `bh97_landscape.md §1.2(b)` 的 Conjecture 6.10 逐字版是 "(a) two triangle-free **n**-factors / (b) n triangle-free 2-factors"——英文页目前回避了细节（安全 ✓），若展开必须用逐字口径。

### F10【MINOR·证据等级】`README.md:66` 证据等级段落

- "a peer-reviewed survey (Plummer 2007) that we **read in full**"：campaign 记录的是"PDF 已下载、p.812 逐字核对"（landscape §1.2(b)、§6 可靠性分级），说"read in full"略超证据。建议改 `whose relevant page (p. 812) we checked verbatim`。
- 建议补上 landscape §6 明确登记的那条残余风险：KS95 的 "triangle-free 2-factorisation" **精确定义**未获全文核实（摘要级证据，两来源）；若其含义与"分解为两个无三角形 2-因子"不同，命题 3 的定位需再改。现在只写了泛泛的 "if their proofs contain more than the statements above"。

### F11【MINOR】`repo-publish/README.md:33` "campaign/ 64 路攻击报告（lane_*.md）"

实测 `campaign/lane_*.md` = **10** 个（lane_01…lane_12，缺 10/11 等），其余材料在 `CAMPAIGN.md / MERGE_1.md / PREPUB_REVIEW.md / r2_0*.md / 各 lane*_scripts`。"64 路"是战役的代理路数（article §一：21+24+19），不是文件数。建议：`campaign/ — 64 路战役档案：各路报告（lane_*.md）、合并备忘、发布前三色审查、可复算脚本、AABC25 中文工作记录`。

### F12【MINOR】`repo-publish/README.md:46` "two 'claimed complete proof but had a gap' cases" 与出处

- 权威清单是 `article_draft_zh.md §五`（12 行表）与 `PREPUB_REVIEW.md`；后者写的是 **3 处**被标"完全证明"实则有洞（Y1–Y3，见 `PREPUB_REVIEW.md:9`、`:42`），article 表格中显式"证明有洞"只有 1 行（行 2）。"two" 两处都对不上。
- 指向 `campaign/r2_01_aabc25_struct.md §10` 也不准：§10 是 R2-01 相对二稿的变更记录，不含全战役 12 处清单。
建议改为 `…12 items during the campaign (the canonical table is §5 of article/article_draft_zh.md; PREPUB_REVIEW counts three "labelled complete, actually had a hole" cases, Y1–Y3)`，或删掉具体计数。

### F13【MINOR】`README.md:3` 把改写句标为 "verbatim"

主句 "Every 6-regular **simple** graph is decomposable into three 2-factors, **one of which** has a component with at least 4 vertices — … **verbatim**"，而 main.tex:792–794 原文是 "Every 6-regular graph is decomposable into three 2-factors, **where one of these 2-factors** has a component with at least 4 vertices"（无 "simple"）。proof.md:26 的定理 5 是**逐字**的 ✓，README 这处是改写。建议 README 照抄原文并在附近注明 "all graphs in this note are simple" 的约定（proof.md §0 已有该约定），或去掉 "verbatim"。

---

## 重验记录（全部为本轮自写实现，脚本在 /tmp/verif/，不复制上游代码）

R1【逐步重推 proof.md 全部陈述】手推 + 纸面核对：
- 引理 1←引理 0、引理 2←引理 1、命题 3←命题 6、推论 3.1←推论 6.1、定理 4←定理 2′、定理 5←定理 3、推论 6←系 4、注记 (d)←系 5：**逐条对应，量词与条件无增无减**；定理 5 与 main.tex:792–794 **逐字一致**（grep 核对行号 792–794 ✓）。
- 重点项：(1) 步(6) 度数计数 M 边 2+0 / 非 M 边 1+1 ✓，"两条 B 边至多共享一个端点"用于步(5) 的 P_x 无交并 ✓；(2) 步(7) 闭合——三边两两相邻在简单图中只能共点成星或成三角形，B 二部排除三角形，星情形每点至少缺一对 ✓；(3) 步(2) m=2 早退（3 个互异三角形宿主不存在）✓，且 n ≥ 5 ∧ 3|n ⟹ m ≥ 2 ✓；(4) 步(3) 双射完整：u≠v ⟹ e_u≠e_v（否则 |τ∩σ| ≥ 2）✓、|E(B)| = n = 3m = 3|V(B)|/2 ✓；(5) 定理 4 情形 2a **无循环论证**——步(2)(3) 只用"两个边不交三角形因子之并"（E(S)∩E(T)=∅ 与两因子支撑性即可），不触及引理 2 的反设 ✓；(6) 记账 ⌊(n−4)/3⌋ = m−2、情形 1 得 n−3、情形 2a/2b 得 (m−1)+(m−1)+m = 3m−2，**无 off-by-one** ✓；(7) 定理 5 三分穷尽（3∤n ⟹ 无三角形因子因 3|3·#tri；3|n 分有无三角形因子）✓，n ≥ 9 边界（6-正则 ⟹ n ≥ 7）✓；(8) 推论 6 两分支覆盖完整（n≡0 时 n ≥ 9；3∤n 时 3⌊n/3⌋ ≤ n−1）✓；(9) 注记 (d) 依赖表述与 `lane_05_delta6.md` 推论 A′ 逐字相符（"even+Δ≤6 ⟹ ce ≤ n−1 ⟺ 6-正则 ∧ n ≡ 0 (mod 3)"），且如实披露"依赖内部报告" ✓。

R2【Φ/翻折构造独立实现 + 全参数扫描】自写（bitmask 版）：对每个标记 3-正则二部 B（s ≤ 5）、每个完美匹配（Kuhn）、每个定向，验证 Φ(σ)、Φ(−σ) 为划分 E(L(B)) 的无三角形 2-因子：
- s=3：48 组合、零违反；s=4：3,456、零违反；**s=5：829,440、零违反**（35.0s）；合计 832,944 组合零反例。
- 顺带复现四稿 §7.3 的观测："#comp(Φ(σ)) = #comp(Φ(−σ))" 在 s≤4 全 3,504 例 + s=5 抽样 8,265 例**全部相等**（仅记录，未证）。
- 命令：`/opt/homebrew/Caskroom/miniconda/base/bin/python3 /tmp/verif/ver_phi_B.py`、`run_s5.py`。

R3【n=9 危险类完备重跑】自写枚举：9 点集划成 3 个三元组 = 280 个三角形因子 ✓；边不交**有序对 10,080** ✓；去重后**不同图 5,040** ✓；对全部 5,040 个 4-正则图，用 R2 的 Φ 构造（每个图都跑遍其匹配与定向）验证存在无三角形 2-因子 → **"所有 2-因子皆三角形之并"的 9 点图不存在**（引理 2 在 n=9 上完备成立；数字与 `verify_round2_proof.md:50` 一致）。命令：`python3 /tmp/verif/ver_phi.py A`（3.8s）。

R4【计数全面复算】
- 标记 3-正则二部 B：s=3,4,5,6 = **1 / 24 / 2,040 / 297,200**（回溯枚举 + 列和状态 DP 两法一致）→ 299,265 ✓ 与四稿/日志 `sweep_star_B_exh6.log` 一致。
- 6-正则 n=9：20,160 + 5,040 + 4,536 + 280 = **30,016** ✓（按 2-因子补图四类型手算并程序复核）。
- 6-正则 n=10/11/12 同构类：`geng -d3 -D3 10 | wc -l = 21`、`-d4 -D4 11 = 266`、`-d5 -D5 12 = 7849` **本轮亲自跑出** ✓（连通 19/265/7848 + 不连通 2/1/1 ✓）。
- 4-正则 n ≤ 8：1 + 15 + 465 + 19,355 = **19,836** ✓；n=8 的 19,355 用"geng 五类 + 暴力求 |Aut| 求轨道大小（840+2520+10080+2520+3360 = 19,320，加 K4∪K4 的 35）"独立交叉验证 ✓ → README 的 "all 4-regular graphs on n ≤ 8 vertices, 19,836" 属实 ✓。
- 组合数 829,440 / 832,944 / 1,183,920 的分解（见 F1）✓。

R5【18,279 份证书全量复核】**自写校验器**（与上游 h_verify.py 不同源：自己实现划分完整性、单边/简单圈判定、正则性、Φ/Φ−/F2 划分与无三角形）跑 `data/*.jsonl`：**18,281 条记录（含 C_s3_s0 的 2 条 smoke），失败 0** ✓。另核对记录内 `comps`/`comp_eq`/`npieces`/`bound` 字段与实测一致 ✓。
命令：`python3 /tmp/verif/ver_certs.py data/*.jsonl`。

R6【表内其余数字与数据的一致性】A_n12 npieces 直方图 {3:193,…,9:65,**10:5**} ✓、A_n10 {4:2,…,8:2} ✓、A_n11 {3:15,…,8:10} ✓、B 段 max 11/12/13/13 ✓ —— 与 `harden_numeric.md §1.2/§2` 逐格一致；8,000+2,100 条记录的 npieces **全部 ≤ bound** ✓。

R7【ce=3 的独立见证】n=9 四个同构类各取代表（K_9 减四类 2-因子），自写搜索给出 3 个边不交 Hamilton 圈分解 → ce ≤ 3，加平凡下界（27 边/每条 ≤ 9 边）得 **ce = 3** ✓（4/4 类）；n=10 用 `extra_n10_ce3_certs.jsonl` 的 21 条 3 件证书经 R5 校验（有效分解）+ 平凡下界（30 边/每件 ≤ 10 边）→ **21/21 类 ce = 3** ✓（与双引擎结论一致，但我未复算 MILP/LP）。

R8【复现性与负对照】`run_d1/d2/d3` 三份 A 段证书 `shasum` **各自唯一哈希**（逐字节一致）✓；摘要 JSON 删去 `elapsed_s` 后三遍相同 ✓（自写比较）；`logs/verify_negative_control.log` = "注入 5 条、检出 5 条、PASS" ✓。

R9【命令可运行性实测】见 F4（三次实跑记录）。

---

## 攻过但未发现问题的方向（诚实清单）

1. **整套证明的数学**：无洞、无循环论证、无 off-by-one、无边界遗漏（引理 1/2、命题 3、推论 3.1、定理 4 情形 1/2a/2b、定理 5 三分、推论 6 两分支、注记 a–f 全部手推一遍）。特别检查了任务点名的三处高危：步(6) 度数计数、步(7) 无三角形闭合、情形 2a 引用步(2)(3) 的独立性——均成立。
2. **过度声称**：KS95 降级后在英文页落实到位（"no novelty for the existence statement" ✓）；"no precedent" 有 "To the best of our knowledge + 检索出处" 缓冲 ✓；paywall/未读全文的证据等级标注**确实出现在结果页**（README:66）与仓库 README:45 ✓；AAFJLS 2004 与 Hartvigsen 2024 的定位与 `bh97_landscape.md §2.4/§3.3` 一致 ✓；BH97 的"判定算法、无 YES 刻画、作者自登 NP-完全猜想"转述与 Plummer p.812 逐字一致，且**避开了 F-B 的 (a) 项误译** ✓。
3. **残余风险的如实出现**："L(B) s ≥ 7 由证明承担"在 README:56 明确写出且口径准确（s ≤ 6 穷举 = 12 点 B / 18 点 L(B)）✓。
4. **数字**：README 验证表除 F1 那一个标签外，其余每个数字（21/266/7,849；19,836+5,040；30,016 与 ce=3；8,000；299,265+2,100；18,279；负对照 5/5）都经独立重算或全量复核成立 ✓。四稿 §4 登记的 "3,504 之差待核" 本轮**已解**：口径差异，两个数都对（F1）。
5. **ΣΦ 构造的正确性**：自写实现全参数零反例（含 s=5 满组合），且"任一定向"这一全称量词在证明与数值两侧都站得住 ✓。
6. **仓库双入口结构**：远端仓库确有 `article/`、`campaign/`、`notes/`、`paper/`、`2509.01901_src/`，故 `repo-publish/README.md` 顶层的 `article/article_draft_zh.md` 等链接在**合并到仓库根后**可解析 ✓（本地 `repo-publish/` 是暂存目录，现在点会 404 属预期，不算发现）；三色审查数字 "11 绿 / 11 黄 / 1 红" 与 `PREPUB_REVIEW.md:9` 一致 ✓；"64 路"说法与仓库既存描述一致（但目录清单用法见 F11）。

## 未覆盖面（本轮预算内的 INCONCLUSIVE 项）

- 未复算 n=10 的 MILP/LP（HiGHS）与 n=12 的 BB 引擎本身；我只复核了它们产出的证书合法性 + 平凡下界。
- 未重跑 `h_A_enum.py --n 10/11/12`（需 geng 生成数据 + exact 段耗时 ~150s，可从 count 与 geng 类数交叉确认的部分已确认）。
- 未获取 BH97/KS95 全文（付费墙；本轮无网络检索预算），故"证据等级"只审标注是否与内部记录一致，未独立验证文献内容。
- `paper/`（15+ 定理）与 `notes/` 的对外描述只做了存在性与数字抽检（paper/README 的定理清单存在 ✓），未逐条复核其内容。
- 未审计 `article/article_draft_zh.md` 与 `知乎发布版.md` 的正文（不在本次对象内）。

## 放行范围（若上游按发现清单修完）

- **数学内容整体放行**：proof.md 的定理、证明与注记，results README 的结果陈述与"我们声称/不声称"段落，经本轮独立重算与重推后维持原判可用（F6–F8、F13 属表述，不动数学）。
- **验证表数字放行**：除 F1 一处标签外全部数字成立；修 F1 时建议顺便把 `email_final.txt:9` 与四稿 §4 行 5 的"待核"注记一并改正（同一个口径问题）。
- **发布放行条件**：F5 的推送顺序（四稿 + harden_round2 + results/）完成后再对外发信。

*审查人：Verifier（本轮独立实现；脚本 /tmp/verif/{ver_B.py, ver_phi.py, ver_phi_B.py, run_s5.py, ver_count6.py, ver_certs.py, ver_counts2.py, n9_ce3.py}）*
