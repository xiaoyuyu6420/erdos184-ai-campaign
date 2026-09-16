"""hverify3.py — 第三棒：H 族 492 点在协议 v2 (逐行 δ 合法性) 下的独立全量重验.
背景: 第二棒报告声称「H 族逐行 δ 检查已补跑确认」, 但 campaign v2 的 do_family
会跳过 done 点, 且第一棒证书未存盘 — 该声称无法从现有 artifact 追溯. 本脚本
用独立 state/log 重跑 H 族 k=9..500 全部 492 点, 协议与 campaign v2 完全一致
(独立三重验证 + 类型检查 + 逐行 δ 检查 + 三交集为空).
资源纪律: 单线程, n<=2000 不触 swap 守卫.
"""
import sys, json, os
sys.path.insert(0, '/Users/munich/Desktop/数学/front_tlat')
import campaign as C

C.STATE_F = '/Users/munich/Desktop/数学/front_tlat/hverify3_state.json'
C.LOG_F = '/Users/munich/Desktop/数学/front_tlat/hverify3_log.txt'
json.dump({'done': []}, open(C.STATE_F, 'w'))
C.log('=== hverify3 start: H family full re-verification under protocol v2 ===')
C.do_family('H', range(9, 501))
st = json.load(open(C.STATE_F))
C.log(f'=== hverify3 complete: {len(st["done"])}/492 PASS ===')
print(f'HVERIFY3 COMPLETE: {len(st["done"])}/492', flush=True)
