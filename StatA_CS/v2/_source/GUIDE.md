# Guide de rédaction — StatA_CS v2

Ce guide fixe le ton, la structure et les composants de toutes les pages de la v2.
Il sert à garder les pages cohérentes entre elles (et à les retoucher plus tard).

## 1. Le lecteur

Un étudiant de 3A qui **reprend les statistiques après deux ans sans en faire**.
Il connaît l'algèbre linéaire et les probabilités « de base » mais ne les a plus en tête.
Le compagnon v1 (fichiers `SeanceXX_compagnon.html`) a échoué parce qu'il :

- supposait tout connu (rang, projection, trace, queues gaussiennes, sous-différentiel…) ;
- expliquait une notion nouvelle avec des notions plus avancées encore ;
- renvoyait sans cesse en avant/en arrière (« voir Cours4 diapo 57 ») au lieu d'expliquer ;
- donnait des résultats sans le raisonnement qui y mène.

La v2 doit permettre de **comprendre, refaire seul les raisonnements, et acquérir des réflexes**.

## 2. Règles d'écriture (non négociables)

1. **Français, vouvoiement**, phrases courtes. Termes anglais entre parenthèses à la première occurrence (« parcimonie (*sparsity*) »).
2. **Aucune notion utilisée avant d'être expliquée.** Si un outil est nécessaire (trace, Hölder, union bound…),
   soit un encadré `rappel` court sur place, soit un lien vers `00_rappels.html#ancre` **et** une phrase qui dit ce qu'on en utilise.
3. **Chaque symbole est défini à sa première apparition** dans la page (rappeler $n$, $p$, $X$, $\bstar$… en début de page).
4. **Pourquoi avant comment** : chaque notion commence par le problème qu'elle résout.
5. **Calculs pas à pas** : chaque ligne d'un calcul a sa justification (composant `ol.steps`). Interdit : « il est facile de voir », « immédiatement », « clairement » sans justification.
6. **Idée de preuve avant la preuve** : encadré `idee` (3–6 lignes, le plan), puis la preuve complète repliée (`details.fold.proof`).
7. **Exemple chiffré** pour chaque notion importante (petites matrices, valeurs simples, calcul vérifiable à la main). Vérifiez vos chiffres (Python si besoin).
8. **Fidélité aux diapos** : chaque énoncé des diapos est cité dans un encadré `diapo` (référence `CoursK · diapo N`), puis **décodé** symbole par symbole. Les coquilles ou conventions ambiguës des diapos sont signalées gentiment dans un encadré `remarque` (« Note sur la diapo »).
9. **Conventions de normalisation explicites** : les diapos mélangent $\norm{Y-X\beta}^2$, $\frac1n\norm{Y-X\beta}^2$, $\lambda$, $2r$, $\lambda/2$… Chaque fois qu'un facteur dépend de la convention, dites laquelle est utilisée et ce qui change sinon.
10. **Réflexes** : encadrés `reflexe` au fil du texte, formulés « Quand vous voyez … → pensez … » ou « Pour montrer … → … ».
11. **Pièges** : encadrés `piege` pour les erreurs typiques d'un débutant.
12. **Exercices** en fin de page : au moins 8, gradués ★ à ★★★, chacun avec `indice` puis `solution` complète et rédigée.
13. Ne pas inventer de contenu de diapo : ce qui est hors diapos est signalé (« Pour aller plus loin », « hors diapos »).

## 3. Structure d'une page de séance

```
<!--
title: Séance N — Titre court et parlant
short: SN · mot-clé
description: une phrase
subtitle: ce que couvre la séance (diapos …)
-->
<div class="box objectifs"> … ce que vous saurez faire à la fin (liste) </div>
<h2 id="avant">Avant de commencer</h2>
   - ce qu'il faut savoir (liens vers Rappels) ; - le fil de l'histoire (pourquoi cette séance) ; - conventions de notation
<h2 id="...">1. …</h2>   (une h2 par grand thème, une h3 par diapo ou groupe de diapos)
   chaque h3 : tldr → problème/motivation → construction pas à pas → encadré diapo + décodage
               → exemple chiffré → idée de preuve → preuve détaillée (repliée) → piège/réflexe → quiz rapide
<h2 id="resume">Résumé de la séance</h2>
<h2 id="reflexes">Les réflexes à acquérir</h2>
<h2 id="exercices">Exercices</h2>
<h2 id="suite">Et après ?</h2>  (ce que la séance suivante va faire de tout ça, en 3–5 lignes)
```

Les `h2` ont des `id` explicites et stables (minuscules, tirets). Les `h3` peuvent en avoir (recommandé).

## 4. Composants HTML

Formules : `$...$` en ligne, `$$...$$` centrée (rendu KaTeX à la compilation). `\$` pour un dollar littéral.
Une formule en ligne ne doit pas contenir de ligne vide. `<` et `>` sont permis dans les formules.
Pas de formule dans un attribut HTML.

Macros disponibles : `\R \N \E \P \Var \Cov \tr \rg \sgn \diag \Ker \Ima \supp \argmin \argmax \T` (transposée : `X\T X`),
`\bstar` ($\beta^*$), `\hb` ($\hat\beta$), `\Astar`, `\hA`, `\eps`, `\ind`, `\dd`, `\norm{x}`, `\abs{x}`, `\ps{a}{b}`, `\MC` (exposant MC : `\hb\MC`), `\cF`, `\cA`.
Environnements utiles : `aligned`, `cases`, `pmatrix`, `underbrace`, `boxed`, `\text{…}`.

```html
<p class="tldr">Une phrase qui résume la sous-section.</p>

<div class="box def"><div class="box-h">Définition — Nom <span class="ref">Cours1 · diapo 6</span></div> … </div>
<div class="box thm"><div class="box-h">Théorème — Nom</div> … </div>
<div class="box diapo"><div class="box-h">Ce que dit la diapo <span class="ref">Cours1 · diapo 7</span></div> … (énoncé fidèle) </div>
<div class="box rappel"><div class="box-h">Rappel — Trace d'une matrice</div> … <a href="00_rappels.html#trace">en détail</a></div>
<div class="box intu"><div class="box-h">Intuition</div> … </div>
<div class="box exemple"><div class="box-h">Exemple chiffré</div> … </div>
<div class="box idee"><div class="box-h">Idée de la preuve</div><ol><li>…</li></ol></div>
<div class="box reflexe"><div class="box-h">Réflexe</div><p>Quand vous voyez … → …</p></div>
<div class="box piege"><div class="box-h">Piège</div> … </div>
<div class="box methode"><div class="box-h">Méthode</div> … recette en étapes … </div>
<div class="box remarque"><div class="box-h">Note sur la diapo</div> … </div>
<div class="box resume"> … </div>

<ol class="steps">
  <li>$$ … $$<span class="why">pourquoi cette ligne est vraie</span></li>
</ol>

<details class="fold proof"><summary>Preuve détaillée</summary><div class="fold-body"> … </div></details>
<details class="fold hint"><summary>Indice</summary><div class="fold-body"> … </div></details>
<details class="fold sol"><summary>Solution</summary><div class="fold-body"> … </div></details>
<details class="fold more"><summary>Pour aller plus loin</summary><div class="fold-body"> … </div></details>

<div class="exo"><div class="exo-h">Exercice 3 — Titre <span class="lvl">★★☆</span></div>
  <p>Énoncé…</p>
  <details class="fold hint">…</details><details class="fold sol">…</details></div>

<div class="quiz"><p>Question rapide ?</p><details class="fold sol"><summary>Réponse</summary><div class="fold-body">…</div></details></div>

<div class="cols"><div class="box …">…</div><div class="box …">…</div></div>   (comparaisons côte à côte)
<div class="table-wrap"><table>…</table></div>
<em class="new">terme défini</em>   (mise en valeur d'un terme à sa définition)
```

## 5. Figures

**Figures interactives** (déjà codées dans `app.js`) : `<div class="widget" data-widget="NOM" …></div>`.
Ajoutez dessous un paragraphe qui dit quoi regarder / quoi manipuler.

| NOM | contenu | attributs |
|---|---|---|
| `seuillage` | une coordonnée : identité, Ridge $b/(1+\lambda)$, seuillage doux, (dur) | `data-hard="1"` ; `data-seuil="demi"` pour la convention $\norm{Y-X\beta}^2+\lambda\norm\beta_1$, $X\T X=I$ (seuil $\lambda/2$) ; sinon convention $\frac12(a-b)^2+\lambda\abs a$ (seuil $\lambda$) |
| `l1l2` | $p=2$ : losange $\ell_1$, disque $\ell_2$, ellipses $(\beta-b)\T G(\beta-b)$, point $b$ déplaçable | `data-gram="[[4,1.4],[1.4,1]]"`, `data-b="[2,3]"`, `data-t="1"` (contraintes $\norm\beta_1\le t$ et $\norm\beta_2^2\le t$) |
| `chemin` | chemin du Lasso en design orthogonal ($\hb_j=\sgn(b_j)(\abs{b_j}-\lambda/2)_+$), option Ridge | `data-b="[2.4,-1.6,1,0.4]"` |
| `biaisvariance` | biais², variance, risque du Ridge selon $\lambda$ (base propre de $X\T X$) | `data-mu`, `data-theta`, `data-sigma2` |
| `optimisme` | erreur d'apprentissage vs prédiction vs Cp/AIC vs BIC, modèles emboîtés | — |
| `bridge` | boules $\abs{\beta_1}^\gamma+\abs{\beta_2}^\gamma\le1$, curseur $\gamma$ | — |
| `sousgradient` | droites sous le graphe de $\abs u$ ; $\partial\abs{\cdot}(u_0)$ | — |
| `maxgauss` | simulation : $\max_j\abs{Z_j}$ contre $\sqrt{2\log p}$ | — |
| `logistique` | courbe logistique, curseurs $\beta_0,\beta_1$, log-vraisemblance | — |
| `variantes` | design orthonormé : Lasso, LSLasso, relaxé, adaptatif, elastic net, Ridge | — |
| `cone` | cône $\abs{\delta_2}\le c\abs{\delta_1}$ et noyau de $X$ en dimension 2 | — |

**Figures statiques** : SVG en ligne dans `<figure class="fig"><svg viewBox="0 0 W H">…</svg><figcaption>…</figcaption></figure>`.
Classes de couleur qui suivent le thème clair/sombre : traits `ln` + `c1…c6`, `ck` (texte), `cm` (gris) ; `ax` (axe), `gr` (grille) ;
remplissages `f1…f6`, `fk`, `fm` ; aplats transparents `a1…a5`, `am` ; `dash`, `thin` ; textes `tx`, `tx-b`.
N'utilisez jamais de couleur codée en dur. Calculez les coordonnées (Python) plutôt que de les estimer.

## 6. Liens

- Rappels : `00_rappels.html#ancre` avec les ancres de la section 7 ci-dessous (ne pas en inventer d'autres).
- Autres séances : `0N_seanceN.html` (sans ancre, sauf si vous êtes sûr qu'elle existe).
- Diapos : texte `<span class="ref">CoursK · diapo N</span>` (pas de lien).

## 7. Ancres de la page Rappels (fixes)

`notations` · `algebre` : `vecteurs-normes`, `inegalites-normes`, `rang-noyau`, `gram`, `spectral`, `projection`, `trace` ·
`optimisation` : `gradient`, `convexite`, `lagrange`, `newton`, `young` ·
`probabilites` : `esperance`, `gaussien`, `forme-quadratique`, `queues`, `convergences` ·
`statistique` : `estimateur`, `vraisemblance`, `fisher`, `erreur-test`, `tests`.

## 8. Notations communes

- $n$ observations, $p$ variables ; $X\in\R^{n\times p}$ ; ligne $i$ : $x_i$ (vecteur ligne, comme les diapos) ; colonne $j$ : $X_j\in\R^n$.
- $Y=X\bstar+\eps$, $\eps\sim\N(0,\sigma^2I_n)$ ; $\norm{\cdot}$ euclidienne ; $\norm{u}_n^2=\frac1n\norm u^2$.
- Estimateurs : $\hb\MC$, $\hb^{R}(\lambda)$, $\hb^{L}(\lambda)$ ; support $\Astar=\{j:\bstar_j\ne0\}$, $s$ borne sur $\abs{\Astar}$.
- Normes : $\norm\beta_0=\#\{j:\beta_j\neq0\}$, $\norm\beta_1=\sum\abs{\beta_j}$, $\norm\beta_2$, $\norm\beta_\infty=\max\abs{\beta_j}$.
- $\sgn$, $(x)_+=\max(x,0)$, $\ind\{\cdot\}$ indicatrice, $\abs A$ cardinal, $A^c$ complémentaire.

## 9. Compiler et vérifier

```
cd StatA_CS/v2/_source && npm install && node build.mjs            # toutes les pages
node build.mjs 03_seance3.html                                     # une seule page (erreurs de cette page seulement)
```
La compilation échoue (et liste fichier:ligne) sur toute formule invalide, tout lien interne sans cible, tout id en double.
