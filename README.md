# Erdős #184 — an AI campaign archive, and a resolved open conjecture

**Two ways into this repository, depending on why you are here:**

| You are… | Start here |
|---|---|
| 🎯 **A reader of [arXiv:2509.01901](https://arxiv.org/abs/2509.01901)** (Akbari–Aloni–Beikmohammadi–Clow) — the email you received points you here | **[`results/aabc25-conjecture-6.2/`](results/aabc25-conjecture-6.2/)** — English, self-contained: the result, the complete proof, how to verify it |
| 🇨🇳 **中文读者**（从知乎等渠道过来）——想看这场 AI 攻题战役的故事与战果 | **[`article/article_draft_zh.md`](article/article_draft_zh.md)**（完整发布稿）· [`campaign/`](campaign/)（各路攻击报告与可复算脚本） |

---

## What this repository is

A public archive of one attempt to attack a 60-year-old open problem in graph theory — the Erdős–Gallai question of how few **cycles and edges** are needed to decompose the edge set of a graph — using an orchestrated multi-agent AI pipeline under human direction.

Everything here was produced by that pipeline: attacker agents (proofs and counterexamples), verifier agents (adversarial review, default assumption: *it is wrong*), blue-team agents (bounded repairs), and an orchestrator. The human owner set direction and authorized publication. **No human referee has reviewed this material, and nothing here has been submitted for publication.**

## The headline result (and where it is)

The campaign's most complete outcome so far resolves **Conjecture 6.2** of [arXiv:2509.01901](https://arxiv.org/abs/2509.01901) verbatim, and strengthens the corresponding case of their **Problem 6.1**:

> Every $6$-regular simple graph on $n$ vertices decomposes into three $2$-factors, one of which has a component with at least $4$ vertices; and if $n \equiv 0 \pmod 3$ the edge set decomposes into at most $n-2$ cycles and edges (hence $\mathrm{ce}(G) \le n-1$ for every $6$-regular graph).

- **English, self-contained presentation and proof**: [`results/aabc25-conjecture-6.2/`](results/aabc25-conjecture-6.2/)
- **Full working record (Chinese, 4th revision)**: [`campaign/r2_01_aabc25_struct.md`](campaign/r2_01_aabc25_struct.md) — proof, verification tables, novelty positioning, revision log
- **Verification artifacts**: [`campaign/r2_01_scripts/`](campaign/r2_01_scripts/) (original pipelines and logs) and [`campaign/harden_round2/`](campaign/harden_round2/) (independent second-round hardening: scripts, data, logs, three reports), plus the review reports [`campaign/verify_r2_01.md`](campaign/verify_r2_01.md) and [`campaign/harden_round2/verify_round2_proof.md`](campaign/harden_round2/verify_round2_proof.md)

## Repository map

```
results/aabc25-conjecture-6.2/   English entry point: result, complete proof, verification, related work
article/article_draft_zh.md      中文发布稿（含「AI 协作与校对声明」独立章节）
campaign/                        64 路战役档案：各路报告、审查记录、可复算脚本、AABC25 中文工作记录
  campaign/r2_01_aabc25_struct.md    AABC25 结果完整工作记录（中文）
  campaign/harden_round2/            第二轮独立加固：数值、审查、文献三份报告 + 脚本/数据/日志
notes/                           前哨战（平面图五定理）与二部图 / Δ≤5 战线的证明笔记与审查记录
paper/                           英文论文骨架（15+ 定理；AABC25 结果尚未并入，见该目录 README）
2509.01901_src/                  模板论文的 LaTeX 源码（供对照引用）
```

## What is claimed, and what is not

- **Claimed**: the statements and proofs in `results/aabc25-conjecture-6.2/` (verified by two independent verification passes, plus exhaustive machine checks — see that directory).
- **Not claimed**: that the *existence* statement behind the L(B) construction step is new (it coincides with an observation of Kouider–Sabidussi 1995; we claim only the explicit construction and its counting consequence), any novelty for the reduction recorded in the template paper at `main.tex:316–318`, or any results from the campaign outside the scope of the reports above.
- **Known limits**: the two papers closest to the construction step (Bertram–Horák 1997; Kouider–Sabidussi 1995) are paywalled and were not read in full; the positioning in `results/aabc25-conjecture-6.2/README.md` rests on a peer-reviewed survey transcription (Plummer 2007) and on published abstracts, and is labelled as such there.
- **Errors caught so far**: the verification chain has caught and dispositioned 12 items during the campaign (canonical table: §5 of `article/article_draft_zh.md`); `campaign/PREPUB_REVIEW.md` counts three cases that had been labelled complete proofs and actually had a gap (Y1–Y3). The revision log for the result above is in `campaign/r2_01_aabc25_struct.md` §10.

## AI collaboration statement (summary)

All content was produced by a multi-agent AI system under human direction: proof/counterexample agents, adversarial verifier agents (default assumption: the claim is false), repair agents, and an orchestrator. Publication was authorized by the human owner. The full statement, including the pre-publication three-colour review (11 green / 11 yellow repaired / 1 red retracted), is in `article/article_draft_zh.md` §5.

*本仓库的全部内容由多智能体 AI 系统在人类指导下产出；未经同行评议，未提交任何期刊。发布由人类所有者授权。*

（完整声明见 `article/article_draft_zh.md` 第五节；含三色审查结论「11 绿 / 11 黄修复 / 1 红撤回」与累计 12 处错误的处置记录。）

---

## 战役战果（中文速览）

围绕 Erdős–Gallai 圈+边分解猜想（Erdős #184，60 年开放问题），战役产出 **15+ 条定理级结果**（含完全图精确值 $\mathrm{ce}(K_{2m})=2m-1$、块可加性恒等式、Eulerian 环面图 $\le n-1$、Dirac 正则图 $\le n-1$ 等）、**4 个反例/否定结果**（含 7 点反例否证 $\Delta\le 6 \Rightarrow n-1$），以及把剩余困难精确压缩到三块可攻阵地的战场地图。其中推进最完整的一条——AABC25 论文登记的 Conjecture 6.2——已在 [`results/`](results/) 给出完整证明与验证，并经两轮独立审查放行。

- 第一幕（21 路多样性攻击）：已完成并审查
- 第二幕（24 路深化）：主体完成；**AABC25 六正则猜想已解决并经加固**（见 [`results/aabc25-conjecture-6.2/`](results/aabc25-conjecture-6.2/)）
- 第三幕（19 路对抗收拢）：排队中

**复现**：各报告内的脚本均可独立运行；含随机性的脚本已固定种子（如 `campaign/lane08_scripts/lane08_verify.py` seed=20260911）。本轮 AABC25 相关的一键复现命令见 [`results/aabc25-conjecture-6.2/README.md`](results/aabc25-conjecture-6.2/README.md)。
