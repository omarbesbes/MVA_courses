"""figures_P04.py — static SVG figures of Partie 4 (interior point methods), written to figures/P04/.

Run: python3 figures_P04.py        (then node build.mjs Partie04.html)

Every coordinate is computed here: central paths by Newton's method on the barrier, simplex paths in exact
arithmetic, path-following runs with the same rule as the widgets (halve the step until the point stays inside
and the penalized function decreases). Colour code of the page: X_ad blue (1), cost and level lines orange-red (2),
optimum and simplex path green (3), Newton / path-following iterates gold (4), dual objects violet (5),
non-admissible points pink (6), central path in the text colour (ck).
"""
import math
import re
from fractions import Fraction as Fr

import numpy as np

from figures_common import Canvas, Fig

SUB = "P04"


def rich(s):
    """Text with _{..} (subscript) and ^{..} (superscript) turned into SVG tspans (no '_' or '^' is shown)."""
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    s = re.sub(r"_\{([^}]*)\}", r'<tspan baseline-shift="sub" font-size="75%">\1</tspan>', s)
    s = re.sub(r"\^\{([^}]*)\}", r'<tspan baseline-shift="super" font-size="75%">\1</tspan>', s)
    return s


def T(c, x, y, s, cls="tx-s", anchor="start"):
    c.add(f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}">{rich(s)}</text>')


def FT(f, x, y, s, cls="tx-s", anchor="start", dx=0, dy=0):
    T(f.c, f.X(x) + dx, f.Y(y) + dy, s, cls, anchor)


# ---------------------------------------------------------------------------------------------
# Barrier in inequality form: minimise cu.u - mu sum log(R - G u)   (u in R^2)
class Poly2:
    def __init__(self, G, R):
        self.G = np.array(G, float)
        self.R = np.array(R, float)

    def slacks(self, u):
        return self.R - self.G @ u

    def F(self, u, mu, cu):
        s = self.slacks(u)
        if np.any(s <= 0):
            return np.inf
        return cu @ u - mu * np.sum(np.log(s))

    def step(self, u, mu, cu, pure=False):
        s = self.slacks(u)
        g = cu + mu * (self.G.T @ (1 / s))
        H = mu * (self.G.T * (1 / s ** 2)) @ self.G
        d = -np.linalg.solve(H, g)
        t = 1.0
        if not pure:
            f0 = self.F(u, mu, cu)
            while not (np.all(self.slacks(u + t * d) > 0) and self.F(u + t * d, mu, cu) < f0):
                t /= 2
                if t < 1e-14:
                    break
        return u + t * d, t, -(g @ d) / mu

    def center(self, mu, cu, u0, tol=1e-13):
        u = np.array(u0, float)
        for _ in range(300):
            u, t, lam2 = self.step(u, mu, cu)
            if lam2 < tol:
                break
        return u

    def path(self, cu, u0, mus):
        out, u = [], np.array(u0, float)
        for mu in mus:
            u = self.center(mu, cu, u)
            out.append(u.copy())
        return out


# The polygon of Allaire Ex. 4.2.1: x >= 0, -3x1+2x2 <= 2, -x1+2x2 <= 4, x1+x2 <= 5 ; max x1 + 2 x2
PENT = Poly2([[-1, 0], [0, -1], [-3, 2], [-1, 2], [1, 1]], [0, 0, 2, 4, 5])
PENT_V = [(0, 0), (5, 0), (2, 3), (1, 2.5), (0, 1)]
CU = np.array([-1.0, -2.0])
MUS = list(np.logspace(3, -6, 400))


def pent_frame(f, labels=True):
    f.path(PENT_V, "a1", close=True)
    f.path(PENT_V, "ln c1 thin", close=True)


# ---------------------------------------------------------------------------------------------
def fig_kleeminty():
    c = Canvas("kleeminty", 640, 322, "Klee-Minty en dimension 2 : le simplexe visite les quatre sommets ; nombre de pivots 2^d - 1 contre itérations de points intérieurs", sub=SUB)
    f = Fig(c, (52, 44, 200, 236), (-0.6, 6.4), (-1.5, 27))
    V = [(0, 0), (5, 0), (5, 5), (0, 25)]
    f.axes(xticks=[0, 5], yticks=[0, 5, 25], xlabel="x₁", ylabel="x₂")
    f.path(V, "a1", close=True)
    f.path(V, "ln c1 thin", close=True)
    # central path of max 2x1 + x2 : constraints x>=0, x1<=5, 4x1+x2<=25
    P = Poly2([[-1, 0], [0, -1], [1, 0], [4, 1]], [0, 0, 5, 25])
    cu = np.array([-2.0, -1.0])
    pts = P.path(cu, [2.0, 5.0], list(np.logspace(3, -5, 300)))
    f.path([tuple(p) for p in pts] + [(0, 25)], "ln ck thin")
    ac = P.center(1.0, np.zeros(2), [2.0, 5.0])
    f.circle(ac[0], ac[1], 3.5, "fk")
    for (a, b), (p, q) in zip(V[:-1], V[1:]):
        c.arrow(f.X(a), f.Y(b), f.X(p), f.Y(q), 3, "ln c3")
    vals = ["0", "10", "15", "25 : optimum"]
    offs = [(-6, 16, "end"), (8, 14, "start"), (8, 4, "start"), (8, 4, "start")]
    for (a, b), v, (dx, dy, an) in zip(V, vals, offs):
        f.circle(a, b, 4, "f3")
        f.text(a, b, v, "tx-s t3", an, dx=dx, dy=dy)
    c.text(52, 16, "d = 2 : max 2x₁ + x₂ (Dantzig)", "tx-b")
    f.text(ac[0], ac[1], "trajectoire centrale", "tx-s", "start", dx=7, dy=4)
    # right panel: log2 scale
    g = Fig(c, (370, 44, 250, 236), (0.5, 10.5), (0, 10.5))
    for k in [0, 2, 4, 6, 8, 10]:
        g.line(0.5, k, 10.5, k, "gr")
        g.text(0.5, k, str(2 ** k), "tx-s", "end", dx=-5, dy=4)
    for d in range(1, 11):
        g.text(d, 0, str(d), "tx-s", "middle", dy=14)
    g.line(0.5, 0, 10.5, 0, "ax")
    g.line(0.5, 0, 0.5, 10.5, "ax")
    dz = [(d, math.log2(2 ** d - 1)) for d in range(1, 11)]
    g.path(dz, "ln c3")
    for d, y in dz:
        g.circle(d, y, 3.5, "f3")
    ipm = [3, 5, 5, 5, 6, 6, 6, 7, 7, 7]  # HiGHS highs-ipm, presolve off (verify_P04/v07b_km_ipm.py)
    ip = [(d, math.log2(v)) for d, v in zip(range(1, 11), ipm)]
    g.path(ip, "ln c4")
    for d, y in ip:
        g.circle(d, y, 3.5, "f4")
    g.text(0.8, 9.9, "simplexe, règle de Dantzig :", "tx-s t3", "start")
    FT(g, 0.8, 9.25, "2^{d} − 1 pivots", "tx-s t3", "start")
    g.text(10.4, 1.9, "points intérieurs (HiGHS) :", "tx-s t4", "end")
    g.text(10.4, 1.25, "3 à 7 itérations", "tx-s t4", "end")
    g.text(10.5, 0, "d", "tx-s", "end", dy=28)
    c.text(370, 16, "itérations (échelle logarithmique)", "tx-b")
    c.save()


def fig_barrieres():
    c = Canvas("barrieres", 620, 310, "La fonction pénalisée -mu log x + x pour mu = 1, 1/2, 1/4 et la droite x ; minimums en x = mu", sub=SUB)
    f = Fig(c, (52, 16, 460, 250), (0, 3), (-0.15, 3.2))
    f.axes(xticks=[0, 1, 2, 3], yticks=[0, 1, 2, 3], xlabel="x", ylabel="f(x)")
    f.line(0, -0.15, 0, 3.2, "ln cm thin")
    styles = {1: "ln c2", 0.5: "ln c2 dash", 0.25: "ln c2 thin"}
    for mu, cls in styles.items():
        xs = np.linspace(1e-4, 3, 900)
        pts = [(x, (-mu * math.log(x) + x) if (-mu * math.log(x) + x) <= 3.2 else float("nan")) for x in xs]
        f.path(pts, cls)
    f.line(0, 0, 3, 3, "ln cm dash")
    labels = [(1, "μ = 1"), (0.5, "μ = 1/2"), (0.25, "μ = 1/4")]
    for mu, lab in labels:
        y3 = -mu * math.log(3) + 3
        f.text(3, y3, lab, "tx-s t2", "start", dx=6, dy=4)
    f.text(3, 3, "μ = 0 : c·x = x", "tx-s", "start", dx=6, dy=4)
    for mu, lab in [(1, "1"), (0.5, "1/2"), (0.25, "1/4")]:
        y = mu - mu * math.log(mu)
        f.line(mu, -0.15, mu, y, "ln c3 thin dot")
        f.circle(mu, y, 4.5, "f3")
    FT(f, 1, 1, "x^{μ} = μ/c = 1", "tx-s t3", "start", dx=8, dy=20)
    f.text(0.5, 0.5 - 0.5 * math.log(0.5), "1/2", "tx-s t3", "middle", dy=-10)
    f.text(0.25, 0.25 - 0.25 * math.log(0.25), "1/4", "tx-s t3", "middle", dy=-10)
    c.arrow(f.X(1.6), f.Y(0.18), f.X(0.12), f.Y(0.18), 3, "ln c3 thin")
    FT(f, 1.62, 0.18, "quand μ → 0, x^{μ} → 0 (le bord)", "tx-s t3", "start", dy=4)
    f.text(0.17, 3.0, "bord x = 0 : f → +∞", "tx-s", "start")
    c.save()


def tri_xy(x, V):
    lam = (x[0] / 3, x[1] / 6, x[2] / 2)
    return (sum(l * v[0] for l, v in zip(lam, V)), sum(l * v[1] for l, v in zip(lam, V)))


def fig_triangle45():
    c = Canvas("triangle45", 620, 330, "Le triangle de l'exemple (4.5) et sa trajectoire centrale, calculée exactement pour p = 0, 1/4, 2/5", sub=SUB)
    V = [(50.0, 290.0), (220.0, 40.0), (390.0, 290.0)]  # (3,0,0), (0,6,0), (0,0,2)
    a, cc = [2, 1, 3], [1, 4, 2]
    poly = " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in V)
    c.add(f'<polygon points="{poly}" class="a1"/>')
    c.add(f'<polygon points="{poly}" class="ln c1 thin"/>')
    # level lines of the cost c.x = v on the triangle
    verts = [(3, 0, 0), (0, 6, 0), (0, 0, 2)]
    cost = [3, 24, 4]
    for v in [6, 10, 14, 18]:
        pts = []
        for i, j in [(0, 1), (1, 2), (0, 2)]:
            ci, cj = cost[i], cost[j]
            if (ci - v) * (cj - v) < 0:
                t = (v - ci) / (cj - ci)
                pts.append(tuple((1 - t) * np.array(verts[i]) + t * np.array(verts[j])))
        if len(pts) == 2:
            p, q = tri_xy(pts[0], V), tri_xy(pts[1], V)
            c.add(f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}" class="ln c2 hair dash"/>')
            lab = q if q[0] > p[0] else p
            c.text(lab[0] + 5, lab[1] + 4, f"c·x = {v}", "tx-s t2")
    # central path: p = 1/2 - e^t
    pts = []
    for t in np.linspace(6, -14, 500):
        p = 0.5 - math.exp(t)
        s = [ci - ai * p for ai, ci in zip(a, cc)]
        mu = 6 / sum(ai / si for ai, si in zip(a, s))
        x = [mu / si for si in s]
        pts.append(tri_xy(x, V))
    pts.append(V[0])
    d = "".join(("M" if i == 0 else "L") + f"{x:.1f} {y:.1f}" for i, (x, y) in enumerate(pts))
    c.add(f'<path d="{d}" class="ln ck thin"/>')
    ac = tri_xy((1, 2, 2 / 3), V)
    c.add(f'<circle cx="{ac[0]:.1f}" cy="{ac[1]:.1f}" r="4" class="ln ck thin nofill"/>')
    c.text(ac[0] - 8, ac[1] - 8, "centre analytique (1, 2, 2/3) : μ → ∞", "tx-s", "end")
    exact = [((Fr(8, 5), Fr(2, 5), Fr(4, 5)), "a"), ((Fr(9, 5), Fr(6, 25), Fr(18, 25)), "b"),
             ((Fr(216, 101), Fr(12, 101), Fr(54, 101)), "c")]
    for x, lab in exact:
        p = tri_xy([float(v) for v in x], V)
        c.add(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="4" class="fk"/>')
        c.text(p[0], p[1] - 9, lab, "tx-b", "middle")
    c.add(f'<circle cx="{V[0][0]:.1f}" cy="{V[0][1]:.1f}" r="6" class="f3"/>')
    c.text(V[0][0] - 8, V[0][1] + 22, "(3, 0, 0) : coût 3, optimum", "tx-s t3")
    c.text(V[1][0] + 10, V[1][1] - 2, "(0, 6, 0) : coût 24", "tx-s")
    c.text(V[2][0] - 40, V[2][1] + 22, "(0, 0, 2) : coût 4", "tx-s")
    lx = 432
    c.text(lx, 40, "T = {x ≥ 0 : 2x₁ + x₂ + 3x₃ = 6},", "tx-s t1")
    c.text(lx, 54, "dessiné dans son plan", "tx-s t1")
    T(c, lx, 86, "trait plein : la trajectoire centrale x^{μ}", "tx-s")
    T(c, lx, 112, "a : p = 0, μ = 8/5,", "tx-s")
    T(c, lx + 12, 126, "x^{μ} = (8/5, 2/5, 4/5)", "tx-s")
    T(c, lx, 146, "b : p = 1/4, μ = 9/10,", "tx-s")
    T(c, lx + 12, 160, "x^{μ} = (9/5, 6/25, 18/25)", "tx-s")
    T(c, lx, 180, "c : p = 2/5, μ = 216/505 ≈ 0,43,", "tx-s")
    T(c, lx + 12, 194, "x^{μ} = (216, 12, 54)/101", "tx-s")
    c.text(lx, 226, "pointillés : lignes de niveau", "tx-s t2")
    c.text(lx, 240, "du coût c·x", "tx-s t2")
    c.save()


def fig_pentagone():
    c = Canvas("pentagone", 640, 330, "Le polygone de l'exercice 4.2.1 : chemin du simplexe sur le bord, trajectoire centrale à l'intérieur", sub=SUB)
    f = Fig(c, (46, 14, 390, 280), (-0.4, 5.5), (-0.5, 3.75))
    f.axes(xticks=[0, 1, 2, 3, 4, 5], yticks=[0, 1, 2, 3], xlabel="x₁", ylabel="x₂")
    pent_frame(f)
    # level line of the optimum value x1 + 2 x2 = 8 and the direction of decrease of c
    f.line(0.4, 3.8, 5.5, 1.25, "ln c2 thin dash")
    f.text(4.45, 1.0, "x₁ + 2x₂ = 8", "tx-s t2", "start")
    c.arrow(f.X(4.3), f.Y(2.35), f.X(4.3 + 0.35), f.Y(2.35 + 0.7), 2, "ln c2 thin")
    f.text(4.75, 3.2, "−c", "tx-s t2", "start")
    # simplex path (Dantzig, exact): (0,0) -> (0,1) -> (1,5/2) -> (2,3)
    S = [(0, 0), (0, 1), (1, 2.5), (2, 3)]
    for (a, b), (p, q) in zip(S[:-1], S[1:]):
        c.arrow(f.X(a), f.Y(b), f.X(p), f.Y(q), 3, "ln c3")
    for (a, b), v, (dx, dy, an) in zip(S, ["0", "2", "6", "8"], [(-6, 14, "end"), (-6, 4, "end"), (-6, -6, "end"), (0, -10, "middle")]):
        f.circle(a, b, 4, "f3")
        f.text(a, b, v, "tx-s t3", an, dx=dx, dy=dy)
    # central path
    pts = PENT.path(CU, [3.0, 0.8], MUS)
    f.path([tuple(p) for p in pts] + [(2, 3)], "ln ck")
    ac = PENT.center(1.0, np.zeros(2), [2.0, 1.0])
    f.circle(ac[0], ac[1], 4, "ln ck thin nofill")
    f.text(ac[0], ac[1], "centre analytique", "tx-s", "start", dx=8, dy=12)
    for mu, lab, (dx, dy) in [(1, "μ = 1", (8, 4)), (0.3, "μ = 0,3", (8, 6)), (0.1, "μ = 0,1", (8, 8))]:
        u = PENT.center(mu, CU, [3.0, 1.0])
        f.circle(u[0], u[1], 3.5, "fk")
        f.text(u[0], u[1], lab, "tx-s", "start", dx=dx, dy=dy)
    u = PENT.center(10, CU, [3.0, 1.0])
    f.circle(u[0], u[1], 3.5, "fk")
    f.text(u[0], u[1], "μ = 10", "tx-s", "start", dx=8, dy=-4)
    f.circle(2, 3, 6, "f3")
    f.text(2, 3, "optimum (2, 3)", "tx-s t3", "end", dx=-10, dy=-6)
    # legend
    lx = 470
    c.add(f'<line x1="{lx}" y1="60" x2="{lx + 26}" y2="60" class="ln c3"/>')
    c.text(lx + 32, 64, "simplexe : 3 pivots", "tx-s")
    c.text(lx + 32, 78, "sur le bord", "tx-s")
    c.add(f'<line x1="{lx}" y1="104" x2="{lx + 26}" y2="104" class="ln ck"/>')
    c.text(lx + 32, 108, "trajectoire centrale", "tx-s")
    T(c, lx + 32, 122, "x^{μ}, à l'intérieur", "tx-s")
    c.text(lx, 160, "en vert : valeur de", "tx-s t3")
    c.text(lx, 174, "x₁ + 2x₂ aux sommets", "tx-s t3")
    c.text(lx, 210, "max x₁ + 2x₂, soit", "tx-s")
    c.text(lx, 224, "min c·x, c = (−1, −2)", "tx-s")
    c.save()


def fig_contre_exemples():
    c = Canvas("contre_exemples", 640, 300, "Les deux contre-exemples de l'exercice 4.2.6", sub=SUB)
    # panel 1: x1 >= 0, x2 >= 0, x1 - x2 <= 1, min x1
    f = Fig(c, (40, 40, 250, 220), (-0.4, 3.2), (-0.4, 3.6))
    f.axes(xticks=[0, 1, 2, 3], yticks=[0, 1, 2, 3], xlabel="x₁", ylabel="x₂")
    reg = [(0, 0), (1, 0), (3.2, 2.2), (3.2, 3.6), (0, 3.6)]
    f.path(reg, "a1", close=True)
    f.path([(0, 3.6), (0, 0), (1, 0), (3.2, 2.2)], "ln c1 thin")
    f.line(0, 0, 0, 3.45, "ln c3")
    c.arrow(f.X(0), f.Y(3.0), f.X(0), f.Y(3.6), 3, "ln c3")
    f.text(0, 3.45, "face optimale x₁ = 0, non bornée", "tx-s t3", "start", dx=8)
    for t in [0.6, 1.4, 2.2, 3.0]:
        f.circle(0.5, t, 3.5, "f4")
    c.arrow(f.X(0.75), f.Y(0.6), f.X(0.75), f.Y(3.1), 4, "ln c4 thin")
    FT(f, 0.85, 2.3, "f_{μ}(1/2, t) → −∞", "tx-s t4", "start")
    FT(f, 0.85, 2.3, "quand t → +∞", "tx-s t4", "start", dy=14)
    c.arrow(f.X(2.6), f.Y(0.6), f.X(2.0), f.Y(0.6), 2, "ln c2 thin")
    f.text(2.6, 0.6, "−c", "tx-s t2", "start", dx=4, dy=4)
    c.text(40, 20, "1. min x₁, x₁ − x₂ ≤ 1, x ≥ 0", "tx-b")
    # panel 2: x1 + x2 <= 1 and x1 + x2 >= 1
    g = Fig(c, (380, 40, 220, 220), (-0.3, 1.8), (-0.3, 1.8))
    g.axes(xticks=[0, 1], yticks=[0, 1], xlabel="x₁", ylabel="x₂")
    g.path([(0, 0), (1, 0), (0, 1)], "a1", close=True)
    g.path([(1, 0), (1.8, 0), (1.8, 1.8), (0, 1.8), (0, 1)], "a5", close=True)
    g.line(1.3, -0.3, -0.3, 1.3, "ln cm thin")
    g.line(1, 0, 0, 1, "ln c3")
    g.circle(1, 0, 4, "f3")
    g.circle(0, 1, 4, "f3")
    g.text(0.06, 0.12, "x₁ + x₂ ≤ 1", "tx-s t1")
    g.text(0.9, 1.55, "x₁ + x₂ ≥ 1", "tx-s t5")
    FT(g, 0.55, 0.55, "X_{ad} = le segment", "tx-s t3", "start", dx=8)
    FT(g, 0.55, 0.55, "X^{0}_{ad} = ∅ : x₃ = x₄ = 0", "tx-s t3", "start", dx=8, dy=14)
    c.text(380, 20, "2. une égalité écrite avec ≤ et ≥", "tx-b")
    c.save()


def fig_newton1d():
    c = Canvas("newton1d", 640, 290, "Newton sur f(x) = -log x + x : depuis x0 = 1/2 le modèle quadratique donne 3/4 ; depuis x0 = 3 il donne -3, hors du domaine", sub=SUB)
    fx = lambda x: -math.log(x) + x
    # left panel: x0 = 1/2
    f = Fig(c, (46, 34, 250, 210), (0, 2), (0, 3))
    f.axes(xticks=[0, 0.5, 1, 1.5, 2], yticks=[0, 1, 2, 3], xfmt=lambda v: {0: "0", 0.5: "1/2", 1: "1", 1.5: "3/2", 2: "2"}[v], xlabel="x")
    f.path([(x, fx(x) if fx(x) <= 3 else float("nan")) for x in np.linspace(0.01, 2, 400)], "ln c2")
    x0 = 0.5
    q = lambda x: fx(x0) + (1 - 1 / x0) * (x - x0) + 0.5 / x0 ** 2 * (x - x0) ** 2
    f.path([(x, q(x) if -0.1 <= q(x) <= 3 else float("nan")) for x in np.linspace(0, 2, 400)], "ln c4 dash")
    f.circle(0.5, fx(0.5), 4, "f4")
    f.circle(0.75, q(0.75), 4, "f4")
    f.line(0.75, 0, 0.75, fx(0.75), "ln c4 thin dot")
    f.circle(1, 1, 4.5, "f3")
    f.text(0.5, fx(0.5), "x₀ = 1/2", "tx-s t4", "end", dx=-6, dy=16)
    f.text(0.75, 0, "x₁ = 3/4", "tx-s t4", "middle", dy=-6)
    f.text(1, 1, "x* = μ/c = 1", "tx-s t3", "start", dx=6, dy=16)
    f.text(1.05, 2.6, "pointillés : modèle", "tx-s t4", "start")
    f.text(1.05, 2.42, "quadratique en x₀", "tx-s t4", "start")
    c.text(46, 20, "x₀ = 1/2 : erreurs 1/2, 1/4, 1/16, 1/256", "tx-b")
    # right panel: x0 = 3
    g = Fig(c, (370, 34, 250, 210), (-4, 4), (-0.5, 4.5))
    g.axes(xticks=[-3, 0, 1, 3], yticks=[0, 2, 4], xlabel="x")
    g.path([(x, fx(x) if fx(x) <= 4.5 else float("nan")) for x in np.linspace(0.01, 4, 400)], "ln c2")
    x0 = 3.0
    q2 = lambda x: fx(x0) + (1 - 1 / x0) * (x - x0) + 0.5 / x0 ** 2 * (x - x0) ** 2
    g.path([(x, q2(x) if q2(x) <= 4.5 else float("nan")) for x in np.linspace(-4, 4, 400)], "ln c4 dash")
    g.path([(-4, -0.5), (0, -0.5), (0, 4.5), (-4, 4.5)], "am", close=True)
    g.circle(3, fx(3), 4, "f4")
    g.circle(-3, q2(-3), 4.5, "f6")
    g.line(-3, -0.5, -3, q2(-3), "ln c6 thin dot")
    g.text(3, fx(3), "x₀ = 3", "tx-s t4", "start", dx=6, dy=16)
    g.text(-3, q2(-3), "x₁ = −3", "tx-s t6", "middle", dy=-10)
    g.text(-2, 3.6, "hors du", "tx-s", "middle")
    g.text(-2, 3.25, "domaine x > 0", "tx-s", "middle")
    c.text(370, 20, "x₀ = 3 ≥ 2μ/c : le pas pur sort", "tx-b")
    c.save()


def run_path_following(sigma, k, mu0=1.0, tol=1e-6):
    """mu <- sigma mu, then k damped Newton steps; returns the list of (mu, iterates after each Newton step)."""
    u = PENT.center(mu0, CU, [3.0, 1.5])
    mu = mu0
    hist = [(mu, [u.copy()])]
    while 5 * mu > tol:
        mu *= sigma
        its = []
        for _ in range(k):
            u, t, lam2 = PENT.step(u, mu, CU)
            its.append(u.copy())
        hist.append((mu, its))
    return hist


def fig_suivi():
    c = Canvas("suivi", 640, 330, "Suivi de chemin sur le polygone : mu divisé par 1/0,3 à chaque étape, deux pas de Newton amortis par valeur de mu", sub=SUB)
    f = Fig(c, (50, 16, 380, 280), (1.55, 3.35), (1.15, 3.2))
    f.axes(xticks=[2, 2.5, 3], yticks=[1.5, 2, 2.5, 3], xfmt=lambda v: f"{v:g}".replace(".", ","), yfmt=lambda v: f"{v:g}".replace(".", ","), xlabel="x₁", ylabel="x₂")
    # the two edges through the optimum
    f.path([(1.55, (4 + 1.55) / 2), (2, 3), (3.35, 5 - 3.35)], "ln c1 thin")
    f.path([(1.55, (4 + 1.55) / 2), (2, 3), (3.35, 5 - 3.35), (3.35, 1.15), (1.55, 1.15)], "a1", close=True)
    f.text(1.57, 3.1, "−x₁ + 2x₂ = 4", "tx-s t1", "start")
    f.text(3.05, 1.95, "x₁ + x₂ = 5", "tx-s t1", "start", dx=4)
    pts = PENT.path(CU, [3.0, 1.5], list(np.logspace(0.2, -6, 300)))
    f.path([tuple(p) for p in pts] + [(2, 3)], "ln ck thin")
    hist = run_path_following(0.3, 2)
    prev = hist[0][1][-1]
    f.circle(prev[0], prev[1], 4.5, "f4")
    FT(f, prev[0], prev[1], "départ x^{μ₀}, μ₀ = 1", "tx-s", "start", dx=8, dy=4)
    for j, (mu, its) in enumerate(hist[1:], start=1):
        center = PENT.center(mu, CU, its[-1])
        if j <= 4:
            f.circle(center[0], center[1], 3, "ln ck thin nofill")
        for u in its:
            if np.hypot(*(u - prev)) * 150 > 7:
                c.arrow(f.X(prev[0]), f.Y(prev[1]), f.X(u[0]), f.Y(u[1]), 4, "ln c4 thin")
            prev = u
        f.circle(its[-1][0], its[-1][1], 3, "f4")
        if j <= 2:
            lab = {1: "cible x^{μ₁}, μ₁ = 0,3", 2: "cible x^{μ₂}, μ₂ = 0,09"}[j]
            FT(f, center[0], center[1], lab, "tx-s", "end", dx=-8, dy=4 if j == 1 else 26)
    f.circle(2, 3, 5, "f3")
    f.text(2, 3, "optimum", "tx-s t3", "start", dx=8, dy=-8)
    lx = 460
    c.add(f'<line x1="{lx}" y1="70" x2="{lx + 26}" y2="70" class="ln ck thin"/>')
    c.text(lx + 32, 74, "trajectoire centrale", "tx-s")
    c.add(f'<circle cx="{lx + 13}" cy="96" r="3" class="ln ck thin nofill"/>')
    T(c, lx + 32, 100, "cibles x^{μₖ}", "tx-s")
    c.add(f'<circle cx="{lx + 13}" cy="122" r="3" class="f4"/>')
    c.text(lx + 32, 126, "itérés (2 pas de", "tx-s t4")
    c.text(lx + 32, 140, "Newton par μ)", "tx-s t4")
    c.text(lx, 180, "μₖ₊₁ = 0,3 μₖ", "tx-b")
    c.text(lx, 200, "l'itéré reste près de", "tx-s")
    c.text(lx, 214, "sa cible : le départ", "tx-s")
    c.text(lx, 228, "suivant est bon", "tx-s")
    c.save()
    return hist


def fig_ecart(hist):
    c = Canvas("ecart", 620, 300, "Ecart de dualité n mu et vraie erreur c.x - min le long du suivi de chemin, en échelle logarithmique", sub=SUB)
    K = len(hist) - 1
    f = Fig(c, (60, 16, 440, 240), (0, K), (-7.5, 1.2))
    for e in range(-7, 2):
        f.line(0, e, K, e, "gr")
        f.text(0, e, f"10{sup(e)}", "tx-s", "end", dx=-5, dy=4)
    for k in range(0, K + 1):
        f.text(k, -7.5, str(k), "tx-s", "middle", dy=14)
    f.line(0, -7.5, K, -7.5, "ax")
    f.line(0, -7.5, 0, 1.2, "ax")
    f.text(K, -7.5, "k (valeurs de μ)", "tx-s", "end", dy=28)
    gap = [(k, math.log10(5 * mu)) for k, (mu, its) in enumerate(hist)]
    err = [(k, math.log10(CU @ its[-1] + 8)) for k, (mu, its) in enumerate(hist)]
    f.path(gap, "ln ck")
    for p in gap:
        f.circle(p[0], p[1], 3.5, "fk")
    f.path(err, "ln c4")
    for p in err:
        f.circle(p[0], p[1], 3.5, "f4")
    f.text(gap[2][0], gap[2][1], "nμₖ = 5 × 0,3ᵏ", "tx-s", "start", dx=8, dy=-8)
    f.text(err[4][0], err[4][1], "vraie erreur c·xₖ − min", "tx-s t4", "end", dx=-8, dy=14)
    c.text(515, 80, "pente : log₁₀ 0,3", "tx-s")
    c.text(515, 94, "par étape", "tx-s")
    c.text(515, 130, "l'erreur reste", "tx-s t4")
    c.text(515, 144, "sous nμ", "tx-s t4")
    c.save()


def sup(e):
    m = {"-": "⁻", "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹"}
    return "".join(m[ch] for ch in str(e))


if __name__ == "__main__":
    fig_kleeminty()
    fig_barrieres()
    fig_triangle45()
    fig_pentagone()
    fig_contre_exemples()
    fig_newton1d()
    h = fig_suivi()
    fig_ecart(h)
    for k, (mu, its) in enumerate(h):
        u = its[-1]
        print(f"  k={k} mu={mu:.3e} x=({u[0]:.5f}; {u[1]:.5f}) err={CU @ u + 8:.3e} 5mu={5 * mu:.3e}")
