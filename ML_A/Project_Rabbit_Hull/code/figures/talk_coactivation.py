"""Talk figure: co-activation matrices."""
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

from matplotlib.colors import LinearSegmentedColormap, PowerNorm
t3, r5 = np.load(os.path.join(R, "t3_sum_union.npz")), np.load(os.path.join(R, "r5_coactivation.npz"))
def reorder(C, o): return C[np.ix_(o, o)]
U = reorder(t3["U_K12_Cn"], t3["U_K12_order"]); S = reorder(t3["S_K9_Cn"], t3["S_K9_order"])
C = r5["K200_C_by_class_image"].astype(float)
d = np.sqrt(np.diag(C)); D = C / np.outer(d, d)
o = r5["K200_order_by_class_image"]; dc = r5["K200_dominant_class"][o]
bounds = np.where(np.diff(dc) != 0)[0] + 0.5
cmap = LinearSegmentedColormap.from_list("wb", ["#ffffff", BLUE, "#0d2f5c"])
norm = PowerNorm(0.5, vmin=0, vmax=1)
fig, axs = plt.subplots(1, 3, figsize=(5.5, 1.85))
labs = ["union of\nfour triangles", "sum of\ntwo triangles", "DINOv2, 200 archetypes\n(ordered by class)"]
for ax, M, lab, L in zip(axs, [U, S, D], labs, "abc"):
    im = ax.imshow(M, cmap=cmap, norm=norm, interpolation="nearest")
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values(): sp.set_linewidth(0.8)
    ax.set_xlabel(lab, labelpad=3, linespacing=1.15)
    panel_letter(ax, L, x=0.0, y=1.01)
for bb in bounds:
    axs[2].axhline(bb, color=INK, lw=0.4); axs[2].axvline(bb, color=INK, lw=0.4)
fig.subplots_adjust(left=0.005, right=0.89, top=0.93, bottom=0.27, wspace=0.05)
cax = fig.add_axes([0.915, 0.27, 0.022, 0.66])
cb = fig.colorbar(im, cax=cax, ticks=[0, 0.01, 0.1, 0.5, 1])
cb.set_ticklabels(["0", "0.01", "0.1", "0.5", "1"])
cb.outline.set_linewidth(0.8); cb.ax.tick_params(width=0.8, size=3, labelsize=9)
cb.set_label("$C_{ij}/\\sqrt{C_{ii}C_{jj}}$", fontsize=9, labelpad=3)
save(fig, "talk_coactivation")
