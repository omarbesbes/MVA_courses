"""figures_01.py -- static SVG figures of page 01 (background), written to figures/01/. Run: python3 figures_01.py"""
import sys, math
import numpy as np
sys.path.insert(0, "/home/user/MVA_courses/ML_A/Project_Rabbit_Hull/code")
from rh.aa import archetypal_analysis, kmeans
from figures_common import Canvas, Fig, esc

SUB = "01"


def rect(c, x, y, w, h, cls, extra=""):
    c.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="3" class="{cls}"{extra}/>')


def box(c, x, y, w, h, lines, cls="f1 a1", tcls="tx"):
    rect(c, x, y, w, h, cls, ' stroke-width="1.2"')
    n = len(lines)
    for i, s in enumerate(lines):
        c.text(x + w / 2, y + h / 2 + (i - (n - 1) / 2) * 15 + 5, s, tcls, "middle")


def fig_tokens():
    c = Canvas("tokens", 720, 300, "An image cut into a 16 by 16 grid of patches, then a sequence of 261 tokens", sub=SUB)
    gx, gy, g = 20, 60, 11.5
    for i in range(16):
        for j in range(16):
            rect(c, gx + j * g, gy + i * g, g, g, "f3 a3", ' stroke-width="0.6"')
    c.text(gx + 8 * g, 38, "image 224 × 224 px", "tx-b", "middle")
    c.text(gx + 8 * g, 52, "16 × 16 patches of 14 × 14 px", "tx-s", "middle")
    c.arrow(gx + 16 * g + 8, gy + 8 * g, 262, gy + 8 * g, 3)
    c.text(236, gy + 8 * g - 8, "flatten + linear map", "tx-s", "middle")
    # sequence
    sx, sy, w, h = 275, 60, 24, 24
    labels = [("cls", "f2 a2"), ("r1", "f5 a5"), ("r2", "f5 a5"), ("r3", "f5 a5"), ("r4", "f5 a5")]
    for i, (l, cl) in enumerate(labels):
        rect(c, sx + i * (w + 3), sy, w, h, cl, ' stroke-width="1"')
        c.text(sx + i * (w + 3) + w / 2, sy + 16, l, "tx-s", "middle")
    for i in range(5, 12):
        rect(c, sx + i * (w + 3), sy, w, h, "f3 a3", ' stroke-width="1"')
        c.text(sx + i * (w + 3) + w / 2, sy + 16, f"p{i-4}" if i < 11 else "…", "tx-s", "middle")
    c.text(sx, sy - 12, "t = 261 tokens = 1 class + 4 registers + 256 patches", "tx-b")
    # embedding vector
    ex, ey = 275, 130
    c.text(ex, ey - 8, "each token is a vector of d = 768 numbers (a row of the matrix X ∈ ℝ²⁶¹ˣ⁷⁶⁸)", "tx-s")
    for r, (l, cl) in enumerate([("class token", "f2 a2"), ("4 registers", "f5 a5"), ("patch 1", "f3 a3"), ("patch 2", "f3 a3"), ("…  patch 256", "f3 a3")]):
        rect(c, ex, ey + r * 20, 270, 17, cl, ' stroke-width="1"')
        c.text(ex + 8, ey + r * 20 + 13, l, "tx-s")
    c.text(ex + 280, ey + 50, "+ position embedding", "tx-s")
    c.text(ex + 280, ey + 66, "added to each patch row", "tx-s")
    c.text(ex, ey + 128, "Same sequence enters every layer; its length (261) and width (768) never change.", "tx-s")
    c.text(20, 270, "green = patch tokens · orange = class token · purple = registers", "tx-s")
    c.save()


def fig_block():
    c = Canvas("block", 720, 330, "A pre-norm transformer block with two residual additions", sub=SUB)
    cx = 190
    c.text(cx, 20, "x  (residual stream, 261 × 768)", "tx-b", "middle")
    ys = [40, 210]
    # stream line
    c.add(f'<line x1="{cx}" y1="30" x2="{cx}" y2="310" class="ln c3" stroke-width="2.5"/>')
    # branch 1
    for k, (y0, name, sub) in enumerate([(52, "Attention", "12 heads, mixes tokens"), (172, "MLP", "768 → 3072 → 768, each token alone")]):
        bx = 330
        c.add(f'<path d="M{cx} {y0} H{bx-10} " class="ln c2 thin"/>')
        box(c, bx - 10, y0 - 16, 60, 32, ["LN"], "f4 a4")
        c.add(f'<line x1="{bx+50}" y1="{y0}" x2="{bx+70}" y2="{y0}" class="ln c2 thin"/>')
        box(c, bx + 70, y0 - 22, 130, 44, [name, "× LayerScale"], "f2 a2")
        c.text(bx + 210, y0 - 2, sub, "tx-s")
        c.add(f'<path d="M{bx+200} {y0} H{bx+206} " class="ln c2 thin"/>')
        # return to stream
        yy = y0 + 62
        c.add(f'<path d="M{bx+135} {y0+22} V{yy} H{cx+12}" class="ln c2 thin dash"/>')
        c.add(f'<circle cx="{cx}" cy="{yy}" r="11" class="f3 a3 ln c3"/>')
        c.text(cx, yy + 5, "+", "tx-b", "middle")
    c.text(cx - 14, 120, "x + Attn(LN(x))", "tx-s", "end")
    c.text(cx - 14, 240, "x + MLP(LN(·))", "tx-s", "end")
    c.text(cx - 14, 300, "next block", "tx-s", "end")
    c.text(20, 322, "after the last block: final LayerNorm → the token activations that the paper analyses", "tx-s")
    c.save()


def fig_student_teacher():
    c = Canvas("student_teacher", 720, 300, "DINO self-distillation: student and teacher, centring, cross-entropy", sub=SUB)
    box(c, 20, 50, 110, 44, ["global crops", "224 px (2)"], "f3 a3")
    box(c, 20, 170, 110, 44, ["all crops", "+ 8 local 96 px"], "f3 a3")
    c.text(75, 120, "one image", "tx-s", "middle")
    box(c, 175, 50, 120, 44, ["teacher ViT"], "f1 a1")
    box(c, 175, 170, 120, 44, ["student ViT"], "f2 a2")
    box(c, 335, 50, 100, 44, ["head → softmax", "prototypes"], "f1 a1")
    box(c, 335, 170, 100, 44, ["head → softmax", "prototypes"], "f2 a2")
    box(c, 475, 50, 90, 30, ["centring"], "f4 a4")
    c.arrow(130, 72, 175, 72, 1); c.arrow(295, 72, 335, 72, 1); c.arrow(435, 65, 475, 65, 1)
    c.arrow(130, 192, 175, 192, 2); c.arrow(295, 192, 335, 192, 2)
    box(c, 560, 110, 140, 50, ["cross-entropy", "H(p_teacher, p_student)"], "f4 a4")
    c.arrow(565, 72, 620, 110, 1); c.arrow(435, 192, 620, 160, 2)
    c.add(f'<path d="M235 170 V120 " class="ln c1 thin dash"/>')
    c.text(245, 142, "EMA of the student", "tx-s")
    c.arrow(235, 130, 235, 96, 1, "ln c1 thin dash")
    c.text(335, 130, "no gradient through the teacher", "tx-s")
    c.text(20, 270, "Gradient (orange) only reaches the student; the teacher is a slow average of past students.", "tx-s")
    c.save()


def fig_superposition():
    c = Canvas("superposition", 720, 300, "Superposition: three directions in the plane and a read-out with interference", sub=SUB)
    f = Fig(c, (30, 40, 220, 220), (-1.4, 1.4), (-1.4, 1.4))
    ang = np.deg2rad([0, 120, 240]); D = np.c_[np.cos(ang), np.sin(ang)]
    f.line(-1.3, 0, 1.3, 0, "ax"); f.line(0, -1.3, 0, 1.3, "ax")
    for i, (x, y) in enumerate(D):
        c.arrow(f.X(0), f.Y(0), f.X(x), f.Y(y), 2)
        f.text(x * 1.18, y * 1.18, f"d{i+1}", "tx-b", "middle", dy=4)
    c.text(30, 28, "3 features in a 2-D space (d₂ = 120°, d₃ = 240°)", "tx-b")
    # two active
    a = np.array([1, 1, 0.]) @ D
    f.circle(a[0], a[1], 5, "f3")
    f.text(a[0], a[1], "a = d₁ + d₂", "tx-s", "start", dx=8, dy=-6)
    # readout table
    c.text(300, 60, "Read-out  rᵢ = dᵢ · a", "tx-b")
    rows = [("a = d₁", [1, -.5, -.5]), ("a = d₁ + d₂", [.5, .5, -1.]), ("a = d₁ + ½ d₂", [.75, 0, -.75])]
    c.text(300, 84, "", "tx-s")
    for j, h in enumerate(["r₁", "r₂", "r₃"]):
        c.text(500 + j * 60, 84, h, "tx-b", "middle")
    for i, (name, r) in enumerate(rows):
        y = 112 + i * 34
        c.text(300, y, name, "tx")
        for j, v in enumerate(r):
            true = [1, 0, 0][j] if i == 0 else ([1, 1, 0][j] if i == 1 else [1, .5, 0][j])
            rect(c, 472 + j * 60, y - 17, 56, 24, "f3 a3" if abs(v - true) < 1e-9 else "f2 a2", ' stroke-width="1"')
            c.text(500 + j * 60, y, f"{v:g}", "tx", "middle")
    c.text(300, 232, "green: read-out equals the true code · orange: interference from", "tx-s")
    c.text(300, 248, "non-orthogonal directions (cosine −½ between any two atoms).", "tx-s")
    c.text(300, 276, "With one feature active the others read −½: a threshold fixes it.", "tx-s")
    c.save()


def make_data(rng, n=240):
    ang = np.deg2rad([12, 48, 84])
    U = np.c_[np.cos(ang), np.sin(ang)]
    X = []
    for _ in range(n):
        k = 1 if rng.random() < 0.85 else 2
        idx = rng.choice(3, k, replace=False)
        z = np.zeros(3); z[idx] = rng.exponential(1, k) + 0.4
        X.append(z @ U * 1.0 + rng.normal(0, 0.05, 2))
    return np.array(X), U


def nmf(X, K, rng, it=400):
    W = rng.random((len(X), K)); H = rng.random((K, 2))
    for _ in range(it):
        H *= (W.T @ X) / (W.T @ W @ H + 1e-9); W *= (X @ H.T) / (W @ H @ H.T + 1e-9)
    return H


def fig_zoo():
    rng = np.random.default_rng(3)
    X, U = make_data(rng)
    c = Canvas("zoo", 720, 500, "The same 2-D data set factorised by five methods", sub=SUB)
    panels = []
    mu = X.mean(0)
    # kmeans
    km = kmeans(X, 3, seed=0)["centers"]
    # pca
    u, s, vt = np.linalg.svd(X - mu, full_matrices=False)
    pc = [(mu, vt[0] * s[0] / math.sqrt(len(X)) * 2), (mu, vt[1] * s[1] / math.sqrt(len(X)) * 2)]
    H = nmf(X, 2, rng)
    aa = archetypal_analysis(X, 3, seed=0)["Z"]
    # sparse k=1 unit atoms: spherical k-means on directions
    Xn = X / np.linalg.norm(X, axis=1, keepdims=True)
    A = Xn[rng.choice(len(X), 3, replace=False)]
    for _ in range(50):
        lab = np.argmax(Xn @ A.T, 1)
        for j in range(3):
            if (lab == j).any():
                v = Xn[lab == j].mean(0); A[j] = v / np.linalg.norm(v)
    titles = [("k-means", "Zᵢ one-hot", 1), ("PCA", "D Dᵀ = I", 1), ("NMF", "Z ≥ 0, D ≥ 0", 1),
              ("Archetypal analysis", "Zᵢ ∈ simplex, Dᵢ ∈ conv(A)", 1), ("Sparse code (SAE-like)", "‖Zᵢ‖₀ ≤ 1, ‖Dᵢ‖ = 1", 2)]
    pw, ph = 210, 210
    pos = [(15, 25), (250, 25), (485, 25), (15, 265), (250, 265)]
    for p, (tt, cons, col) in enumerate(titles):
        x0, y0 = pos[p]
        f = Fig(c, (x0, y0 + 24, pw, ph - 24), (-0.3, 4.9), (-0.3, 4.9))
        c.text(x0, y0 + 4, tt, "tx-b"); c.text(x0, y0 + 18, cons, "tx-s")
        rect(c, x0, y0 + 24, pw, ph - 24, "gr", ' fill="none" stroke-width="0.8"')
        for x, y in X:
            f.circle(x, y, 1.8, "f3")
        if p == 0:
            for (x, y) in km: f.circle(x, y, 6, "f1"); 
        if p == 1:
            for m, v in pc:
                c.arrow(f.X(m[0]), f.Y(m[1]), f.X(m[0] + v[0]), f.Y(m[1] + v[1]), 2)
                c.arrow(f.X(m[0]), f.Y(m[1]), f.X(m[0] - v[0]), f.Y(m[1] - v[1]), 2)
        if p == 2:
            for h in H:
                c.arrow(f.X(0), f.Y(0), f.X(h[0]), f.Y(h[1]), 2)
        if p == 3:
            hull = np.array(aa)
            order = np.argsort(np.arctan2(hull[:, 1] - hull[:, 1].mean(), hull[:, 0] - hull[:, 0].mean()))
            f.path([tuple(hull[i]) for i in order], "ln c1 thin", close=True)
            for (x, y) in hull: f.circle(x, y, 6, "f1")
        if p == 4:
            for a in A:
                c.arrow(f.X(0), f.Y(0), f.X(a[0] * 4.2), f.Y(a[1] * 4.2), 2)
    c.text(485, 290, "Same data, five constraints:", "tx-b")
    for i, s_ in enumerate(["k-means: 3 centres;", "PCA: orthogonal signed axes;", "NMF: positive parts;",
                           "AA: corners of a polygon;", "sparse code: unit directions."]):
        c.text(485, 310 + i * 17, s_, "tx-s")
    c.text(485, 410, "blue: atoms that are points", "tx-s")
    c.text(485, 427, "orange: atoms that are directions", "tx-s")
    c.text(485, 444, "green: data (240 points, rays", "tx-s")
    c.text(485, 461, "at 12°, 48°, 84°)", "tx-s")
    c.save()
    # numbers for the check script
    return X, km, aa, H, A


def fig_sae():
    c = Canvas("sae", 720, 280, "Architecture of a sparse autoencoder", sub=SUB)
    box(c, 20, 100, 90, 60, ["activation", "a ∈ ℝ⁷⁶⁸"], "f3 a3")
    box(c, 160, 100, 120, 60, ["encoder", "z = Ψ(a)"], "f2 a2")
    box(c, 330, 90, 130, 80, ["code z ∈ ℝ³²⁰⁰⁰", "k = 8 non-zero", "z ≥ 0"], "f4 a4")
    box(c, 510, 100, 90, 60, ["decoder", "z D"], "f1 a1")
    box(c, 635, 100, 70, 60, ["â ≈ a"], "f3 a3")
    for x1, x2 in [(110, 160), (280, 330), (460, 510), (600, 635)]:
        c.arrow(x1, 130, x2, 130, 2)
    # sparse bar code
    for i in range(40):
        hot = i in (3, 11, 19, 26, 31, 35)
        h = 22 if hot else 2
        rect(c, 335 + i * 3, 220 - h, 2.4, h, "f2" if hot else "gr", "")
    c.text(335, 236, "a few concepts i fire with strength zᵢ", "tx-s")
    c.text(160, 190, "single layer + ReLU / TopK", "tx-s")
    c.text(510, 190, "rows of D = atoms (c × d)", "tx-s")
    c.text(20, 40, "loss = ‖a − z D‖² (reconstruction); sparsity comes from Ψ", "tx-b")
    c.text(20, 262, "R² = 1 − ‖A − Z D‖² / ‖A − mean(A)‖²   (paper: R² > 88 %)", "tx-s")
    c.save()


def fig_archetypal():
    rng = np.random.default_rng(5)
    X, _ = make_data(rng, 200)
    c = Canvas("archetypal", 720, 300, "Archetypal constraint: atoms are convex combinations of centroids of the data", sub=SUB)
    cent = kmeans(X, 14, seed=1)["centers"]
    f = Fig(c, (30, 40, 330, 230), (-0.3, 4.9), (-0.3, 4.9))
    rect(c, 30, 40, 330, 230, "gr", ' fill="none" stroke-width="0.8"')
    c.text(30, 28, "data (green), centroids C (grey), atoms D = S C (blue)", "tx-b")
    for x, y in X: f.circle(x, y, 1.8, "f3")
    for x, y in cent: f.circle(x, y, 3.5, "f6")
    S = rng.dirichlet(np.ones(14) * 0.3, 5)
    atoms = S @ cent
    # hull of centroids
    from rh.aa import project_simplex  # noqa
    from itertools import combinations
    pts = [tuple(p) for p in cent]
    def hull(P):
        P = sorted(P)
        def cr(o, a, b): return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
        lo = []
        for p in P:
            while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 0: lo.pop()
            lo.append(p)
        up = []
        for p in reversed(P):
            while len(up) >= 2 and cr(up[-2], up[-1], p) <= 0: up.pop()
            up.append(p)
        return lo[:-1] + up[:-1]
    h = hull(pts)
    f.path(h, "ln c1 thin dash", close=True)
    for x, y in atoms: f.circle(x, y, 6, "f1")
    c.text(400, 60, "In the paper:", "tx-b")
    for i, s in enumerate(["C : 128,000 k-means centroids (rows, in ℝ⁷⁶⁸)", "S : 32,000 × 128,000, each row ≥ 0 and sums to 1", "D = S C : atom i = convex combination of centroids",
                           "⇒ every atom lies in conv(centroids) ≈ conv(A)", "⇒ atoms are in-distribution (no atom outside the data)", "Codes Z ≥ 0, ‖Zᵢ‖₀ ≤ 8 (BatchTopK)"]):
        c.text(400, 90 + i * 24, s, "tx-s" if i else "tx")
    c.text(400, 250, "Dashed polygon = convex hull of the centroids.", "tx-s")
    c.text(400, 266, "Toy: 14 centroids, 5 atoms in the plane.", "tx-s")
    c.save()


if __name__ == "__main__":
    for fn in (fig_tokens, fig_block, fig_student_teacher, fig_superposition, fig_zoo, fig_sae, fig_archetypal):
        fn()
