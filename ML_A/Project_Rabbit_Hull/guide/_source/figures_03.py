"""figures_03.py -- static SVG figures of page 03 (concepts and tasks), written to figures/03/.
Run: python3 figures_03.py   (then node build.mjs 03_concepts_tasks.html)"""
from figures_common import Canvas

SUB = "03"


def rect(c, x, y, w, h, cls, extra=""):
    c.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" class="{cls}"{extra}/>')


def fig_rowconv():
    c = Canvas("rowconv", 720, 250, "Row convention: a = z D, a row of codes times the dictionary gives a row of activations", sub=SUB)
    # z: 1 x c row of cells, 3 active
    nz, cw = 14, 22
    x0, y0 = 30, 60
    active = {2: "f2", 6: "f2", 11: "f2"}
    for i in range(nz):
        rect(c, x0 + i * cw, y0, cw, 26, "f2 a2" if i in active else "gr", ' style="stroke-width:1"' if i not in active else ' stroke-width="1"')
    for i in active:
        c.text(x0 + i * cw + cw / 2, y0 + 18, "z" + "₁₂₃"[list(active).index(i)] if False else "+", "tx-b", "middle")
    c.text(x0, y0 - 12, "z ∈ ℝᶜ : c = 32 000 codes, at most k = 8 non-zero", "tx-b")
    c.text(x0 + nz * cw / 2, y0 + 48, "row vector, ≥ 0", "tx-s", "middle")
    # times
    c.text(x0 + nz * cw + 18, y0 + 19, "×", "tx-b", "middle")
    # D: c rows, d columns
    dx, dy, dw, rh = 400, 40, 170, 18
    rows = 8
    for r in range(rows):
        hot = r in (2, 5, 6)
        rect(c, dx, dy + r * rh, dw, rh, "f1 a1" if hot else "gr", ' stroke-width="1"')
        c.text(dx + 8, dy + r * rh + 13, f"D{'ᵢ'}  (atom, unit norm)" if hot else "…", "tx-s")
    c.text(dx, dy - 12, "D ∈ ℝᶜˣᵈ : one atom per row", "tx-b")
    c.text(dx + dw / 2, dy + rows * rh + 20, "d = 768 columns", "tx-s", "middle")
    # arrows z active -> D rows
    for (i, r) in zip(active, (2, 5, 6)):
        c.add(f'<line x1="{x0 + i * cw + cw / 2:.1f}" y1="{y0 + 26}" x2="{dx - 4}" y2="{dy + r * rh + rh / 2:.1f}" class="ln c2 thin dash"/>')
    # equals a
    c.text(dx + dw + 24, y0 + 40, "=", "tx-b", "middle")
    ax, ay = 606, 76
    for i in range(6):
        rect(c, ax, ay + i * 0 , 0, 0, "gr")
    rect(c, ax, ay, 90, 26, "f3 a3", ' stroke-width="1"')
    c.text(ax + 45, ay - 10, "a ∈ ℝᵈ", "tx-b", "middle")
    c.text(ax + 45, ay + 44, "token activation", "tx-s", "middle")
    c.text(ax + 45, ay + 58, "(a row)", "tx-s", "middle")
    c.text(360, 232, "a = Σ over the active i of  zᵢ Dᵢ  — a non-negative combination of at most k atoms", "tx-s", "middle")
    c.save()


def fig_pipeline():
    c = Canvas("pipeline", 740, 300, "Pipeline: image, DINOv2, token activations A, sparse codes Z, probe", sub=SUB)
    # image grid
    gx, gy, g = 14, 70, 11
    for i in range(16):
        for j in range(16):
            rect(c, gx + j * g * 0.6, gy + i * g * 0.6, g * 0.6, g * 0.6, "gr", ' stroke-width="0.6" fill="none"')
    c.text(gx + 48, gy - 24, "image 224 × 224", "tx-b", "middle")
    c.text(gx + 48, gy - 10, "16 × 16 patches of 14 px", "tx-s", "middle")
    # special tokens
    # boxes
    def box(x, y, w, h, cls, lines, tcls="tx-b"):
        rect(c, x, y, w, h, cls, ' rx="6" stroke-width="1.5"')
        for k, s in enumerate(lines):
            c.text(x + w / 2, y + h / 2 + (k - (len(lines) - 1) / 2) * 15 + 4, s, tcls if k == 0 else "tx-s", "middle")
    box(140, 100, 90, 70, "ln c3 a3", ["f", "DINOv2-B", "+ 4 registers"])
    box(290, 100, 110, 70, "ln c3 a3", ["A", "261 × 768", "tokens × width"])
    box(460, 100, 110, 70, "ln c2 a2", ["Z", "261 × 32 000", "k = 8 per row"])
    box(630, 100, 90, 70, "ln c5 a5", ["Y", "261 × o", "probe outputs"])
    c.arrow(112, 135, 138, 135, 3); c.arrow(230, 135, 288, 135, 3)
    c.arrow(400, 135, 458, 135, 2); c.arrow(570, 135, 628, 135, 5)
    c.text(430, 92, "SAE encoder", "tx-s", "middle")
    c.text(430, 190, "A ≈ Z D", "tx-b", "middle")
    c.text(600, 92, "W′ = D Wᵀ  (c × o)", "tx-s", "middle")
    # lower path: A -> Wᵀ -> Y
    c.add('<path d="M345 172 L345 240 L675 240 L675 172" class="ln c5 thin dash" fill="none" marker-end="url(#03-pipeline-arr-5)"/>')
    c.text(510, 232, "same outputs directly: Y = A Wᵀ  (W is o × d)", "tx-s", "middle")
    c.text(510, 262, "Y = A Wᵀ = (Z D) Wᵀ = Z (D Wᵀ) = Z W′", "tx-b", "middle")
    c.text(510, 282, "the probe read in the concept basis (reconstruction error and probe bias are left out by the paper)", "tx-s", "middle")
    c.save()


def fig_elsewhere():
    c = Canvas("elsewhere_logic", 700, 280, "Logic of an Elsewhere concept: fires off the object, only if the object is present", sub=SUB)
    n, s = 7, 30

    def grid(ox, oy, obj, fire, title, sub):
        for i in range(n):
            for j in range(n):
                cls = "gr"
                if (i, j) in obj:
                    cls = "f3 a3"
                if (i, j) in fire:
                    cls = "f2"
                rect(c, ox + j * s, oy + i * s, s, s, cls + (" " if cls == "gr" else ""), ' stroke-width="1"' if cls != "f2" else ' fill-opacity="0.55" stroke-width="1"')
        c.text(ox + n * s / 2, oy - 22, title, "tx-b", "middle")
        c.text(ox + n * s / 2, oy - 7, sub, "tx-s", "middle")
    obj = {(i, j) for i in range(2, 5) for j in range(1, 3)}
    fire = {(i, j) for i in range(n) for j in range(n) if (i, j) not in obj and j >= 3 and (i + j) % 2 == 0}
    grid(20, 50, obj, fire, "object present", "concept fires on tokens away from the object")
    grid(260, 50, set(), set(), "object removed", "the concept is silent everywhere")
    grid(500, 50, obj, set(), "a plain background detector", "would fire here and there, object or not")
    # third grid: background detector fires on far cells regardless -> show nothing; instead legend
    c.add(f'<rect x="500" y="50" width="{n*s}" height="{n*s}" class="gr" fill="none"/>')
    # background detector in the right grid: fire on right columns regardless
    for i in range(n):
        for j in range(5, 7):
            rect(c, 500 + j * s, 50 + i * s, s, s, "f4", ' fill-opacity="0.5" stroke-width="1"')
    c.text(20, 28 + 250, "■ object tokens", "tx-s"); c.text(150, 278, "■ concept fires", "tx-s")
    c.text(300, 278, "Elsewhere = (not on the object) AND (object exists in the image)", "tx-b")
    c.save()


if __name__ == "__main__":
    fig_rowconv(); fig_pipeline(); fig_elsewhere()
