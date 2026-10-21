"""figures_L02.py — static SVG figures of Lesson 2 (Kantorovich's relaxation, the discrete problem), written to figures/L02/.

Run: python3 figures_L02.py        (then node build.mjs Lesson02.html)
Every coordinate and every number displayed is computed here (plans by the north-west rule or by POT's exact solver).
Colour code: source alpha = 2 (orange-red), target beta = 1 (blue), plans / maps / interpolations = 3 (green).
"""
import math

import numpy as np

from figures_common import Canvas, Fig

SUB = "L02"

try:
    import ot  # only used to double-check the plans drawn below
except ImportError:  # pragma: no cover
    ot = None


def north_west(a, b, tol=1e-12):
    a, b = [float(v) for v in a], [float(v) for v in b]
    n, m = len(a), len(b)
    P = np.zeros((n, m))
    i = j = 0
    order = []
    while i < n and j < m:
        t = min(a[i], b[j])
        P[i, j] = t
        a[i] -= t
        b[j] -= t
        order.append((i, j))
        ri, cj = a[i] <= tol, b[j] <= tol
        if ri:
            i += 1
        if cj:
            j += 1
    return P, order


def num(v):
    """0.3 -> '.3', 0.15 -> '.15', 1 -> '1'."""
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return s[1:] if s.startswith("0.") else s


# ---------------------------------------------------------------------------------------------
def fig_split():
    c = Canvas("split", 660, 214, "A map cannot split an atom; a coupling can; a map can merge atoms", sub=SUB)
    titles = ["a map cannot split δ₀", "a coupling can: ½ and ½", "a map can merge atoms"]
    for k in range(3):
        f = Fig(c, (22 + k * 216, 40, 190, 120), (-1.5, 1.5), (0, 1))
        c.text(22 + k * 216 + 95, 22, titles[k], "tx-b", "middle")
        f.line(-1.5, 1, 1.5, 1, "gr")
        f.line(-1.5, 0, 1.5, 0, "gr")
        if k < 2:
            f.circle(0, 1, 8, "f2")
            f.text(0, 1, "α = δ₀", "tx-s t2", "start", dx=12, dy=-6)
            for y in (-1, 1):
                f.circle(y, 0, 6, "f1")
                f.text(y, 0, "½", "tx-s t1", "middle", dy=18)
            f.text(1.5, 0, "β", "tx-s t1", "end", dy=-8)
        if k == 0:
            c.arrow(f.X(0) + 3, f.Y(1) + 8, f.X(1) - 4, f.Y(0) - 8, 3, "ln c3 thin")
            f.text(0.55, 0.55, "T(0)", "tx-s t3", "start", dx=6)
            f.text(-1, 0.35, "nothing", "tx-s", "middle")
            f.text(-1, 0.22, "arrives", "tx-s", "middle")
            c.text(22 + 95, 196, "T♯δ₀ is a single Dirac, at T(0): ≠ β", "tx-s", "middle")
        if k == 1:
            for y in (-1, 1):
                c.arrow(f.X(0) + 5 * y, f.Y(1) + 7, f.X(y) - 5 * y, f.Y(0) - 8, 3, "ln c3")
                f.text(0.5 * y, 0.5, "½", "tx-s t3", "middle", dx=14 * y)
            c.text(22 + 216 + 95, 196, "P = (½  ½): mass is split", "tx-s", "middle")
        if k == 2:
            for x in (-1, 1):
                f.circle(x, 1, 6, "f2")
                f.text(x, 1, "½", "tx-s t2", "middle", dy=-10)
                c.arrow(f.X(x) - 4 * x, f.Y(1) + 7, f.X(0) + 6 * x, f.Y(0) - 8, 3, "ln c3")
            f.circle(0, 0, 8, "f1")
            f.text(0, 0, "β = δ₀", "tx-s t1", "start", dx=12, dy=4)
            c.text(22 + 2 * 216 + 95, 196, "T(−1) = T(1) = 0 is admissible", "tx-s", "middle")
    c.save()


def fig_matrix():
    a = np.array([0.10, 0.25, 0.30, 0.20, 0.15])
    b = np.array([0.20, 0.10, 0.15, 0.25, 0.20, 0.10])
    x = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    y = np.array([0.5, 1.2, 2.0, 2.6, 3.3, 4.2])
    Pnw, _ = north_west(a, b)
    Pprod = np.outer(a, b)
    C = (x[:, None] - y[None]) ** 2
    if ot is not None:
        assert abs(np.sum(Pnw * C) - ot.emd2(a, b, C)) < 1e-9
    c = Canvas("matrix", 660, 300, "Two couplings of the same histograms drawn as matrices with their marginals", sub=SUB)
    cell = 30
    for k, (P, title) in enumerate([(Pprod, "product plan a ⊗ b"), (Pnw, "optimal plan (sorted points)")]):
        x0, y0 = 90 + k * 320, 82
        c.text(x0 + 3 * cell, 18, title, "tx-b", "middle")
        for j in range(6):  # target marginal on top
            h = b[j] * 160
            c.add(f'<rect x="{x0 + j * cell + 7:.1f}" y="{y0 - 6 - h:.1f}" width="{cell - 14}" height="{h:.1f}" class="a1 ln c1 thin"/>')
        for i in range(5):  # source marginal on the left
            w = a[i] * 160
            c.add(f'<rect x="{x0 - 6 - w:.1f}" y="{y0 + i * cell + 7:.1f}" width="{w:.1f}" height="{cell - 14}" class="a2 ln c2 thin"/>')
        for i in range(6):
            c.add(f'<line x1="{x0}" y1="{y0 + i * cell}" x2="{x0 + 6 * cell}" y2="{y0 + i * cell}" class="gr"/>')
        for j in range(7):
            c.add(f'<line x1="{x0 + j * cell}" y1="{y0}" x2="{x0 + j * cell}" y2="{y0 + 5 * cell}" class="gr"/>')
        for i in range(5):
            for j in range(6):
                if P[i, j] > 1e-12:
                    r = 2 + 26 * math.sqrt(P[i, j])
                    c.add(f'<circle cx="{x0 + (j + 0.5) * cell:.1f}" cy="{y0 + (i + 0.5) * cell:.1f}" r="{r:.1f}" class="f3"/>')
        nnz = int(np.sum(P > 1e-12))
        c.text(x0 + 3 * cell, y0 + 5 * cell + 22, f"{nnz} non-zero entries" + ("  (n m = 30)" if k == 0 else "  (n + m − 1 = 10)"), "tx-s", "middle")
        c.text(x0 + 3 * cell, y0 + 5 * cell + 38, f"cost for |x − y|²: {np.sum(P * C):.3f}", "tx-s t3", "middle")
        c.text(x0 - 6, y0 - 8, "b", "tx-i", "end")
        c.text(x0 - 40, y0 + 5 * cell + 16, "a", "tx-i", "middle")
    c.text(330, 292, "rows: sources x = 0, 1, 2, 3, 4 (weights a);  columns: targets y = 0.5, 1.2, 2, 2.6, 3.3, 4.2 (weights b);  disc area ∝ Pᵢⱼ", "tx-s", "middle")
    c.save()
    return np.sum(Pprod * C), np.sum(Pnw * C)


def fig_segment():
    c = Canvas("segment", 580, 262, "The couplings of a two-by-two problem form a segment, and the cost is linear along it", sub=SUB)
    f = Fig(c, (66, 26, 470, 186), (-0.03, 0.36), (0, 5.6))
    f.axes(xticks=[0, 0.1, 0.2, 0.3], yticks=[0, 1, 2, 3, 4, 5], xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:g}", xlabel="s = P₁₁", ylabel="cost ⟨C, P(s)⟩ = 5 − 8s")
    f.line(0, 0, 0.3, 0, "ln c3")
    f.line(0, 0.04, 0, -0.04, "ln c3")
    f.fn(lambda s: 5 - 8 * s, "ln c4", 0, 0.3, 50)
    f.circle(0, 5, 5, "fk")
    f.text(0, 5, "s = 0: P = (0 .5 / .3 .2), cost 5", "tx-s", "start", dx=9, dy=-8)
    f.circle(0.15, 3.8, 5, "fm")
    f.text(0.15, 3.8, "product a ⊗ b (s = 0.15): cost 3.8", "tx-s", "start", dx=6, dy=-10)
    f.circle(0.3, 2.6, 6, "f3")
    f.text(0.3, 2.6, "s = 0.3: P = (.3 .2 / 0 .5)", "tx-s t3", "end", dx=-4, dy=22)
    f.text(0.3, 2.6, "optimal, cost 2.6", "tx-s t3", "end", dx=-4, dy=38)
    f.text(0.15, 0, "feasible s: [0, 0.3]", "tx-s t3", "middle", dy=-7)
    c.save()


def fig_cycle():
    c = Canvas("cycle", 660, 236, "A support with a cycle can be perturbed both ways; the support of a vertex is a forest", sub=SUB)
    rows = [(0, 70), (0, 160)]
    cols = [(150, 50), (150, 115), (150, 180)]
    a = np.array([0.6, 0.4]); b = np.array([0.3, 0.45, 0.25])
    panels = [(40, "product plan: 6 edges, a cycle"), (380, "a vertex: 4 = n + m − 1 edges, no cycle")]
    Pv = np.array([[0.3, 0.3, 0.0], [0.0, 0.15, 0.25]])
    # labels of the alternating perturbation, in panel coordinates (x, y baseline)
    eps_lab = {(0, 0): (75, 52, "+ε"), (0, 1): (128, 103, "−ε"), (1, 0): (30, 131, "−ε"), (1, 1): (75, 158, "+ε")}
    for k, (x0, title) in enumerate(panels):
        c.text(x0 + 110, 20, title, "tx-b", "middle")
        P = np.outer(a, b) if k == 0 else Pv
        for i, (rx, ry) in enumerate(rows):
            for j, (cx, cy) in enumerate(cols):
                if P[i, j] > 1e-12:
                    cls = "ln cm thin"
                    if k == 0 and (i, j) in eps_lab:
                        cls = "ln c3"
                    if k == 1:
                        cls = "ln c3"
                    c.add(f'<line x1="{x0 + rx}" y1="{ry}" x2="{x0 + cx}" y2="{cy}" class="{cls}"/>')
                    if k == 0 and (i, j) in eps_lab:
                        lx, ly, lab = eps_lab[(i, j)]
                        c.text(x0 + lx, ly, lab, "tx-s t3", "middle")
                    if k == 1:
                        c.text(x0 + 0.5 * rx + 0.5 * cx + 6, 0.5 * ry + 0.5 * cy - 5, num(P[i, j]), "tx-s t3", "middle")
        for i, (rx, ry) in enumerate(rows):
            c.add(f'<circle cx="{x0 + rx}" cy="{ry}" r="7" class="f2"/>')
            c.text(x0 + rx - 12, ry + 4, f"x{'₁₂'[i]}", "tx-s t2", "end")
        for j, (cx, cy) in enumerate(cols):
            c.add(f'<circle cx="{x0 + cx}" cy="{cy}" r="7" class="f1"/>')
            c.text(x0 + cx + 12, cy + 4, f"y{'₁₂₃'[j]}", "tx-s t1", "start")
    c.text(150, 222, "green cycle: P ± εE keeps all row and column sums", "tx-s", "middle")
    c.text(490, 222, "P = (.3 .3 0 / 0 .15 .25): a path, i.e. a tree", "tx-s", "middle")
    c.save()


def fig_nw():
    a = [0.2, 0.5, 0.3]
    b = [0.5, 0.1, 0.4]
    P, order = north_west(a, b)
    c = Canvas("nw", 660, 250, "The north-west corner rule on a = (0.2, 0.5, 0.3), b = (0.5, 0.1, 0.4), and its reading on the line", sub=SUB)
    cell, x0, y0 = 46, 80, 58
    c.text(x0 + 1.5 * cell, 18, "fill from the top-left corner", "tx-b", "middle")
    for i in range(4):
        c.add(f'<line x1="{x0}" y1="{y0 + i * cell}" x2="{x0 + 3 * cell}" y2="{y0 + i * cell}" class="gr"/>')
        c.add(f'<line x1="{x0 + i * cell}" y1="{y0}" x2="{x0 + i * cell}" y2="{y0 + 3 * cell}" class="gr"/>')
    for j in range(3):
        c.text(x0 + (j + 0.5) * cell, y0 - 8, f"b{'₁₂₃'[j]} = {b[j]:g}", "tx-s t1", "middle")
    for i in range(3):
        c.text(x0 - 8, y0 + (i + 0.5) * cell + 4, f"a{'₁₂₃'[i]} = {a[i]:g}", "tx-s t2", "end")
    pts = [(x0 + (j + 0.5) * cell, y0 + (i + 0.5) * cell) for i, j in order]
    for k in range(len(pts) - 1):
        (u1, v1), (u2, v2) = pts[k], pts[k + 1]
        dx, dy = u2 - u1, v2 - v1
        L = math.hypot(dx, dy)
        c.arrow(u1 + dx / L * 15, v1 + dy / L * 15, u2 - dx / L * 15, v2 - dy / L * 15, 3, "ln c3 thin")
    for k, (i, j) in enumerate(order):
        cx, cy = x0 + (j + 0.5) * cell, y0 + (i + 0.5) * cell
        c.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="13" class="fs ln c3 thin"/>')
        c.text(cx, cy + 4, num(P[i, j]), "tx-s", "middle")
        c.text(cx + 15, cy - 10, str(k + 1), "tx-s t3", "start")
    c.text(x0 + 1.5 * cell, y0 + 3 * cell + 22, "5 steps, 5 = n + m − 1 entries", "tx-s", "middle")
    # right: the line
    f = Fig(c, (340, 50, 290, 150), (-0.3, 2.8), (0, 1))
    xs, ys = [0.0, 1.0, 2.0], [0.5, 1.5, 2.5]
    c.text(485, 18, "on the line: sorted mass to sorted mass", "tx-b", "middle")
    f.line(-0.3, 1, 2.8, 1, "gr")
    f.line(-0.3, 0, 2.8, 0, "gr")
    for i in range(3):
        for j in range(3):
            if P[i, j] > 1e-12:
                c.add(f'<line x1="{f.X(xs[i]):.1f}" y1="{f.Y(1) + 8:.1f}" x2="{f.X(ys[j]):.1f}" y2="{f.Y(0) - 8:.1f}" class="ln c3" stroke-width="{1 + 22 * P[i, j]:.1f}" stroke-opacity="0.55"/>')
                f.text(0.5 * xs[i] + 0.5 * ys[j], 0.5, num(P[i, j]), "tx-s t3", "middle", dx=(-9 if j < i else 9))
    for i in range(3):
        f.circle(xs[i], 1, 3 + 14 * math.sqrt(a[i]), "f2")
        f.text(xs[i], 1, f"x = {xs[i]:g}", "tx-s t2", "middle", dy=-16)
    for j in range(3):
        f.circle(ys[j], 0, 3 + 14 * math.sqrt(b[j]), "f1")
        f.text(ys[j], 0, f"y = {ys[j]:g}", "tx-s t1", "middle", dy=24)
    c.save()


def fig_uncross():
    c = Canvas("uncross", 660, 250, "Uncrossing two arrows never increases a convex cost h(x − y)", sub=SUB)
    f = Fig(c, (40, 46, 250, 130), (-0.4, 2.4), (0, 1))
    c.text(165, 18, "crossed (dashed) or uncrossed (green)", "tx-b", "middle")
    f.line(-0.4, 1, 2.4, 1, "gr")
    f.line(-0.4, 0, 2.4, 0, "gr")
    c.add(f'<line x1="{f.X(0):.1f}" y1="{f.Y(1) + 7:.1f}" x2="{f.X(2):.1f}" y2="{f.Y(0) - 7:.1f}" class="ln c2 thin dash"/>')
    c.add(f'<line x1="{f.X(1):.1f}" y1="{f.Y(1) + 7:.1f}" x2="{f.X(1):.1f}" y2="{f.Y(0) - 7:.1f}" class="ln c2 thin dash"/>')
    c.add(f'<line x1="{f.X(0) - 4:.1f}" y1="{f.Y(1) + 7:.1f}" x2="{f.X(1) - 4:.1f}" y2="{f.Y(0) - 7:.1f}" class="ln c3"/>')
    c.add(f'<line x1="{f.X(1) + 4:.1f}" y1="{f.Y(1) + 7:.1f}" x2="{f.X(2) + 4:.1f}" y2="{f.Y(0) - 7:.1f}" class="ln c3"/>')
    for v, lab in [(0, "x = 0"), (1, "x′ = 1")]:
        f.circle(v, 1, 6, "f2")
        f.text(v, 1, lab, "tx-s t2", "middle", dy=-12)
    for v, lab in [(1, "y′ = 1"), (2, "y = 2")]:
        f.circle(v, 0, 6, "f1")
        f.text(v, 0, lab, "tx-s t1", "middle", dy=20)
    c.text(165, 218, "h(z) = z²: crossed 4 + 0 = 4;  uncrossed 1 + 1 = 2", "tx-s", "middle")
    # right: increments of a convex function
    g = Fig(c, (380, 36, 250, 160), (-2.0, 1.6), (-0.3, 4.2))
    c.text(505, 18, "a convex h has increasing increments", "tx-b", "middle")
    g.line(-2.0, 0, 1.6, 0, "ax")
    g.fn(lambda z: z * z, "ln ck thin", -2.0, 1.6, 200)
    u, eta, delta = -1.5, 1.0, 1.5
    for z0, cls, lab in [(u, "c2", "h(u+η) − h(u) = −2"), (u + delta, "c3", "h(u+δ+η) − h(u+δ) = 1")]:
        z1 = z0 + eta
        g.line(z0, z0 * z0, z1, z0 * z0, f"ln {cls} thin dash")
        g.line(z1, z0 * z0, z1, z1 * z1, f"ln {cls}")
        g.circle(z0, z0 * z0, 3.5, f"f{cls[1]}")
        g.circle(z1, z1 * z1, 3.5, f"f{cls[1]}")
    g.text(u, 0, "u", "tx-s", "middle", dy=14)
    g.text(u + eta, 0, "u+η", "tx-s", "middle", dy=14)
    g.text(u + delta, 0, "u+δ", "tx-s", "middle", dy=26)
    g.text(u + delta + eta, 0, "u+δ+η", "tx-s", "middle", dy=14)
    c.text(505, 230, "same step η, further right: larger increment", "tx-s", "middle")
    c.text(505, 244, "u = −1.5, δ = 1.5, η = 1:  orange −2  ≤  green +1", "tx-s", "middle")
    c.save()


def perm_matrix(sig):
    n = len(sig)
    M = np.zeros((n, n))
    for i, s in enumerate(sig):
        M[i, s - 1] = 1
    return M


def fig_bvn():
    P = np.array([[0.6, 0.4, 0.0], [0.4, 0.3, 0.3], [0.0, 0.3, 0.7]])
    terms = [(0.4, (2, 1, 3)), (0.3, (1, 2, 3)), (0.3, (1, 3, 2))]
    S = sum(l * perm_matrix(s) for l, s in terms)
    assert np.allclose(S, P)
    c = Canvas("bvn", 660, 170, "A bistochastic matrix written as a convex combination of three permutation matrices", sub=SUB)
    cell = 26

    def grid(x0, y0, M, values):
        for i in range(3):
            for j in range(3):
                cls = "a3" if M[i, j] > 0 else "nofill"
                c.add(f'<rect x="{x0 + j * cell}" y="{y0 + i * cell}" width="{cell}" height="{cell}" class="{cls} ln cm hair"/>')
                if values:
                    c.text(x0 + (j + 0.5) * cell, y0 + (i + 0.5) * cell + 4, num(M[i, j]) if M[i, j] > 0 else "0", "tx-s", "middle")
                elif M[i, j] > 0:
                    c.add(f'<circle cx="{x0 + (j + 0.5) * cell}" cy="{y0 + (i + 0.5) * cell}" r="6" class="f3"/>')
    y0 = 40
    grid(20, y0, P, True)
    c.text(20 + 1.5 * cell, 26, "P", "tx-i", "middle")
    c.text(120, y0 + 1.5 * cell + 5, "=", "tx-b", "middle")
    xs = [170, 330, 490]
    names = ["σ = [2, 1, 3]", "σ = [1, 2, 3]", "σ = [1, 3, 2]"]
    for k, ((lam, sig), x0) in enumerate(zip(terms, xs)):
        c.text(x0 + 4, y0 + 1.5 * cell + 5, f"{lam:g} ×", "tx-b", "start")
        grid(x0 + 46, y0, perm_matrix(sig), False)
        c.text(x0 + 46 + 1.5 * cell, y0 + 3 * cell + 18, names[k], "tx-s", "middle")
        if k < 2:
            c.text(x0 + 138, y0 + 1.5 * cell + 5, "+", "tx-b", "middle")
    c.text(330, 160, "σ = [σ(1), σ(2), σ(3)];  weights 0.4 + 0.3 + 0.3 = 1;  never more than (n − 1)² + 1 = 5 terms for n = 3", "tx-s", "middle")
    c.save()


def fig_atoms():
    xa, aa = [-1.0, 0.0, 1.0], [0.25, 0.5, 0.25]
    yb, bb = [-1.0, 1.0], [0.5, 0.5]
    c = Canvas("atoms", 660, 236, "With atoms, the best map can cost three times the best coupling", sub=SUB)
    # (from, to, mass, label x, label y, anchor)
    # labels of the two crossing arrows placed beside their own arrow, away from the crossing point
    maps = [(-1.0, -1.0, 0.25, -1.0, 0.5, "end"), (0.0, 1.0, 0.5, 0.87, 0.33, "start"), (1.0, -1.0, 0.25, -0.4, 0.17, "start")]
    plan = [(-1.0, -1.0, 0.25, -1.0, 0.5, "end"), (0.0, -1.0, 0.25, -0.62, 0.22, "start"), (0.0, 1.0, 0.25, 0.62, 0.22, "end"), (1.0, 1.0, 0.25, 1.0, 0.5, "start")]
    cost_map = sum(m * (x - y) ** 2 for x, y, m, *_ in maps)
    cost_plan = sum(m * (x - y) ** 2 for x, y, m, *_ in plan)
    if ot is not None:
        C = (np.array(xa)[:, None] - np.array(yb)[None]) ** 2
        assert abs(ot.emd2(np.array(aa), np.array(bb), C) - cost_plan) < 1e-12
    for k, (arrows, title, cost) in enumerate([(maps, "best map", cost_map), (plan, "best coupling", cost_plan)]):
        f = Fig(c, (40 + k * 320, 50, 260, 120), (-1.5, 1.5), (0, 1))
        c.text(40 + k * 320 + 130, 20, f"{title}: cost {cost:g}", "tx-b", "middle")
        f.line(-1.5, 1, 1.5, 1, "gr")
        f.line(-1.5, 0, 1.5, 0, "gr")
        for x, y, m, lx, ly, anc in arrows:
            off = 4 * y if (k == 1 and x == 0) else 0
            c.add(f'<line x1="{f.X(x) + off:.1f}" y1="{f.Y(1) + 9:.1f}" x2="{f.X(y):.1f}" y2="{f.Y(0) - 9:.1f}" class="ln c3" stroke-width="{1 + 10 * m:.1f}" stroke-opacity="0.7"/>')
            dx = -8 if (anc == "end" and x == y) else (8 if (anc == "start" and x == y) else 0)
            f.text(lx, ly, f"{num(m)} × {(x - y) ** 2:g}", "tx-s t3", anc, dx=dx)
        for x, m in zip(xa, aa):
            f.circle(x, 1, 3 + 12 * math.sqrt(m), "f2")
            f.text(x, 1, num(m), "tx-s t2", "middle", dy=-14)
        for y, m in zip(yb, bb):
            f.circle(y, 0, 3 + 12 * math.sqrt(m), "f1")
            f.text(y, 0, f"{num(m)} at {y:g}".replace("-", "−"), "tx-s t1", "middle", dy=24)
    c.text(170, 228, "the atom at 0 must go whole to one side", "tx-s", "middle")
    c.text(490, 228, "the atom at 0 is split, the outer atoms stay", "tx-s", "middle")
    c.save()
    return cost_map, cost_plan


def fig_quantile():
    c = Canvas("quantile", 660, 262, "One-dimensional Kantorovich solution with an atom: couple equal quantile levels", sub=SUB)
    f = Fig(c, (40, 40, 250, 150), (-0.3, 2.3), (0, 1.15))
    c.text(165, 20, "α = ½δ₀ + ½𝒰[1, 2] and β = 𝒰[0, 2]", "tx-b", "middle")
    f.line(-0.3, 0, 2.3, 0, "ax")
    f.path([(0, 0), (0, 0.5), (2, 0.5), (2, 0)], "a1", close=True)
    f.path([(0, 0), (0, 0.5), (2, 0.5), (2, 0)], "ln c1 thin nofill")
    f.path([(1, 0), (1, 0.5), (2, 0.5), (2, 0)], "a2", close=True)
    f.path([(1, 0), (1, 0.5), (2, 0.5), (2, 0)], "ln c2 thin nofill dash")
    f.lollipop(0, 1.0, 2)
    f.text(0, 1.0, "atom ½ at 0", "tx-s t2", "start", dx=9, dy=4)
    f.text(1.5, 0.5, "α: density ½", "tx-s t2", "middle", dy=-8)
    f.text(0.5, 0.5, "β: density ½", "tx-s t1", "middle", dy=-8)
    for v in (0, 1, 2):
        f.text(v, 0, str(v), "tx-s", "middle", dy=14)
    g = Fig(c, (380, 40, 250, 150), (0, 1), (0, 2.1))
    g.axes(xticks=[0, 0.5, 1], yticks=[0, 1, 2], xfmt=lambda v: {0: "0", 0.5: "½", 1: "1"}[v], yfmt=lambda v: f"{v:g}", grid=False, xlabel="level r", ylabel="quantile")
    rr = np.linspace(0, 0.5, 60)
    g.path([(0, 0)] + [(r, 2 * r) for r in rr] + [(0.5, 0)], "a3", close=True)
    g.line(0, 0, 1, 2, "ln c1")
    g.line(0, 0.012, 0.5, 0.012, "ln c2")
    g.line(0.5, 1, 1, 2, "ln c2 dash")
    g.text(0.66, 1.32, "quantile of β: 2r", "tx-s t1", "end", dx=-8)
    g.text(0.27, 0.0, "α: the atom", "tx-s t2", "middle", dy=-8)
    g.text(0.8, 1.6, "equal for r > ½", "tx-s t2", "end", dx=-6, dy=-4)
    c.text(505, 20, "quantile functions", "tx-b", "middle")
    c.text(505, 238, "levels r ≤ ½: from the atom at 0 to 2r ∈ [0, 1] (split)", "tx-s", "middle")
    c.text(505, 254, "cost = integral of (2r)² over [0, ½] = 1/6", "tx-s t3", "middle")
    c.save()


def fig_interp():
    x = np.array([0.0, 1.0]); y = np.array([0.0, 1.0, 2.0])
    a = np.array([0.6, 0.4]); b = np.array([0.3, 0.45, 0.25])
    P, _ = north_west(a, b)
    Tbar = (P @ y) / a
    c = Canvas("interp", 600, 290, "Displacement interpolation of a plan: every non-zero entry becomes a moving atom", sub=SUB)
    f = Fig(c, (70, 30, 470, 210), (-0.3, 2.3), (0, 1))
    f.line(-0.3, 0, 2.3, 0, "gr")
    f.line(-0.3, 1, 2.3, 1, "gr")
    for i in range(2):
        for j in range(3):
            if P[i, j] > 1e-12:
                c.add(f'<line x1="{f.X(x[i]):.1f}" y1="{f.Y(0):.1f}" x2="{f.X(y[j]):.1f}" y2="{f.Y(1):.1f}" class="ln c3" stroke-width="{1 + 16 * P[i, j]:.1f}" stroke-opacity="0.45"/>')
    t = 0.5
    f.line(-0.3, t, 2.3, t, "ln cm thin dash")
    for i in range(2):
        for j in range(3):
            if P[i, j] > 1e-12:
                z = (1 - t) * x[i] + t * y[j]
                f.circle(z, t, 3 + 12 * math.sqrt(P[i, j]), "f3")
                f.text(z, t, num(P[i, j]), "tx-s", "middle", dy=-13)
    for i in range(2):
        f.circle(x[i], 0, 3 + 12 * math.sqrt(a[i]), "f2")
        f.text(x[i], 0, f"{num(a[i])} at {x[i]:g}", "tx-s t2", "middle", dy=26)
    for j in range(3):
        f.circle(y[j], 1, 3 + 12 * math.sqrt(b[j]), "f1")
        f.text(y[j], 1, f"{num(b[j])} at {y[j]:g}", "tx-s t1", "middle", dy=-16)
    for i in range(2):
        f.line(Tbar[i] - 0.04, 1 - 0.05, Tbar[i] + 0.04, 1 + 0.05, "ln c3")
        f.line(Tbar[i] - 0.04, 1 + 0.05, Tbar[i] + 0.04, 1 - 0.05, "ln c3")
    f.text(Tbar[1], 1, f"T̄(x₂) = {Tbar[1]:g}", "tx-s t3", "middle", dy=24)
    f.text(Tbar[0], 1, f"T̄(x₁) = {Tbar[0]:g}", "tx-s t3", "middle", dy=24)
    f.text(-0.3, 0, "t = 0", "tx-s", "end", dx=-6, dy=4)
    f.text(-0.3, 1, "t = 1", "tx-s", "end", dx=-6, dy=4)
    f.text(-0.3, t, "t = ½", "tx-s", "end", dx=-6, dy=4)
    c.text(305, 282, "at t = ½ there are 4 atoms (one per non-zero Pᵢⱼ); green crosses: barycentric projection (mean destination)", "tx-s", "middle")
    c.save()
    return Tbar


def fig_simplex():
    a = np.array([0.6, 0.4]); b = np.array([0.3, 0.45, 0.25])
    C = np.array([[3.0, 1, 2], [1, 2, 4]])
    verts = [(0, 0.35), (0, 0.45), (0.15, 0.45), (0.3, 0.3), (0.3, 0.05)]

    def plan(s, t):
        return np.array([[s, t, a[0] - s - t], [b[0] - s, b[1] - t, b[2] - a[0] + s + t]])

    cost = lambda s, t: float(np.sum(plan(s, t) * C))
    assert abs(cost(0.1, 0.2) - (4 * 0.1 + 0.2 + 1)) < 1e-12
    path = [(0.3, 0.3), (0.15, 0.45), (0, 0.45), (0, 0.35)]
    c = Canvas("simplex", 620, 344, "The transport polytope of a 2 by 3 problem, cost level lines and the path of the network simplex", sub=SUB)
    f = Fig(c, (70, 24, 300, 260), (-0.04, 0.36), (0.0, 0.52))
    f.axes(xticks=[0, 0.1, 0.2, 0.3], yticks=[0, 0.1, 0.2, 0.3, 0.4, 0.5], xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:g}", xlabel="s = P₁₁", ylabel="t = P₁₂")
    poly = verts + [verts[0]]
    f.path(poly, "a3", close=True)
    f.path(poly, "ln c3 thin")
    # the level line through the optimum touches the polytope only there
    opt_line = [(s_, 0.35 - 4 * s_) for s_ in np.linspace(-0.012, 0.0875, 20)]  # stops below the label "cost 1.45"
    f.path(opt_line, "ln c3 thin dash")
    for lev in [1.7, 2.3, 2.9]:  # chosen so that no level line crosses a vertex label
        s0, s1 = -0.04, 0.36
        pts = [(s, lev - 1 - 4 * s) for s in np.linspace(s0, s1, 50)]
        pts = [p for p in pts if 0.0 <= p[1] <= 0.52]
        if len(pts) > 1:
            f.path(pts, "ln cm hair dash")
            lab = [p for p in pts if p[1] >= 0.025][0] if lev - 1 - 4 * 0.36 < 0.025 else pts[-1]
            f.text(lab[0], lab[1], f"{lev:g}", "tx-s", "start", dx=3, dy=-2)
    for k in range(len(path) - 1):
        (s1, t1), (s2, t2) = path[k], path[k + 1]
        X1, Y1, X2, Y2 = f.X(s1), f.Y(t1), f.X(s2), f.Y(t2)
        L = math.hypot(X2 - X1, Y2 - Y1)
        c.arrow(X1 + (X2 - X1) / L * 9, Y1 + (Y2 - Y1) / L * 9, X2 - (X2 - X1) / L * 9, Y2 - (Y2 - Y1) / L * 9, 2, "ln c2")
    offs = {(0, 0.35): (-8, 4, "end"), (0, 0.45): (-8, -6, "end"), (0.15, 0.45): (0, -10, "middle"), (0.3, 0.3): (8, 4, "start"), (0.3, 0.05): (8, 4, "start")}
    for v in verts:
        cls = "f3" if v == (0, 0.35) else "fk"
        f.circle(v[0], v[1], 5, cls)
        dx, dy, anc = offs[v]
        f.text(v[0], v[1], f"cost {cost(*v):.2f}", "tx-s" + (" t3" if v == (0, 0.35) else ""), anc, dx=dx, dy=dy)
    f.text(0.3, 0.3, "start: north-west", "tx-s t2", "start", dx=8, dy=18)
    f.text(0.0, 0.35, "optimum", "tx-s t3", "end", dx=-8, dy=18)
    # right: the plans along the path
    x0 = 420
    c.text(x0 + 80, 30, "the four plans visited", "tx-b", "middle")
    for k, (s, t) in enumerate(path):
        P = plan(s, t)
        yy = 56 + k * 62
        c.text(x0, yy, f"{k}: cost {cost(s, t):.2f}", "tx-s" + (" t3" if k == 3 else ""), "start")
        for i in range(2):
            row = "  ".join(num(v) if v > 1e-12 else "0" for v in P[i])
            c.text(x0 + 10, yy + 16 + 14 * i, f"( {row} )", "tx-s", "start")
    c.text(310, 336, "C = (3 1 2 / 1 2 4);  cost = 1 + 4s + t on the pentagon;  dashed: level lines of the cost", "tx-s", "middle")
    c.save()


if __name__ == "__main__":
    fig_split()
    print("matrix costs (product, optimal):", fig_matrix())
    fig_segment()
    fig_cycle()
    fig_nw()
    fig_uncross()
    fig_bvn()
    print("atoms costs (map, plan):", fig_atoms())
    fig_quantile()
    print("barycentric projection:", fig_interp())
    fig_simplex()
