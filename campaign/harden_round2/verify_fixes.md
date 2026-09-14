# verify_fixes —— R2-01 四稿（`campaign/r2_01_aabc25_struct.md`，2026-09-14 第二轮加固版）修订复核

审查人：Verifier（第二轮审查员本人，复用同一独立实现与判定标准）。
日期：2026-09-14。立场：只读复核；默认"改动可能引入新错/漏改旧错"，逐条查证后才放行。
复核对象：四稿 + `harden_round2/harden_numeric.md` + `email_final.txt`（21 行）+ 仓库同步状态。
方法学提示：本轮拿到的**最强证据是 diff**——GitHub 仓库 `campaign/r2_01_aabc25_struct.md` 仍是三稿（`2026-09-12 三稿·收尾版`，34,195 字节），我把它拉下来与本地四稿做了逐行 diff（`/tmp/r2_diff.txt`，146 行、9 个 hunk），因此"哪些行改了、哪些行没改"是**机器比对**结论，不依赖记忆。

---

## 判定

**PASS（四稿正文）** —— F1–F6 全部真实修好；F5 的新证明我重推一遍**正确**；数学内容除 F5 补全与 F1 表述修正外**逐字节零改动**（diff 证明）；§4 行 12 的数字与 `harden_numeric.md` 抽查**全中**；无残留自相矛盾（仅 3 处措辞残留，MINOR）。

**但邮件有 1 条 MAJOR（发送前必须处置）**：`email_final.txt` 声称 "The complete proof, verification scripts, and review records are available at ⟨repo⟩"，而该仓库**当前仍是不含本轮修订的三稿 + 完全没有 `harden_round2/`**（见 F-A）。这是事实性不实陈述（不是数学问题），作者一点开就会看到含已修错误的旧稿与缺失的验证材料。

---

## 发现清单

### F-A【MAJOR · `email_final.txt:13-14`（+ `:9` 的验证声称）】仓库内容与邮件"available at"不匹配（发送前必须修）

**证据（两路独立）**：
1. GitHub contents API `repos/xiaoyuyu6420/erdos184-ai-campaign/contents/campaign`（30 条）= CAMPAIGN.md、MERGE_1.md、PREPUB_REVIEW.md、article_draft_zh.md、lane02..lane11_scripts、lane_01..lane_12.md、prepub_independent_check.py、`r2_01_aabc25_struct.md`、`r2_01_scripts`、`r2_02_d3exact.md`、`r2_02_scripts`、`verify_r2_01.md`。**没有 `harden_round2/`**（即无 `harden_numeric.md`、`verify_round2_proof.md`、`bh97_landscape.md`、`h_*.py`、`data/`、`logs/`）。
2. `raw.githubusercontent.com/.../campaign/r2_01_aabc25_struct.md` 头部 = 「**2026-09-12 三稿·收尾版**」，且其第 90 行仍是本次 Review 要求修掉的假等式 `和 ≤ 3⌊n/3⌋ = n−1`（本轮 F1）。

**后果**：邮件第 9 行的验证声称（10/11/12 同构类全穷举、8,000 随机、18,279 证书、负对照）与第 11 行"含验证方法论与内部审查纠错清单的协作声明"所指向的材料，在邮件给出的链接处**不可得**；而可得的 `r2_01_aabc25_struct.md` 是**含已知错误、且新颖性表述已被自己推翻**的旧版本（对收件人正是最不该看到的版本）。
**影响**：不触及数学结论，但直接影响邮件的可信度与作者的第一印象；属"发送前置条件"。
**建议**：发送前推送四稿 + 整个 `harden_round2/`（脚本、data、logs、三份报告），并确认 README/协作声明已覆盖 R2-01（现有 README 叙述的是更早的 Act-1 阶段，需确认它不落后于四稿）。

### F-B【MINOR · 四稿 `:187`（§7.1）与 `:204`（§8[BH97]）】Conjecture 6.10 的转述漏了 (a) 的 "n-factors"

四稿写作「**Conjecture 6.10**：2n-正则（n ≥ 3）分解为**两个 / n 个无三角形 2-因子**的识别问题猜想为 NP-完全」。Plummer 2007 p.812 原文（我独立下载镜像 PDF 核对，31 页本第 22 页 = 印刷页 812）：

> "Conjecture 6.10. The problems of (a) recognizing which 2n-regular graphs decompose into **two triangle-free n-factors**, and (b) recognizing which 2n-regular graphs decompose into n triangle-free 2-factors are both NP-complete for all n ⩾ 3."

即 (a) 是 **two triangle-free n-factors**（不是"两个 2-因子"）。有意思的是：`harden_round2/bh97_landscape.md §1.2(b)` **引对了**（逐字），是四稿摘引时走样。
**影响**：不改变"BH97 是特例性判定算法、不含 YES 刻画"的结论（该结论由 Theorem 6.9 逐字 + 无施引转述判据支撑 ✓，我已独立核实），但属于可被审稿人抓到的引文不精确。
**修复**：按 landscape 的逐字版引用（把 (a)(b) 并列写出）。

### F-C【MINOR · `email_final.txt:9`】"exhaustive checks over all 1,183,920 parameter combinations" 措辞与数字精度

两处小问题：① 1,183,920 中 s=6 段是**300 个 B 的抽样**（不是全部 297,200 个 B 的全组合），"over **all** ... combinations" 对 s=6 不成立；② 我第二轮独立复算 s≤5 的"全部匹配 × 全部 2^s 定向" = **829,440**，与一轮报告的 832,944 差 3,504（不是 32 的整数倍，疑为一轮实现的匹配计数偏差）。数字本身不承载数学结论，但邮件给出的是精确数。
**修复建议**：改为 "over 0.83M (M,σ) combinations exhaustively for s ≤ 5 plus sampling at s = 6" 或干脆 "over a million parameter combinations"。

### F-D【MINOR · 四稿 `:104`（§4 标题）与 `:123`（行 12）】

① §4 标题仍写「三稿已收尾」（四稿中的 stale 描述）；② 行 12「② 21/21 类 ce = 3，**slack = 5**」未标基准——slack=5 是相对 n−2 = 8（任务书数字），而**本定理对 n=10 的界是 n−1 = 9，slack 应为 6**（`harden_numeric.md` §0/§1.3 两者都写了，四稿摘引时只留了一个）。行 12 前半句「≤ 各自界（n−1/n−1/n−2）」已正确区分 ✓，只需把 slack 的基准补全。

### F-E【MINOR · 四稿 `:67`（命题 6 标题）与 `:5`（摘要点 2）】

命题 6 标题仍带「（**本稿新增**）」、摘要仍写「**本次新增**命题 6」，与同一句/同页的 [KS95] 降级并存。虽然按字面是"本稿相对上一版本新增"的变更记录语，但在已声明"不主张其首创性"的语境里易被读成新颖性声称。
**修复**：改为「（本稿新补的显式构造版）」之类的中性措辞。

### F-F【MINOR · 四稿 `:117`（§4 行 6）】n−2 证据的出处指向过粗

行 6 写「n−2 的强制断言由第二轮独立实现补上——n=9 全量 30,016 图件数全部 ≤ 7 = n−2，零失败（见 `harden_round2/`；另经第二轮审查员独立实现复算一致）」。事实核对：`harden_round2` 的数值三段（A/B/C）最小 n = 10，**没有测 n=9**；n=9 的 ≤ n−2 证据只存在于 `harden_round2/verify_round2_proof.md`（第二轮审查员实现）。措辞"由第二轮独立实现补上"＋"另经第二轮审查员独立实现复算"读起来像两套实现，实际只有一套。
**修复**：改成「见 `harden_round2/verify_round2_proof.md`（第二轮审查员独立实现）；harden_numeric.md 的 A/B/C 段未覆盖 n=9」。

---

## (a) F1–F6 逐条核验：**全部真实修好**（含 F5 新证明重推）

| # | 位置（四稿行号） | 证据 | 结论 |
|---|---|---|---|
| F1 | `:96` 系 4 | 已改为「和 ≤ 3⌊n/3⌋ ≤ n−1（n ≡ 1 时取等；n ≡ 2 时 3⌊n/3⌋ = n−2 更强）」 | **修好且写得更强** ✓（diff 确认） |
| F2 | `:117` 行 6 | 明确「脚本内自动断言为 ≤ n−1（`r2_core.py:509`），n−2 的强制断言由第二轮独立实现补上」；我在第二轮的原报告里确实做了 n=9 全量 30,016 图 ≤ 7 的独立复算 | **修好** ✓（仅出处指向需细化，见 F-F） |
| F3 | `:141-143` Lean | `exists_two_factor_with_long_cycle` 已加 `(hcard : 5 ≤ Fintype.card V)` | **修好** ✓（空图反例已排除） |
| F4 | `:33` + `:203` | 新增归因段：「本归约的原型是 AABC25 论文自述的观察——main.tex:316–318 …… 本稿未将其声称为新」；§8 的 [AABC25] 条目也补了"归约原型见 main.tex:316–318" | **修好** ✓ |
| F5 | `:90-94` 定理 3 证明 | 由一句指针扩为三分解决策；**我重推一遍，见下** | **修好且证明正确** ✓ |
| F6 | `:114` 行 3 | 明确「64 = `pipeline_star` 路由到 Φ 构造的次数；此外枚举对**每个 B** 均执行 `phi_forced_check`（299,265 次全覆盖，非仅 64 例）」。我第一轮读过 `sweep_star_B.py`：`run_exhaustive` 里 `phi_forced_check(B_adj, ...)` 对每个 B 都调用 ✓，且日志 `sweep_star_B_exh6.log` 的 `{first-factor: 299201, phi-construction: 64}` 正是 `pipeline_star` 的 `how` 统计 ✓ | **修好** ✓（两个数字各归其位） |

### F5 新证明重推（定理 3 三分解决策）

三个情形：**A** n ≢ 0 (mod 3)；**B** n ≡ 0 (mod 3) 且 G 无三角形因子；**B′** n ≡ 0 (mod 3) 且 G 有三角形因子 S。逐条：

- **穷尽性**：A ∪ B ∪ B′ 覆盖所有 6-正则图（n 是否 ≡ 0 mod 3；≡ 0 时 G 有无三角形因子）✓。
- **情形 A**：「三角形因子存在 ⟹ n = 3·(三角形数) ≡ 0；故 3 ∤ n 时 G 无三角形因子」——三角形因子是支撑 2-因子、分量全为三角形，故其点数必为 3 的倍数 ✓。于是 引理 0（k=3，需 G 6-正则 ✓）给的任一 2-因子分解 G = F ⊔ F₁ ⊔ F₂ 中，F 非三角形因子；2-因子的分量是圈，简单图中圈长 ≥ 3，故 F 有长 ≥ 4 的圈 ⟹ 含 ≥4 点分量 ✓。达标 ✓。
- **情形 B**：G 无三角形因子 ⟹ 引理 0 的三个因子**都**非三角形因子 ⟹ 各含 ≥4 点分量 ✓（"同上"指理由同构：任一因子非三角形因子即达标，这里三个都达标）。达标 ✓。
- **情形 B′**（任务书点名要重推的三处）：
  - `H := G − E(S)` 的 **4-正则性**：G 6-正则、S 是支撑 2-因子（每点度 2），删边后每点度 6−2 = 4 ✓；H 是 G 的子图 ⟹ 支撑、简单 ✓。
  - **|V(H)| ≥ 5**：|V(H)| = n；n ≡ 0 (mod 3) 且 6-正则 ⟹ n ≥ 7 且 n ≡ 0 ⟹ n ≥ 9 ≥ 5 ✓（H 为空、为小图的风险被 n ≥ 9 排除；这也正是 F3 要给引理 1 补的那条前提 ✓）。
  - **S′ 与 T 的合法性**：引理 1（已含 |V| ≥ 5 ✓）给出 H 的 2-因子 S′，含长 ≥ 4 的圈 ⟹ 含 ≥4 点分量 ✓；T := H − E(S′)：H 4-正则减去一个支撑 2-因子 ⟹ 每点度 2 ⟹ T 是 G 的支撑 2-因子 ✓。
  - **三分解**：E(S) ⊔ [E(S′) ⊔ E(T)] = E(S) ⊔ E(H) = E(G) ✓（S′、T 边不交且并 = E(H) ✓）；三个因子都支撑 G、都是 2-正则 ✓；含 ≥4 点分量者 = S′ ✓。达标 ✓。
- 结论：**覆盖 Conjecture 原文（逐字见 main.tex:792–794 ✓）的"三 2-因子分解 + 其一含 ≥4 点分量"**，且论证只用到 引理 0、引理 1 与整除性——与旧指针版本相比**没有削弱或加强任何声明**（旧版把整件事转交给 §1 注，而 §1 注的两种情形与之等价 ✓）。

---

## (b) 数学内容是否除 F5 补全与 F1 表述外零改动：**是**（diff 证明）

以仓库三稿为基线，`diff -u` 只有 9 个 hunk，涉及的行区间与内容为：

| hunk | 行区间（三稿→四稿） | 内容 | 是否声明过 |
|---|---|---|---|
| 1 | 1–11 → 1–12 | 标题（三稿→四稿）、摘要点 2（KS95 降级）、点 4（F6 澄清）、新增 4b、点 5（v2 + 降级） | ✓ 已声明 |
| 2 | 29–34 → 30–37 | 归约 1 后新增归因段（F4） | ✓ |
| 3 | 85–93 → 88–99 | 定理 3 证明（F5）+ 系 4（F1） | ✓ |
| 4 | 105–122 → 111–131 | §4 行 3（F6）、行 6（F2）、新增行 12、新增残余风险边界段 | ✓ |
| 5 | 129–137 → 138–146 | Lean 引理 1 加 `hcard`（F3） | ✓ |
| 6 | 168–187 → 177–197 | §6 第 1 条（KS95 定位）、§7.1 全节重写、§7.2 版本更正、§7.3(+) Hartvigsen24 | ✓ |
| 7 | 190–203 → 200–215 | §8 五条引用（[AABC25] v2、[BH97] 综述级、新增 [KS95]、EJC 结案、新增 [Hartvigsen24]） | ✓ |
| 8 | 208–213 → 220–226 | §9 新增 `harden_round2/` 索引 | ✓ |
| 9 | 216–218 → 229–236 | §10 新增第 6 条 | ✓ |

**未被任何 hunk 触及**（= 逐字节相同）的数学正文：§0 全文、引理 0（陈述+证明）、归约 1 证明、归约 2（陈述+证明）、§1 注、**引理 1 的陈述与 (1)–(8) 全部证明**、推论 1.1、**命题 6 的陈述与三段证明**、推论 6.1、**定理 2′ 的陈述与情形 1/2/2a/2b 全部记账**、定理 2、系 5、注记 A、注记 B、§5 其余 4 个 Lean 目标。→ **(b) 成立** ✓。这也间接说明：我自己第二轮审查（含 n=9 全量、命题 6 全参数、引理 1 危险类完备）**对四稿仍然有效**，无需重做。

---

## (c) 残留旧声称扫描：**无自相矛盾**（3 处措辞残留已列为 MINOR）

| 扫描项 | 结果 |
|---|---|
| 系 4 假等式 `= n−1` | **已修** ✓（`:96`） |
| "v1 残留" | 仅剩正确历史语境：`:192`「已出 v2（2025-09-07）……数学内容与 v1 相同」、`:203`「v1 (2025-09-02)、v2 (2025-09-07)」 ✓ 无"仍为 v1"类陈述 |
| "仍无 v2 / 检索时仍为 v1" | **已删** ✓（三稿的 §7.2 该句与 §8「本次联网复核仍为 v1」均在 diff 中被替换） |
| 命题 6 = 全新存在性结果 | **已同步降级** ✓：摘要点 2（"在断言上重合……不主张其首创性"）、摘要点 5（"降级为 [KS95] 观察的显式构造版"）、§6.1 第 1 条（"按 [KS95] 观察的显式构造版定位"）、§7.1（整节）、§8[KS95] 条目（"命题 6 降级依据"）四处一致。**仅标题 `:67` 的"（本稿新增）"与摘要 `:5`"本次新增"是变更记录语残留**（F-E） |
| "全新数学"/"未见已有表述"/"无条件存在性定理" | 无残留 ✓：`:9` 是**否定句**（"不声称「全新数学」"）、`:204` 是**对 BH97 的正确刻画**（"是判定算法而非无条件存在性定理"）、`:231` 是第 5 条变更记录里对三稿历史的引用 ✓ |
| §4 陈旧描述 | 仅 `:104` 标题"三稿已收尾"（F-D）✓；`:108`/`:116` 的"（三稿审查修订）"是**正确的历史标注** ✓ |
| [BH97] 全文状态 | 一致 ✓：摘要/§7.1/§8 三处都说"全文仍未获取 + 综述级转述为据" ✓（我已独立核对 Plummer 原文，见下） |

---

## (d) §4 行 12 数字 vs `harden_numeric.md`：**抽查全中**

| 行 12 声称 | 我核到的证据 | 结论 |
|---|---|---|
| n=10/11/12 = **21 / 266 / 7,849 类** | `data/A_n10.jsonl.summary.json`（classes 21）、`A_n11`（266）、`A_n12`（7849）；geng 命令与规模见 `harden_numeric.md` §1.1 | ✓ |
| 件数 max **8 / 8 / 10** ≤ 各自界（n−1/n−1/n−2），零违反 | `A_n10` max_pieces 8 / `A_n11` 8 / `A_n12` 10；三个 `.violations` 均 0 字节 | ✓ |
| n=12 **5 类**件数恰 = n−2 = 10，其**精确 ce = 3** | `data/extra_n12_tight.json`：n12#1335/#3974/#4472/#5130/#5482，各 `npieces_construct: 10, ce_bb: 3` | ✓ |
| n=10 全 21 类精确 ce = 3（BB + MILP 双引擎一致） | `A_n10` summary：`exact_ce_hist {3: 21}`、`exact_milp_fail 0`、每行 `ce_bb = ce_milp = 3`（LP 下界 ≈3.0000000） | ✓ |
| 随机 n=15/18/21/24 × **2,000**（共 8,000） | `data/B_summary.json`：四档各 2000、fail 0、max_pieces **11/12/13/13** = 行 12 的"max 件数 11/12/13/13"、界 13/16/19/22 ✓ | ✓ |
| 对抗族 s=7 ×500 B×3 / s=8 ×200 B×3 = **2,100** | `C_s7_summary.json` records_ok 1500、`C_s8_summary.json` 600，B_fail 0，`comp_eq_all: true` | ✓ |
| **18,279** 份证书经独立校验器复核零失败 | `harden_numeric.md` §0：A 8136 + B 8000 + C 2100 + 额外 43 = 18,279 ✓（A = 21+266+7849 = 8136 ✓；额外 43 = 21 + 22 ✓）；`logs/verify_A_n11_n12.log`/`verify_B.log`/`verify_C.log` 均 `"failures": []` | ✓ |
| 校验器负对照 **5/5** 注入错误全检出 | `logs/verify_negative_control.log`：「负对照注入错误 5 条，检出失败 5 条 …… **PASS（全部检出）**」 | ✓ |
| 三遍重跑证书 sha256 逐字节一致 | `logs/D_compare.log`：A_n10/A_n11/A_n12 证书「逐字节一致」；摘要仅墙钟字段不同；`harden_numeric.md` §4 并如实记录首轮 shasum 比较的假报警与定位 | ✓ |

唯一需要改的是行 12 的"slack = 5"缺基准说明（见 F-D）；`harden_numeric.md` §0 自己已如实标注了"任务书界 vs 定理界"的差异，四稿行 12 前半句也没有混淆 ✓。

---

## (e) `email_final.txt` 逐句核对（21 行）

| 邮件句子 | 核对 | 结论 |
|---|---|---|
| `:3` "Your proof that every graph of maximum degree at most 4 can be decomposed into at most n−1 cycles and edges" | `main.tex:167-169` Thm（Δ≤4 ⟹ ce ≤ n−1）✓ | 准确 ✓ |
| `:5` "we can prove Conjecture 6.2 …… verbatim" | 四稿定理 3 + 我重推 F5 证明 ✓；编号 6.2 我用 `main.tex` 前导（`\newtheorem{theorem}{Theorem}[section]` 共享计数器、§6 = Future Work）复算：781 行 problem = 6.1、792 行 conjecture = 6.2 ✓ | 准确 ✓ |
| `:5` "every 6-regular graph on n vertices with n ≡ 0 (mod 3) admits a decomposition into at most n−2 …… (hence at most n−1 for all 6-regular graphs)" | 四稿定理 2′ + 系 4 ✓（与四稿一致，未超范围） | 准确 ✓ |
| `:7` 结构归约 + Φ(M) ⊔ Φ(−M) 逐点划分 | 四稿引理 1 步(2)(3) + 命题 6 ✓ | 准确 ✓ |
| `:7` "This last step is an explicit, self-contained form of the line-graph observation of Kouider and Sabidussi …… we make no novelty claim for that existence statement itself." | 与四稿 §7.1/摘要点 2 的降级一致 ✓（措辞甚至更保守） | 准确 ✓ |
| `:9` "exhaustive checks over all 1,183,920 parameter combinations" | 见 **F-C**（数含 s=6 抽样；我的复算 829,440 ≠ 一轮 832,944） | **需改措辞** |
| `:9` "exact ce computations for all 30,016 six-regular graphs on 9 vertices" | 我在第二轮独立验证过：n=9 全量 30,016 图 ce = 3（完备 Hamilton 圈配对搜索，四类代表均 3 个边不交 Hamilton 圈；ce ≥ 3 由 27 边/圈 ≤ 9 边）✓ | 准确 ✓ |
| `:9` "exhaustive verification over all isomorphism classes …… (21, 266 and 7,849 classes, with exact ce determined for every 10-vertex class)" | 见 (d) ✓ | 准确 ✓ |
| `:9` "adversarial family sweeps (299,265 instances) plus 8,000 random instances on up to 24 vertices" | 299,265 = 上游对抗族 ✓（我第一轮核过计数）；8,000 ✓（B_summary） | 准确 ✓ |
| `:9` "two independent verification passes over the argument, the code and the literature" | 一轮 `verify_r2_01.md` + 二轮 `verify_round2_proof.md` ✓；文献复核 = `bh97_landscape.md` ✓（加上 AI 协作声明 `:11` 的披露，"two passes"可读懂） | 准确 ✓ |
| `:11` "assistance of an orchestrated AI system under my direction …… collaboration statement …… included in the repository" | 仓库 README 确有 AI 协作声明摘要（我的抓取显示"64 路 AI 子代理"、三色审查、12 处纠错）✓；但**需确认该声明已覆盖 R2-01 本轮的 F1–F6 与 KS95 降级**（现有叙述看起来是更早阶段的口径） | 基本符合，建议确认 ✓ |
| `:13-14` "The complete proof, verification scripts, and review records are available at ⟨repo⟩" | **F-A：当前不成立**（仓库是三稿 + 无 harden_round2） | **MAJOR，发送前必须修** |
| `:16` "Nothing has been submitted for publication." | 与战役规则一致 ✓ | 准确 ✓ |

---

## 独立复核记录（本轮新做的核对，命令可复算）

| 核对 | 命令/方法 | 结果 |
|---|---|---|
| 四稿 vs 三稿逐行 diff | `curl raw.githubusercontent.com/.../campaign/r2_01_aabc25_struct.md` → `diff -u` | 146 行 / 9 hunk；数学正文零改动（见 (b)） |
| 仓库内容是否含加固材料 | GitHub contents API `.../contents/campaign` + HTML tree 页（两路） | 无 `harden_round2/`、无 `verify_round2_proof.md`/`bh97_landscape.md`（F-A） |
| arXiv 版本史 | `curl arxiv.org/abs/2509.01901`（含 v1/v2 两版页） | **v1 = 2025-09-02、v2 = 2025-09-07** ✓ 与四稿一致；v2 摘要确为 Erdős–Gallai 框架 ✓ |
| 本地 main.tex 与 v2 逐字节相同 | 下载 `arxiv.org/e-print/2509.01901v2` 解包后 `md5`+`diff` | 两侧 md5 = `03cb993baf01cb18392dc226e98b3475`，`diff -q` 无差异 ⟹ **行号引用（781–794、316–318）继续有效** ✓ |
| Plummer 2007 Theorem 6.9 / Conjecture 6.10 原文 | 下载 `ftp.eecs.umich.edu/~pettie/matching/Plummer-f-factor-survey.pdf`（31 页）→ pypdf 抽文本 | Theorem 6.9 与四稿引文**逐字一致** ✓；Conjecture 6.10 存在但四稿转述走样（F-B） |
| EJC 2026 综述"无覆盖"结案 | 下载 `combinatorics.org/.../v33i2p40/pdf`（19 页）→ 关键词计数 | van den Heuvel–Toft, EJC 33(2) #P2.40（Published 2026-05-22）；全文 **0 次**出现 Bertram/Horák/Kouider/triangle-free/4-regular/6-regular/ce ⟹ 结案正确 ✓ |
| §4 行 12 数字全量抽查 | 读 `data/*.jsonl.summary.json`、`B_summary.json`、`C_s*_summary.json`、`extra_n12_tight.json`、`logs/verify_*`、`logs/D_compare.log`、`logs/verify_negative_control.log` | 全中（见 (d)） ✓ |
| 证书负对照"不是空转" | 读 `logs/verify_negative_control.log` | 5 类注入错误 5/5 检出 ✓ |

**未做/未能核实（如实声明）**：
1. 未重跑 `harden_round2/` 的脚本（只读摘要/日志 + 抽查数据文件；数据文件与日志自洽 ✓）——若需"重跑级"确认，可调用 `run_D_repro.sh`（其自身已提供三遍 sha256 一致性证据）。
2. **KS95 摘要**未能独立复核（出版商页反爬，我未取到 PDF/tldr）；四稿/landscape 已如实标注为"出版商元数据级证据（2 源 + S2）" ✓ 且该降级方向保守（放弃而非主张新颖性），风险低。
3. [Hartvigsen24] 预印本我只确认了四稿/landscape 的转述方式，未独立下载核对（仅作 (+) 的对照定位，非结论性引用）。
4. "v1/v2 被引均为 0"未独立复核（监控性陈述，低风险）。

---

## 放行范围

**可放行（干净）**：
- 四稿全部数学内容（F5 新证明经重推正确；其余与三稿逐字节相同，我在第二轮对三稿的独立复算结论**继续有效**）；
- F1–F6 的处置（除 F-F 的出处指向建议细化）；
- §4 行 12 的全部数字与 `harden_numeric.md`（抽查一致、负对照有效、复现性有记录）；
- 摘要点 2/5、§6.1、§7.1、§8 的 KS95 降级链（四处一致，无残留强声称）；
- 事实更正与文献升级（v2 逐字节相同我已独立验证；Plummer Theorem 6.9 逐字我已独立验证；EJC"无覆盖"结案我已独立验证）。

**发送/发布前处置（按优先级）**：
1. 【F-A · MAJOR】推送四稿 + 整个 `harden_round2/` 到邮件给出的仓库；确认 README/协作声明不落后；否则把邮件那句"available at"改为实际可得的位置，或先推后发。
2. 【F-B · MINOR】§7.1/§8 的 Conjecture 6.10 按逐字引用改写（(a) two triangle-free **n**-factors）。
3. 【F-C · MINOR】邮件 `:9` 的 1,183,920 措辞放宽（或写明 s ≤ 5 全组合 + s = 6 抽样）。
4. 【F-D/F-E/F-F · MINOR】§4 标题"三稿已收尾"、行 12 的 slack 基准、命题 6 标题的"（本稿新增）"、行 6 的证据文件指向。
