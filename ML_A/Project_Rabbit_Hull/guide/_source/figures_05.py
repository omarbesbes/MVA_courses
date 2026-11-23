"""figures_05.py — static figures of page 5 (MRH). Run: python3 figures_05.py"""
import math
import numpy as np
from figures_common import Canvas, Fig

def hull(P):
    P = sorted(map(tuple, P))
    def cr(o, a, b): return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lo, up = [], []
    for p in P:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 1e-12: lo.pop()
        lo.append(p)
    for p in reversed(P):
        while len(up) >= 2 and cr(up[-2], up[-1], p) <= 1e-12: up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]

def poly(f, pts, cls, extra=""):
    f.path(list(pts), cls, close=True, extra=extra)

# ---------------------------------------------------------------- 1. linear (sparse) code versus block-convex code
def fig_codes():
    c = Canvas("codes", 760, 335, "Left: a sparse linear code with two active directions gives a cone or a box. Right: a block-convex code gives a Minkowski sum of a triangle and a segment.", sub="05")
    # left panel
    L = Fig(c, (40, 40, 300, 240), (-0.5, 3.5), (-0.5, 3.0))
    c.text(40, 24, "Sparse linear code  x = z₁d₁ + z₂d₂,  0 ≤ zⱼ ≤ M", "tx-b")
    L.axes(xticks=(), yticks=(), grid=False)
    d1, d2, M = np.array([1.0, 0.25]), np.array([0.3, 1.0]), 2.2
    box = [(0, 0), tuple(M*d1), tuple(M*d1+M*d2), tuple(M*d2)]
    poly(L, box, "a2"); poly(L, box, "ln c2")
    L.line(0, 0, 3.4*d1[0], 3.4*d1[1], "ln c2 thin dash"); L.line(0, 0, 3.4*d2[0], 3.4*d2[1], "ln c2 thin dash")
    for d, nm in ((d1, "d₁"), (d2, "d₂")):
        c.arrow(L.X(0), L.Y(0), L.X(d[0]), L.Y(d[1]), 2, "ln c2")
        L.text(d[0], d[1], nm, "tx-b", dx=6, dy=-6)
    L.circle(0, 0, 4, "fk")
    c.text(40, 304, "a box of codes: each feature varies on its own;", "tx-s")
    c.text(40, 320, "tiles = segments [0, M dⱼ] anchored at the origin", "tx-s")
    # right panel
    R = Fig(c, (410, 40, 300, 240), (-0.5, 5.5), (-0.5, 4.5))
    c.text(410, 24, "Block-convex code  x = p₁ + p₂,  p₁ ∈ P₁,  p₂ ∈ P₂", "tx-b")
    T = np.array([[0, 0], [3.0, 0], [0.5, 1.5]]); S = np.array([[0, 0.0], [1.0, 1.5]])
    Sm = hull([tuple(a+b) for a in T for b in S])
    poly(R, Sm, "am"); poly(R, Sm, "ln cm thin")
    poly(R, T, "a1"); poly(R, T, "ln c1")
    R.line(S[0][0], S[0][1], S[1][0], S[1][1], "ln c5")
    for p in T: R.circle(p[0], p[1], 4.5, "f1")
    for p in S: R.circle(p[0], p[1], 4.5, "f5")
    R.text(1.5, 0.0, "P₁ (a triangle)", "tx-b", "middle", dy=18)
    R.text(S[1][0], S[1][1], "P₂ (a segment)", "tx-b", "end", dx=-8, dy=4)
    R.text(4.0, 2.4, "P₁ ⊕ P₂", "tx-b", "middle")
    c.text(410, 304, "each tile: a convex combination of its archetypes,", "tx-s"); c.text(410, 320, "weights in a simplex (non-negative, sum 1)", "tx-s")
    c.save()

# ---------------------------------------------------------------- 2. layout of a block-convex code
def fig_layout():
    c = Canvas("layout", 760, 300, "Layout of a block-convex code vector: m blocks, a few active, each active block sums to one.", sub="05")
    c.text(20, 24, "A code vector z = (z₁ | z₂ | … | z_m), one block per tile; x = Σ over the active tiles of zᵢ Aₜᵢ", "tx-b")
    sizes = [4, 3, 5, 3, 4, 3]; active = {1: [0.0, 0.7, 0.3], 3: [0.2, 0.0, 0.8]}
    active = {1: [0.0, 0.7, 0.3], 4: [0.5, 0.0, 0.25, 0.25]}
    x0, y0, w, h = 20, 50, 28, 34; gap = 14; x = x0
    labels = []
    for i, n in enumerate(sizes):
        act = i in active
        x_start = x
        for j in range(n):
            val = active[i][j] if act and j < len(active[i]) else 0.0
            cls = "a1 ln c1 thin" if act else "am ln cm thin"
            if act and j >= len(active[i]): val = 0.0
            c.add(f'<rect x="{x:.1f}" y="{y0}" width="{w}" height="{h}" class="{cls}" rx="3"/>')
            c.text(x + w/2, y0 + h/2 + 4, f"{val:g}" if act else "0", "tx-b" if (act and val > 0) else "tx-s", "middle")
            x += w
        c.text((x_start + x)/2, y0 + h + 18, f"tile T{i+1}" + (" — active" if act else ""), "tx-b" if act else "tx-s", "middle")
        if act:
            c.text((x_start + x)/2, y0 + h + 34, "Σ = 1, zᵢ ≥ 0", "tx-s", "middle")
            c.add(f'<path d="M{x_start:.1f} {y0-8} L{x_start:.1f} {y0-14} L{x-0:.1f} {y0-14} L{x:.1f} {y0-8}" class="ln c1 thin"/>')
        x += gap
    W = x
    # polytopes below
    c.text(20, 170, "Each active block selects a point of its polytope; the activation is the sum of these points.", "tx")
    f1 = Fig(c, (90, 190, 120, 90), (0, 3), (0, 2.2)); f2 = Fig(c, (330, 190, 120, 90), (0, 3), (0, 2.2)); f3 = Fig(c, (570, 190, 120, 90), (0, 4), (0, 2.5))
    P1 = [(0.2, 0.2), (2.6, 0.4), (1.2, 2.0)]; P2 = [(0.2, 0.3), (2.7, 0.3), (2.6, 1.9), (0.4, 1.8)]
    z1 = np.array([0.0, 0.7, 0.3]); z2 = np.array([0.5, 0.0, 0.25, 0.25])
    p1 = z1 @ np.array(P1)[[0, 1, 2]] if False else (0.7*np.array(P1[1]) + 0.3*np.array(P1[2]))
    p2 = 0.5*np.array(P2[0]) + 0.25*np.array(P2[2]) + 0.25*np.array(P2[3])
    poly(f1, P1, "a1"); poly(f1, P1, "ln c1"); f1.circle(*p1, 5, "f3"); f1.text(1.4, 0.0, "P₂ (tile T2)", "tx-s", "middle", dy=16)
    poly(f2, P2, "a1"); poly(f2, P2, "ln c1"); f2.circle(*p2, 5, "f3"); f2.text(1.5, 0.0, "P₅ (tile T5)", "tx-s", "middle", dy=16)
    sm = hull([(a[0]+b[0], a[1]+b[1]) for a in P1 for b in P2])
    # sum shown centred in its own frame (shifted by -(0.2+0.2) just for display)
    poly(f3, [(a-0.2, b-0.2) for a, b in sm], "am"); poly(f3, [(a-0.2, b-0.2) for a, b in sm], "ln cm thin")
    f3.circle(p1[0]+p2[0]-0.2, p1[1]+p2[1]-0.2, 6, "f3"); f3.text(2.0, 0.0, "P₂ ⊕ P₅ ∋ x = p₂ + p₅", "tx-s", "middle", dy=16)
    c.text(238, 240, "+", "tx-b"); c.text(478, 240, "=", "tx-b")
    c.save()

# ---------------------------------------------------------------- 3. support function of a polygon
def fig_support():
    c = Canvas("support", 760, 330, "Support function of a pentagon: h(u) is the largest inner product with u, read off a supporting line; its graph over the unit circle.", sub="05")
    P = np.array([(0.5, 0.3), (3.0, 0.0), (3.8, 1.5), (2.4, 2.6), (0.9, 2.0)])
    F = Fig(c, (30, 40, 330, 250), (-0.5, 4.5), (-0.5, 3.5))
    c.text(30, 24, "h(u) = max over x ∈ P of ⟨u, x⟩", "tx-b")
    F.axes(grid=False)
    poly(F, P, "a1"); poly(F, P, "ln c1")
    th = math.radians(35); u = np.array([math.cos(th), math.sin(th)])
    vals = P @ u; k = int(vals.argmax()); hv = vals[k]
    # supporting line: points y with <u,y> = hv
    t = np.array([-u[1], u[0]]); a = u*hv - 2.2*t; b = u*hv + 2.2*t
    F.line(a[0], a[1], b[0], b[1], "ln c2 dash")
    F.line(0, 0, u[0]*hv, u[1]*hv, "ln c2")
    c.arrow(F.X(0), F.Y(0), F.X(u[0]*1.2), F.Y(u[1]*1.2), 2, "ln c2")
    F.text(u[0]*1.2, u[1]*1.2, "u (unit)", "tx-b", dx=6, dy=14)
    F.circle(*P[k], 6, "f3"); F.text(P[k][0], P[k][1], "maximiser", "tx-s", "end", dx=-10, dy=24)
    F.text(u[0]*hv*0.72, u[1]*hv*0.72, "h(u)", "tx-b", dx=-8, dy=-9, anchor="end") if False else F.text(u[0]*hv*0.72, u[1]*hv*0.72, "h(u)", "tx-b", "end", dx=-8, dy=-9)
    F.text(-0.3, -0.3, "0", "tx-s")
    # right: h as a function of the angle
    G = Fig(c, (410, 40, 320, 250), (0, 360), (0, 5.0))
    c.text(410, 24, "h on the unit circle: u = (cos θ, sin θ)", "tx-b")
    G.axes(xticks=(0, 90, 180, 270, 360), yticks=(0, 1, 2, 3, 4), xfmt=lambda v: f"{v}°", xlabel="θ", grid=True)
    f = lambda a: max(float(p @ np.array([math.cos(math.radians(a)), math.sin(math.radians(a))])) for p in P)
    G.fn(f, "ln c1")
    G.circle(35, f(35), 5, "f3"); G.text(35, f(35), "θ = 35°", "tx-s", dx=8, dy=-8)
    G.text(180, 4.8, "each smooth arc belongs to one vertex of P,", "tx-s", "middle")
    G.text(180, 4.5, "each kink is the normal of an edge", "tx-s", "middle")
    c.save()

fig_codes(); fig_layout(); fig_support()
