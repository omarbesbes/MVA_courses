"""R3 — per-image archetypal analysis in its sandwich  PCA(K-1) <= AA(K) <= k-means(K).

For each image, X = its 256 final-layer patch tokens (768-d). For K in KS: FVU of PCA(K-1) (rh.aa.pca_fvu),
AA(K) (rh.aa.archetypal_analysis; first start = the k-means solution, second = FurthestSum) and k-means(K)
(the k-means run that initialises AA: rh.aa.kmeans, k-means++, 3 restarts; returned as ``kmeans_fvu``).
Gap ratio g = (AA - PCA) / (k-means - PCA): 0 = AA as good as the affine subspace, 1 = no better than clusters.

Datasets (rows of the result table):
  post      trained model, post-norm, the 200 images "first 20 of each class" of the statistics list
  pre       trained model, pre-norm, the first 100 of those images
  random    random-weights twin, post-norm, the same 100 images
Nulls, per image, through the same pipeline (computed for the 100 images of ``pre``/``random`` in post-norm):
  n1        256 samples of the Gaussian with that image's mean and covariance (rh.nulls.gaussian_like)
  n2        positive control: 256 Dirichlet(0.5) mixtures of 10 tokens drawn at random from the image, plus
            isotropic Gaussian noise whose scale is tuned (bisection) so that PCA(9) FVU equals the image's own.

Usage: python r3_aa_sandwich.py [n_images_post]   (default 200)
"""
import os
import sys
import time
from multiprocessing import Pool

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import dino, rnd, save_json  # noqa: E402
from rh.aa import archetypal_analysis, pca_fvu  # noqa: E402
from rh.nulls import dirichlet_mixtures, gaussian_like  # noqa: E402

KS = (2, 3, 5, 10, 20, 30, 50)
AA_ITER = 300
AA_RESTARTS = 2


def sandwich(X, seed):
    X = np.asarray(X, dtype=np.float64)
    pca = pca_fvu(X, np.array(KS) - 1)
    aa, km = np.zeros(len(KS)), np.zeros(len(KS))
    for i, K in enumerate(KS):
        r = archetypal_analysis(X, K, n_iter=AA_ITER, n_restarts=AA_RESTARTS, seed=seed + K)
        aa[i], km[i] = r["fvu"], r["kmeans_fvu"]
    return np.stack([pca, aa, km])                       # 3 x len(KS)


def positive_control(X, seed):
    """Dirichlet(0.5) mixtures of 10 tokens + isotropic noise matched on PCA(9) FVU."""
    X = np.asarray(X, dtype=np.float64)
    rng = np.random.default_rng(seed)
    V = X[rng.choice(X.shape[0], size=10, replace=False)]
    M = dirichlet_mixtures(V, X.shape[0], alpha=0.5, seed=rng)
    G = rng.standard_normal(M.shape)
    target = pca_fvu(X, 9)
    lo, hi = 0.0, 1.0
    while pca_fvu(M + hi * G, 9) < target:
        hi *= 2
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if pca_fvu(M + mid * G, 9) < target:
            lo = mid
        else:
            hi = mid
    s = 0.5 * (lo + hi)
    return M + s * G, s, pca_fvu(M + s * G, 9), target


def job(args):
    tag, i, X, seed = args
    t0 = time.time()
    extra = {}
    if tag == "n1":
        X = gaussian_like(X, seed=seed).astype(np.float64)
    elif tag == "n2":
        X, s, got, target = positive_control(X, seed)
        extra = {"noise_sigma": s, "pca9_fvu": got, "pca9_target": target}
    return tag, i, sandwich(X, seed), extra, time.time() - t0


def aggregate(R):
    """R: n_img x 3 x len(KS)."""
    pca, aa, km = R[:, 0], R[:, 1], R[:, 2]
    with np.errstate(invalid="ignore", divide="ignore"):
        g = (aa - pca) / (km - pca)
    n = R.shape[0]
    sem = lambda a: np.nanstd(a, 0, ddof=1) / np.sqrt(np.isfinite(a).sum(0))  # noqa: E731
    return {"n_images": int(n), "K": list(KS),
            "pca_Km1_mean": rnd(pca.mean(0), 5), "pca_Km1_sem": rnd(sem(pca), 5),
            "aa_mean": rnd(aa.mean(0), 5), "aa_sem": rnd(sem(aa), 5),
            "kmeans_mean": rnd(km.mean(0), 5), "kmeans_sem": rnd(sem(km), 5),
            "gap_ratio_mean": rnd(np.nanmean(g, 0), 4), "gap_ratio_sem": rnd(sem(g), 4),
            "gap_ratio_median": rnd(np.nanmedian(g, 0), 4),
            "sandwich_violations": int(((aa < pca - 1e-9) | (aa > km + 1e-9)).sum())}


def main():
    t0 = time.time()
    n_post = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    per_class = n_post // 10
    img = np.array([c * 100 + j for c in range(10) for j in range(per_class)])        # 200 images
    img100 = np.array([c * 100 + j for c in range(10) for j in range(per_class // 2)])  # first 10 per class
    post = dino.load_features("trained", "postnorm")
    pre = dino.load_features("trained", "prenorm")
    rnd_post = dino.load_features("random", "postnorm")
    jobs = []
    for i, im in enumerate(img):
        jobs.append(("post", i, np.asarray(post[im]), 10_000 + int(im)))
    for i, im in enumerate(img100):
        jobs.append(("pre", i, np.asarray(pre[im]), 20_000 + int(im)))
        jobs.append(("random", i, np.asarray(rnd_post[im]), 30_000 + int(im)))
        jobs.append(("n1", i, np.asarray(post[im]), 40_000 + int(im)))
        jobs.append(("n2", i, np.asarray(post[im]), 50_000 + int(im)))
    sizes = {"post": len(img), "pre": len(img100), "random": len(img100), "n1": len(img100), "n2": len(img100)}
    R = {k: np.full((n, 3, len(KS)), np.nan) for k, n in sizes.items()}
    extras = {"n2": []}
    done = 0
    with Pool(4) as pool:
        for tag, i, r, extra, dt in pool.imap_unordered(job, jobs, chunksize=1):
            R[tag][i] = r
            if extra:
                extras["n2"].append(extra)
            done += 1
            if done % 25 == 0:
                print(f"{done}/{len(jobs)} jobs, {time.time() - t0:.0f} s (last {dt:.1f} s)", flush=True)
    res = {k: aggregate(v) for k, v in R.items()}
    sig = np.array([e["noise_sigma"] for e in extras["n2"]])
    res["n2"]["noise_sigma"] = {"mean": float(sig.mean()), "min": float(sig.min()), "max": float(sig.max())}
    res["n2"]["pca9_fvu_match_max_abs_err"] = float(max(abs(e["pca9_fvu"] - e["pca9_target"]) for e in extras["n2"]))
    out = {"experiment": "R3 per-image AA sandwich PCA(K-1) <= AA(K) <= k-means(K)",
           "design": {"K": list(KS), "post_images": "statistics images, first %d of each class (index list "
                      "c*100+j)" % per_class, "pre/random/n1/n2 images": "first %d of each class" % (per_class // 2),
                      "AA": f"rh.aa.archetypal_analysis(n_iter={AA_ITER}, n_restarts={AA_RESTARTS}: k-means start "
                            "+ FurthestSum start), float64", "k-means": "the k-means++ run (3 restarts) that "
                            "initialises AA (rh.aa.kmeans), so AA <= k-means by construction",
                      "PCA": "rh.aa.pca_fvu(X, K-1)", "gap_ratio": "(AA - PCA)/(kmeans - PCA) per image, then mean",
                      "n1": "rh.nulls.gaussian_like(image tokens), 256 samples",
                      "n2": "Dirichlet(0.5) mixtures of 10 random tokens of the image + isotropic noise, noise "
                            "scale bisected to match the image's PCA(9) FVU",
                      "seeds": "per image: post 10000+i, pre 20000+i, random 30000+i, n1 40000+i, n2 50000+i "
                               "(i = index in the 1000-image list), + K for AA"},
           "results": res}
    save_json("r3_aa_sandwich", out, t0)
    for k, v in res.items():
        print(f"{k:7s} PCA {v['pca_Km1_mean']}\n        AA  {v['aa_mean']}\n        KM  {v['kmeans_mean']}\n"
              f"        g   {v['gap_ratio_mean']}  violations {v['sandwich_violations']}")


if __name__ == "__main__":
    main()
