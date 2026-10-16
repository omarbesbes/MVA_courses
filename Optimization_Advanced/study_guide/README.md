# LSD study guide

Study guide for the MVA course **Foundations of Distributed and Large Scale Computing Optimization** (E. Chouzenoux, J.-C. Pesquet; TA L. Girometti), written from the official slides, the TD correction and the lab subjects stored in the parent folder.

Open `index.html` in a browser (no server needed; everything, including KaTeX, is local).

| page | content |
|---|---|
| `index.html` | the course map, how to use the guide, the one principle behind everything, dependency graph, notation, resources, exam preparation |
| `01_convex_analysis.html` | Parts I–II: Hilbert spaces, lsc, existence, convexity |
| `02_subdifferential_conjugate.html` | Part III: subdifferential, calculus, conjugate, support functions, Fenchel–Young |
| `03_proximity_operator.html` | Part IV: proximity operator, cookbook, Moreau decomposition |
| `04_fixed_point_forward_backward.html` | Part V: Fejér sequences, Krasnosel'skii–Mann, averaged operators, Forward–Backward, projected gradient, proximal point |
| `05_douglas_rachford_ppxa.html` | Part V / V.2: Douglas–Rachford, parallel DR, PPXA+ |
| `06_duality_admm_primal_dual.html` | Fenchel–Rockafellar duality, Lagrangian, ADMM, primal-dual algorithms |
| `07_majorization_minimization.html` | Part VI: Majorization–Minimization, half-quadratic, 3MG, block-coordinate, variable-metric FB |
| `08_labs.html` | the five labs worked theoretically |
| `09_toolbox.html` | the 22 recurring tricks, algorithm chooser, proof patterns, cheat-sheets |
| `10_memorize.html` | skeleton, flashcards, minimal pairs, counterexamples, quiz, exam-style problems |

Each result is a card: statement, "in one sentence", why it is true, proof (step by step, tricks named), what each hypothesis buys, pitfalls, an interactive visualization when it helps, a "to remember" line, and links to what it uses and what uses it. Hover a dotted link to see the statement it points to. Tick "known" on a card when you can restate it from memory (saved in your browser).

`tools/` contains the scripts used to build the cross-reference registry and to validate the pages in a headless browser:

```
python3 tools/build_registry.py --check     # rebuild assets/registry.js, check ids and links
node tools/validate.js --all                # KaTeX errors, widget rendering, console errors (needs playwright)
python3 tools/extract_outline.py            # Markdown outline of all pages
```
