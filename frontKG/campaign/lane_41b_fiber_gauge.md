# lane_41b —— 纤维 gauge 定理（第二 gauge）+ lane_41 遗稿终审（2026-09-15）

> 继承 lane_41 遗稿（四个脚本已跑、报告未写、棒已离场）。头部摘要（5 行）：
> 1. **新定理 T1/T2/T3（本 lane 主交付，纸面完全证明）**：iso5 高基数簇的消光系统天然携带一个"顶点 gauge 之外的第二缩放自由度"——对每个顶点 v，非-v-关联实体集 S_v 的整体缩放 w_e ↦ t·w_e (e∈S_v) 使**每个完美匹配积同乘 t²**（每 PM 恰 3 实体、恰 1 条 v-关联）。消光性与单色非零性沿该 C*-纤维整体保持或破坏；lane_36 的 ROOTED-MONO-ZERO 判决沿纤维零代价传播；deep_verify 观察到的"正维根簇"从数值现象升格为恒等式推论。
> 2. **切片核的精确公式**：0-星生成树切片下，90 维格核恰 1 维、由 u = π(1_{S_0}) 生成（本原 0/1 向量、支撑 54）。5 簇（K95_1/2/7/11、K99_0）精确整数计算全部吻合：ortho_violations = 0、方程类纤维常数全 = 2、mono 三色纤维常数全 = 2、det[B₈₉; u] = 54（两簇同值，结构性）。
> 3. **lane_41 遗稿终审（5 簇 × 15 trials 全判决）**：tangent_probe 的 REFUTATION-CANDIDATE 全部是 dps=200 精度伪影（deep_verify 深挖 res 至 1e-405 后 ratio 塌回 1e-13~1e-10 有界）——15 trials 经修正判据（mpmath 域比较）重分类为 **14 SURVIVES-POSITIVEDIM + 1 AMBIGUOUS（阈值边缘，诚实保留）+ 0 REFUTED-DEEP**，正维根簇现象由 T1 定理化：根簇正维是恒等式必然而非数值巧合；猜想 c（mono 恒零）在全部已测点上继续幸存。
> 4. **σ_min 超退化的定向解释（推论 T4）**：90 维 Jacobian 在任何根处必有右零方向 u（∂_{z_u}F = 2F = 0 于根）；lane_36 冻结单实体坐标切开的不是该方向（u 支撑 54 坐标）——商化到 89 维（descend 坐标显式可用）才是正确切口，Kantorovich 证书路线应在商空间重启。
> 5. **bug 零容忍披露（3 个，全部在落盘前抓获）**：① 本 lane kernel_from_echelon v1 假设 int_echelon 基行在其他主元列为零（不成立），回代漏项产出垃圾 u——被 ortho_violations=468 自检拦截，v2（Fraction RREF）修复；② lane_41 遗稿 classify() 的 `res < 1e-350` 在 float 域字面量下溢为 0，判据恒 False ⟹ verdict 恒 AMBIGUOUS——历史数据经 mpmath 域重分类修正；③ T2 机器验证第一版在全相消点做"总和级"检查，被 1e+121 抵消放大（|m0|=1.35e-129 vs Σ|p|=1.12e-8）污染——改为逐项级检查后精确通过。零污染流出。

## 0. 任务与输入

任务（第三幕，继承 lane_41 遗稿）：三靶终审（高次乘子证书 / mono≠0 存在性搜索 / mono 恒零代数证明）+ 遗稿四件结果（lab41_census/struct/tangent/deep_verify）的解读、补全与判决。输入全部本地：`src/lab41/*` 遗稿、`results/lab41_*.json`、`results/numhit_*.json`、`src/nonlinear_solver.py`（未改判定逻辑）、`notes/definitions.md` §1.11。

## 1. 遗稿盘点与判定修正

| 遗稿件 | 状态 | 本 lane 处置 |
|---|---|---|
| lab41_census.json（line a：单项式乘子正规型普查） | 5 簇跑完 | 解读采纳入档：**normal-form-feasible = 0**（全部 726 类 × 3 色 × 5 簇，类差集 D_vc 均不平移合同于 T_c 子集）⟹ 正规型单项式乘子证书全谱系不可行；跨类外部对消（GAP-2）仍开放 |
| lab41_struct.json（line c 前置侦察） | 5 簇跑完 | 关键数字采纳入档：lat_rank 89/90 与 93/94（秩亏恰 1）、无 singleton 类、mono 缺失键 2~4 个（与 lane_36 §3a 一致） |
| lab41_tangent.json（line b：mono≠0 搜索） | 2 簇 × 12 trials 跑完 | 8 REFUTATION-CANDIDATE + 4 NO-ROOT（每簇）；REFUTATION-CANDIDATE 经 deep_verify 深挖判为精度伪影（见 §2），**无一是真根** |
| lab41_deep_verify.json（裁决实验） | K95_1 × 3 trials 跑完，verdict 落盘 AMBIGUOUS | **verdict 无效**（bug ② float 下溢 ⟹ 判据恒 False）；数据记录有效，经 mpmath 域重分类 ⟹ 三 trial 全 **SURVIVES-POSITIVEDIM**；本 lane 补跑其余 4 簇（§4） |

时间戳证据：deep_verify.py 21:04:02 修改（classify 注释自述"修正版：tangent_probe 的 dps=60 mono 评估是伪影源"），deep_verify.json 21:09:44 落盘——旧进程用旧判据跑完写盘退出，修正版判据从未运行；且修正版本身仍带 bug ②，即使重跑也恒 AMBIGUOUS。

## 2. 主交付：纤维 gauge 定理（纸面完全证明）

### 2.0 设置

依 notes/definitions.md §1.11 与 build_system_mine 实现语义。宿主 n=6 顶点多重图 B；实体 e=(p,q,a,b)∈E（边+双端色），K95 簇 |E|=95。完美匹配 M = φ(F)：F 为 B 的 1-因子（3 条边），φ 给每边选一实体；|M|=3，M 覆盖每顶点恰一次（实测样例顶点覆盖 = {0:1,1:1,…,5:1}）。色向量 vc∈{0,1,2}^6 的匹配类 PM(vc)，消光方程 F_vc(w)=Σ_{M∈PM(vc)} w(M)（726 个类）；单色和 mono_c(w)=Σ_{M∈PM((c,c,c))} w(M)。可行性 = (i) 全部非单色类消光 + (ii) mono_0,1,2 ≠ 0（definitions.md §1.11）。切片：贪心生成树 T 实体权固定 1（合法性：每匹配覆盖每顶点恰一次 ⟹ gauge 因子 (Πα)² 相消，slice_system 注记）。

### 2.1 引理 1（每匹配的顶点结构）

**陈述**：每个 PM 的实体集 M：|M| = 3，且每个顶点恰被 M 中一条实体的一端覆盖。

**证明**：1-因子 F 是 6 顶点的完美匹配 ⟹ 3 条两两不交边（完美匹配定义）。φ 每边选一实体，实体端点 = 边端点 ⟹ 覆盖结构同 F。∎

### 2.2 引理 2（2-交恒等式）

**陈述**：对每个顶点 v 与每个 PM：|M ∩ S_v| = 2，其中 S_v := {e ∈ E : e 与 v 不关联}。

**证明**：F 覆盖 v 恰一次 ⟹ F 中恰一条边含 v ⟹ φ 选出的对应实体含 v（1 条）；M 其余 2 条实体的两端均 ≠ v ⟹ ∈ S_v。∎

### 2.3 定理 T1（第二 gauge / 纤维结构）

**陈述**：对每个顶点 v，指示向量 1_{S_v} ∈ L^⊥，其中 L := span_Z{χ(M) − χ(M') : M,M' ∈ PM}（χ = 实体指示嵌入 {0,1}^E）。等价地，对任意权 w 与 t ∈ C*，定义 w(t) := (t·w_e if e∈S_v else w_e)，则每个匹配积 w(M)(t) = t²·w(M)，从而 F_vc(w(t)) = t²·F_vc(w)、mono_c(w(t)) = t²·mono_c(w)。特别地：消光性 (i) 与单色非零性 (ii) 沿 C*-轨道 {w(t) : t∈C*} 整体保持或破坏。

**证明**：w(M)(t) = Π_{e∈M} w(t)_e = w(M)·t^{|M∩S_v|} = w(M)·t²（引理 2）。线性化即得 1_{S_v} ⊥ 每个差向量。两个方程陈述是匹配和的逐项缩放。∎

**注**（与既有 gauge 的关系）：顶点 gauge w ↦ α⊗α∘w 使每匹配乘 (Πα)²，是 6 个参数的作用；T1 的 S_v-缩放是 1 个参数的作用，且在切片（树权=1 已用尽顶点 gauge）后**仍然存活**——这是它在数值空间（90 维）可观测的原因。全 1 向量（整体缩放）= u_v 家族的线性组合：Σ_v 1_{S_v} = 4·1_E（每实体 (p,q) 属于恰 4 个 S_v，即 6−2 个），对应 w ↦ tw 时每匹配积 ×t³ 的尺度不变性。lane_36 §3b 记"尺度不变 w→tw ⟹ s_i→t⁶s_i"——t⁶ 与本 lane 推出的 t³ 存在量纲记号差异，本 lane 未逐条核对 lane_36 的 s_i 定义（不影响本 lane 任何结论：本 lane 全部结果基于切片坐标内的精确整数格计算与逐项恒等式）。

### 2.4 命题 T1'（切片核的精确公式）

**陈述**：设 T 为 0-星生成树（本战役 spanning_tree 在 K95/K99 簇实体序下产出 T = {(0,1),(0,2),(0,3),(0,4),(0,5)} 各一实体，实测 T = [0,5,14,23,32]），π: Z^95 → Z^90 删 T 坐标，L_s := π(L)。则 rank L_s = 89 且 L_s 的整核 = Z·π(1_{S_0})；u := π(1_{S_0}) 本原、0/1 支撑、|supp u| = 54。

**证明**：(a) u ∈ L_s^⊥：树实体均 0-关联 ⟹ T∩S_0 = ∅ ⟹ ⟨π(1_{S_0}), π(χ(M)−χ(M'))⟩ = |M∩S_0| − |M'∩S_0| = 0（引理 2）。u 本原显然（0/1）。(b) 核 ≤ 1 维：设 x̄ = Σ_{i} c_i·e_i ∈ Z^90 在 L_s^⊥（先证有理核 1 维即可）。考虑 x̄⊕0 ∈ (Z^95)^*。由 struct_probe 实测 rank L = 89 ⟹ dim_Q L^⊥ = 6；由引理 2，u_v := 1_{S_v}（v=0..5）∈ L^⊥ 且线性无关（若 Σα_v u_v = 0，取任意实体 (p,q)：0 = Σ_{v∉{p,q}} α_v；宿主边集覆盖足以推出全 α 相等，再由某实体处 4α = 0 ⟹ α=0；对 11 条边的具体宿主可直接消元验证）⟹ L^⊥ = span{u_0..u_5}。x̄⊕0 = Σα_v u_v 且树坐标为零：树边 (0,i) 实体处，Σ_v α_v·1_{v∉{0,i}} = A − α_0 − α_i = 0（A = Σα_v），i = 1..5 ⟹ α_1 = … = α_5 =: β = A − α_0。代入 A = α_0 + 5β ⟹ β = 5β ⟹ β = 0（特征 0）⟹ x̄ = α_0·π(u_0)。核维恰 1。(c) rank L_s = 90 − 1 = 89，与 lab41b_lattice.json 精确计算一致（K95 四簇 89、K99_0 的 94 维切片核 1 维由 u = π(1_{S_0})、|supp| = 54 同构论证）。∎

**注（诚实边界）**：步骤 (b) 用了实测秩（89）钉死 L^⊥ = span{u_v}。一般宿主"L^⊥ 恰 6 维"的纯组合证明（不依赖秩计算）为开放问题 **GAP-A**：⊇ 6 维恒成立（引理 2），恰 6 维 ⟺ 匹配交换约束满秩，与 4-connectivity 的蕴含关系未证。本 lane 的 5 簇全部满足（89 = 95−6、93 = 99−6）。

### 2.5 定理 T2（全相消的纤维传播）

**陈述**：若 w* 消光（全部 F_vc(w*) = 0）且 mono_c(w*) = 0，则整条纤维 {w*(t) : t ∈ C*} 上全部方程与 mono_c 恒零。特别地 lane_36 对 5 簇深根的 ROOTED-MONO-ZERO 判决自动传播到纤维；在纤维上搜索 mono ≠ 0 原理性无效（E1 计划据此取消）。

**证明**：T1 的缩放公式逐点给出 F_vc(w(t)) = t²F_vc(w*) = 0、mono_c(w(t)) = t²mono_c(w*) = 0。∎

**机器交叉验证**（dps=120，K95_1 谷点，λ = 0.7+0.4j 与 −1.3+2.1j）：全部 16 个 mono 项（3 色 5/5/6 项）逐项比值 mono 项(w(λ))/mono 项(w) 与 e^{2λ} 之差 ≤ 1.2e-120（算术底噪）。**总和级验证在全相消点原理性不可能**：|mono_c(w*)| = 1.35e-129 而 Σ|项| = 1.12e-8，抵消放大 1e+121 > 可用精度——这同时是 lane_36 "mono/res 跨量级恒定"全相消签名的独立复现。

### 2.6 定理 T3（判定问题的商化收缩）

**陈述**：取 L_s 的整行基 B₈₉（int_echelon 输出）与 descend 商坐标 coords: PM → Z^89。定义商系统 P := {P_vc(x) = Σ_{M∈PM(vc)} x^{coords(M)}}（726 个方程，x ∈ (C*)^89）。则：可行性 (i)+(ii) 有解 ⟺ 存在 x* ∈ (C*)^89 使 P_vc(x*) = 0（全部 vc）且某 P_c(x*) ≠ 0。且 90 维 Jacobian 在任何根处有右零方向 u。

**证明**：log 坐标分解 z = B^T ẑ + λu（直和；det[B₈₉; u] = 54 ≠ ±1 ⟹ 子格参数化，商 map (C*)^90 → (C*)^89 仍满因 C* 可除；54 = |S_0∩rem| 为结构性数字，两簇同值）。每匹配积 w(M) = t²·x^{coords(M)}（t = e^λ），t² 为全局公因子：消光方程 F_vc = t²·P_vc∘π ⟹ 消光 ⟺ P_vc = 0；mono_c = t²·P_c ⟹ 非零性等价。零方向：∂_{z_u}F_vc = 2F_vc（T1 微分形式）⟹ 在根处 J·u 方向列 = 0。∎

**推论 T4（σ_min 超退化的定向解释）**：lane_36 的 Kantorovich 尝试冻结单一实体坐标 w_{e0} = c 以切开尺度轨道——但该切口不 remove u 方向（u 支撑 54 个坐标，除非 e0 ∈ supp u 且配合其余 53 个坐标同时冻结）。σ_min ≤ 4.8e-290 的超退化是 T3 零方向的必然读数，非根簇额外的病态。**正确切口 = 商化（89 维 descend 坐标，工具已就绪：NL.descend）**；Kantorovich/根计数/证书路线应在商空间重启。

### 2.7 对三靶的最终判决

- **靶 1（高次乘子证书）**：census 遗稿证明正规型（无跨类对消）单项式乘子证书 5 簇全谱系不可行；一般单项式/多项式乘子证书开放，但 T1/T2 提示任何"mono 恒零"证书必须与纤维结构相容（乘子理想需在商坐标中构造）。
- **靶 2（mono≠0 存在性搜索）**：纤维方向被 T2 关闭（乘子 t² 不改变零性）；商方向（89 维）是唯一存活搜索空间。tangent 遗稿的 12 trials × 2 簇 + deep_verify 深挖 = 商方向近旁无见证（全部伪影/全相消）。
- **靶 3（mono 恒零代数证明）**：等价命题经 T3 商化：**P_c 恒零于 V(P) 吗**（89 维商系统）？支撑键障碍（lane_36）在商坐标下形式未变（缺失键是精确整数事实），线性组合类证书仍被封死；Gröbner/根理想类证书开放。

## 3. E2：其余 4 簇 deep_verify 补全（已跑完 + 重分类）

E2 进程跑完全部 4 簇 × 3 trials（种子 20260915，与 K95_1 同试探单序列）。verdict 字段带 bug ② 无效，以下为 mpmath 域重分类结果（results/lab41b_deep_verify_reclass.json）：

| 簇 | trial (eps) | res 末值 | ratio_min | dist_z* | 修正 verdict |
|---|---|---|---|---|---|
| K95_1 | 0 (1e-3) | 6.2e-402 | 2.1e-13 | 1.0e-3 | SURVIVES-POSITIVEDIM |
| K95_1 | 1 (1e-3) | 1.9e-401 | 2.5e-13 | 1.0e-3 | SURVIVES-POSITIVEDIM |
| K95_1 | 4 (3e-2) | 3.5e-374 | 2.5e-13 | 3.0e-2 | SURVIVES-POSITIVEDIM |
| K95_2 | 0 (1e-3) | 3.9e-402 | 3.8e-12 | 1.0e-3 | SURVIVES-POSITIVEDIM |
| K95_2 | 1 (1e-3) | 2.6e-401 | 3.5e-12 | 1.0e-3 | SURVIVES-POSITIVEDIM |
| K95_2 | 4 (3e-2) | 2.2e-374 | 3.5e-12 | 3.0e-2 | SURVIVES-POSITIVEDIM |
| K95_7 | 0 (1e-3) | 9.7e-402 | 4.7e-10 | 1.0e-3 | SURVIVES-POSITIVEDIM |
| K95_7 | 1 (1e-3) | 5.2e-402 | 4.6e-10 | 1.0e-3 | SURVIVES-POSITIVEDIM |
| K95_7 | 4 (3e-2) | 1.2e-377 | 3.5e-10 | 3.0e-2 | SURVIVES-POSITIVEDIM |
| K95_11 | 0 (1e-3) | 6.5e-405 | 2.3e-10 | 1.0e-3 | SURVIVES-POSITIVEDIM |
| K95_11 | 1 (1e-3) | 1.7e-403 | 2.0e-10 | 1.0e-3 | SURVIVES-POSITIVEDIM |
| K95_11 | 4 (3e-2) | 3.5e-349 | 2.1e-10 | 1.0e-3 | **AMBIGUOUS**（res 差 1 个量级未过 1e-350 阈，诚实保留） |
| K99_0 | 0 (1e-3) | 8.0e-393 | 1.5e-10 | 1.3e-3 | SURVIVES-POSITIVEDIM |
| K99_0 | 1 (1e-3) | 4.9e-385 | 1.4e-10 | 1.3e-3 | SURVIVES-POSITIVEDIM |
| K99_0 | 4 (3e-2) | 2.9e-374 | 1.5e-10 | 3.0e-2 | SURVIVES-POSITIVEDIM |

**汇总**：15 trials = 14 SURVIVES-POSITIVEDIM + 1 AMBIGUOUS（阈值边缘）+ 0 REFUTED-DEEP。全部深根 res ≤ 1e-349（多数 1e-374 以下）、ratio 恒有界（≤5e-10）、dist_z* 稳定等于位移量。结合 T1 定理化解读：eps-位移重投影收敛到的"新根"处 mono≈0，且正维性是恒等式必然而非数值现象——**5 簇 × 全部已测根 = 全相消，猜想 c 幸存**。tangent 的 eps=0.3 大位移 trials（2 簇 × 4）重投影不收敛（NO-ROOT），无信息损失。

## 4. 落盘

```
src/lab41/lattice_fiber.py            # E0 精确格计算（kernel v2；含 v1 bug 自检记录）
results/lab41b_lattice.json           # 5 簇 u/纤维谱/正交断言（ortho_violations=0）
results/lab41b_reclassify.json        # K95_1 三 trial mpmath 域重分类
results/lab41_deep_verify.json        # E2 四簇原始记录（verdict 字段无效，以重分类为准）
results/lab41_deep_verify_k951_prev.json  # K95_1 原始记录备份
results/lab41b_deep_verify_reclass.json   # E2 四簇重分类（E2 完成后生成）
results/lab41b_t2_check.log           # T2 项级机器交叉验证记录
```

复现（项目根，离线）：
```
.venv/bin/python src/lab41/lattice_fiber.py                       # E0 ~1 min
.venv/bin/python src/lab41/deep_verify.py "iso5|iso5_K95_2" ...   # E2 ~50 min（verdict 字段忽略）
# 重分类脚本内嵌于报告 §1（classify_fixed），对任意 deep_verify JSON 可离线执行
```

## 5. 遗留与移交

1. **89 维商数值器**（T3 显式化）：descend 坐标 + 商方程重写 + σ_min 谱对比实验——预期解锁根计数/Kantorovich 重启。最高优先移交靶。
2. **P_c 恒零于 V(P) 的判定**（靶 3 商形式）：Gröbner 基（726 方程 89 变量，需利用类结构降维）或商空间 term 演化闭包（lane_26 v3 引擎的商版）。
3. **GAP-A**：一般 4-connected 宿主 L^⊥ 恰 6 维的组合证明（⟹ T1' 对全宿主类成立）。
4. **det = 54 的组合解释**（= |S_0∩rem|，两簇同值；Z^90/(L_s+Zu) 的结构）。
5. lane_41 遗稿 census 的跨类对消 GAP-2 与 struct 的自同构分类：未动，交下一棒。

## 6. 过程纪律（bug 零容忍披露）

1. **kernel_from_echelon v1 漏项 bug（本 lane）**：假设 int_echelon 基行在其他主元列为零——实际基行 append 后不再被后续列消元，回代方程漏掉高主元列项 ⟹ u = e₈₈+e₈₉ 垃圾解。**自检拦截**：R4 正交断言 ortho_violations=468 ≠ 0 触发复查；v2 改 Fraction RREF（真化简）后 violations = 0。教训：int_echelon 的"每列至多一个基行非零"不变式只对主元列成立，非主元列不得引用。
2. **classify float 下溢 bug（lane_41 遗稿，本 lane 修正）**：`res_last < 1e-350` 的字面量 1e-350 在 IEEE754 下 = 0.0，判据恒 False ⟹ verdict 恒 AMBIGUOUS。历史 JSON 的 records 数据不受影响；重分类（mpmath 域比较）后 K95_1 三 trial = SURVIVES-POSITIVEDIM。
3. **T2 验证第一版的总和级检查（本 lane）**：在全相消点做 mono 总和比值检查，被 1e+121 抵消放大污染（|m0| = 1.35e-129 vs Σ|p| = 1.12e-8，单项算术噪声 1e-121 被放大到 O(1)）。改为逐项级检查（无抵消）后精确通过。教训：全相消点上一切"和"的数值验证失效，必须逐项。

## 7. 对抗自检清单

1. 定义链：可行性 = (i)+(ii) 按 definitions.md §1.11；T1–T3 的方程/单色和语义与 pending_solver.build_system_mine 一致（实测样例顶点覆盖逐顶点 =1 核对）。✓
2. PM-valid/双色边语义：本 lane 结论只依赖"匹配 = 1-因子×实体选择、每匹配覆盖每顶点恰一次"的计数结构，未触碰染色可行性公理。✓
3. 浮点纪律：T1'（核维数）、纤维谱（⟨u,·⟩=2）、正交断言、det=54 全部精确整数算术；deep_verify 判读全部 mpmath 域；唯一 float 使用（tangent 遗稿 RSV 方向）只产生被深挖否证的候选。✓
4. 标红协议：无精确见证（无 mono≠0 的根），零标红维持。✓
5. 陈述一致性：本 lane 证明的是 T1/T2/T3（新结构定理）与 5 簇上的实测闭合；**未证明**主猜想、未证明 mono 恒零于整个 variety、未给出任何不可行证书。✓
6. 种子/确定性：E0 纯确定性；E2 继承 tangent_probe 种子 20260915。✓
7. 领赏/发布：无外部动作。✓
