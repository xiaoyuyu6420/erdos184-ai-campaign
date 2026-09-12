#!/bin/zsh
# n=8 全枚举：32 块 × 2^23，每次最多 9 个并发（留 1 核给系统/n=9 任务）
cd "$(dirname "$0")"
T=268435456; C=8388608
for c in $(seq 0 31); do
  lo=$((c * C)); hi=$(((c + 1) * C))
  while [ $(jobs -r | wc -l) -ge 9 ]; do sleep 2; done
  ./f_enum9 full 8 $lo $hi > out8_$c.txt 2> out8_$c.err &
done
wait
echo ALL_N8_DONE
