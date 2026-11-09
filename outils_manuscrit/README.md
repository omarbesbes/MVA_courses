# Outils « fiche vraiment manuscrite »

Ces outils sont communs à deux fiches d'examen :

| Fiche | Source (à compiler depuis son dossier) | Sorties |
| --- | --- | --- |
| Intégration stochastique | `Integration_sto_B/Fiche_examen/fiche_integration_sto_realiste.tex` (police Kalam, stylo bleu) | `fiche_integration_sto_realiste_impression.pdf`, `..._quadrille.pdf` |
| Optimisation | `Opti_CS/Fiche_examen/fiche_opti_realiste.tex` (police Patrick Hand, stylo noir) | `fiche_opti_realiste_impression.pdf`, `..._quadrille.pdf` |

Chaque fiche garde son propre contenu (`fiche_contenu.tex`), partagé avec ses autres versions (imprimée et manuscrite). La fabrication se fait en deux étapes :

```bash
lualatex fiche_xxx_realiste.tex                                   # 1. composition irrégulière
python3 ../../outils_manuscrit/reencrage.py fiche_xxx_realiste.pdf  # 2. réencrage (~2 min/page)
```

## 1. Composition irrégulière (`manuscrit.lua`, chargé par le `.tex`)

- **Espacement :** irrégulier entre les lettres et entre les mots, calculé avant la coupure des lignes. Aucune césure (`\hyphenpenalty=10000`).
- **Lettres :** chaque glyphe (texte, maths, symboles) reçoit sa propre petite rotation, une échelle, une inclinaison et un décalage de ligne de base. Une partie est commune au mot, une partie est propre à la lettre. Les polices non manuscrites (maths) penchent en plus comme l'écriture. Les polices reconnues comme manuscrites se règlent dans `manuscrit.handfonts`, `{ "Kalam", "Patrick" }` par défaut.
- **Tracés à main levée (TikZ, dans chaque `.tex`) :** cadres ou soulignés de titres, étoiles, triangles « ! », flèches, coches, lettres à double barre (𝔼 ℙ ℝ ℤ…).
- **Ratures :** quelques corrections volontaires via `\rature{...}`. La macro est définie vide dans les autres versions des fiches.
- **Encres :** des couleurs « marqueurs », remplacées à l'étape 2 :

| Marqueur | Couleur du marqueur | Stylo final |
| --- | --- | --- |
| noir | (0,0,0) | stylo noir |
| bleu pur | (0,0,255) | stylo bleu |
| rouge pur | (255,0,0) | stylo rouge |
| vert pur | (0,255,0) | stylo vert |
| cyan | (0,255,255) | stylo violet |
| magenta | (255,0,255) | crayon à papier (traits de colonnes) |

## 2. Réencrage (`reencrage.py`)

1. **Séparation des encres :** rendu à 600 dpi, puis séparation des encres d'après les marqueurs.
2. **Déformation élastique :** le même champ s'applique à toutes les encres, à plusieurs échelles :
   - rotation de la feuille, dérive lente des colonnes ;
   - lignes qui ondulent et penchent, avec un début de ligne irrégulier ;
   - mots décalés, forme de chaque lettre légèrement altérée.
3. **Réencrage au stylo :** on extrait le squelette des traits, puis on le repasse avec une pointe de largeur quasi constante, calée sur l'encre majoritaire. Tout a ainsi le même stylo. La largeur varie le long du trait, avec un petit dépôt d'encre aux extrémités. Le gras reste plus épais.
4. **Texture :** pression et grain de l'encre ; crayon grainé.
5. **Composition :** composition soustractive sur blanc **exact** (palette explicite : l'imprimante ne touche pas au fond).

Dépendances : `numpy scipy scikit-image opencv-python-headless img2pdf pillow` et `pdftoppm` (poppler). Pour une autre « écriture », change `--seed` (réencrage), `math.randomseed` (`manuscrit.lua`) et `\pgfmathsetseed` (tracés).

## Conseils d'impression

- **Fichier :** imprime `..._impression.pdf` (sans quadrillage). La version `..._quadrille.pdf` sert à l'écran ou sur papier blanc.
- **Réglages :** taille réelle (100 %), couleur, recto-verso bord long. Si l'imprimante rogne les bords (marges d'environ 4 mm), choisis « ajuster » (≈ 97 %).
- **Imprimante :** de préférence à jet d'encre. L'encre pénètre le papier comme celle d'un stylo, alors que le toner laser brille légèrement.
- **Papier :** une feuille simple petits carreaux (90 g, passe en imprimante) ou du papier blanc mat.
- **Finition au vrai stylo :** repasse quelques soulignés ou cadres, ajoute deux ou trois annotations, un coup de surligneur. L'encre réelle (avec le relief du stylo) par-dessus rend la feuille très difficile à distinguer, même de près.
