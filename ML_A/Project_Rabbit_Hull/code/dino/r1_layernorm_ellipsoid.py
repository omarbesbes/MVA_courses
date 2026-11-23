"""R1 — the final LayerNorm puts every output token on an ellipsoid.

LayerNorm:  y = gamma * u + beta,  u = (x - mean(x)) / sqrt(var(x) + eps)   (statistics over the 768 coordinates
of the token). Hence 1^T u = 0 and ||u||^2 = 768 var/(var + eps): u lies on a sphere of dimension 766 and, if no
gamma_k vanishes, y lies on an ellipsoid E of dimension 766 that depends only on (gamma, beta).

Measured here on the 256,000 final-layer patch tokens of the 1000 statistics images (trained model):
  1. how exactly the tokens satisfy the two constraints, and the range of |gamma|;
  2. for 2000 pairs of tokens of the same image and 2000 pairs from different images: angle between the u's,
     chord length ||y - y'||, and how deep inside E the chord midpoint lies, in units of the half chord:
       depth_radial  distance from the midpoint to its radial projection (in u-space) on E  [the brief's measure]
       depth_exact   Euclidean distance from the midpoint to E (secular equation), <= depth_radial
  3. the pre-norm tokens are not on a sphere: coefficient of variation of their norm.
"""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import dino, save_json, summ  # noqa: E402

D = 768


def ellipsoid_distance(T, gamma, R, n_bisect=80):
    """Exact Euclidean distance from the points beta + T (rows of T = y - beta) to the ellipsoid
    E = {beta + gamma * u : ||u|| = R, sum(u) = 0}.

    min_z || G z - t ||^2  s.t. ||z|| = R, with u = Q z (Q an orthonormal basis of the hyperplane) and
    G = diag(gamma) Q. Stationarity: (H + mu I) z = G^T t with H = G^T G; the global minimiser is the root of
    ||z(mu)|| = R[i] in (-lambda_min, inf), found by bisection (vectorised over the rows of T; R per row).
    """
    one = np.ones((D, 1)) / np.sqrt(D)
    Q = np.linalg.svd(np.eye(D) - one @ one.T)[0][:, :D - 1]            # orthonormal basis of {sum u = 0}
    G = gamma[:, None] * Q
    lam, W = np.linalg.eigh(G.T @ G)
    C = (T @ G) @ W                                                      # coefficients of G^T t in the eigenbasis
    R = np.broadcast_to(np.asarray(R, dtype=np.float64), (T.shape[0],))
    lo = np.full(T.shape[0], -lam[0] * (1 - 1e-12))
    # upper bracket: ||z(mu)|| <= ||C|| / (lam_min + mu) -> below R as soon as mu > ||C||/R - lam_min
    hi = np.maximum(np.linalg.norm(C, axis=1) / R - lam[0], 0.0) + 1.0
    for _ in range(n_bisect):
        mid = 0.5 * (lo + hi)
        nz = np.sqrt(((C / (lam[None, :] + mid[:, None])) ** 2).sum(1))
        too_long = nz > R                                                # ||z|| decreases with mu
        lo = np.where(too_long, mid, lo)
        hi = np.where(too_long, hi, mid)
    mu = 0.5 * (lo + hi)
    Zc = C / (lam[None, :] + mu[:, None])
    Yp = (Zc @ W.T) @ G.T                                                # nearest point of E, minus beta
    return np.linalg.norm(Yp - T, axis=1), mu


def pair_stats(Y, Y2, gamma, beta):
    U, U2 = (Y - beta) / gamma, (Y2 - beta) / gamma
    nu, nu2 = np.linalg.norm(U, axis=1), np.linalg.norm(U2, axis=1)
    cos = (U * U2).sum(1) / (nu * nu2)
    angle = np.degrees(np.arccos(np.clip(cos, -1, 1)))
    chord = np.linalg.norm(Y - Y2, axis=1)
    M = 0.5 * (Y + Y2)
    Um = 0.5 * (U + U2)
    R = 0.5 * (nu + nu2)
    Up = Um * (R / np.linalg.norm(Um, axis=1))[:, None]
    depth_radial = np.linalg.norm(M - (gamma * Up + beta), axis=1)
    depth_exact, _ = ellipsoid_distance(M - beta, gamma, R)
    self_check, _ = ellipsoid_distance(Y - beta, gamma, nu)             # tokens themselves: must be ~0
    half = 0.5 * chord
    return {
        "angle_deg": summ(angle), "cosine_u": summ(cos), "chord": summ(chord),
        "cosine_y": summ((Y * Y2).sum(1) / (np.linalg.norm(Y, axis=1) * np.linalg.norm(Y2, axis=1))),
        "depth_radial": summ(depth_radial), "depth_exact": summ(depth_exact),
        "depth_radial_over_half_chord": summ(depth_radial / half),
        "depth_exact_over_half_chord": summ(depth_exact / half),
        "sphere_formula_tan_quarter_angle": summ(np.tan(np.radians(angle) / 4)),
        "u_space_depth_over_half_chord": summ((R - np.linalg.norm(Um, axis=1)) / (0.5 * np.linalg.norm(U - U2, axis=1))),
        "selfcheck_token_distance_to_ellipsoid_max": float(self_check.max()),
        "exact_le_radial_all": bool((depth_exact <= depth_radial * (1 + 1e-9) + 1e-9).all()),
        "min_depth_exact_over_half_chord": float((depth_exact / half).min()),
    }


def main():
    t0 = time.time()
    model = dino.load_model(True)
    gamma, beta, eps = dino.final_norm_params(model)
    post = dino.load_features("trained", "postnorm")
    pre = dino.load_features("trained", "prenorm")
    n_img = post.shape[0]

    # ---- 1. constraints, all tokens
    mean_u, var_u, norm_u, norm_pre, std_pre, norm_post, ln_err = [], [], [], [], [], [], 0.0
    for b in range(0, n_img, 50):
        y = np.asarray(post[b:b + 50], dtype=np.float64).reshape(-1, D)
        x = np.asarray(pre[b:b + 50], dtype=np.float64).reshape(-1, D)
        u = (y - beta) / gamma
        mean_u.append(u.mean(1))
        var_u.append(u.var(1))
        norm_u.append(np.linalg.norm(u, axis=1) / np.sqrt(D))
        norm_pre.append(np.linalg.norm(x, axis=1))
        std_pre.append(x.std(1))
        norm_post.append(np.linalg.norm(y, axis=1))
        y_ref = gamma * (x - x.mean(1, keepdims=True)) / np.sqrt(x.var(1, keepdims=True) + eps) + beta
        ln_err = max(ln_err, float(np.abs(y_ref - y).max()))
    mean_u, var_u, norm_u = map(np.concatenate, (mean_u, var_u, norm_u))
    norm_pre, std_pre, norm_post = map(np.concatenate, (norm_pre, std_pre, norm_post))
    ag = np.abs(gamma)
    constraints = {
        "n_tokens": int(mean_u.size),
        "max_abs_mean_u": float(np.abs(mean_u).max()),
        "max_abs_var_u_minus_1": float(np.abs(var_u - 1).max()),
        "norm_u_over_sqrt_d": summ(norm_u, 8),
        "norm_u_over_sqrt_d_spread_max_minus_min": float(norm_u.max() - norm_u.min()),
        "layernorm_recomputed_from_prenorm_max_abs_err": ln_err,
        "note": "u = (y - beta)/gamma from float32 tokens, computed in float64; var is the population variance "
                "over the 768 coordinates; eps = %g makes var(u) = var/(var+eps) slightly below 1" % eps,
    }
    gamma_stats = {"abs_min": float(ag.min()), "abs_median": float(np.median(ag)), "abs_max": float(ag.max()),
                   "abs_q01": float(np.quantile(ag, 0.01)), "abs_q99": float(np.quantile(ag, 0.99)),
                   "n_negative": int((gamma < 0).sum()), "n_abs_below_0.05": int((ag < 0.05).sum()),
                   "axis_ratio_max_over_min": float(ag.max() / ag.min()),
                   "beta_norm": float(np.linalg.norm(beta)), "beta_abs_max": float(np.abs(beta).max()),
                   "eps": eps}

    # ---- 2. chords
    rng = np.random.default_rng(0)
    n_pairs = 2000
    img = rng.integers(n_img, size=n_pairs)
    p1 = rng.integers(256, size=n_pairs)
    p2 = (p1 + rng.integers(1, 256, size=n_pairs)) % 256                 # a different position
    img_a = rng.integers(n_img, size=n_pairs)
    img_b = (img_a + rng.integers(1, n_img, size=n_pairs)) % n_img       # a different image
    q1, q2 = rng.integers(256, size=n_pairs), rng.integers(256, size=n_pairs)

    def take(ii, pp):
        return np.stack([np.asarray(post[i, p], dtype=np.float64) for i, p in zip(ii, pp)])

    pairs = {"within_image": pair_stats(take(img, p1), take(img, p2), gamma, beta),
             "across_images": pair_stats(take(img_a, q1), take(img_b, q2), gamma, beta)}

    # ---- 3. pre-norm tokens
    prenorm = {"norm": summ(norm_pre), "norm_cv": float(norm_pre.std() / norm_pre.mean()),
               "per_token_std": summ(std_pre), "per_token_std_cv": float(std_pre.std() / std_pre.mean()),
               "postnorm_norm": summ(norm_post), "postnorm_norm_cv": float(norm_post.std() / norm_post.mean())}

    out = {"experiment": "R1 LayerNorm ellipsoid", "data": "trained model, final-layer patch tokens, 1000 Imagenette "
           "val images x 256 tokens", "constraints": constraints, "gamma": gamma_stats, "pairs": pairs,
           "pairs_design": "2000 pairs (image, two distinct positions) and 2000 pairs (two distinct images, any "
                           "positions), numpy default_rng(0)",
           "prenorm": prenorm,
           "definitions": {
               "depth_radial": "||m - (gamma*u_p + beta)||, m = chord midpoint, u_p = midpoint of the two u's "
                               "rescaled to the mean of their norms",
               "depth_exact": "min over the ellipsoid {gamma*u+beta: ||u|| = R, sum u = 0} of the Euclidean "
                              "distance to m (secular equation, bisection)",
               "ratios": "depth divided by half the chord length ||y - y'||/2; on a sphere this is tan(angle/4)"}}
    save_json("r1_layernorm_ellipsoid", out, t0)
    c, g = constraints, gamma_stats
    print(f"max|mean u| = {c['max_abs_mean_u']:.2e}, max|var u - 1| = {c['max_abs_var_u_minus_1']:.2e}, "
          f"||u||/sqrt(d) in [{c['norm_u_over_sqrt_d']['min']:.6f}, {c['norm_u_over_sqrt_d']['max']:.6f}]")
    print(f"|gamma|: min {g['abs_min']:.3f}, median {g['abs_median']:.3f}, max {g['abs_max']:.3f}")
    for k, v in pairs.items():
        print(f"{k}: angle {v['angle_deg']['mean']:.1f} deg, chord {v['chord']['mean']:.1f}, depth/half-chord "
              f"radial {v['depth_radial_over_half_chord']['mean']:.3f} "
              f"(q25 {v['depth_radial_over_half_chord']['q25']:.3f}, q75 {v['depth_radial_over_half_chord']['q75']:.3f}), "
              f"exact {v['depth_exact_over_half_chord']['mean']:.3f} (min {v['min_depth_exact_over_half_chord']:.3f}); "
              f"self-check {v['selfcheck_token_distance_to_ellipsoid_max']:.1e}")
    print(f"pre-norm norm CV = {prenorm['norm_cv']:.3f} (post-norm: {prenorm['postnorm_norm_cv']:.3f})")


if __name__ == "__main__":
    main()
