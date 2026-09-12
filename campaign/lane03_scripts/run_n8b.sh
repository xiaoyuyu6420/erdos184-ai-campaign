#!/bin/zsh
# n=8 全枚举 v2：f_enum9m（memo 版），32 块 × 2^23，9 并发，按块序执行（稀疏块先完成）
cd "$(dirname "$0")"
C=8388608
for c in $(seq 0 31); do
  lo=$((c * C)); hi=$(((c + 1) * C))
  while [ $(jobs -r | wc -l) -ge 9 ]; do sleep 2; done
  ./f_enum9m full 8 $lo $hi > out8_$c.txt 2> out8_$(c).err &
done
wait
echo ALL_N8_DONE >> n8_master.log
