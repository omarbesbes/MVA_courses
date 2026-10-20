"""figures_L08.py — static SVG figures of Lesson 8 (Wasserstein gradient flows), written to figures/L08/.

Run: python3 figures_L08.py        (then node build.mjs Lesson08.html)
Every curve is computed here: closed forms (Gaussian flows, Ornstein-Uhlenbeck), ODE solutions (scipy) and exact
transport plans (POT) where needed.
"""
import math

import numpy as np

from figures_common import Canvas, Fig

SUB = "L08"


def gauss(x, m, s):
    return np.exp(-0.5 * ((x - m) / s) ** 2) / (s * math.sqrt(2 * math.pi))


def mix_pdf(x, w, m, s):
    return sum(wk * gauss(x, mk, sk) for wk, mk, sk in zip(w, m, s))


def filled(f, xs, ys, cls_fill, cls_line):
    """A density curve with a light fill under it."""
    pts = list(zip(xs, ys))
    f.path([(xs[0], 0)] + pts + [(xs[-1], 0)], cls_fill, close=True)
    f.path(pts, cls_line)


# ---------------------------------------------------------------------------------------------
def fig_euler():
    c = Canvas("euler", 660, 270, "Explicit versus implicit Euler steps; one implicit step for the absolute value", sub=SUB)
    # left: stiff quadratic h = 5 x^2 (L = 10), tau = 0.25
    f = Fig(c, (52, 30, 260, 190), (0, 1.05), (-4, 6))
    f.axes(xticks=[0, 0.25, 0.5, 0.75, 1], yticks=[-4, -2, 0, 2, 4, 6], xfmt=lambda v: f"{v:g}", xlabel="time t")
    L, tau = 10.0, 0.25
    f.fn(lambda t: math.exp(-L * t), "ln c1", 0, 1.05, 300)
    ex = [(k * tau, (1 - tau * L) ** k) for k in range(5)]
    im = [(k * tau, (1 + tau * L) ** (-k)) for k in range(5)]
    f.path(ex, "ln c5 thin")
    f.path(im, "ln c3 thin")
    for (t, v) in ex:
        f.circle(t, v, 4, "f5")
    for (t, v) in im:
        f.circle(t, v, 4, "f3")
    # legend in the empty upper-left corner
    f.circle(0.04, 5.3, 4, "f5")
    f.text(0.04, 5.3, "explicit: × (1 − τL) = × (−1.5)", "tx-s t5", "start", dx=8, dy=4)
    f.circle(0.04, 4.4, 4, "f3")
    f.text(0.04, 4.4, "implicit: × 1/(1 + τL) = × 0.286", "tx-s t3", "start", dx=8, dy=4)
    f.line(0.015, 3.5, 0.065, 3.5, "ln c1")
    f.text(0.04, 3.5, "exact e⁻¹⁰ᵗ", "tx-s t1", "start", dx=8, dy=4)
    c.text(182, 18, "h(x) = 5x², x₀ = 1, step τ = 0.25", "tx-b", "middle")
    # right: one implicit step for h = |x|, x_k = 1.5, tau = 0.5
    g = Fig(c, (390, 30, 250, 190), (-1.0, 2.6), (0, 3.0))
    g.axes(xticks=[-1, 0], yticks=[0, 1, 2, 3], xfmt=lambda v: f"{v:g}", grid=False)
    xk, tk = 1.5, 0.5
    g.fn(lambda x: abs(x), "ln cm", -1.0, 2.6, 400)
    g.fn(lambda x: (x - xk) ** 2 / (2 * tk), "ln c5 thin dash", -0.2, 2.6, 400)
    g.fn(lambda x: abs(x) + (x - xk) ** 2 / (2 * tk), "ln c3", -0.15, 2.28, 400)
    g.line(1.0, 0, 1.0, 1.25, "ln c3 thin dot")
    g.circle(1.0, 1.25, 4.5, "f3")
    g.circle(xk, 0, 4.5, "f2")
    g.circle(1.0, 0, 4.5, "f3")
    g.text(1.0, 0, "xₖ₊₁ = 1", "tx-s t3", "end", dx=2, dy=16)
    g.text(xk, 0, "xₖ = 1.5", "tx-s t2", "start", dx=-2, dy=16)
    g.text(-0.95, 1.0, "h(x) = |x|", "tx-s", "start", dy=-4)
    g.text(2.6, 0.95, "(x − xₖ)²/(2τ)", "tx-s t5", "end", dy=-10)
    g.text(2.25, 2.75, "sum", "tx-s t3", "end")
    c.text(515, 18, "one implicit step: τ = 0.5, xₖ = 1.5", "tx-b", "middle")
    c.text(330, 262, "left: the explicit step overshoots and blows up when τ > 2/L; right: the implicit step needs no derivative", "tx-s", "middle")
    c.save()


def fig_jko_heat():
    c = Canvas("jko_heat", 660, 270, "JKO steps for the heat equation from a Gaussian, against the exact heat flow", sub=SUB)
    s0, tau = 0.5, 0.25
    # JKO standard deviations (closed form), exact sqrt(s0^2 + 2t)
    def jko_sigmas(tau, T=1.0):
        s, out = s0, [(0.0, s0)]
        for k in range(1, int(round(T / tau)) + 1):
            s = (s + math.sqrt(s * s + 4 * tau)) / 2
            out.append((k * tau, s))
        return out
    js = jko_sigmas(tau)
    f = Fig(c, (40, 30, 300, 190), (-4.2, 4.2), (0, 0.85))
    f.axes(xticks=[-4, -2, 0, 2, 4], yticks=[], grid=False, yaxis=False)
    xs = np.linspace(-4.2, 4.2, 400)
    filled(f, xs, gauss(xs, 0, s0), "a2", "ln c2 thin")
    for (t, sj) in [js[1], js[4]]:
        se = math.sqrt(s0 ** 2 + 2 * t)
        f.path(list(zip(xs, gauss(xs, 0, se))), "ln c3")
        f.path(list(zip(xs, gauss(xs, 0, sj))), "ln c5 thin dash")
    f.text(0.35, 0.79, "t = 0", "tx-s t2", "start")
    f.text(0.0, gauss(0, 0, js[1][1]), "t = 0.25", "tx-s", "start", dx=8, dy=-2)
    f.text(1.45, gauss(1.45, 0, 1.5) + 0.02, "t = 1", "tx-s", "start", dx=4, dy=-6)
    c.text(190, 18, "densities: exact (green), JKO with τ = 0.25 (purple, dashed)", "tx-b", "middle")
    g = Fig(c, (410, 30, 230, 190), (0, 1.02), (0.4, 1.6))
    g.axes(xticks=[0, 0.25, 0.5, 0.75, 1], yticks=[0.5, 1.0, 1.5], xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:g}", xlabel="time t", ylabel="standard deviation")
    g.fn(lambda t: math.sqrt(s0 ** 2 + 2 * t), "ln c3", 0, 1.02, 200)
    js2 = jko_sigmas(0.0625)
    for (t, sj) in js2:
        g.circle(t, sj, 2.6, "f5")
    for (t, sj) in js:
        g.circle(t, sj, 4.5, "f5")
    g.text(0.55, math.sqrt(0.25 + 1.1) + 0.02, "exact √(0.25 + 2t)", "tx-s t3", "end", dy=-8)
    g.text(1.0, 0.66, "JKO, τ = 0.25 (big dots)", "tx-s t5", "end")
    g.text(1.0, 0.55, "and τ = 0.0625 (small dots)", "tx-s t5", "end")
    c.text(330, 262, "each JKO step solves σ² − σₗσ − τ = 0; the error at t = 1 is 0.076 for τ = 0.25 and 0.022 for τ = 0.0625 (first order)", "tx-s", "middle")
    c.save()


def fig_vert_horiz():
    c = Canvas("vert_horiz", 660, 250, "Vertical perturbation by mixing versus horizontal perturbation by moving mass", sub=SUB)
    xs = np.linspace(-3, 4.2, 500)
    a = gauss(xs, -0.5, 0.7)
    # left: mixing
    f = Fig(c, (30, 34, 290, 150), (-3, 4.2), (0, 0.66))
    f.line(-3, 0, 4.2, 0, "ax")
    th = 0.2
    b = gauss(xs, 2.6, 0.35)
    filled(f, xs, a, "a2", "ln c2 thin")
    f.path(list(zip(xs, b * 0.55)), "ln c1 thin dash")
    f.path(list(zip(xs, (1 - th) * a + th * b)), "ln cm")
    pk = gauss(-0.5, -0.5, 0.7)
    c.arrow(f.X(-0.5), f.Y(pk) - 2, f.X(-0.5), f.Y((1 - th) * pk) + 2, 5, "ln c5 thin")
    c.arrow(f.X(2.6), f.Y(0.0) - 2, f.X(2.6), f.Y(th * gauss(2.6, 2.6, 0.35)) + 3, 5, "ln c5 thin")
    f.text(-0.5, pk, "α", "tx-i t2", "middle", dx=-14, dy=4)
    f.text(2.6, 0.55 * gauss(2.6, 2.6, 0.35), "β (shape)", "tx-s t1", "start", dx=10, dy=4)
    f.text(1.0, 0.2, "(1 − ϑ)α + ϑβ", "tx-s", "start", dy=-16)
    c.text(175, 22, "mixing (vertical): mass appears and disappears", "tx-b", "middle")
    c.text(175, 205, "read by the first variation δf/δα:", "tx-s", "middle")
    c.text(175, 219, "a function — the value of a unit of mass at x", "tx-s", "middle")
    # right: moving, T(x) = 1.4 x + 1.2
    g = Fig(c, (360, 34, 290, 150), (-3, 4.2), (0, 0.66))
    g.line(-3, 0, 4.2, 0, "ax")
    filled(g, xs, a, "a2", "ln c2 thin")
    T = lambda x: 1.4 * x + 1.2
    g.path(list(zip(xs, gauss(xs, 0.5, 0.98))), "ln c3")
    for x in [-1.6, -0.9, -0.3, 0.3]:
        y = 0.08 + 0.06 * (x + 1.6)
        c.arrow(g.X(x), g.Y(y), g.X(T(x)) - 3, g.Y(y), 3, "ln c3 thin")
        g.circle(x, y, 2.6, "f2")
    g.text(-0.5, pk, "α", "tx-i t2", "middle", dx=-14, dy=4)
    g.text(2.2, gauss(2.2, 0.5, 0.98), "(Id + τv)#α", "tx-s t3", "start", dx=6, dy=-4)
    c.text(505, 22, "moving (horizontal): mass slides along v", "tx-b", "middle")
    c.text(505, 205, "read by the Wasserstein gradient ∇δf/δα:", "tx-s", "middle")
    c.text(505, 219, "a vector field — where moving mass raises f", "tx-s", "middle")
    c.save()


def fig_four_flows():
    c = Canvas("four_flows", 660, 230, "Four Wasserstein gradient flows from the same two-bump density", sub=SUB)
    w0, m0, s0 = np.array([0.5, 0.5]), np.array([-1.0, 2.0]), np.array([0.3, 0.4])
    M = float(w0 @ m0)
    xs = np.linspace(-3.5, 4.0, 600)

    def comps(kind, t):
        if kind == "pot":   # V = x^2/4: x(t) = x0 e^{-t/2}
            e = math.exp(-0.5 * t); return m0 * e, s0 * e
        if kind == "heat":
            return m0, np.sqrt(s0 ** 2 + 2 * t)
        if kind == "agg":   # velocity -(x - M)/2
            e = math.exp(-0.5 * t); return M + (m0 - M) * e, s0 * e
        e = math.exp(-t)    # Ornstein-Uhlenbeck towards N(0,1)
        return m0 * e, np.sqrt(s0 ** 2 * e * e + 1 - e * e)
    panels = [("pot", "potential ∫ x²/4 dα", "∂ₜρ = div(ρ x/2)"), ("heat", "entropy ∫ ρ log ρ", "∂ₜρ = Δρ"),
              ("agg", "interaction ⅛∬(x−y)²", "∂ₜρ = div(ρ (x − m)/2)"), ("fp", "KL(· | 𝒩(0,1))", "∂ₜρ = Δρ + div(ρ x)")]
    for i, (kind, title, pde) in enumerate(panels):
        f = Fig(c, (14 + i * 162, 34, 148, 140), (-3.5, 4.0), (0, 1.3))
        f.line(-3.5, 0, 4.0, 0, "ax")
        for v in [-2, 0, 2]:
            f.text(v, 0, f"{v:g}", "tx-s", "middle", dy=13)
        filled(f, xs, mix_pdf(xs, w0, m0, s0), "a2", "ln c2 thin")
        if kind == "fp":
            f.path(list(zip(xs, gauss(xs, 0, 1))), "ln c1 thin dash")
        if kind == "agg":
            f.line(M, 0, M, 1.3, "ln cm thin dot")
        for t, cls in [(0.4, "ln c3 thin"), (1.2, "ln c3")]:
            m, sd = comps(kind, t)
            f.path(list(zip(xs, np.minimum(mix_pdf(xs, w0, m, sd), 1.3))), cls)
        c.text(14 + i * 162 + 74, 22, title, "tx-b", "middle")
        c.text(14 + i * 162 + 74, 204, pde, "tx-s", "middle")
    c.text(330, 224, "orange-red: t = 0;  thin green: t = 0.4;  thick green: t = 1.2;  dotted line: the conserved mean (interaction)", "tx-s", "middle")
    c.save()


if __name__ == "__main__":
    for fn in [fig_euler, fig_jko_heat, fig_vert_horiz, fig_four_flows]:
        fn()
