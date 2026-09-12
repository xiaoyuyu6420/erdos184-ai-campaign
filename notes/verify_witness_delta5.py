#!/usr/bin/env python3
"""
独立验证 attack_delta5.md 的 witness G*（第 1 项攻击）。
从笔记 §3.1 的文字描述独立重建图，然后：
  (1) 基本性质：n=12, m=21, Δ=5, 连通, 无桥, 无割点(2-连通)
  (2) 显式分解（§3.4）：合法划分、11 件、盖满 21 边
  (3) 精确 ce(G*)：位掩码 DP（所有简单圈枚举 + 最低边分支）
  (4) 最大边不交圈 packing（无链式约束）——对照 §3.2 的 "=4"
  (5) 最大链式序列长度 k —— 对照 §3.2 的 k=4
  (6) 全部链式 4-序列（集合 × 全部合法顺序）：逐个算 s,t,c,λ、
      情形 1/2、判据 t≥λ+1 / t≥λ+2 是否成立、框架上界 k+(n−c)、
      (A)(†)(‡) 是否满足、Σ|V|（P4′ 用）
  (7) 分类对照 §3.3 的"两类"说法
"""
import itertools
from collections import namedtuple

# ---------- 建图（严格按笔记 §3.1 文字，不抄坐标） ----------
names = ['p','q','r','a2','b2','a3','b3','a4','b4','f','g1','g2']
idx = {v:i for i,v in enumerate(names)}
N = len(names)

edge_list = []
# 4 个三角形：T1=pqr；T2 挂在 p；T3 挂在 q；T4 挂在 r（单点粘合）
triangles = {
    'T1': ('p','q','r'),
    'T2': ('p','a2','b2'),
    'T3': ('q','a3','b3'),
    'T4': ('r','a4','b4'),
}
for t,(x,y,z) in triangles.items():
    edge_list += [(x,y),(y,z),(z,x)]
# 三个星灌木
for center, leaves in [('f',['p','q','r']),
                       ('g1',['a2','a3','a4']),
                       ('g2',['b2','b3','b4'])]:
    for l in leaves:
        edge_list.append((center,l))

# 去重、排序、编号
eset = sorted({tuple(sorted((idx[a],idx[b]))) for a,b in edge_list})
M = len(eset)
eid = {e:i for i,e in enumerate(eset)}
adj = [set() for _ in range(N)]
for (u,v) in eset:
    adj[u].add(v); adj[v].add(u)
FULL = (1<<M) - 1

def report(msg): print(msg)

report("="*72)
report("G* 基本量")
report("="*72)
report(f"n={N}  m={M}  (笔记称 12 点 21 边)")
degs = [len(adj[v]) for v in range(N)]
report("度数: " + ", ".join(f"{names[v]}:{degs[v]}" for v in range(N)))
report(f"Δ = {max(degs)}  (笔记称 5, 且 p,q,r 度 5)")
assert M == 21 and N == 12
assert sorted(degs) == [3,3,3,3,3,3,3,3,3,5,5,5]
assert max(degs) == 5

# ---------- (1) 连通 / 桥 / 割点 ----------
def connected(vertices, edges, exclude_vertex=None, edge_mask=None):
    vs = [v for v in vertices if v != exclude_vertex]
    if not vs: return True
    seen = {vs[0]}; stack=[vs[0]]
    em = set(edges) if edge_mask is None else {eset[i] for i in range(M) if edge_mask>>i & 1}
    while stack:
        x = stack.pop()
        for (a,b) in em:
            if a==x and b!=exclude_vertex and b not in seen: seen.add(b); stack.append(b)
            if b==x and a!=exclude_vertex and a not in seen: seen.add(a); stack.append(a)
    return len(seen)==len(vs)

G_conn = connected(range(N), eset)
bridges = [e for e in eset if not connected(range(N), eset, edge_mask=FULL ^ (1<<eid[e]))]
arts = [v for v in range(N) if not connected(range(N), eset, exclude_vertex=v)]
report(f"连通: {G_conn};  桥: {len(bridges)};  割点: {[names[v] for v in arts]}")
assert G_conn and not bridges and not arts, "2-连通性失败"
report("=> Δ=5、2-连通、无桥：全部属实")

# ---------- 工具：圈枚举 ----------
def all_simple_cycles():
    """所有简单圈（≥3 顶点），返回去重后的 edge-mask 列表及顶点集。"""
    cycles = {}
    for start in range(N):
        # DFS 简单路，只允许顶点 >= start，且圈的最小顶点 = start
        stack = [(start, [start], 0)]  # vertex, path, edge-mask
        while stack:
            v, path, em = stack.pop()
            for w in sorted(adj[v]):
                if w < start: continue
                e = tuple(sorted((v,w)))
                if eid[e] & em and (em>>eid[e])&1: continue
                if (em>>eid[e])&1: continue
                if w == start and len(path) >= 3:
                    key = frozenset(path)
                    if key not in cycles:
                        cycles[key] = (em | (1<<eid[e]), frozenset(path))
                elif w not in path:
                    stack.append((w, path+[w], em | (1<<eid[e])))
    return list(cycles.values())

cyc_list = all_simple_cycles()
cyc_masks = [c[0] for c in cyc_list]
cyc_verts = [c[1] for c in cyc_list]
report(f"\n简单圈总数 = {len(cyc_list)}")

# 纯圈（只用三角形边）应当恰为 T1..T4
tri_edge_masks = {}
for t,(x,y,z) in triangles.items():
    m=0
    for a,b in [(x,y),(y,z),(z,x)]:
        m |= 1<<eid[tuple(sorted((idx[a],idx[b])))]
    tri_edge_masks[t]=m
tri_edge_set = 0
for m in tri_edge_masks.values(): tri_edge_set |= m
pure = [i for i,msk in enumerate(cyc_masks) if msk & ~tri_edge_set == 0]
report(f"纯三角形圈 = {len(pure)} 个（笔记称恰 T1..T4 共 4 个）")
assert len(pure)==4

# ---------- (2) 显式分解（笔记 §3.4） ----------
def mkpath(vs):
    m=0
    for a,b in zip(vs, vs[1:]+vs[:1]):
        m |= 1<<eid[tuple(sorted((idx[a],idx[b])))]
    return m
expl = [mkpath(['g1','a2','p','q','a3']),
        mkpath(['g2','b2','p','r','b4']),
        mkpath(['q','f','r'])]
singles = ['a2b2','a3b3','a4r','a4b4','g1a4','b3q','b3g2','pf']
expl_masks=[]
# 直接按名字对解析
def edge_of(sn):
    for a in names:
        if sn.startswith(a) and sn[len(a):] in [n for n in names]:
            b = sn[len(a):]
            return tuple(sorted((idx[a], idx[b])))
    raise ValueError(sn)
expl_masks = expl + [1<<eid[edge_of(s)] for s in singles]
acc=0; ok=True
for m in expl_masks:
    if m & acc: ok=False
    acc |= m
report(f"\n显式分解: {len(expl_masks)} 件, 覆盖边数 = {bin(acc).count('1')}, 划分合法 = {ok and acc==FULL}")
assert len(expl_masks)==11 and acc==FULL and ok
report("=> 显式分解合法、11 件 = n−1：属实  (ce(G*) ≤ 11)")

# ---------- (3) 精确 ce(G*)：位掩码 DP ----------
cyc_by_edge = [[] for _ in range(M)]
for cm in cyc_masks:
    for i in range(M):
        if (cm>>i)&1: cyc_by_edge[i].append(cm)

INF = 99
dp = [INF]*(1<<M); dp[0]=0
for mask in range(1, 1<<M):
    low = (mask & -mask).bit_length()-1
    rest = mask ^ (1<<low)
    best = dp[rest]+1  # 单边
    for cm in cyc_by_edge[low]:
        if cm & mask == cm:
            v = dp[mask ^ cm]+1
            if v<best: best=v
    dp[mask]=best
ce_exact = dp[FULL]
report(f"\n精确 ce(G*) = {ce_exact}  (笔记称 11)")
if ce_exact != 11:
    report("!! 笔记的 ce(G*)=11 声称错误：真实值 = %d（哈密顿 12-圈 + pqr 三角形 + 6 单边 = 8 件）" % ce_exact)
    report("   证书: 圈 p-b2-a2-g1-a3-q-b3-g2-b4-a4-r-f-p (12边), 圈 p-q-r-p (3边),")
    report("         单边 pa2, qf, rb4, b2g2, a3b3, a4g1  —— 合法划分, 12+3+6=21 ✓")

# ---------- (4) 最大边不交 packing（无链式约束） ----------
best_pack = 0
def dfs_pack(i, used, cnt):
    global best_pack
    best_pack = max(best_pack, cnt)
    if cnt + (len(cyc_masks)-i) <= best_pack: return
    for j in range(i, len(cyc_masks)):
        if cyc_masks[j] & used == 0:
            dfs_pack(j+1, used|cyc_masks[j], cnt+1)
dfs_pack(0,0,0)
report(f"\n最大边不交圈 packing（无链式约束）= {best_pack}  (笔记 §3.2 称 4)")
assert best_pack == 4

# ---------- (5) 最大链式序列长度 k ----------
def dfs_chain(used, covered, depth):
    best = depth
    for j,cm in enumerate(cyc_masks):
        if cm & used: continue
        if cyc_verts[j] & covered:
            best = max(best, dfs_chain(used|cm, covered|cyc_verts[j], depth+1))
    return best
k_max = 0
for j,cm in enumerate(cyc_masks):
    k_max = max(k_max, dfs_chain(cm, cyc_verts[j], 1))
report(f"最大链式序列长度 k = {k_max}  (笔记称 4)")
assert k_max == 4

# ---------- (6) 全部链式 4-序列：逐集合 × 全部合法顺序 ----------
# 收集所有深度 4 的链式集合
sets4 = set()
def collect_chain(used, covered, chosen):
    if len(chosen)==4:
        sets4.add(frozenset(chosen)); return
    for j,cm in enumerate(cyc_masks):
        if cm & used: continue
        if cyc_verts[j] & covered:
            collect_chain(used|cm, covered|cyc_verts[j], chosen+[cm])
for j,cm in enumerate(cyc_masks):
    collect_chain(cm, cyc_verts[j], [cm])
report(f"\n链式 4-序列的集合数 = {len(sets4)}")

def components(edge_mask):
    """返回 (comp_id per vertex, 非平凡分量数 t, 孤立点数 s)"""
    comp = [-1]*N; cid=0
    em = {eset[i] for i in range(M) if (edge_mask>>i)&1}
    for v in range(N):
        if comp[v]!=-1: continue
        stack=[v]; comp[v]=cid
        while stack:
            x=stack.pop()
            for (a,b) in em:
                if a==x and comp[b]==-1: comp[b]=cid; stack.append(b)
                if b==x and comp[a]==-1: comp[a]=cid; stack.append(a)
        cid+=1
    sizes=[0]*cid
    for v in range(N): sizes[comp[v]]+=1
    t = sum(1 for z in sizes if z>=2); s = sum(1 for z in sizes if z==1)
    return comp, t, s

results=[]
for fs in sorted(sets4, key=lambda s: sorted(s)):
    cms = sorted(fs)
    union_e = 0; union_v = set()
    for cm in cms:
        union_e |= cm
        union_v |= {v for v in range(N) if any((cyc_masks[i]>>0)&0 for i in [])}
    # 顶点集
    vsets=[]
    for cm in cms:
        vs=set()
        for i in range(M):
            if (cm>>i)&1:
                u,w = eset[i]; vs.add(u); vs.add(w)
        vsets.append(vs)
    union_v = set().union(*vsets)
    H = FULL ^ union_e
    comp, t, s = components(H)
    # 共享点 S
    cnt = {v:0 for v in union_v}
    for vs in vsets:
        for v in vs: cnt[v]+=1
    S = {v for v in union_v if cnt[v]>=2}
    lam = sum(1 for v in S if sum(1 for i in range(M) if (H>>i)&1 and v in eset[i])==1)
    c = t+s
    bound = 4 + (N - c)
    # 全部合法顺序 -> 情形 & 判据
    orders=[]
    for perm in itertools.permutations(range(4)):
        seen=set(); good=True; pattern=[]
        for pi in perm:
            si = vsets[pi] & seen
            if pi>0 or True:
                if not si and seen: good=False; break
            pattern.append(len(si)); seen |= vsets[pi]
        if good: orders.append((perm, pattern))
    # 每个顺序下框架是否成功
    succ = []
    for perm, pattern in orders:
        case1 = any(x>=2 for x in pattern[1:]) if len(pattern)>1 else False
        if case1:
            okc = (t >= lam+1)
        else:
            okc = (t >= lam+2)
        succ.append(okc)
    # (A)(†)(‡)
    def degH(v):
        return sum(1 for i in range(M) if (H>>i)&1 and v in eset[i])
    A_ok = all(degH(v)<=1 for v in S)
    # (†)
    dag = False
    for pi,cm in enumerate(cms):
        for i in range(M):
            if (cm>>i)&1:
                u,w = eset[i]
                if u not in S and w not in S and comp[u]==comp[w]:
                    dag = True
    # (‡): 对每条 i>=2 的圈上共享点(在链式顺序里充当 S_i 的)检查。
    # 严格版：对每个顺序、每个充当 v_i 的共享活跃点，其在该圈上的两邻居不在其 H' 分量中
    dq_bad = False
    for perm,pattern in orders:
        seen=set()
        for pos,pi in enumerate(perm):
            if pos>0:
                si = vsets[pi]&seen
                for v in si:
                    if degH(v)==1:
                        # 该圈上 v 的邻居
                        nbrs=[]
                        for i in range(M):
                            if (cms[pi]>>i)&1:
                                u,w = eset[i]
                                if u==v: nbrs.append(w)
                                if w==v: nbrs.append(u)
                        for b in nbrs:
                            if comp[b]==comp[v]:
                                dq_bad = True
                seen |= vsets[pi]
            else:
                seen |= vsets[pi]
    sigma = sum(len(vs) for vs in vsets)
    is_pure = set(cms)=={tri_edge_masks[x] for x in ['T1','T2','T3','T4']}
    results.append(dict(cms=cms, pure=is_pure, t=t,s=s,c=c,lam=lam,bound=bound,
                        any_succ=any(succ), A=A_ok, dag=dag, dq_bad=dq_bad,
                        sigma=sigma, n_orders=len(orders)))

bad = [r for r in results if r['any_succ']]
report("\n--- 全部 4-集合统计 ---")
report(f"含框架成功顺序的集合数 = {len(bad)}  (必须为 0，判据才被否证)")
assert not bad, "存在框架成功的极值序列！"
lam_counts={}
t_counts={}
for r in results:
    lam_counts[r['lam']]=lam_counts.get(r['lam'],0)+1
    t_counts[(r['t'],r['lam'])]=t_counts.get((r['t'],r['lam']),0)+1
report(f"(t,λ) 分布: {dict(sorted(t_counts.items()))}")
bounds_set = sorted({r['bound'] for r in results})
report(f"框架上界取值: {bounds_set} -> " +
       str({b: sum(1 for r in results if r['bound']==b) for b in bounds_set}))
report(f"笔记§3.3 称 c∈{{3,4}} → 上界∈{{12,13}}: 实际 c 集合 = {sorted({r['c'] for r in results})}")
report(f"纯型集合数 = {sum(1 for r in results if r['pure'])}; 总集合数 = {len(results)}")
report(f"(A) 全部满足: {all(r['A'] for r in results)}")
report(f"(†) 全部满足: {not any(r['dag'] for r in results)}")
report(f"(‡) 全部满足: {not any(r['dq_bad'] for r in results)}")
sigmas = sorted({r['sigma'] for r in results}, reverse=True)
report(f"Σ|V| 可取值(降序): {sigmas}  → (P4′) 极值 Σ = {sigmas[0]}")
extremal = [r for r in results if r['sigma']==sigmas[0]]
report(f"(P4′) 极值集合数 = {len(extremal)}, 其中框架成功 = {sum(1 for r in extremal if r['any_succ'])}")
report(f"极值集合的 (t,λ,bound): {sorted({(r['t'],r['lam'],r['bound']) for r in extremal})}")

# 非纯型样例
nonpure = [r for r in results if not r['pure']]
report(f"\n非纯型共 {len(nonpure)} 个；前 5 个 (t,λ,c,bound,Σ): " +
       str([(r['t'],r['lam'],r['c'],r['bound'],r['sigma']) for r in nonpure[:5]]))

report("\n" + "="*72)
report("总结论：witness G* 的全部可程序化声称 = " +
       ("全部属实" if (ce_exact==11 and best_pack==4 and k_max==4 and not bad
                        and all(r['A'] for r in results) and not any(r['dag'] for r in results)
                        and not any(r['dq_bad'] for r in results)) else "存在偏差，见上") )
