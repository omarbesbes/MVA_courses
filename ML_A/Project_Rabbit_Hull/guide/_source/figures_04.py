"""figures_04.py -- static SVG figures of page 04 (statistics and geometry), written to figures/04/.
Run: python3 figures_04.py   (then node build.mjs 04_statistics_geometry.html)"""
import numpy as np
from figures_common import Canvas, Fig

SUB = "04"
c_, d_ = 32000, 768


def fig_coherence_scale():
    c = Canvas("coherence_scale", 720, 250, "Log scale of inner products between unit vectors: Welch bound, Grassmannian frame, random vectors, SAE atoms", sub=SUB)
    f = Fig(c, (40, 120, 650, 10), (0.02, 1.0), (0, 1))
    X = lambda v: f.x0 + (np.log10(v) - np.log10(0.02)) / (np.log10(1.0) - np.log10(0.02)) * f.w
    y = 135
    c.add(f'<line x1="{X(0.02):.1f}" y1="{y}" x2="{X(1.0):.1f}" y2="{y}" class="ax"/>')
    for v in (0.02, 0.05, 0.1, 0.2, 0.5, 1.0):
        c.add(f'<line x1="{X(v):.1f}" y1="{y-4}" x2="{X(v):.1f}" y2="{y+4}" class="ax"/>')
        c.text(X(v), y + 20, f"{v:g}", "tx-s", "middle")
    c.text(X(1.0), y + 40, "|⟨Dᵢ, Dⱼ⟩|  (log scale)", "tx-s", "end")
    welch = np.sqrt((c_ - d_) / (d_ * (c_ - 1)))
    sd = 1 / np.sqrt(d_)
    P = c_ * (c_ - 1) / 2
    rmax = np.sqrt(2 * np.log(P) / d_)
    items = [  # value, label, class, row (above=1/2, below negative)
        (welch, f"Welch bound {welch:.4f}", "c6", 1),
        (sd, f"random: std {sd:.4f}", "c6", 2),
        (0.065897, "Grassmannian frame 0.0659", "c2", 1),
        (rmax, f"random: largest of 5×10⁸ pairs ≈ {rmax:.2f}", "c6", 2),
        (0.92, "SAE: largest ≈ 0.92 (read off Fig. 10 A)", "c1", 1),
    ]
    anchors = {0: "start", 1: "start", 2: "start", 3: "start", 4: "end"}
    for k, (v, lab, cl, row) in enumerate(items):
        yy = y - 14 - (row - 1) * 34 if True else y
        c.add(f'<line x1="{X(v):.1f}" y1="{y}" x2="{X(v):.1f}" y2="{yy+6:.1f}" class="ln {cl} thin"/>')
        c.add(f'<circle cx="{X(v):.1f}" cy="{y}" r="4.5" class="f{cl[1]}"/>')
        c.text(X(v) + (-4 if anchors[k] == "end" else 4), yy, lab, "tx-s", anchors[k])
    c.text(40, 28, "Where the paper's three dictionaries sit on one axis (c = 32 000, d = 768)", "tx-b")
    c.text(40, 232, "Grey: baselines and bounds. Orange: the numerically computed Grassmannian frame. Blue: the learned SAE dictionary.", "tx-s")
    c.save()


def fig_linear_segment():
    c = Canvas("linear_segment", 720, 270, "A linear map sends a chord to a chord and an arc to an arc, or flattens it onto a line", sub=SUB)
    th = np.linspace(0.15, np.pi - 0.15, 60)
    arc = np.stack([np.cos(th), np.sin(th)], 1)
    A = np.array([[1.3, 0.5], [-0.3, 0.7]])  # full rank
    B = np.array([[1.0, 0.6], [0.0, 0.0]])  # rank 1
    panels = [("In activation space", np.eye(2)), ("Full-rank linear map: chord stays straight", A), ("Rank-1 linear map: everything on a line", B)]
    for i, (title, M) in enumerate(panels):
        ox, oy, s = 120 + i * 240, 190, 62
        c.text(ox, 38, title, "tx-b", "middle")
        pts = arc @ M.T
        chord = np.array([arc[0], arc[-1]]) @ M.T
        mid = chord.mean(0)
        P = lambda q: (ox + s * q[0], oy - s * q[1])
        c.add('<path d="M' + "L".join(f"{P(q)[0]:.1f} {P(q)[1]:.1f}" for q in pts) + '" class="ln c3" fill="none" style="stroke-width:2.4"/>')
        c.add(f'<line x1="{P(chord[0])[0]:.1f}" y1="{P(chord[0])[1]:.1f}" x2="{P(chord[1])[0]:.1f}" y2="{P(chord[1])[1]:.1f}" class="ln c2 dash"/>')
        for q, lab in ((chord[0], "a"), (chord[1], "b")):
            c.add(f'<circle cx="{P(q)[0]:.1f}" cy="{P(q)[1]:.1f}" r="4.5" class="f1"/>')
            c.text(P(q)[0] + (-9 if lab == "a" else 9), P(q)[1] + 4, lab if i == 0 else lab + "′", "tx", "end" if lab == "a" else "start")
        c.add(f'<circle cx="{P(mid)[0]:.1f}" cy="{P(mid)[1]:.1f}" r="3.5" class="f2"/>')
    c.text(120, 250, "green: a curved set of tokens", "tx-s", "middle")
    c.text(360, 250, "orange dashed: the chord, image of the chord", "tx-s", "middle")
    c.text(600, 250, "curved set may become flat, never the reverse", "tx-s", "middle")
    c.save()


def fig_sr_vs_r2():
    sr = [9.0, 8.1, 5.4, 7.2, 5.6, 5.4, 4.9, 4.4, 4.4, 2.8, 2.6, 2.7]
    r2 = [0.63, 0.75, 0.83, 0.77, 0.81, 0.86, 0.90, 0.94, 0.96, 0.99, 1.00, 1.00]
    bound = [2 / r for r in r2]
    c = Canvas("sr_vs_r2", 720, 330, "Stable rank read off Figure 14 against the upper bound 2 divided by R squared", sub=SUB)
    f = Fig(c, (60, 40, 620, 230), (0, 11), (0, 10))
    f.axes(xticks=range(0, 12), yticks=range(0, 11, 2), xfmt=lambda v: str(int(v)), yfmt=lambda v: str(int(v)), xlabel="index in the list (layer 0–11 for R², layer 1–12 for stable rank)")
    f.path([(i, b) for i, b in enumerate(bound)], "ln c6", extra=' style="stroke-width:2"')
    f.path([(i, s) for i, s in enumerate(sr)], "ln c1", extra=' style="stroke-width:1.5"')
    for i, s in enumerate(sr):
        f.circle(i, s, 4.5, "f1")
    f.text(6.0, 7.6, "stable rank (left plot of Fig. 14)", "tx", "start", dx=0)
    f.text(2.0, 1.2, "bound 2/R² if both are computed on the same matrix", "tx-s", "start", dx=0, dy=0)
    f.line(0, 2, 11, 2, "dash")
    f.text(11, 2, "2", "tx-s", "end", dy=-6)
    c.text(60, 20, "Every point lies above the bound, which is impossible for one centred matrix", "tx-b")
    c.text(60, 322, "Values read off the two plots of Fig. 14 (paper p. 16); bound derived in section 8.", "tx-s")
    c.save()


if __name__ == "__main__":
    fig_coherence_scale()
    fig_linear_segment()
    fig_sr_vs_r2()
