# Fiche « vraiment manuscrite » : comment elle est fabriquée

Le contenu est le même que dans les autres versions (`../fiche_contenu.tex`). Seule la façon d'« écrire » change, en deux étapes.

## 1. Composition irrégulière (LuaLaTeX + `manuscrit.lua`)

`../fiche_integration_sto_realiste.tex`, à compiler avec `lualatex` :

- **Police :** police manuscrite Kalam pour le texte. Les maths sont en Euler et penchent comme l'écriture.
- **Espacement :** irrégulier entre les lettres et entre les mots, calculé *avant* la coupure des lignes. Aucun mot n'est coupé.
- **Lettres :** chaque glyphe du texte, des maths et des symboles reçoit sa propre petite rotation, une échelle, une inclinaison et un décalage de ligne de base. Une partie est commune au mot, une partie est propre à la lettre, si bien que deux « e » ne sont jamais identiques.
- **Tracés à la main (TikZ) :** les cadres de titres (avec débord aux coins), ★ △ → ✓, les lettres à double barre 𝔼 ℙ ℝ 𝔽 𝔾 𝕋 et l'indicatrice 𝟙.
- **Mise en forme manuscrite :** soulignement au lieu de l'italique. La taille d'écriture varie un peu d'une section à l'autre.
- **Ratures :** trois corrections volontaires (macro `\rature`) :
  - « Tchebi » barré avant « Tchebychev » ;
  - « ≤ » barré dans Jensen ;
  - « + » barré dans ∫W dW.
- **Encres :** des couleurs « marqueurs » (bleu pur, rouge pur, vert pur, noir, magenta = crayon), remplacées à l'étape 2.

## 2. Réencrage (`reencrage.py`)

1. **Séparation des encres :** rendu à 600 dpi, puis séparation des encres d'après les marqueurs.
2. **Déformation élastique :** le même champ s'applique à toutes les encres, à plusieurs échelles :
   - rotation de la feuille, dérive lente des colonnes ;
   - chaque ligne qui ondule et penche, avec un début de ligne irrégulier ;
   - mots légèrement décalés, forme de chaque lettre légèrement altérée.
3. **Réencrage au stylo :** on extrait le squelette des traits, puis on le repasse avec une pointe de largeur quasi constante. Texte, maths et symboles ont ainsi le même stylo. La largeur varie doucement le long du trait, avec un petit dépôt d'encre aux extrémités.
4. **Texture :** pression et grain de l'encre. Les séparations de colonnes sont au crayon à papier grainé.
5. **Composition :** composition soustractive sur blanc **exact**, avec une palette explicite (l'imprimante ne touche pas au fond).

```bash
lualatex fiche_integration_sto_realiste.tex
python3 manuscrit/reencrage.py fiche_integration_sto_realiste.pdf   # ~4 min
```

Lance ces commandes depuis `Fiche_examen/`.

Dépendances : `numpy scipy scikit-image opencv-python-headless img2pdf pillow` et `pdftoppm` (poppler). Pour une autre « écriture », change `--seed` (réencrage), `math.randomseed` (`manuscrit.lua`) et `\pgfmathsetseed` (tracés).

## Sorties

- **`fiche_integration_sto_realiste_impression.pdf` :** sans quadrillage, à imprimer, idéalement sur papier petits carreaux.
- **`fiche_integration_sto_realiste_quadrille.pdf` :** petits carreaux 5 mm dessinés, pour l'écran ou du papier blanc.

## Conseils d'impression (pour le réalisme)

- **Réglages :** taille réelle (100 %), couleur, recto-verso bord long. Si l'imprimante rogne les bords (marges de 4 mm), choisis « ajuster » (≈ 97 %).
- **Imprimante :** de préférence à jet d'encre. L'encre pénètre le papier comme celle d'un stylo, alors que le toner laser brille légèrement.
- **Papier :** une feuille simple petits carreaux (90 g, passe en imprimante) ou du papier blanc mat.
- **Finition au vrai stylo :** repasse quelques cadres ou soulignements au stylo rouge, ajoute deux ou trois annotations, un coup de surligneur. L'encre réelle (avec le relief du stylo) par-dessus rend la feuille très difficile à distinguer, même de près.
