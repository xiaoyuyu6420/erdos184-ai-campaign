/*
 * f_enum.c — 全枚举 n 点简单图求 f(n) = max ce(G)（边不相交圈+单边分解的最少部件数）。
 * ce(G) = m - max_save(G)。剪枝: (1) ce<=m; (2) 多轮贪心 packing 给 ce 上界;
 * (3) 精算 packing DFS + suffix 上界 + 提前截断。
 * 用法: ./f_enum n [nthreads]
 * 编译: cc -O2 -o f_enum f_enum.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <pthread.h>

#define MAXN 8
#define MAXE 28
#define MAXCIRC 9000
#define GREEDY_ROUNDS 8
#define NCHUNK 256

static int N, NE;
static int eu[MAXE], ev[MAXE];
static uint32_t ebit[MAXE];
static int eidx_tab[MAXN][MAXN];
static volatile int f_cur;            /* 全局最优（剪枝提示，允许略旧；正确性由 final 归约保证） */
static pthread_mutex_t f_lock = PTHREAD_MUTEX_INITIALIZER;

typedef struct {
    uint32_t circ_mask[MAXCIRC];
    int      circ_len[MAXCIRC];
    int      n_circ;
    int      suffix[MAXCIRC + 2];
    int      best_save, cutoff_target;
    uint32_t c_m[MAXCIRC];
    int      c_s[MAXCIRC];
} Ctx;

static inline uint64_t rng_next(uint64_t *s) {
    uint64_t x = *s; x ^= x << 13; x ^= x >> 7; x ^= x << 17;
    return *s = x;
}
static inline uint32_t emask_ab(int a, int b) { return ebit[eidx_tab[a < b ? a : b][a < b ? b : a]]; }

/* 在 adj(live) 中找一个圈；返回圈边 mask（0=无圈）。 */
static uint32_t find_cycle(const uint32_t *adj, uint64_t *seed) {
    int color[MAXN] = {0}, par[MAXN], order[MAXN], pos[MAXN];
    int stack[MAXN], path[MAXN];
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
                int len = plen - k;
                if (len < 3) continue;
                uint32_t mask = emask_ab(u, w);
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

static int greedy_save(const uint32_t *adj0, uint64_t seed) {
    uint32_t adj[MAXN];
    memcpy(adj, adj0, sizeof(uint32_t) * N);
    uint64_t s = seed | 1;
    int save = 0;
    for (;;) {
        uint32_t c = find_cycle(adj, &s);
        if (!c) break;
        save += __builtin_popcount(c) - 1;
        for (int e = 0; e < NE; e++)
            if (c >> e & 1) { adj[eu[e]] &= ~(1u << ev[e]); adj[ev[e]] &= ~(1u << eu[e]); }
    }
    return save;
}

static void rec_dfs(Ctx *X, const uint32_t *adj, int s, int *path, int *plen, uint32_t *ue, int cur, uint32_t in_path) {
    if (*plen >= 3 && (adj[cur] >> s & 1)) {
        int e_close = eidx_tab[s < cur ? s : cur][s < cur ? cur : s];
        if (!(*ue >> e_close & 1) && X->n_circ < MAXCIRC) {
            X->circ_mask[X->n_circ] = *ue | (1u << e_close);
            X->circ_len[X->n_circ] = *plen;
            X->n_circ++;
        }
    }
    for (int w = s + 1; w < N; w++) {
        if (in_path >> w & 1) continue;               /* 简单路径：顶点不重复 */
        if (!(adj[cur] >> w & 1)) continue;
        int ei = eidx_tab[cur < w ? cur : w][cur < w ? w : cur];
        if (*ue >> ei & 1) continue;
        path[*plen] = w;
        int sv_len = *plen; uint32_t sv_ue = *ue;
        (*plen)++; *ue |= 1u << ei;
        rec_dfs(X, adj, s, path, plen, ue, w, in_path | (1u << w));
        *plen = sv_len; *ue = sv_ue;
    }
}

static void pack_dfs(Ctx *X, int i, uint32_t rem, int cur_save) {
    if (cur_save >= X->cutoff_target) {
        if (cur_save > X->best_save) X->best_save = cur_save;
        return;
    }
    if (i == X->n_circ || cur_save + X->suffix[i] <= X->best_save) {
        if (cur_save > X->best_save) X->best_save = cur_save;
        return;
    }
    pack_dfs(X, i + 1, rem, cur_save);                       /* 跳过圈 i */
    if ((X->c_m[i] & rem) == X->c_m[i])                      /* 圈 i 全部边可用 */
        pack_dfs(X, i + 1, rem & ~X->c_m[i], cur_save + X->c_s[i]);
}

/* 返回精确 ce；若确认 ce < fcur 返回 -1（剪枝语义）。 */
static int exact_ce(Ctx *X, const uint32_t *adj, int m, int fcur) {
    X->n_circ = 0;
    int path[MAXN]; int plen; uint32_t ue;
    for (int s = 0; s < N; s++) {
        path[0] = s; plen = 1; ue = 0;
        rec_dfs(X, adj, s, path, &plen, &ue, s, 1u << s);
    }
    for (int i = 0; i < X->n_circ; i++) {
        X->c_m[i] = X->circ_mask[i];
        X->c_s[i] = __builtin_popcount(X->circ_mask[i]) - 1;
    }
    for (int i = 0; i < X->n_circ; i++)                       /* save 降序 */
        for (int j = i + 1; j < X->n_circ; j++)
            if (X->c_s[j] > X->c_s[i]) {
                uint32_t tm = X->c_m[i]; X->c_m[i] = X->c_m[j]; X->c_m[j] = tm;
                int ts = X->c_s[i]; X->c_s[i] = X->c_s[j]; X->c_s[j] = ts;
            }
    X->suffix[X->n_circ] = 0;
    for (int i = X->n_circ - 1; i >= 0; i--) X->suffix[i] = X->suffix[i + 1] + X->c_s[i];
    X->best_save = 0;
    X->cutoff_target = m - (fcur - 1);
    pack_dfs(X, 0, ((uint32_t)1 << NE) - 1, 0);
    if (X->best_save >= X->cutoff_target) return -1;
    return m - X->best_save;
}

typedef struct { long long lo, hi; long long solved; long long best_graph; int best_val; } Job;

static void *worker(void *arg) {
    Job *J = (Job*)arg;
    Ctx *X = malloc(sizeof(Ctx));
    if (!X) { fprintf(stderr, "malloc failed\n"); exit(3); }
    long long solved = 0;
    for (long long gm = J->lo; gm < J->hi; gm++) {
        uint32_t adj[MAXN];
        for (int i = 0; i < N; i++) adj[i] = 0;
        int m = 0;
        for (int e = 0; e < NE; e++)
            if ((uint32_t)gm >> e & 1) {
                adj[eu[e]] |= 1u << ev[e];
                adj[ev[e]] |= 1u << eu[e];
                m++;
            }
        int fcur = f_cur;
        if (m < fcur) continue;
        if (m - greedy_save(adj, (uint64_t)gm * 2654435761u + 1) < fcur) continue;
        solved++;
        int val = exact_ce(X, adj, m, fcur);
        if (val < 0) continue;
        pthread_mutex_lock(&f_lock);
        if (val > f_cur) {
            f_cur = val; J->best_val = val; J->best_graph = gm;
            fprintf(stderr, "NEW f(%d) >= %d  (mask 0x%llx, m=%d)\n", N, val, (unsigned long long)gm, m);
        }
        pthread_mutex_unlock(&f_lock);
    }
    J->solved = solved;
    free(X);
    return NULL;
}

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: %s n [lo hi]\n", argv[0]); return 1; }
    N = atoi(argv[1]);
    long long g_lo = 1, g_hi = 0;   /* 默认全区间 */
    if (argc >= 4) { g_lo = atoll(argv[2]); g_hi = atoll(argv[3]); }
    NE = N * (N - 1) / 2;
    int k = 0;
    for (int u = 0; u < N; u++)
        for (int v = u + 1; v < N; v++) {
            eu[k] = u; ev[k] = v; ebit[k] = 1u << k;
            eidx_tab[u][v] = eidx_tab[v][u] = k;
            k++;
        }
    f_cur = N - 1;    /* 树 witness */
    long long total = 1LL << NE;
    if (g_hi <= 0) g_hi = total;
    if (g_lo < 1) g_lo = 1;
    if (g_hi > total) g_hi = total;
    fprintf(stderr, "n=%d edges=%d range=[%lld,%lld)\n", N, NE, g_lo, g_hi);

    Job J = { g_lo, g_hi, 0, 0, 0 };
    worker(&J);
    printf("f(%d) 范围[%lld,%lld) = %d   [精确求解图数: %lld; 本块最优 mask 0x%llx]\n",
           N, g_lo, g_hi, f_cur, J.solved, (unsigned long long)J.best_graph);
    if (J.best_val == f_cur && J.best_graph) {
        int mm = 0; for (int e = 0; e < NE; e++) mm += (J.best_graph >> e & 1);
        printf("witness (m=%d) 边表:\n", mm);
        for (int e = 0; e < NE; e++) if (J.best_graph >> e & 1) printf("  (%d,%d)\n", eu[e], ev[e]);
    }
    return 0;
}

#if 0
    if (bv == f_cur && bg) {
        printf("witness 边表 (m = ");
        int mm = 0; for (int e = 0; e < NE; e++) mm += (bg >> e & 1);
        printf("%d):\n", mm);
        for (int e = 0; e < NE; e++) if (bg >> e & 1) printf("  (%d,%d)\n", eu[e], ev[e]);
    }
    return 0;
#endif
