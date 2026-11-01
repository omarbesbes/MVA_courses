"""Fonctions communes aux scripts de verification de la partie II du DM."""
import numpy as np


def E(eps, a):
    """Nombre moyen de tokens par passe : 1 + sum_k prod_{j<=k} (a_j + eps_j)."""
    return 1 + np.cumprod(a + eps).sum()


def gradE(eps, a):
    """d_t E = P_{t-1} T_t."""
    al = a + eps
    g = len(a)
    P = np.r_[1, np.cumprod(al)]
    T = np.ones(g)
    for t in range(g - 2, -1, -1):
        T[t] = 1 + al[t + 1] * T[t + 1]
    return P[:g] * T


def proj(y, s, u, B):
    """Projection sur K = {0 <= z <= u, s.z <= B} : clip, puis dichotomie sur le multiplicateur."""
    z = np.clip(y, 0, u)
    if s @ z <= B:
        return z
    lo, hi = 0.0, max(np.max(y / s), 0) + 1
    for _ in range(100):
        mid = (lo + hi) / 2
        if s @ np.clip(y - mid * s, 0, u) > B:
            lo = mid
        else:
            hi = mid
    return np.clip(y - hi * s, 0, u)


def pg(a, s, B, x0, it=4000):
    """Gradient projete en montee, pas 1/L."""
    u = 1 - a
    g = len(a)
    L = np.sqrt(sum((g - max(i, j) + 1) ** 2
                    for i in range(1, g + 1) for j in range(1, g + 1) if i != j))
    tau = 1 / L
    x = proj(x0, s, u, B)
    for _ in range(it):
        xn = proj(x + tau * gradE(x, a), s, u, B)
        if np.linalg.norm(xn - x) < 1e-14:
            return xn
        x = xn
    return x


def best_of(a, s, B, rng, starts=6, it=6000, extra=()):
    """Meilleur point KKT parmi plusieurs departs aleatoires (et departs supplementaires)."""
    u = 1 - a
    x0s = [rng.uniform(0, u) for _ in range(starts)] + list(extra)
    return max((pg(a, s, B, x0, it=it) for x0 in x0s), key=lambda x: E(x, a))


def modelA(a, s, B):
    """Modele additif : glouton par sensibilite croissante (sac a dos fractionnaire)."""
    u = 1 - a
    x = np.zeros(len(a))
    rem = B
    for t in np.argsort(s, kind="stable"):
        take = min(u[t], rem / s[t])
        x[t] = take
        rem -= take * s[t]
        if rem <= 1e-15:
            break
    return x


A6 = np.full(6, 0.6)
PROFILS = {"S2": np.array([2.0, 1.7, 1.4, 1.1, 0.8, 0.5]),
           "S3": np.array([0.3, 2.5, 0.3, 0.3, 2.5, 0.3])}
