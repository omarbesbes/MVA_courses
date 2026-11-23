"""Tests of the shared numerical modules (rh.aa, rh.interp, rh.nulls).

Run with      python -m pytest code/tests -q
or directly   python code/tests/test_core.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import numpy as np

from rh.aa import archetypal_analysis, fvu, kmeans, pca_fvu, project_simplex, simplex_codes
from rh.interp import chord_test, graph_paths, knn_graph, knn_search, nearest_dist, resample_path
from rh.nulls import dirichlet_mixtures, gaussian_like, layernorm


def _brute_dist(Q, X):
    Q = np.asarray(Q, dtype=np.float64)
    X = np.asarray(X, dtype=np.float64)
    return np.sqrt(((Q[:, None, :] - X[None, :, :]) ** 2).sum(-1))


# --------------------------------------------------------------------------------------------------------------
# rh.aa
# --------------------------------------------------------------------------------------------------------------
def test_project_simplex():
    rng = np.random.default_rng(0)
    # known cases
    assert np.allclose(project_simplex(np.array([0.5, 0.5])), [0.5, 0.5])
    assert np.allclose(project_simplex(np.array([2.0, 0.0])), [1.0, 0.0])
    assert np.allclose(project_simplex(np.array([1.0, 1.0, 1.0])), [1 / 3, 1 / 3, 1 / 3])
    assert np.allclose(project_simplex(np.array([-1.0, -2.0])), [1.0, 0.0])
    assert project_simplex(np.array([0.2, 0.3, 0.5])).shape == (3,)
    for scale in (0.1, 1.0, 30.0):
        V = rng.standard_normal((300, 7)) * scale
        P = project_simplex(V)
        assert P.shape == V.shape
        assert P.min() >= 0.0
        assert np.allclose(P.sum(1), 1.0, atol=1e-12)
        # KKT: P = max(V - theta, 0) with one theta per row
        for v, p in zip(V, P):
            on = p > 0
            theta = (v - p)[on]
            assert np.ptp(theta) < 1e-10
            assert np.all(v[~on] - theta.mean() <= 1e-10)
        # no point of the simplex is closer
        S = rng.dirichlet(np.ones(7), size=2000)
        d_proj = np.linalg.norm(V - P, axis=1)
        d_other = np.sqrt(((V[:, None, :] - S[None, :, :]) ** 2).sum(-1)).min(1)
        assert np.all(d_proj <= d_other + 1e-12)
    # points of the simplex are fixed
    S = rng.dirichlet(np.full(5, 0.3), size=100)
    assert np.allclose(project_simplex(S), S, atol=1e-12)


def test_pca_fvu_and_kmeans():
    rng = np.random.default_rng(1)
    X = rng.standard_normal((120, 9)) @ rng.standard_normal((9, 9))
    assert pca_fvu(X, 0) == 1.0
    assert pca_fvu(X, 9) < 1e-12
    Xc = X - X.mean(0)
    _, _, Vt = np.linalg.svd(Xc, full_matrices=False)
    for r in (1, 3, 6):
        rec = Xc @ Vt[:r].T @ Vt[:r] + X.mean(0)
        assert abs(pca_fvu(X, r) - fvu(X, rec)) < 1e-12
    vec = pca_fvu(X, np.array([0, 2, 4]))
    assert vec.shape == (3,) and np.all(np.diff(vec) < 0)
    prev = 1.0
    for K in (1, 2, 4, 8):
        km = kmeans(X, K, n_restarts=5, seed=0)
        rec = km["centers"][km["labels"]]
        assert abs(km["fvu"] - fvu(X, rec)) < 1e-10
        # every point is assigned to its nearest centre
        assert np.array_equal(km["labels"], _brute_dist(X, km["centers"]).argmin(1))
        assert km["fvu"] <= prev + 1e-12
        prev = km["fvu"]
    assert abs(kmeans(X, 1)["fvu"] - 1.0) < 1e-12


def test_aa_objective_non_increasing():
    rng = np.random.default_rng(2)
    X = rng.standard_normal((300, 12)) * np.linspace(2.0, 0.3, 12)
    for K in (3, 6):
        for init_km in (True, False):
            r = archetypal_analysis(X, K, n_restarts=2, seed=3, init_from_kmeans=init_km)
            h = np.array(r["history"])
            assert np.all(np.diff(h) <= 1e-12), "the AA objective went up"
            A, B, Z = r["A"], r["B"], r["Z"]
            assert A.shape == (300, K) and B.shape == (K, 300) and Z.shape == (K, 12)
            for M in (A, B):
                assert M.min() >= 0.0 and np.allclose(M.sum(1), 1.0, atol=1e-9)
            assert np.allclose(Z, B @ X, atol=1e-9)
            assert abs(r["fvu"] - fvu(X, A @ Z)) < 1e-10
            assert r["fvu"] <= h[0] + 1e-12
            if init_km:
                assert r["fvu"] <= r["kmeans_fvu"] + 1e-10
    # more convex steps on fixed archetypes cannot do worse than the returned codes
    A2, _ = simplex_codes(X, r["Z"], A0=r["A"], n_iter=50)
    assert fvu(X, A2 @ r["Z"]) <= r["fvu"] + 1e-10


def test_sandwich_pca_aa_kmeans():
    """FVU[PCA(K - 1)] <= FVU[AA(K)] <= FVU[k-means(K)] on random data."""
    rng = np.random.default_rng(4)
    sets = {
        "gaussian": rng.standard_normal((200, 10)),
        "anisotropic": rng.standard_normal((256, 30)) * (1.0 / np.arange(1, 31)),
        "clusters": rng.standard_normal((240, 6)) + 4.0 * rng.standard_normal((6, 6))[rng.integers(0, 6, 240)],
        "uniform": rng.random((150, 4)),
        "d > N": rng.standard_normal((40, 100)),
    }
    for name, X in sets.items():
        for K in (2, 3, 5, 8):
            r = archetypal_analysis(X, K, n_restarts=2, seed=5)
            lo = pca_fvu(X, K - 1)
            hi_own = r["kmeans_fvu"]
            hi = kmeans(X, K, n_restarts=10, seed=6)["fvu"]
            assert lo <= r["fvu"] + 1e-9, (name, K, lo, r["fvu"])
            assert r["fvu"] <= hi_own + 1e-9, (name, K, r["fvu"], hi_own)
            assert r["fvu"] <= hi + 1e-9, (name, K, r["fvu"], hi)
            assert 0.0 <= r["fvu"] <= 1.0


def test_aa_recovers_planted_simplex():
    """Noise-free Dirichlet mixtures of K known vertices: AA finds the simplex."""
    rng = np.random.default_rng(7)
    K, d, N = 4, 8, 600
    V = rng.standard_normal((K, d))
    X, W = dirichlet_mixtures(V, N, alpha=0.3, seed=rng, return_weights=True)
    assert np.allclose(X, W @ V)
    r = archetypal_analysis(X, K, n_restarts=3, seed=0)
    assert r["fvu"] < 1e-3, r["fvu"]
    edge = _brute_dist(V, V)[np.triu_indices(K, 1)].mean()
    D = _brute_dist(V, r["Z"])
    assert sorted(D.argmin(1)) == list(range(K)), "archetypes and vertices are not in one-to-one correspondence"
    assert D.min(1).max() < 0.05 * edge, D.min(1).max() / edge
    # the codes are the planted weights (up to the matching)
    perm = D.argmin(1)
    assert np.abs(r["A"][:, perm] - W).max() < 0.05
    # when the vertices belong to the sample the optimum is zero and it is reached
    for K, d, N, alpha in ((6, 20, 1000, 1.0), (10, 30, 800, 0.5)):
        V = rng.standard_normal((K, d))
        X, W = dirichlet_mixtures(V, N, alpha=alpha, seed=rng, return_weights=True)
        X[:K] = V
        r = archetypal_analysis(X, K, n_restarts=3, seed=0)
        assert r["fvu"] < 1e-8, (K, r["fvu"])
        assert _brute_dist(V, r["Z"]).min(1).max() < 1e-3


# --------------------------------------------------------------------------------------------------------------
# rh.interp
# --------------------------------------------------------------------------------------------------------------
def test_nearest_dist_bruteforce():
    rng = np.random.default_rng(8)
    for dtype in (np.float64, np.float32):
        for d, offset in ((3, 0.0), (40, 0.0), (40, 100.0), (300, 20.0)):
            X = (rng.standard_normal((1500, d)) + offset).astype(dtype)
            Q = (rng.standard_normal((257, d)) + offset).astype(dtype)
            Q[:50] = X[100:150]                                    # queries that are sample points
            Q[50:60] = X[200:210] + dtype(1e-3)                    # and near misses
            D = _brute_dist(Q, X)
            for chunk in (1024, 7):
                dist, idx = nearest_dist(Q, X, chunk=chunk, return_index=True)
                assert dist.dtype == np.float64 and dist.shape == (257,)
                assert np.allclose(dist, D.min(1), rtol=1e-12, atol=1e-12)
                assert np.array_equal(idx, D.argmin(1))
                assert np.all(dist[:50] == 0.0), "a sample point must be at distance exactly 0"
            assert np.array_equal(nearest_dist(Q, X), dist)
    # leave-one-out: the nearest *other* sample
    X = rng.random((800, 5))
    D = _brute_dist(X, X)
    np.fill_diagonal(D, np.inf)
    loo, idx = nearest_dist(X, X, exclude=np.arange(800), return_index=True)
    assert np.allclose(loo, D.min(1), rtol=1e-12) and np.array_equal(idx, D.argmin(1))
    # two exclusions per query, one of them void (-1)
    ex = np.stack([np.arange(800), np.where(np.arange(800) % 2 == 0, D.argmin(1), -1)], axis=1)
    D2 = D.copy()
    even = np.arange(0, 800, 2)
    D2[even, D.argmin(1)[even]] = np.inf
    assert np.allclose(nearest_dist(X, X, exclude=ex), D2.min(1), rtol=1e-12)
    # duplicated samples, 1-D query
    Xd = np.concatenate([X[:10], X[:10]])
    assert nearest_dist(X[3], Xd)[0] == 0.0


def test_knn_search_and_graph():
    rng = np.random.default_rng(9)
    X = rng.standard_normal((400, 6)) * rng.uniform(0.2, 3.0, size=(400, 1))   # norms vary: cosine != euclidean
    k = 7
    D = _brute_dist(X, X)
    np.fill_diagonal(D, np.inf)
    idx, dist = knn_search(X, k, "euclidean", chunk=64)
    assert np.array_equal(idx, np.argsort(D, axis=1)[:, :k])
    assert np.allclose(dist, np.sort(D, axis=1)[:, :k], rtol=1e-12)
    Xn = X / np.linalg.norm(X, axis=1, keepdims=True)
    Cd = 1.0 - Xn @ Xn.T
    np.fill_diagonal(Cd, np.inf)
    idx_c, dist_c = knn_search(X, k, "cosine", chunk=64)
    assert np.array_equal(idx_c, np.argsort(Cd, axis=1)[:, :k])
    assert np.allclose(dist_c, np.take_along_axis(D, idx_c, 1), rtol=1e-12)     # weights stay Euclidean
    assert not np.array_equal(idx, idx_c)
    for metric, nb in (("euclidean", idx), ("cosine", idx_c)):
        G = knn_graph(X, k, metric, chunk=64)
        assert G.shape == (400, 400) and abs(G - G.T).max() == 0.0
        Gd = G.toarray()
        member = np.zeros((400, 400), dtype=bool)
        member[np.repeat(np.arange(400), k), nb.ravel()] = True
        union = member | member.T
        assert np.array_equal(Gd > 0, union), "the graph is not the union of the two directed k-NN relations"
        assert np.allclose(Gd[union], D[union], rtol=1e-12)
        assert np.all(np.diff(G.indptr) >= k)
    # duplicated points keep their zero-length edge
    Xd = np.concatenate([X[:50], X[:50]])
    Gdup = knn_graph(Xd, 3, "euclidean")
    assert Gdup[0, 50] == 0.0 and Gdup.nnz == len(Gdup.data)
    path = graph_paths(Gdup, [[0, 50]])[0]
    assert list(path) == [0, 50]


def test_chord_test_dense_square():
    """In a densely sampled convex set a chord stays next to the sample: the straight curve is ~0."""
    rng = np.random.default_rng(10)
    N = 20000
    X = rng.random((N, 2))
    pairs = rng.integers(0, N, size=(60, 2))
    r = chord_test(X, pairs, n_steps=101, k=10, metric="euclidean")
    assert r["lin"].shape == (60, 101) and r["graph"].shape == (60, 101) and r["t"].shape == (101,)
    assert np.all(r["lin"][:, [0, -1]] == 0.0) and np.all(r["graph"][:, [0, -1]] == 0.0)
    assert np.allclose(r["chord"], np.linalg.norm(X[pairs[:, 0]] - X[pairs[:, 1]], axis=1))
    # typical spacing is 0.5 / sqrt(N) = 0.0035; chords are ~0.5 long
    assert r["lin"].mean() < 0.006, r["lin"].mean()
    assert r["lin"].max() < 0.03, r["lin"].max()
    assert (r["lin"][:, 50] / r["chord"]).mean() < 0.02          # nowhere near the triangle value 0.5
    assert np.nanmax(r["graph"]) < 0.03
    assert not np.isnan(r["graph"]).any()
    assert np.all(r["path_len"] >= r["chord"] * (1 - 1e-12))
    assert np.all(r["path_len"] <= 1.5 * r["chord"] + 0.05)
    assert np.all(r["n_hops"] >= 1)


def test_chord_test_paths():
    # a ring: the chord between antipodal points crosses the empty disc, the graph path follows the circle
    n = 200
    ang = 2 * np.pi * np.arange(n) / n
    X = np.stack([np.cos(ang), np.sin(ang)], axis=1)
    edge = 2 * np.sin(np.pi / n)
    r = chord_test(X, [[0, 100], [10, 60], [5, 5]], n_steps=101, k=2, metric="euclidean")
    assert np.allclose(r["chord"], [2.0, np.sqrt(2.0), 0.0])
    assert np.allclose(r["n_hops"], [100, 50, 0])
    assert np.allclose(r["path_len"], [100 * edge, 50 * edge, 0.0])
    assert abs(r["lin"][0, 50] - 1.0) < 1e-12                    # the centre of the circle: half the chord away
    assert np.nanmax(r["graph"]) <= edge / 2 + 1e-12             # never further than half an edge
    assert np.all(r["lin"][2] == 0.0) and np.all(r["graph"][2] == 0.0)
    # vertices of a regular simplex: the nearest sample to any point of an edge is one of its two ends
    V = np.eye(11)
    pairs = np.array([[0, 1], [2, 7], [10, 3]])
    r = chord_test(V, pairs, n_steps=51, k=10, metric="euclidean")
    tri = np.sqrt(2.0) * np.minimum(r["t"], 1 - r["t"])
    assert np.allclose(r["lin"], tri[None, :], atol=1e-12)
    assert np.allclose(r["n_hops"], 1) and np.allclose(r["graph"], tri[None, :], atol=1e-12)
    # two far-apart groups with a small k: no path, NaN row
    rng = np.random.default_rng(11)
    X = np.concatenate([rng.random((50, 3)), rng.random((50, 3)) + 100.0])
    r = chord_test(X, [[0, 1], [0, 60]], n_steps=21, k=3, metric="euclidean")
    assert not np.isnan(r["graph"][0]).any()
    assert np.isnan(r["graph"][1]).all() and np.isnan(r["path_len"][1]) and np.isnan(r["n_hops"][1])
    assert not np.isnan(r["lin"]).any()
    # resampling: equal arc-length steps, exact ends
    P, L = resample_path(np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 3.0]]), 9)
    assert L == 4.0 and np.allclose(np.linalg.norm(np.diff(P, axis=0), axis=1)[[0, 3, 7]], 0.5)
    assert np.array_equal(P[0], [0.0, 0.0]) and np.array_equal(P[-1], [1.0, 3.0]) and np.allclose(P[2], [1.0, 0.0])
    # float32 input and the cosine graph run through the same code
    Xf = rng.standard_normal((300, 16)).astype(np.float32)
    r = chord_test(Xf, [[0, 1], [2, 3]], n_steps=11, k=15, metric="cosine")
    assert np.all(r["lin"][:, [0, -1]] == 0.0) and np.all(r["graph"][:, [0, -1]] == 0.0)


# --------------------------------------------------------------------------------------------------------------
# rh.nulls
# --------------------------------------------------------------------------------------------------------------
def test_gaussian_like():
    rng = np.random.default_rng(12)
    X = (rng.standard_normal((500, 6)) @ rng.standard_normal((6, 6)) + np.arange(6)).astype(np.float32)
    G = gaussian_like(X, n=200000, seed=1)
    assert G.dtype == np.float32 and G.shape == (200000, 6)
    C = np.cov(X.astype(np.float64), rowvar=False)
    assert np.abs(G.mean(0) - X.mean(0)).max() < 0.05
    assert np.abs(np.cov(G.astype(np.float64), rowvar=False) - C).max() < 0.03 * np.abs(C).max()
    assert gaussian_like(X).shape == X.shape
    assert np.array_equal(gaussian_like(X, seed=3), gaussian_like(X, seed=3))
    assert not np.array_equal(gaussian_like(X, seed=3), gaussian_like(X, seed=4))
    # exact matching of the first two sample moments, also when d > N and when the covariance is singular
    Xw = rng.standard_normal((40, 100))
    Xs = dirichlet_mixtures(rng.standard_normal((5, 30)), 256, alpha=0.5, seed=rng)   # rank 4
    for Y in (X, Xw, Xs):
        E = gaussian_like(Y, seed=2, exact=True).astype(np.float64)
        Y = np.asarray(Y, dtype=np.float64)
        assert E.shape == Y.shape
        assert np.abs(E.mean(0) - Y.mean(0)).max() < 1e-4
        CY, CE = np.cov(Y, rowvar=False), np.cov(E, rowvar=False)
        assert np.abs(CE - CY).max() < 1e-4 * np.abs(CY).max()
        ks = np.arange(0, 8)
        assert np.allclose(pca_fvu(E, ks), pca_fvu(Y, ks), atol=1e-5)


def test_layernorm():
    rng = np.random.default_rng(13)
    X = rng.standard_normal((50, 32)) * 3 + 1
    U = layernorm(X)
    assert np.allclose(U.mean(1), 0.0, atol=1e-12) and np.allclose((U ** 2).sum(1), 32.0)
    g, b = rng.uniform(0.5, 2.0, 32), rng.standard_normal(32)
    assert np.allclose(layernorm(X, g, b), U * g + b)
    assert np.allclose(layernorm(5.0 * X + 2.0), U)             # invariant to positive affine rescaling of a row


if __name__ == "__main__":
    import time

    tests = [(name, fn) for name, fn in sorted(globals().items()) if name.startswith("test_") and callable(fn)]
    failed = 0
    for name, fn in tests:
        t0 = time.time()
        try:
            fn()
            print(f"ok    {name}  ({time.time() - t0:.1f} s)")
        except AssertionError as err:
            failed += 1
            print(f"FAIL  {name}: {err!r}")
    print(f"{len(tests) - failed}/{len(tests)} tests passed")
    sys.exit(1 if failed else 0)
