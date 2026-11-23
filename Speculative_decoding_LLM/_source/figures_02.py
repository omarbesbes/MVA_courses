"""figures_02.py — static figure of page 2 (the lossless frontier). Writes figures/02/*.svg.

    python3 figures_02.py && node build.mjs 02_lossless.html
"""
from figures_common import Canvas

SUB = "02"


def drafters():
    """Four sources of a draft: separate small model, head on the target, lookup, parallel block drafter."""
    c = Canvas("drafters", 660, 372, "Four ways to produce a draft: a separate small model, a head on the target, a lookup, a block drafter; for each, where its knowledge comes from and how many passes a draft costs.", SUB)
    c.text(190, 16, "what it knows", "tx-s", "middle")
    c.text(350, 16, "how it drafts", "tx-s", "middle")
    c.text(548, 16, "cost of a draft", "tx-s", "middle")
    rows = [
        (["separate", "small model"], ["its own weights"], 2, ["one token per pass", "of the small model"], 4, [1, 2, 3, 4], "4 tokens: 4 passes of a model"),
        (["head on", "the target"], ["the target's", "hidden state"], 1, ["one token per pass", "of one layer"], 4, [1, 2, 3, 4], "4 tokens: 4 passes of one layer"),
        (["lookup"], ["the prompt, past", "outputs, a datastore"], None, ["a search:", "no model"], 4, [0, 0, 0, 0], "4 tokens: no pass"),
        (["block", "drafter"], ["the target's", "hidden states"], 1, ["the whole block", "in one pass"], 8, [1, 1, 1, 1, 1, 1, 1, 1], "8 tokens: 1 pass (16 in the papers)"),
    ]
    for r, (name, know, kk, how, n, passes, cost) in enumerate(rows):
        y = 30 + r * 86
        for i, line in enumerate(name):
            c.text(14, y + 26 + i * 17 - (0 if len(name) > 1 else -8), line, "tx-b")
        c.box(112, y + 4, 156, 48, know, kk)
        c.arrow(269, y + 28, 288, y + 28, "m", "ln cm thin")
        c.box(290, y + 4, 136, 48, how, 2 if r != 2 else None)
        c.arrow(427, y + 28, 446, y + 28, "m", "ln cm thin")
        w = 22 if n == 4 else 20
        gap = 6 if n == 4 else 3.5
        x0 = 452
        for i in range(n):
            c.chip(x0 + i * (w + gap), y + 6, w, 24, str(passes[i]) if passes[i] else "–", 2)
        c.text(x0, y + 48, cost, "tx-s")
        if r < 3:
            c.line(14, y + 72, 646, y + 72, "gr")
    c.text(112, 366, "The number in a token is the pass that wrote it; a dash means no pass.", "tx-s")
    c.save()


if __name__ == "__main__":
    drafters()
