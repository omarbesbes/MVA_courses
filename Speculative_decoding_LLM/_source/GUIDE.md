# Writing guide — Speculative_decoding_LLM

The contract for every page of the guide. **The reference implementation is page 1**:
`pages/01_foundations/*.html` (text), `widgets/01_foundations.js` (interactive figures), `figures_01.py`
(static figures). Read it before writing a page, and match its tone, density and structure.

## 1. The reader and the goal

A master's student (MVA level) who knows what a language model and a softmax are, and wants to **understand
speculative decoding completely**: why it works, what the exact algorithm guarantees, where its ceiling is, and
above all **what each lossy (approximate) method tries and what it achieves**. The reader should be able to
redo every derivation alone, read any paper of the field afterwards, and choose a method for a given setting.
The pages must be interesting to read: a clear story, small numbers to compute, figures to play with.

## 2. Writing rules

1. **English**, second person, short sentences. Define a term at its first use (`<em class="new">term</em>`).
2. **Why before how.** Every method starts with the problem it attacks, in one or two sentences.
3. **Faithful to the papers.** The source of truth is the folder of research notes
   (`notes/*.md`, next to this file: one file per topic, facts marked VERIFIED or [V],
   each with a quote and a URL). Every important statement of a paper (rule, theorem, headline result) is quoted in
   a `paper` box with its exact reference (authors, year, section / table / figure), then **decoded** symbol by
   symbol (`dl.decode`). Never write a number, a venue, a model name or a formula of a paper that is not in the
   notes as VERIFIED; if you need a fact that is missing, check the primary source yourself (arXiv abstract or
   HTML page) and list it in your final report. What you add for pedagogy (intuition, toy example, analogy,
   derivation on a small vocabulary) is presented as such, never attributed to a paper.
4. **One notation for the whole guide** (§9). Papers swap letters (some call the target $q$ and the draft $p$):
   translate everything to the notation of the guide and say so in the decoding (“the paper writes … for our …”).
5. **What it tries / what it achieves.** Every method gets a **method card** (`article.mcard`, §4) with four
   rows: what it tries, how it decides, what it achieves, what it costs. “What it achieves” gives the numbers
   reported by the authors **with their setting** (target and draft models, task, hardware or metric, baseline).
   Speedups of different papers are **never** compared in a chart or ranked in a sentence: models, tasks,
   hardware and baselines differ. Say “the authors report”, not “the method gives”.
6. **Lossless or lossy, precisely.** For each method say what is preserved: the output distribution of the
   target (lossless), only its greedy output, or nothing provable (lossy), and what is known about the bias.
7. **Step-by-step computations** in `ol.steps`, each line with its justification (`span.why`). Never “clearly”
   or “it is easy to see” without the reason. **Idea before proof:** an `idea` box (3–6 lines), then the full
   proof in `details.fold.proof`.
8. **A worked example with numbers** for every rule — a vocabulary of 3 to 6 tokens, checkable by hand.
   **Every number of a toy example is computed by a script before it is written** (Python, exact fractions when
   possible). Toy numbers are announced as toy numbers; they are never presented as model outputs.
9. **Pitfalls** (`pitfall`), **reflexes** (`reflex`, “When you see … → …”), **quick checks** (`quiz`) along the
   way; “in practice” boxes (`practice`) for what a serving stack does; reminders (`recall`) for prerequisites,
   with a link to the page of the guide where the notion was introduced.
10. **Exercises** at the end of each page: 6–10, graded ★ to ★★★, each with a hint (`details.fold.hint`) and a
    complete solution (`details.fold.sol`).
11. **No hype, no filler.** No “revolutionary”, “game-changing”. If the evidence for a method is thin (one
    paper, small benchmarks, no code), say it. If papers disagree, show both.
12. **Sources at the end of each page**: the papers cited on the page, with authors, title, venue, year and a
    link to the arXiv abstract (`https://arxiv.org/abs/…`).

## 3. Structure of a page

```
pages/NN_name/00_intro.html      header comment (see below), objectives box, “Before you start” (h2 id="start"):
                                 how to read this page, the story of the page in 5–7 steps (ol.chain),
                                 what you need (links to earlier pages), notation used on the page
pages/NN_name/01_….html …        one file per section (h2), in the order of the story; each method (h3):
                                 tldr → method card → the problem → paper box + decoding → toy example →
                                 idea → proof or derivation (fold) → pitfalls / reflexes / quick checks
pages/NN_name/xx_exercises.html  exercises with hints and solutions
pages/NN_name/xx_wrapup.html     summary (box summary), one comparison table of the methods of the page,
                                 reflexes (ul.checklist), what comes next, glossary, sources
```
Header comment of the first part:
```
<!--
title: N — Short, telling title
short: N · keyword
description: one sentence (meta description)
subtitle: what the page covers, one or two sentences
-->
```
Parts are concatenated in file-name order. **Every h2 and h3 has an explicit, stable id** (lower case,
hyphens; the build fails otherwise), unique within the page. Number the h2 (“1. …”, “2. …”) like page 1.

## 4. Components

Formulas: `$...$` inline, `$$...$$` display (rendered by KaTeX at build time); `\$` for a dollar sign. An
inline formula must not contain an empty line. A display formula is never inside a `<p>` (close the paragraph
before `$$`). Split long display formulas with `\begin{aligned} … \\ … \end{aligned}` so that they fit in the
column (the checker reports them). Formulas inside `<code>` and `<pre>` are not rendered. Inside a formula, write `<` and `>` as they are
(`$\al>c$`, `$x_{<t}$`), never as `&lt;` / `&gt;`; outside formulas use the entities.

Macros: `\R \E \P \V` (vocabulary) `\al \be \ga \eps \TV \KL \JS \Hent` (entropy) `\Mp \Mq` (target and draft
models) `\argmin \argmax \softmax \ind \dd \norm{x} \abs{x} \pos{x}` ($(x)_+$) `\tok{cat}` (a token, in monospace).

```html
<p class="tldr">One sentence that summarises the section.</p>

<article class="mcard">
  <header class="mcard-h">
    <p class="mcard-name">Judge Decoding</p>
    <p class="mcard-meta">Bachmann et al. · ICLR 2025 · <a href="https://arxiv.org/abs/2501.19309">arXiv 2501.19309</a></p>
    <p class="tags"><span class="tag lossy">lossy</span><span class="tag train">trained judge</span><span class="tag unit">token level</span></p>
  </header>
  <dl class="mfacts">
    <dt class="tries">What it tries</dt><dd>…</dd>
    <dt class="how">How it decides</dt><dd>…</dd>
    <dt class="gets">What it achieves</dt><dd>… numbers with their setting and reference …</dd>
    <dt class="costs">What it costs</dt><dd>…</dd>
  </dl>
</article>
```
Tags: `lossless` · `greedy` (lossless for greedy decoding only) · `lossy` · `train` (something is trained) ·
`free` (training-free) · `unit` (token level / block level / step level / routing) · `year`.

```html
<div class="box paper"><div class="box-h">In the paper <span class="ref">Leviathan et al. 2023, Algorithm 1</span></div> … faithful quote … </div>
<dl class="decode"><dt>$symbol$</dt><dd>meaning in words</dd> … </dl>
<div class="box recall"><div class="box-h">Reminder — total variation</div> … <a href="01_foundations.html#tv">page 1</a></div>
<div class="box practice"><div class="box-h">In practice — …</div> … </div>
<div class="box def|thm|intu|example|idea|reflex|pitfall|method|remark|summary|objectives"><div class="box-h">Title</div> … </div>
<ol class="steps"><li>$$ … $$<span class="why">why this line is true</span></li></ol>
<details class="fold proof|hint|sol|more"><summary>Full proof</summary><div class="fold-body"> … </div></details>
<div class="exo"><div class="exo-h">Exercise N — Title <span class="lvl">★★</span></div> … </div>
<div class="quiz"><p>Question?</p><details class="fold sol"><summary>Answer</summary><div class="fold-body">…</div></details></div>
<div class="cols"> … </div>   <div class="table-wrap"><table> … </table></div>   <ol class="chain"> … </ol>

<!-- a sequence of tokens: p = from the target, q = drafted, ok = accepted, no = rejected, fix = correction by the
     target, lax = accepted only by a relaxed rule, dim = discarded, ctx = context -->
<div class="toks"><span class="lab">draft</span><span class="tok ok">The</span><span class="tok ok"> cat</span><span class="tok no"> sat</span><span class="tok dim"> on</span></div>

<!-- pseudo-code: one <li> per line, classes in1 / in2 / in3 indent -->
<div class="algo"><div class="algo-h">Algorithm — one round</div><ol>
  <li><span class="kw">for</span> $i=1,\dots,\ga$: …</li><li class="in1">… <span class="cm">comment</span></li></ol></div>

<!-- a handful of numbers from ONE paper in ONE setting (never across papers); widths are % of the largest value -->
<div class="hbars" role="img" aria-label="…"><span class="hb-l">Standard verification</span><span class="hb-t"><i class="base" style="--v:31%"></i></span><span class="hb-v">6.3</span> … </div>
<p class="hbars-cap">Tokens accepted per target call. Setting and reference.</p>

<span class="sw p"></span>target &nbsp; <span class="sw q"></span>draft   <!-- colour keys: p q ok lax fix no -->
```
Links: other pages as `NN_name.html#anchor` (only the anchors listed in §8, or anchors of page 1, which exists);
papers as `https://arxiv.org/abs/…` (the build opens external links in a new tab).

## 5. Figures

**Colour code of the guide** (by entity, never by rank): target model $p$ = 1 (blue), draft model $q$ = 2
(orange-red), accepted = 3 (green), relaxed / lossy zone = 4 (amber), correction or residual = 5 (purple),
rejected = 6 (pink). Text never wears a series colour: labels are in text colours, a coloured mark beside them
carries the identity. A legend is present whenever a figure has two series or more.

**Chart rules** (they come from a checklist that was run on this palette — do not change colours):
thin marks (bars at most 24 px wide, rounded at the data end only; lines 2 px; markers with a ring); solid
hairline grids (dashes are reserved for thresholds); **one y-axis** per plot, never two scales; direct labels
only for the one or two values the figure is about; every interactive chart has a hover/focus tooltip **and**
a table view (`tableView`), so that no value is reachable by hover only. Numbers from different papers never
share a chart.

**Static figures**: written by `figures_NN.py`, which imports `figures_common` (classes `Fig`, `Canvas`) and
writes `figures/NN/*.svg` (`Canvas(name, W, H, label, sub="NN")`); included with
`<figure class="fig"><!-- include figures/NN/name.svg --><figcaption>…</figcaption></figure>`.
Compute every coordinate in the script. Colours are CSS classes only (strokes `c1…c6`, `ck`, `cm`; fills
`f1…f6`, `fk`, `fm`, `fs`; washes `a1…a6`, `am`; text `tx tx-s tx-b tx-i tx-m`), so that figures follow the
light and dark themes. `Canvas` has helpers for diagrams: `box(x, y, w, h, lines, k)`, `chip(x, y, w, h, s, k,
strike)`, `arrow(x1, y1, x2, y2, k)`, `rect`, `line`, `path`, `text`. Use Unicode in SVG text (α, γ, ≤, ×),
never `_` or `^`. At least three static figures per page (diagrams of the control flow are the most useful).

**Interactive figures**: `widgets/NN_name.js`, a code fragment inserted by the build inside the scope of
`app.js`, which registers `WIDGETS.name = function (box) { … }` (`name` unique in the whole guide; prefix it
with the page, e.g. `p3rulelab`). Helpers of `app.js` (never redefine these names; prefix your own helpers):
`el`, `fmt`, `pct`, `Plot` (methods `axes`, `poly`, `area`, `fn`, `dot`, `seg`, `text`, `bar(xc, dx, wpx, y,
cls)`, `clip`, `unclip`, `crosshair(xs, rowsAt)`, `tx`, `ty`, `ix`, `iy`, `clear`), `svgPoint`, `tipShow`,
`tipHide`, `hoverable(node, info, marks)`, `scaffold`, `slider`, `select`, `button`, `checkbox`, `readout`,
`legend`, `tableView`, `redrawers`, `frac`, `mulberry32`, `gaussRand`, `addSvg`, `normalize`, `overlap`,
`tvDist`, `klDiv`, `jsDiv`, `entropy`, `argmaxIndex`, `sampleIndex`, `residual`, `setBar`, `dragBars`.
Place with `<div class="widget" data-widget="name"><p class="w-noscript">Interactive figure (needs
JavaScript).</p></div>`, followed by a paragraph “What to look at: …”. At least two per page.
Pitfalls of the helpers: `new Plot(svg, …)` and `Plot.clear()` empty the whole `svg`; `svg .ln` sets
`stroke-width` in CSS, which beats a `stroke-width` attribute, so variable widths must be inline styles;
`fmt` prints “—” for NaN; labels built from data go through `textContent`, never `innerHTML`; push your
redraw function to `redrawers` only if the drawing depends on the theme.

## 6. Build and check

```
cd Speculative_decoding_LLM/_source
python3 figures_NN.py                      # static figures of the page
node build.mjs NN_name.html                # fast: renders only this page; fails on any KaTeX error,
                                           # heading without id, broken anchor, JS syntax error
node tools/check_page.cjs NN_name.html --shots <scratch>/shots_NN
                                           # console errors, widgets drawn, overflowing formulas and boxes,
                                           # phone width; screenshots of every figure and widget
```
Look at every screenshot (light and dark) and fix overlapping labels, clipped text, empty plots.

## 7. Files, and working in parallel

Several pages are written at the same time. A writer only creates or edits **its own files**:
`pages/NN_name/`, `widgets/NN_name.js`, `figures_NN.py`, `figures/NN/`. Shared files (`app.js`, `style.css`,
`build.mjs`, `template.html`, `figures_common.py`, `GUIDE.md`, other pages) are not edited by writers; ask for
a change in the final report instead. No git operations.

## 8. Pages and fixed anchors

| Page | File | Content |
|---|---|---|
| Home | `index.html` | how to read, the story in one page, the map of methods, the summary table |
| 1 | `01_foundations.html` | the exact algorithm: draft, verify, accept; proof; speed-up law; the ceiling |
| 2 | `02_lossless.html` | the lossless frontier: better drafts, trees, block verification, adaptive length, systems |
| 3 | `03_relaxed.html` | lossy I: relaxing the acceptance test with a statistical rule; the trade-off theory |
| 4 | `04_judges.html` | lossy II: judging correctness instead of agreement (learned and training-free judges) |
| 5 | `05_reasoning.html` | lossy III: speculating on reasoning steps; token routing; the border with cascades |
| 6 | `06_practice.html` | beyond text, evaluation, deployment, risks, a decision guide, open problems |

Anchors that other pages may link to (they must exist with exactly these ids):

- `01_foundations.html`: `start`, `slow`, `asymmetry`, `greedy`, `rule`, `rule-proof`, `tv`, `optimal`,
  `greedy-case`, `rounds`, `expected-tokens`, `speedup`, `speedup-limits`, `ceiling`, `exercises`, `sources`.
- the anchors of pages 2–6 are listed in §10 (filled in when the plan of each page is fixed).

## 9. Notation common to all pages (the notation of Leviathan et al. 2023)

- $\Mp$: the **target model** (large, slow), the one whose output we want; $p(x)=p(x\mid x_{<t})$ its next-token
  distribution after the current prefix. $\Mq$: the **draft model** (small, fast; “approximation model”,
  “drafter”, “assistant”); $q(x)$ its next-token distribution. $\V$: the vocabulary.
- $\ga$: the number of tokens drafted per round (draft length, “lookahead”). A **round** = one draft of $\ga$
  tokens + one parallel call of the target.
- $\be$: the probability that a drafted token is accepted, for a given prefix; $\al=\E[\be]$ the average
  **acceptance rate**. $c$: the **cost coefficient**, time of one call of $\Mq$ divided by the time of one call
  of $\Mp$.
- $\TV(p,q)=\frac12\sum_x\abs{p(x)-q(x)}=1-\sum_x\min(p(x),q(x))$ (total variation; Leviathan et al. write $D_{LK}$).
- Tokens accepted per round and tokens generated per target call are different quantities (the second counts
  the extra token given by the target): always say which one a number is.
- Logarithms are natural unless stated; entropy $\Hent(p)=-\sum_xp(x)\log p(x)$.
