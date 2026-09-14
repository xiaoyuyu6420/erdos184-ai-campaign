# Conjecture 6.2 of arXiv:2509.01901 — proof, verification, and how to check it

**Result.** *Every $6$-regular graph is decomposable into three $2$-factors, where one of these $2$-factors has a component with at least $4$ vertices* — Conjecture 6.2 of Akbari–Aloni–Beikmohammadi–Clow, [arXiv:2509.01901](https://arxiv.org/abs/2509.01901), quoted verbatim (all graphs in this repository are simple, as in [`proof.md`](proof.md) §0). Moreover the corresponding case of their *Problem 6.1* is not only settled but strengthened: if $G$ is $6$-regular on $n$ vertices with $n \equiv 0 \pmod 3$, then $\mathrm{ce}(G) \le n-2$, where $\mathrm{ce}(G)$ is the minimum number of parts in a decomposition of $E(G)$ into cycles and single edges. When $3 \nmid n$ no $2$-factor can be a union of triangles, so a Petersen $2$-factorization already gives $\lfloor n/3\rfloor$ cycles per factor and at most $3\lfloor n/3\rfloor \le n-1$ parts; the case that genuinely needs new input is $n \equiv 0 \pmod 3$. Together: $\mathrm{ce}(G) \le n-1$ for **every** $6$-regular simple graph.

> **Status: not peer-reviewed, not submitted.** Written and checked by an orchestrated AI system under human direction. Please treat it as a claim to be checked, not as an authority.
>
> *Note: the English paper skeleton under [`../../paper/`](../../paper/) predates this result and still lists the case $n \equiv 0 \pmod 3$ as open. The authoritative statement of the result is [`proof.md`](proof.md); the skeleton will be updated when the paper is revised.*

## Read this first

| If you want… | Read |
|---|---|
| The complete proof, self-contained | [`proof.md`](proof.md) |
| The shape of the argument in five lines | the "Proof outline" below |
| What was machine-verified, and how to re-run it | "Verification" below |
| How this relates to Bertram–Horák (1997), Kouider–Sabidussi (1995), Hartvigsen (2024) | "Related work and what we do *not* claim" below |
| The full working record, including two review rounds and every correction | [`../../campaign/r2_01_aabc25_struct.md`](../../campaign/r2_01_aabc25_struct.md) (Chinese) and [`../../campaign/harden_round2/`](../../campaign/harden_round2/) |

## The two reductions (why this is the right thing to prove)

The template paper observes (at `main.tex:316–318` of its source) that if a $6$-regular graph can be split into three $2$-factors with at least one component of size $\ge 4$, then its edges can be partitioned into $\le n-1$ cycles and edges: a $2$-factor on $n$ vertices whose components all have length $\ge 3$ has at most $\lfloor n/3\rfloor$ components, and one component of size $\ge 4$ saves exactly one part. So the conjecture is precisely the statement that closes the computation — and Theorem 4 of [`proof.md`](proof.md) pushes the same accounting one unit further, to $n-2$, in the last open case $n \equiv 0 \pmod 3$.

## Proof outline

1. **Reduction to a 4-regular lemma.** For the hard case $n = 3m$: if $G$ has a $2$-factor with a component of size $\ge 4$, count components as above and finish. Otherwise every $2$-factor is a union of triangles; in particular (Petersen 2-factorization) the complement $H$ of a triangle factor is $4$-regular, and it suffices to find *in $H$* a $2$-factor with a component of size $\ge 4$. Hence everything reduces to: **every $4$-regular simple graph on at least $5$ vertices has a $2$-factor containing a cycle of length $\ge 4$** (Lemma 2 of [`proof.md`](proof.md)).
2. **The 4-regular lemma, by contradiction.** Assume every $2$-factor of $G$ is a union of triangles. Then $G$ is the union of two edge-disjoint triangle factors $F, F'$; each triangle of $F$ meets each triangle of $F'$ in at most one vertex; this forces a structure: $G$ is the **line graph $L(B)$ of a cubic bipartite graph $B$**, with an explicit bijection between vertices of $G$ and edges of $B$.
3. **A perfect matching and a flip.** $B$ cubic bipartite has a perfect matching $M$ (Hall). Orient $M$ arbitrarily. For each vertex $x$ of $B$ (a triangle of $F$ or $F'$), the three edges of $B$ at $x$ pair up into three adjacency pairs at $x$; a pair of edges of $B$ sharing $x$ *is* an edge of $L(B) = G$. Take **two** of the three pairs at $x$ if $x$ is a tail of its matching edge, and **one** if it is a head. The resulting edge set $\Phi(\sigma)$ is a spanning $2$-factor, and it contains **no triangle**: a triangle of $\Phi$ would need all three pairs at some $x$, and one pair is always missing.
4. **The flip partitions.** Reversing the orientation gives $\Phi(-\sigma)$, which picks at every $x$ exactly the pairs $\Phi(\sigma)$ did not. So $\Phi(\sigma) \sqcup \Phi(-\sigma)$ **partitions** $E(L(B))$ into two triangle-free $2$-factors — contradicting the assumption in step 2, and both factors have at most $1 + \lfloor (n-4)/3 \rfloor = m-1$ components.
5. **Accounting.** In the case where $G$ has two edge-disjoint triangle factors $S, T$, the flip covers $S \cup T$ by two triangle-free $2$-factors of $\le m-1$ components each, and the remaining $2$-factor has $\le m$ components: total $\le 3m-2 = n-2$. In every other case a simpler count gives $\le n-2$ or better. The conjecture itself (three $2$-factors, one with a component of size $\ge 4$) follows from the same case split, with $S, S', T := H - E(S')$ in the one case that needs care. Full details and all statements: [`proof.md`](proof.md).

## Verification

Everything below was produced by programs in this repository, with fixed seeds where randomness is involved, and each construction is re-checked by a **verifier written independently of the constructive code** (degree, spanning-ness, cycle validity, partition completeness). Two verification passes were run by different agents, the second one re-implementing the constructions from scratch.

**Machine-verified, all with zero counterexamples:**

| Check | Scale |
|---|---|
| Exhaustive: the lemma's parameter space (all matchings × all orientations) | all $s \le 5$ cases (832,944 combinations: 48 / 3,456 / 829,440 for $s = 3, 4, 5$) + sampled $s = 6$ (1,183,920 combinations in total) |
| Exhaustive: all *isomorphism classes* of $6$-regular graphs, $n = 10, 11, 12$ | 21 / 266 / 7,849 classes, all decompositions within bounds; exact $\mathrm{ce}$ determined for all 21 ten-vertex classes (all equal to 3) |
| Exhaustive: all $4$-regular graphs on $n \le 8$ vertices (the lemma), plus the complete "dangerous class" on $9$ vertices | 19,836 graphs + 5,040 worst-case graphs, no exception |
| Exhaustive: all labelled $6$-regular graphs on $9$ vertices, exact $\mathrm{ce}$ | 30,016 graphs, all with $\mathrm{ce} = 3$ |
| Random $6$-regular graphs, $n = 15, 18, 21, 24$ | 8,000 instances, all within bounds |
| Adversarial families built to force the dangerous structure | 299,265 + 2,100 instances, all pass |
| Independently re-checked decomposition certificates | 18,279 certificates, zero failures; the checker was itself validated against 5 injected error types (5/5 detected) |

**Reproduce.** Requirements: Python 3 with `networkx`, and [`geng` from nauty](https://pallini.di.uniroma1.it/) for the isomorphism-class enumerations (the numbers below were produced with Python 3.13.12, networkx 3.6.1, nauty 2.9.3). Paths are relative to the repository root.

```bash
# second-round, independently written hardening suite (campaign/harden_round2/)
cd campaign/harden_round2
geng -d3 -D3 10 -q > data/geng_10_d3.g6      # all 3-regular graphs on 10 vertices (complement = 6-regular)
geng -d4 -D4 11 -q > data/geng_11_d4.g6
geng -d5 -D5 12 -q > data/geng_12_d5.g6
python3 h_common.py                          # anchor self-tests
python3 h_A_exact.py anchors                 # exact-ce anchors (independent reference values)
python3 h_A_enum.py --n 10 --g6 data/geng_10_d3.g6 --out data/A_n10.jsonl --exact
python3 h_A_enum.py --n 11 --g6 data/geng_11_d4.g6 --out data/A_n11.jsonl
python3 h_A_enum.py --n 12 --g6 data/geng_12_d5.g6 --out data/A_n12.jsonl
python3 h_B_random.py --count 2000 --shard 200 --procs 8 --nlist 15,18,21,24
python3 h_C_adv.py --s 7 --count 500 --shard 50 --procs 8
python3 h_C_adv.py --s 8 --count 200 --shard 50 --procs 8
# independent re-check of every certificate produced above (this reads the .jsonl files)
# note: use an interpreter that has networkx installed; the records below were produced
#       with /opt/homebrew/Caskroom/miniconda/base/bin/python3 (3.13.12, networkx 3.6.1)
# (`data/C_s3_s0.jsonl` holds two placeholder records with no certificate and is excluded.)
python3 h_verify.py data/A_n10.jsonl data/A_n11.jsonl data/A_n12.jsonl \
    data/B_n15_s*.jsonl data/B_n18_s*.jsonl data/B_n21_s*.jsonl data/B_n24_s*.jsonl \
    data/C_s7_s*.jsonl data/C_s8_s*.jsonl \
    data/extra_n10_ce3_certs.jsonl \
    data/extra_n12_ce3_certs.jsonl data/extra_n12_ce3_sample_certs.jsonl data/extra_n12_1960_ce3.jsonl
# expected: {"total_records": 18279, "total_failures": 0}
sh run_D_repro.sh && python3 h_D_compare.py  # three passes, byte-identical certificates

# original pipeline (campaign/r2_01_scripts/)
cd ../r2_01_scripts && python3 r2_selftest.py && python3 sweep_6reg.py small
```

The complete command list, timings and expected outputs are in [`../../campaign/harden_round2/harden_numeric.md`](../../campaign/harden_round2/harden_numeric.md) §8.

**Known limits of the verification (stated plainly).** The lemma's "dangerous class" is fully parameterised by cubic bipartite graphs $B$ with $2s$ vertices; exhaustive search covers $s \le 6$, i.e. $B$ with up to $12$ vertices and $4$-regular graphs $L(B)$ with up to $18$ vertices. For $s \ge 7$ the statement is covered by the proof only. The random sweeps are smoke tests, not probabilistic evidence. Full details, including the two review rounds and the errors they caught, are in [`../../campaign/harden_round2/harden_numeric.md`](../../campaign/harden_round2/harden_numeric.md) and [`../../campaign/verify_r2_01.md`](../../campaign/verify_r2_01.md).

## Related work and what we do *not* claim

- **Bertram–Horák 1997**, *Decomposing 4-regular graphs into triangle-free 2-factors*, SIAM J. Discrete Math. 10:309–317 — a **polynomial decision algorithm** that either decomposes a given $4$-regular graph into two triangle-free $2$-factors or reports that this is impossible. We found no characterisation of the YES instances in any source we could access; its authors themselves conjectured (as transcribed in Plummer's 2007 survey, Theorem 6.9 and Conjecture 6.10) that the corresponding recognition problems are **NP-complete** for all higher degrees. It says nothing about cycle–edge decompositions.
- **Kouider–Sabidussi 1995**, *Factorizations of 4-regular graphs and Petersen's theorem*, J. Combin. Theory Ser. B 63:170–184 — its abstract records the observation that *a $3$-regular graph has a perfect matching if and only if its line graph has a triangle-free $2$-factorisation*. Since a cubic bipartite graph always has a perfect matching (Hall), the **existence statement** of Proposition 3 in [`proof.md`](proof.md) is a special case of that observation. We therefore claim **no novelty for the existence statement**; what we contribute is the explicit, self-contained construction (the flip $\Phi(\sigma) \sqcup \Phi(-\sigma)$, which partitions the adjacency pairs pointwise) and its counting consequence that drives the $n-2$ bound.
- **Abreu–Aldred–Funk–Jackson–Labbate–Sheehan 2004**, JCTB 92:395–404 — two non-isomorphic $2$-factors in graphs of minimum degree $\ge 8$; this is the analogue the template paper cites for the $8$-regular case, and it does not cover $6$-regular graphs.
- **Hartvigsen 2024** (preprint) — a polynomial algorithm *and a characterisation* for triangle-free $2$-factors in general graphs; relevant to the open strengthening "(+) every $4$-regular graph has a fully triangle-free $2$-factor", which we do **not** prove.
- **The template paper's own reduction** (`main.tex:316–318`): the observation that a suitable three-$2$-factor split yields $\le n-1$ parts is theirs, and we do not claim it.

**Evidence level of the two paywalled items.** The Bertram–Horák statement above is quoted from a peer-reviewed survey (Plummer 2007, p. 812, checked verbatim). The Kouider–Sabidussi sentence is quoted from the published abstract (two independent sources agree), and the full text was not obtained — in particular we could not check what exactly "triangle-free 2-factorisation" requires there; if it means something weaker than a decomposition into two triangle-free 2-factors, the positioning of Proposition 3 would need revision. Neither paper was read in full. If their proofs contain more than the statements above, this **positioning** — not the theorems — would need to change.

## What we claim

The statements and complete proofs in [`proof.md`](proof.md): the $4$-regular lemma, the flip/partition proposition and its counting corollary, the bound $\mathrm{ce} \le n-2$ for $n \equiv 0 \pmod 3$, the verbatim resolution of Conjecture 6.2, and the resulting $\mathrm{ce} \le n-1$ for all $6$-regular graphs and for all even graphs of maximum degree $6$. To the best of our knowledge (searches recorded in [`../../campaign/harden_round2/bh97_landscape.md`](../../campaign/harden_round2/bh97_landscape.md)), the structural reduction "every $2$-factor a union of triangles $\Rightarrow G \cong L(B)$ of a cubic bipartite $B$" and the resolution of Conjecture 6.2 have no precedent — but we are a machine pipeline, and we would rather you checked than trusted us.
