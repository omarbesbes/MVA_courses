# Statistiques avancées 3A — version pédagogique (v2)

Guide d'étude du cours de S. Lemler, réécrit pour quelqu'un qui reprend les statistiques : intuition,
calculs ligne par ligne, idées de preuve puis preuves complètes, rappels des prérequis sur place, réflexes,
exercices corrigés, et les TD corrigés pas à pas.

**Ouvrir `index.html` dans un navigateur.** Les pages sont autonomes (formules, polices et figures incluses) :
elles fonctionnent hors connexion.

| Page | Contenu |
|---|---|
| `index.html` | mode d'emploi, l'histoire du cours en une page |
| `00_rappels.html` | la boîte à outils : algèbre linéaire, optimisation, probabilités, statistique |
| `01_seance1.html` … `06_seance6.html` | une page par séance (la Séance 5 suit la version 2026 des diapos GLM, la Séance 4 intègre les preuves manuscrites de la professeure) |
| `08_td1.html`, `09_td2.html`, `10_td3.html` | les TD : énoncé, méthode, indice, solution détaillée, comparaison avec le corrigé officiel |
| `07_fiche.html` | fiche réflexes et formulaire |
| `11_revision.html` | **révision pour l'examen** : tout le cours et les TD triés en « par cœur », « à savoir refaire », « à comprendre » ; plan sur deux jours, mode auto-test (formules floutées), théorèmes et hypothèses, preuves express, pièges, questions par séance |
| `Revision_examen_StatA.pdf` | la page de révision en PDF A4, preuves et réponses dépliées (pour imprimer) |
| `Revision_essentiel_StatA.pdf` | les synthèses seulement (cours en une page, conventions, théorèmes, preuves, pièges, jour J), pour la dernière relecture |

Sources : `../Cours1.pdf` … `../Cours6.pdf`, `../Cours5_enrichi_annote.pdf`, `../Preuves_cours 4.pdf`,
`../TD_et_correction/`.

Les sources des pages sont dans `_source/` (fragments HTML, style, figures interactives) ; pour reconstruire :
`cd _source && npm install && node build.mjs`, puis `node pdf.mjs` pour les deux PDF (demande Playwright).
Les règles de rédaction sont dans `_source/GUIDE.md`.
