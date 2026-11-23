"""figures_05.py — static figures of page 5 (steps and routing). Writes figures/05/*.svg.

    python3 figures_05.py && node build.mjs 05_reasoning.html
"""
from figures_common import Canvas

SUB = "05"


def method_map():
    """Two axes: the unit that is accepted (token / step) and whether the large model still processes it."""
    c = Canvas("map", 660, 330, "A two by two map of methods: unit of acceptance (token or step) against whether the large model still processes what is accepted.", SUB)
    x0, y0, cw, rh = 176, 44, 236, 134
    c.text(x0 + cw / 2, 30, "unit accepted: a token", "tx-b", "middle")
    c.text(x0 + cw + cw / 2, 30, "unit accepted: a step", "tx-b", "middle")
    rows = [("the large model", "still processes", "what is accepted", "→ latency saved,", "   compute not"),
            ("the large model", "is skipped on", "what is accepted", "→ compute saved; quality:", "   the small model's")]
    cells = [
        [["exact speculative decoding", "(pages 1–2)", "relaxed acceptance (page 3)", "judges (page 4)"],
         ["SpecReason: reads, gives a mark", "Lookahead Reasoning: writes", "its own step in parallel", "GSI, SPECS"]],
        [["token routing: R2R, CITER", "(the large model reads the", "small model's tokens later,", "in bulk)"],
         ["RSD: a reward model accepts", "step-level cascades", "", ""]],
    ]
    for r in range(2):
        y = y0 + r * rh
        for k, line in enumerate(rows[r]):
            c.text(14, y + 34 + k * 16, line, "tx-b" if k < 3 else "tx-s")
        for col in range(2):
            x = x0 + col * cw
            c.rect(x + 4, y + 4, cw - 8, rh - 8, ("a1 ln c1 thin" if r == 0 else "a2 ln c2 thin"), 8)
            for k, line in enumerate(cells[r][col]):
                if line:
                    c.text(x + 18, y + 34 + k * 19, line, "tx")
    c.text(x0 + cw / 2, 324, "blue: speculative side", "tx-s", "middle")
    c.text(x0 + cw + cw / 2, 324, "orange: cascade side", "tx-s", "middle")
    c.save()


def flows():
    """Three ways to accept a drafted step: RSD, SpecReason, Lookahead Reasoning."""
    c = Canvas("flows", 660, 356, "Control flow of three step-level methods: who judges the drafted step and what the large model does.", SUB)
    rows = [
        ("RSD", ["small model", "drafts a step"], ["reward model", "scores it: r"], "r ≥ δ ?", ["large model", "rewrites the step"], None),
        ("SpecReason", ["small model", "drafts a step"], ["large model reads it,", "gives a mark 0–9"], "mark ≥ 7 ?", ["large model", "rewrites the step"], 1),
        ("Lookahead", ["small model", "drafts a step"], ["large model writes its", "own step, in parallel"], "same meaning ?", ["use the large", "model's step"], 1),
    ]
    for r, (name, a, b, q, d, bk) in enumerate(rows):
        y = 16 + r * 114
        c.text(14, y + 38, name, "tx-b")
        if r == 2:
            c.text(14, y + 54, "Reasoning", "tx-b")
        c.box(104, y + 12, 118, 46, a, 2)
        c.arrow(223, y + 35, 246, y + 35, "m", "ln cm thin")
        c.box(248, y + 12, 150, 46, b, bk)
        c.arrow(399, y + 35, 422, y + 35, "m", "ln cm thin")
        c.box(424, y + 16, 104, 38, [q], None)
        # yes: keep the draft
        c.arrow(529, y + 35, 556, y + 35, "m", "ln cm thin")
        c.text(542, y + 29, "yes", "tx-s", "middle")
        c.box(558, y + 16, 92, 38, ["keep the draft"], 3)
        # no: fallback
        c.arrow(476, y + 55, 476, y + 72, "m", "ln cm thin")
        c.text(486, y + 68, "no", "tx-s")
        c.box(410, y + 74, 132, 34, d, 1, lh=14)
    c.save()


if __name__ == "__main__":
    method_map()
    flows()
