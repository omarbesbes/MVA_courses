"""R6 — is the position code of the final layer additive in row and column?

P = mean patch token per position over the 1000 statistics images (256 x 768), centred over positions, read as
a 16 x 16 table of vectors P[i, j] (i = row = vertical index, j = column = horizontal index).

  two-way additive fit   P[i, j] ~ r_i + c_j,  r_i = mean_j P[i, j], c_j = mean_i P[i, j]   (least squares)
  R2_add = 1 - ||P - r - c||^2 / ||P||^2.  A table of generic vectors gives 30/255 = 0.118 (degrees of freedom).

For the 16 row effects and the 16 column effects: share of their variance on their first principal component
and on the first two, cosine between the leading row and column directions, Spearman correlation between the
1-D coordinate (projection on the leading direction) and the grid index.

Noise control: P is an average over 1000 images, so part of the non-additive residual is sampling noise.
Split-half (even / odd images): fit on one half, evaluate on the other; the ceiling is the R2 of one half's P
predicted by the other half's P.

Datasets: trained model, final layer, before and after the final LayerNorm; random-weights twin (context).
"""
import os
import sys
import time

import numpy as np
from scipy.stats import spearmanr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import dino, rnd, save_json  # noqa: E402

G = 16


def additive_parts(P):
    """P: (256, d) centred over positions -> (row effects 16 x d, column effects 16 x d, fitted table 256 x d)."""
    T = P.reshape(G, G, -1)
    r, c = T.mean(1), T.mean(0)
    fit = (r[:, None, :] + c[None, :, :]).reshape(G * G, -1)
    return r, c, fit


def factor_stats(E):
    """E: (16, d) effects (zero mean over the index). PCA shares, coordinates, Spearman with the index."""
    s = np.linalg.svd(E, full_matrices=False)
    e = s[1] ** 2
    coord = E @ s[2][:2].T                                   # (16, 2)
    rho = spearmanr(coord[:, 0], np.arange(G))[0]
    # how linear is the 1-D coordinate in the index, and how much of the factor is a straight segment?
    idx = np.arange(G) - (G - 1) / 2
    lin_dir = (idx[:, None] * E).sum(0) / (idx ** 2).sum()   # least-squares slope vector: E_i ~ idx_i * lin_dir
    r2_linear = 1 - ((E - idx[:, None] * lin_dir) ** 2).sum() / (E ** 2).sum()
    return {"var_share_pc1": float(e[0] / e.sum()), "var_share_pc1_2": float(e[:2].sum() / e.sum()),
            "var_share_pc1_3": float(e[:3].sum() / e.sum()),
            "participation_ratio": float(e.sum() ** 2 / (e ** 2).sum()),
            "spearman_coord1_vs_index_abs": float(abs(rho)),
            "r2_linear_in_index": float(r2_linear),
            "coord_pc1": rnd(coord[:, 0], 4), "coord_pc2": rnd(coord[:, 1], 4)}, s[2][0]


def analyse(X, label):
    """X: (n_img, 256, d) array-like (memmap)."""
    n = X.shape[0]
    sums = np.zeros((2, 256, X.shape[2]))
    sq = 0.0
    for b in range(0, n, 50):
        x = np.asarray(X[b:b + 50], dtype=np.float64)
        par = (np.arange(b, b + x.shape[0]) % 2)
        sums[0] += x[par == 0].sum(0)
        sums[1] += x[par == 1].sum(0)
        sq += float((x ** 2).sum())
    n_half = np.array([(np.arange(n) % 2 == 0).sum(), (np.arange(n) % 2 == 1).sum()])
    P_raw = sums.sum(0) / n
    grand = P_raw.mean(0)
    P = P_raw - grand
    tot_var = sq - n * 256 * float(grand @ grand)            # all tokens about the grand mean
    r, c, fit = additive_parts(P)
    ss = float((P ** 2).sum())
    r2_add = 1 - float(((P - fit) ** 2).sum()) / ss
    row_stats, v_r = factor_stats(r)
    col_stats, v_c = factor_stats(c)
    sv = np.linalg.svd(P, compute_uv=False)
    # split-half
    Pa = sums[0] / n_half[0]
    Pb = sums[1] / n_half[1]
    Pa, Pb = Pa - Pa.mean(0), Pb - Pb.mean(0)
    cv = []
    for A, B in ((Pa, Pb), (Pb, Pa)):
        _, _, fitA = additive_parts(A)
        ssB = float((B ** 2).sum())
        cv.append({"r2_additive_fit_of_other_half": 1 - float(((B - fitA) ** 2).sum()) / ssB,
                   "r2_ceiling_other_half_table": 1 - float(((B - A) ** 2).sum()) / ssB})
    # residual structure: what the non-additive part looks like
    res = P - fit
    sres = np.linalg.svd(res, compute_uv=False)
    out = {
        "label": label, "n_images": int(n),
        "r2_additive": r2_add,
        "r2_additive_null_generic_table": 30 / 255,
        "share_rows": float(G * (r ** 2).sum() / ss), "share_columns": float(G * (c ** 2).sum() / ss),
        "rows": row_stats, "columns": col_stats,
        "cos_leading_row_vs_column_direction_abs": float(abs(v_r @ v_c)),
        "position_share_of_token_variance": float(n * ss / tot_var),
        "P_frobenius_norm": float(np.sqrt(ss)), "token_total_variance_per_token": float(tot_var / (n * 256)),
        "P_centred_top2_pc_share": float((sv[:2] ** 2).sum() / (sv ** 2).sum()),
        "P_centred_stable_rank": float((sv ** 2).sum() / sv[0] ** 2),
        "P_centred_singular_values_top10": rnd(sv[:10], 4),
        "residual_top_singular_values": rnd(sres[:6], 4),
        "split_half": {"a_to_b": cv[0], "b_to_a": cv[1],
                       "r2_additive_cv_mean": float(np.mean([d["r2_additive_fit_of_other_half"] for d in cv])),
                       "r2_ceiling_mean": float(np.mean([d["r2_ceiling_other_half_table"] for d in cv]))},
        # the two-factor "segment" model: P[i,j] ~ a_i v_r + b_j v_c with one direction per factor
        "r2_rank1_factors": float(1 - ((P - ((r @ v_r)[:, None, None] * v_r + (c @ v_c)[None, :, None] * v_c)
                                        .reshape(256, -1)) ** 2).sum() / ss),
    }
    # strictly linear ("two segments") model: P[i,j] ~ i * a + j * b
    ii, jj = np.meshgrid(np.arange(G) - 7.5, np.arange(G) - 7.5, indexing="ij")
    A = np.stack([ii.ravel(), jj.ravel()], 1)
    coef = np.linalg.lstsq(A, P, rcond=None)[0]
    out["r2_linear_in_row_and_column_index"] = float(1 - ((P - A @ coef) ** 2).sum() / ss)
    return out


def main():
    t0 = time.time()
    res = {}
    for which, kind in (("trained", "prenorm"), ("trained", "postnorm"), ("random", "prenorm"), ("random", "postnorm")):
        try:
            X = dino.load_features(which, kind)
        except FileNotFoundError as e:
            print("skipped", which, kind, e)
            continue
        res[f"{which}_{kind}"] = analyse(X, f"{which} model, final layer, {kind}")
        o = res[f"{which}_{kind}"]
        print(f"{which:8s}{kind:9s} R2_add {o['r2_additive']:.4f} (cv {o['split_half']['r2_additive_cv_mean']:.4f}, "
              f"ceiling {o['split_half']['r2_ceiling_mean']:.4f}) | rows PC1 {o['rows']['var_share_pc1']:.3f} "
              f"PC1-2 {o['rows']['var_share_pc1_2']:.3f} rho {o['rows']['spearman_coord1_vs_index_abs']:.3f} | cols PC1 "
              f"{o['columns']['var_share_pc1']:.3f} PC1-2 {o['columns']['var_share_pc1_2']:.3f} rho "
              f"{o['columns']['spearman_coord1_vs_index_abs']:.3f} | cos {o['cos_leading_row_vs_column_direction_abs']:.3f} "
              f"| pos share of var {o['position_share_of_token_variance']:.4f} | rank-1 factors R2 "
              f"{o['r2_rank1_factors']:.3f} | linear R2 {o['r2_linear_in_row_and_column_index']:.3f}")
    save_json("r6_position_additive", {
        "experiment": "R6 additivity of the position code (final layer)",
        "definitions": {
            "P": "mean patch token per position over the images, minus its mean over the 256 positions",
            "r2_additive": "1 - ||P - r_i - c_j||^2/||P||^2 with r, c the row / column means of the 16x16 table",
            "rows/columns": "PCA of the 16 effects: var_share_pc1, var_share_pc1_2, participation_ratio; "
                            "coord_pc1/2 = coordinates of the 16 effects; spearman of coord_pc1 with the index; "
                            "r2_linear_in_index = share of the effects explained by index * (one vector)",
            "r2_rank1_factors": "R2 of P[i,j] ~ a_i v_r + b_j v_c (one direction per factor, free coordinates)",
            "r2_linear_in_row_and_column_index": "R2 of P[i,j] ~ i a + j b (two straight segments)",
            "position_share_of_token_variance": "n_img ||P||_F^2 / sum over all tokens of ||x - grand mean||^2",
            "split_half": "even vs odd images: additive fit of one half evaluated on the other half's table; "
                          "ceiling = other half's table predicted by this half's table"},
        "results": res}, t0)


if __name__ == "__main__":
    main()
