#!/usr/bin/env python3
"""阳性锚点: 手推解, 交 verifier 金标准终审."""

from verifier import verify

# 锚点0: HOP(2^0, 4, 4), n=4, s=0, m=4, gamma = 2*4*3/4 = 6 晚
# 夫妻 A,B,C,D; 每晚 K4 划分成 2+2 (即 K4 的 1-factor), 每桌 4 人交替
anchor_n4 = []
for factor in [("{A,B}|{C,D}", (0, 2), (4, 6)),
               ("{A,C}|{B,D}", (0, 4), (2, 6)),
               ("{A,D}|{B,C}", (0, 6), (2, 4))]:
    _, (a, b), (c, d) = factor
    for flip in (0, 1):
        t1 = [a, a + 1, b + flip, b + 1 - flip]
        t2 = [c, c + 1, d + flip, d + 1 - flip]
        anchor_n4.append([t1, t2])

# 锚点1: HOP(2^0, 6), n=3, m=3, gamma=4 (单圆桌, paper2 已解类)
anchor_hop6 = [
    [[1, 0, 2, 3, 5, 4]],
    [[1, 0, 3, 2, 4, 5]],
    [[1, 0, 4, 5, 2, 3]],
    [[1, 0, 5, 4, 3, 2]],
]

# 锚点2: HOP(2, 4), n=3, s=1, m1=2, gamma=6 (单圆桌, paper2 已解类)
anchor_hop2_4 = [
    [[0, 1], [2, 3, 4, 5]],
    [[0, 1], [2, 3, 5, 4]],
    [[2, 3], [0, 1, 4, 5]],
    [[2, 3], [0, 1, 5, 4]],
    [[4, 5], [0, 1, 2, 3]],
    [[4, 5], [0, 1, 3, 2]],
]

if __name__ == "__main__":
    cases = [
        ("HOP(4,4) n=4 [OPEN 类 n=4≡4 mod 8]", 4, [2, 2], anchor_n4),
        ("HOP(6) n=3 [已解锚点 单圆桌]", 3, [3], anchor_hop6),
        ("HOP(2,4) n=3 [已解锚点 单圆桌]", 3, [2], anchor_hop2_4),
    ]
    for name, n, ml, seating in cases:
        ok, msgs = verify(n, ml, seating)
        tag = "PASS" if ok else "FAIL"
        print(f"[{tag}] {name}: {msgs[-1]}")
        if not ok:
            for msg in msgs[:-1]:
                print("      ", msg)
