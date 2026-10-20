"""figures_L06.py — static SVG figures of Lesson 6 (dynamic OT, flow matching, diffusion), written to figures/L06/.

Run: python3 figures_L06.py        (then node build.mjs Lesson06.html)
Every coordinate is computed here (closed forms, ODE integrations, a small Benamou–Brenier solver, exact LPs).
Colour code: source / noise alpha_0 = 2 (orange-red), target / data alpha_1 = 1 (blue), flows, interpolations and
barycenters = 3 (green), a third measure = 5 (purple).
"""
import math

import numpy as np
from scipy import optimize, sparse, stats
from scipy.sparse.linalg import splu

from figures_common import Canvas, Fig, esc, fmt1

SUB = "L06"
NORM = stats.norm


def gauss(x, m, s):
    return np.exp(-0.5 * ((x - m) / s) ** 2) / (s * math.sqrt(2 * math.pi))


def arrow_data(c, f, x1, y1, x2, y2, k, cls=None):
    """an arrow between two points given in the data coordinates of panel f"""
    c.arrow(f.X(x1), f.Y(y1), f.X(x2), f.Y(y2), k, cls)


# ---------------------------------------------------------------------------------------------
def fig_lagrange_euler():
    """Lagrangian (trajectories) and Eulerian (densities + velocity at fixed places) views of N(0,1) -> N(4,4)."""
    c = Canvas("lagrange_euler", 660, 300, "Lagrangian and Eulerian descriptions of the same motion from N(0,1) to N(4,4)", sub=SUB)
    # left: particle trajectories in the (x, t) plane
    f = Fig(c, (40, 34, 270, 222), (-3.5, 9.5), (0, 1))
    for t in [0, 0.5, 1]:
        f.line(-3.5, t, 9.5, t, "gr")
    f.line(-3.5, 0, 9.5, 0, "ax")
    for xv in [-2, 0, 2, 4, 6, 8]:
        f.text(xv, 0, str(xv), "tx-s", "middle", dy=14)
    for t in [0, 0.5, 1]:
        f.text(-3.5, t, f"t = {fmt1(t)}", "tx-s", "end", dx=-4, dy=4)
    zs = NORM.ppf((np.arange(9) + 0.5) / 9)
    for z in zs:
        f.line(z, 0, 4 + 2 * z, 1, "ln c3 thin")
        f.circle(z, 0, 3.2, "f2")
        f.circle(4 + 2 * z, 1, 3.2, "f1")
        f.circle(2 + 1.5 * z, 0.5, 2.6, "f3")
    c.text(175, 22, "Lagrangian: follow each particle", "tx-b", "middle")
    c.text(175, 286, "x(t) = 4t + (1 + t) x(0): one line per particle", "tx-s", "middle")
    # right: densities at fixed times, and the velocity field at fixed positions
    rows = [(0.0, 214), (0.5, 140), (1.0, 66)]
    for t, y0 in rows:
        g = Fig(c, (375, y0 - 52, 270, 52), (-3.5, 9.5), (0, 0.42))
        m, s = 4 * t, 1 + t
        xs = np.linspace(-3.5, 9.5, 400)
        cls = "a2" if t == 0 else ("a1" if t == 1 else "a3")
        lcl = "ln c2 thin" if t == 0 else ("ln c1 thin" if t == 1 else "ln c3 thin")
        g.path([(-3.5, 0)] + [(x, gauss(x, m, s)) for x in xs] + [(9.5, 0)], cls, close=True)
        g.path([(x, gauss(x, m, s)) for x in xs], lcl)
        g.line(-3.5, 0, 9.5, 0, "ax")
        c.text(368, y0 - 14, f"t = {fmt1(t)}", "tx-s", "end")
        for xv in [-2, 0, 2, 4, 6, 8]:
            v = 4 + (xv - 4 * t) / (1 + t)
            L = 0.16 * v
            c.arrow(g.X(xv), y0 + 9, g.X(xv + L), y0 + 9, 3, "ln c3 thin")
    for xv in [-2, 0, 2, 4, 6, 8]:
        c.text(Fig(c, (375, 0, 270, 1), (-3.5, 9.5), (0, 1)).X(xv), 244, str(xv), "tx-s", "middle")
    c.text(510, 22, "Eulerian: density and velocity at fixed places", "tx-b", "middle")
    c.text(510, 286, "green arrows: v(t, x) = 4 + (x − 4t)/(1 + t) at x = −2, 0, …, 8", "tx-s", "middle")
    c.save()


def fig_rotation():
    """Two velocity fields that leave the standard Gaussian unchanged (cf. StatOT Fig. 5.1)."""
    c = Canvas("rotation", 600, 290, "The zero field and the rotation field both leave the standard Gaussian unchanged", sub=SUB)
    for col, (title, rot) in enumerate([("v = 0", False), ("v(x) = Jx  (rotation)", True)]):
        f = Fig(c, (40 + col * 300, 34, 220, 220), (-2.6, 2.6), (-2.6, 2.6))
        for r, op in [(0.6, 0.3), (1.2, 0.22), (1.8, 0.15), (2.4, 0.1)]:
            th = np.linspace(0, 2 * np.pi, 120)
            f.path([(r * math.cos(a), r * math.sin(a)) for a in th], "ln c2 thin", extra=f' stroke-opacity="{0.25 + op:.2f}"')
        for gx in np.arange(-2, 2.01, 1.0):
            for gy in np.arange(-2, 2.01, 1.0):
                if not rot or (gx == 0 and gy == 0):
                    f.circle(gx, gy, 2.2, "fm")
                else:
                    vx, vy = -gy * 0.32, gx * 0.32
                    arrow_data(c, f, gx, gy, gx + vx, gy + vy, 3, "ln c3 thin")
        c.text(150 + col * 300, 22, title, "tx-b", "middle")
    c.text(150, 276, "kinetic energy 0", "tx-s", "middle")
    c.text(450, 276, "kinetic energy E‖Jx‖² = 2 (per unit of angular speed²)", "tx-s", "middle")
    c.save()


def fig_gauss_plane():
    """Paths between N(0,1) and N(4,4) drawn in the (mean, standard deviation) plane, where W2 is Euclidean."""
    c = Canvas("gauss_plane", 660, 290, "Three paths between N(0,1) and N(4,4) in the plane of means and standard deviations", sub=SUB)
    f = Fig(c, (52, 26, 330, 220), (-0.4, 4.6), (0.6, 2.75))
    f.axes(xticks=[0, 1, 2, 3, 4], yticks=[1, 1.5, 2, 2.5], yfmt=fmt1, xlabel="mean m", ylabel="st. dev. σ")
    ts = np.linspace(0, 1, 100)
    # translate then dilate
    f.path([(0, 1), (4, 1), (4, 2)], "ln cm dash")
    # bent path
    f.path([(4 * t, 1 + t + 2 * t * (1 - t)) for t in ts], "ln c5")
    # geodesic
    f.line(0, 1, 4, 2, "ln c3")
    f.circle(0, 1, 5, "f2")
    f.circle(4, 2, 5, "f1")
    f.text(0, 1, "α₀ = N(0, 1)", "tx-s t2", "start", dx=6, dy=16)
    f.text(4, 2, "α₁ = N(4, 2²)", "tx-s t1", "start", dx=8, dy=4)
    f.text(0.75, 1.1875, "geodesic: action 17 = W₂²", "tx-s t3", "start", dy=-8)
    f.text(2.1, 1.0, "translate, then dilate: action 34", "tx-s", "middle", dy=-6)
    f.text(1.6, 1 + 0.4 + 2 * 0.4 * 0.6, "bent: action 18.33", "tx-s t5", "end", dx=-6, dy=-4)
    for t in [0.5]:
        f.circle(4 * t, 1 + t, 4, "f3")
        f.circle(4 * t, 1 + t + 2 * t * (1 - t), 4, "f5")
        f.circle(4, 1, 4, "fm")
    # right: densities at t = 1/2
    g = Fig(c, (430, 50, 210, 170), (-3, 8), (0, 0.42))
    g.line(-3, 0, 8, 0, "ax")
    for xv in [-2, 0, 2, 4, 6, 8]:
        g.text(xv, 0, str(xv), "tx-s", "middle", dy=14)
    xs = np.linspace(-3, 8, 400)
    for (m, s, cls) in [(2, 1.5, "ln c3"), (2, 2.0, "ln c5"), (4, 1.0, "ln cm dash")]:
        g.path([(x, gauss(x, m, s)) for x in xs], cls)
    c.text(535, 36, "the three densities at t = ½", "tx-b", "middle")
    g.text(4, gauss(4, 4, 1), "N(4, 1)", "tx-s", "start", dx=6, dy=-2)
    g.text(2, gauss(2, 2, 1.5), "N(2, 1.5²)", "tx-s t3", "end", dx=-14, dy=-2)
    g.text(-1.6, gauss(-1.6, 2, 2.0), "N(2, 2²)", "tx-s t5", "end", dx=-2, dy=-4)
    c.save()


def fig_perspective():
    """Level sets of the perspective function J(a, m) = m²/a and a convexity check."""
    c = Canvas("perspective", 640, 290, "Level sets of J(a, m) = m^2/a in the half-plane a >= 0", sub=SUB)
    f = Fig(c, (60, 24, 300, 236), (-2.6, 2.6), (-0.5, 3.3))
    f.path([(-2.6, -0.5), (2.6, -0.5), (2.6, 0), (-2.6, 0)], "am", close=True)
    f.axes(xticks=[-2, -1, 0, 1, 2], yticks=[0, 1, 2, 3], grid=False, xlabel="momentum m", ylabel="density a")
    for cval, op in [(0.5, 0.9), (1, 0.75), (2, 0.6), (4, 0.45)]:
        ms = np.linspace(-2.6, 2.6, 300)
        pts = [(m, m * m / cval) if m * m / cval <= 3.3 else None for m in ms]
        f.path(pts, "ln c3 thin", extra=f' stroke-opacity="{op}"')
    for idx, cval in enumerate([0.5, 1, 2, 4]):
        aa = 3.05 - 0.55 * idx
        f.text(-math.sqrt(aa * cval), aa, f"J = {fmt1(cval)}", "tx-s t3", "end", dx=-5, dy=4)
    f.text(-2.5, -0.27, "a < 0: J = +∞", "tx-s", "start")
    # points of the convexity example
    P, Q, Mid = (2, 1), (0, 3), (1, 2)
    f.line(P[0], P[1], Q[0], Q[1], "ln ck thin dash")
    f.circle(*P, 4.5, "f2")
    f.circle(*Q, 4.5, "f1")
    f.circle(*Mid, 4.5, "f3")
    f.text(*P, "J(1, 2) = 4", "tx-s", "start", dx=8, dy=4)
    f.text(*Q, "J(3, 0) = 0", "tx-s", "start", dx=8, dy=4)
    x0 = 515
    c.text(x0, 50, "points (a, m) = (density, momentum)", "tx-s", "middle")
    c.text(x0, 84, "J is convex:", "tx-b", "middle")
    c.text(x0, 102, "green midpoint (2, 1): J = ½ ≤ ½(4 + 0) = 2", "tx-s", "middle")
    c.text(x0, 140, "J is 1-homogeneous:", "tx-b", "middle")
    c.text(x0, 158, "J(ηa, ηm) = η J(a, m), η ≥ 0", "tx-s", "middle")
    c.text(x0, 196, "no momentum without mass:", "tx-b", "middle")
    c.text(x0, 214, "J(0, m) = +∞ if m ≠ 0;  J(0, 0) = 0", "tx-s", "middle")
    c.save()


def fig_staggered():
    """The staggered space-time grid of the discretized Benamou–Brenier problem."""
    c = Canvas("staggered", 600, 300, "Staggered grid: densities at cell centres and integer times, momenta at faces and mid-times", sub=SUB)
    Nx, T = 4, 3
    x0, y0, cw, ch = 96, 250, 76, 70  # pixel geometry: cell width, time-step height
    X = lambda x: x0 + x * cw          # x in cell units (faces at integers)
    Y = lambda t: y0 - t * ch          # t in time-step units
    for k in range(T + 1):
        c.add(f'<line x1="{X(0):.1f}" y1="{Y(k):.1f}" x2="{X(Nx):.1f}" y2="{Y(k):.1f}" class="gr"/>')
    for j in range(Nx + 1):
        c.add(f'<line x1="{X(j):.1f}" y1="{Y(0):.1f}" x2="{X(j):.1f}" y2="{Y(T):.1f}" class="gr"/>')
    for k in range(T + 1):
        for i in range(Nx):
            cls = "f2" if k == 0 else ("f1" if k == T else "fk")
            c.add(f'<circle cx="{X(i + 0.5):.1f}" cy="{Y(k):.1f}" r="5" class="{cls}"/>')
    for k in range(T):
        for j in range(Nx + 1):
            xc, yc = X(j), Y(k + 0.5)
            if j in (0, Nx):
                c.text(xc, yc + 4, "0", "tx-s", "middle")
            else:
                c.arrow(xc - 13, yc, xc + 13, yc, 3, "ln c3 thin")
        for i in range(Nx):
            xc, yc = X(i + 0.5), Y(k + 0.5)
            c.add(f'<line x1="{xc - 4:.1f}" y1="{yc - 4:.1f}" x2="{xc + 4:.1f}" y2="{yc + 4:.1f}" class="ln c5 thin"/>')
            c.add(f'<line x1="{xc - 4:.1f}" y1="{yc + 4:.1f}" x2="{xc + 4:.1f}" y2="{yc - 4:.1f}" class="ln c5 thin"/>')
    c.text(X(0) - 14, Y(0) + 4, "t = 0", "tx-s", "end")
    c.text(X(0) - 14, Y(T) + 4, "t = 1", "tx-s", "end")
    c.text(X(0) - 14, Y(1) + 4, "time ↑", "tx-s", "end")
    c.text(X(Nx / 2), Y(0) + 24, "space →  (cells i = 0, …, N − 1; faces j = 0, …, N)", "tx-s", "middle")
    lx = X(Nx) + 30
    c.add(f'<circle cx="{lx:.1f}" cy="62" r="5" class="fk"/>')
    c.text(lx + 12, 66, "ρ(k, i): centres, times k/T", "tx-s", "start")
    c.add(f'<circle cx="{lx:.1f}" cy="86" r="5" class="f2"/>')
    c.text(lx + 12, 90, "fixed: ρ(0, ·) = a₀", "tx-s t2", "start")
    c.add(f'<circle cx="{lx:.1f}" cy="110" r="5" class="f1"/>')
    c.text(lx + 12, 114, "fixed: ρ(T, ·) = a₁", "tx-s t1", "start")
    c.arrow(lx - 10, 140, lx + 8, 140, 3, "ln c3 thin")
    c.text(lx + 12, 144, "m(k, j): faces, mid-times", "tx-s", "start")
    c.text(lx, 168, "0", "tx-s", "middle")
    c.text(lx + 12, 168, "no flux through the walls", "tx-s", "start")
    c.add(f'<line x1="{lx - 4:.1f}" y1="188" x2="{lx + 4:.1f}" y2="196" class="ln c5 thin"/>')
    c.add(f'<line x1="{lx - 4:.1f}" y1="196" x2="{lx + 4:.1f}" y2="188" class="ln c5 thin"/>')
    c.text(lx + 12, 196, "averages (ρ̄, m̄) where J is", "tx-s", "start")
    c.text(lx + 12, 210, "evaluated: centres, mid-times", "tx-s", "start")
    c.save()


# ---------------------------------------------------------------------------------------------
class BB1D:
    """Benamou–Brenier on a 1D staggered grid, solved by Douglas–Rachford (Papadakis, Peyré, Oudet 2014)."""

    def __init__(self, a0, a1, L, R, T):
        N = len(a0)
        self.N, self.T, self.dx, self.dt = N, T, (R - L) / N, 1.0 / T
        self.nr, self.nm = (T + 1) * N, T * (N + 1)
        rows, cols, vals, b, r = [], [], [], [], 0
        ir = lambda k, i: k * N + i
        im = lambda k, j: self.nr + k * (N + 1) + j
        for i in range(N):
            rows += [r]; cols += [ir(0, i)]; vals += [1.0]; b.append(a0[i]); r += 1
            rows += [r]; cols += [ir(T, i)]; vals += [1.0]; b.append(a1[i]); r += 1
        for k in range(T):
            rows += [r]; cols += [im(k, 0)]; vals += [1.0]; b.append(0.0); r += 1
            rows += [r]; cols += [im(k, N)]; vals += [1.0]; b.append(0.0); r += 1
        for k in range(T):
            for i in range(N):
                rows += [r] * 4
                cols += [ir(k + 1, i), ir(k, i), im(k, i + 1), im(k, i)]
                vals += [1 / self.dt, -1 / self.dt, 1 / self.dx, -1 / self.dx]
                b.append(0.0); r += 1
        A = sparse.csr_matrix((vals, (rows, cols)), shape=(r, self.nr + self.nm))[: r - 1]  # one redundant row
        self.A, self.b = A, np.array(b[: r - 1])
        self.lu = splu(sparse.csc_matrix(A @ A.T))
        It = np.zeros((T, T + 1)); It[range(T), range(T)] = 0.5; It[range(T), np.arange(T) + 1] = 0.5
        Ix = np.zeros((N, N + 1)); Ix[range(N), range(N)] = 0.5; Ix[range(N), np.arange(N) + 1] = 0.5
        self.It, self.Ix = It, Ix
        self.Kt = np.linalg.inv(np.eye(T + 1) + It.T @ It)
        self.Kx = np.linalg.inv(np.eye(N + 1) + Ix.T @ Ix)
        self.a0, self.a1 = a0, a1

    def split(self, U):
        return U[: self.nr].reshape(self.T + 1, self.N), U[self.nr:].reshape(self.T, self.N + 1)

    def interp(self, U):
        rho, m = self.split(U)
        return self.It @ rho, m @ self.Ix.T

    def proj_C(self, U):
        return U - self.A.T @ self.lu.solve(self.A @ U - self.b)

    def proj_D(self, U, rb, mb):
        rho, m = self.split(U)
        U2 = np.concatenate([(self.Kt @ (rho + self.It.T @ rb)).ravel(), ((m + mb @ self.Ix) @ self.Kx.T).ravel()])
        rb2, mb2 = self.interp(U2)
        return U2, rb2, mb2

    @staticmethod
    def prox_J(a, m, tau):
        A = np.maximum(a, 0.0) + 1.0
        for _ in range(60):
            f = (A - a) * (A + 2 * tau) ** 2 - tau * m * m
            A = A - f / ((A + 2 * tau) ** 2 + 2 * (A - a) * (A + 2 * tau))
        A = np.where(A > 1e-14, A, 0.0)
        return A, np.where(A > 0, m * A / (A + 2 * tau), 0.0)

    def solve(self, iters, gamma=10.0):
        T, N = self.T, self.N
        tk = np.arange(T + 1)[:, None] / T
        U = np.concatenate([((1 - tk) * self.a0 + tk * self.a1).ravel(), np.zeros(T * (N + 1))])
        rb, mb = self.interp(U)
        wU, wr, wm = U.copy(), rb.copy(), mb.copy()
        xU, xr, xm = self.proj_D(wU, wr, wm)
        tau = gamma * self.dt * self.dx
        actions = []
        for _ in range(iters):
            yU = self.proj_C(2 * xU - wU)
            yr, ym = self.prox_J(2 * xr - wr, 2 * xm - wm, tau)
            wU, wr, wm = wU + yU - xU, wr + yr - xr, wm + ym - xm
            xU, xr, xm = self.proj_D(wU, wr, wm)
            with np.errstate(all="ignore"):
                actions.append(float(np.where(yr > 0, ym * ym / yr, 0.0).sum() * self.dt * self.dx))
        self.U = self.proj_C(xU)
        return np.array(actions)


def fig_bb_solver():
    c = Canvas("bb_solver", 660, 300, "Benamou-Brenier solved on a staggered grid by Douglas-Rachford, against the exact McCann interpolation", sub=SUB)
    L, R, N, T = -4.0, 4.0, 64, 32
    dx = (R - L) / N
    x = L + (np.arange(N) + 0.5) * dx
    a0 = 0.5 * gauss(x, -2, 0.4) + 0.5 * gauss(x, 0, 0.4)
    a1 = gauss(x, 2, 0.6)
    a0 /= a0.sum() * dx; a1 /= a1.sum() * dx
    S = BB1D(a0, a1, L, R, T)
    acts = S.solve(1000)
    rb, mb = S.interp(S.U)
    edges = L + dx * np.arange(N + 1)
    c0 = np.concatenate([[0], np.cumsum(a0 * dx)]); c1 = np.concatenate([[0], np.cumsum(a1 * dx)])
    uu = (np.arange(400000) + 0.5) / 400000
    qa, qb = np.interp(uu, c0, edges), np.interp(uu, c1, edges)
    ref = float(np.mean((qa - qb) ** 2))
    # left: densities at five times, stacked
    times = [0, 0.25, 0.5, 0.75, 1.0]
    for r, t in enumerate(times):
        y0 = 268 - r * 50
        g = Fig(c, (62, y0 - 46, 320, 46), (L, R), (0, 1.15))
        k = int(round(t * T))
        if 0 < k < T:
            dens = 0.5 * (rb[k - 1] + rb[k])
        else:
            dens = a0 if k == 0 else a1
        qh = (1 - t) * qa + t * qb
        hh, _ = np.histogram(qh, bins=edges); hh = hh / (len(uu) * dx)
        cls = "a2" if t == 0 else ("a1" if t == 1 else "a3")
        pts = []
        for i in range(N):
            pts += [(edges[i], dens[i]), (edges[i + 1], dens[i])]
        g.path([(L, 0)] + pts + [(R, 0)], cls, close=True)
        g.path(pts, "ln " + ("c2" if t == 0 else ("c1" if t == 1 else "c3")) + " thin")
        pe = []
        for i in range(N):
            pe += [(edges[i], hh[i]), (edges[i + 1], hh[i])]
        g.path(pe, "ln ck hair dash")
        g.line(L, 0, R, 0, "ax")
        c.text(56, y0 - 6, f"t = {fmt1(t)}", "tx-s", "end")
    for xv in [-4, -2, 0, 2, 4]:
        c.text(Fig(c, (62, 0, 320, 1), (L, R), (0, 1)).X(xv), 284, str(xv), "tx-s", "middle")
    # right: action along the iterations (relative error, log scale)
    h = Fig(c, (458, 40, 180, 180), (1, 3), (9.2, 9.5))
    its = np.arange(1, len(acts) + 1)
    h.axes(xticks=[1, 2, 3], yticks=[9.2, 9.3, 9.4, 9.5], xfmt=lambda v: {1: "10", 2: "100", 3: "1000"}[v],
           yfmt=lambda v: f"{v:.1f}")
    h.line(1, ref, 3, ref, "ln c1 thin dash")
    pts = [(math.log10(i), a) if 9.2 <= a <= 9.5 else None for i, a in zip(its, acts) if i >= 10]
    h.path(pts, "ln c3")
    c.text(548, 26, "action along the iterations", "tx-s", "middle")
    c.text(548, 248, "iteration (log scale)", "tx-s", "middle")
    c.text(548, 268, f"blue dashed: discrete W₂² = {ref:.4f}", "tx-s t1", "middle")
    c.text(548, 284, f"after 1000 iterations: {acts[-1]:.4f}", "tx-s t3", "middle")
    c.save()
    return acts, ref


# ---------------------------------------------------------------------------------------------
def fig_couplings():
    """Independent pairs, the flow-matching trajectories they induce, and OT pairs (2D)."""
    import ot
    c = Canvas("couplings", 660, 256, "Independent pairing, the induced flow-matching trajectories, and optimal-transport pairing", sub=SUB)
    rng = np.random.default_rng(4)
    n = 14
    X0 = rng.standard_normal((n, 2)) * 0.5 + np.array([-2.0, 0.0])
    comp = rng.integers(0, 2, n)
    centers = np.array([[2.0, 1.4], [2.0, -1.4]])
    X1 = centers[comp] + rng.standard_normal((n, 2)) * 0.3
    perm = rng.permutation(n)
    G = ot.emd(np.ones(n) / n, np.ones(n) / n, ot.dist(X0, X1))
    sig_ot = np.argmax(G, 1)
    # exact flow-matching field: source N((-2,0), 0.5^2 I), target mixture of N(c_k, 0.3^2 I), independent coupling
    m0, s0, s1 = np.array([-2.0, 0.0]), 0.5, 0.3

    def v(t, x):
        out = np.zeros_like(x); W = np.zeros((len(x), 2))
        for k in range(2):
            mt = (1 - t) * m0 + t * centers[k]
            st2 = (1 - t) ** 2 * s0 ** 2 + t ** 2 * s1 ** 2
            W[:, k] = -((x - mt) ** 2).sum(1) / (2 * st2)
        W = np.exp(W - W.max(1, keepdims=True)); W /= W.sum(1, keepdims=True)
        for k in range(2):
            mt = (1 - t) * m0 + t * centers[k]
            st2 = (1 - t) ** 2 * s0 ** 2 + t ** 2 * s1 ** 2
            vk = (centers[k] - m0) + (t * s1 ** 2 - (1 - t) * s0 ** 2) / st2 * (x - mt)
            out += W[:, [k]] * vk
        return out
    K = 200
    traj = [X0.copy()]
    xcur = X0.copy()
    for k in range(K):
        t = k / K; hstep = 1 / K
        k1 = v(t, xcur); k2 = v(t + hstep / 2, xcur + hstep / 2 * k1); k3 = v(t + hstep / 2, xcur + hstep / 2 * k2); k4 = v(t + hstep, xcur + hstep * k3)
        xcur = xcur + hstep / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        traj.append(xcur.copy())
    traj = np.array(traj)
    titles = ["independent pairs (X₀, X₁)", "flow-matching trajectories", "optimal-transport pairs"]
    for col in range(3):
        f = Fig(c, (14 + col * 218, 30, 200, 190), (-3.2, 3.1), (-2.6, 2.6))
        if col == 0:
            for i in range(n):
                f.line(X0[i, 0], X0[i, 1], X1[perm[i], 0], X1[perm[i], 1], "ln cm hair")
        elif col == 1:
            for i in range(n):
                f.path([(p[0], p[1]) for p in traj[::4, i]] + [(traj[-1, i, 0], traj[-1, i, 1])], "ln c3 thin")
        else:
            for i in range(n):
                f.line(X0[i, 0], X0[i, 1], X1[sig_ot[i], 0], X1[sig_ot[i], 1], "ln c3 thin")
        for p in X0:
            f.circle(p[0], p[1], 3.4, "f2")
        ends = traj[-1] if col == 1 else X1
        for p in ends:
            f.circle(p[0], p[1], 3.4, "f1")
        c.text(114 + col * 218, 22, titles[col], "tx-b", "middle")
    c.text(114, 246, "straight segments, they cross", "tx-s", "middle")
    c.text(332, 246, "curved, never cross; land on a new pairing", "tx-s", "middle")
    c.text(550, 246, "straight, do not cross (McCann)", "tx-s", "middle")
    c.save()


def fig_tweedie():
    """Tweedie's formula on two atoms: noised density, score, and the denoiser tanh(z / sigma^2)."""
    c = Canvas("tweedie", 660, 270, "Tweedie's formula for data at -1 and +1 observed with Gaussian noise of standard deviation 0.5", sub=SUB)
    sig = 0.5
    rho = lambda z: 0.5 * gauss(z, 1, sig) + 0.5 * gauss(z, -1, sig)
    f = Fig(c, (40, 40, 270, 180), (-3, 3), (0, 1.25))
    f.line(-3, 0, 3, 0, "ax")
    for xv in [-3, -2, -1, 0, 1, 2, 3]:
        f.text(xv, 0, str(xv), "tx-s", "middle", dy=14)
    zs = np.linspace(-3, 3, 400)
    f.path([(-3, 0)] + [(z, rho(z)) for z in zs] + [(3, 0)], "a5", close=True)
    f.path([(z, rho(z)) for z in zs], "ln c5 thin")
    f.lollipop(-1, 1.0, 1)
    f.lollipop(1, 1.0, 1)
    f.text(-1, 1.0, "W = −1", "tx-s t1", "middle", dy=-10)
    f.text(1, 1.0, "W = +1", "tx-s t1", "middle", dy=-10)
    f.text(1.3, 0.62, "density ρ of Z = W + 0.5 ε", "tx-s t5", "start")
    z0 = 0.3
    f.circle(z0, 0, 4, "fk")
    f.text(z0, 0, "z = 0.3", "tx-s", "middle", dy=28)
    c.text(175, 26, "data and noised density", "tx-b", "middle")
    g = Fig(c, (400, 40, 240, 180), (-1.5, 1.5), (-1.25, 1.25))
    g.axes(xticks=[-1, 0, 1], yticks=[-1, 0, 1], grid=True, xlabel="z")
    g.fn(lambda z: z, "ln cm thin dash", -1.25, 1.25)
    g.fn(lambda z: math.tanh(z / sig ** 2), "ln c3", -1.5, 1.5)
    hh = 1e-6
    score = (math.log(rho(z0 + hh)) - math.log(rho(z0 - hh))) / (2 * hh)
    den = z0 + sig ** 2 * score
    g.line(z0, z0, z0, den, "ln c2 thin")
    g.circle(z0, z0, 3.5, "fk")
    g.circle(z0, den, 4, "f3")
    g.text(z0, den, f"{den:.3f}", "tx-s t3", "start", dx=8, dy=4)
    g.text(z0, (z0 + den) / 2, "σ² × score", "tx-s t2", "start", dx=6)
    g.text(-1.4, -1.0, "identity", "tx-s", "start", dy=-6)
    c.text(520, 26, "denoiser z ↦ E[W | Z = z] = tanh(z/σ²)", "tx-b", "middle")
    c.text(330, 262, "Tweedie: E[W | Z = z] = z + σ² (log ρ)′(z); here the score at 0.3 is " + f"{score:.3f}", "tx-s", "middle")
    c.save()


def _land_paths(z0, ys, ws, lam_grid):
    """schedule-free probability flow dy/dlam = E[X | lam X + Z = y] for 1D atoms; returns y on lam_grid."""
    logw = np.log(ws)
    def post(lam, y):
        lw = logw[None, :] - 0.5 * (y[:, None] - lam * ys[None, :]) ** 2
        lw -= lw.max(1, keepdims=True); w = np.exp(lw); w /= w.sum(1, keepdims=True)
        return w @ ys
    out = [z0.copy()]
    y = z0.copy()
    for l0, l1 in zip(lam_grid[:-1], lam_grid[1:]):
        h = l1 - l0
        k1 = post(l0, y); k2 = post(l0 + h / 2, y + h / 2 * k1); k3 = post(l0 + h / 2, y + h / 2 * k2); k4 = post(l1, y + h * k3)
        y = y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        out.append(y.copy())
    return np.array(out)


def fig_schedules():
    """Noise N(0,1) to two atoms: linear and variance-preserving schedules and OT rays all end on the same map (1D)."""
    c = Canvas("schedules", 660, 280, "Three ways from noise to two atoms in one dimension; same terminal map", sub=SUB)
    ys, ws = np.array([-2.0, 1.0]), np.array([0.3, 0.7])
    z0 = NORM.ppf((np.arange(16) + 0.5) / 16)
    lam_grid = np.concatenate([np.linspace(0, 2, 201), np.geomspace(2, 400, 600)[1:]])
    Y = _land_paths(z0, ys, ws, lam_grid)
    q = NORM.ppf(0.3)
    target = np.where(z0 < q, -2.0, 1.0)
    ts = np.linspace(0, 0.997, 160)
    schedules = [("linear: tX₁ + (1 − t)X₀", lambda t: t, lambda t: 1 - t),
                 ("variance-preserving (cos/sin)", lambda t: math.sin(math.pi * t / 2), lambda t: math.cos(math.pi * t / 2))]
    for col in range(3):
        f = Fig(c, (30 + col * 215, 30, 190, 200), (-3.2, 3.0), (0, 1))
        f.line(-3.2, 0, 3.0, 0, "ax")
        f.line(-3.2, 1, 3.0, 1, "gr")
        for xv in [-2, 0, 2]:
            f.text(xv, 0, str(xv), "tx-s", "middle", dy=14)
        for i in range(len(z0)):
            if col < 2:
                a, b = schedules[col][1], schedules[col][2]
                pts = []
                for t in ts:
                    lam = a(t) / b(t)
                    yv = np.interp(lam, lam_grid, Y[:, i])
                    pts.append((b(t) * yv, t))
                pts.append((target[i], 1.0))
                cls = "ln c3 thin"
            else:
                pts = [(z0[i], 0), (target[i], 1)]
                cls = "ln c3 thin"
            f.path(pts, cls)
            f.circle(z0[i], 0, 2.6, "f2")
        f.circle(-2, 1, 5, "f1"); f.circle(1, 1, 6, "f1")
        f.line(q, 0, q, 0.06, "ln ck thin")
        title = schedules[col][0] if col < 2 else "OT rays (monotone map)"
        c.text(125 + col * 215, 20, title, "tx-b", "middle")
    c.text(10, 36, "data", "tx-s t1", "start")
    c.text(10, 232, "noise", "tx-s t2", "start")
    c.text(330, 262, f"every particle starting left of Φ⁻¹(0.3) = {q:.3f} (black tick) lands on −2, every other on +1", "tx-s", "middle")
    c.text(330, 276, "trajectories differ, the terminal map is the same: in 1D it is the monotone (optimal) map", "tx-s", "middle")
    c.save()


def _sqrtm(S):
    w, U = np.linalg.eigh(S)
    return U @ np.diag(np.sqrt(w)) @ U.T


def _isqrtm(S):
    w, U = np.linalg.eigh(S)
    return U @ np.diag(1 / np.sqrt(w)) @ U.T


def fig_fm_gauss():
    """Gaussian flow matching with non-commuting covariances: the terminal map is not the Brenier map."""
    c = Canvas("fm_gauss", 600, 300, "Flow matching between N(0, diag(4,1)) and N(0, [[2,1],[1,2]]): flow map versus Brenier map", sub=SUB)
    S0 = np.diag([4.0, 1.0]); S1 = np.array([[2.0, 1.0], [1.0, 2.0]])
    r0, ir0 = _sqrtm(S0), _isqrtm(S0)
    C = ir0 @ S1 @ ir0
    Tt = lambda t: r0 @ _sqrtm((1 - t) ** 2 * np.eye(2) + t ** 2 * C) @ ir0
    Tfm = Tt(1.0)
    Tot = ir0 @ _sqrtm(r0 @ S1 @ r0) @ ir0
    f = Fig(c, (20, 20, 300, 260), (-2.7, 2.7), (-2.35, 2.35))
    f.line(-2.7, 0, 2.7, 0, "gr"); f.line(0, -2.35, 0, 2.35, "gr")
    th = np.linspace(0, 2 * np.pi, 200)
    circ = np.c_[np.cos(th), np.sin(th)]
    e0 = circ @ r0.T; e1 = circ @ _sqrtm(S1).T
    f.path([tuple(p) for p in e0], "ln c2 thin")
    f.path([tuple(p) for p in e1], "ln c1 thin")
    angles = np.deg2rad(np.arange(0, 360, 30))
    pts0 = np.c_[np.cos(angles), np.sin(angles)] @ r0.T
    for p in pts0[::2]:
        tr = [Tt(t) @ p for t in np.linspace(0, 1, 60)]
        f.path([tuple(q) for q in tr], "ln c3 thin")
    for p in pts0:
        a, b = Tfm @ p, Tot @ p
        f.line(a[0], a[1], b[0], b[1], "ln ck hair dash")
        f.circle(p[0], p[1], 3, "f2")
        f.circle(a[0], a[1], 3.6, "f3")
        c.add(f'<circle cx="{f.X(b[0]):.1f}" cy="{f.Y(b[1]):.1f}" r="4" class="ln ck thin nofill"/>')
    cost = lambda T: np.trace((T - np.eye(2)) @ S0 @ (T - np.eye(2)).T)
    x0 = 345
    c.text(x0, 50, "orange: α₀ = N(0, Σ₀), 12 points", "tx-s", "start")
    c.text(x0, 68, "blue: α₁ = N(0, Σ₁) (1-st.-dev. ellipses)", "tx-s", "start")
    c.text(x0, 86, "green curves: flow-matching paths (6 shown)", "tx-s", "start")
    c.text(x0, 104, "green dots: flow map T₁ᶠᴹ (independent", "tx-s", "start")
    c.text(x0, 118, "coupling); black circles: Brenier map Tᴼᵀ", "tx-s", "start")
    c.text(x0, 160, f"cost of T₁ᶠᴹ: E‖T(X) − X‖² = {cost(Tfm):.4f}", "tx-s t3", "start")
    c.text(x0, 178, f"W₂² (Brenier map) = {cost(Tot):.4f}", "tx-s", "start")
    c.text(x0, 196, f"excess {100 * (cost(Tfm) / cost(Tot) - 1):.1f}%: Σ₀Σ₁ ≠ Σ₁Σ₀", "tx-s", "start")
    a = (Tfm - Tfm.T) / 2
    c.text(x0, 234, "T₁ᶠᴹ = [[{:.3f}, {:.3f}], [{:.3f}, {:.3f}]]".format(*Tfm.ravel()), "tx-s", "start")
    c.text(x0, 252, "not symmetric: it hides a rotation", "tx-s", "start")
    c.save()
    return Tfm, Tot


def _land2d(z, Y, p, lam_max=40.0):
    logp = np.log(p)
    lams = np.concatenate([np.linspace(0, 2, 61), np.geomspace(2, lam_max, 101)[1:]])
    def post(lam, y):
        d2 = ((y[:, None, :] - lam * Y[None, :, :]) ** 2).sum(-1)
        lw = logp[None, :] - 0.5 * d2
        lw -= lw.max(1, keepdims=True); w = np.exp(lw)
        return w / w.sum(1, keepdims=True)
    y = z.copy()
    f = lambda lam, y: post(lam, y) @ Y
    for l0, l1 in zip(lams[:-1], lams[1:]):
        h = l1 - l0
        k1 = f(l0, y); k2 = f(l0 + h / 2, y + h / 2 * k1); k3 = f(l0 + h / 2, y + h / 2 * k2); k4 = f(l1, y + h * k3)
        y = y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return np.argmax(post(lam_max, y), 1)


def _laguerre_weights(Y, p, n=401, box=6.0):
    u = np.linspace(-box, box, n)
    G1, G2 = np.meshgrid(u, u)
    zg = np.c_[G1.ravel(), G2.ravel()]
    wg = np.exp(-0.5 * (zg ** 2).sum(1)); wg /= wg.sum()
    D = ((zg[:, None, :] - Y[None, :, :]) ** 2).sum(-1)
    def masses(gf, temp):
        g = np.concatenate([[0.0], gf])
        cc = -(D - g[None, :]) / temp
        cc -= cc.max(1, keepdims=True); w = np.exp(cc); w /= w.sum(1, keepdims=True)
        return (wg[:, None] * w).sum(0)
    g = np.zeros(len(Y) - 1)
    for temp in [0.3, 0.1, 0.03, 0.01, 0.003]:
        g = optimize.root(lambda gf: masses(gf, temp)[1:] - p[1:], g, method="hybr").x
    return np.concatenate([[0.0], g])


def fig_cells():
    """Noise N(0, I) to three atoms: cells of the flow-matching / probability-flow map versus Laguerre (OT) cells."""
    c = Canvas("cells", 620, 300, "Gaussian noise to three atoms: where each noise sample lands, flow versus optimal transport", sub=SUB)
    Y = np.array([[-3.0, 0.0], [3.0, 0.0], [0.0, 1.0]]); p = np.ones(3) / 3
    g = _laguerre_weights(Y, p)
    box = (-3.5, 3.5, -2.6, 2.6)
    f = Fig(c, (20, 18, 340, 262), (box[0], box[1]), (box[2], box[3]))
    for r in [1, 2, 3]:
        th = np.linspace(0, 2 * np.pi, 160)
        f.path([(r * math.cos(a), r * math.sin(a)) for a in th], "ln cm hair", extra=' stroke-opacity="0.5"')
    # Laguerre boundaries: points where two costs tie and are below the third
    def lag_cost(z):
        return ((z[:, None, :] - Y[None, :, :]) ** 2).sum(-1) - g[None, :]
    # scan horizontal lines for transitions, for both partitions
    hs = np.linspace(box[2], box[3], 53)
    xs = np.linspace(box[0], box[1], 141)
    Z = np.array([[x, h] for h in hs for x in xs])
    lab_fm = _land2d(Z, Y, p).reshape(len(hs), len(xs))
    lab_ot = np.argmin(lag_cost(Z), 1).reshape(len(hs), len(xs))
    curves = {}
    for name, lab, labeler in [("fm", lab_fm, lambda z: _land2d(z, Y, p)), ("ot", lab_ot, lambda z: np.argmin(lag_cost(z), 1))]:
        jobs = []
        for r, h in enumerate(hs):
            for j in range(len(xs) - 1):
                if lab[r, j] != lab[r, j + 1]:
                    jobs.append((h, xs[j], xs[j + 1], lab[r, j], lab[r, j + 1]))
        lo = np.array([J[1] for J in jobs]); hi = np.array([J[2] for J in jobs]); hv = np.array([J[0] for J in jobs])
        left = np.array([J[3] for J in jobs])
        for _ in range(26):
            mid = 0.5 * (lo + hi)
            lm = labeler(np.c_[mid, hv])
            same = lm == left
            lo = np.where(same, mid, lo); hi = np.where(same, hi, mid)
        for J, xm in zip(jobs, 0.5 * (lo + hi)):
            key = tuple(sorted((J[3], J[4])))
            curves.setdefault((name, key), []).append((xm, J[0]))
    for (name, key), pts in curves.items():
        pts = sorted(pts, key=lambda q: q[1])
        f.path(pts, "ln c3" if name == "fm" else "ln ck thin dash")
    for k, yk in enumerate(Y):
        f.circle(yk[0], yk[1], 6, "f1")
    f.text(-3, 0, "y₁", "tx-s t1", "middle", dy=-10)
    f.text(3, 0, "y₂", "tx-s t1", "middle", dy=-10)
    f.text(0, 1, "y₃", "tx-s t1", "start", dx=8, dy=-6)
    x0 = 380
    c.add(f'<line x1="{x0}" y1="60" x2="{x0 + 28}" y2="60" class="ln c3"/>')
    c.text(x0 + 36, 64, "boundaries of the flow cells", "tx-s", "start")
    c.text(x0 + 36, 78, "(flow matching = probability flow)", "tx-s", "start")
    c.add(f'<line x1="{x0}" y1="100" x2="{x0 + 28}" y2="100" class="ln ck thin dash"/>')
    c.text(x0 + 36, 104, "Laguerre cells of the OT map", "tx-s", "start")
    c.text(x0, 140, "atoms y₁ = (−3, 0), y₂ = (3, 0), y₃ = (0, 1),", "tx-s", "start")
    c.text(x0, 156, "weight ⅓ each; grey circles: N(0, I) contours", "tx-s", "start")
    c.text(x0, 190, "both maps give each atom mass ⅓,", "tx-s", "start")
    c.text(x0, 206, "but they do not send the same noise", "tx-s", "start")
    c.text(x0, 222, "samples to the same atoms", "tx-s", "start")
    c.save()
    return g


def fig_bridges():
    """Endpoint couplings lifted to paths: straight segments (eps = 0) and Brownian bridges over Sinkhorn plans."""
    import ot
    c = Canvas("bridges", 660, 240, "Straight segments for optimal transport and Brownian bridges for Schrodinger bridges", sub=SUB)
    rng = np.random.default_rng(11)
    ang = np.deg2rad(np.arange(6) * 60 + 15)
    Xs = 0.35 * np.c_[np.cos(ang * 2 + 0.4), np.sin(ang * 2 + 0.4)] * np.array([[1.0], [0.6], [0.9], [0.5], [0.8], [0.7]])
    Ys = 2.0 * np.c_[np.cos(ang), np.sin(ang)]
    a = np.ones(6) / 6
    C = ot.dist(Xs, Ys)
    for col, eps in enumerate([0.0, 0.05, 0.3]):
        f = Fig(c, (14 + col * 218, 30, 200, 180), (-2.6, 2.6), (-2.3, 2.3))
        P = ot.emd(a, a, C) if eps == 0 else ot.sinkhorn(a, a, C, eps * 2, numItermax=5000)
        # 36 paths allocated proportionally to P
        counts = np.floor(P * 36 + 0.5).astype(int)
        for i in range(6):
            for j in range(6):
                for _ in range(counts[i, j]):
                    ts = np.linspace(0, 1, 41)
                    if eps == 0:
                        pts = [(1 - t) * Xs[i] + t * Ys[j] for t in ts]
                    else:
                        dW = rng.standard_normal((40, 2)) * math.sqrt(eps / 40)
                        W = np.vstack([[0, 0], np.cumsum(dW, 0)])
                        B = W - ts[:, None] * W[-1]
                        pts = [(1 - t) * Xs[i] + t * Ys[j] + B[k] for k, t in enumerate(ts)]
                    f.path([tuple(q) for q in pts], "ln c3 hair", extra=' stroke-opacity="0.75"')
        for q in Xs:
            f.circle(q[0], q[1], 3.6, "f2")
        for q in Ys:
            f.circle(q[0], q[1], 3.6, "f1")
        c.text(114 + col * 218, 22, "ε = 0 (optimal transport)" if eps == 0 else f"ε = {fmt1(eps)}", "tx-b", "middle")
    c.text(330, 230, "the endpoint coupling is the (entropic) OT plan; each pair is joined by a straight line (ε = 0) or a Brownian bridge", "tx-s", "middle")
    c.save()


def fig_multimarginal():
    """Comonotone multimarginal plan on the line and the barycenter quantile function."""
    c = Canvas("multimarginal", 600, 290, "Three measures on the line: the comonotone multimarginal plan and the barycenter", sub=SUB)
    xs = [np.array([0.0, 3.0]), np.array([0.0, 1.0, 2.0]), np.array([1.0, 2.0, 3.0, 5.0])]
    ws = [np.array([0.5, 0.5]), np.ones(3) / 3, np.ones(4) / 4]
    f = Fig(c, (50, 24, 380, 224), (0, 1), (-0.3, 5.4))
    f.axes(xticks=[0, 0.25, 0.5, 0.75, 1], yticks=[0, 1, 2, 3, 4, 5], xfmt=lambda v: {0: "0", 0.25: "¼", 0.5: "½", 0.75: "¾", 1: "1"}[v],
           grid=False, xlabel="level u", ylabel="quantile")
    cuts = sorted(set([0.25, 1 / 3, 0.5, 2 / 3, 0.75]))
    for u in cuts:
        f.line(u, -0.3, u, 5.4, "ln cm hair dash")
    def qf(x, w, u):
        cw = np.cumsum(w)
        return x[min(np.searchsorted(cw, u - 1e-12), len(x) - 1)]
    cols = ["c1", "c5", "c4"]
    offs = [0.06, 0.0, -0.06]
    for s in range(3):
        bounds = np.concatenate([[0], np.cumsum(ws[s])])
        for k in range(len(xs[s])):
            f.line(bounds[k], xs[s][k] + offs[s], bounds[k + 1], xs[s][k] + offs[s], f"ln {cols[s]}")
    edges = [0] + cuts + [1]
    for u0, u1 in zip(edges[:-1], edges[1:]):
        um = 0.5 * (u0 + u1)
        b = np.mean([qf(xs[s], ws[s], um) for s in range(3)])
        f.line(u0, b, u1, b, "ln c3")
        f.circle(um, b, 3.4, "f3")
    x0 = 446
    c.text(x0, 50, "β₁ = ½(δ₀ + δ₃)", "tx-s t1", "start")
    c.text(x0, 68, "β₂ = ⅓(δ₀ + δ₁ + δ₂)", "tx-s t5", "start")
    c.add(f'<text x="{x0}" y="86" class="tx-s" text-anchor="start" style="fill: var(--s4)">β₃ = ¼(δ₁ + δ₂ + δ₃ + δ₅)</text>')
    c.text(x0, 112, "green: average quantile =", "tx-s t3", "start")
    c.text(x0, 128, "barycenter (weights ⅓)", "tx-s t3", "start")
    c.text(x0, 160, "dashed: cuts at", "tx-s", "start")
    c.text(x0, 176, "u = ¼, ⅓, ½, ⅔, ¾;", "tx-s", "start")
    c.text(x0, 192, "6 intervals = 6 atoms", "tx-s", "start")
    c.text(x0, 208, "of the comonotone plan", "tx-s", "start")
    c.save()


if __name__ == "__main__":
    for fn in [fig_lagrange_euler, fig_rotation, fig_gauss_plane, fig_perspective, fig_staggered, fig_bb_solver,
               fig_couplings, fig_tweedie, fig_schedules, fig_fm_gauss, fig_cells, fig_bridges, fig_multimarginal]:
        out = fn()
        if fn is fig_bb_solver:
            print("   BB solver: action after 1000 iterations", out[0][-1], " discrete W2^2", out[1])
        if fn is fig_cells:
            print("   Laguerre weights", out)
