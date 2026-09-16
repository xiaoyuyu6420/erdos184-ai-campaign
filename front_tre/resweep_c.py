#!/usr/bin/env python3
"""修复后片引理扫描独立重跑入口：n=4..14 全量（真值口径）。"""
import sys, json
sys.path.insert(0, '/Users/munich/Desktop/数学/front_tre')
from sweep3 import run_piece_lemma_sweep

outf = open('/Users/munich/Desktop/数学/front_tre/results3.jsonl', 'a', buffering=1)
run_piece_lemma_sweep(range(4, 15), outf)
outf.close()
print("resweep C done")
