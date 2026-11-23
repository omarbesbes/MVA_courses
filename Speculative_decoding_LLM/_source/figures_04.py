"""figures_04.py — static figures of page 4 (judges). Writes figures/04/*.svg.

    python3 figures_04.py && node build.mjs 04_judges.html
"""
from figures_common import Canvas

SUB = "04"


def pipeline():
    """Verification with a judge: one target pass gives the exact test and, through a linear head, the judge."""
    c = Canvas("pipeline", 660, 318, "The target reads the draft once; its distributions give the exact test and its hidden states feed a linear judge; a token passes if either accepts.", SUB)
    xs = [190, 276, 362, 448, 534]
    toks = ["x̃₁", "x̃₂", "x̃₃", "x̃₄", "x̃₅"]
    exact = [1, 0, 1, 0, 1]      # toy masks
    judge = [1, 1, 1, 0, 1]
    c.chip(20, 278, 150, 26, "prefix")
    for i, x in enumerate(xs):
        c.chip(x, 278, 70, 26, toks[i], 2, tcls="tx-i")
        c.arrow(x + 35, 277, x + 35, 248, "m", "ln cm thin")
    c.arrow(95, 277, 95, 248, "m", "ln cm thin")
    c.box(20, 206, 584, 40, ["target Mp — one pass over prefix + draft"], 1)
    # the three rows, named on the left
    c.text(20, 162, "judge", "tx-b")
    c.text(20, 177, "reads the hidden states", "tx-s")
    c.text(20, 100, "exact test", "tx-b")
    c.text(20, 115, "reads the distributions", "tx-s")
    c.text(20, 40, "decision", "tx-b")
    c.text(20, 55, "yes if either says yes", "tx-s")
    for i, x in enumerate(xs):
        xm = x + 35
        c.arrow(xm, 205, xm, 184, "m", "ln cm thin")
        c.chip(xm - 30, 148, 60, 34, "yes" if judge[i] else "no", 4 if judge[i] else 6, tcls="tx-s")
        c.line(xm, 147, xm, 122, "ln cm hair")
        c.chip(xm - 30, 86, 60, 34, "yes" if exact[i] else "no", 3 if exact[i] else 6, tcls="tx-s")
        c.arrow(xm, 85, xm, 62, "m", "ln cm thin")
        before = all(exact[j] or judge[j] for j in range(i))
        ok = (exact[i] or judge[i]) and before
        c.chip(xm - 30, 26, 60, 34, "accept" if ok else ("reject" if before else "—"),
               (3 if exact[i] else 4) if ok else (6 if before else None), tcls="tx-s")
    c.save()


def mining():
    """AutoJudge: label one mismatch by swapping the drafter's token and letting the target regenerate."""
    c = Canvas("mining", 660, 250, "Swap the drafter's token into the target's answer, regenerate the rest, compare the final answers.", SUB)
    c.box(16, 20, 190, 52, ["target's answer y", "final answer α"], 1)
    c.arrow(207, 46, 244, 46, "m", "ln cm thin")
    c.box(246, 20, 190, 52, ["first mismatch t:", "swap in the drafter's token"], 2)
    c.arrow(437, 46, 474, 46, "m", "ln cm thin")
    c.box(476, 20, 168, 52, ["target regenerates", "the rest → answer α′"], 1)
    c.arrow(560, 73, 560, 108, "m", "ln cm thin")
    c.box(476, 110, 168, 40, ["is α′ equivalent to α?"], None)
    # yes branch
    c.arrow(475, 130, 352, 130, "m", "ln cm thin")
    c.text(414, 124, "yes", "tx-s", "middle")
    c.box(160, 104, 190, 52, ["label: unimportant", "keep the new text as y"], 4)
    c.path("M160 130 H110 V74", "ln cm thin nofill")
    c.arrow(110, 84, 110, 74, "m", "ln cm thin")
    # no branch
    c.arrow(560, 151, 560, 186, "m", "ln cm thin")
    c.text(570, 172, "no", "tx-s")
    c.box(446, 188, 198, 52, ["label: important", "keep the target's token"], 6)
    c.text(124, 206, "in both cases, continue with the next mismatch", "tx-s")
    c.path("M446 214 H60 V74", "ln cm thin nofill")
    c.arrow(60, 84, 60, 74, "m", "ln cm thin")
    c.save()


if __name__ == "__main__":
    pipeline()
    mining()
