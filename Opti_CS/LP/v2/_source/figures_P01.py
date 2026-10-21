"""figures_P01.py — figures statiques de la partie 1 (modéliser, forme standard, géométrie, existence), écrites dans figures/P01/.

Lancer : python3 figures_P01.py        (puis node build.mjs Partie01.html)
Toutes les coordonnées sont calculées ici ; les nombres affichés sont vérifiés par les scripts du dossier verify_P01.
Code couleur (GUIDE.md §5) : X_ad = 1 (bleu), coût / lignes de niveau = 2, optimum = 3 (vert), contraintes en gris.
"""
import math

import numpy as np

from figures_common import Canvas, Fig

SUB = "P01"


def line_in_box(a, b, r, xr, yr):
    """Les deux extrémités du segment {a x + b y = r} dans la boîte xr × yr."""
    pts = []
    if abs(b) > 1e-12:
        for x in xr:
            y = (r - a * x) / b
            if yr[0] - 1e-9 <= y <= yr[1] + 1e-9:
                pts.append((x, y))
    if abs(a) > 1e-12:
        for y in yr:
            x = (r - b * y) / a
            if xr[0] - 1e-9 <= x <= xr[1] + 1e-9:
                pts.append((x, y))
    best, d = None, -1
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            dd = math.dist(pts[i], pts[j])
            if dd > d:
                d, best = dd, (pts[i], pts[j])
    return best


def half_plane_polygon(cons, xr, yr):
    """Polygone {a x + b y <= r pour tout (a, b, r)} ∩ boîte (Sutherland–Hodgman)."""
    P = [(xr[0], yr[0]), (xr[1], yr[0]), (xr[1], yr[1]), (xr[0], yr[1])]
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


def cline(f, a, b, r, cls="ln cm thin"):
    seg = line_in_box(a, b, r, f.xr, f.yr)
    if seg:
        f.line(seg[0][0], seg[0][1], seg[1][0], seg[1][1], cls)
    return seg


def farrow(c, f, x1, y1, x2, y2, k, cls=None):
    c.arrow(f.X(x1), f.Y(y1), f.X(x2), f.Y(y2), k, cls)


# ---------------------------------------------------------------------------------------------
def fig_atelier():
    c = Canvas("atelier", 660, 420, "Atelier : polygone des plans de production admissibles, lignes de niveau du profit et optimum (30, 40)", sub=SUB)
    f = Fig(c, (58, 18, 400, 360), (0, 80), (0, 72))
    f.axes(xticks=[0, 10, 20, 30, 40, 50, 60, 70, 80], yticks=[0, 10, 20, 30, 40, 50, 60, 70], xlabel="x₁ (bureaux)", ylabel="x₂ (étagères)")
    poly = [(0, 0), (50, 0), (30, 40), (15, 55), (0, 60)]
    f.path(poly, "a1", close=True)
    f.path(poly, "ln c1", close=True)
    cline(f, 2, 1, 100)
    cline(f, 1, 1, 70)
    cline(f, 1, 3, 180)
    f.text(47, 9, "machines", "tx-s", "start")
    f.text(62, 11, "main-d'œuvre", "tx-s", "start")
    f.text(68, 112 / 3, "bois", "tx-s", "start", dx=0, dy=-6)
    # lignes de niveau du profit 40 x1 + 30 x2
    s = cline(f, 40, 30, 1200, "ln c2 thin dash")
    s = cline(f, 40, 30, 2400, "ln c2")
    f.text(12, 26, "profit 1200 €", "tx-s t2", "start")   # à droite de la ligne pointillée, dans le polygone
    # gradient
    g = np.array([4, 3]) / 5 * 12
    farrow(c, f, 30, 40, 30 + g[0], 40 + g[1], 2)
    f.text(30 + g[0], 40 + g[1], "c = (40, 30)", "tx-s t2", "start", dx=4, dy=-2)
    # sommets : les étiquettes près des points seraient coupées par les droites ; les valeurs sont listées à droite
    for (x, y) in [(0, 0), (50, 0), (15, 55), (0, 60)]:
        f.circle(x, y, 4, "f1")
    f.text(0, 0, "0 €", "tx-s", "start", dx=6, dy=-6)
    f.text(50, 0, "2000 €", "tx-s", "end", dx=-10, dy=-8)
    f.circle(30, 40, 6, "f3")
    f.text(30, 40, "(30, 40) : 2400 €", "tx-b t3", "end", dx=-9, dy=4)
    # légende à droite
    x0 = 478
    c.text(x0, 60, "Contraintes (gris) :", "tx-b")
    c.text(x0, 80, "machines  2x₁ + x₂ ≤ 100", "tx-s")
    c.text(x0, 97, "main-d'œuvre  x₁ + x₂ ≤ 70", "tx-s")
    c.text(x0, 114, "bois  x₁ + 3x₂ ≤ 180", "tx-s")
    c.text(x0, 131, "et x₁ ≥ 0, x₂ ≥ 0 (les axes)", "tx-s")
    c.text(x0, 165, "Profit : 40x₁ + 30x₂", "tx-b t2")
    c.text(x0, 183, "lignes de niveau ⟂ c :", "tx-s t2")
    c.text(x0, 199, "pointillé 1200 €, plein 2400 €", "tx-s t2")
    c.text(x0, 233, "Optimum : le dernier", "tx-b t3")
    c.text(x0, 251, "point touché quand la", "tx-s t3")
    c.text(x0, 268, "ligne de niveau avance", "tx-s t3")
    c.text(x0, 285, "dans la direction de c", "tx-s t3")
    c.text(x0, 318, "Sommets → profit :", "tx-b")
    for k, (lab, cls) in enumerate([("(0, 0) → 0 €", "tx-s"), ("(50, 0) → 2000 €", "tx-s"), ("(30, 40) → 2400 €", "tx-s tx-b t3"),
                                    ("(15, 55) → 2250 €", "tx-s"), ("(0, 60) → 1800 €", "tx-s")]):
        c.text(x0, 336 + 16 * k, lab, cls)
    c.save()


def fig_ex421():
    c = Canvas("ex421", 660, 410, "Exercice 4.2.1 : polygone admissible, trois contraintes étiquetées, sommets et valeurs de x1 + 2 x2", sub=SUB)
    f = Fig(c, (56, 14, 490, 364), (-0.6, 6.4), (-0.6, 4.6))
    f.axes(xticks=[0, 1, 2, 3, 4, 5, 6], yticks=[0, 1, 2, 3, 4], xlabel="x₁", ylabel="x₂")
    poly = [(0, 0), (5, 0), (2, 3), (1, 2.5), (0, 1)]
    f.path(poly, "a1", close=True)
    f.path(poly, "ln c1", close=True)
    cline(f, -3, 2, 2)
    cline(f, -1, 2, 4)
    cline(f, 1, 1, 5)
    f.text(2.4, 4.6, "(1)  −3x₁ + 2x₂ ≤ 2", "tx-s", "end", dx=-16, dy=12)
    f.text(5.2, 4.6, "(2)  −x₁ + 2x₂ ≤ 4", "tx-s", "end", dx=-30, dy=10)
    f.text(5.0, 0, "(3)  x₁ + x₂ ≤ 5", "tx-s", "start", dx=10, dy=-30)
    # lignes de niveau de x1 + 2 x2
    cline(f, 1, 2, 4, "ln c2 thin dash")
    cline(f, 1, 2, 8, "ln c2")
    f.text(2.1, 1.08, "coût 4", "tx-s t2", "start")
    f.text(5.6, 1.25, "coût 8", "tx-s t2", "start")
    d = np.array([1, 2]) / math.sqrt(5) * 0.9
    farrow(c, f, 2, 3, 2 + d[0], 3 + d[1], 2)
    f.text(2 + d[0], 3 + d[1], "c = (1, 2)", "tx-s t2", "start", dx=6, dy=4)
    for (x, y), lab, anc, dx, dy in [((0, 0), "(0, 0) → 0", "start", 6, -6), ((5, 0), "(5, 0) → 5", "start", 8, -6),
                                       ((1, 2.5), "(1, 5/2) → 6", "end", -8, -4), ((0, 1), "(0, 1) → 2", "start", 8, 4)]:
        f.circle(x, y, 4, "f1")
        f.text(x, y, lab, "tx-s", anc, dx=dx, dy=dy)
    f.circle(2, 3, 6, "f3")
    f.text(2, 3, "(2, 3) → 8 : optimum", "tx-b t3", "start", dx=22, dy=5)
    c.text(560, 120, "Xad (bleu)", "tx-b t1")
    c.text(560, 138, "= les 5 inégalités", "tx-s")
    c.text(560, 154, "(1), (2), (3),", "tx-s")
    c.text(560, 170, "x₁ ≥ 0, x₂ ≥ 0", "tx-s")
    c.save()


# --- projection oblique pour l'exemple (4.5) ---
def P3(x1, x2, x3, o=(178, 214)):
    return (o[0] - 36 * x1 + 60 * x2, o[1] + 30 * x1 - 66 * x3)


def fig_triangle():
    c = Canvas("triangle", 660, 340, "Le triangle T de l'exemple (4.5) en perspective, ses sommets, les valeurs du coût et des lignes de niveau sur T", sub=SUB)
    O = P3(0, 0, 0)
    for end, lab in [((3.7, 0, 0), "x₁"), ((0, 7.2, 0), "x₂"), ((0, 0, 2.75), "x₃")]:
        e = P3(*end)
        c.arrow(O[0], O[1], e[0], e[1], "k", "ax")
        c.text(e[0] + (6 if lab != "x₁" else -24), e[1] + (4 if lab != "x₃" else -4), lab, "tx-i")
    A, B, C = (3, 0, 0), (0, 6, 0), (0, 0, 2)
    pts = [P3(*A), P3(*B), P3(*C)]
    d = "M" + " L".join(f"{p[0]:.1f} {p[1]:.1f}" for p in pts) + "Z"
    c.add(f'<path d="{d}" class="a1"/>')
    c.add(f'<path d="{d}" class="ln c1"/>')
    # lignes de niveau x1 + 4 x2 + 2 x3 = g sur T
    cost = np.array([1, 4, 2])
    V = [np.array(A, float), np.array(B, float), np.array(C, float)]
    vals = [cost @ v for v in V]
    for g in [4, 10, 16]:
        seg = []
        for i, j in [(0, 1), (1, 2), (0, 2)]:
            vi, vj = vals[i], vals[j]
            if (vi - g) * (vj - g) <= 0 and vi != vj:
                t = (g - vi) / (vj - vi)
                p = V[i] + t * (V[j] - V[i])
                if not any(np.allclose(p, q) for q in seg):
                    seg.append(p)
        if len(seg) == 2:
            p, q = P3(*seg[0]), P3(*seg[1])
            c.add(f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}" class="ln c2 thin dash"/>')
            m = P3(*(0.35 * seg[0] + 0.65 * seg[1]))
            c.text(m[0] + 5, m[1] - 4, f"coût {g}", "tx-s t2")
    # direction de plus forte descente sur T : −(projection de c sur le plan de T)
    G = np.array([1.0, 2.0, 2 / 3])
    n = np.array([2, 1, 3])
    pc = cost - (cost @ n) / (n @ n) * n
    dvec = -pc / np.linalg.norm(pc) * 1.6
    g0, g1 = P3(*G), P3(*(G + dvec))
    c.arrow(g0[0], g0[1], g1[0], g1[1], 3, "ln c3 thin")
    c.add(f'<circle cx="{g0[0]:.1f}" cy="{g0[1]:.1f}" r="3" class="fk"/>')
    c.text(g0[0] + 8, g0[1] + 4, "descente dans T", "tx-s t3")
    # sommets
    for v, lab, dx, dy, cls in [(A, "(3, 0, 0) : coût 3 — minimum", -10, 22, "tx-b t3"), (B, "(0, 6, 0) : coût 24", -20, 22, "tx-s"),
                                (C, "(0, 0, 2) : coût 4", 10, -8, "tx-s")]:
        p = P3(*v)
        c.add(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="{6 if v == A else 4}" class="{"f3" if v == A else "f1"}"/>')
        c.text(p[0] + dx, p[1] + dy, lab, cls)
    c.text(430, 60, "T = {x ≥ 0 : 2x₁ + x₂ + 3x₃ = 6}", "tx-b t1")
    c.text(430, 80, "coût x₁ + 4x₂ + 2x₃", "tx-s t2")
    c.text(430, 98, "pointillés : lignes de niveau sur T", "tx-s t2")
    c.save()


def fig_issues():
    c = Canvas("issues", 660, 290, "Les trois issues d'un programme linéaire : ensemble vide, valeur moins l'infini, optimum atteint", sub=SUB)
    titles = ["(a) Xad vide : valeur +∞", "(b) non borné : valeur −∞", "(c) optimum atteint"]
    for k in range(3):
        x0 = 22 + k * 216
        f = Fig(c, (x0, 34, 190, 190), (-0.4, 4.6), (-0.4, 4.6))
        f.line(-0.4, 0, 4.6, 0, "ax")
        f.line(0, -0.4, 0, 4.6, "ax")
        c.text(x0 + 95, 20, titles[k], "tx-b", "middle")
        if k == 0:
            P1 = half_plane_polygon([(1, 1, 1), (-1, 0, 0), (0, -1, 0)], f.xr, f.yr)
            P2 = half_plane_polygon([(-1, -1, -3), (-1, 0, 0), (0, -1, 0)], f.xr, f.yr)
            f.path(P1, "am", close=True)
            f.path(P2, "am", close=True)
            cline(f, 1, 1, 1)
            cline(f, 1, 1, 3)
            f.text(0.15, 0.25, "x₁+x₂ ≤ 1", "tx-s", "start")
            f.text(2.1, 2.3, "x₁+x₂ ≥ 3", "tx-s", "start")
            c.text(x0 + 95, 250, "aucun point ne vérifie tout :", "tx-s", "middle")
            c.text(x0 + 95, 266, "inf sur ∅ = +∞ (convention)", "tx-s", "middle")
        else:
            cons = [(-1, 1, 1), (1, -1, 2), (-1, 0, 0), (0, -1, 0)]
            P = half_plane_polygon(cons, f.xr, f.yr)
            f.path(P, "a1", close=True)
            # bord de Xad (sans les côtés de la boîte)
            f.path([(3.6, 4.6), (0, 1), (0, 0), (2, 0), (4.6, 2.6)], "ln c1")   # coupé au bord de la boîte (−x₁ + x₂ = 1 en x₂ = 4,6)
            if k == 1:
                for g in [1, 3, 5, 7]:
                    cline(f, 1, 1, g, "ln c2 thin dash")
                farrow(c, f, 1.6, 1.6, 3.6, 3.6, 2)
                f.text(3.6, 3.6, "−c", "tx-s t2", "start", dx=6, dy=12)
                c.text(x0 + 95, 250, "min −x₁ − x₂ : on descend", "tx-s", "middle")
                c.text(x0 + 95, 266, "sans fin le long de (1, 1)", "tx-s", "middle")
            else:
                for g in [-2, 0, 2]:
                    cline(f, -1, 2, g, "ln c2 thin dash" if g != -2 else "ln c2")
                farrow(c, f, 2.6, 2.2, 3.1, 1.2, 2)
                f.text(3.1, 1.2, "−c", "tx-s t2", "start", dx=4, dy=8)
                f.circle(2, 0, 6, "f3")
                f.text(2, 0, "(2, 0) : −2", "tx-b t3", "middle", dy=24)
                c.text(x0 + 95, 250, "même Xad, min −x₁ + 2x₂ :", "tx-s", "middle")
                c.text(x0 + 95, 266, "minimum −2 atteint en (2, 0)", "tx-s", "middle")
    c.save()


def fig_xpm():
    c = Canvas("xpm", 660, 292, "x = x+ − x− : les parties positive et négative, et tous les couples (x+, x−) qui représentent le même x", sub=SUB)
    f = Fig(c, (40, 40, 260, 190), (-3, 3), (-3, 3))
    f.axes(xticks=[-3, -2, -1, 0, 1, 2, 3], yticks=[-2, 0, 2], grid=False)
    f.fn(lambda x: max(0, x), "ln c1", -3, 3, 600)
    f.fn(lambda x: max(0, -x), "ln c5 dash", -3, 3, 600)
    f.text(3.0, 0.6, "x⁺ = max(0, x)", "tx-s t1", "end")
    f.text(-3.0, 0.6, "x⁻ = max(0, −x)", "tx-s t5", "start")
    f.text(3, -3, "x", "tx-i", "end", dy=-4)
    c.text(170, 18, "parties positive et négative", "tx-b", "middle")
    c.text(170, 282, "x = x⁺ − x⁻ et |x| = x⁺ + x⁻", "tx-s", "middle")
    g = Fig(c, (390, 40, 200, 190), (0, 4.2), (0, 4.2))
    g.axes(xticks=[0, 1, 2, 3, 4], yticks=[2, 3, 4], grid=True, xlabel="x⁺", ylabel="x⁻")
    g.line(0, 1, 3.2, 4.2, "ln c1")
    g.line(2, 0, 4.2, 2.2, "ln c1 thin")
    g.circle(0, 1, 6, "f3")
    g.circle(2, 3, 4.5, "fm")
    g.circle(2, 0, 5, "f3")
    g.text(0, 1, "(0, 1)", "tx-b t3", "start", dx=8, dy=12)
    g.text(2, 3, "(2, 3)", "tx-s", "end", dx=-8, dy=-2)
    g.text(3.0, 4.0, "x = −1", "tx-s t1", "start", dx=8, dy=8)
    g.text(4.2, 2.2, "x = 2", "tx-s t1", "start", dx=4, dy=4)
    c.text(490, 18, "tous les (x⁺, x⁻) ≥ 0 avec x⁺ − x⁻ = x", "tx-b", "middle")
    c.text(490, 282, "vert : le seul sommet de chaque demi-droite", "tx-s", "middle")
    c.save()


def fig_epi():
    c = Canvas("epigraphe", 660, 290, "Linéariser |x| et un maximum de fonctions affines : l'épigraphe est une intersection de demi-plans", sub=SUB)
    f = Fig(c, (40, 34, 240, 200), (-2.2, 2.2), (-0.4, 2.6))
    f.axes(xticks=[-2, -1, 0, 1, 2], yticks=[1, 2], grid=False)
    P = half_plane_polygon([(1, -1, 0), (-1, -1, 0)], f.xr, f.yr)
    f.path(P, "a1", close=True)
    cline(f, 1, -1, 0)
    cline(f, -1, -1, 0)
    f.fn(abs, "ln c1", -2.2, 2.2, 400)
    f.text(1.9, 1.9, "t ≥ x", "tx-s", "end", dx=-10, dy=0)
    f.text(-1.9, 1.9, "t ≥ −x", "tx-s", "start", dx=10, dy=0)
    f.text(0, 2.2, "t ≥ |x|", "tx-b t1", "middle")
    f.circle(0, 0, 5, "f3")
    f.text(2.2, -0.4, "x", "tx-i", "end", dy=-4)
    f.text(-2.2, 2.6, "t", "tx-i", "start", dx=4, dy=12)
    c.text(160, 20, "min |x| : min t, t ≥ x, t ≥ −x", "tx-b", "middle")
    g = Fig(c, (360, 34, 270, 200), (-1, 5), (-0.6, 4.2))
    g.axes(xticks=[-1, 0, 1, 2, 3, 4, 5], yticks=[1, 2, 3, 4], grid=False)
    cons = [(-1, -1, -2), (0.5, -1, -0.5), (2, -1, 4)]   # t >= 2 - x ; t >= x/2 + 1/2 ; t >= 2x - 4  (écrits a x + b t <= r)
    P = half_plane_polygon(cons, g.xr, g.yr)
    g.path(P, "a1", close=True)
    for a, b, r in cons:
        cline(g, a, b, r)
    gfun = lambda x: max(2 - x, x / 2 + 0.5, 2 * x - 4)
    g.fn(gfun, "ln c1", -1, 5, 600)
    g.text(-0.85, 3.1, "t ≥ 2 − x", "tx-s", "start")
    g.text(5.0, 1.9, "t ≥ x/2 + 1/2", "tx-s", "end")
    g.text(3.6, 3.2, "t ≥ 2x − 4", "tx-s", "end", dx=-8, dy=0)
    g.circle(1, 1, 6, "f3")
    g.text(1, 1, "(1, 1)", "tx-b t3", "middle", dy=20)
    c.text(495, 20, "min max(2 − x, x/2 + 1/2, 2x − 4)", "tx-b", "middle")
    c.text(330, 276, "bleu : l'épigraphe {(x, t) : t ≥ f(x)}, intersection de demi-plans ; vert : le point bas, solution du PL", "tx-s", "middle")
    c.save()


def fig_lad():
    c = Canvas("lad", 660, 330, "Régression : moindres valeurs absolues (LAD) contre moindres carrés, avec un point aberrant", sub=SUB)
    f = Fig(c, (50, 16, 420, 270), (-0.5, 5.5), (-1, 13))
    f.axes(xticks=[0, 1, 2, 3, 4, 5], yticks=[0, 2, 4, 6, 8, 10, 12], xlabel="x", ylabel="y")
    xs = [0, 1, 2, 3, 4, 5]
    ys = [1, 2, 3, 3, 5, 12]
    for x, y in zip(xs, ys):
        f.line(x, y, x, x + 1, "ln c3 hair dash")
    f.fn(lambda x: x + 1, "ln c3", -0.5, 5.5)
    w, b = 64 / 35, -5 / 21
    f.fn(lambda x: w * x + b, "ln c5 dash", -0.5, 5.5)
    for x, y in zip(xs, ys):
        f.circle(x, y, 4.5, "fk")
    f.text(5, 12, "point aberrant", "tx-s", "end", dx=-10, dy=4)
    f.text(5.5, 3.6, "LAD : y = x + 1", "tx-b t3", "end")
    f.text(5.5, w * 5.5 + b, "moindres carrés", "tx-s t5", "end", dx=-30, dy=-6)
    x0 = 488
    c.text(x0, 40, "LAD (vert) :", "tx-b t3")
    c.text(x0, 58, "min Σ |yᵢ − (w xᵢ + b)|", "tx-s")
    c.text(x0, 75, "w = 1, b = 1 ; passe par", "tx-s")
    c.text(x0, 92, "4 des 6 points", "tx-s")
    c.text(x0, 126, "Moindres carrés (violet) :", "tx-b t5")
    c.text(x0, 144, "min Σ (yᵢ − (w xᵢ + b))²", "tx-s")
    c.text(x0, 161, "w = 64/35 ≈ 1,83", "tx-s")
    c.text(x0, 178, "b = −5/21 ≈ −0,24", "tx-s")
    c.text(x0, 212, "pointillés verts : les", "tx-s t3")
    c.text(x0, 229, "résidus de LAD (0, 0, 0,", "tx-s t3")
    c.text(x0, 246, "−1, 0, 6) : somme 7", "tx-s t3")
    c.save()


def fig_cone():
    c = Canvas("cone", 660, 360, "Preuve de l'existence : le cône C engendré par les colonnes (a_i, c_i), la verticale t = b et les coûts réalisables", sub=SUB)
    f = Fig(c, (60, 16, 380, 300), (-1, 6), (-6, 10))
    f.axes(xticks=[0, 1, 2, 3, 4, 5, 6], yticks=[-6, -4, -2, 0, 2, 4, 6, 8, 10], grid=False, xlabel="t = a·x", ylabel="y = c·x")
    cols = [(1, 2), (2, 1), (1, -1)]
    # cône : secteur entre (1, -1) et (1, 2), découpé dans la boîte
    P = half_plane_polygon([(-2, 1, 0), (-1, -1, 0)], f.xr, f.yr)   # y <= 2t et y >= -t
    f.path(P, "am", close=True)
    for a, cc in [(1, 2), (1, -1)]:
        s = 6 if a * 6 * abs(cc) <= 10 else 5
        f.line(0, 0, 5, 5 * cc, "ln cm thin")
    f.line(0, 0, 6, 3, "ln cm thin")
    for (a, cc), lab, dx, dy in zip(cols, ["𝒜₁ = (1, 2)", "𝒜₂ = (2, 1)", "𝒜₃ = (1, −1)"], [-6, 8, -6], [-6, 14, 16]):
        f.circle(a, cc, 5, "fk")
        f.text(a, cc, lab, "tx-s", "end" if dx < 0 else "start", dx=dx, dy=dy)
    b = 4
    f.line(b, -6, b, 10, "ln cm thin dash")
    f.line(b, -4, b, 8, "ln c1")
    for y in [6, 3, 0, -2, -3, -3.5]:
        f.circle(b, y, 3, "f2")
    farrow(c, f, b + 0.35, 5.5, b + 0.35, -3.6, 2, "ln c2 thin")
    f.text(b, 8, "(b, 8)", "tx-s", "start", dx=8, dy=4)
    f.circle(b, -4, 6, "f3")
    f.text(b, -4, "(b, z₀) = (4, −4) ∈ C", "tx-b t3", "end", dx=-10, dy=14)
    f.text(b + 0.35, 1.5, "c·xᵏ ↓ z₀", "tx-s t2", "start", dx=6, dy=0)
    x0 = 470
    c.text(x0, 40, "Exemple : min 2x₁ + x₂ − x₃", "tx-b")
    c.text(x0, 57, "x ≥ 0, x₁ + 2x₂ + x₃ = 4", "tx-s")
    c.text(x0, 85, "gris : le cône C des", "tx-s")
    c.text(x0, 101, "combinaisons Σ xᵢ 𝒜ᵢ, xᵢ ≥ 0", "tx-s")
    c.text(x0, 129, "bleu : C ∩ {t = b} =", "tx-s t1")
    c.text(x0, 145, "les coûts réalisables", "tx-s t1")
    c.text(x0, 161, "= [−4, 8], fermé", "tx-s t1")
    c.text(x0, 189, "orange : une suite", "tx-s t2")
    c.text(x0, 205, "minimisante (b, c·xᵏ)", "tx-s t2")
    c.text(x0, 233, "vert : sa limite reste", "tx-s t3")
    c.text(x0, 249, "dans C (C est fermé)", "tx-s t3")
    c.save()


def fig_expinf():
    c = Canvas("expinf", 660, 270, "Un convexe fermé où le minimum d'un coût linéaire n'est pas atteint, et un polyèdre où il l'est", sub=SUB)
    f = Fig(c, (40, 34, 250, 180), (-0.3, 6), (-0.3, 1.6))
    f.axes(xticks=[0, 1, 2, 3, 4, 5, 6], yticks=[1], grid=False)
    xs = np.linspace(0, 6, 300)
    pts = [(0, 1.6), (0, 1)] + [(x, math.exp(-x)) for x in xs] + [(6, 1.6)]
    f.path(pts, "a1", close=True)
    f.fn(lambda x: math.exp(-x), "ln c1", 0, 6)
    f.line(0, 1, 0, 1.6, "ln c1")
    f.text(3, 0.9, "K = {x ≥ 0, y ≥ e⁻ˣ}", "tx-s t1", "middle")
    f.text(6, 0.3, "inf y = 0, jamais atteint", "tx-s t2", "end")
    c.text(165, 20, "convexe fermé, coût y : pas de minimum", "tx-b", "middle")
    g = Fig(c, (380, 34, 250, 180), (-0.3, 6), (-0.3, 1.6))
    g.axes(xticks=[0, 1, 2, 3, 4, 5, 6], yticks=[1], grid=False)
    P = half_plane_polygon([(-1, -2, -2), (-1, 0, 0), (0, -1, 0)], g.xr, g.yr)
    g.path(P, "a1", close=True)
    g.path([(0, 1.6), (0, 1), (2, 0), (6, 0)], "ln c1")
    g.line(2, 0, 6, 0, "ln c3")
    g.circle(2, 0, 5, "f3")
    g.text(3, 0.9, "x ≥ 0, x₁ + 2x₂ ≥ 2", "tx-s t1", "middle")
    g.text(6, 0.3, "min x₂ = 0, atteint", "tx-s t3", "end")
    c.text(505, 20, "polyèdre, coût x₂ : minimum atteint", "tx-b", "middle")
    c.text(330, 252, "à gauche, les valeurs de y forment ]0, +∞[ (pas fermé) ; à droite, les valeurs de x₂ forment [0, +∞[ (fermé)", "tx-s", "middle")
    c.save()


if __name__ == "__main__":
    fig_atelier()
    fig_ex421()
    fig_triangle()
    fig_issues()
    fig_xpm()
    fig_epi()
    fig_lad()
    fig_cone()
    fig_expinf()
