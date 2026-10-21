# Guide de rédaction — Programmation linéaire, version 2

Le contrat de toutes les pages de la v2 : la page d'accueil `index`, la page `Rappels` et huit parties
`Partie01` … `Partie08`. Les pages sont **en français** (le cours est en français).

**Modèle de qualité.** La v2 du cours de transport optimal, écrite en anglais avec la même méthode :
`../../../Optimal_transport_ML/v2/_source/pages/Lesson03/*.html` (texte), `widgets/Lesson03.js` (figures interactives),
`figures_L03.py` (figures statiques). Lisez-la avant d'écrire : même ton, même densité, mêmes composants. Vous
écrivez en français ce qu'elle fait en anglais.

## 1. Le lecteur et le but

Un élève ingénieur de CentraleSupélec (cursus ingénieur), qui suit aussi le master MVA, inscrit au cours
*Optimisation — Programmation linéaire*. Il veut **tout comprendre et savoir tout refaire seul** : l'intuition, le
sens de chaque symbole, les preuves pas à pas, de petits exemples chiffrés, les réflexes pour l'examen, la
résolution des exercices — et **à quoi sert la programmation linéaire, en particulier en machine learning**. Il
peut être rouillé en algèbre linéaire (rang, bases, déterminants), en convexité et en dualité : rappelez ce qu'il
faut, là où il le faut.

Le guide v1 (`../programmation-lineaire-decortiquee.html`) est une référence dense, de niveau « expert ». La v2
est la version **pédagogique et facile à suivre** : on avance lentement, on explique avant de démontrer, on calcule
sur des exemples, on rappelle les prérequis en route.

## 2. Règles d'écriture

1. **Français**, vouvoiement, phrases courtes. Définissez chaque terme à sa première apparition
   (`<em class="new">terme</em>`). Typographie française : guillemets « … », espace avant `: ; ! ?` (le build la
   rend insécable), virgule décimale (`3,5` dans le texte, `3{,}5` dans une formule). Préférez les **fractions
   exactes** aux décimaux : la PL se calcule exactement. Si un point a des coordonnées décimales, séparez-les par
   un point-virgule : $(5{,}9\,;\,0)$.
2. **Le pourquoi avant le comment.** Chaque notion commence par le problème qu'elle résout.
3. **Fidèle au cours.** Chaque énoncé important du cours (définition, lemme, proposition, théorème, algorithme,
   exercice, exemple des diapos) est cité dans un encadré `course` avec sa référence exacte, puis **décodé**
   symbole par symbole (`dl.decode`). Sources (dans `Opti_CS/LP/`) :
   - les **diapos** du cours, `ProgLin.pdf` (63 pages, avec des transparents qui se complètent) : citez
     « Diapo N », N étant la page du PDF où le passage cité est complet ;
   - le **livre** de G. Allaire, chapitre 4, `OptiAllaire_LP.pdf` : citez « Allaire, Prop. 4.2.8, p. 125 »
     (numéro de l'énoncé et **page imprimée** du livre ; pages imprimées 119–142 = pages 1–24 du PDF, annexe
     p. 189–193 = PDF 25–29) ;
   - pour les rappels seulement : les chapitres 2 et 3 du même livre, `../Continuous/OptiAllaire-12-55_theory.pdf`
     (pages imprimées 13–56 = PDF 1–44 : existence, KKT, Farkas, dualité) et
     `../Continuous/OptiAllaire-56-117_algo_optimisation.pdf` (chapitre 3 : algorithmes, Newton).

   Quand les diapos et le livre diffèrent (énoncé, hypothèse, notation : ${}^tA$ dans les diapos, $A^*$ dans le
   livre), dites-le. N'inventez pas de contenu de cours : ce qui est ajouté pour la pédagogie est présenté comme tel
   (intuition, rappel, remarque, pour aller plus loin).
4. **Des rappels en route.** Dès qu'un prérequis sert (rang, base, Cramer, convexité, compacité, Lagrangien,
   Farkas…), rappelez-le sur place : un encadré `recall` intitulé « Rappel — … » qui dit exactement ce qui sert,
   avec un lien vers la page Rappels (`Rappels.html#ancre`, ancres du §8) ou vers la partie où on l'a vu
   (« Rappel — les coûts réduits (partie 3) »). L'élève ne doit jamais devoir quitter la page pour suivre un
   argument, mais peut suivre un lien pour approfondir.
5. **Applications.** Deux sortes d'encadrés :
   - `ml` (« En machine learning — … ») : où l'idée sert en apprentissage automatique, avec un exemple concret
     (données, modèle, fonction de perte). Pistes vraies et classiques : régression en norme $\ell^1$ (LAD) et
     régression quantile comme PL ; SVM en norme $\ell^1$ ; *basis pursuit* / acquisition comprimée ; transport
     optimal discret (Kantorovich) = PL, et sa dualité ; affectation (algorithme hongrois, appariement des
     prédictions de DETR) ; relaxation PL pour l'inférence MAP dans les modèles graphiques ; coupes de graphes
     (flot max / coupe min) pour la segmentation d'images ; PL en nombres entiers pour vérifier des réseaux ReLU
     (contraintes « big-M ») ; sélection sous budget (sac-à-dos) ; plus courts chemins (Viterbi). Au moins
     **trois** par partie quand le lien existe ; soyez exacts et sobres, pas d'effet d'annonce.
   - `app` (« En pratique — … ») : recherche opérationnelle et solveurs (planning, transport, réseaux ;
     `scipy.optimize.linprog` avec HiGHS, `milp`, PuLP/CBC, OR-Tools, Gurobi/CPLEX ; ce que fait vraiment un solveur).

   L'élève suit aussi le cours *Optimal Transport for ML* : quand c'est pertinent (problème de Kantorovich,
   Birkhoff–von Neumann, dualité, simplexe de réseau), faites le lien vers sa v2, par exemple
   `../../../Optimal_transport_ML/v2/Lesson02.html` (pages `Lesson01.html` … `Lesson08.html`, `Reminders.html`).
6. **Calculs pas à pas** dans `ol.steps`, chaque ligne avec sa justification (`span.why`). Jamais « clairement »,
   « il est facile de voir » sans la raison.
7. **L'idée avant la preuve** : un encadré `idea` (3–6 lignes), puis la preuve complète dans `details.fold.proof`.
8. **Un exemple chiffré** pour chaque notion importante : petit, vérifiable à la main. **Chaque nombre de la
   page est calculé par un script avant d'être écrit** (Python : `fractions.Fraction`, numpy,
   `scipy.optimize.linprog` / `milp`), y compris les réponses des exercices et les nombres lus sur les widgets.
   Rangez vos scripts dans le dossier `verify/` que l'on vous indique.
9. **Pièges** (`pitfall`), **réflexes** (`reflex`, « Quand vous voyez … → … »), **vérifiez-vous** (`quiz`) en
   route.
10. **Exercices.** Les exercices du livre et les exemples des diapos de la partie sont **entièrement corrigés** :
    chaque énoncé cité dans un encadré `course`, puis un indice (`details.fold.hint`) et une solution complète
    (`details.fold.sol`). Si l'énoncé a un défaut (coquille, hypothèse manquante), dites-le gentiment dans un
    encadré `remark` (« Note sur les sources ») avec une vérification, et corrigez les deux versions si besoin.
    Puis 8 à 12 exercices supplémentaires gradués (★ à ★★★), avec indices et solutions.
11. **Notes sur les sources.** Les coquilles et imprécisions trouvées dans les diapos ou le livre vont dans un
    encadré `remark` (« Note sur les sources ») et dans la liste en fin de page, chacune avec un contre-exemple ou
    une vérification. Le guide v1 en a relevé beaucoup (fichier `v1_coquilles.txt` indiqué dans votre consigne) :
    **vérifiez chacune** avant de la reprendre.

## 3. Structure d'une partie

```
pages/PartieNN/00_intro.html     commentaire d'en-tête (ci-dessous), encadré objectifs, « Avant de commencer »
                                 (h2 id="start") : comment lire cette page, l'histoire de la partie en 5–7 étapes
                                 (ol.chain), ce qu'il faut savoir (rappels repliés + liens vers Rappels et les parties
                                 précédentes), tableau de notation (diapos / livre / ce guide), code couleur des figures
pages/PartieNN/01_….html …       un fichier par section (h2), dans l'ordre du cours ; chaque section :
                                 tldr → problème → encadré du cours + décodage → exemple → idée → preuve (repliée) →
                                 rappels / applications / pièges / réflexes / vérifiez-vous
pages/PartieNN/xx_exercices.html les exercices du livre et des diapos de la partie, entièrement corrigés (h2 id="exercices")
pages/PartieNN/xx_plus.html      exercices supplémentaires
pages/PartieNN/xx_bilan.html     (h2 id="bilan") résumé (box summary), fiche de formules (tableau), réflexes
                                 (ul.checklist), les applications de la partie (un tableau), et ensuite, sources et
                                 notes sur les sources
```
Commentaire d'en-tête du premier fichier :
```
<!--
title: Partie N — Titre court et parlant
short: N · mot-clé
description: une phrase (meta description)
subtitle: ce que couvre la page, une ou deux phrases
kicker: Optimisation · Programmation linéaire · guide v2 · partie N
-->
```
Les fichiers sont concaténés dans l'ordre de leurs noms. **Chaque h2 et h3 a un id explicite et stable**
(minuscules, tirets, sans accents ; le build échoue sinon), unique dans la page. Numérotez les h2 (« 1. … »,
« 2. … »). Les ids imposés du §8 doivent exister.

## 4. Composants

Formules : `$...$` en ligne, `$$...$$` centrées (rendues par KaTeX au build) ; `\$` pour un dollar. Une formule en
ligne ne contient pas de ligne vide. Une formule centrée n'est jamais dans un `<p>` (fermez le paragraphe avant
`$$`). Coupez les longues formules avec `\begin{aligned} … \\ … \end{aligned}` pour qu'elles tiennent dans la
colonne (le vérificateur les signale). Dans le texte HTML, écrivez `&lt;` et `&gt;` (dans les formules, `<` et `>`
sont permis).

Macros : `\R \N \Z \Q` (ensembles de nombres), `\Xad` ($X_{\mathrm{ad}}$), `\Pad`, `\Xado` ($X^0_{\mathrm{ad}}$),
`\rg \Ker \Ima \conv \card`, `\eps`, `\Id`, `\argmin \argmax`, `\T` (transposée, $A^\top$), `\ind`, `\ct`
($\tilde c$, coûts réduits), `\Nc \Ac` (nœuds et arcs d'un graphe), `\Mc` (matrices), `\Sc` (permutations),
`\norm{x} \abs{x} \ps{a}{b}`.

```html
<p class="tldr">Une phrase qui résume la section.</p>
<div class="box course"><div class="box-h">Dans le cours <span class="ref">Diapo 9</span></div> … citation fidèle … </div>
<div class="box course"><div class="box-h">Dans le livre <span class="ref">Allaire, Lemme 4.2.5, p. 123</span></div> … </div>
<dl class="decode"><dt>$symbole$</dt><dd>sens en mots</dd> … </dl>
<div class="box recall"><div class="box-h">Rappel — le rang d'une matrice</div> … <a href="Rappels.html#rang">en savoir plus</a></div>
<div class="box ml"><div class="box-h">En machine learning — la régression robuste en norme ℓ¹</div> … </div>
<div class="box app"><div class="box-h">En pratique — ce que fait un solveur</div> … </div>
<div class="box def|thm|intu|example|idea|reflex|pitfall|method|remark|summary|objectives"><div class="box-h">Titre</div> … </div>
<ol class="steps"><li>$$ … $$<span class="why">pourquoi cette ligne est vraie</span></li></ol>
<details class="fold proof|hint|sol|more"><summary>Démonstration complète</summary><div class="fold-body"> … </div></details>
<div class="exo"><div class="exo-h">Exercice N — Titre <span class="lvl">★★</span></div> … </div>
<div class="quiz"><p>Question ?</p><details class="fold sol"><summary>Réponse</summary><div class="fold-body">…</div></details></div>
<div class="cols"> … </div>   <div class="table-wrap"><table> … </table></div>   <ol class="chain"> … </ol>
```
Titres d'encadrés : « Définition — … », « Lemme — … », « Proposition — … », « Théorème — … », « Intuition — … »,
« Exemple — … », « L'idée », « Réflexe », « Piège — … », « Méthode — … », « Remarque — … », « Note sur les
sources », « Rappel — … », « En machine learning — … », « En pratique — … ». Boutons des replis :
« Démonstration complète », « Indice », « Solution », « Pour aller plus loin », « Réponse ».

Liens : les autres parties `PartieNN.html` (avec une ancre seulement si elle est dans la liste du §8) ; la page
Rappels `Rappels.html#ancre` (§8) ; le guide v1 `../programmation-lineaire-decortiquee.html` ; les sources
`../ProgLin.pdf`, `../OptiAllaire_LP.pdf` ; la v2 du cours de transport optimal (règle 5).

## 5. Figures

**Figures statiques** : écrites par `figures_PNN.py`, qui importe `figures_common` (classes `Fig`, `Canvas`) et écrit
`figures/PNN/*.svg` (`Canvas(nom, W, H, label, sub="PNN")`) ; incluses par
`<figure class="fig"><!-- include figures/PNN/nom.svg --><figcaption>…</figcaption></figure>`. Toutes les coordonnées
sont calculées dans le script. Couleurs : classes CSS uniquement (traits `c1…c6`, remplissages `f1…f6`, aplats
`a1…a5`, texte `tx tx-s tx-b tx-i`, couleurs de texte `t1…t6`, texte sur un disque coloré `on-fill`), pour suivre
les thèmes clair et sombre. **Code couleur de la PL** : ensemble admissible $\Xad$ = 1 (bleu : aplat `a1`, bord `c1`),
coût / lignes de niveau / direction $c$ = 2 (rouge orangé), optimum / sommet courant / chemin du simplexe = 3 (vert),
objets duaux ($p$, ensemble $\Pad$) = 5 (violet), points entiers = 4 (or), solutions non admissibles = 6 (rose) ou
gris ; droites de contraintes en gris (`cm thin`) avec leur étiquette. Texte en Unicode dans les SVG (x₁, ≤, ε, ℝ…),
jamais `_` ni `^`. Au moins **cinq** figures par partie.

**Figures interactives** : `widgets/PartieNN.js`, un fragment de code inséré par le build dans la portée de `app.js`,
qui enregistre `WIDGETS.nom = function (box) { … }` (`nom` unique sur tout le site, préfixé : `p3simplexe`). Utilisez
les outils de `app.js` : `el`, `fmt`, `Plot` (axes, poly, fn, dot, seg, text, clip), `scaffold`, `slider`, `select`,
`button`, `checkbox`, `readout`, `legend`, `addSvg`, `svgPoint`, `frac`, `matStr`, `mulberry32`, `gaussRand`,
`combinations`, et les outils de PL :
- `Fr` (rationnels exacts : `Fr(7, 2)`, `Fr.of(x)`, `.add .sub .mul .div .neg .cmp .sign .isZero .val .str`),
  `frMat`, `frVec`, `frDet(M)` (déterminant exact), `frSolve(B, r)` ;
- `basicSolution(A, b, cols)` → `{x, status}` (« singulière », « non admissible », « admissible », « dégénérée ») ;
- `simplex(A, b, c, basis, {rule})` : le simplexe du cours en arithmétique exacte, depuis une base admissible ;
  renvoie `{status, steps}`, chaque étape donnant la base, $x$, le coût, les coûts réduits, la variable entrante, la
  direction $B^{-1}a_i$, les rapports, la variable sortante et le pas $\eps_k$ (voir le commentaire dans `app.js`) ;
- `halfPlanePolygon(cons, box)` (polygone $\{a x + b y \le r\}$ découpé dans une boîte), `lineInBox(a, b, r, box)` ;
- `arrowMarker(svg, cls)`, `drawArc(g, p, q, {bend, label, marker, cls, r})`, `drawNode(g, p, label, {cls, r})`
  pour les graphes ; `hungarian(C)` (affectation optimale).

**Ne redéfinissez jamais un de ces noms** ; préfixez vos propres fonctions (`p7maxflow`). Placement :
`<div class="widget" data-widget="nom"><p class="w-noscript">Figure interactive (nécessite JavaScript).</p></div>`,
suivi d'un paragraphe « À observer : … ». Au moins **trois** par partie ; libellés en français.
Pièges des outils : `new Plot(svg, …)` et `Plot.clear()` vident tout le `svg` ; `svg .ln` fixe `stroke-width` en CSS,
ce qui l'emporte sur un attribut : une épaisseur variable se met en style en ligne (`style: "stroke-width:3px"`) ;
`fmt` affiche « — » pour NaN et ±∞ pour les infinis.

## 6. Construire et vérifier

```
cd Opti_CS/LP/v2/_source
python3 figures_PNN.py                       # figures statiques de la partie
node build.mjs PartieNN.html                 # rapide : ne construit que cette page ; échoue sur toute erreur KaTeX,
                                             # titre sans id, ancre cassée, erreur de syntaxe JS
node tools/check_page.cjs PartieNN.html --shots /tmp/…/shots_PNN
                                             # erreurs console, widgets dessinés, formules trop larges,
                                             # largeur téléphone ; captures de chaque figure et widget
```
Regardez chaque capture (claire et sombre) et corrigez les étiquettes qui se chevauchent, le texte coupé, les
tracés vides.

## 7. Fichiers et travail en parallèle

Plusieurs parties sont écrites en même temps. Un rédacteur ne crée ou ne modifie que **ses fichiers** :
`pages/PartieNN/`, `widgets/PartieNN.js`, `figures_PNN.py`, `figures/PNN/`. Les fichiers partagés (`app.js`,
`style.css`, `build.mjs`, `template.html`, `figures_common.py`, `GUIDE.md`, les autres pages) ne sont pas modifiés :
demandez un changement dans votre rapport final. Aucune opération git.

## 8. Plan du guide et ancres imposées

| Page | Contenu | Sources |
|---|---|---|
| `Partie01` Modéliser | qu'est-ce qu'un PL, modéliser (exemples), forme standard et réductions (4.2)–(4.4), géométrie (exemple (4.5), plan qui balaie), vocabulaire, existence (Lemme 4.2.3), Ex. 4.2.1 | Diapos 4–5 ; Allaire §4.1, 4.2.1 p. 119–122 |
| `Partie02` Sommets | bases, solutions basiques, dégénérescence, sommets = solutions basiques (4.2.5), optimum en un sommet (4.2.6, Rem. 4.2.7), nombre de sommets, Ex. 4.2.2 | Diapo 5 ; Allaire p. 122–124 |
| `Partie03` Simplexe | coûts réduits (4.6), Prop. 4.2.8, Rem. 4.2.9, l'algorithme, test du rapport, tableau, dégénérescence et cyclage, Lemme 4.2.10, choix du pivot, phase I (4.8), inversion de la base, Ex. 4.2.3–4.2.5 | Diapos 6–11 ; Allaire §4.2.2 p. 124–128 |
| `Partie04` Points intérieurs | barrière logarithmique, problème pénalisé, Lemme 4.2.11, trajectoire centrale, Newton, Ex. 4.2.6 | Allaire §4.2.3 p. 129–131 (absent des diapos) |
| `Partie05` Dualité | Lagrangien, fonction duale, dual, dualité faible, Th. 4.2.13, écarts complémentaires, Rem. 4.2.14, sens économique, lien avec les coûts réduits, centre d'appels (diapo 15), Ex. 4.2.7–4.2.10 | Diapos 13–15 ; Allaire §4.2.4 p. 131–134 |
| `Partie06` Nombres entiers | PL en nombres entiers, relaxation, arrondir ne suffit pas (diapo 18), polyèdres et enveloppe convexe, Lemme 4.3.1, (totale) unimodularité, Prop. 4.3.3, Lemme 4.3.5 (Poincaré), Ex. 4.3.1, centre d'appels entier (diapo 24) | Diapos 17–24 ; Allaire §4.3, 4.3.1 p. 134–137 |
| `Partie07` Flots | graphes, flots, Kirchhoff, matrice d'incidence (Lemme 4.3.9), flot à coût minimum, Th. 4.3.7, transport (Rem. 4.3.6) et constructeur automobile (diapo 39), flot maximal (Ex. 4.3.2), chemin de coût minimum (Ex. 4.3.3, Dijkstra), affectation (§4.3.3, Rem. 4.3.10) | Diapos 26–46 ; Allaire §4.3.2–4.3.3 p. 137–142 |
| `Partie08` Problèmes célèbres | sac-à-dos, glouton, voyageur de commerce et sa formulation, séparation-évaluation (*branch and bound*), relaxation lagrangienne, modéliser des liens logiques | Diapos 48–63 (absent du livre) |

**Ancres imposées** (ids qui doivent exister, pour les liens entre pages) — dans chaque partie : `start`,
`exercices`, `bilan` ; et en plus :
- `Partie01` : `forme-standard`, `geometrie`, `existence`
- `Partie02` : `bases`, `sommets-basiques`, `optimum-sommet`
- `Partie03` : `couts-reduits`, `algorithme`, `degenerescence`, `phase-1`
- `Partie04` : `barriere`, `trajectoire-centrale`
- `Partie05` : `dual`, `dualite-faible`, `theoreme-dualite`, `ecarts-complementaires`, `centre-appels`
- `Partie06` : `relaxation`, `unimodularite`, `poincare`
- `Partie07` : `flots`, `matrice-incidence`, `transport`, `flot-maximal`, `plus-court-chemin`, `affectation`
- `Partie08` : `sac-a-dos`, `voyageur`, `separation-evaluation`, `modelisation-logique`

**Ancres de la page Rappels** :
`algebre` (`rang`, `bases-coordonnees`, `inverse-cramer`, `determinant`, `transposee`, `systemes`, `blocs`) ·
`convexite` (`ensembles-convexes`, `polyedres`, `points-extremaux`, `enveloppe-convexe`, `fonctions-convexes`, `cones`) ·
`analyse` (`inf-sup`, `compacite`, `fermes`, `suites-minimisantes`) ·
`optimisation` (`lagrangien`, `kkt`, `point-selle`, `dualite-lagrangienne`, `farkas`, `separation`, `newton`, `penalisation`) ·
`graphes` (`graphes-orientes`, `chemins-cycles`, `dijkstra`) ·
`complexite` (`grand-o`, `polynomial-exponentiel`, `np`, `denombrement`) ·
`entiers` (`arithmetique`, `arrondi`).

## 9. Notation commune

Programme linéaire standard : $\min\{c\cdot x : Ax=b,\ x\ge 0\}$, $A\in\Mc_{m\times n}(\R)$, $m\le n$, $\rg A=m$,
$b\in\R^m$, $c\in\R^n$ ; $\Xad$ l'ensemble admissible. Base $B$ ($m$ colonnes de $A$, inversible), $N$ les autres
colonnes, $x=(x_B,x_N)$, $c=(c_B,c_N)$ ; coûts réduits $\ct_N = c_N - N^\top B^{-\top} c_B$ ; $e_i$ le $i$-ème vecteur
de base ; $a_i$ la $i$-ème colonne de $A$. Transposée : $A^\top$ dans ce guide (${}^tA$ dans les diapos, $A^*$ dans
le livre). Dual : $\max\{b\cdot p : A^\top p\le c\}$, $p\in\R^m$, $\Pad$ l'ensemble admissible dual. Produit scalaire
$c\cdot x$. Graphe $G=(\Nc,\Ac)$, flot $x_{ij}$, capacités $u_{ij}$, coûts $c_{ij}$, flots extérieurs $b_i$.
Le tableau de notation de chaque page rappelle les écarts entre diapos, livre et guide.
