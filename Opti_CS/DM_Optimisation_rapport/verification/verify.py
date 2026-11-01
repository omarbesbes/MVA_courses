"""Verification independante des resultats du rapport DM (decodage speculatif)."""
import itertools
import numpy as np
from scipy.optimize import linprog

rng = np.random.default_rng(0)

# ---------------- Partie I : PL de couplage ----------------
def lp_value(p, q):
    n = len(p)
    c = -np.eye(n).ravel()
    A = np.zeros((2 * n, n * n))
    for x in range(n):
        A[x, x * n:(x + 1) * n] = 1
    for y in range(n):
        A[n + y, y::n] = 1
    res = linprog(c, A_eq=A, b_eq=np.r_[q, p], bounds=(0, None), method="highs")
    return -res.fun, A

errs = []
for _ in range(200):
    n = rng.integers(3, 10)
    p = rng.dirichlet(np.ones(n) * rng.choice([0.3, 1, 3]))
    q = rng.dirichlet(np.ones(n) * rng.choice([0.3, 1, 3]))
    v, A = lp_value(p, q)
    errs.append(abs(v - np.minimum(p, q).sum()))
print("PL: max |val - beta| =", max(errs))
print("rang A (n=5) =", np.linalg.matrix_rank(lp_value(np.ones(5) / 5, np.ones(5) / 5)[1]), "(attendu 2n-1 = 9)")

# lossy: max trace s.t. rows q, cols r, TV(r,p)<=eps
def lossy_value(p, q, eps):
    n = len(p)
    nv = n * n + n + n  # pi, r, t
    c = np.zeros(nv); c[:n * n] = -np.eye(n).ravel()
    Aeq = np.zeros((2 * n, nv)); beq = np.zeros(2 * n)
    for x in range(n):
        Aeq[x, x * n:(x + 1) * n] = 1; beq[x] = q[x]
    for y in range(n):
        Aeq[n + y, y:n * n:n] = 1; Aeq[n + y, n * n + y] = -1
    Aub = []; bub = []
    for y in range(n):
        row = np.zeros(nv); row[n * n + y] = 1; row[n * n + n + y] = -1; Aub.append(row); bub.append(p[y])
        row = np.zeros(nv); row[n * n + y] = -1; row[n * n + n + y] = -1; Aub.append(row); bub.append(-p[y])
    row = np.zeros(nv); row[n * n + n:] = 1; Aub.append(row); bub.append(2 * eps)
    res = linprog(c, A_ub=np.array(Aub), b_ub=bub, A_eq=Aeq, b_eq=beq, bounds=(0, None), method="highs")
    return -res.fun

e2 = []
for _ in range(100):
    n = rng.integers(3, 8)
    p = rng.dirichlet(np.ones(n)); q = rng.dirichlet(np.ones(n))
    beta = np.minimum(p, q).sum()
    for eps in [0, 0.05, 0.2, 0.6]:
        e2.append(abs(lossy_value(p, q, eps) - min(1, beta + eps)))
print("Prop 2: max ecart =", max(e2))

# ---------------- Partie II ----------------
def E(eps, a):
    al = a + eps
    return 1 + np.cumprod(al).sum()

def gradE(eps, a):
    al = a + eps; g = len(a)
    P = np.r_[1, np.cumprod(al)]  # P[k] = P_k
    T = np.ones(g)
    for t in range(g - 2, -1, -1):
        T[t] = 1 + al[t + 1] * T[t + 1]
    return P[:g] * T

def hessE(eps, a):
    al = a + eps; g = len(a)
    H = np.zeros((g, g))
    for i in range(g):
        for j in range(g):
            if i != j:
                e = np.zeros(g); h = 1e-6; e[j] = h
                H[i, j] = (gradE(eps + e, a)[i] - gradE(eps - e, a)[i]) / (2 * h)
    return H

def proj(y, s, u, B):
    z = np.clip(y, 0, u)
    if s @ z <= B:
        return z
    lo, hi = 0.0, max(np.max(y / s), 0) + 1
    for _ in range(200):
        mid = (lo + hi) / 2
        if s @ np.clip(y - mid * s, 0, u) > B:
            lo = mid
        else:
            hi = mid
    return np.clip(y - hi * s, 0, u)

def pg(a, s, B, x0, tau=None, it=20000):
    u = 1 - a; g = len(a)
    if tau is None:
        L = np.sqrt(sum((g - max(i, j) + 1) ** 2 for i in range(1, g + 1) for j in range(1, g + 1) if i != j))
        tau = 1 / L
    x = proj(x0, s, u, B)
    for _ in range(it):
        xn = proj(x + tau * gradE(x, a), s, u, B)
        if np.linalg.norm(xn - x) < 1e-13:
            x = xn; break
        x = xn
    return x

def kkt_lambda(x, a, s, u, B, tol=1e-7):
    g = gradE(x, a); rho = g / s
    inner = (x > tol) & (x < u - tol)
    return rho, inner

def modelA(a, s, B):
    u = 1 - a; x = np.zeros(len(a)); rem = B
    for t in np.argsort(s, kind="stable"):
        take = min(u[t], rem / s[t]); x[t] = take; rem -= take * s[t]
        if rem <= 1e-15: break
    return x

# Prop 3 example
a = np.array([0.55, 0.7]); s = np.array([1.5, 0.6]); u = 1 - a; B = 0.35 * s @ u
x = pg(a, s, B, np.zeros(2))
print("Prop 3: eps* =", x, "E* =", E(x, a), " modele A E =", E(modelA(a, s, B), a))
k = s[0] / s[1]; c = a[1] + B / s[1]
print("  E* formule fermee =", 1 + (1 + c + k * a[0]) ** 2 / (4 * k), " lambda =", (1 + c + k * a[0]) / (2 * s[0]))

# S1 S2 S3
g = 6; a = np.full(g, 0.6); u = 1 - a
profiles = {"S1": np.ones(g), "S2": np.array([2.0, 1.7, 1.4, 1.1, 0.8, 0.5]), "S3": np.array([0.3, 2.5, 0.3, 0.3, 2.5, 0.3])}
for name, s in profiles.items():
    B = 0.3 * s @ u
    best = None
    vals = []
    for r in range(30):
        x0 = rng.uniform(0, u)
        x = pg(a, s, B, x0)
        vals.append(E(x, a))
        if best is None or E(x, a) > E(best, a):
            best = x
    xa = modelA(a, s, B)
    rho, inner = kkt_lambda(best, a, s, u, B)
    print(f"{name}: E_B={E(best, a):.4f} (spread {max(vals)-min(vals):.1e})  E_A={E(xa, a):.4f}  unif={E(0.3*u, a):.4f}")
    print("   part relachee B :", np.round(best / u, 3), " A :", np.round(xa / u, 3))
    print("   rho =", np.round(rho, 4), " interieures :", np.where(inner)[0] + 1)

# frontiere S3 : convexe ou concave ?
for name in ["S2", "S3"]:
    s = profiles[name]; Bm = s @ u
    Bs = np.linspace(0, Bm, 41); Es = []
    for B in Bs:
        best = max((pg(a, s, B, rng.uniform(0, u), it=6000) for _ in range(6)), key=lambda x: E(x, a))
        Es.append(E(best, a))
    d2 = np.diff(Es, 2)
    print(f"frontiere {name}: min d2 = {d2.min():.3e}, max d2 = {d2.max():.3e}  (convexe si d2 >= 0)")

# ordre 2 : hessienne sur le cone critique au point trouve (S2)
s = profiles["S2"]; B = 0.3 * s @ u
best = max((pg(a, s, B, rng.uniform(0, u)) for _ in range(10)), key=lambda x: E(x, a))
H = hessE(best, a)
inner = (best > 1e-7) & (best < u - 1e-7)
idx = np.where(inner)[0]
print("S2 interieures:", idx + 1)
if len(idx) >= 2:
    sI = s[idx]
    # base de {d : s_I . d = 0}
    Q, _ = np.linalg.qr(np.c_[sI, np.eye(len(idx))[:, :len(idx) - 1]])
    Z = Q[:, 1:]
    Hr = Z.T @ H[np.ix_(idx, idx)] @ Z
    print("  valeurs propres hessienne restreinte (doivent etre <= 0 pour un max local):", np.linalg.eigvalsh(Hr))

# Multi-start sur instances aleatoires + certification globale grossiere gamma=3 par grille sur la face de budget
worst = 0
for trial in range(40):
    g = rng.choice([3, 4]); a = rng.uniform(0.3, 0.95, g); u = 1 - a; s = rng.uniform(0.2, 3, g)
    B = rng.uniform(0.1, 0.9) * s @ u
    sols = [pg(a, s, B, rng.uniform(0, u), it=8000) for _ in range(10)]
    vals = [E(x, a) for x in sols]
    best = max(vals)
    # grille fine sur les g-1 premieres coordonnees, derniere par budget sature
    grid = np.linspace(0, 1, 61)
    gbest = -1
    for comb in itertools.product(grid, repeat=g - 1):
        x = np.array(comb) * u[:-1]
        rem = B - s[:-1] @ x
        if rem < -1e-12: continue
        xl = min(u[-1], rem / s[-1])
        xx = np.r_[x, xl]
        gbest = max(gbest, E(xx, a))
    worst = max(worst, gbest - best)
print("certification grille (gamma 3-4) : max(E_grille - E_PG) =", worst, "(<= 0 ou ~0 attendu)")
