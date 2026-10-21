"""figures_L01.py — static SVG figures of Lesson 1 (Monge's problem), written to figures/L01/.

Run: python3 figures_L01.py        (then node build.mjs Lesson01.html)
Every coordinate is computed here; colours are CSS classes (see figures_common.py).
"""
import math

import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.special import erf

from figures_common import Canvas, Fig, esc

SUB = "L01"


def ncdf(x):
    return 0.5 * (1 + erf(np.asarray(x) / math.sqrt(2)))


def gauss(x, m, s):
    return np.exp(-0.5 * ((x - m) / s) ** 2) / (s * math.sqrt(2 * math.pi))


# ---------------------------------------------------------------------------------------------
def fig_timeline():
    # (year, label, side, colour)  side: +1 above (mathematics), -1 below (algorithms and applications)
    ev = [
        (1781, "Monge", 1, "3"), (1931, "Schrödinger", 1, "4"), (1942, "Kantorovich", 1, "1"),
        (1946, "Birkhoff", 1, "1"), (1953, "von Neumann", 1, "1"), (1987, "Brenier", 1, "3"),
        (1997, "McCann", 1, "3"), (1998, "Jordan–Kinderlehrer–Otto", 1, "4"), (2003, "Villani", 1, "m"),
        (2010, "Figalli", 1, "m"),
        (1947, "Dantzig (simplex)", -1, "1"), (1955, "Kuhn (Hungarian)", -1, "3"), (1964, "Sinkhorn", -1, "4"),
        (2013, "Cuturi (fast Sinkhorn)", -1, "4"), (2017, "Wasserstein GAN", -1, "5"),
    ]

    def X(year):
        if year < 1800:
            return 44 + (year - 1781) * 1.2
        return 122 + (year - 1925) * (600 - 122) / (2020 - 1925)

    # Staircase layout: each label is a flag to the left of its leader (to the right for Monge),
    # placed one row above every leader its text covers, so that no leader crosses a label.
    placed = []  # (side, row, a0, a1, x, ...)
    for yr, lab, side, col in sorted(ev, key=lambda e: e[0]):
        x = X(yr)
        text = f"{lab} {yr}"
        w = 6.0 * len(text)
        if yr < 1800:
            a0, a1, anchor, tx = x + 6, x + 6 + w, "start", x + 6
        else:
            a0, a1, anchor, tx = x - 6 - w, x - 6, "end", x - 6
        r = 1 + max([p[1] for p in placed if p[0] == side and a0 - 4 <= p[4] <= a1 + 4], default=-1)
        while any(p[0] == side and p[1] == r and not (a1 + 8 < p[2] or a0 - 8 > p[3]) for p in placed):
            r += 1
        placed.append((side, r, a0, a1, x, tx, anchor, text, col))
    top = max(p[1] for p in placed if p[0] == 1)
    bot = max(p[1] for p in placed if p[0] == -1)
    dy0, step = 26, 21
    y0 = 34 + dy0 + step * top + 8          # axis: title, then the highest row
    ybot = y0 + dy0 + step * bot + 6         # lowest label
    H = int(ybot + 58)
    c = Canvas("timeline", 660, H, "A timeline of optimal transport from Monge (1781) to Wasserstein GANs (2017)", sub=SUB)
    c.add(f'<line x1="30" y1="{y0}" x2="92" y2="{y0}" class="ax"/>')
    c.add(f'<line x1="108" y1="{y0}" x2="630" y2="{y0}" class="ax"/>')
    for xb in (96, 104):
        c.add(f'<line x1="{xb - 3}" y1="{y0 + 6}" x2="{xb + 3}" y2="{y0 - 6}" class="ax"/>')
    for side, r, a0, a1, x, tx, anchor, text, col in placed:
        ylab = y0 - side * (dy0 + step * r)
        cls = "ln cm hair" if col == "m" else f"ln c{col} hair"
        c.add(f'<line x1="{x:.1f}" y1="{y0}" x2="{x:.1f}" y2="{ylab:.1f}" class="{cls}"/>')
        c.add(f'<circle cx="{x:.1f}" cy="{y0}" r="4" class="f{col}"/>')
        c.add(f'<circle cx="{x:.1f}" cy="{ylab:.1f}" r="2.4" class="f{col}"/>')
        c.text(tx, ylab + 4, text, "tx-s", anchor)
    c.text(30, 20, "mathematics of transport", "tx-b")
    c.text(30, ybot + 24, "algorithms and machine learning", "tx-b")
    leg = [("3", "this lesson"), ("1", "Lesson 2"), ("5", "Lessons 3–5"), ("4", "Lessons 6–8"), ("m", "background")]
    xl = 36
    for col, lab in leg:
        c.add(f'<circle cx="{xl}" cy="{ybot + 44}" r="4" class="f{col}"/>')
        c.text(xl + 8, ybot + 48, lab, "tx-s")
        xl += 26 + 6.0 * len(lab)
    c.save()
    return placed


# ---------------------------------------------------------------------------------------------
def fig_crossing():
    c = Canvas("crossing", 640, 270, "Uncrossing argument for the distance cost, and a crossing optimal pairing for the squared cost", sub=SUB)
    # left: schematic uncrossing
    f = Fig(c, (40, 40, 240, 160), (-0.3, 3.3), (-0.3, 2.3))
    x1, y1, x2, y2 = (0, 0), (3, 2), (0, 2), (3, 0)
    z = (1.5, 1.0)
    f.line(*x1, *y1, "ln c3")
    f.line(*x2, *y2, "ln c3")
    f.line(*x1, *y2, "ln cm dash")
    f.line(*x2, *y1, "ln cm dash")
    for p in (x1, x2):
        f.circle(*p, 5, "f2")
    for p in (y1, y2):
        f.circle(*p, 5, "f1")
    f.circle(*z, 3.5, "fk")
    f.text(*z, "z", "tx-i", "middle", dy=-9)
    f.text(*x1, "x₁", "tx-i", "end", dx=-8, dy=5)
    f.text(*x2, "x₂", "tx-i", "end", dx=-8, dy=5)
    f.text(*y1, "y₁", "tx-i", "start", dx=8, dy=5)
    f.text(*y2, "y₂", "tx-i", "start", dx=8, dy=5)
    c.text(160, 22, "distance cost: never optimal to cross", "tx-b", "middle")
    c.text(160, 222, "solid: crossing pairs x₁→y₁, x₂→y₂", "tx-s", "middle")
    c.text(160, 238, "dashed: swap, shorter than the broken", "tx-s", "middle")
    c.text(160, 252, "lines x₁→z→y₂ and x₂→z→y₁", "tx-s", "middle")
    # right: squared-cost counterexample
    g = Fig(c, (370, 40, 240, 140), (-0.4, 4.6), (-0.4, 2.4))
    X1, Y1, X2, Y2 = (0, 0), (3, 1), (1, 0), (4, 2)
    g.axes(xticks=[], yticks=[0, 1, 2], grid=True, yaxis=False)
    g.line(*X1, *Y1, "ln c3")
    g.line(*X2, *Y2, "ln c3")
    g.line(*X1, *Y2, "ln cm dash")
    g.line(*X2, *Y1, "ln cm dash")
    for p in (X1, X2):
        g.circle(*p, 5, "f2")
    for p in (Y1, Y2):
        g.circle(*p, 5, "f1")
    g.circle(2, 2 / 3, 3, "fk")
    g.text(*X1, "x₁", "tx-i", "middle", dx=0, dy=20)
    g.text(*X2, "x₂", "tx-i", "middle", dx=0, dy=20)
    g.text(*Y1, "y₁", "tx-i", "start", dx=7, dy=12)
    g.text(*Y2, "y₂", "tx-i", "start", dx=7, dy=4)
    c.text(490, 22, "squared cost: crossing can be optimal", "tx-b", "middle")
    d2 = lambda a, b: (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2
    cr2, sw2 = d2(X1, Y1) + d2(X2, Y2), d2(X1, Y2) + d2(X2, Y1)
    cr1, sw1 = math.sqrt(d2(X1, Y1)) + math.sqrt(d2(X2, Y2)), math.sqrt(d2(X1, Y2)) + math.sqrt(d2(X2, Y1))
    c.text(490, 222, f"‖x−y‖²: crossing {cr2:g} < swap {sw2:g}", "tx-s", "middle")
    c.text(490, 238, f"‖x−y‖: crossing {cr1:.3f} > swap {sw1:.3f}", "tx-s", "middle")
    c.text(490, 254, "solid: optimal for ‖x−y‖²;  dashed: for ‖x−y‖", "tx-s", "middle")
    c.save()


# ---------------------------------------------------------------------------------------------
def fig_regimes():
    c = Canvas("regimes", 630, 220, "Sorted versus nested pairing of two sources and two targets for three exponents", sub=SUB)
    for k, p in enumerate([2, 1, 0.5]):
        x0 = 20 + k * 205
        f = Fig(c, (x0 + 15, 52, 160, 86), (-0.2, 2.2), (0, 1))
        f.line(-0.2, 1, 2.2, 1, "gr")
        f.line(-0.2, 0, 2.2, 0, "gr")
        # sorted 0->1, 1->2 ; nested 0->2, 1->1
        f.line(0, 1, 1, 0, "ln c3")
        f.line(1, 1, 2, 0, "ln c3")
        f.line(0, 1, 2, 0, "ln cm dash")
        f.line(1, 1, 1, 0, "ln cm dash")
        for v in (0, 1):
            f.circle(v, 1, 5, "f2")
            f.text(v, 1, str(v), "tx-s", "middle", dy=-9)
        for v in (1, 2):
            f.circle(v, 0, 5, "f1")
            f.text(v, 0, str(v), "tx-s", "middle", dy=17)
        nested = 2 ** p
        ptxt = {2: "p = 2", 1: "p = 1", 0.5: "p = ½"}[p]
        c.text(x0 + 95, 18, ptxt, "tx-b", "middle")
        c.text(x0 + 95, 172, "sorted (green): 2", "tx-s t3", "middle")
        nest = {2: "nested (grey): 2² = 4", 1: "nested (grey): 2¹ = 2", 0.5: f"nested (grey): √2 ≈ {nested:.3f}"}[p]
        c.text(x0 + 95, 186, nest, "tx-s", "middle")
        verdict = {2: "sorting wins", 1: "a tie", 0.5: "nesting wins"}[p]
        c.text(x0 + 95, 206, verdict, "tx-b", "middle")
    c.save()


# ---------------------------------------------------------------------------------------------
def fig_measures():
    c = Canvas("measures", 660, 215, "Mass of a set for a discrete measure, a density and a mixture", sub=SUB)
    # (a) discrete
    f = Fig(c, (20, 40, 190, 120), (0, 3), (0, 0.85))
    A = (1, 3)
    f.path([(A[0], 0), (A[0], 0.85), (A[1], 0.85), (A[1], 0)], "am", close=True)
    f.line(0, 0, 3, 0, "ax")
    pts, w = [0.5, 1.5, 2.5], [0.2, 0.5, 0.3]
    for x, m in zip(pts, w):
        f.lollipop(x, m, 2)
        f.text(x, m, f"{m:g}", "tx-s", "middle", dy=-9)
    for v in (0, 1, 2, 3):
        f.text(v, 0, str(v), "tx-s", "middle", dy=14)
    c.text(115, 22, "discrete measure (3 atoms)", "tx-b", "middle")
    f.text(2, 0.85, "A", "tx-i", "middle", dy=-4)
    c.text(115, 192, f"A = [1, 3]:  α(A) = 0.5 + 0.3 = {0.5 + 0.3:g}", "tx-s", "middle")
    # (b) density
    g = Fig(c, (240, 40, 190, 120), (0, 3), (0, 0.85))
    rho = lambda x: 0.6 * gauss(x, 1.0, 0.35) + 0.4 * gauss(x, 2.2, 0.3)
    xs = np.linspace(0, 3, 301)
    B = (1, 2)
    xb = np.linspace(B[0], B[1], 101)
    g.path([(B[0], 0)] + [(x, rho(x)) for x in xb] + [(B[1], 0)], "a2", close=True)
    g.path([(x, rho(x)) for x in xs], "ln c2")
    g.line(0, 0, 3, 0, "ax")
    massB = 0.6 * (ncdf((2 - 1.0) / 0.35) - ncdf((1 - 1.0) / 0.35)) + 0.4 * (ncdf((2 - 2.2) / 0.3) - ncdf((1 - 2.2) / 0.3))
    for v in (0, 1, 2, 3):
        g.text(v, 0, str(v), "tx-s", "middle", dy=14)
    c.text(335, 22, "a density (two bumps)", "tx-b", "middle")
    g.text(1.5, 0.0, "A", "tx-i", "middle", dy=-6)
    c.text(335, 192, f"A = [1, 2]:  α(A) = area ≈ {massB:.2f}", "tx-s", "middle")
    # (c) mixture 1/2 delta_0 + 1/2 U[0,1]
    h = Fig(c, (460, 40, 180, 120), (-0.25, 1.25), (0, 0.85))
    h.path([(0, 0), (0, 0.85), (0.5, 0.85), (0.5, 0)], "am", close=True)
    h.path([(0, 0), (0, 0.5), (1, 0.5), (1, 0)], "a2", close=True)
    h.path([(0, 0.5), (1, 0.5), (1, 0)], "ln c2 thin")
    h.lollipop(0, 0.7, 2)
    h.text(0, 0.7, "atom ½", "tx-s", "start", dx=8, dy=0)
    h.text(0.75, 0.5, "½ × density 1", "tx-s", "middle", dy=-6)
    h.line(-0.25, 0, 1.25, 0, "ax")
    for v, s in ((0, "0"), (0.5, "½"), (1, "1")):
        h.text(v, 0, s, "tx-s", "middle", dy=14)
    c.text(550, 22, "a mixture: ½δ₀ + ½ uniform", "tx-b", "middle")
    h.text(0.25, 0.85, "A", "tx-i", "middle", dy=-4)
    c.text(550, 192, "A = [0, ½]:  α(A) = ½ + ¼ = ¾", "tx-s", "middle")
    c.save()
    return massB


# ---------------------------------------------------------------------------------------------
def fig_pushforward():
    c = Canvas("pushforward", 600, 400, "Mass conservation through the graph of an increasing map T", sub=SUB)
    T = lambda x: (x + x * x) / 2
    Tp = lambda x: 0.5 + x
    rho_b = lambda y: 2 / np.sqrt(1 + 8 * y)
    G = Fig(c, (200, 30, 300, 260), (0, 1), (0, 1))
    G.axes(xticks=[0, 0.5, 1], yticks=[0, 0.5, 1], xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:g}", grid=True)
    x0, dx = 0.62, 0.07
    y_lo, y_hi = T(x0), T(x0 + dx)
    # vertical strip from the axis to the graph
    G.path([(x0, 0), (x0, y_lo), (x0 + dx, y_hi), (x0 + dx, 0)], "a2", close=True)
    # horizontal strip from the graph to the axis
    G.path([(0, y_lo), (x0, y_lo), (x0 + dx, y_hi), (0, y_hi)], "a1", close=True)
    G.fn(T, "ln c3", 0, 1, 200)
    G.line(0, 0, 1, 1, "gr")
    G.text(1, T(1), "T(x) = (x + x²)/2", "tx-s t3", "end", dx=-4, dy=-8)
    G.text(x0 + dx / 2, 0, "dx", "tx-s", "middle", dy=28)
    G.text(0, (y_lo + y_hi) / 2, "T′(x) dx", "tx-s", "start", dx=6, dy=4)
    # source density below (uniform, height 1)
    S = Fig(c, (200, 318, 300, 50), (0, 1), (0, 1.25))
    S.path([(0, 0), (0, 1), (1, 1), (1, 0)], "a2", close=True)
    S.path([(0, 0), (0, 1), (1, 1), (1, 0)], "ln c2 thin")
    S.path([(x0, 0), (x0, 1), (x0 + dx, 1), (x0 + dx, 0)], "a2", close=True)
    S.line(0, 0, 1, 0, "ax")
    c.text(350, 390, "source α = 𝒰[0,1] (density 1)", "tx-s t2", "middle")
    # target density on the left (drawn leftwards from the y axis of G)
    xs_right = 170
    scale = 70  # pixels per unit density
    ys = np.linspace(0, 1, 201)
    pts = [(xs_right - scale * rho_b(y), G.Y(y)) for y in ys]
    d = "M" + f"{xs_right} {G.Y(0):.1f}" + "".join(f"L{px:.1f} {py:.1f}" for px, py in pts) + f"L{xs_right} {G.Y(1):.1f}Z"
    c.add(f'<path d="{d}" class="a1"/>')
    d2 = "M" + "L".join(f"{px:.1f} {py:.1f}" for px, py in pts)
    c.add(f'<path d="{d2}" class="ln c1 thin"/>')
    c.add(f'<line x1="{xs_right}" y1="{G.Y(0):.1f}" x2="{xs_right}" y2="{G.Y(1):.1f}" class="ax"/>')
    # highlighted strip in the target density
    yy = np.linspace(y_lo, y_hi, 20)
    strip = [(xs_right, G.Y(y_lo))] + [(xs_right - scale * rho_b(y), G.Y(y)) for y in yy] + [(xs_right, G.Y(y_hi))]
    ds = "M" + "L".join(f"{px:.1f} {py:.1f}" for px, py in strip) + "Z"
    c.add(f'<path d="{ds}" class="a1"/>')
    for val in (1, 2):
        xv = xs_right - scale * val
        c.add(f'<line x1="{xv:.1f}" y1="{G.Y(0) + 4:.1f}" x2="{xv:.1f}" y2="{G.Y(0) + 8:.1f}" class="ax"/>')
        c.text(xv, G.Y(0) + 20, str(val), "tx-s", "middle")
    c.text(100, 22, "target β: ρβ(y) = 2/√(1+8y)", "tx-s t1", "middle")
    # equality of masses
    mass_src = dx * 1.0
    mass_tgt = (math.sqrt(1 + 8 * y_hi) - math.sqrt(1 + 8 * y_lo)) / 2
    c.text(520, 120, "same mass in", "tx-s", "start")
    c.text(520, 134, "both strips:", "tx-s", "start")
    c.text(520, 150, f"{mass_src:.3f} = {mass_tgt:.3f}", "tx-s", "start")
    c.save()
    return mass_src, mass_tgt


# ---------------------------------------------------------------------------------------------
def fig_nomap():
    c = Canvas("nomap", 660, 215, "Monge's problem is not symmetric: maps can merge atoms but not split them", sub=SUB)
    ytop, ybot = 60, 150
    panels = [
        ("no map: δ₀ → ½δ₋₁ + ½δ₁", "a map sends 0 to one place"),
        ("T ≡ 0: ½δ₋₁ + ½δ₁ → δ₀", "atoms can be merged"),
        ("𝒰[0,1] → ½δ₀ + ½δ₁", "cells [0,½) → 0, [½,1] → 1"),
    ]
    for k, (title, sub) in enumerate(panels):
        x0 = 20 + k * 215
        f = Fig(c, (x0 + 15, ytop, 170, ybot - ytop), (-1.4, 1.4), (0, 1))
        X = f.X
        c.add(f'<line x1="{x0 + 10}" y1="{ytop}" x2="{x0 + 195}" y2="{ytop}" class="gr"/>')
        c.add(f'<line x1="{x0 + 10}" y1="{ybot}" x2="{x0 + 195}" y2="{ybot}" class="gr"/>')
        c.text(x0 + 100, 24, title, "tx-b", "middle")
        c.text(x0 + 100, 200, sub, "tx-s", "middle")
        if k == 0:
            c.add(f'<circle cx="{X(0):.1f}" cy="{ytop}" r="9" class="f2"/>')
            for xt in (-1, 1):
                c.add(f'<circle cx="{X(xt):.1f}" cy="{ybot}" r="6.4" class="f1"/>')
                c.arrow(X(0), ytop + 10, X(xt) * 0.92 + X(0) * 0.08, ybot - 9, "m", "ln cm thin dash")
            c.text(X(0), (ytop + ybot) / 2 + 5, "✗", "tx-b", "middle")
            c.text(X(0) + 14, ytop - 12, "mass 1", "tx-s", "start")
            c.text(X(1), ybot + 22, "½ each", "tx-s", "middle")
        elif k == 1:
            for xs in (-1, 1):
                c.add(f'<circle cx="{X(xs):.1f}" cy="{ytop}" r="6.4" class="f2"/>')
                c.arrow(X(xs), ytop + 8, X(0) + (X(xs) - X(0)) * 0.1, ybot - 10, "3", "ln c3 thin")
            c.add(f'<circle cx="{X(0):.1f}" cy="{ybot}" r="9" class="f1"/>')
            c.text(X(-1), ytop - 12, "½", "tx-s", "middle")
            c.text(X(1), ytop - 12, "½", "tx-s", "middle")
            c.text(X(0), ybot + 24, "mass 1", "tx-s", "middle")
        else:
            # source: uniform segment [0,1] drawn on [-1.2, 1.2]; cells
            a, b = -1.2, 1.2
            mid = (a + b) / 2
            c.add(f'<rect x="{X(a):.1f}" y="{ytop - 6}" width="{X(mid) - X(a):.1f}" height="12" class="a2"/>')
            c.add(f'<rect x="{X(mid):.1f}" y="{ytop - 6}" width="{X(b) - X(mid):.1f}" height="12" class="a5"/>')
            c.add(f'<rect x="{X(a):.1f}" y="{ytop - 6}" width="{X(b) - X(a):.1f}" height="12" class="ln c2 thin nofill"/>')
            for xt, cell in ((-1, (a, mid)), (1, (mid, b))):
                c.add(f'<circle cx="{X(xt):.1f}" cy="{ybot}" r="6.4" class="f1"/>')
                for u in np.linspace(cell[0] + 0.15, cell[1] - 0.15, 3):
                    c.arrow(X(u), ytop + 8, X(xt) + (X(u) - X(xt)) * 0.12, ybot - 9, "3", "ln c3 hair")
            c.text(X(a), ytop - 12, "0", "tx-s", "middle")
            c.text(X(mid), ytop - 12, "½", "tx-s", "middle")
            c.text(X(b), ytop - 12, "1", "tx-s", "middle")
            c.text(X(-1), ybot + 22, "0", "tx-s", "middle")
            c.text(X(1), ybot + 22, "1", "tx-s", "middle")
    c.text(8, ytop + 4, "α", "tx-i t2")
    c.text(8, ybot + 4, "β", "tx-i t1")
    c.save()


# ---------------------------------------------------------------------------------------------
def fig_splitting():
    c = Canvas("splitting", 640, 300, "The segment example: splitting is optimal but no map splits; n-cell maps come close", sub=SUB)
    for k in range(2):
        x0 = 30 + k * 320
        f = Fig(c, (x0 + 20, 40, 240, 200), (-1.35, 1.35), (-0.05, 1.05))
        f.line(0, 0, 0, 1, "ln c2")
        f.line(-1, 0, -1, 1, "ln c1")
        f.line(1, 0, 1, 1, "ln c1")
        f.text(0, 0, "α", "tx-i t2", "middle", dy=18)
        f.text(-1, 0, "β (½)", "tx-i t1", "middle", dy=18)
        f.text(1, 0, "β (½)", "tx-i t1", "middle", dy=18)
        if k == 0:
            for t in (0.1, 0.3, 0.5, 0.7, 0.9):
                for s in (-1, 1):
                    c.arrow(f.X(0), f.Y(t), f.X(0.93 * s), f.Y(t), "3", "ln c3 thin")
            c.text(x0 + 140, 22, "optimal plan: split every point", "tx-b", "middle")
            c.text(x0 + 140, 268, "cost exactly 1 — but it is not a map", "tx-s", "middle")
        else:
            n = 3
            for j in range(n + 1):
                for xx in (-1, 0, 1):
                    f.line(xx - 0.05, j / n, xx + 0.05, j / n, "ln ck thin")
            for j in range(n):
                for r in (0.25 / (2 * n), 0.75 / (2 * n)):
                    tl = j / n + r
                    c.arrow(f.X(0), f.Y(tl), f.X(-0.95), f.Y(j / n + 2 * r), "3", "ln c3 thin")
                    tu = j / n + 1 / (2 * n) + r
                    c.arrow(f.X(0), f.Y(tu), f.X(0.95), f.Y(j / n + 2 * r), "3", "ln c3 thin")
            cost = 1 + 1 / (12 * n * n)
            c.text(x0 + 140, 22, f"a map with n = {n} cells", "tx-b", "middle")
            c.text(x0 + 140, 268, f"cost 1 + 1/(12n²) = {cost:.4f}", "tx-s", "middle")
            c.text(x0 + 140, 284, "lower half-cells go left, upper half-cells go right", "tx-s", "middle")
    c.save()


# ---------------------------------------------------------------------------------------------
def fig_monotone():
    c = Canvas("monotone", 620, 300, "A symmetric positive definite linear map and a rotation applied to points of the unit circle", sub=SUB)
    th = math.radians(30)
    R30 = np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]])
    B = R30 @ np.diag([1.6, 0.6]) @ R30.T
    angles = np.linspace(0, 2 * math.pi, 12, endpoint=False)  # every 30°: four points on the eigen-axes
    P = np.c_[np.cos(angles), np.sin(angles)]
    circ = np.linspace(0, 2 * math.pi, 200)
    for k, (M, title, sub) in enumerate([(B, "T(x) = Bx, B symmetric positive definite", "the gradient of ½⟨Bx, x⟩: optimal"),
                                          (R30, "T(x) = R₃₀° x, a rotation", "monotone, not a gradient: not optimal")]):
        x0 = 20 + k * 305
        f = Fig(c, (x0 + 25, 36, 230, 210), (-1.85, 1.85), (-1.68, 1.68))
        f.line(-1.85, 0, 1.85, 0, "gr")
        f.line(0, -1.68, 0, 1.68, "gr")
        f.path([(math.cos(a), math.sin(a)) for a in circ], "ln c2 thin")
        img = [(M @ np.array([math.cos(a), math.sin(a)])) for a in circ]
        f.path([tuple(v) for v in img], "ln c1 thin" + ("" if k == 0 else " dash"))
        if k == 0:
            for v in (R30[:, 0], R30[:, 1]):
                f.line(-1.8 * v[0], -1.8 * v[1], 1.8 * v[0], 1.8 * v[1], "ln cm hair dash")
        for p in P:
            q = M @ p
            c.arrow(f.X(p[0]), f.Y(p[1]), f.X(q[0]), f.Y(q[1]), "3", "ln c3 thin")
            f.circle(p[0], p[1], 2.6, "f2")
        c.text(x0 + 140, 22, title, "tx-b", "middle")
        c.text(x0 + 140, 268, sub, "tx-s", "middle")
    c.text(310, 290, "orange: points x of the unit circle;  green arrows: x → T(x);  blue: the image of the circle", "tx-s", "middle")
    c.save()
    return B


# ---------------------------------------------------------------------------------------------
def sample_disk(n, rng):
    pts = []
    while len(pts) < n:
        p = rng.uniform(-1, 1, 2)
        if p @ p <= 1:
            pts.append(p)
    return np.array(pts)


def in_dumbbell(p):
    return (np.hypot(p[0] - 0.95, p[1]) <= 0.55) or (np.hypot(p[0] + 0.95, p[1]) <= 0.55) or (abs(p[0]) <= 0.95 and abs(p[1]) <= 0.06)


def fig_tearing():
    c = Canvas("tearing", 640, 340, "Empirical Brenier maps from a disk to an ellipse and to two disks joined by a bridge", sub=SUB)
    rng = np.random.default_rng(7)
    n = 300
    X = sample_disk(n, rng)
    # ellipse target
    E = []
    while len(E) < n:
        p = rng.uniform(-1, 1, 2)
        if p @ p <= 1:
            E.append(np.array([1.45 * p[0], 0.62 * p[1]]))
    E = np.array(E)
    D = []
    while len(D) < n:
        p = np.array([rng.uniform(-1.5, 1.5), rng.uniform(-0.55, 0.55)])
        if in_dumbbell(p):
            D.append(p)
    D = np.array(D)
    rows = []
    for Y in (E, D):
        C = ((X[:, None, :] - Y[None, :, :]) ** 2).sum(-1)
        r, col = linear_sum_assignment(C)
        rows.append((Y, col, C[r, col].mean()))
    costs = []
    for row, (Y, col, cost) in enumerate(rows):
        costs.append(cost)
        TY = Y[col]
        if row == 0:
            cls = np.where(TY[:, 0] < -0.5, "f5", np.where(TY[:, 0] > 0.5, "f6", "f4"))
        else:
            cls = np.where(np.abs(TY[:, 0]) <= 0.40, "f4", np.where(TY[:, 0] < 0, "f5", "f6"))
        for k, t in enumerate((0, 0.5, 1)):
            f = Fig(c, (40 + k * 205, 22 + row * 160, 180, 120), (-1.6, 1.6), (-1.07, 1.07))
            P = (1 - t) * X + t * TY
            for p, cl in zip(P, cls):
                c.add(f'<circle cx="{f.X(p[0]):.1f}" cy="{f.Y(p[1]):.1f}" r="1.9" class="{cl}"/>')
            if row == 0:
                c.text(40 + k * 205 + 90, 16, f"t = {t:g}" if t != 0.5 else "t = ½", "tx-b", "middle")
        lab = "to an ellipse (convex)" if row == 0 else "to a dumbbell (not convex)"
        c.text(640 - 8, 22 + row * 160 + 135, lab, "tx-s", "end")
    c.save()
    return costs


# ---------------------------------------------------------------------------------------------
def fig_gauss1d():
    c = Canvas("gauss1d", 660, 270, "Gaussians on the line as points of a half-plane, and the quantile map from N(0,1) to N(3,4)", sub=SUB)
    f = Fig(c, (50, 34, 220, 180), (-1, 4), (0, 2.6))
    f.axes(xticks=[-1, 0, 1, 2, 3, 4], yticks=[0, 1, 2], xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:g}", grid=True, yaxis=False)
    f.line(-1, 0, 4, 0, "ln ck")
    A, B = (0, 1), (3, 2)
    f.line(*A, *B, "ln c3")
    f.circle(*A, 5.5, "f2")
    f.circle(*B, 5.5, "f1")
    f.circle(1.5, 1.5, 4, "f3")
    f.text(*A, "N(0, 1)", "tx-s t2", "start", dx=6, dy=16)
    f.text(*B, "N(3, 4)", "tx-s t1", "end", dx=-6, dy=-10)
    f.text(1.5, 1.5, "t = ½", "tx-s t3", "end", dx=-6, dy=-6)
    f.text(4, 0, "m", "tx-i", "end", dx=0, dy=-6)
    f.text(-1, 2.6, "σ", "tx-i", "start", dx=4, dy=4)
    f.text(1.5, 0, "Diracs (σ = 0)", "tx-s", "middle", dy=-6)
    c.text(160, 20, "the (m, σ) half-plane", "tx-b", "middle")
    c.text(160, 252, f"W₂ = distance = √10 ≈ {math.sqrt(10):.3f}", "tx-s", "middle")
    # right: densities and quantile rays
    g_top = Fig(c, (330, 40, 300, 70), (-3.5, 9.0), (0, 0.42))
    g_bot = Fig(c, (330, 150, 300, 70), (-3.5, 9.0), (0, 0.42))
    xs = np.linspace(-3.5, 9.0, 400)
    pa = gauss(xs, 0, 1)
    pb = gauss(xs, 3, 2)
    ybase_top = g_top.Y(0)
    ybase_bot = g_bot.Y(0.42)  # target density drawn downward from the top of the bottom panel
    # top density upward
    d = "M" + f"{g_top.X(xs[0]):.1f} {ybase_top:.1f}" + "".join(f"L{g_top.X(x):.1f} {g_top.Y(y):.1f}" for x, y in zip(xs, pa)) + f"L{g_top.X(xs[-1]):.1f} {ybase_top:.1f}Z"
    c.add(f'<path d="{d}" class="a2"/>')
    c.add(f'<path d="' + "M" + "L".join(f"{g_top.X(x):.1f} {g_top.Y(y):.1f}" for x, y in zip(xs, pa)) + '" class="ln c2 thin"/>')
    # bottom density downward
    scale = (g_bot.Y(0) - g_bot.Y(0.42)) / 0.42
    pts = [(g_bot.X(x), ybase_bot + scale * y) for x, y in zip(xs, pb)]
    d = "M" + f"{pts[0][0]:.1f} {ybase_bot:.1f}" + "".join(f"L{px:.1f} {py:.1f}" for px, py in pts) + f"L{pts[-1][0]:.1f} {ybase_bot:.1f}Z"
    c.add(f'<path d="{d}" class="a1"/>')
    c.add('<path d="' + "M" + "L".join(f"{px:.1f} {py:.1f}" for px, py in pts) + '" class="ln c1 thin"/>')
    c.add(f'<line x1="{g_top.X(-3.5):.1f}" y1="{ybase_top:.1f}" x2="{g_top.X(9):.1f}" y2="{ybase_top:.1f}" class="ax"/>')
    c.add(f'<line x1="{g_bot.X(-3.5):.1f}" y1="{ybase_bot:.1f}" x2="{g_bot.X(9):.1f}" y2="{ybase_bot:.1f}" class="ax"/>')
    from scipy.stats import norm
    for r in np.arange(0.05, 1.0, 0.1):
        xa = norm.ppf(r)
        xb = 3 + 2 * xa
        c.add(f'<line x1="{g_top.X(xa):.1f}" y1="{ybase_top:.1f}" x2="{g_bot.X(xb):.1f}" y2="{ybase_bot:.1f}" class="ln c3 thin"/>')
    for v in (-2, 0, 2, 4, 6, 8):
        c.text(g_bot.X(v), ybase_bot + 0 - 4 if False else g_top.Y(0) + 13, "", "tx-s")
    for v in (-2, 0, 2, 4, 6, 8):
        c.text(g_bot.X(v), 258, str(v), "tx-s", "middle")
        c.add(f'<line x1="{g_bot.X(v):.1f}" y1="244" x2="{g_bot.X(v):.1f}" y2="248" class="ax"/>')
    c.add(f'<line x1="{g_bot.X(-3.5):.1f}" y1="246" x2="{g_bot.X(9):.1f}" y2="246" class="ax"/>')
    c.text(g_top.X(0), g_top.Y(0.4) - 6, "α = N(0, 1)", "tx-s t2", "middle")
    c.text(g_bot.X(6.8), ybase_bot + 26, "β = N(3, 4)", "tx-s t1", "middle")
    c.text(480, 20, "T(x) = 2x + 3 joins equal quantile levels", "tx-b", "middle")
    c.save()


# ---------------------------------------------------------------------------------------------
def mixture_pdf(x, w, m, s):
    return sum(wi * gauss(x, mi, si) for wi, mi, si in zip(w, m, s))


def mixture_cdf(x, w, m, s):
    return sum(wi * ncdf((x - mi) / si) for wi, mi, si in zip(w, m, s))


SRC = ([0.46, 0.54], [-1.45, 0.78], [0.34, 0.43])
TGT = ([0.24, 0.43, 0.33], [-2.02, 0.05, 1.92], [0.24, 0.39, 0.28])


def fig_quantilemap():
    c = Canvas("quantilemap", 660, 300, "Construction of the one-dimensional Monge map from the two cumulative distribution functions", sub=SUB)
    xs = np.linspace(-3.4, 3.4, 4001)
    Ca = mixture_cdf(xs, *SRC)
    Cb = mixture_cdf(xs, *TGT)
    qinv = lambda C, r: float(np.interp(r, C, xs))
    f = Fig(c, (40, 30, 300, 210), (-3.4, 3.4), (0, 1.02))
    f.axes(xticks=[-3, -2, -1, 0, 1, 2, 3], yticks=[0, 0.2, 0.5, 0.8, 1], xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:g}", grid=False)
    f.path(list(zip(xs[::8], Ca[::8])), "ln c2")
    f.path(list(zip(xs[::8], Cb[::8])), "ln c1")
    pts_map = []
    for r in (0.2, 0.5, 0.8):
        xa, xb = qinv(Ca, r), qinv(Cb, r)
        pts_map.append((xa, xb))
        f.line(xa, 0, xa, r, "ln c3 thin dot")
        f.line(xa, r, xb, r, "ln c3 thin dot")
        f.line(xb, r, xb, 0, "ln c3 thin dot")
        c.arrow(f.X(xb), f.Y(r) + 2, f.X(xb), f.Y(0) - 3, "3", "ln c3 thin")
        f.circle(xa, 0, 3.5, "f2")
        f.circle(xb, 0, 3.5, "f1")
    f.text(-3.3, 0.93, "CDF of α", "tx-s t2", "start")
    f.text(-1.0, 0.93, "CDF of β", "tx-s t1", "start")
    c.text(190, 18, "CDFs: up from x, across at level r, down to T(x)", "tx-b", "middle")
    # right: graph of T
    g = Fig(c, (420, 30, 210, 210), (-3.4, 3.4), (-3.4, 3.4))
    g.axes(xticks=[-3, 0, 3], yticks=[-3, 0, 3], xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:g}", grid=True)
    xx = np.linspace(-2.9, 2.6, 600)
    Tx = np.interp(mixture_cdf(xx, *SRC), Cb, xs)
    g.path(list(zip(xx, Tx)), "ln c3")
    g.line(-3.4, -3.4, 3.4, 3.4, "gr")
    for xa, xb in pts_map:
        g.circle(xa, xb, 3.5, "f3")
    g.text(3.4, -3.4, "x", "tx-i", "end", dy=-6)
    g.text(-3.4, 3.4, "T(x)", "tx-i", "start", dx=4, dy=4)
    c.text(525, 18, "the map T (green)", "tx-b", "middle")
    # densities as small strips under each panel
    h = Fig(c, (420, 262, 210, 28), (-3.4, 3.4), (0, 1.05))
    pa = mixture_pdf(xs, *SRC)
    h.path([(-3.4, 0)] + list(zip(xs[::10], pa[::10])) + [(3.4, 0)], "a2", close=True)
    h.path(list(zip(xs[::10], pa[::10])), "ln c2 thin")
    k = Fig(c, (40, 262, 300, 28), (-3.4, 3.4), (0, 1.25))
    pb = mixture_pdf(xs, *TGT)
    k.path([(-3.4, 0)] + list(zip(xs[::10], pb[::10])) + [(3.4, 0)], "a1", close=True)
    k.path(list(zip(xs[::10], pb[::10])), "ln c1 thin")
    k.path([(-3.4, 0)] + list(zip(xs[::10], pa[::10])) + [(3.4, 0)], "a2", close=True)
    c.save()
    return [(r, qinv(Ca, r), qinv(Cb, r)) for r in (0.2, 0.5, 0.8)]


# ---------------------------------------------------------------------------------------------
def fig_ex7():
    """Exercise 7 of the sheet: piecewise constant densities on [0, 1] and the map T = C_beta^{-1} o C_alpha."""
    c = Canvas("ex7map", 640, 250, "Exercise 7: the two piecewise constant densities and the optimal map, a broken line", sub=SUB)
    ra = lambda x: 2 / 3 if x < 0.5 else 4 / 3          # normalised densities (mass 3/2 divided out)
    rb = lambda y: 4 / 3 if y < 0.5 else 2 / 3
    Ca = lambda x: 2 * x / 3 if x <= 0.5 else 1 / 3 + 4 * (x - 0.5) / 3
    Cbi = lambda u: 3 * u / 4 if u <= 2 / 3 else 0.5 + 1.5 * (u - 2 / 3)
    T = lambda x: Cbi(Ca(x))
    xsplit = 0.75  # C_alpha(3/4) = 2/3 = C_beta(1/2)
    assert abs(Ca(xsplit) - 2 / 3) < 1e-12
    f = Fig(c, (60, 34, 240, 160), (0, 1), (0, 1.55))
    f.axes(xticks=[0, 0.5, 0.75, 1], yticks=[0, 2 / 3, 4 / 3], xfmt=lambda v: {0: "0", 0.5: "½", 0.75: "¾", 1: "1"}[v],
           yfmt=lambda v: {0: "0", 2 / 3: "2/3", 4 / 3: "4/3"}[v], grid=True, yaxis=False)
    for rho, k, a in ((ra, 2, "a2"), (rb, 1, "a1")):
        pts = [(0, 0), (0, rho(0.25)), (0.5, rho(0.25)), (0.5, rho(0.75)), (1, rho(0.75)), (1, 0)]
        f.path(pts, a, close=True)
        f.path(pts, f"ln c{k}")
    f.line(xsplit, 0, xsplit, 1.5, "ln c3 thin dash")
    f.text(xsplit, 1.5, "Cα = 2/3 here", "tx-s t3", "middle", dy=-4)
    f.text(0.25, 2 / 3, "α", "tx-i t2", "middle", dy=-6)
    f.text(0.25, 4 / 3, "β", "tx-i t1", "middle", dy=-6)
    f.text(0.62, 4 / 3, "α", "tx-i t2", "middle", dy=-6)
    f.text(0.88, 2 / 3, "β", "tx-i t1", "middle", dy=-6)
    c.text(180, 18, "normalised densities of α (orange) and β (blue)", "tx-b", "middle")
    g = Fig(c, (420, 34, 160, 160), (0, 1), (0, 1))
    g.axes(xticks=[0, 0.5, 0.75, 1], yticks=[0, 0.25, 0.5, 1], xfmt=lambda v: {0: "0", 0.5: "½", 0.75: "¾", 1: "1"}[v],
           yfmt=lambda v: {0: "0", 0.25: "¼", 0.5: "½", 1: "1"}[v], grid=True, yaxis=False)
    g.line(0, 0, 1, 1, "gr")
    corners = [(x, T(x)) for x in (0, 0.5, 0.75, 1)]
    g.path(corners, "ln c3")
    for (x0, y0), (x1, y1) in zip(corners[:-1], corners[1:]):
        if x1 < 1:
            g.circle(x1, y1, 3.2, "f3")
        slope = (y1 - y0) / (x1 - x0)
        g.text((x0 + x1) / 2, (y0 + y1) / 2, "slope " + {0.5: "½", 1.0: "1", 2.0: "2"}[round(slope, 9)], "tx-s t3", "start", dx=7, dy=10)
    c.text(500, 18, "T = Cβ⁻¹ ∘ Cα (green), below the diagonal", "tx-b", "middle")
    c.text(500, 236, "corners (½, ¼) and (¾, ½); cost 5/144", "tx-s", "middle")
    c.save()
    return corners, sum(  # cost by the midpoint rule on a fine grid, as a check of 5/144
        (x - T(x)) ** 2 * ra(x) / 200000 for x in (np.arange(200000) + 0.5) / 200000)


# ---------------------------------------------------------------------------------------------
def fig_mccann():
    c = Canvas("mccann", 640, 345, "McCann interpolation between two point clouds along the optimal assignment, and the mixture", sub=SUB)
    rng = np.random.default_rng(3)
    n = 60
    A = np.c_[rng.normal(-1.55, 0.22, n), rng.normal(0.0, 0.32, n)]
    ang = np.sort(rng.uniform(0, 2 * math.pi, n))
    rad = 0.62 + 0.04 * rng.normal(size=n)
    Bc = np.c_[1.55 + rad * np.cos(ang), rad * np.sin(ang)]
    C = ((A[:, None] - Bc[None]) ** 2).sum(-1)
    r, col = linear_sum_assignment(C)
    TB = Bc[col]
    f = Fig(c, (30, 30, 580, 196), (-2.8, 2.8), (-0.947, 0.947))
    for p, q in zip(A, TB):
        f.line(p[0], p[1], q[0], q[1], "ln cm hair")
    for p in A:
        f.circle(p[0], p[1], 2.8, "f2")
    for q in Bc:
        f.circle(q[0], q[1], 2.8, "f1")
    M = 0.5 * (A + TB)
    for p in M:
        f.circle(p[0], p[1], 2.8, "f3")
    c.text(320, 18, "displacement interpolation: α (t = 0), the cloud at t = ½ (green), β (t = 1)", "tx-b", "middle")
    dmin = min(np.linalg.norm(M[i] - M[j]) for i in range(n) for j in range(i + 1, n))
    g = Fig(c, (175, 262, 290, 78), (-2.8, 2.8), (-0.75, 0.75))
    for p in A:
        c.add(f'<circle cx="{g.X(p[0]):.1f}" cy="{g.Y(p[1]):.1f}" r="2.3" class="f2" fill-opacity="0.45"/>')
    for q in Bc:
        c.add(f'<circle cx="{g.X(q[0]):.1f}" cy="{g.Y(q[1]):.1f}" r="2.3" class="f1" fill-opacity="0.45"/>')
    c.text(320, 250, "the mixture ½α + ½β at t = ½: both clouds at half weight, nothing has moved", "tx-s", "middle")
    c.save()
    return C[r, col].mean(), dmin


if __name__ == "__main__":
    fig_timeline()
    fig_crossing()
    fig_regimes()
    print("measures: mass of [1,2] =", fig_measures())
    print("pushforward strip masses:", fig_pushforward())
    fig_nomap()
    fig_splitting()
    print("monotone B =", fig_monotone().round(4).tolist())
    print("tearing mean costs (ellipse, dumbbell):", fig_tearing())
    fig_gauss1d()
    print("quantile map points (r, x, T(x)):", fig_quantilemap())
    print("mccann mean cost, min distance at t=1/2:", fig_mccann())
    print("ex7 corners of T, cost (5/144 = %.6f):" % (5 / 144), fig_ex7())
