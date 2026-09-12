#!/bin/zsh
# lane03 收尾 kst 精算队列（2026-09-11 第三次上阵）。三队列并行，结果追加到 kst_big_results.txt
cd "$(dirname "$0")"
ulimit -s 262144
{
echo "== kst 收尾批次 $(date) =="
./kst_memo 2 8
./kst_memo 2 9
./kst_memo 3 10
./kst_memo 3 11
./kst_memo 3 12
./kst_memo 4 7
echo "QUEUE_A_DONE"
} > kst_qA.txt 2>&1 &
{
./kst_memo 4 8
./kst_memo 6 6
echo "QUEUE_B_DONE"
} > kst_qB.txt 2>&1 &
{
./kst_memo 5 6
echo "QUEUE_C_DONE"
} > kst_qC.txt 2>&1 &
wait
cat kst_qA.txt kst_qB.txt kst_qC.txt > kst_big_results.txt
echo ALL_KST_DONE
