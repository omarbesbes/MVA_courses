"""figures_06.py — static figure of page 6 (practice). Writes figures/06/*.svg.

    python3 figures_06.py && node build.mjs 06_practice.html
"""
from figures_common import Canvas

SUB = "06"


def decide():
    """Four questions before switching a lossy rule on."""
    c = Canvas("decide", 660, 392, "Decision flow: four questions, each with an exit toward an exact method, before choosing a relaxed rule.", SUB)
    qs = [
        (["Is the output ordinary text?"], ["Codes or actions: see §1", "(relaxed rules are usual there)"], 4),
        (["Have you taken the exact gains?", "a drafter fitted to the target, draft length, load"], ["Do that first (page 2):", "nothing to re-evaluate"], 1),
        (["Can you measure quality and safety", "on your own task, at each setting of the rule?"], ["Stay exact"], 1),
        (["Is the drafter a capable model of the task?", "a real small model, not a drafting head"], ["Stay exact,", "or change the drafter"], 1),
    ]
    qx, qw, ox, ow, h, step = 14, 344, 420, 226, 46, 76
    for r, (q, o, k) in enumerate(qs):
        y = 12 + r * step
        c.box(qx, y, qw, h, q, None)
        c.arrow(qx + qw + 1, y + h / 2, ox - 3, y + h / 2, "m", "ln cm thin")
        c.text((qx + qw + ox) / 2, y + h / 2 - 6, "no", "tx-s", "middle")
        c.box(ox, y, ow, h, o, k)
        c.arrow(qx + qw / 2, y + h + 1, qx + qw / 2, y + step - 3, "m", "ln cm thin")
        c.text(qx + qw / 2 + 8, y + h + 18, "yes", "tx-s")
    y = 12 + 4 * step
    c.box(qx, y, ox + ow - qx, 58, ["A relaxed rule, chosen in the table below", "exact rule on the first tokens of the answer · report the time per answer, not the tokens per round"], 4, lh=18)
    c.text(qx, 388, "blue: an exact method · amber: a lossy rule", "tx-s")
    c.save()


if __name__ == "__main__":
    decide()
