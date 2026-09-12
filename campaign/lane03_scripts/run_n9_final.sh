#!/bin/zsh
# lane03 收尾 n=9 定向族（去冗余 gjoin 版）。结果: n9_final_results.txt
cd "$(dirname "$0")"
{
echo "== n=9 定向族收尾 $(date) =="
./f_enum9m thresh 9
./f_one gjoin 4 5 8
./f_one gjoin 3 6 8
./f_one gjoin 2 7 8
echo ALL_N9_FINAL_DONE
} > n9_final_results.txt 2> n9_final_progress.log
