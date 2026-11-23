"""R5 — co-activation of a global archetypal analysis versus image identity (the paper's Fig. 17 right).

Tokens: trained model, final layer, post-norm patch tokens of 100 images (the first 10 statistics images of
each Imagenette class), N = 25,600. AA (rh.aa.archetypal_analysis, float32, k-means start) with K archetypes;
codes A (N x K, rows on the simplex); co-activation C = A^T A.

Per archetype k: usage mass per image m_ki = sum of A[t, k] over the tokens t of image i, and per class.
  top-image share = max_i m_ki / sum_i m_ki   (1/100 if spread evenly over images)
  top-class share = same over classes          (1/10)
  dominant image / class = the argmax.
Off-diagonal co-activation mass: share of sum_{k != l} C_kl on pairs (k, l) with the same dominant image, and
with the same dominant class; baseline = the same share after shuffling the dominant labels over the
archetypes (mean of 500 permutations).
Hierarchical clustering of C: average linkage on the distance 1 - C_kl / sqrt(C_kk C_ll), cut into 10 and 20
blocks; adjusted mutual information of the block labels with the dominant class and the dominant image.
Also: share of the total C mass inside the clustering blocks (block-diagonality).

Usage: python r5_coactivation.py [K ...]   (default 200 50)
"""
import os
import sys
import time

import numpy as np
from scipy.cluster.hierarchy import fcluster, leaves_list, linkage
from scipy.spatial.distance import squareform

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import RESULTS, dino, rnd, save_json  # noqa: E402
from rh.aa import archetypal_analysis  # noqa: E402

N_PER_CLASS = 10


def ami(a, b):
    from sklearn.metrics import adjusted_mutual_info_score
    return float(adjusted_mutual_info_score(a, b))


def same_label_share(C, lab, rng, n_perm=500):
    off = C.copy()
    np.fill_diagonal(off, 0.0)
    tot = off.sum()
    share = float(off[lab[:, None] == lab[None, :]].sum() / tot)
    perm = [float(off[(p := rng.permutation(lab))[:, None] == p[None, :]].sum() / tot) for _ in range(n_perm)]
    return {"share": share, "perm_baseline_mean": float(np.mean(perm)), "perm_baseline_q95": float(np.quantile(perm, 0.95))}


def analyse(A, img_of_tok, cls_of_tok, n_img, seed=0):
    K = A.shape[1]
    A = A.astype(np.float64)
    M_img = np.zeros((K, n_img))
    np.add.at(M_img.T, img_of_tok, A)                       # M_img[k, i] = sum_t in i A[t, k]
    M_cls = np.zeros((K, 10))
    np.add.at(M_cls.T, cls_of_tok, A)
    usage = A.sum(0)
    used = usage > 1e-9
    with np.errstate(invalid="ignore", divide="ignore"):
        top_img_share = M_img.max(1) / usage
        top_cls_share = M_cls.max(1) / usage
    dom_img = M_img.argmax(1)
    dom_cls = M_cls.argmax(1)
    C = A.T @ A
    rng = np.random.default_rng(seed)
    d = np.sqrt(np.maximum(np.diag(C), 1e-30))
    S = C / d[:, None] / d[None, :]
    D = np.clip(1.0 - S, 0.0, None)
    np.fill_diagonal(D, 0.0)
    D = 0.5 * (D + D.T)
    Z = linkage(squareform(D, checks=False), method="average")
    order_clust = leaves_list(Z)
    blocks = {}
    for nb in (10, 20):
        lab = fcluster(Z, nb, criterion="maxclust")
        inside = lab[:, None] == lab[None, :]
        off = C.copy()
        np.fill_diagonal(off, 0.0)
        blocks[str(nb)] = {"n_blocks_obtained": int(lab.max()),
                           "block_sizes": sorted(np.bincount(lab)[1:].tolist(), reverse=True),
                           "ami_dominant_class": ami(lab, dom_cls), "ami_dominant_image": ami(lab, dom_img),
                           "offdiag_mass_inside_blocks": float(off[inside].sum() / off.sum()),
                           "labels": lab.tolist()}
    order_cls = np.lexsort((dom_img, dom_cls))
    # how concentrated is each token's code
    nnz = (A > 1e-6).sum(1)
    tokmax = A.max(1)
    res = {
        "K": int(K), "n_archetypes_used": int(used.sum()),
        "top_image_share": {"mean": float(np.nanmean(top_img_share)), "median": float(np.nanmedian(top_img_share)),
                            "q90": float(np.nanquantile(top_img_share, 0.9)), "uniform": 1 / n_img,
                            "frac_archetypes_above_0.5": float(np.nanmean(top_img_share > 0.5))},
        "top_class_share": {"mean": float(np.nanmean(top_cls_share)), "median": float(np.nanmedian(top_cls_share)),
                            "q90": float(np.nanquantile(top_cls_share, 0.9)), "uniform": 0.1,
                            "frac_archetypes_above_0.5": float(np.nanmean(top_cls_share > 0.5))},
        "n_distinct_dominant_images": int(len(np.unique(dom_img))),
        "n_distinct_dominant_classes": int(len(np.unique(dom_cls))),
        "offdiag_coactivation_same_dominant_image": same_label_share(C, dom_img, rng),
        "offdiag_coactivation_same_dominant_class": same_label_share(C, dom_cls, rng),
        "diag_share_of_total_C_mass": float(np.trace(C) / C.sum()),
        "hierarchical_blocks": blocks,
        "codes": {"mean_nonzeros_per_token": float(nnz.mean()), "median_nonzeros_per_token": float(np.median(nnz)),
                  "mean_max_weight_per_token": float(tokmax.mean())},
        "top_image_share_per_archetype": rnd(top_img_share, 4), "top_class_share_per_archetype": rnd(top_cls_share, 4),
        "dominant_image": dom_img.tolist(), "dominant_class": dom_cls.tolist(),
    }
    arrays = {"C_clustered": C[np.ix_(order_clust, order_clust)].astype(np.float16), "order_clustered": order_clust,
              "C_by_class_image": C[np.ix_(order_cls, order_cls)].astype(np.float16), "order_by_class_image": order_cls,
              "dominant_image": dom_img, "dominant_class": dom_cls,
              "blocks10": np.array(blocks["10"]["labels"]), "blocks20": np.array(blocks["20"]["labels"])}
    return res, arrays


def main():
    t0 = time.time()
    Ks = [int(a) for a in sys.argv[1:]] or [200, 50]
    post = dino.load_features("trained", "postnorm")
    imgs = np.array([c * 100 + j for c in range(10) for j in range(N_PER_CLASS)])
    X = np.asarray(post[imgs], dtype=np.float32).reshape(-1, dino.DIM)
    n_img = len(imgs)
    img_of_tok = np.repeat(np.arange(n_img), dino.N_PATCH)
    cls_of_tok = np.repeat(imgs // 100, dino.N_PATCH)
    out = {"experiment": "R5 co-activation of a global AA vs image identity",
           "design": {"tokens": "trained post-norm patch tokens of the statistics images c*100+j, j < 10 "
                                "(10 per class, 100 images), N = 25600",
                      "AA": "rh.aa.archetypal_analysis(n_iter=150, n_restarts=1 (k-means start, 2 k-means++ "
                            "restarts), dtype float32, seed 0)",
                      "co-activation": "C = A^T A", "clustering": "scipy average linkage on 1 - C/sqrt(diag diag)",
                      "AMI": "sklearn adjusted_mutual_info_score"}, "results": {}}
    npz = {}
    for K in Ks:
        t1 = time.time()
        r = archetypal_analysis(X, K, n_iter=150, n_restarts=1, seed=0, dtype=np.float32, kmeans_restarts=2,
                                verbose=True)
        res, arrays = analyse(r["A"], img_of_tok, cls_of_tok, n_img)
        res.update({"aa_fvu": float(r["fvu"]), "kmeans_fvu": float(r.get("kmeans_fvu", np.nan)),
                    "aa_iterations": len(r["history"]) - 2, "aa_time_s": round(time.time() - t1, 1)})
        out["results"][str(K)] = res
        npz.update({f"K{K}_{k}": v for k, v in arrays.items()})
        np.savez_compressed(os.path.join(RESULTS, "r5_coactivation.npz"), **npz)
        save_json("r5_coactivation", out, t0)
        b = res["hierarchical_blocks"]
        print(f"K={K}: fvu AA {res['aa_fvu']:.4f} (k-means {res['kmeans_fvu']:.4f}); top-image share mean "
              f"{res['top_image_share']['mean']:.3f} (1/100), top-class {res['top_class_share']['mean']:.3f} (1/10); "
              f"off-diag same image {res['offdiag_coactivation_same_dominant_image']}, same class "
              f"{res['offdiag_coactivation_same_dominant_class']}; AMI10 class {b['10']['ami_dominant_class']:.3f} "
              f"image {b['10']['ami_dominant_image']:.3f}; AMI20 class {b['20']['ami_dominant_class']:.3f} image "
              f"{b['20']['ami_dominant_image']:.3f}; {time.time() - t1:.0f} s", flush=True)


if __name__ == "__main__":
    main()
