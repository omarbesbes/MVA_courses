"""figures_L07.py — static SVG figures of Lesson 7 (entropic regularization and Sinkhorn), written to figures/L07/.

Run: python3 figures_L07.py        (then node build.mjs Lesson07.html)

Every plotted quantity is computed here: the entropic plans by log-domain Sinkhorn, the Gaussian quantities by the
closed forms of OT4ML Prop. 9.26 / Cor. 9.27, the null experiment of the statistics figure by sampling (POT for W2).
"""
import json
import math
import os

import numpy as np
from scipy.special import logsumexp

from figures_common import Canvas, Fig

SUB = "L07"
HERE = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------------------------------------------
# helpers
def sinkhorn_log(a, b, C, eps, tol=1e-11, maxit=200000, ref=True):
    """Log-domain Sinkhorn for min <C,P> + eps KL(P | a x b); returns (f, g, P, iterations)."""
    la, lb = np.log(a), np.log(b)
    f = np.zeros(len(a)); g = np.zeros(len(b))
    for it in range(1, maxit + 1):
        f = -eps * logsumexp(lb[None, :] + (g[None, :] - C) / eps, axis=1)
        g = -eps * logsumexp(la[:, None] + (f[:, None] - C) / eps, axis=0)
        if it % 5 == 0 or it < 5:
            P = np.exp(la[:, None] + lb[None, :] + (f[:, None] + g[None, :] - C) / eps)
            if np.abs(P.sum(1) - a).sum() < tol:
                break
    P = np.exp(la[:, None] + lb[None, :] + (f[:, None] + g[None, :] - C) / eps)
    return f, g, P, it


def monotone_plan(a, b):
    n, m = len(a), len(b)
    P = np.zeros((n, m)); ra, rb = a.copy(), b.copy(); i = j = 0
    while i < n and j < m:
        t = min(ra[i], rb[j]); P[i, j] += t; ra[i] -= t; rb[j] -= t
        if ra[i] <= 1e-15: i += 1
        else: j += 1
    return P


def heatmap(c, M, x0, y0, w, h, levels=10, cls="fk", gamma=0.5):
    """Draw the matrix M (rows = source, top to bottom; columns = target, left to right) as opacity cells.
    Runs of equal level in a row are merged into one rectangle to keep the SVG small."""
    n, m = M.shape
    q = (M / M.max()) ** gamma
    lev = np.floor(q * levels + 0.5).astype(int)
    cw, ch = w / m, h / n
    for i in range(n):
        j = 0
        while j < m:
            L = lev[i, j]; k = j
            while k + 1 < m and lev[i, k + 1] == L:
                k += 1
            if L > 0:
                c.add(f'<rect x="{x0 + j * cw:.2f}" y="{y0 + i * ch:.2f}" width="{(k - j + 1) * cw + 0.15:.2f}" '
                      f'height="{ch + 0.15:.2f}" class="{cls}" fill-opacity="{L / levels:.2f}"/>')
            j = k + 1
    c.add(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{h:.1f}" class="ln cm hair nofill"/>')


def side_profile(c, v, x0, y0, w, h, cls_fill, cls_line, vertical):
    """A histogram drawn along a side of a heat map: vertical=True puts it on the left (bars grow to the left)."""
    n = len(v); vmax = v.max()
    pts = []
    if vertical:
        for i in range(n):
            yy = y0 + (i + 0.5) / n * h
            pts.append((x0 + w - v[i] / vmax * w, yy))
        d = f"M{x0 + w:.1f} {y0:.1f}" + "".join(f"L{px:.1f} {py:.1f}" for px, py in pts) + f"L{x0 + w:.1f} {y0 + h:.1f}Z"
    else:
        for j in range(n):
            xx = x0 + (j + 0.5) / n * w
            pts.append((xx, y0 + h - v[j] / vmax * h))
        d = f"M{x0:.1f} {y0 + h:.1f}" + "".join(f"L{px:.1f} {py:.1f}" for px, py in pts) + f"L{x0 + w:.1f} {y0 + h:.1f}Z"
    c.add(f'<path d="{d}" class="{cls_fill}"/>')
    d2 = "M" + "L".join(f"{px:.1f} {py:.1f}" for px, py in pts)
    c.add(f'<path d="{d2}" class="{cls_line}"/>')


def box_axes(f, xticks=(), yticks=(), xfmt=str, yfmt=str, xlabel=None, ylabel=None, grid=True):
    """Ticks, grid and the two axes drawn on the left and bottom edges of the box (for log scales, where the
    default axes of figures_common would draw an axis at log10(1) = 0)."""
    for v in xticks:
        if grid: f.line(v, f.yr[0], v, f.yr[1], "gr")
        f.text(v, f.yr[0], xfmt(v), "tx-s", "middle", dy=14)
    for v in yticks:
        if grid: f.line(f.xr[0], v, f.xr[1], v, "gr")
        f.text(f.xr[0], v, yfmt(v), "tx-s", "end", dx=-5, dy=4)
    f.line(f.xr[0], f.yr[0], f.xr[1], f.yr[0], "ax")
    f.line(f.xr[0], f.yr[0], f.xr[0], f.yr[1], "ax")
    if xlabel: f.text(f.xr[1], f.yr[0], xlabel, "tx-s", "end", dy=28)
    if ylabel: f.text(f.xr[0], f.yr[1], ylabel, "tx-s", "start", dx=4, dy=-6)


def clipped(pts, yr):
    """Replace the points outside the vertical range by None (Fig.path then lifts the pen)."""
    return [p if yr[0] <= p[1] <= yr[1] else None for p in pts]


# the 1D histograms shared with widgets/Lesson07.js (pair "split")
N = 48
T = (np.arange(N) + 0.5) / N
def bump(m, s): return np.exp(-(T - m) ** 2 / (2 * s * s))
def hist(v):
    v = v + 0.01 * v.max(); return v / v.sum()
A_SPLIT = hist(0.6 * bump(0.22, 0.06) + 0.4 * bump(0.55, 0.05))
B_SPLIT = hist(bump(0.7, 0.09))
C_LINE = (T[:, None] - T[None, :]) ** 2


# ---------------------------------------------------------------------------------------------------------------
def fig_penalty():
    """Running example: objective along the segment of couplings, and x(eps) as a function of eps."""
    c = Canvas("penalty", 660, 290, "Entropic objective along the couplings of the running example, and the entropic path", sub=SUB)
    p = 0.3
    xs = np.linspace(1e-6, p - 1e-6, 300)
    def KLx(x):
        P = np.array([x, p - x, 0.5 - x, 0.5 - p + x]); Q = np.array([p * .5, p * .5, (1 - p) * .5, (1 - p) * .5])
        return np.sum(P * np.log(P / Q))
    cost = lambda x: 0.8 - 2 * x
    eps = 0.5
    f = Fig(c, (50, 40, 270, 200), (0, 0.3), (0, 0.9))
    f.axes(xticks=[0, 0.1, 0.15, 0.2, 0.3], yticks=[0, 0.2, 0.4, 0.6, 0.8], xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:g}",
           xlabel="x = P₁₁")
    f.path([(x, cost(x)) for x in xs], "ln c1 thin dash")
    f.path([(x, eps * KLx(x)) for x in xs], "ln c5 thin dash")
    tot = [(x, cost(x) + eps * KLx(x)) for x in xs]
    f.path(tot, "ln ck")
    i = int(np.argmin([t[1] for t in tot]))
    xm, ym = tot[i]
    f.circle(xm, ym, 4.5, "f3")
    f.line(xm, 0, xm, ym, "ln c3 thin dot")
    f.circle(0.3, cost(0.3), 4.5, "f1")
    f.circle(0.177, 0.85, 4, "f3"); f.text(0.177, 0.85, f"minimizer x(ε) = {xm:.3f}", "tx-s t3", "start", dx=8, dy=4)
    f.circle(0.177, 0.77, 4, "f1"); f.text(0.177, 0.77, "LP vertex x = 0.3", "tx-s t1", "start", dx=8, dy=4)
    f.text(0.035, 0.56, "⟨C, P⟩", "tx-s t1", "start")
    f.text(0.15, 0.055, "ε·KL(P | a⊗b)", "tx-s t5", "middle")
    f.text(0.02, 0.33, "sum, ε = 0.5", "tx-b", "start")
    c.text(185, 18, "Objective along the couplings P(x)", "tx-b", "middle")
    # right: x(eps) against eps
    def xeps(e):
        g = lambda d: -2 + e * np.log((p - d) * (0.5 - d) / (d * (0.5 - p + d)))
        lo, hi = 1e-300, p * (1 - 1e-15)
        for _ in range(3000):
            mid = math.sqrt(lo * hi) if hi / lo > 4 else 0.5 * (lo + hi)
            if g(mid) > 0: lo = mid
            else: hi = mid
        return p - 0.5 * (lo + hi)
    g = Fig(c, (400, 40, 236, 200), (-2, 2), (0.14, 0.31))
    box_axes(g, xticks=[-2, -1, 0, 1, 2], yticks=[0.15, 0.2, 0.25, 0.3], xfmt=lambda v: {-2: "0.01", -1: "0.1", 0: "1", 1: "10", 2: "100"}[v],
             yfmt=lambda v: f"{v:g}", xlabel="ε (log scale)")
    es = np.linspace(-2, 2, 200)
    g.path([(e, xeps(10 ** e)) for e in es], "ln c3")
    g.line(-2, 0.3, 2, 0.3, "ln c1 thin dash")
    g.line(-2, 0.15, 2, 0.15, "ln cm thin dash")
    g.text(2, 0.3, "LP vertex 0.3", "tx-s t1", "end", dy=-5)
    g.text(-1.95, 0.15, "independent coupling a⊗b: 0.15", "tx-s", "start", dy=-5)
    c.text(518, 18, "The entropic path: x(ε) against ε", "tx-b", "middle")
    c.save()
    return xm


def fig_path():
    c = Canvas("path", 660, 236, "Entropic plans between two histograms for decreasing temperatures, and the exact optimal plan", sub=SUB)
    a, b, C = A_SPLIT, B_SPLIT, C_LINE
    panels = [(0.1, "ε = 0.1"), (0.01, "ε = 0.01"), (0.001, "ε = 0.001"), (None, "exact OT (ε → 0)")]
    S = 128
    for k, (eps, title) in enumerate(panels):
        x0 = 40 + k * 156; y0 = 52
        if eps is None:
            P = monotone_plan(a, b)
        else:
            P = sinkhorn_log(a, b, C, eps)[2]
        heatmap(c, P, x0, y0, S, S, levels=12)
        side_profile(c, a, x0 - 22, y0, 20, S, "a2", "ln c2 thin", vertical=True)
        side_profile(c, b, x0, y0 - 22, S, 20, "a1", "ln c1 thin", vertical=False)
        c.text(x0 + S / 2, y0 + S + 18, title, "tx-b", "middle")
        msk = P > 0
        KL = np.sum(P[msk] * np.log(P[msk] / np.outer(a, b)[msk]))
        cost = (P * C).sum()
        c.text(x0 + S / 2, y0 + S + 33, f"⟨C,P⟩ = {cost:.4f},  KL = {KL:.2f}", "tx-s", "middle")
    c.text(30, 20, "a (source, rows)", "tx-s t2", "start")
    c.text(330, 20, "b (target, columns) on top of each plan", "tx-s t1", "middle")
    c.save()


def fig_scaling():
    """One Sinkhorn cycle on the running example (eps = 0.5): K, row scaling, column scaling, with marginals."""
    c = Canvas("scaling", 660, 230, "One Sinkhorn cycle on the running example: Gibbs kernel, row scaling, column scaling", sub=SUB)
    p, eps = 0.3, 0.5
    a = np.array([p, 1 - p]); b = np.array([0.5, 0.5]); C = np.array([[0., 1.], [1., 0.]])
    K = np.exp(-C / eps)
    v = np.ones(2); u = a / (K @ v)
    P1 = u[:, None] * K * v[None, :]
    v = b / (K.T @ u)
    P2 = u[:, None] * K * v[None, :]
    mats = [(K, "K = exp(−C/ε)", "start: v = 𝟙"), (P1, "diag(u) K", "rows fixed"), (P2, "diag(u) K diag(v)", "columns fixed")]
    cell = 46
    for k, (M, title, sub) in enumerate(mats):
        x0 = 60 + k * 210; y0 = 54
        for i in range(2):
            for j in range(2):
                op = M[i, j] / M.max() * 0.8
                c.add(f'<rect x="{x0 + j * cell:.1f}" y="{y0 + i * cell:.1f}" width="{cell:.1f}" height="{cell:.1f}" class="fk" fill-opacity="{op:.2f}"/>')
                c.add(f'<rect x="{x0 + j * cell:.1f}" y="{y0 + i * cell:.1f}" width="{cell:.1f}" height="{cell:.1f}" class="ln cm hair nofill"/>')
                c.add(f'<rect x="{x0 + j * cell + 7:.1f}" y="{y0 + i * cell + 15:.1f}" width="{cell - 14:.1f}" height="16" rx="3" class="fs" fill-opacity="0.85"/>')
                c.text(x0 + j * cell + cell / 2, y0 + i * cell + 27, f"{M[i, j]:.3f}", "tx-s", "middle")
        rs, cs = M.sum(1), M.sum(0)
        for i in range(2):
            ok = abs(rs[i] - a[i]) < 1e-12
            c.text(x0 + 2 * cell + 8, y0 + i * cell + 27, f"{rs[i]:.3f}" + (" ✓" if ok else ""), "tx-s t2" if ok else "tx-s", "start")
        for j in range(2):
            ok = abs(cs[j] - b[j]) < 1e-12
            c.text(x0 + j * cell + cell / 2, y0 + 2 * cell + 15, f"{cs[j]:.3f}" + ("✓" if ok else ""), "tx-s t1" if ok else "tx-s", "middle")
        c.text(x0 + cell, y0 - 22, title, "tx-b", "middle")
        c.text(x0 + cell, y0 - 8, sub, "tx-s", "middle")
        if k < 2:
            c.arrow(x0 + 2 * cell + 58, y0 + cell, x0 + 2 * cell + 98, y0 + cell, 3)
            c.text(x0 + 2 * cell + 78, y0 + cell - 8, "u ← a / Kv" if k == 0 else "v ← b / Kᵀu", "tx-s t3", "middle")
    c.text(330, 205, "row sums on the right of each matrix (target a = (0.3, 0.7)), column sums below (target b = (0.5, 0.5));", "tx-s", "middle")
    c.text(330, 220, "each half-step makes one marginal exact (✓) and breaks the other", "tx-s", "middle")
    c.save()
    return u, v, P1, P2


def fig_projections():
    """Iterates of Sinkhorn on the running example, in the coordinates (first row sum, first column sum)."""
    c = Canvas("projections", 660, 290, "Sinkhorn iterates of the running example in the plane (first row sum, first column sum)", sub=SUB)
    p, eps = 0.3, 0.5
    a = np.array([p, 1 - p]); b = np.array([0.5, 0.5]); C = np.array([[0., 1.], [1., 0.]])
    K = np.exp(-C / eps)
    pts = []; Pc = K.copy(); half = []
    for it in range(6):
        Pc = (a / Pc.sum(1))[:, None] * Pc; pts.append((Pc.sum(1)[0], Pc.sum(0)[0])); half.append(Pc.copy())
        Pc = Pc * (b / Pc.sum(0))[None, :]; pts.append((Pc.sum(1)[0], Pc.sum(0)[0])); half.append(Pc.copy())
    f = Fig(c, (60, 30, 330, 220), (0.28, 0.42), (0.33, 0.52))
    f.axes(xticks=[0.3, 0.32, 0.34, 0.36, 0.38, 0.4, 0.42], yticks=[0.35, 0.4, 0.45, 0.5], xfmt=lambda v: f"{v:g}",
           yfmt=lambda v: f"{v:g}", xlabel="first row sum (P𝟙)₁")
    c.text(64, 22, "first column sum (Pᵀ𝟙)₁", "tx-s", "start")
    f.line(0.3, 0.33, 0.3, 0.52, "ln c2")
    f.line(0.28, 0.5, 0.42, 0.5, "ln c1")
    f.text(0.3, 0.335, "𝒞¹ = {P𝟙 = a}", "tx-s t2", "start", dx=5, dy=0)
    f.text(0.36, 0.5, "𝒞² = {Pᵀ𝟙 = b}", "tx-s t1", "start", dy=-6)
    for k in range(len(pts) - 1):
        (x1, y1), (x2, y2) = pts[k], pts[k + 1]
        c.arrow(f.X(x1), f.Y(y1), f.X(x2), f.Y(y2), 3, "ln c3 hair")
    for k, (x, y) in enumerate(pts[:7]):
        f.circle(x, y, 3, "f3")
        on_row = (k % 2 == 0)
        f.text(x, y, str(k + 1), "tx-s t3", "end" if on_row else "middle", dx=-6 if on_row else 0, dy=4 if on_row else -8)
    f.circle(0.3, 0.5, 4.5, "fk")
    f.text(0.3, 0.5, "Pε", "tx-b", "end", dx=-7, dy=-6)
    # right: the KL values along the iterations (Pythagoras)
    uu = np.ones(2); vv = np.ones(2)
    for it in range(200):
        uu = a / (K @ vv); vv = b / (K.T @ uu)
    Pstar = uu[:, None] * K * vv[None, :]
    def KL(P, Q): return np.sum(P * np.log(P / Q) - P + Q)
    vals = [KL(Pstar, K)] + [KL(Pstar, H) for H in half]
    g = Fig(c, (456, 30, 180, 220), (0, 12), (-7, 0))
    box_axes(g, xticks=[0, 4, 8, 12], yticks=[0, -2, -4, -6], xfmt=lambda v: f"{v:g}", yfmt=lambda v: "1" if v == 0 else f"1e{int(v)}",
             xlabel="half-step k")
    c.text(460, 22, "KL(Pε | P⁽ᵏ⁾), log scale", "tx-s", "start")
    g.path([(k, math.log10(max(v_, 1e-12))) for k, v_ in enumerate(vals)], "ln c3")
    for k, v_ in enumerate(vals):
        g.circle(k, math.log10(max(v_, 1e-12)), 2.5, "f3")
    c.save()
    return pts, vals


def fig_softmin():
    """Soft c-transform f(x) = min^eps_b ((x - y_j)^2 - g_j) for several eps, against the hard envelope."""
    c = Canvas("softmin", 660, 280, "Soft c-transforms of a potential for decreasing temperatures, and the hard lower envelope", sub=SUB)
    ys = np.array([-1.6, -0.6, 0.3, 1.1, 1.9]); gj = np.array([0.3, 0.9, 0.2, 0.8, 0.4]); bj = np.ones(5) / 5
    xs = np.linspace(-2.6, 2.9, 260)
    f = Fig(c, (50, 20, 420, 220), (-2.6, 2.9), (-1.0, 2.0))
    f.axes(xticks=[-2, -1, 0, 1, 2], yticks=[-1, 0, 1, 2], xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:g}", xlabel="x")
    for y, g in zip(ys, gj):
        f.path(clipped([(x, (x - y) ** 2 - g) for x in xs], f.yr), "ln cm hair")
    hard = [(x, np.min((x - ys) ** 2 - gj)) for x in xs]
    f.path(hard, "ln ck")
    for eps, cls in [(0.5, "ln c2"), (0.15, "ln c5"), (0.03, "ln c1")]:
        soft = [(x, -eps * logsumexp(np.log(bj) - ((x - ys) ** 2 - gj) / eps)) for x in xs]
        f.path(clipped(soft, f.yr), cls + " thin")
    for y, g in zip(ys, gj):
        f.circle(y, -g, 3, "fm")
    x0 = 492
    items = [("ε = 0.5", "c2"), ("ε = 0.15", "c5"), ("ε = 0.03", "c1"), ("ε → 0: hard transform", "ck")]
    for k, (lab, cls) in enumerate(items):
        y = 44 + 22 * k
        c.add(f'<line x1="{x0}" y1="{y - 4}" x2="{x0 + 22}" y2="{y - 4}" class="ln {cls}"/>')
        c.text(x0 + 28, y, lab, "tx-s", "start")
    notes = ["f(x): soft minimum over j of",
             "(x − yⱼ)² − gⱼ, weights bⱼ = 1/5",
             "grey: the five parabolas",
             "dots: their minima (yⱼ, −gⱼ)",
             "soft ≥ hard, and soft − hard",
             "≤ ε log 5 everywhere"]
    for k, t in enumerate(notes):
        c.text(x0, 150 + 16 * k, t, "tx-s", "start")
    c.save()


def fig_hilbert():
    """Hilbert's projective metric: the positive quadrant, the image cone of K, two rays and their images."""
    c = Canvas("hilbert", 660, 280, "Birkhoff contraction: a positive matrix maps the positive quadrant into a narrower cone", sub=SUB)
    eps = 0.5
    K = np.exp(-np.array([[0., 1.], [1., 0.]]) / eps)
    v = np.array([1.0, 4.0]); w = np.array([3.0, 1.0])
    dH = lambda x, y: math.log((x / y).max() / (x / y).min())
    Kv, Kw = K @ v, K @ w
    eta = (K[0, 0] * K[1, 1]) / (K[0, 1] * K[1, 0]); lam = (math.sqrt(eta) - 1) / (math.sqrt(eta) + 1)
    f = Fig(c, (40, 16, 250, 230), (0, 5.2), (0, 5.2))
    f.axes(xticks=[0, 1, 2, 3, 4, 5], yticks=[1, 2, 3, 4, 5], xfmt=lambda t: f"{t:g}", yfmt=lambda t: f"{t:g}", grid=False)
    # image cone K R^2_+ : rays through K e1 = (1, K21) and K e2 = (K12, 1)
    s1 = K[1, 0] / K[0, 0]; s2 = K[0, 1] / K[1, 1]   # slopes of the two extreme rays K e1, K e2
    r1 = (5.2, 5.2 * s1); r2 = (5.2 * s2, 5.2)
    f.path([(0, 0), r1, (5.2, 5.2), r2], "a3", close=True)
    f.line(0, 0, r1[0], r1[1], "ln c3 thin"); f.line(0, 0, r2[0], r2[1], "ln c3 thin")
    for vec, cls, lab in [(v, "c2", "v"), (w, "c1", "v′")]:
        f.line(0, 0, vec[0], vec[1], f"ln {cls} thin dash")
        f.circle(vec[0], vec[1], 3.5, "f" + cls[1])
        f.text(vec[0], vec[1], lab, f"tx-i t{cls[1]}", "start", dx=6, dy=4)
    for vec, cls, lab in [(Kv, "c2", "Kv"), (Kw, "c1", "Kv′")]:
        f.line(0, 0, vec[0], vec[1], f"ln {cls}")
        f.circle(vec[0], vec[1], 3.5, "f" + cls[1])
        f.text(vec[0], vec[1], lab, f"tx-i t{cls[1]}", "start", dx=6, dy=12 if lab == "Kv′" else -4)
    f.text(4.9, 1.3, "K R²₊", "tx-b t3", "end")
    c.text(165, 274, "rays = vectors up to a positive factor", "tx-s", "middle")
    # right: explanation with numbers
    x = 330
    lines = [
        ("K = exp(−C/ε) = [[1, e⁻²], [e⁻², 1]]  (running example, ε = 0.5)", "tx-s"),
        ("Hilbert distance: d(u, u′) = log max(u/u′) − log min(u/u′)", "tx-s"),
        (f"v = (1, 4), v′ = (3, 1):  d(v, v′) = log 12 = {dH(v, w):.3f}", "tx-s"),
        (f"Kv = ({Kv[0]:.3f}, {Kv[1]:.3f}),  Kv′ = ({Kw[0]:.3f}, {Kw[1]:.3f})", "tx-s"),
        (f"d(Kv, Kv′) = {dH(Kv, Kw):.3f}", "tx-s"),
        (f"η(K) = e⁴ = {eta:.2f},  λ(K) = (√η − 1)/(√η + 1) = tanh 1 = {lam:.4f}", "tx-s"),
        (f"Birkhoff: {dH(Kv, Kw):.3f} ≤ λ · {dH(v, w):.3f} = {lam * dH(v, w):.3f}  ✓", "tx-b t3"),
        ("Every vector is sent inside the green cone, whose", "tx-s"),
        (f"Hilbert diameter is log η(K) = {math.log(eta):.0f}: K contracts d.", "tx-s"),
    ]
    for k, (s, cls) in enumerate(lines):
        c.text(x, 46 + 24 * k, s, cls, "start")
    c.save()
    return dH(v, w), dH(Kv, Kw), lam, Kv, Kw


def k_eps(sa, sb, eps): return (math.sqrt(eps ** 2 + 16 * sa ** 2 * sb ** 2) - eps) / 4
def L_gauss(ma, sa, mb, sb, eps):
    k = k_eps(sa, sb, eps)
    return (ma - mb) ** 2 + sa ** 2 + sb ** 2 - 2 * k - eps / 2 * math.log(1 - k ** 2 / (sa ** 2 * sb ** 2))
def S_gauss(ma, sa, mb, sb, eps):
    return L_gauss(ma, sa, mb, sb, eps) - 0.5 * L_gauss(ma, sa, ma, sa, eps) - 0.5 * L_gauss(mb, sb, mb, sb, eps)


def fig_gauss():
    """Entropic plans between N(0,1) and N(1,4): covariance ellipses, Monge map, barycentric projection."""
    c = Canvas("gauss", 660, 318, "Entropic plans between two Gaussians on the line, for two temperatures", sub=SUB)
    ma, sa, mb, sb = 0.0, 1.0, 1.0, 2.0
    for k, eps in enumerate([0.1, 2.0]):
        f = Fig(c, (46 + k * 330, 34, 250, 214), (-3, 3), (-5, 7))
        f.axes(xticks=[-2, 0, 2], yticks=[-4, 0, 4], xfmt=lambda t: f"{t:g}", yfmt=lambda t: f"{t:g}", grid=False, xlabel="x (source)")
        c.text(46 + k * 330 + 4, 30, "y (target)", "tx-s", "start")
        kk = k_eps(sa, sb, eps)
        S = np.array([[sa ** 2, kk], [kk, sb ** 2]])
        vals, vecs = np.linalg.eigh(S)
        for r, cls in [(2.0, "ln cm thin"), (1.0, "ln ck thin")]:
            th = np.linspace(0, 2 * np.pi, 120)
            pts = [(ma + r * (vecs[0, 0] * math.sqrt(vals[0]) * math.cos(t) + vecs[0, 1] * math.sqrt(vals[1]) * math.sin(t)),
                    mb + r * (vecs[1, 0] * math.sqrt(vals[0]) * math.cos(t) + vecs[1, 1] * math.sqrt(vals[1]) * math.sin(t))) for t in th]
            f.path(pts, cls, close=True)
        xx = np.linspace(-3, 3, 50)
        f.path(clipped([(x, mb + sb / sa * (x - ma)) for x in xx], f.yr), "ln c1 thin dash")
        f.path(clipped([(x, mb + kk / sa ** 2 * (x - ma)) for x in xx], f.yr), "ln c3")
        cv = sb ** 2 - kk ** 2 / sa ** 2
        c.text(46 + k * 330 + 125, 14, f"ε = {eps:g}:  corr = {kk / (sa * sb):.3f},  Var(Y | X) = {cv:.3f}", "tx-b", "middle")
    c.text(330, 298, "black / grey: 1 and 2 standard-deviation ellipses of the plan;  dashed blue: Monge map y = 1 + 2x;", "tx-s", "middle")
    c.text(330, 312, "green: barycentric projection x ↦ E[Y | X = x], slope = corr × 2 < 2", "tx-s", "middle")
    c.save()


def fig_bias():
    """Bias of the raw entropic value and of the Sinkhorn divergence for N(0,1) vs N(1,4), and the shrinkage of the raw loss."""
    c = Canvas("bias", 660, 300, "Entropic bias of the raw value and of the Sinkhorn divergence, and the shrinking minimizer of the raw loss", sub=SUB)
    ma, sa, mb, sb = 0.0, 1.0, 1.0, 2.0
    W2 = (ma - mb) ** 2 + (sa - sb) ** 2
    f = Fig(c, (56, 42, 300, 210), (-3, 2), (-8, 1))
    box_axes(f, xticks=[-3, -2, -1, 0, 1, 2], yticks=[-8, -6, -4, -2, 0], xfmt=lambda t: {-3: "0.001", -2: "0.01", -1: "0.1", 0: "1", 1: "10", 2: "100"}[t],
             yfmt=lambda t: "1" if t == 0 else f"1e{t:g}", xlabel="ε")
    es = np.linspace(-3, 2, 160)
    f.path([(e, math.log10(L_gauss(ma, sa, mb, sb, 10 ** e) - W2)) for e in es], "ln c2")
    f.path([(e, math.log10(abs(S_gauss(ma, sa, mb, sb, 10 ** e) - W2))) for e in es], "ln c3")
    f.path(clipped([(e, math.log10(10 ** (2 * e) / 128)) for e in es], (-8, 1)), "ln c3 thin dash")
    f.text(-2.9, -1.3, "raw: Lε − W₂²", "tx-s t2", "start")
    f.text(-1.0, -5.2, "debiased: |Sε − W₂²|", "tx-s t3", "start")
    f.text(-0.35, -7.3, "dashed: ε²/128 (slope 2)", "tx-s t3", "start")
    c.text(206, 16, "N(0,1) against N(1,4): bias as a function of ε", "tx-b", "middle")
    c.text(60, 34, "error (log scale)", "tx-s", "start")
    # right: best width s for the raw and debiased losses, alpha = N(0,1), beta = N(0,s^2)
    g = Fig(c, (436, 42, 200, 210), (0, 3), (0, 1.15))
    g.axes(xticks=[0, 1, 2, 3], yticks=[0, 0.25, 0.5, 0.75, 1.0], xfmt=lambda t: f"{t:g}", yfmt=lambda t: f"{t:g}", xlabel="ε")
    es2 = np.linspace(0.001, 3, 160)
    g.path([(e, math.sqrt(max(1 - e / 2, 0))) for e in es2], "ln c2")
    g.line(0, 1, 3, 1, "ln c3")
    g.text(0.1, 1.0, "Sinkhorn divergence: s = 1", "tx-s t3", "start", dy=-6)
    g.text(0.35, 0.42, "raw loss: s = √(1 − ε/2)", "tx-s t2", "start")
    g.text(2.05, 0.04, "collapse to δ₀", "tx-s t2", "start", dy=-4)
    c.text(536, 16, "best fit N(0, s²) of N(0, 1)", "tx-b", "middle")
    c.text(440, 34, "best width s", "tx-s", "start")
    c.save()


def samples_data():
    """Null experiment: two independent samples of N(0, I_d); W2 (exact, POT), sqrt of the Sinkhorn divergence
    (log-domain Sinkhorn, symmetric averaged updates for the self terms) and MMD (Gaussian kernel, bandwidth^2 = d).
    The result is cached in figures/L07/_samples.json (the computation takes a few minutes)."""
    path = os.path.join(HERE, "figures", SUB, "_samples.json")
    if os.path.exists(path):
        return json.load(open(path))
    import ot
    rng = np.random.default_rng(2026)

    def value(X, Y, eps, sym=False):
        n, m = len(X), len(Y)
        C = ((X[:, None, :] - Y[None, :, :]) ** 2).sum(-1)
        la, lb = -np.log(n) * np.ones(n), -np.log(m) * np.ones(m)
        f = np.zeros(n); g = np.zeros(m)
        for it in range(2000):
            if sym:
                fn = -eps * logsumexp(lb[None, :] + (f[None, :] - C) / eps, axis=1); f = 0.5 * (f + fn); g = f
            else:
                f = -eps * logsumexp(lb[None, :] + (g[None, :] - C) / eps, axis=1)
                g = -eps * logsumexp(la[:, None] + (f[:, None] - C) / eps, axis=0)
            if it % 10 == 9:
                P = np.exp(la[:, None] + lb[None, :] + (f[:, None] + g[None, :] - C) / eps)
                if np.abs(P.sum(1) - 1 / n).sum() < 1e-9: break
        return f.mean() + g.mean()

    def mmd(X, Y, s2):
        k = lambda A, B: np.exp(-((A[:, None, :] - B[None, :, :]) ** 2).sum(-1) / (2 * s2))
        return math.sqrt(max(k(X, X).mean() + k(Y, Y).mean() - 2 * k(X, Y).mean(), 0))

    ns = [16, 32, 64, 128, 256, 512]; out = {}
    for d, epss in [(6, [3.0, 0.3]), (2, [0.2])]:
        res = {"W2": [], "MMD": []}
        for e in epss: res[f"S{e}"] = []
        for n in ns:
            vals = {k: [] for k in res}
            for r in range(24 if n <= 128 else 12):
                X = rng.standard_normal((n, d)); Y = rng.standard_normal((n, d))
                vals["W2"].append(math.sqrt(ot.emd2(np.ones(n) / n, np.ones(n) / n, ot.dist(X, Y))))
                vals["MMD"].append(mmd(X, Y, d))
                for e in epss:
                    s = value(X, Y, e) - 0.5 * value(X, X, e, True) - 0.5 * value(Y, Y, e, True)
                    vals[f"S{e}"].append(math.sqrt(max(s, 0)))
            for k in res: res[k].append(float(np.median(vals[k])))
        slopes = {k: float(np.polyfit(np.log(ns), np.log(res[k]), 1)[0]) for k in res}
        out[str(d)] = {"ns": ns, "res": res, "slopes": slopes, "eps": epss}
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(out, open(path, "w"), indent=1)
    return out


def fig_samples():
    D = samples_data()
    c = Canvas("samples", 660, 330, "Null experiment: W2, Sinkhorn divergence and MMD between two samples of the same Gaussian", sub=SUB)
    for k, d in enumerate(["6", "2"]):
        R = D[d]; ns = np.array(R["ns"])
        x0 = 56 + k * 330
        f = Fig(c, (x0, 36, 250, 190), (math.log10(12), math.log10(700)), (math.log10(0.03), math.log10(3.2)))
        box_axes(f, xticks=[math.log10(v) for v in [16, 64, 256]], yticks=[math.log10(v) for v in [0.03, 0.1, 0.3, 1, 3]],
                 xfmt=lambda t: f"{10 ** t:.0f}", yfmt=lambda t: f"{10 ** t:g}", xlabel="sample size n")
        series = [("W2", "c2", "W₂")]
        Skeys = [key for key in R["res"] if key.startswith("S")]
        cols = ["c3", "c5"]
        for i, key in enumerate(Skeys):
            series.append((key, cols[i], f"√Sε, ε = {float(key[1:]):g}"))
        series.append(("MMD", "c1", "MMD"))
        for key, cls, lab in series:
            ys = np.array(R["res"][key])
            f.path([(math.log10(n), math.log10(y)) for n, y in zip(ns, ys)], f"ln {cls} thin")
            for n, y in zip(ns, ys):
                f.circle(math.log10(n), math.log10(y), 2.6, "f" + cls[1])
        for i, (key, cls, lab) in enumerate(series):
            y = 272 + 14 * i
            c.add(f'<line x1="{x0 + 10}" y1="{y - 4}" x2="{x0 + 28}" y2="{y - 4}" class="ln {cls} thin"/>')
            c.text(x0 + 34, y, f"{lab}: slope {R['slopes'][key]:.2f}", "tx-s", "start")
        c.text(x0 + 125, 22, f"dimension d = {d}", "tx-b", "middle")
    c.save()


def fig_unbalanced():
    c = Canvas("unbalanced", 660, 240, "Unbalanced entropic transport for a small and a large marginal penalty", sub=SUB)
    n = 60; t = (np.arange(n) + 0.5) / n
    def mix(w1, m1, w2, m2):
        g1, g2 = np.exp(-(t - m1) ** 2 / 0.005), np.exp(-(t - m2) ** 2 / 0.005)
        return w1 * g1 / g1.sum() + w2 * g2 / g2.sum()
    a, b = mix(0.7, 0.3, 0.3, 0.7), mix(0.3, 0.35, 0.7, 0.75)
    C = (t[:, None] - t[None, :]) ** 2; eps = 0.002
    lK = -C / eps + np.log(a)[:, None] + np.log(b)[None, :]
    out = {}
    for k, tau in enumerate([0.05, 1.0, np.inf]):
        w = 1.0 if tau == np.inf else tau / (tau + eps)
        lu, lv = np.zeros(n), np.zeros(n)
        for it in range(200000):
            lun = w * (np.log(a) - logsumexp(lK + lv[None, :], axis=1))
            lvn = w * (np.log(b) - logsumexp(lK + lun[:, None], axis=0))
            done = max(np.abs(lun - lu).max(), np.abs(lvn - lv).max()) < 1e-11
            lu, lv = lun, lvn
            if done: break
        P = np.exp(lK + lu[:, None] + lv[None, :])
        x0, y0, S = 46 + k * 210, 40, 140
        heatmap(c, P, x0, y0, S, S, levels=12)
        r, s = P.sum(1), P.sum(0)
        # prescribed (light fill) and transported (line) marginals
        vmax = max(a.max(), b.max())
        def prof(v, vert, cls, fill):
            pts = []
            for i in range(n):
                if vert: pts.append((x0 - 2 - v[i] / vmax * 26, y0 + (i + 0.5) / n * S))
                else: pts.append((x0 + (i + 0.5) / n * S, y0 - 2 - v[i] / vmax * 26))
            d = "M" + "L".join(f"{px:.1f} {py:.1f}" for px, py in pts)
            if fill:
                base = (f"L{x0 - 2:.1f} {y0 + S:.1f}L{x0 - 2:.1f} {y0:.1f}Z" if vert else f"L{x0 + S:.1f} {y0 - 2:.1f}L{x0:.1f} {y0 - 2:.1f}Z")
                c.add(f'<path d="{d}{base}" class="{cls}"/>')
            else:
                c.add(f'<path d="{d}" class="{cls}"/>')
        prof(a, True, "a2", True); prof(r, True, "ln c2 thin", False)
        prof(b, False, "a1", True); prof(s, False, "ln c1 thin", False)
        lab = "τ = ∞ (balanced)" if tau == np.inf else f"τ = {tau:g}"
        c.text(x0 + S / 2, y0 + S + 18, lab, "tx-b", "middle")
        moved = P[t < 0.5][:, t >= 0.5].sum()
        c.text(x0 + S / 2, y0 + S + 33, f"mass {P.sum():.3f}, left → right {moved:.3f}", "tx-s", "middle")
        out[str(tau)] = (float(P.sum()), float(moved))
    c.save()
    return out


if __name__ == "__main__":
    print("penalty: x_eps(0.5) on the grid =", fig_penalty())
    fig_path()
    print("scaling:", fig_scaling())
    print("projections:", fig_projections())
    fig_softmin()
    print("hilbert:", fig_hilbert())
    fig_gauss()
    fig_bias()
    fig_samples()
    print("unbalanced:", fig_unbalanced())
