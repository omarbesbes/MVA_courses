"""R2 — the paper's interpolation test (Fig. 17, left) with null models.

For two tokens x_i, x_j of a sample X of N tokens: distance to the nearest sample along the straight segment
and along the shortest path of the k-NN graph (rh.interp.chord_test; k = 15, cosine neighbours, Euclidean
distances, 101 positions, 300 random pairs).

Datasets (N = 50,000 tokens drawn once, seed 0, from the 256,000 cached final-layer patch tokens):
  a  trained model, after the final LayerNorm
  b  trained model, before the final LayerNorm (same token indices)
  c  Gaussian with the mean and full covariance of (a)                      [convex support, same 2nd moments]
  d  Gaussian with the moments of (b), pushed through the model's final LayerNorm  [ellipsoid, no structure]
  e  random-weights twin, after its final LayerNorm (same token indices)
  f  Gaussian-mixture null: k-means (200 clusters) on (a); each point = its cluster centre + Gaussian noise with
     that cluster's per-coordinate variance
For (a) also k in {5, 50} and N in {5,000, 20,000} (nested random subsets, new pairs).

Reading: a normalised straight curve equal to min(t, 1 - t) (peak 0.5) means that the nearest sample of every
point of the segment is one of its two endpoints.
"""
import os
import sys
import time

import numpy as np
from scipy import sparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import QUICKLOOK, RESULTS, dino, rnd, save_json  # noqa: E402
from rh import interp, nulls  # noqa: E402
from rh.aa import kmeans  # noqa: E402

N = 50_000
N_PAIRS = 300
N_STEPS = 101
K_MAIN = 15


def graph_from_knn(idx, dist):
    """Symmetric (union) k-NN graph from neighbour lists; same construction as rh.interp.knn_graph."""
    n = idx.shape[0]
    i = np.repeat(np.arange(n, dtype=np.int64), idx.shape[1])
    j = idx.ravel()
    w = dist.ravel()
    lo, hi = np.minimum(i, j), np.maximum(i, j)
    _, first = np.unique(lo * n + hi, return_index=True)
    lo, hi, w = lo[first], hi[first], w[first]
    rows, cols, data = np.concatenate([lo, hi]), np.concatenate([hi, lo]), np.concatenate([w, w])
    order = np.lexsort((cols, rows))
    rows, cols, data = rows[order], cols[order], data[order]
    indptr = np.concatenate([[0], np.cumsum(np.bincount(rows, minlength=n))])
    return sparse.csr_matrix((data, cols.astype(np.int32), indptr), shape=(n, n))


def graph_curves(X, pairs, graph, n_steps=N_STEPS):
    """Graph half of chord_test for a given graph (used for the k-variants, where the straight half is unchanged)."""
    paths = interp.graph_paths(graph, pairs)
    P = len(pairs)
    gra = np.full((P, n_steps), np.nan)
    path_len, n_hops = np.full(P, np.nan), np.full(P, np.nan)
    buf, owners = [], []
    for p, nodes in enumerate(paths):
        if nodes is None:
            continue
        pts, length = interp.resample_path(np.asarray(X[nodes], dtype=np.float64), n_steps)
        path_len[p], n_hops[p] = length, len(nodes) - 1
        buf.append(pts)
        owners.append(p)
    if buf:
        gra[np.array(owners)] = interp.nearest_dist(np.concatenate(buf, 0), X).reshape(-1, n_steps)
    return {"graph": gra, "path_len": path_len, "n_hops": n_hops}


def summarise(res, X, nn_dist, k, label, extra=None):
    t = np.linspace(0, 1, N_STEPS)
    chord = res["chord"]
    lin, gra = res["lin"], res["graph"]
    ok = np.isfinite(res["path_len"])
    lin_n = lin / chord[:, None]
    gra_n = gra[ok] / chord[ok, None]
    mid = (t >= 0.2) & (t <= 0.8)
    tri = chord[:, None] * np.minimum(t, 1 - t)[None, :]
    on_triangle = np.abs(lin - tri) <= 1e-6 * chord[:, None]
    hops = res["n_hops"][ok]
    out = {
        "label": label, "N": int(X.shape[0]), "k": int(k), "n_pairs": int(len(chord)), "n_steps": N_STEPS,
        "n_disconnected_pairs": int((~ok).sum()),
        "summary": {
            "mean_chord": float(chord.mean()),
            "mean_nn_dist": float(nn_dist.mean()), "median_nn_dist": float(np.median(nn_dist)),
            "peak_mean_lin_normalised": float(lin_n.mean(0).max()),
            "peak_mean_lin_raw": float(lin.mean(0).max()),
            "mean_lin_at_midpoint_raw": float(lin[:, N_STEPS // 2].mean()),
            "frac_pairs_midpoint_nearest_is_endpoint": float(on_triangle[:, N_STEPS // 2].mean()),
            "frac_points_on_triangle": float(on_triangle[:, 1:-1].mean()),
            "mean_graph_normalised_middle60": float(gra_n[:, mid].mean()) if ok.any() else None,
            "mean_graph_raw_middle60": float(gra[ok][:, mid].mean()) if ok.any() else None,
            "max_mean_graph_raw": float(gra[ok].mean(0).max()) if ok.any() else None,
            "mean_path_len_over_chord": float((res["path_len"][ok] / chord[ok]).mean()) if ok.any() else None,
            "mean_hops": float(hops.mean()) if ok.any() else None,
            "mean_edge_length_on_paths": float((res["path_len"][ok] / np.maximum(hops, 1)).mean()) if ok.any() else None,
            "mean_nn_dist_over_mean_chord": float(nn_dist.mean() / chord.mean()),
        },
        "curves": {
            "lin_raw_mean": rnd(lin.mean(0), 4), "lin_raw_std": rnd(lin.std(0), 4),
            "lin_norm_mean": rnd(lin_n.mean(0), 5), "lin_norm_std": rnd(lin_n.std(0), 5),
            "graph_raw_mean": rnd(gra[ok].mean(0), 4) if ok.any() else None,
            "graph_raw_std": rnd(gra[ok].std(0), 4) if ok.any() else None,
            "graph_norm_mean": rnd(gra_n.mean(0), 5) if ok.any() else None,
            "graph_norm_std": rnd(gra_n.std(0), 5) if ok.any() else None,
        },
    }
    if extra:
        out.update(extra)
    s = out["summary"]
    print(f"[{label} | N={X.shape[0]} k={k}] chord {s['mean_chord']:.2f}  NN {s['mean_nn_dist']:.2f}  lin peak(norm) "
          f"{s['peak_mean_lin_normalised']:.4f} (raw {s['peak_mean_lin_raw']:.2f}; midpoint->endpoint in "
          f"{100 * s['frac_pairs_midpoint_nearest_is_endpoint']:.0f}% of pairs)  graph mid60 norm "
          f"{s['mean_graph_normalised_middle60']:.4f} raw {s['mean_graph_raw_middle60']:.2f}  path/chord "
          f"{s['mean_path_len_over_chord']:.2f}  hops {s['mean_hops']:.1f}  disconnected {out['n_disconnected_pairs']}",
          flush=True)
    return out


def run_dataset(X, pairs, label, ks=(K_MAIN,), seed=0):
    """Full test for k = K_MAIN, graph half only for the other k (the straight half does not depend on k)."""
    t0 = time.time()
    X = np.ascontiguousarray(X, dtype=np.float32)
    rng = np.random.default_rng(1000 + seed)
    sub = rng.choice(X.shape[0], size=min(2000, X.shape[0]), replace=False)
    nn_dist = interp.nearest_dist(X[sub], X, exclude=sub)
    idx, dist = interp.knn_search(X, k=max(ks), metric="cosine")
    t_knn = time.time() - t0
    outs = {}
    G = graph_from_knn(idx[:, :K_MAIN], dist[:, :K_MAIN])
    res = interp.chord_test(X, pairs, n_steps=N_STEPS, graph=G)
    outs[K_MAIN] = summarise(res, X, nn_dist, K_MAIN, label,
                             {"n_edges": int(G.nnz // 2), "mean_knn_edge_length": float(dist[:, :K_MAIN].mean())})
    for k in ks:
        if k == K_MAIN:
            continue
        Gk = graph_from_knn(idx[:, :k], dist[:, :k])
        rk = dict(res)
        rk.update(graph_curves(X, pairs, Gk))
        outs[k] = summarise(rk, X, nn_dist, k, label, {"n_edges": int(Gk.nnz // 2),
                                                        "mean_knn_edge_length": float(dist[:, :k].mean())})
    for o in outs.values():
        o["runtime_s"] = round(time.time() - t0, 1)
        o["knn_time_s"] = round(t_knn, 1)
    return outs


def gmm_null(A, n_clusters=200, seed=0):
    km = kmeans(A, n_clusters, n_restarts=1, seed=seed, n_iter=30)
    lab = km["labels"]
    C = km["centers"].astype(np.float64)
    var = np.zeros_like(C)
    for c in range(C.shape[0]):
        m = lab == c
        if m.sum() > 1:
            var[c] = np.asarray(A[m], dtype=np.float64).var(0)
    rng = np.random.default_rng(seed + 7)
    X = C[lab] + rng.standard_normal(A.shape) * np.sqrt(var[lab])
    return X.astype(np.float32), {"kmeans_fvu": float(km["fvu"]), "n_clusters": int(n_clusters),
                                  "min_cluster_size": int(np.bincount(lab, minlength=n_clusters).min())}


def main(only=None):
    t0 = time.time()
    model = dino.load_model(True)
    gamma, beta, eps = dino.final_norm_params(model)
    del model
    post = dino.load_features("trained", "postnorm")
    pre = dino.load_features("trained", "prenorm")
    rng = np.random.default_rng(0)
    tok = np.sort(rng.choice(post.shape[0] * 256, size=N, replace=False))
    A = np.asarray(post.reshape(-1, dino.DIM)[tok], dtype=np.float32)
    B = np.asarray(pre.reshape(-1, dino.DIM)[tok], dtype=np.float32)
    prng = np.random.default_rng(1)
    pairs = np.stack([prng.choice(N, size=2, replace=False) for _ in range(N_PAIRS)])
    perm = np.random.default_rng(2).permutation(N)

    out_path = os.path.join(RESULTS, "r2_interpolation_nulls.json")
    out = {"experiment": "R2 interpolation test with nulls", "datasets": {}, "variants_k": {}, "variants_N": {},
           "design": {"N": N, "token_sampling": "numpy default_rng(0).choice(256000, N, replace=False), sorted",
                      "pairs": "300 pairs of distinct indices, default_rng(1); the same index pairs in every dataset",
                      "k": K_MAIN, "metric": "cosine neighbours, Euclidean edge lengths and distances",
                      "n_steps": N_STEPS, "t": "linspace(0, 1, 101): fraction of the chord / of the path length",
                      "nn_dist": "leave-one-out Euclidean nearest-neighbour distance of 2000 random points"}}

    def save():
        save_json("r2_interpolation_nulls", out, t0)

    todo = only or ["a", "b", "c", "d", "f", "e", "N"]
    if "a" in todo:
        r = run_dataset(A, pairs, "a trained post-norm", ks=(5, 15, 50))
        out["datasets"]["a"] = r[15]
        out["variants_k"] = {"5": r[5], "15": r[15], "50": r[50]}
        save()
    if "b" in todo:
        out["datasets"]["b"] = run_dataset(B, pairs, "b trained pre-norm")[15]
        save()
    if "c" in todo:
        out["datasets"]["c"] = run_dataset(nulls.gaussian_like(A, seed=0), pairs, "c Gaussian, moments of (a)")[15]
        save()
    if "d" in todo:
        Xd = nulls.layernorm(nulls.gaussian_like(B, seed=1), gamma, beta, eps).astype(np.float32)
        out["datasets"]["d"] = run_dataset(Xd, pairs, "d Gaussian with moments of (b), then final LayerNorm")[15]
        del Xd
        save()
    if "f" in todo:
        Xf, info = gmm_null(A)
        out["datasets"]["f"] = run_dataset(Xf, pairs, "f Gaussian mixture (200 k-means clusters of (a))")[15]
        out["datasets"]["f"]["gmm"] = info
        del Xf
        save()
    if "e" in todo:
        twin = dino.load_features("random", "postnorm")
        E = np.asarray(twin.reshape(-1, dino.DIM)[tok], dtype=np.float32)
        out["datasets"]["e"] = run_dataset(E, pairs, "e random twin post-norm")[15]
        del E
        save()
    if "N" in todo:
        for n in (5000, 20000):
            sub = np.sort(perm[:n])
            p = np.stack([np.random.default_rng(3 + n).choice(n, size=2, replace=False) for _ in range(N_PAIRS)])
            out["variants_N"][str(n)] = run_dataset(A[sub], p, f"a trained post-norm, subset N={n}")[15]
        out["variants_N"][str(N)] = out["datasets"].get("a")
        save()

    # quicklook
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        t = np.linspace(0, 1, N_STEPS)
        fig, axes = plt.subplots(2, 3, figsize=(13, 7), sharex=True)
        for ax, (key, d) in zip(axes.ravel(), sorted(out["datasets"].items())):
            ax.plot(t, d["curves"]["lin_raw_mean"], label="straight")
            ax.plot(t, d["curves"]["graph_raw_mean"], label="k-NN graph path")
            ax.plot(t, d["summary"]["mean_chord"] * np.minimum(t, 1 - t), "k:", lw=0.8, label="chord x min(t,1-t)")
            ax.set_title(d["label"], fontsize=9)
            ax.legend(fontsize=7)
        os.makedirs(QUICKLOOK, exist_ok=True)
        fig.savefig(os.path.join(QUICKLOOK, "r2_curves.png"), dpi=90)
    except Exception as exc:                                             # pragma: no cover
        print("quicklook failed:", exc)
    print(f"R2 done in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main(sys.argv[1].split(",") if len(sys.argv) > 1 else None)
