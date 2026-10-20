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
    label_bg(c, F.X(0.5) + 82, F.Y(T(0.5)) + 16, "(0.5, T(0.5) = 2):  s = 0", "tx-s t3")
    F.circle(1.0, 0.0, 4, "fk")
    label_bg(c, F.X(1.0) + 50, F.Y(0.0) + 4, "(1, 0):  s = 4.5", "tx-s")
    label_bg(c, F.X(-1.05), F.Y(T(-1.05)) - 12, "y = T(x) = 1 + 2x", "tx-b t3", cw=7.2, h=15)
    c.save()


if __name__ == "__main__":
    for fn in [fig_prices, fig_slack]:
        fn()
