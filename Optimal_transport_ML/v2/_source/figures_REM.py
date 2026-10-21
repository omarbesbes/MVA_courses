"""figures_REM.py — static SVG figures of the Reminders page, written to figures/REM/.

Run: python3 figures_REM.py        (then node build.mjs Reminders.html)
Every coordinate is computed here. Colours are CSS classes (see figures_common.py).
Colour code: source / first measure = 2 (orange-red), target / reference = 1 (blue), third object = 5 (purple),
maps, interpolations, optimal objects = 3 (green), neutral = grey (m).
"""
import math

import numpy as np

from figures_common import Canvas, Fig, fmt1

SUB = "REM"


def gauss(x, m, s):
    return np.exp(-0.5 * ((x - m) / s) ** 2) / (s * math.sqrt(2 * math.pi))


def area(f, fn, x0, x1, cls, n=300):
    """Closed area under the graph of fn between x0 and x1, down to y = 0."""
    xs = np.linspace(x0, x1, n)
    f.path([(x0, 0)] + [(x, fn(x)) for x in xs] + [(x1, 0)], cls, close=True)


# ---------------------------------------------------------------------------------------------
def fig_pushforward():
    """U[0,2] pushed by T(x) = x^2/2: equal masses, compressed (T' < 1) or stretched (T' > 1)."""
    c = Canvas("pushforward", 680, 370, "Push-forward of the uniform law on [0,2] by T(x) = x squared over 2", sub=SUB)
    T = lambda x: x * x / 2
    main = Fig(c, (190, 20, 300, 240), (0, 2), (0, 2.1))
    for v in [0, 0.5, 1, 1.5, 2]:
        main.line(v, 0, v, 2.1, "gr")
        main.text(v, 0, fmt1(v), "tx-s", "middle", dy=14)
        main.line(0, v, 2, v, "gr")
    main.line(0, 0, 2, 0, "ax")
    main.line(0, 0, 0, 2.1, "ax")
    strips = [(0.2, 0.6), (1.4, 1.8)]
    # source density below: uniform on [0, 2], height 1/2
    src = Fig(c, (190, 296, 300, 44), (0, 2), (0, 0.62))
    src.line(0, 0, 2, 0, "ax")
    src.path([(0, 0), (0, 0.5), (2, 0.5), (2, 0)], "ln c2 thin")
    for a, b in strips:
        src.path([(a, 0), (a, 0.5), (b, 0.5), (b, 0)], "a2", close=True)
        src.text((a + b) / 2, 0.5, "mass 0.2", "tx-s t2", "middle", dy=-4)
    c.text(497, 330, "α = 𝒰[0,2]", "tx-b t2", "start")
    c.text(497, 344, "density ½", "tx-s t2", "start")
    # target density on the left, sideways: it grows to the left
    dmax = 2.2
    tgt = Fig(c, (40, 20, 132, 240), (dmax, 0), (0, 2.1))
    tgt.line(0, 0, 0, 2.1, "ax")
    rho = lambda y: 1 / (2 * math.sqrt(2 * y))
    y0 = 1 / (8 * 2.15 ** 2)  # rho(y0) = 2.15
    ys = np.linspace(y0, 2, 300)
    tgt.path([(rho(y), y) for y in ys], "ln c1")
    tgt.line(0.25, 2, 0, 2, "ln c1 hair dot")
    for a, b in strips:
        ya, yb = T(a), T(b)
        yy = np.linspace(max(ya, y0), yb, 60)
        tgt.path([(0, yy[0])] + [(rho(y), y) for y in yy] + [(0, yb)], "a1", close=True)
    for v in [0.5, 1, 1.5, 2]:
        tgt.text(0, v, fmt1(v), "tx-s", "start", dx=4, dy=4)
    tgt.line(0.5, 0, 0.5, 2.1, "ln cm hair dash")
    tgt.text(0.5, 0, "½", "tx-s", "middle", dy=14)
    tgt.text(2, 0, "2", "tx-s", "middle", dy=14)
    tgt.text(1.25, 0, "density", "tx-s", "middle", dy=26)
    c.text(40, 12, "β = T#α", "tx-b t1", "start")
    # graph of T and the strips
    xs = np.linspace(0, 2, 300)
    main.path([(x, T(x)) for x in xs], "ln c3")
    main.text(1.62, 1.75, "y = T(x) = x²/2", "tx-b t3", "end")
    for a, b in strips:
        main.path([(a, 0), (a, T(a)), (b, T(b)), (b, 0)], "a2", close=True)
        main.path([(0, T(a)), (a, T(a)), (b, T(b)), (0, T(b))], "a1", close=True)
        for x in (a, b):
            main.line(x, 0, x, T(x), "ln c2 hair dash")
            main.line(0, T(x), x, T(x), "ln c1 hair dash")
    for k, line in enumerate(["[1.4, 1.8] ↦ [0.98, 1.62]:", "length 0.64, so density", "0.2/0.64 ≈ 0.31 < ½: stretched"]):
        c.text(500, 92 + 14 * k, line, "tx-s t1", "start")
    for k, line in enumerate(["[0.2, 0.6] ↦ [0.02, 0.18]:", "length 0.16, so density", "0.2/0.16 = 1.25 > ½: compressed"]):
        c.text(500, 206 + 14 * k, line, "tx-s t1", "start")
    c.text(500, 160, "ρβ(T(x)) T′(x) = ρα(x)", "tx-s t3", "start")
    c.text(340, 366, "x (source)", "tx-s", "middle")
    c.save()


# ---------------------------------------------------------------------------------------------
def fig_cdf_quantile():
    """CDF and quantile function of 1/4 d0 + 1/2 U[1,2] + 1/4 d3."""
    c = Canvas("cdf_quantile", 660, 290, "CDF and quantile function of a measure with two atoms and a uniform part", sub=SUB)
    f = Fig(c, (46, 30, 250, 200), (-0.6, 3.6), (0, 1.08))
    f.axes(xticks=[0, 1, 2, 3], yticks=[0, 0.25, 0.5, 0.75, 1], yfmt=fmt1, xlabel="x")
    # CDF pieces
    f.line(-0.6, 0, 0, 0, "ln c2")
    f.line(0, 0.25, 1, 0.25, "ln c2")
    f.line(1, 0.25, 2, 0.75, "ln c2")
    f.line(2, 0.75, 3, 0.75, "ln c2")
    f.line(3, 1, 3.6, 1, "ln c2")
    f.line(0, 0, 0, 0.25, "ln c2 hair dot")
    f.line(3, 0.75, 3, 1, "ln c2 hair dot")
    for (x, y) in [(0, 0.25), (3, 1)]:
        f.circle(x, y, 4, "f2")
    for (x, y) in [(0, 0), (3, 0.75)]:
        c.add(f'<circle cx="{f.X(x):.1f}" cy="{f.Y(y):.1f}" r="4" class="fs ln c2 thin"/>')
    # level 1/2 -> median 1.5
    f.line(-0.6, 0.5, 1.5, 0.5, "ln c3 thin dash")
    f.line(1.5, 0.5, 1.5, 0, "ln c3 thin dash")
    f.circle(1.5, 0.5, 3.5, "f3")
    f.text(1.5, 0, "1.5", "tx-s t3", "middle", dy=26)
    # two short lines, so that the label ends before the CDF starts rising at x = 1
    f.text(0.06, 0.25, "jump ¼ =", "tx-s", "start", dx=2, dy=-21)
    f.text(0.06, 0.25, "atom at 0", "tx-s", "start", dx=2, dy=-8)
    # anchored at its end, left of the vertical jump at x = 3 (it used to cross it)
    f.text(2.94, 0.75, "flat: no mass in (2,3)", "tx-s", "end", dx=0, dy=-8)
    c.text(171, 18, "CDF  C(x) = α((−∞, x])", "tx-b", "middle")
    # quantile function
    g = Fig(c, (390, 30, 230, 200), (0, 1), (-0.25, 3.4))
    g.axes(xticks=[0, 0.25, 0.5, 0.75, 1], yticks=[0, 1, 2, 3], xfmt=fmt1, xlabel="t")
    g.line(0, 0, 0.25, 0, "ln c2")
    g.line(0.25, 1, 0.75, 2, "ln c2")
    g.line(0.75, 3, 1, 3, "ln c2")
    g.line(0.25, 0, 0.25, 1, "ln c2 hair dot")
    g.line(0.75, 2, 0.75, 3, "ln c2 hair dot")
    for (x, y) in [(0.25, 0), (0.75, 2)]:
        g.circle(x, y, 4, "f2")
    for (x, y) in [(0.25, 1), (0.75, 3)]:
        c.add(f'<circle cx="{g.X(x):.1f}" cy="{g.Y(y):.1f}" r="4" class="fs ln c2 thin"/>')
    g.line(0.5, -0.25, 0.5, 1.5, "ln c3 thin dash")
    g.line(0, 1.5, 0.5, 1.5, "ln c3 thin dash")
    g.circle(0.5, 1.5, 3.5, "f3")
    g.text(0.13, 0, "flat = atom", "tx-s", "middle", dy=-8)
    g.text(0.74, 2.5, "jump = gap", "tx-s", "end", dx=-6)
    c.text(505, 18, "quantile  C⁻¹(t) = inf{x : C(x) ≥ t}", "tx-b", "middle")
    c.text(330, 282, "filled dot: value taken; open dot: limit not taken.  Green: the median, C⁻¹(½) = 1.5.", "tx-s", "middle")
    c.save()


# ---------------------------------------------------------------------------------------------
def fig_sorting():
    c = Canvas("sorting", 640, 218, "Matching three points to three points on the line: crossing versus sorted", sub=SUB)
    xs, ys = [0, 1, 3], [1, 2, 5]
    titles = ["reversed: (0−5)² + (1−2)² + (3−1)² = 30", "sorted: (0−1)² + (1−2)² + (3−5)² = 6"]
    for col, perm in enumerate([[2, 1, 0], [0, 1, 2]]):
        f = Fig(c, (40 + col * 320, 48, 260, 120), (-0.5, 5.5), (0, 1))
        f.line(-0.5, 1, 5.5, 1, "gr")
        f.line(-0.5, 0, 5.5, 0, "gr")
        for i, x in enumerate(xs):
            f.line(x, 1, ys[perm[i]], 0, "ln c3")
        for x in xs:
            f.circle(x, 1, 6, "f2")
            f.text(x, 1, str(x), "tx-s", "middle", dy=-11)
        for y in ys:
            f.circle(y, 0, 6, "f1")
            f.text(y, 0, str(y), "tx-s", "middle", dy=20)
        c.text(40 + col * 320 + 130, 18, titles[col], "tx-b", "middle")
        c.text(28 + col * 320, 53, "x", "tx-i t2", "end")
        c.text(28 + col * 320, 173, "y", "tx-i t1", "end")
    c.text(320, 210, "uncrossing two segments never increases a convex cost h(x − y): the sorted matching is optimal", "tx-s", "middle")
    c.save()

# ---------------------------------------------------------------------------------------------
def fig_couplings():
    """Three couplings with the same marginals: independent, monotone, anti-monotone."""
    a = np.array([0.1, 0.4, 0.3, 0.2])
    b = np.array([0.3, 0.2, 0.2, 0.3])

    def nw(a, b):
        P = np.zeros((len(a), len(b)))
        ra, rb = a.copy(), b.copy()
        i = j = 0
        while i < len(a) and j < len(b):
            t = min(ra[i], rb[j])
            P[i, j] += t
            ra[i] -= t
            rb[j] -= t
            if ra[i] <= 1e-12:
                i += 1
            else:
                j += 1
        return P

    plans = [("independent  π = α ⊗ β", np.outer(a, b)), ("monotone (sorted)", nw(a, b)),
             ("anti-monotone", nw(a, b[::-1])[:, ::-1])]
    c = Canvas("couplings", 660, 250, "Three couplings with the same marginals: independent, monotone, anti-monotone", sub=SUB)
    for col, (title, P) in enumerate(plans):
        x0 = 30 + col * 215
        cost = sum(P[i, j] * (i - j) ** 2 for i in range(4) for j in range(4))
        # marginal bars: a on the left (rows), b on top (columns)
        cell = 34
        gx, gy = x0 + 40, 66
        for j in range(4):
            h = b[j] * 70
            c.add(f'<rect x="{gx + j * cell + 9:.1f}" y="{gy - 6 - h:.1f}" width="16" height="{h:.1f}" class="a1 ln c1 hair"/>')
        for i in range(4):
            wdt = a[i] * 70
            c.add(f'<rect x="{gx - 6 - wdt:.1f}" y="{gy + i * cell + 9:.1f}" width="{wdt:.1f}" height="16" class="a2 ln c2 hair"/>')
        for i in range(4):
            for j in range(4):
                cx, cy = gx + j * cell + cell / 2, gy + i * cell + cell / 2
                c.add(f'<rect x="{gx + j * cell:.1f}" y="{gy + i * cell:.1f}" width="{cell}" height="{cell}" class="gr"/>')
                if P[i, j] > 1e-9:
                    r = 16 * math.sqrt(P[i, j] / 0.4)
                    c.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" class="f3"/>')
        c.text(x0 + 100, 16, title, "tx-b", "middle")
        c.text(x0 + 108, 222, f"∫ |x − y|² dπ = {cost:.2f}", "tx-s t3", "middle")
    c.text(330, 244, "rows: α = (0.1, 0.4, 0.3, 0.2), columns: β = (0.3, 0.2, 0.2, 0.3), on the points 0, 1, 2, 3;  disc area ∝ mass", "tx-s", "middle")
    c.save()
    return plans


# ---------------------------------------------------------------------------------------------
def fig_gaussian():
    c = Canvas("gaussian", 640, 290, "A Gaussian vector with covariance [[2,1],[1,2]]: ellipses, eigenvectors, projections", sub=SUB)
    S = np.array([[2.0, 1.0], [1.0, 2.0]])
    w, V = np.linalg.eigh(S)
    R = V @ np.diag(np.sqrt(w)) @ V.T
    f = Fig(c, (40, 20, 250, 250), (-4.3, 4.3), (-4.3, 4.3))
    f.line(-4.3, 0, 4.3, 0, "ax")
    f.line(0, -4.3, 0, 4.3, "ax")
    rng = np.random.default_rng(7)
    Z = rng.standard_normal((160, 2)) @ R.T
    for p in Z:
        if abs(p[0]) < 4.2 and abs(p[1]) < 3.7:
            f.circle(p[0], p[1], 1.6, "fm")
    for k, cls in [(1, "ln c2"), (2, "ln c2 thin dash")]:
        th = np.linspace(0, 2 * math.pi, 200)
        pts = [(R @ np.array([math.cos(t), math.sin(t)]) * k) for t in th]
        f.path([(p[0], p[1]) for p in pts], cls)
    for lam, vec in [(w[1], V[:, 1]), (w[0], V[:, 0])]:
        v = vec * math.sqrt(lam)
        if v[0] < 0:
            v = -v
        f.line(0, 0, v[0], v[1], "ln c3")
        f.circle(v[0], v[1], 3, "f3")
    # labels just outside the one-sigma ellipse, which passes through the tips of the scaled eigenvectors
    f.text(1.5, 1.58, "√3", "tx-b t3", "start", dx=2)
    f.text(0.86, -0.9, "1", "tx-b t3", "start", dx=2, dy=6)
    f.text(-4.2, 4.0, "1σ and 2σ ellipses", "tx-s t2", "start")
    f.text(-4.2, -4.0, "x ∼ 𝒩(0, Σ), 160 samples", "tx-s", "start")
    # right: laws of the projections
    g = Fig(c, (360, 36, 260, 170), (-5, 5), (0, 0.42))
    g.axes(xticks=[-4, -2, 0, 2, 4], yticks=[], grid=False, yaxis=False)
    rows = [(1.0, "ln c5", "θ = (1, −1)/√2:  θᵀΣθ = 1"), (2.0, "ln c1 dash", "θ = (1, 0):  θᵀΣθ = 2"),
            (3.0, "ln c3", "θ = (1, 1)/√2:  θᵀΣθ = 3")]
    for k, (var, cls, lab) in enumerate(rows):
        g.fn(lambda x, v=var: math.exp(-x * x / (2 * v)) / math.sqrt(2 * math.pi * v), cls, n=300)
        y = 238 + 15 * k
        c.add(f'<line x1="380" y1="{y - 4}" x2="398" y2="{y - 4}" class="{cls}"/>')
        c.text(406, y, lab, "tx-s", "start")
    c.text(490, 22, "law of ⟨θ, x⟩ = 𝒩(0, θᵀΣθ)", "tx-b", "middle")
    c.save()

# ---------------------------------------------------------------------------------------------
def fig_jensen():
    c = Canvas("jensen", 520, 300, "Jensen's inequality: the function of the mean lies below the mean of the function", sub=SUB)
    phi = lambda s: s * s
    u1, u2, lam = 0.5, 2.5, 0.7
    m = (1 - lam) * u1 + lam * u2
    f = Fig(c, (50, 20, 420, 240), (-0.1, 3.0), (-0.4, 7.2))
    f.axes(xticks=[], yticks=[], grid=False)
    f.fn(phi, "ln c1", -0.1, 2.68, 300)
    f.line(u1, phi(u1), u2, phi(u2), "ln c2")
    xt0 = m - (phi(m) + 0.4) / (2 * m)
    f.line(xt0, -0.4, 2.7, phi(m) + 2 * m * (2.7 - m), "ln c3 thin dash")
    for u in [u1, u2]:
        f.circle(u, phi(u), 4.5, "f2")
        f.line(u, -0.4, u, phi(u), "gr")
    Ephi = (1 - lam) * phi(u1) + lam * phi(u2)
    f.line(m, -0.4, m, Ephi, "ln cm thin dot")
    f.circle(m, Ephi, 5, "f2")
    f.circle(m, phi(m), 5, "f3")
    f.text(u1, -0.4, "u₁", "tx-i", "middle", dy=16)
    f.text(u2, -0.4, "u₂", "tx-i", "middle", dy=16)
    f.text(m, -0.4, "E[U]", "tx-s", "middle", dy=16)
    f.text(m, Ephi, f"E φ(U) = {Ephi:.2f}  (on the chord)", "tx-s t2", "end", dx=-9, dy=-4)
    f.text(m, phi(m), f"φ(E U) = {phi(m):.2f}  (on the graph)", "tx-s t3", "start", dx=9, dy=14)
    f.text(2.62, phi(2.62), "φ convex", "tx-b t1", "end", dx=-8)
    f.text(xt0, -0.4, "tangent at E U", "tx-s t3", "start", dx=14, dy=-3)
    c.text(260, 292, "U = u₁ with prob. 0.3, u₂ with prob. 0.7;  φ(s) = s²;  gap = Var(U) = 0.84", "tx-s", "middle")
    c.save()

# ---------------------------------------------------------------------------------------------
def fig_convexity():
    c = Canvas("convexity", 660, 240, "Convex, non-convex, strongly versus strictly convex", sub=SUB)
    # (a) convex
    f = Fig(c, (20, 30, 190, 140), (-1.6, 1.6), (-0.4, 2.6))
    f.line(-1.6, 0, 1.6, 0, "ax")
    f.fn(lambda x: x * x, "ln c1", -1.6, 1.6)
    f.line(-1.2, 1.44, 1.0, 1.0, "ln c2")
    f.circle(-1.2, 1.44, 3.5, "f2")
    f.circle(1.0, 1.0, 3.5, "f2")
    x0 = 0.45
    xt = x0 + (-0.4 - x0 * x0) / (2 * x0)
    f.line(xt, -0.4, 1.5, x0 * x0 + 2 * x0 * (1.5 - x0), "ln c3 thin dash")
    f.circle(x0, x0 * x0, 3.5, "f3")
    c.text(115, 18, "convex", "tx-b", "middle")
    c.text(115, 190, "chords above the graph,", "tx-s", "middle")
    c.text(115, 204, "tangents below", "tx-s", "middle")
    # (b) not convex
    g = Fig(c, (240, 30, 190, 140), (-1.7, 1.7), (-1.6, 1.6))
    h = lambda x: x ** 4 - 2 * x ** 2 + 0.35 * x
    g.line(-1.7, 0, 1.7, 0, "ax")
    g.fn(h, "ln c1", -1.6, 1.55)
    xa, xb = -1.05, 0.95
    g.line(xa, h(xa), xb, h(xb), "ln c2")
    g.circle(xa, h(xa), 3.5, "f2")
    g.circle(xb, h(xb), 3.5, "f2")
    roots = sorted(r.real for r in np.roots([4, 0, -4, 0.35]) if abs(r.imag) < 1e-9)
    for r in [roots[0], roots[2]]:
        g.circle(r, h(r), 4, "f5")
    g.text(roots[0], h(roots[0]), "global min", "tx-s t5", "middle", dy=16)
    g.text(roots[2], h(roots[2]), "local min", "tx-s t5", "middle", dy=16)
    c.text(335, 18, "not convex", "tx-b", "middle")
    c.text(335, 190, "a chord passes below the graph;", "tx-s", "middle")
    c.text(335, 204, "a local min is not global", "tx-s", "middle")
    # (c) strongly vs strictly
    k = Fig(c, (460, 30, 190, 140), (-1.4, 1.4), (-0.3, 2.2))
    k.line(-1.4, 0, 1.4, 0, "ax")
    k.fn(lambda x: x ** 2, "ln c3", -1.4, 1.4)
    k.fn(lambda x: x ** 4, "ln c5", -1.2, 1.2)
    c.text(555, 18, "strongly vs strictly", "tx-b", "middle")
    c.text(555, 190, "green x²: f″ = 2, strongly convex", "tx-s t3", "middle")
    c.text(555, 204, "purple x⁴: f″(0) = 0, strictly only", "tx-s t5", "middle")
    c.text(330, 232, "blue: the function;  orange: a chord;  green dashed: a tangent", "tx-s", "middle")
    c.save()

# ---------------------------------------------------------------------------------------------
def fig_legendre():
    c = Canvas("legendre", 660, 300, "Legendre transform of exp: supporting lines of slope y have intercept -f*(y)", sub=SUB)
    X0, X1, Y0, Y1 = -3.2, 1.5, -0.6, 4.4
    f = Fig(c, (50, 24, 300, 236), (X0, X1), (Y0, Y1))
    f.axes(xticks=[-3, -2, -1, 0, 1], yticks=[0, 1, 2, 3, 4], grid=False)
    f.fn(math.exp, "ln c1", X0, math.log(Y1), 300)

    def clipline(slope, icpt, cls):
        # the part of the line y = slope x + icpt inside the panel
        xa = max(X0, (Y0 - icpt) / slope)
        xb = min(X1, (Y1 - icpt) / slope)
        f.line(xa, slope * xa + icpt, xb, slope * xb + icpt, cls)

    cols = [(0.5, "c5"), (1.0, "c2"), (2.0, "c3")]
    for y, cl in cols:
        fs = y * math.log(y) - y
        clipline(y, -fs, f"ln {cl} thin")
        f.circle(math.log(y), y, 4, "f" + cl[1])
        f.circle(0, -fs, 4, "fs ln " + cl + " thin")
    clipline(2.0, -(2 * math.log(2) - 2) - 1.0, "ln c3 hair dash")
    c.text(f.X(1.5) + 6, f.Y(2.45), "dashed:", "tx-s t3", "start")
    c.text(f.X(1.5) + 6, f.Y(2.45) + 13, "lower line", "tx-s t3", "start")
    c.text(f.X(1.5) + 6, f.Y(2.45) + 26, "of slope 2", "tx-s t3", "start")
    f.text(-1.0, 3.6, "f(x) = eˣ", "tx-b t1", "middle")
    c.text(200, 14, "the tangent of slope y touches at x = log y; its intercept is −f*(y)", "tx-s", "middle")
    # right panel: f*(y) = y log y - y
    g = Fig(c, (430, 24, 210, 236), (0, 3.4), (-1.15, 1.0))
    g.axes(xticks=[0, 1, 2, 3], yticks=[-1, -0.5, 0, 0.5, 1], yfmt=fmt1, grid=False)
    g.fn(lambda y: y * math.log(y) - y, "ln ck", 1e-4, 3.4, 300)
    for y, cl in cols:
        g.circle(y, y * math.log(y) - y, 4.5, "f" + cl[1])
    g.text(3.3, 3.3 * math.log(3.3) - 3.3, "f*(y) = y log y − y", "tx-b", "end", dy=-10)
    g.text(0.42, 0.5 * math.log(0.5) - 0.5, "−0.85", "tx-s t5", "middle", dy=22)  # below-left: clear of the curve
    g.text(1.0, -1.0, "−1", "tx-s t2", "middle", dy=18)
    g.text(2.0, 2 * math.log(2) - 2, "−0.61", "tx-s t3", "start", dx=8, dy=4)
    c.text(535, 14, "the conjugate, at the three slopes", "tx-s", "middle")
    c.text(330, 294, "slopes y = 0.5 (purple), 1 (orange), 2 (green); open dots: intercepts −f*(y) = 0.85, 1, 0.61", "tx-s", "middle")
    c.save()

# ---------------------------------------------------------------------------------------------
def fig_lp():
    c = Canvas("lp", 520, 300, "A linear program in the plane: the optimum is reached at a vertex", sub=SUB)
    f = Fig(c, (50, 20, 300, 250), (-0.3, 5.0), (-0.3, 4.2))
    f.axes(xticks=[0, 1, 2, 3, 4], yticks=[0, 1, 2, 3, 4], grid=False)
    # constraints: x>=0, y>=0, x+y<=4, x+3y<=9, 2x+y<=7
    V = [(0, 0), (3.5, 0), (3, 1), (1.5, 2.5), (0, 3)]
    f.path(V, "a3", close=True)
    f.path(V + [V[0]], "ln c3 thin")
    # objective max x + 2y (direction c = (1,2)); level lines x + 2y = k
    for k in [1, 2.5, 4, 5.5, 6.5]:
        x0, x1 = -0.3, min(5.0, k + 0.2)
        f.line(x0, (k - x0) / 2, x1, (k - x1) / 2, "ln cm hair dash" if k != 6.5 else "ln c2 thin")
    for v in V:
        f.circle(v[0], v[1], 3.5, "fm")
    f.circle(1.5, 2.5, 6, "f2")
    f.text(1.5, 2.5, "optimal vertex (1.5, 2.5)", "tx-s t2", "start", dx=10, dy=-8)
    c.arrow(f.X(2.2), f.Y(0.6), f.X(2.2 + 0.5), f.Y(0.6 + 1.0), 2, "ln c2 thin")
    f.text(2.75, 1.65, "c = (1, 2)", "tx-s t2", "start")
    f.text(2.45, (6.5 - 2.45) / 2, "x + 2y = 6.5", "tx-s t2", "start", dx=4, dy=-6)
    f.text(0.15, 0.35, "feasible polygon", "tx-s t3", "start")
    c.text(440, 60, "maximize x + 2y", "tx-b", "middle")
    c.text(440, 80, "subject to x, y ≥ 0,", "tx-s", "middle")
    c.text(440, 96, "x + y ≤ 4, x + 3y ≤ 9,", "tx-s", "middle")
    c.text(440, 112, "2x + y ≤ 7", "tx-s", "middle")
    c.text(440, 150, "level lines x + 2y = k", "tx-s", "middle")
    c.text(440, 166, "slide in the direction c;", "tx-s", "middle")
    c.text(440, 182, "the last contact is a vertex", "tx-s", "middle")
    c.text(440, 198, "(or a whole edge)", "tx-s", "middle")
    c.save()


# ---------------------------------------------------------------------------------------------
def fig_gd():
    c = Canvas("gd", 600, 280, "Gradient descent on an ill-conditioned quadratic: small step versus large step", sub=SUB)
    f = Fig(c, (40, 20, 520, 220), (-0.35, 1.15), (-1.05, 1.15))
    f.line(-0.35, 0, 1.15, 0, "ax")
    f.line(0, -1.05, 0, 1.15, "ax")
    for lev in [0.05, 0.2, 0.5, 1.0, 2.0, 3.5, 5.5]:
        th = np.linspace(0, 2 * math.pi, 200)
        a, b = math.sqrt(2 * lev), math.sqrt(2 * lev / 10)
        f.path([(a * math.cos(t), b * math.sin(t)) for t in th], "gr")
    for tau, cls, fcls in [(0.1, "ln c3", "f3"), (0.19, "ln c2", "f2")]:
        x = np.array([1.0, 1.0])
        pts = [x.copy()]
        for _ in range(12):
            x = x - tau * np.array([1.0, 10.0]) * x
            pts.append(x.copy())
        f.path([(p[0], p[1]) for p in pts], cls + " thin")
        for p in pts:
            f.circle(p[0], p[1], 3, fcls)
    f.circle(0, 0, 4, "fk")
    f.text(1.0, 1.0, "start (1, 1)", "tx-s", "end", dx=-8, dy=-4)
    f.text(-0.33, 1.0, "green: τ = 0.1 = 1/L, the x₂-coordinate is 0 after one step", "tx-s t3", "start")
    f.text(-0.33, 0.9, "orange: τ = 0.19, zigzag: x₂ is multiplied by −0.9 at each step", "tx-s t2", "start")
    f.text(0, 0, "minimizer", "tx-s", "end", dx=-6, dy=14)
    c.text(300, 272, "f(x) = ½(x₁² + 10 x₂²): L = 10, μ = 1; the level sets are flat ellipses; any τ > 2/L = 0.2 diverges", "tx-s", "middle")
    c.save()

# ---------------------------------------------------------------------------------------------
def fig_ode():
    c = Canvas("ode_flow", 560, 300, "Flow of the linear vector field v(x) = Ax: a spiral sink, trajectories and the flow map", sub=SUB)
    A = np.array([[-0.5, -1.0], [1.0, -0.5]])
    f = Fig(c, (40, 20, 300, 260), (-2.6, 2.6), (-2.25, 2.25))
    f.line(-2.6, 0, 2.6, 0, "ax")
    f.line(0, -2.25, 0, 2.25, "ax")
    for gx in np.linspace(-2.25, 2.25, 10):
        for gy in np.linspace(-2.0, 2.0, 9):
            v = A @ np.array([gx, gy])
            n = np.linalg.norm(v)
            if n < 1e-9:
                continue
            s = 0.17 / max(n, 0.6)
            x1, y1 = f.X(gx), f.Y(gy)
            x2, y2 = f.X(gx + s * v[0]), f.Y(gy + s * v[1])
            c.arrow(x1, y1, x2, y2, "m", "ln cm hair")

    def expA(t):
        # e^{tA} for A = -0.5 I + J, J rotation generator
        return math.exp(-0.5 * t) * np.array([[math.cos(t), -math.sin(t)], [math.sin(t), math.cos(t)]])

    for x0 in [np.array([2.2, 0.0]), np.array([-1.6, 1.6]), np.array([0.3, -2.1])]:
        ts = np.linspace(0, 8, 400)
        pts = [expA(t) @ x0 for t in ts]
        f.path([(p[0], p[1]) for p in pts], "ln c3 thin")
        f.circle(x0[0], x0[1], 4, "f2")
        for t in [1, 2]:
            p = expA(t) @ x0
            f.circle(p[0], p[1], 3, "f3")
    f.text(2.2, 0, "x₀", "tx-i t2", "start", dx=6, dy=-6)
    # right panel: a small square of particles and its image by the flow map at t = 1
    g = Fig(c, (370, 40, 170, 170), (-0.6, 2.6), (-0.6, 2.6))
    g.line(-0.6, 0, 2.6, 0, "ax")
    g.line(0, -0.6, 0, 2.6, "ax")
    sq = [np.array([1.6 + 0.6 * i / 4, 0.2 + 0.6 * j / 4]) for i in range(5) for j in range(5)]
    for p in sq:
        g.circle(p[0], p[1], 2.2, "f2")
        q = expA(1.0) @ p
        g.circle(q[0], q[1], 2.2, "f3")
    g.text(1.9, 0.2, "particles at t = 0", "tx-s t2", "middle", dy=18)
    q = expA(1.0) @ np.array([1.9, 0.5])
    g.text(q[0], q[1], "Tₜ(particles), t = 1", "tx-s t3", "middle", dy=-24)
    c.text(455, 240, "the flow map Tₜ = exp(tA) rotates", "tx-s", "middle")
    c.text(455, 256, "and contracts (area × e⁻ᵗ)", "tx-s", "middle")
    c.text(280, 296, "grey: v(x) = Ax with A = [[−0.5, −1], [1, −0.5]];  green: trajectories, dots at t = 1, 2", "tx-s", "middle")
    c.save()


# ---------------------------------------------------------------------------------------------
def fig_continuity():
    c = Canvas("continuity", 640, 290, "Continuity equation: the displacement interpolation between N(0,1) and N(4,4), with its velocity field", sub=SUB)
    f = Fig(c, (40, 20, 400, 220), (-3.5, 9.5), (-0.08, 0.45))
    f.line(-3.5, 0, 9.5, 0, "ax")
    for v in range(-2, 10, 2):
        f.text(v, 0, str(v), "tx-s", "middle", dy=14)
    rows = [(0, "ln c2", "a2", "t2", "t = 0: 𝒩(0, 1)"), (0.5, "ln c3", "a3", "t3", "t = ½: 𝒩(2, 1.5²)"),
            (1, "ln c1", "a1", "t1", "t = 1: 𝒩(4, 2²)")]
    for k, (t, cls, acls, tcl, lab) in enumerate(rows):
        m, s = 4 * t, 1 + t
        fn = lambda x, m=m, s=s: gauss(x, m, s)
        area(f, fn, -3.5, 9.5, acls)
        f.fn(fn, cls, -3.5, 9.5, 300)
        f.text(6.0, 0.42 - 0.045 * k, lab, "tx-s " + tcl, "start")
    t = 0.5
    for y in np.arange(-0.6, 5.6, 1.1):
        v = 4 + (y - 4 * t) / (1 + t)
        x1, y1 = f.X(y), f.Y(-0.068)
        x2 = f.X(y + 0.28 * v)
        c.arrow(x1, y1, x2, y1, 3, "ln c3 thin")
    f.text(-3.45, -0.068, "vₜ(y), t = ½", "tx-s t3", "start", dy=4)
    c.text(240, 282, "particles move by x ↦ (1 − t)x + t(4 + 2x); velocity field vₜ(y) = 4 + (y − 4t)/(1 + t)", "tx-s", "middle")
    g = Fig(c, (470, 60, 150, 130), (0, 1), (0, 1))
    g.line(0, 0.2, 1, 0.2, "ax")
    g.path([(0.25, 0.2), (0.25, 0.75), (0.75, 0.75), (0.75, 0.2)], "a3", close=True)
    g.text(0.25, 0.2, "a", "tx-i", "middle", dy=16)
    g.text(0.75, 0.2, "b", "tx-i", "middle", dy=16)
    c.arrow(g.X(0.0), g.Y(0.5), g.X(0.23), g.Y(0.5), 2, "ln c2 thin")
    c.arrow(g.X(0.77), g.Y(0.5), g.X(1.0), g.Y(0.5), 1, "ln c1 thin")
    g.text(0.0, 0.5, "in: ρv(a)", "tx-s t2", "start", dy=-8)
    g.text(1.0, 0.5, "out: ρv(b)", "tx-s t1", "end", dy=-8)
    c.text(545, 40, "mass in [a, b]", "tx-b", "middle")
    c.text(545, 222, "d/dt ∫ ρ over [a, b] = ρv(a) − ρv(b)", "tx-s", "middle")
    c.text(545, 238, "⇔ ∂ₜρ + ∂ₓ(ρv) = 0", "tx-s t3", "middle")
    c.save()

# ---------------------------------------------------------------------------------------------
def fig_kl():
    c = Canvas("kl_reverse", 600, 260, "Fitting one Gaussian to a two-mode law: forward KL covers, reverse KL picks a mode", sub=SUB)
    p = lambda x: 0.5 * gauss(x, -2, 0.5) + 0.5 * gauss(x, 2, 0.5)
    f = Fig(c, (40, 20, 520, 200), (-5.5, 5.5), (0, 0.85))
    f.line(-5.5, 0, 5.5, 0, "ax")
    for v in range(-4, 5, 2):
        f.text(v, 0, str(v), "tx-s", "middle", dy=14)
    area(f, p, -5.5, 5.5, "a1")
    f.fn(p, "ln c1", -5.5, 5.5, 400)
    f.fn(lambda x: gauss(x, 0, math.sqrt(4.25)), "ln c2", -5.5, 5.5, 300)
    f.fn(lambda x: gauss(x, 2, 0.5004), "ln c5 dash", -5.5, 5.5, 300)
    rows = [("ln c1", "t1", "target p = ½𝒩(−2, 0.5²) + ½𝒩(2, 0.5²)"), ("ln c2", "t2", "argmin over q of KL(p | q):  𝒩(0, 2.06²)"),
            ("ln c5 dash", "t5", "argmin over q of KL(q | p):  𝒩(2, 0.50²)")]
    for k, (cls, tcl, lab) in enumerate(rows):
        y = 34 + 16 * k
        c.add(f'<line x1="52" y1="{y - 4}" x2="70" y2="{y - 4}" class="{cls}"/>')
        c.text(76, y, lab, "tx-s " + tcl, "start")
    c.text(300, 252, "forward KL (maximum likelihood) is mass-covering;  reverse KL (variational inference) is mode-seeking", "tx-s", "middle")
    c.save()

# ---------------------------------------------------------------------------------------------
def fig_fdiv():
    c = Canvas("fdiv", 540, 270, "Generators of the classical f-divergences", sub=SUB)
    f = Fig(c, (50, 20, 300, 220), (0, 3.2), (-0.05, 2.2))
    f.axes(xticks=[0, 1, 2, 3], yticks=[0, 0.5, 1, 1.5, 2], yfmt=fmt1, xlabel="s = ratio of densities")
    gens = [("KL: s log s − s + 1", lambda s: s * math.log(s) - s + 1, "ln c2", 1e-4, 3.2),
            ("reverse KL: s − 1 − log s", lambda s: s - 1 - math.log(s), "ln c5", 0.06, 3.2),
            ("TV: |s − 1|", lambda s: abs(s - 1), "ln cm", 0.0, 3.2),
            ("Hellinger: (√s − 1)²", lambda s: (math.sqrt(s) - 1) ** 2, "ln c3", 0.0, 3.2),
            ("χ²: (s − 1)²", lambda s: (s - 1) ** 2, "ln c1", 0.0, 1 + math.sqrt(2.2))]
    for k, (lab, fn, cls, a, b) in enumerate(gens):
        f.fn(fn, cls, a, b, 300)
        y = 54 + k * 22
        c.add(f'<line x1="368" y1="{y - 4}" x2="386" y2="{y - 4}" class="{cls}"/>')
        c.text(392, y, lab, "tx-s", "start")
    f.circle(1, 0, 4, "fk")
    c.text(368, 54 + 5 * 22, "all vanish at s = 1 (dot)", "tx-s", "start")
    c.text(450, 30, "φ(s)", "tx-b", "middle")
    c.save()

# ---------------------------------------------------------------------------------------------
def fig_brownian():
    c = Canvas("brownian", 600, 284, "Five Brownian paths on [0,1], the envelopes ±√t and ±2√t, and the law of B at time 1", sub=SUB)
    f = Fig(c, (40, 20, 420, 220), (0, 1), (-2.6, 2.6))
    f.axes(xticks=[0, 0.25, 0.5, 0.75, 1], yticks=[-2, -1, 0, 1, 2], xfmt=fmt1, grid=False)
    ts = np.linspace(0, 1, 401)
    for k, cls in [(1, "ln cm thin dash"), (2, "ln cm thin dot")]:
        f.path([(t, k * math.sqrt(t)) for t in ts], cls)
        f.path([(t, -k * math.sqrt(t)) for t in ts], cls)
    rng = np.random.default_rng(3)
    cols = ["c1", "c2", "c3", "c5", "c4"]
    for i in range(5):
        dB = rng.standard_normal(400) * math.sqrt(1 / 400)
        B = np.clip(np.concatenate([[0], np.cumsum(dB)]), -2.55, 2.55)
        f.path([(t, b) for t, b in zip(ts, B)], f"ln {cols[i]} hair")
    f.text(0.02, 2.35, "dashed: ±√t;  dotted: ±2√t", "tx-s", "start")
    g = Fig(c, (470, 20, 110, 220), (0, 0.45), (-2.6, 2.6))
    g.line(0, -2.6, 0, 2.6, "ax")
    ys = np.linspace(-2.6, 2.6, 300)
    g.path([(0, -2.6)] + [(gauss(y, 0, 1), y) for y in ys] + [(0, 2.6)], "am", close=True)
    g.path([(gauss(y, 0, 1), y) for y in ys], "ln cm")
    g.text(0.2, 1.5, "B₁ ∼ 𝒩(0, 1)", "tx-s", "start")
    c.text(470, 256, "t", "tx-i", "middle")
    c.text(250, 276, "B₀ = 0, independent increments B(t) − B(s) ∼ 𝒩(0, t − s): the spread grows like √t, not t", "tx-s", "middle")
    c.save()

# ---------------------------------------------------------------------------------------------
def fig_ou():
    c = Canvas("ou", 640, 270, "Ornstein-Uhlenbeck flow from N(3, 0.25) to N(0,1): densities and KL decay", sub=SUB)
    f = Fig(c, (40, 20, 340, 210), (-3.5, 5), (0, 0.85))
    f.line(-3.5, 0, 5, 0, "ax")
    for v in range(-3, 6):
        f.text(v, 0, str(v), "tx-s", "middle", dy=14)

    def law(t):
        return 3 * math.exp(-t), math.sqrt(0.25 * math.exp(-2 * t) + 1 - math.exp(-2 * t))

    f.fn(lambda x: gauss(x, 0, 1), "ln c1 dash", -3.5, 5, 300)
    for t in [0, 0.25, 0.5, 1, 2]:
        m, s = law(t)
        cls = "ln c2" if t == 0 else "ln c3 thin"
        f.fn(lambda x, m=m, s=s: gauss(x, m, s), cls, -3.5, 5, 300)
        f.text(m, gauss(m, m, s), f"{t:g}", "tx-s " + ("t2" if t == 0 else "t3"), "middle", dy=-6)
    f.text(-3.3, 0.78, "numbers: the time t", "tx-s", "start")
    f.text(-3.3, 0.70, "blue dashed: 𝒩(0, 1)", "tx-s t1", "start")
    c.text(210, 262, "law of Xₜ: 𝒩(3e⁻ᵗ, 0.25e⁻²ᵗ + 1 − e⁻²ᵗ)", "tx-s", "middle")
    g = Fig(c, (440, 20, 180, 210), (0, 3), (0, 3.2))
    g.axes(xticks=[0, 1, 2, 3], yticks=[0, 0.5, 1, 2, 3], yfmt=fmt1, grid=False)
    tt = np.linspace(0, 3, 200)
    g.line(0, 1, 3, 1, "ln c1 thin dash")
    g.path([(t, law(t)[0]) for t in tt], "ln c2")
    g.path([(t, law(t)[1]) for t in tt], "ln c3")
    g.text(0.15, 2.75, "mean 3e⁻ᵗ → 0", "tx-s t2", "start", dx=6)
    g.text(1.6, 1.0, "std → 1", "tx-s t3", "start", dy=-6)
    g.text(0.05, 0.5, "std at t = 0: 0.5", "tx-s t3", "start", dx=6, dy=14)
    c.text(530, 262, "mean and standard deviation of Xₜ", "tx-s", "middle")
    c.save()

if __name__ == "__main__":
    for fn in [fig_pushforward, fig_cdf_quantile, fig_sorting, fig_couplings, fig_gaussian, fig_jensen, fig_convexity,
               fig_legendre, fig_lp, fig_gd, fig_ode, fig_continuity, fig_kl, fig_fdiv, fig_brownian, fig_ou]:
        fn()
