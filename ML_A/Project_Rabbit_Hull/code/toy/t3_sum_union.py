"""T3 - sum or union? Does a block-diagonal co-activation matrix A^T A reveal Minkowski tiles?

(U) union of 4 well-separated triangles in R^20 (each point in one triangle, Dirichlet(1) weights);
(S) Minkowski sum T1 + T2 of two triangles spanning independent planes (Dirichlet(1) weights on each).
Archetypal analysis with K = number of extreme points (12 for U, 9 for S) and K = 30; co-activation
C = A^T A, normalised C_ij / sqrt(C_ii C_jj), average-linkage ordering, block-diagonality index.
Writes results/t3_sum_union.json and results/t3_sum_union.npz.
"""
import json, os, sys, time
import numpy as np
from scipy.cluster.hierarchy import linkage, leaves_list, fcluster
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import squareform

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from rh.aa import archetypal_analysis  # noqa: E402

RES = os.path.join(HERE, "..", "results")
rng = np.random.default_rng(3)
D, N = 20, 4000
R, _ = np.linalg.qr(rng.standard_normal((D, D)))           # random rotation


def triangle(rng):
    """Equilateral triangle of circumradius 1 in the plane of the first two coordinates, random rotation."""
    a = rng.uniform(0, 2 * np.pi) + np.array([0, 2 * np.pi / 3, 4 * np.pi / 3])
    return np.c_[np.cos(a), np.sin(a)]


# (U) union: 4 triangles, each in its own random plane, centres 8 apart
U_vert, U_lab, XU = [], [], []
centres = 8.0 * np.linalg.qr(rng.standard_normal((D, 4)))[0].T / np.sqrt(2)  # pairwise distance 8
for g in range(4):
    B = np.linalg.qr(rng.standard_normal((D, 2)))[0]
    V = centres[g] + triangle(rng) @ B.T
    n_g = N // 4
    XU.append(rng.dirichlet(np.ones(3), size=n_g) @ V)
    U_vert.append(V)
    U_lab += [g] * n_g
XU, U_vert, U_lab = np.vstack(XU), np.vstack(U_vert), np.array(U_lab)

# (S) sum: T1 in span(e1, e2), T2 in span(e3, e4), then the random rotation
T1 = np.zeros((3, D)); T1[:, :2] = triangle(rng)
T2 = np.zeros((3, D)); T2[:, 2:4] = 1.3 * triangle(rng)
T1, T2 = T1 @ R.T, T2 @ R.T
Wp = rng.dirichlet(np.ones(3), size=N)
Wq = rng.dirichlet(np.ones(3), size=N)
XS = Wp @ T1 + Wq @ T2
S_vert = (T1[:, None, :] + T2[None, :, :]).reshape(9, D)    # index 3 i + j  <->  a_i + b_j


def normalise(C):
    s = np.sqrt(np.clip(np.diag(C), 1e-300, None))
    return C / s[:, None] / s[None, :]


def cluster(Cn, n_groups):
    Dm = np.clip(1.0 - Cn, 0, None)
    np.fill_diagonal(Dm, 0.0)
    Z = linkage(squareform(Dm, checks=False), method="average", optimal_ordering=True)
    order = leaves_list(Z)
    out = {}
    for g in n_groups:
        lab = fcluster(Z, g, criterion="maxclust")
        same = lab[:, None] == lab[None, :]
        off = ~np.eye(len(lab), dtype=bool)
        share = float(Cn[same & off].sum() / Cn[off].sum())
        sizes = np.bincount(lab)[1:]
        K = len(lab)
        null = float((sizes * (sizes - 1)).sum() / (K * (K - 1)))   # share expected for unstructured C
        out[g] = {"share_in_blocks": share, "null_share": null, "sizes": sizes.tolist(), "labels": lab.tolist()}
    return order, out


def match(Z, V):
    Dm = np.linalg.norm(Z[:, None, :] - V[None, :, :], axis=2)
    r, c = linear_sum_assignment(Dm)
    return r, c, Dm


summary, arrays = {}, {}
t0 = time.time()
diamS = float(np.linalg.norm(S_vert[:, None] - S_vert[None], axis=2).max())
for name, X, Ktrue, groups, Vtrue in [("U", XU, 12, [4], U_vert), ("S", XS, 9, [2, 3], S_vert)]:
    for K in [Ktrue, 30]:
        aa = archetypal_analysis(X, K, n_restarts=3, seed=11, n_iter=1000)
        A, Z = aa["A"], aa["Z"]
        C = A.T @ A
        Cn = normalise(C)
        order, blocks = cluster(Cn, groups)
        key = f"{name}_K{K}"
        res = {"K": K, "fvu": float(aa["fvu"]), "blocks": {str(g): v for g, v in blocks.items()},
               "mean_offdiag_Cn": float(Cn[~np.eye(K, dtype=bool)].mean()),
               "frac_offdiag_Cn_above_0.1": float((Cn[~np.eye(K, dtype=bool)] > 0.1).mean())}
        dist_nearest = np.linalg.norm(Z[:, None] - Vtrue[None], axis=2).min(1)
        diam = float(np.linalg.norm(Vtrue[:, None] - Vtrue[None], axis=2).max())
        res["archetype_to_nearest_vertex_over_diam"] = {"max": float(dist_nearest.max() / diam),
                                                       "median": float(np.median(dist_nearest) / diam)}
        res["n_true_vertices_hit_within_2pct"] = int(
            (np.linalg.norm(Vtrue[:, None] - Z[None], axis=2).min(1) / diam < 0.02).sum())
        if name == "U":
            # does every archetype serve a single triangle? purity of the A-weights per archetype
            mass = np.stack([A[U_lab == g].sum(0) for g in range(4)])          # (4, K)
            res["archetype_purity_min"] = float((mass.max(0) / mass.sum(0)).min())
            # agreement of the K-cluster blocks with triangles (by archetype -> dominant triangle)
            dom = mass.argmax(0)
            lab = np.array(blocks[4]["labels"])
            agree = np.mean([(lab[i] == lab[j]) == (dom[i] == dom[j]) for i in range(K) for j in range(i + 1, K)])
            res["pairwise_agreement_blocks_vs_triangles"] = float(agree)
        if name == "S" and K == 9:
            r, c, Dm = match(Z, S_vert)
            perm = np.empty(9, dtype=int); perm[c] = r                    # perm[v] = archetype matched to vertex v
            res["matched_max_dist_over_diam"] = float(Dm[r, c].max() / diamS)
            Cm = C[np.ix_(perm, perm)] / N
            G1, G2 = Wp.T @ Wp / N, Wq.T @ Wq / N
            Kr = np.kron(G1, G2)
            Wtrue = (Wp[:, :, None] * Wq[:, None, :]).reshape(N, 9)      # product code w_i v_j
            Ctrue = Wtrue.T @ Wtrue / N
            res["kron_rel_err_AA"] = float(np.linalg.norm(Cm - Kr) / np.linalg.norm(Kr))
            res["kron_rel_err_true_product_code"] = float(np.linalg.norm(Ctrue - Kr) / np.linalg.norm(Kr))
            res["AA_vs_true_product_code_rel_err"] = float(np.linalg.norm(Cm - Ctrue) / np.linalg.norm(Ctrue))
            # codes are not unique (9 points in a 4-dim affine space): compare A with the product code itself
            res["mean_abs_code_diff"] = float(np.abs(A[:, perm] - Wtrue).sum(1).mean())
            arrays["S_kron"], arrays["S_C_matched"] = Kr, Cm
            Cn_m = normalise(Cm)
            # block index of the tile partition itself: archetypes a_i + b_j grouped by i (or by j)
            off = ~np.eye(9, dtype=bool)
            for tile, labt in [("by_T1_index", np.repeat(np.arange(3), 3)), ("by_T2_index", np.tile(np.arange(3), 3))]:
                same = labt[:, None] == labt[None, :]
                res[f"share_in_blocks_{tile}"] = float(Cn_m[same & off].sum() / Cn_m[off].sum())
            res["null_share_3x3"] = 6 * 3 / 72
        summary[key] = res
        arrays[f"{key}_Cn"], arrays[f"{key}_order"] = Cn.astype(np.float32), order
        print(key, json.dumps({k: v for k, v in res.items() if k != "blocks"}),
              {g: (round(v["share_in_blocks"], 3), round(v["null_share"], 3), v["sizes"]) for g, v in blocks.items()},
              f"[{time.time() - t0:.0f}s]", flush=True)

# 2-D PCA views for the figure
for name, X in [("U", XU), ("S", XS)]:
    Xc = X - X.mean(0)
    _, _, Vt = np.linalg.svd(Xc, full_matrices=False)
    arrays[f"{name}_pc2"] = (Xc @ Vt[:2].T).astype(np.float32)
    arrays[f"{name}_pc_var"] = (np.linalg.svd(Xc, compute_uv=False) ** 2 / (Xc ** 2).sum())[:6]
    summary[f"{name}_pca_variance_first6"] = arrays[f"{name}_pc_var"].tolist()
arrays["U_labels"] = U_lab
json.dump(summary, open(os.path.join(RES, "t3_sum_union.json"), "w"), indent=1)
np.savez_compressed(os.path.join(RES, "t3_sum_union.npz"), **arrays)
print(f"done in {time.time() - t0:.0f}s")
