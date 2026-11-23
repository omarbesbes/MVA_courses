"""Figure: the chord test on convex supports (T1). Full width, two panels."""
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from rh.plotstyle import setup, save, panel_letter, BLUE, ORANGE, AQUA, GRAY, INK, INK2, FULL  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

setup()
z = np.load(os.path.join(HERE, "..", "results", "t1_chords.npz"))
t, dims, sup = z["t"], list(z["dims"]), list(z["supports"])
L, G = z["lin_curve"], z["graph_curve"]
fig, (a, b) = plt.subplots(1, 2, figsize=(FULL, 2.1), gridspec_kw={"width_ratios": [1, 1.15]})
si = sup.index("simplex")
a.plot(t, np.minimum(t, 1 - t), color=GRAY, lw=0.8, ls=(0, (3, 2)))
a.text(0.5, 0.515, "triangle $\\min(t,1-t)$", color=INK2, ha="center", va="bottom", fontsize=7)
for d, ls in [(2, ":"), (50, "-")]:
    j = dims.index(d)
    a.plot(t, L[si, j], color=ORANGE, ls=ls, lw=1.3)
    a.plot(t, G[si, j], color=BLUE, ls=ls, lw=1.3)
a.text(0.66, 0.36, "straight, $d$=50", color=INK, fontsize=7, ha="left")
a.text(0.5, 0.205, "graph, $d$=50", color=INK, fontsize=7, ha="center")
a.text(0.5, 0.03, "straight and graph, $d$=2", color=INK, fontsize=7, ha="center")
a.set_xlabel("position along the path $t$")
a.set_ylabel("dist. to sample / chord")
a.set_xlim(0, 1); a.set_ylim(0, 0.6)
panel_letter(a, "a", x=-0.1, y=1.03)
cols = {"simplex": BLUE, "cube": AQUA, "gauss": GRAY, "sphere": ORANGE}
marks = {"simplex": "o", "cube": "s", "gauss": "^", "sphere": "D"}
names = {"simplex": "simplex", "cube": "cube", "gauss": "Gaussian", "sphere": "sphere (non-convex)"}
b.axhline(0.5, color=INK2, lw=0.6, ls=(0, (3, 2)))
for k, s in enumerate(sup):
    b.plot(dims, L[k, :, 50], color=cols[s], marker=marks[s], lw=1.1, ms=3, label=names[s])
b.set_xscale("log")
b.set_xticks(dims); b.set_xticklabels([str(d) for d in dims]); b.minorticks_off()
b.set_xlabel("dimension $d$  ($N$ = 20,000)")
b.set_ylabel("midpoint value, straight path")
b.set_ylim(0, 0.56)
b.legend(loc="lower right", handlelength=1.6)
panel_letter(b, "b", x=-0.1, y=1.03)
fig.subplots_adjust(wspace=0.32, left=0.08, right=0.99, bottom=0.2, top=0.9)
save(fig, "fig_chords")
