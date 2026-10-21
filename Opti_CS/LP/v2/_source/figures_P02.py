"""figures_P02.py — static SVG figures of Partie 2 (sommets et solutions basiques), written to figures/P02/.

Run: python3 figures_P02.py        (then node build.mjs Partie02.html)

The running example is the polygon of Allaire, Exercice 4.2.1, in standard form (m = 3, n = 5):
    -3 x1 + 2 x2 + x3 = 2,   -x1 + 2 x2 + x4 = 4,   x1 + x2 + x5 = b3   (b3 = 5, or 7/2 for the degenerate variant)
Every coordinate below is computed (exact fractions for the basic points).
"""
from fractions import Fraction as Fr
from itertools import combinations

import numpy as np

from figures_common import Canvas, Fig, esc

SUB = "P02"
SUBS = "₀₁₂₃₄₅₆₇₈₉"
A421 = [[-3, 2, 1, 0, 0], [-1, 2, 0, 1, 0], [1, 1, 0, 0, 1]]


def sub(k):
    return "".join(SUBS[int(ch)] for ch in str(k))


def rich(s):
    """Escapes s and turns X_ad, x_B into SVG subscripts (no underscore is left in the figure)."""
    s = esc(s)
    for a, b in [("X_ad", "ad"), ("x_B", "B")]:
        s = s.replace(a, a[0] + f'<tspan baseline-shift="sub" font-size="75%">{b}</tspan>')
    return s


def rtext(c, x, y, s, cls="tx-s", anchor="start"):
    c.add(f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}">{rich(s)}</text>')


def frtext(f, x, y, s, cls="tx-s", anchor="start", dx=0, dy=0):
    rtext(f.c, f.X(x) + dx, f.Y(y) + dy, s, cls, anchor)


def fs(v):
    v = Fr(v)
    s = str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"
    return s.replace("-", "−")


def solve(B, r):
    n = len(B)
    M = [[Fr(v) for v in row] + [Fr(r[i])] for i, row in enumerate(B)]
    for k in range(n):
        p = next((i for i in range(k, n) if M[i][k] != 0), None)
        if p is None:
            return None
        M[p], M[k] = M[k], M[p]
        for i in range(n):
            if i != k and M[i][k] != 0:
                f = M[i][k] / M[k][k]
                M[i] = [a - f * b for a, b in zip(M[i], M[k])]
    return [M[i][n] / M[i][i] for i in range(n)]


def basic_points(b):
    """All the bases of the polygon (m = 3, n = 5): list of (cols, x) with x the point of the basis (None if singular)."""
    out = []
    for cols in combinations(range(5), 3):
        B = [[A421[i][j] for j in cols] for i in range(3)]
        xb = solve(B, b)
        x = None
        if xb is not None:
            x = [Fr(0)] * 5
            for j, v in zip(cols, xb):
                x[j] = v
        out.append((cols, x))
    return out


def lines421(b3):
    """The five lines x_i = 0 in the plane (x1, x2), as a x1 + b x2 = r."""
    return [(1, 0, 0), (0, 1, 0), (-3, 2, 2), (-1, 2, 4), (1, 1, b3)]


def clip_line(a, b, r, box):
    x0, x1, y0, y1 = box
    pts = []
    if abs(b) > 1e-12:
        for x in (x0, x1):
            y = (r - a * x) / b
            if y0 - 1e-9 <= y <= y1 + 1e-9:
                pts.append((x, y))
    if abs(a) > 1e-12:
        for y in (y0, y1):
            x = (r - b * y) / a
            if x0 - 1e-9 <= x <= x1 + 1e-9:
                pts.append((x, y))
    best, d = None, -1
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            dd = np.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1])
            if dd > d:
                d, best = dd, (pts[i], pts[j])
    return best


def polygon(cons, box):
    """Vertices of {a x + b y <= r} inside the box (Sutherland-Hodgman), in order."""
    P = [(box[0], box[2]), (box[1], box[2]), (box[1], box[3]), (box[0], box[3])]
    for a, b, r in cons:
        out = []
        for i in range(len(P)):
            p, q = P[i], P[(i + 1) % len(P)]
            fp, fq = a * p[0] + b * p[1] - r, a * q[0] + b * q[1] - r
            if fp <= 1e-12:
                out.append(p)
            if (fp < -1e-12 and fq > 1e-12) or (fp > 1e-12 and fq < -1e-12):
                t = fp / (fp - fq)
                out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
        P = out
    return P


def poly421(b3):
    return [(-1, 0, 0), (0, -1, 0), (-3, 2, 2), (-1, 2, 4), (1, 1, float(b3))]


def draw_lines(f, box, b3, labels, cls="ln cm thin"):
    """Draws the five lines x_i = 0 and their labels: labels[i] = (x, y, anchor, dx, dy) or None."""
    for i, (a, b, r) in enumerate(lines421(float(b3))):
        seg = clip_line(a, b, r, box)
        f.line(seg[0][0], seg[0][1], seg[1][0], seg[1][1], cls)
        if labels[i]:
            x, y, anc, dx, dy = labels[i]
            f.text(x, y, f"x{sub(i + 1)} = 0", "tx-s", anc, dx=dx, dy=dy)


# ---------------------------------------------------------------------------------------------
def fig_sommets():
    c = Canvas("sommets", 660, 300, "Sommet ou pas : un sommet du polygone, un point d'une arête, un point intérieur", sub=SUB)
    box = (-0.4, 5.8, -0.4, 3.9)
    f = Fig(c, (34, 22, 360, 250), (box[0], box[1]), (box[2], box[3]))
    f.axes(xticks=[0, 1, 2, 3, 4, 5], yticks=[0, 1, 2, 3], grid=False, xlabel="x₁", ylabel="x₂")
    P = polygon(poly421(5), box)
    f.path(P, "a1", close=True)
    f.path(P, "ln c1", close=True)
    # a vertex
    f.circle(2, 3, 5.5, "f3")
    f.text(2, 3, "sommet (2 ; 3)", "tx-s t3", "start", dx=8, dy=-6)
    # a point of an edge: midpoint of (3, 2) and (4, 1)
    f.line(3, 2, 4, 1, "ln c6", ' style="stroke-width:3.2px"')
    for (u, v) in [(3, 2), (4, 1)]:
        f.circle(u, v, 3.5, "f6")
    f.circle(3.5, 1.5, 4.5, "fk")
    f.text(3.5, 1.5, "(7/2 ; 3/2) = milieu de", "tx-s", "start", dx=10, dy=-4)
    f.text(3.5, 1.5, "(3 ; 2) et (4 ; 1)", "tx-s", "start", dx=10, dy=9)
    # an interior point
    f.line(0.5, 1, 1.5, 1, "ln c6", ' style="stroke-width:3.2px"')
    f.line(1, 0.5, 1, 1.5, "ln c6", ' style="stroke-width:3.2px"')
    f.circle(1, 1, 4.5, "fk")
    f.text(1, 1, "(1 ; 1)", "tx-s", "start", dx=6, dy=16)
    # right panel: theta arbitrary -> midpoint of a shorter segment
    X0, Y0 = 420, 110
    c.text(530, 40, "Si x = θy + (1−θ)z avec y ≠ z,", "tx-s", "middle")
    c.text(530, 54, "x est aussi le milieu d'un segment", "tx-s", "middle")
    yx, zx, th = 430.0, 615.0, 1 / 3  # x = theta y + (1 - theta) z
    xx = th * yx + (1 - th) * zx
    delta = min(th, 1 - th)
    c.add(f'<line x1="{yx}" y1="{Y0 + 40}" x2="{zx}" y2="{Y0 + 40}" class="ln cm thin"/>')
    for px, lab in [(yx, "y"), (zx, "z")]:
        c.add(f'<circle cx="{px}" cy="{Y0 + 40}" r="4" class="fm"/>')
        c.text(px, Y0 + 62, lab, "tx-i", "middle")
    lo, hi = xx - delta * (zx - yx), xx + delta * (zx - yx)
    c.add(f'<line x1="{lo:.1f}" y1="{Y0 + 40}" x2="{hi:.1f}" y2="{Y0 + 40}" class="ln c6" style="stroke-width:3.2px"/>')
    c.add(f'<circle cx="{xx:.1f}" cy="{Y0 + 40}" r="4.5" class="fk"/>')
    c.text(xx, Y0 + 28, "x", "tx-i", "middle")
    c.text(lo, Y0 + 84, "x + u", "tx-s", "middle")
    c.text(hi, Y0 + 84, "x − u = z", "tx-s", "middle")
    c.text(530, Y0 + 120, "θ = 1/3 ;  u = δ(y − z), δ = min(θ, 1−θ)", "tx-s", "middle")
    rtext(c, 530, Y0 + 136, "x ± u restent sur [y, z], donc dans X_ad", "tx-s", "middle")
    c.save()


def fig_droites():
    c = Canvas("droites", 660, 420, "Les cinq droites xi = 0 de l'Exercice 4.2.1 et les dix points de base", sub=SUB)
    box = (-4.7, 6.3, -0.9, 5.8)
    f = Fig(c, (40, 16, 600, 370), (box[0], box[1]), (box[2], box[3]))
    P = polygon(poly421(5), box)
    f.path(P, "a1", close=True)
    labels = [(0, 5.8, "start", 5, 12), (6.3, 0, "end", -2, -6), (3.2, 5.8, "start", 6, 12),
              (-4.7, -0.35, "start", 4, 16), (5.85, -0.85, "end", -8, -4)]
    draw_lines(f, box, 5, labels)
    f.path(P, "ln c1", close=True)
    lab = {  # basis -> (anchor, dx, dy) of its label
        (0, 1, 2): ("start", 9, -2), (0, 1, 3): ("end", -8, -8), (0, 1, 4): ("start", 8, 14),
        (0, 2, 3): ("start", 8, 16), (0, 2, 4): ("middle", 0, 18), (0, 3, 4): ("middle", 0, 18),
        (1, 2, 3): ("start", 8, -6), (1, 2, 4): ("end", -8, -4), (1, 3, 4): ("end", -8, 14), (2, 3, 4): ("start", 8, 16),
    }
    for cols, x in basic_points([2, 4, 5]):
        ok = all(v >= 0 for v in x)
        f.circle(float(x[0]), float(x[1]), 5, "f1" if ok else "f6")
        anc, dx, dy = lab[cols]
        name = "{" + ",".join(str(j + 1) for j in cols) + "}"
        f.text(float(x[0]), float(x[1]), name, "tx-s " + ("t1" if ok else "t6"), anc, dx=dx, dy=dy)
    rtext(c, 52, 410, "● admissible : sommet (x_B ≥ 0)", "tx-s t1")
    rtext(c, 270, 410, "● non admissible (une composante de x_B < 0)", "tx-s t6")
    c.save()


def fig_degenere():
    c = Canvas("degenere", 660, 330, "Variante degeneree x1 + x2 <= 7/2 : trois droites passent par (1 ; 5/2)", sub=SUB)
    box = (-0.6, 4.4, -0.5, 3.9)
    f = Fig(c, (40, 16, 330, 280), (box[0], box[1]), (box[2], box[3]))
    f.axes(xticks=[0, 1, 2, 3, 4], yticks=[0, 1, 2, 3], grid=False)
    b3 = Fr(7, 2)
    P = polygon(poly421(b3), box)
    f.path(P, "a1", close=True)
    labels = [None, None, (1.95, 3.9, "start", 4, 12), (3.75, 3.9, "start", 5, 16), (3.5, 0, "start", 4, -26)]
    draw_lines(f, box, b3, labels)
    f.path(P, "ln c1", close=True)
    for cols, x in basic_points([2, 4, b3]):
        if all(v >= 0 for v in x):
            f.circle(float(x[0]), float(x[1]), 5, "f1")
    f.circle(1, 2.5, 8, "ln c3 nofill")
    f.circle(1, 2.5, 5, "f3")
    f.text(1, 2.5, "(1 ; 5/2)", "tx-b t3", "end", dx=-12, dy=-8)
    # right: the three bases
    X = 395
    c.text(X, 40, "Trois bases, un seul point :", "tx-b")
    rows = [("{1, 2, 3}", "x₄ = x₅ = 0", "x_B = (x₁, x₂, x₃) = (1, 5/2, 0)"),
            ("{1, 2, 4}", "x₃ = x₅ = 0", "x_B = (x₁, x₂, x₄) = (1, 5/2, 0)"),
            ("{1, 2, 5}", "x₃ = x₄ = 0", "x_B = (x₁, x₂, x₅) = (1, 5/2, 0)")]
    for k, (bs, nul, xb) in enumerate(rows):
        y = 72 + 46 * k
        c.text(X, y, "B = " + bs + " :  " + nul, "tx-s")
        rtext(c, X + 12, y + 16, xb, "tx-s t3")
    c.text(X, 222, "Chaque fois une variable de base est nulle :", "tx-s")
    c.text(X, 238, "x = (1, 5/2, 0, 0, 0) n'a que 2 < m = 3", "tx-s")
    c.text(X, 254, "composantes non nulles. Trois droites", "tx-s")
    c.text(X, 270, "xᵢ = 0 au lieu de n − m = 2 s'y croisent.", "tx-s")
    c.save()


def fig_perturbation():
    c = Canvas("perturbation", 660, 290, "Perturber dans le noyau : un point d'arete est un milieu, un sommet est coince", sub=SUB)
    box = (-0.4, 5.6, -0.4, 3.7)
    for k in range(2):
        f = Fig(c, (30 + 330 * k, 30, 290, 200), (box[0], box[1]), (box[2], box[3]))
        f.axes(xticks=[0, 1, 2, 3, 4, 5], yticks=[0, 1, 2, 3], grid=False)
        P = polygon(poly421(5), box)
        f.path(P, "a1", close=True)
        f.path(P, "ln c1", close=True)
        if k == 0:
            c.text(30 + 145, 18, "x = (7/2, 3/2, 19/2, 9/2, 0) : k = 4 > m", "tx-b", "middle")
            f.line(2, 3, 5, 0, "ln c6", ' style="stroke-width:3.4px"')
            f.circle(3.5, 1.5, 5, "fk")
            f.circle(2, 3, 4, "f6")
            f.circle(5, 0, 4, "f6")
            f.text(3.5, 1.5, "x", "tx-i", "start", dx=8, dy=4)
            f.text(2, 3, "x − (3/2) y", "tx-s", "start", dx=8, dy=-4)
            f.text(4.75, 0.6, "x + (3/2) y", "tx-s", "start", dx=4, dy=0)
            c.text(30 + 145, 262, "y = (1, −1, 5, 3, 0) : Ay = 0 et y₅ = 0,", "tx-s", "middle")
            rtext(c, 30 + 145, 278, "x ± εy ∈ X_ad pour ε ≤ 3/2 : x n'est pas un sommet", "tx-s", "middle")
        else:
            c.text(360 + 145, 18, "x = (2, 3, 2, 0, 0) : k = 3, colonnes libres", "tx-b", "middle")
            f.circle(2, 3, 5, "f3")
            # the two directions along the lines x4 = 0 and x5 = 0, both ways
            mk = c.arrow_marker(6)
            for (dx, dy) in [(1, -1), (-1, -1 / 2)]:
                for sgn in (1, -1):
                    x2, y2 = 2 + sgn * 0.8 * dx, 3 + sgn * 0.8 * dy
                    inside = (x2 + y2 <= 5 + 1e-9) and (-x2 + 2 * y2 <= 4 + 1e-9)
                    cls = "ln c3 thin" if inside else "ln c6 thin dash"
                    c.add(f'<line x1="{f.X(2):.1f}" y1="{f.Y(3):.1f}" x2="{f.X(x2):.1f}" y2="{f.Y(y2):.1f}" class="{cls}" marker-end="url(#{mk})"/>')
            frtext(f, 2.8, 2.2, "reste dans X_ad", "tx-s t3", "start", dx=6, dy=4)
            f.text(1.2, 2.6, "reste", "tx-s t3", "end", dx=-4, dy=10)
            f.text(2.8, 3.4, "x₅ < 0", "tx-s t6", "start", dx=4, dy=0)
            f.text(1.2, 3.4, "x₄ < 0", "tx-s t6", "end", dx=-4, dy=-4)
            c.text(360 + 145, 262, "Bouger en gardant x₄ = x₅ = 0 est impossible :", "tx-s", "middle")
            c.text(360 + 145, 278, "x + u et x − u ne sont jamais tous deux admissibles", "tx-s", "middle")
    c.save()


def fig_glisser():
    c = Canvas("glisser", 660, 330, "Reduire le support : de l'interieur a un sommet en glissant dans le noyau (c = 0)", sub=SUB)
    box = (-0.4, 5.9, -0.4, 3.8)
    f = Fig(c, (40, 20, 380, 270), (box[0], box[1]), (box[2], box[3]))
    f.axes(xticks=[0, 1, 2, 3, 4, 5], yticks=[0, 1, 2, 3], grid=False, xlabel="x₁", ylabel="x₂")
    P = polygon(poly421(5), box)
    f.path(P, "a1", close=True)
    f.path(P, "ln c1", close=True)
    mk3 = c.arrow_marker(3)
    mkm = c.arrow_marker("m")
    # path 1: (1,1) -> (4,1) -> (5,0)
    for (a, b) in [((1, 1), (4, 1)), ((4, 1), (5, 0))]:
        c.add(f'<line x1="{f.X(a[0]):.1f}" y1="{f.Y(a[1]):.1f}" x2="{f.X(b[0]):.1f}" y2="{f.Y(b[1]):.1f}" class="ln c3" marker-end="url(#{mk3})"/>')
    # path 2: (1,1) -> (1, 5/2)
    c.add(f'<line x1="{f.X(1):.1f}" y1="{f.Y(1):.1f}" x2="{f.X(1):.1f}" y2="{f.Y(2.5):.1f}" class="ln cm thin dash" marker-end="url(#{mkm})"/>')
    for (u, v), cls in [((1, 1), "fk"), ((4, 1), "fk"), ((5, 0), "f3"), ((1, 2.5), "fm")]:
        f.circle(u, v, 5 if cls != "fk" else 4.5, cls)
    f.text(1, 1, "x⁰", "tx-i", "end", dx=-6, dy=16)
    f.text(4, 1, "x¹", "tx-i", "start", dx=4, dy=-8)
    f.text(5, 0, "x²", "tx-i", "start", dx=6, dy=-6)
    f.text(1, 2.5, "variante", "tx-s", "end", dx=-8, dy=4)
    X = 445
    c.text(X, 46, "x⁰ = (1, 1, 3, 3, 3)", "tx-b")
    c.text(X, 62, "k = 5 ; y = (1, 0, 3, 1, −1), ε₀ = 3", "tx-s")
    c.text(X, 92, "x¹ = (4, 1, 12, 6, 0)", "tx-b")
    c.text(X, 108, "k = 4 ; y = (1, −1, 5, 3, 0), ε₀ = 1", "tx-s")
    c.text(X, 138, "x² = (5, 0, 17, 9, 0)", "tx-b t3")
    c.text(X, 154, "k = 3, colonnes a₁, a₃, a₄ libres :", "tx-s t3")
    c.text(X, 170, "sommet, base {1, 3, 4}", "tx-s t3")
    c.text(X, 210, "Variante (direction (0, 1)) : ε₀ = 3/2", "tx-s")
    c.text(X, 226, "annule x₃ et x₄ d'un coup :", "tx-s")
    c.text(X, 242, "(1, 5/2, 0, 0, 3/2), sommet en un pas", "tx-s")
    c.save()


def fig_demi_plan():
    c = Canvas("demi_plan", 660, 270, "Un demi-plan n'a pas de sommet ; le quadrant positif ne contient aucune droite", sub=SUB)
    box = (-2, 2, -2, 2)
    f = Fig(c, (40, 30, 220, 200), (box[0], box[1]), (box[2], box[3]))
    H = polygon([(1, 1, 1)], box)
    f.path(H, "a1", close=True)
    seg = clip_line(1, 1, 1, box)
    f.line(seg[0][0], seg[0][1], seg[1][0], seg[1][1], "ln c1")
    f.text(0.75, 1.55, "x₁ + x₂ = 1", "tx-s t1", "start")
    for (p, t) in [((0.2, 0.8), 0.7), ((-0.9, -0.6), 0.7)]:
        f.line(p[0] - t, p[1] + t, p[0] + t, p[1] - t, "ln c6", ' style="stroke-width:3px"')
        f.circle(p[0], p[1], 4.5, "fk")
    f.text(0.2, 0.8, "p", "tx-i", "start", dx=7, dy=-4)
    f.text(-0.9, -0.6, "q", "tx-i", "start", dx=7, dy=-4)
    c.text(150, 20, "H = {x₁ + x₂ ≤ 1} : aucun sommet", "tx-b", "middle")
    c.text(150, 252, "p ± t(1, −1) ∈ H pour tout t", "tx-s", "middle")
    # right: the quadrant
    g = Fig(c, (400, 30, 220, 200), (-0.5, 3), (-0.5, 3))
    g.path([(0, 0), (3, 0), (3, 3), (0, 3)], "a1", close=True)
    g.line(0, 0, 3, 0, "ln c1")
    g.line(0, 0, 0, 3, "ln c1")
    g.line(-0.5, 2.3, 3, 0.55, "ln c6 dash")
    g.circle(1.5, 1.3, 4.5, "fk")
    g.text(1.5, 1.3, "x⁰", "tx-i", "start", dx=4, dy=-8)
    g.text(-0.5, 2.3, "x⁰ + t d", "tx-s t6", "start", dx=2, dy=-8)
    g.circle(0, 0, 5, "f3")
    g.text(0, 0, "sommet 0", "tx-s t3", "start", dx=8, dy=14)
    c.text(510, 20, "ℝ²₊ (forme standard) : pas de droite", "tx-b", "middle")
    c.text(510, 252, "x⁰ + t d ≥ 0 pour tout t ∈ ℝ  ⇒  d = 0", "tx-s", "middle")
    c.save()


def fig_cube():
    c = Canvas("cube", 660, 300, "Le carre et le cube de l'Exercice 4.2.2 : sommets et bases", sub=SUB)
    # left: the square, standard form x1 + s1 = 1, x2 + s2 = 1
    f = Fig(c, (70, 60, 150, 150), (-0.15, 1.15), (-0.15, 1.15))
    f.path([(0, 0), (1, 0), (1, 1), (0, 1)], "a1", close=True)
    f.path([(0, 0), (1, 0), (1, 1), (0, 1)], "ln c1", close=True)
    lab = {(0, 0): ("{s₁, s₂}", "end", -8, 1), (1, 0): ("{x₁, s₂}", "start", 8, 1),
           (1, 1): ("{x₁, x₂}", "start", 8, -1), (0, 1): ("{s₁, x₂}", "end", -8, -1)}
    for (u, v), (t, anc, dx, side) in lab.items():
        f.circle(u, v, 5, "f3")
        y1, y2 = (-20, -7) if side < 0 else (16, 29)
        f.text(u, v, f"({u}, {v})", "tx-s", anc, dx=dx, dy=y1)
        f.text(u, v, t, "tx-s t3", anc, dx=dx, dy=y2)
    c.text(145, 24, "d = 2 : n = 4, m = 2, 4 sommets", "tx-b", "middle")
    c.text(145, 262, "xᵢ + sᵢ = 1, xᵢ ≥ 0, sᵢ ≥ 0", "tx-s", "middle")
    # right: the cube, oblique projection
    X0, Y0, S = 385, 228, 120

    def P(u):
        return (X0 + S * u[0] + 0.45 * S * u[2], Y0 - S * u[1] - 0.32 * S * u[2])
    V = [(a, b, d) for a in (0, 1) for b in (0, 1) for d in (0, 1)]
    hidden = (0, 0, 1)  # the hidden vertex of this view
    for u in V:
        for k in range(3):
            if u[k] == 0:
                w = list(u)
                w[k] = 1
                w = tuple(w)
                p, q = P(u), P(w)
                cls = "ln c1 thin dash" if hidden in (u, w) else "ln c1"
                c.add(f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}" class="{cls}"/>')
    place = {(0, 0, 0): ("end", -8, 14), (1, 0, 0): ("start", 6, 16), (0, 1, 0): ("end", -8, 4), (1, 1, 0): ("start", 6, 18),
             (0, 0, 1): ("start", 6, -7), (1, 0, 1): ("start", 9, 4), (0, 1, 1): ("end", -8, -4), (1, 1, 1): ("start", 8, -4)}
    for u in V:
        p = P(u)
        hl = u == (1, 0, 1)
        c.add(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="{5.5 if hl else 4.5}" class="{"f2" if hl else "f3"}"/>')
        anc, dx, dy = place[u]
        c.text(p[0] + dx, p[1] + dy, f"({','.join(str(v) for v in u)})", "tx-s t2" if hl else "tx-s", anc)
    c.text(490, 24, "d = 3 : n = 6, m = 3, 2³ = 8 sommets", "tx-b", "middle")
    c.text(490, 262, "en orange : x = (1, 0, 1), s = (0, 1, 0),", "tx-s t2", "middle")
    c.text(490, 278, "base {x₁, s₂, x₃}", "tx-s t2", "middle")
    c.save()


def fig_aretes():
    c = Canvas("aretes", 660, 330, "Aretes et bases voisines sur le polygone de l'Exercice 4.2.1", sub=SUB)
    box = (-1.9, 6.4, -0.7, 3.9)
    f = Fig(c, (24, 14, 456, 290), (box[0], box[1]), (box[2], box[3]))
    P = polygon(poly421(5), (-0.5, 6, -0.5, 3.9))
    f.path(P, "a1", close=True)
    f.path(P, "ln c1", close=True)
    verts = [((0, 0), "{3, 4, 5}", "end", -8, 16), ((5, 0), "{1, 3, 4}", "start", 8, 16),
             ((2, 3), "{1, 2, 3}", "start", 10, -4), ((1, 2.5), "{1, 2, 5}", "end", -10, 2), ((0, 1), "{2, 4, 5}", "end", -8, 4)]
    for (u, v), t, anc, dx, dy in verts:
        f.circle(u, v, 5, "f3")
        f.text(u, v, t, "tx-s t3", anc, dx=dx, dy=dy)
    edges = [((0, 0), (5, 0), "x₁ entre, x₅ sort", "middle", 0, 18, "sur x₂ = 0"),
             ((5, 0), (2, 3), "x₂ entre, x₄ sort", "start", 18, 0, "sur x₅ = 0"),
             ((2, 3), (1, 2.5), "x₅ entre, x₃ sort", "end", -2, -24, "sur x₄ = 0"),
             ((1, 2.5), (0, 1), "x₄ entre, x₁ sort", "end", -14, -4, "sur x₃ = 0"),
             ((0, 1), (0, 0), "x₃ entre, x₂ sort", "end", -10, -2, "sur x₁ = 0")]
    for (a, b, t, anc, dx, dy, on) in edges:
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        f.text(mx, my, t, "tx-s", anc, dx=dx, dy=dy)
        f.text(mx, my, on, "tx-s t1", anc, dx=dx, dy=dy + 13)
    X = 500
    c.text(X, 40, "Deux sommets voisins :", "tx-b")
    c.text(X, 58, "leurs bases ont m − 1 = 2", "tx-s")
    c.text(X, 74, "colonnes en commun.", "tx-s")
    c.text(X, 104, "L'arête est portée par la", "tx-s")
    c.text(X, 120, "droite xᵢ = 0 de la variable", "tx-s")
    c.text(X, 136, "restée hors base dans les", "tx-s")
    c.text(X, 152, "deux bases.", "tx-s")
    c.text(X, 182, "Passer d'un sommet à son", "tx-s")
    c.text(X, 198, "voisin = échanger une colonne :", "tx-s")
    c.text(X, 214, "une variable entre dans la", "tx-s")
    c.text(X, 230, "base, une autre en sort.", "tx-s")
    c.text(X, 260, "C'est le pas du simplexe", "tx-s t3")
    c.text(X, 276, "(partie 3).", "tx-s t3")
    c.save()


if __name__ == "__main__":
    fig_sommets()
    fig_droites()
    fig_degenere()
    fig_perturbation()
    fig_glisser()
    fig_demi_plan()
    fig_cube()
    fig_aretes()
