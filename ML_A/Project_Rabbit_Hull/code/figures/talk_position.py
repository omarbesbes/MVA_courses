"""Talk figure: position table in its first two principal directions."""
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

z = np.load(os.path.join(R, "r6_position_plane.npz"))
P, F, sh = z["coords_P"], z["coords_F"].reshape(16, 16, 2), z["var_shares"]
fig, ax = plt.subplots(figsize=(2.9, 2.75))
for i in range(16):
    ax.plot(F[i, :, 0], F[i, :, 1], color=GRAY, lw=0.8)
    ax.plot(F[:, i, 0], F[:, i, 1], color=GRAY, lw=0.8)
ax.scatter(P[:, 0], P[:, 1], s=14, color=BLUE, lw=0, zorder=3)
ax.set_aspect("equal")
ax.set_xlabel(f"PC 1 ({100 * sh[0]:.0f}%)"); ax.set_ylabel(f"PC 2 ({100 * sh[1]:.0f}%)")
ax.legend(handles=[Line2D([], [], color=BLUE, marker="o", ls="none", ms=5), Line2D([], [], color=GRAY, lw=1.4)],
          labels=["mean token at a position", "additive fit $r_i+c_j$"], loc="lower center", bbox_to_anchor=(0.5, 1.0),
          ncol=1, fontsize=9, handlelength=1.4, handletextpad=0.4, borderaxespad=0.1, labelspacing=0.2)
fig.subplots_adjust(left=0.17, right=0.98, top=0.82, bottom=0.15)
save(fig, "talk_position")
