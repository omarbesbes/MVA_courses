# Writing guide — Optimal_transport_ML v2

The contract for every v2 page (one page per lesson, plus `Reminders` and the home page `index`).
**The reference implementation is Lesson 3**: `pages/Lesson03/*.html` (text), `widgets/Lesson03.js`
(interactive figures), `figures_L03.py` (static figures). Read it before writing a page, and match its tone,
density and structure.

## 1. The reader and the goal

A master's student (MVA / IASD) who follows the lectures and wants to **understand everything and redo every
argument alone**: the intuition, the meaning of each symbol, step-by-step proofs, small numerical examples,
reflexes for the exam — and **what optimal transport is used for in machine learning**. The student may be
rusty in measure theory, convex analysis and probability: recall what is needed, where it is needed.
The v1 companion (`../companion/LessonNN.html`) is a dense, research-style reference with labs; v2 is the
pedagogical version.

## 2. Writing rules

1. **English**, second person, short sentences. Define a term at its first use (`<em class="new">term</em>`).
2. **Why before how.** Every notion starts with the problem it solves.
3. **Faithful to the course.** Every important statement of the course (definition, theorem, proposition,
   algorithm, exercise) is quoted in a box with its exact reference, then **decoded** symbol by symbol
   (`dl.decode`). Lesson 3 quotes the student's handwritten notes (`board` boxes). The other lessons quote the
   course resources (`course` boxes): the book *Optimal Transport for Machine Learners* (`ressources/OT4ML.pdf`,
   cite as “OT4ML Thm. 2.23, p. 26”: statement number and PDF page), the compact notes
   (`ressources/CourseOT-compact.pdf`), the 2019 notes (`ressources/CourseOT.pdf`), Peyré–Cuturi
   (`ressources/1803.00567v4.pdf`, “CompOT”), Chewi–Niles-Weed–Rigollet (`ressources/2407.18163v2.pdf`, “StatOT”),
   the slides and the exercise sheets (`course material exercices and one slides/`). Do not invent course
   content; what is added for pedagogy is presented as such (intuition, reminder, remark, going further).
4. **Reminders here and there.** Whenever a prerequisite is used (convexity, Jensen, Lagrange duality, KL,
   matrix square roots, change of variables…), recall it on the spot: a short `recall` box titled
   “Reminder — …” saying exactly what is used, with a link to the Reminders page (`Reminders.html#anchor`,
   anchors listed in §8) or to the lesson where it was seen. Also recall results of earlier lessons when they
   are reused (“Reminder — Brenier’s theorem (Lesson 1)”). A student should never have to leave the page to
   follow an argument, but can follow a link to go deeper.
5. **Machine-learning applications.** Each section that has a use in ML gets an `ml` box (“In machine
   learning — …”): what problem it solves, with a concrete example (data, model, loss), and a pointer to the
   reference in the course resources when there is one (the book has many: colour transfer, domain
   adaptation, word mover's distance, Wasserstein GANs, flow matching, diffusion models, Sinkhorn losses,
   single-cell trajectories, two-layer networks, transformers…). At least **four** per lesson. Be concrete
   and correct; no hype.
6. **Step-by-step computations** in `ol.steps`, each line with its justification (`span.why`). Never
   “clearly” or “it is easy to see” without the reason.
7. **Idea before proof:** an `idea` box (3–6 lines), then the full proof in `details.fold.proof`.
8. **A worked example with numbers** for every important notion — small, checkable by hand.
   **Every number on the page is computed by a script before it is written** (Python with numpy / scipy /
   POT, or exact fractions), including exercise answers and numbers quoted from widgets.
9. **Pitfalls** (`pitfall`), **reflexes** (`reflex`, “When you see … → …”), **quick checks** (`quiz`) along the
   way.
10. **Exercises.** The lesson's exercise sheet is **fully solved**: each exercise quoted in a `course` box,
    then a hint (`details.fold.hint`) and a complete solution (`details.fold.sol`). If the sheet's own
    solution has an error, say so gently in a `remark` box with a check. Then 8–12 extra graded exercises
    (★ to ★★★) with hints and solutions.
11. **Notes on the sources.** Typos or convention clashes found in the resources go in a `remark` box (“Note on
    the sources”) and in the list at the end of the page, each with a counter-example or a check.
12. **Lectures not yet given.** Lessons 4–8 are prepared before the lecture, from the resources. Say so in the
    “How to read this page” paragraph; the page must still be complete and self-contained.

## 3. Structure of a lesson page

```
pages/LessonNN/00_intro.html     header comment (see below), objectives box, “Before you start” (h2 id="start"):
                                 how to read this page, the story of the lesson in 5–7 steps (ol.chain),
                                 what you need (folded refreshers + links to Reminders and earlier lessons),
                                 notation decoder (table), colour code of the figures
pages/LessonNN/01_….html …       one file per section (h2), in the order of the lecture; each section:
                                 tldr → problem → course box + decoding → example → idea → proof (fold) →
                                 reminders / ML boxes / pitfalls / reflexes / quick checks
pages/LessonNN/xx_sheet.html     the exercise sheet, fully solved
pages/LessonNN/xx_exercises.html extra exercises
pages/LessonNN/xx_wrapup.html    summary (box summary), formula sheet (table), reflexes (ul.checklist),
                                 machine learning: the applications of this lesson (one table), what comes next,
                                 glossary English–French, sources and notes on the sources
```
Header comment of the first part:
```
<!--
title: Lesson N — Short, telling title
short: LN · keyword
description: one sentence (meta description)
subtitle: what the page covers, one or two sentences
kicker: Optimal Transport for ML · Lesson N · study guide v2
-->
```
Parts are concatenated in file-name order. **Every h2 and h3 has an explicit, stable id** (lower case,
hyphens; the build fails otherwise), unique within the page. Number the h2 (“1. …”, “2. …”) like Lesson 3.

## 4. Components

Formulas: `$...$` inline, `$$...$$` display (rendered by KaTeX at build time); `\$` for a dollar sign. An
inline formula must not contain an empty line. A display formula is never inside a `<p>` (close the
paragraph before `$$`). Split long display formulas with `\begin{aligned} … \\ … \end{aligned}` so that they
fit in the column (the checker reports them). Avoid characters missing from KaTeX's fonts (circled digits…).

Macros: `\R \N \E \P \X \Y \Z \M` ($\mathcal M_1^+$) `\Pc \U \Lc \B` (Bures) `\al \be \ga \eps \TV \KL \Id \tr
\diam \supp \Lip \dv` (divergence) `\argmin \argmax \T \ind \dd \norm{x} \abs{x} \ps{a}{b} \wto \pf{T}{\al}`
($T_\#\alpha$).

```html
<p class="tldr">One sentence that summarises the section.</p>
<div class="box course"><div class="box-h">In the course <span class="ref">OT4ML Thm. 2.23, p. 26</span></div> … faithful quote … </div>
<dl class="decode"><dt>$symbol$</dt><dd>meaning in words</dd> … </dl>
<div class="box recall"><div class="box-h">Reminder — Jensen's inequality</div> … <a href="Reminders.html#norms">more</a></div>
<div class="box ml"><div class="box-h">In machine learning — colour transfer between images</div> … </div>
<div class="box def|thm|intu|example|idea|reflex|pitfall|method|remark|summary|objectives"><div class="box-h">Title</div> … </div>
<ol class="steps"><li>$$ … $$<span class="why">why this line is true</span></li></ol>
<details class="fold proof|hint|sol|more"><summary>Full proof</summary><div class="fold-body"> … </div></details>
<div class="exo"><div class="exo-h">Exercise N — Title <span class="lvl">★★</span></div> … </div>
<div class="quiz"><p>Question?</p><details class="fold sol"><summary>Answer</summary><div class="fold-body">…</div></details></div>
<div class="cols"> … </div>   <div class="table-wrap"><table> … </table></div>   <ol class="chain"> … </ol>
```
Links: other v2 lessons as `LessonNN.html` (an anchor only if it already exists — Lesson 3's do); the
Reminders page as `Reminders.html#anchor` (§8); the v1 companion as `../companion/LessonNN.html#id`; resources
as `../ressources/…` (paths must exist).

## 5. Figures

**Static figures**: written by `figures_LNN.py`, which imports `figures_common` (classes `Fig`, `Canvas`) and
writes `figures/LNN/*.svg` (`Canvas(name, W, H, label, sub="LNN")`); included with
`<figure class="fig"><!-- include figures/LNN/name.svg --><figcaption>…</figcaption></figure>`.
Compute every coordinate in the script. Colours are CSS classes only (strokes `c1…c6`, fills `f1…f6`, washes
`a1…a5`, text `tx tx-s tx-b tx-i`, text colours `t1 t2 t3 t5`), so that figures follow the light and dark
themes. Colour code of the course: **source α = 2 (orange-red), target β = 1 (blue), third measure γ = 5
(purple), maps / interpolations / barycenters = 3 (green)**, mixtures and total variation = grey.
Use Unicode in SVG text (αₜ, W₂, √, ∜, …), never `_` or `^`. At least six figures per lesson.

**Interactive figures**: `widgets/LessonNN.js`, a code fragment inserted by the build inside the scope of
`app.js`, which registers `WIDGETS.name = function (box) { … }` (`name` unique in the whole site; prefix it,
e.g. `l5slices`). Use the helpers of `app.js`: `el`, `fmt`, `Plot` (axes, poly, fn, dot, seg, text, clip),
`scaffold`, `slider`, `select`, `button`, `checkbox`, `readout`, `legend`, `addSvg`, `svgPoint`, `frac`,
`matStr`, `mulberry32`, `gaussRand`, `monotonePlan`, `planCost`, `gpdf`, `updf`, `Line1D`, `MQ`/`US`,
`quantiles`, `w2q`, `densityFromQ`, `curve`, `areaPts`, `mmul`, `msym`, `msqrt`, `minv`, `bures`,
`ellipsePts`, `WeightTriangle`, `hungarian`, `redrawers`. **Never redefine one of these names**; prefix your
own helpers (e.g. `l5sort`). Place with `<div class="widget" data-widget="name"><p class="w-noscript">Interactive
figure (needs JavaScript).</p></div>`, followed by a paragraph “What to look at: …”. At least three per lesson.
Pitfalls of the helpers: `new Plot(svg, …)` and `Plot.clear()` empty the whole `svg` (two panels in one svg need
one `Plot` whose `g` you switch by hand, or plain `el` drawing); `svg .ln` sets `stroke-width` in CSS, which beats a
`stroke-width` attribute, so variable widths must be inline styles (`style: "stroke-width:3px"`); `fmt` prints
“—” for NaN and ±∞ for infinities.

## 6. Build and check

```
cd Optimal_transport_ML/v2/_source
python3 figures_LNN.py                     # static figures of the lesson
node build.mjs LessonNN.html               # fast: renders only this page; fails on any KaTeX error,
                                           # heading without id, broken anchor, JS syntax error
node tools/check_page.cjs LessonNN.html --shots /tmp/…/shots_LNN
                                           # console errors, widgets drawn, overflowing formulas,
                                           # phone width; screenshots of every figure and widget
```
Look at every screenshot (light and dark) and fix overlapping labels, clipped text, empty plots.

## 7. Files, and working in parallel

Several lessons are written at the same time. A writer only creates or edits **its own files**:
`pages/LessonNN/`, `widgets/LessonNN.js`, `figures_LNN.py`, `figures/LNN/`. Shared files (`app.js`,
`style.css`, `build.mjs`, `template.html`, `figures_common.py`, `GUIDE.md`, other pages) are not edited by
writers; ask for a change in the final report instead. No git operations.

## 8. Anchors of the Reminders page (fixed)

`measures` (`measures-basics`, `pushforward`, `couplings`, `conditional`, `convergence`) ·
`oned` (`cdf-quantile`, `sorting`) · `linalg` (`spd`, `sqrtm`, `gaussians`, `permutations`) ·
`analysis` (`norms`, `lipschitz`, `jacobian`, `divergence`, `ode`, `continuity-eq`) ·
`convex` (`convex-functions`, `legendre`, `lagrange`, `lp`, `gradient-descent`, `first-variation`) ·
`information` (`entropy`, `f-divergences`, `bregman`) · `kernels` (`mmd`) ·
`stochastic` (`brownian`, `fokker-planck`) ·
`ot-recap` (`ot-monge`, `ot-kantorovich`, `ot-wasserstein`, `ot-duality`, `ot-closed-forms`).

## 9. Notation common to all lessons

$\al,\be$ probability measures (source, target), $\ga$ a third one; $\X,\Y$ spaces; $c$ a cost, $d$ a distance;
$\pf{T}{\al}$ push-forward; $\U(\al,\be)$ couplings; $\Lc(\al,\be)$ the Kantorovich cost; $W_p$ Wasserstein;
$a,b$ histograms (weights), $P$ or $\pi$ a plan, $C$ a cost matrix, $\ps{P}{C}=\sum_{ij}P_{ij}C_{ij}$;
$C_\al$, $C_\al^{-1}$ CDF and quantile function; $\N(m,\Sigma)$ Gaussian, $\B$ Bures distance;
$f,g$ dual potentials (Lessons 4, 7), $\eps$ entropic regularization (Lesson 7).
When a lesson's sources use another notation, the notation decoder of the page says so.
