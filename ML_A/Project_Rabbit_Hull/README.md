# Into the Rabbit Hull: a critical study of the Minkowski representation hypothesis

Student project (MVA, ML-A) on *Into the Rabbit Hull: From Task-Relevant Concepts in DINO to Minkowski Geometry*
(Fel, Wang et al., ICLR 2026, arXiv:2510.08638). The paper proposes that a DINOv2 token is a sum of convex
mixtures of archetypes (the Minkowski representation hypothesis, MRH). The project reads Part III of the paper
critically: it nests the linear hypothesis in the MRH, delimits the attention argument, shows what the final
layer normalisation excludes, tests the three empirical signatures against null models, examines the
identifiability result, and tests additivity on the one observable factor, token position. Toy experiments and
DINOv2 experiments support each point.

## Deliverables

| What | Path |
|---|---|
| Report | `report/report.pdf` (source `report/report.tex`, bibliography `report/refs.bib`) |
| Slides (11 + 3 backup) | `slides/slides.pdf` (source `slides/slides.tex`) |
| Speaker notes | `slides/speaker_notes.md` |
| Study guide | `guide/index.html`, to open in a browser; the other pages are linked from it |

Pages of the guide (all in `guide/`):

| Page | Content |
|---|---|
| `index.html` | the paper in three sentences, how to use the guide, table of claims and verdicts, map of the paper |
| `01_background.html` | vision transformers, DINOv2, interpretability, dictionaries |
| `02_toolbox.html` | mathematical tools: frames, convex sets, Minkowski sums, softmax, archetypal analysis, graphs, attribution |
| `03_concepts_tasks.html` | Part I of the paper: concepts and tasks |
| `04_statistics_geometry.html` | Part II: statistics and geometry of the dictionary, position |
| `05_minkowski.html` | Part III: the hypothesis, the attention argument, the evidence, the implications |
| `06_critical_reading.html` | the project's own analysis, with the experiments behind it |
| `07_selftest.html` | self-test, the talk, glossary |

## Layout of `code/`

| Folder | Content |
|---|---|
| `code/toy/` | toy experiments T1 to T4 on synthetic data |
| `code/dino/` | DINOv2 experiments R0 to R7 |
| `code/rh/` | shared modules: archetypal analysis, interpolation test, null models, DINOv2 loading, plot style |
| `code/figures/` | scripts of the report figures (`fig_*.py`) and of the slide figures (`talk_*.py`) |
| `code/results/` | JSON and NPZ results, with `README_toy.md` and `README_dino.md` describing every field |
| `code/tests/` | tests of the shared modules (`test_core.py`) |

Experiments, scripts and results (scripts are run from `code/`; results in `code/results/`):

| Experiment | Script | Results file |
|---|---|---|
| T1 chord test on four supports | `toy/t1_chords.py` | `t1_chords.json`, `.npz` |
| T2 archetypal analysis between PCA and k-means | `toy/t2_sandwich.py` | `t2_sandwich.json`, `.npz` |
| T3 union of triangles against sum of two triangles | `toy/t3_sum_union.py` | `t3_sum_union.json`, `.npz` |
| T4 hexagon and the gap in the identifiability proof | `toy/t4_hexagon.py` | `t4_hexagon.json`, `.npz` |
| R0 feature extraction and image lists | `dino/r0_extract.py` | `r0_image_lists.json` (features go to the cache) |
| R1 final layer normalisation puts tokens on an ellipsoid | `dino/r1_layernorm_ellipsoid.py` | `r1_layernorm_ellipsoid.json` |
| R2 interpolation test with null models | `dino/r2_interpolation_nulls.py` | `r2_interpolation_nulls.json` |
| R3 per-image archetypal analysis in its sandwich | `dino/r3_aa_sandwich.py` | `r3_aa_sandwich.json` |
| R3b within-image variance (errors in the paper's units) | `dino/r3b_within_variance.py` | `r3_within_variance.json` |
| R4 residual decomposition and attention statistics | `dino/r4_attention_anatomy.py` | `r4_attention_anatomy.json` |
| R5 global archetypes: co-activation against image identity | `dino/r5_coactivation.py` | `r5_coactivation.json`, `.npz` |
| R6 is the position code additive? | `dino/r6_position_additive.py` | `r6_position_additive.json` |
| R6b 2-D view of the position table | `dino/r6b_position_plane.py` | `r6_position_plane.npz` |
| R7 position across depth | `dino/r7_position_layers.py` | `r7_position_layers.json` |

R8 (PCA maps) was not run.

## Data and model

- Model: DINOv2 ViT-B/14 with 4 registers (`dinov2_vitb14_reg`, LVD-142M weights), loaded from the official
  `facebookresearch/dinov2` torch hub entry, plus a random-weights twin of the same architecture.
- Data: Imagenette (320 px) validation split; 1,000 images for the statistics (100 per class) and 200 held-out
  images. Preprocessing: shorter side 256, centre crop 224, ImageNet mean and standard deviation.
- Everything runs on CPU. Model weights and cached features are stored outside the repository, in a cache
  directory set by the environment variable `RH_CACHE` (or `--cache` for scripts that take it).
  Every DINOv2 result file records package versions, the weights hash and its own `runtime_s`.

## How to rebuild

Python scripts are run from `code/`; they need numpy, scipy, matplotlib, torch and torchvision.

```
cd code
python -m pytest tests -q                   # tests of the shared modules
python toy/t1_chords.py                     # likewise t2_sandwich.py, t3_sum_union.py, t4_hexagon.py
python dino/r0_extract.py                   # once: downloads the model and caches the features
python dino/r1_layernorm_ellipsoid.py       # likewise r2 ... r7, r3b and r6b (see the table above)
python figures/fig_chords.py                # likewise the other fig_*.py: writes report/figures/*.pdf
python figures/talk_chords.py               # likewise the other talk_*.py: writes slides/figures/*.pdf
```

Seeds are fixed. The figures read the files in `code/results/`, so they can be redrawn without rerunning the
DINOv2 experiments.

```
cd report && latexmk -pdf report.tex        # report/report.pdf
cd slides && latexmk -pdf slides.tex        # slides/slides.pdf
cd guide/_source && node build.mjs          # all pages; or: node build.mjs 06_critical_reading.html
cd guide/_source && node tools/check_page.cjs 06_critical_reading.html   # check one built page
```

The guide is built from `guide/_source/pages/`; its authoring contract is in `guide/_source/GUIDE.md`.

## Licences and figures

The guide reproduces several figures of the paper, which is published under the Creative Commons Attribution 4.0
licence (CC BY 4.0); each is credited in its caption. All figures of the report and of the slides, and the
figures of the guide marked "From the project report", are original and generated by the scripts in
`code/figures/`.
