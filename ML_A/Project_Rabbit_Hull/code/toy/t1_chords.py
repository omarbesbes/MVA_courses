"""T1 - chords leave the sample, not the support.

The chord test of the paper (Fig. 17, left) on four supports in R^d, three of them convex by construction:
simplex (uniform in a regular simplex), cube (uniform in [0,1]^d, a Minkowski sum of d segments), gauss
(standard Gaussian), sphere (uniform on S^{d-1}, the only non-convex support).
N = 20,000, d in {2,3,5,10,20,50,100}, 200 random pairs, k = 15 Euclidean neighbours; then N in {1e3,1e4,1e5}
at d = 20 for simplex and gauss.  Writes results/t1_chords.json and results/t1_chords.npz.
"""
import json, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from rh.interp import chord_test, knn_graph  # noqa: E402

RES = os.path.join(HERE, "..", "results")
SUPPORTS = ["simplex", "cube", "gauss", "sphere"]
DIMS = [2, 3, 5, 10, 20, 50, 100]
N0, P, K, NS = 20000, 200, 15, 101
NS_SCAN = [1000, 10000, 100000]


def regular_simplex(d):
    E = np.eye(d + 1) - 1.0 / (d + 1)                       # centred standard basis of R^{d+1}
    Q, _ = np.linalg.qr(E[:, :d])                           # orthonormal basis of the hyperplane sum = 0
    return E @ Q                                            # (d+1, d), all edges of length sqrt(2)


def sample(name, d, n, rng):
    if name == "simplex":
        return rng.dirichlet(np.ones(d + 1), size=n) @ regular_simplex(d)
    if name == "cube":
        return rng.random((n, d))
    if name == "gauss":
        return rng.standard_normal((n, d))
    if name == "sphere":
        Z = rng.standard_normal((n, d))
        return Z / np.linalg.norm(Z, axis=1, keepdims=True)
    raise ValueError(name)


def run(name, d, n, seed):
    rng = np.random.default_rng(seed)
    X = sample(name, d, n, rng)
    pairs = rng.choice(n, size=(P, 2), replace=True)
    pairs = pairs[pairs[:, 0] != pairs[:, 1]]
    G, idx, dist = knn_graph(X, k=K, metric="euclidean", return_knn=True)
    r = chord_test(X, pairs, n_steps=NS, graph=G)
    lin = r["lin"] / r["chord"][:, None]
    gra = r["graph"] / r["chord"][:, None]
    mid = (r["t"] >= 0.2) & (r["t"] <= 0.8)
    ok = np.isfinite(gra[:, 0])
    return {
        "lin_curve": lin.mean(0), "graph_curve": np.nanmean(gra, 0),
        "lin_mid": float(lin[:, NS // 2].mean()), "lin_mid_sd": float(lin[:, NS // 2].std()),
        "graph_mid60": float(np.nanmean(gra[:, mid])), "graph_mid": float(np.nanmean(gra[:, NS // 2])),
        "nn_over_chord": float(dist[:, 0].mean() / r["chord"].mean()),
        "pathlen_over_chord": float(np.nanmean(r["path_len"] / r["chord"])),
        "n_hops": float(np.nanmean(r["n_hops"])), "frac_connected": float(ok.mean()), "n_pairs": int(len(pairs)),
        "examples_lin": lin[:5], "examples_graph": gra[:5],
    }


t0 = time.time()
summ, curves = {}, {}
L = np.full((len(SUPPORTS), len(DIMS), NS), np.nan)
Gc = np.full_like(L, np.nan)
ex = {}
for a, s in enumerate(SUPPORTS):
    for b, d in enumerate(DIMS):
        o = run(s, d, N0, seed=1000 * a + d)
        L[a, b], Gc[a, b] = o.pop("lin_curve"), o.pop("graph_curve")
        el, eg = o.pop("examples_lin"), o.pop("examples_graph")
        if s == "simplex" and d in (2, 50):
            ex[f"ex_lin_simplex_d{d}"], ex[f"ex_graph_simplex_d{d}"] = el, eg
        summ[f"{s}_d{d}"] = o
        print(f"{s:8s} d={d:4d}  lin mid {o['lin_mid']:.3f}  graph mid60 {o['graph_mid60']:.3f}  "
              f"NN/chord {o['nn_over_chord']:.3f}  len/chord {o['pathlen_over_chord']:.2f}  hops {o['n_hops']:.1f}"
              f"  conn {o['frac_connected']:.2f}  [{time.time() - t0:.0f}s]", flush=True)

scan = {}
for s in ["simplex", "gauss"]:
    for n in NS_SCAN:
        o = run(s, 20, n, seed=77 + n)
        for k_ in ["lin_curve", "graph_curve", "examples_lin", "examples_graph"]:
            o.pop(k_)
        scan[f"{s}_N{n}"] = o
        print(f"scan {s:8s} d=20 N={n:6d}  lin mid {o['lin_mid']:.3f}  graph mid60 {o['graph_mid60']:.3f}  "
              f"NN/chord {o['nn_over_chord']:.3f}  [{time.time() - t0:.0f}s]", flush=True)
slopes = {}
for s in ["simplex", "gauss"]:
    y = [scan[f"{s}_N{n}"]["nn_over_chord"] for n in NS_SCAN]
    slopes[s] = {"loglog_slope_nn_over_chord_vs_N": float(np.polyfit(np.log(NS_SCAN), np.log(y), 1)[0]),
                 "expected_-1/d": -1 / 20,
                 "lin_mid": [scan[f"{s}_N{n}"]["lin_mid"] for n in NS_SCAN],
                 "graph_mid60": [scan[f"{s}_N{n}"]["graph_mid60"] for n in NS_SCAN]}
    print(s, slopes[s])

json.dump({"config": {"N": N0, "pairs": P, "k": K, "n_steps": NS, "metric": "euclidean", "dims": DIMS,
                      "supports": SUPPORTS, "N_scan": NS_SCAN},
           "by_support_dim": summ, "N_scan_d20": scan, "N_scaling": slopes},
          open(os.path.join(RES, "t1_chords.json"), "w"), indent=1)
np.savez_compressed(os.path.join(RES, "t1_chords.npz"), lin_curve=L, graph_curve=Gc, t=np.linspace(0, 1, NS),
                    dims=np.array(DIMS), supports=np.array(SUPPORTS), **ex)
print(f"done in {time.time() - t0:.0f}s")
