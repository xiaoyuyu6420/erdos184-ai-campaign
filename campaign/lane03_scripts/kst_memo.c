/*
 * kst_memo.c — ce(K_{s,t}) 精确计算（memo 化 packing，解决 K_{3,8+} 无 memo 的指数爆炸）。
 *
 * 与 f_enum9 的差别：
 *   - packing DFS 加哈希 memo（key=(圈序号 i, 剩余边集 rem)，advisory：冲突只降速不损正确性）；
 *   - MAXCIRC = 1,500,000：K_{5,6} 有 1,280,910 个圈（4-圈150 + 6-圈2400 + 8-圈189000 + 10-圈1089360），
 *     圈数超 MAXCIRC 会被静默丢弃 → max_save 低估 → ce 高估 → 结果无效，故容量必须覆盖全圈数。
 *     覆盖范围：K_{3,t} 任意 t（圈 ≤ 6），K_{4,t} 到 t=9（322k），K_{5,6}（1.28M）；K_{5,7}（4.26M）超限不可用。
 *   - 递归深度 = 圈数（可达 1.3M），必须在大栈下运行：ulimit -s 262144 (256MB)。
 *
 * 用法: ulimit -s 262144 && ./kst_memo s t
 * 编译: cc -O2 -o kst_memo kst_memo.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define MAXN 16
#define MAXCIRC 1500000
#define MEMO_BITS 24
#define MEMO_SIZE (1u << MEMO_BITS)
#define PROBE_LIMIT 128  /* 表近满时限长探测，找不到空槽就放弃缓存（advisory），防活锁 */

static int N, NE, nc;
static int eu[120], ev[120];
static int eidx_tab[MAXN][MAXN];

static uint64_t c_m[MAXCIRC];
static int64_t  c_s[MAXCIRC];
static uint64_t circ_mask[MAXCIRC];

/* memo：开放寻址 + 代数失效（本程序每进程只算一个图，gen 恒 1） */
static struct { uint64_t key; int64_t val; uint32_t gen; } *memo;
static uint32_t memo_gen = 0;

static inline uint64_t memo_hash(uint64_t k) { return k * 0x9E3779B97F4A7C15ull >> (64 - MEMO_BITS); }

/* 全局邻接数组 */
static uint32_t adjm[MAXN];

static void rec_cyc(int s, int *path, int plen, uint64_t ue, int cur, uint32_t in_path) {
    if (plen >= 3 && (adjm[cur] >> s & 1)) {
        int e_close = eidx_tab[s < cur ? s : cur][s < cur ? cur : s];
        if (!(ue >> e_close & 1) && nc < MAXCIRC) {
            circ_mask[nc++] = ue | (1ull << e_close);
        }
    }
    for (int w = s + 1; w < N; w++) {
        if (in_path >> w & 1) continue;
        if (!(adjm[cur] >> w & 1)) continue;
        int ei = eidx_tab[cur < w ? cur : w][cur < w ? w : cur];
        if (ue >> ei & 1) continue;
        path[plen] = w;
        int sv_len = plen; uint64_t sv_ue = ue;
        plen++; ue |= 1ull << ei;
        rec_cyc(s, path, plen, ue, w, in_path | (1u << w));
        plen = sv_len; ue = sv_ue;
    }
}

static int64_t best_from(int i, uint64_t rem) {
    if (i == nc || rem == 0) return 0;
    uint64_t key = (rem << 16) | (uint64_t)i;
    uint64_t h = memo_hash(key);
    for (int p = 0; p < PROBE_LIMIT; p++) {
        if (memo[h].gen != memo_gen) break;          /* 空槽 */
        if (memo[h].key == key) return memo[h].val;  /* 命中 */
        h = (h + 1) & (MEMO_SIZE - 1);
    }
    int64_t best = best_from(i + 1, rem);
    if ((c_m[i] & rem) == c_m[i]) {
        int64_t cand = c_s[i] + best_from(i + 1, rem & ~c_m[i]);
        if (cand > best) best = cand;
    }
    /* 插入：限长探测找空槽；找不到就放弃缓存（只降速不损正确性） */
    uint64_t h2 = memo_hash(key);
    for (int p = 0; p < PROBE_LIMIT; p++) {
        if (memo[h2].gen != memo_gen) { memo[h2] = (typeof(*memo)){key, best, memo_gen}; break; }
        if (memo[h2].key == key) break;
        h2 = (h2 + 1) & (MEMO_SIZE - 1);
    }
    return best;
}

typedef struct { uint64_t m; int64_t s; } CircSort;
static int cmp_desc(const void *a, const void *b) {
    int64_t sa = ((const CircSort*)a)->s, sb = ((const CircSort*)b)->s;
    return (sb > sa) - (sb < sa);
}

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: %s s t\n", argv[0]); return 1; }
    int s = atoi(argv[1]), t = atoi(argv[2]);
    N = s + t;
    NE = 0;
    for (int u = 0; u < s; u++)
        for (int v = 0; v < t; v++) {
            eu[NE] = u; ev[NE] = s + v;
            eidx_tab[u][s + v] = eidx_tab[s + v][u] = NE;
            NE++;
        }
    for (int i = 0; i < N; i++) adjm[i] = 0;
    for (int e = 0; e < NE; e++) { adjm[eu[e]] |= 1u << ev[e]; adjm[ev[e]] |= 1u << eu[e]; }

    /* 枚举全部简单圈（canonical：最小顶点起点） */
    nc = 0;
    int path[MAXN];
    for (int st = 0; st < N; st++) {
        path[0] = st;
        rec_cyc(st, path, 1, 0, st, 1u << st);
    }
    if (nc >= MAXCIRC) {
        printf("K_{%d,%d}: 圈数 %d >= MAXCIRC %d，结果不可信，拒绝输出\n", s, t, nc, MAXCIRC);
        return 2;
    }
    for (int i = 0; i < nc; i++) { c_m[i] = circ_mask[i]; c_s[i] = __builtin_popcountll(circ_mask[i]) - 1; }
    {
        static CircSort *cs = NULL;
        if (!cs) cs = malloc(sizeof(CircSort) * MAXCIRC);
        for (int i = 0; i < nc; i++) { cs[i].m = c_m[i]; cs[i].s = c_s[i]; }
        qsort(cs, nc, sizeof(CircSort), cmp_desc);
        for (int i = 0; i < nc; i++) { c_m[i] = cs[i].m; c_s[i] = cs[i].s; }
    }
    memo = calloc(MEMO_SIZE, sizeof(*memo));
    if (!memo) { fprintf(stderr, "memo alloc failed\n"); return 3; }
    memo_gen++;
    uint64_t full = 0;
    for (int e = 0; e < NE; e++) full |= 1ull << e;
    int64_t save = best_from(0, full);
    int ce = (int)(NE - save);
    printf("ce(K_{%d,%d}) = %d   (n=%d, m=%d, 圈数=%d)\n", s, t, ce, N, NE, nc);
    return 0;
}
