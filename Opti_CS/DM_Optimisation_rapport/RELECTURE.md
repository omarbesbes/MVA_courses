# Relecture du DM d'optimisation : « Où relâcher la vérification ? »

Relecture du rapport préliminaire (version HTML/PDF du binôme), avec vérification des démonstrations et des chiffres.
La version corrigée et mise en forme est `rapport_dm.tex` (PDF compilé : `rapport_dm.pdf`, 18 pages annexes comprises).
Les numéros de figures ci-dessous sont ceux de la version LaTeX.

## Verdict

Le travail est **correct sur le fond** et d'un niveau nettement supérieur aux trois DM d'exemple : ceux-là traitent un problème quadratique classique en quelques pages de notebook, alors que le vôtre combine un PL avec simplexe et dualité, un problème non concave avec KKT et gradient projeté, des preuves complètes et des données réelles.

- Toutes les démonstrations ont été relues ligne à ligne, deux fois. Elles sont justes.
- Une **affirmation de fond est fausse** : la convexité générale de la frontière E\*(B), contredite par votre propre figure 8(b).
- **Deux chiffres sont surestimés**, dans le résumé (« perd jusqu'à 26 % ») et la conclusion (« plus d'un quart ») : le modèle additif perd 20,8 %, et c'est l'optimum qui va 26 % plus vite.
- Le reste relève de la rigueur (quelques étapes non justifiées), du vocabulaire du cours (noms et numéros de théorèmes), de conflits de notation et de la mise en page.

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
| Frontière S2 : gain max 0,97 sur A, 0,40 sur l'uniforme | 0,972 (à B = 0,51 B_max, soit +28,6 %) et 0,400 | ✓ |
| « jusqu'à 26 % » (résumé) | à B = 0,3 B_max : l'optimum est 26,3 % plus rapide que A, A perd 20,8 % | ✗ corrigé |
| « plus d'un quart » (conclusion) | perte de A : 20,8 % à 0,3 B_max, 22,2 % au pire | ✗ corrigé |
| λ = pente de la frontière | S2 : écart ≤ 0,28 % ; encadrement exact (voir plus bas) : 208 tests, aucune violation | ✓ |
| Unimodalité (multi-départs) | 30 départs : écart ≤ 9e-16 ; grille fine pour γ = 3 et 4 : aucun point meilleur | ✓ |
| Ordre 2 en S2 (hessienne restreinte à la face active) | valeur propre −2,28 < 0 : vrai maximum local | ✓ |
| « La frontière E\*(B) est convexe » | convexe en S2, **non convexe en S3** (d² min = −0,21) | ✗ corrigé |
| Référence [5], arXiv:2610.08678 | existe (Y. Zhang, Z. Wang, N. Gong, Y. Yang, 6 oct. 2026) ; elle vérifie bien plus strictement le début du bloc, comme le dit le rapport | ✓ |

Les données réelles (§4) n'ont pas pu être revérifiées, faute des fichiers de données.

## Corrections apportées dans `rapport_dm.tex`

### Erreur de fond
1. **§3.5, frontière vitesse–budget.** Le rapport affirmait en général que « λ\*(B) croît avec B : la frontière E\*(B) est convexe… conséquence des dérivées croisées positives ». C'est vrai en S2, mais la figure 8(b) montre une frontière **concave** en S3. Le texte présente maintenant les deux effets concurrents (complémentarité contre tri par rendement, comme dans un sac à dos) et un **résultat démontré** qui les réconcilie :
   - pour B < s·u, le budget est saturé ; si B n'est pas l'une des valeurs « sommets » B_I = Σ_{t∈I} s_t u_t, l'optimum a donc une position intérieure ;
   - l'encadrement du prix marginal (point 9) donne alors une droite d'appui locale par en dessous, de pente λ ;
   - une fonction continue qui a une telle droite en tout point d'un intervalle y est convexe (preuve en note de bas de page).

   Donc **E\* est convexe entre deux budgets sommets consécutifs, et sa pente ne peut baisser qu'en un B_I**. C'est exactement ce que l'on observe (`verification/s3_structure.py`). En S3, l'optimum relâche l'une après l'autre les positions bon marché 1, 3 et 4, puis le pivot 2 (un temps avec la position 6), et le pivot tardif 5 en dernier. La pente chute en B_I pour I = {1}, {1, 3}, {1, 3, 4} et {1, 2, 3, 4, 6}, et E\* est affine (une position intérieure) ou strictement convexe (deux positions intérieures) entre ces points. En S2, aucune chute : E\* est convexe sur toute la plage.

### Rigueur des preuves
2. **Prop. 1, étape 4 (non-unicité).** Le cycle ±δ suppose deux cases π_xy > 0 et π_x'y' > 0 avec x ≠ x' et y ≠ y'. Leur existence n'était pas justifiée. L'argument (trois lignes) a été ajouté, ainsi que la raison pour laquelle les quatre cases du cycle sont hors diagonale ({q > p} et {p > q} sont disjoints).
3. **Prop. 1, étape 2.** π^L divise par TV : on a ajouté le cas TV = 0 (p = q, π = diag(p)).
4. **Totale unimodularité de A.** Le lemme de Poincaré du cours demande au plus un +1 et au plus un −1 par colonne. Or A en a deux +1. Correction : multiplier les n lignes « colonne » par −1 (ce qui ne change que des signes de déterminants), puis appliquer Poincaré. On précise aussi que la TU ne sert pas ici à l'intégrité, puisque b = (q, p) n'est pas entier.
5. **rg(A) = 2n − 1.** Seule l'inégalité ≤ était montrée ; l'inégalité ≥ a été ajoutée (une famille de 2n − 1 colonnes indépendantes).
6. **Qualification (§3.3).** La définition 2.5.15 demande ⟨∇Fᵢ, w⟩ < 0, avec l'égalité permise pour les contraintes affines. Le rapport écrivait « ≤ 0 », ce qui est inexact ; c'est corrigé, avec renvoi à la Rq 2.5.16 (w = 0).
7. **Nom du théorème (§3.3).** Le Th 2.5.17 donne les conditions KKT, qui sont **nécessaires**. Le « théorème de Kuhn–Tucker » du cours (Th 2.6.4) est la version convexe, qui les rend suffisantes ; il **ne s'applique pas** ici puisque J n'est pas convexe. Le texte le dit maintenant explicitement.
8. **Projection sur K.** Il manquait la phrase qui justifie que z(ν) est bien la projection. Elle est ajoutée, avec les multiplicateurs des bornes écrits explicitement (ω⁰_t = (ν s_t − y_t)₊, ω¹_t = (y_t − ν s_t − u_t)₊) et la condition de stationnarité : (z(ν), ν) vérifie KKT pour un problème convexe à contraintes affines, donc la condition est suffisante (Th 2.6.4).
9. **« λ = prix marginal ».** Le rapport le justifiait par un raisonnement au premier ordre, analogue au lemme 2.6.6 qui suppose la convexité. Il est maintenant **démontré sans convexité**. Comme E est affine en chaque variable (∂²_tt E = 0), dépenser h de budget en plus (ou en moins) sur une position intérieure donne exactement E\*(B + h) ≥ E\*(B) + λh et E\*(B − h) ≥ E\*(B) − λh. Le taux d'accroissement à gauche est donc ≤ λ, celui de droite ≥ λ, et λ = dE\*/dB partout où E\* est dérivable.
10. **Annexe A.** Le résultat porte sur les *valeurs d'adhérence* (et non sur la convergence de toute la suite) ; c'est précisé. La garantie de montée vaut pour tout τ < 2/L (et pas seulement τ = 1/L), ce qui explique proprement la remarque sur τ = 4/L.
11. **Prop. 3.** L'intervalle de projection [η₋, η₊] imposé par les bornes est maintenant explicite (« projeté sur le segment s'il en sort » restait vague).
12. **Prix dual du budget (§2.6).** La figure 4(b) trace dα\*/dε = −2μ\*_B (valeurs 1 puis 0), pas le multiplicateur μ\*_B lui-même (qui vaut −1/2). On note maintenant κ = −2μ\*_B, et on justifie le signe μ\*_B ≤ 0.

### Ajout théorique (vérifié)
13. **Lemme « concavité le long des échanges ».** Transférer du budget d'une position i à une position j (direction s_j e_i − s_i e_j) donne toujours un trinôme strictement concave. Ce lemme explique la Prop. 3 (c'est exactement ce cas pour γ = 2) et rend plausible l'unimodalité observée, sans la démontrer pour γ ≥ 3.

### Chiffres, figures, références (dernière relecture)
14. **Résumé.** « Un modèle qui ignore la structure perd jusqu'à 26 % » était faux : en S2, A donne 2,79 tokens par passe contre 3,52 pour l'optimum. L'optimum est donc 26 % plus rapide, mais A ne perd que 20,8 %. Le résumé dit maintenant « l'allocation optimale est 26 % plus rapide ».
15. **Conclusion.** « Plus d'un quart de la vitesse » devient « plus d'un cinquième », avec les deux valeurs.
16. **Ordre des figures.** La figure du PL (valeur et deux solutions optimales) passe en premier : les mentions « figure 1 b » écrites dans les images sont ainsi justes. Les figures 2, 3 et 9 n'étaient citées nulle part dans le texte ; les renvois sont ajoutés.
17. **Chen et al. (2023)** est cité à côté de Leviathan et al. : ils ont proposé le même algorithme indépendamment.
18. **Mise en page.** Les guillemets français ne se séparent plus de leur contenu en fin de ligne. La compilation ne donne plus aucun avertissement, y compris un doublon d'ancre hyperref dans l'annexe A.

### Notations (conflits supprimés)
- Variables duales du PL (u, v) → **(φ, ψ)**, car u_t désigne la marge 1 − a_t de la partie II, qui est aussi le nom utilisé dans les figures.
- Indices de la hessienne s, t → **i, j**, car s est la sensibilité.
- Base du simplexe B → **𝓑, A_𝓑**, car B est le budget.
- Multiplicateur de la projection μ → **ν**, et multiplicateurs de ses bornes **ω⁰, ω¹** ; paramètre de la Prop. 3 τ → **η**, car τ est le pas.
- Nombre d'itérations K → **N** dans l'annexe A, car K est l'ensemble admissible.

## Avis sur le sujet et la démarche

**Points forts.**
- Le sujet est original, bien motivé (l'exemple concret du §1 est excellent) et relié à votre projet de recherche.
- Il exploite naturellement des parties du cours : PL et forme standard, simplexe en deux phases, dualité (certificat explicite, écarts complémentaires, prix duaux), KKT avec qualification, gradient projeté, inéquation d'Euler.
- La démarche est exemplaire : modèle, puis existence, structure, conditions d'optimalité, algorithme, validation, données réelles. Chaque affirmation numérique est confrontée à une preuve ou à un solveur indépendant.
- Le résultat principal est clair, contre-intuitif et bien démontré (Prop. 4 et lecture KKT du rendement ρ_t) : il faut relâcher le début du bloc. En S2, l'optimum va 26 % plus vite que le modèle additif à 0,3 B_max, et jusqu'à 28,6 % selon le budget.

**Points faibles ou risques.**
- **Les hypothèses (H1)–(H3) et les sensibilités proxies sont fortes.** Vous le dites dans les limites, et c'est bien.
- **L'unicité n'est démontrée que pour γ = 2.** Pour γ ≥ 3, l'affirmation reste empirique ; la renforcer est l'ajout le plus rentable (voir plus bas).
- **Concision.** Les consignes du cours demandent un « rapport concis : effort de synthèse ». À 18 pages annexes comprises, une partie de la validation (§2.5) et la reproduction pourraient passer en annexe.
- **Aide de l'IA.** Le cours l'accepte à condition que tout soit justifié et compréhensible sans lire d'article, et en lien avec le cours. Le rapport respecte ces conditions ; assurez-vous de pouvoir défendre chaque preuve vous-mêmes.

## Conformité aux consignes du professeur

| Consigne | Statut |
|---|---|
| Modélisation (variables, objectif, contraintes) | ✓ très soignée (§1, §2.1, §3.1) |
| Existence et unicité | ✓ PL : complet, avec caractérisation exacte de la non-unicité. Partie II : existence ✓, unicité seulement pour γ = 2 |
| Théorème du cours, conditions d'optimalité avec ou sans multiplicateurs | ✓ dualité PL, KKT (Th 2.5.17), Euler (Th 2.5.1) |
| Choix de l'algorithme | ✓ simplexe (PL), gradient projeté (projection quasi explicite) |
| Convergence, cas de plusieurs minima locaux | ✓ annexe A et multi-départs ; à renforcer (ordre 2, certification globale) |
| Illustrations | ✓ 9 figures, toutes citées dans le texte |
| Un point d'originalité | ✓ **méthode du simplexe** et **mise en œuvre de la dualité**. « Plusieurs minima locaux » n'est pas vraiment montré (problème empiriquement unimodal) : ne le revendiquez pas comme tel, parlez d'objectif non concave |

## Ce qui ferait clairement un travail « de binôme » (par priorité)

1. **Conditions d'ordre 2 et certification globale (petit effort, gros gain).** Ajoutez la vérification d'ordre 2 au point trouvé : hessienne de E restreinte au cône critique, négative (en S2, la valeur propre restreinte vaut −2,28). Pour γ ≤ 4, ajoutez une certification globale par grille ou par énumération des faces actives (voir `verification/verify.py`). Cela répond directement à la consigne « précisions… si le problème possède plusieurs minima locaux ».

2. **Dualité lagrangienne du problème non concave (partie II).** On dualise la contrainte de budget : θ(λ) = λB + max_{0≤ε≤u} [E(ε) − λ s·ε].
   - **Fait clé :** E − λ s·ε est affine en chaque coordonnée séparément, donc ce maximum sur le pavé est atteint en un **sommet**. θ(λ) se calcule exactement en 2^γ évaluations.
   - **Dualité faible :** min_λ θ(λ) majore E\*.
   - **Résultats chiffrés** (`verification/dual_gap.py`) : en S2, borne duale 3,801 contre E\* = 3,522, soit un saut de dualité de 0,28 (la frontière y est convexe). En S3, 5,001 contre 4,984, soit presque aucun saut.

   C'est une illustration très parlante du saut de dualité en non-convexe, qui renforce le critère « mise en œuvre de la dualité » au-delà du cas PL. Elle se raccorde au nouveau résultat sur la frontière : la borne duale est exactement l'enveloppe concave de la frontière E\* (dualité lagrangienne = concavification de la fonction valeur). Elle colle presque à E\* en S3, où la frontière est essentiellement concave, et s'en écarte en S2, où la frontière est convexe : la borne 3,801 est la corde entre E\*(0) = 2,430 et E(u) = 7, prise en 0,3 B_max.

3. **(Optionnel) Une contrainte non linéaire.** Mesurer la déviation par une divergence (KL, χ², ‖r − p‖₂²) au lieu de la variation totale. La partie I devient un problème convexe à contrainte non linéaire, avec multiplicateurs de Lagrange. C'est un quatrième critère d'originalité (« contraintes non linéaires »), mais c'est un vrai travail supplémentaire.

4. **Mise en forme finale.**
   - Mettre les deux noms (ligne `\author` de `rapport_dm.tex`, qui porte encore « Prénom Nom 1 » et « Prénom Nom 2 ») et éventuellement une ligne sur la répartition du travail.
   - Raccourcir : déplacer une partie du §2.5 en annexe.

## Scripts de vérification (`verification/`)

| Script | Contenu |
|---|---|
| `verify.py` | partie I (PL, rang, Prop. 2), Prop. 3, scénarios S1–S3, unimodalité, ordre 2, certification par grille |
| `dual_gap.py` | dualité lagrangienne de la partie II : borne duale et saut de dualité |
| `frontier.py` | frontières S2/S3 : gains absolus et relatifs, pente contre λ |
| `envelope.py` | encadrement exact du prix marginal (point 9) |
| `s3_structure.py` | structure de la frontière : affine, convexe, cassures aux budgets sommets |
