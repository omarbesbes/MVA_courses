# -*- coding: utf-8 -*-
"""Construit les deux notebooks du TP 2026 prédit :
  - TP2026_prediction_enonce.ipynb  (questions + cellules vides)
  - TP2026_prediction_corrige.ipynb (corrigé complet, à exécuter)
Usage : python3 build.py   (depuis n'importe où)
"""
import os
import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)

CELLS = []  # (kind, source, role) ; role in {'B' (les deux), 'C' (corrigé), 'E' (énoncé)}


def md(src, role='C'):
    CELLS.append(('md', src.strip('\n'), role))


def code(src, role='C'):
    CELLS.append(('code', src.strip('\n'), role))


# =====================================================================
# EN-TÊTE
# =====================================================================
md(r'''
# TP d'optimisation — sujet 2026 (prédiction)

Ce TP contient 2 parties :

1. Optimisation continue : convexe avec contraintes (Uzawa ou pénalisation) et non convexe (algorithme stochastique)

2. Optimisation discrète : un problème d'affectation utilisant l'algorithme du simplexe et un problème de programmation dynamique

La notation du TP tiendra compte

* de la justification de l'existence et unicité de minima globaux pour chaque problème de minimisation rencontré

* d'une explication préalable à chaque cellule et de commentaires après chaque cellule

* de l'illustration des résultats avec des figures
''', 'B')

md(r'''
> **Comment ce sujet a été prédit.** On part du TP 2025 (énoncé et corrigé), de l'en-tête 2026 et des 4 notebooks fournis
> (`DescenteGradient`, `Uzawa`, `Pénalisation`, `Sac-a-dos`).
>
> | Bloc | TP 2025 | En-tête 2026 | Prédiction |
> |---|---|---|---|
> | Continu, convexe | Newton sans contrainte, puis Newton sur le système KKT (contrainte d'**égalité**) | « convexe avec contraintes (Uzawa ou pénalisation) » | mêmes $A,k,b,f_1,f_2$ ; contrainte d'**inégalité** convexe ; Uzawa + pénalisation |
> | Continu, non convexe | recuit simulé, `basinhopping`, `dual_annealing` | inchangé | idem, avec en plus le recuit codé à la main |
> | Affectation | `linear_sum_assignment`, `linprog`, `milp`, unicité | inchangé | idem |
> | Programmation dynamique | absent | **nouveau** | sac à dos (le notebook fourni) |
>
> Les fonctions sont écrites de façon **générique** (`J, DJ, F, DF`) : si l'énoncé change la fonction ou les contraintes,
> il suffit de remplacer leur définition.
''', 'B')

md(r'''
**Plan de rédaction suivi pour chaque problème** (c'est ce que le barème demande) :

1. **Existence** : fonction continue et coercive sur un fermé, ou ensemble admissible compact (Weierstrass), ou ensemble admissible fini et non vide.
2. **Unicité** : stricte convexité sur un convexe ; sinon on montre qu'elle est fausse, ou on la teste numériquement.
3. **Algorithme** : hypothèses de convergence, choix des paramètres.
4. **Vérification** avec une fonction de `scipy`.
5. **Figure**, puis commentaire.

Chaque cellule de code est précédée d'une explication et suivie d'un commentaire du résultat.
''')

# =====================================================================
# PARTIE 1
# =====================================================================
md(r'''
## Partie 1 — Optimisation continue

### 1.0 Données et fonctions

Soit $A$ une matrice carrée $5\times 5$ et $k,b$ deux vecteurs de $\mathbb{R}^5$. On définit 2 fonctions de $\mathbb{R}^5$ dans $\mathbb{R}$ :

$$f_1(x) = \|x^4\|_1+\vec k\cdot x^3+x\cdot A x - \vec b\cdot x \qquad\text{où } x^n:=(x_1^n,\ldots, x_5^n)$$

$$f_2(x)=f_1(x)+10\,\cos\,(f_1(x))$$
''', 'B')

md(r'''
*Cellule suivante* : import des bibliothèques. `rng` fixe la graine aléatoire, ce qui rend les résultats stochastiques reproductibles.
''')
code(r'''
import numpy as np
import numpy.linalg as nl
import matplotlib.pyplot as plt
import time, itertools, warnings
from scipy import optimize
from scipy.optimize import (minimize, root, basinhopping, dual_annealing, shgo,
                            linprog, milp, LinearConstraint, Bounds,
                            linear_sum_assignment)
warnings.filterwarnings('ignore', category=RuntimeWarning)
plt.rcParams.update({'figure.dpi': 90, 'axes.grid': True, 'grid.alpha': 0.3})
rng = np.random.default_rng(0)   # graine fixée : résultats reproductibles
np.random.seed(0)
''', 'B')

md(r'''
*Cellule suivante* : les données (les valeurs du corrigé 2025 ; il suffit de les modifier si l'énoncé 2026 en change).
''')
code(r'''
k = np.array([1.0, -1.0, 1, -.2, -1])
b = np.array([-1.0, 2.0, -1.5, 2, 1.5])
A = np.array([[ -5, 1, -1, 3, 2],
              [ 1, -5, 1, 1, 2],
              [ 2, 2, -10, 1, -5],
              [ 0, 2, 1, 0, 1],
              [ 1, 3, -2, 0, -2]], dtype=float)
''', 'B')
md(r'''
*Commentaire.* $A$ n'est pas symétrique. Seule sa partie symétrique $\frac{A+A^T}{2}$ intervient dans $x\cdot Ax$, c'est pourquoi $A+A^T$ apparaît dans le gradient et dans la hessienne.
''')

md(r'''
**Question.** Définir $f_1,\ f_2$ (gradients et hessiennes compris) et tracer les graphes $z=f_i(0,\ldots,0,x,0,\ldots,0)$ pour $i=1$ et $2$, où $x$ occupe tour à tour chacune des 5 coordonnées et varie dans $[-4,4]$.
''', 'B')

md(r'''
*Cellule suivante* : définition des fonctions, de leurs gradients et de leurs hessiennes ($\odot$ désigne le produit terme à terme).

$$\nabla f_1(x)=4x^3+3\,k\odot x^2+(A+A^T)x-b,\qquad \nabla^2 f_1(x)=\mathrm{diag}(12x^2+6\,k\odot x)+A+A^T$$

Avec $h(t)=t+10\cos t$, on a $f_2=h\circ f_1$, donc

$$\nabla f_2=h'(f_1)\,\nabla f_1=(1-10\sin f_1)\nabla f_1,\qquad \nabla^2 f_2=(1-10\sin f_1)\,\nabla^2 f_1-10\cos(f_1)\,\nabla f_1\,\nabla f_1^T .$$
''')
code(r'''
def f1(x):
    x = np.asarray(x, dtype=float)
    return np.sum(x**4) + k @ x**3 + x @ A @ x - b @ x

def df1(x):
    x = np.asarray(x, dtype=float)
    return 4*x**3 + 3*k*x**2 + (A + A.T) @ x - b

def Hf1(x):
    x = np.asarray(x, dtype=float)
    return np.diag(12*x**2 + 6*k*x) + A + A.T

def f2(x):
    return f1(x) + 10*np.cos(f1(x))

def df2(x):
    return (1 - 10*np.sin(f1(x))) * df1(x)

def Hf2(x):
    g = df1(x)
    return (1 - 10*np.sin(f1(x))) * Hf1(x) - 10*np.cos(f1(x)) * np.outer(g, g)
''')
md(r'''
*Cellule suivante* : on vérifie ces formules par différences finies centrées. On reprend `grad_h` du notebook `DescenteGradient.ipynb` fourni par l'enseignant. Une erreur dans le gradient est l'erreur la plus fréquente en TP, d'où ce test.
''')
code(r'''
def grad_h(F, x, h=1e-5):
    """Gradient par différences finies centrées (DescenteGradient.ipynb)."""
    x = np.asarray(x, dtype=float)
    e, g = np.zeros(len(x)), np.zeros(len(x))
    for n in range(len(x)):
        e[n] = h
        g[n] = (F(x + e) - F(x - e)) / (2*h)
        e[n] = 0
    return g

def hess_h(dF, x, h=1e-5):
    """Hessienne par différences finies sur le gradient."""
    return np.array([(dF(x + h*e) - dF(x - h*e)) / (2*h) for e in np.eye(len(x))]).T

xt = rng.uniform(-2, 2, 5)
for nom, f, df, Hf in [('f1', f1, df1, Hf1), ('f2', f2, df2, Hf2)]:
    eg = nl.norm(df(xt) - grad_h(f, xt)) / nl.norm(df(xt))
    eH = nl.norm(Hf(xt) - hess_h(df, xt)) / nl.norm(Hf(xt))
    print(f"{nom} : erreur relative gradient = {eg:.1e}, hessienne = {eH:.1e}")
''')
md(r'''
*Commentaire.* Les erreurs relatives sont de l'ordre de $10^{-9}$ ou moins, ce qui est la précision attendue des différences finies centrées. Les gradients et les hessiennes sont donc justes.
''')

md(r'''
*Cellule suivante* : tracé des coupes $x\mapsto f_j(x\,e_i)$, $i=1,\dots,5$ (première ligne $f_1$, deuxième ligne $f_2$).
''')
code(r'''
x_range = np.linspace(-4, 4, 400)
fig, axs = plt.subplots(2, 5, figsize=(18, 6.5), sharex=True)
for i in range(5):
    E = np.zeros((x_range.size, 5)); E[:, i] = x_range
    axs[0, i].plot(x_range, [f1(e) for e in E], color='C0')
    axs[1, i].plot(x_range, [f2(e) for e in E], color='C1')
    axs[0, i].set_title(rf"$f_1(x\,e_{i+1})$")
    axs[1, i].set_title(rf"$f_2(x\,e_{i+1})$")
    axs[1, i].set_xlabel(rf"$x_{i+1}$")
fig.suptitle(r"Coupes $z=f_j(0,\ldots,x,\ldots,0)$ pour $x\in[-4,4]$")
plt.tight_layout(); plt.show()
''')
md(r'''
*Commentaire.*
* Sur chaque axe, $f_1(x e_i)=x^4+k_i x^3+A_{ii}x^2-b_ix$. Le terme $x^4$ domine à l'infini et la fonction tend vers $+\infty$. Comme $A_{ii}\le 0$, on voit un **double puits** sur plusieurs axes (très net pour $x_3$, où $A_{33}=-10$) : $f_1$ a plusieurs minima locaux et **n'est pas convexe**.
* $f_2$ suit la même tendance, avec en plus des oscillations rapides dues à $10\cos(f_1)$ : elle a beaucoup de minima locaux et convient bien pour tester des méthodes stochastiques.
''')

md(r'''
#### Existence et unicité des minima globaux de $f_1$ et $f_2$ sur $\mathbb{R}^5$

**Coercivité de $f_1$.** D'après Cauchy–Schwarz, $\|x\|^4=(\sum x_i^2)^2\le 5\sum x_i^4$. On a aussi $|k\cdot x^3|\le\|k\|_\infty\sum|x_i|^3\le\|k\|_\infty\|x\|^3$, $|x\cdot Ax|\le\|A\|_2\|x\|^2$ et $|b\cdot x|\le\|b\|\,\|x\|$. Donc

$$f_1(x)\ \ge\ \tfrac15\|x\|^4-\|k\|_\infty\|x\|^3-\|A\|_2\|x\|^2-\|b\|\,\|x\|\ \xrightarrow[\|x\|\to\infty]{}\ +\infty .$$

**Existence.** $f_1$ est continue et coercive sur $\mathbb{R}^5$, elle admet donc un minimum global : une suite minimisante est bornée, on en extrait une sous-suite convergente et on passe à la limite par continuité. De plus $f_2\ge f_1-10$, donc $f_2$ est aussi coercive et admet un minimum global.

**Unicité : non garantie.** $\nabla^2 f_1(0)=A+A^T$ a des valeurs propres strictement négatives (cellule suivante), donc $f_1$ n'est **pas convexe** et l'argument de stricte convexité ne s'applique pas. On verra en 1.2 que $f_1$ a plusieurs minima locaux et que le minimum global de $f_2$ est atteint en une **infinité** de points.
''')
code(r'''
vp = nl.eigvalsh(A + A.T)
print("valeurs propres de A + A^T = Hf1(0) :", vp.round(3))
# rayon R au-delà duquel f1 > 0 = f1(0) : les minimiseurs globaux sont dans la boule B(0,R)
nk, nA, nb = np.max(np.abs(k)), nl.norm(A, 2), nl.norm(b)
R = max(np.roots([1/5, -nk, -nA, -nb, 0]).real)
print(f"f1(x) > f1(0) = 0 dès que ||x|| > R = {R:.2f}")
''')
md(r'''
*Commentaire.* Quatre valeurs propres sont négatives, donc $0$ est un point selle de $f_1$ et $f_1$ n'est pas convexe. La borne de coercivité montre que tout minimiseur global de $f_1$ (et de $f_2$, voir 1.2) est dans la boule de rayon $R\approx 11$. Cela justifie le pavé $[-11,11]^5$ que demande `dual_annealing`.
''')

md(r'''
### Boîte à outils : fonctions des notebooks fournis
''', 'B')
md(r'''
*Cellule suivante* : on reprend
* `gradientPasConstant` du notebook `DescenteGradient.ipynb`, modifiée pour **renvoyer l'historique** au lieu de tracer les points dans la boucle ;
* l'algorithme de **Newton** du corrigé 2025, qui résout $J_F(x)\,p=F(x)$ avec `solve` (plus stable et moins coûteux que `inv`) ;
* `nature(H)`, qui classe un point critique d'après les valeurs propres de la hessienne : minimum, maximum, point selle ou dégénéré.
''')
code(r'''
def gradientPasConstant(gradF, x0, tau, tol=1e-6, Niter=1000):
    """Descente de gradient à pas fixe : x_{n+1} = x_n - tau * grad F(x_n)."""
    xn = np.array(x0, dtype=float); L = [xn.copy()]
    for n in range(Niter):
        g = gradF(xn)
        if nl.norm(g) < tol:
            return xn, np.array(L), True
        xn = xn - tau * g
        L.append(xn.copy())
    return xn, np.array(L), False

def Newton(F, JF, x0, prec=1e-10, Niter=100):
    """Newton pour F(x) = 0 : x_{n+1} = x_n - JF(x_n)^{-1} F(x_n)."""
    x = np.array(x0, dtype=float)
    for it in range(1, Niter + 1):
        try:
            p = nl.solve(JF(x), F(x))
        except nl.LinAlgError:
            return x, it, False
        x = x - p
        if not np.all(np.isfinite(x)):
            return x, it, False
        if nl.norm(p) < prec:
            return x, it, True
    return x, Niter, False

def nature(H, rtol=1e-6):
    """Nature d'un point critique d'après le spectre de la hessienne."""
    vp = nl.eigvalsh((H + H.T) / 2)
    if np.min(np.abs(vp)) < rtol * np.max(np.abs(vp)):
        return 'dégénéré', vp
    if np.all(vp > 0):  return 'min local', vp
    if np.all(vp < 0):  return 'max local', vp
    return 'point selle', vp
''')
md(r'''
*Commentaire.* Ces trois fonctions servent dans tout le TP : Newton pour les points critiques, la descente de gradient pour la pénalisation, `nature` pour vérifier qu'un point est bien un minimum.
''')

# ---------------------------------------------------------------------
# 1.1 CONVEXE SOUS CONTRAINTES
# ---------------------------------------------------------------------
md(r'''
### 1.1 Minimisation convexe sous contraintes d'inégalité : Uzawa et pénalisation

On considère le problème
$$(\mathcal P)\qquad \min_{x\in K} J(x),\qquad K=\{x\in\mathbb{R}^n,\ F(x)\le 0\},\quad F=(F_1,\dots,F_m),$$
et son lagrangien $L(x,p)=J(x)+p\cdot F(x)$ pour $p\in\mathbb{R}_+^m$.
''', 'B')

md(r'''
#### Rappels de cours (à citer dans les justifications)

* **Existence** : $J$ continue et coercive, ou $K$ compact, et $K$ fermé non vide.
* **Unicité** : $J$ strictement convexe et $K$ convexe ($K$ est convexe dès que chaque $F_i$ est convexe).
* **Kuhn–Tucker** : si $J$ et les $F_i$ sont convexes et $C^1$, et si les contraintes sont **qualifiées** (condition de **Slater** : il existe $\tilde x$ avec $F_i(\tilde x)<0$ pour chaque $F_i$ non affine ; les contraintes affines sont toujours qualifiées), alors
$$x^* \text{ minimise } J \text{ sur } K\iff \exists\, p^*\in\mathbb{R}_+^m:\ \nabla J(x^*)+\textstyle\sum_i p_i^*\nabla F_i(x^*)=0,\quad F(x^*)\le 0,\quad p_i^*F_i(x^*)=0 .$$
  De façon équivalente, $(x^*,p^*)$ est un **point selle** de $L$.
* **Uzawa** : c'est un gradient projeté **sur le problème dual** $\max_{p\ge 0}\ \mathcal G(p)$, où $\mathcal G(p)=\min_x L(x,p)$ et $\nabla\mathcal G(p)=F(x_p)$ :
$$x_n=\arg\min_x L(x,p_n)\ \ (\text{i.e. }\nabla J(x_n)+DF(x_n)^Tp_n=0),\qquad p_{n+1}=\max\big(0,\ p_n+\mu F(x_n)\big).$$
  **Convergence** (Allaire) : si $J$ est $\alpha$-convexe, c'est-à-dire $\langle\nabla J(x)-\nabla J(y),x-y\rangle\ge\alpha\|x-y\|^2$, et si $F$ est convexe et $M$-lipschitzienne, alors $x_n\to x^*$ pour $0<\mu<2\alpha/M^2$.
* **Pénalisation (extérieure)** :
$$J_\varepsilon(x)=J(x)+\frac1\varepsilon\sum_i\max(0,F_i(x))^2 ,\qquad \nabla J_\varepsilon=\nabla J+\frac2\varepsilon\,DF^T\max(0,F).$$
  $t\mapsto\max(0,t)^2$ est convexe et croissante, donc $J_\varepsilon$ est convexe et $C^1$ dès que $J$ et les $F_i$ le sont. Elle est strictement convexe et coercive si $J$ l'est, d'où un unique minimiseur $x_\varepsilon$, et $x_\varepsilon\to x^*$ quand $\varepsilon\to0$. En pratique $\|x_\varepsilon-x^*\|=O(\varepsilon)$, et $\frac2\varepsilon\max(0,F(x_\varepsilon))\to p^*$ : la pénalisation fournit aussi une estimation des multiplicateurs.

**Convention du code** : `DF(x)` est la **jacobienne** $m\times n$ (ligne $i$ = $\nabla F_i$), donc $\nabla_x L = \nabla J + DF^T p$.
''')

md(r'''
*Cellule suivante* : un **Uzawa générique** (on garde l'historique pour tracer la convergence) et la **fonction pénalisée** $J_\varepsilon$ avec son gradient.
L'étape $x_n=\arg\min_x L(x,p_n)$ est résolue comme dans le notebook fourni, en cherchant le zéro de $\nabla_xL$ avec `optimize.root`, avec un **départ à chaud** au point précédent. Si `root` échoue, ou si l'option `inner='min'` est choisie, on minimise directement $L(\cdot,p_n)$ avec `minimize`. On s'arrête quand $x_n$ et $p_n$ sont tous deux stationnaires.
''')
code(r'''
def Uzawa(J, DJ, F, DF, x0, mu=0.5, tol=1e-8, Niter=2000, inner='root'):
    """Minimise J sous F(x) <= 0. DF = jacobienne m x n de F.
    Renvoie x, p, historiques (x_n), (p_n) et un booléen de convergence."""
    x = np.array(x0, dtype=float)
    p = np.zeros(len(F(x)))
    hx, hp = [x.copy()], [p.copy()]
    for n in range(Niter):
        gradL = lambda y: DJ(y) + DF(y).T @ p
        sol = root(gradL, x) if inner == 'root' else None
        if sol is None or not sol.success:
            sol = minimize(lambda y: J(y) + p @ F(y), x, jac=gradL, method='BFGS')
        x_new = sol.x
        p_new = np.maximum(0, p + mu * F(x_new))          # projection sur R_+^m
        hx.append(x_new.copy()); hp.append(p_new.copy())
        if nl.norm(x_new - x) < tol and nl.norm(p_new - p) < tol:
            return x_new, p_new, np.array(hx), np.array(hp), True
        x, p = x_new, p_new
    return x, p, np.array(hx), np.array(hp), False

def penalise(J, DJ, F, DF, eps):
    """J_eps = J + (1/eps) sum max(0,F_i)^2 et son gradient."""
    Je  = lambda x: J(x) + np.sum(np.maximum(0, F(x))**2) / eps
    dJe = lambda x: DJ(x) + (2/eps) * DF(x).T @ np.maximum(0, F(x))
    return Je, dJe
''')
md(r'''
*Commentaire.* Les deux méthodes ne demandent que $J,\nabla J,F,DF$. Un changement d'énoncé ne touche donc que les définitions.

⚠️ **Bug dans les notebooks fournis** : `Uzawa.ipynb` calcule `DL = DJ(x) + np.dot(DF(x), p)` et `Pénalisation.ipynb` utilise `np.dot(DF(x), e)`, alors que `DF` y est la jacobienne (ligne $i$ = $\nabla F_i$). Il faut **la transposée** : $DF(x)^Tp$. En dimension 2 avec 2 contraintes, les tailles coïncident et Python ne signale aucune erreur, mais le résultat est faux (voir l'exemple 1 bis).
''')

# ---------------- Exemple 1 : 2D -----------------
md(r'''
#### Exemple 1 (dimension 2, pour visualiser)

$$J(x,y)=4x^2+y^2,\qquad F_1(x,y)=1-x-y\le 0,\qquad F_2(x,y)=e^x-y\le 0 .$$

1. Justifier l'existence et l'unicité du minimum.
2. Écrire les conditions de Kuhn–Tucker et en déduire la solution.
3. Appliquer l'algorithme d'Uzawa. Étudier l'influence du pas $\mu$.
4. Appliquer la méthode de pénalisation. Étudier l'influence de $\varepsilon$.
5. Comparer avec `minimize`.
''', 'B')
md(r'''
**1. Existence et unicité.**
* $K$ est **fermé** ($F$ est continue), **convexe** ($F_1$ est affine et $F_2$ est convexe, somme de $e^x$ et d'une fonction linéaire) et **non vide** : $(0,2)\in K$ avec $F_1=-1<0$ et $F_2=-1<0$, donc **Slater** est vérifié.
* $\nabla^2J=\mathrm{diag}(8,2)\succeq 2I$, donc $J$ est $\alpha$-convexe avec $\alpha=2$ : strictement convexe et coercive.
* Il existe donc un **unique** minimiseur, et les conditions KKT sont **nécessaires et suffisantes**.

**2. Solution par KKT.** Le minimum sans contrainte $(0,0)$ viole les deux contraintes. On teste les deux contraintes actives : $x+y=1$ et $y=e^x$ donnent $e^x+x=1$, dont l'unique solution est $x=0$ (la fonction $x\mapsto e^x+x$ est strictement croissante). On obtient $(x^*,y^*)=(0,1)$. En ce point $\nabla J=(0,2)$, $\nabla F_1=(-1,-1)$, $\nabla F_2=(1,-1)$, et
$$\begin{pmatrix}0\\2\end{pmatrix}+p_1\begin{pmatrix}-1\\-1\end{pmatrix}+p_2\begin{pmatrix}1\\-1\end{pmatrix}=0\iff p_1=p_2=1\ \ge 0 .$$
Les conditions KKT sont satisfaites. Comme elles sont suffisantes ici, **$x^*=(0,1)$ est l'unique minimiseur**, avec $J^*=1$ et $p^*=(1,1)$.
''')
md(r'''
*Cellule suivante* : codage de $J$, $\nabla J$, $F$ et de la jacobienne $DF$, puis vérification numérique des conditions KKT en $x^*$.
''')
code(r'''
J1  = lambda x: 4*x[0]**2 + x[1]**2
DJ1 = lambda x: np.array([8*x[0], 2*x[1]])
F1c = lambda x: np.array([1 - x[0] - x[1], np.exp(x[0]) - x[1]])
DF1c = lambda x: np.array([[-1.0, -1.0],
                           [np.exp(x[0]), -1.0]])
x1_star, p1_star = np.array([0.0, 1.0]), np.array([1.0, 1.0])
print("F(x*)              =", F1c(x1_star))
print("grad_x L(x*, p*)   =", DJ1(x1_star) + DF1c(x1_star).T @ p1_star)
''')
md(r'''
*Commentaire.* Les deux contraintes sont actives ($F(x^*)=0$) et le gradient du lagrangien est nul : $(x^*,p^*)$ satisfait bien les conditions KKT. Ce sera la référence pour mesurer l'erreur des algorithmes.
''')

md(r'''
*Cellule suivante* : **Uzawa** depuis $x_0=(0,0)$ avec $\mu=0{,}5$ et $\mu=1$.
''')
code(r'''
for mu in [0.5, 1.0]:
    x, p, hx, hp, ok = Uzawa(J1, DJ1, F1c, DF1c, [0, 0], mu=mu)
    print(f"mu={mu}: convergé={ok}, {len(hx)-1} itérations, x={x.round(8)}, p={p.round(6)}, "
          f"erreur={nl.norm(x - x1_star):.1e}")
''')
md(r'''
*Commentaire.* Uzawa retrouve $x^*=(0,1)$ et $p^*=(1,1)$. Les multiplicateurs calculés coïncident avec ceux obtenus à la main, et le nombre d'itérations dépend fortement de $\mu$.
''')

md(r'''
*Cellule suivante* : **figure**. À gauche, lignes de niveau de $J$, ensemble admissible $K$ (grisé) et trajectoire des itérés $x_n$ d'Uzawa. À droite, l'erreur $\|x_n-x^*\|$ pour plusieurs pas $\mu$.
Prédiction théorique : $\alpha=2$ et, près de la solution, $M\approx\|DF(x^*)\|_2=\sqrt2$, d'où **$\mu<2\alpha/M^2=2$**.
''')
code(r'''
M = nl.norm(DF1c(x1_star), 2)
print(f"alpha = 2, M = ||DF(x*)|| = {M:.3f}  ->  borne théorique mu < {2*2/M**2:.2f}")

fig, ax = plt.subplots(1, 2, figsize=(14, 5.5))
X, Y = np.meshgrid(np.linspace(-1.5, 1.5, 300), np.linspace(-0.5, 2.5, 300))
ax[0].contour(X, Y, 4*X**2 + Y**2, levels=20, cmap='viridis', alpha=.7)
adm = (1 - X - Y <= 0) & (np.exp(X) - Y <= 0)
ax[0].contourf(X, Y, adm, levels=[0.5, 1], colors=['grey'], alpha=.25)
t = np.linspace(-1.5, 1.5, 200)
ax[0].plot(t, 1 - t, 'k--', label=r'$F_1=0$ : $y=1-x$')
ax[0].plot(t, np.exp(t), 'k-', label=r'$F_2=0$ : $y=e^x$')
_, _, hx, _, _ = Uzawa(J1, DJ1, F1c, DF1c, [0, 0], mu=0.5)
ax[0].plot(hx[:, 0], hx[:, 1], 'o-', ms=3, color='C3', label=r'itérés $x_n$ (Uzawa, $\mu=0.5$)')
ax[0].plot(*x1_star, 'r*', ms=18, label=r'$x^*=(0,1)$')
ax[0].set_xlim(-1.5, 1.5); ax[0].set_ylim(-0.5, 2.5); ax[0].set_aspect('equal')
ax[0].set_title("Uzawa : les itérés arrivent par l'extérieur de $K$"); ax[0].legend(fontsize=8, loc='upper left')

for mu, ls in [(0.2, '-'), (0.5, '-'), (1.0, '-'), (1.5, ':'), (1.9, '-'), (2.1, '-')]:
    _, _, hx, _, ok = Uzawa(J1, DJ1, F1c, DF1c, [0, 0], mu=mu, Niter=2000)
    err = np.maximum(nl.norm(hx[:61] - x1_star, axis=1), 1e-16)
    ax[1].semilogy(err, ls=ls, lw=2, label=rf"$\mu={mu}$" + ("" if ok else " : ne converge pas"))
ax[1].set_xlabel("itération $n$"); ax[1].set_ylabel(r"$\|x_n-x^*\|$")
ax[1].set_title(r"Influence du pas $\mu$"); ax[1].legend()
plt.tight_layout(); plt.show()
''')
md(r'''
*Commentaire.*
* Les itérés $x_n$ sont **hors de $K$** au début. Uzawa est une méthode **duale** : $x_n$ minimise $L(\cdot,p_n)$ sans contrainte, et $x_n$ n'est admissible qu'à la limite.
* La convergence est **linéaire**, d'autant plus rapide que $\mu$ s'approche de $1$ ici. Les courbes $\mu=0.5$ et $\mu=1.5$ sont confondues : près de la solution, l'erreur est multipliée à chaque itération par $|1-\mu|$. Pour $\mu=2.1$ la suite **oscille** sans converger, en accord avec la borne théorique $\mu<2\alpha/M^2=2$, qui n'est qu'une condition suffisante.
''')

md(r'''
*Cellule suivante* : **pénalisation**, d'abord avec la descente de gradient à pas fixe du notebook fourni.
La hessienne de $J_\varepsilon$ a une plus grande valeur propre $L_\varepsilon\approx 8+4/\varepsilon$. Le pas doit vérifier $\tau<2/L_\varepsilon$ : il **diminue avec $\varepsilon$**. On prend $\tau=1/L_\varepsilon$.
''')
code(r'''
print(" eps     tau       itérations   ||x_eps - x*||   max F(x_eps)")
for eps in [1e-1, 1e-2, 1e-3]:
    Je, dJe = penalise(J1, DJ1, F1c, DF1c, eps)
    tau = 1.0 / (8 + 4/eps)
    xe, L, ok = gradientPasConstant(dJe, [0, 0], tau, tol=1e-8, Niter=200000)
    print(f"{eps:6.0e}  {tau:.2e}   {len(L)-1:8d}      {nl.norm(xe - x1_star):.2e}      {F1c(xe).max():.2e}")
''')
md(r'''
*Commentaire.* L'erreur $\|x_\varepsilon-x^*\|$ est proportionnelle à $\varepsilon$, et la contrainte est légèrement violée ($\max F>0$), comme toujours avec une pénalisation **extérieure**. Le nombre d'itérations reste ici très faible. C'est un cas particulier : les gradients des **deux** contraintes actives engendrent $\mathbb{R}^2$, donc la hessienne de $J_\varepsilon$ vaut $\approx\frac4\varepsilon I$ et le problème reste bien conditionné. Avec moins de contraintes actives que de variables, le conditionnement se dégrade en $1/\varepsilon$ ; on le voit sur l'exemple 2.
''')

md(r'''
*Cellule suivante* : pénalisation résolue par `minimize` (BFGS) pour $\varepsilon=10^{0},\dots,10^{-6}$, avec **continuation** : chaque problème démarre au minimiseur précédent. On trace l'erreur et l'estimation $\frac2\varepsilon\max(0,F(x_\varepsilon))$ des multiplicateurs.
''')
code(r'''
eps_list = np.logspace(0, -6, 13)
x = np.zeros(2); errs, mults, chemin = [], [], []
for eps in eps_list:
    Je, dJe = penalise(J1, DJ1, F1c, DF1c, eps)
    x = minimize(Je, x, jac=dJe, method='BFGS', options={'gtol': 1e-12}).x   # départ à chaud
    errs.append(nl.norm(x - x1_star)); mults.append(2/eps*np.maximum(0, F1c(x))); chemin.append(x)
mults, chemin = np.array(mults), np.array(chemin)

fig, ax = plt.subplots(1, 3, figsize=(17, 4.8))
ax[0].loglog(eps_list, errs, 'o-', label=r'$\|x_\varepsilon-x^*\|$')
ax[0].loglog(eps_list, eps_list, 'k--', label=r'pente 1 : $O(\varepsilon)$')
ax[0].set_xlabel(r'$\varepsilon$'); ax[0].invert_xaxis(); ax[0].legend(); ax[0].set_title("Erreur de pénalisation")
ax[1].semilogx(eps_list, mults[:, 0], 'o-', label=r'$\frac{2}{\varepsilon}F_1^+(x_\varepsilon)$')
ax[1].semilogx(eps_list, mults[:, 1], 's-', label=r'$\frac{2}{\varepsilon}F_2^+(x_\varepsilon)$')
ax[1].axhline(1, color='k', ls='--', label=r'$p^*=1$'); ax[1].invert_xaxis()
ax[1].set_xlabel(r'$\varepsilon$'); ax[1].legend(); ax[1].set_title("Estimation des multiplicateurs")
t = np.linspace(-0.6, 0.6, 200)
ax[2].plot(t, 1 - t, 'k--', t, np.exp(t), 'k-')
ax[2].plot(chemin[:, 0], chemin[:, 1], 'o-', color='C2', label=r'$x_\varepsilon$, $\varepsilon\downarrow 0$')
ax[2].plot(*x1_star, 'r*', ms=15, label='$x^*$'); ax[2].set_xlim(-.6, .6); ax[2].set_ylim(.3, 1.6)
ax[2].set_title(r"Trajectoire de $x_\varepsilon$ (par l'extérieur)"); ax[2].legend()
plt.tight_layout(); plt.show()
''')
md(r'''
*Commentaire.* L'erreur décroît exactement comme $O(\varepsilon)$ (pente 1 en échelle log-log). Les quantités $\frac2\varepsilon F_i^+(x_\varepsilon)$ tendent vers $p^*=(1,1)$, ce qui recoupe Uzawa et le calcul KKT. Les points $x_\varepsilon$ approchent $x^*$ **depuis l'extérieur** de $K$.
''')

md(r'''
*Cellule suivante* : comparaison avec `minimize(method='SLSQP')`. Attention à la convention : pour SLSQP une contrainte `'ineq'` signifie $g(x)\ge0$, il faut donc passer $-F$.
''')
code(r'''
cons = [{'type': 'ineq', 'fun': lambda x: -F1c(x), 'jac': lambda x: -DF1c(x)}]
t0 = time.time(); r = minimize(J1, [0, 0], jac=DJ1, constraints=cons, method='SLSQP', tol=1e-12); tS = time.time() - t0
t0 = time.time(); xU, pU, hxU, _, _ = Uzawa(J1, DJ1, F1c, DF1c, [0, 0], mu=1.0); tU = time.time() - t0
Je, dJe = penalise(J1, DJ1, F1c, DF1c, 1e-6)
t0 = time.time(); xP = minimize(Je, chemin[-2], jac=dJe, method='BFGS').x; tP = time.time() - t0
print(f"{'méthode':<22}{'x':<28}{'J(x)':<12}{'erreur':<10}temps")
for nom, xx, tt in [('SLSQP', r.x, tS), ('Uzawa (mu=1)', xU, tU), ('Pénalisation 1e-6', xP, tP)]:
    print(f"{nom:<22}{str(xx.round(6)):<28}{J1(xx):<12.6f}{nl.norm(xx - x1_star):<10.1e}{tt:.3f}s")
''')
md(r'''
*Commentaire.* Les trois méthodes donnent le même point $(0,1)$ avec $J^*=1$. SLSQP (programmation quadratique séquentielle) est la plus précise. Uzawa est exact au critère d'arrêt près. La pénalisation garde une erreur $O(\varepsilon)$.
''')

# ---------------- Exemple 1 bis : notebook du prof -----------------
md(r'''
#### Exemple 1 bis : le test du notebook `Uzawa.ipynb` fourni

$$J(x,y)=4x^2+y^2,\qquad F(x,y)=\big(y^{4/3}e^x-1,\ x-y+1\big)\le 0 .$$
''', 'B')
md(r'''
**Existence et unicité.** $K$ est fermé et non vide ($(-0.2,0.8)\in K$), et $J$ est continue et coercive : le minimum **existe**. Attention, $F_1$ n'est **pas convexe** : le déterminant de sa hessienne vaut $-\frac{4}{3}y^{2/3}e^{2x}<0$, donc l'argument « Kuhn–Tucker + convexité » du notebook ne s'applique pas tel quel. On montre l'unicité directement. Le minimiseur de $J$ sur le demi-plan **convexe** $\{y\ge x+1\}\supset K$ s'obtient en minimisant $4x^2+(x+1)^2$, d'où $x=-0.2$ et $y=0.8$. Ce point vérifie $F_1=0.8^{4/3}e^{-0.2}-1\approx-0.39<0$, donc il est dans $K$. Il minimise donc $J$ sur $K$, et c'est l'**unique** minimiseur, puisque c'est l'unique minimiseur sur un ensemble plus grand. Les multiplicateurs sont $p^*=(0,\,1.6)$.

Deux pièges dans le code fourni :
1. `x[1]**(4/3)` renvoie `nan` si $y<0$. On écrit `np.cbrt(y)**4`, qui vaut $|y|^{4/3}$.
2. Le produit `np.dot(DF(x), p)` doit être `DF(x).T @ p` (voir plus haut).

*Cellule suivante* : on compare la version « bug » (jacobienne non transposée) et la version corrigée.
''')
code(r'''
J0  = lambda x: 4*x[0]**2 + x[1]**2
DJ0 = lambda x: np.array([8*x[0], 2*x[1]])
F0  = lambda x: np.array([np.cbrt(x[1])**4 * np.exp(x[0]) - 1, x[0] - x[1] + 1])
DF0 = lambda x: np.array([[np.cbrt(x[1])**4*np.exp(x[0]), 4/3*np.cbrt(x[1])*np.exp(x[0])],
                          [1.0, -1.0]])
DF0_bug = lambda x: DF0(x).T          # reproduit np.dot(DF(x), p) du notebook fourni
x0_star = np.array([-0.2, 0.8])
for nom, D in [('notebook fourni (DF p)', DF0_bug), ('corrigé (DF^T p)', DF0)]:
    x, p, hx, _, ok = Uzawa(J0, DJ0, F0, D, [0, 0], mu=0.2)
    print(f"{nom:<24}: x = {x.round(6)}, p = {p.round(4)}, erreur = {nl.norm(x - x0_star):.1e}")
''')
md(r'''
*Commentaire.* Le code fourni converge vers $(-0.2017,\,0.7983)$, la valeur affichée dans `Uzawa.ipynb`, alors que la vraie solution est $(-0.2,\,0.8)$ : l'erreur de $2\cdot10^{-3}$ vient de la transposée oubliée. Avec $DF^Tp$, on retrouve la solution exacte et $p^*=(0,1.6)$ : seule la contrainte affine est active.
''')

# ---------------- Exemple 2 : 5D -----------------
md(r'''
#### Exemple 2 (données du TP, $\mathbb{R}^5$) : projection sur un convexe

C'est la version **inégalité** de la contrainte du TP 2025. On note
$$U_{ad}=\Big\{x\in\mathbb{R}^5:\ G(x)=x_1^2+x_2^2+x_3^2+x_4^2+x_5^4-1\le 0,\ \ x_1+x_2+x_3+x_4+x_5\le \tfrac12\Big\}$$
et on cherche la projection de $b$ sur $U_{ad}$ :
$$\min_{x\in U_{ad}} J(x)=\tfrac12\|x-b\|^2 .$$

1. Justifier l'existence et l'unicité.
2. Résoudre par Uzawa. Vérifier les conditions KKT.
3. Résoudre par pénalisation.
4. Comparer avec `minimize`.
''', 'B')
md(r'''
**Existence et unicité.** $G$ est convexe (somme des fonctions convexes $x_i^2$ et $x_5^4$) et la seconde contrainte est affine, donc $U_{ad}$ est **convexe** et **fermé**. Il est **borné** ($|x_i|\le1$), donc **compact**. Il est non vide et Slater est vérifié : $G(0)=-1<0$ et $0<\frac12$. $J$ est $1$-convexe ($\nabla^2J=I$). Par le **théorème de projection** sur un convexe fermé non vide, il existe un **unique** minimiseur $x^*=P_{U_{ad}}(b)$, et les conditions KKT sont nécessaires et suffisantes. Enfin $b\notin U_{ad}$ ($G(b)>0$), donc au moins une contrainte est active.

*Remarque.* L'étape d'Uzawa est presque explicite : $\nabla_xL=0$ donne $x_i=\frac{b_i-p_2}{1+2p_1}$ pour $i\le4$, et $x_5$ est l'unique racine réelle de $x_5+4p_1x_5^3=b_5-p_2$ (fonction strictement croissante). Le code générique avec `root` s'applique quand même.

*Cellule suivante* : définitions, Uzawa pour plusieurs $\mu$, et référence SLSQP.
''')
code(r'''
G   = lambda x: np.sum(x[:4]**2) + x[4]**4 - 1
dG  = lambda x: np.array([2*x[0], 2*x[1], 2*x[2], 2*x[3], 4*x[4]**3])
J2  = lambda x: 0.5*np.sum((x - b)**2)
DJ2 = lambda x: x - b
F2c  = lambda x: np.array([G(x), np.sum(x) - 0.5])
DF2c = lambda x: np.vstack([dG(x), np.ones(5)])

cons = [{'type': 'ineq', 'fun': lambda x: -F2c(x), 'jac': lambda x: -DF2c(x)}]
ref = minimize(J2, np.zeros(5), jac=DJ2, constraints=cons, method='SLSQP', tol=1e-14)
x2_star = ref.x
print("G(b) =", G(b).round(3), " -> b n'est pas admissible")
print("SLSQP : x* =", x2_star.round(6), " J* =", round(ref.fun, 6), " F(x*) =", F2c(x2_star).round(8))
res_uz = {}
for mu in [0.1, 0.5, 1.0, 1.5, 2.0]:
    x, p, hx, hp, ok = Uzawa(J2, DJ2, F2c, DF2c, np.zeros(5), mu=mu, Niter=500)
    res_uz[mu] = (hx, hp)
    print(f"Uzawa mu={mu}: convergé={ok}, it={len(hx)-1:4d}, p={p.round(5)}, erreur={nl.norm(x - x2_star):.1e}")
xU, pU = Uzawa(J2, DJ2, F2c, DF2c, np.zeros(5), mu=1.0)[:2]
print("KKT : grad_x L(x*,p*) =", (DJ2(xU) + DF2c(xU).T @ pU).round(10), " ; p_i F_i =", (pU*F2c(xU)).round(10))
print("borne suffisante 2*alpha/M^2 avec M = ||DF(x*)|| :", round(2/nl.norm(DF2c(x2_star), 2)**2, 3))
''')
md(r'''
*Commentaire.*
* Uzawa et SLSQP donnent le même $x^*$. Les **deux contraintes sont actives** ($F(x^*)\approx0$) et les multiplicateurs sont **strictement positifs**, $p^*\approx(1.19,\ 0.38)$. Les conditions KKT (gradient du lagrangien nul, complémentarité $p_iF_i=0$) sont vérifiées à la précision machine.
* La convergence a lieu pour $\mu\le1$ et échoue pour $\mu\ge1.5$. La borne théorique $2\alpha/M^2\approx0.38$ n'est que **suffisante** : en pratique on peut prendre $\mu$ un peu plus grand, mais pas trop.
''')
md(r'''
*Cellule suivante* : **figures**. Convergence d'Uzawa (erreur et multiplicateurs), erreur de la pénalisation en fonction de $\varepsilon$, et comparaison des coordonnées de $b$ et de son projeté.
''')
code(r'''
fig, ax = plt.subplots(1, 4, figsize=(20, 4.6))
for mu, (hx, hp) in res_uz.items():
    ax[0].semilogy(np.maximum(nl.norm(hx - x2_star, axis=1), 1e-16), label=rf"$\mu={mu}$")
ax[0].set_xlim(0, 150); ax[0].set_xlabel('itération'); ax[0].set_title(r"Uzawa : $\|x_n-x^*\|$"); ax[0].legend()
hx, hp = res_uz[0.5]
ax[1].plot(hp[:, 0], label=r'$p_1$ (contrainte $G$)'); ax[1].plot(hp[:, 1], label=r'$p_2$ (contrainte affine)')
ax[1].set_xlim(0, 80); ax[1].set_xlabel('itération'); ax[1].set_title(r"Multiplicateurs ($\mu=0.5$)"); ax[1].legend()
x = np.zeros(5); errs = []
eps_list = np.logspace(0, -6, 13)
for eps in eps_list:
    Je, dJe = penalise(J2, DJ2, F2c, DF2c, eps)
    x = minimize(Je, x, jac=dJe, method='BFGS', options={'gtol': 1e-12}).x
    errs.append(nl.norm(x - x2_star))
ax[2].loglog(eps_list, errs, 'o-', label='pénalisation'); ax[2].loglog(eps_list, eps_list, 'k--', label='pente 1')
ax[2].invert_xaxis(); ax[2].set_xlabel(r'$\varepsilon$'); ax[2].set_title(r"$\|x_\varepsilon-x^*\|$"); ax[2].legend()
idx = np.arange(5)
ax[3].bar(idx - 0.2, b, 0.4, label='$b$'); ax[3].bar(idx + 0.2, x2_star, 0.4, label=r'$x^*=P_{U_{ad}}(b)$')
ax[3].set_xticks(idx, [f'$x_{i+1}$' for i in idx]); ax[3].set_title('Projection de $b$'); ax[3].legend()
plt.tight_layout(); plt.show()
''')
md(r'''
*Commentaire.* On retrouve les mêmes comportements qu'en dimension 2 : convergence linéaire d'Uzawa, d'autant plus rapide que $\mu$ est grand tant qu'on reste sous le seuil de divergence ; erreur $O(\varepsilon)$ pour la pénalisation. La projection ramène $b$, de norme $\approx3.7$, sur le bord de $U_{ad}$ : les composantes sont fortement réduites et leur somme vaut exactement $\frac12$.
''')
md(r'''
*Cellule suivante* : pénalisation résolue par la **descente de gradient à pas fixe** (notebook fourni), avec $\tau=1/L_\varepsilon$ et $L_\varepsilon\approx1+\frac2\varepsilon\|DF(x^*)\|^2$. Ici 2 contraintes seulement sont actives en dimension 5.
''')
code(r'''
LF = nl.norm(DF2c(x2_star), 2)**2
print(" eps     tau        itérations   ||x_eps - x*||")
for eps in [1e-1, 1e-2, 1e-3]:
    Je, dJe = penalise(J2, DJ2, F2c, DF2c, eps)
    tau = 1.0 / (1 + 2*LF/eps)
    xe, L, ok = gradientPasConstant(dJe, np.zeros(5), tau, tol=1e-8, Niter=300000)
    print(f"{eps:6.0e}  {tau:.2e}   {len(L)-1:9d}      {nl.norm(xe - x2_star):.2e}")
''')
md(r'''
*Commentaire.* Le nombre d'itérations est multiplié par $\approx10$ chaque fois que $\varepsilon$ est divisé par 10. La hessienne de $J_\varepsilon$ a des valeurs propres $\approx1$ dans les directions tangentes aux contraintes et $\approx\frac1\varepsilon$ dans les directions normales, donc son conditionnement est en $1/\varepsilon$. C'est la limite pratique de la pénalisation : on ne peut pas prendre $\varepsilon$ arbitrairement petit avec un gradient à pas fixe. D'où la **continuation** (suite de $\varepsilon$ décroissants avec départ à chaud), ou l'utilisation de BFGS ou de Newton.
''')

# ---------------- Variante : f1 sur U_ad -----------------
md(r'''
#### Variante : minimiser $f_1$ (non convexe) sur $U_{ad}^{\le}=\{G\le 0\}$

C'est ce qu'il faut savoir dire si l'énoncé reprend $f_1$ avec la contrainte du TP 2025 sous forme d'inégalité.
* **Existence** : $U_{ad}^{\le}$ est compact ($|x_i|\le1$) et $f_1$ est continue, donc le minimum existe (**Weierstrass**).
* **Unicité** : **non garantie**, car $f_1$ n'est pas convexe. Uzawa n'a plus de garantie de convergence : $L(\cdot,p)$ n'est pas forcément convexe et le point selle peut ne pas exister.

*Cellule suivante* : SLSQP multi-départs, puis Uzawa (étape interne par BFGS) pour plusieurs $\mu$.
''')
code(r'''
consG = [{'type': 'ineq', 'fun': lambda x: -G(x), 'jac': lambda x: -dG(x)}]
loc = {}
for s in range(100):
    x0 = rng.normal(size=5); x0 /= max(1, np.sqrt(G(x0) + 1))
    r = minimize(f1, x0, jac=df1, constraints=consG, method='SLSQP', tol=1e-12)
    if r.success and G(r.x) < 1e-8:
        loc.setdefault(round(r.fun, 4), r.x)
print("minima locaux (valeur : x) trouvés par SLSQP multi-départs :")
for v, x in sorted(loc.items()):
    print(f"  {v:9.4f} : {x.round(4)}")
JG = lambda x: f1(x); FG = lambda x: np.array([G(x)]); DFG = lambda x: dG(x)[None, :]
for mu in [0.5, 1.0, 5.0]:
    x, p, hx, _, ok = Uzawa(JG, df1, FG, DFG, np.zeros(5), mu=mu, Niter=400, inner='min')
    print(f"Uzawa mu={mu}: convergé={ok}, f1={f1(x):.4f}, G={G(x):.1e}, p={p.round(3)}")
''')
md(r'''
*Commentaire.* On trouve **deux** minima locaux sur le bord de $U_{ad}$ (valeurs $\approx-15.71$ et $\approx-12.85$) : il n'y a pas d'argument d'unicité, et le minimum global est le plus bas des deux. Uzawa converge vers le bon point pour certains $\mu$ seulement, ou s'arrête sur un autre point KKT, ou ne converge pas. C'est l'illustration que **la convexité est indispensable** à la théorie d'Uzawa.

⚠️ Le corrigé 2025 compare avec `NonlinearConstraint(cont, 1, 1)` alors que `cont` contient déjà le $-1$. Cela impose $G(x)=1$ au lieu de $G(x)=0$, et c'est pour cela que `trust-constr` y trouvait $-22.29$ sur un mauvais ensemble. Il faut écrire `NonlinearConstraint(cont, 0, 0)`, ou `(-np.inf, 0)` pour l'inégalité.
''')

# ---------------------------------------------------------------------
# 1.2 NON CONVEXE
# ---------------------------------------------------------------------
md(r'''
### 1.2 Algorithme du recuit simulé : recherche du minimum global de fonctions non convexes

Algorithme :

* Soit $x_k$ donné. Choix de $y$ de façon aléatoire dans un voisinage $U_k$ de $x_k$
* Si $f(y)<f(x_k)$ alors $x_{k+1}=y$
* Sinon
    * $x_{k+1}=y$ avec une proba $p=e^{-(f(y)-f(x_k))/T(k)}$
    * $x_{k+1}=x_k$ avec proba $1-p$

La fonction $T$ est décroissante, constante par paliers, et $U_k$ est un voisinage de plus en plus petit.

1. Tester l'algorithme de Newton pour $f_1$ et $f_2$ avec différentes données initiales.
2. Programmer le recuit simulé et l'appliquer à $f_1$ et $f_2$.
3. Chercher le minimum global de $f_1$ et $f_2$ à l'aide de *shgo*, *basinhopping* ou bien *dual_annealing*. Comparer.
''', 'B')
md(r'''
⚠️ L'énoncé 2025 inversait les probabilités (« $x_{k+1}=x_k$ avec proba $e^{-\Delta/T}$ »). Avec cette version, quand $T\to0$, on accepterait **toujours** les dégradations. La règle correcte, dite de **Metropolis**, est celle écrite ci-dessus : on accepte une dégradation $\Delta>0$ avec probabilité $e^{-\Delta/T}$. Cette probabilité tend vers $0$ quand la température baisse.

*Cellule suivante* : **Newton multi-départs** sur $\nabla f_1=0$ depuis 300 points tirés uniformément dans $[-4,4]^5$. On classe les points critiques obtenus avec `nature`.
''')
code(r'''
def multistart_newton(df, Hf, f, N=300, box=4):
    pts = []
    for _ in range(N):
        x, it, ok = Newton(df, Hf, rng.uniform(-box, box, 5), prec=1e-10, Niter=200)
        if ok and nl.norm(df(x)) < 1e-6 and nl.norm(x) < 50:
            pts.append(x)
    crit = {}
    for x in pts:
        key = tuple(np.round(x, 5))
        crit.setdefault(key, [x, 0]); crit[key][1] += 1
    return sorted([(f(x), nature(Hf(x))[0], c, x) for x, c in crit.values()], key=lambda t: t[0])

crit1 = multistart_newton(df1, Hf1, f1)
print(f"{len(crit1)} points critiques distincts de f1 :")
for v, nat, c, x in crit1:
    print(f"  f1 = {v:10.4f}   {nat:<12} trouvé {c:3d} fois   x = {x.round(3)}")
''')
md(r'''
*Commentaire.* Newton cherche un zéro du gradient : il converge vers le point critique le plus « proche » de l'initialisation, qu'il soit minimum, maximum ou point selle. $f_1$ a **plusieurs minima locaux** et beaucoup de points selles, ce qui confirme la non-convexité. Le plus bas des minima, $f_1\approx-139.25$, est le candidat au minimum global. Le résultat dépend entièrement du point de départ, d'où l'intérêt des méthodes stochastiques.
''')
md(r'''
*Cellule suivante* : **figure** des valeurs critiques de $f_1$ trouvées par Newton, colorées selon leur nature. Puis Newton sur $f_2$ : on regarde la nature des points obtenus.
''')
code(r'''
couleurs = {'min local': 'C2', 'point selle': 'C1', 'max local': 'C3', 'dégénéré': 'C7'}
fig, ax = plt.subplots(1, 2, figsize=(15, 4.5))
for v, nat, c, x in crit1:
    ax[0].bar(f"{v:.1f}", c, color=couleurs[nat])
for nat, col in couleurs.items():
    ax[0].bar(0, 0, color=col, label=nat)
ax[0].set_xlabel("valeur critique $f_1(x)$"); ax[0].set_ylabel("nb de départs (sur 300)")
ax[0].set_title("Newton multi-départs sur $f_1$ : bassins d'attraction"); ax[0].legend()
ax[0].tick_params(axis='x', rotation=70)

pts2 = []
for _ in range(150):
    x, it, ok = Newton(df2, Hf2, rng.uniform(-3, 3, 5), prec=1e-9, Niter=200)
    if ok and nl.norm(df2(x)) < 1e-5 and nl.norm(x) < 50:
        pts2.append((f1(x), f2(x), nature(Hf2(x))[0], 1 - 10*np.sin(f1(x))))
t1 = np.array([p[0] for p in pts2]); t2 = np.array([p[1] for p in pts2]); nat2 = [p[2] for p in pts2]
sel = t1 < 60
tt = np.linspace(crit1[0][0], 60, 1500)
ax[1].plot(tt, tt + 10*np.cos(tt), lw=1, label=r'$h(t)=t+10\cos t$')
ax[1].scatter(t1[sel], t2[sel], c=[couleurs[n] for n, s_ in zip(nat2, sel) if s_], s=20, zorder=3,
              label='points critiques de $f_2$ trouvés par Newton')
ax[1].set_xlabel('$t=f_1(x)$'); ax[1].set_ylabel('$f_2(x)$'); ax[1].legend(loc='upper left')
ax[1].set_title("Newton sur $f_2$ : tous sur les paliers $h'(f_1(x))=0$")
plt.tight_layout(); plt.show()
print("nature des points critiques de f2 :", {n: nat2.count(n) for n in set(nat2)})
print("part des points critiques de f2 avec 1 - 10 sin(f1) = 0 :",
      np.mean([abs(p[3]) < 1e-6 for p in pts2]).round(2))
''')
md(r'''
*Commentaire.* À gauche : chaque minimum local de $f_1$ attire une part importante des 300 départs, et le minimum global n'attire qu'environ 20 % d'entre eux. À droite : pour $f_2$, $\nabla f_2=(1-10\sin f_1)\nabla f_1$ s'annule sur des **hypersurfaces entières** $\{\sin f_1=0.1\}$. Newton y converge presque toujours : les points trouvés tombent tous sur les extrema de $h$, minima et maxima confondus, et la hessienne y vaut $-10\cos(f_1)\nabla f_1\nabla f_1^T$ : elle est de rang 1, donc le point est **dégénéré**. Newton n'apporte presque rien pour $f_2$ (le corrigé 2025 classait ces points en « point selle » sans voir qu'ils sont dégénérés).
''')

md(r'''
*Cellule suivante* : **recuit simulé codé à la main**, selon l'algorithme de l'énoncé :
* paliers de température $T_p=T_0\,\alpha^p$, avec `n_iter` itérations par palier ;
* voisinage $U_k$ : un pavé de demi-côté $r_p=\max(r_0\,\alpha^{p/2},r_{\min})$, qui rétrécit avec les paliers ;
* acceptation de Metropolis ; on conserve le meilleur point rencontré, puis on le **polit** par une descente locale (BFGS).
''')
code(r'''
def recuit(f, x0, T0=50., alpha=0.85, n_paliers=60, n_iter=300, r0=2., r_min=1e-2, seed=0):
    g = np.random.default_rng(seed)
    x = np.array(x0, dtype=float); fx = f(x)
    best, fbest = x.copy(), fx
    hist_f, hist_best, hist_T = [], [], []
    for p in range(n_paliers):
        T = T0 * alpha**p                       # température constante par palier, décroissante
        r = max(r0 * alpha**(p/2), r_min)       # voisinage de plus en plus petit
        for _ in range(n_iter):
            y = x + r * g.uniform(-1, 1, x.size)
            fy = f(y); d = fy - fx
            if d < 0 or g.random() < np.exp(-d / T):   # Metropolis
                x, fx = y, fy
                if fx < fbest:
                    best, fbest = x.copy(), fx
            hist_f.append(fx); hist_best.append(fbest); hist_T.append(T)
    poli = minimize(f, best, method='BFGS')
    return poli.x, poli.fun, fbest, (np.array(hist_f), np.array(hist_best), np.array(hist_T))

res_rec = {}
for nom, f in [('f1', f1), ('f2', f2)]:
    res_rec[nom] = [recuit(f, np.zeros(5), seed=s) for s in range(10)]
    vals = [r[1] for r in res_rec[nom]]
    print(f"{nom} : valeurs finales (10 graines) = {np.round(vals, 4)}")
''')
md(r'''
*Commentaire.* Pour $f_1$, toutes les graines aboutissent (après polissage) à $-139.2489$. Pour $f_2$, 9 graines sur 10 trouvent $-145.1385$, mais une reste piégée dans un minimum local ($-138.86$). Le recuit est **stochastique** : on le relance plusieurs fois et on garde le meilleur résultat.
''')
md(r'''
*Cellule suivante* : **figure** de l'évolution d'une exécution du recuit : valeur courante $f(x_k)$, meilleure valeur et température $T(k)$ en paliers.
''')
code(r'''
fig, ax = plt.subplots(1, 2, figsize=(16, 4.8))
for a, nom in zip(ax, ['f1', 'f2']):
    i_best = int(np.argmin([r[1] for r in res_rec[nom]]))
    hf, hb, hT = res_rec[nom][i_best][3]
    a.plot(hf, lw=.5, color='C0', label=r'$f(x_k)$ courant')
    a.plot(hb, lw=2, color='C3', label='meilleur')
    a.set_ylim(hb[-1] - 10, 60); a.set_xlabel('itération $k$'); a.set_title(f"Recuit simulé sur ${nom[0]}_{nom[1]}$")
    a2 = a.twinx(); a2.semilogy(hT, 'k--', lw=1, label='$T(k)$'); a2.set_ylabel('température'); a2.grid(False)
    a.legend(loc='upper right')
plt.tight_layout(); plt.show()
''')
md(r'''
*Commentaire.* Quand la température est élevée, l'algorithme accepte beaucoup de dégradations : $f(x_k)$ fluctue fortement et l'espace est **exploré**. Quand $T$ baisse et que le voisinage rétrécit, les dégradations deviennent rares et la suite se **stabilise** dans un puits, puis descend au fond (phase d'**exploitation**). C'est la phase exploratoire qui permet de sortir des minima locaux.
''')

md(r'''
*Cellule suivante* : méthodes globales de `scipy`.
* `basinhopping` : sauts aléatoires suivis de minimisations locales, avec un critère d'acceptation de Metropolis.
* `dual_annealing` : recuit simulé généralisé avec recherche locale. Il exige un pavé de recherche. La borne de coercivité garantit que $[-11,11]^5$ contient tous les minimiseurs globaux, mais ce pavé est inutilement grand : tous les points critiques trouvés par Newton vérifient $|x_i|\le 3.1$. On prend donc $[-5,5]^5$, ce qui rend la recherche bien plus efficace.
* `shgo` : méthode déterministe par complexes simpliciaux.
''')
code(r'''
bornes = [(-5, 5)] * 5
glob = {}
print(f"{'fonction':<9}{'méthode':<16}{'f*':<14}{'x*':<48}{'temps':<8}nfev")
for nom, f, df in [('f1', f1, df1), ('f2', f2, df2)]:
    for meth in ['basinhopping', 'dual_annealing', 'shgo']:
        t0 = time.time()
        if meth == 'basinhopping':
            r = basinhopping(f, np.zeros(5), niter=300, seed=1, minimizer_kwargs={'jac': df})
        elif meth == 'dual_annealing':
            r = dual_annealing(f, bounds=bornes, seed=1)
        else:
            r = shgo(f, bornes, sampling_method='sobol', n=512, minimizer_kwargs={'jac': df})
        glob[(nom, meth)] = r
        print(f"{nom:<9}{meth:<16}{r.fun:<14.6f}{str(np.round(r.x, 4)):<48}{time.time()-t0:<8.2f}{r.nfev}")
''')
md(r'''
*Commentaire.*
* **$f_1$** : les trois méthodes donnent $f_1^*\approx-139.2489$ au **même point** $x^*\approx(-2.057,\,2.531,\,-3.022,\,1.335,\,-1.835)$, comme Newton multi-départs et le recuit. La hessienne y est définie positive ; c'est donc numériquement le minimum global, et il semble unique. *Remarque :* avec le pavé $[-11,11]^5$, `dual_annealing` et `shgo` s'arrêtent parfois sur les minima locaux $-107.8$ ou $-132.3$. Aucune méthode stochastique n'est **garantie** : on relance avec plusieurs graines et on recoupe les méthodes.
* **$f_2$** : `basinhopping` et `dual_annealing` atteignent $-145.1385$ en des points $x$ **différents**. Ce n'est pas une imprécision : c'est expliqué ci-dessous. `shgo`, déterministe, échantillonne puis minimise localement ; il est mal adapté aux oscillations très rapides de $f_2$ et reste bloqué dans un minimum local.
''')
md(r'''
#### Analyse exacte du minimum global de $f_2$ (non-unicité)

On a $f_2=h\circ f_1$ avec $h(t)=t+10\cos t$. Comme $f_1$ est continue sur $\mathbb{R}^5$ (connexe) et coercive, $f_1(\mathbb{R}^5)=[m_1,+\infty[$ avec $m_1=\min f_1$, et donc
$$\min_{\mathbb{R}^5} f_2=\min_{t\ge m_1}h(t).$$
On a $h'(t)=1-10\sin t$, et les minima locaux de $h$ sont $t_j=\pi-\arcsin(0.1)+2j\pi$, où $h(t_j)=t_j-\sqrt{99}$. Le minimum vaut $f_2^*=h(t^*)$, où $t^*$ est le plus petit $t_j\ge m_1$ (sauf si $h(m_1)$ est plus petit).

**Conséquence** : l'ensemble des minimiseurs globaux de $f_2$ est la **ligne de niveau** $\{x:\ f_1(x)=t^*\}$. Elle contient une infinité de points : le long de toute demi-droite issue de $x^*_1$, $f_1$ passe continûment de $m_1<t^*$ à $+\infty$, et prend donc la valeur $t^*$ (théorème des valeurs intermédiaires). **Le minimum global de $f_2$ existe mais n'est pas unique.** Ses minima locaux « parasites » sont les lignes de niveau $\{f_1=t_j\}$ pour $j$ plus grand.

*Cellule suivante* : vérification numérique et figure de $h$.
''')
code(r'''
m1 = min(glob[('f1', m)].fun for m in ['basinhopping', 'dual_annealing', 'shgo'])
h = lambda t: t + 10*np.cos(t)
tj = np.pi - np.arcsin(0.1) + 2*np.pi*np.arange(-40, 40)
tj = tj[tj >= m1]
t_star = tj[0]
f2_star = min(h(t_star), h(m1))
print(f"m1 = min f1 = {m1:.6f} ; t* = {t_star:.6f} ; f2* prédit = {f2_star:.6f} (h(m1) = {h(m1):.3f})")
for meth in ['basinhopping', 'dual_annealing', 'shgo']:
    r = glob[('f2', meth)]
    print(f"{meth:<15}: f2 = {r.fun:.6f}, f1(x) = {f1(r.x):.6f}, x = {r.x.round(3)}")
print("écart entre les deux minimiseurs trouvés :",
      round(nl.norm(glob[('f2', 'basinhopping')].x - glob[('f2', 'dual_annealing')].x), 3))

tt = np.linspace(m1, m1 + 40, 2000)
plt.figure(figsize=(11, 4.5))
plt.plot(tt, h(tt), label=r'$h(t)=t+10\cos t$')
plt.axvline(m1, color='k', ls=':', label=r'$m_1=\min f_1$')
plt.plot(tj[:6], h(tj[:6]), 'o', color='C1', label=r'minima locaux $t_j$ de $h$')
plt.plot(t_star, f2_star, 'r*', ms=16, label=rf'minimum global : $f_2^*={f2_star:.4f}$')
vals_rec = [r[1] for r in res_rec['f2']]
plt.plot([f1(r[0]) for r in res_rec['f2']], vals_rec, 'kx', ms=9, label='résultats du recuit (10 graines)')
plt.xlabel('$t=f_1(x)$'); plt.ylabel('$f_2=h(t)$'); plt.legend(); plt.title(r'$f_2=h\circ f_1$ : $\min\ f_2=\min_{t\geq m_1}\ h(t)$')
plt.show()
''')
md(r'''
*Commentaire.* La valeur prédite par l'analyse ($-145.13853$) est exactement celle trouvée par `basinhopping` et `dual_annealing`, et en chacun des points trouvés on a $f_1(x)=t^*\approx-135.1887$, bien que les $x$ diffèrent nettement. Les échecs du recuit tombent exactement sur les minima locaux suivants de $h$ ($t_{j+1}$, etc.). Conclusion : **$f_2$ a un minimum global, atteint sur toute une hypersurface** ; **$f_1$ a un minimum global**, et toutes les méthodes trouvent le même point, ce qui laisse penser qu'il est unique, sans que la convexité permette de le démontrer.
''')

# =====================================================================
# PARTIE 2
# =====================================================================
md(r'''
## Partie 2 — Optimisation discrète

### 2.1 Programmation linéaire entière : problème d'affectation

On souhaite ranger N objets éparpillés sur le sol dans N boîtes sur le sol.

Les boîtes sont **alignées** selon l'axe des x et sont ordonnées de gauche à droite (si $i < i'$, la boîte $i$ est à gauche de la boîte $i'$). La boîte $i$ est centrée sur un point $B_i$ situé sur l'axe des abscisses.
De même l'objet n°$j$ est repéré par le point $O_j$ du plan $(x, y)$. Les objets doivent être rangés de manière à :

* n'avoir qu'un seul objet par boîte,
* ce que tous les objets soient rangés,
* minimiser la distance totale de déplacement, somme des distances nécessaires pour ranger chaque objet.

Pour ranger l'objet n°$j$ dans la boîte n°$i$, la distance nécessaire est $\|O_j - B_i\|$ (distance euclidienne).

Une solution est une matrice binaire $x\in\mathcal{M}_{n}(\{0,1\})$ telle que $x_{i,j} = 1$ si l'objet $j$ est dans la boîte $i$, 0 sinon.

1. Proposer la mise en œuvre la plus simple à l'aide d'une fonction de la librairie optimize et résoudre le problème pour l'exemple donné dans les fichiers de données.
''', 'B')
md(r'''
*Cellule suivante* : lecture des données. Les fichiers de l'examen ne sont pas disponibles ici. `PositionObjets.txt` et `PositionCasiers.txt` ont été **reconstruits** à partir de la figure du corrigé 2025 (précision $\approx10^{-2}$) : 15 casiers régulièrement espacés sur $[-0.5,0.5]\times\{0\}$ et 15 objets. Le jour J, il suffit de changer les noms de fichiers. Si un fichier est absent, on utilise les coordonnées intégrées.
''')
code(r'''
import os
import pandas as pd

def lire(nom, defaut):
    if os.path.exists(nom):
        return pd.read_csv(nom, sep='\t').values.astype(float)
    print(f"{nom} absent : données intégrées utilisées")
    return defaut

O_def = np.array([[0.093,-0.26],[-0.85,-0.273],[0.873,-1.673],[-0.443,-1.877],[-0.433,0.573],
                  [-1.1,-0.867],[0.867,-0.617],[0.40,-2.117],[-0.967,-0.973],[0.167,0.21],
                  [-1.97,0.48],[-0.74,0.10],[-0.557,0.293],[-0.557,-0.30],[1.117,-1.623]])
B_def = np.c_[-0.5 + np.arange(15)/14, np.zeros(15)]
PositionObjets  = lire('PositionObjets.txt', O_def)
PositionCasiers = lire('PositionCasiers.txt', B_def)
n = PositionCasiers.shape[0]
print("n =", n, "; casiers triés de gauche à droite :", np.all(np.diff(PositionCasiers[:, 0]) > 0))
''', 'B')
md(r'''
*Commentaire.* Il y a $n=15$ casiers, numérotés de gauche à droite. C'est indispensable pour que « juste à gauche » corresponde à « indice $i-1$ ».
''')

md(r'''
**Existence.** L'ensemble admissible est l'ensemble des **matrices de permutation** $n\times n$. Il est **fini** ($n!\approx1.3\cdot10^{12}$ éléments pour $n=15$, donc pas d'énumération possible) et non vide. Le minimum existe donc. **Unicité** : rien ne la garantit a priori (des distances égales peuvent créer des ex æquo), on la testera à la question 4.

**Mise en œuvre la plus simple** : `linear_sum_assignment`, l'algorithme hongrois en $O(n^3)$, appliqué à la matrice des coûts $D_{ij}=\|O_j-B_i\|$.

*Cellule suivante* : matrice des distances et résolution.
''')
code(r'''
# D[i, j] = distance entre la boîte i et l'objet j
D = np.sqrt(((PositionCasiers[:, None, :] - PositionObjets[None, :, :])**2).sum(axis=2))
row, col = linear_sum_assignment(D)            # boîte row[t] <- objet col[t]
X_lsa = np.zeros((n, n)); X_lsa[row, col] = 1
cout_lsa = D[row, col].sum()
print("distance totale minimale :", round(cout_lsa, 6))
print("boîte de chaque objet    :", np.argmax(X_lsa, axis=0) + 1)
''')
md(r'''
*Commentaire.* Le coût optimal sans contrainte supplémentaire est $\approx15.40$. `np.argmax(X, axis=0)` donne, pour chaque objet (colonne), le numéro de sa boîte (ligne).
''')
md(r'''
*Cellule suivante* : **figure**. Les casiers sont en bleu, les objets en rouge, et un trait relie chaque objet à sa boîte. L'axe $x$ est dilaté d'un facteur 3 pour séparer les casiers, comme dans le corrigé 2025. La fonction sera réutilisée.
''')
code(r'''
def trace_affectation(X, titre, ax=None, surligne=()):
    ax = ax or plt.figure(figsize=(14, 5)).gca()
    boite = np.argmax(X, axis=0)
    s = 3                                                         # dilatation de l'axe x
    ax.scatter(s*PositionCasiers[:, 0], PositionCasiers[:, 1], s=90, label='casiers', zorder=3)
    ax.scatter(s*PositionObjets[:, 0], PositionObjets[:, 1], s=90, color='red', label='objets', zorder=3)
    for j in range(n):
        i = boite[j]
        lw = 3 if j in surligne else 1.2
        ax.plot([s*PositionObjets[j, 0], s*PositionCasiers[i, 0]], [PositionObjets[j, 1], PositionCasiers[i, 1]], lw=lw)
        ax.annotate(j + 1, (s*PositionObjets[j, 0] - .15, PositionObjets[j, 1] - .2))
    for i in range(n):
        ax.annotate(i + 1, (s*PositionCasiers[i, 0] - .05, .12), color='C0', fontsize=8)
    ax.set_title(titre); ax.legend(loc='lower left'); ax.margins(y=0.12)
    return ax

trace_affectation(X_lsa, f"Affectation optimale (linear_sum_assignment) : coût = {cout_lsa:.4f}")
plt.show()
''')
md(r'''
*Commentaire.* Les objets proches de l'axe vont dans les casiers les plus proches. Les objets lointains (11, 4, 8, 3, 15) sont affectés de façon à éviter des croisements coûteux. Les traits ne se croisent presque pas, ce qui est typique d'une affectation de coût minimal.
''')

md(r'''
**Formulation en programme linéaire et lien avec le simplexe.**
$$\min\ \sum_{i,j}D_{ij}x_{ij}\quad\text{s.c.}\quad \sum_j x_{ij}=1\ (\forall i),\quad \sum_i x_{ij}=1\ (\forall j),\quad x_{ij}\ge 0 .$$
La matrice des contraintes est la matrice d'incidence d'un graphe **biparti**, elle est donc **totalement unimodulaire**. Le polytope (de Birkhoff) a pour sommets exactement les matrices de permutation (Birkhoff–von Neumann). Le simplexe renvoie un sommet optimal, donc **entier** : la relaxation continue suffit.

*Cellule suivante* : construction de $A_{eq}$ en vectorisant $x$ (`reshape` ligne par ligne : $x_{ij}\to$ indice $i\,n+j$) et résolution par le **simplexe dual** (`method='highs-ds'`).
⚠️ `method='simplex'` et `'revised simplex'` sont obsolètes depuis SciPy 1.9 et peuvent avoir disparu selon la version installée. `'highs-ds'` est le simplexe de HiGHS.
''')
code(r'''
def ligne(M):
    """Transforme une matrice de coefficients m_ij en une ligne de contrainte (vecteur n^2)."""
    return M.reshape(1, n*n)

def contraintes_affectation():
    Aeq, beq = [], []
    for j in range(n):                     # objet j dans une et une seule boîte
        M = np.zeros((n, n)); M[:, j] = 1; Aeq.append(ligne(M)); beq.append(1)
    for i in range(n):                     # boîte i contient un et un seul objet
        M = np.zeros((n, n)); M[i, :] = 1; Aeq.append(ligne(M)); beq.append(1)
    return np.concatenate(Aeq, axis=0), np.array(beq, dtype=float)

Aeq0, beq0 = contraintes_affectation()
c = D.reshape(n*n)
sol = linprog(c, A_eq=Aeq0, b_eq=beq0, bounds=(0, 1), method='highs-ds')
X_lp = sol.x.reshape(n, n)
print("coût simplexe :", round(sol.fun, 6), "| coût hongrois :", round(cout_lsa, 6))
print("écart à l'intégralité max |x - round(x)| :", np.abs(X_lp - X_lp.round()).max())
print("rang de Aeq :", nl.matrix_rank(Aeq0), "sur", Aeq0.shape[0], "lignes")
''')
md(r'''
*Commentaire.* Le simplexe donne le même coût que l'algorithme hongrois, et une solution **entière** sans l'avoir imposée, comme le prévoit la totale unimodularité. Le rang vaut $2n-1$ et non $2n$ : une contrainte est redondante, car la somme des lignes « objets » égale la somme des lignes « boîtes ».
''')

md(r'''
2. On veut à présent rajouter la contrainte suivante : l'objet n°1 doit se situer dans la boîte située juste à gauche de la boîte contenant l'objet n°2. On formule le problème comme un programme linéaire en nombres entiers.

a) Comment traduire mathématiquement que la boîte $i$ contient un objet et un seul et que l'objet $j$ se trouve dans une boîte et une seule ?

b) Traduire mathématiquement la nouvelle contrainte de proximité des objets 1 et 2.

c) Implémenter le programme linéaire à l'aide de `scipy.optimize.linprog`. Attention : le coût et $x$ doivent être codés comme des vecteurs et non des matrices.
''', 'B')
md(r'''
**a)** Boîte $i$ : $\sum_j x_{ij}=1$. Objet $j$ : $\sum_i x_{ij}=1$.

**b)** « L'objet 1 est dans la boîte $i$ $\iff$ l'objet 2 est dans la boîte $i+1$ », c'est-à-dire
$$x_{i,1}=x_{i+1,2}\quad (i=1,\dots,n-1),\qquad x_{n,1}=0 .$$
⚠️ Le corrigé 2025 oublie $x_{n,1}=0$. Sans cette contrainte, la solution « objet 1 dans la **dernière** boîte et objet 2 dans la **première** » est admissible : en sommant les égalités, on obtient seulement $x_{n,1}=x_{1,2}$. Ici cela ne change pas l'optimum, mais la formulation est fausse.

*Cellule suivante* : ajout de ces $n$ égalités et résolution par le simplexe.
''')
code(r'''
Aeq_12, beq_12 = [Aeq0], [beq0]
for i in range(n - 1):
    M = np.zeros((n, n)); M[i, 0] = 1; M[i + 1, 1] = -1        # x_{i,1} - x_{i+1,2} = 0
    Aeq_12.append(ligne(M)); beq_12.append([0.])
M = np.zeros((n, n)); M[n - 1, 0] = 1                          # x_{n,1} = 0
Aeq_12.append(ligne(M)); beq_12.append([0.])
Aeq_12, beq_12 = np.concatenate(Aeq_12, axis=0), np.concatenate(beq_12)

sol2 = linprog(c, A_eq=Aeq_12, b_eq=beq_12, bounds=(0, 1), method='highs-ds')
X2 = sol2.x.reshape(n, n); boite2 = np.argmax(X2, axis=0)
print("distance minimale :", round(sol2.fun, 6), f"(+{sol2.fun - cout_lsa:.4f} par rapport à Q1)")
print("écart à l'intégralité :", np.abs(X2 - X2.round()).max())
print("boîte de l'objet 1 :", boite2[0] + 1, "; boîte de l'objet 2 :", boite2[1] + 1)
''')
md(r'''
*Commentaire.* La contrainte coûte un peu de distance supplémentaire et elle est bien respectée (objet 1 dans la boîte $i$, objet 2 dans la boîte $i+1$). La solution est encore **entière** sur cet exemple. Les contraintes ajoutées détruisent pourtant en général la totale unimodularité : rien ne garantit l'intégralité, il faut toujours la **vérifier**.
''')
code(r'''
fig, ax = plt.subplots(1, 2, figsize=(17, 5), gridspec_kw={'width_ratios': [1, 2.6]})
ax[0].imshow(X2, cmap='Blues'); ax[0].set_xlabel('objet $j$'); ax[0].set_ylabel('boîte $i$')
ax[0].set_xticks(range(n), range(1, n + 1)); ax[0].set_yticks(range(n), range(1, n + 1))
ax[0].set_title('matrice $x_{ij}$ (Q2)')
trace_affectation(X2, f"Q2 : objet 1 juste à gauche de l'objet 2 — coût {sol2.fun:.4f}", ax=ax[1], surligne=(0, 1))
plt.tight_layout(); plt.show()
''')
md(r'''
*Commentaire.* La matrice $x$ est une matrice de permutation (un seul 1 par ligne et par colonne). Sur la figure, les traits épais des objets 1 et 2 aboutissent à deux casiers **voisins**, celui de l'objet 1 à gauche.
''')

md(r'''
3. Proposer une modélisation pour traduire la contrainte que la boîte contenant l'objet n°7 se situe à côté de la boîte contenant l'objet n°5. Modifier le programme pour intégrer cette contrainte supplémentaire.
''', 'B')
md(r'''
« À côté » signifie que les indices des boîtes diffèrent de 1. Deux modélisations linéaires sont possibles :

* **(F1)**, celle du corrigé 2025 : si 7 est dans la boîte $i$, alors 5 n'est dans aucune boîte $j$ avec $|j-i|>1$ :
  $$x_{i,7}+\sum_{|j-i|>1}x_{j,5}\le 1\qquad\forall i .$$
* **(F2)**, plus serrée : $x_{i,7}\le x_{i-1,5}+x_{i+1,5}$ pour tout $i$ (avec $x_{0,5}=x_{n+1,5}=0$).

Les deux sont exactes sur les points **entiers**. (F2) donne une relaxation continue plus proche de l'enveloppe convexe.

*Cellule suivante* : résolution de la relaxation par le simplexe, puis par `milp` (branch and bound) avec la contrainte d'intégrité.
''')
code(r'''
def contrainte_7_5(forme):
    Aub = []
    for i in range(n):
        M = np.zeros((n, n))
        if forme == 'F1':
            M[i, 6] = 1
            for j in range(n):
                if abs(i - j) > 1: M[j, 4] = 1
        else:                                   # F2 : x_{i,7} - x_{i-1,5} - x_{i+1,5} <= 0
            M[i, 6] = 1
            if i > 0: M[i - 1, 4] = -1
            if i < n - 1: M[i + 1, 4] = -1
        Aub.append(ligne(M))
    return np.concatenate(Aub, axis=0), (np.ones(n) if forme == 'F1' else np.zeros(n))

res_q3 = {}
for forme in ['F1', 'F2']:
    Aub, bub = contrainte_7_5(forme)
    lp = linprog(c, A_eq=Aeq_12, b_eq=beq_12, A_ub=Aub, b_ub=bub, bounds=(0, 1), method='highs-ds')
    Aall = np.concatenate([Aeq_12, Aub]); lb = np.r_[beq_12, -np.inf*np.ones(n)]; ub = np.r_[beq_12, bub]
    mi = milp(c, constraints=LinearConstraint(Aall, lb, ub), integrality=np.ones(n*n), bounds=Bounds(0, 1))
    res_q3[forme] = (lp, mi)
    print(f"{forme} : relaxation LP = {lp.fun:.6f} (max partie fractionnaire {np.abs(lp.x - lp.x.round()).max():.3f})"
          f" | MILP = {mi.fun:.6f}")
X3 = res_q3['F1'][1].x.reshape(n, n).round(); b3 = np.argmax(X3, axis=0)
print("boîtes : objet 5 ->", b3[4] + 1, ", objet 7 ->", b3[6] + 1, "| objet 1 ->", b3[0] + 1, ", objet 2 ->", b3[1] + 1)
''')
md(r'''
*Commentaire.*
* Avec (F1), le simplexe renvoie des valeurs **non entières** (des tiers) : la matrice des contraintes n'est plus totalement unimodulaire, et la relaxation donne seulement une **borne inférieure** du coût entier.
* `milp` impose l'intégrité et donne la vraie solution, identique pour (F1) et (F2). La relaxation de (F2) est plus serrée (borne plus haute, plus proche du coût entier).
* Les contraintes sont respectées : 5 et 7 sont dans des boîtes voisines, 1 est juste à gauche de 2.
''')
code(r'''
lp1 = res_q3['F1'][0].x.reshape(n, n)
fig, ax = plt.subplots(1, 3, figsize=(20, 5), gridspec_kw={'width_ratios': [1, 1, 2.4]})
for a, M, t in [(ax[0], lp1, 'relaxation LP (F1) : non entière'), (ax[1], X3, 'MILP : entière')]:
    im = a.imshow(M, cmap='Blues', vmin=0, vmax=1); a.set_title(t)
    a.set_xticks(range(n), range(1, n + 1), fontsize=7); a.set_yticks(range(n), range(1, n + 1), fontsize=7)
plt.colorbar(im, ax=ax[1], fraction=.046)
trace_affectation(X3, f"Q3 : + objets 5 et 7 voisins — coût {res_q3['F1'][1].fun:.4f}", ax=ax[2], surligne=(0, 1, 4, 6))
plt.tight_layout(); plt.show()
''')
md(r'''
*Commentaire.* À gauche, les cases à $1/3$ montrent que la relaxation « mélange » plusieurs affectations. Au milieu, `milp` renvoie une matrice de permutation. À droite, les traits épais vérifient visuellement les deux contraintes. Le coût augmente encore légèrement : chaque contrainte réduit l'ensemble admissible, donc le minimum ne peut que croître.
''')

md(r'''
4. On aimerait vérifier que la solution obtenue est la seule solution optimale. Proposer une stratégie pour le vérifier et conclure quant à l'unicité de la solution.
''', 'B')
md(r'''
**Stratégie.** Soit $x^*$ une solution optimale entière. Pour une matrice de permutation $y$, $\sum_{ij}x^*_{ij}y_{ij}$ compte les affectations communes à $x^*$ et $y$. Cette quantité vaut $n$ si et seulement si $y=x^*$. On ajoute donc la coupe
$$\sum_{i,j}x^*_{ij}\,y_{ij}\le n-1 ,$$
qui exclut **exactement** $x^*$, et on résout à nouveau par `milp`. Si le nouvel optimum est **strictement** plus grand, $x^*$ est l'**unique** solution optimale. S'il est égal, il existe une autre solution optimale.

*Cellule suivante* : test pour les trois problèmes (Q1, Q2, Q3).
''')
code(r'''
def deuxieme_meilleur(Aeq, beq, Aub, bub, Xstar):
    A_ = [Aeq, ligne(Xstar)] + ([Aub] if Aub is not None else [])
    lb = [beq, [-np.inf]] + ([-np.inf*np.ones(len(bub))] if Aub is not None else [])
    ub = [beq, [n - 1]] + ([bub] if Aub is not None else [])
    r = milp(c, constraints=LinearConstraint(np.concatenate(A_), np.concatenate(lb), np.concatenate(ub)),
             integrality=np.ones(n*n), bounds=Bounds(0, 1))
    return r.fun, r.x.reshape(n, n).round()

Aub3, bub3 = contrainte_7_5('F1')
cas = [('Q1', Aeq0, beq0, None, None, X_lsa, cout_lsa),
       ('Q2', Aeq_12, beq_12, None, None, X2.round(), sol2.fun),
       ('Q3', Aeq_12, beq_12, Aub3, bub3, X3, res_q3['F1'][1].fun)]
ecarts = []
for nom, Aeq, beq, Aub, bub, Xs, v in cas:
    v2, X2nd = deuxieme_meilleur(Aeq, beq, Aub, bub, Xs)
    ecarts.append(v2 - v)
    print(f"{nom} : optimum = {v:.6f}, meilleur autre = {v2:.6f}, écart = {v2 - v:.2e}, "
          f"objets déplacés = {int(n - (Xs*X2nd).sum())}  ->  {'UNIQUE' if v2 - v > 1e-9 else 'NON unique'}")
plt.figure(figsize=(6, 3.5)); plt.bar(['Q1', 'Q2', 'Q3'], ecarts, color='C2')
plt.ylabel('2e meilleur coût − optimum'); plt.title("Test d'unicité par coupe"); plt.show()
''')
md(r'''
*Commentaire.* Pour chaque question, le meilleur coût **en dehors** de $x^*$ est strictement supérieur à l'optimum : **la solution optimale est unique**. L'écart est faible : la deuxième meilleure solution s'obtient en échangeant seulement 2 objets, ce qui est typique quand des distances sont presque égales. Cela explique aussi pourquoi les fichiers reconstruits, à $10^{-2}$ près, donnent la même affectation que le corrigé 2025 à un échange près.
''')

# ---------------------------------------------------------------------
# 2.2 PROGRAMMATION DYNAMIQUE
# ---------------------------------------------------------------------
md(r'''
### 2.2 Programmation dynamique : le problème du sac à dos

Étant donné la capacité $W$ d'un sac et des objets de valeurs $v_i$ et de poids $w_i$ (entiers), on cherche la valeur maximale des objets que l'on peut mettre dans le sac sans dépasser la capacité.

Exemple : capacité = 5, objets (valeur, poids) = [(60, 5), (50, 3), (70, 4), (30, 2)], résultat = 80 (les objets de valeurs 50 et 30 tiennent ensemble).

1. Formuler le problème comme un problème d'optimisation en nombres entiers. Justifier l'existence d'une solution. Est-elle unique ?
2. Écrire l'équation de programmation dynamique (Bellman). Programmer l'algorithme et **retrouver les objets choisis**.
3. Vérifier le résultat (force brute pour $n$ petit, `milp`). Comparer avec la relaxation continue (`linprog`).
4. Étudier la complexité.
5. Proposer un moyen de vérifier l'unicité de la solution optimale.
''', 'B')
md(r'''
**1. Formulation.**
$$\max_{x\in\{0,1\}^n}\ \sum_i v_ix_i\quad\text{s.c.}\quad\sum_i w_ix_i\le W .$$
**Existence** : l'ensemble admissible est **fini** (au plus $2^n$ éléments) et **non vide** ($x=0$), donc le maximum existe. **Unicité** : non en général (deux objets identiques, ou deux sous-ensembles de même valeur). On la teste à la question 5.

**2. Principe d'optimalité de Bellman.** Soit $V(i,c)$ la valeur maximale avec les objets $1..i$ et une capacité $c$. Une solution optimale de $(i,c)$ contient l'objet $i$ ou non. Dans les deux cas, le reste est une solution optimale du sous-problème correspondant :
$$V(0,c)=0,\qquad V(i,c)=\begin{cases}V(i-1,c)&\text{si }w_i>c\\ \max\big(V(i-1,c),\ v_i+V(i-1,c-w_i)\big)&\text{sinon}\end{cases}$$
La réponse est $V(n,W)$. On retrouve les objets en **remontant** la table : l'objet $i$ est pris si et seulement si $V(i,c)\ne V(i-1,c)$.

*Cellule suivante* : le code fourni par l'enseignant (`Sac-a-dos.ipynb`), tel quel.
''')
code(r'''
class Item(object):

    def __init__(self, value, weight):
        self.value = value
        self.weight = weight


def get_maximum_value(items, capacity):
    dp = [0] * (capacity + 1)
    for item in items:
        dp_tmp = [total_value for total_value in dp]
        for current_weight in range(capacity + 1):
            total_weight = current_weight + item.weight
            if total_weight <= capacity:
                dp_tmp[total_weight] = max(dp_tmp[total_weight],
                                           dp[current_weight] + item.value)
        dp = dp_tmp
    return max(dp)


print(get_maximum_value([Item(60, 10), Item(100, 20), Item(120, 30)], 50))
print(get_maximum_value([Item(60, 5), Item(50, 3), Item(70, 4), Item(30, 2)], 5))
''', 'B')
md(r'''
*Commentaire sur le code fourni.* `dp` est initialisé à 0 partout, donc après le traitement des $i$ premiers objets, `dp[c]` vaut exactement $V(i,c)$ : la meilleure valeur pour une capacité $c$. La mise à jour `dp_tmp[c] = max(dp_tmp[c], dp[c-w] + v)` est l'équation de Bellman, et le `max(dp)` final vaut simplement `dp[capacity]`. La copie `dp_tmp` empêche d'utiliser deux fois le même objet (sac à dos 0/1). Complexité : $O(nW)$ en temps, $O(W)$ en mémoire. En revanche, ce code ne renvoie **pas les objets choisis**. On écrit donc une version avec la table complète $V(i,c)$.

*Cellule suivante* : version avec table, reconstruction de la solution et **comptage des solutions optimales**. $N(i,c)$ est le nombre de sous-ensembles de $\{1..i\}$ de poids $\le c$ et de valeur $V(i,c)$ ; on l'obtient par la même récurrence en ajoutant les deux cas quand ils donnent le maximum.
''')
code(r'''
def sac_a_dos(v, w, W):
    """Programmation dynamique 0/1. Renvoie la valeur optimale, les objets choisis (indices 0..n-1),
    la table V (n+1) x (W+1) et le nombre de solutions optimales N(n, W)."""
    v, w = list(v), list(w); m = len(v)
    V = np.zeros((m + 1, W + 1), dtype=np.int64)
    N = np.zeros((m + 1, W + 1), dtype=np.int64); N[0, :] = 1
    for i in range(1, m + 1):
        for c in range(W + 1):
            sans = V[i - 1, c]
            avec = v[i - 1] + V[i - 1, c - w[i - 1]] if w[i - 1] <= c else -1
            V[i, c] = max(sans, avec)
            N[i, c] = (N[i - 1, c] if sans == V[i, c] else 0) + \
                      (N[i - 1, c - w[i - 1]] if avec == V[i, c] else 0)
    choisis, c = [], W                         # remontée de la table
    for i in range(m, 0, -1):
        if V[i, c] != V[i - 1, c]:
            choisis.append(i - 1); c -= w[i - 1]
    return int(V[m, W]), sorted(choisis), V, int(N[m, W])

for objets, W in [([(60, 10), (100, 20), (120, 30)], 50), ([(60, 5), (50, 3), (70, 4), (30, 2)], 5)]:
    v, w = zip(*objets)
    val, ch, V, nb = sac_a_dos(v, w, W)
    print(f"W={W}: valeur = {val}, objets choisis (valeur, poids) = {[objets[i] for i in ch]}, nb de solutions optimales = {nb}")
''')
md(r'''
*Commentaire.* On retrouve 220 et 80, comme avec le code fourni, et on connaît maintenant les objets choisis : $\{100,120\}$ et $\{50,30\}$. Dans ces deux exemples, la solution optimale est unique ($N=1$).
''')

md(r'''
*Cellule suivante* : instance plus grande (15 objets aléatoires, $W=40$). Trois vérifications :
* **force brute** sur les $2^{15}=32768$ sous-ensembles ;
* **`milp`** : on maximise, donc on minimise $-v\cdot x$, avec $x$ binaire ;
* **relaxation continue** `linprog` ($0\le x_i\le1$), qui donne une **borne supérieure**.
''')
code(r'''
g = np.random.default_rng(3)
n_obj, Wcap = 15, 40
w_obj = g.integers(1, 16, n_obj); v_obj = g.integers(5, 60, n_obj)
val_dp, choix_dp, V, nb_opt = sac_a_dos(v_obj, w_obj, Wcap)

# force brute (vectorisée) sur tous les sous-ensembles
S = ((np.arange(2**n_obj)[:, None] >> np.arange(n_obj)) & 1)
ok = S @ w_obj <= Wcap
val_bf = (S @ v_obj)[ok].max()
# milp
r_milp = milp(-v_obj, constraints=LinearConstraint(w_obj[None, :], -np.inf, Wcap),
              integrality=np.ones(n_obj), bounds=Bounds(0, 1))
# relaxation continue
r_lp = linprog(-v_obj, A_ub=w_obj[None, :], b_ub=[Wcap], bounds=(0, 1), method='highs-ds')
print("poids  :", w_obj); print("valeurs:", v_obj)
print(f"DP = {val_dp}, force brute = {val_bf}, milp = {-r_milp.fun:.0f}, relaxation LP = {-r_lp.fun:.3f}")
print("objets choisis (DP)   :", [i + 1 for i in choix_dp], "poids total =", int(w_obj[choix_dp].sum()))
print("objets choisis (milp) :", [int(i) + 1 for i in np.flatnonzero(r_milp.x > .5)])
print("solution LP           :", r_lp.x.round(3))
''')
md(r'''
*Commentaire.* DP, force brute et `milp` donnent la même valeur optimale. La relaxation continue donne une valeur **plus grande** : c'est une borne supérieure, avec un objet **fractionnaire**. On retrouve la solution gloutonne de Dantzig : on trie les objets par rapport $v_i/w_i$ décroissant et on coupe le dernier. La contrainte $w\cdot x\le W$ n'est pas totalement unimodulaire, donc, contrairement à l'affectation, **arrondir la relaxation ne suffit pas**.
''')
md(r'''
*Cellule suivante* : **figures**. La table $V(i,c)$, la fonction $c\mapsto V(n,c)$, et les objets classés par rapport valeur/poids, avec ceux qui sont choisis mis en évidence.
''')
code(r'''
fig, ax = plt.subplots(1, 3, figsize=(20, 4.8))
im = ax[0].imshow(V, aspect='auto', origin='lower', cmap='viridis')
ax[0].set_xlabel('capacité $c$'); ax[0].set_ylabel('objets considérés $i$'); ax[0].set_title('table de Bellman $V(i,c)$')
plt.colorbar(im, ax=ax[0])
c_path = Wcap; chemin = [(n_obj, c_path)]
for i in range(n_obj, 0, -1):
    if V[i, c_path] != V[i - 1, c_path]: c_path -= w_obj[i - 1]
    chemin.append((i - 1, c_path))
ax[0].plot([p[1] for p in chemin], [p[0] for p in chemin], 'r.-', label='remontée')
ax[0].legend(loc='upper left')
ax[1].step(range(Wcap + 1), V[-1], where='post')
ax[1].set_xlabel('capacité $c$'); ax[1].set_ylabel('$V(n,c)$'); ax[1].set_title('valeur optimale selon la capacité')
ordre = np.argsort(-v_obj / w_obj)
coul = ['C3' if i in choix_dp else 'C7' for i in ordre]
ax[2].bar(range(n_obj), (v_obj / w_obj)[ordre], color=coul)
ax[2].set_xticks(range(n_obj), [f"{i+1}\n({w_obj[i]})" for i in ordre], fontsize=8)
ax[2].set_xlabel('objet (poids), trié par $v_i/w_i$'); ax[2].set_ylabel('$v_i/w_i$')
ax[2].set_title('objets choisis (rouge) vs rapport valeur/poids')
plt.tight_layout(); plt.show()
''')
md(r'''
*Commentaire.*
* La table croît avec $i$ et avec $c$. La remontée (en rouge) part de $(n,W)$, et chaque saut horizontal correspond à un objet pris.
* $c\mapsto V(n,c)$ est une fonction en **escalier croissante** : un peu de capacité en plus peut ne rien rapporter, ou permettre un nouvel objet.
* Les objets choisis sont surtout ceux de meilleur rapport $v_i/w_i$, mais **pas exactement** : la stratégie gloutonne n'est pas optimale en nombres entiers. C'est ce que corrige la programmation dynamique.
''')

md(r'''
*Cellule suivante* : **complexité**. On mesure le temps de la DP en faisant varier $n$ (à $W$ fixé), puis $W$ (à $n$ fixé).
''')
code(r'''
def chrono(m, W, rep=1):
    gg = np.random.default_rng(m + W)
    vv, ww = gg.integers(1, 100, m), gg.integers(1, 50, m)
    t0 = time.perf_counter()
    for _ in range(rep): get_maximum_value([Item(int(a), int(b)) for a, b in zip(vv, ww)], W)
    return (time.perf_counter() - t0) / rep

ns = [20, 40, 80, 160, 320]; Ws = [100, 200, 400, 800, 1600]
tn = [chrono(m, 400) for m in ns]; tW = [chrono(80, W) for W in Ws]
fig, ax = plt.subplots(1, 2, figsize=(12, 4))
ax[0].loglog(ns, tn, 'o-', label='mesuré'); ax[0].loglog(ns, tn[0]*np.array(ns)/ns[0], 'k--', label='pente 1')
ax[0].set_xlabel('$n$ (W = 400)'); ax[0].set_ylabel('temps (s)'); ax[0].legend()
ax[1].loglog(Ws, tW, 'o-', label='mesuré'); ax[1].loglog(Ws, tW[0]*np.array(Ws)/Ws[0], 'k--', label='pente 1')
ax[1].set_xlabel('$W$ (n = 80)'); ax[1].legend()
fig.suptitle(r'Complexité de la programmation dynamique : $O(nW)$'); plt.tight_layout(); plt.show()
''')
md(r'''
*Commentaire.* Le temps est **linéaire en $n$ et linéaire en $W$**, ce qui confirme la complexité $O(nW)$. Cette complexité est **pseudo-polynomiale** : elle est polynomiale en la *valeur* $W$, mais exponentielle en sa *taille* ($\log_2W$ bits). Le sac à dos est NP-difficile ; la DP reste efficace tant que $W$ est modéré, alors que la force brute coûte $O(2^n)$.
''')

md(r'''
*Cellule suivante* : **unicité**. Sur un exemple construit avec des ex æquo, $(v,w)=(6,4),(6,4),(5,3),(7,5),(1,1)$ et $W=8$, on compte les solutions optimales avec $N(n,W)$ et on les énumère par force brute.
''')
code(r'''
v_t, w_t, W_t = np.array([6, 6, 5, 7, 1]), np.array([4, 4, 3, 5, 1]), 8
val, ch, _, nb = sac_a_dos(v_t, w_t, W_t)
S = ((np.arange(2**5)[:, None] >> np.arange(5)) & 1)
opt = [tuple(int(i) + 1 for i in np.flatnonzero(s)) for s in S if s @ w_t <= W_t and s @ v_t == val]
print(f"valeur optimale = {val}, nombre de solutions optimales (DP) = {nb}")
print("solutions optimales (force brute) :", opt)
print(f"instance aléatoire précédente : {nb_opt} solution(s) optimale(s)")
''')
md(r'''
*Commentaire.* Ici, 4 sous-ensembles différents atteignent la valeur 12 : **la solution n'est pas unique**. Le compteur $N$ calculé par la DP coïncide avec l'énumération, et il ne coûte rien de plus que la DP elle-même. Pour l'instance aléatoire, $N=1$ : la solution est unique. Autre méthode, comme pour l'affectation : ajouter à `milp` la coupe $\sum_{i\in S^*}x_i\le|S^*|-1$ et vérifier que l'optimum baisse strictement. *(Cette coupe exclut $S^*$ et tous ses sur-ensembles. Les valeurs étant $>0$, un sur-ensemble admissible de $S^*$ aurait une valeur strictement plus grande, ce qui est impossible : la coupe n'exclut aucune autre solution optimale.)*
''')
md(r'''
*Variante (si elle est demandée) : sac à dos **non borné**, où chaque objet peut être pris plusieurs fois.* Il suffit de parcourir les capacités **dans l'ordre croissant**, sur un seul tableau :
$V(c)=\max\big(V(c),\ v_i+V(c-w_i)\big)$. Pour le sac à dos 0/1 sur un seul tableau, on parcourt au contraire $c$ **dans l'ordre décroissant**, ce qui évite la copie `dp_tmp`.
''')
code(r'''
def sac_non_borne(v, w, W):
    V = [0] * (W + 1)
    for c in range(W + 1):
        for vi, wi in zip(v, w):
            if wi <= c: V[c] = max(V[c], vi + V[c - wi])
    return V[W]

def sac_01_1D(v, w, W):
    V = [0] * (W + 1)
    for vi, wi in zip(v, w):
        for c in range(W, wi - 1, -1):          # ordre décroissant : chaque objet au plus une fois
            V[c] = max(V[c], vi + V[c - wi])
    return V[W]

for v_, w_, W_ in [([60, 50, 70, 30], [5, 3, 4, 2], 5), ([60, 100, 120], [10, 20, 30], 50)]:
    print(f"W={W_}: 0/1 (1D, ordre décroissant) = {sac_01_1D(v_, w_, W_)} | non borné = {sac_non_borne(v_, w_, W_)}")
''')
md(r'''
*Commentaire.* La version 1D en ordre décroissant redonne 80 et 220. En version non bornée, le premier exemple donne encore 80 ($(50,3)+(30,2)$ reste le meilleur choix), mais le second donne 300 contre 220 : on prend 5 fois l'objet $(60,10)$, qui a le meilleur rapport valeur/poids.
''')

# ---------------------------------------------------------------------
# ANNEXE
# ---------------------------------------------------------------------
md(r'''
## Annexe : pièges et rappels pour le jour J

| Piège | Ce qu'il faut faire |
|---|---|
| `linprog(method='simplex')` ou `'revised simplex'` | obsolètes (SciPy ≥ 1.9) : utiliser `method='highs-ds'` (simplexe dual) ou `'highs'` |
| `linprog` minimise ; bornes par défaut $(0,+\infty)$ | pour maximiser, passer $-c$ ; préciser `bounds=(0,1)` si besoin |
| `milp(c, constraints=LinearConstraint(A, lb, ub), integrality=np.ones(N), bounds=Bounds(0,1))` | égalité : `lb = ub = b` ; inégalité $\le$ : `lb = -np.inf` |
| SLSQP : `{'type':'ineq','fun':g}` signifie $g(x)\ge0$ | passer `-F` pour une contrainte $F\le0$ |
| `NonlinearConstraint(fun, lb, ub)` | vérifier que `fun` ne contient pas déjà le second membre (bug du corrigé 2025) |
| `dual_annealing` exige des bornes | les justifier par la coercivité (boule $B(0,R)$) |
| `y**(4/3)` avec $y<0$ donne `nan` | `np.cbrt(y)**4` |
| Uzawa / pénalisation fournis : `np.dot(DF(x), p)` | il faut `DF(x).T @ p` si `DF` est la jacobienne $m\times n$ |
| Contrainte « objet 1 juste à gauche de 2 » | ne pas oublier $x_{n,1}=0$ |
| Recuit : probabilité d'acceptation | accepter une dégradation avec probabilité $e^{-\Delta/T}$ (Metropolis) |
| Chaînes LaTeX dans matplotlib | préfixe `r"..."` (sinon `SyntaxWarning: invalid escape sequence`) |

**Phrases types pour l'existence et l'unicité**
* *Continue + coercive sur un fermé non vide ⇒ existence* (suite minimisante bornée, Bolzano–Weierstrass).
* *Continue sur un compact non vide ⇒ existence* (Weierstrass).
* *Strictement convexe sur un convexe ⇒ au plus un minimiseur.*
* *$\alpha$-convexe (hessienne $\succeq\alpha I$) ⇒ strictement convexe et coercive ⇒ existence et unicité.*
* *Problème convexe + Slater ⇒ KKT nécessaires et suffisantes.*
* *Ensemble admissible fini non vide (permutations, sous-ensembles) ⇒ existence ; unicité testée par une coupe ou par comptage.*
* *Non convexe : unicité non garantie ; exhiber deux minimiseurs ou la tester numériquement (multi-départs).*
''')

# =====================================================================
# Écriture des deux notebooks
# =====================================================================

def build(version):
    nb = new_notebook()
    nb.metadata['kernelspec'] = {'name': 'python3', 'display_name': 'Python 3', 'language': 'python'}
    nb.metadata['language_info'] = {'name': 'python'}
    cells = []
    for kind, src, role in CELLS:
        if version == 'corrige':
            if role == 'E':
                continue
            cells.append(new_markdown_cell(src) if kind == 'md' else new_code_cell(src))
        else:
            if role in ('B', 'E'):
                cells.append(new_markdown_cell(src) if kind == 'md' else new_code_cell(src))
            elif kind == 'code':
                if not (cells and cells[-1].cell_type == 'code' and cells[-1].source.startswith('# À compléter')):
                    cells.append(new_code_cell('# À compléter\n'))
    nb.cells = cells
    return nb


if __name__ == '__main__':
    for version in ['enonce', 'corrige']:
        nb = build(version)
        path = os.path.join(OUT, f'TP2026_prediction_{version}.ipynb')
        nbformat.write(nb, path)
        print('écrit :', path, f'({len(nb.cells)} cellules)')
