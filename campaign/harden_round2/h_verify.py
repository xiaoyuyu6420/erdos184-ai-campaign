#!/usr/bin/env python3
"""h_verify.py — 独立证书校验器（只用 networkx + 本文件自己的逻辑；不 import h_common / h_A_exact）。

用法: python3 h_verify.py cert1.jsonl [cert2.jsonl ...]

对每条证书记录（JSON 每行）做独立复核：
  1) 由 rec["edges"] 重建图 G（networkx），断言简单图 + 度 = rec.get("reg", 6)；
  2) 划分完整性：rec["pieces"] 的边多重集 == E(G)（无重复、无外来边、全覆盖）；
  3) 每件：单边 或 圈（点数 ≥3、每点度 2、连通、边数 == 点数）；
  4) 件数 ≤ rec["bound"]；
  5) 若含 phi_pieces/phim_pieces/f2_pieces（C 任务）：三组互不相交且并 == E(G)；
     phi/phim 的每件为长度 ≥4 的圈；且其边集的三角形数为 0（nx.triangles）；
     phi ⊔ phim == W_edges（若给出）。
所有断言失败会写入 failures（含完整记录）并计数；末尾输出总结 JSON。
"""
import sys
import json
from collections import Counter

import networkx as nx


def norm_edge(e):
    return (e[0], e[1]) if e[0] <= e[1] else (e[1], e[0])


def edges_of_piece(p):
    return [norm_edge(e) for e in p]


def edges_of_pieces(ps):
    out = []
    for p in ps:
        out += edges_of_piece(p)
    return out


def is_cycle_like(edges):
    """单边 或 圈（返回 True/False + 原因）。"""
    if len(edges) == 1:
        return True, "single"
    g = nx.Graph()
    g.add_edges_from(edges)
    if g.number_of_nodes() != len(edges):
        return False, f"点数 {g.number_of_nodes()} != 边数 {len(edges)}"
    if any(d != 2 for _, d in g.degree()):
        return False, "存在度 != 2 的点"
    if not nx.is_connected(g):
        return False, "不连通"
    if g.number_of_nodes() < 3:
        return False, "点数 < 3"
    return True, f"cycle({g.number_of_nodes()})"


def check_record(rec):
    """返回 (ok, notes, stats)。"""
    notes = []
    errs = []
    n = rec["n"]
    reg = rec.get("reg", 6)
    E = [tuple(e) for e in rec["edges"]]
    Gm = nx.Graph()
    Gm.add_nodes_from(range(n))
    Gm.add_edges_from(E)
    if Gm.number_of_edges() != len(set(E)):
        errs.append("edges 列表含重复边")
    if any(u == v for u, v in E):
        errs.append("edges 含自环")
    degs = dict(Gm.degree())
    if any(d != reg for d in degs.values()):
        errs.append(f"度序列不是 {reg}-正则: {sorted(set(degs.values()))}")
    if Gm.number_of_nodes() != n:
        errs.append("顶点数不符")
    EG = {tuple(sorted(e)) for e in E}
    pieces = rec["pieces"]
    seen = Counter()
    for p in pieces:
        for e in edges_of_piece(p):
            seen[e] += 1
    if set(seen) != EG:
        errs.append(f"件边集与 E(G) 不一致（差 {len(set(seen) ^ EG)} 条）")
    for e, c in seen.items():
        if c > 1:
            errs.append(f"边 {e} 被覆盖 {c} 次")
    cyc_lens = []
    for p in pieces:
        ok, why = is_cycle_like([tuple(e) for e in p])
        if not ok:
            errs.append(f"件不合法（{why}）")
        elif why.startswith("cycle"):
            cyc_lens.append(int(why[6:-1]))
    npieces = len(pieces)
    if npieces > rec["bound"]:
        errs.append(f"件数 {npieces} > 界 {rec['bound']}")
    stats = {"npieces": npieces, "min_cycle": min(cyc_lens) if cyc_lens else None,
             "max_cycle": max(cyc_lens) if cyc_lens else None}
    # --- C 任务附加字段 ---
    if "phi_pieces" in rec:
        phi = rec["phi_pieces"]
        phim = rec["phim_pieces"]
        f2 = rec.get("f2_pieces", [])
        W = [tuple(e) for e in rec["W_edges"]]
        sets = [Counter(edges_of_pieces(phi)), Counter(edges_of_pieces(phim)),
                Counter(edges_of_pieces(f2))]
        allp = sum(sets, Counter())
        if set(allp) != EG or any(v > 1 for v in allp.values()):
            errs.append("phi/phim/f2 三组未划分 E(G)")
        if set(sum(sets[:2], Counter())) != {tuple(sorted(e)) for e in W}:
            errs.append("phi ⊔ phim != E(W)")
        for name, ps in (("phi", phi), ("phim", phim)):
            lens = []
            for p in ps:
                ok, why = is_cycle_like([tuple(e) for e in p])
                if not ok:
                    errs.append(f"{name} 件不合法（{why}）")
                elif why.startswith("cycle"):
                    lens.append(int(why[6:-1]))
            if lens and min(lens) < 4:
                errs.append(f"{name} 含三角形（圈长 {min(lens)}）")
            gsub = nx.Graph()
            gsub.add_edges_from(edges_of_pieces(ps))
            tri = sum(v for _, v in nx.triangles(gsub).items())
            if tri != 0:
                errs.append(f"{name} 三角形数 {tri//3} != 0")
            stats[f"{name}_comps"] = len(ps)
        stats["comp_eq"] = (len(phi) == len(phim))
    return (len(errs) == 0), errs + notes, stats


def main(files):
    total = 0
    bad = 0
    failures = []
    per_file = {}
    for fp in files:
        cnt = 0
        badf = 0
        hist_n = {}
        with open(fp) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                cnt += 1
                ok, errs, stats = check_record(rec)
                key = rec["n"]
                hist_n.setdefault(key, Counter())[stats["npieces"]] += 1
                if "comp_eq" in stats:
                    hist_n[key + 10000] = hist_n.get(key + 10000, Counter())
                    hist_n[key + 10000][bool(stats["comp_eq"])] += 1
                if not ok:
                    bad += 1
                    badf += 1
                    failures.append({"file": fp, "tag": rec.get("tag"), "errs": errs})
        total += cnt
        per_file[fp] = {"records": cnt, "failures": badf,
                        "npieces_hist": {str(k): dict(v) for k, v in sorted(hist_n.items())}}
    out = {"files": per_file, "total_records": total,
           "total_failures": len(failures), "failures": failures[:50]}
    print(json.dumps(out, indent=1, ensure_ascii=False))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
