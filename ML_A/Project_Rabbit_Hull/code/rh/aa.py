"""Archetypal analysis with its two natural baselines, k-means and PCA (numpy only).

Archetypal analysis (Cutler & Breiman, 1994) factorises a data matrix X (N x d) as

    X  ~  A B X,      A in R^{N x K}, B in R^{K x N},  rows of A and of B on the probability simplex.

The K archetypes Z = B X are convex combinations of data points, and every point is reconstructed as a
convex combination of the archetypes. Two facts frame every number produced here:

* a k-means solution is a feasible point of this problem (A one-hot, B = cluster averaging), so the optimum
  satisfies AA(K) <= k-means(K);
* the reconstructions A Z live in the affine hull of K points, a subspace of dimension at most K - 1, so
  AA(K) >= PCA(K - 1), the error of the best (K - 1)-dimensional affine subspace.

All errors are reported as FVU, the fraction of variance unexplained: ||X - Xhat||_F^2 / ||X - mean(X)||_F^2.
"""
from __future__ import annotations

import numpy as np

__all__ = ["project_simplex", "archetypal_analysis", "kmeans", "pca_fvu", "fvu", "simplex_codes"]


# --------------------------------------------------------------------------------------------------------------
# basic tools
# --------------------------------------------------------------------------------------------------------------
def project_simplex(V):
    """Euclidean projection of every row of V onto the probability simplex {z >= 0, sum z = 1}.

    Sort-based algorithm (Held et al. 1974; Duchi et al. 2008), vectorised over rows.
    """
    V = np.asarray(V)
    one_d = V.ndim == 1
    if one_d:
        V = V[None, :]
    n, m = V.shape
    U = -np.sort(-V, axis=1)                       # descending
    css = np.cumsum(U, axis=1) - 1.0
    k = np.arange(1, m + 1, dtype=V.dtype)
    cond = U - css / k > 0
    rho = m - 1 - np.argmax(cond[:, ::-1], axis=1)  # last index where the condition holds
    theta = css[np.arange(n), rho] / (rho + 1.0)
    out = np.maximum(V - theta[:, None], 0.0)
    return out[0] if one_d else out


def fvu(X, Xhat):
    """Fraction of variance unexplained: ||X - Xhat||_F^2 / ||X - mean(X)||_F^2."""
    X = np.asarray(X, dtype=np.float64)
    Xhat = np.asarray(Xhat, dtype=np.float64)
    sst = float(((X - X.mean(0)) ** 2).sum())
    return float(((X - Xhat) ** 2).sum()) / sst


def pca_fvu(X, r):
    """FVU of the best r-dimensional affine subspace (mean + top-r principal directions).

    r = 0 gives 1.0. A vector of ranks returns a vector of errors (one SVD).
    """
    X = np.asarray(X, dtype=np.float64)
    s = np.linalg.svd(X - X.mean(0), compute_uv=False)
    e = s ** 2
    tot = e.sum()
    tail = np.concatenate([[tot], tot - np.cumsum(e)])    # tail[r] = energy outside the top r directions
    tail = np.maximum(tail, 0.0) / tot
    r_arr = np.minimum(np.atleast_1d(r), len(e))
    out = tail[r_arr]
    return float(out[0]) if np.ndim(r) == 0 else out


def _reduce(X):
    """Centre X and, when d > N, express its rows in an orthonormal basis of their span (exact isometry)."""
    Xc = X - X.mean(0, keepdims=True)
    N, d = Xc.shape
    if d > N:
        U, s, _ = np.linalg.svd(Xc, full_matrices=False)
        keep = s > s[0] * 1e-12 if s[0] > 0 else np.ones_like(s, dtype=bool)
        Xc = U[:, keep] * s[keep]
    return np.ascontiguousarray(Xc)


# --------------------------------------------------------------------------------------------------------------
# k-means
# --------------------------------------------------------------------------------------------------------------
def _sqdist(X, C, x2=None):
    if x2 is None:
        x2 = (X ** 2).sum(1)
    d2 = x2[:, None] - 2.0 * (X @ C.T) + (C ** 2).sum(1)[None, :]
    return np.maximum(d2, 0.0)


def _kmeanspp(X, K, rng, x2):
    N = X.shape[0]
    centers = np.empty((K, X.shape[1]), dtype=X.dtype)
    centers[0] = X[rng.integers(N)]
    d2 = _sqdist(X, centers[:1], x2)[:, 0]
    for k in range(1, K):
        tot = d2.sum()
        if not np.isfinite(tot) or tot <= 0:
            idx = rng.integers(N)
        else:
            idx = min(int(np.searchsorted(np.cumsum(d2), rng.random() * tot)), N - 1)
        centers[k] = X[idx]
        d2 = np.minimum(d2, _sqdist(X, centers[k:k + 1], x2)[:, 0])
    return centers


def kmeans(X, K, n_restarts=3, seed=0, n_iter=100, tol=1e-7):
    """Lloyd's algorithm with k-means++ initialisation.

    Returns a dict with ``labels`` (N,), ``centers`` (K, d, in the coordinates of X), ``fvu`` and ``inertia``.
    """
    X0 = np.asarray(X)
    dtype = np.float32 if X0.dtype == np.float32 else np.float64
    X0 = X0.astype(dtype, copy=False)
    mean = X0.mean(0, keepdims=True)
    Xc = X0 - mean
    N = Xc.shape[0]
    K = int(min(K, N))
    x2 = (Xc ** 2).sum(1)
    sst = float(x2.sum(dtype=np.float64))
    rng = np.random.default_rng(seed)
    best = None
    for _ in range(max(1, n_restarts)):
        C = _kmeanspp(Xc, K, rng, x2)
        prev = np.inf
        labels = np.zeros(N, dtype=np.int64)
        for _it in range(n_iter):
            d2 = _sqdist(Xc, C, x2)
            labels = d2.argmin(1)
            inertia = float(d2[np.arange(N), labels].sum(dtype=np.float64))
            counts = np.bincount(labels, minlength=K)
            sums = np.zeros_like(C, dtype=np.float64)
            np.add.at(sums, labels, Xc)
            nz = counts > 0
            C = C.copy()
            C[nz] = (sums[nz] / counts[nz, None]).astype(dtype)
            if (~nz).any():                           # re-seed empty clusters on the worst-fitted points
                far = np.argsort(-d2[np.arange(N), labels])[: int((~nz).sum())]
                C[~nz] = Xc[far]
                prev = np.inf
                continue
            if prev - inertia <= tol * max(sst, 1e-300):
                break
            prev = inertia
        d2 = _sqdist(Xc, C, x2)
        labels = d2.argmin(1)
        inertia = float(d2[np.arange(N), labels].sum(dtype=np.float64))
        if best is None or inertia < best["inertia"]:
            best = {"labels": labels, "centers": C + mean, "inertia": inertia}
    best["fvu"] = best["inertia"] / sst if sst > 0 else 0.0
    return best


# --------------------------------------------------------------------------------------------------------------
# archetypal analysis
# --------------------------------------------------------------------------------------------------------------
def _lam_max(C, n_power=30):
    """Largest eigenvalue of a symmetric PSD matrix (power iterations, cheap and safe as an upper estimate)."""
    K = C.shape[0]
    if K <= 64:
        return float(np.linalg.eigvalsh(C.astype(np.float64))[-1])
    v = np.ones(K, dtype=np.float64) / np.sqrt(K)
    Cd = C.astype(np.float64, copy=False)
    lam = 0.0
    for _ in range(n_power):
        w = Cd @ v
        lam = float(np.linalg.norm(w))
        if lam == 0:
            return 0.0
        v = w / lam
    return lam * 1.05


def _cost_A(A, C, XZt, sst):
    """||X - A Z||_F^2 from C = Z Z^T and XZt = X Z^T."""
    return sst - 2.0 * float((A * XZt).sum(dtype=np.float64)) + float(((A @ C) * A).sum(dtype=np.float64))


def simplex_codes(X, Z, A0=None, n_iter=200, tol=1e-9):
    """Best convex codes of the rows of X on the rows of Z: min_A ||X - A Z||_F^2, rows of A on the simplex.

    Accelerated projected gradient (FISTA with function restart). Returns (A, cost).
    """
    X = np.asarray(X)
    Z = np.asarray(Z, dtype=X.dtype)
    C = Z @ Z.T
    XZt = X @ Z.T
    sst = float((X.astype(np.float64) ** 2).sum())
    K = Z.shape[0]
    A = np.full((X.shape[0], K), 1.0 / K, dtype=X.dtype) if A0 is None else A0.astype(X.dtype, copy=True)
    A, cost = _update_A(A, C, XZt, sst, n_inner=n_iter, tol=tol)
    return A, cost


def _update_A(A, C, XZt, sst, n_inner=10, tol=0.0):
    """A few FISTA steps on the convex sub-problem in A; never returns a worse point than it was given."""
    L = _lam_max(C)
    if L <= 0:
        return A, _cost_A(A, C, XZt, sst)
    step = 1.0 / L                     # the gradient is 2 (A C - XZt), with Lipschitz constant 2 L
    cost0 = _cost_A(A, C, XZt, sst)
    best_A, best_cost = A, cost0
    Y, t = A, 1.0
    prev_cost = cost0
    for _ in range(n_inner):
        A_new = project_simplex(Y - step * (Y @ C - XZt))
        cost = _cost_A(A_new, C, XZt, sst)
        if cost > prev_cost:           # function restart: fall back to a plain projected-gradient step
            A_new = project_simplex(A - step * (A @ C - XZt))
            cost = _cost_A(A_new, C, XZt, sst)
            t = 1.0
        t_new = 0.5 * (1.0 + np.sqrt(1.0 + 4.0 * t * t))
        Y = A_new + ((t - 1.0) / t_new) * (A_new - A)
        A, t = A_new, t_new
        if cost < best_cost:
            improved = best_cost - cost
            best_A, best_cost = A, cost
            if tol > 0 and improved <= tol * max(sst, 1e-300):
                break
        prev_cost = cost
    return best_A, best_cost


def _furthest_sum(X, K, rng, x2=None):
    """FurthestSum initialisation (Morup & Hansen, 2012): K mutually distant data points."""
    N = X.shape[0]
    if x2 is None:
        x2 = (X ** 2).sum(1)
    first = int(rng.integers(N))
    chosen = [first]
    sum_d = np.sqrt(_sqdist(X, X[first:first + 1], x2)[:, 0])
    for _ in range(K - 1):
        s = sum_d.copy()
        s[chosen] = -np.inf
        nxt = int(np.argmax(s))
        chosen.append(nxt)
        sum_d += np.sqrt(_sqdist(X, X[nxt:nxt + 1], x2)[:, 0])
    # the first point was random: replace it by the point furthest from the others
    sum_d -= np.sqrt(_sqdist(X, X[first:first + 1], x2)[:, 0])
    s = sum_d.copy()
    s[chosen[1:]] = -np.inf
    chosen[0] = int(np.argmax(s))
    return np.array(chosen)


def _aa_run(X, K, A, B, n_iter, tol, n_inner, sst):
    """Alternating minimisation from (A, B). Monotone: the returned cost is <= the cost of the input."""
    dtype = X.dtype
    Z = B @ X
    C = Z @ Z.T
    XZt = X @ Z.T
    cost = _cost_A(A, C, XZt, sst)
    history = [cost / sst]
    mu = None
    for it in range(n_iter):
        cost_start = cost
        # ---- codes A (convex sub-problem, accelerated projected gradient, warm start)
        A, cost = _update_A(A, C, XZt, sst, n_inner=n_inner)
        # ---- archetypes through B (projected gradient with an adaptive step, as in PCHA)
        AtA = A.T @ A
        AtX = A.T @ X
        for _b in range(2):
            G = (AtA @ Z - AtX) @ X.T                                      # half the gradient in B
            gnorm2 = float((G.astype(np.float64) ** 2).sum())
            if gnorm2 == 0:
                break
            if mu is None:                                                # first guess: 1 / Lipschitz bound
                x_top = _lam_max(X.T @ X) if X.shape[1] <= X.shape[0] else _lam_max(X @ X.T)
                mu = 1.0 / max(_lam_max(AtA) * x_top, 1e-300)
            accepted = False
            for _ls in range(40):
                B_new = project_simplex(B - mu * G).astype(dtype, copy=False)
                Z_new = B_new @ X
                cost_new = (sst - 2.0 * float((Z_new * AtX).sum(dtype=np.float64))
                            + float(((AtA @ Z_new) * Z_new).sum(dtype=np.float64)))
                if cost_new <= cost:
                    B, Z, cost = B_new, Z_new, cost_new
                    mu *= 1.5
                    accepted = True
                    break
                mu *= 0.5
            if not accepted:
                break
        C = Z @ Z.T
        XZt = X @ Z.T
        history.append(cost / sst)
        if it >= 10 and cost_start - cost <= tol * sst:
            break
    # final polish of the codes
    A, cost = _update_A(A, C, XZt, sst, n_inner=5 * n_inner)
    history.append(cost / sst)
    return A, B, cost, history


def archetypal_analysis(X, K, n_iter=500, n_restarts=3, seed=0, tol=1e-7, init_from_kmeans=True,
                        n_inner=10, dtype=None, verbose=False, kmeans_restarts=3):
    """Archetypal analysis: minimise ||X - A B X||_F^2 with the rows of A and B on the simplex.

    Parameters
    ----------
    X : (N, d) array. K : number of archetypes.
    n_restarts : number of initialisations. With ``init_from_kmeans`` the first one starts from the k-means
        solution (A one-hot, B = cluster averaging); since the iterations never increase the objective, the
        returned error is then <= the k-means error. The second starts from FurthestSum, the others from random
        data points.
    dtype : float64 by default; pass np.float32 for large problems.
    kmeans_restarts : number of k-means++ initialisations of the k-means run that provides the first start
        (its best solution is used, and its error is returned as ``kmeans_fvu``).

    Returns
    -------
    dict with ``A`` (N, K), ``B`` (K, N), ``Z`` = B X (archetypes, in the coordinates of X), ``fvu``
    (recomputed at the end from the residual X - A Z itself, hence >= 0), ``history`` (FVU per outer iteration
    of the best run), ``kmeans_fvu`` (if the k-means start was used), ``fvu_restarts``.

    Notes
    -----
    The problem is invariant by translation (rows sum to one), so X is centred; when d > N the rows are
    expressed in an orthonormal basis of their span, which is the Gram-matrix formulation in exact form.
    """
    X0 = np.asarray(X)
    if dtype is None:
        dtype = np.float64
    Xr = _reduce(X0.astype(np.float64, copy=False)).astype(dtype, copy=False)
    N = Xr.shape[0]
    K = int(min(K, N))
    x2 = (Xr.astype(np.float64) ** 2).sum(1)
    sst = float(x2.sum())
    rng = np.random.default_rng(seed)
    best = None
    fvus = []
    km_fvu = None
    for r in range(max(1, n_restarts)):
        if r == 0 and init_from_kmeans:
            km = kmeans(Xr, K, n_restarts=kmeans_restarts, seed=int(rng.integers(2 ** 31)))
            km_fvu = km["fvu"]
            labels = km["labels"]
            A0 = np.zeros((N, K), dtype=dtype)
            A0[np.arange(N), labels] = 1.0
            counts = np.maximum(np.bincount(labels, minlength=K), 1)
            B0 = (A0 / counts[None, :]).T.copy()
        else:
            if (r == 1 and init_from_kmeans) or (r == 0 and not init_from_kmeans):
                idx = _furthest_sum(Xr, K, rng, x2.astype(dtype))
            else:
                idx = rng.choice(N, size=K, replace=False)
            B0 = np.zeros((K, N), dtype=dtype)
            B0[np.arange(K), idx] = 1.0
            Z0 = B0 @ Xr
            A0 = np.full((N, K), 1.0 / K, dtype=dtype)
            A0, _ = _update_A(A0, Z0 @ Z0.T, Xr @ Z0.T, sst, n_inner=50)
        A, B, cost, hist = _aa_run(Xr, K, A0, B0, n_iter, tol, n_inner, sst)
        fvus.append(cost / sst)
        if verbose:
            print(f"  AA restart {r}: fvu = {cost / sst:.6f} after {len(hist) - 2} iterations")
        if best is None or cost < best["cost"]:
            best = {"A": A, "B": B, "cost": cost, "history": hist}
    # the costs above come from the expansion sst - 2 <A, X Z^T> + <A Z Z^T, A>, which loses digits when the
    # fit is nearly exact; the reported error is the residual itself
    resid = Xr - best["A"] @ (best["B"] @ Xr)
    cost = float((resid.astype(np.float64) ** 2).sum())
    out = {
        "A": best["A"], "B": best["B"],
        "Z": best["B"].astype(np.float64) @ X0.astype(np.float64),
        "fvu": cost / sst if sst > 0 else 0.0,
        "history": best["history"], "fvu_restarts": fvus,
    }
    if km_fvu is not None:
        out["kmeans_fvu"] = km_fvu
    return out
