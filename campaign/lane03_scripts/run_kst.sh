#!/bin/zsh
cd "$(dirname "$0")"
{
for st in "3,10" "3,11" "3,12" "4,7" "4,8" "5,5" "5,6"; do
  s=${st%,*}; t=${st#*,}
  /usr/bin/time -l ./kst_memo $s $t 2>&1 | grep -E "ce\(K|real"
done
echo ALL_KST_DONE
} > kst_big_results.txt 2>&1
