"""Structure de la frontiere E*(B) (rapport, §3.5) : E* est affine quand une seule position est
interieure, convexe entre deux budgets sommets B_I = sum_{t in I} s_t u_t consecutifs, et sa pente
ne baisse qu'en un B_I. On suit l'optimum le long de B en S2 et S3."""
import numpy as np
from common import E, best_of, A6, PROFILS

rng = np.random.default_rng(5)
a = A6
u = 1 - a
for name, s in PROFILS.items():
    Bm = s @ u
    f = np.linspace(0, 1, 201)
    Es, ni, codes = [], [], []
    xprev = None
    for fk in f:
        x = best_of(a, s, fk * Bm, rng, starts=3, extra=() if xprev is None else (xprev,))
        xprev = x
        Es.append(E(x, a))
        ni.append(int(((x > 1e-6) & (x < u - 1e-6)).sum()))
        codes.append("".join("0" if xi < 1e-6 else ("U" if xi > ui - 1e-6 else "i") for xi, ui in zip(x, u)))
    Es, ni = np.array(Es), np.array(ni)
    print(f"{name} : structure de l'optimum le long de B (0 : borne basse, U : borne haute, i : interieure)")
    for k in range(len(f)):
        if k == 0 or codes[k] != codes[k - 1]:
            print(f"    B/Bmax = {f[k]:.3f}  {codes[k]}")
    d2 = np.diff(Es, 2) / (f[1] * Bm) ** 2
    for n in sorted(set(ni.tolist())):
        idx = [k for k in range(len(d2)) if ni[k] == ni[k + 1] == ni[k + 2] == n]
        if idx:
            print(f"    {n} position(s) interieure(s) : d2 E* dans [{d2[idx].min():.2e}, {d2[idx].max():.2e}]")
    neg = np.where(d2 < -1e-6)[0] + 1
    print("    d2 E* < 0 seulement pres de B/Bmax =", np.round(f[neg], 3))
    # passage par un sommet du pave : les positions interieures changent toutes d'un morceau au suivant
    ints = [{k for k, ch in enumerate(c) if ch == "i"} for c in codes]
    sommets = []
    for k in range(1, len(codes)):
        if codes[k] != codes[k - 1] and ints[k - 1] and ints[k] and not (ints[k - 1] & ints[k]):
            I = [t for t, ch in enumerate(codes[k]) if ch == "U"]
            sommets.append(s[I] @ u[I] / Bm)
    print("    passages par un sommet du pave, en B_I / Bmax :", np.round(sommets, 3))
