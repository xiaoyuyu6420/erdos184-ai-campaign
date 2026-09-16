"""diff_analysis.py — 论文测试向量 vs 我方阵的逐 entry 差异分析"""
import sys
sys.path.insert(0, '/Users/munich/Desktop/数学/front_tlat')
from latpack import *

for (fam, n, t), T in sorted(PAPER_TS.items()):
    bad = []
    for (r, c, s) in T:
        actual = symbol(fam, r, c, n)
        if actual != s:
            # 需要的 delta
            need = (s - r - c) % n
            need = need if need <= n // 2 else need - n
            bad.append((r, c, s, actual, need))
    tag = "OK " if not bad else "DIFF"
    print(f"{fam}_{n}#{t}: {tag} n_bad={len(bad)}", bad if bad else "")
    if bad:
        # 试着判断是列错还是符号错：对该行找使 delta=0 的列
        for (r, c, s, actual, need) in bad:
            cands = [cc for cc in range(n) if (r + cc) % n == s and cc not in [x[1] for x in T if x[0] != r]]
            print(f"    不一致 ({r},{c},{s}): 实算符号 {actual}, 需要δ={need}; 同行δ=0且列不冲突的候选列: {cands}")
