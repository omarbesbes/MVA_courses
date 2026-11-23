"""check_01.py -- every number written on page 01_background.html. numpy only."""
import numpy as np
np.set_printoptions(precision=4, suppress=True)
print("== tokens ==")
print("224/14 =", 224 // 14, " patches", (224 // 14) ** 2, " tokens", 256 + 1 + 4, " 12*64 =", 12 * 64, " 261*768 =", 261 * 768)
print("params per attention: 4*768*768 =", 4 * 768 * 768, " MLP 2*768*3072 =", 2 * 768 * 3072, " attention matrix 261x261 =", 261 * 261)
print("== softmax toy ==")
s = np.array([2., 1., 0.]); w = np.exp(s) / np.exp(s).sum(); V = np.array([[3., 0.], [0., 3.], [-3., -3.]])
print("scores", s, "weights", w, "sum", w.sum(), "output", w @ V)
print("tokens-scaling 1/sqrt(64) =", 1 / 8, " scores 16,8,0 /8 =", np.array([16, 8, 0]) / 8)
print("== superposition ==")
ang = np.deg2rad([0, 120, 240]); D = np.c_[np.cos(ang), np.sin(ang)]
print("Gram\n", D @ D.T)
for z in ([1, 0, 0], [1, 1, 0], [1, 0.5, 0]):
    a = np.array(z) @ D; print("z", z, "a", a, "readout D a =", D @ a)
ang5 = np.deg2rad(np.arange(5) * 72); D5 = np.c_[np.cos(ang5), np.sin(ang5)]
print("pentagon coherence", np.abs(D5 @ D5.T - np.eye(5)).max(), "cos72 =", np.cos(np.deg2rad(72)))
print("Welch c=5,d=2:", np.sqrt((5 - 2) / (2 * 4)), " c=3:", np.sqrt(1 / 4))
print("P(two of 5 features active) with p=0.1:", 1 - 0.9 ** 5 - 5 * 0.1 * 0.9 ** 4)
print("== topk toy ==")
P = np.array([[2.0, -0.5, 1.0, 0.3], [0.2, 0.1, -0.3, 0.4], [3.0, 1.5, 0.8, 2.2]])
print("relu\n", np.maximum(P, 0))
def topk(P, k):
    Z = np.zeros_like(P)
    for i, r in enumerate(P):
        j = np.argsort(-r)[:k]; Z[i, j] = np.maximum(r[j], 0)
    return Z
print("top-2 per row\n", topk(P, 2))
R = np.maximum(P, 0); thr = np.sort(R.ravel())[::-1][5]  # keep 6 = 3 rows * 2
B = np.where(R >= np.sort(R.ravel())[::-1][5], R, 0); print("batchtopk (6 total)\n", B, "per row counts", (B > 0).sum(1))
print("== SAE R2 / FVU ==")
print("R2>88% -> FVU <", 1 - 0.88)
print("== archetypal ==")
print("S 32000x128000 entries", 32000 * 128000, " vs free D 32000x768", 32000 * 768)
print("tokens 1.4e6*261 =", 1.4e6 * 261)
