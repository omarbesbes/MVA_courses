"""Talk figure: chord test, data panels only."""
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

z = np.load(os.path.join(R, "t1_chords.npz"))
dims, sup, L = list(z["dims"]), list(z["supports"]), z["lin_curve"]
r2 = json.load(open(os.path.join(R, "r2_interpolation_nulls.json")))["datasets"]
fig, (b, c) = plt.subplots(1, 2, figsize=(5.5, 1.95), gridspec_kw={"wspace": 0.42})
cols = {"simplex": BLUE, "cube": AQUA, "gauss": GRAY, "sphere": ORANGE}
marks = {"simplex": "o", "cube": "s", "gauss": "^", "sphere": "D"}
names = {"simplex": "simplex", "cube": "cube", "gauss": "Gaussian", "sphere": "sphere (non-convex)"}
b.axhline(0.5, color=INK2, lw=1.0, ls=(0, (3, 2)))
b.text(100, 0.515, "nearest sample is an endpoint", fontsize=8.5, va="bottom", ha="right")
for k, s in enumerate(sup):
    b.plot(dims, L[k, :, 50], color=cols[s], marker=marks[s], label=names[s])
b.set_xscale("log"); b.set_xticks(dims); b.set_xticklabels([str(d) for d in dims]); b.minorticks_off()
b.set_xlabel("dimension $d$"); b.set_ylabel("midpoint value $\\rho$"); b.set_ylim(0, 1.3); b.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
b.legend(loc="upper center", ncol=2, handlelength=1.2, columnspacing=0.8, borderaxespad=0.1, labelspacing=0.2, fontsize=8.5)
panel_letter(b, "a", x=-0.02, y=1.0)
t = np.linspace(0, 1, 101)
for key, col in [("c", GRAY), ("a", BLUE)]:
    cu = r2[key]["curves"]
    c.plot(t, cu["lin_norm_mean"], color=col, lw=3.6 if key == "c" else 1.8, zorder=2 if key == "c" else 3)
    c.plot(t, cu["graph_norm_mean"], color=col, lw=1.8, ls=(0, (3, 1.6)))
c.set_xlim(0, 1); c.set_ylim(0, 1.0)
c.set_xlabel("position along the path"); c.set_ylabel("dist. to nearest\nsample / chord")
l1_ = c.legend(handles=[Line2D([], [], color=BLUE, lw=2), Line2D([], [], color=GRAY, lw=3)],
               labels=["DINOv2 tokens", "Gaussian, same cov."], loc="upper center", bbox_to_anchor=(0.5, 1.02),
               handlelength=1.4, borderaxespad=0.1, fontsize=8.5, labelspacing=0.2)
c.add_artist(l1_)
c.legend(handles=[Line2D([], [], color=INK, lw=1.8), Line2D([], [], color=INK, lw=1.8, ls=(0, (3, 1.6)))],
         labels=["straight path", "graph path"], loc="upper center", bbox_to_anchor=(0.5, 0.8), ncol=2,
         handlelength=1.6, columnspacing=0.8, borderaxespad=0.1, fontsize=8.5)
panel_letter(c, "b", x=-0.02, y=1.0)
fig.subplots_adjust(left=0.1, right=0.995, top=0.93, bottom=0.2)
save(fig, "talk_chords")
