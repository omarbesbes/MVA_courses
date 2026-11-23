# DINOv2 results (`r*` files)

Model: DINOv2 ViT-B/14 with 4 registers (`dinov2_vitb14_reg`, LVD-142M weights) and a random-weights twin
(same architecture, `torch.manual_seed(0)`, `pretrained=False`). Data: Imagenette 320 px validation split;
1000 "statistics" images (first 100 file names of each class, sorted; image index i -> class i // 100) and 200
held-out images (next 20 per class). Preprocessing: shorter side 256 (bicubic), centre crop 224, ImageNet
mean/std. Every JSON file has a `versions` block (package versions, model identifier, weights SHA-256),
`written` and `runtime_s`. Scripts: `code/dino/rN_*.py`; shared code `code/rh/dino.py`, `code/dino/common.py`.
Large features live outside the repository (`SP/lab_cache/feats`, written by `code/dino/r0_extract.py`).

Summary objects (`summ`) are `{mean, std, min, q25, median, q75, max, n}`.

## r0_image_lists.json
The image lists (paths and classes) of the statistics and held-out sets.

## r1_layernorm_ellipsoid.json — final LayerNorm puts tokens on an ellipsoid
- `constraints`: `max_abs_mean_u`, `max_abs_var_u_minus_1` with u = (y - beta)/gamma over all 256,000 tokens;
  `norm_u_over_sqrt_d` (summ) and its max-min spread; `layernorm_recomputed_from_prenorm_max_abs_err`.
- `gamma`: |gamma| min / median / max / 1% / 99% quantiles, number negative, axis ratio, beta norm, eps.
- `pairs.within_image`, `pairs.across_images` (2000 pairs each): `angle_deg` between u's, `cosine_u`,
  `cosine_y`, `chord` = ||y - y'||, `depth_radial` (midpoint to its radial projection on the ellipsoid, the
  brief's measure), `depth_exact` (true Euclidean distance to the ellipsoid, secular equation),
  `*_over_half_chord` ratios, `sphere_formula_tan_quarter_angle` (the ratio on a sphere), `u_space_depth_over_half_chord`,
  `selfcheck_token_distance_to_ellipsoid_max` (must be ~0).
- `prenorm`: summ of pre-norm token norms and `norm_cv`; same for post-norm (`postnorm_norm_cv`).

## r2_interpolation_nulls.json — the paper's interpolation test with nulls
- `design`: N = 50,000 tokens, 300 pairs (same index pairs for all datasets), k = 15 cosine neighbours, 101 steps.
- `datasets.{a..f}`: a trained post-norm, b trained pre-norm, c Gaussian with moments of (a), d Gaussian with
  moments of (b) through the final LayerNorm, e random twin post-norm, f Gaussian mixture (k-means 200 on (a)).
  Each: `summary` {`mean_chord`, `mean_nn_dist`, `peak_mean_lin_normalised` (0.5 = nearest sample of the midpoint is
  an endpoint), `frac_pairs_midpoint_nearest_is_endpoint`, `frac_points_on_triangle`, `mean_graph_normalised_middle60`,
  `mean_path_len_over_chord`, `mean_hops`, ...}; `curves` {`lin_raw_mean/std`, `lin_norm_mean/std`,
  `graph_raw_mean/std`, `graph_norm_mean/std`} (101 values, t = linspace(0,1,101); "norm" = divided by each
  pair's chord); `n_edges`, `mean_knn_edge_length`, `n_disconnected_pairs`. (f) also has `gmm`.
- `variants_k.{5,15,50}`: dataset (a) with other k (straight curves identical). `variants_N.{5000,20000,50000}`:
  nested subsets of (a), new pairs.

## r3_aa_sandwich.json — per-image AA between PCA and k-means
- `results.{post, pre, random, n1, n2}`: post = trained post-norm (200 images, 20 per class), pre = trained
  pre-norm, random = random twin post-norm, n1 = per-image Gaussian null, n2 = Dirichlet(0.5) mixtures of 10
  tokens + noise matched on PCA(9) FVU (100 images each, 10 per class; nulls built from the post-norm tokens).
  Fields per K in `K` = [2,3,5,10,20,30,50]: `pca_Km1_mean/sem`, `aa_mean/sem`, `kmeans_mean/sem` (FVU),
  `gap_ratio_mean/sem/median` with g = (AA - PCA)/(kmeans - PCA) per image, `sandwich_violations`.
  n2 also `noise_sigma`, `pca9_fvu_match_max_abs_err`.

## r4_attention_anatomy.json — residual decomposition and attention statistics (100 images)
`trained` and `random_twin`, each with: `i_residual_identity` (max abs error of x12 = x0 + sum attn + sum mlp);
`ii_decomposition.{raw, centred_within_image}.{mean_of_token_ratios, pooled}`: `f_emb`, `f_attn`, `f_mlp`, `sum`,
per-layer lists, embedding split into patch / position parts, plus `mean_term_norms`;
`iii_last_block_recomputation` (per-head recomputation vs module output); `iv_attention`: 12x12 (block x head)
`entropy_nats`, `mean_exp_entropy`, `top1_mass`, `special_tokens_mass`, `self_mass` and per-block means;
`v_last_block_keys`: numerical rank of the 261x64 key matrix per head (and with a ones column);
`vi_heads_per_token` (participation ratio of per-head update norms, share of heads above 10% / 50% of the
largest) and `vi_mean_head_share`; `vii_value_variance_explained_by_position` (12x12).

## r5_coactivation.json / r5_coactivation.npz — global AA co-activation vs image identity
- JSON `results.{200, 50}` (K): `aa_fvu`, `kmeans_fvu`, `top_image_share` / `top_class_share` (mean, median,
  q90, uniform, frac above 0.5), `n_distinct_dominant_images/classes`,
  `offdiag_coactivation_same_dominant_image/class` {`share`, `perm_baseline_mean`, `perm_baseline_q95`},
  `diag_share_of_total_C_mass`, `hierarchical_blocks.{10,20}` {`ami_dominant_class`, `ami_dominant_image`,
  `offdiag_mass_inside_blocks`, `block_sizes`, `labels`}, `codes` (non-zeros per token), per-archetype shares and
  dominant labels.
- NPZ keys `K{K}_C_clustered`, `K{K}_order_clustered`, `K{K}_C_by_class_image`, `K{K}_order_by_class_image`
  (float16 C = A^T A in two orders), `K{K}_dominant_image`, `K{K}_dominant_class`, `K{K}_blocks10/20`.

## r6_position_additive.json — is the final-layer position code additive?
`results.{trained,random}_{prenorm,postnorm}`: `r2_additive` (P_ij ~ r_i + c_j), `r2_additive_null_generic_table`
(30/255), `share_rows/columns`, `rows`/`columns` {`var_share_pc1`, `var_share_pc1_2`, `spearman_coord1_vs_index_abs`,
`r2_linear_in_index`, coordinates}, `cos_leading_row_vs_column_direction_abs`, `position_share_of_token_variance`,
`split_half` (cross-validated R2 and noise ceiling), `r2_rank1_factors`, `r2_linear_in_row_and_column_index`,
spectrum of P.

## r7_position_layers.json — position across depth
`per_depth` (depth 0 = block-1 input, 1..12 = block outputs, "12+LN"): stable rank of centred / uncentred P_l,
top-1/top-2 shares, position share of token variance, `probe` (ridge position decoder, 256 classes, 300 train /
100 held-out images, three ridge strengths: accuracy, within-1-patch accuracy, row / column accuracy),
`probe_accuracy` (lambda_rel = 1e-3); `coords_2d` (256x2 PCA coordinates for selected depths);
`paper_values_for_comparison`.

R8 (PCA maps) was not run.
