# Speculative decoding for LLMs — from the exact algorithm to lossy verification

A step-by-step study guide to **speculative decoding**: a small, fast model writes a draft, the large model
checks it in one parallel pass, and the text comes out several times faster. The guide starts from scratch
(why decoding is slow, the exact accept / resample rule and its proof, the speed-up law) and then concentrates
on the **state of the art in lossy speculative decoding**: for every approach, *what it tries* and *what it
achieves*, with the numbers reported by the authors and the setting in which they were measured.

**Open `index.html` in a browser.** The pages are self-contained (formulas, fonts and figures are inlined):
they work offline.

| Page | Content |
|---|---|
| `index.html` | How to read the guide, the story in one page, the map of the methods, the summary table “what it tries / what it achieves” |
| `01_foundations.html` | The exact algorithm: why decoding is slow, draft-then-verify, the accept / resample rule and its proof, acceptance rate = overlap of two distributions, tokens per round, the speed-up law, the ceiling |
| `02_lossless.html` | The lossless frontier: trained drafters, drafting heads (Medusa, the EAGLE line), lookups, trees of candidates, block verification, adaptive draft length, what happens on a loaded server |
| `03_relaxed.html` | Lossy I — relaxing the acceptance test with a statistical rule: lenience, top-k and margin rules, BiLD, typical acceptance, mentored decoding, fuzzy speculative decoding, speculative cascades, and the theory of the speed / fidelity trade-off |
| `04_judges.html` | Lossy II — judging correctness instead of agreement: Judge Decoding, AutoJudge and their successors, training-free semantic verification |
| `05_reasoning.html` | Lossy III — speculating on reasoning steps (reward-guided speculative decoding, SpecReason, Lookahead Reasoning…), token-level routing between a small and a large model, and the border with cascades |
| `06_practice.html` | Beyond text (images, actions, speech), how to evaluate a lossy method honestly, what is deployed, risks (watermarks, side channels), a decision guide, open problems |

Each page follows the same pattern: the problem before the method, the statement of the paper quoted with its
reference and decoded symbol by symbol, a toy example with numbers you can check by hand, the idea of the proof
and then the proof, pitfalls, quick checks, exercises with solutions, and interactive figures (drag the
probability bars, move the thresholds, watch the acceptance rate and the bias).

**About the numbers.** Every number attributed to a paper was checked against the paper (sources read in
November 2026) and is given with its setting. Speed-ups from different papers are not comparable (different
models, tasks, hardware and baselines) and are never ranked against one another. Numbers in toy examples are
computed by scripts and announced as toy numbers.

## Sources and rebuilding

The sources are in `_source/`: one folder of HTML fragments per page (`pages/<page>/`), the shared style and
scripts (`style.css`, `app.js`, `template.html`), one widget file per page (`widgets/<page>.js`), one figure
generator per page (`figures_NN.py`, writing `figures/NN/*.svg`), and the research notes the pages were written
from (`notes/`: one file per topic, each fact with a quotation and a link). The writing rules are in
`_source/GUIDE.md`.

```
cd _source
npm install                      # KaTeX, used at build time only
python3 figures_01.py            # one generator per page (numpy)
node build.mjs                   # all pages; or: node build.mjs 01_foundations.html
node tools/check_page.cjs 01_foundations.html --shots /tmp/shots   # headless checks and screenshots (Playwright)
```
