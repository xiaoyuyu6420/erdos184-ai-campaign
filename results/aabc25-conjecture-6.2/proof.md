# A complete proof: 6-regular graphs, three 2-factors, and `ce ≤ n − 2`

*Self-contained. The three results are: the 4-regular lemma (Lemma 2), the bound $\mathrm{ce}(G) \le n-2$ for 6-regular graphs with $n \equiv 0 \pmod 3$ (Theorem 4), and Conjecture 6.2 of [arXiv:2509.01901](https://arxiv.org/abs/2509.01901) verbatim (Theorem 5).*

---

## 0. Notation and statements

All graphs are finite and **simple** (no loops, no multiple edges). $n = |V(G)|$, and $\deg$ denotes degree.

- A **2-factor** of $G$ is a spanning 2-regular subgraph: a disjoint union of cycles, each of length $\ge 3$. A **triangle factor** is a 2-factor all of whose components are triangles.
- A **cycle–edge decomposition** of $G$ is a partition of $E(G)$ into parts, each of which is a cycle or a single edge. $\mathrm{ce}(G)$ denotes the minimum number of parts in such a decomposition.
- $L(B)$ is the **line graph** of $B$: its vertices are the edges of $B$, two adjacent when the corresponding edges of $B$ share an endpoint.
- A graph is **cubic** if it is 3-regular, and **$k$-regular** if every vertex has degree $k$.

**Lemma 1 (Petersen).** *Every $2k$-regular simple graph decomposes into $k$ edge-disjoint spanning 2-factors.*

**Lemma 2 (4-regular lemma).** *Every 4-regular simple graph $G$ with $|V(G)| \ge 5$ has a 2-factor containing a cycle of length at least $4$.*

**Proposition 3 (the flip).** *Let $B$ be a cubic bipartite simple graph, $W = L(B)$, and $M$ a perfect matching of $B$. For any orientation $\sigma$ of $M$ let $\Phi(\sigma) \subseteq E(W)$ be the edge set constructed in Lemma 2, steps (4)–(5), and let $-\sigma$ be the reversed orientation. Then*
$$E(\Phi(\sigma)) \;\sqcup\; E(\Phi(-\sigma)) \;=\; E(W),$$
*and both $\Phi(\sigma)$ and $\Phi(-\sigma)$ are triangle-free 2-factors (every component has at least $4$ vertices).*

**Theorem 4 (strengthened bound).** *Every $6$-regular simple graph $G$ on $n = 3m \ge 9$ vertices satisfies $\mathrm{ce}(G) \le n - 2$.*

**Theorem 5 (= Conjecture 6.2 of arXiv:2509.01901, verbatim).** *Every 6-regular graph is decomposable into three 2-factors, where one of these 2-factors has a component with at least 4 vertices.*

**Corollary 6.** *Every $6$-regular simple graph satisfies $\mathrm{ce}(G) \le n-1$.*

**Remarks** on tightness, dependencies and related work are in §5.

---

## 1. Lemma 1 (Petersen's 2-factorization)

*Proof.* Every component of a $2k$-regular graph has all degrees even, hence is Eulerian. Orient the edges of each component along an Euler tour, so that every edge is oriented exactly once and at every vertex the out-degree equals the in-degree, both equal to $k$.

Build a bipartite graph $B(G)$: on the left the copies $v_{\text{out}}$, on the right the copies $v_{\text{in}}$, with one edge $u_{\text{out}} \!-\! v_{\text{in}}$ for each arc $(u,v)$ of the orientation. Then $B(G)$ is $k$-regular and bipartite, so it has a perfect matching: for $S$ a set of left vertices, the $k|S|$ edges leaving $S$ all enter $N(S)$, and every vertex of $N(S)$ absorbs at most $k$ of them, so $|N(S)| \ge |S|$ (Hall). Removing a perfect matching leaves a $(k-1)$-regular bipartite graph; iterating gives $k$ edge-disjoint perfect matchings.

Each perfect matching corresponds to a set of arcs in which every vertex of $G$ has exactly one outgoing and one incoming arc, hence a disjoint union of directed cycles. A directed 2-cycle $u \to v$, $v \to u$ would need both $(u,v)$ and $(v,u)$ to be arcs; but each edge of $G$ was oriented exactly once, and a simple graph has only one edge between $u$ and $v$. So every directed cycle has length $\ge 3$, and the underlying undirected subgraph is a spanning 2-factor. The $k$ matchings give $k$ edge-disjoint spanning 2-factors partitioning $E(G)$. $\blacksquare$

## 2. Lemma 2 (every 4-regular graph has a 2-factor with a cycle of length ≥ 4)

*Proof.* Suppose the contrary: **every** 2-factor of $G$ is a union of triangles. We derive a contradiction in eight steps.

**(1) Two edge-disjoint triangle factors.** By Lemma 1 with $k=2$, $E(G) = E(F) \sqcup E(F')$ where $F, F'$ are spanning 2-factors. By assumption both are triangle factors. Write $n = 3m$ and note $m \ge 2$ (as $n \ge 5$ and $3 \mid n$).

**(2) Two triangles meet in at most one vertex.** Let $\tau$ be a triangle of $F$ and $\sigma$ a triangle of $F'$. If two distinct vertices $a,b$ belonged to both, then the edge $ab$ would belong to both (a triangle is a clique on its three vertices), contradicting $E(F) \cap E(F') = \varnothing$. So $|V(\tau) \cap V(\sigma)| \le 1$.

Every vertex $v$ lies in exactly one triangle $\tau(v)$ of $F$ and exactly one triangle $\sigma(v)$ of $F'$. If two distinct vertices $v,v'$ of the same triangle $\tau$ had $\sigma(v) = \sigma(v')$, then $|V(\tau) \cap V(\sigma(v))| \ge 2$, contradicting the previous paragraph. Hence:

> the three vertices of any $\tau \in F$ lie in three **distinct** triangles of $F'$ (and symmetrically).

In particular, if $m = 2$ there are not even three triangles in $F'$ to host the vertices of a single $\tau$ — a contradiction. So $m \ge 3$ for a hypothetical counterexample.

**(3) $G$ is the line graph of a cubic bipartite graph.** Construct a bipartite graph $B$: the two sides are the triangle sets of $F$ and of $F'$, and **each vertex $v$ of $G$ contributes one edge $e_v$ of $B$ joining $\tau(v)$ to $\sigma(v)$.** By (2), $B$ is simple (a double edge would mean some pair $\tau, \sigma$ shares two vertices), bipartite by construction, and cubic (every triangle has exactly three vertices, hence degree $3$ in $B$; $|E(B)| = n = 3m = 3|V(B)|/2$).

Moreover $G \cong L(B)$: the vertices of $G$ correspond bijectively to the edges of $B$, and for two vertices $u \ne v$ of $G$,
$$u \sim_G v \iff \text{the edge } uv \text{ lies in } F \text{ or } F' \iff u, v \text{ share a triangle} \iff e_u, e_v \text{ share an endpoint in } B .$$
The first equivalence holds because $E(G) = E(F) \sqcup E(F')$ is exactly the union of the triangle edge sets.

**(4) A perfect matching, oriented.** $B$ is cubic bipartite, so it has a perfect matching $M$ (Hall, as in Lemma 1). Orient every edge of $M$ arbitrarily. For a vertex $x$ of $B$, let $e_x$ be its matching edge (so $x$ is either the **tail** or the **head** of $e_x$), and let $f_x, g_x$ be the other two edges at $x$.

**(5) The construction $\Phi$.** An edge of $L(B)$ is a pair of edges of $B$ sharing a unique vertex (unique because $B$ is simple). For each $x$, the three pairs
$$P_x \;=\; \bigl\{\{e_x,f_x\},\ \{e_x,g_x\},\ \{f_x,g_x\}\bigr\}$$
are edge-disjoint across different $x$, so $E(L(B)) = \bigsqcup_x P_x$. Define
$$\Phi \;:=\; \bigcup_{x \in V(B)} \begin{cases} \bigl\{\{e_x,f_x\},\ \{e_x,g_x\}\bigr\} & x \text{ a tail of } e_x;\\[2pt] \bigl\{\{f_x,g_x\}\bigr\} & x \text{ a head of } e_x.\end{cases}$$
We view $\Phi$ as an edge set of $G \cong L(B)$; note $\Phi$ takes **two** pairs at tails and **one** pair at heads.

**(6) $\Phi$ is a spanning 2-factor.** Each edge $h = xy$ of $B$ is a vertex of $L(B)$; its degree in $\Phi$ is the number of pairs of $P_x \cup P_y$ that contain $h$.

- If $h \in M$: $h = e_x = e_y$, and $x$, $y$ are its two ends, one a tail and one a head. The tail end contributes the two pairs containing $h$; the head end contributes none. Degree $2$.
- If $h \notin M$: then $h \in \{f_x,g_x\}$ at $x$. If $x$ is a tail, $h$ is paired with $e_x$; if $x$ is a head, $h$ is paired with the other non-matching edge at $x$. Either way exactly **one** pair at $x$ contains $h$, and likewise exactly one at $y$. Degree $2$.

So every vertex of $L(B)$ has $\Phi$-degree $2$: $\Phi$ is a spanning 2-regular subgraph, i.e. a disjoint union of cycles (each of length $\ge 3$, as $G$ is simple).

**(7) $\Phi$ contains no triangle.** Three pairwise $\Phi$-adjacent vertices of $G$ correspond to three pairwise adjacent edges of $B$, i.e. to either a triangle of $B$ (impossible, $B$ is bipartite) or to the three edges at one common vertex $x$ — the star $\{e_x,f_x,g_x\}$. For $\Phi$ to contain a triangle at $x$, all three pairs of $P_x$ would have to be in $\Phi$. But $\Phi$ omits at least one pair at every $x$: at a tail, $\{f_x,g_x\} \notin \Phi$; at a head, $\{e_x,f_x\} \notin \Phi$. Contradiction.

**(8) Conclusion.** $\Phi$ is a 2-factor all of whose components have length $\ge 4$, contradicting the assumption that every 2-factor of $G$ is a union of triangles. $\blacksquare$

## 3. Proposition 3 (the flip partitions the edge set)

*Proof.* At each vertex $x$ of $B$: if $x$ is a tail for $\sigma$, then $\Phi(\sigma)$ takes the two pairs $\{e_xf_x\},\{e_xg_x\}$ and $\Phi(-\sigma)$ (for which $x$ is a head) takes $\{f_xg_x\}$; if $x$ is a head for $\sigma$, the roles reverse. In both cases the two edge sets take **complementary** pairs inside $P_x$, and the number of pairs taken is $2+1$ or $1+2$. Since $E(L(B)) = \bigsqcup_x P_x$, we get $E(\Phi(\sigma)) \sqcup E(\Phi(-\sigma)) = E(L(B))$.

Both sets are 2-factors with no triangle: steps (6) and (7) of Lemma 2 used only the **tail/head dichotomy at each vertex**, never the particular orientation, so they apply verbatim to any orientation, in particular to $\sigma$ and to $-\sigma$. $\blacksquare$

**Corollary 3.1 (counting).** In the situation of Proposition 3, if $|V(L(B))| = n$ then $\Phi(\sigma)$ and $\Phi(-\sigma)$ each have at most $1 + \lfloor (n-4)/3 \rfloor$ components.

*Proof.* A triangle-free 2-factor has all components of length $\ge 4$; in particular it has a component of length $\ge 4$, and its remaining components have length $\ge 3$. If there are $c$ components then $n \ge 4 + 3(c-1)$, so $c \le 1 + (n-4)/3$. $\blacksquare$

## 4. Theorem 4, Theorem 5, Corollary 6

### Proof of Theorem 4 ($n = 3m \ge 9$, $6$-regular $\Rightarrow \mathrm{ce}(G) \le n-2$)

Fix a 2-factorization $E(G) = E(F) \sqcup E(F') \sqcup E(F'')$ (Lemma 1, $k=3$).

**Case 1: $G$ has no triangle factor.** Then none of $F,F',F''$ is a triangle factor, so each has a component of length $\ge 4$. A 2-factor on $n$ vertices with a component of length $\ge 4$ has at most $1 + \lfloor (n-4)/3\rfloor = 1 + (m-2) = m-1$ components. Hence the three factors together give
$$\mathrm{ce}(G) \;\le\; 3(m-1) \;=\; n-3 \;\le\; n-2 .$$

**Case 2: $G$ has a triangle factor $S$** (necessarily exactly $m$ triangles). Put $H := G - E(S)$; this is a 4-regular spanning simple graph on $n \ge 9 \ge 5$ vertices.

**Case 2a: $H$ has a triangle factor $T$.** Then $S$ and $T$ are edge-disjoint triangle factors whose union $W := S \cup T$ is 4-regular and spanning. Apply steps (2)–(3) of Lemma 2 to $W$ — these steps use **only** the hypothesis "union of two edge-disjoint triangle factors" and not the assumption of Lemma 2 — obtaining $W \cong L(B)$ for a cubic bipartite simple $B$. By Proposition 3 and Corollary 3.1, $E(W) = E(\Phi(\sigma)) \sqcup E(\Phi(-\sigma))$ with both 2-factors having at most $m-1$ components. The remainder $R := G - E(W) = H - E(T)$ is a spanning 2-factor (degree $4 - 2 = 2$), hence has at most $\lfloor n/3\rfloor = m$ components. Therefore
$$\mathrm{ce}(G) \;\le\; (m-1) + (m-1) + m \;=\; 3m - 2 \;=\; n-2 .$$

**Case 2b: $H$ has no triangle factor.** Decompose $H = T \sqcup U$ into two spanning 2-factors (Lemma 1, $k=2$). Neither $T$ nor $U$ is a triangle factor (each is a 2-factor of $H$, and $H$ has none), so each has at most $m-1$ components, and
$$\mathrm{ce}(G) \;\le\; m + (m-1) + (m-1) \;=\; 3m-2 \;=\; n-2 . \qquad \blacksquare$$

### Proof of Theorem 5 (Conjecture 6.2, verbatim)

Let $G$ be $6$-regular simple on $n$ vertices.

- **If $3 \nmid n$:** a triangle factor would force $n = 3\cdot(\text{number of triangles})$, so $G$ has no triangle factor. Take any 2-factorization (Lemma 1, $k=3$); its first factor is a 2-factor but not a triangle factor, so it has a component with at least $4$ vertices. Done.
- **If $3 \mid n$ and $G$ has no triangle factor:** the same argument applies to any 2-factorization.
- **If $3 \mid n$ and $G$ has a triangle factor $S$:** then $n \ge 9$ (as $6$-regular simple graphs satisfy $n \ge 7$, and $3 \mid n$), so $n \ge 9 \ge 5$. The graph $H := G - E(S)$ is 4-regular spanning simple, so by Lemma 2 it has a 2-factor $S'$ containing a cycle of length $\ge 4$; the complement $T := H - E(S')$ is again a spanning 2-factor. Now
$$E(S) \;\sqcup\; E(S') \;\sqcup\; E(T) \;=\; E(G)$$
is a decomposition into three edge-disjoint spanning 2-factors, and $S'$ has a component with at least $4$ vertices. $\blacksquare$

### Proof of Corollary 6 (all $6$-regular graphs)

If $n \equiv 0 \pmod 3$: a $6$-regular simple graph on $n$ vertices has $n \ge 9$ (as $6$-regular simple graphs satisfy $n \ge 7$), so Theorem 4 gives $\mathrm{ce}(G) \le n-2 \le n-1$. If $3 \nmid n$, take any 2-factorization (Lemma 1, $k=3$): every 2-factor has at most $\lfloor n/3 \rfloor$ components, so
$$\mathrm{ce}(G) \;\le\; 3 \lfloor n/3 \rfloor \;\le\; n-1 . \qquad \blacksquare$$

## 5. Remarks

**(a) Tightness.** We do **not** claim that $n-2$ (or $n-1$) is tight. The bounds come from counting components; the true values are much smaller in the cases we computed exactly: every 6-regular graph on $9$ vertices and every isomorphism class of 6-regular graphs on $10$ vertices has $\mathrm{ce} = 3$. Whether some $6$-regular graph needs $\Theta(n)$ parts is open.

**(b) The $n-3$ question.** The accounting above uses, at best, "$m-1$ components in a factor with a $\ge 4$-cycle, $m$ otherwise". Reaching $n-3$ in the residual configurations (Case 2b with $S$ a triangle factor, and Case 2a when $R$ is itself a triangle factor — e.g. $K_{3,3,3}$, where the true value is $3 \ll 7$) would need a different mechanism; we register it as open.

**(c) Relation to the template paper's own reduction.** [AABC25] observe (source `main.tex:316–318`) that a three-2-factor split with a component of size $\ge 4$ yields $\le n-1$ parts. That reduction is theirs; we use it as the frame, and our Theorem 4 pushes the same accounting to $n-2$ in the last open case. We claim no novelty for the reduction itself.

**(d) Even graphs of maximum degree 6.** Combining Corollary 6 with the reduction recorded in our campaign report [`../../campaign/lane_05_delta6.md`](../../campaign/lane_05_delta6.md) (which shows that for graphs with all degrees even and $\Delta \le 6$, the only remaining case is "$6$-regular with $n \equiv 0 \pmod 3$") gives: **every graph with all degrees even and maximum degree at most $6$ satisfies $\mathrm{ce}(G) \le n-1$.** Tightness for this family is open. (This corollary depends on that internal report, not only on this document.)

**(e) Novelty, stated conservatively.** The structural reduction of Lemma 2, steps (2)–(3) ("every 2-factor a union of triangles $\Rightarrow G \cong L(B)$, $B$ cubic bipartite") we did not find in the literature. The **existence** statement of Proposition 3 is a special case of an observation of Kouider–Sabidussi (1995) — a cubic graph has a perfect matching iff its line graph admits a triangle-free 2-factorization; cubic bipartite graphs always have a perfect matching (Hall). We therefore claim only the **explicit, self-contained construction** (the flip, with its pointwise partition of the adjacency pairs and the "any orientation" quantifier) and its counting consequence. Bertram–Horák (1997) give a polynomial *decision* algorithm for decomposing a 4-regular graph into two triangle-free 2-factors (it can also report impossibility), and we found no characterization of the YES instances in any source we could access — its authors conjectured the corresponding recognition problems to be NP-complete for higher degrees (transcribed in Plummer's 2007 survey, Theorem 6.9 and Conjecture 6.10). Neither paper concerns cycle–edge decompositions. Details and sources: [`README.md`](README.md) and [`../../campaign/harden_round2/bh97_landscape.md`](../../campaign/harden_round2/bh97_landscape.md).

**(f) Where the proofs were checked by machine.** The constructive steps (Petersen factorization, the $\Phi$ construction, the flip, the case analysis) are implemented in [`../../campaign/r2_01_scripts/`](../../campaign/r2_01_scripts/) and independently re-implemented and re-run in [`../../campaign/harden_round2/`](../../campaign/harden_round2/). All checks report zero counterexamples; the known limit is that the exhaustive sweep of the lemma's parameter space covers cubic bipartite $B$ with up to $12$ vertices, i.e. 4-regular graphs $L(B)$ on up to $18$ vertices ($s \le 6$); larger $B$ are covered by the proof only. The full evidence tables are in [`README.md`](README.md) and [`../../campaign/r2_01_aabc25_struct.md`](../../campaign/r2_01_aabc25_struct.md).
