"""Figure: one hexagon, two generative stories (T4). Full width, four panels."""
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from rh.plotstyle import setup, save, panel_letter, BLUE, LIGHT_BLUE, ORANGE, GRAY, INK, INK2, FULL  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

setup()
z = np.load(os.path.join(HERE, "..", "results", "t4_hexagon.npz"))
H, G, T = z["H"], z["G"], z["T"]
Hc = np.vstack([H, H[:1]])
fig, axs = plt.subplots(1, 4, figsize=(FULL, 1.95))
labels = ["three segments\n$S_0\\oplus S_{60}\\oplus S_{120}$", "two triangles\n$T\\oplus(-T)$",
          "sparse linear codes\n$x=\\Sigma_k\\, t_k g_k$", "block-convex codes\n$x=p+q$"]
for i, ax in enumerate(axs):
    ax.plot(Hc[:, 0], Hc[:, 1], color=INK, lw=0.8, zorder=3)
    ax.set_aspect("equal")
    ax.set_xlim(-1.12, 1.12); ax.set_ylim(-1.0, 1.0)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_xlabel(labels[i], labelpad=3)
    panel_letter(ax, "abcd"[i], x=0.0, y=0.97)
# (a) the three generators through the centre
for g in G:
    axs[0].plot([-g[0] / 2, g[0] / 2], [-g[1] / 2, g[1] / 2], color=ORANGE, lw=1.5, solid_capstyle="round")
# (b) T and -T, and one translate T + (-t) at a vertex to show the sum
Tc, mTc = np.vstack([T, T[:1]]), np.vstack([-T, -T[:1]])
axs[1].fill(Tc[:, 0], Tc[:, 1], color=BLUE, alpha=0.85, lw=0, zorder=2)
axs[1].fill(mTc[:, 0], mTc[:, 1], color=LIGHT_BLUE, alpha=0.75, lw=0, zorder=1)
axs[1].text(0, 0.36, "$T$", color="white", ha="center", va="center", fontsize=8, zorder=4)
axs[1].text(0, -0.42, "$-T$", color=INK, ha="center", va="center", fontsize=8, zorder=4)
# (c), (d) the clouds
for ax, X, c in [(axs[2], z["X_lin"], ORANGE), (axs[3], z["X_blk"], BLUE)]:
    ax.scatter(X[:, 0], X[:, 1], s=1.2, lw=0, color=c, alpha=0.2, rasterized=True, zorder=2)
fig.subplots_adjust(wspace=0.08, left=0.01, right=0.99, top=0.97, bottom=0.22)
save(fig, "fig_hexagon")
