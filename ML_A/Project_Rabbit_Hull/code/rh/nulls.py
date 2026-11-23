"""Null models and planted data sets (numpy only).

gaussian_like        Gaussian surrogate with the mean and covariance of a data set (optionally matched exactly)
dirichlet_mixtures   convex combinations of given vertices with Dirichlet weights (a planted polytope)
layernorm            the LayerNorm map x -> gamma * (x - mean(x)) / std(x) + beta, applied to every row
"""
from __future__ import annotations

import numpy as np

__all__ = ["gaussian_like", "dirichlet_mixtures", "layernorm"]


def gaussian_like(X, n=None, seed=0, exact=False):
    """Samples from the Gaussian N(mean, cov) fitted to the rows of X. Returns a float32 array (n, d).

    Parameters
    ----------
    X : (N, d) data.  n : number of samples (default N).  seed : seed of the generator.
    exact : False (default): i.i.d. draws from N(mean(X), cov(X)), cov with the 1 / (N - 1) normalisation.
        True: the *sample* mean and the *sample* covariance of the output equal those of X exactly (up to
        rounding), so that every second-order statistic — the PCA spectrum in particular — is identical and
        only the higher-order structure differs. This is a Gaussian sample conditioned on its first two
        empirical moments; it needs n >= rank(cov) + 1 (always true for n = N).

    The covariance is never formed when d > N: the factor comes from the SVD of the centred data.
    """
    X = np.asarray(X)
    if X.ndim != 2:
        raise ValueError("X must be a 2-D array")
    N, d = X.shape
    if N < 2:
        raise ValueError("at least two rows are needed to fit a covariance")
    n = N if n is None else int(n)
    rng = np.random.default_rng(seed)
    mu = X.mean(0, dtype=np.float64)
    Xc = np.asarray(X, dtype=np.float64) - mu
    if d <= N:
        C = (Xc.T @ Xc) / (N - 1)
        lam, V = np.linalg.eigh(C)
        lam = np.maximum(lam, 0.0)
        keep = lam > lam.max() * 1e-12 if lam.max() > 0 else np.zeros_like(lam, dtype=bool)
        F = np.sqrt(lam[keep])[:, None] * V[:, keep].T          # (r, d): rows = sqrt(lambda) * eigenvector
    else:
        _, s, Vt = np.linalg.svd(Xc, full_matrices=False)
        keep = s > s[0] * 1e-12 if s[0] > 0 else np.zeros_like(s, dtype=bool)
        F = (s[keep] / np.sqrt(N - 1))[:, None] * Vt[keep]
    r = F.shape[0]
    G = rng.standard_normal((n, r))
    if exact:
        if n < r + 1:
            raise ValueError(f"exact=True needs n >= rank + 1 = {r + 1} samples")
        G = G - G.mean(0)
        Q, _ = np.linalg.qr(G)                                   # Q^T Q = I_r and the columns of Q sum to zero
        G = Q * np.sqrt(n - 1)                                   # sample covariance (1 / (n - 1)) is exactly I_r
    return (mu + G @ F).astype(np.float32)


def dirichlet_mixtures(V, n, alpha=1.0, seed=0, return_weights=False):
    """n convex combinations of the rows of V with Dirichlet(alpha, ..., alpha) weights (float64).

    alpha = 1 is the uniform distribution on the simplex of weights; alpha < 1 pushes the mass towards the
    vertices. ``seed`` may be an int or a numpy Generator.
    """
    V = np.asarray(V, dtype=np.float64)
    rng = seed if isinstance(seed, np.random.Generator) else np.random.default_rng(seed)
    W = rng.dirichlet(np.full(V.shape[0], float(alpha)), size=int(n))
    X = W @ V
    return (X, W) if return_weights else X


def layernorm(X, gamma=None, beta=None, eps=0.0):
    """LayerNorm applied to every row: gamma * (x - mean(x)) / sqrt(var(x) + eps) + beta (float64).

    With gamma = 1, beta = 0, eps = 0 the output lies on the sphere of radius sqrt(d) inside the hyperplane
    of zero-sum vectors; a general (gamma, beta) maps this sphere to an ellipsoid of dimension d - 2.
    """
    X = np.asarray(X, dtype=np.float64)
    U = X - X.mean(1, keepdims=True)
    U = U / np.sqrt(U.var(1, keepdims=True) + eps)
    if gamma is not None:
        U = U * np.asarray(gamma, dtype=np.float64)
    if beta is not None:
        U = U + np.asarray(beta, dtype=np.float64)
    return U
