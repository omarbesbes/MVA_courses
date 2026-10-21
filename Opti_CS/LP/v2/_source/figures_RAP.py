"""figures_RAP.py — static SVG figures of the page Rappels.html, written to figures/RAP/.

Run: python3 figures_RAP.py        (then node build.mjs Rappels.html)
Every coordinate is computed here. Colours are CSS classes (see figures_common.py) and follow the colour code of
the LP pages (GUIDE.md §5): admissible set = 1 (blue), cost = 2 (orange-red), optimum / chosen point = 3 (green),
integer points = 4 (gold), dual objects (multipliers, certificates, separating hyperplanes) = 5 (purple),
non-admissible points = 6 (pink), constraint lines and neutral objects = grey.
"""
import math

import numpy as np

from figures_common import Canvas, Fig, esc

SUB = "RAP"
F = lambda p, q=1: p / q  # readability of fractions in coordinates


# ---------------------------------------------------------------------------------------------- helpers
def clip_poly(P, box):
    """Sutherland–Hodgman: the polygon P (list of (x, y)) clipped to box = (x0, x1, y0, y1)."""
    x0, x1, y0, y1 = box
    edges = [(1, 0, x1), (-1, 0, -x0), (0, 1, y1), (0, -1, -y0)]  # a x + b y <= r
    for a, b, r in edges:
        out = []
        for i in range(len(P)):
            p, q = P[i], P[(i + 1) % len(P)]
            fp, fq = a * p[0] + b * p[1] - r, a * q[0] + b * q[1] - r
            if fp <= 1e-12:
                out.append(p)
            if (fp < -1e-12 < fq) or (fq < -1e-12 < fp):
                t = fp / (fp - fq)
                out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
        P = out
        if not P:
            break
    return P


def line_in_box(a, b, r, box):
    """The segment of {a x + b y = r} inside box = (x0, x1, y0, y1)."""
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
            dd = math.dist(pts[i], pts[j])
            if dd > d:
                best, d = (pts[i], pts[j]), dd
    return best


def farrow(f, x1, y1, x2, y2, k, cls=None):
    """An arrow in the data coordinates of the panel f."""
    f.c.arrow(f.X(x1), f.Y(y1), f.X(x2), f.Y(y2), k, cls)


def grid(f, xs, ys, cls="gr"):
    for v in xs:
        f.line(v, f.yr[0], v, f.yr[1], cls)
    for v in ys:
        f.line(f.xr[0], v, f.xr[1], v, cls)


def bg_text(c, x, y, s, cls="tx-s", anchor="start", w=None):
    """Text on a light rectangle (pixel coordinates), so that it stays readable over lines."""
    w = w if w is not None else 6.2 * len(s) + 6
    x0 = x - (w / 2 if anchor == "middle" else (w - 3 if anchor == "end" else 3))
    c.add(f'<rect x="{x0:.1f}" y="{y - 11:.1f}" width="{w:.1f}" height="15" rx="3" class="lbl-bg"/>')
    c.text(x, y, s, cls, anchor)


def rich(c, x, y, parts, cls="tx-s", anchor="start"):
    """Text with subscripts: parts = [("x", ""), ("K", "sub"), …] (pixel coordinates)."""
    s = f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}">'
    for t, kind in parts:
        if kind == "sub":
            s += f'<tspan baseline-shift="sub" font-size="75%">{esc(t)}</tspan>'
        else:
            s += f"<tspan>{esc(t)}</tspan>"
    c.add(s + "</text>")


def xad(c, x, y, cls="tx-b t1", anchor="start"):
    """The label X_ad (pixel coordinates)."""
    rich(c, x, y, [("X", ""), ("ad", "sub")], cls, anchor)


def fn_clip(f, fn, cls, x0, x1, n=600, style=None):
    """Graph of fn on [x0, x1], cut where it leaves the vertical range of the panel (crossing points included)."""
    lo, hi = f.yr
    xs = np.linspace(x0, x1, n + 1)
    ys = [fn(x) for x in xs]
    pts = []
    for i, (x, y) in enumerate(zip(xs, ys)):
        inside = lo <= y <= hi
        if i > 0:
            xp, yp = xs[i - 1], ys[i - 1]
            pin = lo <= yp <= hi
            if pin != inside:
                lim = hi if (y > hi or yp > hi) else lo
                t = (lim - yp) / (y - yp)
                pts.append((xp + t * (x - xp), lim))
                if not inside:
                    pts.append(None)
        if inside:
            pts.append((x, y))
    f.path(pts, cls, extra=f' style="{style}"' if style else "")


def dot(f, x, y, cls="fk", r=4):
    f.circle(x, y, r, cls)


def open_dot(f, x, y, k="k", r=4.2):
    f.c.add(f'<circle cx="{f.X(x):.1f}" cy="{f.Y(y):.1f}" r="{r}" class="fs ln c{k} thin"/>')


PENTA = [(0, 0), (5, 0), (2, 3), (1, 2.5), (0, 1)]  # Ex. 4.2.1, counter-clockwise
CONS = [((-3, 2), 2, "−3x₁ + 2x₂ = 2"), ((-1, 2), 4, "−x₁ + 2x₂ = 4"), ((1, 1), 5, "x₁ + x₂ = 5")]


def draw_penta(f, box, labels=True, fill="a1", stroke="ln c1 thin"):
    for (a, r, lab) in CONS:
        seg = line_in_box(a[0], a[1], r, box)
        f.line(seg[0][0], seg[0][1], seg[1][0], seg[1][1], "ln cm hair")
    f.path(PENTA, fill, close=True)
    f.path(PENTA, stroke, close=True)


# ---------------------------------------------------------------------------------------------- 1. rank
def fig_rang():
    """Solutions of x1 + 2 x2 = 4: a particular solution plus the kernel; with x >= 0, a segment."""
    c = Canvas("rang", 640, 330, "Les solutions de x1 + 2 x2 = 4 forment une droite parallèle au noyau", sub=SUB)
    box = (-3.6, 5.6, -2.0, 3.2)
    f = Fig(c, (40, 14, 560, 560 * 5.2 / 9.2), box[:2], box[2:])
    grid(f, range(-3, 6), range(-2, 4))
    f.line(box[0], 0, box[1], 0, "ax")
    f.line(0, box[2], 0, box[3], "ax")
    f.text(box[1], 0, "x₁", "tx-s", "end", dx=-2, dy=14)
    f.text(0, box[3], "x₂", "tx-s", "start", dx=5, dy=12)
    # kernel: t (2, -1)
    f.line(-3.6, 1.8, 3.6, -1.8, "ln cm dash")
    f.text(-3.3, 1.65, "Ker A = {x : x₁ + 2x₂ = 0}", "tx-s", "start", dy=-8)
    # solution line x1 + 2 x2 = 4
    seg = line_in_box(1, 2, 4, box)
    f.line(seg[0][0], seg[0][1], seg[1][0], seg[1][1], "ln ck thin")
    f.text(3.25, -1.05, "{x : Ax = b} = x₀ + Ker A", "tx-s", "start")
    # admissible segment
    f.line(0, 2, 4, 0, "ln c1")
    rich(c, f.X(2.25) + 4, f.Y(1.0) - 8, [("X", ""), ("ad", "sub"), (" = {Ax = b, x ≥ 0}", "")], "tx-b t1")
    # x0 and the translation of the kernel
    farrow(f, 0, 0, 3.92, 0.04, "m")
    dot(f, 4, 0, "fk")
    f.text(4, 0, "x₀ = (4, 0)", "tx-s", "start", dx=8, dy=-8)
    dot(f, 0, 2, "fk")
    f.text(0, 2, "(0, 2)", "tx-s", "end", dx=-6, dy=14)   # below-left: clear of the axis and of the line
    # kernel direction drawn at x0
    farrow(f, 4, 0, 2.08, 0.96, "m", "ln cm thin")
    f.text(3.1, 0.45, "+ t(−2, 1)", "tx-s", "start", dx=0, dy=-12)   # above the line, clear of it
    # row of A, orthogonal to the kernel
    farrow(f, 0, 0, 0.96, 1.92, "5", "ln c5 thin")
    f.text(1.0, 2.0, "a = (1, 2), orthogonal au noyau", "tx-s t5", "start", dx=4, dy=4)
    c.save()


# ---------------------------------------------------------------------------------------------- 2. coordinates
def cone_panel(c, box_px, a1, a2, b, coeffs, names, inside, title):
    box = (-0.6, 8.6, -1.6, 5.8)
    f = Fig(c, box_px, box[:2], box[2:])
    grid(f, range(0, 9), range(-1, 6))
    f.line(box[0], 0, box[1], 0, "ax")
    f.line(0, box[2], 0, box[3], "ax")
    R = 40
    cone = clip_poly([(0, 0), (R * a1[0], R * a1[1]), (R * (a1[0] + a2[0]), R * (a1[1] + a2[1])), (R * a2[0], R * a2[1])], box)
    f.path(cone, "a1", close=True)
    # coordinate path: k1 a1 then k2 a2
    k1, k2 = coeffs
    mid = (k1 * a1[0], k1 * a1[1])
    f.line(0, 0, mid[0], mid[1], "ln c3 thin dash" if inside else "ln c6 thin dash")
    f.line(mid[0], mid[1], b[0], b[1], "ln c3 thin dash" if inside else "ln c6 thin dash")
    farrow(f, 0, 0, a1[0], a1[1], "k", "ln ck thin")
    farrow(f, 0, 0, a2[0], a2[1], "k", "ln ck thin")
    farrow(f, 0, 0, b[0] * 0.985, b[1] * 0.985, "3" if inside else "6", "ln c3" if inside else "ln c6")
    f.text(a1[0], a1[1], names[0], "tx-b", "start", dx=4, dy=14)
    f.text(a2[0], a2[1], names[1], "tx-b", "end" if a2[1] > 0 else "start", dx=-4 if a2[1] > 0 else 2, dy=0 if a2[1] > 0 else 16)
    dot(f, mid[0], mid[1], "fm", 3)
    f.text(b[0], b[1], "b = (5, 5)", "tx-b t3" if inside else "tx-b t6", "start", dx=6, dy=4)
    c.text(box_px[0] + box_px[2] / 2, box_px[1] - 6, title, "tx-b", "middle")
    return f


def fig_coordonnees():
    c = Canvas("coordonnees", 680, 330, "Les coordonnées de b dans deux bases : positives, b est dans le cône ; une négative, il n'y est pas", sub=SUB)
    w = 310
    h = w * 7.4 / 9.2
    f1 = cone_panel(c, (20, 30, w, h), (2, 1), (1, 3), (5, 5), (2, 1), ("a₁", "a₂"), True, "base (a₁, a₂) : b = 2a₁ + 1a₂")
    f1.text(4, 2, "2a₁", "tx-s", "start", dx=6, dy=12)
    c.text(20 + w / 2, 30 + h + 18, "coordonnées (2, 1) ≥ 0 : b est dans le cône (bleu)", "tx-s t3", "middle")
    f2 = cone_panel(c, (355, 30, w, h), (2, 1), (3, -1), (5, 5), (4, -1), ("a₁", "a₃"), False, "base (a₁, a₃) : b = 4a₁ − 1a₃")
    f2.text(8, 4, "4a₁", "tx-s", "end", dx=-2, dy=16)
    c.text(355 + w / 2, 30 + h + 18, "coordonnée −1 < 0 : b est hors du cône (bleu)", "tx-s t6", "middle")
    c.save()


# ---------------------------------------------------------------------------------------------- 3. determinant
def fig_determinant():
    c = Canvas("determinant", 660, 270, "Le déterminant de deux vecteurs du plan est l'aire signée du parallélogramme qu'ils engendrent", sub=SUB)
    box = (-0.5, 4.6, -0.5, 4.5)
    w = 230
    f = Fig(c, (40, 22, w, w * 5.0 / 5.1), box[:2], box[2:])
    grid(f, range(0, 5), range(0, 5))
    f.line(box[0], 0, box[1], 0, "ax")
    f.line(0, box[2], 0, box[3], "ax")
    par = [(0, 0), (2, 1), (3, 4), (1, 3)]
    f.path(par, "a1", close=True)
    f.path(par, "ln c1 thin", close=True)
    f.path([(0, 0), (1, 0), (1, 1), (0, 1)], "am", close=True)
    farrow(f, 0, 0, 2, 1, "k", "ln ck thin")
    farrow(f, 0, 0, 1, 3, "k", "ln ck thin")
    for x in range(0, 5):
        for y in range(0, 5):
            dot(f, x, y, "fm", 2)
    bg_text(c, f.X(2) + 6, f.Y(1) + 12, "a₁ = (2, 1)", "tx-s")
    bg_text(c, f.X(1) - 6, f.Y(3) - 4, "a₂ = (1, 3)", "tx-s", "end")
    f.text(0.5, 0.5, "1", "tx-s", "middle", dy=4)
    # text column
    x0 = 300
    lines = [("det(a₁, a₂) = 2·3 − 1·1 = 5", "tx-b"),
             ("aire du parallélogramme = 5 (bleu)", "tx-s t1"),
             ("= 5 fois l'aire du carré unité (gris) ;", "tx-s"),
             ("det(a₂, a₁) = −5 : l'ordre des colonnes", "tx-s"),
             ("change le signe, pas l'aire.", "tx-s"),
             ("", ""),
             ("Colonnes liées : a₁ = (2, 1), a₂′ = (4, 2) = 2a₁", "tx-b"),
             ("det(a₁, a₂′) = 2·2 − 4·1 = 0 : le parallélogramme", "tx-s"),
             ("est aplati sur une droite (trait rose).", "tx-s t6")]
    y = 40
    for s, cls in lines:
        if s:
            c.text(x0, y, s, cls, "start")
        y += 19
    # small flat parallelogram
    g = Fig(c, (300, 210, 180, 45), (-0.3, 6.3), (-0.2, 3.2))
    farrow(g, 0, 0, 2, 1, "k", "ln ck thin")
    g.line(0, 0, 6, 3, "ln c6")
    farrow(g, 0, 0, 4, 2, "6", "ln c6 thin")
    g.text(4, 2, "a₂′", "tx-s t6", "start", dx=6, dy=10)
    g.text(2, 1, "a₁", "tx-s", "end", dx=-4, dy=-4)
    c.save()


# ---------------------------------------------------------------------------------------------- 4. convex sets
def fig_convexes():
    c = Canvas("convexes", 680, 220, "Un ensemble convexe, un ensemble non convexe, et les points entiers d'un polygone", sub=SUB)
    box = (-0.4, 5.4, -0.4, 3.4)
    w = 205
    h = w * 3.8 / 5.8
    titles = ["convexe : le segment reste dedans", "non convexe : le segment sort", "points entiers : pas convexe"]
    for k in range(3):
        x0 = 15 + k * 225
        f = Fig(c, (x0, 30, w, h), box[:2], box[2:])
        c.text(x0 + w / 2, 20, titles[k], "tx-b", "middle")
        if k == 0:
            f.path(PENTA, "a1", close=True)
            f.path(PENTA, "ln c1 thin", close=True)
            y, z = (0.4, 0.6), (3.8, 0.8)
            f.line(*y, *z, "ln c3")
            dot(f, *y, "f3"); dot(f, *z, "f3")
            y2, z2 = (0.3, 1.1), (1.9, 2.6)
            f.line(*y2, *z2, "ln c3")
            dot(f, *y2, "f3"); dot(f, *z2, "f3")
            xad(c, f.X(3.2), f.Y(0.25))
        elif k == 1:
            L = [(0, 0), (5, 0), (5, 1), (1.5, 1), (1.5, 3), (0, 3)]
            f.path(L, "am", close=True)
            f.path(L, "ln cm thin", close=True)
            y, z = (4.5, 0.5), (0.75, 2.6)
            f.line(*y, *z, "ln c3")
            # part outside: between the crossings with y = 1 and x = 1.5
            t1 = (1 - y[1]) / (z[1] - y[1])
            t2 = (1.5 - y[0]) / (z[0] - y[0])
            p1 = (y[0] + t1 * (z[0] - y[0]), 1)
            p2 = (1.5, y[1] + t2 * (z[1] - y[1]))
            f.line(*p1, *p2, "ln c6")
            dot(f, *y, "f3"); dot(f, *z, "f3")
            f.text((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2, "dehors", "tx-s t6", "start", dx=8, dy=-2)
        else:
            f.path(PENTA, "ln c1 hair dash", close=True)
            pts = [(x, y) for x in range(0, 6) for y in range(0, 4)
                   if all(a[0] * x + a[1] * y <= r + 1e-9 for (a, r, _) in CONS)]
            for p in pts:
                dot(f, *p, "f4", 3.6)
            y, z = (0, 1), (1, 2)
            f.line(*y, *z, "ln cm thin dash")
            open_dot(f, 0.5, 1.5, "6", 4.2)
            c.text(x0 + w / 2, 30 + h + 16, "le milieu de (0, 1) et (1, 2) n'est pas entier", "tx-s t6", "middle")
    c.save()


# ---------------------------------------------------------------------------------------------- 5. polyhedron
def fig_polyedre():
    c = Canvas("polyedre", 660, 360, "Le polygone de l'exercice 4.2.1 : intersection de cinq demi-plans, cinq sommets", sub=SUB)
    box = (-1.2, 6.4, -0.8, 4.3)
    w = 470
    f = Fig(c, (40, 12, w, w * 5.1 / 7.6), box[:2], box[2:])
    grid(f, range(-1, 7), range(0, 5))
    f.line(box[0], 0, box[1], 0, "ax")
    f.line(0, box[2], 0, box[3], "ax")
    f.text(box[1], 0, "x₁", "tx-s", "end", dx=-2, dy=14)
    f.text(0, box[3], "x₂", "tx-s", "start", dx=5, dy=12)
    draw_penta(f, box)
    # constraint labels
    bg_text(c, f.X(-1.15), f.Y(2.2), "−3x₁ + 2x₂ ≤ 2", "tx-s")
    f.text(2.6, 3.5, "−x₁ + 2x₂ ≤ 4", "tx-s", "start", dy=-4)
    f.text(4.3, 0.9, "x₁ + x₂ ≤ 5", "tx-s", "start", dx=6)
    f.text(0, -0.5, "x₂ ≥ 0", "tx-s", "start", dx=40, dy=0)
    f.text(-0.1, 3.9, "x₁ ≥ 0", "tx-s", "end", dx=-4)
    # inward ticks
    for (a, r, _), p in zip(CONS, [(0.5, 1.75), (1.5, 2.75), (3.5, 1.5)]):
        n = np.array(a, float)
        n = n / np.linalg.norm(n)
        q = (p[0] - 0.35 * n[0], p[1] - 0.35 * n[1])
        farrow(f, p[0], p[1], q[0], q[1], "m", "ln cm hair")
    # vertices
    labels = {(0, 0): ("(0, 0)", "end", -6, 14), (5, 0): ("(5, 0)", "start", 4, 14), (2, 3): ("(2, 3)", "start", 6, -4),
              (1, 2.5): ("(1, 5/2)", "end", -6, -6), (0, 1): ("(0, 1)", "end", -6, 4)}
    for v in PENTA:
        dot(f, *v, "fk", 4.2)
        s, an, dx, dy = labels[v]
        f.text(*v, s, "tx-b", an, dx=dx, dy=dy)
    # a point on an edge that is not a vertex
    m = (1.5, 2.75)
    open_dot(f, *m, "6", 4.2)
    xad(c, f.X(2.2), f.Y(1.4), "tx-b t1", "middle")
    # legend column
    x0 = 525
    for i, (s, cls) in enumerate([("Cinq sommets", "tx-b"), ("(gros points).", "tx-s"), ("", ""),
                                  ("Le point rose", "tx-s t6"), ("m = (3/2, 11/4)", "tx-s t6"), ("est le milieu de", "tx-s t6"),
                                  ("(1, 5/2) et (2, 3) :", "tx-s t6"), ("ce n'est pas", "tx-s t6"), ("un sommet.", "tx-s t6"),
                                  ("", ""), ("Petites flèches :", "tx-s"), ("côté admissible.", "tx-s")]):
        if s:
            c.text(x0, 40 + 17 * i, s, cls, "start")
    c.save()


# ---------------------------------------------------------------------------------------------- 6. functions
def fig_fonctions():
    c = Canvas("fonctions", 660, 215, "Minimum d'une fonction linéaire, concave ou convexe sur un intervalle", sub=SUB)
    fs = [("linéaire : f(x) = (1 − x)/2", lambda x: (1 - x) / 2, [1.0], None),
          ("concave : f(x) = 1 − x²", lambda x: 1 - x * x, [-1.0, 1.0], (-1, 1)),
          ("convexe : f(x) = x²", lambda x: x * x, [0.0], (-1, 1))]
    notes = ["min en un sommet (x = 1)", "min aux deux sommets ±1", "min à l'intérieur (x = 0)"]
    for k, (title, fn, mins, chord) in enumerate(fs):
        x0 = 30 + k * 215
        f = Fig(c, (x0, 34, 180, 130), (-1.25, 1.25), (-0.25, 1.25))
        c.text(x0 + 90, 18, title, "tx-b", "middle")
        f.line(-1.25, 0, 1.25, 0, "ax")
        f.line(0, -0.25, 0, 1.25, "gr")
        f.line(-1, 0, 1, 0, "ln c1")  # the polytope [-1, 1]
        f.fn(fn, "ln c2", -1, 1)
        if chord:
            f.line(-1, fn(-1), 1, fn(1), "ln cm thin dash")
        for v in (-1, 1):
            dot(f, v, 0, "fk", 3.5)
            f.line(v, 0, v, fn(v), "ln cm hair dot")
            dot(f, v, fn(v), "f2", 3.5)
        for m in mins:
            dot(f, m, fn(m), "f3", 5)
        f.text(-1, 0, "−1", "tx-s", "middle", dy=14)
        f.text(1, 0, "1", "tx-s", "middle", dy=14)
        c.text(x0 + 90, 200, notes[k], "tx-s t3", "middle")
    c.save()


# ---------------------------------------------------------------------------------------------- 7. existence
def fig_existence():
    c = Canvas("existence", 680, 210, "Quatre fonctions : trois sans minimum, chacune parce qu'une hypothèse du théorème 2.2.1 manque", sub=SUB)
    panels = [("K = ]0, 1] pas fermé", "J(x) = x : inf 0, non atteint"),
              ("J pas continue", "J(0) = 1, J(x) = x sinon"),
              ("pas infinie à l'infini", "J(x) = e⁻ˣ sur [0, +∞["),
              ("toutes les hypothèses", "J(x) = (x − 1)² + ½ sur ℝ")]
    for k, (t1, t2) in enumerate(panels):
        x0 = 15 + k * 168
        if k < 2:
            f = Fig(c, (x0 + 10, 40, 130, 120), (-0.3, 1.3), (-0.25, 1.25))
        elif k == 2:
            f = Fig(c, (x0 + 10, 40, 130, 120), (-0.4, 5.2), (-0.15, 1.15))
        else:
            f = Fig(c, (x0 + 10, 40, 130, 120), (-1.0, 3.0), (-0.3, 3.0))
        c.text(x0 + 75, 18, t1, "tx-b", "middle")
        c.text(x0 + 75, 190, t2, "tx-s", "middle")
        f.line(f.xr[0], 0, f.xr[1], 0, "ax")
        f.line(0, f.yr[0], 0, f.yr[1], "ax")
        if k == 0:
            f.line(0, 0, 1, 0, "ln c1")
            open_dot(f, 0, 0, "1")
            dot(f, 1, 0, "f1", 3.5)
            f.fn(lambda x: x, "ln c2", 0.02, 1)
            open_dot(f, 0, 0, "2", 3.8)
            f.text(1, 1, "J", "tx-s t2", "end", dx=-6)
        elif k == 1:
            f.line(0, 0, 1, 0, "ln c1")
            dot(f, 0, 0, "f1", 3.5)
            dot(f, 1, 0, "f1", 3.5)
            f.fn(lambda x: x, "ln c2", 0.03, 1)
            open_dot(f, 0, 0, "2", 3.8)
            dot(f, 0, 1, "f2", 4)
            f.text(0, 1, "J(0) = 1", "tx-s t2", "start", dx=7, dy=4)
        elif k == 2:
            f.line(0, 0, 5.2, 0, "ln c1")
            f.fn(lambda x: math.exp(-x), "ln c2", 0, 5.2)
            f.line(0, 0, 5.2, 0, "ln cm thin dash")
            f.text(4.8, 0.12, "→ 0", "tx-s", "end", dy=-4)
        else:
            f.line(-1, 0, 3, 0, "ln c1")
            fn_clip(f, lambda x: (x - 1) ** 2 + 0.5, "ln c2", -1, 3)
            dot(f, 1, 0.5, "f3", 5)
            f.text(1, 0.5, "min", "tx-s t3", "middle", dy=-9)
    c.save()


# ---------------------------------------------------------------------------------------------- 8. closed sets
def fig_fermes():
    c = Canvas("fermes", 660, 230, "Un ensemble fermé dont la projection n'est pas fermée", sub=SUB)
    # left: ]0,1] and the sequence 1/k
    f = Fig(c, (30, 70, 230, 60), (-0.15, 1.15), (-0.5, 0.5))
    c.text(145, 30, "K = ]0, 1] : xₖ = 1/k ∈ K", "tx-b", "middle")
    c.text(145, 48, "mais lim xₖ = 0 ∉ K : K n'est pas fermé", "tx-s", "middle")
    f.line(-0.15, 0, 1.15, 0, "ax")
    f.line(0, 0, 1, 0, "ln c1")
    open_dot(f, 0, 0, "1", 4.5)
    dot(f, 1, 0, "f1", 4)
    for k in range(1, 9):
        dot(f, 1 / k, 0, "f2", 3)
    for k in (1, 2, 3):
        f.text(1 / k, 0, f"1/{k}" if k > 1 else "1", "tx-s", "middle", dy=18)
    f.text(0, 0, "0", "tx-s", "middle", dy=18)
    # right: H = {x > 0, x y >= 1} and its projection
    g = Fig(c, (330, 20, 300, 180), (-0.4, 4.2), (-0.6, 4.2))
    g.line(-0.4, 0, 4.2, 0, "ax")
    g.line(0, -0.6, 0, 4.2, "ax")
    xs = np.linspace(1 / 4.2, 4.2, 200)
    region = [(x, 1 / x) for x in xs] + [(4.2, 4.2), (1 / 4.2, 4.2)]
    g.path(region, "a1", close=True)
    g.path([(x, 1 / x) for x in xs], "ln c1 thin")
    g.text(2.2, 2.6, "H = {x > 0, xy ≥ 1}", "tx-s t1", "start")
    g.text(2.2, 2.6, "fermé", "tx-s t1", "start", dy=14)
    g.line(0, -0.3, 4.2, -0.3, "ln c5")
    open_dot(g, 0, -0.3, "5", 4.2)
    g.text(1.4, -0.3, "projection ]0, +∞[ : pas fermée", "tx-s t5", "start", dy=16)
    for x in (1.0, 0.5, 0.3):
        dot(g, x, 1 / x, "f2", 3)
        g.line(x, 1 / x, x, -0.3, "ln cm hair dot")
    c.save()


# ---------------------------------------------------------------------------------------------- 9. Farkas
def fig_farkas():
    c = Canvas("farkas", 680, 352, "Lemme de Farkas : b est dans le cône des colonnes, ou un vecteur w sépare b du cône", sub=SUB)
    box = (-1.6, 6.2, -2.4, 5.8)
    w = 300
    h = w * 8.2 / 7.8
    a1, a2 = (2, 1), (1, 3)
    for k in range(2):
        x0 = 20 + k * 340
        f = Fig(c, (x0, 8, w, h), box[:2], box[2:])
        grid(f, range(-1, 7), range(-2, 6))
        f.line(box[0], 0, box[1], 0, "ax")
        f.line(0, box[2], 0, box[3], "ax")
        R = 40
        cone = clip_poly([(0, 0), (R * 2, R * 1), (R * 3, R * 4), (R * 1, R * 3)], box)
        f.path(cone, "a1", close=True)
        farrow(f, 0, 0, *a1, "k", "ln ck thin")
        farrow(f, 0, 0, *a2, "k", "ln ck thin")
        f.text(*a1, "a₁", "tx-b", "start", dx=2, dy=-8 if k else 14)
        f.text(*a2, "a₂", "tx-b", "end", dx=-4, dy=0)
        f.text(1.4, 3.75, "cône(a₁, a₂)", "tx-s t1", "start")
        if k == 0:
            f.line(0, 0, 4, 2, "ln c3 thin dash")
            f.line(4, 2, 5, 5, "ln c3 thin dash")
            farrow(f, 0, 0, 4.93, 4.93, "3", "ln c3")
            f.text(5, 5, "b = (5, 5)", "tx-b t3", "end", dx=-10, dy=-2)
            f.text(4, 2, "2a₁", "tx-s", "start", dx=6, dy=10)
            c.text(x0 + w / 2, h + 26, "(I) : b = Ax avec x = (2, 1) ≥ 0", "tx-b t3", "middle")
        else:
            # the line w.y = 0 with w = (1, -2): y2 = y1 / 2
            seg = line_in_box(1, -2, 0, box)
            f.line(seg[0][0], seg[0][1], seg[1][0], seg[1][1], "ln c5 thin dash")
            half = clip_poly([(-40, -20), (40, 20), (40, 60), (-40, 60)], box)
            f.path(half, "a5", close=True)
            farrow(f, 0, 0, 1, -2, "5", "ln c5")
            f.text(1, -2, "w = (1, −2)", "tx-b t5", "start", dx=6, dy=4)
            farrow(f, 0, 0, 3.94, 0.985, "6", "ln c6")
            f.text(4, 1, "b′ = (4, 1)", "tx-b t6", "start", dx=-2, dy=16)
            f.text(-1.4, 3.6, "{y : w·y ≤ 0}", "tx-s t5", "start")
            c.text(x0 + w / 2, h + 26, "(II) : Aᵀw = (0, −5) ≤ 0 et b′·w = 2 > 0", "tx-b t6", "middle")
    c.save()


# ---------------------------------------------------------------------------------------------- 10. separation
def fig_separation():
    c = Canvas("separation", 640, 320, "Projection d'un point sur un convexe fermé et hyperplan séparateur", sub=SUB)
    box = (-0.6, 6.2, -0.6, 5.0)
    w = 400
    f = Fig(c, (30, 10, w, w * 5.6 / 6.8), box[:2], box[2:])
    grid(f, range(0, 7), range(0, 6))
    f.line(box[0], 0, box[1], 0, "ax")
    f.line(0, box[2], 0, box[3], "ax")
    f.path(PENTA, "a1", close=True)
    f.path(PENTA, "ln c1 thin", close=True)
    f.text(1.6, 1.0, "K", "tx-b t1", "middle")
    seg = line_in_box(1, 1, 6.5, box)
    f.line(seg[0][0], seg[0][1], seg[1][0], seg[1][1], "ln c5 thin dash")
    f.text(6.0, 0.5, "y₁ + y₂ = 13/2", "tx-s t5", "end", dx=-8, dy=4)
    f.line(4, 4, 2.5, 2.5, "ln cm thin dash")
    dot(f, 4, 4, "f2", 4.5)
    f.text(4, 4, "x₀ = (4, 4)", "tx-b t2", "start", dx=8, dy=4)
    dot(f, 2.5, 2.5, "f3", 4.5)
    rich(c, f.X(2.5) - 10, f.Y(2.5) + 20, [("x", ""), ("K", "sub"), (" = (5/2, 5/2)", "")], "tx-b t3", "end")
    # right angle mark at xK
    u = np.array([1, 1]) / math.sqrt(2) * 0.22
    v = np.array([1, -1]) / math.sqrt(2) * 0.22
    p0 = np.array([2.5, 2.5])
    f.path([tuple(p0 + v), tuple(p0 + v + u), tuple(p0 + u)], "ln cm hair")
    x0 = 455
    lines = [("Projection (Th. 5.1.3) :", "tx-b"), ("le point de K le plus proche", "tx-s"), ("de x₀ ; ici sur le côté", "tx-s"),
             ("x₁ + x₂ = 5, à distance 3/√2.", "tx-s"), ("", ""), ("Séparation (Th. 5.1.12) :", "tx-b"),
             ("", ""), ("= −3/2 (y₁ + y₂),", "tx-s t5"), ("α = −39/4.", "tx-s t5"),
             ("L(x₀) = −12 < α", "tx-s"), ("< −15/2 ≤ L(x), x ∈ K.", "tx-s")]
    for i, (s, cls) in enumerate(lines):
        if s:
            c.text(x0, 40 + 19 * i, s, cls, "start")
    rich(c, x0, 40 + 19 * 6, [("L(y) = (x", ""), ("K", "sub"), (" − x₀)·y", "")], "tx-s t5")
    c.save()


# ---------------------------------------------------------------------------------------------- 11. KKT
def fig_kkt():
    c = Canvas("kkt", 680, 360, "Conditions de KKT sur l'exercice 4.2.1 : à l'optimum, c est dans le cône des normales des contraintes actives", sub=SUB)
    box = (-2.6, 6.0, -0.6, 5.4)
    w = 470
    f = Fig(c, (20, 10, w, w * 6.0 / 8.6), box[:2], box[2:])
    grid(f, range(-2, 7), range(0, 6))
    f.line(box[0], 0, box[1], 0, "ax")
    f.line(0, box[2], 0, box[3], "ax")
    draw_penta(f, box)
    # cost level line through (2, 3): x1 + 2 x2 = 8
    seg = line_in_box(1, 2, 8, box)
    f.line(seg[0][0], seg[0][1], seg[1][0], seg[1][1], "ln c2 thin dash")
    f.text(5.9, 1.05, "x₁ + 2x₂ = 8", "tx-s t2", "end", dy=-6)

    def normcone(p, n1, n2, scale):
        u1 = np.array(n1, float) / np.linalg.norm(n1) * scale
        u2 = np.array(n2, float) / np.linalg.norm(n2) * scale
        f.path([p, (p[0] + u1[0], p[1] + u1[1]), (p[0] + u1[0] + u2[0], p[1] + u1[1] + u2[1]), (p[0] + u2[0], p[1] + u2[1])], "a5", close=True)
        farrow(f, p[0], p[1], p[0] + u1[0], p[1] + u1[1], "5", "ln c5 thin")
        farrow(f, p[0], p[1], p[0] + u2[0], p[1] + u2[1], "5", "ln c5 thin")
        return u1, u2
    cdir = np.array([1, 2]) / math.sqrt(5) * 1.45
    # optimum (2, 3)
    u1, u2 = normcone((2, 3), (-1, 2), (1, 1), 1.1)
    farrow(f, 2, 3, 2 + cdir[0], 3 + cdir[1], "2", "ln c2")
    f.text(2 + cdir[0], 3 + cdir[1], "c", "tx-b t2", "start", dx=6, dy=4)
    f.text(2 + u1[0], 3 + u1[1], "(−1, 2)", "tx-s t5", "end", dx=-4, dy=-2)
    f.text(2 + u2[0], 3 + u2[1], "(1, 1)", "tx-s t5", "start", dx=6, dy=6)
    dot(f, 2, 3, "f3", 5)
    # non-optimal vertex (1, 5/2)
    v1, v2 = normcone((1, 2.5), (-3, 2), (-1, 2), 1.1)
    farrow(f, 1, 2.5, 1 + cdir[0], 2.5 + cdir[1], "2", "ln c2")
    f.text(1 + v1[0], 2.5 + v1[1], "(−3, 2)", "tx-s t5", "end", dx=-4, dy=4)
    dot(f, 1, 2.5, "fm", 4.5)
    xad(c, f.X(1.6), f.Y(0.9), "tx-b t1", "middle")
    x0 = 505
    lines = [("max x₁ + 2x₂, c = (1, 2)", "tx-b t2"), ("", ""),
             ("En (2, 3) (vert) :", "tx-b t3"), ("c = ⅓(−1, 2) + 4/3(1, 1)", "tx-s"), ("multiplicateurs ⅓, 4/3 ≥ 0 :", "tx-s"),
             ("c est dans le cône violet,", "tx-s"), ("KKT vérifiées : optimum.", "tx-s t3"), ("", ""),
             ("En (1, 5/2) (gris) :", "tx-b"), ("c = −1·(−3, 2) + 2·(−1, 2)", "tx-s"), ("un multiplicateur < 0 :", "tx-s"),
             ("c sort du cône violet,", "tx-s"), ("pas optimal.", "tx-s t6")]
    for i, (s, cls) in enumerate(lines):
        if s:
            c.text(x0, 30 + 19 * i, s, cls, "start")
    c.save()


# ---------------------------------------------------------------------------------------------- 12. saddle point
def fig_selle():
    c = Canvas("selle", 680, 300, "Le Lagrangien de min v² sous 1 − v ≤ 0 a un point-selle en (1, 2) ; fonctions primale et duale", sub=SUB)
    f = Fig(c, (40, 22, 290, 240), (-0.5, 2.5), (0, 4))
    for v in range(0, 3):
        f.line(v, 0, v, 4, "gr")
        f.text(v, 0, str(v), "tx-s", "middle", dy=14)
    for q in range(0, 5):
        f.line(-0.5, q, 2.5, q, "gr")
        f.text(-0.5, q, str(q), "tx-s", "end", dx=-5, dy=4)
    f.line(-0.5, 0, 2.5, 0, "ax")
    f.text(2.5, 0, "v", "tx-i", "end", dx=-2, dy=-6)
    f.text(-0.5, 4, "q", "tx-i", "start", dx=6, dy=12)
    # level sets L(v, q) = v^2 + q (1 - v) = lev: q = (lev - v^2) / (1 - v)
    for lev in [0, 0.5, 1.5, 2, 2.5, 3, 4]:
        for side in (0, 1):
            vs = np.linspace(-0.5, 0.995, 300) if side == 0 else np.linspace(1.005, 2.5, 300)
            pts = []
            for v in vs:
                q = (lev - v * v) / (1 - v)
                pts.append((v, q) if 0 <= q <= 4 else None)
            f.path(pts, "ln cm hair")
    f.line(1, 0, 1, 4, "ln c3 thin")
    f.line(-0.5, 0.5, 2.5, 3.5, "ln c3 thin")
    dot(f, 1, 2, "f3", 5)
    f.text(1, 2, "(u, p) = (1, 2)", "tx-b t3", "start", dx=8, dy=16)
    f.text(2.45, 3.5, "L = 1", "tx-s t3", "end", dy=16)
    c.text(185, 14, "lignes de niveau de L(v, q) = v² + q(1 − v)", "tx-b", "middle")
    # right: primal and dual functions
    g = Fig(c, (410, 22, 250, 240), (-0.2, 4.2), (-0.6, 4.5))
    for t in range(0, 5):
        g.line(t, -0.6, t, 4.5, "gr")
        g.text(t, -0.6, str(t), "tx-s", "middle", dy=14)
    for y in range(0, 5):
        g.line(-0.2, y, 4.2, y, "gr")
        g.text(-0.2, y, str(y), "tx-s", "end", dx=-5, dy=4)
    g.line(-0.2, 0, 4.2, 0, "ax")
    g.fn(lambda v: v * v, "ln c1", 1, 2.12)
    g.fn(lambda q: q - q * q / 4, "ln c5", 0, 4.2)
    g.line(1, 1, 1, 4.5, "ln c1 hair dot")
    g.line(1, 1, 4.2, 1, "ln cm hair dash")
    dot(g, 1, 1, "f1", 4.5)
    dot(g, 2, 1, "f5", 4.5)
    g.text(2.12, 4.4, "𝒥(v) = v² si v ≥ 1", "tx-s t1", "start", dx=4, dy=8)
    g.text(0.95, 3.3, "+∞ si v < 1", "tx-s t1", "end")
    g.text(3.1, 2.0, "𝒢(q) =", "tx-s t5", "start")
    g.text(3.1, 2.0, "q − q²/4", "tx-s t5", "start", dy=14)
    g.text(1, 1, "min 𝒥 = 1", "tx-s t1", "end", dx=-6, dy=16)
    g.text(2, 1, "max 𝒢 = 1", "tx-s t5", "start", dx=4, dy=-8)
    c.text(535, 14, "primal 𝒥 (en v) et dual 𝒢 (en q)", "tx-b", "middle")
    c.save()


# ---------------------------------------------------------------------------------------------- 13. Newton
def fig_newton():
    c = Canvas("newton", 680, 280, "La méthode de Newton sur x² − 2 = 0 : tangentes, et erreur qui chute de façon quadratique", sub=SUB)
    f = Fig(c, (45, 25, 280, 210), (0.9, 2.1), (-1.3, 2.3))
    for x in (1, 1.5, 2):
        f.line(x, -1.3, x, 2.3, "gr")
        f.text(x, -1.3, f"{x:g}".replace(".", ","), "tx-s", "middle", dy=14)
    for y in (-1, 0, 1, 2):
        f.line(0.9, y, 2.1, y, "gr")
        f.text(0.9, y, f"{y:g}".replace("-", "−"), "tx-s", "end", dx=-5, dy=4)
    f.line(0.9, 0, 2.1, 0, "ax")
    F_ = lambda x: x * x - 2
    f.fn(F_, "ln c2", 0.9, 2.1)
    xs = [1.0, 1.5, 17 / 12]
    for k, x in enumerate(xs[:2]):
        xn = xs[k + 1]
        f.line(x, 0, x, F_(x), "ln cm hair dot")
        f.line(x, F_(x), xn, 0, "ln c3 thin")
        dot(f, x, F_(x), "f2", 3.5)
    for k, x in enumerate(xs):
        dot(f, x, 0, "f3", 4)
    f.text(1.0, 0, "x₀ = 1", "tx-s t3", "start", dx=4, dy=-8)
    f.text(1.5, 0, "x₁ = 3/2", "tx-s t3", "start", dx=6, dy=16)
    f.text(17 / 12, 0, "x₂ = 17/12", "tx-s t3", "end", dx=-4, dy=16)
    f.text(2.05, F_(2.05), "F(x) = x² − 2", "tx-s t2", "end", dx=-6, dy=4)
    c.text(185, 16, "tangente en xₙ, coupée avec l'axe : xₙ₊₁", "tx-b", "middle")
    # right: errors, log scale
    g = Fig(c, (410, 25, 250, 210), (0, 5), (-13, 0.5))
    for n in range(0, 6):
        g.line(n, -13, n, 0.5, "gr")
        g.text(n, -13, str(n), "tx-s", "middle", dy=14)
    for e in (0, -3, -6, -9, -12):
        g.line(0, e, 5, e, "gr")
        g.text(0, e, f"10{sup(e)}", "tx-s", "end", dx=-5, dy=4)
    g.line(0, -13, 5, -13, "ax")
    g.text(5, -13, "n", "tx-i", "end", dx=-2, dy=-6)
    newton = [1.0, 1.5, 17 / 12, 577 / 408, 665857 / 470832]
    en = [math.log10(abs(x - math.sqrt(2))) for x in newton]
    dbl = [math.log10(0.5 ** n) for n in range(6)]
    lo, hi = 1.0, 2.0
    bis = []
    for n in range(6):
        mid = (lo + hi) / 2
        bis.append(math.log10(abs(mid - math.sqrt(2))))
        if mid * mid > 2:
            hi = mid
        else:
            lo = mid
    g.path(list(zip(range(5), en)), "ln c3")
    for n, e in enumerate(en):
        dot(g, n, e, "f3", 3.5)
    g.path(list(zip(range(6), dbl)), "ln c5 thin")
    g.path(list(zip(range(6), bis)), "ln cm thin dash")
    for i, (lab, cl, lc) in enumerate([("Newton, racine simple", "tx-s t3", "ln c3"), ("Newton sur x², racine double", "tx-s t5", "ln c5 thin"),
                                       ("dichotomie", "tx-s", "ln cm thin dash")]):
        y = -10.2 - 1.1 * i
        g.line(0.15, y, 0.55, y, lc)
        g.text(0.55, y, lab, cl, "start", dx=5, dy=4)
    c.text(535, 16, "erreur |xₙ − √2| (échelle log)", "tx-b", "middle")
    c.save()


def sup(e):
    table = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")
    return str(e).translate(table)


# ---------------------------------------------------------------------------------------------- 14. penalization
def fig_penalisation():
    c = Canvas("penalisation", 680, 280, "Pénalisation extérieure et barrière intérieure pour min x sous x ≥ 1", sub=SUB)
    eps = [1, 0.5, 0.2]
    cls = ["ln c2 thin", "ln c2", "ln c2"]
    styles = ["stroke-opacity:0.45", "stroke-opacity:0.7", ""]
    for k in range(2):
        x0 = 40 + k * 340
        f = Fig(c, (x0, 30, 280, 200), (0, 2.6), (0, 3.2))
        for x in (0, 0.5, 1, 1.5, 2, 2.5):
            f.line(x, 0, x, 3.2, "gr")
            f.text(x, 0, f"{x:g}".replace(".", ","), "tx-s", "middle", dy=14)
        for y in (0, 1, 2, 3):
            f.line(0, y, 2.6, y, "gr")
            f.text(0, y, str(y), "tx-s", "end", dx=-5, dy=4)
        f.path([(1, 0), (2.6, 0), (2.6, 3.2), (1, 3.2)], "a1", close=True)
        f.line(1, 0, 1, 3.2, "ln c1 thin")
        f.fn(lambda x: x, "ln cm thin dash", 0, 2.6)
        for e, cl, st in zip(eps, cls, styles):
            if k == 0:
                fn = lambda x, e=e: x + max(1 - x, 0) ** 2 / e
                xm = 1 - e / 2
                fn_clip(f, fn, cl, 0, 2.6, style=st or None)
                dot(f, xm, fn(xm), "f6", 4)
            else:
                fn = lambda x, e=e: x - e * math.log(x - 1)
                xm = 1 + e
                fn_clip(f, fn, cl, 1.00001, 2.6, n=3000, style=st or None)
                dot(f, xm, fn(xm), "f3", 4)
        f.text(2.55, 0.3, "x ≥ 1", "tx-s t1", "end")
        if k == 0:
            c.text(x0 + 140, 18, "extérieure : x + (1/ε) max(1 − x, 0)²", "tx-b", "middle")
            c.text(x0 + 140, 268, "minimiseurs 1 − ε/2 = 1/2, 3/4, 9/10 (roses) : hors de K", "tx-s t6", "middle")
        else:
            c.text(x0 + 140, 18, "intérieure : x − μ log(x − 1)", "tx-b", "middle")
            c.text(x0 + 140, 268, "minimiseurs 1 + μ = 2, 3/2, 6/5 (verts) : dans K", "tx-s t3", "middle")
    c.save()


# ---------------------------------------------------------------------------------------------- 15. graph
GNODES = {"s": (60, 150), "a": (210, 60), "b": (210, 240), "c": (370, 60), "d": (370, 240), "p": (520, 150)}
GARCS = [("s", "a", 4), ("s", "b", 1), ("b", "a", 2), ("a", "c", 1), ("b", "c", 5), ("b", "d", 8), ("c", "d", 3), ("c", "p", 6), ("d", "p", 1)]


def arc_px(c, p, q, label, cls, k, r=17, off=11, lab_cls="tx-b"):
    dx, dy = q[0] - p[0], q[1] - p[1]
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    s = (p[0] + ux * r, p[1] + uy * r)
    e = (q[0] - ux * (r + 2), q[1] - uy * (r + 2))
    mid = c.arrow_marker(k)
    c.add(f'<line x1="{s[0]:.1f}" y1="{s[1]:.1f}" x2="{e[0]:.1f}" y2="{e[1]:.1f}" class="{cls}" marker-end="url(#{mid})"/>')
    mx, my = (s[0] + e[0]) / 2, (s[1] + e[1]) / 2
    nx, ny = -uy, ux
    bg_text(c, mx + nx * off, my + ny * off + 4, label, lab_cls, "middle", w=16)


def fig_graphe():
    c = Canvas("graphe", 600, 300, "Un graphe orienté à 6 nœuds et 9 arcs, avec le coût de chaque arc", sub=SUB)
    offs = {("s", "a"): -12, ("s", "b"): 12, ("b", "a"): 12, ("a", "c"): -12, ("b", "c"): -12, ("b", "d"): 12,
            ("c", "d"): -12, ("c", "p"): -12, ("d", "p"): 12}
    for (u, v, w) in GARCS:
        arc_px(c, GNODES[u], GNODES[v], str(w), "ln cm thin", "m", off=offs[(u, v)])
    for n, (x, y) in GNODES.items():
        c.add(f'<circle cx="{x}" cy="{y}" r="16" class="f1"/>')
        c.add(f'<text x="{x}" y="{y + 4.5}" class="on-fill" text-anchor="middle">{n}</text>')
    deg = {"s": (2, 0), "a": (1, 2), "b": (3, 1), "c": (2, 2), "d": (1, 2), "p": (0, 2)}
    for n, (x, y) in GNODES.items():
        dy = -26 if y < 150 else (32 if y > 150 else -26)
        c.text(x, y + dy, f"d⁺ = {deg[n][0]}, d⁻ = {deg[n][1]}", "tx-s", "middle")
    c.text(60, 290, "source s", "tx-s", "middle")
    c.text(520, 290, "puits p", "tx-s", "middle")
    c.save()


# ---------------------------------------------------------------------------------------------- 16. rounding
def fig_arrondi():
    c = Canvas("arrondi", 660, 320, "Arrondir l'optimum d'un programme linéaire ne donne pas l'optimum entier", sub=SUB)
    box = (-0.5, 5.3, -0.5, 3.6)
    w = 420
    f = Fig(c, (40, 10, w, w * 4.1 / 5.8), box[:2], box[2:])
    grid(f, range(0, 6), range(0, 4))
    f.line(box[0], 0, box[1], 0, "ax")
    f.line(0, box[2], 0, box[3], "ax")
    poly = [(0, 0), (4, 0), (3, 1.5), (0, 3)]
    for a, b_, r in [(6, 4, 24), (1, 2, 6)]:
        seg = line_in_box(a, b_, r, box)
        f.line(seg[0][0], seg[0][1], seg[1][0], seg[1][1], "ln cm hair")
    f.path(poly, "a1", close=True)
    f.path(poly, "ln c1 thin", close=True)
    f.text(4.15, 0.75, "6x₁ + 4x₂ ≤ 24", "tx-s", "start")
    f.text(0.2, 3.1, "x₁ + 2x₂ ≤ 6", "tx-s", "start", dx=8)
    seg = line_in_box(5, 4, 21, box)
    f.line(seg[0][0], seg[0][1], seg[1][0], seg[1][1], "ln c2 thin dash")
    pts = [(x, y) for x in range(0, 6) for y in range(0, 4) if 6 * x + 4 * y <= 24 and x + 2 * y <= 6]
    for p in pts:
        dot(f, *p, "f4", 3.5)
    dot(f, 3, 1.5, "f3", 5.5)
    f.text(3, 1.5, "(3, 3/2) : 21", "tx-b t3", "start", dx=9, dy=-4)
    open_dot(f, 3, 2, "6", 5)
    f.text(3, 2, "(3, 2) : non admissible", "tx-s t6", "start", dx=9, dy=-2)
    f.c.add(f'<circle cx="{f.X(3):.1f}" cy="{f.Y(1):.1f}" r="7" class="nofill ln c4 thin"/>')
    f.text(3, 1, "(3, 1) : 19", "tx-s", "end", dx=-8, dy=18)
    f.c.add(f'<circle cx="{f.X(4):.1f}" cy="{f.Y(0):.1f}" r="7" class="nofill ln c3"/>')
    f.text(4, 0, "(4, 0) : 20", "tx-b t3", "start", dx=10, dy=-6)
    x0 = 480
    lines = [("max 5x₁ + 4x₂", "tx-b t2"), ("", ""), ("Relaxation (vert plein) :", "tx-s"), ("x = (3, 3/2), valeur 21.", "tx-s t3"),
             ("", ""), ("Arrondis :", "tx-s"), ("(3, 2) sort (rose),", "tx-s t6"), ("(3, 1) vaut 19.", "tx-s"), ("", ""),
             ("Optimum entier (cercle", "tx-s"), ("vert) : (4, 0), valeur 20.", "tx-s t3"), ("Points entiers : or.", "tx-s t4")]
    for i, (s, cls) in enumerate(lines):
        if s:
            c.text(x0, 30 + 19 * i, s, cls, "start")
    c.save()


if __name__ == "__main__":
    fig_rang()
    fig_coordonnees()
    fig_determinant()
    fig_convexes()
    fig_polyedre()
    fig_fonctions()
    fig_existence()
    fig_fermes()
    fig_farkas()
    fig_separation()
    fig_kkt()
    fig_selle()
    fig_newton()
    fig_penalisation()
    fig_graphe()
    fig_arrondi()
