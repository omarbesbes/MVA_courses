# Relecture du DM d'optimisation : « Où relâcher la vérification ? »

Relecture du rapport préliminaire (version HTML/PDF du binôme), avec vérification des démonstrations et des chiffres.
La version corrigée et mise en forme est `rapport_dm.tex` (PDF compilé : `rapport_dm.pdf`).

## Verdict

Le travail est **correct sur le fond** et d'un niveau nettement supérieur aux trois DM d'exemple : ceux-là traitent un problème quadratique classique en quelques pages de notebook, alors que le vôtre combine un PL avec simplexe et dualité, un problème non concave avec KKT et gradient projeté, des preuves complètes et des données réelles.

- Toutes les démonstrations ont été relues ligne à ligne. Elles sont justes.
- Une **affirmation de fond est fausse** : la convexité générale de la frontière E\*(B), contredite par votre propre figure 6(b).
- Le reste relève de la rigueur (quelques étapes non justifiées), du vocabulaire du cours (noms et numéros de théorèmes) et de conflits de notation.

## Ce qui a été vérifié, et comment

Recalcul indépendant avec numpy et le solveur HiGHS de SciPy (scripts dans `verification/`) :

| Résultat du rapport | Recalcul | Statut |
|---|---|---|
| Valeur de (P0) = β = Σ min(p, q), 200 paires aléatoires | écart max 3,9e-16 | ✓ |
| rg(A) = 2n − 1 | 9 pour n = 5 | ✓ |
| Prop. 2 : α\*(ε) = min(1, β + ε), 400 cas | écart max 3,9e-16 | ✓ |
| Prop. 3 : ε\* = (0,16475 ; 0,086875), E\* = 2,2772, modèle A 2,2590 | identique | ✓ |
| λ = 1,19125 = dE\*/dB (γ = 2) | formule fermée, identique | ✓ |
| S1 : E = 4,12 (B), 4,12 (A), 3,21 (uniforme) | 4,1212 / 4,1212 / 3,2132 | ✓ |
| S2 : E = 3,52 (B), 2,79 (A), ρ₁ = ρ₂ = λ = 1,308 | 3,5224 / 2,7887 / 1,3079 | ✓ |
| S3 : E = 4,98 (B), 4,96 (A) | 4,9843 / 4,9635 | ✓ |
| Unimodalité (multi-départs) | 30 départs : écart ≤ 9e-16 ; grille fine pour γ = 3 et 4 : aucun point meilleur | ✓ |
| Ordre 2 en S2 (hessienne restreinte à la face active) | valeur propre −2,28 < 0 : vrai maximum local | ✓ |
| « La frontière E\*(B) est convexe » | convexe en S2, **non convexe en S3** (d² min = −0,21) | ✗ |

Les données réelles (§4) n'ont pas pu être revérifiées, faute des fichiers de données.

## Corrections apportées dans `rapport_dm.tex`

### Erreur de fond
1. **§3.5, frontière vitesse–budget.** Le rapport affirmait en général que « λ\*(B) croît avec B : la frontière E\*(B) est convexe… conséquence des dérivées croisées positives ». C'est vrai en S2, mais la figure 6(b) montre une frontière **concave** en S3 : on dépense d'abord sur les positions bon marché, très rentables, puis sur les pivots chers, ce qui donne des rendements décroissants comme dans un sac à dos. Le texte présente maintenant les deux effets concurrents (complémentarité contre tri par rendement). J'ai ajouté le seul cas démontré : pour γ = 2, régime intérieur, E\*(B) est un polynôme de degré 2 convexe (formule fermée dans la Prop. 3).

### Rigueur des preuves
2. **Prop. 1, étape 4 (non-unicité).** Le cycle ±δ suppose deux cases π_xy > 0 et π_x'y' > 0 avec x ≠ x' et y ≠ y'. Leur existence n'était pas justifiée ; l'argument (trois lignes) a été ajouté.
3. **Prop. 1, étape 2.** π^L divise par TV : on a ajouté le cas TV = 0 (p = q, π = diag(p)).
4. **Totale unimodularité de A.** Le lemme de Poincaré du cours demande au plus un +1 et au plus un −1 par colonne. Or A en a deux +1. Correction : multiplier les n lignes « colonne » par −1 (ce qui ne change que des signes de déterminants), puis appliquer Poincaré. On précise aussi que la TU ne sert pas ici à l'intégrité, puisque b = (q, p) n'est pas entier.
5. **rg(A) = 2n − 1.** Seule l'inégalité ≤ était montrée ; l'inégalité ≥ a été ajoutée (une famille de 2n − 1 colonnes indépendantes).
6. **Qualification (§3.3).** La définition 2.5.15 demande ⟨∇Fᵢ, w⟩ < 0, avec l'égalité permise pour les contraintes affines. Le rapport écrivait « ≤ 0 », ce qui est inexact ; c'est corrigé, avec renvoi à la Rq 2.5.16 (w = 0).
7. **Nom du théorème (§3.3).** Le Th 2.5.17 donne les conditions KKT, qui sont **nécessaires**. Le « théorème de Kuhn–Tucker » du cours (Th 2.6.4) est la version convexe, qui les rend suffisantes ; il **ne s'applique pas** ici puisque J n'est pas convexe. Le texte le dit maintenant explicitement.
8. **Projection sur K.** Il manquait la phrase qui justifie que z(ν) est bien la projection : (z(ν), ν) vérifie KKT pour un problème convexe à contraintes affines, donc condition suffisante (Th 2.6.4). Ajoutée.
9. **« λ = prix marginal ».** Dans le cas non concave, l'argument est heuristique (le lemme 2.6.6 suppose la convexité). Il est désormais présenté comme tel : exact pour γ = 2 (démontré), vérifié numériquement sinon.
10. **Annexe A.** Le résultat porte sur les *valeurs d'adhérence* (et non sur la convergence de toute la suite) ; c'est précisé. La garantie de montée vaut pour tout τ < 2/L (et pas seulement τ = 1/L), ce qui explique proprement la remarque sur τ = 4/L.
11. **Prop. 3.** L'intervalle de projection [η₋, η₊] imposé par les bornes est maintenant explicite (« projeté sur le segment s'il en sort » restait vague).
12. **Prix dual du budget (§2.6).** La figure 2(b) trace dα\*/dε = −2μ\*_B (valeurs 1 puis 0), pas le multiplicateur μ\*_B lui-même (qui vaut −1/2). On note maintenant κ = −2μ\*_B, et on justifie le signe μ\*_B ≤ 0.

### Ajout théorique (vérifié)
13. **Lemme « concavité le long des échanges ».** Transférer du budget d'une position i à une position j (direction s_j e_i − s_i e_j) donne toujours un trinôme strictement concave. Ce lemme explique la Prop. 3 (c'est exactement ce cas pour γ = 2) et rend plausible l'unimodalité observée, sans la démontrer pour γ ≥ 3.

### Notations (conflits supprimés)
- Borne haute u_t → **m_t** (« marge »), car u désignait aussi la variable duale du §2.3.
- Indices de la hessienne s, t → **i, j**, car s est la sensibilité.
- Base du simplexe B → **𝓑, A_𝓑**, car B est le budget.
- Multiplicateur de la projection μ → **ν** ; paramètre de la Prop. 3 τ → **η**, car τ est le pas.
- Nombre d'itérations K → **N** dans l'annexe A, car K est l'ensemble admissible.

## Avis sur le sujet et la démarche

**Points forts.**
- Le sujet est original, bien motivé (l'exemple concret du §1 est excellent) et relié à votre projet de recherche.
- Il exploite naturellement des parties du cours : PL et forme standard, simplexe en deux phases, dualité (certificat explicite, écarts complémentaires, prix duaux), KKT avec qualification, gradient projeté, inéquation d'Euler.
- La démarche est exemplaire : modèle, puis existence, structure, conditions d'optimalité, algorithme, validation, données réelles. Chaque affirmation numérique est confrontée à une preuve ou à un solveur indépendant.
- Le résultat principal (relâcher le début du bloc, jusqu'à 26 % de gain sur le modèle additif) est clair, contre-intuitif et bien démontré : Prop. 4 et lecture KKT du rendement ρ_t.

**Points faibles ou risques.**
- **Les hypothèses (H1)–(H3) et les sensibilités proxies sont fortes.** Vous le dites dans les limites, et c'est bien.
- **L'unicité n'est démontrée que pour γ = 2.** Pour γ ≥ 3, l'affirmation reste empirique ; la renforcer est l'ajout le plus rentable (voir plus bas).
- **Concision.** Les consignes du cours demandent un « rapport concis : effort de synthèse ». À 16–17 pages, une partie de la validation (§2.5) et la reproduction pourraient passer en annexe.
- **Aide de l'IA.** Le cours l'accepte à condition que tout soit justifié et compréhensible sans lire d'article, et en lien avec le cours. Le rapport respecte ces conditions ; assurez-vous de pouvoir défendre chaque preuve vous-mêmes.

## Conformité aux consignes du professeur

| Consigne | Statut |
|---|---|
| Modélisation (variables, objectif, contraintes) | ✓ très soignée (§1, §2.1, §3.1) |
| Existence et unicité | ✓ PL : complet, avec caractérisation exacte de la non-unicité. Partie II : existence ✓, unicité seulement pour γ = 2 |
| Théorème du cours, conditions d'optimalité avec ou sans multiplicateurs | ✓ dualité PL, KKT (Th 2.5.17), Euler (Th 2.5.1) |
| Choix de l'algorithme | ✓ simplexe (PL), gradient projeté (projection quasi explicite) |
| Convergence, cas de plusieurs minima locaux | ✓ annexe A et multi-départs ; à renforcer (ordre 2, certification globale) |
| Illustrations | ✓ 9 figures |
| Un point d'originalité | ✓ **méthode du simplexe** et **mise en œuvre de la dualité**. « Plusieurs minima locaux » n'est pas vraiment montré (problème empiriquement unimodal) : ne le revendiquez pas comme tel, parlez d'objectif non concave |

## Ce qui ferait clairement un travail « de binôme » (par priorité)

1. **Conditions d'ordre 2 et certification globale (petit effort, gros gain).** Ajoutez la vérification d'ordre 2 au point trouvé : hessienne de E restreinte au cône critique, négative (en S2, la valeur propre restreinte vaut −2,28). Pour γ ≤ 4, ajoutez une certification globale par grille ou par énumération des faces actives (voir `verification/verify.py`). Cela répond directement à la consigne « précisions… si le problème possède plusieurs minima locaux ».

2. **Dualité lagrangienne du problème non concave (partie II).** On dualise la contrainte de budget : θ(λ) = λB + max_{0≤ε≤m} [E(ε) − λ s·ε].
   - **Fait clé :** E − λ s·ε est affine en chaque coordonnée séparément, donc ce maximum sur le pavé est atteint en un **sommet**. θ(λ) se calcule exactement en 2^γ évaluations.
   - **Dualité faible :** min_λ θ(λ) majore E\*.
   - **Résultats chiffrés** (`verification/dual_gap.py`) : en S2, borne duale 3,801 contre E\* = 3,522, soit un saut de dualité de 0,28 (la frontière y est convexe). En S3, 5,001 contre 4,984, soit presque aucun saut.

   C'est une illustration très parlante du saut de dualité en non-convexe, qui renforce le critère « mise en œuvre de la dualité » au-delà du cas PL.

3. **(Optionnel) Une contrainte non linéaire.** Mesurer la déviation par une divergence (KL, χ², ‖r − p‖₂²) au lieu de la variation totale. La partie I devient un problème convexe à contrainte non linéaire, avec multiplicateurs de Lagrange. C'est un quatrième critère d'originalité (« contraintes non linéaires »), mais c'est un vrai travail supplémentaire.

4. **Mise en forme finale.**
   - Mettre les deux noms (le rapport portait « [Nom Prénom] ») et éventuellement une ligne sur la répartition du travail.
   - Vérifier que la référence [5] (arXiv:2610.08678) existe bien et est correctement citée ; je n'ai pas pu la vérifier.
   - Raccourcir : déplacer une partie du §2.5 en annexe.
