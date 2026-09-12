/*
 * f_enum9.c — f_enum 的 n<=9 扩展版 + 定向族模式（lane03 收尾）。
 *
 * 改进（相对 f_enum.c）：
 *   - 边掩码 uint64_t（n=9 需 36 bits，uint32 不够）；
 *   - 圈排序改 qsort（原插入排序 O(circ^2)，K_8=8018 圈时是精算瓶颈）；
 *   - MAXCIRC=64000（K_9 全圈数 = 62814，恰够；K_10=496644 不适用，故限 n<=9）；
 *   - 新模式：bip / join / thresh / kst（n=9 全枚举 2^36 不可行，改定向族）。
 *
 * 语义与 f_enum.c 完全一致：ce(G) = m − max_save；贪心给 save 下界用于剪枝（保真实性），
 * 精算枚举全部简单圈 + DFS packing，返回精确 ce 或 -1（确认 ce < f_cur）。
 *
 * 用法:
 *   f_enum9 full  <n> [lo hi [f0]]     全枚举 2^NE（n<=8 实用；与 f_enum 交叉验证）
 *   f_enum9 bip   <s> <t> [lo hi [f0]] 枚举二部图全部 2^(st) 子集（侧 s,t）
 *   f_enum9 join  <j> <k> [lo hi [f0]] 枚举 K_j ∨ H，H 取遍 k 点图（2^(k(k-1)/2)）
 *   f_enum9 thresh <n> [f0]            枚举全部 2^(n-1) 个阈值图
 *   f_enum9 kst   <s> <t>              精确计算 ce(K_{s,t}) 一次
 * 编译: cc -O2 -o f_enum9 f_enum9.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define MAXN 10
#define MAXE 45
#define MAXCIRC 64000

static int N, NE;
static int eu[MAXE], ev[MAXE];
static int eidx_tab[MAXN][MAXN];
static uint64_t fixmask;              /* join 模式的固定边（K_j 团 + 交叉边） */
static uint64_t f_cur;

typedef struct {
    uint64_t circ_mask[MAXCIRC];
    int      n_circ;
    int64_t  suffix[MAXCIRC + 2];
    int64_t  best_save, cutoff_target;
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

/* 在 adj(live) 中找一个圈；返回圈边 mask（0=无圈）。 */
static uint64_t find_cycle(const uint32_t *adj, uint64_t *seed) {
    int color[MAXN] = {0}, par[MAXN], pos[MAXN];
    int stack[MAXN], path[MAXN], order[MAXN];
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

/* capped-memo packing：value(i,rem) = min(真最大额外节省, CAP)。
   CAP = cutoff_target+? 精算一次调用内固定 → memo 语义可靠（部分求值的结果 ≤ CAP，缓存安全）。
   memo 为 advisory：开放寻址 + 代数失效（每次 exact_ce 调用 gen++，跨图不共享）；表满时放弃缓存只降速。 */
typedef struct { uint64_t key; int64_t val; uint32_t gen; } MemoEnt;
#define MEMO_BITS 22
#define MEMO_SIZE (1u << MEMO_BITS)
static MemoEnt *memo_tbl;
static uint32_t memo_gen = 0;

static inline uint64_t memo_hash(uint64_t k) { return k * 0x9E3779B97F4A7C15ull >> (64 - MEMO_BITS); }
/* key: i < 2^16, rem < 2^45 → (rem<<16)|i 唯一 */
#define MEMO_KEY(i, rem) (((rem) << 16) | (uint64_t)(i))
#define PROBE_LIMIT 64

static int64_t best_capped(Ctx *X, int i, uint64_t rem, int64_t cap) {
    if (i == X->n_circ || rem == 0) return 0;
    uint64_t key = MEMO_KEY(i, rem);
    uint64_t h = memo_hash(key);
    for (int p = 0; p < PROBE_LIMIT; p++) {
        MemoEnt *e = &memo_tbl[h];
        if (e->gen != memo_gen) break;                 /* 空槽 */
        if (e->key == key) return e->val;              /* 命中 */
        h = (h + 1) & (MEMO_SIZE - 1);
    }
    int64_t best = best_capped(X, i + 1, rem, cap);    /* 跳过圈 i */
    if (best < cap && (X->c_m[i] & rem) == X->c_m[i]) {
        int64_t cand = X->c_s[i] + best_capped(X, i + 1, rem & ~X->c_m[i], cap);
        if (cand > best) best = cand;
    }
    if (best > cap) best = cap;
    /* 写缓存：找空槽（gen 不符即视为空），限长探测 */
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

/* 返回精确 ce；若确认 ce < fcur 返回 -1（剪枝语义）。fcur=0 时精算。 */
static int exact_ce(Ctx *X, const uint32_t *adj, int m, int fcur) {
    X->n_circ = 0;
    int path[MAXN]; int plen; uint64_t ue;
    for (int s = 0; s < N; s++) {
        path[0] = s; plen = 1; ue = 0;
        rec_dfs(X, adj, s, path, &plen, &ue, s, 1u << s);
    }
    static CircSort cs[MAXCIRC];
    for (int i = 0; i < X->n_circ; i++) {
        cs[i].m = X->circ_mask[i];
        cs[i].s = __builtin_popcountll(X->circ_mask[i]) - 1;
    }
    int nc = X->n_circ;
    qsort(cs, nc, sizeof(CircSort), cmp_desc);
    for (int i = 0; i < nc; i++) { X->c_m[i] = cs[i].m; X->c_s[i] = cs[i].s; }
    X->suffix[nc] = 0;
    for (int i = nc - 1; i >= 0; i--) X->suffix[i] = X->suffix[i + 1] + X->c_s[i];
    memo_alloc();
    memo_gen++;                              /* 新图 → 旧缓存全部失效 */
    int64_t cap = (int64_t)m - (fcur - 1);   /* 达到即证明 ce < fcur */
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
        fprintf(stderr,
            "usage: %s full <n> [lo hi [f0]]\n"
            "       %s bip <s> <t> [lo hi [f0]]\n"
            "       %s join <j> <k> [lo hi [f0]]\n"
            "       %s thresh <n> [f0]\n"
            "       %s kst <s> <t>\n", argv[0], argv[0], argv[0], argv[0], argv[0]);
        return 1;
    }
    const char *mode = argv[1];
    uint64_t fixed = 0;
    long long g_lo = 0, g_hi = 0;
    int f0_idx = -1;

    if (!strcmp(mode, "kst")) {
        int s = atoi(argv[2]), t = atoi(argv[3]);
        N = s + t;
        NE = 0;
        for (int u = 0; u < s; u++)
            for (int v = 0; v < t; v++) {
                eu[NE] = u; ev[NE] = s + v;
                eidx_tab[u][s + v] = eidx_tab[s + v][u] = NE;
                NE++;
            }
        fixmask = 0;
        f_cur = 0;
        Ctx *X = calloc(1, sizeof(Ctx));
        uint32_t adj[MAXN]; int m;
        build_adj(adj, ((uint64_t)1 << NE) - 1, &m);
        int val = exact_ce(X, adj, m, 0);
        printf("ce(K_{%d,%d}) = %d   (n=%d, m=%d)\n", s, t, val, N, m);
        return 0;
    }
    if (!strcmp(mode, "thresh")) {
        N = atoi(argv[2]);
        set_edges_all();
        f_cur = (argc >= 4) ? (uint64_t)atoi(argv[3]) : (uint64_t)(N - 1);
        Ctx *X = calloc(1, sizeof(Ctx));
        long long ns = 1ll << (N - 1);
        long long bestg = -1; int bestv = (int)f_cur;
        for (long long st = 0; st < ns; st++) {
            uint64_t gm = 0;
            for (int v = 1; v < N; v++)
                if (st >> (v - 1) & 1)
                    for (int u = 0; u < v; u++) gm |= 1ull << eidx_tab[u][v];
            uint32_t adj[MAXN]; int m;
            build_adj(adj, gm, &m);
            if (m < (int)f_cur) continue;
            int val = exact_ce(X, adj, m, (int)f_cur);
            if (val >= 0 && val > f_cur) {
                f_cur = val; bestg = st; bestv = val;
                fprintf(stderr, "NEW thresh f(%d) >= %d (string 0x%llx, m=%d)\n", N, val, (unsigned long long)st, m);
            }
        }
        printf("mode=thresh n=%d over %lld graphs: f >= %d  (best string 0x%llx)\n",
               N, ns, bestv, (unsigned long long)bestg);
        return 0;
    }

    if (!strcmp(mode, "full")) {
        N = atoi(argv[2]);
        set_edges_all();
        fixmask = 0;
        if (argc >= 5) { g_lo = atoll(argv[3]); g_hi = atoll(argv[4]); f0_idx = 5; }
    } else if (!strcmp(mode, "bip")) {
        int s = atoi(argv[2]), t = atoi(argv[3]);
        N = s + t;
        NE = 0;
        for (int u = 0; u < s; u++)
            for (int v = 0; v < t; v++) {
                eu[NE] = u; ev[NE] = s + v;
                eidx_tab[u][s + v] = eidx_tab[s + v][u] = NE;
                NE++;
            }
        fixmask = 0;
        if (argc >= 6) { g_lo = atoll(argv[4]); g_hi = atoll(argv[5]); f0_idx = 6; }
    } else if (!strcmp(mode, "join")) {
        int j = atoi(argv[2]), k = atoi(argv[3]);
        N = j + k;
        set_edges_all();
        for (int u = 0; u < N; u++)
            for (int v = u + 1; v < N; v++)
                if (!(u >= j && v >= j)) fixed |= 1ull << eidx_tab[u][v];
        fixmask = fixed;
        if (argc >= 6) { g_lo = atoll(argv[4]); g_hi = atoll(argv[5]); f0_idx = 6; }
    } else {
        fprintf(stderr, "unknown mode\n");
        return 1;
    }
    f_cur = (f0_idx >= 1 && argc >= f0_idx + 1) ? (uint64_t)atoi(argv[f0_idx]) : (uint64_t)(N - 1);

    long long total = 1ll << NE;
    if (g_hi <= 0) g_hi = total;
    if (g_lo < 0) g_lo = 0;
    if (g_hi > total) g_hi = total;
    fprintf(stderr, "mode=%s n=%d edges=%d range=[%lld,%lld) f0=%llu\n",
            mode, N, NE, g_lo, g_hi, (unsigned long long)f_cur);
    Ctx *X = calloc(1, sizeof(Ctx));
    if (!X) { fprintf(stderr, "malloc failed\n"); return 3; }
    long long solved = 0, best_graph = 0;
    int best_val = (int)f_cur;
    for (long long gm = g_lo; gm < g_hi; gm++) {
        uint64_t G = (uint64_t)gm | fixmask;
        uint32_t adj[MAXN]; int m;
        build_adj(adj, G, &m);
        int fcur = (int)f_cur;
        if (m < fcur) continue;
        if (m - greedy_save(adj, (uint64_t)gm * 2654435761ull + 1) < fcur) continue;
        solved++;
        int val = exact_ce(X, adj, m, fcur);
        if (val < 0) continue;
        if (val > f_cur) {
            f_cur = val; best_val = val; best_graph = gm;
            fprintf(stderr, "NEW f(%d) >= %d  (mask 0x%llx, m=%d)\n", N, val, (unsigned long long)G, m);
        }
    }
    printf("mode=%s f(%d) 范围[%lld,%lld) = %d   [精算图数: %lld; 本块最优可变掩码 0x%llx]\n",
           mode, N, g_lo, g_hi, (int)f_cur, solved, (unsigned long long)best_graph);
    return 0;
}
