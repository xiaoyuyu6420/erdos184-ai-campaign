# AI-Assisted Graph Theory Research: Cycle-Edge Decompositions and Conjecture 6.2

[![Graph Theory](https://img.shields.io/badge/topic-Graph%20Theory-blue.svg)](#)
[![Combinatorics](https://img.shields.io/badge/topic-Combinatorics-green.svg)](#)
[![Automated Verification](https://img.shields.io/badge/verification-18%2C279%20certificates-success.svg)](#)

This repository hosts mathematical proofs, formal reduction frameworks, and exhaustive computational verification scripts developed in an AI-assisted investigation of cycle–edge decompositions in finite simple graphs (rooted in the Erdős–Gallai problem, Erdős #184).

---

## Quick Navigation

| Target / Interest | Recommended Entry Point | Description |
|---|---|---|
| 🎯 **Resolution of Conjecture 6.2** | **[`results/aabc25-conjecture-6.2/`](results/aabc25-conjecture-6.2/)** | **English, self-contained:** Complete proof, reduction theorems, and replication scripts for [arXiv:2509.01901](https://arxiv.org/abs/2509.01901). |
| 📊 **Computational Verification** | **[`campaign/harden_round2/`](campaign/harden_round2/)** | Full verification suite: 18,279 explicit certificates, isomorphism class sweeps ($n \le 12$), negative controls. |
| 📝 **Comprehensive Research Paper** | **[`paper/draft_v2/`](paper/draft_v2/)** | Full mathematical write-up incorporating 15+ theorems across cycle-edge decompositions. |
| 🗂️ **Repository Directory Map** | **[`INDEX.md`](INDEX.md)** | Index of modular directories corresponding to specific open questions and sub-problems. |
| 🇨🇳 **中文概要与方法论** | **[`article/article_draft_zh.md`](article/article_draft_zh.md)** | 研究背景综述、多智能体辅助形式化方法论与验证审计记录。 |

---

## Primary Result: Resolution of Conjecture 6.2 (arXiv:2509.01901)

Our primary completed milestone resolves **Conjecture 6.2** of Akbari, Aloni, Beikmohammadi, and Clow ([arXiv:2509.01901](https://arxiv.org/abs/2509.01901)) verbatim, and improves the corresponding bound in their **Problem 6.1**:

> **Theorem (Conjecture 6.2 verbatim).** Every $6$-regular simple graph decomposes into three $2$-factors, one of which has a component with at least $4$ vertices.
>
> **Theorem (Strengthened Bound).** For every $6$-regular simple graph on $n$ vertices with $n \equiv 0 \pmod 3$, $\mathrm{ce}(G) \le n - 2$. Consequently, $\mathrm{ce}(G) \le n - 1$ holds for all $6$-regular graphs.

- **Self-contained Proof**: [`results/aabc25-conjecture-6.2/proof.md`](results/aabc25-conjecture-6.2/proof.md)
- **Methodology & Context**: [`results/aabc25-conjecture-6.2/README.md`](results/aabc25-conjecture-6.2/README.md)
- **Zero-Failure Verification**: Verified across all 832,944 combinations for $s \le 5$, all 30,016 labelled 6-regular graphs on 9 vertices, and all isomorphism classes on $n \in \{10, 11, 12\}$ (21, 266, and 7,849 classes respectively).

---

## Directory Organization

The codebase is organized modularly by sub-problem and research focus. For a detailed reference guide, see **[`INDEX.md`](INDEX.md)**.

### Core Deliverables
- **`results/`**: Self-contained mathematical deliverables formatted for external academic review.
- **`paper/`**: LaTeX draft papers, with `paper/draft_v2/` containing the consolidated manuscript.
- **`article/`**: Methodological overviews and reflective research notes (in Chinese).

### Problem-Specific Modules
- **`front184/`**: Primary investigation into Erdős #184 (cycle–edge decompositions). Includes working logs, historical notes, and earlier verification scripts.
- **`campaign/`**: Computational artifacts, including `campaign/harden_round2/` (the independent secondary verification suite and JSONL certificates).
- **`front20/`**, **`front583/`**, **`frontKG/`**, **`front203/`**: Exploratory research directories investigating related open problems (Erdős #20 sunflower problem, Gallai path decomposition, Krenn–Gu conjecture).
- **`front_t*` (`front_tk`, `front_tmm`, `front_tre`, etc.)**: Targeted explorations into specific conjectures from recent literature (e.g., `front_tre` examines Conjecture 6.4 on cubic graphs from arXiv:2509.01901).
- **`notes/`**: Scratchpads and structural lemmas for specific graph classes (planar, bipartite, degree-bounded).

---

## Methodology & Academic Transparency

### Multi-Agent Formal Verification
This project explored the capability of multi-agent LLM orchestration to assist in rigorous mathematical research:
1. **Structural Provers**: Devising combinatorial reductions and candidate decomposition strategies.
2. **Adversarial Verifiers**: Independently checking arguments line-by-line under a falsification mandate and independently re-implementing verification code from mathematical statements without sharing codebases.
3. **Computational Engines**: Running exhaustive brute-force and integer linear programming checks across complete isomorphism classes via `nauty` and `networkx`.

### Scientific Boundaries & Verification Limits
- **Existence vs Construction**: As noted in our proof documents, the existence of a triangle-free 2-factorization in line graphs of cubic graphs is related to an observation by Kouider & Sabidussi (1995). We claim no novelty for the general existence statement, but provide an explicit algebraic/combinatorial construction $\Phi(M) \sqcup \Phi(-M)$ that yields quantitative accounting bounds for cycle-edge decomposition.
- **Computational Verification Scope**: The structural reduction is exhaustively verified on all parameter combinations for bipartite core graphs up to $2s = 12$ vertices ($n \le 18$ for line graphs). Graphs with $s \ge 7$ are covered strictly by the mathematical proof.
- **Non-peer-reviewed**: While subjected to multi-layered adversarial checking, these results have not undergone external peer review. Independent inspection by domain experts is warmly welcomed.

---

## License & Attribution

All custom code and mathematical write-ups in this repository are available under the MIT License. If you use or build upon these results or verification pipelines, please cite or link back to this repository.
