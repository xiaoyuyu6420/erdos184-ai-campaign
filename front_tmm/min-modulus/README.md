# Minimum modulus for the unique multiset-sum problem

[![Lean CI](https://github.com/jarfo/min-modulus/actions/workflows/build.yml/badge.svg)](https://github.com/jarfo/min-modulus/actions/workflows/build.yml)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

This repository is the Lean 4 formalization accompanying the paper

> José A. R. Fonollosa, *Minimum modulus for the unique multiset-sum problem*,
> [arXiv:2607.08366](https://arxiv.org/abs/2607.08366), 2026.

The code in this repository is licensed under the Apache License 2.0; see [LICENSE](LICENSE).

The main theorem of the paper is kernel-checked end-to-end: `nmin_eq` builds
with **0 errors, 0 sorries** and uses only the standard axioms
(`propext`, `Classical.choice`, `Quot.sound`, checked with `#print axioms nmin_eq`).

The repository also formalizes Proposition 2 of the paper (optimality among
elementary abelian $`2`$-groups): if $`g_0, \dots, g_{n-1} \in (\mathbb{Z}_2)^k`$
have unique multiset sums, then $`k \ge n - 1`$, so the least such group has
order $`2^{n-1}`$. See [Proposition 2](#proposition-2-elementary-abelian-2-groups)
below (also 0 sorries, standard axioms only).

Finally, the repository formalizes the resolution of **open problem 4** of the
paper — the exact minimum order for unique multiset sums over *all* finite
abelian groups — following

> Michael Inal, *The Exact Minimum Order for Unique Multiset Sums in Finite
> Abelian Groups*, [OSF preprint](https://doi.org/10.17605/OSF.IO/C58Q9), 2026.

The answer is $`m_{\mathrm{ab}}(n) = 2^{n-1}`$: a lower bound valid over every
finite abelian group (not just elementary abelian ones), matched by the
elementary abelian construction, with a classification of the extremal case.
See [Open problem 4](#open-problem-4-all-finite-abelian-groups) below (0
sorries, standard axioms only).

## The problem and the theorem

Fix $`n \ge 2`$. A set $`A = \{a_0 < \dots < a_{n-1}\}`$ of residues in
$`\mathbb{Z}_N`$ is **valid mod $`N`$** if the all-ones multiset is the *only*
size-$`n`$ multiset drawn from $`A`$ whose sum is $`p = \sum a_i \pmod N`$.
Validity is exactly the condition under which the permanent of an
$`n \times n`$ matrix equals a single coefficient of its row-product
polynomial mod $`x^N - 1`$, extractable by a size-$`N`$ transform (a DFT over
$`\mathbb{C}`$, or a number-theoretic transform over a finite field) — so one
wants the smallest modulus $`N`$ that is still valid.

For the super-increasing set $`A = \{2^k - 1 : 0 \le k < n\}`$ the paper proves

> **Theorem.** $`N_{\min}(n) = 2^n - 2^{\lfloor \log_2 n \rfloor}`$ for all $`n \ge 2`$.

The Lean development proves exactly this, for all $`n \ge 2`$ (not up to a
bound): the main theorem `nmin_eq` states
`IsLeast {N | 2 ≤ N ∧ Valid n N} (2^n − 2^m)` with `m = Nat.log 2 n`, combining
the paper's Theorem A (validity / upper bound) and Theorem B (lower bound).
That this $`N`$ is minimal over *all* residue sets (not just the
super-increasing one) remains a conjecture (Conjecture 1 in the paper,
CP-certified for $`n \le 7`$) and is not formalized.

## Layout

A single Lake package rooted at the repository root:

```
lakefile.toml, lean-toolchain, lake-manifest.json
MinModulus.lean                 -- root module, imports the three files below
MinModulus/
  UniqueSums.lean               -- Theorems A, B and the main theorem `nmin_eq`
  ElemAbelian2.lean             -- Proposition 2 (elementary abelian 2-groups)
  AbelianMin.lean               -- Open problem 4 (all finite abelian groups)
scripts/check_axioms.lean       -- axiom audit, run in CI
```

## Build

| | |
|---|---|
| Toolchain | Lean 4 `v4.32.0`, Mathlib pinned `v4.32.0` (prebuilt cache) |
| Build | `lake build` — green (0 errors, 0 warnings, 0 sorries) |
| Axioms | `propext`, `Classical.choice`, `Quot.sound` only |

With [elan](https://github.com/leanprover/elan) on your `PATH` (it reads
`lean-toolchain` and fetches Lean `v4.32.0` automatically):

```sh
lake exe cache get   # fetch the prebuilt Mathlib cache
lake build
```

To reproduce the axiom audit:

```sh
lake env lean scripts/check_axioms.lean
```

## What is formalized

The development is stated in **`k`-space over ℕ**: a candidate multiset is
`k : ℕ → ℕ` with `∑_{i<n} k i = n`, validity is the paper's k-vector condition
with `Nat.ModEq`, and the paper's signed multiples $`V = \pm jN`$ appear only
through the congruence `M ≡ 2^n − 1 [MOD N]` on $`M = \sum k_i 2^i`$ — no
integer subtraction anywhere.

| Lean declaration | Corresponds to (paper) | Status |
|---|---|---|
| `a`, `dsum`, `val`, `Supp`, `Valid` | Problem statement, k-vector form | ✅ defined |
| `sum_two_pow`, `sum_a_add_dsum` | §3 reduction identities | ✅ proved |
| `not_valid_of_witness` | Lemma 1 (reduction), witness direction | ✅ proved |
| `val_pad`, `dsum_pad`, `supp_mono`, `update_top`, `shift_*`, `unshift_*` | (plumbing) | ✅ proved |
| `ones_rep`, `ones_erase_rep`, `exists_rep_le`, `exists_rep_lt`, `exists_rep_compl` | §6 Prop. 1 (master achievability criterion), existence half | ✅ proved |
| `dsum_succ_of_lt`, `exists_dsum_eq` | Lemma 3 (digit sum), contiguity (upward) half | ✅ proved |
| **`theoremB`** | **§6 Theorem B — lower bound, all four cases** | ✅ **proved** |
| `gmin`, `gmin_add_le`, `gmin_add_pow`, `gmin_ones` | §4 greedy digit sum $`s_{\min}`$, top-coin / all-ones values | ✅ proved |
| `gmin_le_dsum` | Lemma 3 (digit sum), minimality (downward) half | ✅ proved |
| `ones_unique` | Lemma 2 ($`V \ne 0`$) | ✅ proved |
| `dsum_le_val`, `val_le_dsum_mul` | §3 trivial range $`n \le M \le n \cdot 2^{n-1}`$ | ✅ proved |
| `gmin_step` | §5 Lemma 4 (step), $`s_{\min}(M + 2^n - 2^t) \ge s_{\min}(M) + 1`$ | ✅ proved |
| `slack` | §5 slack bound $`s_{\min}(M_j) \ge n + j`$, induction on $`j`$ | ✅ proved |
| **`theoremA`** | **§5 Theorem A — upper bound / validity** | ✅ **proved** |
| **`nmin_eq`** | **Main theorem, `IsLeast {N ∣ 2 ≤ N ∧ Valid n N} (2^n − 2^m)`** | ✅ **proved** |

## Proposition 2: elementary abelian 2-groups

[`MinModulus/ElemAbelian2.lean`](MinModulus/ElemAbelian2.lean) formalizes
Proposition 2: if $`g_0, \dots, g_{n-1} \in (\mathbb{Z}_2)^k`$ have unique
multiset sums, then $`k \ge n - 1`$. Equivalently, the least elementary abelian
$`2`$-group admitting such a family has order $`2^{n-1}`$.

The theorem `MinModulus.elementaryAbelianTwoGroups_optimal` matches the paper's
statement: `UniqueMultisetSums` quantifies over multiplicity vectors
$`m : \mathrm{Fin}\ n \to \mathbb{N}`$ with $`\sum_i m_i = n`$, and casting
$`m_i`$ into $`\mathbb{Z}_2`$ before scaling gives the correct multiset sum in
$`(\mathbb{Z}_2)^k`$. The conclusion `n - 1 ≤ k` (truncated subtraction) is
equivalent to $`k \ge n - 1`$.

The proof follows the paper's argument: the map $`\Lambda(x) = \sum_i x_i g_i`$
and the coordinate-sum functional are built as linear maps; a nonzero
$`u \in \ker \Lambda \cap \ker(\mathrm{sum})`$ has even positive support $`S`$,
and doubling half of $`S`$ while dropping the other half yields a size-$`n`$
multiset with the same group sum but a multiplicity $`\ne 1`$, contradicting
uniqueness; rank–nullity then gives
$`n = \mathrm{rank}\ \Lambda + \dim \ker \Lambda \le k + 1`$.

The hypothesis is non-vacuous: $`n = 2`$, $`k = 1`$, $`g = (0, 1)`$ satisfies it
and meets the bound with equality.

## Open problem 4: all finite abelian groups

[`MinModulus/AbelianMin.lean`](MinModulus/AbelianMin.lean) formalizes Inal's
resolution of the paper's fourth open problem. Write $`n = m + 1`$. A tuple
`g : Fin (m+1) → G` in a finite abelian group `G` is **valid** (`ValidTuple`) if
the all-ones vector is the only $`k : \mathrm{Fin}\ (m+1) \to \mathbb{N}`$ with
$`\sum_i k_i = m + 1`$ and $`\sum_i k_i \cdot g_i = \sum_i g_i`$. Let
$`m_{\mathrm{ab}}(n)`$ be the least order of a finite abelian group admitting a
valid tuple. Then $`m_{\mathrm{ab}}(n) = 2^{n-1}`$.

The key observation is that validity forces the translated differences
$`g_{j+1} - g_0`$ to be **dissociated**: their subset-sum map
`ssum g : Finset (Fin m) → G` is injective (`ssum_injective`), which embeds the
Boolean cube into `G`.

| Lean declaration | Corresponds to (Inal) | Status |
|---|---|---|
| `ValidTuple`, `diff`, `ssum` | Definitions (validity, differences, subset-sum map) | ✅ defined |
| `not_collision_disjoint`, `ssum_injective` | Lemma 3.1 — validity forces dissociation | ✅ proved |
| **`card_ge`** | **Cor. 3.2 — lower bound `2^(n-1) ≤ |G|`** | ✅ **proved** |
| `elem_valid`, `elem_card` | Prop. 3.3 — sharpness (standard tuple in $`(\mathbb{Z}_2)^{n-1}`$) | ✅ proved |
| **`mab_isLeast`** | **Thm. 1.1 — `m_ab(n) = 2^(n-1)`, as `IsLeast`** | ✅ **proved** |
| `diff_order_two`, `equality_order_two`, `ssum_bijective` | Thm. 4.1 — the extremal group is elementary abelian | ✅ proved |
| **`equality_classification`** | **Thm. 4.1 — differences form an $`\mathbb{F}_2`$-basis** | ✅ **proved** |
| **`equality_addEquiv`** | **Thm. 1.1 — explicit $`\phi : G \to (\mathbb{Z}_2)^{n-1}`$, $`\phi(g_i - g_0) = e_i`$** | ✅ **proved** |

The lower bound `card_ge` holds for *every* finite abelian group, strengthening
Proposition 2 (which is restricted to elementary abelian $`2`$-groups) and the
previously available counting bound $`\binom{2n}{n}/2^n`$. At equality, a second
use of validity (representing $`2(g_i - g_0)`$ as a subset sum and rivalling the
all-ones vector with a multiplicity-3 entry) shows every difference has order
two; combined with the bijectivity of `ssum`, the differences form an
$`\mathbb{F}_2`$-basis, so — up to translation and isomorphism — the only
extremal tuple is $`(0, e_1, \dots, e_{n-1})`$ in $`(\mathbb{Z}_2)^{n-1}`$.

This settles the abelian minimum-order question (open problem 4). It is separate
from Conjecture 1 (minimality of $`N`$ over all residue sets in $`\mathbb{Z}_N`$),
which remains open.

## Deviations from the paper proof

* **Theorem B** constructs the four witness representations directly by
  induction on bit-width with a parity split, instead of certifying them
  via `s_min`/popcount.
* **Theorem A** avoids popcount entirely and follows the paper's §5
  route directly. `gmin w M` (binary digits of `M` below bit `w`, plus the
  whole quotient on the top coin) is defined by the one-bit-peeling recursion
  `gmin (w+1) M = M % 2 + gmin w (M / 2)`, so every proof is an induction
  whose steps only use literal `/2`, `%2` — `omega` handles all arithmetic.
  `gmin_step` is the paper's Lemma 4 (subtraction encoded as
  `M' + 2^t = M + 2^{w+1}`), proved by bit-peeling with a parity split;
  `slack` iterates it over `j` from the base `gmin_ones`. No range
  restriction on `j`, no `Nat.log` case analysis, no small-`n` evaluations.
* Lemma 2 (`ones_unique`) is a descent on the bottom coin: parity forces
  `k 0 = 1 + 2t`, and `gmin_le_dsum` + `gmin_add_le` force `t = 0`.

## Formalization notes (kept for reference)

- `omega` treats `2^w` as an **opaque atom**, but *does* abstract nonlinear
  products (`j * N`) as atoms — provide bridging equations by `ring` and let
  omega finish linearly. Corners that are vacuous on paper via pow semantics
  need explicit case splits feeding omega the reduced facts.
- Mathlib v4.32 names: `Nat.lt_two_pow_self` (argument implicit),
  `Function.update_of_ne` / `Function.update_self`,
  `Nat.log_eq_of_pow_le_of_lt_pow` for concrete `Nat.log` values (does **not**
  reduce by `decide`). Note `Finset.range_subset` now means
  `range n ⊆ s ↔ ∀ x < n, x ∈ s`; the `range m ⊆ range n ↔ m ≤ n` form is
  `Finset.range_subset_range`.
- Goals of the form `val w (fun i => …) = …` are stated about a lambda;
  `rw`/`omega` need the beta-reduced shape — open such proofs with `show`,
  or reuse `shift_*` through a pointwise `Finset.sum_congr`.
