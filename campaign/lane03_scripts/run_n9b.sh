#!/bin/zsh
cd "$(dirname "$0")"
{
echo "== join K_j ∨ H (f_enum9m memo 版) =="
./f_enum9m join 2 7
./f_enum9m join 3 6
./f_enum9m join 4 5
./f_enum9m thresh 9
echo "== join 1 8 (2^28 长跑，可能超时未完成) =="
./f_enum9m join 1 8
echo ALL_N9B_DONE
} > n9b_results.txt 2> n9b_progress.log &
echo "n9b launched pid $!"
