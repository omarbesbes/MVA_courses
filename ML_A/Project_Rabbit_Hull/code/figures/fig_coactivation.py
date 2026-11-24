"""Figure: normalised co-activation matrices (E3). Full width, three matrices, one colour bar, square-root scale."""
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from rh.plotstyle import setup, save, panel_letter, BLUE, INK, FULL  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, PowerNorm  # noqa: E402

setup()
R = os.path.join(HERE, "..", "results")
t3, r5 = np.load(os.path.join(R, "t3_sum_union.npz")), np.load(os.path.join(R, "r5_coactivation.npz"))
def reorder(C, o):
    return C[np.ix_(o, o)]
U = reorder(t3["U_K12_Cn"], t3["U_K12_order"])
S = reorder(t3["S_K9_Cn"], t3["S_K9_order"])
C = r5["K200_C_by_class_image"].astype(float)
d = np.sqrt(np.diag(C)); D = C / np.outer(d, d)
o = r5["K200_order_by_class_image"]
dc = r5["K200_dominant_class"][o]
bounds = np.where(np.diff(dc) != 0)[0] + 0.5
cmap = LinearSegmentedColormap.from_list("wb", ["#ffffff", BLUE, "#0d2f5c"])
norm = PowerNorm(0.5, vmin=0, vmax=1)  # square-root scale
fig, axs = plt.subplots(1, 3, figsize=(FULL, 2.45))
labs = ["union of four triangles", "sum of two triangles", "DINOv2, 200 archetypes (ordered by class)"]
for ax, M, lab, L in zip(axs, [U, S, D], labs, "abc"):
    im = ax.imshow(M, cmap=cmap, norm=norm, interpolation="nearest")
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_linewidth(0.5)
    ax.set_xlabel(lab, labelpad=3)
    panel_letter(ax, L, x=0.0, y=1.01)
for bb in bounds:
    axs[2].axhline(bb, color=INK, lw=0.3); axs[2].axvline(bb, color=INK, lw=0.3)
fig.subplots_adjust(left=0.01, right=0.9, top=0.94, bottom=0.12, wspace=0.06)
cax = fig.add_axes([0.925, 0.12, 0.012, 0.82])
cb = fig.colorbar(im, cax=cax, ticks=[0, 0.01, 0.1, 0.25, 0.5, 1])
cb.set_ticklabels(["0", "0.01", "0.1", "0.25", "0.5", "1"])
cb.outline.set_linewidth(0.5); cb.ax.tick_params(width=0.5, size=2, labelsize=6.5)
cb.set_label("$C_{ij}/\\sqrt{C_{ii}C_{jj}}$ (square-root scale)", fontsize=7)
save(fig, "fig_coactivation")
