#!/bin/zsh
# 全 Parikh 扫描：对每个 (n, x) 判定是否存在 theta < T 的词。
# T = t_x + t_{n-x}（x>=4）；x in {0,1,2,3} 用定理值复核。
# 输出 CSV 追加到 sweep_results.csv
cd /Users/munich/Desktop/数学/front_abs
nmax=${1:-40}
tl=${2:-600}
echo "n,x,T,status,min_found,word,nodes,secs" > sweep_results.csv
for (( n = 8; n <= nmax; n++ )); do
  for (( x = 0; x * 2 <= n; x++ )); do
    y=$(( n - x ))
    if (( x >= 4 )); then
      T=$(( (x + 2) / 4 + (y + 2) / 4 ))
    else
      case $x in
        0) T=$(( n / 2 )) ;;
        1) T=$(( n / 4 )) ;;
        2) T=$(( (n - 2) / 2 )) ;;
        3) T=$(( (n + 2) / 4 )) ;;
      esac
    fi
    start=$(date +%s.%N)
    out=$(./search $n $x $T $tl)
    end=$(date +%s.%N)
    secs=$(echo "$end $start" | awk '{printf "%.2f", $1-$2}')
    st=$(echo "$out" | grep -q NO_WORD_BELOW_T && echo OK || echo CAND)
    if [[ $st == "OK" ]]; then minfound=$T; word=-; else minfound=$(echo "$out" | grep BEST_EXACT | awk '{print $2}'); word=$(echo "$out" | grep BEST_EXACT | awk '{print $3}'); fi
    nodes=$(echo "$out" | grep -o 'nodes=[0-9]*' | head -1 | cut -d= -f2)
    ab=$(echo "$out" | grep -o 'aborted=[01]' | cut -d= -f2)
    [[ $ab == "1" ]] && st="ABORTED"
    echo "$n,$x,$T,$st,$minfound,$word,$nodes,$secs" | tee -a sweep_results.csv
  done
done
echo "SWEEP DONE n<=$nmax"
