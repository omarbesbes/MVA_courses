"""figures_02.py -- static SVG figures of page 02 (toolbox), written to figures/02/.
Run: python3 figures_02.py   (then node build.mjs 02_toolbox.html)"""
import math, sys
import numpy as np
from figures_common import Canvas, Fig
sys.path.insert(0, "/home/user/MVA_courses/ML_A/Project_Rabbit_Hull/code")
SUB = "02"


def hull(P):
    P = sorted(map(tuple, P))
    def cr(o, a, b): return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lo = []
    for p in P:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 1e-12: lo.pop()
        lo.append(p)
    up = []
    for p in reversed(P):
        while len(up) >= 2 and cr(up[-2], up[-1], p) <= 1e-12: up.pop()
        up.append(p)
    return np.array(lo[:-1] + up[:-1])


def msum(A, B):
    return hull([np.add(a, b) for a in A for b in B])


def poly(c, P, ox, oy, s, cls, flip=True):
    pts = " ".join(f"{ox + s*x:.1f},{oy - s*y:.1f}" for x, y in P)
    c.add(f'<polygon points="{pts}" class="{cls}"/>')


def fig_welchcurve():
    c = Canvas("welchcurve", 720, 330, "Welch bound and the coherence of random unit vectors in dimension 768, as functions of the number of vectors", sub=SUB)
    d = 768
    f = Fig(c, (70, 24, 610, 250), (3.0, 6.0), (0, 0.3))
    f.axes(xticks=[3, 4, 5, 6], yticks=[0, 0.1, 0.2, 0.3], xfmt=lambda v: f"10^{int(v)}".replace("10^3", "10³").replace("10^4", "10⁴").replace("10^5", "10⁵").replace("10^6", "10⁶"),
           yfmt=lambda v: f"{v:g}", xlabel="number of vectors c (log scale)", ylabel="coherence μ")
    welch = lambda cc: math.sqrt((cc - d) / (d * (cc - 1)))
    rnd = lambda cc: math.sqrt(2 * math.log(cc * (cc - 1)) / d)
    f.fn(lambda x: welch(10**x), "ln c1", 3.0, 6.0)
    f.fn(lambda x: rnd(10**x), "ln c2", 3.0, 6.0)
    f.line(3.0, 1 / math.sqrt(d), 6.0, 1 / math.sqrt(d), "ln c6 dash thin")
    x0 = math.log10(32000)
    f.line(x0, 0, x0, 0.3, "ln c3 dash thin")
    f.circle(x0, welch(32000), 4.5, "f1"); f.circle(x0, 0.065897, 4.5, "f3"); f.circle(x0, rnd(32000), 4.5, "f2")
    f.text(x0, 0.2285, "random: 0.23", "tx-s", "end", dx=-8, dy=-6)
    f.text(x0, 0.0659, "paper's numerical frame: 0.066", "tx-s", "end", dx=-9, dy=-8)
    f.text(x0, welch(32000), "Welch: 0.036", "tx-s", "start", dx=9, dy=18)
    f.text(3.05, 0.235, "random pairs: √(2 ln(c(c−1))/d)", "tx-s", "start")
    f.text(6.0, 0.0361, "dashed: 1/√d = 0.036, std of one random inner product", "tx-s", "end", dy=-7)
    f.text(3.05, 0.075, "Welch bound (blue)", "tx-s", "start")
    f.text(x0, 0.3, "c = 32 000", "tx-s", "middle", dy=-8)
    c.save()


def fig_spectra():
    from numpy.linalg import svd
    rng = np.random.default_rng(1)
    c_, d = 32000, 768
    D = rng.standard_normal((c_, d)); D /= np.linalg.norm(D, axis=1, keepdims=True)
    sv = np.linalg.svd(D, compute_uv=False)
    idx = np.arange(1, d + 1)
    dec = idx ** -0.45; dec = dec * math.sqrt(c_ / (dec ** 2).sum())
    cv = Canvas("spectra", 720, 330, "Singular values of a 32,000 by 768 matrix with unit rows: tight frame, random rows, and an anisotropic example", sub=SUB)
    f = Fig(cv, (60, 24, 620, 250), (1, 768), (0, 24))
    f.axes(xticks=[1, 200, 400, 600, 768], yticks=[0, 6.455, 12, 18, 24], yfmt=lambda v: f"{v:g}", xlabel="index i", ylabel="σᵢ")
    f.path(list(zip(idx, dec)), "ln c2")
    f.path(list(zip(idx, sv)), "ln c6")
    f.line(1, math.sqrt(c_ / d), 768, math.sqrt(c_ / d), "ln c1")
    f.text(768, math.sqrt(c_ / d), "tight frame: all σᵢ = √(c/d) = 6.455", "tx-s", "end", dy=-24)
    f.text(768, sv[300], "random rows: 5.46 to 7.44", "tx-s", "end", dy=22)
    f.text(30, dec[0], "an anisotropic dictionary (illustrative, Σσᵢ² = c)", "tx-s", "start", dx=4, dy=-8)
    cv.save()


def fig_hexagon():
    c = Canvas("hexagon", 720, 250, "The regular hexagon as a sum of three segments and as a triangle plus its reflection", sub=SUB)
    s = 70
    def seg(a): return np.array([[0, 0], [math.cos(a), math.sin(a)]])
    T = np.array([[0, 0], [1, 0], [.5, math.sqrt(3) / 2]])
    A = [seg(0), seg(math.pi / 3), seg(2 * math.pi / 3)]
    H = msum(msum(A[0], A[1]), A[2]); H = H - H.mean(0)
    y0 = 140
    ox = 40
    for k, S in enumerate(A):
        S0 = S - S.mean(0)
        poly(c, S0, ox + 20, y0, s, "ln c2 thin")
        c.add(f'<line x1="{ox + 20 + s*S0[0,0]:.1f}" y1="{y0 - s*S0[0,1]:.1f}" x2="{ox + 20 + s*S0[1,0]:.1f}" y2="{y0 - s*S0[1,1]:.1f}" class="ln c2" style="stroke-width:3"/>')
        if k < 2: c.text(ox + 20 + 70, y0 + 4, "⊕", "tx-b", "middle")
        ox += 105
    ox0 = ox - 10
    c.text(ox0, y0 + 4, "=", "tx-b", "middle")
    poly(c, H, ox0 + 80, y0, s, "f1 a1 ln c1")
    c.text(ox0 + 80, y0 + 112, "hexagon", "tx-s", "middle")
    c.text(ox0 + 165, y0 + 4, "=", "tx-b", "middle")
    T0 = T - T.mean(0)
    poly(c, T0, ox0 + 230, y0, s, "f5 a5 ln c5")
    c.text(ox0 + 275, y0 + 4, "⊕", "tx-b", "middle")
    poly(c, -T0, ox0 + 320, y0, s, "f5 a5 ln c5")
    c.text(ox0 + 275, y0 + 112, "T ⊕ (−T)", "tx-s", "middle")
    c.text(150, 235, "three segments (zonotope)", "tx-s", "middle")
    c.save()


def fig_squarebary():
    c = Canvas("squarebary", 720, 270, "Barycentric weights of a point: unique in a triangle, not in a square", sub=SUB)
    s = 150
    # triangle
    T = np.array([[0, 0], [1, 0], [0.3, 0.85]]); ox, oy = 60, 220
    poly(c, T, ox, oy, s, "f1 a1 ln c1")
    p = np.array([0.4, 0.3])
    lam = np.linalg.solve(np.vstack([T.T, np.ones(3)]), np.r_[p, 1])
    c.add(f'<circle cx="{ox+s*p[0]:.1f}" cy="{oy-s*p[1]:.1f}" r="5" class="f3"/>')
    for k, nm in enumerate("123"):
        c.text(ox + s * T[k, 0] + (-14 if k == 0 else 8), oy - s * T[k, 1] + (14 if k < 2 else -6), "v" + "₁₂₃"[k], "tx-b")
    c.text(ox, 248, f"p = {lam[0]:.2f} v₁ + {lam[1]:.2f} v₂ + {lam[2]:.2f} v₃ : the only way", "tx-s")
    # square
    ox2 = 410
    Q = np.array([[0, 0], [1, 0], [1, 1], [0, 1.]]) * 0.9
    poly(c, Q, ox2, oy, s, "f1 a1 ln c1")
    p = Q.mean(0)
    for (i, j, k) in [(0, 2, "ln c2"), (1, 3, "ln c5")]:
        c.add(f'<line x1="{ox2+s*Q[i,0]:.1f}" y1="{oy-s*Q[i,1]:.1f}" x2="{ox2+s*Q[j,0]:.1f}" y2="{oy-s*Q[j,1]:.1f}" class="{k} dash"/>')
    c.add(f'<circle cx="{ox2+s*p[0]:.1f}" cy="{oy-s*p[1]:.1f}" r="5" class="f3"/>')
    for k in range(4):
        c.text(ox2 + s * Q[k, 0] + (-16 if Q[k, 0] == 0 else 6), oy - s * Q[k, 1] + (14 if Q[k, 1] == 0 else -6), "v" + "₁₂₃₄"[k], "tx-b")
    c.text(ox2 - 10, 248, "centre = ½(v₁+v₃) = ½(v₂+v₄) = ¼(v₁+v₂+v₃+v₄)", "tx-s")
    c.text(ox2 - 10, 26, "four vertices in the plane: weights are not unique", "tx-b")
    c.text(ox - 0, 26, "three affinely independent vertices: unique", "tx-b")
    c.save()


def fig_aasandwich():
    from rh.aa import archetypal_analysis, pca_fvu
    rng = np.random.default_rng(0)
    N, dim, rank = 256, 50, 8
    _ = rng.standard_normal((256, 50))  # same stream as the check script (isotropic draw first)
    X = rng.standard_normal((N, rank)) @ (rng.standard_normal((rank, dim)) * np.linspace(2, 0.5, rank)[:, None]) + 0.3 * rng.standard_normal((N, dim))
    Ks = [2, 3, 4, 5, 7, 10, 15, 20]
    P, A, Km = [], [], []
    for K in Ks:
        r = archetypal_analysis(X, K, n_restarts=3, seed=0, n_iter=300)
        P.append(float(pca_fvu(X, K - 1))); A.append(r["fvu"]); Km.append(r["kmeans_fvu"])
    cv = Canvas("aasandwich", 720, 320, "Archetypal analysis lies between the best affine subspace and k-means", sub=SUB)
    f = Fig(cv, (60, 24, 610, 245), (1, 21), (0, 0.8))
    f.axes(xticks=[2, 5, 10, 15, 20], yticks=[0, 0.2, 0.4, 0.6, 0.8], yfmt=lambda v: f"{v:g}", xlabel="K (number of archetypes / clusters)", ylabel="FVU")
    f.path(list(zip(Ks, P)), "ln c6"); f.path(list(zip(Ks, A)), "ln c1"); f.path(list(zip(Ks, Km)), "ln c2")
    for K, a in zip(Ks, A): f.circle(K, a, 3.5, "f1")
    f.text(20.8, Km[-1], "k-means (K clusters)", "tx-s", "end", dy=-8)
    f.text(20.8, A[-1], "archetypal analysis", "tx-s", "end", dy=-8)
    f.text(20.8, P[-1], "best (K−1)-dim. affine subspace", "tx-s", "end", dy=16)
    cv.save()


if __name__ == "__main__":
    for fn in (fig_welchcurve, fig_spectra, fig_hexagon, fig_squarebary, fig_aasandwich):
        fn()
