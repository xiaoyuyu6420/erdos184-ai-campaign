"""resume2.py — 补齐 campaign_state.json 的 G 族缺口 + 越前沿采样点 (上一棒未完成的尾巴).
复用 campaign.py 的全部验证协议 (三重验证 + 类型检查 + 交集检查), 断点续跑兼容.
"""
import sys, json
sys.path.insert(0, '/Users/munich/Desktop/数学/front_tlat')
import campaign as C

st = C.load_state()
done = set(st['done'])
gaps_G = [k for k in range(9, 501) if f'G_{4*k+2}' not in done]
gaps_H = [k for k in range(9, 501) if f'H_{4*k}' not in done]
C.log(f'=== resume2 start: G gaps k={gaps_G} | H gaps k={gaps_H} ===')
if gaps_H:
    C.do_family('H', gaps_H)
if gaps_G:
    C.do_family('G', gaps_G)
# 越前沿采样 (论文前沿 10000 之上), 单点预算放大
C.log('=== resume2: frontier samples ===')
C.do_family('H', [2501, 3000, 3501, 4000, 4501, 5001])
C.do_family('G', [2501, 3000, 3501, 4000, 4501, 5001])
C.log('=== resume2 complete ===')
print('RESUME2 COMPLETE', flush=True)
