"""Figure: the chord test (E1). Full width, three panels: schematic, T1 midpoint value vs dimension, R2 curves."""
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from rh.plotstyle import setup, save, panel_letter, BLUE, ORANGE, AQUA, GRAY, INK, INK2, FULL  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Ellipse  # noqa: E402

setup()
R = os.path.join(HERE, "..", "results")
z = np.load(os.path.join(R, "t1_chords.npz"))
dims, sup, L = list(z["dims"]), list(z["supports"]), z["lin_curve"]
r1 = json.load(open(os.path.join(R, "r1_layernorm_ellipsoid.json")))["pairs"]
r2 = json.load(open(os.path.join(R, "r2_interpolation_nulls.json")))["datasets"]

fig = plt.figure(figsize=(FULL, 2.1))
gs = fig.add_gridspec(1, 3, width_ratios=[1.15, 1, 1], left=0.005, right=0.995, bottom=0.2, top=0.93, wspace=0.3)
a, b, c = (fig.add_subplot(g) for g in gs)

# (a) schematic
a.set_aspect("equal"); a.axis("off")
A, B = 1.0, 0.62
a.add_patch(Ellipse((0, 0), 2 * A, 2 * B, fill=False, ec=INK, lw=0.7))
th = np.radians([38, 142])
y1, y2 = np.array([A * np.cos(th[0]), B * np.sin(th[0])]), np.array([A * np.cos(th[1]), B * np.sin(th[1])])
m = (y1 + y2) / 2
a.plot([y1[0], y2[0]], [y1[1], y2[1]], color=INK, lw=0.8)
a.plot(*zip(y1, y2), "o", color=INK, ms=3)
a.plot(*m, "o", color=INK, ms=3)
top = np.array([m[0], B * np.sqrt(1 - m[0] ** 2 / A ** 2)])
a.annotate("", xy=top, xytext=m, arrowprops=dict(arrowstyle="<->", lw=0.8, color=INK, shrinkA=2, shrinkB=0, mutation_scale=6))
a.text(top[0] + 0.07, (top[1] + m[1]) / 2, "depth", ha="left", va="center", fontsize=7)
a.text(y1[0] + 0.05, y1[1] + 0.04, "$y'$", ha="left", va="bottom")
a.text(y2[0] - 0.05, y2[1] + 0.04, "$y$", ha="right", va="bottom")
a.text(m[0] + 0.06, m[1] - 0.05, "$m$", ha="left", va="top")
a.text(0.0, -0.45, "$\\mathcal{E}$", ha="center", va="center", fontsize=9)
wi, ac = r1["within_image"], r1["across_images"]
l1 = f"same image: {wi['angle_deg']['mean']:.0f}° apart, depth = {100 * wi['depth_exact_over_half_chord']['mean']:.0f}% of half-chord"
l2 = f"different images: {ac['angle_deg']['mean']:.0f}°, {100 * ac['depth_exact_over_half_chord']['mean']:.1f}%"
a.text(0.0, -0.82, l1, ha="center", va="top", fontsize=6.3)
a.text(0.0, -0.98, l2, ha="center", va="top", fontsize=6.3)
a.set_xlim(-1.2, 1.2); a.set_ylim(-1.0, 0.8)
panel_letter(a, "a", x=0.0, y=0.98)

# (b) midpoint value vs dimension
cols = {"simplex": BLUE, "cube": AQUA, "gauss": GRAY, "sphere": ORANGE}
marks = {"simplex": "o", "cube": "s", "gauss": "^", "sphere": "D"}
names = {"simplex": "simplex", "cube": "cube", "gauss": "Gaussian", "sphere": "sphere (non-convex)"}
b.axhline(0.5, color=INK2, lw=0.6, ls=(0, (3, 2)))
b.text(2.0, 0.515, "nearest sample is an endpoint", fontsize=6.5, va="bottom", ha="left")
for k, s in enumerate(sup):
    b.plot(dims, L[k, :, 50], color=cols[s], marker=marks[s], lw=1.1, ms=3, label=names[s])
b.set_xscale("log")
b.set_xticks(dims); b.set_xticklabels([str(d) for d in dims]); b.minorticks_off()
b.set_xlabel("dimension $d$  ($N$ = 20,000)")
b.set_ylabel("midpoint value $\\rho$")
b.set_ylim(0, 0.95)
b.legend(loc="upper left", handlelength=1.6, borderaxespad=0.1, labelspacing=0.3, fontsize=6.5)
panel_letter(b, "b", x=-0.14, y=1.02)

# (c) R2 curves
t = np.linspace(0, 1, 101)
for key, col in [("c", GRAY), ("a", BLUE)]:
    cu = r2[key]["curves"]
    c.plot(t, cu["lin_norm_mean"], color=col, lw=2.6 if key == "c" else 1.1, zorder=2 if key == "c" else 3)
    c.plot(t, cu["graph_norm_mean"], color=col, lw=1.3, ls=(0, (3, 1.6)))
c.set_xlim(0, 1); c.set_ylim(0, 0.8)
c.set_xlabel("position along the path")
c.set_ylabel("dist. to nearest sample / chord", fontsize=7.5)
l1_ = c.legend(handles=[Line2D([], [], color=BLUE, lw=1.3), Line2D([], [], color=GRAY, lw=1.3)],
               labels=["DINOv2 tokens", "Gaussian, same covariance"], loc="upper center", bbox_to_anchor=(0.5, 1.02),
               handlelength=1.4, borderaxespad=0.1, fontsize=6.3, labelspacing=0.25)
c.add_artist(l1_)
c.legend(handles=[Line2D([], [], color=INK, lw=1.2), Line2D([], [], color=INK, lw=1.2, ls=(0, (3, 1.6)))],
         labels=["straight path", "graph path"], loc="upper center", bbox_to_anchor=(0.5, 0.84), ncol=2,
         handlelength=1.8, columnspacing=1.0, borderaxespad=0.1, fontsize=6.3)
panel_letter(c, "c", x=-0.14, y=1.02)
save(fig, "fig_chords")
