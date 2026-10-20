"""figures_L03.py — static SVG figures of Lesson 3 (Wasserstein distances), written to figures/L03/.

Run: python3 figures_L03.py        (then node build.mjs Lesson03.html)
"""
import math

import numpy as np

from figures_common import Canvas, Fig, fmt1

SUB = "L03"


# ---------------------------------------------------------------------------------------------
def fig_wpq():
    c = Canvas("wpq", 560, 300, "W_p of a small moved mass: epsilon to the power 1/p for p = 1, 2, 4", sub=SUB)
    f = Fig(c, (52, 18, 470, 236), (0, 1), (0, 1))
    f.axes(xticks=[0, 0.25, 0.5, 0.75, 1], yticks=[0, 0.25, 0.5, 0.75, 1], xlabel="ε (mass moved by a distance 1)", ylabel="Wₚ")
    for p, k in [(1, 2), (2, 1), (4, 5)]:
        f.fn(lambda e: e ** (1 / p), f"ln c{k}", 0, 1, 400)
    e0 = 0.04
    f.line(e0, 0, e0, e0 ** 0.25, "ln cm thin dash")
    for p, k in [(1, 2), (2, 1), (4, 5)]:
        f.circle(e0, e0 ** (1 / p), 4, f"f{k}")
    f.text(0.66, 0.30, "W₄ = ∜ε", "tx-b t5")
    f.text(0.66, 0.21, "W₂ = √ε", "tx-b t1")
    f.text(0.66, 0.12, "W₁ = ε", "tx-b t2")
    f.text(e0, 0, "ε = 0.04", "tx-s", "start", dx=4, dy=-6)
    c.save()


def fig_testfn():
    c = Canvas("testfn", 660, 190, "Three classes of test functions: compact support, vanishing at infinity, bounded", sub=SUB)
    # subscripts c, 0, b as SVG tspans (no Unicode subscript exists for c and b)
    def sub(letter):
        return f'C<tspan baseline-shift="sub" font-size="75%">{letter}</tspan>'
    panels = [
        ("c", " : zero outside a bounded set", lambda x: max(0.0, 1 - abs(x) / 2), "ln c3"),
        ("0", " : tends to 0 at infinity", lambda x: 1 / (1 + x * x), "ln c1"),
        ("b", " : only bounded", lambda x: math.atan(x) / (math.pi / 2) * 0.9, "ln c2"),
    ]
    for i, (letter, title, fn, cls) in enumerate(panels):
        f = Fig(c, (14 + i * 218, 30, 196, 120), (-7, 7), (-1.1, 1.1))
        f.line(-7, 0, 7, 0, "ax")
        f.line(-7, 1, 7, 1, "gr")
        f.line(-7, -1, 7, -1, "gr")
        f.fn(fn, cls, -7, 7, 400)
        c.add(f'<text x="{14 + i * 218 + 98:.1f}" y="20.0" class="tx-b" text-anchor="middle">{sub(letter)}{title}</text>')
    c.add(f'<text x="330.0" y="182.0" class="tx-s" text-anchor="middle">fewer test functions  ⇐   {sub("c")} ⊂ {sub("0")} ⊂ {sub("b")}   ⇒   more demanding convergence</text>')
    c.save()


def fig_escape():
    c = Canvas("escape", 600, 230, "Escaping mass: (1-1/n) delta_0 + (1/n) delta_n for n = 4 and n = 10", sub=SUB)
    for row, n in enumerate([4, 10]):
        f = Fig(c, (40, 22 + row * 104, 530, 66), (-0.5, 11), (0, 1))
        f.line(-0.5, 0, 11, 0, "ax")
        for v in range(0, 11, 2):
            f.text(v, 0, str(v), "tx-s", "middle", dy=14)
        f.lollipop(0, 1 - 1 / n, 2)
        f.lollipop(n, 1 / n, 2)
        f.text(0, 1 - 1 / n, f"mass {1 - 1 / n:g}", "tx-s", "start", dx=8, dy=4)
        f.text(n, 1 / n, f"mass 1/{n}", "tx-s", "middle", dy=-10)
        c.arrow(f.X(0.25), f.Y(0.06), f.X(n - 0.25), f.Y(0.06), 3, "ln c3 thin dash")
        f.text((n) / 2, 0.06, f"W₁ pays (1/{n}) × {n} = 1", "tx-s t3", "middle", dy=-6)
        c.text(8, f.Y(0.5), f"n={n}", "tx-b")
    c.save()


def fig_riemann():
    c = Canvas("riemann", 560, 300, "Quantile functions of the Riemann measure (n = 5) and of the uniform law", sub=SUB)
    f = Fig(c, (52, 16, 300, 250), (0, 1), (0, 1))
    n = 5
    f.axes(xticks=[0, 0.2, 0.4, 0.6, 0.8, 1], yticks=[0, 0.2, 0.4, 0.6, 0.8, 1], xlabel="t", ylabel="quantile")
    for k in range(1, n + 1):
        a, b = (k - 1) / n, k / n
        f.path([(a, a), (b, b), (a, b)], "a3", close=True)
        f.line(a, b, b, b, "ln c2")
    f.line(0, 0, 1, 1, "ln c1 thin")
    f.text(0.55, 0.36, "uniform: t", "tx-s t1")
    f.text(0.05, 0.47, "Riemann: k/n on", "tx-s t2")
    f.text(0.05, 0.42, "((k−1)/n, k/n]", "tx-s t2")
    # right: the atoms and what they collect
    g = Fig(c, (390, 120, 150, 60), (0, 1), (0, 1))
    g.line(0, 0, 1, 0, "ax")
    for k in range(1, n + 1):
        g.path([((k - 1) / n, 0), (k / n, 0), (k / n, 0.55), ((k - 1) / n, 0.55)], "a1", close=True)
        g.lollipop(k / n, 1, 2, r=3.5)
    g.text(0, 0, "0", "tx-s", "middle", dy=14)
    g.text(1, 0, "1", "tx-s", "middle", dy=14)
    c.text(465, 100, "atom k/n collects the", "tx-s", "middle")
    c.text(465, 112, "uniform mass to its left", "tx-s", "middle")
    c.text(465, 212, "green area = W₁ = 1/(2n)", "tx-s t3", "middle")
    c.save()


def fig_tv():
    c = Canvas("tv", 640, 200, "Total variation versus transport: two close Diracs, two shifted uniform laws", sub=SUB)
    f = Fig(c, (20, 40, 270, 110), (-0.2, 1.2), (0, 1.15))
    f.line(-0.2, 0, 1.2, 0, "ax")
    f.lollipop(0.45, 1, 1)
    f.lollipop(0.55, 1, 2)
    f.text(0.45, 0, "x", "tx-i", "middle", dy=18)
    f.text(0.58, 0, "xₙ", "tx-i", "middle", dy=18)
    c.text(155, 22, "Diracs at xₙ and at x", "tx-b", "middle")
    c.text(155, 186, "TV = 2 however close;  Wₚ = d(xₙ, x)", "tx-s", "middle")
    g = Fig(c, (350, 40, 270, 110), (-0.2, 1.6), (0, 1.25))
    a = 0.35
    g.line(-0.2, 0, 1.6, 0, "ax")
    g.path([(0, 0), (0, 1), (a, 1), (a, 0)], "a1", close=True)
    g.path([(1, 0), (1, 1), (1 + a, 1), (1 + a, 0)], "a2", close=True)
    g.path([(0, 0), (0, 1), (1, 1), (1, 0)], "ln c1 thin nofill")
    g.path([(a, 0), (a, 1), (1 + a, 1), (1 + a, 0)], "ln c2 thin nofill dash")
    g.text(0, 0, "0", "tx-s", "middle", dy=14)
    g.text(1, 0, "1", "tx-s", "middle", dy=14)
    g.text(a, 0, "a", "tx-s", "middle", dy=14)
    c.text(485, 22, "𝒰[0,1] versus 𝒰[a,1+a]", "tx-b", "middle")
    c.text(485, 186, "TV = shaded area = 2a;   W₁ = a", "tx-s", "middle")
    c.save()


def gauss(x, m, s):
    return np.exp(-0.5 * ((x - m) / s) ** 2) / (s * math.sqrt(2 * math.pi))


def fig_displacement():
    c = Canvas("displacement", 660, 270, "Mixture versus displacement interpolation between two Gaussians", sub=SUB)
    m0, s0, m1, s1 = -2.0, 0.5, 2.0, 1.0
    ts = [0, 0.25, 0.5, 0.75, 1]
    for col, t in enumerate(ts):
        for row in range(2):
            f = Fig(c, (96 + col * 113, 34 + row * 116, 102, 74), (-4.5, 5), (0, 0.85))
            f.line(-4.5, 0, 5, 0, "ax")
            if row == 0:
                fn = lambda x: (1 - t) * gauss(x, m0, s0) + t * gauss(x, m1, s1)
                f.path([(-4.5, 0)] + [(x, fn(x)) for x in np.linspace(-4.5, 5, 300)] + [(5, 0)], "am", close=True)
                f.fn(fn, "ln cm", n=300)
            else:
                m, s = (1 - t) * m0 + t * m1, (1 - t) * s0 + t * s1
                fn = lambda x: gauss(x, m, s)
                f.path([(-4.5, 0)] + [(x, fn(x)) for x in np.linspace(-4.5, 5, 300)] + [(5, 0)], "a3", close=True)
                f.fn(fn, "ln c3", n=300)
            if row == 0:
                c.text(96 + col * 113 + 51, 24, f"t = {t:g}", "tx-b", "middle")
    c.text(8, 34 + 44, "mixture", "tx-b")
    c.text(8, 34 + 116 + 44, "displacement", "tx-b")
    c.text(370, 262, "top: (1−t)α + tβ fades one bump into the other;  bottom: αₜ moves and reshapes the mass", "tx-s", "middle")
    c.save()


def fig_split():
    c = Canvas("split", 420, 200, "Space-time picture of the displacement interpolation from delta_0 to (delta_-1 + delta_1)/2", sub=SUB)
    f = Fig(c, (60, 20, 300, 140), (-1.3, 1.3), (0, 1))
    f.line(-1.3, 0, 1.3, 0, "ax")
    f.line(-1.3, 1, 1.3, 1, "gr")
    f.line(0, 0, -1, 1, "ln c3")
    f.line(0, 0, 1, 1, "ln c3")
    f.circle(0, 0, 6, "f2")
    f.circle(-1, 1, 5, "f1")
    f.circle(1, 1, 5, "f1")
    t = 0.55
    f.line(-1.3, t, 1.3, t, "ln cm thin dash")
    f.circle(-t, t, 4, "f3")
    f.circle(t, t, 4, "f3")
    f.text(-1.3, 0, "t = 0", "tx-s", "end", dx=-6, dy=4)
    f.text(-1.3, 1, "t = 1", "tx-s", "end", dx=-6, dy=4)
    f.text(-1.3, t, f"t", "tx-s", "end", dx=-6, dy=4)
    f.text(0, 0, "α = δ₀", "tx-s t2", "middle", dy=18)
    f.text(1, 1, "β", "tx-s t1", "start", dx=8, dy=4)
    f.text(0, t, "αₜ = ½δ₋ₜ + ½δₜ", "tx-s t3", "middle", dy=-8)
    c.text(210, 192, "the atom splits and both halves move at constant speed", "tx-s", "middle")
    c.save()


def fig_frechet():
    c = Canvas("frechet", 440, 230, "Points on a circle: their Euclidean average falls inside, their Frechet mean stays on the circle", sub=SUB)
    f = Fig(c, (40, 10, 360, 200), (-1.25, 1.25), (-0.2, 1.2))
    angs = np.deg2rad([25, 55, 100, 150])
    th = np.linspace(np.deg2rad(5), np.deg2rad(175), 200)
    f.path([(math.cos(a), math.sin(a)) for a in th], "ln cm thin")
    pts = np.c_[np.cos(angs), np.sin(angs)]
    for p in pts:
        f.circle(p[0], p[1], 5, "f1")
    e = pts.mean(0)
    am = angs.mean()
    fm = (math.cos(am), math.sin(am))
    f.line(e[0] - 0.05, e[1] - 0.05, e[0] + 0.05, e[1] + 0.05, "ln c2")
    f.line(e[0] - 0.05, e[1] + 0.05, e[0] + 0.05, e[1] - 0.05, "ln c2")
    f.text(e[0], e[1], "Euclidean average (off the curve)", "tx-s t2", "middle", dy=22)
    f.circle(fm[0], fm[1], 6, "f3")
    f.text(fm[0], fm[1], "Fréchet mean", "tx-s t3", "middle", dy=-12)
    f.text(-1.2, -0.1, "arc-length distance on the curve", "tx-s")
    c.save()


def fig_grid():
    c = Canvas("grid", 600, 170, "Fixed-grid barycenter of delta_0 and delta_3 on the grid {0,...,4}", sub=SUB)
    f = Fig(c, (40, 30, 520, 90), (-0.4, 4.4), (0, 1))
    f.line(-0.4, 0, 4.4, 0, "ax")
    Fv = [4.5, 2.5, 2.5, 4.5, 8.5]
    for g in range(5):
        f.circle(g, 0, 3, "fm")
        f.text(g, 0, str(g), "tx-s", "middle", dy=16)
        f.text(g, 1, f"F = {Fv[g]:g}", "tx-s", "middle", dy=-4)
    f.lollipop(0, 0.7, 1)
    f.lollipop(3, 0.7, 5)
    f.text(0, 0.7, "β₁ = δ₀", "tx-s t1", "start", dx=8)
    f.text(3, 0.7, "β₂ = δ₃", "tx-s t5", "start", dx=8)
    f.line(1.5, 0, 1.5, 0.55, "ln c3 dash")
    f.circle(1.5, 0.55, 5, "fs")
    c.add(f'<circle cx="{f.X(1.5):.1f}" cy="{f.Y(0.55):.1f}" r="5" class="ln c3 thin nofill"/>')
    f.text(1.5, 0.55, "Dirac at 1.5: off the grid (F = 2.25)", "tx-s t3", "middle", dy=-10)
    f.lollipop(1, 0.35, 3)
    f.lollipop(2, 0.35, 3)
    c.text(300, 160, "F(x) = ½x² + ½(x−3)²: every α carried by {1, 2} is a grid barycenter (value 2.5)", "tx-s", "middle")
    c.save()


def fig_nonunique():
    c = Canvas("nonunique", 560, 250, "Two different Wasserstein barycenters of the same pair of measures", sub=SUB)
    for col, (name, pairs) in enumerate([("barycenter A", [((-1, 0), (0, -1)), ((1, 0), (0, 1))]),
                                         ("barycenter B", [((-1, 0), (0, 1)), ((1, 0), (0, -1))])]):
        f = Fig(c, (30 + col * 280, 30, 220, 190), (-1.35, 1.35), (-1.25, 1.25))
        f.line(-1.35, 0, 1.35, 0, "gr")
        f.line(0, -1.25, 0, 1.25, "gr")
        for p, q in pairs:
            f.line(p[0], p[1], q[0], q[1], "ln cm thin dash")
            m = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
            f.circle(m[0], m[1], 6, "f3")
        for x in [(-1, 0), (1, 0)]:
            f.circle(x[0], x[1], 6, "f1")
        for y in [(0, -1), (0, 1)]:
            f.circle(y[0], y[1], 6, "f5")
        c.text(30 + col * 280 + 110, 20, name, "tx-b", "middle")
    c.text(280, 244, "blue: β₁ = ½(δ₍₋₁,₀₎ + δ₍₁,₀₎);  purple: β₂ = ½(δ₍₀,₋₁₎ + δ₍₀,₁₎);  green: two barycenters (λ = ½, ½)", "tx-s", "middle")
    c.save()


def fig_quantile():
    c = Canvas("quantile", 660, 250, "One-dimensional barycenter: average the quantiles (horizontally), not the CDFs (vertically)", sub=SUB)
    # left: densities
    f = Fig(c, (36, 30, 270, 170), (-0.3, 4.3), (0, 1.15))
    f.line(-0.3, 0, 4.3, 0, "ax")
    f.path([(0, 0), (0, 1), (1, 1), (1, 0)], "a1", close=True)
    f.path([(0, 0), (0, 1), (1, 1), (1, 0)], "ln c1 thin nofill")
    f.path([(2, 0), (2, 0.5), (4, 0.5), (4, 0)], "a5", close=True)
    f.path([(2, 0), (2, 0.5), (4, 0.5), (4, 0)], "ln c5 thin nofill")
    f.path([(1, 0), (1, 2 / 3), (2.5, 2 / 3), (2.5, 0)], "ln c3")
    f.path([(0, 0), (0, 0.5), (1, 0.5), (1, 0), (2, 0), (2, 0.25), (4, 0.25), (4, 0)], "ln cm thin dash")
    for v in range(5):
        f.text(v, 0, str(v), "tx-s", "middle", dy=14)
    c.text(171, 20, "densities", "tx-b", "middle")
    f.text(0.5, 1, "β₁ = 𝒰[0,1]", "tx-s t1", "middle", dy=-6)
    f.text(3, 0.5, "β₂ = 𝒰[2,4]", "tx-s t5", "middle", dy=-6)
    f.text(2.6, 0.8, "barycenter 𝒰[1, 2.5]", "tx-s t3", "start")
    f.text(3, 0.25, "mixture", "tx-s", "middle", dy=-5)
    # right: CDFs with horizontal averaging
    g = Fig(c, (370, 30, 270, 170), (-0.3, 4.3), (0, 1.05))
    g.axes(xticks=[0, 1, 2, 3, 4], yticks=[0, 0.25, 0.5, 0.75, 1], yfmt=fmt1, grid=False)
    cdf = lambda a, b: (lambda x: min(1, max(0, (x - a) / (b - a))))
    g.fn(cdf(0, 1), "ln c1", -0.3, 4.3, 400)
    g.fn(cdf(2, 4), "ln c5", -0.3, 4.3, 400)
    g.fn(cdf(1, 2.5), "ln c3", -0.3, 4.3, 400)
    g.fn(lambda x: 0.5 * cdf(0, 1)(x) + 0.5 * cdf(2, 4)(x), "ln cm thin dash", -0.3, 4.3, 400)
    for t in [0.25, 0.75]:
        q1, q2 = t, 2 + 2 * t
        g.line(q1, t, q2, t, "ln c3 thin dot")
        g.circle((q1 + q2) / 2, t, 4, "f3")
    c.text(505, 20, "CDFs", "tx-b", "middle")
    g.text(2.6, 0.12, "dashed: mixture", "tx-s", "start")
    c.text(330, 244, "at each level t the barycenter puts its quantile at the average of the input quantiles", "tx-s", "middle")
    c.save()


def fig_fixedpoint():
    c = Canvas("fixedpoint", 600, 320, "One step of the fixed-point algorithm: average the optimal maps, then push the current measure", sub=SUB)
    blobs = [((110, 75), 72, 34, -15, "β₁"), ((345, 40), 62, 26, 8, "β₂"), ((530, 120), 50, 40, 25, "β₃")]
    for (cx, cy), rx, ry, rot, lab in blobs:
        c.add(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" transform="rotate({rot} {cx} {cy})" class="a1 ln c1 thin"/>')
        c.text(cx - rx - 6, cy - ry + 6, lab, "tx-b t1", "end")
    c.add('<ellipse cx="300" cy="252" rx="95" ry="36" class="a2 ln c2 thin"/>')
    c.text(402, 276, "α⁽ˡ⁾ (current guess)", "tx-b t2", "start")
    x = (300, 250)
    targets = [(130, 82), (352, 40), (515, 125)]
    for i, tpt in enumerate(targets):
        c.arrow(x[0], x[1], tpt[0] + (x[0] - tpt[0]) * 0.035, tpt[1] + (x[1] - tpt[1]) * 0.035, 1, "ln c1 thin dash")
        c.add(f'<circle cx="{tpt[0]}" cy="{tpt[1]}" r="4" class="f1"/>')
    c.text(130, 100, "T₁(x)", "tx-s t1", "middle")
    c.text(362, 44, "T₂(x)", "tx-s t1", "start")
    c.text(515, 143, "T₃(x)", "tx-s t1", "middle")
    avg = (sum(t[0] for t in targets) / 3, sum(t[1] for t in targets) / 3)
    c.add(f'<ellipse cx="{avg[0]:.1f}" cy="{avg[1] + 10:.1f}" rx="70" ry="24" class="a3 ln c3 thin dash"/>')
    c.arrow(x[0], x[1], avg[0] - 0.8, avg[1] + 6, 3, "ln c3")
    c.add(f'<circle cx="{avg[0]:.1f}" cy="{avg[1]:.1f}" r="5" class="f3"/>')
    c.text(avg[0] + 9, avg[1] + 4, "T(x)", "tx-b t3", "start")
    c.text(avg[0] + 74, avg[1] + 22, "α⁽ˡ⁺¹⁾", "tx-b t3", "start")
    c.add(f'<circle cx="{x[0]}" cy="{x[1]}" r="5" class="f2"/>')
    c.text(x[0] - 10, x[1] + 4, "x", "tx-i", "end")
    c.text(300, 312, "dashed blue: the optimal maps Tₖ(x);  green arrow: x ↦ T(x) = Σ λₖ Tₖ(x);  green ellipse: α⁽ˡ⁺¹⁾ = T#α⁽ˡ⁾", "tx-s", "middle")
    c.save()


def fig_kcsplit():
    """Sheet, Exercises 1 and 3: U[0,1] and (delta_0 + delta_1)/2. Upwards a map, downwards a split."""
    c = Canvas("kcsplit", 640, 236, "The monotone plan between the uniform law on [0,1] and two Diracs, as arrows and as a set in the product", sub=SUB)
    f = Fig(c, (50, 34, 250, 140), (-0.12, 1.12), (0, 1))
    f.path([(0, 0), (1, 0), (1, 0.07), (0, 0.07)], "a2 ln c2 thin", close=True)
    for k in range(20):
        s = (k + 0.5) / 20
        f.line(s, 0.07, 0.0 if s < 0.5 else 1.0, 0.94, "ln c3 hair")
    for x in (0.0, 1.0):
        f.circle(x, 0.97, 5.5, "f1")
    f.text(0, 0.97, "½δ₀", "tx-s t1", "end", dx=-9, dy=4)
    f.text(1, 0.97, "½δ₁", "tx-s t1", "start", dx=9, dy=4)
    f.text(0.5, 0, "α = U[0, 1]", "tx-s t2", "middle", dy=18)
    f.text(0, 0, "0", "tx-s", "middle", dy=32)
    f.text(0.5, 0, "½", "tx-s", "middle", dy=32)
    f.text(1, 0, "1", "tx-s", "middle", dy=32)
    f.line(0.5, -0.02, 0.5, 0.09, "ln ck thin")
    c.text(175, 18, "up: each s has one destination (a map T)", "tx-s", "middle")
    c.text(175, 228, "down: each atom spreads over an interval (a split)", "tx-s", "middle")
    g = Fig(c, (390, 34, 210, 140), (-0.1, 1.1), (-0.25, 1.25))
    g.axes(xticks=(0, 0.5, 1), yticks=(0, 1), xfmt=lambda v: {0: "0", 0.5: "½", 1: "1"}[v], yfmt=lambda v: str(v), grid=False)
    g.line(0, 0, 0.5, 0, "ln c3")
    g.line(0.5, 1, 1, 1, "ln c3")
    g.line(0.75, -0.25, 0.75, 1.25, "ln cm thin dash")  # a vertical line, away from the label of the lower segment
    g.circle(0.75, 1, 4.5, "f3")
    g.text(0.75, 1.25, "one point", "tx-s", "middle", dy=-6)
    g.text(0.5, 1, "graph of T", "tx-s t3", "end", dx=-6, dy=4)
    g.text(0.25, 0, "a whole segment", "tx-s", "middle", dy=-9)
    g.text(1.1, -0.25, "s (point of α)", "tx-s", "end", dy=30)
    g.text(-0.1, 1.25, "T(s)", "tx-s", "start", dx=4, dy=-6)
    c.text(495, 228, "the support of π in the product [0, 1] × ℝ", "tx-s", "middle")
    c.save()


def fig_nonmonge():
    """Sheet, Exercise 6: the optimal plan splits every point; maps only approach its cost."""
    c = Canvas("nonmonge", 660, 262, "A segment sent onto two parallel segments: the optimal plan splits every point, maps only approach its cost", sub=SUB)
    def segments(f, label):
        f.line(-1, 0, -1, 1, "ln c1")
        f.line(1, 0, 1, 1, "ln c1")
        f.line(0, 0, 0, 1, "ln c2")
        f.text(-1, 1, "S₋", "tx-s t1", "middle", dy=-8)
        f.text(0, 1, "S₀", "tx-s t2", "middle", dy=-8)
        f.text(1, 1, "S₊", "tx-s t1", "middle", dy=-8)
        for v in (0, 1):
            f.text(-1, v, str(v), "tx-s", "end", dx=-7, dy=4)
    f = Fig(c, (54, 30, 250, 180), (-1.25, 1.25), (0, 1))
    segments(f, "")
    for s in (0.08, 0.26, 0.44, 0.62, 0.8, 0.96):
        c.arrow(f.X(0) - 4, f.Y(s), f.X(-1) + 4, f.Y(s), 3)
        c.arrow(f.X(0) + 4, f.Y(s), f.X(1) - 4, f.Y(s), 3)
    c.text(179, 232, "optimal plan π⋆: each (0, s) sends ½ left, ½ right", "tx-s", "middle")
    c.text(179, 250, "horizontal moves only: cost exactly 1", "tx-s t3", "middle")
    n = 3
    g = Fig(c, (384, 30, 250, 180), (-1.25, 1.25), (0, 1))
    for k in range(n):
        a0, am, a1 = k / n, k / n + 1 / (2 * n), (k + 1) / n
        g.path([(0, a0), (0, am), (-1, a1), (-1, a0)], "a3 ln c3 hair", close=True)
        g.path([(0, am), (0, a1), (1, a1), (1, a0)], "a3 ln c3 hair", close=True)
        g.line(-0.05, am, 0.05, am, "ln ck hair")
    segments(g, "")
    c.text(509, 232, f"a map with n = {n} strips: half of each strip goes left,", "tx-s", "middle")
    c.text(509, 250, f"half right, stretched ×2: cost 1 + 1/(12n²) ≈ {1 + 1 / (12 * n * n):.4f}", "tx-s t3", "middle")
    c.save()


if __name__ == "__main__":
    for fn in [fig_wpq, fig_testfn, fig_escape, fig_riemann, fig_tv, fig_displacement, fig_split,
               fig_frechet, fig_grid, fig_nonunique, fig_quantile, fig_fixedpoint, fig_kcsplit, fig_nonmonge]:
        fn()
