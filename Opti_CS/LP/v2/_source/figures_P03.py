"""figures_P03.py — static SVG figures of Partie 3 (l'algorithme du simplexe), written to figures/P03/.

Run: python3 figures_P03.py        (then node build.mjs Partie03.html)

Every coordinate is computed here. The numbers written on the figures (paths, reduced costs, ratios, Klee–Minty
vertices, LAD fit) are those of the verification scripts (verify_P03/v01…v12); they are recomputed below
in exact arithmetic where it matters.
"""
from fractions import Fraction as Fr

import numpy as np

from figures_common import Canvas, Fig

SUB = "P03"

# The polygon of Ex. 4.2.1: -3x1 + 2x2 <= 2, -x1 + 2x2 <= 4, x1 + x2 <= b3, x >= 0.
CONS = [(-3, 2, 2, "x₃ = 0"), (-1, 2, 4, "x₄ = 0"), (1, 1, 5, "x₅ = 0")]
V421 = [(0, 0), (0, 1), (1, 2.5), (2, 3), (5, 0)]


def fs(v):
    """A fraction as text with a Unicode minus."""
    v = Fr(v).limit_denominator(1000)
    s = str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"
    return s.replace("-", "−")


def subtext(c, x, y, parts, cls="tx", anchor="start"):
    """A text with subscripts: parts = [("x", False), ("B", True), ...] (no Unicode subscript exists for B)."""
    out = ""
    for t, is_sub in parts:
        t = t.replace("&", "&amp;").replace("<", "&lt;")
        out += f'<tspan baseline-shift="sub" font-size="75%">{t}</tspan>' if is_sub else t
    c.add(f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}">{out}</text>')


def pt(p):
    return "(" + " ; ".join(fs(v) for v in p) + ")"


def clip_line(a, b, r, box):
    """Segment of a x + b y = r inside box = (x0, x1, y0, y1)."""
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
                best, d = (pts[i], pts[j]), dd
    return best


def polygon(cons, box):
    """Vertices of {a x + b y <= r} ∩ box (Sutherland–Hodgman), as in app.js."""
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


def draw_lp(f, cons, box, labels=True, label_pos=None):
    """The admissible polygon (blue) and the constraint lines (grey) with their labels."""
    P = polygon([(a, b, r) for a, b, r, _ in cons] + [(-1, 0, 0), (0, -1, 0)], box)
    f.path(P, "a1", close=True)
    f.path(P, "ln c1 thin", close=True)
    for k, (a, b, r, lab) in enumerate(cons):
        seg = clip_line(a, b, r, box)
        if seg:
            f.line(seg[0][0], seg[0][1], seg[1][0], seg[1][1], "ln cm hair")
            if labels and label_pos:
                x, y, anc = label_pos[k]
                f.text(x, y, lab, "tx-s", anc)
    return P


def arrow_data(c, f, p, q, k, cls=None, shorten=0.0):
    """Arrow between two data points (shortened by `shorten` pixels at the end)."""
    x1, y1, x2, y2 = f.X(p[0]), f.Y(p[1]), f.X(q[0]), f.Y(q[1])
    L = np.hypot(x2 - x1, y2 - y1)
    if shorten and L > 0:
        x2 -= (x2 - x1) / L * shorten
        y2 -= (y2 - y1) / L * shorten
        x1 += (x2 - x1) / L * 3
        y1 += (y2 - y1) / L * 3
    c.arrow(x1, y1, x2, y2, k, cls)


# ---------------------------------------------------------------------------------------------
def fig_idee():
    c = Canvas("idee", 640, 320, "Le simplexe sur le polygone de l'exercice 4.2.1 : de sommet en sommet, le coût baisse", sub=SUB)
    box = (-0.4, 5.6, -0.4, 3.7)
    f = Fig(c, (40, 16, 360, 252), (box[0], box[1]), (box[2], box[3]))
    f.axes(xticks=[0, 1, 2, 3, 4, 5], yticks=[0, 1, 2, 3], grid=False, xlabel="x₁", ylabel="x₂")
    draw_lp(f, CONS, box, label_pos=[(1.72, 3.6, "end"), (3.45, 3.6, "start"), (4.6, 0.75, "start")])
    # level lines of x1 + 2x2 (= - cost)
    for v in (2, 6, 8):
        seg = clip_line(1, 2, v, box)
        f.line(seg[0][0], seg[0][1], seg[1][0], seg[1][1], "ln c2 hair dash")
    f.text(4.3, 1.85, "x₁ + 2x₂ = 8", "tx-s t2", "start", dy=-6)
    f.text(2.6, 1.7, "= 6", "tx-s t2", "start", dy=-6)
    f.text(1.25, 0.375, "= 2", "tx-s t2", "start", dy=-6)
    # path (Dantzig)
    path = [(0, 0), (0, 1), (1, 2.5), (2, 3)]
    for p, q in zip(path, path[1:]):
        arrow_data(c, f, p, q, 3, "ln c3", shorten=7)
    for p in V421:
        f.circle(p[0], p[1], 3.5, "fm")
    for k, p in enumerate(path):
        f.circle(p[0], p[1], 5 if k < 3 else 6.5, "f3")
    lab = [("x⁰", -18, 16), ("x¹", -20, 4), ("x²", -22, -2), ("x³", 6, -10)]
    for p, (s_, dx, dy) in zip(path, lab):
        f.text(p[0], p[1], s_, "tx-b t3", "start", dx=dx, dy=dy)
    # direction of decrease of the cost c = (-1, -2): -c = (1, 2)
    o = (2.9, 0.25)
    c.arrow(f.X(o[0]), f.Y(o[1]), f.X(o[0] + 0.3), f.Y(o[1] + 0.6), 2, "ln c2 thin")
    f.text(o[0], o[1], "−c", "tx-b t2", "end", dx=-4, dy=-2)
    # right panel: the four vertices
    X0 = 432
    c.text(X0, 28, "Le chemin du simplexe", "tx-b")
    c.text(X0, 44, "(règle du plus négatif)", "tx-s")
    rows = [("x⁰ = (0 ; 0)", "coût 0", "base {x₃, x₄, x₅}"), ("x¹ = (0 ; 1)", "coût −2", "base {x₂, x₄, x₅}"),
            ("x² = (1 ; 5/2)", "coût −6", "base {x₁, x₂, x₅}"), ("x³ = (2 ; 3)", "coût −8", "base {x₁, x₂, x₃}")]
    for k, (a, b, cc) in enumerate(rows):
        y = 74 + 46 * k
        c.text(X0, y, a, "tx t3" if k == 3 else "tx")
        c.text(X0 + 116, y, b, "tx-s t2")
        c.text(X0, y + 16, cc, "tx-s")
    c.text(X0, 268, "Coût = −x₁ − 2x₂ :", "tx-s")
    c.text(X0, 283, "on maximise x₁ + 2x₂.", "tx-s")
    c.text(X0, 304, "En x³, aucune arête ne descend.", "tx-s t3")
    c.save()


def fig_pentes():
    c = Canvas("pentes", 640, 280, "Les coûts réduits sont les pentes du coût le long des arêtes qui partent du sommet", sub=SUB)
    box = (-0.4, 5.6, -0.4, 3.7)
    f = Fig(c, (36, 14, 290, 200), (box[0], box[1]), (box[2], box[3]))
    f.axes(xticks=[0, 1, 2, 3, 4, 5], yticks=[0, 1, 2, 3], grid=False, xlabel="x₁", ylabel="x₂")
    draw_lp(f, CONS, box)
    arrow_data(c, f, (0, 0), (5, 0), 2, "ln c2", shorten=6)
    arrow_data(c, f, (0, 0), (0, 1), 2, "ln c2", shorten=6)
    f.circle(0, 0, 5.5, "f3")
    f.circle(5, 0, 4, "fm")
    f.circle(0, 1, 4, "fm")
    f.text(2.5, 0, "x₁ entre : c̃₁ = −1", "tx-s t2", "middle", dy=-7)
    f.text(0, 1, "x₂ entre : c̃₂ = −2", "tx-s t2", "start", dx=8, dy=-6)
    f.text(0, 0, "x⁰", "tx-b t3", "end", dx=-6, dy=14)
    c.text(36 + 145, 266, "Au sommet (0 ; 0) : deux arêtes, deux variables hors base", "tx-s", "middle")
    # right: cost along each edge
    g = Fig(c, (380, 18, 236, 196), (0, 5.5), (-5.6, 0.5))
    g.axes(xticks=[0, 1, 2, 3, 4, 5], yticks=[0, -1, -2, -3, -4, -5], xlabel="ε", ylabel="coût c·x(ε)")
    g.line(0, 0, 5, -5, "ln c2")
    g.line(0, 0, 1, -2, "ln c2 dash")
    g.circle(5, -5, 4.5, "f3")
    g.circle(1, -2, 4.5, "f3")
    g.text(2.6, -1.75, "pente −1 (x₁ entre)", "tx-s t2", "start")
    g.text(1.15, -0.55, "pente −2 (x₂ entre)", "tx-s t2", "start")
    g.text(5, -5, "ε = 5", "tx-s", "end", dx=-6, dy=4)
    g.text(1, -2, "ε = 1", "tx-s", "end", dx=-6, dy=14)
    c.text(380 + 118, 266, "c·x(ε) = c·x⁰ + ε c̃ᵢ, jusqu'au bout de l'arête", "tx-s", "middle")
    c.save()


def fig_rapport():
    c = Canvas("rapport", 640, 300, "Le test du rapport : la première variable de base qui s'annule arrête le pas", sub=SUB)
    # left: x_B(eps) for the iteration at (0,1): basis {x2, x4, x5}, x1 enters, dir = (-3/2, 2, 5/2), x_B = (1, 2, 4)
    f = Fig(c, (46, 22, 280, 200), (0, 2.05), (-1.3, 4.3))
    f.path([(0, -1.3), (1, -1.3), (1, 4.3), (0, 4.3)], "a3", close=True)
    f.axes(xticks=[0, 0.5, 1, 1.5, 2], yticks=[-1, 0, 1, 2, 3, 4], xfmt=lambda v: fs(v), xlabel="ε")
    subtext(c, f.X(0) + 4, f.Y(4.3) - 8, [("x", False), ("B", True), ("(ε)", False)], "tx-s")
    f.line(0, 1, 2, 4, "ln c1")              # x2 = 1 + 3/2 eps
    f.line(0, 2, 1.65, -1.3, "ln c2")        # x4 = 2 - 2 eps
    f.line(0, 4, 2, -1, "ln c5")             # x5 = 4 - 5/2 eps
    f.circle(1, 0, 5, "f3")
    f.circle(1.6, 0, 4, "f6")
    f.text(1.6, 0, "8/5", "tx-s t6", "end", dx=-5, dy=15)
    f.text(0.5, -1.1, "0 ≤ ε ≤ ε₁ = 1", "tx-s t3", "middle")
    c.text(46, 258, "x₂ = 1 + 3ε/2", "tx-s t1")
    c.text(136, 258, "x₄ = 2 − 2ε", "tx-s t2")
    c.text(218, 258, "x₅ = 4 − 5ε/2", "tx-s t5")
    c.text(186, 284, "x₁ entre depuis (0 ; 1) : rapports —, 2/2 = 1, 4/(5/2) = 8/5", "tx-s", "middle")
    # right: the same move in the plane
    box = (-0.3, 5.4, -0.3, 3.8)
    g = Fig(c, (380, 30, 240, 172), (box[0], box[1]), (box[2], box[3]))
    g.axes(xticks=[0, 1, 2, 3, 4, 5], yticks=[0, 1, 2, 3], grid=False, xlabel="x₁", ylabel="x₂")
    draw_lp(g, CONS, box)
    g.line(0, 1, 1.6, 3.4, "ln c6 thin dash")
    arrow_data(c, g, (0, 1), (1, 2.5), 3, "ln c3", shorten=6)
    g.circle(0, 1, 5, "f3")
    g.circle(1, 2.5, 5, "f3")
    g.circle(1.6, 3.4, 4.5, "f6")
    g.text(1, 2.5, "ε = 1 : x₄ = 0", "tx-s t3", "start", dx=8, dy=12)
    g.text(1.6, 3.4, "ε = 8/5 : x₅ = 0, mais x₄ < 0", "tx-s t6", "start", dx=8, dy=0)
    g.text(0, 1, "(0 ; 1)", "tx-s", "start", dx=7, dy=12)
    c.text(500, 258, "Le point x(ε) suit l'arête ; au-delà de", "tx-s", "middle")
    c.text(500, 274, "ε = 1, il sort du polygone (x₄ < 0).", "tx-s", "middle")
    c.save()


def fig_degenere():
    c = Canvas("degenere", 640, 300, "Un sommet dégénéré : trois droites passent par (1 ; 5/2), trois bases le décrivent", sub=SUB)
    cons = [(-3, 2, 2, "−3x₁ + 2x₂ = 2  (x₃ = 0)"), (-1, 2, 4, "−x₁ + 2x₂ = 4  (x₄ = 0)"), (1, 1, 3.5, "x₁ + x₂ = 7/2  (x₅ = 0)")]
    box = (-0.4, 4.2, -0.4, 3.6)
    f = Fig(c, (40, 14, 300, 250), (box[0], box[1]), (box[2], box[3]))
    f.axes(xticks=[0, 1, 2, 3, 4], yticks=[0, 1, 2, 3], grid=False, xlabel="x₁", ylabel="x₂")
    draw_lp(f, cons, box)
    # line labels placed by hand along each line
    f.text(1.62, 3.42, "x₃ = 0", "tx-s", "start")
    f.text(3.2, 3.35, "x₄ = 0", "tx-s", "middle")
    f.text(3.3, 0.55, "x₅ = 0", "tx-s", "start")
    for p in [(0, 0), (0, 1), (3.5, 0)]:
        f.circle(p[0], p[1], 3.5, "fm")
    f.circle(1, 2.5, 7, "f3")
    f.text(1, 2.5, "(1 ; 5/2)", "tx-b t3", "end", dx=-9, dy=4)
    seg = clip_line(1, 2, 6, box)
    f.line(seg[0][0], seg[0][1], seg[1][0], seg[1][1], "ln c2 hair dash")
    ang = np.degrees(np.arctan2(f.Y(1.0) - f.Y(1.5), f.X(4.0) - f.X(3.0)))
    rad = np.radians(ang)
    lx, ly = f.X(3.2) + 10 * np.sin(rad), f.Y(1.4) - 10 * np.cos(rad)
    c.add(f'<text x="{lx:.1f}" y="{ly:.1f}" class="tx-s t2" text-anchor="middle" transform="rotate({ang:.1f} {lx:.1f} {ly:.1f})">x₁ + 2x₂ = 6</text>')
    X0 = 366
    c.text(X0, 30, "Un sommet, trois bases", "tx-b")
    c.text(X0, 48, "min −x₁ − 2x₂ : optimum (1 ; 5/2), coût −6", "tx-s")
    rows = [("{x₁, x₂, x₃} : x₃ = 0 en base", "c̃₄ = 1/3, c̃₅ = 4/3 ≥ 0", "t3", "le critère conclut"),
            ("{x₁, x₂, x₄} : x₄ = 0 en base", "c̃₃ = 1/5, c̃₅ = 8/5 ≥ 0", "t3", "le critère conclut"),
            ("{x₁, x₂, x₅} : x₅ = 0 en base", "c̃₃ = −1 < 0,  c̃₄ = 2", "t6", "le critère échoue (sommet optimal)")]
    for k, (a, b, cl, d) in enumerate(rows):
        y = 84 + 62 * k
        c.text(X0, y, a, "tx")
        c.text(X0 + 8, y + 17, b, f"tx-s {cl}")
        c.text(X0 + 8, y + 33, d, "tx-s")
    c.text(X0, 272, "x₁ + x₂ ≤ 7/2 au lieu de 5 (variante de l'ex. 4.2.1)", "tx-s")
    c.save()


def fig_chemins():
    c = Canvas("chemins", 640, 270, "Deux règles de choix, deux chemins sur le polygone de l'exercice 4.2.1", sub=SUB)
    box = (-0.4, 5.6, -0.4, 3.7)
    paths = [("Plus négatif (Dantzig) : 3 pivots", [(0, 0), (0, 1), (1, 2.5), (2, 3)],
              [("x₂ entre", 8, 4, "start"), ("x₁ entre", 8, 10, "start"), ("x₃ entre", 6, 16, "start")]),
             ("Plus petit indice (Bland) : 2 pivots", [(0, 0), (5, 0), (2, 3)],
              [("x₁ entre", 0, -7, "middle"), ("x₂ entre", 10, 0, "start")])]
    for i, (title, path, labs) in enumerate(paths):
        x0 = 30 + 316 * i
        f = Fig(c, (x0, 30, 280, 196), (box[0], box[1]), (box[2], box[3]))
        f.axes(xticks=[0, 1, 2, 3, 4, 5], yticks=[0, 1, 2, 3], grid=False)
        draw_lp(f, CONS, box)
        for p, q in zip(path, path[1:]):
            arrow_data(c, f, p, q, 3, "ln c3", shorten=7)
        for p in V421:
            f.circle(p[0], p[1], 3, "fm")
        for p in path:
            f.circle(p[0], p[1], 4.5, "f3")
        c.text(x0 + 140, 18, title, "tx-b", "middle")
        for (p, q), (lab, dx, dy, anc) in zip(zip(path, path[1:]), labs):
            mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
            f.text(mx, my, lab, "tx-s t3", anc, dx=dx, dy=dy)
    c.text(320, 262, "Le plus raide au départ (pente −2) n'est pas le plus court : 3 pivots au lieu de 2.", "tx-s", "middle")
    c.save()


def fig_klee_minty():
    c = Canvas("klee-minty", 640, 330, "Le cube déformé de Klee et Minty (n = 3) : la règle du plus négatif visite les 8 sommets", sub=SUB)
    # vertices of: x1 <= 5, 4x1 + x2 <= 25, 8x1 + 4x2 + x3 <= 125 (scaled u = x1/5, x2/25, x3/125)
    path = [(0, 0, 0), (5, 0, 0), (5, 5, 0), (0, 25, 0), (0, 25, 25), (5, 5, 65), (5, 0, 85), (0, 0, 125)]
    costs = [4 * a + 2 * b + d for a, b, d in path]
    verts = []
    for b1 in (0, 1):
        x1 = 5 * b1
        for b2 in (0, 1):
            x2 = (25 - 4 * x1) * b2
            for b3 in (0, 1):
                x3 = (125 - 8 * x1 - 4 * x2) * b3
                verts.append(((b1, b2, b3), (x1, x2, x3)))
    assert sorted(v[1] for v in verts) == sorted(path)

    def P(x):
        u1, u2, u3 = x[0] / 5, x[1] / 25, x[2] / 125
        return (130 + 220 * u1 + 110 * u2, 300 - 40 * u1 - 70 * u2 - 210 * u3)
    # edges of the combinatorial cube
    for (bits, x) in verts:
        for k in range(3):
            if bits[k] == 0:
                nb = list(bits); nb[k] = 1
                y = next(v[1] for v in verts if v[0] == tuple(nb))
                p, q = P(x), P(y)
                c.add(f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}" class="ln cm hair"/>')
    for a, b in zip(path, path[1:]):
        p, q = P(a), P(b)
        L = np.hypot(q[0] - p[0], q[1] - p[1])
        ux, uy = (q[0] - p[0]) / L, (q[1] - p[1]) / L
        c.arrow(p[0] + 6 * ux, p[1] + 6 * uy, q[0] - 8 * ux, q[1] - 8 * uy, 3, "ln c3 thin")
    offs = {0: (-10, 14, "end"), 1: (8, 14, "start"), 2: (10, 4, "start"), 3: (-10, 4, "end"), 4: (-10, -4, "end"),
            5: (10, 2, "start"), 6: (10, 4, "start"), 7: (-10, -2, "end")}
    for k, x in enumerate(path):
        p = P(x)
        c.add(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="{6.5 if k == 7 else 4.5}" class="f3"/>')
        dx, dy, anc = offs[k]
        c.text(p[0] + dx, p[1] + dy, f"{k} : ({x[0]}, {x[1]}, {x[2]})", "tx-s", anc)
    X0 = 458
    c.text(X0, 28, "max 4x₁ + 2x₂ + x₃ sous", "tx-b")
    c.text(X0, 46, "x₁ ≤ 5,  4x₁ + x₂ ≤ 25,", "tx-s")
    c.text(X0, 62, "8x₁ + 4x₂ + x₃ ≤ 125,  x ≥ 0", "tx-s")
    c.text(X0, 92, "Coûts 4x₁ + 2x₂ + x₃ visités :", "tx-s")
    c.text(X0, 108, " → ".join(str(v) for v in costs[:4]) + " →", "tx-s t3")
    c.text(X0, 124, " → ".join(str(v) for v in costs[4:]), "tx-s t3")
    c.text(X0, 154, "7 pivots, chacun améliore le coût :", "tx-s")
    c.text(X0, 170, "il passe par les 8 sommets.", "tx-s")
    c.text(X0, 200, "En dimension n : 2ⁿ − 1 pivots", "tx-b")
    c.text(X0, 218, "(vérifié pour n = 1, …, 10 ;", "tx-s")
    c.text(X0, 234, "n = 10 : 1023 pivots).", "tx-s")
    c.text(X0, 264, "Les axes sont déformés (x₁ ≤ 5,", "tx-s")
    c.text(X0, 280, "x₂ ≤ 25, x₃ ≤ 125) pour la lisibilité.", "tx-s")
    c.save()


def fig_phases():
    c = Canvas("phases", 640, 300, "Phase I puis phase II : trouver un sommet, puis l'améliorer", sub=SUB)

    def box(x, y, w, h, lines, cls="a1", tcls="tx"):
        c.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" class="{cls}"/>')
        c.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" class="ln cm hair nofill"/>')
        for k, s in enumerate(lines):
            c.text(x + w / 2, y + 18 + 16 * k, s, tcls if k == 0 else "tx-s", "middle")
    box(20, 20, 180, 56, ["Problème (4.1)", "Ax = b, x ≥ 0"], "am", "tx-b")
    box(20, 120, 180, 56, ["Rendre b ≥ 0", "lignes où bᵢ < 0 : × (−1)"], "am")
    box(240, 120, 190, 72, ["Phase I : (4.8)", "min Σ yᵢ, Ax + y = b,", "x ≥ 0, y ≥ 0 ; départ (0, b)"], "a4", "tx-b")
    box(470, 20, 150, 56, ["Valeur > 0", "Xad est vide : stop"], "a2", "tx-b")
    box(470, 120, 150, 72, ["Valeur = 0", "y = 0 ; chasser les yᵢ", "restés en base à 0"], "a3", "tx-b")
    box(470, 228, 150, 56, ["Phase II", "simplexe sur c"], "a3", "tx-b")
    box(240, 228, 190, 56, ["Résultat", "sommet optimal ou −∞"], "am", "tx-b")
    c.arrow(110, 76, 110, 118, "m", "ln cm thin")
    c.arrow(200, 148, 238, 148, "m", "ln cm thin")
    c.arrow(430, 140, 468, 66, "m", "ln cm thin")
    c.arrow(430, 160, 468, 160, "m", "ln cm thin")
    c.arrow(545, 192, 545, 226, "m", "ln cm thin")
    c.arrow(470, 256, 432, 256, "m", "ln cm thin")
    c.save()


def fig_anatomie():
    c = Canvas("anatomie", 640, 220, "Le tableau du simplexe : B⁻¹A et B⁻¹b, puis la ligne des coûts réduits", sub=SUB)
    x0, y0, w1, w2, h1, h2 = 170, 30, 300, 90, 110, 44
    c.add(f'<rect x="{x0}" y="{y0}" width="{w1}" height="{h1}" class="a1"/>')
    c.add(f'<rect x="{x0 + w1}" y="{y0}" width="{w2}" height="{h1}" class="a3"/>')
    c.add(f'<rect x="{x0}" y="{y0 + h1}" width="{w1}" height="{h2}" class="a2"/>')
    c.add(f'<rect x="{x0 + w1}" y="{y0 + h1}" width="{w2}" height="{h2}" class="am"/>')
    c.add(f'<rect x="{x0}" y="{y0}" width="{w1 + w2}" height="{h1 + h2}" class="ln cm thin nofill"/>')
    c.add(f'<line x1="{x0 + w1}" y1="{y0}" x2="{x0 + w1}" y2="{y0 + h1 + h2}" class="ln cm thin"/>')
    c.add(f'<line x1="{x0}" y1="{y0 + h1}" x2="{x0 + w1 + w2}" y2="{y0 + h1}" class="ln cm thin"/>')
    c.text(x0 + w1 / 2, y0 + 50, "B⁻¹A", "tx-b", "middle")
    c.text(x0 + w1 / 2, y0 + 70, "colonnes de base : vecteurs eⱼ ; colonne i : d = B⁻¹aᵢ", "tx-s", "middle")
    c.text(x0 + w1 + w2 / 2, y0 + 50, "B⁻¹b", "tx-b", "middle")
    subtext(c, x0 + w1 + w2 / 2, y0 + 70, [("= x", False), ("B", True)], "tx-s", "middle")
    subtext(c, x0 + w1 / 2, y0 + h1 + 27, [("c̃ᵀ = cᵀ − c", False), ("B", True), ("ᵀ B⁻¹A  (0 sur la base)", False)], "tx-b t2", "middle")
    c.text(x0 + w1 + w2 / 2, y0 + h1 + 27, "−c·x", "tx-b", "middle")
    c.text(x0 - 10, y0 + 30, "1re variable de base", "tx-s", "end")
    c.text(x0 - 10, y0 + 60, "…", "tx-s", "end")
    c.text(x0 - 10, y0 + 90, "m-ième variable de base", "tx-s", "end")
    c.text(x0 - 10, y0 + h1 + 27, "coûts réduits", "tx-s t2", "end")
    c.text(x0 + w1 / 2, y0 - 10, "une colonne par variable x₁ … xₙ", "tx-s", "middle")
    c.text(x0 + w1 + w2 / 2, y0 - 10, "second membre", "tx-s", "middle")
    c.text(320, 212, "Un pivot = une élimination de Gauss–Jordan sur tout le tableau, ligne des coûts comprise.", "tx-s", "middle")
    c.save()


def fig_lad():
    c = Canvas("lad", 640, 300, "Régression en norme ℓ¹ : la droite optimale passe par deux points de données", sub=SUB)
    X = np.arange(7.0)
    Y = np.array([1, 3, 2, 5, 4, 6, 18.0])
    f = Fig(c, (46, 16, 380, 250), (-0.4, 6.6), (-1, 19))
    f.axes(xticks=list(range(7)), yticks=[0, 5, 10, 15], xlabel="x", ylabel="y")
    ls = np.polyfit(X, Y, 1)          # 59/28, -3/4
    f.line(-0.4, ls[1] + ls[0] * -0.4, 6.6, ls[1] + ls[0] * 6.6, "ln c2 dash")
    f.line(-0.4, 0.6, 6.6, 7.6, "ln c3")
    for x, y in zip(X, Y):
        yl = 1 + x
        if abs(y - yl) > 1e-9:
            f.line(x, yl, x, y, "ln c3 hair dot")
    for x, y in zip(X, Y):
        f.circle(x, y, 4.5, "fk")
    for k in (0, 5):
        f.circle(X[k], Y[k], 8, "ln c3 thin nofill")
    f.text(6, 18, "point aberrant (6 ; 18)", "tx-s", "end", dx=-10, dy=4)
    f.text(6.55, 7.4, "ℓ¹ : y = 1 + x", "tx-s t3", "end", dy=22)
    f.text(5.2, 11.5, "moindres carrés", "tx-s t2", "end")
    X0 = 450
    c.text(X0, 30, "Données : x = 0, …, 6", "tx-b")
    c.text(X0, 48, "y = 1, 3, 2, 5, 4, 6, 18", "tx-s")
    c.text(X0, 78, "min Σ |yᵢ − a − b xᵢ|  (PL)", "tx-s t3")
    c.text(X0, 94, "→ a = 1, b = 1, valeur 15", "tx-s t3")
    c.text(X0, 110, "résidus nuls en x = 0 et x = 5", "tx-s t3")
    c.text(X0, 140, "Moindres carrés :", "tx-s t2")
    c.text(X0, 156, "b = 59/28 ≈ 2,11 ; a = −3/4", "tx-s t2")
    c.text(X0, 186, "Montez le point aberrant à 100 :", "tx-s")
    c.text(X0, 202, "la droite ℓ¹ ne bouge pas,", "tx-s")
    c.text(X0, 218, "la pente des moindres carrés", "tx-s")
    c.text(X0, 234, "passe à ≈ 10,9.", "tx-s")
    c.save()


def fig_ex424():
    c = Canvas("ex424", 640, 280, "Exercice 4.2.4 : le polygone, les lignes de niveau de 2x₁ − x₂ et le pas du simplexe", sub=SUB)
    cons = [(1, 1, 1, "x₁ + x₂ = 1"), (-1, 1, 0.5, "x₂ − x₁ = 1/2")]
    box = (-0.25, 1.25, -0.2, 1.15)
    f = Fig(c, (46, 14, 330, 232), (box[0], box[1]), (box[2], box[3]))
    f.axes(xticks=[0, 0.25, 0.5, 0.75, 1], yticks=[0, 0.25, 0.5, 0.75, 1], grid=False,
           xfmt=lambda v: fs(v), yfmt=lambda v: fs(v), xlabel="x₁", ylabel="x₂")
    draw_lp(f, cons, box, label_pos=[(0.8, 0.3, "start"), (0.66, 1.12, "start")])
    for v, ytop in ((0, 1.15), (-0.5, 1.15), (1, 0.95)):
        seg = clip_line(2, -1, v, (box[0], box[1], box[2], ytop))
        f.line(seg[0][0], seg[0][1], seg[1][0], seg[1][1], "ln c2 hair dash")
    arrow_data(c, f, (0, 0), (0, 0.5), 3, "ln c3", shorten=7)
    for p in [(0, 0), (1, 0), (0.25, 0.75), (0, 0.5)]:
        f.circle(p[0], p[1], 3.5, "fm")
    f.circle(0, 0, 5, "f3")
    f.circle(0, 0.5, 6.5, "f3")
    f.text(0, 0, "x⁰", "tx-b t3", "start", dx=8, dy=-6)
    f.text(0, 0.5, "x¹", "tx-b t3", "start", dx=9, dy=-8)
    f.text(0.25, 0.75, "(1/4 ; 3/4)", "tx-s", "start", dx=8, dy=-4)
    f.text(1, 0, "(1 ; 0)", "tx-s", "start", dx=7, dy=-5)
    o = (0.47, 0.18)
    c.arrow(f.X(o[0]), f.Y(o[1]), f.X(o[0] - 0.16), f.Y(o[1] + 0.08), 2, "ln c2 thin")
    f.text(o[0], o[1], "−c", "tx-b t2", "start", dx=4, dy=4)
    X0 = 410
    c.text(X0, 32, "Sommets et coûts 2x₁ − x₂ :", "tx-b")
    for k, (a, b) in enumerate([("x⁰ = (0 ; 0)", "0"), ("(1 ; 0)", "2"), ("(1/4 ; 3/4)", "−1/4"), ("x¹ = (0 ; 1/2)", "−1/2  minimum")]):
        c.text(X0, 58 + 20 * k, a, "tx-s t3" if k == 3 else "tx-s")
        c.text(X0 + 100, 58 + 20 * k, b, "tx-s t3" if k == 3 else "tx-s")
    c.text(X0, 158, "Un seul pivot depuis x⁰ :", "tx-s")
    c.text(X0, 174, "x₂ entre (c̃₂ = −1), x₄ sort,", "tx-s")
    c.text(X0, 190, "ε = min(1/1, (1/2)/1) = 1/2.", "tx-s")
    c.text(X0, 210, "Puis c̃₁ = 1 et c̃₄ = 1 : optimal.", "tx-s t3")
    c.text(X0, 240, "Tirets : 2x₁ − x₂ = 1, 0, −1/2", "tx-s t2")
    c.text(X0, 256, "(de droite à gauche).", "tx-s t2")
    c.save()


# ---------------------------------------------------------------------------------------------
# Simplex tableaux of the page, computed in exact arithmetic and written as HTML fragments
# figures/P03/tab-*.html (included by the page with <!-- include figures/P03/tab-….html -->).
# The simplex below is a line-by-line port of `simplex` in app.js (same entering and leaving rules).

def simplex_exact(A, b, c, basis, rule="dantzig", max_iter=60):
    m, n = len(A), len(A[0])
    cF = [Fr(v) for v in c]
    bas = list(basis)
    T = [[Fr(v) for v in row] for row in A]
    rhs = [Fr(v) for v in b]

    def pivot(r, col):
        piv = T[r][col]
        T[r] = [v / piv for v in T[r]]
        rhs[r] = rhs[r] / piv
        for i in range(m):
            if i != r and T[i][col] != 0:
                f = T[i][col]
                T[i] = [T[i][j] - f * T[r][j] for j in range(n)]
                rhs[i] = rhs[i] - f * rhs[r]
    for k in range(m):
        col = bas[k]
        p = k
        while T[p][col] == 0:
            p += 1
        T[p], T[k] = T[k], T[p]
        rhs[p], rhs[k] = rhs[k], rhs[p]
        pivot(k, col)
    assert all(v >= 0 for v in rhs)
    steps = []
    for _ in range(max_iter + 1):
        x = [Fr(0)] * n
        for r, col in enumerate(bas):
            x[col] = rhs[r]
        red = [Fr(0) if j in bas else cF[j] - sum(cF[bas[i]] * T[i][j] for i in range(m)) for j in range(n)]
        st = dict(basis=list(bas), x=x, cost=sum(cF[j] * x[j] for j in range(n)), reduced=red, entering=-1,
                  dir=None, ratios=None, leaving=-1, eps=None, T=[r[:] for r in T], xB=rhs[:])
        steps.append(st)
        e = -1
        for j in range(n):
            if red[j] < 0 and (e < 0 or (rule != "bland" and red[j] < red[e])):
                e = j
                if rule == "bland":
                    break
        if e < 0:
            return "optimal", steps
        st["entering"] = e
        st["dir"] = [T[r][e] for r in range(m)]
        st["ratios"] = [rhs[r] / d if d > 0 else None for r, d in enumerate(st["dir"])]
        lr = -1
        for r, q in enumerate(st["ratios"]):
            if q is not None and (lr < 0 or q < st["ratios"][lr] or (q == st["ratios"][lr] and bas[r] < bas[lr])):
                lr = r
        if lr < 0:
            return "unbounded", steps
        st["leaving"], st["eps"] = lr, st["ratios"][lr]
        pivot(lr, e)
        bas[lr] = e
    return "maxiter", steps


def hname(j, nx, art="y"):
    return f"x<sub>{j + 1}</sub>" if j < nx else f"{art}<sub>{j - nx + 1}</sub>"


TINT_E = "background: color-mix(in srgb, var(--s2) 14%, transparent)"
TINT_L = "background: color-mix(in srgb, var(--s6) 14%, transparent)"
TINT_P = "background: color-mix(in srgb, var(--s3) 26%, transparent); font-weight: 700"


def tab_html(st, nx, title=None, caption=True, cost_label="c̃", art="y"):
    n = len(st["reduced"])
    e, lr = st["entering"], st["leaving"]
    h = ['<div class="table-wrap"><table style="width:auto; min-width:60%; text-align:right; font-variant-numeric: tabular-nums">']
    if title:
        h.append(f'<caption style="caption-side: top; text-align: left; font-weight: 650; padding-bottom: 0.3rem">{title}</caption>')
    h.append("<thead><tr><th>base</th>")
    for j in range(n):
        h.append(f'<th style="text-align:right{"; " + TINT_E if j == e else ""}">{hname(j, nx, art)}</th>')
    h.append('<th style="text-align:right">x<sub>B</sub></th>')
    if st["ratios"] is not None:
        h.append('<th style="text-align:right">rapport</th>')
    h.append("</tr></thead><tbody>")
    for r, col in enumerate(st["basis"]):
        h.append(f'<tr{" style=" + chr(34) + TINT_L + chr(34) if r == lr else ""}><th>{hname(col, nx, art)}</th>')
        for j in range(n):
            stl = TINT_P if (r == lr and j == e) else TINT_E if j == e else ""
            h.append(f'<td{" style=" + chr(34) + stl + chr(34) if stl else ""}>{fs(st["T"][r][j])}</td>')
        h.append(f'<td>{fs(st["xB"][r])}</td>')
        if st["ratios"] is not None:
            q = st["ratios"][r]
            h.append(f'<td>{"—" if q is None else fs(q)}</td>')
        h.append("</tr>")
    h.append(f'<tr><th style="color: var(--s2)">{cost_label}</th>')
    for j in range(n):
        h.append(f'<td style="color: var(--s2){"; " + TINT_E if j == e else ""}">{fs(st["reduced"][j])}</td>')
    h.append(f'<td>{fs(-st["cost"])}</td>')
    if st["ratios"] is not None:
        h.append("<td></td>")
    h.append("</tr></tbody></table></div>")
    if caption:
        if e >= 0 and lr >= 0:
            h.append(f'<p class="small muted">{hname(e, nx, art)} entre (c̃ = {fs(st["reduced"][e])}) ; '
                     f'rapports sur les d &gt; 0 : ε = {fs(st["eps"])}, {hname(st["basis"][lr], nx, art)} sort (case pivot en vert).</p>')
        elif e >= 0:
            h.append(f'<p class="small muted">{hname(e, nx, art)} entre (c̃ = {fs(st["reduced"][e])}) mais sa colonne est ≤ 0 : aucun rapport, problème non borné.</p>')
        else:
            h.append('<p class="small muted">Tous les coûts réduits sont ≥ 0 : optimal.</p>')
    return "".join(h)


def write_tab(name, html):
    import os
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures", SUB)
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, name + ".html"), "w") as f:
        f.write(html + "\n")


def tables():
    A421 = [[-3, 2, 1, 0, 0], [-1, 2, 0, 1, 0], [1, 1, 0, 0, 1]]
    # Ex. 4.2.1 (max x1 + 2x2), most negative rule: 4 tableaux
    st, steps = simplex_exact(A421, [2, 4, 5], [-1, -2, 0, 0, 0], [2, 3, 4])
    assert st == "optimal" and [s_["x"][:2] for s_ in steps] == [[0, 0], [0, 1], [1, Fr(5, 2)], [2, 3]]
    for k, s_ in enumerate(steps):
        write_tab(f"tab-421-{k}", tab_html(s_, 5, f"Tableau {k} — sommet {pt(s_['x'][:2])}, coût {fs(s_['cost'])}"))
    # Bland on the same problem
    st, steps = simplex_exact(A421, [2, 4, 5], [-1, -2, 0, 0, 0], [2, 3, 4], "bland")
    for k, s_ in enumerate(steps):
        write_tab(f"tab-421b-{k}", tab_html(s_, 5, f"Tableau {k} (règle de Bland) — sommet {pt(s_['x'][:2])}, coût {fs(s_['cost'])}"))
    # Ex. 4.2.3 as printed: min x1 + 2x2
    st, steps = simplex_exact(A421, [2, 4, 5], [1, 2, 0, 0, 0], [2, 3, 4])
    assert st == "optimal" and len(steps) == 1
    write_tab("tab-423-imprime", tab_html(steps[0], 5, "Tableau initial de l'exercice 4.2.3 tel qu'imprimé (min x₁ + 2x₂)"))
    # variant b3 = 7/2 (degenerate pivot), most negative rule
    st, steps = simplex_exact(A421, [2, 4, Fr(7, 2)], [-1, -2, 0, 0, 0], [2, 3, 4])
    assert steps[2]["eps"] == 0
    for k in (1, 2, 3):
        write_tab(f"tab-deg-{k}", tab_html(steps[k], 5, f"Tableau {k} — sommet {pt(steps[k]['x'][:2])}, coût {fs(steps[k]['cost'])}"))
    # Ex. 4.2.4
    st, steps = simplex_exact([[1, 1, 1, 0], [-1, 1, 0, 1]], [1, Fr(1, 2)], [2, -1, 0, 0], [2, 3])
    assert steps[-1]["x"] == [0, Fr(1, 2), Fr(1, 2), 0]
    for k, s_ in enumerate(steps):
        write_tab(f"tab-424-{k}", tab_html(s_, 4, f"Tableau {k} — sommet {pt(s_['x'][:2])}, coût {fs(s_['cost'])}"))
    # Ex. 4.2.5
    st, steps = simplex_exact([[1, 0, -3, 3], [0, 1, -8, 4]], [6, 4], [0, 0, 3, -1], [0, 1])
    assert steps[-1]["x"] == [3, 0, 0, 1] and steps[-1]["cost"] == -1
    for k, s_ in enumerate(steps):
        write_tab(f"tab-425-{k}", tab_html(s_, 4, f"Tableau {k} — x = ({', '.join(fs(v) for v in s_['x'])}), coût {fs(s_['cost'])}"))
    # Phase I example: x1 + x2 >= 2, x1 - x2 <= 1, x2 <= 3 ; first row multiplied by -1 ; artificials y1, y2, y3
    At = [[1, 1, -1, 0, 0], [1, -1, 0, 1, 0], [0, 1, 0, 0, 1]]
    Ab = [row + [int(i == k) for k in range(3)] for i, row in enumerate(At)]
    st, steps = simplex_exact(Ab, [2, 1, 3], [0] * 5 + [1] * 3, [5, 6, 7])
    assert steps[-1]["cost"] == 0 and steps[-1]["basis"] == [1, 0, 4]
    for k, s_ in enumerate(steps):
        write_tab(f"tab-p1-{k}", tab_html(s_, 5, f"Phase I, tableau {k} — (x₁ ; x₂) = {pt(s_['x'][:2])}, Σ yᵢ = {fs(s_['cost'])}", cost_label="c̃ (phase I)"))
    st, steps = simplex_exact(At, [2, 1, 3], [2, 1, 0, 0, 0], [1, 0, 4])
    assert steps[-1]["x"][:2] == [0, 2] and steps[-1]["cost"] == 2
    for k, s_ in enumerate(steps):
        write_tab(f"tab-p2-{k}", tab_html(s_, 5, f"Phase II, tableau {k} — sommet {pt(s_['x'][:2])}, coût 2x₁ + x₂ = {fs(s_['cost'])}"))
    # an artificial variable left in the basis at zero: A = [[3,1,2],[2,1,1]], b = (1,1)
    st, steps = simplex_exact([[3, 1, 2, 1, 0], [2, 1, 1, 0, 1]], [1, 1], [0, 0, 0, 1, 1], [3, 4])
    fin = steps[-1]
    assert fin["cost"] == 0 and fin["basis"] == [1, 4] and fin["xB"] == [1, 0]
    write_tab("tab-art", tab_html(fin, 3, f"Fin de la phase I — Σ yᵢ = 0, mais y₂ est encore en base (à la valeur 0)", cost_label="c̃ (phase I)"))
    # supplementary exercises
    st, steps = simplex_exact([[-1, 1, 1, 0], [1, -2, 0, 1]], [1, 2], [-1, -1, 0, 0], [2, 3])
    assert st == "unbounded"
    for k, s_ in enumerate(steps):
        write_tab(f"tab-s2-{k}", tab_html(s_, 4, f"Tableau {k} — sommet {pt(s_['x'][:2])}, coût {fs(s_['cost'])}"))
    st, steps = simplex_exact([[1, 1, 1, 0, 0], [1, 3, 0, 1, 0], [1, 0, 0, 0, 1]], [4, 6, 3], [-3, -2, 0, 0, 0], [2, 3, 4])
    assert steps[-1]["x"][:2] == [3, 1]
    for k, s_ in enumerate(steps):
        write_tab(f"tab-s3-{k}", tab_html(s_, 5, f"Tableau {k} — sommet {pt(s_['x'][:2])}, coût {fs(s_['cost'])}"))
    st, steps = simplex_exact([[1, 2, -1, 0, 1, 0], [1, 1, 0, 1, 0, 1]], [6, 2], [0, 0, 0, 0, 1, 1], [4, 5])
    assert steps[-1]["cost"] == 2
    for k, s_ in enumerate(steps):
        write_tab(f"tab-s4-{k}", tab_html(s_, 4, f"Phase I, tableau {k} — Σ yᵢ = {fs(s_['cost'])}", cost_label="c̃ (phase I)"))
    st, steps = simplex_exact([[1, 1, 1, 1, 0], [-1, 0, 1, 0, 1]], [3, 1], [0, 0, 0, 1, 1], [3, 4])
    assert steps[-1]["cost"] == 0 and sorted(steps[-1]["basis"]) == [0, 2]
    for k, s_ in enumerate(steps):
        write_tab(f"tab-s5-{k}", tab_html(s_, 3, f"Phase I, tableau {k} — x = ({', '.join(fs(v) for v in s_['x'][:3])}), Σ yᵢ = {fs(s_['cost'])}", cost_label="c̃ (phase I)"))
    st, steps = simplex_exact([[1, 1, 1], [-1, 0, 1]], [3, 1], [2, 1, 3], [0, 2])
    assert steps[-1]["x"] == [0, 2, 1] and steps[-1]["cost"] == 5
    for k, s_ in enumerate(steps):
        write_tab(f"tab-s5b-{k}", tab_html(s_, 3, f"Phase II, tableau {k} — x = ({', '.join(fs(v) for v in s_['x'])}), coût {fs(s_['cost'])}"))
    print("wrote the tableaux")


if __name__ == "__main__":
    fig_idee()
    fig_pentes()
    fig_rapport()
    fig_anatomie()
    fig_degenere()
    fig_chemins()
    fig_klee_minty()
    fig_phases()
    fig_lad()
    fig_ex424()
    tables()
