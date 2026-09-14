# harden_round2 — 数值加固报告（定理 2′ / 系 4 的盲区补全）

日期：2026-09-14 · 工作目录：`/Users/munich/Desktop/数学/front184/campaign/harden_round2/`
环境：macOS arm64，Python 3.13.12（`/usr/bin/env python3`），networkx 3.6.1，scipy 1.17.1（HiGHS MILP），
nauty 2.9.3（`/opt/homebrew/bin/geng`），10 逻辑核。

**零反例声明**：本轮全部实验（共 **18,279 条构造性证书**：A 8136 + B 8000 + C 2100 + 额外 43；`data/C_s3_s0.jsonl` 另有 2 条**采样占位记录**（`sample_error` 槽，非证书、不参与复核）；`h_verify.py` 按上述 18,279 份证书全量复核 **0 失败**——2026-09-14 第五轮实跑复现）
**未发现任何反例**：
- 全部 6-正则图样本都构造出了 ≤ n−2（n ≡ 0 mod 3）或 ≤ n−1（一般 n）的合法分解，并给出显式证书；
- 独立校验器（networkx 实现，与构造代码不同源）逐条复核 **0 失败**；
- 所有 `*.violations` 文件为空（0 字节）。

校验口径：18,258 条经独立校验器一次批量复核（A 8136 + B 8000 + C 2100 + n=12 的 22 条），
另 21 条 n=10 的精确 ce=3 见证单独复核（共 18,279 条全覆盖，0 失败）。

---

## 0. 任务书与定理的一处不一致（如实上报，未自行修改定义）

任务书 A 块写「**n=10（界 n−2=8）**」，但同一条消息给出的定理为：
- n ≡ 0 (mod 3) ⟹ ce ≤ n−2；
- **一般 n ⟹ ce ≤ n−1**。

10 ≡ 1 (mod 3)，故定理对 n=10 保证的是 **n−1 = 9**（上游原稿对 n=10 也用 9，见 `r2_01_aabc25_struct.md` §4 行 7「pieces ≤ 9」）。
处理方式：**按定理的界运行**（n=10 用 9，n=11 用 10，n=12 用 10），同时**额外记录是否达到 n−2**（数据保留，
不替代定理陈述）。结论：n=10 全部 21 类的构造件数 ≤ 8 = n−2（且精确 ce = 3）；n=11 全部 266 类 ≤ 8 ≤ n−2 = 9。
即实测比任务书标注的界更强，但这是**数据**，不是对定理陈述的修改。

---

## 1. 任务 A：同构意义下全穷举（geng 代表元 + 补图法）

### 1.1 生成命令与规模（nauty 2.9.3）

```
/opt/homebrew/bin/geng -d3 -D3 10 -q > data/geng_10_d3.g6     # 21 个（含 2 个不连通：K4∪K3,3、K4∪prism）
/opt/homebrew/bin/geng -d4 -D4 11 -q > data/geng_11_d4.g6     # 266 个（-c 连通为 265；差 1 个为 K5∪(K6−PM)）
/opt/homebrew/bin/geng -d5 -D5 12 -q > data/geng_12_d5.g6     # 7849 个（-c 连通为 7848；唯一不连通类为 K6∪K6）
```
（`geng` 输出即同构类代表元，每类恰一个；耗时 0.00s / 0.01s / 4.58s。日志 `logs/geng_generate.log`。）

补图步骤：每个 k-正则补图得 6-正则（断言逐图检查 6-正则）。n=10 全类 = 21，n=11 全类 = 266，n=12 全类 = 7849。

### 1.2 运行命令与结果

```
python3 h_A_enum.py --n 10 --g6 data/geng_10_d3.g6 --out data/A_n10.jsonl --exact   # 150.0s
python3 h_A_enum.py --n 11 --g6 data/geng_11_d4.g6 --out data/A_n11.jsonl           # 0.4s
python3 h_A_enum.py --n 12 --g6 data/geng_12_d5.g6 --out data/A_n12.jsonl           # 10.8s
```
日志：`logs/A_n10.log`、`logs/A_n11.log`、`logs/A_n12.log`；摘要：`data/A_n*.jsonl.summary.json`。

| n | 类数 | 定理界 | 构造件数 min/max | 件数直方图 | 达到 ≤ n−2 的类数 | 违反 |
|---|---|---|---|---|---|---|
| 10 | 21 | 9 (=n−1) | 4 / 8 | {4:2, 5:10, 6:4, 7:3, 8:2} | 21/21 | 0 |
| 11 | 266 | 10 (=n−1) | 3 / 8 | {3:15, 4:42, 5:63, 6:92, 7:44, 8:10} | 266/266 | 0 |
| 12 | 7849 | 10 (=n−2) | 3 / **10** | {3:193, 4:1152, 5:2218, 6:2305, 7:1430, 8:481, 9:65, **10:5**} | 7849/7849 | 0 |

- **n=12 有 5 个类的构造件数恰好 = n−2 = 10**（tag：`n12#1335, #3974, #4472, #5130, #5482`，全部是
  「恰有 1 个三角形因子」路线：m + (m−1) + (m−1) = 4+3+3）。其余 7844 类 ≤ 9。
- 路线分布（n=12）：`flat(ntri=0)` 7671、`flat(ntri=1)` 176、**`phi(ntri=2)` 仅 2**（`n12#2101` 件数 4、`n12#5166` 件数 5）。
  即 Φ(σ)⊔Φ(−σ) 机制在 n=12 只被 2 个类触发，但这两个类正是「两个三角形因子」的危险构型，机制非死代码。
- n=10 / n=11 无 `phi` 路线（3 ∤ n 时不可能出现三角形因子，与理论一致）。

### 1.3 n=10 精确 ce（两个独立求解器 + LP 下界）

对 21 个类逐类计算精确 ce（唯一正解，非上界）：
- 求解器 1：自研迭代加深 DFS + 状态 memo（最低未覆盖边分支，件 = 单边或简单圈）；
- 求解器 2：exact-cover ILP（scipy.optimize.milp / HiGHS，`Σx = k` 可行性形式，每个更小 k 的不可行证明即最优性证书）；
- 附加：LP 松弛下界（独立第三方证据）。

**结果：21/21 类的精确 ce = 3（BB = MILP，LP 下界 ≈ 3.0000000000）**。30 条边 / 每件 ≤ 10 条 ⟹ 3 是平凡下界，
故 ce = 3 即「三件必为 Hamilton 圈」的 Hamilton 圈分解。
Slack（界 − ce）：对 n−1=9 为 6；对任务书标注的 n−2=8 为 5。
21 个 ce=3 见证已写成证书 `data/extra_n10_ce3_certs.jsonl`，经独立校验器复核 **0 失败**（`logs/verify_n10_ce3.log`）。

解析正确性锚点（对照上游 `r2_01` 公布的独立求解器取值，只取数值不 import 代码）：
K_{1,4}=4、K_{2,3}=3、K_{3,3}=4、K3∪K_{3,4}=7、K7=3、K8−PM=3、n=9 的 4 个 6-正则类=3
—— 我的 BB、MILP 全部命中（`logs/A_exact_anchors.log`，总耗时 13.5s）。与上游 n=9「四类精确 ce=3」独立互验一致。

---

## 2. 任务 B：随机大样本（n=15,18,21,24，各 2000）

采样：`networkx.random_regular_graph(6, n, seed=SEED_BASE + n*100000 + i)`，`SEED_BASE = 20260914`（种子逐记录落盘）。
networkx 该算法为 Steger–Wormald 交换算法（文档：d = O(n^{1/3}) 时渐近均匀）——与上游的 MCMC 采样器不同源。

```
python3 h_B_random.py --count 2000 --shard 200 --procs 8 --nlist 15,18,21,24   # 3.6s（8 进程）
```

| n | 样本 | 定理界 n−2 | 构造件数 min/max | 直方图 | 违反/采样失败 | 重复样本 |
|---|---|---|---|---|---|---|
| 15 | 2000 | 13 | 3 / 11 | {3:55,4:242,5:501,6:597,7:398,8:164,9:37,10:5,11:1} | 0 / 0 | 0 |
| 18 | 2000 | 16 | 3 / 12 | {3:25,4:185,5:378,6:526,7:498,8:272,9:80,10:27,11:8,12:1} | 0 / 0 | 0 |
| 21 | 2000 | 19 | 3 / 13 | {3:23,4:117,5:312,6:441,7:492,8:342,9:183,10:63,11:21,12:5,13:1} | 0 / 0 | 0 |
| 24 | 2000 | 22 | 3 / 13 | {3:10,4:86,5:243,6:431,7:475,8:398,9:229,10:83,11:34,12:8,13:3} | 0 / 0 | 0 |

8000 个样本边集去重后 8000 个唯一（无重复采样）。**全部 8000 个样本的路线都是 `flat(ntri=0)`**
（即我们取到的 3 个 2-因子都没有三角形因子）⟹ 该路线件数 ≤ 3(m−1) = n−3；
观察到的最大件数 11 / 12 / 13 / 13 均 ≤ n−3（= 12 / 15 / 18 / 21）。
数据说明：随机样本中未出现「三角形因子」结构；`phi` 机制在 B 段零触发（这是样本性质，不是机制缺陷）。
注意：这只说明**我们抽到的那组 2-因子分解**无三角形因子；不排除图本身存在三角形因子而不在我们抽的分解里。

---

## 3. 任务 C：对抗族加宽（L(B) 星型族）

构造（本目录独立实现，思路同上游 `sweep_star_B.py`）：
B = 随机 3-正则二部简单图（s+s 点，配置模型拒绝采样，`SEED_C = 777001`）；
W = L(B)（3s 点 4-正则）= star(L) ⊔ star(R)；每个 B 取 3 个 (完美匹配, 定向) 组合
（第 1 个为 Kuhn 匹配 + 随机定向；第 2、3 个打乱匹配邻接序 + 随机定向）；
F₂ = R = K_n − W（(n−5)-正则）的任一 2-因子（n=21：16-正则 → 2-因子分解取一；n=24：19-正则 → blossom 完美匹配后 18-正则 → 分解取一）；
G = W ⊔ F₂ 断言 6-正则；件数 = comps(Φσ) + comps(Φ−σ) + comps(F₂)。

```
python3 h_C_adv.py --s 7 --count 500 --shard 50 --procs 8   # 500 个 B × 3 组合，1.7s
python3 h_C_adv.py --s 8 --count 200 --shard 50 --procs 8   # 200 个 B × 3 组合，1.9s
```

| s | n | B 数 | (M,σ) 记录 | 件数 min/max | 界 n−2 | 违反 | Φσ/Φ−σ 划分 E(W) | 两者无三角形 | #comp(Φσ)=#comp(Φ−σ) |
|---|---|---|---|---|---|---|---|---|---|
| 7 | 21 | 500 | 1500 | 3 / 10 | 19 | 0 | 1500/1500 | 1500/1500 | **1500/1500** |
| 8 | 24 | 200 | 600 | 3 / 12 | 22 | 0 | 600/600 | 600/600 | **600/600** |

- 件数直方图 s=7：{3:215,4:403,5:353,6:303,7:157,8:52,9:16,10:1}；s=8：{3:73,4:122,5:147,6:147,7:61,8:34,9:10,10:5,12:1}。
- 每个 Φ 因子的分量数 ≤ s−1 = m−1（观察值：Φ 分量数直方图 s=7 {1:905,2:548,3:47}、s=8 {1:334,2:237,3:28,4:1}）。
- **上游「#comp(Φ(σ)) = #comp(Φ(−σ)) 恒相等」的观察在 s=7、s=8 上继续成立（2100/2100 条）**——仅记录数据，不解释。
- 全部 2100 条记录经独立校验器复核 **0 失败**（含 Φ 划分、无三角形（逐件圈长 ≥4 + nx.triangles=0）、件数 ≤ n−2）。

---

## 4. 任务 D：复现性抽检

```
sh run_D_repro.sh     # 11m24s：A 部分主检查（n=10 含 exact ce、n=11、n=12）完整跑三遍
```
- run_d1 / run_d2：`PYTHONHASHSEED=0`（两遍）；
- run_d3：`PYTHONHASHSEED=12345`（检验结果不依赖集合迭代序）。

结果（`logs/D_compare.log`，比较器 `h_D_compare.py`）：

| 比较 | 证书 JSONL（sha256） | 摘要 JSON |
|---|---|---|
| d1 vs d2（同 hash seed） | **逐字节一致** | 剔除墙钟字段 `elapsed_s` 后内容一致 |
| d1 vs d3（不同 hash seed） | **逐字节一致** | 剔除 `elapsed_s` 后内容一致 |

- 证书 sha256 示例：`A_n12.jsonl = 455a227cf26d09ef…`（三遍相同）。
- **诚实说明**：D 脚本首轮直接用 `shasum` 比 `summary.json`，报了「不一致」；定位后确认差异**仅为墙钟字段
  `elapsed_s`**（176.8s vs 其他），证书文件本身三遍逐字节一致。比较器已改为「证书按字节比、摘要剔除墙钟字段比」，
  结果 PASS（`logs/D_repro.log` 保留了首轮 diff 作为审计记录）。
- 另：n=10 的 `--exact` 部分含 MILP（HiGHS），三遍的 `ce_bb/ce_milp/lp_lb` 数值完全一致（在摘要比较覆盖内）。

---

## 5. 额外实验：真实 ce 的松弛度（超出任务书，登记为数据）

1. **n=10 全类**：ce = 3（21/21，双引擎 + LP 下界；见 §1.3）。即 6-正则 10 点图全部可分解为 3 个 Hamilton 圈。
2. **n=12 抽样**：对 §1.2 中构造件数达 10 的 5 个类 + 等距抽样 12 个类（共 17 类）用 Held-Karp 位掩码 DP
   找 3-Hamilton 圈分解（`h_extra_n12_ce3_sample.py`）：
   - 随机 DP 路线命中 16/17（1 个未命中：`n12#1960`，只是随机路线未命中，非结论）；
   - 对 `n12#1960` 用**完备** BB（`ub=3`，8.8s）找到 3 件分解 ⟹ 17/17 类都有 3 件分解；
   - 所有 3 件分解证书经独立校验器复核 **0 失败**。36 条边 / 每件 ≤ 12 ⟹ 3 是平凡下界，
     故这 17 类的**精确 ce = 3**（由「已验证的 3 件分解 + 平凡下界」直接证明，无需 MILP）。
   - **降级说明**：n=12 的 MILP（HiGHS）未能定值——5 个类各跑单类 176.4 / 351.4 / 287.3 / 460.2 / 308.6s
     （求解时限 120s，含建模时间）全部报 Time limit reached（`logs/extra_n12_verify3.log`、`data/extra_n12_ce3.json`）。
     故 n=12 的精确 ce 只用 BB + 独立证书验证的路子（对 17 个类），其余 7832 个类未做精确 ce（未跑）；MILP 的失败不影响 ce=3 结论
     （结论只用「已验证的 3 件分解 + 平凡下界」，见上）。
3. 由此，n=12 上「构造件数 = n−2」的 5 个类真实 ce 均为 3：**构造件数远非最优**（构造路径保守，界很松）。

---

## 6. 独立性与校验设计

| 组件 | 实现 | 与构造的独立性 |
|---|---|---|
| 构造库 `h_common.py` | 自研（欧拉定向、Kuhn 匹配、2-因子分解、Φ 分解、审账管线） | 不 import 上游 `r2_core.py`，不 import 上游任何代码 |
| 精确 ce 求解器 1 | 自研 ID-DFS + memo（mask 状态） | 与求解器 2 引擎不同 |
| 精确 ce 求解器 2 | exact-cover ILP / HiGHS（scipy） | 与求解器 1 引擎不同；LP 下界为第三证据 |
| 证书校验器 `h_verify.py` | **只用 networkx**（is_connected/degree/triangles）+ 独立划分逻辑 | 与 `h_common` 完全不同源、不同数据结构 |
| 复现性 | `run_D_repro.sh` + `h_D_compare.py` | 三遍独立进程，含两个不同 `PYTHONHASHSEED` |
| 锚点 | 对照上游公布的独立数值（K_{1,4}、K_{3,3}、K3∪K_{3,4}、K7、K8−PM、n=9 四类） | 只取数值不取代码 |
| 校验器负对照 | `logs/verify_negative_control.log` | 对正确证书注入 5 类错误（件重叠/缺边/外来边/非圈/超界），**5/5 全部检出** → 「0 失败」不是空转 |

---

## 7. 覆盖与局限

**已覆盖**
- n=10：**同构意义下全类** 21 个（补图法）+ 每类精确 ce（双引擎）+ 独立证书复核。
  （上游此前只有 890,100 个**标记图**的截断抽样，未做同构类全穷举、未做精确 ce 全类。）
- n=11：全类 266 个，全部给出 ≤ 8 件证书（≤ n−2 = 9，亦 ≤ n−1 = 10）。
- n=12：全类 7849 个（上游只测过 200 个随机；对抗族 s=4 的 2040 个 B 与之部分重叠但样本不同）。
  其中 5 类的构造件数达 n−2 = 10，且这 5 类已确认精确 ce = 3。
- B：n=15/18/21/24 各 2000 个随机样本（共 8000），全部 ≤ n−3 实际值，种子落盘、无重复。
- C：s=7 500 个 B × 3 组合、s=8 200 个 B × 3 组合（上游只到 s=6 穷举 / s=8..40 随机单组合）。
- 校验总量：**18,279 条全部经独立校验器复核，0 失败**（其中 18,258 条一次批量跑；21 条 n=10 的 ce=3 见证单独跑）。
  注意 18,258 条里已含 n=12 的 22 条 3 件分解证书（5 个「件数=n−2」类 + 16 条抽样 + n12#1960）。

**未覆盖 / 局限（如实声明）**
1. **n=13,14,16,...（更大 n 的同构全类穷举）未做**：n=13 的 6-正则 = 补 6-正则，geng 规模会到 10^5–10^6 级；本轮未跑。
2. **n≥13 的精确 ce 全部未做**：精确 ce 只跑到 n=12 的 17 个类（n=10 全类）。n=15+ 的精确 ce 现状为"未跑"。
3. **随机样本的分布**：networkx 采样器是 Steger–Wormald 渐近均匀（d=6 = O(n^{1/3}) 范围内），非精确均匀；
   「零反例」只是 8000 个样本上的事实，不能读作概率性结论。
4. **C 段 B 只做 3 个 (匹配, 定向) 组合**（不是全部组合；上游审查员对 s≤6 做过全组合 1,183,920 个）。
   「任一定向」的覆盖由命题 6 的证明承担，本轮数值只是抽样。
5. **B/C 段的 2-因子只是「我们抽到的那一组」**：路线统计（如 n≥15 全为 ntri=0）说明的是该组分解的性质，
   不代表图无三角形因子。
6. **n=12 的 5 个「构造件数 = n−2」类**：本报告只给出「精确 ce = 3 ≤ n−2」的数据；
   它们是否使定理的界失去紧性、或定理的界在别处更紧，属 Prover 判断，不在本报告范围。
7. MILP 在 n=12 超时（120–176s），n≥13 未尝试；MILP 在 n≤11 与锚点上全部定值成功。
8. LP 下界在部分图上不等于整数最优（如 K_{2,3}: LP=1.5 < ce=3），此时最优性由 MILP 的不可行证明承担。

---

## 8. 文件清单与一键复现

**代码**（全部在本目录，均为本轮自写）
```
h_common.py                 构造库（Petersen 2-因子分解、Φ 分解、审账管线、锚点自检）
h_A_exact.py                精确 ce：BB 求解器 + MILP 求解器 + LP 下界 + 锚点（python3 h_A_exact.py anchors）
h_A_enum.py                 任务 A 驱动（geng 补图全类 + 证书 + n=10 exact）
h_B_random.py               任务 B 驱动（分片 + checkpoint，多进程）
h_C_adv.py                  任务 C 驱动（对抗族，3 组合/B）
h_verify.py                 独立证书校验器（只用 networkx）
h_D_compare.py              D 比较器（证书 sha256 + 摘要剔除墙钟字段）
run_D_repro.sh              D 复现性脚本（三遍 + 比较）
h_extra_n12_tight.py        额外：n=12 件数=n−2 的 5 类精确 ce（BB）
h_extra_n12_verify3.py      额外：上述 5 类 3 件证书 + 独立复核 + MILP 交叉（MILP 超时，如实记录）
h_extra_n12_ce3_sample.py   额外：n=12 抽样 17 类的 3-Hamilton 圈分解（Held-Karp DP）
```
**数据与日志**
```
data/geng_{10_d3,11_d4,12_d5}.g6                 geng 原始输出
data/A_n10.jsonl(+summary/+violations)           n=10 全类证书（21 条）+ 精确 ce 摘要
data/A_n11.jsonl, data/A_n12.jsonl               同上（266 / 7849 条）
data/B_n{15,18,21,24}_s{0..9}.jsonl              随机样本证书（8000 条，含种子）
data/B_summary.json                              B 汇总
data/C_s{7,8}_s*.jsonl, data/C_s{7,8}_summary.json   对抗族证书（2100 条）与汇总
data/extra_n10_ce3_certs.jsonl                   n=10 全类 ce=3 见证（21 条）
data/extra_n12_ce3_certs.jsonl (5), data/extra_n12_1960_ce3.jsonl (1),
data/extra_n12_ce3_sample_certs.jsonl (16)       n=12 3 件分解证书
data/extra_n12_ce3.json, extra_n12_ce3_sample.json, extra_n12_tight.json   精确/抽样结果
run_d1/ run_d2/ run_d3/                          D 三遍输出（含摘要与 sha256 列表）
logs/*.log                                       全部运行日志（tee/重定向落盘）
```
**一键复现**
```sh
cd /Users/munich/Desktop/数学/front184/campaign/harden_round2
/opt/homebrew/bin/geng -d3 -D3 10 -q > data/geng_10_d3.g6
/opt/homebrew/bin/geng -d4 -D4 11 -q > data/geng_11_d4.g6
/opt/homebrew/bin/geng -d5 -D5 12 -q > data/geng_12_d5.g6
python3 h_common.py                                       # 锚点自检
python3 h_A_exact.py anchors                              # 精确 ce 锚点（对照上游独立值）
python3 h_A_enum.py --n 10 --g6 data/geng_10_d3.g6 --out data/A_n10.jsonl --exact
python3 h_A_enum.py --n 11 --g6 data/geng_11_d4.g6 --out data/A_n11.jsonl
python3 h_A_enum.py --n 12 --g6 data/geng_12_d5.g6 --out data/A_n12.jsonl
python3 h_B_random.py --count 2000 --shard 200 --procs 8 --nlist 15,18,21,24
python3 h_C_adv.py --s 7 --count 500 --shard 50 --procs 8
python3 h_C_adv.py --s 8 --count 200 --shard 50 --procs 8
python3 h_verify.py data/A_n10.jsonl data/A_n11.jsonl data/A_n12.jsonl \
    data/B_n15_s*.jsonl data/B_n18_s*.jsonl data/B_n21_s*.jsonl data/B_n24_s*.jsonl \
    data/C_s7_s*.jsonl data/C_s8_s*.jsonl \
    data/extra_n10_ce3_certs.jsonl \
    data/extra_n12_ce3_certs.jsonl data/extra_n12_ce3_sample_certs.jsonl data/extra_n12_1960_ce3.jsonl
sh run_D_repro.sh
python3 h_D_compare.py
```
checkpoint 约定：A 按 tag 断点续跑（重跑跳过已处理类）；B/C 按 (n, shard) 写 `.done` 标记文件，重跑自动跳过已完成分片。

**注意事项**：`data/A_n12.jsonl` 等文件是构造证书本体（5.9MB），复核用 `h_verify.py` 直接读；
所有随机性来自显式 `random.Random(seed)` / 采样器 seed；D 段证明证书在三遍运行（含不同 `PYTHONHASHSEED`）下逐字节一致。
