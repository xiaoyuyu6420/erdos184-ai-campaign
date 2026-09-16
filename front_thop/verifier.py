#!/usr/bin/env python3
"""
HOP(2^<s>, 2m1, ..., 2mt) seating 层金标准验证器（独立实现）.

输入: n (对数), m_list (圆桌的 m_i 列表, 每张 >=2), seating
seating: list of nights; 每个 night = list of tables; 每个 table = 人的循环座位列表.
人编号 0..2n-1, 人 2i 与 2i+1 是夫妻 i.

检查:
  (V1) 每晚每人恰好出现一次
  (V2) 桌大小集合恰为 s 个 2 + 各圆桌 2m_i (作为多重集)
  (V3) 每晚每人与配偶邻座(2 人桌自动; 圆桌循环序两邻恰一为配偶)
  (V4) 全程每个非配偶对恰好邻座一次
  (V5) (可选) 晚数 == 2n(n-1)/m, m=sum(m_i)  [必要条件满足时的期望晚数]
返回 (ok, 消息列表).
"""


def verify(n, m_list, seating, expect_gamma=None):
    msgs = []
    m = sum(m_list)
    partner = {2 * i: 2 * i + 1 for i in range(n)}
    partner.update({2 * i + 1: 2 * i for i in range(n)})

    # 邻座对计数: frozenset({a,b}) -> 次数 (只记非配偶对)
    adj_count = {}
    total_person_nights = 0

    for k, night in enumerate(seating):
        seen = []
        sizes = []
        for t_idx, table in enumerate(night):
            L = len(table)
            sizes.append(L)
            seen.extend(table)
            if L == 2:
                a, b = table
                if partner[a] != b:
                    msgs.append(f"night{k} table{t_idx}: 2人桌非夫妻 {table}")
                continue
            if L < 4 or L % 2 != 0:
                msgs.append(f"night{k} table{t_idx}: 非法桌大小 {L}")
                continue
            if L // 2 not in m_list:
                msgs.append(f"night{k} table{t_idx}: 桌大小 {L} 不在规格中")
                continue
            for pos, p in enumerate(table):
                left, right = table[(pos - 1) % L], table[(pos + 1) % L]
                if partner[p] not in (left, right):
                    msgs.append(f"night{k} table{t_idx}: 人{p} 邻座 {left},{right} 无配偶")
                for q in (left, right):
                    if partner[p] != q and p < q:  # 只从较小端记一次, 避免双边重复计数
                        key = frozenset((p, q))
                        adj_count[key] = adj_count.get(key, 0) + 1
        if sorted(seen) != list(range(2 * n)):
            msgs.append(f"night{k}: 人员覆盖不完整/重复")
        if sorted(sizes) != sorted([2] * (n - m) + [2 * mi for mi in m_list]):
            msgs.append(f"night{k}: 桌大小多重集不符: {sorted(sizes)}")
        total_person_nights += len(seen)

    # V4: 每个非配偶对恰一次
    all_pairs = (2 * n) * (2 * n - 1) // 2 - n
    if len(adj_count) != all_pairs or any(c != 1 for c in adj_count.values()):
        bad_over = [p for p, c in adj_count.items() if c > 1]
        # 找缺失对
        missing = []
        for a in range(2 * n):
            for b in range(a + 1, 2 * n):
                if partner[a] == b:
                    continue
                if frozenset((a, b)) not in adj_count:
                    missing.append((a, b))
        msgs.append(
            f"V4 失败: 非配偶对应 {all_pairs}, 出现 {len(adj_count)} 种, "
            f"超1次 {len(bad_over)} 个, 缺失 {len(missing)} 个 (如 {missing[:5]})"
        )
        return False, msgs

    gamma_expected = expect_gamma if expect_gamma is not None else 2 * n * (n - 1) // m
    if len(seating) != gamma_expected:
        msgs.append(f"晚数 {len(seating)} != 期望 {gamma_expected}")
        return False, msgs

    msgs.append(f"OK: {len(seating)} 晚, {all_pairs} 个非配偶对全部恰好邻座一次")
    return True, msgs


if __name__ == "__main__":
    pass
