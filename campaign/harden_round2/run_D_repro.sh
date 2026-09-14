#!/bin/sh
# run_D_repro.sh — D 任务：复现性抽检。
# 用固定 PYTHONHASHSEED 把 A 部分主检查（n=10 含 exact ce、n=11、n=12）完整跑三遍：
#   run_d1: PYTHONHASHSEED=0      （第 1 遍）
#   run_d2: PYTHONHASHSEED=0      （第 2 遍，须与第 1 遍逐字节一致）
#   run_d3: PYTHONHASHSEED=12345  （不同 hash 序，检验结果不依赖集合迭代序）
# 然后 sha256 对比。
set -e
cd "$(dirname "$0")"
for d in run_d1 run_d2 run_d3; do mkdir -p $d; done
run_all () {
  seed=$1; out=$2
  echo "=== PYTHONHASHSEED=$seed -> $out ==="
  PYTHONHASHSEED=$seed python3 h_A_enum.py --n 10 --g6 data/geng_10_d3.g6 --out $out/A_n10.jsonl --exact
  PYTHONHASHSEED=$seed python3 h_A_enum.py --n 11 --g6 data/geng_11_d4.g6 --out $out/A_n11.jsonl
  PYTHONHASHSEED=$seed python3 h_A_enum.py --n 12 --g6 data/geng_12_d5.g6 --out $out/A_n12.jsonl
}
run_all 0 run_d1
run_all 0 run_d2
run_all 12345 run_d3
echo "=== sha256 ==="
(cd run_d1 && shasum -a 256 A_n10.jsonl A_n10.jsonl.summary.json A_n11.jsonl A_n11.jsonl.summary.json A_n12.jsonl A_n12.jsonl.summary.json) > logs/D_sha_run_d1.txt
(cd run_d2 && shasum -a 256 A_n10.jsonl A_n10.jsonl.summary.json A_n11.jsonl A_n11.jsonl.summary.json A_n12.jsonl A_n12.jsonl.summary.json) > logs/D_sha_run_d2.txt
(cd run_d3 && shasum -a 256 A_n10.jsonl A_n10.jsonl.summary.json A_n11.jsonl A_n11.jsonl.summary.json A_n12.jsonl A_n12.jsonl.summary.json) > logs/D_sha_run_d3.txt
python3 h_D_compare.py | tee logs/D_compare.log
echo "（首轮 shasum 直比会因 summary 的墙钟 elapsed_s 报差异；上面 h_D_compare.py 已剔除时间字段做内容比较）"
if diff -q logs/D_sha_run_d1.txt logs/D_sha_run_d2.txt >/dev/null; then
  echo "D1 vs D2（同 hash seed 两遍）: 逐字节一致"
else
  echo "D1 vs D2: *** 不一致 ***"; diff logs/D_sha_run_d1.txt logs/D_sha_run_d2.txt || true
fi
if diff -q logs/D_sha_run_d1.txt logs/D_sha_run_d3.txt >/dev/null; then
  echo "D1 vs D3（不同 PYTHONHASHSEED）: 逐字节一致"
else
  echo "D1 vs D3: *** 不一致（结果依赖集合迭代序）***"; diff logs/D_sha_run_d1.txt logs/D_sha_run_d3.txt || true
fi
cat logs/D_sha_run_d1.txt
