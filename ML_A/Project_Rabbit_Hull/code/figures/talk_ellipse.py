"""Talk figure: ellipsoid schematic alone."""
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

fig, a = plt.subplots(figsize=(2.2, 1.15))
a.set_aspect("equal"); a.axis("off")
A, B = 1.0, 0.62
a.add_patch(Ellipse((0, 0), 2 * A, 2 * B, fill=False, ec=INK, lw=1.4))
th = np.radians([38, 142])
y1, y2 = np.array([A * np.cos(th[0]), B * np.sin(th[0])]), np.array([A * np.cos(th[1]), B * np.sin(th[1])])
m = (y1 + y2) / 2
a.plot([y1[0], y2[0]], [y1[1], y2[1]], color=INK, lw=1.4)
a.plot(*zip(y1, y2), "o", color=INK, ms=5); a.plot(*m, "o", color=INK, ms=5)
top = np.array([m[0], B * np.sqrt(1 - m[0] ** 2 / A ** 2)])
a.annotate("", xy=top, xytext=m, arrowprops=dict(arrowstyle="<->", lw=1.2, color=INK, shrinkA=2, shrinkB=0, mutation_scale=8))
a.text(top[0] + 0.07, (top[1] + m[1]) / 2, "depth", ha="left", va="center")
a.text(y1[0] + 0.04, y1[1] + 0.05, "$y'$", ha="left", va="bottom")
a.text(y2[0] - 0.04, y2[1] + 0.05, "$y$", ha="right", va="bottom")
a.text(m[0] + 0.07, m[1] - 0.07, "$m$", ha="left", va="top")
a.text(0.0, -0.3, "$\\mathcal{E}$", ha="center", va="center", fontsize=11)
a.set_xlim(-1.05, 1.05); a.set_ylim(-0.65, 0.85)
fig.subplots_adjust(0, 0, 1, 1)
save(fig, "talk_ellipse")
