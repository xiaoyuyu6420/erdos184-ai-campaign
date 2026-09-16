# 补充件：给 arXiv:2509.01901（AABC25）作者的 Conjecture 6.4 成果信材料

生成日期：2026-09-14 ｜ 依据：`front_tre/attack_tre.md`（2026-09-14 修复后收官版）+ `front_tre/librarian_gap_check.md` ｜ 范本：`front184/email_final.txt`

---

## 中文说明

### 发信对象

与 `email_final.txt` 完全同一批收件人：Akbari、Aloni、Beikmohammadi、Clow（2509.01901 四位作者）。收件邮箱沿用主邮件。

### 两个可选件怎么用

- **可选件 ①（并入段，update style）**：插到 `email_final.txt` 第二段（"I am excited to share that we can prove Conjecture 6.2 …"）之后。末句 "scripts and review records are in the same repository as before" 若与主邮件的计算段/仓库段相邻显得重复，可整句删去（主邮件 P4–P6 已覆盖）。
- **可选件 ②（独立短信）**：正文第一句 "We recently wrote to you separately…" 以**主邮件已发或同日发**为前提——若两封都发，请确保主邮件先到或同一天发，否则这句话不成立。若决定只发一封，用 ①、弃 ②。

### 数学口径核对（逐条对齐 attack_tre.md，无夸大）

- **cubic 情形完全证明** = 含完美匹配情形（原文 §6 自己指出容易，Petersen）+ 无完美匹配情形（本项定理 D）。证明链：归约（立方精确公式 f_re = p+1）+ 桥分解（每桥必入 + p 分裂到块）+ 块树计数引理 + 块的圈打包下界。**块下界不是我们证的**：是 CKKPW 2019（Graphs and Combinatorics 35(4), Thm 1.3, arXiv:1903.08795）的即时推论——邮件明写 "we prove nothing new there and cite it"，呼应报告修复记录 #3 的诚实声明。
- **计算数字**：9,588（n≤12 全部连通**奇正则**图，k=1..5）+ 45,870（n=14/16/18 全部连通立方图）= 55,458，零违反；无桥 subcubic n=4..14 全量 60,077 张，块界零违反、唯一紧例 K_{2,3}（恰为 CKKPW 界的取等例）。
- **k ≥ 2**：只有归约 f_re ≤ p+k（完全证明）+ Tutte 障碍型 5-正则构造族（n=36..146，全部 p ≤ n−3）的计算支持；**明写开放、不夸大**。
- **查新**：Conjecture 6.4 至今零引用、无人跟进（Semantic Scholar + OpenAlex，2026-09）；CKKPW 关系已查明并正确归属。

### 注意事项

1. **⚠️ 口径微差（如实标注，非矛盾）**：任务书与报告摘要把 55,458 统称 "cubic n≤18 全量"，但按报告 §2/§5，其中 9,588 实为 n≤12 **全部连通奇正则图**（cubic 只是度数为 3 的那部分，恰 113 张；纯 cubic 口径为 113+509+4,060+41,301 = 45,983）。两份英文均采用精确措辞（"all connected odd-regular graphs on n ≤ 12 … and all connected cubic graphs on n = 14, 16, 18"），与报告底层事实一致、不含夸大；总数 55,458 只以分解形式出现。
2. 报告内部（修复后版本）无矛盾：60,077、K_{2,3} 紧例、CKKPW 引用均为 2026-09-14 口径修正并全量重跑后的数字。
3. 署名 `[Your Name]` 与 email_final.txt 同款占位（实际发送版曾署"枭钰钰"，见 `email_send_body.txt`，发送时替换即可）。
4. AI 披露段沿用 email_final.txt 原文，未改力度。

---

## 可选件 ①：并入 AABC25 邮件的补充段（update style）

> Since our last note, we have also settled the cubic case of your Conjecture 6.4: every cubic graph on n vertices admits a decomposition into at most n−1 cycles and edges. As you observe in Section 6, the case with a perfect matching is easy, so the substance lies in the cubic graphs with no perfect matching. The proof combines three ingredients established in this project — a reduction to odd-degree spanning subgraphs (for cubic G this yields the exact identity f_re(G) = p(G) + 1), a bridge-decomposition lemma (a parity argument forces every bridge into every such subgraph, and p(G) then splits over the bridgeless blocks), and a counting lemma on the resulting block tree — together with one published estimate: the cycle-packing lower bound needed for each bridgeless subcubic block is an immediate consequence of Theorem 1.3 of Choi–Kim–Kostochka–Park–West (Graphs and Combinatorics 35 (2019) 805–813), which we cite rather than reprove. The computations came first, with zero counterexamples: exhaustive checks over all connected odd-regular graphs on n ≤ 12 (9,588 graphs) and all connected cubic graphs on n = 14, 16, 18 (45,870 graphs), plus all 60,077 connected bridgeless subcubic graphs on n ≤ 14 for the block bound, whose unique tight instance is K_{2,3}, matching the cited bound exactly. For k ≥ 2 we can prove the reduction f_re ≤ p + k and verified it on a family of Tutte-obstacle-type 5-regular graphs (n = 36..146), but the case remains open; scripts and review records are in the same repository as before.

---

## 可选件 ②：独立短信（若不并入主邮件）

```
Subject: Cubic case of Conjecture 6.4 in arXiv:2509.01901

Dear Professor Akbari, Professor Aloni, Professor Beikmohammadi, and Professor Clow,

I hope this email finds you well. We recently wrote to you separately about
Conjecture 6.2 and Problem 6.1 of your paper on cycle-edge decompositions
(arXiv:2509.01901); this short note adds a second development: the cubic case
of your Conjecture 6.4 is now completely proved — every cubic graph on n
vertices satisfies f_re(G) <= n - 1.

As you observe in Section 6, the perfect-matching case is easy; the substance
lies in cubic graphs with no perfect matching. The proof has three
ingredients proved in this project and one published estimate.
(i) For cubic G, f_re(G) = p(G) + 1, where p(G) is the minimum size of a
spanning subgraph all of whose degrees are odd.
(ii) If G is connected with no perfect matching, a parity argument forces
every bridge into every such subgraph, and p(G) splits into block
contributions q(X_i) plus the number B of bridges.
(iii) Each bridgeless subcubic block X obeys n(X) - q(X) >= b(X)/2 + 3/2,
where b(X) counts the bridges at its boundary — an immediate consequence of
Theorem 1.3 of Choi, Kim, Kostochka, Park and West, Graphs and Combinatorics
35 (2019) 805-813; we prove nothing new there and cite it. A block-tree
counting lemma then gives p(G) <= n - 2, hence f_re(G) <= n - 1.

For k >= 2 we prove only the reduction f_re <= p + k, supported
computationally by Tutte-obstacle-type 5-regular graphs
(n = 36..146, all with p <= n - 3); the case remains open.

Before writing, we verified the claims exhaustively: all connected
odd-regular graphs on n <= 12 (9,588 graphs) and all connected cubic graphs
on n = 14, 16, 18 (45,870) gave zero counterexamples, and the block
bound holds for all 60,077 connected bridgeless subcubic graphs on n <= 14,
with equality only at K_{2,3}, matching the cited bound. We also found no
literature follow-up to Conjecture 6.4 (zero citations in Semantic Scholar
and OpenAlex, September 2026).

I should mention for transparency that the research was carried out with the
assistance of an orchestrated AI system under my direction. The full
collaboration statement, including the verification methodology and a list of
errors caught and corrected during internal review, is included in the
repository.

The complete proof, verification scripts, and review records are available at:
https://github.com/xiaoyuyu6420/erdos184-ai-campaign

Nothing has been submitted for publication; we would be genuinely grateful
for any feedback.

Best regards,
[Your Name]
```
