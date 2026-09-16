#!/usr/bin/env python3
"""片引理残缺情形搜索：
枚举无桥 subcubic X、度 2 点 v（邻 a,b，ab∉E，即 (c1) 情形），
检查 X' = X - v + ab 是否"ab 不在任何最优打包中"。
判定：含 ab 的最优打包存在
  <=> max over 圈 C∋ab of ( p2(X' - E(C)) + |C| ) == p2(X')
若存在反例对，打印。
同时验证修正片引理 p2 >= n/2 + 3/2（n<=11 无桥 subcubic 全量）。
"""
import sys, subprocess
sys.path.insert(0, '/Users/munich/Desktop/数学/front_tre')
import networkx as nx
from fre_lib import Graph
from sweep3 import p2_subcubic, tjoin_fast
from fast_ver import parse_geng_line


def all_cycles_with_edge(g, eidx):
    """枚举含边 eidx 的所有简单圈（点 ≤ 11，可行）。返回圈边集列表。"""
    u, v = g.edges[eidx]
    # 删 e 后 u→v 的所有简单路径（DFS 枚举）
    adj = [[] for _ in range(g.n)]
    for i, (x, y) in enumerate(g.edges):
        if i != eidx:
            adj[x].append(y)
            adj[y].append(x)
    paths = []
    stack = [(u, [u])]
    # DFS 全部简单路径 u→v
    def dfs(cur, visited, path):
        if cur == v:
            paths.append(list(path))
            return
        for nxt in adj[cur]:
            if nxt not in visited:
                visited.add(nxt)
                path.append(nxt)
                dfs(nxt, visited, path)
                path.pop()
                visited.remove(nxt)
    dfs(u, {u}, [u])
    return [set(eidx if False else 0 for _ in []) for _ in []] or [
        frozenset([eidx] + [g.eid_lookup(path[i], path[i+1]) for i in range(len(path)-1)])
        for path in paths
    ]


def main():
    # 给 Graph 补一个 eid 查询
    orig_init = Graph.__init__
    def init_with_eid(self, n, edges, name=""):
        orig_init(self, n, edges, name)
        self.eid_lookup = lambda x, y: self._eid.get((x, y))
    Graph.__init__ = init_with_eid
    orig2 = orig_init
    def init2(self, n, edges, name=""):
        self.n = n
        self.edges = [tuple(e) for e in edges]
        self.m = len(self.edges)
        self.name = name
        self.adj = [set() for _ in range(n)]
        for u, v in self.edges:
            self.adj[u].add(v)
            self.adj[v].add(u)
        self.deg = [len(a) for a in self.adj]
        self.vmask = [0] * n
        for i, (u, v) in enumerate(self.edges):
            self.vmask[u] |= 1 << i
            self.vmask[v] |= 1 << i
        self._eid = {}
        for i, (u, v) in enumerate(self.edges):
            self._eid[(u, v)] = i
            self._eid[(v, u)] = i
        self.eid_lookup = lambda x, y: self._eid[(x, y)]
    Graph.__init__ = init2

    bad_pairs = 0
    checked = 0
    for n in range(5, 12):
        out = subprocess.run(['geng', '-c', '-D3', str(n)],
                             capture_output=True, text=True).stdout
        for line in out.splitlines():
            N, edges = parse_geng_line(line.strip())
            g = Graph(N, edges)
            if g.bridges():
                continue
            p2 = p2_subcubic(g)
            # 修正片引理
            if p2 < N / 2 + 1.5:
                print(f'!!! 修正片引理违反 n={N} p2={p2}')
            if p2 < N / 2 + 2 - 1e-9:
                pass  # 原版，仅记录
            # 度 2 点
            for v in range(N):
                if g.deg[v] != 2:
                    continue
                a, b = sorted(g.adj[v])
                if b in g.adj[a]:
                    continue  # (c2) 三角情形跳过
                # 构造 X' = X - v + ab（重编号: >v 的点减 1）
                def mv(x):
                    return x if x < v else x - 1
                a2, b2 = mv(a), mv(b)
                e2 = [tuple(mv(x) for x in e) for e in edges if v not in e] + [(a2, b2)]
                g2 = Graph(N - 1, e2)
                if g2.bridges():
                    continue
                checked += 1
                p2b = p2_subcubic(g2)
                eidx = g2._eid[(a2, b2)]
                best = 0
                # 枚举含 ab 的圈
                u2, v2 = a2, b2
                adj2 = [[] for _ in range(g2.n)]
                for i, (x, y) in enumerate(g2.edges):
                    if i != eidx:
                        adj2[x].append(y)
                        adj2[y].append(x)
                cyc_best = 0
                def dfs(cur, visited, pathedges):
                    global cyc_best
                    if cur == v2:
                        L = len(pathedges) + 1
                        # 打包 = 圈 + p2(其余)
                        es = set(pathedges) | {eidx}
                        # 删圈边
                        e3 = [e for i2, e in enumerate(g2.edges) if i2 not in es]
                        g3 = Graph(N - 1, e3) if e3 else Graph(N - 1, [])
                        rest = p2_subcubic(g3) if e3 else 0
                        if rest + L > cyc_best:
                            cyc_best = rest + L
                        return
                    for nxt in adj2[cur]:
                        if nxt not in visited:
                            ei = g2._eid[(cur, nxt)]
                            visited.add(nxt)
                            dfs(nxt, visited, pathedges + [ei])
                            visited.remove(nxt)
                dfs(u2, {u2}, [])
                if cyc_best < p2b:
                    bad_pairs += 1
                    print(f'残缺对: n={N} v={v} a={a} b={b} p2(X\')={p2b} 含ab最优={cyc_best}')
                    print(f'   g6={line.strip()}')
        print(f'  n={n} done, 累计检查对 {checked}, 残缺 {bad_pairs}', flush=True)
    print(f'完成: 检查 {checked} 对, 残缺 {bad_pairs}')


if __name__ == '__main__':
    main()
