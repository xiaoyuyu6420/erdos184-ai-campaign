# paper/ — 英文论文骨架（draft_en.tex）

**状态：骨架阶段（statements 终稿 + 证明概要；完整证明不在本文内）。**

- 论文文件：`draft_en.tex`（amsart，英文）。编译：`pdflatex draft_en.tex`（依赖 `amssymb/amsmath/amsthm/geometry/hyperref`）。
- 蓝线原则：**只收录 PREPUB_REVIEW 放行内容**（GREEN G1–G11 + 已修复/降级处置后的 YELLOW 项）；RED 项（R1）已撤回且不再出现，其"教训"以正确方向写入 §9（Proposition 9.2）。
- 完整证明全部存于 `../campaign/` 与 `../notes/`（逐定理出处见下表），计划组装为论文附录 A–D。

## 一、定理清单与证明状态

| 论文编号 | 内容 | 状态 | 完整证明出处（campaign 归档） | 验证方式 |
|---|---|---|---|---|
| Thm 3.1 | ce(K_{2m})=2m−1、ce(K_{2m+1})=m | **已完整证明** | `campaign/lane_09_blocks.md` Thm G（记录在案的证明出处；lane_07 对偶数阶仅有上界+数值，论文未写成"双路独立证明"） | 下界逐行审；独立求解器 K₄–K₈ |
| Lem 2.2 / Thm 3.2 / Cor 3.3–3.4 / Prop 3.5 / Thm 3.6 | 块可加等式、恒等式、转移原理、超额可加、合并判据、仙人掌公式 | **已完整证明** | `campaign/lane_09_blocks.md` Thm A / Lem 1.6 / Cor B/C / Thm D / Thm E | 脚本 988 项 ALL PASS |
| Thm 4.1 | 外平面 ≤ n−1 | **已完整证明** | `notes/attack_planar.md` Thm A（A1–A3，含复核修补） | 前哨战审查通过 |
| Thm 4.2 | 欧拉平面 ≤ n−2 | **已完整证明** | `notes/attack_planar.md` Thm B | 同上 |
| Thm 4.3 | 欧拉极大平面 n−2 个面三角形（存在性） | **已完整证明** | `notes/attack_planar.md` Thm C（"最小性"已撤） | 同上 |
| Thm 4.4 | 无桥 cubic ≤ 5n/6；含桥 ≤ n−1 | **已完整证明** | `notes/attack_planar.md` Thm D/D′（+ lane_06 L6.4 曲面无关注记） | 同上 |
| Thm 4.5 | 欧拉环面 ≤ n−1（三角剖分分支 ≤ n−2） | **已完整证明** | `campaign/lane_06_genus.md` L6.3 | PREPUB G4 |
| Thm 4.6 / Cor 4.7 | 亏格界 5n/3+2g−8/3、欧拉 n+2g−4(−3)；欧拉平面三角剖分 ≤ n−4（n≥8）、n=7 不存在 | **已完整证明** | `campaign/lane_06_genus.md` L6.1/L6.2/L6.2′（**Y1 已修**：原计数论证作废，改用度列 (6¹,4⁶)+外平面矛盾论证） | PREPUB G4 + 蓝队修复 + 穷举 n≤7 |
| Cor 4.9 | 下界 f(g) ≥ ⌈(4g−4)/3⌉ | **已完整证明**（由 Thm 7.3 + Ringel 公式组装） | `campaign/lane_06_genus.md` L6.6 | Ringel 公式 g=2 窗口核对（G11） |
| Thm 5.1 / Cor 5.2 | Dirac 正则（D≥⌊n/2⌋，**n ≥ n₀**）⟹ ce ≤ n−1（三分情形） | **已完整证明**（条件于 CKLOT 已发表定理） | `campaign/lane_07_mindegree.md` Thm A（源码逐字核对 lines 282–290） | PREPUB G5；**n₀ 限定词强制**（Y7） |
| Thm 6.1 / Cor 6.2 | 反例 K₃∪K_{3,4}（n=7, Δ=6, ce=7=n） | **已完整证明** | `campaign/lane_05_delta6.md` Thm B | 四重验证（DP/分支定界/可行性穷举/独立实现 + 证书逐件） |
| Thm 6.3 | even+Δ≤6 ⟹ ce ≤ 3⌊n/3⌋；非 6-正则或 n≢0 (mod 3) 时 ≤ n−1 | **已完整证明** | `campaign/lane_05_delta6.md` Thm A（**Y11 措辞已修**：圈分量口径） | PREPUB G6 |
| Thm 6.5 | 一般 Δ≤6 ⟹ ce ≤ (m+2τ)/3 | **已完整证明** | `campaign/lane_05_delta6.md` Thm D | PREPUB G6 |
| Rem 6.6（危险区） | 非 even 的 ce ≤ n **未证** | 诚实缺口声明 | `campaign/lane_05_delta6.md` 引理 E | PREPUB 注意事项 6 |
| Rem 6.7 | K_{3,n−3} 机理（**n ≥ 7**；n=6 例外 ce=n−2） | **已完整证明** | `campaign/lane_05_delta6.md` 命题 H（**Y6 off-by-one 已修**） | 脚本 §4.1 表 |
| Thm 7.1 | 2-degenerate ⟹ ce ≤ n−c−s(G)，等号 iff 森林（K₄-minor-free） | **已完整证明** | `campaign/lane_08_degeneracy.md` T2 | 自包含归纳 + 725 例机器检验 |
| Thm 7.2 | d=3 ⟹ ce ≤ ⌊(5n−8)/3⌋（一般 d 公式） | **已完整证明** | `campaign/lane_08_degeneracy.md` T3a | 630 例零违反 |
| Thm 7.3 | ce(K_{3,q}) = ⌈4q/3⌉（全体 q≥2） | **已完整证明** | `campaign/lane_08_degeneracy.md` T3c（**Y5 算术笔误已修**：K_{3,2}=3 件） | 率引理 + q=6,7 精确搜索 |
| Conj 7.4（T3b） | d=3 上界 4/3 | **猜想**（630 例数值支持） | `campaign/lane_08_degeneracy.md` T3b | **Y4 已降级**：下界 4/3 已证、上界 4/3 开放、已证上界 5/3 |
| Thm 7.6 | 每个 d≥3 有 d-degenerate 反例族 ce>n−1（K_{3,7}；K_{3,q}+e 非二部；K_{5,11}；K_{2k+1,q}） | **已完整证明** | `campaign/lane_08_degeneracy.md` T4 | 双机器证书（3324 圈 / 794530 圈枚举） |
| Thm 8.1 | K_{s,t} 下界 | **已知结果重述**（无新颖性声称） | `notes/attack_bipartite.md` Thm 1.1 | 小值表精确命中 |
| Thm 8.2 / Cor 8.3 | ce(K₂∨K_{1,c−1})=c−1+⌈(c+2)/3⌉；f(n)≥n（n≥7） | **已完整证明** | `campaign/lane_03_constant.md` M2 / N.1（B 级抽查通过，G9） | c=2..8 双证书 |
| Prop 8.4 | 2-连通 4-正则 n≤8 ⟹ ce ≤ n/2−1 | **已完整证明**（限 n≤8） | `campaign/lane_04_delta5_savings.md` C2（G10）；n≥10 诚实标开放 | n=6 唯一类 + Dirac |
| Prop 9.1 | 不动点卡死 + 塔步条件版 log* 深度 | **已完整证明**（(b) 为**收窄后陈述**） | `campaign/lane_12_expansion.md` 12.1（**Y2 已修**） | 与 BM 源码 lines 1039–1049 对齐 |
| Prop 9.2 | 相变幻影：2^{(log d)^θ} 深度 Θ(log log log n) ≫ log* n | **已完整证明** | `campaign/lane_12_expansion.md` 12.2（**Y8/Y9 常数已修**：crossover ≈5607、x*≈2095.4、ln ln n=10.72） | 脚本复算 |
| Prop 9.3 | spanning 自鲁棒化不可能；(b′) P₄ 有限验证；(c) 结合 | **已完整证明**（**降级形式**：原 (b) 渐近构造已撤回，星形反例 + 证明洞，仅存 P₄ 有限命题） | `campaign/lane_12_expansion.md` 12.3(a)/(b′)/(c)（**Y3 处置**） | P₄ 全枚举 10 子集；星形反例手工推演 |

## 二、诚实条款执行记录

1. **只写 GREEN**：正文定理全部对应 PREPUB_REVIEW G1–G11（含修复后放行的 YELLOW 处置）。lane_02/lane_10/lane_11（未审）未收录；r2_01/r2_02（审查后产出、未过 adversarial 轮）未收录。
2. **命题 12.3(b) 降级**：按蓝队处置，只陈述有限存在性 (b′)（P₄，ε₀ ≤ 24/25），并在正文与致谢中明写"原渐近构造已撤回"。
3. **R1 撤回落实**：全文无"O(n log log log n) 优于现状"表述；§9 以 Proposition 9.2 写出相反方向（log log log n ≫ log* n）；"BM 无懈可击"一律带"架构内"限定（Y10）。
4. **d=3 常数口径**（Y4）：下界 4/3 已证（精确极族）；上界 4/3 = Conjecture 7.4；已证上界 5/3。
5. **[TODO: verify] 标注**：所有文献级不确定（Erdős–Gallai 1960 出处、E71、Pyber、CFS14 作者、BM22 标题、AABC25 作者名单、CKLOT 第五作者、Walecki、Stahl–Beineke、HNS17、AAFJLS04 标题、新颖性复查）均在 `.tex` 中用 `\TODO{}` 显式标注，未硬编。

## 三、骨架 vs 完整

- **完整（终稿质量）**：全部定理/引理/猜想的**陈述**；全部**证明概要**（每条 2–5 句，忠实于归档证明的主干）。
- **骨架**：完整证明本体（在归档，待组装为附录 A–D：A=块演算（lane_09），B=平面/曲面（notes/attack_planar + lane_06），C=Δ 与简并度（lane_05/lane_08/lane_07），D=BM 解剖（lane_12））；Introduction 的文献细节（TODO 标注处）；参考文献条目核对。
- **数值锚点**（K₄–K₈、Petersen=7、K_{3,q} 表、反例四重验证等）写入正文 sketch 或 "Complete proof" 行，全部可由 `../campaign/*_scripts/` 与 `../campaign/prepub_independent_check.py` 复算。

## 四、待办（下轮）

1. 组装附录 A–D（从归档 .md 翻译成 LaTeX，逐行对照原证明）。
2. 核对所有 `\TODO{}` 文献项；补 MRZ/DOI。
3. 新颖性复查（平面版、K₄-minor-free 版、曲面版）——归档中已各做一次查新（2026-09-10/11），发布前需再跑一轮。
4. 致谢中 AI 声明的期刊合规措辞（当前版本按"multi-agent system + adversarial review + error list"写，符合诚实条款）。
| Cor 4.8 | Hamilton 提升推论（含 5-连通环面 ≤ 4n/3+1/3） | **已完整证明**（一行组合：Thm 4.6(i) + Hamiltonicity） | `campaign/lane_06_genus.md` L6.5 | 两个输入均已验证 |
