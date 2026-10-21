"""figures_P05.py — static SVG figures of Partie 5 (la dualité), written to figures/P05/.

Run: python3 figures_P05.py        (then node build.mjs Partie05.html)

Every number drawn here is computed here (exact fractions where it matters); the same numbers were checked by the
verification scripts of the page (fil rouge (R), production example, centre d'appels, Exercice 4.2.7).
Colour code (GUIDE.md §5): admissible set 1 (blue), cost / level lines 2, optimum 3 (green), dual objects 5 (violet).
"""
from fractions import Fraction as Fr

import numpy as np

from figures_common import Canvas, Fig, esc

SUB = "P05"


# ------------------------------------------------------------------------------------------------ helpers
def half_plane_polygon(cons, box):
    """Vertices of {a x + b y <= r for (a, b, r) in cons} inside box = (x0, x1, y0, y1) (Sutherland-Hodgman)."""
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


def line_in_box(a, b, r, box):
    """The segment of the line a x + b y = r inside box, or None."""
    pts = []
    if abs(b) > 1e-12:
        for x in (box[0], box[1]):
            y = (r - a * x) / b
            if box[2] - 1e-9 <= y <= box[3] + 1e-9:
                pts.append((x, y))
    if abs(a) > 1e-12:
        for y in (box[2], box[3]):
            x = (r - b * y) / a
            if box[0] - 1e-9 <= x <= box[1] + 1e-9:
                pts.append((x, y))
    if len(pts) < 2:
        return None
    best, d = None, -1
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            dd = np.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1])
            if dd > d:
                best, d = (pts[i], pts[j]), dd
    return best


def draw_line(f, a, b, r, box, cls="ln cm thin"):
    s = line_in_box(a, b, r, box)
    if s:
        f.line(s[0][0], s[0][1], s[1][0], s[1][1], cls)
    return s


def rich(s):
    """Escapes s and writes P_ad with a true subscript (no underscore is left in the figure)."""
    return esc(s).replace("P_ad", 'P<tspan baseline-shift="sub" font-size="75%">ad</tspan>')


def ftext(f, x, y, s, cls="tx-s", anchor="start", dx=0, dy=0):
    f.c.add(f'<text x="{f.X(x) + dx:.1f}" y="{f.Y(y) + dy:.1f}" class="{cls}" text-anchor="{anchor}">{rich(s)}</text>')


def ctext(c, x, y, s, cls="tx-s", anchor="start"):
    c.add(f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}">{rich(s)}</text>')


def frs(q):
    q = Fr(q)
    s = str(q.numerator) if q.denominator == 1 else f"{q.numerator}/{q.denominator}"
    return s.replace("-", "−")


# ------------------------------------------------------------------------------------------------ §1
def fig_bornes():
    """Weak duality on the real line, for the running example (R)."""
    c = Canvas("bornes", 660, 244, "Bornes inférieures données par des combinaisons de contraintes, et coûts de points admissibles, sur une même droite", sub=SUB)
    f = Fig(c, (40, 70, 590, 60), (0, 28), (0, 1))
    y0 = 0.5
    f.line(0, y0, 28, y0, "ax")
    for v in range(0, 29, 2):
        f.line(v, y0, v, y0 - 0.08, "ax")
    # zone between best bound and best cost collapses at 13
    duals = [(0, "p = (0, 0)"), (6, "p = (0, 2/3)"), (8, "p = (1, 0)"), (11, "p = (1, 1/3)"), (12, "p = (3/2, 0)")]
    prims = [(16, "x = (0, 8)"), (27, "x = (9, 0)")]
    f.path([(0, y0 - 0.05), (13, y0 - 0.05), (13, y0 + 0.05), (0, y0 + 0.05)], "a5", close=True)
    f.path([(13, y0 - 0.05), (28, y0 - 0.05), (28, y0 + 0.05), (13, y0 + 0.05)], "a1", close=True)
    # dual values below, staggered
    for k, (v, lab) in enumerate(duals):
        f.circle(v, y0, 5, "f5")
        dy = 26 if k % 2 == 0 else 56
        c.add(f'<line x1="{f.X(v):.1f}" y1="{f.Y(y0) + 6:.1f}" x2="{f.X(v):.1f}" y2="{f.Y(y0) + dy - 12:.1f}" class="ln c5 hair"/>')
        f.text(v, y0, f"{v}", "tx-b t5", "middle", dy=dy)
        f.text(v, y0, lab, "tx-s t5", "middle", dy=dy + 13)
    for k, (v, lab) in enumerate(prims):
        f.circle(v, y0, 5, "f1")
        c.add(f'<line x1="{f.X(v):.1f}" y1="{f.Y(y0) - 6:.1f}" x2="{f.X(v):.1f}" y2="{f.Y(y0) - 22:.1f}" class="ln c1 hair"/>')
        f.text(v, y0, f"{v}", "tx-b t1", "middle", dy=-38)
        f.text(v, y0, lab, "tx-s t1", "middle", dy=-25)
    f.circle(13, y0, 7, "f3")
    c.add(f'<line x1="{f.X(13):.1f}" y1="{f.Y(y0) - 8:.1f}" x2="{f.X(13):.1f}" y2="{f.Y(y0) - 22:.1f}" class="ln c3 hair"/>')
    f.text(13, y0, "optimum : 13", "tx-b t3", "end", dx=8, dy=-38)
    f.text(13, y0, "x̄ = (3, 2) et p̄ = (7/5, 1/5)", "tx-s t3", "end", dx=8, dy=-25)
    c.text(40, 20, "◀ bornes b·p (combinaisons admissibles) : toutes ≤ 13", "tx-s t5", "start")
    c.text(630, 20, "coûts c·x (points admissibles) : tous ≥ 13 ▶", "tx-s t1", "end")
    c.text(330, 218, "Aucune borne ne dépasse un coût : c’est la dualité faible.", "tx-s", "middle")
    c.text(330, 234, "La meilleure borne rejoint le meilleur coût : c’est le théorème de dualité.", "tx-s", "middle")
    c.save()


# ------------------------------------------------------------------------------------------------ §2
def fig_lagrangien():
    """min over x_i >= 0 of k x_i, for k < 0, k = 0, k > 0."""
    c = Canvas("lagrangien", 660, 200, "Minimum sur xⱼ positif d'une fonction linéaire k xⱼ, selon le signe de k", sub=SUB)
    panels = [(-1.0, "(c − Aᵀp)ⱼ < 0", "inf = −∞ : xⱼ → +∞"), (0.0, "(c − Aᵀp)ⱼ = 0", "min = 0, atteint en tout xⱼ ≥ 0"), (1.0, "(c − Aᵀp)ⱼ > 0", "min = 0, atteint en xⱼ = 0")]
    for i, (k, title, sub) in enumerate(panels):
        x0 = 20 + i * 215
        f = Fig(c, (x0 + 20, 40, 170, 110), (0, 4), (-3, 3))
        f.line(0, 0, 4, 0, "ax")
        f.line(0, -3, 0, 3, "ax")
        f.fn(lambda t: k * t * 0.7, "ln c2", 0, 4)
        f.text(4, 0, "xⱼ", "tx-s", "end", dy=14)
        if k < 0:
            c.arrow(f.X(3.3), f.Y(-2.31) + 4, f.X(3.75), f.Y(-2.63) + 9, 6, "ln c6 thin")
            f.text(2.0, -2.2, "→ −∞", "tx-b t6", "end")
        elif k == 0:
            f.path([(0, -0.08), (4, -0.08), (4, 0.08), (0, 0.08)], "a3", close=True)
            f.circle(0, 0, 4.5, "f3")
            f.circle(2, 0, 4.5, "f3")
            f.circle(4, 0, 4.5, "f3")
        else:
            f.circle(0, 0, 5, "f3")
        c.text(x0 + 105, 24, title, "tx-b", "middle")
        c.text(x0 + 105, 178, sub, "tx-s", "middle")
    c.save()


def fig_fonction_duale():
    """The plane of p for (R): P_ad (where G > −∞), level lines of b·p, optimum."""
    c = Canvas("fonction-duale", 600, 330, "Fonction duale de l'exemple (R) : ensemble admissible dual en violet, G(p) = b·p dedans, moins l'infini dehors", sub=SUB)
    box = (-0.4, 2.6, -0.35, 1.6)
    f = Fig(c, (50, 20, 400, 280), box[:2], box[2:])
    f.axes(xticks=[0, 1, 2], yticks=[0, 1], xlabel="p₁", ylabel="p₂")
    cons = [(2, 1, 3), (1, 3, 2), (-1, 0, 0), (0, -1, 0)]
    poly = half_plane_polygon(cons, box)
    # outside: light grey hatch-like fill (whole box minus polygon is drawn as box then polygon over it)
    f.path([(box[0], box[2]), (box[1], box[2]), (box[1], box[3]), (box[0], box[3])], "am", close=True)
    f.path(poly, "fs", close=True)
    f.path(poly, "a5", close=True)
    f.path(poly, "ln c5 thin", close=True)
    for (a, b, r, lab, pos) in [(2, 1, 3, "2p₁ + p₂ = 3  (colonne de x₁)", (1.62, 0.05)), (1, 3, 2, "p₁ + 3p₂ = 2  (colonne de x₂)", (-0.55, 0.9))]:
        draw_line(f, a, b, r, box)
    f.text(0.82, 1.5, "2p₁ + p₂ = 3", "tx-s", "start")
    f.text(2.05, 0.05, "p₁ + 3p₂ = 2", "tx-s", "start")
    # level lines of b.p = 8 p1 + 9 p2
    for v in [4, 8, 13]:
        draw_line(f, 8, 9, v, box, "ln c2 thin dash" if v != 13 else "ln c2 thin")
    ftext(f, 1.0, 0.21, "P_ad", "tx-b t5", "start")
    f.text(0.98, 0.08, "G(p) = b·p", "tx-s t5", "start")
    f.text(1.95, 1.3, "G(p) = −∞", "tx-b", "middle")
    f.text(1.95, 1.18, "(une composante de c − Aᵀp < 0)", "tx-s", "middle")
    f.circle(1.4, 0.2, 6, "f3")
    f.text(1.4, 0.2, "p̄ = (7/5, 1/5), b·p̄ = 13", "tx-s t3", "start", dx=10, dy=-6)
    # legend on the right
    lx = 465
    c.text(lx, 60, "lignes de niveau", "tx-s", "start")
    c.text(lx, 74, "de b·p = 8p₁ + 9p₂ :", "tx-s", "start")
    c.add(f'<line x1="{lx}" y1="90" x2="{lx + 30}" y2="90" class="ln c2 thin dash"/>')
    c.text(lx + 36, 94, "4 et 8", "tx-s", "start")
    c.add(f'<line x1="{lx}" y1="108" x2="{lx + 30}" y2="108" class="ln c2 thin"/>')
    c.text(lx + 36, 112, "13 (optimum)", "tx-s", "start")
    c.text(lx, 150, "p ≥ 0 vient des", "tx-s", "start")
    c.text(lx, 164, "colonnes −e₁, −e₂", "tx-s", "start")
    c.text(lx, 178, "des variables d’écart", "tx-s", "start")
    c.save()


# ------------------------------------------------------------------------------------------------ §4
def fig_cas():
    c = Canvas("cas", 660, 268, "Les neuf combinaisons primal / dual : quatre seulement sont possibles", sub=SUB)
    x0, y0, cw, ch = 170, 56, 160, 62
    cols = ["optimum fini", "non borné (+∞)", "vide"]
    rows = ["optimum fini", "non borné (−∞)", "vide"]
    c.text(x0 + 1.5 * cw, 18, "DUAL (4.18) : max b·p", "tx-b t5", "middle")
    for j, t in enumerate(cols):
        c.text(x0 + (j + 0.5) * cw, 44, t, "tx-s t5", "middle")
    c.text(20, 36, "PRIMAL (4.15) :", "tx-b t1", "start")
    c.text(20, 50, "min c·x", "tx-b t1", "start")
    for i, t in enumerate(rows):
        c.text(x0 - 10, y0 + (i + 0.5) * ch + 4, t, "tx-s t1", "end")
    cells = {
        (0, 0): ("a3", "possible", "valeurs égales (4.19)", "ex. : (R), 13 = 13"),
        (1, 2): ("a4", "possible", "dual vide", "ex. : min −x₁, x₁ − x₂ = 0"),
        (2, 1): ("a4", "possible", "primal vide", "ex. : min x₁, x₁ + x₂ = −1"),
        (2, 2): ("a4", "possible", "les deux vides", "ex. : min −x₁, 0·x₁ = 1"),
    }
    for i in range(3):
        for j in range(3):
            X, Y = x0 + j * cw, y0 + i * ch
            if (i, j) in cells:
                cls, t1, t2, t3 = cells[(i, j)]
                c.add(f'<rect x="{X + 2}" y="{Y + 2}" width="{cw - 4}" height="{ch - 4}" rx="6" class="{cls}"/>')
                c.text(X + cw / 2, Y + 20, t1, "tx-b t3" if cls == "a3" else "tx-b t4", "middle")
                c.text(X + cw / 2, Y + 35, t2, "tx-s", "middle")
                c.text(X + cw / 2, Y + 50, t3, "tx-s", "middle")
            else:
                c.add(f'<rect x="{X + 2}" y="{Y + 2}" width="{cw - 4}" height="{ch - 4}" rx="6" class="am"/>')
                c.text(X + cw / 2, Y + 30, "impossible", "tx-s", "middle")
                why = {(0, 1): "dualité faible", (0, 2): "Th. 4.2.13", (1, 0): "dualité faible", (1, 1): "dualité faible", (2, 0): "Th. 4.2.13"}[(i, j)]
                c.text(X + cw / 2, Y + 45, f"({why})", "tx-s", "middle")
    c.text(330, 262, "Lecture : un primal fini force un dual fini (et réciproquement) ; un problème non borné force l’autre à être vide.", "tx-s", "middle")
    c.save()


# ------------------------------------------------------------------------------------------------ §7
def fig_sensibilite():
    """V(b1) for the production example: concave piecewise linear, slopes = shadow price of wood."""
    c = Canvas("sensibilite", 640, 336, "Profit optimal en fonction du stock de bois : concave, linéaire par morceaux, de pente le prix ombre", sub=SUB)
    f = Fig(c, (56, 22, 540, 250), (0, 16), (0, 270))
    f.axes(xticks=[0, 2, 4, 6, 8, 10, 12, 14, 16], yticks=[0, 50, 100, 150, 200, 250], xlabel="b₁ (bois)", ylabel="V(b₁) = profit maximal")
    pts = [(0, 0), (5, 150), (7.5, 195), (12, 240), (16, 240)]
    f.path(pts, "ln c3")
    for (x, y) in pts[1:-1]:
        f.circle(x, y, 3.5, "f3")
    # slopes labels
    for (a, b), s in zip(zip(pts[:-1], pts[1:]), ["pente 30", "pente 18", "pente 10", "pente 0"]):
        xm, ym = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        if s == "pente 0":
            f.text(xm, ym, s, "tx-s t3", "middle", dy=-10)
        else:
            f.text(xm, ym, s, "tx-s t3", "start", dx=8, dy=14)
    # current b1 = 10, tangent of slope 10 (it contains the segment of slope 10)
    f.line(6.0, 220 - 40, 13.2, 220 + 32, "ln c5 thin dash")
    f.circle(10, 220, 6, "f5")
    f.line(10, 0, 10, 220, "ln cm thin dot")
    f.text(10, 130, "b₁ = 10 : V = 220,", "tx-s t5", "start", dx=8)
    f.text(10, 130, "pente y₁ = 10", "tx-s t5", "start", dx=8, dy=14)
    f.text(7.5, 195, "(15/2 ; 195)", "tx-s", "start", dx=8, dy=14)
    f.text(12, 240, "(12 ; 240)", "tx-s", "middle", dy=-10)
    f.text(5, 150, "(5 ; 150)", "tx-s", "end", dx=-8, dy=-4)
    c.text(330, 312, "Le prix ombre du bois vaut 10 tant que b₁ reste dans [15/2 ; 12] (la base optimale ne change pas) ;", "tx-s", "middle")
    c.text(330, 328, "au-delà de 12, le bois ne limite plus rien : son prix tombe à 0.", "tx-s", "middle")
    c.save()


# ------------------------------------------------------------------------------------------------ §8
def fig_frise():
    c = Canvas("frise", 660, 300, "Le centre d'appels : trois tranches horaires, cinq intervalles à effectif constant, demande et effectif optimal", sub=SUB)
    L, R = 70, 630
    ts = [0, 1, 2, 3, 4, 5]  # alpha1 < alpha2 < beta1 < alpha3 < beta2 < beta3, placed schematically
    names = ["α₁ = 0", "α₂", "β₁", "α₃", "β₂", "β₃ = 24"]
    X = lambda t: L + (R - L) * t / 5
    # shifts
    shifts = [(0, 2, "tranche 1 : S₁ = 4", 5), (1, 4, "tranche 2 : S₂ = 5", 8), (3, 5, "tranche 3 : S₃ = 6", 4)]
    for k, (a, b, lab, xopt) in enumerate(shifts):
        y = 18 + k * 26
        c.add(f'<rect x="{X(a):.1f}" y="{y}" width="{X(b) - X(a):.1f}" height="18" rx="4" class="a1"/>')
        c.add(f'<rect x="{X(a):.1f}" y="{y}" width="{X(b) - X(a):.1f}" height="18" rx="4" class="ln c1 thin"/>')
        c.text((X(a) + X(b)) / 2, y + 13, f"{lab} ; x{'₁₂₃'[k]} = {xopt}", "tx-s", "middle")
    # time axis
    ya = 112
    c.add(f'<line x1="{L}" y1="{ya}" x2="{R}" y2="{ya}" class="ax"/>')
    for t, nm in zip(ts, names):
        c.add(f'<line x1="{X(t):.1f}" y1="{ya - 4}" x2="{X(t):.1f}" y2="{ya + 4}" class="ax"/>')
        c.add(f'<line x1="{X(t):.1f}" y1="14" x2="{X(t):.1f}" y2="{ya}" class="gr"/>')
        c.text(X(t), ya + 17, nm, "tx-s", "middle")
    # demand vs staffing, per interval
    cdem = [5, 10, 6, 12, 4]
    staff = [5, 13, 8, 12, 4]
    duals = ["4", "0", "0", "5", "1"]
    base, scale = 262, 7.0
    for j in range(5):
        x1, x2 = X(j) + 6, X(j + 1) - 6
        w = (x2 - x1) / 2 - 2
        hc, hs = cdem[j] * scale, staff[j] * scale
        c.add(f'<rect x="{x1:.1f}" y="{base - hc:.1f}" width="{w:.1f}" height="{hc:.1f}" class="f2" fill-opacity="0.75"/>')
        c.add(f'<rect x="{x1 + w + 4:.1f}" y="{base - hs:.1f}" width="{w:.1f}" height="{hs:.1f}" class="f1" fill-opacity="0.75"/>')
        c.text(x1 + w / 2, base - hc - 4, str(cdem[j]), "tx-s t2", "middle")
        c.text(x1 + w + 4 + w / 2, base - hs - 4, str(staff[j]), "tx-s t1", "middle")
        c.text((x1 + x2) / 2, base + 14, f"I{'₁₂₃₄₅'[j]} : p{'₁₂₃₄₅'[j]} = {duals[j]}", "tx-s t5", "middle")
    c.add(f'<line x1="{L}" y1="{base}" x2="{R}" y2="{base}" class="ax"/>')
    c.text(L - 6, 150, "clients cⱼ", "tx-s t2", "end")
    c.text(L - 6, 164, "effectif (Ux)ⱼ", "tx-s t1", "end")
    c.text(L - 6, base + 14, "prix duaux", "tx-s t5", "end")
    c.text(330, 296, "Positions des instants schématiques : seul leur ordre compte. Effectif optimal x = (5, 8, 4), coût 84.", "tx-s", "middle")
    c.save()


def fig_centre_dual():
    """The dual of the call centre reduced to (p2, p4)."""
    c = Canvas("centre-dual", 600, 320, "Dual du centre d'appels réduit au plan (p2, p4) : polygone, lignes de niveau de 74 − p2 + 2p4, optimum (0, 5)", sub=SUB)
    box = (-0.5, 6.5, -0.5, 6.8)
    f = Fig(c, (50, 20, 380, 270), box[:2], box[2:])
    f.axes(xticks=[0, 1, 2, 3, 4, 5, 6], yticks=[0, 1, 2, 3, 4, 5, 6], xlabel="p₂", ylabel="p₄")
    cons = [(1, 0, 4), (1, 1, 5), (0, 1, 6), (-1, 0, 0), (0, -1, 0)]
    poly = half_plane_polygon(cons, box)
    f.path(poly, "a5", close=True)
    f.path(poly, "ln c5 thin", close=True)
    draw_line(f, 1, 0, 4, box)
    draw_line(f, 1, 1, 5, box)
    draw_line(f, 0, 1, 6, box)
    f.text(4, 6.3, "p₂ = 4 (p₁ ≥ 0)", "tx-s", "start", dx=4)
    f.text(3.0, 2.6, "p₂ + p₄ = 5 (p₃ ≥ 0)", "tx-s", "start")
    f.text(6.45, 6, "p₄ = 6 (p₅ ≥ 0)", "tx-s", "end", dy=14)
    # level lines -p2 + 2p4 = k  <=>  phi = 74 + k
    for k in [0, 4, 10]:
        draw_line(f, -1, 2, k, box, "ln c2 thin dash" if k != 10 else "ln c2 thin")
    for (vx, vy, val, dx, dy, anc) in [(0, 0, 74, 8, 14, "start"), (4, 0, 70, 6, 14, "start"), (4, 1, 72, 8, 4, "start"), (0, 5, 84, 10, 16, "start")]:
        f.circle(vx, vy, 4, "f5" if val != 84 else "f3")
        f.text(vx, vy, f"φ = {val}", "tx-s t5" if val != 84 else "tx-b t3", anc, dx=dx, dy=dy)
    lx = 445
    for k, s in enumerate(["φ(p₂, p₄) = 74 − p₂ + 2p₄", "", "tirets : φ = 74, 78", "trait plein : φ = 84", "", "optimum (p₂, p₄) = (0, 5)", "p₁ = 4, p₃ = 0, p₅ = 1"]):
        if s:
            c.text(lx, 50 + 16 * k, s, "tx-s" if k not in (5, 6) else "tx-s t3", "start")
    c.save()


# ------------------------------------------------------------------------------------------------ §9
def fig_ex427():
    c = Canvas("ex427", 600, 340, "Exercice 4.2.7 : le dual en dimension 2, ses quatre contraintes, et son optimum au sommet (12/7, 8/7)", sub=SUB)
    box = (-0.3, 3.6, -0.3, 3.4)
    f = Fig(c, (50, 20, 380, 290), box[:2], box[2:])
    f.axes(xticks=[0, 1, 2, 3], yticks=[0, 1, 2, 3], xlabel="p₁", ylabel="p₂")
    cons = [(4, 1, 8), (1, 3, 9), (1, 2, 4), (2, 1, 6), (-1, 0, 0), (0, -1, 0)]
    poly = half_plane_polygon(cons, box)
    f.path(poly, "a5", close=True)
    f.path(poly, "ln c5 thin", close=True)
    labels = {0: ("(i) 4p₁ + p₂ = 8", (1.12, 3.22)), 1: ("(ii) p₁ + 3p₂ = 9", (2.15, 2.5)), 2: ("(iii) p₁ + 2p₂ = 4", (2.75, 0.75)), 3: ("(iv) 2p₁ + p₂ = 6", (2.58, 1.62))}
    for k, (a, b, r) in enumerate(cons[:4]):
        draw_line(f, a, b, r, box)
        lab, (x, y) = labels[k]
        f.text(x, y, lab, "tx-s", "end" if k == 0 else "start")
    # level line p1 + p2 = 20/7
    v = 20 / 7
    draw_line(f, 1, 1, v, box, "ln c2 thin")
    draw_line(f, 1, 1, 2, box, "ln c2 thin dash")
    px, py = 12 / 7, 8 / 7
    f.circle(px, py, 6, "f3")
    # a light outline keeps the label legible where the dashed level line p1 + p2 = 2 crosses it
    c.add(f'<text x="{f.X(px) - 10:.1f}" y="{f.Y(py) + 18:.1f}" class="tx-b t3" text-anchor="end" '
          f'style="paint-order:stroke;stroke:var(--surface);stroke-width:4px;stroke-linejoin:round">p̄ = (12/7, 8/7)</text>')
    # normals at the optimum (scaled) and the objective direction
    sc = 0.11
    for (nx, ny, k) in [(4, 1, 5), (1, 2, 5), (1, 1, 2)]:
        c.arrow(f.X(px), f.Y(py), f.X(px + sc * nx * (1 if k == 5 else 2.2)), f.Y(py + sc * ny * (1 if k == 5 else 2.2)), k, f"ln c{k} thin")
    f.text(px + sc * 4, py + sc * 1, "(4, 1)", "tx-s t5", "start", dx=4, dy=10)
    f.text(px + sc * 1, py + sc * 2, "(1, 2)", "tx-s t5", "end", dx=-4, dy=-4)
    f.text(px + sc * 2.2, py + sc * 2.2, "b = (1, 1)", "tx-s t2", "start", dx=8, dy=-6)
    lx = 445
    for k, s in enumerate(["Sommets de P_ad", "et valeur de p₁ + p₂ :", "(0, 0) : 0", "(2, 0) : 2", "(12/7, 8/7) : 20/7", "(0, 2) : 2", "",
                           "Contraintes (ii) et (iv) lâches", "à l’optimum ⇒ x₂ = x₄ = 0.", "", "(1, 1) = (1/7)(4, 1) + (3/7)(1, 2) :", "les poids 1/7 et 3/7 sont x₁, x₃."]):
        if s:
            ctext(c, lx, 40 + 16 * k, s, "tx-s", "start")
    ftext(f, 0.05, 0.12, "P_ad", "tx-b t5", "start", dx=4)
    c.save()


if __name__ == "__main__":
    fig_bornes()
    fig_lagrangien()
    fig_fonction_duale()
    fig_cas()
    fig_sensibilite()
    fig_frise()
    fig_centre_dual()
    fig_ex427()
