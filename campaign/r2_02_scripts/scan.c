/*
 * scan.c — R2-02: d=3 exact constant exhaustive scanner.
 *
 * Exhaustively generates all unlabeled 3-degenerate graphs on n vertices
 * (n up to N from command line), computes for each:
 *   - exact ce (min #pieces of a partition of E into simple cycles + single edges)
 *   - exact tau (min T-join size, T = odd-degree vertices) [restricted]
 *   - 3-core status, "pure core" classification
 *   - good-peel property: exists v (deg<=3) with ce(G) - ce(G-v) <= beta(n)
 * Aggregates: max ce vs phi(n) := floor((4n-6)/3), pure-core slack by residue,
 * witnesses with optimal decompositions.
 *
 * Also compiles as CLI solver:  cc -O2 -DCLI -o cecli scan.c
 *   stdin: "n m" then m lines "u v" (0-based); stdout: "ce=%d tau=%d degen=%d"
 *
 * build:  cc -O2 -o scan scan.c
 * usage:  ./scan N [--brute7] [--peeln K] [--taun K] [--corepeeln K]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

#define MAXN 12
#define MAXM 48
#define MEMOBITS 24
#define CYCCAP 65536
#define NOCAP 1000000000

typedef struct { int n, m; uint16_t adj[MAXN]; } Graph;

/* ---------------- phi / beta ---------------- */
static int phif(int n){
  if(n <= 1) return 0;
  if(n == 2) return 1;
  return (4*n - 6)/3;
}
static int betaf(int n){ return phif(n) - phif(n-1); }

/* ---------------- exact ce solver ---------------- */
static int g_n, g_m;
static uint16_t g_adj[MAXN];
static int g_eu[MAXM], g_ev[MAXM];
static int g_eidx[MAXN][MAXN];
static int g_Lmax;

static uint32_t *mk_key; static uint8_t *mk_val; static uint32_t *mk_tag;
static uint32_t cur_tag;
#define MEMOSZ (1u<<MEMOBITS)

static void solver_alloc(void){
  mk_key = calloc(MEMOSZ, sizeof(uint32_t));
  mk_val = calloc(MEMOSZ, 1);
  mk_tag = calloc(MEMOSZ, sizeof(uint32_t));
  cur_tag = 0;
}
static void solver_new_graph(void){ cur_tag++; }

static inline int memo_get(uint32_t k){
  if(k == 0) return 0;
  uint32_t i = (k * 2654435761u) & (MEMOSZ-1);
  for(int p = 0; p < 64; p++, i = (i+1) & (MEMOSZ-1)){
    if(mk_tag[i] != cur_tag) return -1;
    if(mk_key[i] == k) return mk_val[i];
  }
  return -1;
}
static inline void memo_put(uint32_t k, uint8_t v){
  uint32_t i = (k * 2654435761u) & (MEMOSZ-1);
  for(int p = 0; p < 64; p++, i = (i+1) & (MEMOSZ-1)){
    if(mk_tag[i] != cur_tag){ mk_tag[i] = cur_tag; mk_key[i] = k; mk_val[i] = v; return; }
    if(mk_key[i] == k) return;
  }
}

static uint32_t cycbuf[CYCCAP];
static int cyccnt; static int cycovf;

static int g_base; /* base edge id, included in every recorded cycle */
static int g_cap = NOCAP; /* capped solving: memoized values are min(ce, g_cap) */

static void dfs_cycles(int cur, int target, uint32_t mask, uint32_t visited, uint32_t pathmask){
  for(int x = 0; x < g_n; x++){
    if(!((g_adj[cur] >> x) & 1)) continue;
    int eid = g_eidx[cur][x];
    if(!((mask >> eid) & 1)) continue;
    if(x == target){
      if(cyccnt < CYCCAP) cycbuf[cyccnt++] = pathmask | (1u << eid) | (1u << g_base);
      else cycovf = 1;
      continue;
    }
    if((visited >> x) & 1) continue;
    dfs_cycles(x, target, mask, visited | (1u << x), pathmask | (1u << eid));
    if(cycovf) return;
  }
}
static int cycles_through(int e, uint32_t mask){
  int u = g_eu[e], v = g_ev[e];
  cyccnt = 0; cycovf = 0;
  g_base = e;
  dfs_cycles(v, u, mask & ~(1u << e), 1u << v, 0u);
  return cyccnt;
}

static int pc32(uint32_t x){ return __builtin_popcount(x); }

static int solve_rec(uint32_t mask){
  if(!mask) return 0;
  int r = memo_get(mask);
  if(r >= 0) return r;
  int e = __builtin_ctz(mask);
  int best = 1 + solve_rec(mask & ~(1u << e));
  if(best > g_cap) best = g_cap;
  if(best < g_cap && best > 1){
    int nc = cycles_through(e, mask);
    for(int i = 1; i < nc; i++){           /* sort by length desc */
      uint32_t key = cycbuf[i]; int j = i - 1;
      while(j >= 0 && pc32(cycbuf[j]) < pc32(key)){ cycbuf[j+1] = cycbuf[j]; j--; }
      cycbuf[j+1] = key;
    }
    for(int i = 0; i < nc; i++){
      uint32_t rest = mask & ~cycbuf[i];
      int lb = 1 + (pc32(rest) + g_Lmax - 1) / g_Lmax;
      if(lb >= best) continue;
      int val = 1 + solve_rec(rest);
      if(val > g_cap) val = g_cap;
      if(val < best){ best = val; if(best == 1) break; }
    }
    if(cycovf){ fprintf(stderr, "FATAL: cycle cap overflow\n"); exit(3); }
  }
  memo_put(mask, (uint8_t)best);
  return best;
}

static int longest_cycle(void){
  int n = g_n; int best = 0;
  static int (*dp)[MAXN];
  static int allocated = 0;
  if(!allocated){
    dp = malloc((size_t)(1 << MAXN) * MAXN * sizeof(int));
    allocated = 1;
  }
  if(n < 3) return 0;
  for(int s = 0; s < n; s++){
    int lim = 1 << n;
    for(int S = 0; S < lim; S++)
      for(int v = 0; v < n; v++) dp[S][v] = -1;
    dp[1 << s][s] = 0;
    for(int S = 1; S < lim; S++){
      if(!((S >> s) & 1)) continue;
      for(int v = 0; v < n; v++){
        if(dp[S][v] < 0) continue;
        if(v != s && ((g_adj[v] >> s) & 1)){
          int len = dp[S][v] + 1;
          if(len > best) best = len;
        }
        for(int x = 0; x < n; x++){
          if((S >> x) & 1) continue;
          if(!((g_adj[v] >> x) & 1)) continue;
          if(dp[S][v] + 1 > dp[S | (1 << x)][x]) dp[S | (1 << x)][x] = dp[S][v] + 1;
        }
      }
    }
  }
  return best;
}

static void solver_setup(const Graph *G){
  g_n = G->n; g_m = G->m;
  memcpy(g_adj, G->adj, sizeof(uint16_t) * MAXN);
  memset(g_eidx, -1, sizeof(g_eidx));
  int e = 0;
  for(int u = 0; u < g_n; u++)
    for(int v = u+1; v < g_n; v++)
      if((g_adj[u] >> v) & 1){ g_eu[e] = u; g_ev[e] = v; g_eidx[u][v] = g_eidx[v][u] = e; e++; }
  if(e != g_m){ fprintf(stderr, "FATAL: m mismatch (%d vs %d)\n", e, g_m); exit(3); }
  solver_new_graph();
  if(g_cap < NOCAP){
    g_Lmax = g_n > 3 ? g_n : 3;   /* valid upper bound; skips the 2^n DP in capped mode */
  } else {
    g_Lmax = longest_cycle();
    if(g_Lmax < 3) g_Lmax = 3;
  }
}
static int ce_solve(const Graph *G){
  solver_setup(G);
  if(g_m == 0) return 0;
  return solve_rec((g_m >= 32) ? 0xffffffffu : ((1u << g_m) - 1));
}

/* reconstruct an optimal decomposition of the graph most recently solved */
static int dec_pc[MAXM][MAXN + 2]; static int dec_len[MAXM]; static int dec_cnt;
static void extract_decomp(void){
  dec_cnt = 0;
  uint32_t mask = (g_m >= 32) ? 0xffffffffu : ((1u << g_m) - 1);
  while(mask){
    int val = memo_get(mask);
    int e = __builtin_ctz(mask);
    if(1 + memo_get(mask & ~(1u << e)) == val){
      dec_len[dec_cnt] = 2; dec_pc[dec_cnt][0] = g_eu[e]; dec_pc[dec_cnt][1] = g_ev[e]; dec_cnt++;
      mask &= ~(1u << e);
      continue;
    }
    int nc = cycles_through(e, mask);
    int found = 0;
    for(int i = 0; i < nc; i++){
      uint32_t rest = mask & ~cycbuf[i];
      int r = memo_get(rest);
      if(r >= 0 && 1 + r == val){
        int u = g_eu[e], v = g_ev[e];
        int L = 0; dec_pc[dec_cnt][L++] = u; dec_pc[dec_cnt][L++] = v;
        int prev = u, cur = v;
        uint32_t used = (1u << u) | (1u << v);
        while(cur != u){
          int advanced = 0;
          for(int x = 0; x < g_n; x++){
            if(!((g_adj[cur] >> x) & 1)) continue;
            int eid = g_eidx[cur][x];
            if(!((cycbuf[i] >> eid) & 1)) continue;
            if(x == prev) continue;
            if(x == u){ prev = cur; cur = u; advanced = 1; break; }
            if((used >> x) & 1) continue;
            dec_pc[dec_cnt][L++] = x; used |= 1u << x;
            prev = cur; cur = x; advanced = 1; break;
          }
          if(!advanced) break;
        }
        dec_len[dec_cnt] = L; dec_cnt++;
        mask = rest; found = 1; break;
      }
    }
    if(!found){ fprintf(stderr, "FATAL: decomposition reconstruction failed\n"); exit(3); }
  }
}

/* ---------------- tau (min T-join) ---------------- */
static int tau_solve(const Graph *G){
  int n = G->n;
  int d[MAXN][MAXN];
  for(int i = 0; i < n; i++)
    for(int j = 0; j < n; j++)
      d[i][j] = (i == j) ? 0 : (((G->adj[i] >> j) & 1) ? 1 : 9999);
  for(int k = 0; k < n; k++)
    for(int i = 0; i < n; i++)
      for(int j = 0; j < n; j++)
        if(d[i][k] + d[k][j] < d[i][j]) d[i][j] = d[i][k] + d[k][j];
  int T[MAXN], t = 0;
  for(int v = 0; v < n; v++) if(pc32(G->adj[v]) & 1) T[t++] = v;
  if(t == 0) return 0;
  if(t > 12){ fprintf(stderr, "FATAL: tau t>12\n"); exit(3); }
  static int dp[1 << 12];
  int full = (1 << t) - 1;
  dp[0] = 0;
  for(int S = 1; S <= full; S++){
    int i = __builtin_ctz(S);
    int best = 9999;
    for(int j = 0; j < t; j++){
      if(j == i || !((S >> j) & 1)) continue;
      int v = d[T[i]][T[j]] + dp[S ^ (1 << i) ^ (1 << j)];
      if(v < best) best = v;
    }
    dp[S] = best;
  }
  return dp[full];
}

/* ---------------- basic graph utils ---------------- */
static int connected(const Graph *G){
  if(G->n == 0) return 1;
  int seen[MAXN] = {0}; int st[MAXN], sp = 0;
  st[sp++] = 0; seen[0] = 1; int cnt = 1;
  while(sp){
    int v = st[--sp];
    for(int x = 0; x < G->n; x++)
      if(((G->adj[v] >> x) & 1) && !seen[x]){ seen[x] = 1; cnt++; st[sp++] = x; }
  }
  return cnt == G->n;
}
static int mindeg(const Graph *G){
  int mn = 999;
  for(int v = 0; v < G->n; v++){ int d = pc32(G->adj[v]); if(d < mn) mn = d; }
  return G->n ? mn : 0;
}
static int is3degenerate(const Graph *G){
  uint16_t adj[MAXN]; memcpy(adj, G->adj, sizeof(adj));
  int alive[MAXN]; for(int i = 0; i < G->n; i++) alive[i] = 1;
  for(int step = 0; step < G->n; step++){
    int found = -1;
    for(int v = 0; v < G->n; v++){
      if(!alive[v]) continue;
      if(pc32(adj[v]) <= 3){ found = v; break; }
    }
    if(found < 0) return 0;
    alive[found] = 0;
    for(int u = 0; u < G->n; u++)
      if(alive[u] && ((adj[found] >> u) & 1)){ adj[u] &= ~(1 << found); adj[found] &= ~(1 << u); }
  }
  return 1;
}
static int degeneracy_exact(const Graph *G){
  uint16_t adj[MAXN]; memcpy(adj, G->adj, sizeof(adj));
  int alive[MAXN]; for(int i = 0; i < G->n; i++) alive[i] = 1;
  int k = 0, remaining = G->n;
  while(remaining > 0){
    int found = -1;
    for(int v = 0; v < G->n; v++){
      if(!alive[v]) continue;
      if(pc32(adj[v]) <= k){ found = v; break; }
    }
    if(found < 0){ k++; continue; }
    alive[found] = 0; remaining--;
    for(int u = 0; u < G->n; u++)
      if(alive[u] && ((adj[found] >> u) & 1)){ adj[u] &= ~(1 << found); adj[found] &= ~(1 << u); }
  }
  return k;
}
static void remove_vertex(const Graph *G, int rm, Graph *out){
  out->n = G->n - 1; out->m = G->m - pc32(G->adj[rm]);
  int map[MAXN]; int nx = 0;
  for(int i = 0; i < G->n; i++) map[i] = (i == rm) ? -1 : nx++;
  for(int i = 0; i < out->n; i++) out->adj[i] = 0;
  for(int i = 0; i < G->n; i++){
    if(i == rm) continue;
    for(int j = 0; j < G->n; j++){
      if(j == rm) continue;
      if((G->adj[i] >> j) & 1) out->adj[map[i]] |= 1u << map[j];
    }
  }
}
/* every deg-3 vertex has independent neighborhood? (requires mindeg>=3 to be meaningful) */
static int is_pure_core(const Graph *G){
  if(mindeg(G) < 3) return 0;
  for(int v = 0; v < G->n; v++){
    if(pc32(G->adj[v]) != 3) continue;
    int nb[3], t = 0;
    for(int x = 0; x < G->n; x++) if((G->adj[v] >> x) & 1) nb[t++] = x;
    if(((G->adj[nb[0]] >> nb[1]) & 1) || ((G->adj[nb[0]] >> nb[2]) & 1) || ((G->adj[nb[1]] >> nb[2]) & 1))
      return 0;
  }
  return 1;
}
static int has_k1_vertex(const Graph *G){
  for(int v = 0; v < G->n; v++){
    if(pc32(G->adj[v]) != 3) continue;
    int nb[3], t = 0;
    for(int x = 0; x < G->n; x++) if((G->adj[v] >> x) & 1) nb[t++] = x;
    if(((G->adj[nb[0]] >> nb[1]) & 1) || ((G->adj[nb[0]] >> nb[2]) & 1) || ((G->adj[nb[1]] >> nb[2]) & 1))
      return 1;
  }
  return 0;
}

/* ---------------- canonical form (invariant cells + within-cell perms) ---------------- */
static int cn_n; static uint16_t cn_adj[MAXN]; static int cn_col[MAXN];
static int cn_ncell; static int cn_cellid[MAXN];
static int cn_cellverts[MAXN][MAXN]; static int cn_cellsize[MAXN];
static int cn_poscell[MAXN];
static uint16_t cn_best[MAXN]; static int cn_has;
static int cn_perm[MAXN]; static int cn_used[MAXN];
static uint16_t rows[MAXN];

static uint64_t fnv1a(const void *data, size_t len, uint64_t seed){
  const uint8_t *p = data;
  uint64_t h = seed;
  for(size_t i = 0; i < len; i++){ h ^= p[i]; h *= 1099511628211ULL; }
  return h;
}

static void invariant_colors(const Graph *G, int *colf, uint64_t *sighash){
  int n = G->n;
  static uint64_t sig[MAXN], sig2[MAXN];
  for(int v = 0; v < n; v++) sig[v] = (uint64_t)pc32(G->adj[v]);
  for(int round = 0; round < 4; round++){
    for(int v = 0; v < n; v++){
      uint64_t nb[MAXN]; int t = 0;
      for(int x = 0; x < n; x++) if((G->adj[v] >> x) & 1) nb[t++] = sig[x];
      for(int i = 1; i < t; i++){ uint64_t key = nb[i]; int j = i-1; while(j >= 0 && nb[j] > key){ nb[j+1] = nb[j]; j--; } nb[j+1] = key; }
      uint64_t h = 1469598103934665603ULL;
      h = fnv1a(&sig[v], sizeof(uint64_t), h);
      h = fnv1a(nb, t * sizeof(uint64_t), h);
      sig2[v] = h;
    }
    memcpy(sig, sig2, sizeof(uint64_t) * n);
  }
  memcpy(sighash, sig, sizeof(uint64_t) * n);
  /* partition ids for reference (not used for ordering) */
  {
    static uint64_t ids[MAXN]; int nid = 0;
    for(int v = 0; v < n; v++){
      int found = -1;
      for(int i = 0; i < nid; i++) if(ids[i] == sig[v]){ found = i; break; }
      if(found < 0){ ids[nid++] = sig[v]; found = nid - 1; }
      colf[v] = found;
    }
  }
}

static void cn_eval(void){
  int pos[MAXN];
  for(int i = 0; i < cn_n; i++) pos[cn_perm[i]] = i;
  for(int i = 0; i < cn_n; i++){
    int v = cn_perm[i]; uint16_t r = 0;
    for(int x = 0; x < cn_n; x++)
      if((cn_adj[v] >> x) & 1) r |= (uint16_t)(1u << pos[x]);
    rows[i] = r;
  }
  if(!cn_has || memcmp(rows, cn_best, sizeof(uint16_t) * cn_n) < 0){
    memcpy(cn_best, rows, sizeof(uint16_t) * cn_n);
    cn_has = 1;
  }
}
static void cn_rec(int idx){
  if(idx == cn_n){ cn_eval(); return; }
  int cell = cn_poscell[idx];
  for(int t = 0; t < cn_cellsize[cell]; t++){
    int v = cn_cellverts[cell][t];
    if(cn_used[v]) continue;
    cn_perm[idx] = v; cn_used[v] = 1;
    cn_rec(idx + 1);
    cn_used[v] = 0;
  }
}
static void canon(const Graph *G, uint64_t *h1, uint64_t *h2, uint16_t *bestout){
  cn_n = G->n;
  memcpy(cn_adj, G->adj, sizeof(uint16_t) * MAXN);
  static uint64_t vsig[MAXN];
  invariant_colors(G, cn_col, vsig);
  /* build cells; order cells by MIN signature hash in cell (isomorphism-invariant) */
  cn_ncell = 0;
  static uint64_t cellkey[MAXN];
  for(int v = 0; v < cn_n; v++){
    int found = -1;
    for(int i = 0; i < cn_ncell; i++) if(cellkey[i] == vsig[v]){ found = i; break; }
    if(found < 0){ cellkey[cn_ncell] = vsig[v]; found = cn_ncell; cn_ncell++; }
    cn_cellid[v] = found;
  }
  /* order cells by cellkey value */
  static int order[MAXN];
  for(int i = 0; i < cn_ncell; i++) order[i] = i;
  for(int i = 1; i < cn_ncell; i++){
    int key = order[i]; int j = i - 1;
    while(j >= 0 && cellkey[order[j]] > cellkey[key]){ order[j+1] = order[j]; j--; }
    order[j+1] = key;
  }
  for(int i = 0; i < cn_ncell; i++) cn_cellsize[i] = 0;
  int pos = 0;
  for(int i = 0; i < cn_ncell; i++){
    int cell = order[i];
    for(int v = 0; v < cn_n; v++)
      if(cn_cellid[v] == cell){ cn_cellverts[cell][cn_cellsize[cell]++] = v; }
    for(int t = 0; t < cn_cellsize[cell]; t++) cn_poscell[pos++] = cell;
  }
  memset(cn_used, 0, sizeof(cn_used));
  cn_has = 0;
  cn_rec(0);
  *h1 = fnv1a(cn_best, sizeof(uint16_t) * cn_n, 1469598103934665603ULL);
  *h2 = fnv1a(cn_best, sizeof(uint16_t) * cn_n, 1099511628211ULL);
  if(bestout) memcpy(bestout, cn_best, sizeof(uint16_t) * cn_n);
}

/* ---------------- level generation with dedup ---------------- */
typedef struct {
  Graph *graphs;
  uint64_t *k1; uint64_t *k2;
  int count, cap;
} Level;

static void level_init(Level *L, int cap){
  L->cap = cap; L->count = 0;
  L->graphs = malloc(sizeof(Graph) * cap);
  L->k1 = malloc(sizeof(uint64_t) * cap);
  L->k2 = malloc(sizeof(uint64_t) * cap);
  if(!L->graphs || !L->k1 || !L->k2){ fprintf(stderr, "OOM level_init\n"); exit(1); }
}
static void level_free(Level *L){ free(L->graphs); free(L->k1); free(L->k2); L->count = L->cap = 0; }

typedef struct { uint64_t h1, h2; int gidx; } Dent;
static Dent *dtab; static int dtab_sz, dtab_mask;

static void dtab_init(int sz){
  dtab_sz = 1; while(dtab_sz < sz) dtab_sz <<= 1;
  dtab_mask = dtab_sz - 1;
  dtab = malloc(sizeof(Dent) * dtab_sz);
  for(int i = 0; i < dtab_sz; i++){ dtab[i].gidx = -1; dtab[i].h1 = 0; dtab[i].h2 = 0; }
}
static void dtab_clear(void){
  for(int i = 0; i < dtab_sz; i++) dtab[i].gidx = -1;
}
/* returns 1 if inserted, 0 if duplicate; gidx = index in L */
static int dtab_insert(Level *L, int gidx, uint64_t h1, uint64_t h2){
  uint64_t i = (h1 * 0x9E3779B97F4A7C15ULL) & (uint64_t)dtab_mask;
  for(int p = 0; p < 128; p++, i = (i + 1) & (uint64_t)dtab_mask){
    if(dtab[i].gidx < 0){
      dtab[i].gidx = gidx; dtab[i].h1 = h1; dtab[i].h2 = h2;
      return 1;
    }
    if(dtab[i].h1 == h1 && dtab[i].h2 == h2){
      /* 128-bit canonical hash match: treat as duplicate */
      return 0;
    }
  }
  fprintf(stderr, "FATAL: dtab full\n"); exit(3);
}

static void add_child(Level *L, const Graph *parent, uint16_t Smask){
  Graph ch;
  ch.n = parent->n + 1;
  ch.m = parent->m + pc32(Smask);
  for(int i = 0; i < parent->n; i++) ch.adj[i] = parent->adj[i];
  for(int i = ch.n; i < MAXN; i++) ch.adj[i] = 0;
  ch.adj[parent->n] = Smask;
  for(int x = 0; x < parent->n; x++)
    if((Smask >> x) & 1) ch.adj[x] |= (uint16_t)(1u << parent->n);
  if(L->count >= L->cap){ fprintf(stderr, "FATAL: level cap\n"); exit(3); }
  uint64_t h1, h2;
  canon(&ch, &h1, &h2, NULL);
  int idx = L->count;
  L->graphs[idx] = ch; L->k1[idx] = h1; L->k2[idx] = h2;
  if(dtab_insert(L, idx, h1, h2)) L->count++;
}

/* ---------------- stats ---------------- */
static long long stat_attempts[16];
static long long stat_count[16];
static int stat_maxce[16];
static int stat_maxce_count[16];
static Graph stat_maxce_wit[16][4];
static int stat_maxce_decomp[16][MAXM][MAXN+2];
static int stat_maxce_declen[16][MAXM];
static int stat_maxce_deccnt[16];
static long long stat_violations[16];
static long long stat_cores[16], stat_pure[16];
static int stat_pureminslack[16][3]; static Graph stat_purewit[16][3]; static int stat_purewitok[16][3];
static long long stat_pureBviol[16];
static long long stat_mixed[16];
static long long stat_gp_fail[16]; static Graph stat_gp_wit[16]; static int stat_gp_witok[16];
static long long stat_gp_checked[16];
static long long stat_tight[16], stat_tight_core[16], stat_gpfail_tight[16];
static long long stat_certified[16], stat_certified_pure[16];
static int stat_tau_excess[16]; static Graph stat_tau_wit[16]; static int stat_tauwitok[16];
static long long stat_tau_count[16];

static void record_witness(int n, const Graph *G, int ce){
  if(stat_maxce_count[n] < 4){
    stat_maxce_wit[n][stat_maxce_count[n]] = *G;
    if(stat_maxce_count[n] == 0 && g_cap == NOCAP){
      solver_setup(G);
      solve_rec((g_m >= 32) ? 0xffffffffu : ((1u << g_m) - 1));
      extract_decomp();
      stat_maxce_deccnt[n] = dec_cnt;
      for(int i = 0; i < dec_cnt; i++){
        stat_maxce_declen[n][i] = dec_len[i];
        for(int j = 0; j < dec_len[i]; j++) stat_maxce_decomp[n][i][j] = dec_pc[i][j];
      }
    }
  }
  stat_maxce_count[n]++;
}

static void process_graph(const Graph *G, int n, int peeln, int corepeeln, int taun){
  /* capped mode only: cheap certification. If provably ce <= phif(n)-1, the graph
     cannot be a violation nor tight (phi); skip the exact solve. Sound because
     ce <= m and ce <= (m+2tau)/3 (R1). */
  if(g_cap < NOCAP){
    int phi = phif(n);
    if(G->m <= phi - 1){ stat_certified[n]++; if(is_pure_core(G)) stat_certified_pure[n]++; stat_count[n]++; return; }
    int tau = tau_solve(G);
    if(G->m + 2*tau <= 3*(phi-1)){ stat_certified[n]++; if(is_pure_core(G)) stat_certified_pure[n]++; stat_count[n]++; return; }
  }
  int ce = ce_solve(G);
  stat_count[n]++;
  if(ce > stat_maxce[n]){ stat_maxce[n] = ce; stat_maxce_count[n] = 0; }
  if(ce == stat_maxce[n]) record_witness(n, G, ce);
  if(ce > phif(n)) stat_violations[n]++;
  if(ce == phif(n)){
    stat_tight[n]++;
    if(mindeg(G) >= 3) stat_tight_core[n]++;
  }

  int md = mindeg(G);
  int iscore = (md >= 3);
  if(iscore){
    stat_cores[n]++;
    if(has_k1_vertex(G)) stat_mixed[n]++;
    if(is_pure_core(G)){
      stat_pure[n]++;
      int r = n % 3;
      int slack = phif(n) - ce;
      if(!stat_purewitok[n][r] || slack < stat_pureminslack[n][r]){
        stat_pureminslack[n][r] = slack;
        stat_purewit[n][r] = *G;
        stat_purewitok[n][r] = 1;
      }
      if(r != 0 && ce > phif(n) - 1) stat_pureBviol[n]++;
    }
    /* good peel check on cores at higher n */
    if(n <= corepeeln){
      stat_gp_checked[n]++;
      int ok = 0;
      for(int v = 0; v < G->n && !ok; v++){
        int d = pc32(G->adj[v]);
        if(d > 3) continue;
        Graph H; remove_vertex(G, v, &H);
        int ceh = ce_solve(&H);
        if(ce - ceh <= betaf(n)) ok = 1;
      }
      if(!ok && stat_gp_fail[n] == 0){ stat_gp_wit[n] = *G; stat_gp_witok[n] = 1; }
      if(!ok){ stat_gp_fail[n]++; if(ce >= phif(n)) stat_gpfail_tight[n]++; }
    }
  }
  /* good-peel for ALL connected graphs at small n */
  if(n <= peeln && connected(G)){
    stat_gp_checked[n]++;
    int ok = 0;
    for(int v = 0; v < G->n && !ok; v++){
      int d = pc32(G->adj[v]);
      if(d > 3) continue;
      Graph H; remove_vertex(G, v, &H);
      int ceh = ce_solve(&H);
      if(ce - ceh <= betaf(n)) ok = 1;
    }
    if(!ok && stat_gp_fail[n] == 0){ stat_gp_wit[n] = *G; stat_gp_witok[n] = 1; }
    if(!ok){ stat_gp_fail[n]++; if(ce >= phif(n)) stat_gpfail_tight[n]++; }
  }
  /* tau for R1-route analysis */
  if(n <= taun || G->m >= 3*n - 12){
    int tau = tau_solve(G);
    stat_tau_count[n]++;
    int ex = G->m + 2*tau - (4*n - 6);
    if(!stat_tauwitok[n] || ex > stat_tau_excess[n]){
      stat_tau_excess[n] = ex;
      stat_tau_wit[n] = *G;
      stat_tauwitok[n] = 1;
    }
  }
}

/* ---------------- self tests ---------------- */
static Graph mkpath(int n){
  Graph G; G.n = n; G.m = n - 1;
  for(int i = 0; i < n; i++) G.adj[i] = 0;
  for(int i = 0; i + 1 < n; i++){ G.adj[i] |= 1u << (i+1); G.adj[i+1] |= 1u << i; }
  return G;
}
static void selftest(void){
  /* phi */
  int exp[13] = {0,0,1,2,3,4,6,7,8,10,11,12,14};
  for(int n = 0; n <= 12; n++) if(phif(n) != exp[n]){ fprintf(stderr, "phi selftest FAIL n=%d\n", n); exit(3); }
  /* ce values */
  { Graph G = mkpath(3); int c = ce_solve(&G); if(c != 2){ fprintf(stderr, "P3 ce=%d != 2\n", c); exit(3);} }
  { Graph G = mkpath(4); int c = ce_solve(&G); if(c != 3){ fprintf(stderr, "P4 ce=%d != 3\n", c); exit(3);} }
  { /* K4 */ Graph G; G.n = 4; G.m = 6; for(int i=0;i<4;i++) G.adj[i] = 0x0F & ~(1<<i);
    int c = ce_solve(&G); if(c != 3){ fprintf(stderr, "K4 ce=%d != 3\n", c); exit(3);} 
    int t = tau_solve(&G); if(t != 2){ fprintf(stderr, "K4 tau=%d != 2\n", t); exit(3);} }
  { /* C6 */ Graph G; G.n = 6; G.m = 6; for(int i=0;i<6;i++) G.adj[i]=0;
    for(int i=0;i<6;i++){ int j=(i+1)%6; G.adj[i]|=1<<j; G.adj[j]|=1<<i; }
    int c = ce_solve(&G); if(c != 1){ fprintf(stderr, "C6 ce=%d != 1\n", c); exit(3);} }
  { /* K3,3 */ Graph G; G.n = 6; G.m = 9; for(int i=0;i<6;i++) G.adj[i]=0;
    for(int i=0;i<3;i++) for(int j=3;j<6;j++){ G.adj[i]|=1<<j; G.adj[j]|=1<<i; }
    int c = ce_solve(&G); if(c != 4){ fprintf(stderr, "K33 ce=%d != 4\n", c); exit(3);}
    int t = tau_solve(&G); if(t != 3){ fprintf(stderr, "K33 tau=%d != 3\n", t); exit(3);} }
  { /* K3,4 */ Graph G; G.n = 7; G.m = 12; for(int i=0;i<7;i++) G.adj[i]=0;
    for(int i=0;i<3;i++) for(int j=3;j<7;j++){ G.adj[i]|=1<<j; G.adj[j]|=1<<i; }
    int c = ce_solve(&G); if(c != 6){ fprintf(stderr, "K34 ce=%d != 6\n", c); exit(3);} }
  { /* K5-e */ Graph G; G.n = 5; G.m = 9; for(int i=0;i<5;i++) G.adj[i]=0;
    for(int i=0;i<5;i++) for(int j=i+1;j<5;j++){ if(i==0&&j==1) continue; G.adj[i]|=1<<j; G.adj[j]|=1<<i; }
    int c = ce_solve(&G); if(c != 4){ fprintf(stderr, "K5-e ce=%d != 4\n", c); exit(3);} }
  { /* star K1,4: ce = 4 = m */ Graph G; G.n = 5; G.m = 4; for(int i=0;i<5;i++) G.adj[i]=0;
    for(int j=1;j<5;j++){ G.adj[0]|=1<<j; G.adj[j]|=1<<0; }
    int c = ce_solve(&G); if(c != 4){ fprintf(stderr, "K14 ce=%d != 4\n", c); exit(3);} }
  { /* tau star K1,3 = 3 */ Graph G; G.n = 4; G.m = 3; for(int i=0;i<4;i++) G.adj[i]=0;
    for(int j=1;j<4;j++){ G.adj[0]|=1<<j; G.adj[j]|=1<<0; }
    int t = tau_solve(&G); if(t != 3){ fprintf(stderr, "K13 tau=%d != 3\n", t); exit(3);} }
  fprintf(stderr, "selftests OK\n");
}

/* ---------------- brute validation (labeled enumeration) ---------------- */
static void brute_validate(int n){
  int E = n*(n-1)/2;
  if(E > 21){ fprintf(stderr, "brute: too many edges\n"); return; }
  int eu[21], ev[21], e = 0;
  for(int u = 0; u < n; u++) for(int v = u+1; v < n; v++){ eu[e] = u; ev[e] = v; e++; }
  Level L; level_init(&L, 2000000);
  dtab_init(1 << 22); dtab_clear();
  long long total = 0, kept = 0;
  for(long long M = 0; M < (1LL << E); M++){
    total++;
    Graph G; G.n = n; G.m = pc32((uint32_t)M);
    for(int i = 0; i < n; i++) G.adj[i] = 0;
    for(int i = 0; i < E; i++) if((M >> i) & 1){ G.adj[eu[i]] |= 1u << ev[i]; G.adj[ev[i]] |= 1u << eu[i]; }
    if(!is3degenerate(&G)) continue;
    uint64_t h1, h2;
    canon(&G, &h1, &h2, NULL);
    int idx = L.count;
    L.graphs[idx] = G; L.k1[idx] = h1; L.k2[idx] = h2;
    if(dtab_insert(&L, idx, h1, h2)) L.count++;
    kept++;
  }
  printf("BRUTE n=%d: labeled=%lld 3deg=%lld unlabeled=%lld\n", n, total, kept, (long long)L.count);
  level_free(&L); free(dtab);
}

/* ---------------- main ---------------- */
#ifndef CLI
int main(int argc, char **argv){
  if(argc < 2){ fprintf(stderr, "usage: %s N [--brute7] [--peeln K] [--taun K] [--corepeeln K] [--maxlvl cap] [--cap C --capn N] [--wit name]\n", argv[0]); return 1; }
  int N = atoi(argv[1]);
  int peeln = 8, taun = 8, corepeeln = 10;
  int brute7 = 0;
  int cap = NOCAP, capn = 9;
  const char *witname = "scan_wit.txt";
  long long lvlcap = 12000000;
  for(int i = 2; i < argc; i++){
    if(!strcmp(argv[i], "--brute7")) brute7 = 1;
    else if(!strcmp(argv[i], "--peeln")) peeln = atoi(argv[++i]);
    else if(!strcmp(argv[i], "--taun")) taun = atoi(argv[++i]);
    else if(!strcmp(argv[i], "--corepeeln")) corepeeln = atoi(argv[++i]);
    else if(!strcmp(argv[i], "--maxlvl")) lvlcap = atoll(argv[++i]);
    else if(!strcmp(argv[i], "--cap")) cap = atoi(argv[++i]);
    else if(!strcmp(argv[i], "--capn")) capn = atoi(argv[++i]);
    else if(!strcmp(argv[i], "--wit")) witname = argv[++i];
  }
  if(N > MAXN - 2){ fprintf(stderr, "N too large\n"); return 1; }
  solver_alloc();
  selftest();

  if(brute7){ for(int n = 4; n <= (N >= 7 ? 7 : N); n++) brute_validate(n); }

  clock_t t0 = clock();
  FILE *witf = fopen(witname, "w");

  Level prev, cur;
  /* level 0: single empty graph */
  level_init(&prev, 4);
  Graph G0; G0.n = 0; G0.m = 0; memset(G0.adj, 0, sizeof(G0.adj));
  prev.graphs[0] = G0; prev.count = 1;

  for(int n = 1; n <= N; n++){
    if(n > capn) g_cap = cap; else g_cap = NOCAP;
    dtab_init(1 << 25); dtab_clear();
    level_init(&cur, (int)lvlcap);
    stat_attempts[n] = 0;
    for(int i = 0; i < prev.count; i++){
      const Graph *P = &prev.graphs[i];
      int pn = P->n;
      /* subsets of size <= 3 */
      add_child(&cur, P, 0); stat_attempts[n]++;
      for(int a = 0; a < pn; a++){ add_child(&cur, P, (uint16_t)(1u << a)); stat_attempts[n]++; }
      for(int a = 0; a < pn; a++) for(int b = a+1; b < pn; b++){
        add_child(&cur, P, (uint16_t)((1u << a) | (1u << b))); stat_attempts[n]++;
      }
      for(int a = 0; a < pn; a++) for(int b = a+1; b < pn; b++) for(int c = b+1; c < pn; c++){
        add_child(&cur, P, (uint16_t)((1u << a) | (1u << b) | (1u << c))); stat_attempts[n]++;
      }
    }
    double el = (double)(clock() - t0) / CLOCKS_PER_SEC;
    fprintf(stderr, "level n=%d: attempts=%lld graphs=%d (%.1fs)\n", n, stat_attempts[n], cur.count, el);
    /* process */
    int epeeln = (g_cap == NOCAP) ? peeln : 0;
    int etaun  = (g_cap == NOCAP) ? taun : 0;
    int ecorep = (g_cap == NOCAP) ? corepeeln : 0;
    for(int i = 0; i < cur.count; i++){
      process_graph(&cur.graphs[i], n, epeeln, ecorep, etaun);
      if(g_cap < NOCAP && (i + 1) % 500000 == 0)
        fprintf(stderr, "  n=%d progress %d/%d (%.1fs)\n", n, i + 1, cur.count,
                (double)(clock() - t0) / CLOCKS_PER_SEC);
    }
    printf("== n=%d graphs=%d maxce=%d phi=%d C2=%d violations=%lld%s\n",
           n, cur.count, stat_maxce[n], phif(n), (phif(n) + ((n % 3) ? 1 : 0)), stat_violations[n],
           (g_cap == NOCAP) ? "" : " [CAPPED]");
    printf("   cores=%lld mixed=%lld pure=%lld pureminslack(r0/r1/r2)=%d/%d/%d pureBviol=%lld\n",
           stat_cores[n], stat_mixed[n], stat_pure[n],
           stat_purewitok[n][0] ? stat_pureminslack[n][0] : -1,
           stat_purewitok[n][1] ? stat_pureminslack[n][1] : -1,
           stat_purewitok[n][2] ? stat_pureminslack[n][2] : -1,
           stat_pureBviol[n]);
    printf("   gpchecked=%lld gpfail=%lld gpfail_tight=%lld tight=%lld tight_core=%lld tauexcess=%d taucount=%lld\n",
           stat_gp_checked[n], stat_gp_fail[n], stat_gpfail_tight[n],
           stat_tight[n], stat_tight_core[n], stat_tau_excess[n], stat_tau_count[n]);
    if(g_cap < NOCAP)
      printf("   certified(ce<=%d by m/R1)=%lld certified_pure=%lld solved=%lld\n",
             phif(n) - 1, stat_certified[n], stat_certified_pure[n],
             stat_count[n] - stat_certified[n]);
    fflush(stdout);
    /* witnesses to file */
    fprintf(witf, "=== n=%d maxce=%d (phi=%d) witnesses=%d\n", n, stat_maxce[n], phif(n), stat_maxce_count[n]);
    for(int w = 0; w < stat_maxce_count[n] && w < 4; w++){
      const Graph *G = &stat_maxce_wit[n][w];
      fprintf(witf, "W n=%d m=%d edges:", n, G->m);
      for(int u = 0; u < G->n; u++) for(int v = u+1; v < G->n; v++)
        if((G->adj[u] >> v) & 1) fprintf(witf, " (%d,%d)", u, v);
      fprintf(witf, "\n");
      if(w == 0 && stat_maxce_deccnt[n] > 0){
        fprintf(witf, "DECOMP %d pieces:", stat_maxce_deccnt[n]);
        for(int p = 0; p < stat_maxce_deccnt[n]; p++){
          fprintf(witf, " [");
          for(int j = 0; j < stat_maxce_declen[n][p]; j++)
            fprintf(witf, "%s%d", j ? "," : "", stat_maxce_decomp[n][p][j]);
          fprintf(witf, "]");
        }
        fprintf(witf, "\n");
      }
    }
    for(int r = 0; r < 3; r++){
      if(stat_purewitok[n][r]){
        const Graph *G = &stat_purewit[n][r];
        fprintf(witf, "PURE n=%d r=%d slack=%d m=%d edges:", n, r, stat_pureminslack[n][r], G->m);
        for(int u = 0; u < G->n; u++) for(int v = u+1; v < G->n; v++)
          if((G->adj[u] >> v) & 1) fprintf(witf, " (%d,%d)", u, v);
        fprintf(witf, "\n");
      }
    }
    if(stat_tauwitok[n] && stat_tau_excess[n] > 0){
      const Graph *G = &stat_tau_wit[n];
      fprintf(witf, "TAUEXCESS n=%d excess=%d m=%d edges:", n, stat_tau_excess[n], G->m);
      for(int u = 0; u < G->n; u++) for(int v = u+1; v < G->n; v++)
        if((G->adj[u] >> v) & 1) fprintf(witf, " (%d,%d)", u, v);
      fprintf(witf, "\n");
    }
    if(stat_gp_witok[n] && stat_gp_fail[n] > 0){
      const Graph *G = &stat_gp_wit[n];
      fprintf(witf, "GPFAIL n=%d edges:", n);
      for(int u = 0; u < G->n; u++) for(int v = u+1; v < G->n; v++)
        if((G->adj[u] >> v) & 1) fprintf(witf, " (%d,%d)", u, v);
      fprintf(witf, "\n");
    }
    fflush(witf);
    level_free(&prev);
    prev = cur;
    free(dtab);
  }
  fclose(witf);
  fprintf(stderr, "total time %.1fs\n", (double)(clock() - t0) / CLOCKS_PER_SEC);
  return 0;
}
#endif /* !CLI */

/* ---------------- CLI solver mode ---------------- */
#ifdef CLI
int main(void){
  solver_alloc();
  int n, m;
  if(scanf("%d %d", &n, &m) != 2) return 1;
  Graph G; G.n = n; G.m = m;
  for(int i = 0; i < n; i++) G.adj[i] = 0;
  for(int i = 0; i < m; i++){
    int u, v; if(scanf("%d %d", &u, &v) != 2) return 1;
    G.adj[u] |= 1u << v; G.adj[v] |= 1u << u;
  }
  int ce = ce_solve(&G);
  int tau = tau_solve(&G);
  int dg = degeneracy_exact(&G);
  printf("ce=%d tau=%d degen=%d\n", ce, tau, dg);
  return 0;
}
#else
int main(int argc, char **argv);
#endif
