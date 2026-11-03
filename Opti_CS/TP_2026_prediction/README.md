# TP d'optimisation 2026 — sujet prédit

Prédiction du TP noté, construite à partir du TP 2025 (énoncé et corrigé), de l'en-tête 2026
et des 4 notebooks fournis (`DescenteGradient`, `Uzawa`, `Pénalisation`, `Sac-a-dos`).

| Fichier | Contenu |
|---|---|
| `TP2026_prediction_corrige.ipynb` | corrigé complet exécuté : justifications existence/unicité, explication avant chaque cellule, commentaire après, figures |
| `TP2026_prediction_corrige.html` | le même corrigé, lisible sans Jupyter |
| `TP2026_prediction_enonce.ipynb` | les questions seules, avec des cellules vides, pour s'entraîner |
| `PositionObjets.txt`, `PositionCasiers.txt` | données reconstruites à partir de la figure du corrigé 2025 (précision ≈ 1e-2) |
| `_source/build.py` | génère les deux notebooks (`python3 _source/build.py`) |

## Contenu prédit
1. **Continu convexe sous contraintes** : Uzawa générique et pénalisation (descente à pas fixe et BFGS) sur trois exemples :
   un exemple 2D avec solution exacte, le test d'`Uzawa.ipynb`, et la projection de `b` sur
   `{x1²+x2²+x3²+x4²+x5⁴ ≤ 1, Σx ≤ 1/2}` (version inégalité de la contrainte 2025). Plus une variante avec `f1`, qui est non convexe.
2. **Non convexe** : Newton multi-départs, recuit simulé codé à la main, `basinhopping`, `dual_annealing`, `shgo`.
   Analyse exacte : `min f2 = min_{t ≥ min f1} (t + 10 cos t)`, atteint sur toute une ligne de niveau de `f1`, donc pas d'unicité.
3. **Affectation** : `linear_sum_assignment`, simplexe (`linprog(method='highs-ds')`) et unimodularité totale,
   contraintes « 1 juste à gauche de 2 » et « 5 à côté de 7 », relaxation fractionnaire puis `milp`, test d'unicité par coupe.
4. **Programmation dynamique** : sac à dos 0/1 (Bellman, reconstruction des objets, comptage des solutions optimales),
   vérification par force brute et `milp`, relaxation LP, complexité O(nW), variante non bornée.

## Bugs repérés dans le matériel fourni
* `Uzawa.ipynb` / `Pénalisation.ipynb` : `np.dot(DF(x), p)` doit être `DF(x).T @ p` (DF est la jacobienne m×n).
  Le notebook fourni affiche (-0.2017, 0.7983) au lieu de la vraie solution (-0.2, 0.8).
* Corrigé 2025 : `NonlinearConstraint(cont, 1, 1)` impose G = 1 au lieu de G = 0.
* Corrigé 2025 : la contrainte « objet 1 juste à gauche de l'objet 2 » oublie x_{n,1} = 0.
* Énoncé 2025, recuit : les probabilités d'acceptation sont inversées (règle de Metropolis : accepter une dégradation avec probabilité e^{-Δ/T}).
* `linprog(method='simplex')` est obsolète : utiliser `'highs-ds'` (simplexe dual).
