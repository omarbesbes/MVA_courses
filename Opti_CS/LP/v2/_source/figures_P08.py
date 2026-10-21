"""figures_P08.py — static SVG figures of Partie 8 (problèmes entiers célèbres), written to figures/P08/.

Run: python3 figures_P08.py        (then node build.mjs Partie08.html)

Every number drawn here is recomputed here (exact fractions for the knapsack, integer distances for the
travelling salesman), with the same data as the page and the widgets:
  sac-à-dos : poids p = (4, 4, 8, 2, 8), utilités u = (16, 15, 22, 4, 12), capacité L = 14 (objets A…E) ;
  voyageur  : 6 villes, distances euclidiennes arrondies à l'entier (convention de la TSPLIB) ;
  voyageur à 4 villes : d12 = 4, d13 = 7, d14 = 5, d23 = 3, d24 = 6, d34 = 2.
"""
import itertools
import math
from fractions import Fraction as F

from figures_common import Canvas, Fig, esc

SUB = "P08"

# ------------------------------------------------------------------ données communes
P_KS = [4, 4, 8, 2, 8]
U_KS = [16, 15, 22, 4, 12]
L_KS = 14
NAMES = "ABCDE"

CITIES = [(20, 20), (35, 30), (25, 0), (65, 10), (65, 30), (75, 50)]
D4 = [[0, 4, 7, 5], [4, 0, 3, 6], [7, 3, 0, 2], [5, 6, 2, 0]]


def fr(x):
    """A fraction in French typography: 47,5 ; 3/4 written ¾ when it is a common one."""
    x = F(x)
    special = {F(1, 2): "½", F(1, 4): "¼", F(3, 4): "¾", F(1, 3): "⅓", F(2, 3): "⅔"}
    if x in special:
        return special[x]
    if x.denominator == 1:
        return str(x.numerator)
    if x.denominator in (2, 4, 5, 8, 10):
        s = f"{float(x):g}"
        return s.replace(".", ",")
    return f"{x.numerator}/{x.denominator}"


def sub(base, s):
    """Text with a subscript (SVG tspan): x with subscript C."""
    return f'{esc(base)}<tspan baseline-shift="sub" font-size="72%">{esc(s)}</tspan>'


def raw_text(c, x, y, html, cls="tx", anchor="start"):
    c.add(f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}">{html}</text>')


# ------------------------------------------------------------------ sac-à-dos : outils exacts
def relax(p, u, L, fixed):
    n = len(p)
    x = [F(0)] * n
    cap = F(L)
    val = F(0)
    for j, v in fixed.items():
        if v == 1:
            x[j] = F(1)
            cap -= p[j]
            val += u[j]
    if cap < 0:
        return None, None
    free = sorted((j for j in range(n) if j not in fixed), key=lambda j: (-F(u[j], p[j]), j))
    for j in free:
        if p[j] <= cap:
            x[j] = F(1)
            cap -= p[j]
            val += u[j]
        else:
            x[j] = cap / p[j]
            val += u[j] * x[j]
            break
    return val, x


def greedy(p, u, L):
    cap, val, x = L, 0, [0] * len(p)
    for j in sorted(range(len(p)), key=lambda j: (-F(u[j], p[j]), j)):
        if p[j] <= cap:
            x[j] = 1
            cap -= p[j]
            val += u[j]
    return val, x


def bnb(p, u, L):
    """Depth first, branch x = 1 first, start from the greedy solution, prune when bound <= best known."""
    g, gx = greedy(p, u, L)
    best = [g]
    nodes = []

    def visit(fixed, parent, depth):
        b, x = relax(p, u, L, fixed)
        nd = dict(id=len(nodes), parent=parent, fixed=dict(fixed), bound=b, x=x, depth=depth, best_before=best[0], kids=[])
        nodes.append(nd)
        if parent is not None:
            nodes[parent]["kids"].append(nd["id"])
        if b is None:
            nd["dec"] = "infeasible"
            return
        if b <= best[0]:
            nd["dec"] = "pruned"
            return
        frac = [j for j in range(len(p)) if x[j].denominator != 1]
        if not frac:
            nd["dec"] = "integer"
            best[0] = int(b)
            return
        k = frac[0]
        nd["dec"] = "branch"
        nd["branch"] = k
        for v in (1, 0):
            f2 = dict(fixed)
            f2[k] = v
            visit(f2, nd["id"], depth + 1)

    visit({}, None, 0)
    return nodes, best[0], g


# ------------------------------------------------------------------ voyageur : outils
def dist_nint(P):
    return [[int(math.floor(math.hypot(a[0] - b[0], a[1] - b[1]) + 0.5)) for b in P] for a in P]


def tour_len(D, t):
    return sum(D[t[k]][t[(k + 1) % len(t)]] for k in range(len(t)))


def best_tour(D):
    n = len(D)
    tours = [(0,) + q for q in itertools.permutations(range(1, n)) if q[0] < q[-1]]
    return min((tour_len(D, t), t) for t in tours)


def nearest_neighbour(D, s=0):
    t, left = [s], set(range(len(D))) - {s}
    while left:
        j = min(left, key=lambda v: (D[t[-1]][v], v))
        t.append(j)
        left.remove(j)
    return tour_len(D, t), t


def cycle_covers(nodes):
    nodes = tuple(sorted(nodes))
    if not nodes:
        yield []
        return
    first, rest = nodes[0], nodes[1:]
    for k in range(2, len(rest) + 1):
        for others in itertools.combinations(rest, k):
            remaining = tuple(v for v in rest if v not in others)
            if 0 < len(remaining) < 3:
                continue
            for perm in itertools.permutations(others):
                if perm[0] < perm[-1]:
                    for cov in cycle_covers(remaining):
                        yield [(first,) + perm] + cov


# ================================================================== 1. croissance
def fig_croissance():
    c = Canvas("croissance", 620, 320, "Croissance de N au cube, 2 puissance N et (N-1)!/2, en échelle logarithmique", sub=SUB)
    f = Fig(c, (62, 20, 470, 250), (2, 25), (0, 27))
    sup = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
    f.axes(xticks=[5, 10, 15, 20, 25], yticks=[0, 3, 6, 9, 12, 15, 18, 21, 24, 27],
           yfmt=lambda v: "10" + str(v).translate(sup), xlabel="nombre N d'objets ou de villes")
    refs = [(9, "1 seconde à 10⁹ opérations par seconde"), (math.log10(365.25 * 86400 * 1e9), "1 an"),
            (math.log10(1.38e10 * 365.25 * 86400 * 1e9), "âge de l'Univers")]
    for y, lab in refs:
        f.line(2, y, 25, y, "ln cm thin dash")
        f.text(2.3, y, lab, "tx-s", "start", dy=-4)
    Ns = list(range(3, 26))
    series = [
        (lambda n: 3 * math.log10(n), "c3", "f3", "N³ (polynomial)"),
        (lambda n: n * math.log10(2), "c4", "f4", "2ᴺ (sous-ensembles : sac-à-dos)"),
        (lambda n: math.log10(math.factorial(n - 1) / 2), "c2", "f2", "(N−1)!/2 (tournées du voyageur)"),
    ]
    for g, cl, fl, lab in series:
        pts = [(n, g(n)) for n in Ns]
        f.path(pts, f"ln {cl}")
        for n, y in pts[::2]:
            f.circle(n, y, 2.6, fl)
    f.text(25, 3 * math.log10(25), "N³", "tx-b t3", "start", dx=6, dy=4)
    f.text(25, 25 * math.log10(2), "2ᴺ", "tx-b t4", "start", dx=6, dy=4)
    f.text(24.6, math.log10(math.factorial(23) / 2), "(N−1)!/2", "tx-b t2", "end", dx=-6, dy=-2)
    # legend
    for i, (g, cl, fl, lab) in enumerate(series):
        y = 62 + 18 * i
        c.add(f'<line x1="80" y1="{y - 4}" x2="100" y2="{y - 4}" class="ln {cl}"/>')
        c.text(106, y, lab, "tx-s")
    c.save()


# ================================================================== 2. objets
def fig_objets():
    W, H = 660, 344
    c = Canvas("objets", W, H, "Les cinq objets du sac-à-dos et trois façons de remplir un sac de capacité 14", sub=SUB)
    unit = 30  # px per unit of weight
    x0 = 150
    # objects row: cards of equal width (the bags below are to scale)
    raw_text(c, 12, 40, "les objets", "tx-b")
    raw_text(c, 12, 56, "triés par u/p décroissant", "tx-s")
    for j in range(5):
        x = x0 + j * 98
        c.add(f'<rect x="{x:.1f}" y="18" width="90" height="66" rx="6" class="am ln cm thin"/>')
        raw_text(c, x + 45, 36, esc(NAMES[j]), "tx-b", "middle")
        raw_text(c, x + 45, 54, f"p = {P_KS[j]},  u = {U_KS[j]}", "tx-s", "middle")
        raw_text(c, x + 45, 72, "u/p = " + fr(F(U_KS[j], P_KS[j])), "tx-s", "middle")
    # three bags
    g, gx = greedy(P_KS, U_KS, L_KS)
    b, rx = relax(P_KS, U_KS, L_KS, {})
    opt = max(((sum(u * t for u, t in zip(U_KS, xx)), xx) for xx in itertools.product([0, 1], repeat=5)
               if sum(p * t for p, t in zip(P_KS, xx)) <= L_KS))
    rows = [
        ("glouton", [F(v) for v in gx], "4", f"utilité {g}, poids {sum(p * t for p, t in zip(P_KS, gx))}"),
        ("optimum", [F(v) for v in opt[1]], "3", f"utilité {opt[0]}, poids {sum(p * t for p, t in zip(P_KS, opt[1]))}"),
        ("relaxation", rx, "5", f"borne {fr(b)}, sac plein"),
    ]
    for r, (name, xs, k, summ) in enumerate(rows):
        y = 120 + 66 * r
        raw_text(c, 12, y + 20, esc(name), "tx-b")
        raw_text(c, 12, y + 36, esc(summ), "tx-s")
        c.add(f'<rect x="{x0}" y="{y}" width="{L_KS * unit}" height="40" rx="4" class="ln cm thin dash nofill"/>')
        xx = x0
        for j in range(5):
            if xs[j] == 0:
                continue
            w = float(xs[j]) * P_KS[j] * unit
            cls = f"a{k} ln c{k} thin"
            c.add(f'<rect x="{xx + 1:.1f}" y="{y + 2}" width="{w - 2:.1f}" height="36" rx="3" class="{cls}"/>')
            lab = NAMES[j] if xs[j] == 1 else fr(xs[j]) + " " + NAMES[j]
            raw_text(c, xx + w / 2, y + 25, esc(lab), "tx-b", "middle")
            xx += w
        if xx < x0 + L_KS * unit - 1:
            raw_text(c, (xx + x0 + L_KS * unit) / 2, y + 25, f"vide : {round((x0 + L_KS * unit - xx) / unit)}", "tx-s", "middle")
    # capacity ruler
    yy = 120 + 66 * 3 - 8
    c.add(f'<line x1="{x0}" y1="{yy}" x2="{x0 + L_KS * unit}" y2="{yy}" class="ax"/>')
    for t in range(0, L_KS + 1, 2):
        c.add(f'<line x1="{x0 + t * unit}" y1="{yy - 3}" x2="{x0 + t * unit}" y2="{yy + 3}" class="ax"/>')
        raw_text(c, x0 + t * unit, yy + 15, str(t), "tx-s", "middle")
    raw_text(c, x0 + L_KS * unit, yy + 30, "poids ; capacité L = 14 (largeur = poids)", "tx-s", "end")
    c.save()


# ================================================================== 3. arbre de séparation-évaluation
def fig_arbre():
    nodes, best, g = bnb(P_KS, U_KS, L_KS)
    W, H = 660, 380
    c = Canvas("arbre", W, H, "Arbre de séparation-évaluation complet du sac-à-dos (capacité 14)", sub=SUB)
    # layout: leaves get consecutive slots (DFS order), parents centred above their children
    slot = [0]
    pos = {}

    def place(i):
        nd = nodes[i]
        if not nd["kids"]:
            pos[i] = slot[0]
            slot[0] += 1
        else:
            for k in nd["kids"]:
                place(k)
            pos[i] = sum(pos[k] for k in nd["kids"]) / len(nd["kids"])

    place(0)
    nslots = slot[0]
    bw, bh = 150, 58
    X = lambda s: 20 + bw / 2 + s * (W - 40 - bw) / (nslots - 1)
    Y = lambda d: 18 + d * 92
    mark = {"branch": ("ln c1 thin", "a1"), "infeasible": ("ln cm thin dash", "am"), "integer": ("ln c3", "a3"),
            "pruned": ("ln c6 thin", "nofill")}
    # edges first
    for nd in nodes:
        if nd["parent"] is None:
            continue
        pa = nodes[nd["parent"]]
        x1, y1 = X(pos[pa["id"]]), Y(pa["depth"]) + bh
        x2, y2 = X(pos[nd["id"]]), Y(nd["depth"])
        c.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" class="ln cm thin"/>')
        k = pa["branch"]
        v = nd["fixed"][k]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        anchor = "end" if x2 < x1 else "start"
        dx = -8 if x2 < x1 else 8
        c.add(f'<rect x="{mx + (dx - 50 if anchor == "end" else dx - 2):.1f}" y="{my - 12:.1f}" width="52" height="17" rx="3" class="lbl-bg"/>')
        raw_text(c, mx + dx, my + 1, sub("x", NAMES[k]) + f" = {v}", "tx-b", anchor)
    for nd in nodes:
        x, y = X(pos[nd["id"]]) - bw / 2, Y(nd["depth"])
        stroke, fill = mark[nd["dec"]]
        c.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw}" height="{bh}" rx="8" class="fs"/>')
        c.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw}" height="{bh}" rx="8" class="{fill} {stroke}"/>')
        cx = x + bw / 2
        num = f"nœud {nd['id']}"
        if nd["bound"] is None:
            used = sum(P_KS[j] for j, v in nd["fixed"].items() if v == 1)
            l1, l2, l3 = num, f"poids fixé {used} > 14", "irréalisable"
        else:
            l1 = f"{num} · borne {fr(nd['bound'])}"
            l2 = "x = (" + ", ".join(fr(t) for t in nd["x"]) + ")"
            if nd["dec"] == "branch":
                l3 = f"fractionnaire : séparer sur {NAMES[nd['branch']]}"
            elif nd["dec"] == "integer":
                l3 = f"entier : meilleure = {int(nd['bound'])}"
            else:
                l3 = f"{fr(nd['bound'])} ≤ {nd['best_before']} : élagué"
        raw_text(c, cx, y + 17, esc(l1), "tx-b", "middle")
        raw_text(c, cx, y + 34, esc(l2), "tx-s", "middle")
        cls3 = {"integer": "tx-s t3", "pruned": "tx-s t6", "infeasible": "tx-s", "branch": "tx-s t1"}[nd["dec"]]
        raw_text(c, cx, y + 50, esc(l3), cls3, "middle")
    # incumbent story
    integ = [nd for nd in nodes if nd["dec"] == "integer"]
    story = f"meilleure solution connue : {g} (glouton)" + "".join(f" → {int(nd['bound'])} (nœud {nd['id']})" for nd in integ)
    raw_text(c, W - 14, H - 12, esc(story), "tx-s", "end")
    raw_text(c, W - 14, H - 28, esc(f"{len(nodes)} nœuds évalués, au lieu des 2⁵ = 32 choix"), "tx-s", "end")
    c.save()
    return nodes


# ================================================================== 4. fonction duale lagrangienne
def fig_lagrange():
    c = Canvas("lagrange", 600, 310, "Fonction duale de la relaxation lagrangienne du sac-à-dos", sub=SUB)
    f = Fig(c, (56, 20, 500, 240), (0, 5), (30, 75))

    def G(lam):
        lam = F(lam)
        return lam * L_KS + sum(max(F(0), U_KS[j] - lam * P_KS[j]) for j in range(5))

    ratios = sorted({F(U_KS[j], P_KS[j]) for j in range(5)})
    f.axes(xticks=[0, 1, 2, 3, 4, 5], yticks=[30, 40, 50, 60, 70], xlabel="multiplicateur λ ≥ 0", ylabel="G(λ)")
    pts = [F(0)] + ratios + [F(5)]
    f.path([(float(t), float(G(t))) for t in pts], "ln c5")
    for t in ratios:
        f.circle(float(t), float(G(t)), 3, "f5")
    opt = 42
    best = min(G(t) for t in ratios)
    lam_star = min(ratios, key=G)
    f.line(0, opt, 5, opt, "ln c3 thin dash")
    f.text(4.95, opt, "optimum entier : 42", "tx-s t3", "end", dy=-5)
    f.line(0, float(best), 5, float(best), "ln cm thin dot")
    f.circle(float(lam_star), float(best), 5, "f5")
    f.text(float(lam_star), float(best), f"min G = G({lam_star.numerator}/{lam_star.denominator}) = {fr(best)}", "tx-b t5", "middle", dy=18)
    f.text(0.05, float(G(0)), f"G(0) = {fr(G(0))} = somme des utilités", "tx-s", "start", dx=6, dy=4)
    # ratio labels under the axis
    for t in ratios:
        f.line(float(t), 30, float(t), float(G(t)), "ln cm hair dot")
    raw_text(c, f.X(2.5), f.Y(73), "coudes aux rapports u/p des objets : 3/2, 2, 11/4, 15/4, 4", "tx-s", "middle")
    c.save()


# ================================================================== 5. arbre des tournées (N = 4)
def lb_path(D, path):
    n = len(D)
    U = [v for v in range(n) if v not in path]
    s = sum(D[path[i]][path[i + 1]] for i in range(len(path) - 1))
    if not U:
        return s + D[path[-1]][0]
    s += min(D[path[-1]][z] for z in U)
    for w in U:
        s += min(D[w][z] for z in [v for v in U if v != w] + [0])
    return s


def fig_arbre_tours():
    D = D4
    m = nearest_neighbour(D)[0]
    W, H = 660, 318
    c = Canvas("arbre-tours", W, H, "Arbre des tournées d'un voyageur à 4 villes, avec bornes et élagage", sub=SUB)
    # build the full tree of paths starting at city 1 (index 0)
    nodes = []

    def build(path, parent):
        i = len(nodes)
        nodes.append(dict(path=path, parent=parent, kids=[]))
        if parent is not None:
            nodes[parent]["kids"].append(i)
        if len(path) < len(D):
            for v in range(len(D)):
                if v not in path:
                    build(path + [v], i)

    build([0], None)
    # simulate the search with m from the nearest neighbour: visited / pruned
    status = {}

    def visit(i):
        nd = nodes[i]
        b = lb_path(D, nd["path"])
        nd["bound"] = b
        if b >= m:
            status[i] = "pruned"
            return
        status[i] = "branch"
        for k in nd["kids"]:
            visit(k)

    visit(0)
    slot = [0]
    pos = {}

    def place(i):
        nd = nodes[i]
        if not nd["kids"]:
            pos[i] = slot[0]
            slot[0] += 1
        else:
            for k in nd["kids"]:
                place(k)
            pos[i] = sum(pos[k] for k in nd["kids"]) / len(nd["kids"])

    place(0)
    X = lambda s: 60 + s * (W - 120) / 5
    Y = lambda d: 24 + d * 74
    bw, bh = 92, 38
    for i, nd in enumerate(nodes):
        if nd["parent"] is None:
            continue
        pa = nd["parent"]
        cls = "ln cm thin" if i in status else "ln cm hair dot"
        c.add(f'<line x1="{X(pos[pa]):.1f}" y1="{Y(len(nodes[pa]["path"]) - 1) + bh:.1f}" x2="{X(pos[i]):.1f}" y2="{Y(len(nd["path"]) - 1):.1f}" class="{cls}"/>')
    for i, nd in enumerate(nodes):
        d = len(nd["path"]) - 1
        x, y = X(pos[i]) - bw / 2, Y(d)
        label = "→".join(str(v + 1) for v in nd["path"])
        if len(nd["path"]) == len(D):
            label += "→1"
            line2 = f"longueur {tour_len(D, nd['path'])}"
        else:
            line2 = f"borne {lb_path(D, nd['path'])}"
        st = status.get(i)
        if st == "branch":
            cls = "a1 ln c1 thin"
        elif st == "pruned":
            cls = "nofill ln c6 thin"
        else:
            cls = "nofill ln cm hair dash"
        c.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw}" height="{bh}" rx="6" class="{cls}"/>')
        tcls = "tx-b" if st else "tx-s"
        raw_text(c, x + bw / 2, y + 15, esc(label), tcls, "middle")
        raw_text(c, x + bw / 2, y + 31, esc(line2), "tx-s t6" if st == "pruned" else "tx-s", "middle")
    raw_text(c, 12, H - 8, esc(f"m = {m} (plus proche voisin depuis 1).  Bleu : séparé ;  rose : borne ≥ m, élagué ;  pointillés : jamais examinés."), "tx-s")
    c.save()


# ================================================================== 6. sous-tours
def fig_sous_tours():
    D = dist_nint(CITIES)
    T, tb = best_tour(D)
    NN, nt = nearest_neighbour(D, 0)
    covers = sorted(cycle_covers(range(6)), key=lambda cv: sum(tour_len(D, cy) for cy in cv))
    two = covers[0]
    assert len(two) == 2
    W, H = 660, 250
    c = Canvas("sous-tours", W, H, "Six villes : la solution des seules contraintes de degré, la tournée optimale et le plus proche voisin", sub=SUB)
    panels = [
        ("contraintes de degré seules", [list(cy) for cy in two], "c6", f"deux sous-tours : {sum(tour_len(D, cy) for cy in two)}"),
        ("tournée optimale", [list(tb)], "c3", f"longueur {T}"),
        ("plus proche voisin depuis 1", [list(nt)], "c4", f"longueur {NN}"),
    ]
    for k, (title, cycles, cl, foot) in enumerate(panels):
        f = Fig(c, (14 + k * 218, 34, 196, 160), (12, 83), (-6, 56))
        raw_text(c, 14 + k * 218 + 98, 18, esc(title), "tx-b", "middle")
        for cy in cycles:
            for a in range(len(cy)):
                i, j = cy[a], cy[(a + 1) % len(cy)]
                f.line(*CITIES[i], *CITIES[j], f"ln {cl}")
                t = {(0, 5): 0.72, (5, 0): 0.28}.get((i, j), 0.5)
                mx = (1 - t) * f.X(CITIES[i][0]) + t * f.X(CITIES[j][0])
                my = (1 - t) * f.Y(CITIES[i][1]) + t * f.Y(CITIES[j][1])
                vx, vy = f.X(CITIES[j][0]) - f.X(CITIES[i][0]), f.Y(CITIES[j][1]) - f.Y(CITIES[i][1])
                ln = math.hypot(vx, vy)
                nx, ny = -vy / ln, vx / ln
                # put the label on the side away from the centre of the panel
                cxp, cyp = f.X(47), f.Y(25)
                if (mx - cxp) * nx + (my - cyp) * ny < 0:
                    nx, ny = -nx, -ny
                raw_text(c, mx + 9 * nx, my + 9 * ny + 4, str(D[i][j]), "tx-s", "middle")
        for v, (x, y) in enumerate(CITIES):
            c.add(f'<circle cx="{f.X(x):.1f}" cy="{f.Y(y):.1f}" r="10" class="f1"/>')
            raw_text(c, f.X(x), f.Y(y) + 4.5, str(v + 1), "on-fill", "middle")
        raw_text(c, 14 + k * 218 + 98, H - 14, esc(foot), f"tx-b t{cl[1]}", "middle")
    c.save()
    return D, T, NN, two


# ================================================================== 7. ReLU et big-M
def fig_relu():
    l, u = -1, 2
    c = Canvas("relu", 620, 330, "Encodage big-M d'un ReLU : graphe, enveloppe convexe et relaxations continues", sub=SUB)
    f = Fig(c, (56, 20, 380, 260), (-1.3, 2.3), (-0.4, 3.3))
    f.axes(xticks=[-1, 0, 1, 2], yticks=[0, 1, 2, 3], xlabel="x (entrée du neurone)", ylabel="y")
    # big-M relaxations (z in [0,1]) projected: y >= 0, y >= x, y <= (x + M)/2, for x in [l, u]
    for M, cls, lab in [(4, "ln c6 thin dot", "M = 4"), (2, "ln c5 thin dash", "M = 2")]:
        poly = [(l, 0), (0, 0), (u, u), (u, min((u + M) / 2, M)), (l, (l + M) / 2)]
        f.path(poly, cls + " nofill", close=True)
        f.text(1.0, (1.0 + M) / 2, lab, "tx-b t" + cls.split()[1][1], "middle", dy=-7)
    # convex hull (triangle)
    f.path([(l, 0), (0, 0), (u, u)], "a1 ln c1 thin", close=True)
    f.line(l, 0, 0, 0, "ln c3")
    f.line(0, 0, u, u, "ln c3")
    f.text(1.25, 1.25, "y = max(0, x)", "tx-b t3", "start", dx=8, dy=10)
    # legend and constraints
    x0 = 452
    lines = [
        ("z ∈ {0, 1} :", "tx-b"),
        ("y ≥ x,  y ≥ 0", "tx-s"),
        ("y ≤ x + M(1 − z)", "tx-s"),
        ("y ≤ M z", "tx-s"),
        ("", "tx-s"),
        ("z = 1 ⇒ y = x ≥ 0", "tx-s t3"),
        ("z = 0 ⇒ y = 0 ≥ x", "tx-s t3"),
        ("", "tx-s"),
        ("relaxé (0 ≤ z ≤ 1) :", "tx-b"),
        ("y ≤ (x + M)/2", "tx-s"),
        ("", "tx-s"),
        ("ici l = −1, u = 2 ;", "tx-s"),
        ("M = 2 est le plus petit", "tx-s"),
        ("M valable : max(|l|, u)", "tx-s"),
        ("", "tx-s"),
        ("bleu : enveloppe convexe", "tx-s t1"),
        ("du graphe sur [l, u]", "tx-s t1"),
    ]
    for i, (s, cls) in enumerate(lines):
        if s:
            raw_text(c, x0, 34 + 17 * i, esc(s), cls)
    c.save()


if __name__ == "__main__":
    fig_croissance()
    fig_objets()
    nodes = fig_arbre()
    fig_lagrange()
    fig_arbre_tours()
    D, T, NN, two = fig_sous_tours()
    fig_relu()
    print("arbre :", [(n["id"], str(n["bound"]), n["dec"]) for n in nodes])
    print("voyageur : optimum", T, "plus proche voisin", NN, "deux sous-tours", [[v + 1 for v in cy] for cy in two])
