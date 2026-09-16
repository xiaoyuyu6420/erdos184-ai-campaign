# 勘误+结果信草稿：给 arXiv:2604.23188 作者（Fazekas–Mammoliti–Mercas–Simpson）

生成日期：2026-09-14 ｜ 依据：`front_abs/attack_abs.md`（定稿，含审查通过标记）+ `front_abs/review_abs.md` ｜ 语气范本：`front184/email_final.txt`

---

## 中文说明

### 发信对象

arXiv:2604.23188《Binary Words Containing Few Abelian Squares》**全部四位作者**。

⚠️ **与任务简报的出入（以报告为准）**：简报只写 Fazekas–Mammoliti 两人，但 `attack_abs.md` §0 核对原文为四人（"作者实为 Fazekas, Mammoliti, Mercas, Simpson（四人；任务简报只列前两人）"）。已再经 arXiv abs 页复核（2026-09-14，v1 提交于 2026-04-25）：**Szilard Zsolt Fazekas, Adam Mammoliti, Robert Mercas, Jamie Simpson**。邮件抬头按四人写；收件邮箱本地没有，留占位 `[authors of arXiv:2604.23188]`。这不是报告内部矛盾，是简报信息不全，如实标注。

### 要点（逐条与 attack_abs.md / review_abs.md 核对一致）

- **勘误 3 条（正文前置，对作者最有用）**：
  1. Thm 6 唯一性条款在 n ≡ 0,1 (mod 4) 为假——显式反例 n=4: abbb（θ=1=⌊n/4⌋ 但既非 b²a 也非其反词）；n=8: bbabbbbb、bbbbbabb；n=12: b⁴ab⁷、b⁷ab⁴。修正版（定理 B）：最小词集 {b^i a b^{n−1−i} : ⌊max(i,n−1−i)/2⌋=⌊n/4⌋}，基数 4/3/2/1；**计数结论 M(1,n)=⌊n/4⌋ 不变**（安慰点，已写进信）。
  2. Table 1 n=8 行：第二个词 "abbbabb" 长 7 且 θ=2≠3，应为 abbbabbb。
  3. Table 3 三行样例长度错（x=1 行系审查补列）：x=1: b⁹ab⁹（长19）→ b⁹ab⁸；x=10: a³b⁵a⁷b⁴（长19）→ a³b⁵a⁷b³；x=13: a⁵b³a⁷b²（长17）→ a⁶b³a⁷b²（=W(13,5)）。
- **两条小边界注（一句带过，来自报告 §1.3 候选条目 + 审查 m-5）**：Conjecture 4 按字面仅 n=4 反例（abab, baba）；Thm 7 在 n=2 有未注明例外（M(2,2)=1）。信中只陈述事实；"补 n≥5 条款"的修改建议因篇幅未进正文，可按需在附件或后续通信中补。
- **自己的结果（放后面）**：①n ≤ 48 全部 Parikh 向量机器验证——Fici–Saarela 猜想与摘要级"构造最优性"（CO）都成立；搜索器每次运行以 "no word below T" 证书收尾、带完备性论证（review_abs.md 独立审查通过）；②4-run 词 θ 的精确封闭公式（命题 C）；③构造最优性对一切 4-run 词的证明（命题 D）——由此反例必须 ≥3 个 b-run，该情形开放、信中明写。
- **计数口径**：distinct abelian square 因子（按词面去重），与原文一致（其引言 abaababa=6 与 Table 1 双重锚定），信中一句话声明，避免作者误解验证范围。

### 注意事项

1. **本地无该项目的 GitHub 仓库**：正文留 `[repository URL]` 占位，**发送前必须补真实链接**。不可直接指向 erdos184-ai-campaign（那是图论战役仓库）冒充；若复用需另建子目录并发布 `search.c`/`sweep*.csv`/`review_abs.md`。AI 披露段说 review records included in the repository，发布时须兑现。
2. **语气**：勘误信惯例——第一段先肯定论文价值；勘误在前；自己的结果在后；用词轻（"small errors in the statements"）；结尾感谢。
3. 上标用 ASCII 记法（`b^4 a b^7`）保证邮件客户端兼容；如需 Unicode 上标（b⁴ab⁷）可整体替换。
4. 抬头称谓用 Dr.（最稳，Mammoliti 职级未核实；如想更恭敬可改 Professor，但需逐人核实）。
5. `attack_abs.md` 与 `review_abs.md` 之间**未发现矛盾**；审查后的修复（定理 B(ii) 词集笔误、命题 D u 偶分支补全、x=1 行补列）均已反映在信中（Thm 6 修正版词集刻画、三行 Table 3 样例）。词集基数 4/3/2/1 因正文篇幅从信中略去，可按需补回或留给仓库附件。
6. 署名 `[Your Name]` 占位，发送时替换。

---

## 英文信正文

```
To: [authors of arXiv:2604.23188]
Subject: Small corrections and some supporting results for arXiv:2604.23188

Dear Dr. Fazekas, Dr. Mammoliti, Dr. Mercas, and Dr. Simpson,

I am writing about your paper "Binary Words Containing Few Abelian Squares"
(arXiv:2604.23188) — the construction behind Theorem 12 is elegant and the
optimality question natural. We found a few small errors in the statements,
and some supporting results; the errors first.

(1) The uniqueness clause of Theorem 6 fails for n = 0, 1 (mod 4): abbb
(n = 4) has theta = 1 = floor(n/4) yet is neither b^2 a nor its reversal;
further counterexamples at n = 8 (bbabbbbb, bbbbbabb) and n = 12
(b^4 a b^7, b^7 a b^4). The count M(1, n) = floor(n/4) is unaffected — the
minimizers are exactly the b^i a b^(n-1-i) with
floor(max(i, n-1-i)/2) = floor(n/4).

(2) Table 1, row n = 8: the second word abbbabb has length 7; read
abbbabbb (theta = 3).

(3) Table 3: three sample words have wrong lengths — x = 1: b^9 a b^9
(19 letters) should be b^9 a b^8; x = 10: a^3 b^5 a^7 b^4 (19) should be
a^3 b^5 a^7 b^3; x = 13: a^5 b^3 a^7 b^2 (17) should be
a^6 b^3 a^7 b^2 (= W(13, 5)).

Two smaller boundary points: Conjecture 4 fails only at n = 4 (abab, baba);
Theorem 7 needs an exception at n = 2 (M(2, 2) = 1).

We count distinct abelian square factors, as in your paper. An exact
branch-and-bound search — each run ends in an explicit "no word below T"
certificate backed by a completeness argument — verified for every Parikh
vector up to length 48 that no word has theta below the construction value
tau_x + tau_y, nor below floor(n/4); the Fici–Saarela conjecture and your
abstract's construction-optimality conjecture therefore hold up to n = 48.
We also prove a closed formula for theta on four-run words
a^i b^u a^j b^v, whence W(x, y) is optimal among four-run words of the same
Parikh vector; any counterexample must have at least three b-runs — that case
remains open.

I should mention for transparency that the research was carried out with the
assistance of an orchestrated AI system under my direction. The full
collaboration statement, including the verification methodology and a list of
errors caught and corrected during internal review, is included in the
repository.

Verification scripts, counterexamples, and review records:
[repository URL]

Nothing has been submitted for publication; thank you for your time, and for
this lovely problem.

Best regards,
[Your Name]
```
