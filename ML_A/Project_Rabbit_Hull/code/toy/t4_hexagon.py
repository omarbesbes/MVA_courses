"""T4 - the hexagon: one convex body, two generative stories, and a gap in the non-identifiability proof.

(a) the regular hexagon H (circumradius 1) equals Z = S_0 + S_60 + S_120 (unit segments centred at 0) and
    T + (-T) (T equilateral, unit side, centred): vertices and support functions are compared.
(b) two point clouds with support H: sparse linear codes and block-convex codes.
(c) for X = T and s = h_Q (Q = [-eps e, eps e] inside T), 0 <= s <= h_X but f = h_X - s is not sublinear.
Writes results/t4_hexagon.json and results/t4_hexagon.npz.
"""
import json, os
import numpy as np
from scipy.spatial import ConvexHull

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")
rng = np.random.default_rng(4)


def hull_vertices(P):
    h = ConvexHull(P)
    V = P[h.vertices]
    ang = np.mod(np.arctan2(V[:, 1], V[:, 0]) + 1e-9, 2 * np.pi)       # vertex at angle 0 first
    return V[np.argsort(ang)]


def support(V, U):
    return (U @ V.T).max(1)


# ---------------- (a) ----------------
ang6 = np.deg2rad(np.arange(0, 360, 60))
H = np.c_[np.cos(ang6), np.sin(ang6)]
G = np.array([[np.cos(a), np.sin(a)] for a in np.deg2rad([0, 60, 120])])        # unit generators
signs = np.array(np.meshgrid([-.5, .5], [-.5, .5], [-.5, .5])).reshape(3, -1).T  # 8 corners of the cube
VZ = hull_vertices(signs @ G)
angT = np.deg2rad([90, 210, 330])
T = np.c_[np.cos(angT), np.sin(angT)] / np.sqrt(3)                               # unit side, centroid 0
VTT = hull_vertices((T[:, None, :] - T[None, :, :]).reshape(-1, 2))
th = np.linspace(0, 2 * np.pi, 720, endpoint=False)
U = np.c_[np.cos(th), np.sin(th)]
hH, hZ, hTT = support(H, U), support(VZ, U), support(VTT, U)
# Minkowski-sum support functions add: check this too, from the generators themselves
hZ_sum = sum(0.5 * np.abs(U @ g) for g in G)
hTT_sum = support(T, U) + support(-T, U)
a = {
    "n_vertices": {"Z": len(VZ), "T_plus_minusT": len(VTT)},
    "max_vertex_err_Z": float(np.abs(VZ - H).max()),
    "max_vertex_err_TT": float(np.abs(VTT - H).max()),
    "max_support_err_Z": float(max(np.abs(hZ - hH).max(), np.abs(hZ_sum - hH).max())),
    "max_support_err_TT": float(max(np.abs(hTT - hH).max(), np.abs(hTT_sum - hH).max())),
    "n_directions": 720,
}
assert len(VZ) == 6 and len(VTT) == 6 and a["max_vertex_err_Z"] < 1e-12 and a["max_vertex_err_TT"] < 1e-12
assert a["max_support_err_Z"] < 1e-12 and a["max_support_err_TT"] < 1e-12

# ---------------- (b) ----------------
n = 4000
tk = rng.uniform(-.5, .5, size=(n, 3)) * (rng.random((n, 3)) >= 0.7)
X_lin = (tk @ G).astype(np.float32)
wp = rng.dirichlet(np.full(3, 0.3), size=n)
wq = rng.dirichlet(np.full(3, 0.3), size=n)
X_blk = (wp @ T + wq @ (-T)).astype(np.float32)
in_hex = lambda X: float((X @ U.T - hH[None, :]).max())                         # <= 0 when inside H
b = {"n": n, "p_zero": 0.7, "dirichlet_alpha": 0.3,
     "max_excess_over_support_lin": in_hex(X_lin), "max_excess_over_support_blk": in_hex(X_blk),
     "frac_exact_zero_lin": float(np.mean(np.all(tk == 0, 1))),
     "cov_lin": np.cov(X_lin.T).tolist(), "cov_blk": np.cov(X_blk.T).tolist()}

# ---------------- (c) ----------------
eps = 0.1
e = np.array([1.0, 0.0])
inr = 1 / (2 * np.sqrt(3))
th_f = np.linspace(0, 2 * np.pi, 3600, endpoint=False)
Uf = np.c_[np.cos(th_f), np.sin(th_f)]
hX = lambda W: support(T, np.atleast_2d(W))
s = lambda W: eps * np.abs(np.atleast_2d(W) @ e)
f = lambda W: hX(W) - s(W)
min_s, min_gap = float(s(Uf).min()), float((hX(Uf) - s(Uf)).min())
u = np.array([np.cos(np.pi / 3), np.sin(np.pi / 3)])
v = np.array([np.cos(2 * np.pi / 3), np.sin(2 * np.pi / 3)])
fu, fv, fuv = float(f(u)[0]), float(f(v)[0]), float(f(u + v)[0])
# grid search over pairs of unit directions for the largest violation f(u+v) - f(u) - f(v)
A = Uf[::10]
Sm = A[:, None, :] + A[None, :, :]
viol = f(Sm.reshape(-1, 2)).reshape(len(A), len(A)) - f(A)[:, None] - f(A)[None, :]
iu = np.unravel_index(np.argmax(viol), viol.shape)
c = {"eps": eps, "e": e.tolist(), "inradius_T": inr, "Q_inside_T": bool(eps < inr),
     "min_s_on_grid": min_s, "min_hX_minus_s_on_grid": min_gap, "n_grid": len(th_f),
     "u": u.tolist(), "v": v.tolist(), "f_u": fu, "f_v": fv, "f_u_plus_v": fuv,
     "violation": fuv - fu - fv, "grid_max_violation": float(viol.max()),
     "grid_argmax_deg": [float(np.rad2deg(th_f[::10][iu[0]])), float(np.rad2deg(th_f[::10][iu[1]]))],
     "frac_pairs_violating": float(np.mean(viol > 1e-12))}
assert min_s >= 0 and min_gap >= -1e-12 and c["violation"] > 0

out = {"a": a, "b": b, "c": c}
with open(os.path.join(RES, "t4_hexagon.json"), "w") as fh:
    json.dump(out, fh, indent=1)
np.savez_compressed(os.path.join(RES, "t4_hexagon.npz"), X_lin=X_lin, X_blk=X_blk, H=H, G=G, T=T,
                    VZ=VZ, VTT=VTT, t_lin=tk.astype(np.float32), w_p=wp.astype(np.float32),
                    w_q=wq.astype(np.float32))
print("(a) vertex errors Z %.1e  T-T %.1e ; support errors Z %.1e  T-T %.1e"
      % (a["max_vertex_err_Z"], a["max_vertex_err_TT"], a["max_support_err_Z"], a["max_support_err_TT"]))
print("(b) max excess over h_H: lin %.2e  blk %.2e ; P(x=0) lin %.3f"
      % (b["max_excess_over_support_lin"], b["max_excess_over_support_blk"], b["frac_exact_zero_lin"]))
print("(c) eps=%.2f e=%s: min s=%.3f, min(h_X - s)=%.4f ; f(u)=%.4f f(v)=%.4f f(u+v)=%.4f -> violation %.4f"
      % (eps, e, min_s, min_gap, fu, fv, fuv, c["violation"]))
print("    grid: max violation %.4f at (%.0f, %.0f) deg; share of violating pairs %.3f"
      % (c["grid_max_violation"], *c["grid_argmax_deg"], c["frac_pairs_violating"]))
