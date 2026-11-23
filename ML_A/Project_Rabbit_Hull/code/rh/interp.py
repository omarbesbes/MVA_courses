"""The chord test: distance to the nearest sample along straight and graph paths (numpy + scipy.sparse.csgraph).

The test of the paper (Fig. 17, left) takes two points x_i, x_j of a sample X, walks from one to the other and
records, at every step, the Euclidean distance to the nearest point of X. Two walks are compared:

* the straight segment  (1 - t) x_i + t x_j;
* the shortest path between i and j in the k-nearest-neighbour graph of X, a broken line through sample
  points, resampled at equally spaced arc lengths.

Both walks start and end on a sample point, so both curves are 0 at the two ends. A straight curve equal to
``chord * min(t, 1 - t)`` (a triangle whose peak is half the chord) means that no sample is closer to the
segment than its own endpoints.

Numerical conventions
---------------------
Candidate neighbours are found with chunked float32 matrix products (BLAS); the distances that are returned
are then recomputed in float64 from coordinate differences, so a query that coincides with a sample gets an
exact 0 and there is no cancellation error of the form |q|^2 - 2 q.x + |x|^2.
"""
from __future__ import annotations

import numpy as np
from scipy import sparse
from scipy.sparse import csgraph

__all__ = ["nearest_dist", "knn_search", "knn_graph", "graph_paths", "resample_path", "chord_test"]

_EPS32 = float(np.finfo(np.float32).eps)


def _as2d(A):
    A = np.asarray(A)
    return A[None, :] if A.ndim == 1 else A


def _rows_norm64(D):
    D = np.asarray(D, dtype=np.float64)
    return np.sqrt(np.einsum("ij,ij->i", D, D))


# --------------------------------------------------------------------------------------------------------------
# nearest sample
# --------------------------------------------------------------------------------------------------------------
def nearest_dist(Q, X, chunk=1024, return_index=False, exclude=None):
    """Euclidean distance from each row of Q to its nearest row of X.

    Parameters
    ----------
    Q : (M, d) queries.  X : (N, d) sample.
    chunk : number of queries per block (the block holds a chunk x N float32 matrix).
    return_index : also return the index of the nearest row.
    exclude : optional (M,) or (M, m) integer array; rows of X that query number i must ignore (use it for
        leave-one-out distances; negative entries are ignored).

    Returns
    -------
    dist (M,) float64, and idx (M,) int64 if ``return_index``.

    Method
    ------
    Both sets are centred on the mean of X (distances are invariant; this removes most of the cancellation).
    For a block of queries the scores |x|^2 - 2 q.x are computed with one float32 matrix product. Every sample
    whose score is within the float32 rounding bound of the best score is kept as a candidate (almost always a
    single one), and candidates are compared in float64 on exact coordinate differences.
    """
    Q = _as2d(Q)
    X = _as2d(X)
    M, d = Q.shape
    N = X.shape[0]
    if X.shape[1] != d:
        raise ValueError(f"dimension mismatch: Q has {d} columns, X has {X.shape[1]}")
    if N == 0:
        raise ValueError("X is empty")
    mu = X.mean(0, dtype=np.float64)
    Xc = np.ascontiguousarray(X - mu.astype(X.dtype) if X.dtype == np.float32 else X - mu, dtype=np.float32)
    x2 = np.einsum("ij,ij->i", Xc, Xc)                       # float32
    x2max = float(x2.max())
    if exclude is not None:
        exclude = np.asarray(exclude, dtype=np.int64)
        if exclude.ndim == 1:
            exclude = exclude[:, None]
        if exclude.shape[0] != M:
            raise ValueError("exclude must have one row per query")
    out = np.empty(M, dtype=np.float64)
    idx = np.empty(M, dtype=np.int64)
    chunk = max(1, int(chunk))
    for s in range(0, M, chunk):
        q64 = np.asarray(Q[s:s + chunk], dtype=np.float64)
        q = (q64 - mu).astype(np.float32)
        c = q.shape[0]
        S = q @ Xc.T                                         # (c, N) float32
        S *= -2.0
        S += x2[None, :]                                     # |x|^2 - 2 q.x  (the |q|^2 term is constant per row)
        if exclude is not None:
            ex = exclude[s:s + c]
            rr = np.repeat(np.arange(c), ex.shape[1])
            cc = ex.ravel()
            ok = cc >= 0
            S[rr[ok], cc[ok]] = np.inf
        smin = S.min(axis=1)
        q2 = np.einsum("ij,ij->i", q, q).astype(np.float64)
        # worst-case rounding error of a float32 dot product of d terms is (d / 2) eps |q| |x|; the bound
        # below covers the best score and a competitor, with a safety factor 4 for the float32 cast of the data
        tol = 4.0 * (d + 2) * _EPS32 * (2.0 * x2max + q2)
        thr = (smin.astype(np.float64) + tol).astype(np.float32)
        thr = np.nextafter(thr, np.float32(np.inf))
        rows, cols = np.nonzero(S <= thr[:, None])           # row-major order: rows is sorted
        if rows.size == 0 or np.count_nonzero(np.diff(rows)) + 1 != c:
            raise ValueError("a query has no admissible sample (non-finite values, or every row excluded)")
        dd = np.empty(rows.size, dtype=np.float64)
        step = max(1, (1 << 24) // max(d, 1))                # at most ~128 MB of float64 differences at a time
        for a in range(0, rows.size, step):
            diff = q64[rows[a:a + step]] - X[cols[a:a + step]]
            dd[a:a + step] = np.sqrt(np.einsum("ij,ij->i", diff, diff))
        starts = np.searchsorted(rows, np.arange(c))
        best = np.minimum.reduceat(dd, starts)
        hit = np.flatnonzero(dd == best[rows])
        first = hit[np.searchsorted(rows[hit], np.arange(c))]
        out[s:s + c] = best
        idx[s:s + c] = cols[first]
    return (out, idx) if return_index else out


# --------------------------------------------------------------------------------------------------------------
# k nearest neighbours and the graph
# --------------------------------------------------------------------------------------------------------------
def knn_search(X, k=15, metric="euclidean", chunk=1024):
    """k nearest neighbours of every row of X among the other rows.

    ``metric`` ("euclidean" or "cosine") decides who the neighbours are; the returned distances are always
    Euclidean lengths |x_i - x_j| (float64, exact).

    Returns ``idx`` (N, k) int64 and ``dist`` (N, k) float64, sorted by increasing ``metric`` distance.
    """
    X = _as2d(X)
    N, d = X.shape
    k = int(k)
    if not 1 <= k <= N - 1:
        raise ValueError(f"k must be between 1 and N - 1 = {N - 1}")
    if metric == "euclidean":
        mu = X.mean(0, dtype=np.float64)
        Y = np.ascontiguousarray(X - mu, dtype=np.float32)
        y2 = np.einsum("ij,ij->i", Y, Y)
    elif metric == "cosine":
        nrm = _rows_norm64(X)
        if not np.all(nrm > 0):
            raise ValueError("cosine neighbours are undefined for zero vectors")
        Y = np.ascontiguousarray(X / nrm[:, None], dtype=np.float32)
        y2 = None
    else:
        raise ValueError("metric must be 'euclidean' or 'cosine'")
    idx = np.empty((N, k), dtype=np.int64)
    chunk = max(1, int(chunk))
    for s in range(0, N, chunk):
        S = Y[s:s + chunk] @ Y.T                             # (c, N) float32
        c = S.shape[0]
        if y2 is None:
            np.negative(S, out=S)                            # cosine distance up to a constant: -cos
        else:
            S *= -2.0
            S += y2[None, :]
        S[np.arange(c), np.arange(s, s + c)] = np.inf        # never one's own neighbour
        if k < N - 1:
            part = np.argpartition(S, k - 1, axis=1)[:, :k]
        else:
            part = np.argsort(S, axis=1)[:, :k]
        order = np.argsort(np.take_along_axis(S, part, axis=1), axis=1, kind="stable")
        idx[s:s + c] = np.take_along_axis(part, order, axis=1)
    dist = np.empty((N, k), dtype=np.float64)
    step = max(1, (1 << 24) // max(d * k, 1))
    for s in range(0, N, step):
        diff = np.asarray(X[idx[s:s + step]], dtype=np.float64) - np.asarray(X[s:s + step], dtype=np.float64)[:, None, :]
        dist[s:s + step] = np.sqrt(np.einsum("nkd,nkd->nk", diff, diff))
    return idx, dist


def knn_graph(X, k=15, metric="cosine", chunk=1024, return_knn=False):
    """Symmetric k-nearest-neighbour graph of the rows of X, as a CSR matrix.

    Neighbours are chosen with ``metric`` ("cosine" or "euclidean"); i and j are joined when j is among the k
    nearest neighbours of i *or* i among those of j (union symmetrisation). Edge weights are Euclidean lengths.
    Zero-length edges (duplicated points) are stored as explicit zeros, which scipy.sparse.csgraph treats as
    edges of weight zero.

    With ``return_knn`` the function returns (graph, idx, dist), idx and dist as in :func:`knn_search`.
    """
    X = _as2d(X)
    N = X.shape[0]
    idx, dist = knn_search(X, k=k, metric=metric, chunk=chunk)
    i = np.repeat(np.arange(N, dtype=np.int64), idx.shape[1])
    j = idx.ravel()
    w = dist.ravel()
    lo, hi = np.minimum(i, j), np.maximum(i, j)
    key = lo * N + hi
    _, first = np.unique(key, return_index=True)             # each undirected edge once
    lo, hi, w = lo[first], hi[first], w[first]
    rows = np.concatenate([lo, hi])
    cols = np.concatenate([hi, lo])
    data = np.concatenate([w, w])
    order = np.lexsort((cols, rows))
    rows, cols, data = rows[order], cols[order], data[order]
    indptr = np.concatenate([[0], np.cumsum(np.bincount(rows, minlength=N))])
    G = sparse.csr_matrix((data, cols.astype(np.int32 if N < 2 ** 31 else np.int64), indptr), shape=(N, N))
    return (G, idx, dist) if return_knn else G


def graph_paths(graph, pairs, block=64):
    """Shortest paths in a weighted undirected graph for a list of (source, target) pairs.

    Returns a list with one entry per pair: the array of node indices from source to target, or None when the
    two nodes are not connected. Dijkstra is run once per distinct source, ``block`` sources at a time.
    """
    pairs = np.asarray(pairs, dtype=np.int64).reshape(-1, 2)
    P = len(pairs)
    paths = [None] * P
    sources, inv = np.unique(pairs[:, 0], return_inverse=True)
    by_source = [[] for _ in range(len(sources))]
    for p in range(P):
        by_source[inv[p]].append(p)
    for s in range(0, len(sources), block):
        blk = sources[s:s + block]
        _, pred = csgraph.dijkstra(graph, directed=False, indices=blk, return_predecessors=True)
        for b, src in enumerate(blk):
            pr = pred[b]
            for p in by_source[s + b]:
                tgt = int(pairs[p, 1])
                if tgt == src:
                    paths[p] = np.array([src], dtype=np.int64)
                    continue
                if pr[tgt] < 0:                              # -9999: not reachable
                    continue
                nodes = [tgt]
                cur = tgt
                while cur != src:
                    cur = int(pr[cur])
                    nodes.append(cur)
                paths[p] = np.array(nodes[::-1], dtype=np.int64)
    return paths


def resample_path(V, n_steps=101):
    """Points equally spaced in arc length along the broken line through the rows of V.

    Returns (points (n_steps, d) float64, total length). The first and last points are V[0] and V[-1] exactly.
    """
    V = np.asarray(V, dtype=np.float64)
    if V.shape[0] == 1:
        return np.repeat(V, n_steps, axis=0), 0.0
    seg = _rows_norm64(np.diff(V, axis=0))
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    L = float(cum[-1])
    if L == 0.0:
        return np.repeat(V[:1], n_steps, axis=0), 0.0
    s = np.linspace(0.0, 1.0, n_steps) * L
    m = np.clip(np.searchsorted(cum, s, side="right") - 1, 0, len(seg) - 1)
    with np.errstate(invalid="ignore", divide="ignore"):
        frac = np.where(seg[m] > 0, (s - cum[m]) / seg[m], 0.0)
    frac = np.clip(frac, 0.0, 1.0)
    pts = (1.0 - frac)[:, None] * V[m] + frac[:, None] * V[m + 1]
    pts[0], pts[-1] = V[0], V[-1]
    return pts, L


# --------------------------------------------------------------------------------------------------------------
# the chord test
# --------------------------------------------------------------------------------------------------------------
def chord_test(X, pairs, n_steps=101, k=15, metric="cosine", chunk=1024, graph=None):
    """Distance to the nearest sample along the straight segment and along the k-NN graph path.

    Parameters
    ----------
    X : (N, d) sample.  pairs : (P, 2) integer array of row indices (i, j).
    n_steps : number of positions along each path (both ends included).
    k, metric : parameters of the k-NN graph (see :func:`knn_graph`); ignored when ``graph`` is given.
    graph : optional precomputed symmetric CSR graph with Euclidean edge lengths.

    Returns
    -------
    dict with
      ``lin``      (P, n_steps)  distance to the nearest row of X at (1 - t) x_i + t x_j, t = linspace(0, 1);
                                 the endpoints are sample points, so the first and last columns are 0;
      ``graph``    (P, n_steps)  the same along the shortest path from i to j in the graph, at n_steps points
                                 equally spaced in arc length; a row of NaN when i and j are not connected;
      ``chord``    (P,)          |x_i - x_j|;
      ``path_len`` (P,)          Euclidean length of the graph path (NaN if not connected);
      ``n_hops``   (P,)          number of edges of the graph path (float; NaN if not connected);
      ``t``        (n_steps,)    the positions, as fractions of the path.
    """
    X = _as2d(X)
    N, d = X.shape
    pairs = np.asarray(pairs, dtype=np.int64).reshape(-1, 2)
    if pairs.size and (pairs.min() < 0 or pairs.max() >= N):
        raise ValueError("pair index out of range")
    P = len(pairs)
    n_steps = int(n_steps)
    t = np.linspace(0.0, 1.0, n_steps)
    xi = np.asarray(X[pairs[:, 0]], dtype=np.float64)
    xj = np.asarray(X[pairs[:, 1]], dtype=np.float64)
    chord = _rows_norm64(xj - xi)

    block = max(1, (1 << 23) // max(n_steps * d, 1))         # pairs per block: at most ~64 MB of float64 points
    lin = np.empty((P, n_steps), dtype=np.float64)
    for s in range(0, P, block):
        a, b = xi[s:s + block], xj[s:s + block]
        pts = (1.0 - t)[None, :, None] * a[:, None, :] + t[None, :, None] * b[:, None, :]
        pts[:, 0, :], pts[:, -1, :] = a, b
        lin[s:s + block] = nearest_dist(pts.reshape(-1, d), X, chunk=chunk).reshape(-1, n_steps)

    if graph is None:
        graph = knn_graph(X, k=k, metric=metric, chunk=chunk)
    paths = graph_paths(graph, pairs)
    gra = np.full((P, n_steps), np.nan, dtype=np.float64)
    path_len = np.full(P, np.nan, dtype=np.float64)
    n_hops = np.full(P, np.nan, dtype=np.float64)
    buf, owners = [], []

    def _flush():
        if buf:
            D = nearest_dist(np.concatenate(buf, axis=0), X, chunk=chunk).reshape(-1, n_steps)
            gra[np.array(owners)] = D
            buf.clear()
            owners.clear()

    for p, nodes in enumerate(paths):
        if nodes is None:
            continue
        pts, L = resample_path(np.asarray(X[nodes], dtype=np.float64), n_steps)
        path_len[p] = L
        n_hops[p] = len(nodes) - 1
        buf.append(pts)
        owners.append(p)
        if len(buf) >= block:
            _flush()
    _flush()
    return {"lin": lin, "graph": gra, "chord": chord, "path_len": path_len, "n_hops": n_hops, "t": t}
