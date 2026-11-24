"""Figure: the position table in its first two principal directions (R6b). Single column."""
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from rh.plotstyle import setup, save, panel_letter, BLUE, GRAY, INK, SINGLE  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

setup()
z = np.load(os.path.join(HERE, "..", "results", "r6_position_plane.npz"))
P, F, sh = z["coords_P"], z["coords_F"].reshape(16, 16, 2), z["var_shares"]
fig, ax = plt.subplots(figsize=(SINGLE, 2.6))
for i in range(16):
    ax.plot(F[i, :, 0], F[i, :, 1], color=GRAY, lw=0.5)   # row i: j varies
    ax.plot(F[:, i, 0], F[:, i, 1], color=GRAY, lw=0.5)   # column i: i varies
ax.scatter(P[:, 0], P[:, 1], s=5, color=BLUE, lw=0, zorder=3)
ax.set_aspect("equal")
ax.set_xlabel(f"PC 1 ({100 * sh[0]:.0f}%)"); ax.set_ylabel(f"PC 2 ({100 * sh[1]:.0f}%)")
ax.legend(handles=[Line2D([], [], color=BLUE, marker="o", ls="none", ms=3), Line2D([], [], color=GRAY, lw=0.8)],
          labels=["mean token at a position", "additive fit $r_i+c_j$"], loc="best", fontsize=6.5, handlelength=1.5, borderaxespad=0.2)
fig.subplots_adjust(left=0.14, right=0.98, top=0.98, bottom=0.14)
save(fig, "fig_position")
