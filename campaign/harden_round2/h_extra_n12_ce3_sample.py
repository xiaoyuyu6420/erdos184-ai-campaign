#!/usr/bin/env python3
"""h_extra_n12_ce3_sample.py — 补充：n=12 上"ce = 3（即 3 个 Hamilton 圈分解）"的存在性抽样。

方法（与 BB 不同的第三条路线）：Held-Karp 位掩码 DP 判 Hamilton 性。
  G 6-正则、36 条边；3 件分解 ⟹ 每件恰 12 条边 = Hamilton 圈（平凡下界 3）。
  随机重启：打乱邻接序 -> DP 找 H₁ -> 在 G−H₁（4-正则）找 H₂ -> 查 G−H₁−H₂ 是否连通（一个 12-圈）。
  成功即得 3 件证书（另经 h_verify.py 独立复核）；失败只说"该随机路线未找到"，不下结论。
用法: python3 h_extra_n12_ce3_sample.py <k>   # 从 A_n12 里等距抽 k 个类
"""
import json
import sys
import time
import random
import os
import subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def hamilton_cycle(n, adj, rng):
    """位掩码 DP（Held-Karp，起点固定 0）；返回顶点序列或 None。"""
    full = (1 << n) - 1
    reach = [0] * (1 << n)          # 位掩码：可达的最后顶点集合
    parent = {}
    reach[1] = 1
    for mask in range(1, 1 << n, 2):     # 只含 0 的掩码
        r = reach[mask]
        if not r:
            continue
        for last in range(n):
            if not (r >> last) & 1:
                continue
            nb = list(adj[last])
            rng.shuffle(nb)
            for w in nb:
                if (mask >> w) & 1:
                    continue
                nm = mask | (1 << w)
                if not (reach[nm] >> w) & 1:
                    reach[nm] |= 1 << w
                    parent[(nm, w)] = last
    # 找 last ∈ N(0) 使 (full, last) 可达（Hamilton 圈 = 0→…→last→0）
    last = None
    for w in adj[0]:
        if (reach[full] >> w) & 1:
            last = w
            break
    if last is None:
        return None
    seq = [last]
    cur = last
    mask = full
    while cur != 0:
        prev = parent[(mask, cur)]
        seq.append(prev)
        mask ^= 1 << cur
        cur = prev
    seq.reverse()
    return seq


def build_adj(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    return adj


def edges_of_cycle(path):
    n = len(path)
    return sorted(tuple(sorted((path[i], path[(i + 1) % n]))) for i in range(n))


def try_ce3(n, edges, rng, restarts=40):
    """返回 3 件证书或 None。"""
    for _ in range(restarts):
        adj = build_adj(n, edges)
        for a in adj:
            rng.shuffle(a)
        h1 = hamilton_cycle(n, adj, rng)
        if h1 is None:
            return None
        E1 = set(edges_of_cycle(h1))
        rest = [e for e in edges if e not in E1]
        adj2 = build_adj(n, rest)
        h2 = hamilton_cycle(n, adj2, rng)
        if h2 is None:
            continue
        E2 = set(edges_of_cycle(h2))
        rest2 = [e for e in rest if e not in E2]
        adj3 = build_adj(n, rest2)
        if all(len(a) == 2 for a in adj3):
            # 连通性检查（一个 12-圈）
            seen = {0}
            stack = [0]
            while stack:
                x = stack.pop()
                for y in adj3[x]:
                    if y not in seen:
                        seen.add(y)
                        stack.append(y)
            if len(seen) == n:
                h3 = hamilton_cycle(n, adj3, rng)
                if h3 is not None:
                    return [edges_of_cycle(h1), edges_of_cycle(h2), edges_of_cycle(h3)]
    return None


def main():
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    rows = [json.loads(l) for l in open('data/A_n12.jsonl')]
    # 5 个构造件数 = n−2 的类 + 等距抽样的类
    tags5 = {'n12#1335', 'n12#3974', 'n12#4472', 'n12#5130', 'n12#5482'}
    sel = [r for r in rows if r['tag'] in tags5]
    rest = [r for r in rows if r['tag'] not in tags5]
    step = max(1, len(rest) // k)
    sel += rest[::step][:k]
    certs = []
    out = {}
    for r in sel:
        edges = [tuple(e) for e in r['edges']]
        rng = random.Random(4242 + int(r['tag'].split('#')[1]))
        t0 = time.time()
        w = try_ce3(12, edges, rng)
        res = {"construct_pieces": r['npieces'], "route": r['route'],
               "ce3_found": w is not None, "s": round(time.time() - t0, 2)}
        out[r['tag']] = res
        print(f"[{r['tag']}] 构造件数={r['npieces']} 3 件分解={'找到' if w else '未找到'} {res['s']}s", flush=True)
        if w:
            certs.append({"tag": r['tag'] + "-ce3dp", "n": 12, "bound": 3, "reg": 6,
                          "route": "dp-ce3", "npieces": 3,
                          "edges": [list(e) for e in edges],
                          "pieces": [[list(e) for e in p] for p in w]})
    with open('data/extra_n12_ce3_sample_certs.jsonl', 'w') as f:
        for c in certs:
            f.write(json.dumps(c) + "\n")
    if certs:
        rr = subprocess.run([sys.executable, 'h_verify.py', 'data/extra_n12_ce3_sample_certs.jsonl'],
                            capture_output=True, text=True)
        print('独立复核:', '"total_failures": 0' in rr.stdout, flush=True)
        out['_verify_zero_failures'] = '"total_failures": 0' in rr.stdout
    out['_found'] = sum(1 for v in out.values() if isinstance(v, dict) and v.get('ce3_found'))
    out['_tried'] = len(sel)
    with open('data/extra_n12_ce3_sample.json', 'w') as f:
        json.dump(out, f, indent=1)
    print(f"命中 {out['_found']}/{out['_tried']} -> data/extra_n12_ce3_sample.json", flush=True)


if __name__ == "__main__":
    main()
