# Optimal Transport for ML — study pages, version 2

Step-by-step rewrites of the lectures of the MVA / IASD course *Optimal Transport for Machine Learning*
(J. Delon, G. Peyré), built from the handwritten class notes. Each page quotes what was written on the
board, decodes every symbol, gives the reason before the result, proves each step with its justification,
and tries everything on small numbers — with interactive figures.

**Open `Lesson03.html` in a browser.** The pages are self-contained (formulas, fonts and figures are inlined):
they work offline.

| Page | Content | Source |
|---|---|---|
| `Lesson03.html` | Lesson 3 (14 Oct 2026): $W_p$ is a distance (gluing), comparison of the $W_p$, weak / weak-* / vague convergence, total variation and the 0/1 cost, displacement interpolation and geodesics, Wasserstein barycenters (Diracs, grid LP, Agueh–Carlier, Gaussians and the fixed-point equation, 1D quantiles, fixed-point algorithm), exercises with solutions | `../ressources/3rd course written notes photos/` |

The first companion (one page per lesson, with labs) is in `../companion/`; its Lesson 3 page links here.

The sources are in `_source/` (one HTML fragment per section, style, interactive figures, figure generator).
To rebuild: `cd _source && npm install && python3 figures.py && node build.mjs`. The writing rules are in
`_source/GUIDE.md`.
