"""Talk figure: AA sandwich, two stacked panels."""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from rh.plotstyle import set_talk_style, talk_save as save, panel_letter, BLUE, LIGHT_BLUE, ORANGE, AQUA, GRAY, INK, INK2  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Ellipse  # noqa: E402
set_talk_style()
R = os.path.join(HERE, "..", "results")

res = json.load(open(os.path.join(R, "r3_aa_sandwich.json")))["results"]
K = np.array(res["post"]["K"])
_wf = os.path.join(R, "r3_within_variance.json")
W = json.load(open(_wf))["within_image_variance_per_coordinate"] if os.path.exists(_wf) else 0.5118
fig, (a, b) = plt.subplots(2, 1, figsize=(2.9, 3.05), sharex=True, gridspec_kw={"hspace": 0.1})
for key, col, lab, mk in [("pca_Km1", GRAY, "PCA$(K-1)$", "^"), ("aa", BLUE, "AA$(K)$", "o"), ("kmeans", ORANGE, "$k$-means$(K)$", "s")]:
    m, s = np.array(res["post"][key + "_mean"]), np.array(res["post"][key + "_sem"])
    a.plot(K, W * m, color=col, marker=mk, ms=4.5, label=lab)
    a.fill_between(K, W * (m - s), W * (m + s), color=col, alpha=0.25, lw=0)
Kp = [3, 5, 10, 20, 30]; vp = [0.32, 0.26, 0.19, 0.138, 0.116]
a.plot(Kp, vp, "x", color=INK, ms=6, mew=1.4, ls="none", label="AA, paper")
a.axhline(0.227, color=INK2, lw=1.0, ls=(0, (3, 2)))
a.text(50, 0.24, "SAE, paper", ha="right", va="bottom", fontsize=8.5)
a.set_yscale("log"); a.set_ylabel("MSE per coordinate")
a.set_yticks([0.03, 0.05, 0.1, 0.2, 0.4]); a.set_yticklabels(["0.03", "0.05", "0.1", "0.2", "0.4"]); a.minorticks_off()
a.legend(loc="lower left", fontsize=8.5, handlelength=1.4, labelspacing=0.2, borderaxespad=0.1)
panel_letter(a, "a", x=0.12, y=0.99)
for key, col, lab, mk in [("post", BLUE, "DINOv2 tokens", "o"), ("n1", GRAY, "Gaussian, same cov.", "^"), ("n2", AQUA, "planted polytope", "s")]:
    m, s = np.array(res[key]["gap_ratio_mean"]), np.array(res[key]["gap_ratio_sem"])
    b.plot(K, m, color=col, marker=mk, ms=4.5, label=lab)
    b.fill_between(K, m - s, m + s, color=col, alpha=0.25, lw=0)
b.set_ylim(0, 0.95); b.set_yticks([0, 0.2, 0.4, 0.6]); b.set_ylabel("gap ratio $g$")
b.set_xscale("log"); b.set_xticks(K); b.set_xticklabels([str(k) for k in K]); b.minorticks_off()
b.set_xlabel("number of archetypes $K$")
b.legend(loc="upper left", fontsize=8.5, handlelength=1.4, labelspacing=0.2, borderaxespad=0.1)
panel_letter(b, "b", x=0.12, y=0.99)
fig.subplots_adjust(left=0.2, right=0.985, top=0.96, bottom=0.12)
save(fig, "talk_sandwich")
