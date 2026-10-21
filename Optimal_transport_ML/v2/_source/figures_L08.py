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
    f.line(0.45, gauss(0.45, 0, math.sqrt(s0 ** 2 + 0.5)), 1.5, 0.55, "ln cm hair")
    f.text(1.5, 0.55, "t = 0.25", "tx-s", "start", dx=4, dy=4)
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
    f.text(1.15, 0.43, "(1 − ϑ)α + ϑβ", "tx-s", "middle")
    f.line(1.95, 0.405, 2.4, 0.215, "ln cm hair")
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


def fig_three_reps():
    """Ornstein-Uhlenbeck flow from two bumps: Langevin paths, deterministic score particles (quantiles), densities."""
    from scipy.special import ndtr
    from scipy.optimize import brentq
    c = Canvas("three_reps", 660, 264, "One Fokker-Planck flow, three representations: noisy particles, deterministic particles, density", sub=SUB)
    w, m, sd = np.array([0.5, 0.5]), np.array([-2.0, 2.0]), np.array([0.3, 0.3])
    T = 3.0

    def law(t):
        e = math.exp(-t)
        return m * e, np.sqrt(sd ** 2 * e * e + 1 - e * e)
    ts = np.linspace(0, T, 121)
    # (a) Langevin paths, Euler-Maruyama with a small step
    rng = np.random.default_rng(3)
    h, K = 0.005, int(T / 0.005)
    starts = np.array([-2.3, -2.0, -1.7, 1.7, 2.0, 2.3])
    X = starts.copy(); P = [X.copy()]
    for k in range(K):
        X = X - h * X + math.sqrt(2 * h) * rng.standard_normal(X.size)
        P.append(X.copy())
    P = np.array(P); tt = np.arange(K + 1) * h
    f = Fig(c, (40, 30, 180, 170), (0, T), (-3.6, 3.6))
    f.axes(xticks=[0, 1, 2, 3], yticks=[-3, 0, 3], xfmt=lambda v: f"{v:g}", grid=False)
    for j in range(len(starts)):
        f.path(list(zip(tt[::4], P[::4, j])), "ln c5 hair")
    c.text(130, 20, "(LD) Langevin particles", "tx-b", "middle")
    c.text(130, 234, "noisy, independent, they cross", "tx-s", "middle")
    # (b) deterministic score particles = quantile curves of the exact law
    g = Fig(c, (260, 30, 180, 170), (0, T), (-3.6, 3.6))
    g.axes(xticks=[0, 1, 2, 3], yticks=[-3, 0, 3], xfmt=lambda v: f"{v:g}", grid=False)
    levels = [0.04, 0.12, 0.25, 0.38, 0.47, 0.53, 0.62, 0.75, 0.88, 0.96]
    for u in levels:
        pts = []
        for t in ts:
            mm, ss = law(t)
            q = brentq(lambda x: (w * ndtr((x - mm) / ss)).sum() - u, -10, 10, xtol=1e-12)
            pts.append((t, q))
        g.path(pts, "ln c3 thin")
    c.text(350, 20, "(WGF) score particles", "tx-b", "middle")
    c.text(350, 234, "ẋ = −x − ∂ₓ log ρₜ: smooth, ordered", "tx-s", "middle")
    # (c) densities
    k = Fig(c, (480, 30, 165, 170), (-3.6, 3.6), (0, 0.75))
    k.line(-3.6, 0, 3.6, 0, "ax")
    for v in [-3, 0, 3]:
        k.text(v, 0, f"{v:g}", "tx-s", "middle", dy=13)
    xs = np.linspace(-3.6, 3.6, 300)
    filled(k, xs, mix_pdf(xs, w, m, sd), "a2", "ln c2 thin")
    for t, cls in [(0.3, "ln c3 thin"), (1.0, "ln c3 thin"), (3.0, "ln c3")]:
        mm, ss = law(t)
        k.path(list(zip(xs, np.minimum(mix_pdf(xs, w, mm, ss), 0.75))), cls)
    k.path(list(zip(xs, gauss(xs, 0, 1))), "ln c1 thin dash")
    c.text(562, 20, "(FP) the density", "tx-b", "middle")
    c.text(562, 234, "t = 0, 0.3, 1, 3; target 𝒩(0,1)", "tx-s", "middle")
    c.text(330, 254, "the three objects describe the same curve of measures αₜ (Ornstein–Uhlenbeck flow from ½𝒩(−2,0.3²) + ½𝒩(2,0.3²))", "tx-s", "middle")
    c.save()


def fig_nonconvex():
    import ot
    c = Canvas("nonconvex", 640, 270, "The squared Wasserstein distance to a fixed measure is not geodesically convex in the plane", sub=SUB)
    f = Fig(c, (40, 30, 200, 200), (-1.35, 1.35), (-1.35, 1.35))
    f.line(-1.35, 0, 1.35, 0, "gr")
    f.line(0, -1.35, 0, 1.35, "gr")
    A0 = [(-1, 0), (1, 0)]; A1 = [(0, 1), (0, -1)]; B = [(-0.5, -0.5), (0.5, 0.5)]
    for p0, p1 in zip(A0, A1):
        f.line(p0[0], p0[1], p1[0], p1[1], "ln cm thin dash")
        f.circle((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, 6, "f3")
    for p0 in A0:
        f.circle(p0[0], p0[1], 6, "f2")
    for p1 in A1:
        f.circle(p1[0], p1[1], 6, "f5")
    for q in B:
        c.add(f'<rect x="{f.X(q[0]) - 5:.1f}" y="{f.Y(q[1]) - 5:.1f}" width="10" height="10" class="f1"/>')
    f.text(-1, 0, "α₀", "tx-i t2", "middle", dy=-10)
    f.text(1, 0, "α₀", "tx-i t2", "middle", dy=-10)
    f.text(0, 1, "α₁", "tx-i t5", "start", dx=8, dy=4)
    f.text(0, -1, "α₁", "tx-i t5", "start", dx=8, dy=4)
    f.text(0.5, 0.5, "β", "tx-i t1", "start", dx=8, dy=4)
    f.text(-0.5, -0.5, "β", "tx-i t1", "end", dx=-8, dy=4)
    f.text(-0.5, 0.5, "α½", "tx-i t3", "end", dx=-8, dy=-4)
    c.text(140, 20, "one geodesic from α₀ to α₁ (dashed)", "tx-b", "middle")
    c.text(140, 250, "W₂²(α₀,β) = W₂²(α₁,β) = ½, but W₂²(α½,β) = 1", "tx-s", "middle")
    # right: t -> W2^2(alpha_t, beta) along this geodesic
    w = np.array([0.5, 0.5]); Bm = np.array(B)
    ts = np.linspace(0, 1, 101); vals = []
    for t in ts:
        X = np.array([((1 - t) * p0[0] + t * p1[0], (1 - t) * p0[1] + t * p1[1]) for p0, p1 in zip(A0, A1)])
        vals.append(ot.emd2(w, w, ot.dist(X, Bm)))
    g = Fig(c, (330, 30, 280, 190), (0, 1), (-0.05, 1.1))
    g.axes(xticks=[0, 0.25, 0.5, 0.75, 1], yticks=[0, 0.5, 1], xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:g}", xlabel="t", ylabel="W₂²(αₜ, β)")
    g.fn(lambda t: 0.5, "ln cm thin dash", 0, 1, 10)
    g.fn(lambda t: 0.5 - 2 * t * (1 - t), "ln c5 thin dash", 0, 1, 200)
    g.path(list(zip(ts, vals)), "ln c3")
    g.text(0.5, 1.0, "along the geodesic: 1 at t = ½", "tx-s t3", "middle", dy=-8)
    g.text(0.97, 0.5, "chord (convexity would need ≤)", "tx-s", "end", dy=-6)
    g.text(0.5, 0.3, "2-semiconcavity bound", "tx-s t5", "middle")
    g.text(0.5, 0.2, "½ − 2t(1 − t)", "tx-s t5", "middle")
    c.save()


def fig_lsi():
    c = Canvas("lsi", 660, 280, "Entropy decay and the Talagrand, HWI and log-Sobolev bounds along the Ornstein-Uhlenbeck flow from N(2, 0.25)", sub=SUB)
    def KL(m, s2): return 0.5 * (s2 + m * m - 1 - math.log(s2))
    def I(m, s2): sd = math.sqrt(s2); return m * m + (sd - 1 / sd) ** 2
    def W(m, s2): return math.sqrt(m * m + (math.sqrt(s2) - 1) ** 2)
    ts = np.linspace(0, 3, 241)
    H0, W0 = KL(2, 0.25), W(2, 0.25)
    # left: entropy and distance with their guaranteed decays (log scale)
    f = Fig(c, (58, 34, 250, 190), (0, 3), (-3, 1))
    f.axes(xticks=[0, 1, 2, 3], yticks=[-3, -2, -1, 0, 1], xfmt=lambda v: f"{v:g}", yfmt=lambda v: {-3: "10⁻³", -2: "10⁻²", -1: "10⁻¹", 0: "1", 1: "10"}[int(v)], xlabel="time t")
    H, Wd, Hb, Wb = [], [], [], []
    for t in ts:
        m, s2 = 2 * math.exp(-t), 1 - 0.75 * math.exp(-2 * t)
        H.append((t, math.log10(KL(m, s2)))); Hb.append((t, math.log10(H0 * math.exp(-2 * t))))
        Wd.append((t, math.log10(W(m, s2)))); Wb.append((t, math.log10(W0 * math.exp(-t))))
    f.path(Hb, "ln cm thin dash"); f.path(H, "ln c3")
    f.path(Wb, "ln cm thin dot"); f.path(Wd, "ln c1")
    f.text(1.55, math.log10(KL(2 * math.exp(-1.55), 1 - 0.75 * math.exp(-3.1))), "H = KL(αₜ | 𝒩(0,1))", "tx-s t3", "end", dx=-6, dy=10)
    f.text(0.08, -2.3, "dashed: H(0) e⁻²ᵗ", "tx-s", "start")
    f.text(0.75, math.log10(W(2 * math.exp(-0.75), 1 - 0.75 * math.exp(-1.5))), "W = W₂(αₜ, 𝒩(0,1))", "tx-s t1", "start", dy=-10)
    f.text(0.08, -2.6, "dotted: W(0) e⁻ᵗ", "tx-s", "start")
    c.text(183, 20, "decay of entropy and distance (log scale)", "tx-b", "middle")
    # right: each static bound divided by H
    g = Fig(c, (390, 34, 250, 190), (0, 3), (0.85, 1.4))
    g.axes(xticks=[0, 1, 2, 3], yticks=[0.9, 1.0, 1.1, 1.2, 1.3, 1.4], xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:.1f}", xlabel="time t")
    R = {"tal": [], "hwi": [], "lsi": []}
    for t in ts:
        m, s2 = 2 * math.exp(-t), 1 - 0.75 * math.exp(-2 * t)
        Hv, Wv, Iv = KL(m, s2), W(m, s2), I(m, s2)
        R["tal"].append((t, Wv * Wv / 2 / Hv)); R["hwi"].append((t, (Wv * math.sqrt(Iv) - Wv * Wv / 2) / Hv)); R["lsi"].append((t, Iv / 2 / Hv))
    g.line(0, 1, 3, 1, "ln c3")
    g.path(R["lsi"], "ln c1 thin"); g.path(R["hwi"], "ln c2 thin dash"); g.path(R["tal"], "ln c5 thin")
    g.text(0.08, R["lsi"][0][1], "(I/2) / H   (log-Sobolev)", "tx-s t1", "start", dx=4, dy=-8)
    g.text(0.3, 1.18, "(W√I − W²/2) / H   (HWI)", "tx-s t2", "start", dx=4, dy=4)
    g.text(1.2, 1.0, "H / H = 1", "tx-s t3", "start", dy=-6)
    g.text(0.08, R["tal"][0][1], "(W²/2) / H   (Talagrand)", "tx-s t5", "start", dx=4, dy=16)
    c.text(515, 20, "each bound divided by H", "tx-b", "middle")
    c.text(330, 270, "exact Gaussian formulas; at t = 0 the chain W²/2 ≤ H ≤ W√I − W²/2 ≤ I/2 reads 2.125 ≤ 2.318 ≤ 3.029 ≤ 3.125", "tx-s", "middle")
    c.save()


def mmd_flow_run(n, T, dt=0.01, seed=1):
    """Energy-distance MMD^2 particle flow x_i' = (2/n) sum_j u(x_i - x_j) - (2/m) sum_j u(x_i - y_j), u(z) = z/|z|."""
    rng = np.random.default_rng(seed)
    X = rng.standard_normal((n, 2)) * 0.5 + np.array([-3.0, 0.0])
    m = 120
    Y = np.r_[rng.standard_normal((m // 2, 2)) * 0.45 + np.array([2.5, 1.5]), rng.standard_normal((m // 2, 2)) * 0.45 + np.array([2.5, -1.5])]
    traj = [X.copy()]
    for k in range(int(round(T / dt))):
        Dxx = X[:, None] - X[None]; rxx = np.sqrt((Dxx ** 2).sum(-1) + 1e-12)
        Dxy = X[:, None] - Y[None]; rxy = np.sqrt((Dxy ** 2).sum(-1) + 1e-12)
        X = X + dt * ((2 / n) * (Dxx / rxx[..., None]).sum(1) - (2 / m) * (Dxy / rxy[..., None]).sum(1))
        if (k + 1) % 10 == 0:
            traj.append(X.copy())
    return np.array(traj), Y


def fig_mmd():
    c = Canvas("mmd", 660, 270, "Energy-distance MMD particle flows with 8 and with 64 particles", sub=SUB)
    for col, n in enumerate([8, 64]):
        traj, Y = mmd_flow_run(n, 12.0)
        f = Fig(c, (20 + col * 330, 30, 300, 200), (-4.6, 4.4), (-3.0, 3.0))
        f.line(-4.6, -3.0, 4.4, -3.0, "gr")
        for y in Y:
            f.circle(y[0], y[1], 2.2, "f1")
        step = 1 if n == 8 else 2
        for i in range(0, n, step):
            f.path(list(zip(traj[:, i, 0], traj[:, i, 1])), "ln c3 hair")
        for x in traj[0]:
            f.circle(x[0], x[1], 2.8, "f2")
        for x in traj[-1]:
            f.circle(x[0], x[1], 3.2, "f3")
        c.text(20 + col * 330 + 150, 20, f"n = {n} particles, t from 0 to 12", "tx-b", "middle")
    c.text(330, 250, "orange-red: initial particles;  green: paths and final positions;  blue: 120 data points (the target β)", "tx-s", "middle")
    c.text(330, 264, "with few particles the flow can only build a coarse quadrature of β; more particles cover it better", "tx-s", "middle")
    c.save()


def fig_halfplane():
    from scipy.integrate import solve_ivp
    c = Canvas("halfplane", 660, 260, "Gaussian Wasserstein gradient flows in the (m, sigma) half-plane: KL, squared W2, Fisher information", sub=SUB)
    vel = [("KL(α | 𝒩(0,1))", lambda m, s: [-m, 1 / s - s]),
           ("W₂²(α, 𝒩(0,1))", lambda m, s: [-2 * m, -2 * (s - 1)]),
           ("Fisher 𝓘(α | 𝒩(0,1))", lambda m, s: [-2 * m, 2 / s ** 3 - 2 * s])]
    starts = [(-1.6, 0.35), (-1.6, 2.6), (1.7, 2.8), (2.0, 0.5), (0.4, 0.25), (-0.3, 2.9), (1.9, 1.6), (-1.8, 1.4)]
    for col, (title, v) in enumerate(vel):
        f = Fig(c, (40 + col * 210, 34, 180, 170), (-2.0, 2.2), (0, 3.1))
        f.axes(xticks=[-2, -1, 0, 1, 2], yticks=[0, 1, 2, 3], xfmt=lambda u: f"{u:g}", grid=False)
        for (m0, s0) in starts:
            sol = solve_ivp(lambda t, z: v(*z), (0, 12), [m0, s0], rtol=1e-9, atol=1e-11, dense_output=True)
            ts = np.r_[np.linspace(0, 2, 120), np.linspace(2.05, 12, 60)]
            Z = sol.sol(ts)
            f.path(list(zip(Z[0], Z[1])), "ln c3 thin")
            f.circle(m0, s0, 3.2, "f2")
            for tk in [0.5, 1.0]:
                zk = sol.sol(tk)
                f.circle(zk[0], zk[1], 2.2, "f5")
        f.circle(0, 1, 5, "f1")
        c.text(40 + col * 210 + 90, 22, title, "tx-b", "middle")
        f.text(-2.0, 3.1, "σ", "tx-i", "start", dx=4, dy=4)
        f.text(2.2, 0, "m", "tx-i", "start", dx=5, dy=5)
    c.text(330, 240, "orange-red: starting Gaussians 𝒩(m, σ²);  green: trajectories;  purple dots: positions at t = 0.5 and t = 1;  blue: the target 𝒩(0,1)", "tx-s", "middle")
    c.text(330, 254, "only the W₂² flow moves on straight lines: the half-plane is flat for W₂ (W₂² = Δm² + Δσ²), and W₂² is the squared distance", "tx-s", "middle")
    c.save()


def cells_model():
    """Toy Waddington landscape (OT4ML Ex. 15.10): f(a) = int V da + sig2 int rho log rho, V(x) = x^4/4 - x^2/2.
    Implicit finite-volume Fokker-Planck on a grid (flux form, exact Gibbs equilibrium); day 0 = N(0, 0.15^2), days 1, 2 at
    t = 1.5, 3. Fates of day-0 cells: backward Kolmogorov equation (truth), exact OT, entropic OT (Sinkhorn)."""
    from scipy.linalg import solve_banded
    sig2, s0, T, L, N, dt = 0.05, 0.15, 1.5, 2.2, 881, 0.0005
    V = lambda x: x ** 4 / 4 - x ** 2 / 2
    x = np.linspace(-L, L, N); dx = x[1] - x[0]
    U = V(x) / sig2; Uh = V(0.5 * (x[1:] + x[:-1])) / sig2
    a = sig2 * np.exp(U[:-1] - Uh) / dx ** 2; b = sig2 * np.exp(U[1:] - Uh) / dx ** 2
    diag = np.zeros(N); diag[:-1] -= a; diag[1:] -= b
    A = np.vstack([np.r_[0, b], diag, np.r_[a, 0]])
    M = -dt * A; M[1] += 1
    AT = np.vstack([np.r_[0, A[2][:-1]], A[1], np.r_[A[0][1:], 0]]); MT = -dt * AT; MT[1] += 1
    nst = int(round(T / dt))
    r0 = gauss(x, 0, s0); r0 /= r0.sum() * dx
    r1 = r0.copy()
    for _ in range(nst): r1 = solve_banded((1, 1), M, r1)
    r2 = r1.copy()
    for _ in range(nst): r2 = solve_banded((1, 1), M, r2)
    u = (x > 0).astype(float); u[np.abs(x) < 1e-12] = 0.5
    for _ in range(2 * nst): u = solve_banded((1, 1), MT, u)
    sub = slice(None, None, 4); xg = x[sub]
    def dens(r):
        m = r[sub] / r[sub].sum(); keep = m > 1e-10
        return xg[keep], m[keep]
    def sinkhorn(mu, nu, C, eps, it=20000):
        K = np.exp(-(C - C.min()) / eps); aa = np.ones_like(mu); bb = np.ones_like(nu)
        for _ in range(it):
            aa = mu / (K @ bb); bb = nu / (K.T @ aa)
        return aa[:, None] * K * bb[None]
    x0, m0 = dens(r0); x1, m1 = dens(r1); x2, m2 = dens(r2)
    eps = 2 * sig2 * T
    P01 = sinkhorn(m0, m1, 0.5 * (x0[:, None] - x1[None]) ** 2, eps)
    P12 = sinkhorn(m1, m2, 0.5 * (x1[:, None] - x2[None]) ** 2, eps)
    P02 = sinkhorn(m0, m2, 0.5 * (x0[:, None] - x2[None]) ** 2, 2 * eps)
    K02 = (P01 / P01.sum(1, keepdims=True)) @ (P12 / P12.sum(1, keepdims=True))
    fate2 = K02[:, x2 > 0].sum(1)
    fated = P02[:, x2 > 0].sum(1) / P02.sum(1)
    return dict(x=x, V=V, r0=r0, r1=r1, r2=r2, u=u, x0=x0, fate2=fate2, fated=fated)


def fig_cells():
    c = Canvas("cells", 660, 304, "A toy Waddington landscape: three snapshots of a cell population and the fate of a day-0 cell inferred by transport", sub=SUB)
    d = cells_model()
    x = d["x"]
    # left, top: the landscape V
    t = Fig(c, (40, 30, 270, 46), (-1.8, 1.8), (-0.3, 0.75))
    t.fn(d["V"], "ln cm thin", -1.7, 1.7)
    t.circle(0, 0.07, 4, "f2")
    c.arrow(t.X(0.12), t.Y(0.05), t.X(0.75), t.Y(-0.12), 2)
    c.arrow(t.X(-0.12), t.Y(0.05), t.X(-0.75), t.Y(-0.12), 2)
    t.text(0, 0.75, "landscape V(x) = x⁴/4 − x²/2", "tx-s", "middle", dy=2)
    # left, bottom: densities of the three snapshots
    f = Fig(c, (40, 96, 270, 140), (-1.8, 1.8), (0, 2.8))
    f.axes(xticks=[-1.5, -1, -0.5, 0, 0.5, 1, 1.5], yticks=[0, 1, 2], xfmt=lambda v: f"{v:g}", xlabel="cell state x")
    keep = np.abs(x) <= 1.8
    filled(f, x[keep], d["r0"][keep], "f2 a1", "ln c2")
    filled(f, x[keep], d["r1"][keep], "f3 a1", "ln c3")
    filled(f, x[keep], d["r2"][keep], "f1 a1", "ln c1")
    f.text(0.12, 2.55, "day 0", "tx-s t2", "start")
    i1 = int(np.argmax(d["r1"] * (x > 0)))
    f.text(x[i1], d["r1"][i1], "day 1", "tx-s t3", "end", dx=-4, dy=-4)
    i2 = int(np.argmax(d["r2"] * (x > 0)))
    f.text(x[i2], d["r2"][i2], "day 2", "tx-s t1", "start", dx=6, dy=-2)
    c.text(175, 20, "three snapshots (different cells each day)", "tx-b", "middle")
    # right: fate probabilities
    g = Fig(c, (400, 34, 240, 190), (-0.45, 0.45), (0, 1))
    g.axes(xticks=[-0.4, -0.2, 0, 0.2, 0.4], yticks=[0, 0.25, 0.5, 0.75, 1], xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:g}", xlabel="position x of the cell at day 0")
    sel = np.abs(x) <= 0.45
    g.path(list(zip(x[sel], d["u"][sel])), "ln cm")
    g.path([(-0.45, 0), (0, 0), (0, 1), (0.45, 1)], "ln c2 thin dash")
    x0 = d["x0"]; s0 = np.abs(x0) <= 0.45
    g.path(list(zip(x0[s0], d["fated"][s0])), "ln c5 thin")
    g.path(list(zip(x0[s0], d["fate2"][s0])), "ln c3 thin dot")
    g.text(0.03, 0.97, "exact OT", "tx-s t2", "start", dy=10)
    g.text(-0.43, 0.93, "truth", "tx-s", "start")
    g.text(-0.43, 0.85, "entropic, day 0 → 2", "tx-s t5", "start")
    g.text(-0.43, 0.77, "entropic, via day 1", "tx-s t3", "start")
    c.text(520, 20, "probability to end in the right valley at day 2", "tx-b", "middle")
    c.text(330, 284, "toy model: Fokker-Planck flow of ∫V dα + σ²∫ρ log ρ (σ² = 0.05), observed at t = 0, 1.5, 3", "tx-s", "middle")
    c.text(330, 298, "fates: truth from the backward Kolmogorov equation; entropic OT with ε = 2σ²Δt, direct or through day 1", "tx-s", "middle")
    c.save()


if __name__ == "__main__":
    for fn in [fig_euler, fig_jko_heat, fig_vert_horiz, fig_four_flows, fig_three_reps, fig_nonconvex, fig_lsi, fig_mmd, fig_halfplane, fig_cells]:
        fn()
