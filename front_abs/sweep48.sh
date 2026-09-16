#!/bin/zsh
cd /Users/munich/Desktop/数学/front_abs
echo "n,x,T,status,min_found,word,nodes,secs" > sweep_48.csv
for (( n = 45; n <= 48; n++ )); do
  for (( x = 0; x * 2 <= n; x++ )); do
    y=$(( n - x ))
    if (( x >= 4 )); then T=$(( (x + 2) / 4 + (y + 2) / 4 ))
    else
      case $x in
        0) T=$(( n / 2 )) ;;
        1) T=$(( n / 4 )) ;;
        2) T=$(( (n - 2) / 2 )) ;;
        3) T=$(( (n + 2) / 4 )) ;;
      esac
    fi
    start=$(date +%s.%N)
    out=$(./search $n $x $T 1800)
    end=$(date +%s.%N)
    secs=$(echo "$end $start" | awk '{printf "%.2f", $1-$2}')
    st=$(echo "$out" | grep -q NO_WORD_BELOW_T && echo OK || echo CAND)
    if [[ $st == "OK" ]]; then minfound=$T; word=-; else minfound=$(echo "$out" | grep BEST_EXACT | awk '{print $2}'); word=$(echo "$out" | grep BEST_EXACT | awk '{print $3}'); fi
    nodes=$(echo "$out" | grep -o 'nodes=[0-9]*' | head -1 | cut -d= -f2)
    ab=$(echo "$out" | grep -o 'aborted=[01]' | cut -d= -f2)
    [[ $ab == "1" ]] && st="ABORTED"
    echo "$n,$x,$T,$st,$minfound,$word,$nodes,$secs" | tee -a sweep_48.csv
  done
done
echo DONE48
