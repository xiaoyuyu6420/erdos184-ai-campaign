#!/usr/bin/env python3
"""h_D_compare.py — D 任务比较器（修正"含墙钟字段"的假不一致）。

比较 run_d1 / run_d2（同 PYTHONHASHSEED=0 两遍）与 run_d3（PYTHONHASHSEED=12345）：
  1) 证书 JSONL：sha256 必须逐字节一致；
  2) 摘要 JSON：剔除墙钟字段 elapsed_s 后内容必须一致（时间字段本身不可复现，属预期）。
输出 PASS/FAIL 与逐文件明细。
"""
import hashlib
import json
import sys

RUNS = ["run_d1", "run_d2", "run_d3"]
FILES = ["A_n10.jsonl", "A_n11.jsonl", "A_n12.jsonl"]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ok = True
    print("== 证书 JSONL sha256 ==")
    for fn in FILES:
        hs = {r: sha(f"{r}/{fn}") for r in RUNS}
        same = len(set(hs.values())) == 1
        ok &= same
        print(f"  {fn}: {'逐字节一致' if same else '*** 不一致 ***'}  {hs['run_d1'][:16]}...")
        if not same:
            for r, h in hs.items():
                print(f"     {r}: {h}")
    print("== 摘要 JSON（剔除墙钟 elapsed_s）==")
    for fn in FILES:
        ds = {}
        for r in RUNS:
            d = json.load(open(f"{r}/{fn}.summary.json"))
            d.pop("elapsed_s", None)
            ds[r] = d
        same = ds["run_d1"] == ds["run_d2"] == ds["run_d3"]
        ok &= same
        print(f"  {fn}.summary.json: {'内容一致' if same else '*** 不一致 ***'}")
        if not same:
            for r in RUNS[1:]:
                for k in ds["run_d1"]:
                    if ds["run_d1"][k] != ds[r].get(k):
                        print(f"     差异 {r}: {k}")
    print("D 复现性:", "PASS（证书逐字节一致；摘要仅墙钟字段不同）" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
