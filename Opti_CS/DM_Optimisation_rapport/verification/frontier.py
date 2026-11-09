"""Frontieres vitesse-budget S2/S3 : gains de l'optimum sur le modele A et sur la deviation
uniforme, et comparaison du multiplicateur lambda avec la pente numerique de E*(B)."""
import numpy as np
from common import E, gradE, best_of, modelA, A6, PROFILS

rng = np.random.default_rng(1)
a = A6
u = 1 - a
for name, s in PROFILS.items():
    Bm = s @ u
    f = np.linspace(0.0, 1.0, 101)
    res = []
    for fk in f:
        B = fk * Bm
        x = best_of(a, s, B, rng, starts=4, it=4000)
        rho = gradE(x, a) / s
        inner = (x > 1e-7) & (x < u - 1e-7)
        res.append((E(x, a), E(modelA(a, s, B), a), E(fk * u, a),
                    rho[inner].mean() if inner.any() else np.nan))
    eb, ea, eu, lam = np.array(res).T
    i, j, k, l = (np.argmax(eb - ea), np.argmax((eb - ea) / ea),
                  np.argmax((eb - ea) / eb), np.argmax(eb - eu))
    print(f"{name}: gain max sur A = {np.max(eb - ea):.3f} (B/Bmax = {f[i]:.2f}) ; "
          f"gain relatif max = {100 * np.max((eb - ea) / ea):.1f} % (B/Bmax = {f[j]:.2f}) ; "
          f"perte relative max de A = {100 * np.max((eb - ea) / eb):.1f} % (B/Bmax = {f[k]:.2f})")
    print(f"    gain max sur l'uniforme = {np.max(eb - eu):.3f} (B/Bmax = {f[l]:.2f})")
    m = np.argmin(abs(f - 0.3))
    print(f"    B = 0,3 Bmax : optimum {eb[m]:.4f}, A {ea[m]:.4f} : optimum +{100 * (eb[m] - ea[m]) / ea[m]:.1f} %, "
          f"A -{100 * (eb[m] - ea[m]) / eb[m]:.1f} %")
    slope = np.gradient(eb, f * Bm)
    ok = ~np.isnan(lam) & (f > 0.02) & (f < 0.98)
    print(f"    ecart max |lambda - pente| / lambda = {100 * np.nanmax(abs(lam[ok] - slope[ok]) / lam[ok]):.2f} % "
          "(petit en S2 ; grand en S3, ou la pente saute aux budgets sommets)")
