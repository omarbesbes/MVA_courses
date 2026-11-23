"""figures_03.py — static figures of page 3 (relaxed acceptance). Writes figures/03/*.svg.

    python3 figures_03.py && node build.mjs 03_relaxed.html
"""
from figures_common import Canvas, Fig
from figures_01 import bar, legend

SUB = "03"


def lenience():
    """Example A with lenience 0.8: caps p/lambda, and the output distribution."""
    names = ["Paris", "the", "a"]
    p = [0.6, 0.3, 0.1]
    q = [0.3, 0.5, 0.2]
    lam = 0.8
    acc = [min(qq, pp / lam) for pp, qq in zip(p, q)]
    A = sum(acc)
    res = [max(0.0, pp - qq) for pp, qq in zip(p, q)]
    Z = sum(res)
    out = [a + (1 - A) * r / Z for a, r in zip(acc, res)]
    c = Canvas("lenience", 620, 318, "Lenience 0.8 on example A: each token's output probability is at most its cap p over lambda.", SUB)
    f = Fig(c, (58, 44, 524, 214), (0, 3), (0, 0.8))
    f.axes(yticks=[0, 0.2, 0.4, 0.6, 0.8], yfmt=lambda v: f"{v:g}", grid=True, yaxis=False)
    for i in range(3):
        xc = i + 0.5
        bar(f, xc, -13, 22, q[i], "f2")
        bar(f, xc, 13, 22, p[i], "f1")
        cap = p[i] / lam
        c.line(f.X(xc) - 34, f.Y(cap), f.X(xc) + 34, f.Y(cap), "ln ck thin")
        c.text(f.X(xc) + 39, f.Y(cap) + 4, f"cap {cap:g}", "tx-s")
        c.add(f'<circle cx="{f.X(xc):.1f}" cy="{f.Y(out[i]):.1f}" r="5" class="fk ring"/>')
        c.text(f.X(xc) - 39, f.Y(out[i]) + 4, f"out {out[i]:g}", "tx-s", "end")
        f.text(xc, 0, f"“{names[i]}”", "tx", "middle", dy=18)
    x = legend(c, 58, 16, [(2, "draft q", "bar"), (1, "target p", "bar")])
    c.add(f'<circle cx="{x + 5:.1f}" cy="11" r="4.5" class="fk"/>')
    c.text(x + 16, 16, "output of the lenient rule", "tx-s")
    c.line(x + 176, 12, x + 198, 12, "ln ck thin")
    c.text(x + 204, 16, "cap p / λ", "tx-s")
    c.text(58, 37, "probability", "tx-s")
    c.save()


def band():
    """Mentored decoding on the four-token example: the band [p/beta, p/alpha], the drafter's probability and the output."""
    p = [0.4, 0.3, 0.2, 0.1]
    q = [0.1, 0.2, 0.3, 0.4]
    alpha, beta = 0.5, 1.4
    out = [min(max(qq, pp / beta), pp / alpha) for pp, qq in zip(p, q)]
    c = Canvas("band", 620, 300, "Mentored decoding: the output is the drafter's probability clipped into a band around the target's probability.", SUB)
    f = Fig(c, (58, 40, 524, 200), (0, 4), (0, 0.9))
    f.axes(yticks=[0, 0.2, 0.4, 0.6, 0.8], yfmt=lambda v: f"{v:g}", grid=True, yaxis=False)
    for i in range(4):
        xc = i + 0.5
        X = f.X(xc)
        lo, hi = p[i] / beta, p[i] / alpha
        # the band, as a bracket
        c.rect(X - 9, f.Y(hi), 18, f.Y(lo) - f.Y(hi), "am ln cm thin", 3)
        c.text(X + 15, f.Y(hi) + 4, f"p/α = {hi:g}", "tx-s")
        c.text(X + 15, f.Y(lo) + 4, f"p/β = {lo:.3g}", "tx-s")
        # target probability
        c.line(X - 16, f.Y(p[i]), X + 16, f.Y(p[i]), "ln c1")
        # drafter probability
        c.line(X - 30, f.Y(q[i]), X - 12, f.Y(q[i]), "ln c2")
        c.text(X - 21, f.Y(q[i]) - 6, f"q = {q[i]:g}", "tx-s", "middle")
        # output
        c.add(f'<circle cx="{X:.1f}" cy="{f.Y(out[i]):.1f}" r="5" class="fk ring"/>')
        f.text(xc, 0, f"token {i + 1}", "tx", "middle", dy=18)
    c.rect(58, 9, 14, 10, "am ln cm hair", 2)
    c.text(78, 18, "band [p/β, p/α]", "tx-s")
    c.line(190, 14, 212, 14, "ln c1")
    c.text(218, 18, "target p", "tx-s")
    c.line(286, 14, 308, 14, "ln c2")
    c.text(314, 18, "draft q", "tx-s")
    c.add('<circle cx="378" cy="14" r="4.5" class="fk"/>')
    c.text(388, 18, "output", "tx-s")
    c.text(58, 34, "probability", "tx-s")
    c.save()


if __name__ == "__main__":
    lenience()
    band()
