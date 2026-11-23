# Toy-experiment results (T1–T4)

Each file is produced by the script of the same name in `code/toy/` (run from `code/`: `python toy/tN_*.py`).
All seeds are fixed; rerunning reproduces the files exactly.

## t1_chords.json / .npz — `toy/t1_chords.py`
Chord test (paper Fig. 17, left) on four supports: `simplex` (uniform in a regular simplex), `cube` ([0,1]^d),
`gauss` (standard normal), `sphere` (uniform on S^{d-1}). N = 20,000, d in {2,3,5,10,20,50,100}, 200 random pairs,
k = 15 Euclidean neighbours, 101 steps.
- `by_support_dim["<support>_d<d>"]`: `lin_mid` (mean over pairs of dist-to-nearest-sample / chord at the midpoint of
  the straight segment; 0.5 = perfect triangle) and its sd `lin_mid_sd`; `graph_mid60` (same quantity along the
  k-NN shortest path, averaged over t in [0.2, 0.8]); `graph_mid`; `nn_over_chord` (mean nearest-neighbour distance
  / mean chord); `pathlen_over_chord`; `n_hops`; `frac_connected`; `n_pairs`.
- `N_scan_d20["<simplex|gauss>_N<N>"]`: the same at d = 20 for N in {1e3, 1e4, 1e5};
  `N_scaling`: log-log slope of nn_over_chord vs N (compare with -1/d = -0.05).
- npz: `lin_curve`, `graph_curve` (4 supports x 7 dims x 101 steps; mean normalised curves), `t`, `dims`, `supports`,
  `ex_lin_simplex_d{2,50}`, `ex_graph_simplex_d{2,50}` (5 individual normalised curves each).

## t2_sandwich.json / .npz — `toy/t2_sandwich.py`
FVU of PCA(K-1), AA(K), k-means(K) on N = 256 points in R^50; sets `polytope` (Dirichlet(0.5) mixtures of 10
Gaussian random vertices + noise with PCA(9) FVU ~ 0.05), `gauss` (Gaussian with exactly the same sample mean and
covariance, `gaussian_like(exact=True)`), `sum` (p + q, two 4-vertex Dirichlet(0.5) tiles, noise with PCA(6)
FVU ~ 0.05). K in {2,3,5,10,20,30}, 20 repetitions. The k-means value is the best of 10 k-means++ runs, which is
also AA's first initialisation (so AA <= k-means holds by construction).
- json: per set and K, `[mean, sem]` for `pca_Km1`, `aa`, `kmeans`, and the gap ratio `g` = (AA-PCA)/(km-PCA);
  `g_polytope_minus_gauss` (paired difference per K, and the share of repetitions with g_poly < g_gauss);
  `noise_check_mean` (mean PCA(9) and PCA(6) FVU per set); `sandwich_violations` (counts, should be 0).
- npz: `fvu` (set x method[pca_Km1, aa, kmeans] x K x rep), `g` (set x K x rep), `K`, `sets`, `methods`.

## t3_sum_union.json / .npz — `toy/t3_sum_union.py`
Union U of 4 separated triangles vs Minkowski sum S = T1 + T2 in R^20, N = 4000, Dirichlet(1) weights. AA with
K = 12 (U) / 9 (S) and K = 30.
- json `"<U|S>_K<K>"`: `fvu`; `blocks[g]` = average-linkage clustering of 1 - Cn cut into g groups:
  `share_in_blocks` (share of off-diagonal normalised co-activation inside blocks), `null_share` (value for an
  unstructured matrix with the same block sizes), `sizes`, `labels`; `mean_offdiag_Cn`;
  `archetype_to_nearest_vertex_over_diam`; `n_true_vertices_hit_within_2pct`.
  U only: `archetype_purity_min`, `pairwise_agreement_blocks_vs_triangles`.
  S_K9 only: `matched_max_dist_over_diam` (Hungarian match archetypes <-> 9 vertex sums a_i + b_j);
  `kron_rel_err_AA` = ||C_AA/N - G1 (x) G2|| / ||G1 (x) G2|| after matching; `kron_rel_err_true_product_code`
  (same for the generating product code w_i v_j); `AA_vs_true_product_code_rel_err`; `mean_abs_code_diff`;
  `share_in_blocks_by_T1_index` / `_by_T2_index` (blocks = the tile partitions) with `null_share_3x3`.
  `<U|S>_pca_variance_first6`.
- npz: `<key>_Cn` (normalised co-activation), `<key>_order` (dendrogram leaf order), `<U|S>_pc2` (2-D PCA view),
  `U_labels`, `S_kron`, `S_C_matched`.

## t4_hexagon.json / .npz — `toy/t4_hexagon.py`
(a) the regular hexagon (circumradius 1) vs Z = S_0 + S_60 + S_120 and T + (-T): vertex and support-function
errors on 720 directions. (b) two clouds of 4000 points: sparse linear codes (`X_lin`; t_k = 0 w.p. 0.7, else
U[-1/2,1/2]) and block-convex codes (`X_blk`; Dirichlet(0.3) on T and on -T); json gives their max excess over
the hexagon's support function (<= 0: inside) and covariances. (c) the gap in the non-identifiability proof:
X = T (centroid 0), Q = [-eps e, eps e], s = h_Q; json `c` has eps, e, the checks 0 <= s <= h_X on 3600
directions, explicit u, v with f(u+v) > f(u) + f(v) for f = h_X - s, the grid maximum of the violation and the
share of violating direction pairs.
- npz: `X_lin`, `X_blk` (float32), `H`, `G` (generators), `T`, `VZ`, `VTT` (computed hull vertices), `t_lin`,
  `w_p`, `w_q`.
