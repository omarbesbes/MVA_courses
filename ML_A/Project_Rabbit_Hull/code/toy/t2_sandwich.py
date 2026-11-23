"""T2 - where archetypal analysis sits between PCA and k-means.

FVU[PCA(K-1)] <= FVU[AA(K)] <= FVU[k-means(K)] for every data set. Gap ratio g = (AA - PCA) / (kmeans - PCA).
Data: N = 256 points in R^50 (one image's token set):
  polytope : Dirichlet(0.5) mixtures of 10 random vertices + isotropic noise, sigma set so that PCA(9) FVU ~ 0.05;
  gauss    : Gaussian with exactly the same sample mean and covariance (rh.nulls.gaussian_like(exact=True));
  sum      : p + q, p and q Dirichlet(0.5) mixtures of 4 random vertices each (6-dim affine hull),
             same noise rule (sigma set so that PCA(6) FVU ~ 0.05).
K in {2, 3, 5, 10, 20, 30}, 20 repetitions. Writes results/t2_sandwich.json and results/t2_sandwich.npz.
"""
import json, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from rh.aa import archetypal_analysis, pca_fvu  # noqa: E402
from rh.nulls import gaussian_like  # noqa: E402

RES = os.path.join(HERE, "..", "results")
N, D, REPS = 256, 50, 20
KS = [2, 3, 5, 10, 20, 30]
SETS = ["polytope", "gauss", "sum"]
TARGET = 0.05


def add_noise(S, r, rng):
    """Isotropic noise with sigma such that the expected FVU outside the r-dim signal subspace is TARGET."""
    ss = ((S - S.mean(0)) ** 2).sum() / N                          # signal variance per point
    sig2 = TARGET * ss / ((D - r) - TARGET * D)
    return S + np.sqrt(sig2) * rng.standard_normal(S.shape), float(np.sqrt(sig2))


def make(rep):
    rng = np.random.default_rng(500 + rep)
    V = rng.standard_normal((10, D))
    Xp, sp = add_noise(rng.dirichlet(np.full(10, 0.5), size=N) @ V, 9, rng)
    Xg = gaussian_like(Xp, seed=900 + rep, exact=True).astype(np.float64)
    V1, V2 = rng.standard_normal((4, D)), rng.standard_normal((4, D))
    S = rng.dirichlet(np.full(4, 0.5), size=N) @ V1 + rng.dirichlet(np.full(4, 0.5), size=N) @ V2
    Xs, ss = add_noise(S, 6, rng)
    return {"polytope": Xp, "gauss": Xg, "sum": Xs}, {"polytope": sp, "sum": ss}


F = np.full((len(SETS), 3, len(KS), REPS), np.nan)               # set, method (pca, aa, km), K, rep
check = {}
t0 = time.time()
for rep in range(REPS):
    data, sig = make(rep)
    for a, s in enumerate(SETS):
        X = data[s]
        check.setdefault(f"{s}_pca9", []).append(pca_fvu(X, 9))
        check.setdefault(f"{s}_pca6", []).append(pca_fvu(X, 6))
        for b, K in enumerate(KS):
            aa = archetypal_analysis(X, K, n_restarts=3, seed=rep * 100 + K, n_iter=500, kmeans_restarts=10)
            F[a, :, b, rep] = [pca_fvu(X, K - 1), aa["fvu"], aa["kmeans_fvu"]]
    print(f"rep {rep}  [{time.time() - t0:.0f}s]", flush=True)

viol = {"pca_gt_aa": int((F[:, 0] > F[:, 1] + 1e-9).sum()), "aa_gt_km": int((F[:, 1] > F[:, 2] + 1e-9).sum())}
G = (F[:, 1] - F[:, 0]) / (F[:, 2] - F[:, 0])                      # (set, K, rep)
sem = lambda x: x.std(-1, ddof=1) / np.sqrt(x.shape[-1])
out = {"config": {"N": N, "d": D, "reps": REPS, "K": KS, "target_fvu_noise": TARGET},
       "noise_check_mean": {k: float(np.mean(v)) for k, v in check.items()}, "sandwich_violations": viol}
for a, s in enumerate(SETS):
    out[s] = {}
    for b, K in enumerate(KS):
        out[s][str(K)] = {m: [float(F[a, i, b].mean()), float(sem(F[a, i, b]))]
                          for i, m in enumerate(["pca_Km1", "aa", "kmeans"])}
        out[s][str(K)]["g"] = [float(G[a, b].mean()), float(sem(G[a, b]))]
# separation of polytope vs gauss by g: paired difference and the share of repetitions with g_poly < g_gauss
out["g_polytope_minus_gauss"] = {str(K): {"mean": float((G[0, b] - G[1, b]).mean()),
                                          "sem": float(sem(G[0, b] - G[1, b])),
                                          "frac_reps_poly_below": float((G[0, b] < G[1, b]).mean())}
                                 for b, K in enumerate(KS)}
json.dump(out, open(os.path.join(RES, "t2_sandwich.json"), "w"), indent=1)
np.savez_compressed(os.path.join(RES, "t2_sandwich.npz"), fvu=F, g=G, K=np.array(KS), sets=np.array(SETS),
                    methods=np.array(["pca_Km1", "aa", "kmeans"]))
print("noise check", out["noise_check_mean"], "violations", viol)
for a, s in enumerate(SETS):
    for b, K in enumerate(KS):
        r = out[s][str(K)]
        print(f"{s:8s} K={K:2d}  PCA {r['pca_Km1'][0]:.3f}  AA {r['aa'][0]:.3f}  KM {r['kmeans'][0]:.3f}  "
              f"g {r['g'][0]:.3f}+-{r['g'][1]:.3f}")
print("g poly - gauss", out["g_polytope_minus_gauss"])
