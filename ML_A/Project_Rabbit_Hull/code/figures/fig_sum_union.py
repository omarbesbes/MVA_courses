"""Figure: sum or union? Data views and clustered co-activation matrices (T3). Full width."""
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from rh.plotstyle import setup, save, panel_letter, BLUE, INK, INK2, FULL  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

setup()
R = os.path.join(HERE, "..", "results")
z = np.load(os.path.join(R, "t3_sum_union.npz"))
js = json.load(open(os.path.join(R, "t3_sum_union.json")))
cmap = LinearSegmentedColormap.from_list("blues", ["#ffffff", "#cfe1f6", BLUE, "#0d3a73"])
fig, axs = plt.subplots(1, 4, figsize=(FULL, 1.95), gridspec_kw={"width_ratios": [1, 1, 1, 1]})
items = [("U", "U_K12", "union of 4 triangles", 4), ("S", "S_K9", "sum $T_1\\oplus T_2$", 3)]
for k, (name, key, title, g) in enumerate(items):
    ax, axm = axs[2 * k], axs[2 * k + 1]
    P = z[f"{name}_pc2"]
    ax.scatter(P[:, 0], P[:, 1], s=0.5, lw=0, color=BLUE, alpha=0.5, rasterized=True)
    ax.set_aspect("equal", adjustable="datalim")
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlabel("PC 1"); ax.set_ylabel("PC 2", labelpad=1)
    ax.set_title(title, fontsize=8, pad=3)
    panel_letter(ax, "abcd"[2 * k], x=-0.05, y=1.07)
    C, o = z[f"{key}_Cn"], z[f"{key}_order"]
    im = axm.imshow(C[np.ix_(o, o)], cmap=cmap, vmin=0, vmax=1, interpolation="nearest")
    axm.set_xticks([]); axm.set_yticks([])
    for sp in axm.spines.values():
        sp.set_visible(True); sp.set_linewidth(0.4)
    b = js[key]["blocks"][str(g)]
    axm.set_title(f"$A^\\top A$, K={js[key]['K']}", fontsize=8, pad=3)
    axm.set_xlabel(f"in-block share {b['share_in_blocks']:.2f} (null {b['null_share']:.2f})", fontsize=7)
    panel_letter(axm, "abcd"[2 * k + 1], x=-0.05, y=1.07)
cax = fig.add_axes([0.992, 0.25, 0.008, 0.6])
cb = fig.colorbar(im, cax=cax)
cb.outline.set_linewidth(0.4); cb.ax.tick_params(labelsize=6, width=0.4)
cb.set_label("normalised co-activation", fontsize=7)
fig.subplots_adjust(wspace=0.25, left=0.02, right=0.975, top=0.86, bottom=0.17)
save(fig, "fig_sum_union")
