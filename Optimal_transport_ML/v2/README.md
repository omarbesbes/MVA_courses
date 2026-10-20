# Optimal Transport for ML — study guide, version 2

A step-by-step study guide for the MVA / IASD course *Optimal Transport for Machine Learning*
(J. Delon, K. Nadjahi, G. Peyré): one page per lesson, written to be understood without help. Each page
quotes the course (book, notes, exercise sheets; the class notes for Lesson 3), decodes every symbol, gives
the reason before the result, proves each step with its justification, tries everything on small numbers,
recalls the prerequisites where they are used, and shows where each idea is used in machine learning. The
exercise sheet of every lesson is solved in full. Interactive figures let you move things and watch.

**Open `index.html` in a browser.** The pages are self-contained (formulas, fonts and figures are inlined):
they work offline.

| Page | Content |
|---|---|
| `index.html` | How to use the guide, the eight lessons, a map of OT in machine learning, notation, resources |
| `Reminders.html` | The prerequisites, recalled from scratch: measures, the line, linear algebra and Gaussians, analysis, convexity and duality, information theory, kernels, stochastic processes, and the OT facts every lesson reuses |
| `Lesson01.html` | Monge: assignment, sorting on the line, push-forwards, Monge maps, Brenier's theorem, Gaussians |
| `Lesson02.html` | Kantorovich: couplings, the linear program, Birkhoff–von Neumann, when plans and maps agree |
| `Lesson03.html` | Wasserstein distances (rebuilt from the class notes of 14 Oct 2026): metric, convergence, total variation, geodesics, barycenters; the continuous Kantorovich sheet |
| `Lesson04.html` | Duality: potentials, complementary slackness, $c$-transforms, Kantorovich–Rubinstein, GANs |
| `Lesson05.html` | Sliced optimal transport |
| `Lesson06.html` | Dynamic OT, Benamou–Brenier, flow matching |
| `Lesson07.html` | Entropic OT and Sinkhorn |
| `Lesson08.html` | Wasserstein gradient flows, JKO, diffusion, two-layer networks |

Lesson 3 follows the handwritten notes of the lecture (`../ressources/3rd course written notes photos/`).
Lessons 1–2 were rebuilt from the course resources; Lessons 4–8 were prepared before the lectures, from the
same resources.

The first companion (one page per lesson, with numerical labs) is in `../companion/`; its pages link here.

## Sources and rebuilding

The sources are in `_source/`: one folder of HTML fragments per page (`pages/<Page>/`), the shared style and
scripts (`style.css`, `app.js`, `template.html`), one widget file per lesson (`widgets/LessonNN.js`), and one
figure generator per lesson (`figures_LNN.py`, writing `figures/LNN/*.svg`). The writing rules are in
`_source/GUIDE.md`.

```
cd _source
npm install                      # KaTeX, used at build time only
python3 figures_L03.py           # one generator per lesson (numpy)
node build.mjs                   # all pages; or: node build.mjs Lesson03.html
node tools/check_page.cjs Lesson03.html --shots /tmp/shots   # headless checks and screenshots (Playwright)
```
