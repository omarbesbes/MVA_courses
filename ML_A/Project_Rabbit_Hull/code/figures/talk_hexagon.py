"""Talk figure: hexagon, four panels (slide width)."""
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

z = np.load(os.path.join(R, "t4_hexagon.npz"))
H, G, T = z["H"], z["G"], z["T"]
Hc = np.vstack([H, H[:1]])
fig, axs = plt.subplots(1, 4, figsize=(5.5, 1.75))
labels = ["three segments\n$S_0\\oplus S_{60}\\oplus S_{120}$", "two triangles\n$T\\oplus(-T)$",
          "sparse linear\ncodes $\\Sigma_k t_k g_k$", "block-convex\ncodes $p+q$"]
for i, ax in enumerate(axs):
    ax.plot(Hc[:, 0], Hc[:, 1], color=INK, lw=1.4, zorder=3)
    ax.set_aspect("equal"); ax.set_xlim(-1.12, 1.12); ax.set_ylim(-1.0, 1.0)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.set_xlabel(labels[i], labelpad=3, linespacing=1.15)
    panel_letter(ax, "abcd"[i], x=0.0, y=0.95)
for g in G:
    axs[0].plot([-g[0] / 2, g[0] / 2], [-g[1] / 2, g[1] / 2], color=ORANGE, lw=2.4, solid_capstyle="round")
Tc, mTc = np.vstack([T, T[:1]]), np.vstack([-T, -T[:1]])
axs[1].fill(Tc[:, 0], Tc[:, 1], color=BLUE, alpha=0.85, lw=0, zorder=2)
axs[1].fill(mTc[:, 0], mTc[:, 1], color=LIGHT_BLUE, alpha=0.75, lw=0, zorder=1)
axs[1].text(0, 0.36, "$T$", color="white", ha="center", va="center", zorder=4)
axs[1].text(0, -0.42, "$-T$", color=INK, ha="center", va="center", zorder=4)
for ax, X, c in [(axs[2], z["X_lin"], ORANGE), (axs[3], z["X_blk"], BLUE)]:
    ax.scatter(X[:, 0], X[:, 1], s=1.5, lw=0, color=c, alpha=0.25, rasterized=True, zorder=2)
fig.subplots_adjust(wspace=0.04, left=0.01, right=0.99, top=0.98, bottom=0.3)
save(fig, "talk_hexagon")
