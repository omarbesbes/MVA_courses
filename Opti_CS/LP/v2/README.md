# Programmation linéaire — guide d'étude, version 2

Un guide d'étude pas à pas du cours *Optimisation — Programmation linéaire* (CentraleSupélec) : huit parties,
écrites pour être comprises sans aide. Chaque page cite le cours (diapos `../ProgLin.pdf` et chapitre 4 du livre
de G. Allaire `../OptiAllaire_LP.pdf`), décode chaque symbole, donne la raison avant le résultat, démontre chaque
étape avec sa justification, essaie tout sur de petits exemples chiffrés, rappelle les prérequis là où ils servent
et montre à quoi sert chaque idée, en recherche opérationnelle et en machine learning. Tous les exercices du livre
et les exemples des diapos sont corrigés. Des figures interactives permettent de manipuler et d'observer.

**Ouvrez `index.html` dans un navigateur.** Les pages sont autonomes (formules, polices et figures incluses) :
elles fonctionnent hors ligne.

| Page | Contenu |
|---|---|
| `index.html` | Mode d'emploi, les huit parties, à quoi sert la PL, notation |
| `Rappels.html` | Les prérequis repris depuis le début : algèbre linéaire, convexité, analyse, optimisation (Lagrangien, Kuhn–Tucker, Farkas, Newton), graphes, complexité |
| `Partie01.html` | Modéliser : forme standard, géométrie, existence d'une solution |
| `Partie02.html` | Sommets et solutions basiques |
| `Partie03.html` | L'algorithme du simplexe |
| `Partie04.html` | Les méthodes de points intérieurs (livre seulement) |
| `Partie05.html` | La dualité, les écarts complémentaires, le centre d'appels |
| `Partie06.html` | Nombres entiers et totale unimodularité |
| `Partie07.html` | Flots, transport et affectation |
| `Partie08.html` | Problèmes entiers célèbres : sac-à-dos, voyageur de commerce, séparation-évaluation (diapos seulement) |

Le premier guide, plus dense, est `../programmation-lineaire-decortiquee.html` ; il renvoie ici.

## Sources et reconstruction

Les sources sont dans `_source/` : un dossier de fragments HTML par page (`pages/<Page>/`), le style et les scripts
communs (`style.css`, `app.js`, `template.html`), un fichier de figures interactives par page (`widgets/PartieNN.js`)
et un générateur de figures statiques par page (`figures_PNN.py`, qui écrit `figures/PNN/*.svg`). Les règles
d'écriture sont dans `_source/GUIDE.md`.

```
cd _source
npm install                      # KaTeX, utilisé seulement à la construction
python3 figures_P03.py           # un générateur par page (numpy)
node build.mjs                   # toutes les pages ; ou : node build.mjs Partie03.html
node tools/check_page.cjs Partie03.html --shots /tmp/shots   # vérifications et captures (Playwright)
```
