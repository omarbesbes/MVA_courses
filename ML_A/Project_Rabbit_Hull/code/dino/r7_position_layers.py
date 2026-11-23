"""R7 — the position code across layers (the paper's Fig. 14-15).

Depth convention: 0 = input of block 1 (patch + position embedding), l = 1..12 = output of block l,
"12+LN" = final LayerNorm applied to depth 12 (the output tokens).

From the sufficient statistics accumulated by r0_extract.py over the 1000 statistics images:
  P_l            mean patch token per position (256 x 768)
  stable rank    ||P||_F^2 / ||P||_2^2, for P_l as it is ("uncentred") and minus its mean over positions
  top-2 share    share of ||P||_F^2 carried by the two leading singular directions (centred = R2 of a 2-D PCA)
  coords         2-D PCA coordinates of the 256 centred position vectors, for selected depths
  variance share n_img ||P_centred||_F^2 / total variance of the patch tokens at that depth
Position probe: ridge least squares on one-hot targets (256 classes), features centred, fit on the patch tokens
of 300 images (first 30 statistics images of each class), tested on 100 held-out images (first 10 held-out
images of each class). lambda = lambda_rel * trace(X_c^T X_c) / 768.
"""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import dino, rnd, save_json  # noqa: E402

COORD_DEPTHS = [0, 2, 4, 6, 8, 9, 10, 11, 12, 13]
LAMBDAS = [1e-5, 1e-3, 1e-1]
HEADLINE_LAMBDA = 1e-3


def spectrum_stats(P):
    s = np.linalg.svd(P, compute_uv=False)
    e = s ** 2
    return {"stable_rank": float(e.sum() / e[0]), "top2_share": float(e[:2].sum() / e.sum()),
            "top1_share": float(e[0] / e.sum()), "participation_ratio": float(e.sum() ** 2 / (e ** 2).sum()),
            "frobenius": float(np.sqrt(e.sum()))}


def main():
    t0 = time.time()
    st = np.load(os.path.join(dino.DEFAULT_CACHE, "feats", "trained_layer_stats.npz"))
    held = np.load(dino.feature_path("heldout_layers_f16"), mmap_mode="r")      # 14 x 100 x 256 x 768
    n_img, n_tr = int(st["n_images"]), int(st["n_train_images"])
    labels = [str(x) for x in st["depth_labels"]]
    L = len(labels)
    target = np.tile(np.arange(256), held.shape[1])
    ti, tj = target // 16, target % 16
    per_depth, coords = [], {}
    for l in range(L):
        P_all = st["pos_sum"][l] / n_img                       # 261 x 768 (cls, 4 reg, 256 patches)
        P = P_all[dino.N_SPECIAL:]
        grand = P.mean(0)
        Pc = P - grand
        unc, cen = spectrum_stats(P), spectrum_stats(Pc)
        tot_var = float(st["sq_sum"][l]) - n_img * 256 * float(grand @ grand)
        U, s, Vt = np.linalg.svd(Pc, full_matrices=False)
        if l in COORD_DEPTHS:
            coords[labels[l]] = rnd(U[:, :2] * s[:2], 4)
        # ---- probe
        n = n_tr * 256
        S_p = st["pos_sum_train"][l]                           # 256 x 768: sum over the train images
        m = S_p.sum(0) / n
        Sc = st["xtx_train"][l] - n * np.outer(m, m)
        XtY = (S_p - n_tr * m[None, :]).T                      # 768 x 256
        Xh = np.asarray(held[l], dtype=np.float64).reshape(-1, dino.DIM) - m
        probe = {}
        for lam_rel in LAMBDAS:
            lam = lam_rel * np.trace(Sc) / dino.DIM
            W = np.linalg.solve(Sc + lam * np.eye(dino.DIM), XtY)
            pred = (Xh @ W).argmax(1)
            pi, pj = pred // 16, pred % 16
            probe[f"{lam_rel:g}"] = {
                "accuracy": float((pred == target).mean()),
                "accuracy_within_1_patch": float((np.maximum(abs(pi - ti), abs(pj - tj)) <= 1).mean()),
                "row_accuracy": float((pi == ti).mean()), "column_accuracy": float((pj == tj).mean()),
                "mean_grid_error": float(np.hypot(pi - ti, pj - tj).mean())}
        d = {"depth": labels[l],
             "stable_rank_uncentred": unc["stable_rank"], "stable_rank_centred": cen["stable_rank"],
             "top2_share_uncentred": unc["top2_share"], "top2_share_centred": cen["top2_share"],
             "top1_share_uncentred": unc["top1_share"], "participation_ratio_centred": cen["participation_ratio"],
             "P_frobenius_uncentred": unc["frobenius"], "P_frobenius_centred": cen["frobenius"],
             "position_share_of_token_variance": float(n_img * (Pc ** 2).sum() / tot_var),
             "centred_singular_values_top6": rnd(s[:6], 4),
             "probe": probe, "probe_accuracy": probe[f"{HEADLINE_LAMBDA:g}"]["accuracy"]}
        per_depth.append(d)
        print(f"depth {labels[l]:>5s}: stable rank unc {unc['stable_rank']:.2f} cen {cen['stable_rank']:.2f} | top-2 "
              f"share cen {cen['top2_share']:.3f} unc {unc['top2_share']:.3f} | pos var share "
              f"{d['position_share_of_token_variance']:.4f} | probe acc "
              + " ".join(f"{probe[f'{x:g}']['accuracy']:.3f}" for x in LAMBDAS)
              + f" | within-1 {probe[f'{HEADLINE_LAMBDA:g}']['accuracy_within_1_patch']:.3f}")
    save_json("r7_position_layers", {
        "experiment": "R7 position across layers",
        "depth_convention": "0 = input of block 1; l = output of block l (l = 1..12); '12+LN' = after the final "
                            "LayerNorm. The paper's Fig. 14 uses layer indices 0-11 (decoding, R2) and 1-12 "
                            "(stable rank) without saying which is which.",
        "n_images_for_P": n_img,
        "probe": {"train_images": n_tr, "test_images": int(held.shape[1]), "classes": 256, "chance": 1 / 256,
                  "method": "ridge least squares on centred one-hot targets, closed form from the normal equations "
                            "accumulated in float64; test features stored as float16",
                  "lambda_rel_values": LAMBDAS, "headline_lambda_rel": HEADLINE_LAMBDA},
        "per_depth": per_depth,
        "coords_2d": {"depths": list(coords.keys()), "note": "256 x 2 PCA coordinates (U S) of the centred position "
                      "matrix, row-major 16 x 16 grid: index p = 16 * row + column", "values": coords},
        "paper_values_for_comparison": {
            "decoding_accuracy_layers_0_11": [1.0, 1.0, 1.0, 0.97, 0.97, 0.95, 0.92, 0.92, 0.82, 0.44, 0.34, 0.23],
            "stable_rank_layers_1_12": [9.0, 8.1, 5.4, 7.2, 5.6, 5.4, 4.9, 4.4, 4.4, 2.8, 2.6, 2.7],
            "r2_top2_layers_0_11": [0.63, 0.75, 0.83, 0.77, 0.81, 0.86, 0.90, 0.94, 0.96, 0.99, 1.00, 1.00],
            "source": "read off Fig. 14 of arXiv:2510.08638v3 (see NOTES.md); ImageNet-1k, not Imagenette"}}, t0)


if __name__ == "__main__":
    main()
