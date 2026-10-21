"""figures_P07.py — figures statiques de la partie 7 (flots, transport, affectation), écrites dans figures/P07/.

Lancer : python3 figures_P07.py        (puis node build.mjs Partie07.html)

Toutes les données (graphe de la diapo 26, flots, capacités, coûts, constructeur automobile, affectation 3 x 3)
sont celles des scripts de vérification ; les coordonnées sont calculées ici.
"""
import itertools
import math

import numpy as np

from figures_common import Canvas, Fig, esc

SUB = "P07"

# ---------------------------------------------------------------------------------------------
# Le graphe de la diapo 26 (Figure 4.2 du livre) : 6 nœuds, 12 arcs, dans l'ordre de la matrice d'incidence.
NODES = ["s", "1", "2", "3", "4", "p"]
ARCS = [("s", "1"), ("s", "3"), ("1", "2"), ("1", "3"), ("2", "1"), ("2", "3"),
        ("2", "4"), ("2", "p"), ("3", "2"), ("3", "4"), ("4", "2"), ("4", "p")]
# Courbure de chaque arc (même convention que drawArc de app.js : point de contrôle = milieu + bend * L * normale).
BEND = {("s", "1"): -0.12, ("s", "3"): 0.12, ("1", "2"): -0.09, ("2", "1"): -0.09, ("1", "3"): 0.0,
        ("2", "3"): 0.07, ("3", "2"): 0.07, ("2", "4"): -0.12, ("4", "2"): -0.12, ("2", "p"): -0.1,
        ("3", "4"): -0.05, ("4", "p"): 0.1}
FLOW5 = [3, 2, 2, 1, 0, 0, 0, 3, 1, 2, 0, 2]       # le flot de la section 2 (b_s = 5, b_p = -5)
U = [5, 4, 2, 3, 1, 1, 3, 4, 2, 3, 1, 5]            # capacités choisies (section 5)
C = [2, 5, 6, 2, 1, 1, 3, 7, 2, 6, 1, 2]            # coûts choisis (sections 3 et 6)
XMIN5 = [3, 2, 0, 3, 0, 0, 2, 0, 2, 3, 0, 5]        # flot de coût minimum de valeur 5 (coût 60)
XMAX = [3, 4, 2, 1, 0, 0, 0, 4, 2, 3, 0, 3]         # flot maximal (Edmonds–Karp), valeur 7
DIST = {"s": 0, "1": 2, "3": 4, "2": 6, "4": 9, "p": 11}
PRED = {"1": "s", "3": "1", "2": "3", "4": "2", "p": "4"}
R = 17


def pos(ox=0, oy=0, sx=1.0, sy=1.0):
    base = {"s": (60, 150), "1": (205, 55), "3": (205, 245), "2": (435, 55), "4": (435, 245), "p": (580, 150)}
    return {k: (ox + v[0] * sx, oy + v[1] * sy) for k, v in base.items()}


def marker(c, k):
    """Pointe de flèche de taille fixe (indépendante de l'épaisseur du trait), remplie avec la classe f{k}."""
    mid = f"{SUB}-{c.name}-mk-{k}"
    if not any(mid in d for d in c.defs):
        c.defs.append(f'<marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" markerWidth="11" markerHeight="11" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="f{k}"/></marker>')
    return mid


def arc(c, P, Q, bend, cls, k, label=None, lab_cls="tx-s", off=11, r=R, style=""):
    """Arc courbé de P vers Q (comme drawArc) ; renvoie le point d'étiquette."""
    dx, dy = Q[0] - P[0], Q[1] - P[1]
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    cx, cy = (P[0] + Q[0]) / 2 - uy * bend * L, (P[1] + Q[1]) / 2 + ux * bend * L

    def towards(a, b, d):
        vx, vy = b[0] - a[0], b[1] - a[1]
        ll = math.hypot(vx, vy)
        return (a[0] + vx / ll * d, a[1] + vy / ll * d)
    s = towards(P, (cx, cy) if bend else Q, r)
    e = towards(Q, (cx, cy) if bend else P, r + 2)
    mk = marker(c, k)
    st = f' style="{style}"' if style else ""
    if bend:
        d = f"M{s[0]:.1f} {s[1]:.1f}Q{cx:.1f} {cy:.1f} {e[0]:.1f} {e[1]:.1f}"
        mid = (0.25 * s[0] + 0.5 * cx + 0.25 * e[0], 0.25 * s[1] + 0.5 * cy + 0.25 * e[1])
    else:
        d = f"M{s[0]:.1f} {s[1]:.1f}L{e[0]:.1f} {e[1]:.1f}"
        mid = ((s[0] + e[0]) / 2, (s[1] + e[1]) / 2)
    c.add(f'<path d="{d}" class="{cls}" fill="none" marker-end="url(#{mk})"{st}/>')
    side = -1 if bend < 0 else 1
    lx, ly = mid[0] - uy * off * side, mid[1] + ux * off * side
    if label is not None:
        c.add(f'<text x="{lx:.1f}" y="{ly + 4:.1f}" class="{lab_cls}" text-anchor="middle">{esc(label)}</text>')
    return (lx, ly)


def node(c, P, label, cls="f1", r=R, tcls="tx-b on-fill"):
    c.add(f'<circle cx="{P[0]:.1f}" cy="{P[1]:.1f}" r="{r}" class="{cls}"/>')
    c.add(f'<text x="{P[0]:.1f}" y="{P[1] + 4.5:.1f}" class="{tcls}" text-anchor="middle">{esc(label)}</text>')


def label_pos_override(a):
    """Décalage d'étiquette par arc, pour éviter les chevauchements."""
    return {("1", "3"): 13, ("2", "4"): 13, ("4", "2"): 13, ("2", "3"): 12, ("3", "2"): 12}.get(a, 11)


# ---------------------------------------------------------------------------------------------
def fig_graphe26():
    c = Canvas("graphe26", 640, 300, "Le graphe orienté de la diapo 26 : six nœuds s, 1, 2, 3, 4, p et douze arcs", sub=SUB)
    P = pos()
    for a in ARCS:
        arc(c, P[a[0]], P[a[1]], BEND[a], "ln ck thin", "k", f"[{a[0]},{a[1]}]", off=label_pos_override(a) + 2)
    for v in NODES:
        node(c, P[v], v, "f1")
    c.text(320, 292, "m = 6 nœuds, n = 12 arcs ; l'arc [i,j] va de i vers j", "tx-s", "middle")
    c.save()


def fig_flot():
    c = Canvas("flot", 640, 330, "Un flot chiffré sur le graphe de la diapo 26, vérifié nœud par nœud", sub=SUB)
    P = pos(oy=20)
    for a, x in zip(ARCS, FLOW5):
        if x > 0:
            arc(c, P[a[0]], P[a[1]], BEND[a], "ln c3", 3, str(x), "tx-b t3", off=label_pos_override(a) + 1,
                style=f"stroke-width:{1.4 + 0.7 * x:.1f}px")
        else:
            arc(c, P[a[0]], P[a[1]], BEND[a], "ln cm thin dash", "m", "0", "tx-s", off=label_pos_override(a))
    for v in NODES:
        node(c, P[v], v, "f1")
    # flots extérieurs
    s, p = P["s"], P["p"]
    c.arrow(s[0] - 52, s[1] - 40, s[0] - 14, s[1] - 10, 2, "ln c2 thin")
    c.text(s[0] - 56, s[1] - 46, "bₛ = +5", "tx-b t2", "start")
    c.arrow(p[0] + 14, p[1] - 10, p[0] + 50, p[1] - 40, 2, "ln c2 thin")
    c.text(p[0] + 8, p[1] - 46, "bₚ = −5", "tx-b t2", "start")
    # bilans
    bil = {"1": "entre 3, sort 3", "2": "entre 3, sort 3", "3": "entre 3, sort 3", "4": "entre 2, sort 2"}
    for v, t in bil.items():
        dy = -27 if v in ("1", "2") else 34
        c.text(P[v][0], P[v][1] + dy, t, "tx-s", "middle")
    c.text(s[0], s[1] + 36, "sort 5", "tx-s", "middle")
    c.text(p[0] + 6, p[1] + 40, "entre 5", "tx-s", "middle")
    c.save()


def fig_incidence():
    A = np.zeros((6, 12), int)
    for l, (j, k) in enumerate(ARCS):
        A[NODES.index(j), l] = 1
        A[NODES.index(k), l] = -1
    cw, ch, x0, y0 = 44, 28, 64, 46
    W, H = x0 + 12 * cw + 18, y0 + 6 * ch + 46
    c = Canvas("incidence", W, H, "La matrice d'incidence nœuds-arcs du graphe de la diapo 26 : un +1 au départ et un −1 à l'arrivée de chaque arc", sub=SUB)
    hl_col, hl_row = ARCS.index(("1", "3")), NODES.index("2")
    # surlignages
    c.add(f'<rect x="{x0 + hl_col * cw}" y="{y0 - 30}" width="{cw}" height="{6 * ch + 30}" class="a3"/>')
    c.add(f'<rect x="{x0 - 50}" y="{y0 + hl_row * ch}" width="{12 * cw + 50}" height="{ch}" class="a5"/>')
    for l, (j, k) in enumerate(ARCS):
        c.text(x0 + l * cw + cw / 2, y0 - 10, f"({j},{k})", "tx-s", "middle")
    for i, v in enumerate(NODES):
        c.text(x0 - 14, y0 + i * ch + ch / 2 + 5, f"nœud {v}", "tx-s", "end")
        for l in range(12):
            val = A[i, l]
            X, Y = x0 + l * cw, y0 + i * ch
            if val == 1:
                c.add(f'<rect x="{X + 3}" y="{Y + 3}" width="{cw - 6}" height="{ch - 6}" rx="4" class="a1"/>')
                c.text(X + cw / 2, Y + ch / 2 + 5, "+1", "tx-b t1", "middle")
            elif val == -1:
                c.add(f'<rect x="{X + 3}" y="{Y + 3}" width="{cw - 6}" height="{ch - 6}" rx="4" class="a2"/>')
                c.text(X + cw / 2, Y + ch / 2 + 5, "−1", "tx-b t2", "middle")
            else:
                c.text(X + cw / 2, Y + ch / 2 + 5, "0", "tx-s", "middle")
    c.add(f'<rect x="{x0}" y="{y0}" width="{12 * cw}" height="{6 * ch}" class="ln cm thin nofill"/>')
    yb = y0 + 6 * ch
    c.text(x0 + hl_col * cw + cw / 2, yb + 18, "colonne de (1,3) :", "tx-s t3", "middle")
    c.text(x0 + hl_col * cw + cw / 2, yb + 32, "+1 en 1, −1 en 3", "tx-s t3", "middle")
    c.text(x0 + 7 * cw, yb + 25, "ligne du nœud 2 = loi de Kirchhoff en 2 :", "tx-s t5", "start")
    c.text(x0 + 7 * cw, yb + 39, "(ce qui sort) − (ce qui entre) = b₂", "tx-s t5", "start")
    c.save()


def fig_libres():
    c = Canvas("libres", 640, 320, "Flot de coût minimum de valeur 5 : arcs vides, saturés et libres", sub=SUB)
    P = pos(oy=10)
    for a, x, u, cc in zip(ARCS, XMIN5, U, C):
        lab = f"{x}/{u}"
        if x == 0:
            arc(c, P[a[0]], P[a[1]], BEND[a], "ln cm thin dash", "m", lab, "tx-s", off=label_pos_override(a) + 1)
        elif x == u:
            arc(c, P[a[0]], P[a[1]], BEND[a], "ln c2", 2, lab, "tx-b t2", off=label_pos_override(a) + 2, style="stroke-width:3px")
        else:
            arc(c, P[a[0]], P[a[1]], BEND[a], "ln c3", 3, lab, "tx-b t3", off=label_pos_override(a) + 2, style="stroke-width:3px")
    for v in NODES:
        node(c, P[v], v, "f1")
    y = 300
    c.add(f'<line x1="40" y1="{y}" x2="66" y2="{y}" class="ln cm thin dash"/>')
    c.text(72, y + 4, "vide : x = 0", "tx-s")
    c.add(f'<line x1="200" y1="{y}" x2="226" y2="{y}" class="ln c2" style="stroke-width:3px"/>')
    c.text(232, y + 4, "saturé : x = u", "tx-s")
    c.add(f'<line x1="370" y1="{y}" x2="396" y2="{y}" class="ln c3" style="stroke-width:3px"/>')
    c.text(402, y + 4, "libre : 0 < x < u (une forêt)", "tx-s")
    c.text(320, 18, "étiquettes : flot / capacité ; bₛ = 5, bₚ = −5, coût 60", "tx-s", "middle")
    c.save()


def fig_transport():
    c = Canvas("transport", 660, 290, "Le constructeur automobile : graphe biparti usines vers concessionnaires, données puis flot optimal", sub=SUB)
    cost = {("U1", "C1"): 8, ("U1", "C2"): 15, ("U1", "C3"): 0, ("U2", "C1"): 10, ("U2", "C2"): 4, ("U2", "C3"): 0}
    xopt = {("U1", "C1"): 80, ("U1", "C2"): 0, ("U1", "C3"): 20, ("U2", "C1"): 0, ("U2", "C2"): 75, ("U2", "C3"): 5}
    for panel, ox in [(0, 0), (1, 340)]:
        Pu = {"U1": (ox + 70, 95), "U2": (ox + 70, 205)}
        Pc = {"C1": (ox + 240, 60), "C2": (ox + 240, 150), "C3": (ox + 240, 240)}
        P = {**Pu, **Pc}
        c.text(ox + 155, 22, "les données (coût cᵢⱼ)" if panel == 0 else "le flot optimal (coût 940)", "tx-b", "middle")
        for (i, j), cc in cost.items():
            if panel == 0:
                cls = "ln cm thin dash" if j == "C3" else "ln ck thin"
                arc(c, P[i], P[j], 0, cls, "k", None)
            else:
                x = xopt[(i, j)]
                if x > 0:
                    arc(c, P[i], P[j], 0, "ln c3", 3, None, style=f"stroke-width:{1.5 + x / 20:.1f}px")
                else:
                    arc(c, P[i], P[j], 0, "ln cm hair dash", "m", None)
            # étiquette près de l'arrivée (t = 0,7) pour éviter les croisements
            t = 0.68 if i == "U1" else 0.72
            X = P[i][0] + t * (P[j][0] - P[i][0])
            Y = P[i][1] + t * (P[j][1] - P[i][1])
            if panel == 0:
                c.add(f'<rect x="{X - 11:.1f}" y="{Y - 9:.1f}" width="22" height="15" rx="3" class="lbl-bg"/>')
                c.text(X, Y + 3, str(cc), "tx-b t2", "middle")
            elif xopt[(i, j)] > 0:
                c.add(f'<rect x="{X - 13:.1f}" y="{Y - 9:.1f}" width="26" height="15" rx="3" class="lbl-bg"/>')
                c.text(X, Y + 3, str(xopt[(i, j)]), "tx-b t3", "middle")
        bu = {"U1": "+100", "U2": "+80"}
        bc = {"C1": "−80", "C2": "−75", "C3": "−25"}
        for v, P0 in Pu.items():
            node(c, P0, v, "f1", r=19)
            c.text(P0[0] - 26, P0[1] + 5, bu[v], "tx-b t1", "end")
        for v, P0 in Pc.items():
            node(c, P0, v, "f5" if v != "C3" else "fm", r=19)
            c.text(P0[0] + 26, P0[1] + 5, bc[v], "tx-b t5", "start")
        if panel == 0:
            c.text(ox + 160, 280, "C3 : concessionnaire imaginaire, coûts nuls", "tx-s", "middle")
        else:
            c.text(ox + 160, 280, "C3 reçoit 20 + 5 = 25 voitures non livrées", "tx-s", "middle")
    c.save()


def fig_retour():
    c = Canvas("retour", 640, 340, "Le flot maximal comme flot de coût minimum : on ajoute l'arc retour (p, s) de coût −1", sub=SUB)
    P = pos(oy=0)
    for a, u in zip(ARCS, U):
        arc(c, P[a[0]], P[a[1]], BEND[a], "ln ck thin", "k", f"u={u}", "tx-s", off=label_pos_override(a) + 3)
    for v in NODES:
        node(c, P[v], v, "f1")
    # arc retour : grande courbe sous le graphe
    s, p = P["s"], P["p"]
    mk = c.arrow_marker(2)
    c.add(f'<path d="M{p[0] - 4:.1f} {p[1] + R:.1f} C{p[0] + 10:.1f} 330 {s[0] - 10:.1f} 330 {s[0] + 4:.1f} {s[1] + R + 2:.1f}" class="ln c2" fill="none" marker-end="url(#{mk})"/>')
    c.text(320, 322, "arc retour (p, s) : coût cₚₛ = −1, capacité +∞ ; tous les autres coûts = 0 ; b = 0 partout", "tx-b t2", "middle")
    c.save()


def fig_coupe():
    c = Canvas("coupe", 640, 330, "Un flot maximal de valeur 7 et la coupe minimale S = {s, 1, 3} de capacité 7", sub=SUB)
    P = pos(oy=14)
    S = {"s", "1", "3"}
    # région S
    c.add('<rect x="18" y="30" width="262" height="270" rx="16" class="a3"/>')
    c.add('<line x1="292" y1="24" x2="292" y2="306" class="ln c2 dash"/>')
    c.text(30, 48, "S = {s, 1, 3}", "tx-b t3")
    c.text(612, 48, "T = {2, 4, p}", "tx-b", "end")
    for a, x, u in zip(ARCS, XMAX, U):
        lab = f"{x}/{u}"
        cross = (a[0] in S) != (a[1] in S)
        if cross and a[0] in S:
            arc(c, P[a[0]], P[a[1]], BEND[a], "ln c2", 2, lab, "tx-b t2", off=label_pos_override(a) + 2, style="stroke-width:3px")
        elif x == 0:
            arc(c, P[a[0]], P[a[1]], BEND[a], "ln cm thin dash", "m", lab, "tx-s", off=label_pos_override(a) + 1)
        else:
            arc(c, P[a[0]], P[a[1]], BEND[a], "ln c1", 1, lab, "tx-b t1", off=label_pos_override(a) + 2,
                style=f"stroke-width:{1.4 + 0.5 * x:.1f}px")
    for v in NODES:
        node(c, P[v], v, "f3" if v in S else "f1")
    c.text(320, 324, "arcs de S vers T saturés : 2 + 2 + 3 = 7 ; arcs de T vers S vides ; valeur du flot = 3 + 4 = 7", "tx-s", "middle")
    c.save()


def fig_arbre():
    c = Canvas("arbre", 640, 320, "Arbre des plus courts chemins depuis s (Dijkstra), coûts sur les arcs, distances aux nœuds", sub=SUB)
    P = pos(oy=14)
    tree = {(PRED[v], v) for v in PRED}
    for a, cc in zip(ARCS, C):
        if a in tree:
            arc(c, P[a[0]], P[a[1]], BEND[a], "ln c3", 3, str(cc), "tx-b t3", off=label_pos_override(a) + 1, style="stroke-width:3.2px")
        else:
            arc(c, P[a[0]], P[a[1]], BEND[a], "ln cm thin", "m", str(cc), "tx-s", off=label_pos_override(a))
    for v in NODES:
        node(c, P[v], v, "f3")
        dy = -26 if v in ("1", "2") else 36
        if v in ("s", "p"):
            dy = 36
        c.text(P[v][0], P[v][1] + dy, f"d = {DIST[v]}", "tx-b t3", "middle")
    c.text(320, 312, "plus court chemin s → 1 → 3 → 2 → 4 → p : 2 + 2 + 2 + 3 + 2 = 11", "tx-s", "middle")
    c.save()


def fig_birkhoff():
    c = Canvas("birkhoff", 660, 320, "Le polytope de Birkhoff : B2 est un segment, une ombre plane de B3 est un hexagone dont les sommets sont des permutations", sub=SUB)
    # --- B2 : segment
    c.text(120, 22, "B₂ : un segment", "tx-b", "middle")
    xa, xb, y = 40, 200, 150

    def mat2(x, yy, t, cls):
        vals = [[t, 1 - t], [1 - t, t]]
        for i in range(2):
            for j in range(2):
                v = vals[i][j]
                s = "1" if v == 1 else "0" if v == 0 else "t" if (i == j) else "1−t"
                c.text(x + j * 26, yy + i * 16, s, cls, "middle")
        c.add(f'<path d="M{x - 14} {yy - 13} l-4 0 l0 {32} l4 0" class="ln cm hair"/>')
        c.add(f'<path d="M{x + 40} {yy - 13} l4 0 l0 {32} l-4 0" class="ln cm hair"/>')
    c.add(f'<line x1="{xa}" y1="{y}" x2="{xb}" y2="{y}" class="ln c1"/>')
    c.add(f'<circle cx="{xa}" cy="{y}" r="6" class="f3"/><circle cx="{xb}" cy="{y}" r="6" class="f3"/>')
    c.add(f'<circle cx="{(xa + xb) / 2}" cy="{y}" r="4" class="f1"/>')
    mat2(xa - 13, y - 52, 1, "tx-s")
    mat2(xb - 13, y - 52, 0, "tx-s")
    mat2((xa + xb) / 2 - 13, y + 30, 0.5, "tx-s")
    c.text(xa, y + 22, "Id", "tx-s t3", "middle")
    c.text(xb, y + 22, "échange", "tx-s t3", "middle")
    c.text(120, 250, "matrices [[t, 1−t], [1−t, t]], 0 ≤ t ≤ 1 ;", "tx-s", "middle")
    c.text(120, 266, "les extrémités t = 1 et t = 0", "tx-s", "middle")
    c.text(120, 282, "sont les deux permutations", "tx-s", "middle")
    # --- B3 : ombre (projection plane)
    Cm = np.array([[6, 2, 7], [3, 1, 5], [4, 3, 8]])
    Dm = np.array([[0, 0, 0], [0, 2, 0], [0, 3, 0]])
    perms = list(itertools.permutations(range(3)))
    pts = []
    for sg in perms:
        M = np.zeros((3, 3))
        for i in range(3):
            M[i, sg[i]] = 1
        pts.append(((Cm * M).sum(), (Dm * M).sum(), sg))
    f = Fig(c, (300, 52, 320, 178), (10.5, 15.5), (-0.5, 3.6))
    hull_order = [(1, 2, 0), (1, 0, 2), (0, 1, 2), (0, 2, 1), (2, 0, 1), (2, 1, 0)]  # ordre le long du bord
    poly = [next((p[0], p[1]) for p in pts if p[2] == h) for h in hull_order]
    f.path(poly, "a1", close=True)
    f.path(poly + [poly[0]], "ln c1 thin")
    for xv in [11, 12, 13, 14, 15]:
        f.line(xv, -0.5, xv, 3.6, "ln c2 hair dash")
        f.text(xv, -0.5, str(xv), "tx-s t2", "middle", dy=14)
    f.text(15.5, -0.5, "→ coût", "tx-s t2", "end", dy=28)
    # centre J/3
    cx, cy = Cm.sum() / 3, Dm.sum() / 3
    f.circle(cx, cy, 4, "f1")
    f.text(cx, cy, "J/3 (coût 13)", "tx-s t1", "start", dx=6, dy=-6)
    for (x, yv, sg) in pts:
        lab = "σ = (" + ",".join(str(t + 1) for t in sg) + ")"
        best = (x == 11)
        f.circle(x, yv, 6 if best else 4.5, "f3" if best else "fk")
        anchor = "end" if x <= 12.5 else "start"
        dx = -9 if anchor == "end" else 9
        dy = 16 if yv < 1 else -8
        f.text(x, yv, lab, "tx-b t3" if best else "tx-s", anchor, dx=dx, dy=dy)
    c.text(460, 22, "une ombre plane de B₃ (6 permutations)", "tx-b", "middle")
    c.text(460, 290, "abscisse : coût Σ cᵢⱼ vᵢⱼ de l'exemple 3 × 3 ; ordonnée : 2v₂₂ + 3v₃₂", "tx-s", "middle")
    c.text(460, 306, "le minimum du coût est atteint en un sommet : σ = (2,3,1), coût 11", "tx-s t3", "middle")
    c.save()


def fig_treillis():
    c = Canvas("treillis", 640, 230, "Le décodage de Viterbi comme plus court chemin dans un treillis", sub=SUB)
    xs = [60, 200, 340, 480, 600]
    ys = {"Soleil": 70, "Pluie": 160}
    obs = ["promenade", "ménage", "courses"]
    path = [("dep", None), (1, "Soleil"), (2, "Pluie"), (3, "Pluie")]
    best = {(0, "Soleil"), (1, "Pluie"), (2, "Pluie")}
    node(c, (xs[0], 115), "départ", "fm", r=24, tcls="tx-s on-fill")
    for t in range(3):
        c.text(xs[t + 1], 24, f"t = {t + 1} : {obs[t]}", "tx-b", "middle")
        for st, y in ys.items():
            P = (xs[t + 1], y)
            if t == 0:
                on = (0, st) in best
                arc(c, (xs[0], 115), P, 0, "ln c3" if on else "ln cm thin", 3 if on else "m", r=24 if False else 22,
                    style="stroke-width:3px" if on else "")
            else:
                for st0, y0 in ys.items():
                    on = (t - 1, st0) in best and (t, st) in best
                    arc(c, (xs[t], y0), P, 0, "ln c3" if on else "ln cm thin", 3 if on else "m", r=22,
                        style="stroke-width:3px" if on else "")
    for t in range(3):
        for st, y in ys.items():
            node(c, (xs[t + 1], y), st, "f3" if (t, st) in best else "f1", r=22, tcls="tx-s on-fill")
    for st, y in ys.items():
        on = (2, st) in best   # le chemin vert se termine par l'arc vers « fin »
        arc(c, (xs[3], y), (xs[4], 115), 0, "ln c3" if on else "ln cm thin", 3 if on else "m", r=22,
            style="stroke-width:3px" if on else "")
    node(c, (xs[4], 115), "fin", "fm", r=22, tcls="tx-s on-fill")
    c.text(320, 210, "coût d'un arc = −ln(probabilité initiale ou de transition × probabilité d'émission) ≥ 0", "tx-s", "middle")
    c.text(320, 225, "chemin le plus court = suite d'états la plus probable : Soleil, Pluie, Pluie", "tx-s t3", "middle")
    c.save()


if __name__ == "__main__":
    fig_graphe26()
    fig_flot()
    fig_incidence()
    fig_libres()
    fig_transport()
    fig_retour()
    fig_coupe()
    fig_arbre()
    fig_birkhoff()
    fig_treillis()
