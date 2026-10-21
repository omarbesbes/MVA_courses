"""figures_P06.py — figures statiques de la partie 6 (nombres entiers et totale unimodularité), écrites dans figures/P06/.

Lancer : python3 figures_P06.py        (puis node build.mjs Partie06.html)
Toutes les coordonnées sont calculées ici ; les nombres affichés sont vérifiés par les scripts de verify_P06.
Code couleur : P (admissible) = 1, coût / lignes de niveau = 2, optimum continu = 3, points entiers = 4,
objets non admissibles = 6, droites de contraintes en gris.
"""
import itertools
import math
from fractions import Fraction as F

from figures_common import Canvas, Fig, esc

SUB = "P06"


# ------------------------------------------------------------------------------------------- outils
def cross(c, x, y, s, cls="ln c6"):
    c.add(f'<line x1="{x - s:.1f}" y1="{y - s:.1f}" x2="{x + s:.1f}" y2="{y + s:.1f}" class="{cls}"/>')
    c.add(f'<line x1="{x - s:.1f}" y1="{y + s:.1f}" x2="{x + s:.1f}" y2="{y - s:.1f}" class="{cls}"/>')


def square(c, x, y, s, cls):
    c.add(f'<rect x="{x - s:.1f}" y="{y - s:.1f}" width="{2 * s:.1f}" height="{2 * s:.1f}" class="{cls}"/>')


def ring(c, x, y, r, cls="ln ck thin nofill"):
    c.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" class="{cls}"/>')


def hull(points):
    """Enveloppe convexe (chaîne monotone), sens trigonométrique."""
    P = sorted(set(points))
    if len(P) < 3:
        return P

    def cr(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in P:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(P):
        while len(up) >= 2 and cr(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def vertices(cons):
    """Sommets exacts de {a x + b y <= r}."""
    V = set()
    for (a1, b1, r1), (a2, b2, r2) in itertools.combinations(cons, 2):
        d = a1 * b2 - a2 * b1
        if d == 0:
            continue
        x, y = F(r1 * b2 - b1 * r2, d), F(a1 * r2 - a2 * r1, d)
        if all(a * x + b * y <= r for a, b, r in cons):
            V.add((x, y))
    V = list(V)
    cx = sum(v[0] for v in V) / len(V)
    cy = sum(v[1] for v in V) / len(V)
    V.sort(key=lambda v: math.atan2(v[1] - cy, v[0] - cx))
    return V


def legend_item(c, x, y, kind, text, cls_text="tx-s"):
    if kind == "opt":
        c.add(f'<circle cx="{x:.1f}" cy="{y - 4:.1f}" r="6" class="f3"/>')
    elif kind == "int":
        c.add(f'<circle cx="{x:.1f}" cy="{y - 4:.1f}" r="6.5" class="f4"/>')
        ring(c, x, y - 4, 9.5)
    elif kind == "pt":
        c.add(f'<circle cx="{x:.1f}" cy="{y - 4:.1f}" r="3.5" class="f4"/>')
    elif kind == "bad":
        cross(c, x, y - 4, 5)
    elif kind == "round":
        square(c, x, y - 4, 4.5, "fm")
    elif kind == "level":
        c.add(f'<line x1="{x - 9:.1f}" y1="{y - 4:.1f}" x2="{x + 9:.1f}" y2="{y - 4:.1f}" class="ln c2 dash"/>')
    elif kind == "level2":
        c.add(f'<line x1="{x - 9:.1f}" y1="{y - 4:.1f}" x2="{x + 9:.1f}" y2="{y - 4:.1f}" class="ln c2 thin"/>')
    elif kind == "P":
        c.add(f'<rect x="{x - 9:.1f}" y="{y - 10:.1f}" width="18" height="12" class="a1"/>')
        c.add(f'<rect x="{x - 9:.1f}" y="{y - 10:.1f}" width="18" height="12" class="ln c1 thin nofill"/>')
    elif kind == "hull":
        c.add(f'<rect x="{x - 9:.1f}" y="{y - 10:.1f}" width="18" height="12" class="a4"/>')
        c.add(f'<rect x="{x - 9:.1f}" y="{y - 10:.1f}" width="18" height="12" class="ln c4 thin nofill dash"/>')
    c.text(x + 16, y, text, cls_text)


def lattice(f, xs, ys, feas):
    for i in xs:
        for j in ys:
            if feas(i, j):
                f.circle(i, j, 3.5, "f4")
            else:
                f.circle(i, j, 1.8, "fm")


# ------------------------------------------------------------------------------------------- 1. diapo 18
def fig_diapo18():
    c = Canvas("diapo18", 660, 380, "Diapo 18 redessinée : maximiser 10x1 + 11x2 sous 10x1 + 12x2 <= 59, x entier positif", sub=SUB)
    f = Fig(c, (44, 18, 360, 310), (-0.3, 6.6), (-0.3, 5.6))
    f.axes(xticks=range(0, 7), yticks=range(0, 6), xlabel="x₁", ylabel="x₂")
    L = 59
    f.path([(0, 0), (L / 10, 0), (0, L / 12)], "a1", close=True)
    f.path([(0, 0), (L / 10, 0), (0, L / 12)], "ln c1 thin", close=True)
    # contrainte
    f.line(-0.25, (L + 2.5) / 12, 6.5, (L - 65) / 12, "ln cm thin")
    f.text(4.05, 2.2, "10x₁ + 12x₂ = 59", "tx-s", "start")
    lattice(f, range(0, 7), range(0, 6), lambda i, j: 10 * i + 12 * j <= L)
    # lignes de niveau 10x1 + 11x2 = 59 et = 54
    for v, cls in [(59, "ln c2 dash"), (54, "ln c2 thin")]:
        f.line(-0.2, (v + 2) / 11, 6.3, (v - 63) / 11, cls)
    # direction du coût
    x0, y0 = 3.6, 3.6
    n = math.hypot(10, 11)
    c.arrow(f.X(x0), f.Y(y0), f.X(x0 + 0.85 * 10 / n), f.Y(y0 + 0.85 * 11 / n), 2)
    f.text(x0 + 0.85 * 10 / n, y0 + 0.85 * 11 / n, "c = (10, 11)", "tx-s t2", "start", dx=4, dy=-2)
    # points remarquables
    square(c, f.X(5), f.Y(0), 5, "fm")
    f.circle(5.9, 0, 5, "f3")
    cross(c, f.X(6), f.Y(0), 6)  # dessinée après l'optimum continu, tout proche (0,1 unité), pour rester visible
    f.circle(1, 4, 6.5, "f4")
    ring(c, f.X(1), f.Y(4), 9.5)
    f.text(1, 4, "(1, 4)", "tx-b", "start", dx=12, dy=-8)
    f.text(6.15, 0.42, "(5,9 ; 0)", "tx-b t3", "start")
    # légende
    lx, ly = 438, 40
    items = [
        ("P", "P : 10x₁ + 12x₂ ≤ 59, x ≥ 0"),
        ("pt", "les 20 points entiers de P"),
        ("opt", "optimum continu (5,9 ; 0) : 59"),
        ("bad", "arrondi (6, 0) : 60 > 59, hors de P"),
        ("round", "arrondi par défaut (5, 0) : 50"),
        ("int", "optimum entier (1, 4) : 54"),
        ("level", "ligne de niveau 59 (continu)"),
        ("level2", "ligne de niveau 54 (entier)"),
    ]
    for k, (kind, text) in enumerate(items):
        legend_item(c, lx, ly + 30 * k, kind, text)
    c.text(438, 300, "Valeurs de 10x₁ + 11x₂ :", "tx-b")
    c.text(438, 318, "arrondi 50 ≤ entier 54 ≤ continu 59", "tx-s")
    c.text(438, 336, "l'optimum entier est à l'autre bout", "tx-s")
    c.text(438, 352, "du triangle, à distance ≈ 6,3", "tx-s")
    c.save()


# ------------------------------------------------------------------------------------------- 2. bornes
def fig_bornes():
    c = Canvas("bornes", 640, 150, "Encadrement de la valeur entière : arrondi admissible, optimum entier, relaxation", sub=SUB)
    f = Fig(c, (40, 30, 560, 40), (45, 61), (0, 1))
    f.line(45, 0, 61, 0, "ax")
    for v in range(46, 61, 2):
        f.line(v, -0.08, v, 0.08, "ax")
        f.text(v, 0, str(v), "tx-s", "middle", dy=16)
    f.path([(50, 0.0), (59, 0.0)], "ln c4", extra=' style="stroke-width:6px;stroke-opacity:0.35"')
    for v, cls, lab, dy in [(50, "fm", "arrondi (5, 0)", -14), (54, "f4", "optimum entier (1, 4)", -14), (59, "f3", "relaxation (5,9 ; 0)", -14)]:
        f.circle(v, 0, 6, cls)
        f.text(v, 0, lab, "tx-b", "middle", dy=dy)
    c.text(320, 112, "max : une solution admissible donne une borne inférieure (50), la relaxation une borne supérieure (59)", "tx-s", "middle")
    c.text(320, 130, "écart de relaxation 59 − 54 = 5 ; perte de l'arrondi 54 − 50 = 4", "tx-s", "middle")
    c.save()


# ------------------------------------------------------------------------------------------- 3. enveloppe convexe entière
def fig_enveloppe():
    c = Canvas("enveloppe", 660, 344, "Enveloppe convexe des points entiers : triangle de la diapo 18 et triangle fin", sub=SUB)
    # gauche : diapo 18
    f = Fig(c, (36, 34, 290, 240), (-0.3, 6.4), (-0.3, 5.3))
    f.axes(xticks=range(0, 7), yticks=range(0, 6))
    P = [(0, 0), (5.9, 0), (0, 59 / 12)]
    pts = [(i, j) for i in range(7) for j in range(6) if 10 * i + 12 * j <= 59]
    H = hull(pts)
    f.path(P, "a1", close=True)
    f.path(P, "ln c1 thin", close=True)
    f.path(H, "a4", close=True)
    f.path(H, "ln c4 dash", close=True)
    lattice(f, range(7), range(6), lambda i, j: 10 * i + 12 * j <= 59)
    for h in H:
        ring(c, f.X(h[0]), f.Y(h[1]), 6.5, "ln c4 thin nofill")
    f.text(2.8, 2.6, "x₁ + x₂ ≤ 5", "tx-s t4", "start", dx=4)
    f.text(0.5, 4, "x₂ ≤ 4", "tx-s t4", "middle", dy=18)
    c.text(181, 20, "diapo 18 : conv(P ∩ ℤ²) a 4 sommets", "tx-b", "middle")
    c.text(181, 318, "sommets (0,0), (5,0), (1,4), (0,4)", "tx-s", "middle")
    # droite : triangle fin
    g = Fig(c, (400, 34, 220, 240), (-0.3, 3.3), (-0.3, 3.3))
    g.axes(xticks=range(0, 4), yticks=range(0, 4))
    T = [(0.25, 0), (2.75, 0), (1.5, 2.5)]
    g.path(T, "a1", close=True)
    g.path(T, "ln c1 thin", close=True)
    sq = [(1, 0), (2, 0), (2, 1), (1, 1)]
    g.path(sq, "a4", close=True)
    g.path(sq, "ln c4 dash", close=True)
    lattice(g, range(4), range(4), lambda i, j: -4 * i + 2 * j <= -1 and 4 * i + 2 * j <= 11)
    g.circle(1.5, 2.5, 6, "f3")
    for p in [(1, 2), (2, 2), (1, 3), (2, 3)]:
        cross(c, g.X(p[0]), g.Y(p[1]), 5)
    g.text(1.5, 2.5, "(3/2 ; 5/2)", "tx-s t3", "start", dx=9, dy=-2)
    c.text(510, 20, "triangle fin : conv(P ∩ ℤ²) = un carré", "tx-b", "middle")
    c.text(510, 318, "4x₁ − 2x₂ ≥ 1, 4x₁ + 2x₂ ≤ 11, x₂ ≥ 0", "tx-s", "middle")
    c.text(510, 334, "les 4 arrondis de l'optimum sont hors de P", "tx-s", "middle")
    c.save()


# ------------------------------------------------------------------------------------------- 4. contre-exemples diapo 20
def fig_contre():
    c = Canvas("contre", 660, 250, "Deux contre-exemples au lemme de la diapo 20 : un polyèdre non borné, une fonction convexe", sub=SUB)
    f = Fig(c, (40, 40, 230, 160), (-0.5, 4), (-0.5, 3))
    f.path([(0, 0), (4, 0), (4, 3), (0, 3)], "a1", close=True)
    f.line(0, 0, 4, 0, "ln c1")
    f.line(0, 0, 0, 3, "ln c1")
    f.line(-0.5, 0, 4, 0, "ax")
    f.line(0, -0.5, 0, 3, "ax")
    f.circle(0, 0, 5.5, "f3")
    f.text(0, 0, "seul sommet : 0", "tx-s t3", "start", dx=8, dy=16)
    c.arrow(f.X(1.4), f.Y(1.4), f.X(2.9), f.Y(1.4), 1)
    c.arrow(f.X(1.4), f.Y(1.4), f.X(1.4), f.Y(2.6), 1)
    f.text(2.9, 2.45, "P = ℝ²₊ (non borné)", "tx-s t1", "middle")
    c.text(155, 24, "« P = conv(S) » faux si P n'est pas borné", "tx-b", "middle")
    c.text(155, 232, "conv{0} = {0} ≠ ℝ²₊", "tx-s", "middle")
    # droite : x^2 sur [-1, 1]
    g = Fig(c, (390, 40, 230, 160), (-1.4, 1.4), (-0.25, 1.35))
    g.line(-1.4, 0, 1.4, 0, "ax")
    g.line(0, -0.25, 0, 1.35, "ax")
    g.line(-1, 0, 1, 0, "ln c1")
    g.fn(lambda x: x * x, "ln c2", -1.15, 1.15)
    g.circle(-1, 1, 5, "f6")
    g.circle(1, 1, 5, "f6")
    g.circle(0, 0, 5.5, "f3")
    g.text(-1, 0, "−1", "tx-s", "middle", dy=16)
    g.text(1, 0, "1", "tx-s", "middle", dy=16)
    g.text(1, 1, "J(±1) = 1", "tx-s t6", "end", dx=-10, dy=4)
    g.text(0, 0, "min J = 0 en 0", "tx-s t3", "start", dx=8, dy=-8)
    g.text(-0.75, 0.62, "J(x) = x²", "tx-s t2", "end")
    c.text(505, 24, "« pour J convexe, min J sur P = min J sur S » faux", "tx-b", "middle")
    c.text(505, 232, "P = [−1, 1], S = {−1, 1} : 0 < 1", "tx-s", "middle")
    c.save()


# ------------------------------------------------------------------------------------------- 5. réseau A Z^2
def fig_reseau():
    c = Canvas("reseau", 660, 320, "Le réseau image A Z^2 : déterminant 1 (tout Z^2) et déterminant 2 (un point sur deux)", sub=SUB)
    for col, (A, title, sub) in enumerate([
        (((2, 1), (1, 1)), "A = (2 1 ; 1 1), det A = 1", "A ℤ² = ℤ² : A⁻¹b entier pour tout b"),
        (((1, 1), (-1, 1)), "A = (1 1 ; −1 1), det A = 2", "A ℤ² = un point sur deux"),
    ]):
        f = Fig(c, (40 + col * 330, 40, 250, 220), (-3.4, 3.4), (-3.0, 3.0))
        f.line(-3.4, 0, 3.4, 0, "ax")
        f.line(0, -3, 0, 3, "ax")
        img = set()
        for i in range(-6, 7):
            for j in range(-6, 7):
                p = (A[0][0] * i + A[0][1] * j, A[1][0] * i + A[1][1] * j)
                img.add(p)
        for x in range(-3, 4):
            for y in range(-2, 3):
                if (x, y) in img:
                    f.circle(x, y, 4, "f4")
                else:
                    f.circle(x, y, 2.2, "fm")
        a1 = (A[0][0], A[1][0])
        a2 = (A[0][1], A[1][1])
        par = [(0, 0), a1, (a1[0] + a2[0], a1[1] + a2[1]), a2]
        f.path(par, "a3", close=True)
        f.path(par, "ln c3 thin", close=True)
        c.arrow(f.X(0), f.Y(0), f.X(a1[0]), f.Y(a1[1]), 3)
        c.arrow(f.X(0), f.Y(0), f.X(a2[0]), f.Y(a2[1]), 3)
        f.text(a1[0], a1[1], "a₁", "tx-b t3", "start", dx=8, dy=16)
        f.text(a2[0], a2[1], "a₂", "tx-b t3", "end", dx=-6, dy=-4)
        if col == 1:
            ring(c, f.X(1), f.Y(0), 8, "ln c6 nofill")
            f.line(1.25, -0.2, 2.35, -1.45, "ln c6 hair")
            f.text(2.4, -1.5, "b = (1, 0)", "tx-s t6", "start", dy=8)
        c.text(165 + col * 330, 24, title, "tx-b", "middle")
        c.text(165 + col * 330, 284, sub, "tx-s", "middle")
    c.text(495, 302, "A⁻¹(1, 0) = (1/2 ; 1/2) : pas entier", "tx-s t6", "middle")
    c.text(165, 302, "aire du parallélogramme = |det A| = 1", "tx-s", "middle")
    c.save()


# ------------------------------------------------------------------------------------------- matrices dessinées
def draw_matrix(c, x0, y0, M, cell=30, hl=None, colors=None, cls_hl="a6"):
    """Dessine une matrice ; hl = (lignes, colonnes) à surligner ; colors[i][j] = classe de texte."""
    m, n = len(M), len(M[0])
    if hl:
        R, C = hl
        for i in R:
            for j in C:
                c.add(f'<rect x="{x0 + j * cell:.1f}" y="{y0 + i * cell:.1f}" width="{cell}" height="{cell}" class="a2"/>')
    for i in range(m):
        for j in range(n):
            v = M[i][j]
            s = "−1" if v == -1 else str(v).replace("-", "−")
            cl = colors[i][j] if colors else ("tx" if v == 0 else "tx-b")
            c.text(x0 + j * cell + cell / 2, y0 + i * cell + cell / 2 + 5, s, cl, "middle")
    # parenthèses
    h = m * cell
    for side, xx in ((-1, x0 - 4), (1, x0 + n * cell + 4)):
        c.add(f'<path d="M{xx - side * 0:.1f} {y0:.1f} Q{xx + side * 7:.1f} {y0 + h / 2:.1f} {xx:.1f} {y0 + h:.1f}" class="ln ck thin"/>')


def fig_unimod_tu():
    c = Canvas("unimod_tu", 660, 250, "Unimodulaire mais pas totalement unimodulaire, contre totalement unimodulaire", sub=SUB)
    U3 = [[1, 1, 0], [-1, 1, 1], [0, 1, 1]]
    draw_matrix(c, 90, 60, U3, cell=36, hl=([0, 1], [0, 1]))
    c.text(144, 34, "det = 1 : unimodulaire", "tx-b", "middle")
    c.text(144, 196, "mais la sous-matrice surlignée", "tx-s", "middle")
    c.text(144, 212, "(1 1 ; −1 1) a pour déterminant 2 :", "tx-s", "middle")
    c.text(144, 228, "pas totalement unimodulaire", "tx-s t6", "middle")
    G = [[1, 1, 0, 0, 0], [-1, 0, 1, 1, 0], [0, -1, -1, 0, 1], [0, 0, 0, -1, -1]]
    draw_matrix(c, 380, 52, G, cell=36)
    c.text(470, 34, "matrice d'incidence d'un graphe orienté", "tx-b", "middle")
    c.text(470, 212, "ses 125 sous-matrices carrées ont toutes", "tx-s", "middle")
    c.text(470, 228, "un déterminant égal à 0, 1 ou −1 : TU", "tx-s t3", "middle")
    c.save()


# ------------------------------------------------------------------------------------------- 6. Poincaré : graphe + matrice
def fig_poincare():
    c = Canvas("poincare", 660, 280, "Structure d'une matrice de Poincaré : la matrice d'incidence d'un graphe orienté", sub=SUB)
    pos = {1: (70, 140), 2: (190, 60), 3: (190, 220), 4: (310, 140)}
    arcs = [(1, 2), (1, 3), (2, 3), (2, 4), (3, 4)]
    mid = c.arrow_marker(1)
    for k, (i, j) in enumerate(arcs):
        (x1, y1), (x2, y2) = pos[i], pos[j]
        d = math.hypot(x2 - x1, y2 - y1)
        ux, uy = (x2 - x1) / d, (y2 - y1) / d
        c.add(f'<line x1="{x1 + 19 * ux:.1f}" y1="{y1 + 19 * uy:.1f}" x2="{x2 - 21 * ux:.1f}" y2="{y2 - 21 * uy:.1f}" class="ln c1 thin" marker-end="url(#{mid})"/>')
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        off = (-uy * 13, ux * 13)
        c.text(mx + off[0], my + off[1] + 4, f"a{'₁₂₃₄₅'[k]}", "tx-s t1", "middle")
    for i, (x, y) in pos.items():
        c.add(f'<circle cx="{x}" cy="{y}" r="17" class="f5"/>')
        c.text(x, y + 5, str(i), "on-fill", "middle")
    c.text(190, 270, "chaque arc part d'un nœud et arrive à un autre", "tx-s", "middle")
    G = [[1, 1, 0, 0, 0], [-1, 0, 1, 1, 0], [0, -1, -1, 0, 1], [0, 0, 0, -1, -1]]
    cols = [["tx-b t3" if v == 1 else "tx-b t6" if v == -1 else "tx" for v in r] for r in G]
    x0, y0, cell = 420, 60, 36
    draw_matrix(c, x0, y0, G, cell=cell, colors=cols)
    for j in range(5):
        c.text(x0 + j * cell + cell / 2, y0 - 10, f"a{'₁₂₃₄₅'[j]}", "tx-s t1", "middle")
    for i in range(4):
        c.text(x0 - 16, y0 + i * cell + cell / 2 + 5, f"nœud {i + 1}", "tx-s", "end")
    c.text(510, 226, "+1 : l'arc part du nœud (une fois par colonne)", "tx-s t3", "middle")
    c.text(510, 244, "−1 : l'arc arrive au nœud (une fois par colonne)", "tx-s t6", "middle")
    c.text(510, 262, "somme de chaque colonne = 0", "tx-s", "middle")
    c.save()


# ------------------------------------------------------------------------------------------- 7. Poincaré : les trois cas
def fig_poincare_cas():
    c = Canvas("poincare_cas", 660, 250, "Les trois cas de la récurrence de Poincaré", sub=SUB)
    cases = [
        ([[1, 0, -1], [-1, 0, 0], [0, 0, 1]], ([0, 1, 2], [1]), "cas 1 : une colonne nulle", "det = 0"),
        ([[1, 0, -1], [-1, 1, 0], [0, 0, 1]], ([0, 1, 2], [1]), "cas 2 : une colonne à un seul ±1", "on développe : det = ± det(mineur)"),
        ([[1, -1, 0], [-1, 0, 1], [0, 1, -1]], None, "cas 3 : un +1 et un −1 partout", "somme des lignes = 0 : det = 0"),
    ]
    for k, (M, hl, title, sub) in enumerate(cases):
        x0 = 60 + k * 215
        draw_matrix(c, x0, 64, M, cell=32, hl=hl)
        c.text(x0 + 48, 36, title, "tx-b", "middle")
        c.text(x0 + 48, 196, sub, "tx-s", "middle")
    c.text(330, 230, "l'hypothèse « au plus un +1 et au plus un −1 par colonne » passe aux mineurs : on recommence", "tx-s", "middle")
    c.save()


# ------------------------------------------------------------------------------------------- 8. centre d'appels
def fig_centre():
    c = Canvas("centre", 660, 330, "Centre d'appels : trois tranches horaires, cinq fractions à effectif constant, et la matrice d'intervalles", sub=SUB)
    # instants schématiques (le cours ne donne que 0 et 24)
    T = {"α₁": 0, "α₂": 5, "β₁": 9, "α₃": 13, "β₂": 18, "β₃": 24}
    X = lambda t: 34 + t / 24 * 370
    yax = 230
    c.add(f'<line x1="{X(0):.1f}" y1="{yax}" x2="{X(24):.1f}" y2="{yax}" class="ax"/>')
    for name, t in T.items():
        c.add(f'<line x1="{X(t):.1f}" y1="{yax - 4}" x2="{X(t):.1f}" y2="{yax + 4}" class="ax"/>')
        c.text(X(t), yax + 18, name, "tx-i", "middle")
    c.text(X(0), yax + 34, "0", "tx-s", "middle")
    c.text(X(24), yax + 34, "24", "tx-s", "middle")
    shifts = [(0, 9, "tranche 1 · salaire 4", 5), (5, 18, "tranche 2 · salaire 5", 8), (13, 24, "tranche 3 · salaire 6", 4)]
    for k, (a, b, lab, x) in enumerate(shifts):
        y = 40 + k * 34
        c.add(f'<rect x="{X(a):.1f}" y="{y}" width="{X(b) - X(a):.1f}" height="20" rx="4" class="a1"/>')
        c.add(f'<rect x="{X(a):.1f}" y="{y}" width="{X(b) - X(a):.1f}" height="20" rx="4" class="ln c1 thin nofill"/>')
        c.text(X(a) + 6, y + 14, lab, "tx-s")
        c.text(X(b) + 6, y + 14, f"x{'₁₂₃'[k]} = {x}", "tx-b t3", "start")
    bounds = [0, 5, 9, 13, 18, 24]
    dem = [5, 10, 6, 12, 4]
    cov = [5, 13, 8, 12, 4]
    for j in range(5):
        xm = (X(bounds[j]) + X(bounds[j + 1])) / 2
        c.add(f'<line x1="{X(bounds[j + 1]):.1f}" y1="34" x2="{X(bounds[j + 1]):.1f}" y2="{yax}" class="gr"/>')
        c.text(xm, 160, f"f{'₁₂₃₄₅'[j]}", "tx-b", "middle")
        c.text(xm, 180, f"c = {dem[j]}", "tx-s t2", "middle")
        c.text(xm, 198, f"présents {cov[j]}", "tx-s t3", "middle")
    c.text(X(12), 318, "coût 4·5 + 5·8 + 6·4 = 84 ; positions des instants schématiques", "tx-s", "middle")
    # matrice tU (fractions x tranches)
    M = [[1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 1, 1], [0, 0, 1]]
    x0, y0, cell = 500, 70, 30
    draw_matrix(c, x0, y0, M, cell=cell)
    for j in range(3):
        c.text(x0 + j * cell + cell / 2, y0 - 10, f"t{'₁₂₃'[j]}", "tx-s t1", "middle")
    for i in range(5):
        c.text(x0 - 14, y0 + i * cell + cell / 2 + 5, f"f{'₁₂₃₄₅'[i]}", "tx-s", "end")
    c.text(545, 40, "ᵗU : des 1 consécutifs", "tx-b", "middle")
    c.text(545, 242, "dans chaque colonne", "tx-s", "middle")
    c.text(545, 260, "→ totalement unimodulaire", "tx-s t3", "middle")
    c.save()


if __name__ == "__main__":
    fig_diapo18()
    fig_bornes()
    fig_enveloppe()
    fig_contre()
    fig_reseau()
    fig_unimod_tu()
    fig_poincare()
    fig_poincare_cas()
    fig_centre()
