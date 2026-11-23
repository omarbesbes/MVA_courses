"""figures_01.py — static figures of page 1 (the exact algorithm). Writes figures/01/*.svg.

    python3 figures_01.py && node build.mjs 01_foundations.html
"""
from figures_common import Canvas, Fig

SUB = "01"


def legend(c, x, y, items):
    """A row of colour keys: items = [(colour index or 'k', label, kind)], kind 'bar' or 'band'."""
    for k, label, kind in items:
        if kind == "band":
            c.rect(x, y - 9, 14, 10, f"a{k} ln c{k} hair", 2)
        else:
            c.rect(x, y - 9, 10, 10, f"f{k}", 2)
        c.text(x + 18, y, label, "tx-s")
        x += 26 + 6.4 * len(label)
    return x


def bar(fig, xc, dx, w, y, cls):
    """A column from 0 to y centred dx pixels from data x = xc, rounded at the top only."""
    X = fig.X(xc) + dx - w / 2
    Y0, Y1 = fig.Y(0), fig.Y(y)
    r = min(4, w / 2, abs(Y0 - Y1))
    d = (f"M{X:.1f} {Y0:.1f}V{Y1 + r:.1f}Q{X:.1f} {Y1:.1f} {X + r:.1f} {Y1:.1f}H{X + w - r:.1f}"
         f"Q{X + w:.1f} {Y1:.1f} {X + w:.1f} {Y1 + r:.1f}V{Y0:.1f}Z")
    fig.c.add(f'<path d="{d}" class="{cls}"/>')


def parallel():
    """Writing is sequential (4 passes), checking is parallel (1 pass, 5 distributions)."""
    c = Canvas("parallel", 660, 336, "Writing four tokens takes four passes of the target; checking a four-token guess takes one pass and returns five distributions.", SUB)
    # --- top: writing
    c.text(20, 22, "Writing four tokens: four passes of the target, one after the other", "tx-b")
    step, bw, bh, cw, ch, y = 158, 92, 40, 42, 26, 40
    for i in range(4):
        x = 20 + step * i
        c.box(x, y, bw, bh, [f"pass {i + 1}"], 1)
        c.arrow(x + bw + 1, y + bh / 2, x + bw + 11, y + bh / 2, "m", "ln cm thin")
        c.chip(x + bw + 12, y + (bh - ch) / 2, cw, ch, f"x{'₁₂₃₄'[i]}", 1, tcls="tx-i")
        if i < 3:
            c.arrow(x + bw + 12 + cw + 1, y + bh / 2, x + step - 1, y + bh / 2, "m", "ln cm thin")
    c.text(20, 106, "time", "tx-s")
    c.arrow(52, 102, 640, 102, "m", "ln cm hair")
    # --- bottom: checking
    c.text(20, 152, "Checking a four-token guess: one pass, five distributions", "tx-b")
    yi, yo, yb = 290, 178, 222          # inputs, outputs, target box
    xs = [20, 142, 228, 314, 400]
    ws = [110, 74, 74, 74, 74]
    c.box(20, yb, 454, 40, ["target Mp — one pass"], 1)
    c.chip(xs[0], yi, ws[0], ch, "prefix")
    for i in range(1, 5):
        c.chip(xs[i], yi, ws[i], ch, f"x̃{'₁₂₃₄'[i - 1]}", 2, tcls="tx-i")
    for i in range(5):
        xm = xs[i] + ws[i] / 2
        c.arrow(xm, yi - 1, xm, yb + 41, "m", "ln cm thin")
        c.arrow(xm, yb - 1, xm, yo + ch + 1, "m", "ln cm thin")
        c.chip(xm - 27, yo, 54, ch, f"p{'₁₂₃₄₅'[i]}", 1, tcls="tx-i")
    # which distribution judges which guess
    c.text(492, yo + 8, "p₁ judges x̃₁,", "tx-s")
    c.text(492, yo + 23, "p₂ judges x̃₂, …", "tx-s")
    c.text(492, yo + 44, "p₅ gives one more", "tx-s")
    c.text(492, yo + 59, "token for free", "tx-s")
    c.text(492, yi + 10, "γ = 4 guessed", "tx-s")
    c.text(492, yi + 25, "tokens (drafter)", "tx-s")
    c.save()


def overlap():
    """Worked example A: p = (0.6, 0.3, 0.1), q = (0.3, 0.5, 0.2); the accepted mass is min(p, q)."""
    names = [" Paris", " the", " a"]
    p = [0.6, 0.3, 0.1]
    q = [0.3, 0.5, 0.2]
    c = Canvas("overlap", 620, 318, "Target and draft distributions on three tokens; the accepted mass is the minimum of the two at each token, 0.7 in total.", SUB)
    f = Fig(c, (58, 44, 524, 214), (0, 3), (0, 0.7))
    f.axes(yticks=[0, 0.2, 0.4, 0.6], yfmt=lambda v: f"{v:g}", grid=True, yaxis=False)
    for i in range(3):
        xc = i + 0.5
        m = min(p[i], q[i])
        # accepted band, behind the two bars
        x0, x1 = f.X(xc) - 44, f.X(xc) + 44
        c.add(f'<rect x="{x0:.1f}" y="{f.Y(m):.1f}" width="{x1 - x0:.1f}" height="{f.Y(0) - f.Y(m):.1f}" class="a3"/>')
        c.line(x0, f.Y(m), x1, f.Y(m), "ln c3 thin")
        bar(f, xc, -13, 22, q[i], "f2")
        bar(f, xc, 13, 22, p[i], "f1")
        f.text(xc, 0, f"“{names[i].strip()}”", "tx", "middle", dy=18)
        c.text(x1 + 5, f.Y(m) + 4, f"kept {m:g}", "tx-s")
    # annotations of what sticks out of the band
    c.text(f.X(0.5) + 30, f.Y(0.53), "gap 0.3, filled", "tx-s")
    c.text(f.X(0.5) + 30, f.Y(0.53) + 14, "by the residual", "tx-s")
    c.text(f.X(1.5) - 30, f.Y(0.4) + 4, "0.2 rejected", "tx-s", "end")
    c.text(f.X(2.5) - 30, f.Y(0.15) + 4, "0.1 rejected", "tx-s", "end")
    legend(c, 58, 16, [(2, "draft q", "bar"), (1, "target p", "bar"), (3, "accepted: min(p, q), total 0.7", "band")])
    c.text(58, 37, "probability", "tx-s")
    c.save()


def timeline():
    """Time accounting of §5, with c = 0.1 and γ = 5: two rounds (3.0 units) against seven target calls."""
    c = Canvas("timeline", 660, 214, "Seven tokens take seven units of time with the target alone, and three units with two speculative rounds when the drafter costs a tenth of the target.", SUB)
    u = 84.0       # pixels per target call
    x0 = 34
    # baseline
    c.text(x0, 20, "Target alone: 7 tokens = 7 calls", "tx-b")
    for i in range(7):
        c.rect(x0 + u * i + 1, 30, u - 2, 30, "a1 ln c1 thin", 5)
        c.text(x0 + u * i + u / 2, 50, f"token {i + 1}", "tx-s", "middle")
    # speculative: two rounds, each 5 drafter calls (0.1) + 1 target call
    c.text(x0, 98, "Speculative decoding (γ = 5, c = 0.1): the same 7 tokens in 2 rounds = 3 units of time", "tx-b")
    x = x0
    yields = [4, 3]
    for r in range(2):
        for j in range(5):
            c.rect(x + 1, 108, 0.1 * u - 2, 30, "a2 ln c2 hair", 2)
            x += 0.1 * u
        c.rect(x + 1, 108, u - 2, 30, "a1 ln c1 thin", 5)
        c.text(x + u / 2, 128, "check", "tx-s", "middle")
        x += u
        c.text(x - 1.5 * u / 2, 154, f"round {r + 1}: {yields[r]} tokens", "tx-s", "middle")
    # time axis
    ya = 182
    c.arrow(x0, ya, x0 + 7 * u + 18, ya, "m", "ln cm hair")
    for i in range(8):
        c.line(x0 + u * i, ya - 4, x0 + u * i, ya + 4, "ln cm hair")
        c.text(x0 + u * i, ya + 18, str(i), "tx-s", "middle")
    c.text(x0 + 7 * u + 18, ya - 8, "time (target calls)", "tx-s", "end")
    c.rect(x0 + 3.2 * u, 112, 10, 10, "f2", 2)
    c.text(x0 + 3.2 * u + 16, 121, "5 drafter calls", "tx-s")
    c.rect(x0 + 3.2 * u, 128, 10, 10, "f1", 2)
    c.text(x0 + 3.2 * u + 16, 137, "1 target call (parallel check)", "tx-s")
    c.save()


if __name__ == "__main__":
    parallel()
    overlap()
    timeline()
