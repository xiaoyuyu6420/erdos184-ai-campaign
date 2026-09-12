/*
 * f_one.c — lane03 收尾补充工具（第三稿）。
 *
 * 模式:
 *   one <n> <mask>        精确计算单个 n 点图（边掩码, 位 i = 边按 (u,v) u<v 字典序）的 ce。
 *                         无剪枝（f0=0 语义），精确 packing。限 n <= 11（NE <= 55 <= 64 bit）。
 *   gjoin <j> <k> [f0]    K_j ∨ H 定向族扫描, H 取遍 k 点核的全部 2^{k(k-1)/2} 个子图。
 *                         这是 f_enum9 join 模式的去冗余修正版: f_enum9 的 join 模式把
 *                         NE = C(n,2) 个位全部当可变位枚举（固定边已在 fixmask 中）,
 *                         实际不同图只有 2^{C(k,2)} 个, 被重复扫 2^{C(j,2)+jk} 倍。
 *                         本版只枚举核边位, 语义（greedy 种子、exact_ce）与 f_enum9 一致。
 *
 * 交叉验证要求（跑正式数据前必须全过）:
 *   one 4 63 = 3 (K_4); one 5 1023 = 2 (K_5 双 Hamilton 圈);
 *   one 6 4060 = 4 (K_{3,3}); one 7 32767 = 7 (G_5 = f(7) witness, 对齐 f_enum);
 *   gjoin 2 5 6 = 7 且 witness = 核星形位 0..3 (对齐 f_enum n=7)。
 *
 * 编译: cc -O2 -o f_one f_one.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define MAXN 12
#define MAXE 66
#define MAXCIRC 200000

static int N, NE;
static int eu[MAXE], ev[MAXE];
static int eidx_tab[MAXN][MAXN];
static uint64_t fixmask;              /* gjoin 模式的固定边（K_j 团 + 交叉边） */
static int core_eu[MAXE], core_ev[MAXE]; /* gjoin: 可变位 p -> 核边 (u,v) */
static int NCORE;

typedef struct {
    uint64_t circ_mask[MAXCIRC];
    int      n_circ;
    int64_t  suffix[MAXCIRC + 2];
    int64_t  best_save;
    uint64_t c_m[MAXCIRC];
    int64_t  c_s[MAXCIRC];
} Ctx;

typedef struct { uint64_t m; int64_t s; } CircSort;
static int cmp_desc(const void *a, const void *b) {
    int64_t sa = ((const CircSort*)a)->s, sb = ((const CircSort*)b)->s;
    return (sb > sa) - (sb < sa);
}

static inline uint64_t rng_next(uint64_t *s) {
    uint64_t x = *s; x ^= x << 13; x ^= x >> 7; x ^= x << 17;
    return *s = x;
}
static inline uint64_t emask_ab(int a, int b) { return (uint64_t)1 << eidx_tab[a < b ? a : b][a < b ? b : a]; }

static uint64_t find_cycle(const uint32_t *adj, uint64_t *seed) {
    int color[MAXN], par[MAXN], pos[MAXN];
    int stack[MAXN], path[MAXN], order[MAXN];
    memset(color, 0, sizeof(color));
    for (int i = 0; i < N; i++) order[i] = i;
    for (int i = N - 1; i > 0; i--) { int j = rng_next(seed) % (i + 1); int t = order[i]; order[i] = order[j]; order[j] = t; }
    for (int si = 0; si < N; si++) {
        int s = order[si];
        if (color[s] || adj[s] == 0) continue;
        memset(par, -1, sizeof(par));
        memset(pos, 0, sizeof(pos));
        int top = 0, plen = 0;
        stack[top++] = s; path[plen++] = s; color[s] = 1;
        while (top > 0) {
            int u = stack[top - 1];
            if (pos[u] >= N) { top--; plen--; color[u] = 2; continue; }
            int w = pos[u]++;
            if (!(adj[u] >> w & 1)) continue;
            if (w == par[u]) continue;
            if (color[w] == 1) {
                int k = plen - 1;
                while (k >= 0 && path[k] != w) k--;
                if (plen - k < 3) continue;
                uint64_t mask = emask_ab(u, w);
                for (int i2 = k; i2 < plen - 1; i2++) mask |= emask_ab(path[i2], path[i2 + 1]);
                return mask;
            }
            if (color[w] == 0) {
                color[w] = 1; par[w] = u;
                stack[top++] = w; path[plen++] = w;
            }
        }
    }
    return 0;
}

static int64_t greedy_save(const uint32_t *adj0, uint64_t seed) {
    uint32_t adj[MAXN];
    memcpy(adj, adj0, sizeof(uint32_t) * N);
    uint64_t s = seed | 1;
    int64_t save = 0;
    for (;;) {
        uint64_t c = find_cycle(adj, &s);
        if (!c) break;
        save += __builtin_popcountll(c) - 1;
        for (int e = 0; e < NE; e++)
            if (c >> e & 1) { adj[eu[e]] &= ~(1u << ev[e]); adj[ev[e]] &= ~(1u << eu[e]); }
    }
    return save;
}

static void rec_dfs(Ctx *X, const uint32_t *adj, int s, int *path, int *plen, uint64_t *ue, int cur, uint32_t in_path) {
    if (*plen >= 3 && (adj[cur] >> s & 1)) {
        int e_close = eidx_tab[s < cur ? s : cur][s < cur ? cur : s];
        if (!(*ue >> e_close & 1) && X->n_circ < MAXCIRC) {
            X->circ_mask[X->n_circ] = *ue | (1ull << e_close);
            X->n_circ++;
        }
    }
    for (int w = s + 1; w < N; w++) {
        if (in_path >> w & 1) continue;
        if (!(adj[cur] >> w & 1)) continue;
        int ei = eidx_tab[cur < w ? cur : w][cur < w ? w : cur];
        if (*ue >> ei & 1) continue;
        path[*plen] = w;
        int sv_len = *plen; uint64_t sv_ue = *ue;
        (*plen)++; *ue |= 1ull << ei;
        rec_dfs(X, adj, s, path, plen, ue, w, in_path | (1u << w));
        *plen = sv_len; *ue = sv_ue;
    }
}

/* advisory memo（与 f_enum9.c 同构） */
typedef struct { uint64_t key; int64_t val; uint32_t gen; } MemoEnt;
#define MEMO_BITS 22
#define MEMO_SIZE (1u << MEMO_BITS)
static MemoEnt *memo_tbl;
static uint32_t memo_gen = 0;
static inline uint64_t memo_hash(uint64_t k) { return k * 0x9E3779B97F4A7C15ull >> (64 - MEMO_BITS); }
#define MEMO_KEY(i, rem) (((rem) << 16) | (uint64_t)(i))
#define PROBE_LIMIT 64

static int64_t best_capped(Ctx *X, int i, uint64_t rem, int64_t cap) {
    if (i == X->n_circ || rem == 0) return 0;
    uint64_t key = MEMO_KEY(i, rem);
    uint64_t h = memo_hash(key);
    for (int p = 0; p < PROBE_LIMIT; p++) {
        MemoEnt *e = &memo_tbl[h];
        if (e->gen != memo_gen) break;
        if (e->key == key) return e->val;
        h = (h + 1) & (MEMO_SIZE - 1);
    }
    int64_t best = best_capped(X, i + 1, rem, cap);
    if (best < cap && (X->c_m[i] & rem) == X->c_m[i]) {
        int64_t cand = X->c_s[i] + best_capped(X, i + 1, rem & ~X->c_m[i], cap);
        if (cand > best) best = cand;
    }
    if (best > cap) best = cap;
    h = memo_hash(key);
    for (int p = 0; p < PROBE_LIMIT; p++) {
        MemoEnt *e = &memo_tbl[h];
        if (e->gen != memo_gen) { e->key = key; e->val = best; e->gen = memo_gen; break; }
        if (e->key == key) break;
        h = (h + 1) & (MEMO_SIZE - 1);
    }
    return best;
}

static void *memo_alloc(void) {
    if (!memo_tbl) memo_tbl = calloc(MEMO_SIZE, sizeof(MemoEnt));
    if (!memo_tbl) { fprintf(stderr, "memo alloc failed\n"); exit(3); }
    return memo_tbl;
}

/* 精确 ce。fcur=0 时 cap = m+1 > 任何 save，绝无截断 => 全精确。 */
static int exact_ce(Ctx *X, const uint32_t *adj, int m, int fcur) {
    X->n_circ = 0;
    int path[MAXN]; int plen; uint64_t ue;
    for (int s = 0; s < N; s++) {
        path[0] = s; plen = 1; ue = 0;
        rec_dfs(X, adj, s, path, &plen, &ue, s, 1u << s);
    }
    if (X->n_circ >= MAXCIRC) { fprintf(stderr, "MAXCIRC overflow\n"); exit(4); }
    static CircSort cs[MAXCIRC];
    for (int i = 0; i < X->n_circ; i++) {
        cs[i].m = X->circ_mask[i];
        cs[i].s = __builtin_popcountll(X->circ_mask[i]) - 1;
    }
    int nc = X->n_circ;
    qsort(cs, nc, sizeof(CircSort), cmp_desc);
    for (int i = 0; i < nc; i++) { X->c_m[i] = cs[i].m; X->c_s[i] = cs[i].s; }
    memo_alloc();
    memo_gen++;
    int64_t cap = (int64_t)m - (fcur - 1);
    int64_t save = best_capped(X, 0, ((uint64_t)1 << NE) - 1, cap);
    if (save >= cap) return -1;
    return (int)(m - save);
}

static void build_adj(uint32_t *adj, uint64_t gm, int *m_out) {
    for (int i = 0; i < N; i++) adj[i] = 0;
    int m = 0;
    for (int e = 0; e < NE; e++)
        if (gm >> e & 1) {
            adj[eu[e]] |= 1u << ev[e];
            adj[ev[e]] |= 1u << eu[e];
            m++;
        }
    *m_out = m;
}

static void set_edges_all(void) {
    NE = 0;
    for (int u = 0; u < N; u++)
        for (int v = u + 1; v < N; v++) {
            eu[NE] = u; ev[NE] = v;
            eidx_tab[u][v] = eidx_tab[v][u] = NE;
            NE++;
        }
}

int main(int argc, char **argv) {
    if (argc < 3) {
        fprintf(stderr, "usage: %s one <n> <mask>\n       %s gjoin <j> <k> [f0]\n", argv[0], argv[0]);
        return 1;
    }
    Ctx *X = calloc(1, sizeof(Ctx));
    uint32_t adj[MAXN]; int m;

    if (!strcmp(argv[1], "one")) {
        N = atoi(argv[2]);
        uint64_t G = strtoull(argv[3], NULL, 0);
        if (N < 1 || N > 11) { fprintf(stderr, "n must be 1..11 (NE<=64 bit)\n"); return 1; }
        set_edges_all();
        if (NE > 64) { fprintf(stderr, "NE overflow\n"); return 1; }
        build_adj(adj, G, &m);
        printf("n=%d mask=0x%llx m=%d ce=%d  (圈数=%d)\n", N, (unsigned long long)G, m,
               exact_ce(X, adj, m, 0), X->n_circ);
        return 0;
    }
    if (!strcmp(argv[1], "gjoin")) {
        int j = atoi(argv[2]), k = atoi(argv[3]);
        N = j + k;
        set_edges_all();
        fixmask = 0;
        NCORE = 0;
        for (int u = 0; u < N; u++)
            for (int v = u + 1; v < N; v++) {
                if (u >= j) {                       /* 核内边 = 可变位 */
                    core_eu[NCORE] = u; core_ev[NCORE] = v; NCORE++;
                } else {
                    fixmask |= 1ull << eidx_tab[u][v];
                }
            }
        if (NCORE > 30) { fprintf(stderr, "core too big\n"); return 1; }
        long long total = 1ll << NCORE;
        long long f_cur = (argc >= 5) ? atoll(argv[4]) : (long long)(N - 1);
        fprintf(stderr, "mode=gjoin n=%d core=%d bits=%d total=%lld f0=%lld\n", N, k, NCORE, total, f_cur);
        long long solved = 0, bestg = -1;
        for (long long gm = 0; gm < total; gm++) {
            uint64_t G = fixmask;
            for (int p = 0; p < NCORE; p++)
                if (gm >> p & 1) G |= 1ull << eidx_tab[core_eu[p] < core_ev[p] ? core_eu[p] : core_ev[p]]
                                             [core_eu[p] < core_ev[p] ? core_ev[p] : core_eu[p]];
            build_adj(adj, G, &m);
            int fcur = (int)f_cur;
            if (m < fcur) continue;
            if (m - greedy_save(adj, (uint64_t)gm * 2654435761ull + 1) < fcur) continue;
            solved++;
            int val = exact_ce(X, adj, m, fcur);
            if (val < 0) continue;
            if (val > f_cur) {
                f_cur = val; bestg = gm;
                fprintf(stderr, "NEW f(%d) >= %d  (core 0x%llx, m=%d)\n", N, val, (unsigned long long)gm, m);
            }
        }
        printf("mode=gjoin K_%d∨H(k=%d): max ce = %lld  [精算图数: %lld; 最优核掩码 0x%llx / 0x%llx]\n",
               j, k, f_cur, solved, (unsigned long long)bestg, (unsigned long long)fixmask);
        return 0;
    }
    fprintf(stderr, "unknown mode\n");
    return 1;
}
