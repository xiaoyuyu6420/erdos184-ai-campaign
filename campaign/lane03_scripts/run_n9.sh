#!/bin/zsh
# n=9 定向族扫描（nice 低优先级，顺序执行；全枚举 2^36 不可行——简报口径见 lane 文档 §8 补充）
cd "$(dirname "$0")"
{
echo "== bip 全部侧划分 (n=9 二部图全覆盖) =="
./f_enum9 bip 1 8
./f_enum9 bip 2 7
./f_enum9 bip 3 6
./f_enum9 bip 4 5
echo "== join K_j ∨ H (j=2,3,4; j=1 的 2^28 若时间允许单独跑) =="
./f_enum9 join 2 7
./f_enum9 join 3 6
./f_enum9 join 4 5
./f_enum9 thresh 9
echo "== join 1 8 (2^28, 低优先级长跑) =="
./f_enum9 join 1 8
echo ALL_N9_DONE
} > n9_results.txt 2> n9_progress.log &
echo "n9 sweep launched pid $!"
