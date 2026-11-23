"""Figure: AA between PCA(K-1) and k-means(K) on polytope and Gaussian data (T2). Single column."""
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from rh.plotstyle import setup, save, panel_letter, BLUE, ORANGE, GRAY, INK, SINGLE  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

setup()
z = np.load(os.path.join(HERE, "..", "results", "t2_sandwich.npz"))
F, K, sets = z["fvu"], z["K"], list(z["sets"])
fig, axs = plt.subplots(1, 2, figsize=(SINGLE, 1.75), sharey=True)
style = [("k-means($K$)", GRAY, "s"), ("AA($K$)", BLUE, "o"), ("PCA($K$-1)", ORANGE, "^")]
for ax, s, title, L in [(axs[0], "polytope", "polytope", "a"), (axs[1], "gauss", "Gaussian, same cov.", "b")]:
    a = sets.index(s)
    for m, (lab, c, mk) in zip([2, 1, 0], style):
        mu = F[a, m].mean(-1)
        se = F[a, m].std(-1, ddof=1) / np.sqrt(F.shape[-1])
        ax.errorbar(K, mu, yerr=se, color=c, marker=mk, ms=2.5, lw=1.0, capsize=0, elinewidth=0.6, label=lab)
    ax.set_xscale("log"); ax.set_xticks(K); ax.set_xticklabels([str(k) for k in K]); ax.minorticks_off()
    ax.set_title(title, fontsize=7, pad=2, loc="right")
    ax.set_xlabel("$K$")
    panel_letter(ax, L, x=-0.04, y=1.06)
axs[0].set_ylabel("FVU")
axs[0].set_ylim(0, 1.0)
axs[1].legend(loc="upper right", handlelength=1.4, borderaxespad=0.2)
fig.subplots_adjust(wspace=0.18, left=0.14, right=0.99, top=0.85, bottom=0.2)
save(fig, "fig_sandwich_toy")
