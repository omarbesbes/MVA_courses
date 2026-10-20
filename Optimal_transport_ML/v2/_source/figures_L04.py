"""figures_L04.py — static SVG figures of Lesson 4 (duality), written to figures/L04/.

Run: python3 figures_L04.py        (then node build.mjs Lesson04.html)
Every coordinate and every number printed in a figure is computed here.
"""
import math

import numpy as np
from scipy import integrate, optimize, special, stats

from figures_common import Canvas, Fig, esc, fmt1

SUB = "L04"


def label_bg(c, x, y, s, cls="tx-s", anchor="middle", pad=3, cw=6.0, h=13):
    """A text label on a small rectangle of the surface colour, so that it stays legible over lines."""
    w = len(s) * cw + 2 * pad
    x0 = x - w / 2 if anchor == "middle" else (x - w if anchor == "end" else x)
    c.add(f'<rect x="{x0 - 0.5:.1f}" y="{y - h + 3:.1f}" width="{w:.1f}" height="{h:.1f}" rx="3" class="fs"/>')
    c.add(f'<text x="{x0 + w / 2:.1f}" y="{y:.1f}" class="{cls}" text-anchor="middle">{esc(s)}</text>')


# ---------------------------------------------------------------------------------------------
def fig_prices():
    """The shipping example of section 1: optimal plan on the contact routes, with the prices."""
    C = np.array([[4, 8, 2], [6, 7, 8], [5, 4, 3]], float)
    a = np.array([0.5, 0.3, 0.2])
    b = np.array([0.4, 0.4, 0.2])
    f = np.array([1, 3, 0], float)
    g = np.array([3, 4, 1], float)
    P = np.array([[0.3, 0, 0.2], [0.1, 0.2, 0], [0, 0.2, 0]])
    slack = C - f[:, None] - g[None, :]
    assert np.allclose(P.sum(1), a) and np.allclose(P.sum(0), b)
    assert np.all(slack >= 0) and np.all(slack[P > 0] == 0)
    assert abs((P * C).sum() - (f @ a + g @ b)) < 1e-12
    c = Canvas("prices", 660, 300, "Optimal shipping plan on the contact routes, with collection and delivery prices", sub=SUB)
    # zigzag order along the tree F3 - W1 - F1 - W2 - F2 - W3
    xw = {0: 175, 1: 375, 2: 575}
    xf = {2: 75, 0: 275, 1: 475}
    yw, yf = 92, 212
    for i in range(3):
        for j in range(3):
            if P[i, j] > 0:
                w = 2 + 22 * P[i, j]
                c.add(f'<line x1="{xw[i]}" y1="{yw}" x2="{xf[j]}" y2="{yf}" class="ln c3" stroke-width="{w:.1f}" stroke-opacity="0.75"/>')
    for i in range(3):
        for j in range(3):
            if P[i, j] > 0:
                mx, my = (xw[i] + xf[j]) / 2, (yw + yf) / 2 + 4
                label_bg(c, mx, my, f"{P[i, j]:g} t · C = {C[i, j]:g}")
    for i in range(3):
        r = 6 + 16 * math.sqrt(a[i])
        c.add(f'<circle cx="{xw[i]}" cy="{yw}" r="{r:.1f}" class="f2"/>')
        c.text(xw[i], yw - r - 24, f"W{'₁₂₃'[i]}", "tx-b", "middle")
        c.text(xw[i], yw - r - 9, f"a = {a[i]:g},  f = {f[i]:g} €", "tx-s t2", "middle")
    for j in range(3):
        r = 6 + 16 * math.sqrt(b[j])
        c.add(f'<circle cx="{xf[j]}" cy="{yf}" r="{r:.1f}" class="f1"/>')
        c.text(xf[j], yf + r + 15, f"F{'₁₂₃'[j]}", "tx-b", "middle")
        c.text(xf[j], yf + r + 29, f"b = {b[j]:g},  g = {g[j]:g} €", "tx-s t1", "middle")
    c.text(330, 292, "green route: fᵢ + gⱼ = Cᵢⱼ   ·   bill ⟨f,a⟩ + ⟨g,b⟩ = 4.4 = cost of the plan", "tx-s", "middle")
    c.save()


def fig_slack():
    """Slack landscape for alpha = N(0,1), beta = N(1,4), c = |x-y|^2."""
    m, s = 1.0, 2.0
    T = lambda x: m + s * x
    f = lambda x: (1 - s) * x ** 2 - 2 * m * x
    g = lambda y: y ** 2 - (y - m) ** 2 / s
    # checks
    for x0, y0 in [(0.3, -1.2), (-1.0, 2.5), (1.7, 0.4)]:
        sl = (x0 - y0) ** 2 - f(x0) - g(y0)
        assert abs(sl - (y0 - T(x0)) ** 2 / s) < 1e-12
    c = Canvas("slack", 600, 400, "Slack landscape of optimal potentials between two Gaussians, with the contact line y = T(x)", sub=SUB)
    X0, Y0, W, H = 120, 22, 400, 300
    xr, yr = (-2.5, 2.5), (-4.0, 6.0)
    F = Fig(c, (X0, Y0, W, H), xr, yr)
    cid = f"{SUB}-slack-clip"
    c.defs.append(f'<clipPath id="{cid}"><rect x="{X0}" y="{Y0}" width="{W}" height="{H}"/></clipPath>')
    c.add(f'<g clip-path="url(#{cid})">')
    xs = [xr[0] - 1, xr[1] + 1]
    for k in range(-12, 12):
        lo, hi = k, k + 1
        # band T(x)+lo <= y <= T(x)+hi ; slack between min and max of k^2/2
        level = min(abs(k + 0.5), 4.5) / 4.5
        pts = [(xs[0], T(xs[0]) + lo), (xs[1], T(xs[1]) + lo), (xs[1], T(xs[1]) + hi), (xs[0], T(xs[0]) + hi)]
        d = "M" + "L".join(f"{F.X(p[0]):.1f} {F.Y(p[1]):.1f}" for p in pts) + "Z"
        c.add(f'<path d="{d}" class="fm" fill-opacity="{0.04 + 0.42 * level:.3f}"/>')
    for k in [1, 2, 3, 4]:
        for sg in (-1, 1):
            F.line(xs[0], T(xs[0]) + sg * k, xs[1], T(xs[1]) + sg * k, "ln ck thin dash", ' stroke-opacity="0.55"')
    F.line(xs[0], T(xs[0]), xs[1], T(xs[1]), "ln c3")
    c.add("</g>")
    c.add(f'<rect x="{X0}" y="{Y0}" width="{W}" height="{H}" class="ln cm hair nofill"/>')
    # level labels on the right edge
    for k in [1, 2, 3, 4]:
        yv = T(xr[1]) - k
        if yr[0] < yv < yr[1]:
            c.text(F.X(xr[1]) + 6, F.Y(yv) + 4, f"s = {k * k / s:g}", "tx-s", "start")
    for k in [1, 2, 3, 4]:
        xv = (yr[1] - k - m) / s
        if xr[0] < xv < xr[1]:
            c.text(F.X(xv), F.Y(yr[1]) - 5, f"s = {k * k / s:g}", "tx-s", "middle")
    # ticks
    for v in [-2, -1, 0, 1, 2]:
        c.add(f'<line x1="{F.X(v):.1f}" y1="{Y0 + H}" x2="{F.X(v):.1f}" y2="{Y0 + H + 4}" class="ax"/>')
        c.text(F.X(v), Y0 + H + 15, f"{v:g}".replace("-", "−"), "tx-s", "middle")
    for v in [-4, -2, 0, 2, 4, 6]:
        c.add(f'<line x1="{X0 - 4}" y1="{F.Y(v):.1f}" x2="{X0}" y2="{F.Y(v):.1f}" class="ax"/>')
        c.text(X0 - 7, F.Y(v) + 4, f"{v:g}".replace("-", "−"), "tx-s", "end")
    c.text(X0 + W, Y0 + H + 30, "x  (source)", "tx-s", "end")
    c.text(X0 - 7, Y0 - 8, "y  (target)", "tx-s", "end")
    # marginal densities: alpha below, beta on the left
    xx = np.linspace(xr[0], xr[1], 241)
    pa = stats.norm.pdf(xx)
    base = Y0 + H + 62
    pts = [(F.X(x), base - 70 * p) for x, p in zip(xx, pa)]
    c.add('<path d="M' + "L".join(f"{u:.1f} {v:.1f}" for u, v in pts) + f'L{F.X(xr[1]):.1f} {base}L{F.X(xr[0]):.1f} {base}Z" class="a2"/>')
    c.add('<path d="M' + "L".join(f"{u:.1f} {v:.1f}" for u, v in pts) + '" class="ln c2 thin"/>')
    c.text(F.X(1.6), base - 12, "α = 𝒩(0,1)", "tx-s t2", "start")
    yy = np.linspace(yr[0], yr[1], 241)
    pb = stats.norm.pdf(yy, m, s)
    left = X0 - 40
    pts = [(left - 160 * p, F.Y(y)) for y, p in zip(yy, pb)]
    c.add('<path d="M' + "L".join(f"{u:.1f} {v:.1f}" for u, v in pts) + f'L{left:.1f} {F.Y(yr[1]):.1f}L{left:.1f} {F.Y(yr[0]):.1f}Z" class="a1"/>')
    c.add('<path d="M' + "L".join(f"{u:.1f} {v:.1f}" for u, v in pts) + '" class="ln c1 thin"/>')
    c.text(left - 6, F.Y(5.6), "β = 𝒩(1,4)", "tx-s t1", "end")
    # annotate the contact line and one point
    F.circle(0.5, T(0.5), 4, "f3")
    label_bg(c, F.X(0.5) + 78, F.Y(T(0.5)) + 17, "(0.5, T(0.5) = 2):  s = 0", "tx-s t3", cw=5.6)
    F.circle(1.0, 0.0, 4, "fk")
    label_bg(c, F.X(1.0) + 56, F.Y(0.0) + 4, "(1, 0):  s = 4.5", "tx-s", cw=5.6)
    label_bg(c, F.X(-1.05), F.Y(T(-1.05)) - 12, "y = T(x) = 1 + 2x", "tx-b t3", cw=7.2, h=15)
    c.save()


def fig_envelope():
    """Discrete c-transform as a lower envelope, for |x-y| and |x-y|^2."""
    xs = np.array([-1.6, -0.45, 0.55, 1.55])
    fs = np.array([0.35, -0.15, 0.45, 0.05])
    c = Canvas("envelope", 660, 270, "Discrete c-transform as the lower envelope of shifted cost curves, for |x-y| and |x-y|^2", sub=SUB)
    for col, (p, title) in enumerate([(1, "c(x, y) = |x − y|"), (2, "c(x, y) = |x − y|²")]):
        F = Fig(c, (40 + col * 320, 30, 270, 190), (-2.2, 2.2), (-0.8, 1.6))
        cid = f"{SUB}-env-clip-{col}"
        c.defs.append(f'<clipPath id="{cid}"><rect x="{F.x0}" y="{F.y0}" width="{F.w}" height="{F.h}"/></clipPath>')
        F.axes(xticks=[-2, -1, 0, 1, 2], yticks=[-0.5, 0, 0.5, 1, 1.5], xfmt=lambda v: f"{v:g}".replace("-", "−"),
               yfmt=lambda v: f"{v:g}".replace("-", "−"), grid=False)
        yy = np.linspace(-2.2, 2.2, 881)
        secs = np.abs(xs[:, None] - yy[None, :]) ** p - fs[:, None]
        env = secs.min(0)
        active = sorted(set(secs.argmin(0).tolist()))
        assert active == [0, 1, 2, 3], active
        c.add(f'<g clip-path="url(#{cid})">')
        for i in range(4):
            F.path(list(zip(yy, secs[i])), "ln cm thin dash")
        F.path(list(zip(yy, env)), "ln c1")
        c.add("</g>")
        for i in range(4):
            F.circle(xs[i], -fs[i], 4.5, "f2")
        c.text(F.x0 + F.w / 2, 18, title, "tx-b", "middle")
        F.text(2.15, env[-1], "f ᶜ", "tx-i t1", "end", dy=-8)
        F.text(xs[0], -fs[0], "(x₁, −f₁)", "tx-s t2", "middle", dy=16)
    c.text(330, 262, "grey dashed: y ↦ c(xᵢ, y) − fᵢ   ·   blue: their lower envelope fᶜ(y) = minᵢ c(xᵢ, y) − fᵢ", "tx-s", "middle")
    c.save()


def fig_brenier():
    """Brenier potentials: Gaussian example (1D) and semi-discrete example (1D)."""
    c = Canvas("brenier", 660, 300, "Convex Brenier potentials: two Gaussians, and a uniform law sent to two atoms", sub=SUB)
    # left: alpha = N(0,1), beta = N(1,4), c = |x-y|^2: f = -x^2 - 2x, phi = x^2 + x
    F = Fig(c, (46, 34, 260, 210), (-2.2, 1.6), (-3.0, 5.0))
    F.axes(xticks=[-2, -1, 0, 1], yticks=[-2, 0, 2, 4], xfmt=lambda v: f"{v:g}".replace("-", "−"),
           yfmt=lambda v: f"{v:g}".replace("-", "−"), grid=False)
    f = lambda x: -x * x - 2 * x
    phi = lambda x: x * x / 2 - f(x) / 2
    assert abs(phi(0.7) - (0.49 + 0.7)) < 1e-12
    F.fn(f, "ln c2 dash", -2.2, 1.6, 300)
    F.fn(phi, "ln c3", -2.2, 1.6, 300)
    x0 = 0.5
    slope = 2 * x0 + 1
    F.line(x0 - 1.3, phi(x0) - 1.3 * slope, x0 + 1.0, phi(x0) + 1.0 * slope, "ln ck thin dot")
    F.circle(x0, phi(x0), 4, "f3")
    F.text(-2.1, 4.4, "φ(x) = x² + x  (convex)", "tx-s t3", "start")
    F.text(-2.1, -2.6, "f(x) = −x² − 2x", "tx-s t2", "start")
    F.text(x0 + 0.08, phi(x0), "slope T(0.5) = 2", "tx-s", "start", dy=16)
    c.text(176, 20, "𝒩(0,1) → 𝒩(1,4):  φ′ = T", "tx-b", "middle")
    # right: alpha = U[0,1], beta = 1/2 d_0.2 + 1/2 d_0.9, c = |x-y|^2 ; phi = max_j x y_j - y_j^2/2 + g_j/2
    y = np.array([0.2, 0.9])
    gopt = np.array([-0.035, 0.035])
    lines = [(yj, -yj * yj / 2 + gj / 2) for yj, gj in zip(y, gopt)]
    phi2 = lambda x: max(a * x + b for a, b in lines)
    kink = (lines[0][1] - lines[1][1]) / (lines[1][0] - lines[0][0])
    assert abs(kink - 0.5) < 1e-12
    G = Fig(c, (380, 34, 250, 120), (0, 1), (-0.1, 0.55))
    G.axes(xticks=[0, 0.5, 1], yticks=[0, 0.25, 0.5], xfmt=fmt1, yfmt=fmt1, grid=False)
    for a, b in lines:
        G.fn(lambda x, a=a, b=b: a * x + b, "ln cm thin dash", 0, 1, 2)
    G.fn(phi2, "ln c3", 0, 1, 400)
    G.text(0.03, 0.47, "φ = max of two lines", "tx-s t3", "start")
    H = Fig(c, (380, 190, 250, 70), (0, 1), (0, 1.05))
    H.axes(xticks=[0, 0.5, 1], yticks=[0.2, 0.9], xfmt=fmt1, yfmt=fmt1, grid=False)
    H.line(0, 0.2, 0.5, 0.2, "ln c3")
    H.line(0.5, 0.9, 1, 0.9, "ln c3")
    H.line(0.5, 0.2, 0.5, 0.9, "ln c3 thin dot")
    H.text(0.97, 0.9, "T = φ′", "tx-s t3", "end", dy=-6)
    c.text(505, 20, "𝒰[0,1] → ½ δ(0.2) + ½ δ(0.9)", "tx-b", "middle")
    c.text(505, 288, "slopes 0.2 and 0.9, kink at x = 0.5", "tx-s", "middle")
    c.save()


def fig_cdf():
    """W1 on the line: alpha = 1/2 d0 + 1/2 d3, beta = U[1,2]; CDFs, area, tent witness."""
    xr = (-0.4, 3.4)
    Ca = lambda x: 0.5 * (x >= 0) + 0.5 * (x >= 3)
    Cb = lambda x: np.clip(x - 1, 0, 1)
    xx = np.linspace(xr[0], xr[1], 38001)
    W1 = np.trapezoid(np.abs(Ca(xx) - Cb(xx)), xx)
    assert abs(W1 - 1.25) < 1e-3
    c = Canvas("cdf", 600, 400, "W1 on the line as the area between two CDFs, with the optimal 1-Lipschitz witness", sub=SUB)
    A = Fig(c, (60, 20, 500, 70), xr, (0, 1.1))
    A.line(xr[0], 0, xr[1], 0, "ax")
    A.lollipop(0, 0.5 * 1.8, 2)
    A.lollipop(3, 0.5 * 1.8, 2)
    A.path([(1, 0), (1, 1.0), (2, 1.0), (2, 0)], "a1", close=True)
    A.path([(1, 0), (1, 1.0), (2, 1.0), (2, 0)], "ln c1 thin nofill")
    A.text(0, 0.9, "½δ₀", "tx-s t2", "start", dx=8)
    A.text(3, 0.9, "½δ₃", "tx-s t2", "end", dx=-8)
    A.text(1.5, 1.0, "β = 𝒰[1,2]", "tx-s t1", "middle", dy=-5)
    B = Fig(c, (60, 120, 500, 130), xr, (-0.05, 1.08))
    B.axes(xticks=[0, 1, 1.5, 2, 3], yticks=[0, 0.5, 1], xfmt=fmt1, yfmt=fmt1, grid=False)
    top = np.maximum(Ca(xx), Cb(xx))
    bot = np.minimum(Ca(xx), Cb(xx))
    pts = list(zip(xx[::50], top[::50])) + list(zip(xx[::-50], bot[::-50]))
    B.path(pts, "a3", close=True)
    B.path([(xr[0], 0), (0, 0), (0, 0.5), (3, 0.5), (3, 1), (xr[1], 1)], "ln c2")
    B.path([(xr[0], 0), (1, 0), (2, 1), (xr[1], 1)], "ln c1")
    c.add(f'<text x="{B.X(0.45):.1f}" y="{B.Y(0.62):.1f}" class="tx-i t2" text-anchor="middle">C<tspan baseline-shift="sub" font-size="11">α</tspan></text>')
    c.add(f'<text x="{B.X(2.35):.1f}" y="{B.Y(1.0) - 6:.1f}" class="tx-i t1" text-anchor="middle">C<tspan baseline-shift="sub" font-size="11">β</tspan></text>')
    B.text(2.65, 0.25, "area = W₁ = 5/4", "tx-s t3", "middle")
    D = Fig(c, (60, 285, 500, 85), xr, (-1.7, 0.3))
    D.axes(xticks=[0, 1, 1.5, 2, 3], yticks=[-1.5, 0], xfmt=fmt1, yfmt=lambda v: f"{v:g}".replace("-", "−"), grid=False)
    D.path([(xr[0], 0.4), (0, 0), (1.5, -1.5), (3, 0), (xr[1], -0.4)], "ln c3")
    D.text(0.55, -0.85, "slope −1", "tx-s t3", "middle")
    D.text(2.45, -0.85, "slope +1", "tx-s t3", "middle")
    D.text(3.38, -0.75, "witness f", "tx-s t3", "end")
    c.save()


def fig_beckmann():
    """Graph Beckmann flow on a 3x2 grid (computed by LP), with the optimal potential."""
    from scipy.optimize import linprog
    nodes = [(x, y) for y in range(2) for x in range(3)]
    idx = {p: k for k, p in enumerate(nodes)}
    edges = []
    for (x, y) in nodes:
        if x < 2:
            edges.append((idx[(x, y)], idx[(x + 1, y)]))
        if y < 1:
            edges.append((idx[(x, y)], idx[(x, y + 1)]))
    a = np.zeros(6); b = np.zeros(6)
    a[idx[(0, 0)]] = 1.0
    b[idx[(2, 0)]] = 0.5; b[idx[(1, 1)]] = 0.5
    r = a - b
    E = len(edges)
    D = np.zeros((6, E))
    for e, (i, j) in enumerate(edges):
        D[i, e] = 1; D[j, e] = -1
    res = linprog(np.ones(2 * E), A_eq=np.hstack([D, -D]), b_eq=r, bounds=[(0, None)] * (2 * E), method="highs")
    m = res.x[:E] - res.x[E:]
    assert abs(res.fun - 2.0) < 1e-9
    fpot = np.array([-(x + y) for (x, y) in nodes], float)
    assert abs(fpot @ r - 2.0) < 1e-12
    c = Canvas("beckmann", 560, 250, "Optimal Beckmann flow on a small grid graph, with the optimal 1-Lipschitz potential", sub=SUB)
    X = lambda x: 110 + 170 * x
    Y = lambda y: 175 - 120 * y
    for (i, j) in edges:
        c.add(f'<line x1="{X(nodes[i][0])}" y1="{Y(nodes[i][1])}" x2="{X(nodes[j][0])}" y2="{Y(nodes[j][1])}" class="ln cm thin"/>')
    mid = c.arrow_marker(3)
    for e, (i, j) in enumerate(edges):
        if abs(m[e]) > 1e-9:
            s_, t_ = (i, j) if m[e] > 0 else (j, i)
            x1, y1, x2, y2 = X(nodes[s_][0]), Y(nodes[s_][1]), X(nodes[t_][0]), Y(nodes[t_][1])
            L = math.hypot(x2 - x1, y2 - y1)
            ux, uy = (x2 - x1) / L, (y2 - y1) / L
            w = 2 + 8 * abs(m[e])
            c.add(f'<line x1="{x1 + 24 * ux:.1f}" y1="{y1 + 24 * uy:.1f}" x2="{x2 - 26 * ux:.1f}" y2="{y2 - 26 * uy:.1f}" class="ln c3" stroke-width="{w:.1f}" marker-end="url(#{mid})"/>')
            lx, ly = (x1 + x2) / 2, (y1 + y2) / 2
            if abs(uy) < 1e-9:
                label_bg(c, lx, ly - 12, f"{abs(m[e]):g}", "tx-s t3")
            else:
                label_bg(c, lx + 18, ly + 4, f"{abs(m[e]):g}", "tx-s t3")
    for k, (x, y) in enumerate(nodes):
        cls = "f2" if a[k] > 0 else ("f1" if b[k] > 0 else "fs")
        c.add(f'<circle cx="{X(x)}" cy="{Y(y)}" r="16" class="{cls}"/>')
        c.add(f'<circle cx="{X(x)}" cy="{Y(y)}" r="16" class="ln cm thin nofill"/>')
        c.text(X(x), Y(y) + 4, f"{fpot[k]:g}".replace("-", "−"), "tx-b", "middle")
    c.text(X(0), Y(0) + 34, "a = 1", "tx-s t2", "middle")
    c.text(X(2), Y(0) + 34, "b = ½", "tx-s t1", "middle")
    c.text(X(1), Y(1) - 24, "b = ½", "tx-s t1", "middle")
    c.text(280, 244, "flow cost Σ ℓₑ|mₑ| = 1 + ½ + ½ = 2 = Σ fᵢ(aᵢ − bᵢ)   (numbers in the vertices: f)", "tx-s", "middle")
    c.save()


def mix_pdf(x, w, m, sd):
    return sum(wk * stats.norm.pdf(x, mk, sk) for wk, mk, sk in zip(w, m, sd))


def fig_witness():
    """Witnesses of TV, W1 and MMD for the same pair of 1D densities."""
    xs = np.linspace(-3.2, 3.2, 6401)
    h = xs[1] - xs[0]
    ra = mix_pdf(xs, [0.5, 0.5], [-1.2, 1.3], [0.35, 0.40])
    rb = mix_pdf(xs, [0.65, 0.35], [-0.4, 0.9], [0.50, 0.30])
    ra /= ra.sum() * h
    rb /= rb.sum() * h
    diff = ra - rb
    TV = np.sum(np.abs(diff)) * h
    wtv = np.sign(diff)
    Ca, Cb = np.cumsum(ra) * h, np.cumsum(rb) * h
    W1 = np.sum(np.abs(Ca - Cb)) * h
    fw = np.concatenate([[0], np.cumsum(-np.sign(Ca - Cb)[:-1] * h)])
    check = np.sum(fw * diff) * h
    assert abs(check - W1) < 2e-3, (check, W1)
    sig = 0.4
    K = np.exp(-(xs[:, None] - xs[None, :]) ** 2 / (2 * sig * sig))
    mxi = K @ diff * h
    MMD = math.sqrt(max(np.sum(mxi * diff) * h, 0))
    wmmd = mxi / MMD
    c = Canvas("witness", 660, 230, "Witness functions of total variation, W1 and MMD for the same pair of densities", sub=SUB)
    panels = [("total variation", TV, wtv, (-1.25, 1.25)), ("W₁", W1, fw - (fw.max() + fw.min()) / 2, None), ("MMD (σ = 0.4)", MMD, wmmd, None)]
    for k, (name, val, wv, yr) in enumerate(panels):
        if yr is None:
            M = np.abs(wv).max() * 1.15
            yr = (-M, M)
        F = Fig(c, (16 + k * 216, 36, 196, 150), (-3.2, 3.2), yr)
        F.line(-3.2, 0, 3.2, 0, "ax")
        sc = 0.9 * yr[1] / max(ra.max(), rb.max())
        F.path([(-3.2, 0)] + list(zip(xs[::20], sc * ra[::20])) + [(3.2, 0)], "a2", close=True)
        F.path([(-3.2, 0)] + list(zip(xs[::20], sc * rb[::20])) + [(3.2, 0)], "a1", close=True)
        F.path(list(zip(xs[::8], wv[::8])), "ln c5")
        c.text(16 + k * 216 + 98, 24, f"{name} = {val:.3f}", "tx-b", "middle")
        for v in [-2, 0, 2]:
            F.text(v, yr[0], f"{v:g}".replace("-", "−"), "tx-s", "middle", dy=14)
    c.text(330, 222, "purple: witness;  shaded: α (orange-red) and β (blue), rescaled", "tx-s", "middle")
    c.save()
    print("   witness values: TV %.4f W1 %.4f MMD %.4f" % (TV, W1, MMD))


def _clip(poly, a, b, cc):
    out = []
    n = len(poly)
    for k in range(n):
        P, Q = poly[k], poly[(k + 1) % n]
        fp, fq = a * P[0] + b * P[1] - cc, a * Q[0] + b * Q[1] - cc
        if fp <= 0:
            out.append(P)
        if fp * fq < 0:
            t = fp / (fp - fq)
            out.append((P[0] + t * (Q[0] - P[0]), P[1] + t * (Q[1] - P[1])))
    return out


def _area(poly):
    if len(poly) < 3:
        return 0.0
    return abs(sum(poly[k][0] * poly[(k + 1) % len(poly)][1] - poly[(k + 1) % len(poly)][0] * poly[k][1] for k in range(len(poly)))) / 2


def _centroid(poly):
    A = cx = cy = 0.0
    for k in range(len(poly)):
        x1, y1 = poly[k]
        x2, y2 = poly[(k + 1) % len(poly)]
        cr = x1 * y2 - x2 * y1
        A += cr; cx += (x1 + x2) * cr; cy += (y1 + y2) * cr
    return (cx / (3 * A), cy / (3 * A))


def power_cells(Y, g):
    cells = []
    for j in range(len(Y)):
        poly = [(0, 0), (1, 0), (1, 1), (0, 1)]
        for k in range(len(Y)):
            if k == j:
                continue
            a = 2 * (Y[k][0] - Y[j][0]); b = 2 * (Y[k][1] - Y[j][1])
            cc = Y[k] @ Y[k] - Y[j] @ Y[j] - g[k] + g[j]
            poly = _clip(poly, a, b, cc)
            if len(poly) < 3:
                break
        cells.append(poly)
    return cells


def _int_sq(poly, y):
    s = 0.0
    p0 = np.array(poly[0])
    for k in range(1, len(poly) - 1):
        p1, p2 = np.array(poly[k]), np.array(poly[k + 1])
        A = abs((p1 - p0)[0] * (p2 - p0)[1] - (p1 - p0)[1] * (p2 - p0)[0]) / 2
        s += A / 3 * sum(np.sum((m - y) ** 2) for m in [(p0 + p1) / 2, (p1 + p2) / 2, (p0 + p2) / 2])
    return s


def fig_laguerre():
    """Voronoi versus balanced power diagram for 5 sites and the uniform law on the square."""
    Y = np.array([[0.2, 0.25], [0.75, 0.2], [0.5, 0.55], [0.2, 0.8], [0.8, 0.8]])
    b = np.array([0.10, 0.15, 0.35, 0.20, 0.20])
    g = np.zeros(5)
    for it in range(400):
        cells = power_cells(Y, g)
        mass = np.array([_area(P) for P in cells])
        g = g + 0.3 * (b - mass)
    g = g - g.mean()
    cells = power_cells(Y, g)
    mass = np.array([_area(P) for P in cells])
    assert np.abs(mass - b).max() < 1e-9
    E = sum(_int_sq(P, Y[j]) - g[j] * _area(P) for j, P in enumerate(cells)) + g @ b
    assert abs(E - 0.050684) < 2e-6, E
    vor = power_cells(Y, np.zeros(5))
    vmass = [_area(P) for P in vor]
    c = Canvas("laguerre", 660, 330, "Voronoi cells versus balanced Laguerre (power) cells for five atoms with prescribed masses", sub=SUB)
    fills = ["a1", "a2", "a3", "a4", "a5"]
    for col, (cl, ms, title) in enumerate([(vor, vmass, "zero weights: Voronoi cells"), (cells, mass, "optimal weights g*: power cells")]):
        X0, Y0, S = 40 + col * 320, 36, 260
        X = lambda x: X0 + S * x
        Yp = lambda y: Y0 + S * (1 - y)
        for j, P in enumerate(cl):
            d = "M" + "L".join(f"{X(p[0]):.1f} {Yp(p[1]):.1f}" for p in P) + "Z"
            c.add(f'<path d="{d}" class="{fills[j]}"/>')
            c.add(f'<path d="{d}" class="ln ck thin nofill" stroke-opacity="0.6"/>')
        c.add(f'<rect x="{X0}" y="{Y0}" width="{S}" height="{S}" class="ln cm thin nofill"/>')
        for j, P in enumerate(cl):
            cx, cy = _centroid(P)
            c.add(f'<circle cx="{X(Y[j][0]):.1f}" cy="{Yp(Y[j][1]):.1f}" r="4.5" class="fk"/>')
            lab = f"{ms[j]:.2f}" if col == 1 else f"{ms[j]:.2f} (b = {b[j]:.2f})"
            tx, ty = X(cx), Yp(cy)
            if abs(tx - X(Y[j][0])) < 30 and abs(ty - Yp(Y[j][1])) < 14:
                ty = Yp(Y[j][1]) + 18
            label_bg(c, tx, ty, lab, "tx-s", cw=5.6)
        c.text(X0 + S / 2, Y0 - 12, title, "tx-b", "middle")
    c.text(330, 324, f"target masses b = (0.10, 0.15, 0.35, 0.20, 0.20)   ·   W₂² = {E:.5f}", "tx-s", "middle")
    c.save()
    print("   laguerre: g* =", np.round(g, 4), " Voronoi masses", np.round(vmass, 4))


def fig_lloyd():
    """Lloyd iterations for U[0,1] with two codepoints, from (0.1, 0.3)."""
    Yv = np.array([0.1, 0.3])
    rows = []
    for it in range(5):
        wall = (Yv[0] + Yv[1]) / 2
        en = integrate.quad(lambda x: (x - Yv[0]) ** 2, 0, wall)[0] + integrate.quad(lambda x: (x - Yv[1]) ** 2, wall, 1)[0]
        rows.append((it, Yv.copy(), wall, en))
        Yv = np.array([wall / 2, (wall + 1) / 2])
    rows.append(("∞", np.array([0.25, 0.75]), 0.5, 1 / 48))
    c = Canvas("lloyd", 600, 250, "Lloyd iterations for the uniform law on [0,1] with two codepoints", sub=SUB)
    for r, (it, Yv, wall, en) in enumerate(rows):
        yy = 30 + r * 36
        F = Fig(c, (90, yy - 10, 360, 20), (0, 1), (-1, 1))
        c.add(f'<rect x="{F.X(0):.1f}" y="{yy - 5}" width="{F.X(1) - F.X(0):.1f}" height="10" class="a2"/>')
        F.line(0, 0, 1, 0, "ax")
        F.line(wall, -0.9, wall, 0.9, "ln ck thin dash")
        for v in Yv:
            F.circle(v, 0, 5, "f3")
        c.text(70, yy + 4, f"ℓ = {it}", "tx-s", "end")
        c.text(470, yy + 4, f"energy {en:.6f}", "tx-s", "start")
    F.text(0, -1, "0", "tx-s", "middle", dy=16)
    F.text(1, -1, "1", "tx-s", "middle", dy=16)
    F.text(0.5, -1, "0.5", "tx-s", "middle", dy=16)
    c.text(270, 246, "green: codepoints;  dashed: Voronoi wall;  shaded: the uniform source", "tx-s", "middle")
    c.save()


def fig_vi():
    """One Gaussian fitted to a bimodal target: forward KL, reverse KL, W2."""
    w = [0.3, 0.7]; mu = [-2.0, 2.0]; sd = [0.5, 0.5]
    pi = lambda x: mix_pdf(x, w, mu, sd)
    mean = float(np.dot(w, mu))
    var = float(np.dot(w, np.square(sd) + np.square(mu)) - mean ** 2)
    assert abs(mean - 0.8) < 1e-12 and abs(math.sqrt(var) - 1.9) < 1e-12
    Q = lambda u: optimize.brentq(lambda t: sum(wk * stats.norm.cdf(t, mk, sk) for wk, mk, sk in zip(w, mu, sd)) - u, -20, 20, xtol=1e-13)
    sW = integrate.quad(lambda u: (Q(u) - mean) * stats.norm.ppf(u), 0, 1, limit=400, points=[0.3])[0]
    assert abs(sW - 1.7036) < 1e-3, sW
    c = Canvas("vi", 600, 260, "Fitting one Gaussian to a bimodal target with forward KL, reverse KL and W2", sub=SUB)
    F = Fig(c, (40, 30, 520, 180), (-4.5, 5.5), (0, 0.62))
    F.axes(xticks=[-4, -2, 0, 2, 4], yticks=[], xfmt=lambda v: f"{v:g}".replace("-", "−"), grid=False, yaxis=False)
    xs = np.linspace(-4.5, 5.5, 801)
    F.path([(-4.5, 0)] + [(x, pi(x)) for x in xs] + [(5.5, 0)], "a1", close=True)
    F.fn(pi, "ln c1 thin", n=800)
    F.fn(lambda x: stats.norm.pdf(x, mean, math.sqrt(var)), "ln c4", n=600)
    F.fn(lambda x: stats.norm.pdf(x, 2.0, 0.5003), "ln c5", n=600)
    F.fn(lambda x: stats.norm.pdf(x, -2.0, 0.5006), "ln c5 dot", n=600)
    F.fn(lambda x: stats.norm.pdf(x, mean, sW), "ln c3 dash", n=600)
    F.text(2.55, 0.56, "π = 0.3 𝒩(−2, 0.5²) + 0.7 𝒩(2, 0.5²)", "tx-s t1", "start")
    F.text(2.35, 0.79, "", "tx-s", "start")
    c.text(300, 236, "gold: forward KL / maximum likelihood  𝒩(0.8, 1.9²)   ·   green dashed: W₂ fit  𝒩(0.8, 1.70²)", "tx-s", "middle")
    c.text(300, 252, "purple: reverse KL (VI), best local minimum 𝒩(2, 0.5²); dotted: the other one 𝒩(−2, 0.5²)", "tx-s", "middle")
    c.save()


def fig_gmm():
    """Component-wise maps (MW2) versus the true monotone map between N(0,1) and a two-component mixture."""
    QB = lambda u: optimize.brentq(lambda t: 0.5 * stats.norm.cdf(t, -1, 0.5) + 0.5 * stats.norm.cdf(t, 1, 0.5) - u, -20, 20, xtol=1e-13)
    w2 = integrate.quad(lambda u: (stats.norm.ppf(u) - QB(u)) ** 2, 0, 1, limit=400)[0]
    assert abs(w2 - 0.07325) < 1e-4, w2
    c = Canvas("gmm", 660, 300, "Component-wise transport between Gaussian mixtures versus the true optimal map", sub=SUB)
    for col, title in enumerate([f"component-wise:  MW₂² = 1.25", f"optimal map:  W₂² = {w2:.3f}"]):
        X0 = 70 + col * 320
        F = Fig(c, (X0, 30, 220, 200), (-3, 3), (-3, 3))
        F.axes(xticks=[-2, 0, 2], yticks=[-2, 0, 2], xfmt=lambda v: f"{v:g}".replace("-", "−"), yfmt=lambda v: f"{v:g}".replace("-", "−"), grid=True)
        xs = np.linspace(-3, 3, 241)
        pa = stats.norm.pdf(xs)
        base = 30 + 200 + 34
        pts = [(F.X(x), base - 60 * p) for x, p in zip(xs, pa)]
        c.add('<path d="M' + "L".join(f"{u:.1f} {v:.1f}" for u, v in pts) + f'L{F.X(3):.1f} {base}L{F.X(-3):.1f} {base}Z" class="a2"/>')
        pb = 0.5 * stats.norm.pdf(xs, -1, 0.5) + 0.5 * stats.norm.pdf(xs, 1, 0.5)
        left = X0 - 30
        pts = [(left - 45 * p, F.Y(y)) for y, p in zip(xs, pb)]
        c.add('<path d="M' + "L".join(f"{u:.1f} {v:.1f}" for u, v in pts) + f'L{left:.1f} {F.Y(3):.1f}L{left:.1f} {F.Y(-3):.1f}Z" class="a1"/>')
        if col == 0:
            F.fn(lambda x: -1 + x / 2, "ln c3", n=10)
            F.fn(lambda x: 1 + x / 2, "ln c3", n=10)
            F.text(-2.9, 2.5, "y = 1 + x/2  (mass ½)", "tx-s t3", "start")
            F.text(2.9, -2.6, "y = −1 + x/2  (mass ½)", "tx-s t3", "end")
        else:
            ys = [QB(stats.norm.cdf(x)) for x in xs[1:-1]]
            F.path(list(zip(xs[1:-1], ys)), "ln c3")
            F.text(-2.9, 2.5, "T = Q_β ∘ C_α", "tx-s t3", "start")
        c.text(X0 + 110, 20, title, "tx-b", "middle")
    c.text(330, 292, "orange-red (bottom): α = 𝒩(0,1);  blue (left): β = ½𝒩(−1, 0.25) + ½𝒩(1, 0.25)", "tx-s", "middle")
    c.save()


if __name__ == "__main__":
    for fn in [fig_prices, fig_slack, fig_envelope, fig_brenier, fig_cdf, fig_beckmann, fig_witness, fig_laguerre, fig_lloyd, fig_vi, fig_gmm]:
        fn()
