# 攻击报告 R2：n=8 障碍突破——加法组合工具攻击裸区

**攻击手（R2 棒）** | 2026-09-13 | 接续：attack_tmm.md（T-02）+ reports/soft-targets-2026-09-12.md 候选 2

---

## 头部摘要（5 行）

1. **新判据（引理 A）**：A={0}∪B valid mod N ⟺ 每个非空 Q⊆B 的和 δ_Q 不可由 B∖Q 中 ≤|Q|+1 个元素（可重复）表出——单模数精确判定程序，与原始定义 3819 例机器核对零失配。
2. **新下界（定理 B，严格证明）**：n=8 valid ⟹ N ≥ 134（N 偶）/ N ≥ 135（N 奇）；一般 n：N ≥ 2^{n−1}+n−2（偶）/ +n−1（奇）。
3. **勘误（重要）**：T-02 推论 4 的「N ≥ 145」计数步骤无依据（2·S₃ 的像可合法落入低层槽位），予以撤回；严格覆盖边界实为 **N ≤ 133**，裸区修正为 **[134, 247]（114 个模数）**。
4. **全裸区精确搜索战役已 nohup 托管**（C 内核，双锚点验证：K=6 在 N*=124 找到 420 个 valid 集含超递增、N*=−1 即 123 严格零解）：**N=128..134 已完成，全部 0 valid（N=134 仅 31.5s）——n=8 验证边界已实际推过 134**，战役升序推进中，任一 N 完成即继续推边界。
5. 产出：`attack_r2_checks.py`、`attack_r2_search.c`、`attack_r2_campaign.py`、日志 `r2_logs/`；本机无 Lean 工具链，形式化陈述已备（§6）。

---

## 结论强度（三选一）

**部分进展**：证明侧交付引理 A（精确判据）+ 定理 B（新下界，覆盖 N ≤ 133）+ T-02 推论 4 勘误 + 终局约束族（引理 C）；计算侧交付单模数判定程序并已托管全裸区 [134, 248] 战役（首战 N=128 已完成：0 valid）。未证明、未反例；Conjecture 1 在 n=8 仍开放。

---

## 0. 与 T-02 的差异（必读勘误）

**撤回**：T-02 §4.2 推论 4「valid ⟹ N ≥ 2^{n−1} + ½C(n−1,⌊n/2⌋)」（n=8 给 145）。该计数把 2·S₃∖{0} 的 ≥⌈35/2⌉ 个像当作「被迫落在 Σ(B) 之外」的增量，但定理 3 只禁止 2x（x∈S₃）落入 S₅∪S₆∪S₇（29 个槽位），它**可以合法落入 S₀..S₄（99 个槽位）或补集**；逐值纤维 ≤ 2（x 与 x+N/2 配对）的记账优化下，全层合并的被迫增量只有个位数（本报告定理 B 严格化为 6）。故「工具覆盖 N<145」不成立，正确边界是 N ≤ 133。

**旁证**：该公式在 n=2 已与事实矛盾（{0,1} 在 N=2 valid，而公式给 N ≥ 3）——它从未是定理，只是与 n ≤ 5 数据相容的猜测。T-02 验证器核对的是定理 3 本身（真），不是推论 4 的计数（未被任何论证支撑）。

**修正后的战区**：证明覆盖 N ≤ 133；裸区 **[134, 247]，114 个模数**；N=248 为超递增集的阳性锚点。

---

## 1. 记号与归约（沿 T-02）

n = 8，A = {a₀ < … < a₇} ⊂ ℤ_N，平移不变（引理 0）WLOG a₀ = 0，记 B = {b₁,…,b₇} = A∖{0}（bᵢ ∈ [1, N−1] 升序）。判据 W（T-02 引理 1，本机已复核）：A invalid ⟺ ∃ c ≠ 0：Σcᵢ = 0，min cᵢ ≥ −1，Σcᵢaᵢ ≡ 0 (mod N)。

## 2. 引理 A（预算判据 / MC 判据）——本轮主工具

**引理 A**。A = {0} ∪ B（|B| = 7）valid mod N **⟺** 对每个非空 Q ⊆ {1,…,7}：

> δ_Q := Σ_{i∈Q} bᵢ **不可**表示为 B∖Q 中至多 |Q|+1 个元素（可重复、含空和 0）之和（mod N）。

**证明**。
（⟸ 反证）设违反：存在 Q、ε ∈ {0,1}、多重集 P（取值于 B∖Q，|P| = |Q| + ε 以下）使 Σ_P ≡ δ_Q。构造 c：cᵢ = mult_P(i)（i ∈ supp P），cᵢ = −1（i ∈ Q），c₀ = |Q| − |P| ≥ 0（若 ε = 1 则把一个 a₀ 记入 Q 的负部、c₀ 相应 = |Q|+1−|P| ≥ 0）。逐项：Σc = |P| − |Q| + c₀ = 0 ✓；min cᵢ ≥ −1 ✓；c ≠ 0（Q ≠ ∅）✓；Σcᵢaᵢ = Σ_P − δ_Q + c₀·0 ≡ 0 ✓。由判据 W，A invalid。
（⟹ 反证）设 A invalid，取判据 W 的 c。令 Q = {i ≥ 1 : cᵢ = −1}，ε = 1_{c₀ = −1}，P = {bᵢ 的 mult_P(i) = max(cᵢ,0) 份}。平衡 Σc = 0 给 c₀ = |Q| + ε − |P| − ε·1 ⟹ |P| ≤ |Q| + 1（预算式）；支撑不交 ✓；同余 Σ_P ≡ Σ_Q − c₀·0 +（ε 项的 a₀ 贡献为 0）⟹ Σ_P ≡ δ_Q ✓。故违反引理 A 右侧。∎

**注**：(a) 预算 |Q|+1 恰吸收 a₀ ∈ 负部的情形；预算与 n 无关，对一般 n 成立。(b) P = ∅ 情形即「δ_Q ≢ 0」（子集和零自由）。(c) MC 单独已蕴含 dissociation（子集和两两不同）：若 P、Q ⊆ B 不交、|P| = |Q|、Σ_P ≡ Σ_Q，则 |P| ≤ |Q|+1 自动满足。
**机器核对**（attack_r2_checks.py）：与原始 multiset 定义在 n = 2..4 全穷举 + n = 5..7 随机抽样共 **3819 对上零失配**；超递增锚点 n = 5..8 在 N* 处均复现 valid。

**引理 B2（元素二倍避让；定理 3 的 s=1 情形，自足证明）**。valid ⟹ 对所有 i, j ≥ 1：2bᵢ ≢ bⱼ。
证：2bᵢ ≡ bⱼ 给 c = 2eᵢ − eⱼ − e₀：Σc = 0，min = −1，Σcᵢaᵢ = 2bᵢ − bⱼ ≡ 0，witness。∎
（亦由引理 A 取 Q = {j}，P = {i, i}，|P| = 2 ≤ 2 直接得出。）因此每个非零二倍 2bᵢ ∈ COMP := ℤ_N ∖ Σ(B)。

## 3. 定理 B（二倍记账下界）——新的严格覆盖边界

**引理 B1（子集和单射 / dissociation）**。valid ⟹ B 的 2⁷ = 128 个子集和 mod N 两两不同。
证：设 T ≠ T′，Σ_T ≡ Σ_T′。P = T∖T′，Q = T′∖T 均非空，Σ_P ≡ Σ_Q；WLOG |P| ≤ |Q| + 1（否则交换两侧，同余取负仍成立）。c = 1_P − 1_Q + (|Q|−|P|)e₀：Σc = 0 ✓，min ≥ −1 ✓，c ≠ 0 ✓，Σcᵢaᵢ ≡ 0 ✓。与 valid 矛盾。∎（B1 亦是引理 A 的直接推论。）

**引理 B3（配对至多一个）**。设 N 偶。称 {u, u+N/2} ⊆ B 为一对。
(a) B 至多含一对：两对 {u,u′},{v,v′} 给出两个不同 2-子集 {u,v′} 与 {u′,v}，其和同为整数 u+v+N/2 —— 与 B1 矛盾。
(b) 若 N/2 ∈ B 则零对：{u, N/2} 与 {u′} 和相同（u+N/2 = u′）—— 2-子集 vs 1-子集碰撞，与 B1 矛盾。∎

**定理 B**。A valid mod N（n = 8）⟹ **N ≥ 134**；且 **N 奇 ⟹ N ≥ 135**。一般 n：N ≥ 2^{n−1}+n−2（N 偶）/ 2^{n−1}+n−1（N 奇）；n = 2 时两侧均紧。

证：二倍映射 x ↦ 2x 在 B 上的纤维：2x ≡ 2y（x ≠ y）⟺ N | 2(x−y)，|x−y| < N ⟹ x−y = ±N/2（N 偶）⟺ 恰为 B3 的一对；故二倍值只在对内碰撞，互异二倍值个数 = |B| − (对数)。又 2bᵢ ≡ 0 ⟺ bᵢ = N/2（至多一个元素）。
- N 奇：2 可逆、零对、无零二倍：7 个互异非零二倍 ∈ COMP（B2）⟹ N ≥ 128 + 7 = 135。
- N 偶、N/2 ∈ B：零对（B3b）：7 个互异二倍、其一为 0：COMP ≥ 6 ⟹ N ≥ 134。
- N 偶、N/2 ∉ B：至多一对（B3a）：互异二倍 ≥ 6，全非零：COMP ≥ 6 ⟹ N ≥ 134。∎

**机器核对**：全部 233 个已遇 valid (A,N)（n ≤ 5 穷举 + 抽样）及超递增锚点 n = 5..8 上零违反。

**推论（覆盖边界）**。n=8 的证明覆盖区 = N ≤ 133（偶 N ≤ 132、奇 N ≤ 133，合并即全体 N ≤ 133）。裸区 = [134, 247]。

## 4. 引理 C（高预算约束族；终局机制候选）

由引理 A 直接读出（证明略——逐条代入）：
(i) 取 Q = B∖{j}（|Q| = 6，预算 7）：p − bⱼ ∉ {k·bⱼ : 0 ≤ k ≤ 7}，即 **p ∉ {3bⱼ,…,8bⱼ}** 对每个 j（0、bⱼ、2bⱼ 情形已被 B1/B2 覆盖）。
(ii) 取 Q = B∖{j,l}：p − bⱼ − b_l ∉ {i·bⱼ + k·b_l : i + k ≤ 6}。
这一族把 p = Σbᵢ 与每个元素的重数结构锁死，是「valid + N ≤ 247 ⟹ 结构逼近超递增 ⟹ 但超递增需要 248」型稳定性论证的原料。本轮未完成该稳定性定理（见 §8 GAP-1′）。

## 5. 计算战役：单模数精确判定（已 nohup 托管）

**判定程序 = 证明**：对固定 N，
1. 升序 DFS 枚举 B：前缀剪枝 = 子集和集无碰撞（dissociation 的精确必要条件；256 位掩码、循环移位实现）；
2. 节点级 F-prune（sound）：F(C) = ∪_{R⊆C} rot_right(reach(C∖R, |R|+2), Σ_R)；候选 x ∈ F(C) ⟺ 插入 x 后 Q = R∪{x} 型碰撞已可见（补集增大不消灭碰撞 ⟹ 安全跳过）；
3. 叶子级：引理 A 完整检查（完备性由此保证：任何违规 Q 的最大元素被插入时若 P 侧需更大元素，则由叶检查捕获）；
4. 每个正解再用原始 multiset 定义独立复核（`Direct(7)`）。
零输出（未截断）⟺ **该 N 无 valid 8-集**——对单个 N 是完整证明。

**正确性验证链**（全部通过后才放行战役）：
- 引理 A ⟺ 原始定义：3819 例零失配（Python）；
- Python 枚举器（同 F-prune 逻辑）K=2,3,4 对暴力全枚举双向一致（8 个 N × 3 个 K）；
- C 内核 vs Python 暴力（K=7，N=9..16）：一致；
- **阳性锚点**：K=6 变体在 N=124（= n=7 的 N*）找到 **420 个 valid 集**（含超递增 (1,3,7,15,31,63)，全部过原始定义复核）；N=123 完整跑完零解（与 n ≤ 7 的 CP 验证一致）；
- K=7 阳性终锚点 N=248 排在战役末尾：应找到超递增 (1,3,7,15,31,63,127) 及其单位伸缩。

**状态**：`nohup python3 attack_r2_campaign.py --start 128 --end 248 --per-n-seconds 1800`（PID 见 `r2_logs/campaign.log` 头部；首轮实测 N=128：28.4s 完成，0 valid，nodes=2.3e7——与定理 B 一致）。完成序为升序，每个完成的 N 即把 n=8 的验证边界推过该 N；被截断的 N 标 `incomplete`，重跑同命令自动续。

**监控**：`tail -f r2_logs/campaign.log`；反例会以 `!!!!! COUNTEREXAMPLE` 大声报告；结果流 `r2_logs/results.jsonl`。

**量级注记**（供 Experimenter 接手）：F-pruned 树在 N≈130 约 2×10⁷ 节点（分钟级/N），随 N 增长（N=248 在 300s 内未完，约 10⁸ 节点量级）；10 线程下全裸区预计数小时至一天。进一步提速方向：NEON 向量化 rotl、按 (b₁,b₂) 动态调度、对 depth ≤ 3 跳过 F 计算。

## 6. Lean 陈述（接续作者仓库框架；本机无工具链，未编译）

```lean
/-- 引理 A：预算判据（B : Fin 7 → ZMod N 单射、非零）。 -/
theorem mc_criterion {N : ℕ} (hN : 2 ≤ N) (B : Fin 7 → ZMod N)
    (hinj : Function.Injective B) (hz : ∀ i, B i ≠ 0) :
    ValidGen (vecCons 0 B) ↔
    ∀ Q : Finset (Fin 7), Q.Nonempty →
      ¬ ∃ m : Fin 7 → ℕ, (∀ i, i ∈ Q → m i = 0) ∧ (∑ i, m i ≤ Q.card + 1) ∧
        (∑ i in Q, B i) = ∑ i, m i • B i

/-- 引理 B1：子集和单射。 -/
theorem subset_sums_injective {N : ℕ} (A : Fin 8 → ZMod N) (hval : ValidGen A)
    (hA0 : A 0 = 0) : (Set.range fun (s : Fin 7 → Bool) => ∑ i, if s i then A (i.castSucc.succ) else 0).InjOn id
  -- 形式化时以「 Fin 7 → Bool 的 128 个子和两两不同」的直陈式为准

/-- 定理 B：二倍记账下界（n = 8）。 -/
theorem double_bookkeeping {N : ℕ} (A : Fin 8 → ZMod N) (hval : ValidGen A)
    (hA0 : A 0 = 0) (hinj : Function.Injective A) :
    134 ≤ N ∧ (Odd N → 135 ≤ N)

/-- 引理 B3(a)：两对 {u, u+N/2} 不共存（N 偶）。 -/
theorem at_most_one_pair {N : ℕ} (hNe : 2 ∣ N) (A : Fin 8 → ZMod N)
    (hinj : Function.Injective A)
    (hdis : Set.InjOn (fun (s : Fin 7 → Bool) => ∑ i, if s i then A (i.castSucc.succ) else 0)
              (Set.univ : Set (Fin 7 → Bool))) :
    ¬ ∃ u v w z : ZMod N, u + v = N ∧ w + z = N ∧
      (∀ e ∈ ({u, v, w, z} : Finset _), e ∈ Set.range A ∧ e ≠ 0) ∧
      ({u, v} ∩ {w, z} = ∅ : Prop)
```

（`subset_sums_injective` 的陈述在实现时应改为标准的 `Function.Injective (fun s : Fin 7 → Bool => …)`；`hdis` 假设即 B1。）

## 7. 自我反例攻击记录（本轮实际抓到的 bug）

按纪律每件工具先自击再上阵，共抓到 6 个 bug，其中 2 个致命：
1. MC 比对时忘做 a₀=0 平移规范化（n=3 即爆）——平移不变引理 0 必须显式执行；
2. **Direct 复核器多重集遍历用了 K 个下标而非全部 K+1 个**（漏掉最大元素的三连拷贝碰撞）——由自测的 missed 列表模式（(4,5)@6、(1,16)@31 全是「最大元素自身倍数」碰撞）定位；
3. **C 内核 leaf_valid 读全局 B 而线程填的是局部 barr**——导致永远零解，K=6 阳性锚点（124 应有解）当场抓出。教训固化为纪律：**验证链必须含阳性锚点**，零解一致性是弱检验；
4. `-DK=6` 被文件内 `#define K 7` 覆盖（编译警告定位）；
5. Python 闭包内 `|=`/`^=` 对集合变量构成重绑定（两次 UnboundLocalError）；
6. 随机抽样 N < n 时 sample 越界（低危）。

## 8. 遗留与下一步

1. **[GAP-1′]（主缺口，承接 T-02 GAP-1）**：「循环群非 2-挠的代价」的稳定性定理：valid + N ≤ 247 ⟹ B 结构逼近超递增 ⟹ 需要 248。引理 C 的约束族 (i)(ii) 是原料；战役产出的逐 N 禁止结构数据（qkill 直方图、各 N 的 dissociated 集计数）是实验侧弹药。
2. **战役收尾**：若 [134,247] 全部 complete 且零 valid —— n=8 全裸区 CP 验证完成（Conjecture 1 的 n=8 情形获得「计算辅助证明」地位，且 N=248 阳性锚点自检）；若出现 COUNTEREXAMPLE——即猜想反例，需立即用独立实现复核。
3. **证明侧下一棒**：把引理 A + 定理 B 形式化进作者仓库（§6 陈述已备，两者证明皆短）；攻击稳定性定理（GAP-1′）。
4. **提速**（若 Experimenter 接手大 N）：NEON 化 256 位 rotl；(b₁,b₂) 级动态调度；depth ≤ 3 跳过 F 计算。
5. T-02 遗留小问题（valid 时 ord(aᵢ) 精确下界）仍开放。

## 9. 文件清单（本轮新增）

- 报告：`/Users/munich/Desktop/数学/front_tmm/attack_tmm_r2.md`（本文件）
- 数学检查：`/Users/munich/Desktop/数学/front_tmm/attack_r2_checks.py`（引理 A ⟺ 原始定义、定理 B/定理 3-s1 零违反审计）
- 搜索内核：`/Users/munich/Desktop/数学/front_tmm/attack_r2_search.c`（编译产物 `r2search`、`r2search6`）
- Python 枚举器（自测基线）：`/Users/munich/Desktop/数学/front_tmm/attack_r2_search.py`
- 战役驱动：`/Users/munich/Desktop/数学/front_tmm/attack_r2_campaign.py`
- 运行数据：`/Users/munich/Desktop/数学/front_tmm/r2_logs/`（campaign.log、results.jsonl、pilot.jsonl）
- 复用：`/Users/munich/Desktop/数学/front_tmm/verify_tmm.py`（T-02 验证器，判据实现独立拷贝于 checks 脚本）
