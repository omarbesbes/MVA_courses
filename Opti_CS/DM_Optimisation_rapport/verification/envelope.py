"""Encadrement exact du prix marginal (rapport, eq. (1)) :
    (E*(B) - E*(B-h)) / h  <=  lambda  <=  (E*(B+h) - E*(B)) / h
des que l'optimum a une position interieure t et 0 < h <= s_t min(eps_t, u_t - eps_t)
(E est affine en chaque variable)."""
import numpy as np
from common import E, gradE, best_of, A6, PROFILS

rng = np.random.default_rng(3)


def check(a, s, B, starts):
    u = 1 - a
    Bm = s @ u
    x = best_of(a, s, B, rng, starts=starts)
    inner = (x > 1e-7) & (x < u - 1e-7)
    if not inner.any():
        return []
    lam = (gradE(x, a) / s)[inner].mean()
    t = np.where(inner)[0]
    hmax = np.max(s[t] * np.minimum(x[t], u[t] - x[t]))
    e0 = E(x, a)
    out = []
    for h in (min(1e-3 * Bm, 0.5 * hmax), min(1e-2 * Bm, 0.9 * hmax)):
        right = (E(best_of(a, s, B + h, rng, starts=starts), a) - e0) / h
        left = (e0 - E(best_of(a, s, B - h, rng, starts=starts), a)) / h
        out.append(max(left - lam, lam - right))
    return out


for name, s in PROFILS.items():
    a = A6
    d = [v for f in np.linspace(0.05, 0.95, 37) for v in check(a, s, f * (s @ (1 - a)), 6)]
    print(f"{name}: {len(d)} tests, pire depassement = {max(d):.1e} (attendu : 0 a l'arrondi pres)")
d = []
for _ in range(60):
    g = rng.integers(3, 6)
    a = rng.uniform(0.3, 0.95, g)
    s = rng.uniform(0.2, 3, g)
    d += check(a, s, rng.uniform(0.1, 0.9) * (s @ (1 - a)), 8)
print(f"aleatoires (gamma = 3 a 5) : {len(d)} tests, pire depassement = {max(d):.1e}")
