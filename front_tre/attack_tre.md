# 奇正则图 f_re 分解攻击报告（软靶 #4，续攻棒）

**靶子**：arXiv:2509.01901 (Akbari–Aloni–Beikmohammadi–Clow) Conjecture 6.4：每个 n 阶 (2k+1)-正则图满足 f_re(G) ≤ n−1（f_re = 分解为 2-正则子图与单边的最小块数）。

## 摘要（5 行）

1. **攻击框架全线打通**：建立分解归约定理 R（f_re = min over 偶子图 H of (m−|H|+Δ(H)/2)，完全证明），把猜想化归为奇宇称生成子图计数 p(G) 的上界；立方情形精确化 f_re = p+1，猜想 ⟺ p2(G) ≥ n/2+2（p2 = 最大偶子图）。
2. **无完美匹配情形（原开放核心）化归为纯结构问题**：桥分解引理 p = Σq(X_i)+B（完全证明，每桥必入 F 的奇偶论证）+ 拼装引理（块树度守恒 Σb=2(k−1) ⟹ r ≥ c+t+2，完全证明）+ 片引理（无桥 subcubic 块的圈打包下界）。
3. **片引理已闭合（查新接管，原 GAP 解除）**：无桥 subcubic 块的圈打包下界 p2 ≥ n/2+3/2 是 CKKPW 2019（Graphs Combin. 35(4), Thm 1.3）的即时特例——原归纳证明卡在"删点后奇阶单块 +1"，两条绕行路线被机器反例封死，恰是 CKKPW 自述困难核心；机器验证 n ≤ 14 无桥 subcubic 全量（60,077 张）p2 ≥ n/2+3/2 零违反，紧例 K_{2,3}（旧报「p2−n/2 ≥ 2 恒成立」系 sweep 整数除法口径错误，已更正，见文末修复记录）。
4. **计算完备验证**：cubic n ≤ 18 全量（上一棒 n ≤ 12 共 9,588 张 + 本次 45,870 张）猜想与 Claim R 零违反；**极小无完美匹配立方图 = n=16（恰 1 张；极小性已知：Chartrand–Goldsmith–Schuster 1979 + Errera 1922，归属见 §7）**，结构 = 3 个细分 K4 叶片 + 1 个三桥中心点，其 p = n/2+1；n=18 的 4 张 PM-free 图同构于"7点片 + 2×细分K4 + 中心点"。
5. **k ≥ 2**：Tutte 障碍型 5-正则 PM-free 构造族（n = 36..146）Claim R (p ≤ n−3) 全过；框架归约 f_re ≤ p+k 已完全证明，k ≥ 2 的片引理对应物未攻。

**结论强度：立方情形完全证明（依赖已发表定理）**——无完美匹配立方图 f_re ≤ n−1 无条件成立；片引理由 CKKPW 2019 Thm 1.3 闭合，**依赖已发表定理 CKKPW 2019 Thm 1.3，本报告贡献 = 归约链 + 桥分解 + 拼装 + 计算验证**；k ≥ 2 情形给出框架归约与计算支持；全题（一般 (2k+1)-正则）未完全解决。

---

## 1. 靶子精确表述（原文核对）

原文 §6（Future Work，main.tex 行 806–810）：

> **Conjecture**: For all n vertex (2k+1)-regular graphs G, f_re(G) ≤ n−1.

上下文（行 804–806）："A nice special case is to solve this conjecture for regular graphs. Notice that Petersen's 2-factor theorem implies it is sufficient to prove the result for (2k+1)-regular graphs. We note that the result is easy to show for (2k+1)-regular graphs with a perfect matching."

即：偶正则由 Thm 1.5（f_re = Δ/2 ≤ n−1）已解；奇正则含完美匹配情形原文一句带过（见 §4.1 推论 2）；**开放核心 = 无完美匹配的奇正则图**。

与上游任务描述一致，无偏差。

**原论文瑕疵核查**：front184 战役的 Y1–Y3（campaign/PREPUB_REVIEW.md）经查是我方自己报告中三处"被标完全证明实则有洞"的证明缺口（lane_06/lane_12），**不是原论文的瑕疵**；原论文 Thm "Even Delta" 已在 front184 G6 条目中与我方本地源码逐字核对一致。本棒未发现原论文新瑕疵，与既往记录无重复。

## 2. 遗产交接

上一棒遗产（/Users/munich/Desktop/数学/front_tre/）：
- `fre_lib.py`（Graph/min_tjoin/p_odd/f_re_exact/f_re_setcover/max_cycle_packing_ILP）、`fast_ver.py`（向量化 DP + networkx 花算法 + geng 解析）、`anchors.py`（7 组锚点）、`sweep.py`/`sweep2.py`、`results.jsonl`（n ≤ 12 全量 9,588 张）、`results2.jsonl`（**空**——上一棒死于配额，sweep2 未跑成）。
- **复跑锚点**：本棒复跑 `anchors.py`，全部 PASS（含 f_re DP vs 集合覆盖独立双路核对、ℓ 的 ILP 交叉验证、定理 R 上界一致性、K6/K4 = n−1 紧例）。
- **上一棒数据**：results.jsonl 覆盖 n ≤ 12 全部连通奇正则图（k=1..5），Claim R（p ≤ n−1−k）违反 0，f_re 精确值（m ≤ 20 的 116 张）违反 0。
- **sweep2 死因定位**：`f_re_exact_fast` 的 `assert m <= 20` 会在 cubic n=14（m=21）处崩；本棒放宽到 m ≤ 22 并重写扫描器（sweep3.py）。

## 3. 框架定理（本棒完全证明）

**约定**：f_re 的块 = 2-正则子图（每点度恰 2、不需生成，即不交圈的并）与单边（K₂）；n = |V|，m = |E|；p(G) = min{|F| : F ⊆ E(G) 生成、每点 deg_F 奇}（最小奇宇称生成子图 = T=V 的最小 T-join）；p2(G) = max{|H| : H ⊆ G、每点 deg_H 偶}（最大偶子图 = 不交圈并，当 G subcubic）。

### 定理 A（分解归约）
**f_re(G) = min over 偶子图 H ⊆ G of ( m − |H| + Δ(H)/2 )**。

**证明**：
(≤) 给定偶子图 H。原文 Theorem 1.5（Even Delta）的证明（构造二部正则化 G₀ = 两侧 V 副本 + 欧拉迹转移边 + (Δ/2 − deg v) 重 v₁v₂ 平行边，König 分解为完美匹配）对**一般偶图** H 成立，产出 Δ(H)/2 个"每点度 ∈ {0,2}"的生成子图分解 H。G−H 的每条边单独成单边块。合计 (m − |H|) + Δ(H)/2 块 ⟹ f_re ≤ RHS。
(≥) 取最优分解（t 个 2-正则块 + s 个单边），令 H = t 个块的边并：每点 v 在 r_v 个块中，deg_H(v) = 2r_v 偶 ⟹ H 是偶子图；Δ(H)/2 = max_v r_v ≤ t ⟹ RHS 处取值 s + Δ(H)/2 ≤ s + t = f_re ⟹ min ≤ f_re。
两者夹合，等号成立。∎

**推论 A1（奇正则上界）**：G (2k+1)-正则 ⟹ f_re(G) ≤ p(G) + k。
取 F = 最小奇宇称生成子图（|F| = p），则 G−F 每点度 (2k+1) − deg_F(v) 为偶 ⟹ G−F 偶图，Δ ≤ 2k ⟹ 由定理 A，f_re ≤ p + k。∎

**推论 A2（含完美匹配情形，即原文 §6 的观察）**：取 F = 完美匹配：p ≤ n/2，G−F 是 2k-正则 ⟹ f_re ≤ n/2 + k ≤ n−1 ⟺ n ≥ 2k+2；正则性给 n ≥ Δ+1 = 2k+2。∎（有 PM 的奇正则图完全解决。）

**推论 A3（立方精确公式）**：G 立方 ⟹ **f_re(G) = p(G) + 1**。
由定理 A：F 全奇 ⟹ deg_{G−F} ∈ {0, 2}（subcubic）⟹ H = G−F 是不交圈并 ⟹ Δ(H)/2 ∈ {0,1} ⟹ f_re = min(|F| + [H ≠ ∅]) = min(p+1, m)。而 G 含圈 C ⟹ F = G−E(C) 每点度 1 或 3 全奇、|F| = m−|C| ≤ m−3 ⟹ p ≤ m−3 < m ⟹ f_re = p+1。∎
**等价形式**：p = m − p2 ⟹ **立方猜想 ⟺ p2(G) ≥ n/2 + 2**。

## 4. 主定理链（立方、无完美匹配）

### 定理 C（桥分解，完全证明）
G 连通立方、Br = 桥集、B = |Br|。块 = G − Br 的连通片 X₁,…,X_k（无桥 subcubic，δ ≥ 2，度 ∈ {2,3}；b_v := v 的关联桥数）。则
**p(G) = Σ_i q(X_i) + B**，其中 q(X_i) = X_i 上 T_i = {v ∈ X_i : b_v 偶} 的最小 T-join。

**证明**：
(1) 每条桥 e 必入任何全奇生成子图 F：设 e 割出 A（|A| 侧）。若 e ∉ F，则 F∩E(A) 在 A 内的奇度点集 = V(A)（全点），而任何子图的奇度点数为偶（握手引理）；又 3|A| − 1 = 2e(A) ⟹ |A| 奇，矛盾。故 e ∈ F。
(2) 于是 v 的 F-度 = deg_{F∩X_i}(v) + b_v，规范 deg_F ≡ 1 (mod 2) ⟹ deg_{F∩X_i} ≡ 1 + b_v (mod 2)，即 F∩X_i 是 T_i-join；T_i 在每块内偶数个点（由 3n_i − Σb = 2e(X_i) ⟹ Σb ≡ n_i，故 #{b 偶} ≡ 0）。反向：各块任取 T_i-join + 全部桥 ⟹ 全奇生成子图。求和取最小即得。∎
（完备性双验：dbd_sub_k4 锚点 p = 2+2+1 = 5 = m−ℓ 一致；sweep3 全部 PM-free 图上 Σq+B = p 无一例外。）

### 片引理 Φ（已闭合；归功于 CKKPW 2019，本棒独立复推换算链）
**陈述**：X 连通无桥 subcubic，n ≥ 3。则 **p2(X) ≥ n/2 + 3/2**。
**推论形式**：对任意 b 规范（deg_X(v) = 3 − b_v，b_v ∈ {0,1}），q(X, {b 偶}) ≤ e(X) − n/2 − 3/2，即 **Φ(X) := n − q(X) ≥ b(X)/2 + 3/2**。
（相容性：全偶子图 H 对任何规范自动合法，因 deg_{X−H} = (3−b_v) − 偶 ≡ 1 + b_v 恒成立。）

**引理 A（外部已发表定理）**：I. Choi, R. Kim, A. V. Kostochka, B. Park, D. B. West, *Largest 2-regular subgraphs in 3-regular graphs*, **Graphs and Combinatorics 35(4) (2019) 805–813**（DOI 10.1007/s00373-019-02021-6，arXiv:1903.08795）Theorem 1.3：subcubic n 点（多）图有 c 条割边、1-deficit d = 3n − 2m，则 **f2(G) ≥ n − max{0, (d+c−1)/2}**，且界紧；f2 = 最大 2-正则子图的顶点数。等式情形（连通，其 Thm 1.6）当且仅当删去全部割边后每个分量是单点、balloon、或 G 族（2-连通立方二部多重图删一点后逐点"爆炸"所得）。

**引理 B（换算：subcubic 上 p2 = f2）**：偶子图 H ⊆ X 每点度 ≤ 3 且为偶 ⟹ 度 ∈ {0,2} ⟹ 每个连通分量全度 2 ⟹ 是圈，故 H 是顶点不交圈的并且 |E(H)| = |V(H)|；反之 2-正则子图是偶子图且边数 = 顶点数。故按边数的最大偶子图 = 按顶点数的最大 2-正则子图，即 p2 = f2。∎

**片引理证明**：X 连通无桥 ⟹ c = 0。三分支：
- (i) 全度 2：X 是圈，p2 = n ≥ n/2 + 3/2（⟺ n ≥ 3）✓。
- (ii) 全度 3（n 必偶）：d = 3n − 2·(3n/2) = 0，引理 A 给 f2 ≥ n − max{0, −1/2} = n ⟹ p2 = n ✓（此分支即 Petersen 1-因子定理：无桥立方图有 2-因子）。
- (iii) 混合（兼有度 2、度 3 点）：d = Σ_v (3 − deg v) ≥ 1（度 2 点贡献 ≥ 1、各项 ≥ 0）；且 2m = Σdeg ≥ 2n + 1 又为偶 ⟹ 2m ≥ 2n + 2 ⟹ m ≥ n + 1。引理 A：
  **p2 = f2 ≥ n − (d−1)/2 = n − (3n−2m−1)/2 = m − n/2 + 1/2 ≥ n/2 + 3/2** ✓。
  （d 偶时右边为半整数：实数不等式链照常成立，p2 取整数只会更富余。）
∎

**推论形式换算（本棒复推）**：设 |X| = n、e(X) = m。取 p2 对应的最大偶子图 H，则 deg_{X−H}(v) = deg_X(v) − deg_H(v) ≡ (3 − b_v) − {0,2} ≡ 1 + b_v (mod 2)，奇度点集恰为 {b_v 偶} ⟹ X − H 是该 T-join ⟹ q ≤ m − p2。于是
Φ(X) = n − q ≥ n − m + p2 ≥ n − m + n/2 + 3/2 = (3n − 2m)/2 + 3/2 = b/2 + 3/2，
末步用 X 上握手：Σ_v deg_X = 3n − b = 2m ⟹ b = 3n − 2m。∎

**紧例（引理 A 等式刻画的 G 族）**：C₃（n=3，p2 = 3 = n/2+3/2）与 **K_{2,3}（n=5，p2 = 4 = n/2+3/2）**——本棒计数器双路复核：T-join p2 = 4 = ILP 圈打包；1-deficit d = 3n−2m = 3，引理 A 界 n − (d−1)/2 = 4 恰取等；K_{2,3} = K_{3,3} 删一点，即 Thm 1.6 G 族最小成员。

**机器验证（口径已修正，2026-09-14）**：P0 于 n ≤ 14 全部 **60,077** 张连通无桥 subcubic 图（geng -c -D3 全量枚举 + 无桥过滤）**零违反**；真值余量 min(2p2 − n) = 3，即 **p2 − n/2 ≥ 3/2 恒成立**，全局唯一紧例 n=5 的 K_{2,3}（g6=`DFw`，已验同构）；偶数 n ≤ 14 余量 ≥ 4（p2 ≥ n/2+2 于偶数 n 成立）。
**[2026-09-14 更正]** 旧版报告称"p2 − n/2 ≥ 2 恒成立（n ≤ 14，59,036 张）"系 sweep3.py 旧版**整数除法口径错误**：旧代码检验 `p2 < N//2 + 2`，奇数 n 上 ⌊n/2⌋+2 = n/2+3/2，故该检查恒等价于 P0 本身——P0 的验证结论不受影响，但"强版 n/2+2"从未在奇数 n 上被检验，且旧日志标签 min(p2 − N//2) 虚高 0.5。已修复 sweep3.py 并全量重跑（resweep_c.log / results3.jsonl）；旧版张数 59,036 与重跑实测 60,077 不符（旧一次性 heredoc 无法复算，以可复现的 geng 全量数为准）。

**历史注记（原 GAP 为何卡死）**：原归纳证明卡在"删点后 X₁ 为奇阶连通无桥单块、需 p2(X) ≥ p2(X₁) + 1"——两条补法均被机器反例封死：(a) 拆点提升（n ≤ 11 共 5,585 对 (X,v) 中 756 对反例，search_gap.py 可复算）；(b) 奇阶强化（K_{2,3}：p2 = 4 < (5+4)/2）。这与 CKKPW 原文自述的困难核心完全吻合（§2："The difficult case is when c = 0 and d > 0"，其解法用 Edmonds 加权匹配 + Plesník 定理）：此 +1 本质需要重活，CKKPW 已完成，故直接引用。

### 拼装引理（完全证明）
设 G 连通立方无完美匹配，块树节点 = 块 k 个（r 个"正片"n ≥ 4、c 个 C₃ 型、t 个单点型），B = k−1 条桥。
(i) 度守恒：Σ_i b(X_i) = 2B = 2(k−1)（每桥两端各记 1）。
(ii) 每块 b ≥ 1（块树连通）；单点 b = 3、C₃ b = 3（度规范 3 − b_v）。
(iii) 2(k−1) = Σb ≥ 3(c+t) + 1·r ⟹ **r ≥ c + t + 2**。
(iv) 块节省：正片 Φ ≥ b/2 + 3/2（片引理）；C₃：q = 0（T = ∅，b ≡ 1）、Φ = 3 = b/2 + 3/2；单点：Φ = 1。
(v) 总账：ΣΦ ≥ Σ_{正}(b_i/2 + 3/2) + 3c + t = B − 1.5(c+t) + 1.5r + 3c + t = B + 1.5r + 1.5c − 0.5t ≥ B + 1.5(r − t) ≥ **B + 2**（由 (iii)：1.5(r+c) − 0.5t ≥ 1.5·(c+t+2) + 1.5c − 0.5t ≥ 2）。
（数值复核：n=16 极小 PM-free 图实测 ΣΦ = 10 ≥ B+2 = 5；n=18 四张 ΣΦ = 11 ≥ 5。）∎

### 定理 D（主定理，立方情形；无条件）
**每个无完美匹配的连通立方图 G 满足 f_re(G) ≤ n − 1。**
证明：Petersen 1-因子定理逆否 ⟹ G 有桥 ⟹ k ≥ 2；定理 C ⟹ p = Σq + B = n − ΣΦ + B ≤ n − (B+2) + B = n − 2；推论 A3 ⟹ f_re = p + 1 ≤ n − 1。∎
片引理 Φ 已闭合（CKKPW 2019 Thm 1.3 + 引理 B 换算，见 §片引理），故本定理**无条件**成立。
**结论强度（诚实声明）**：完全证明**依赖已发表定理 CKKPW 2019 Thm 1.3**（其证明动用 Edmonds 加权匹配 + Plesník 定理）。本报告的独立贡献 = 归约链（定理 A + 推论 A1–A3）+ 桥分解（定理 C）+ 拼装引理 + 计算验证（n ≤ 18 立方全量、n ≤ 14 无桥 subcubic 全量、k=2 构造族）。

## 5. 计算验证（完备性论证）

| 范围 | 图数 | 检查 | 结果 |
|---|---|---|---|
| cubic n ≤ 12 全量（上一棒） | 9,588 | Claim R (p ≤ n−2)、定理 B (ℓ ≥ n/2+2)、f_re 精确（116 张 m ≤ 20） | 0 违反 |
| cubic n = 14 全量 | 509 | 同上 + f_re 精确（m=21 DP，上限放宽至 22） | 0 违反 |
| cubic n = 16 全量 | 4,060 | Claim R + 定理 B + PM-free 块分析 | 0 违反 |
| cubic n = 18 全量 | 41,301 | 同上 | 0 违反 |
| 无桥 subcubic n ≤ 14 全量 | 60,077 | 片引理 P0（p2 ≥ n/2+3/2，真值口径 2p2 ≥ n+3） | 0 违反，min(2p2−n) = 3，紧例 K_{2,3}；偶数 n 余量 ≥ 4（p2 ≥ n/2+2） |
| 5-正则 PM-free 构造族 t = 1..6 | 5 张（n=36..146） | Claim R (p ≤ n−3) + 5-正则性 + 连通性 | 全过 |

**完备性与正确性论证**：
1. **枚举完备**：geng -c -d3 -D3 n / -c -D3 n 生成全部连通立方/最大度 3 简单图（nauty，标准工具）；连通性与正则性在代码中二次断言。
2. **双路核对**：p 的两条独立路径（蛮力 min_tjoin 配对枚举 vs 度量闭包+networkx 最大权匹配）在全部锚点图与随机 40 张 5-正则图上一致（fast_ver.py 自检）；f_re 的两条路径（子集 DP vs 精确覆盖分支定界）在 7 组锚点一致；p2 的 ILP 交叉验证（max_cycle_packing_ILP，scipy.milp）在 K_{2,3}/K₃₃/三棱柱等一致。
3. **阳性锚点**：已知可分解图全部找回（K4/K6 = n−1 紧例、Petersen = 6、C5 = 1、P_4 = 3 等，anchors.py 全 PASS）。
4. **零解声明**：n ≤ 18 立方全量与 n ≤ 14 无桥 subcubic 全量为**完备枚举**（非抽样），零违反是完备命题。
5. **资源纪律**：全程单线程、峰值内存 < 300MB（2²² int8 数组 ≈ 59MB），总计算约 20 分钟，未触碰 swap 红线。2026-09-14 口径修正复跑（resweep_c：n ≤ 14 无桥 subcubic 全量 60,077 张）另加单线程约 40s、峰值内存 < 200MB，复跑前后 swap 均低于 12.5GB 红线。
6. **[2026-09-14 更正]** 上表"无桥 subcubic"行旧记录（59,036 张、min margin = 2）为整数除法口径错误（详见 §片引理更正与文末修复记录第 2 条）；本行数字已按修正后复跑结果更新。

## 6. k ≥ 2 情形

**框架**：推论 A1（f_re ≤ p + k）完全证明 ⟹ k ≥ 2 时猜想由 **Claim R：p(G) ≤ n−1−k** 导出。
**PM-free 结构差异**：k ≥ 2 时"无 PM ⟹ 有桥"不再成立（3q ≤ (2k+1)s 计数不排除无桥 Tutte 障碍），桥分解路线失效；Tutte 障碍 S（o(G−S) > |S|）是正确的割结构，片归纳需按 S-分量重做（未攻）。
**可用外部工具（KRTWZ，2026-09-14 查新补注）**：Kostochka–Raspaud–Toft–West–Zirlin（arXiv:1806.05347）：(2r+1)-正则图割边数 ≤ 2^r − 3(k−1) ⟹ 存在 2k-因子。对本路线直接有用：一旦图有 2k-因子 F，则 G−F 是 1-因子，f_re ≤ n/2 + k ≤ n−1（同推论 A2，n ≥ 2k+2 恒真）——即"有 2k-因子 = 该图已解决"。故 k ≥ 2 的残余难点被精确化为**割边数 ≥ 2^r − 3(k−1) + 1 的图**（k=1 时阈值退化为 ≤2 割边，即 Petersen 定理，恰是本报告已解的立方情形）；S-分量片归纳的目标图类由此锁定，Hanson–Loten–Toft（(2r+1)-正则 ≤ 2^r 割边 ⟹ 2-因子）是其 k=1 特例。
**构造族**：Tutte 障碍型 5-正则 PM-free 链（K₇ 缺 4 边枝 ×t 挂中心链），n = 36, 58, 80, 102, 146 全部确认 PM-free 且 p = 20, 33, 46, 59, 85，**全部满足 p ≤ n−3 且余量巨大**（p ≈ 0.58n ≪ n−3）。数值上 k=2 远离危险区。

## 7. 观察（2026-09-14 归属更正：已知对象的独立重发现 + 结构刻画）

**极小无完美匹配立方图 = 16 阶，恰 1 张**（g6=`O???E?oBEAWOKGK_@o?W_`）：块结构 = 3 × 细分K₄ 叶片（n=5, b=1, q=2, Φ=3 全紧）+ 1 个三桥中心单点（Φ=1）；p = 9 = n/2 + 1。n=18 的 4 张 PM-free 图均为"7点片(Φ=4) + 2×细分K₄ + 中心点"（p = 10 = n/2+1）。
**归属（查新回填）**："16 阶为极小无完美匹配连通立方图"是**已知结果**：G. Chartrand, D. L. Goldsmith, S. Schuster, *A sufficient condition for graphs with 1-factors*, **Colloquium Mathematicum 41(2) (1979)**, Corollary 2a（p. 343 陈述最小性，p. 341 有图；该图即 MathWorld GraphData[{"Cubic",{16,104}}]）。更早的 **Errera (1922)**：连通立方图的桥若全落在一条单路上则有完美匹配——与 Petersen ≤2 桥定理合取，正是"PM-free ⟹ 桥 ≥ 3 且三桥聚于一点"结构的文献对应物。**本棒新增价值 = n ≤ 18 全量枚举确认 16 阶唯一性 + 上述块结构 / p 值刻画**；原「新观察」标题据此降级。
规律：**实测全部 PM-free 立方图 p = n/2 + 1，且超 budget 恰好全部来自单点片**（正片 q = (n_i − b_i)/2 恒取等）。若能证明"非单点块恒 q ≤ (n−b)/2"，则 p ≤ n/2 + t，配合"PM-free ⟹ t ≥ 1"得到 p ≤ n/2 + t 与 t 的上界控制——主定理立方情形已闭合，此路线降级为 k ≥ 2 片归纳的备选素材（θ 全长块是反例障碍：q = ℓ_min > 1）。

## 8. Lean 4 形式化目标陈述

```lean
-- 定义层（mathlib 有 simple_graph；f_re 需自定义）
noncomputable def f_re (G : SimpleGraph V) : ℕ :=
  sInf {t | ∃ (D : Finset (SimpleGraph V)), t = D.card ∧
    (∀ H ∈ D, (∀ v, H.deg v = 2 ∨ H = ⊥) ) ∧ G = D.sup id}  -- 2-正则块 + 单边

-- 定理 A（分解归约）
theorem theorem_A (G : SimpleGraph V) [DecidableEq V] :
    f_re G = ⨅ (H : {H : SimpleGraph V // ∀ v, Even (H.deg v)}),
      (G.edgeFinset.card - H.val.edgeFinset.card) + (maxDeg H.val) / 2 := by sorry

-- 立方精确公式
theorem cubic_exact (G : SimpleGraph V) (hG : ∀ v, G.deg v = 3) :
    f_re G = minTjoinCard G (F : _ := Set.univ) + 1 := by sorry

-- 片引理 hlemma 去假设化（2026-09-14）：片引理不再是未证 GAP，而是外部已发表定理的推论：
--   CKKPW 2019 (Graphs Combin. 35(4):805-813) Thm 1.3 + 换算 p2 = f2（subcubic，见报告 §4 引理 B）。
-- 形式化路径：作为引用型外部公理引入，不在本仓库重证（其证明依赖 Edmonds 加权匹配 + Plesník）。
axiom ckckpw_thm13 (X : SimpleGraph W) (hconn : X.Connected) (hbr : X.Bridgeless)
    (hn : 3 ≤ Fintype.card W) :
    maxEvenSubgraphEdges X ≥ Fintype.card W / 2 + 3/2
  -- 引用型：Choi–Kim–Kostochka–Park–West, Thm 1.3 + 1-deficit 换算；mathlib 化是后续工作

-- 主定理（无条件版）
theorem main_cubic_pmfree (G : SimpleGraph V) (hG : ∀ v, G.deg v = 3)
    (hconn : G.Connected) (hnoPM : ¬∃ M, G.IsPerfectMatching M) :
    f_re G ≤ Fintype.card V - 1 := by sorry
```

## 9. 遗留与下一步攻击方向

1. ~~**闭合片引理 GAP**（最高优先）~~ **【已闭合，2026-09-14，查新接管】**：片引理由 CKKPW 2019 Thm 1.3 + 换算闭合（见 §片引理），原三条候选处置：
   a. 【证实】"p2 ≥ (n+3)/2 for bridgeless subcubic 极可能是已知结果"——出处即 **CKKPW Thm 1.3**（Librarian 检索未找到对应片引理的 Kaneko 定理，"Kaneko 类"猜测作废）；
   b. 【被接管】"临界图结构"计划不必从零做：**CKKPW Thm 1.6 已给出全等式刻画**（等式 ⟺ 删割边后每分量是单点 / balloon / G 族；本报告实测紧例 K_{2,3} 即 G 族最小成员 = K_{3,3} 删一点）；本条机器观察（n ≤ 14 临界图 τ(度2点) ≤ 1 或非单块删点）保留为 Thm 1.6 的独立佐证；
   c. 【降级为可选】"单点片唯一超 budget"拼装路线对主定理不再必需（片引理已闭合），保留为 k ≥ 2 片归纳素材（θ 核块 Φ ≥ 2 + 2β/3 的下界观察仍有效）。
2. **k ≥ 2 的片引理对应物**：近 (2k+1)-正则块（一点缺度）的偶子图下界；Tutte 障碍 S-分量归纳框架。k ≥ 2 无桥 PM-free 奇正则图的存在性本身值得机器搜索（5-正则 n ≤ 22）。
3. **强化数值**：cubic n = 20（3,833,568 张，约 20 小时单线程，需资源窗口）与 5-正则 n = 14 全量。
4. **文献核对清单**（Librarian 已回，2026-09-14，详见 librarian_gap_check.md）：
   ① 【已答】Petersen 1-因子定理多重图版：可引 CKKPW §1 现代表述（"every cubic multigraph with at most two cut-edges has a 2-factor and (equivalently) a 1-factor"），归 Petersen 1891（Acta Math. 15, 193–220）；Lovász–Plummer 书内定理编号未核实（书不可及，查新声明）。
   ② 【已答】bridgeless subcubic 圈打包已知界 = CKKPW Thm 1.3 + Corollary 1.2（cubic 简单图 f2 ≥ min{n, ⌈5(n+2)/6⌉}；无环多重图 ⌈3(n+2)/4⌉）。
   ③ 【弃用】"2-connected subcubic 周长 ≥ (n+3)/2 的紧例刻画"：检索未找到直接来源（现有文献集中于 3-connected/cubic 渐近周长：Bondy–Simonovits 1980、Jackson），该命题真伪未验证；其等式刻画需求由更强的 CKKPW Thm 1.6 结构定理替代——**此路线正式弃用**（弃用理由：投入产出劣于直接引用 Thm 1.6，且命题本身未验证不能作为证明支点）。
   ④ 【已答】极小 PM-free cubic = 16 阶：已知（Chartrand–Goldsmith–Schuster 1979, Colloq. Math. 41(2), Cor. 2a + Errera 1922；与 Sylvester 图族无关），归属详见 §7。

## 附：可复算脚本（/Users/munich/Desktop/数学/front_tre/）

- `anchors.py`：全部锚点自检（python3 anchors.py，全 PASS；2026-09-14 修复后复跑仍全 PASS）。
- `sweep3.py`：本次主扫描（cubic 14/16/18 + PM-free 块分析 + 片引理 n≤14 + k=2 构造族）→ `results3.jsonl`（实测 45,897 行 = 45,870 cubic + 10 旧片引理记录 + 11 新口径片引理记录 + 5 构造族 + 1 gap_search 备注；旧附录写 45,882 系上一棒少计 4 行，已按实测更正）、`sweep3.log`。**2026-09-14 修复**：片引理段抽为 `run_piece_lemma_sweep()`（真值口径 2p2−n，含强版违反与 argmin 记录），k=2 构造族抽为 `run_k2_family()`，main 按序调用。
- `resweep_c.py` → `resweep_c.log`：口径修正后片引理全量重跑入口（n=4..14，60,077 张，单线程约 40s）；结果追加 `results3.jsonl`（键 viol_p0 / viol_strong / min_margin2 / argmin_g6）。
- `search_gap.py`（或本次以 heredoc 运行的版本）：片引理残缺对搜索（n ≤ 11：5,585 对、756 残缺）——历史注记材料（原 GAP 的反例封路），保留可复算。
- 理论依赖的原论文源码：/Users/munich/Desktop/数学/front184/2509.01901_src/main.tex（Conjecture 6.4 在行 806–810）。
- 查新报告：`librarian_gap_check.md`（CKKPW 2019 全家桶、n=16 图归属、靶子查重、谱系一页纸）。

## 修复记录（2026-09-14，Librarian 查新结果应用；蓝队单次通过）

1. **GAP 段替换**（清单项 1）：§4「片引理 Φ」整段重写——原归纳证明 + GAP 声明替换为「引理 A（CKKPW 2019 Thm 1.3，含全引用条目与 Thm 1.6 等式刻画）+ 引理 B（subcubic 上 p2 = f2 换算）+ 三分支推导」。换算链**独立复推**（未照抄查新文本）：p2 = f2（偶子图度 ∈ {0,2} ⟹ 顶点不交圈、边数 = 顶点数）；1-deficit 对齐（d = 3n−2m = Σ(3−deg v)，混合情形 d ≥ 1）；无桥 ⟹ c = 0；m ≥ n+1（2m ≥ 2n+1 且为偶）；n − (d−1)/2 = m − n/2 + 1/2 ≥ n/2+3/2；圈分支（n ≥ 3）与立方分支（d = 0 直接由 Thm 1.3 给 f2 ≥ n）平凡。推论形式换算（X−H 是 T-join ⟹ q ≤ m−p2；握手 b = 3n−2m）亦复推通过。**未发现推不通的环节**。
2. **一致性疑点裁决**（清单项 2）：查新员正确。K_{2,3}（n=5，连通无桥 subcubic）p2 = 4（fre_lib 的 T-join 与 scipy.milp ILP 双路一致），p2 − n/2 = 1.5 < 2；CKKPW 界 n−(d−1)/2 = 4 恰取等（d = 3）。根因：sweep3.py 旧版第 C 段用整数除法 `N//2`——奇数 n 上「p2 ≥ ⌊n/2⌋+2」恒等价于 P0 本身（= n/2+3/2），故 **P0 验证结论不受影响**，但「强版 p2 ≥ n/2+2」从未在奇数 n 上被检验，且旧日志标签 min(p2−N//2) 虚高 0.5。处置：修 sweep3.py（真值口径 2p2−n）并全量重跑 n=4..14：**P0 零违反，min(2p2−n) = 3，全局唯一紧例 K_{2,3}（g6=DFw，已验同构）；偶数 n 余量 ≥ 4**。旧报张数 59,036 与实测 60,077 不符（旧一次性 heredoc 不可复算，以 geng 可复现全量为准）。报告摘要 3、§4 片引理、§5 表格同步改为「p2 ≥ n/2+3/2 恒成立，K_{2,3} 型紧例」。
3. **定理 D 升级**（清单项 3）：§4 定理 D「条件性」→ 无条件；摘要结论强度行改为「立方情形完全证明（依赖已发表定理）」并明写**依赖已发表定理 CKKPW 2019 Thm 1.3，本报告贡献 = 归约链 + 桥分解 + 拼装 + 计算验证**；§8 Lean 主定理删去 hlemma 假设，片引理改为引用型 axiom（注释指向 CKKPW Thm 1.3 + 换算），原 sorry 待办清单保留。
4. **§9 处置**（清单项 4）：1.a 猜想【证实】（出处 CKKPW Thm 1.3；"Kaneko 类"猜测作废）；1.b 临界结构计划【被 CKKPW Thm 1.6 接管】（等式 ⟺ 单点 / balloon / G 族，K_{2,3} = G 族最小成员）；1.c 拼装替代路线【降级为 k ≥ 2 素材】；文献清单 ③（2-connected subcubic 周长命题）【弃用，弃用理由：检索无直接来源、命题真伪未验证、功能被 Thm 1.6 替代】；①②④ 按查新结果回填（Petersen 1891 / CKKPW Cor 1.2 / CGS 1979 + Errera 1922）。
5. **归属补注**（清单项 5）：§7 标题「新观察」→「观察（已知对象的独立重发现 + 结构刻画）」，正文补引 Chartrand–Goldsmith–Schuster 1979（Colloq. Math. 41(2), Cor. 2a）与 Errera 1922（桥聚一条路 ⟹ 有 PM = 「三桥聚于一点」的文献对应物），本棒新增价值收窄为「n ≤ 18 全量枚举确认唯一性 + 块结构 / p 值刻画」；摘要 4 同步补引。
6. **k ≥ 2 补注**（清单项 6）：§6 加 KRTWZ（arXiv:1806.05347）：(2r+1)-正则、割边 ≤ 2^r − 3(k−1) ⟹ 2k-因子；有 2k-因子即解决该图（补 = 1-因子，f_re ≤ n/2+k ≤ n−1），故 k ≥ 2 残余难点精确化为割边数 ≥ 2^r−3(k−1)+1 的图，为 S-分量片归纳锁定目标图类。
7. **锚点复跑**（清单项 7）：`python3 anchors.py` 全部 PASS（7 组：T-join、p_odd、ℓ ILP 交叉、f_re DP vs 集合覆盖、定理 A 上界、立方 f_re = p+1、K6/K4 紧例）；修好的 sweep3.py 经空输出冒烟（C 段 n=4..5 + D 段）确认函数边界与口径正确、n=5 紧例复现。资源纪律：全程单线程 + nice，峰值内存 < 300MB，swap 始终低于 12.5GB 红线。
