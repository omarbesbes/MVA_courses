"""Figure: AA between PCA and k-means (E2). Single column, two stacked panels (R3)."""
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from rh.plotstyle import setup, save, panel_letter, BLUE, ORANGE, AQUA, GRAY, INK, INK2, SINGLE  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

setup()
res = json.load(open(os.path.join(HERE, "..", "results", "r3_aa_sandwich.json")))["results"]
K = np.array(res["post"]["K"])
W = 0.5118  # mean within-image variance per coordinate over the 200 images: MSE = FVU * W
fig, (a, b) = plt.subplots(2, 1, figsize=(SINGLE, 3.1), sharex=True, gridspec_kw={"hspace": 0.1})
for key, col, lab, mk in [("pca_Km1", GRAY, "PCA$(K-1)$", "^"), ("aa", BLUE, "AA$(K)$", "o"), ("kmeans", ORANGE, "$k$-means$(K)$", "s")]:
    m, s = np.array(res["post"][key + "_mean"]), np.array(res["post"][key + "_sem"])
    a.plot(K, W * m, color=col, marker=mk, ms=3, lw=1.2, label=lab)
    a.fill_between(K, W * (m - s), W * (m + s), color=col, alpha=0.25, lw=0)
Kp = [3, 5, 10, 20, 30]; vp = [0.32, 0.26, 0.19, 0.138, 0.116]
a.plot(Kp, vp, "x", color=INK, ms=4, mew=0.9, ls="none", label="AA, paper (Fig. 17)")
a.axhline(0.227, color=INK2, lw=0.6, ls=(0, (3, 2)))
a.text(50, 0.236, "SAE, paper", ha="right", va="bottom", fontsize=6.5)
a.set_yscale("log"); a.set_ylabel("MSE per coordinate")
a.set_yticks([0.03, 0.05, 0.1, 0.2, 0.4]); a.set_yticklabels(["0.03", "0.05", "0.1", "0.2", "0.4"]); a.minorticks_off()
a.legend(loc="lower left", fontsize=6.5, handlelength=1.5, labelspacing=0.25, borderaxespad=0.1)
panel_letter(a, "a", x=-0.2, y=1.0)
for key, col, lab, mk in [("post", BLUE, "DINOv2 tokens", "o"), ("n1", GRAY, "Gaussian, same covariance", "^"), ("n2", AQUA, "planted 10-vertex polytope", "s")]:
    m, s = np.array(res[key]["gap_ratio_mean"]), np.array(res[key]["gap_ratio_sem"])
    b.plot(K, m, color=col, marker=mk, ms=3, lw=1.2, label=lab)
    b.fill_between(K, m - s, m + s, color=col, alpha=0.25, lw=0)
b.set_ylim(0, 0.65); b.set_ylabel("gap ratio $g$")
b.set_xscale("log"); b.set_xticks(K); b.set_xticklabels([str(k) for k in K]); b.minorticks_off()
b.set_xlabel("number of archetypes $K$")
b.legend(loc="lower right", fontsize=6.5, handlelength=1.5, labelspacing=0.25, borderaxespad=0.1)
panel_letter(b, "b", x=-0.2, y=1.0)
fig.subplots_adjust(left=0.17, right=0.98, top=0.97, bottom=0.12)
save(fig, "fig_sandwich")
