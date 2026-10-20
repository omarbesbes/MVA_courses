"""figures_L05.py — static SVG figures of Lesson 5 (sliced optimal transport), written to figures/L05/.

Run: python3 figures_L05.py        (then node build.mjs Lesson05.html)

Every coordinate is computed here (numpy and scipy only). The experiments (Monte Carlo errors, sample rates,
sliced flow) use fixed seeds; the numbers quoted in the text of the page are printed by this script.
"""
import math

import numpy as np
from scipy.optimize import linear_sum_assignment

from figures_common import Canvas, Fig, fmt1

SUB = "L05"


# ---------------------------------------------------------------------------------------------
# helpers
def arc(c, x0, x1, y, h, k, cls=None):
    """A curved arrow above the line y (pixel coordinates), from x0 to x1, colour index k."""
    mid = c.arrow_marker(k)
    cls = cls or f"ln c{k} thin"
    xm = (x0 + x1) / 2
    c.add(f'<path d="M{x0:.1f} {y:.1f} Q{xm:.1f} {y - 2 * h:.1f} {x1:.1f} {y:.1f}" class="{cls}" marker-end="url(#{mid})"/>')


def logfig(c, box, xr, yr):
    """A Fig whose data coordinates are log10 of the plotted values."""
    return Fig(c, box, (math.log10(xr[0]), math.log10(xr[1])), (math.log10(yr[0]), math.log10(yr[1])))


def log_axes(f, xt, yt, xlab=None, ylab=None, yfmt=None):
    for v in xt:
        lv = math.log10(v)
        f.line(lv, f.yr[0], lv, f.yr[1], "gr")
        f.text(lv, f.yr[0], f"{v:g}", "tx-s", "middle", dy=14)
    for v in yt:
        lv = math.log10(v)
        f.line(f.xr[0], lv, f.xr[1], lv, "gr")
        f.text(f.xr[0], lv, yfmt(v) if yfmt else f"{v:g}", "tx-s", "end", dx=-5, dy=4)
    f.line(f.xr[0], f.yr[0], f.xr[1], f.yr[0], "ax")
    f.line(f.xr[0], f.yr[0], f.xr[0], f.yr[1], "ax")
    if xlab:
        f.text(f.xr[1], f.yr[0], xlab, "tx-s", "end", dy=28)
    if ylab:
        f.text(f.xr[0], f.yr[1], ylab, "tx-s", "start", dx=4, dy=-6)


def sup(e):
    return "10" + "".join("⁻⁰¹²³⁴⁵⁶⁷⁸⁹"["-0123456789".index(ch)] for ch in str(e))


def w22_1d(u, v):
    return float(np.mean((np.sort(u) - np.sort(v)) ** 2))


def profile(A, B, phis):
    return np.array([w22_1d(A @ [math.cos(p), math.sin(p)], B @ [math.cos(p), math.sin(p)]) for p in phis])


def kappa(d, p):
    return math.exp(math.lgamma(d / 2) + math.lgamma((p + 1) / 2) - 0.5 * math.log(math.pi) - math.lgamma((d + p) / 2))


# ---------------------------------------------------------------------------------------------
def fig_sort1d():
    c = Canvas("sort1d", 660, 262, "Optimal transport on the line: sort both clouds and match the i-th smallest points", sub=SUB)
    x = [0, 3, 5, 6]
    y = [1, 2, 4, 9]
    f = Fig(c, (24, 40, 370, 150), (-0.6, 9.6), (-1, 1))
    f.line(-0.6, 0, 9.6, 0, "ax")
    for v in range(0, 10):
        f.line(v, -0.04, v, 0.04, "ax")
        f.text(v, 0, str(v), "tx-s", "middle", dy=30)
    for xi, yi in zip(sorted(x), sorted(y)):
        arc(c, f.X(xi), f.X(yi) + (-4 if yi > xi else 4), f.Y(0) - 7, 10 + 7 * abs(yi - xi), 3)
    for k, v in enumerate(sorted(x)):
        f.circle(v, 0, 6, "f2")
        f.text(v, 0, f"x₍{'₁₂₃₄'[k]}₎", "tx-s t2", "middle", dy=18)
    for k, v in enumerate(sorted(y)):
        f.circle(v, 0, 6, "f1")
        f.text(v, 0, f"y₍{'₁₂₃₄'[k]}₎", "tx-s t1", "middle", dy=18)
    c.text(209, 22, "match by rank: 0→1, 3→2, 5→4, 6→9", "tx-b", "middle")
    c.text(209, 236, "W₂² = (1² + 1² + 1² + 3²)/4 = 3   (the 23 other matchings cost more)", "tx-s", "middle")
    # quantile functions
    g = Fig(c, (452, 34, 186, 160), (0, 1), (0, 9.5))
    g.axes(xticks=[0, 0.25, 0.5, 0.75, 1], yticks=[0, 3, 6, 9], xfmt=fmt1, grid=True, xlabel="t")
    for k in range(4):
        a, b = k / 4, (k + 1) / 4
        lo, hi = sorted([sorted(x)[k], sorted(y)[k]])
        g.path([(a, lo), (b, lo), (b, hi), (a, hi)], "a3", close=True)
    for vals, k in [(sorted(x), 2), (sorted(y), 1)]:
        pts = []
        for i, v in enumerate(vals):
            pts += [(i / 4, v), ((i + 1) / 4, v)]
        g.path(pts, f"ln c{k}")
    c.text(545, 22, "quantile functions Fα⁻¹, Fβ⁻¹", "tx-b", "middle")
    c.text(545, 252, "green area = ∫|Fα⁻¹ − Fβ⁻¹| = W₁ = 1.5", "tx-s t3", "middle")
    c.save()


def fig_slice():
    c = Canvas("slice", 660, 290, "Slicing a three-point cloud: project every point on the line spanned by theta", sub=SUB)
    X = np.array([[0, 0], [2, 1], [1, 3.0]])
    th = np.array([0.6, 0.8])
    f = Fig(c, (34, 30, 228, 236), (-0.62, 3.1), (-0.45, 3.42))
    for v in range(0, 4):
        f.text(v, -0.45, str(v), "tx-s", "middle", dy=14)
        f.line(v, -0.45, v, 3.42, "gr")
        f.line(-0.62, v, 3.1, v, "gr")
        f.text(-0.62, v, str(v), "tx-s", "end", dx=-4, dy=4)
    t0, t1 = -0.55, 4.15
    f.line(t0 * th[0], t0 * th[1], t1 * th[0], t1 * th[1], "ln c3")
    for i, p in enumerate(X):
        t = float(p @ th)
        q = t * th
        f.line(p[0], p[1], q[0], q[1], "ln cm thin dash")
        f.circle(q[0], q[1], 4.5, "f3")
        f.circle(p[0], p[1], 6, "f2")
        f.text(p[0], p[1], f"x{'₁₂₃'[i]}", "tx-b t2", "start", dx=8, dy=(14 if i == 0 else -6))
        if t > 0:  # x3's dashed projection line runs up-left from its foot: put that label on the right
            if i == 2:
                f.text(q[0], q[1], f"⟨θ, x{'₁₂₃'[i]}⟩ = {t:g}", "tx-s t3", "start", dx=9, dy=12)
            else:
                f.text(q[0], q[1], f"⟨θ, x{'₁₂₃'[i]}⟩ = {t:g}", "tx-s t3", "end", dx=-8, dy=-2)
    c.arrow(f.X(0), f.Y(0), f.X(0.6 * 0.95), f.Y(0.8 * 0.95), 3, "ln c3")
    f.text(0.55, 0.62, "θ", "tx-i", "start", dx=6, dy=8)
    c.text(148, 18, "θ = (3/5, 4/5); ⟨θ, x₁⟩ = 0", "tx-b", "middle")
    # right: the slices as measures on the line
    rows = [((3 / 5, 4 / 5), "slice along θ = (3/5, 4/5): ⅓(δ₀ + δ₂ + δ₃)"),
            ((1 / math.sqrt(5), -2 / math.sqrt(5)), "along θ′ = (1, −2)/√5: x₁ and x₂ collide")]
    for r, (t, title) in enumerate(rows):
        g = Fig(c, (330, 40 + r * 128, 300, 70), (-2.8, 3.6), (0, 0.75))
        g.line(-2.8, 0, 3.6, 0, "ax")
        for v in range(-2, 4):
            g.line(v, -0.02, v, 0.02, "ax")
            g.text(v, 0, str(v), "tx-s", "middle", dy=14)
        proj = X @ np.array(t)
        vals, counts = np.unique(np.round(proj, 9), return_counts=True)
        for v, k in zip(vals, counts):
            m = k / 3
            g.lollipop(v, m, 2)
            lab = "⅓" if k == 1 else "⅔"
            g.text(v, m, lab, "tx-s t2", "middle", dy=-9)
        c.text(480, 26 + r * 128, title, "tx-b", "middle")
    c.text(480, 282, "the weights travel with their points, and add up when points collide", "tx-s", "middle")
    c.save()


def gauss1(x, m, s):
    return np.exp(-0.5 * ((x - m) / s) ** 2) / (s * math.sqrt(2 * math.pi))


def fig_radon():
    c = Canvas("radon", 660, 300, "Slices of densities: the uniform disk and a two-bump density", sub=SUB)
    # A: the disk and a chord
    f = Fig(c, (14, 40, 170, 170), (-1.3, 1.3), (-1.3, 1.3))
    circ = [(math.cos(a), math.sin(a)) for a in np.linspace(0, 2 * math.pi, 241)]
    f.path(circ, "a2", close=True)
    f.path(circ, "ln c2 thin", close=True)
    ph = math.radians(30)
    th = np.array([math.cos(ph), math.sin(ph)])
    pe = np.array([-th[1], th[0]])
    f.line(-1.28 * th[0], -1.28 * th[1], 1.28 * th[0], 1.28 * th[1], "ln c3")
    c.arrow(f.X(0), f.Y(0), f.X(0.55 * th[0]), f.Y(0.55 * th[1]), 3, "ln c3")
    s = 0.5
    h = math.sqrt(1 - s * s)
    a, b = s * th + h * pe, s * th - h * pe
    f.line(a[0], a[1], b[0], b[1], "ln c5")
    f.circle(s * th[0], s * th[1], 3.5, "f3")
    f.text(a[0], a[1], "⟨θ, x⟩ = s", "tx-s t5", "middle", dy=-8)
    f.text(1.28 * th[0], 1.28 * th[1], "θ", "tx-i", "start", dx=4)
    c.text(99, 26, "uniform disk, density 1/π", "tx-b", "middle")
    c.text(99, 236, "chord length 2√(1 − s²)", "tx-s t5", "middle")
    # B: the slice density
    g = Fig(c, (200, 64, 140, 110), (-1.15, 1.15), (0, 0.72))
    g.line(-1.15, 0, 1.15, 0, "ax")
    for v in [-1, 0, 1]:
        g.text(v, 0, str(v), "tx-s", "middle", dy=14)
    sv = np.linspace(-1, 1, 201)
    dens = [(u, 2 / math.pi * math.sqrt(max(0.0, 1 - u * u))) for u in sv]
    g.path([(-1, 0)] + dens + [(1, 0)], "a2", close=True)
    g.path(dens, "ln c2")
    g.line(s, 0, s, 2 / math.pi * h, "ln c5 thin")
    g.text(s, 2 / math.pi * h, f"{2 / math.pi * h:.3f}", "tx-s t5", "start", dx=4, dy=-2)
    c.text(270, 44, "slice density (2/π)√(1 − s²)", "tx-b", "middle")
    c.text(270, 200, "the same for every θ", "tx-s", "middle")
    c.text(270, 214, "(mean 0, variance ¼)", "tx-s", "middle")
    # C: a two-bump density and three slices
    m1, m2, sd = np.array([-1.0, -0.3]), np.array([0.9, 0.6]), 0.35
    k = Fig(c, (370, 50, 150, 150), (-1.9, 1.9), (-1.9, 1.9))
    for m in (m1, m2):
        for r, cls in [(2 * sd, "a2"), (sd, "a2")]:
            k.path([(m[0] + r * math.cos(t), m[1] + r * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 121)], cls, close=True)
        k.circle(m[0], m[1], 2.5, "f2")
    base = math.degrees(math.atan2(m2[1] - m1[1], m2[0] - m1[0]))
    angles = [base, base + 45, base + 90]
    for j, a in enumerate(angles):
        t = np.array([math.cos(math.radians(a)), math.sin(math.radians(a))])
        k.line(-1.85 * t[0], -1.85 * t[1], 1.85 * t[0], 1.85 * t[1], "ln c3 thin")
        k.text(1.85 * t[0], 1.85 * t[1], str(j + 1), "tx-b t3", "middle", dx=5 * t[0], dy=-5 * t[1] + 4)
    c.text(445, 30, "a two-bump density α", "tx-b", "middle")
    c.text(445, 228, f"directions at {angles[0]:.0f}°, {angles[1]:.0f}°, {angles[2]:.0f}°", "tx-s", "middle")
    for j, a in enumerate(angles):
        t = np.array([math.cos(math.radians(a)), math.sin(math.radians(a))])
        p1, p2 = float(t @ m1), float(t @ m2)
        g2 = Fig(c, (540, 36 + j * 80, 110, 46), (-2.4, 2.4), (0, 1.25))
        g2.line(-2.4, 0, 2.4, 0, "ax")
        u = np.linspace(-2.4, 2.4, 241)
        dd = 0.5 * gauss1(u, p1, sd) + 0.5 * gauss1(u, p2, sd)
        g2.path([(-2.4, 0)] + list(zip(u, dd)) + [(2.4, 0)], "a2", close=True)
        g2.path(list(zip(u, dd)), "ln c2 thin")
        g2.text(-2.4, 1.25, f"slice {j + 1}", "tx-s t3", "start", dy=8)
    c.text(330, 290, "left: one chord per value s; right: each direction sees a different one-dimensional picture of α", "tx-s", "middle")
    c.save()


def fig_profile():
    c = Canvas("profile", 660, 260, "The cross: per-direction cost 1 - |sin 2 phi|, its average and its maximum", sub=SUB)
    f = Fig(c, (20, 36, 170, 170), (-1.45, 1.45), (-1.45, 1.45))
    f.line(-1.45, 0, 1.45, 0, "gr")
    f.line(0, -1.45, 0, 1.45, "gr")
    ph = math.radians(25)
    th = np.array([math.cos(ph), math.sin(ph)])
    f.line(-1.4 * th[0], -1.4 * th[1], 1.4 * th[0], 1.4 * th[1], "ln c3 thin")
    for p in [(-1, 0), (1, 0)]:
        q = (p[0] * th[0]) * th
        f.line(p[0], p[1], q[0], q[1], "ln c2 thin dot")
        f.circle(q[0], q[1], 3.5, "f2")
        f.circle(p[0], p[1], 6, "f2")
    for p in [(0, -1), (0, 1)]:
        q = (p[1] * th[1]) * th
        f.line(p[0], p[1], q[0], q[1], "ln c1 thin dot")
        f.circle(q[0], q[1], 3.5, "f1")
        f.circle(p[0], p[1], 6, "f1")
    f.text(1.4 * th[0], 1.4 * th[1], "θ", "tx-i", "start", dx=3, dy=2)
    f.text(1, 0, "α", "tx-i", "middle", dx=2, dy=20)
    f.text(0, 1, "β", "tx-i", "start", dx=9, dy=4)
    c.text(105, 22, "α = ½(δ₋ₑ₁ + δₑ₁), β = ½(δ₋ₑ₂ + δₑ₂)", "tx-b", "middle")
    c.text(105, 236, "at 25°: α_θ at ±0.906, β_θ at ±0.423", "tx-s", "middle")
    g = Fig(c, (262, 34, 372, 174), (0, 180), (0, 1.08))
    g.axes(xticks=[0, 45, 90, 135, 180], yticks=[0, 0.25, 0.5, 0.75, 1], xfmt=lambda v: f"{v:g}°", yfmt=fmt1, xlabel="direction φ")
    g.fn(lambda a: 1 - abs(math.sin(2 * math.radians(a))), "ln ck", 0, 180, 720)
    sw = 1 - 2 / math.pi
    g.line(0, sw, 180, sw, "ln c3 dash")
    g.line(0, 1, 180, 1, "ln c4 dot")
    g.text(180, sw, f"average = SW₂² = 1 − 2/π ≈ {sw:.3f}", "tx-s t3", "end", dy=-6)
    g.text(135, 1, "maximum = 1 (φ = 0°, 90°, 180°)", "tx-s", "middle", dy=-6)
    v = 1 - math.sin(2 * ph)
    g.circle(25, v, 4.5, "f3")
    g.text(25, v, f"{v:.3f}", "tx-s t3", "start", dx=7, dy=4)
    c.text(448, 20, "W₂²(α_θ, β_θ) = (|cos φ| − |sin φ|)² = 1 − |sin 2φ|", "tx-b", "middle")
    c.text(448, 252, "W₂²(α, β) = 2 for comparison: every coupling costs 2", "tx-s", "middle")
    c.save()


def fig_cw():
    c = Canvas("cw", 660, 240, "Two different measures with the same projections on both coordinate axes", sub=SUB)
    A = np.array([[0, 0], [1, 1.0]])
    B = np.array([[1, 0], [0, 1.0]])
    f = Fig(c, (24, 40, 150, 150), (-0.35, 1.35), (-0.35, 1.35))
    for v in [0, 1]:
        f.line(v, -0.35, v, 1.35, "gr")
        f.line(-0.35, v, 1.35, v, "gr")
        f.text(v, -0.35, str(v), "tx-s", "middle", dy=14)
        f.text(-0.35, v, str(v), "tx-s", "end", dx=-4, dy=4)
    for p in A:
        f.circle(p[0], p[1], 7, "f2")
    for p in B:
        f.circle(p[0], p[1], 7, "f1")
    c.text(99, 24, "α (orange-red), β (blue)", "tx-b", "middle")
    # projections on e1, e2 and the diagonal
    rows = [("on e₁: both ½(δ₀ + δ₁)", np.array([1, 0.0])), ("on e₂: both ½(δ₀ + δ₁)", np.array([0, 1.0])),
            ("on (1,1)/√2: different", np.array([1, 1.0]) / math.sqrt(2))]
    for r, (lab, t) in enumerate(rows):
        g = Fig(c, (210, 40 + r * 58, 150, 30), (-0.2, 1.6), (-1, 1))
        g.line(-0.2, 0, 1.6, 0, "ax")
        pa, pb = A @ t, B @ t
        for vals, yy, k in [(pa, 0.35, 2), (pb, -0.35, 1)]:
            u, cnt = np.unique(np.round(vals, 9), return_counts=True)
            for v, m in zip(u, cnt):
                g.circle(v, yy, round(3 + 3 * math.sqrt(m), 1), f"f{k}")
        for v in [0, 1]:
            g.text(v, -1, str(v), "tx-s", "middle", dy=10)
        c.text(285, 34 + r * 58, lab, "tx-s", "middle")
    c.text(285, 226, "diagonal: atoms 0 and √2 versus one atom at 1/√2", "tx-s", "middle")
    h = Fig(c, (412, 34, 228, 156), (0, 180), (0, 0.55))
    h.axes(xticks=[0, 45, 90, 135, 180], yticks=[0, 0.25, 0.5], xfmt=lambda v: f"{v:g}°", yfmt=fmt1, xlabel="φ")
    h.fn(lambda a: min(math.cos(math.radians(a)) ** 2, math.sin(math.radians(a)) ** 2), "ln ck", 0, 180, 720)
    sw = 0.5 - 1 / math.pi
    h.line(0, sw, 180, sw, "ln c3 dash")
    c.text(526, 22, "W₂²(α_θ, β_θ) = min(cos²φ, sin²φ)", "tx-b", "middle")
    c.text(526, 38, f"dashed: the average SW₂² = ½ − 1/π ≈ {sw:.3f}", "tx-s t3", "middle")
    c.text(526, 226, "zero exactly at φ = 0°, 90°, 180°", "tx-s", "middle")
    c.save()


def fig_kappa():
    c = Canvas("kappa", 600, 300, "The comparison constant kappa_{d,p} as a function of the dimension, log-log", sub=SUB)
    f = logfig(c, (60, 20, 500, 230), (1, 100), (1e-4, 1.2))
    log_axes(f, [1, 2, 5, 10, 20, 50, 100], [1e-4, 1e-3, 1e-2, 0.1, 1], xlab="dimension d", ylab="κ_d,p", yfmt=lambda v: sup(round(math.log10(v))) if v < 1 else "1")
    ds = np.logspace(0, 2, 200)
    for p, k in [(1, 2), (2, 1), (4, 5)]:
        f.path([(math.log10(d), math.log10(kappa(d, p))) for d in ds], f"ln c{k}")
    f.path([(math.log10(d), math.log10(math.sqrt(2 / (math.pi * d)))) for d in ds if d >= 4], "ln cm thin dot")
    f.text(math.log10(60), math.log10(kappa(60, 1)), "p = 1", "tx-b t2", "start", dy=-8)
    f.text(math.log10(60), math.log10(kappa(60, 2)), "p = 2: κ = 1/d", "tx-b t1", "start", dy=-8)
    f.text(math.log10(40), math.log10(kappa(40, 4)), "p = 4", "tx-b t5", "start", dy=-8)
    f.text(math.log10(25), math.log10(math.sqrt(2 / (math.pi * 25))), "dotted: √(2/(πd))", "tx-s", "start", dx=4, dy=-12)
    for d in [3]:
        for p, k in [(1, 2), (2, 1), (4, 5)]:
            f.circle(math.log10(d), math.log10(kappa(d, p)), 4, f"f{k}")
    f.text(math.log10(3), math.log10(kappa(3, 4)), "d = 3: κ = 1/(p + 1)", "tx-s", "end", dx=-8, dy=14)
    c.text(310, 292, "κ_d,p = ∫|θ₁|ᵖ dσ(θ): SW_pᵖ ≤ κ_d,p W_pᵖ, with equality for translations", "tx-s", "middle")
    c.save()


def fig_sphere():
    c = Canvas("sphere", 660, 260, "Sampling directions: the right way and two wrong ways", sub=SUB)
    f = Fig(c, (46, 64, 260, 140), (0, 360), (0, 0.27))
    f.axes(xticks=[0, 90, 180, 270, 360], yticks=[0, 0.1, 0.2], xfmt=lambda v: f"{v:g}°", yfmt=fmt1, xlabel="angle φ")
    f.line(0, 1 / (2 * math.pi), 360, 1 / (2 * math.pi), "ln c3")

    def cube(a):
        a = math.radians(a) % (math.pi / 2)
        a = a if a <= math.pi / 4 else math.pi / 2 - a
        return 1 / (8 * math.cos(a) ** 2)
    f.fn(cube, "ln c2", 0, 360, 720)
    c.text(46, 40, "green: G/‖G‖, G Gaussian (uniform, 1/(2π))", "tx-s t3")
    c.text(46, 54, "red: U/‖U‖, U uniform in a square", "tx-s t2")
    c.text(176, 20, "in the plane: density of the angle φ", "tx-b", "middle")
    g = Fig(c, (390, 64, 250, 140), (-1, 1), (0, 1.6))
    g.axes(xticks=[-1, -0.5, 0, 0.5, 1], yticks=[0, 0.5, 1, 1.5], xfmt=fmt1, yfmt=fmt1, xlabel="height z = θ₃")
    g.line(-1, 0.5, 1, 0.5, "ln c3")
    zc = math.sqrt(1 - (1 / (1.6 * math.pi)) ** 2)
    g.fn(lambda z: 1 / (math.pi * math.sqrt(max(1e-12, 1 - z * z))), "ln c2", -zc, zc, 600)
    c.text(390, 40, "green: uniform on the sphere, density ½", "tx-s t3")
    c.text(390, 54, "red: uniform polar angle, 1/(π√(1 − z²))", "tx-s t2")
    c.text(515, 20, "in space: density of the height", "tx-b", "middle")
    c.text(330, 252, "P(|θ₃| > 0.9): 0.100 for the uniform law, 0.287 with a uniform polar angle", "tx-s", "middle")
    c.save()


def fig_mcerror():
    c = Canvas("mcerror", 600, 300, "Monte Carlo error of the sliced estimate against the number of directions, log-log", sub=SUB)
    rng = np.random.default_rng(12345)
    SW = 1 - 2 / math.pi
    VAR = 0.5 - 4 / math.pi ** 2
    Ks = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
    mae = []
    for K in Ks:
        ph = rng.uniform(0, 2 * math.pi, size=(4000, K))
        est = (1 - np.abs(np.sin(2 * ph))).mean(1)
        mae.append(float(np.mean(np.abs(est - SW))))
    print("mcerror: K, mean|err|, sqrt(Var/K), Var/K")
    for K, m in zip(Ks, mae):
        print(f"   {K:5d}  {m:.3e}  {math.sqrt(VAR / K):.3e}  {VAR / K:.3e}")
    f = logfig(c, (66, 20, 490, 230), (1, 1024), (5e-5, 0.6))
    log_axes(f, [1, 4, 16, 64, 256, 1024], [1e-4, 1e-3, 1e-2, 0.1], xlab="number of directions K", ylab="error",
             yfmt=lambda v: sup(round(math.log10(v))))
    Kc = np.logspace(0, math.log10(1024), 100)
    f.path([(math.log10(K), math.log10(math.sqrt(VAR / K))) for K in Kc], "ln c3")
    f.path([(math.log10(K), math.log10(VAR / K)) for K in Kc], "ln cm dash")
    f.path([(math.log10(K), math.log10(m)) for K, m in zip(Ks, mae)], "ln c2 thin")
    for K, m in zip(Ks, mae):
        f.circle(math.log10(K), math.log10(m), 4, "f2")
    f.text(math.log10(24), math.log10(math.sqrt(VAR / 24)), "√(Var/K): the correct bound", "tx-s t3", "start", dy=-12)
    # labels below descending lines are anchored at their right end, where the line is lowest
    f.text(math.log10(1024), math.log10(mae[-1]), "dots: measured mean |error|", "tx-s t2", "end", dx=-2, dy=20)
    f.text(math.log10(256), math.log10(VAR / 256), "Var/K (printed on the slides): too small", "tx-s", "end", dx=-2, dy=16)
    c.text(310, 292, "the cross of §4: SW₂² = 1 − 2/π, Var = ½ − 4/π² ≈ 0.0947; 4000 runs per K", "tx-s", "middle")
    c.save()
    return Ks, mae


def w2_exact(X, Y):
    C = ((X[:, None, :] - Y[None, :, :]) ** 2).sum(-1)
    r, k = linear_sum_assignment(C)
    return math.sqrt(C[r, k].mean())


def sw2_mc(X, Y, L, rng):
    G = rng.standard_normal((L, X.shape[1]))
    T = G / np.linalg.norm(G, axis=1, keepdims=True)
    px = np.sort(X @ T.T, axis=0)
    py = np.sort(Y @ T.T, axis=0)
    return math.sqrt(((px - py) ** 2).mean())


def fig_rates():
    c = Canvas("rates", 600, 320, "W2 and SW2 between two independent samples of the same standard Gaussian, log-log", sub=SUB)
    rng = np.random.default_rng(2026)
    ns = [10, 20, 50, 100, 200, 500, 1000]
    dims = [(2, 2), (10, 1), (50, 5)]
    reps = 8
    res = {}
    print("rates: d, n, mean W2, mean SW2 (500 directions), over", reps, "pairs")
    for d, _ in dims:
        for n in ns:
            w, s = [], []
            for _ in range(reps):
                X = rng.standard_normal((n, d))
                Y = rng.standard_normal((n, d))
                w.append(w2_exact(X, Y))
                s.append(sw2_mc(X, Y, 500, rng))
            res[(d, n)] = (float(np.mean(w)), float(np.mean(s)))
            print(f"   d={d:3d} n={n:5d}  W2={res[(d, n)][0]:.4f}  SW2={res[(d, n)][1]:.4f}")
    for d, _ in dims:
        lw = math.log(res[(d, 1000)][0] / res[(d, 50)][0]) / math.log(20)
        ls = math.log(res[(d, 1000)][1] / res[(d, 50)][1]) / math.log(20)
        print(f"   slopes between n=50 and 1000, d={d}: W2 {lw:.3f}, SW2 {ls:.3f}")
    f = logfig(c, (60, 20, 410, 250), (10, 1000), (0.05, 15))
    log_axes(f, [10, 20, 50, 100, 200, 500, 1000], [0.1, 0.2, 0.5, 1, 2, 5, 10], xlab="sample size n", ylab="distance")
    for d, k in dims:
        f.path([(math.log10(n), math.log10(res[(d, n)][0])) for n in ns], f"ln c{k}")
        f.path([(math.log10(n), math.log10(res[(d, n)][1])) for n in ns], f"ln c{k} dash")
        for n in ns:
            f.circle(math.log10(n), math.log10(res[(d, n)][0]), 3, f"f{k}")
        f.text(math.log10(1000), math.log10(res[(d, 1000)][0]), f"W₂, d = {d}", f"tx-b t{k}", "start", dx=8, dy=4)
    f.text(math.log10(1000), math.log10(res[(10, 1000)][1]), "SW₂, d = 2, 10, 50", "tx-b", "start", dx=8, dy=4)
    f.path([(math.log10(n), math.log10(0.9 * n ** -0.5 * 2.6)) for n in [10, 1000]], "ln cm thin dot")
    f.text(math.log10(25), math.log10(0.9 * 25 ** -0.5 * 2.6), "slope −½", "tx-s", "start", dx=6, dy=-6)
    c.text(300, 312, f"means over {reps} pairs; W₂ exact (assignment), SW₂ with 500 random directions", "tx-s", "middle")
    c.save()
    return res


def fig_lifted():
    c = Canvas("lifted", 660, 250, "Lifted plans: sort along a direction, then use the matching in the plane", sub=SUB)
    A = np.array([[0, 0], [1, 3.0]])
    B = np.array([[1, 0], [0, 3.0]])
    panels = [("optimal plan: cost 1", None), ("sort along e₁, lift: cost 9", np.array([1, 0.0])),
              ("sort along e₂, lift: cost 1", np.array([0, 1.0]))]
    for j, (title, th) in enumerate(panels):
        f = Fig(c, (46 + j * 215, 34, 150, 160), (-0.5, 1.5), (-0.4, 3.4))
        for v in [0, 1]:
            f.line(v, -0.4, v, 3.4, "gr")
            f.text(v, -0.4, str(v), "tx-s", "middle", dy=14)
        for v in [0, 3]:
            f.line(-0.5, v, 1.5, v, "gr")
            f.text(-0.5, v, str(v), "tx-s", "end", dx=-4, dy=4)
        if th is None:
            pairs = [(0, 0), (1, 1)]
        else:
            ia = np.argsort(A @ th)
            ib = np.argsort(B @ th)
            pairs = list(zip(ia, ib))
        cost = np.mean([np.sum((A[i] - B[k]) ** 2) for i, k in pairs])
        assert abs(cost - float(title.split()[-1])) < 1e-12
        for i, k in pairs:
            f.line(A[i][0], A[i][1], B[k][0], B[k][1], "ln c3")
        for p in A:
            f.circle(p[0], p[1], 6, "f2")
        for p in B:
            f.circle(p[0], p[1], 6, "f1")
        if th is not None:
            x0, y0 = f.X(1.18), f.Y(1.25)
            c.arrow(x0, y0, x0 + 26 * th[0], y0 - 26 * th[1], 3, "ln c3 thin")
            c.text(x0 + 26 * th[0] + 4, y0 - 26 * th[1] + (12 if th[0] > 0 else -4), "θ", "tx-i", "start")
        c.text(46 + j * 215 + 75, 22, title, "tx-b", "middle")
    c.text(330, 230, "α = ½(δ₍₀,₀₎ + δ₍₁,₃₎) (orange-red), β = ½(δ₍₁,₀₎ + δ₍₀,₃₎) (blue)", "tx-s", "middle")
    c.text(330, 245, "every lifted plan is a coupling, so its cost bounds W₂² = 1 from above", "tx-s", "middle")
    c.save()


def flow_data(n=60, seed=21):
    rng = np.random.default_rng(seed)
    X = np.c_[-0.55 + 0.3 * rng.standard_normal(n), 0.15 + 0.45 * rng.standard_normal(n)]
    a = rng.uniform(0, 2 * math.pi, n)
    r = 1.45 + 0.06 * rng.standard_normal(n)
    Y = np.c_[0.25 + r * np.cos(a), r * np.sin(a)]
    return X, Y


def sliced_step(X, Y, thetas, tau):
    """x_i <- x_i + tau * (d / L) * sum_l (T_l(<theta_l, x_i>) - <theta_l, x_i>) theta_l  (T_l: sorted matching)."""
    d = X.shape[1]
    V = np.zeros_like(X)
    for th in thetas:
        px, py = X @ th, Y @ th
        ix, iy = np.argsort(px), np.argsort(py)
        tgt = np.empty_like(px)
        tgt[ix] = py[iy]
        V += np.outer(tgt - px, th)
    return X + tau * d / len(thetas) * V


def fig_flow():
    c = Canvas("flow", 660, 300, "W2 flow along the optimal assignment versus sliced flow by iterated sorting", sub=SUB)
    X0, Y = flow_data()
    n = len(X0)
    C = ((X0[:, None, :] - Y[None, :, :]) ** 2).sum(-1)
    r, sig = linear_sum_assignment(C)
    rng = np.random.default_rng(3)
    traj = [X0.copy()]
    X = X0.copy()
    hist = []
    for it in range(1, 301):
        th = [np.array([math.cos(a), math.sin(a)]) for a in rng.uniform(0, 2 * math.pi, 16)]
        X = sliced_step(X, Y, th, 0.2)
        if it <= 160 and it % 2 == 0:
            traj.append(X.copy())
        if it in (10, 50, 100, 300):
            D = ((X[:, None, :] - Y[None, :, :]) ** 2).sum(-1)
            hist.append((it, float(D[linear_sum_assignment(D)].mean())))
    D = ((X[:, None, :] - Y[None, :, :]) ** 2).sum(-1)
    found = D.argmin(1)
    print(f"flow: n={n}, W2^2 start {C[r, sig].mean():.4f}; W2^2 to target after (it, value): {hist}")
    print(f"      distinct end points {len(set(found))}; agree with optimal assignment {int(np.sum(found == sig))}/{n}")
    if len(set(found)) == n:
        print(f"      cost of the matching found by the flow {np.mean(np.sum((X0 - Y[found]) ** 2, 1)):.4f} vs optimal {C[r, sig].mean():.4f}")
    for j, title in enumerate(["W₂ flow: straight lines", "sliced flow: curved paths"]):
        f = Fig(c, (16 + j * 330, 30, 300, 240), (-2.4, 2.75), (-1.85, 2.0))
        for p in Y:
            f.circle(p[0], p[1], 2.6, "f1")
        for i in range(n):
            if j == 0:
                f.line(X0[i][0], X0[i][1], Y[sig[i]][0], Y[sig[i]][1], "ln c3 hair")
            else:
                f.path([(t[i][0], t[i][1]) for t in traj], "ln c3 hair")
        for p in X0:
            f.circle(p[0], p[1], 2.8, "f2")
        c.text(16 + j * 330 + 150, 20, title, "tx-b", "middle")
    c.text(330, 292, "orange-red: 60 source points; blue: 60 target points on a ring; green: paths (sliced: 16 random directions per step)", "tx-s", "middle")
    c.save()


if __name__ == "__main__":
    for fn in [fig_sort1d, fig_slice, fig_radon, fig_profile, fig_cw, fig_kappa, fig_sphere, fig_mcerror, fig_lifted, fig_flow, fig_rates]:
        fn()
