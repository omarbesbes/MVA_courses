"""R6b: 2-D view of the position table P and of its additive fit r_i + c_j (final layer, post-norm, trained).

Reads  SP/lab_cache/feats/trained_postnorm.npy (1000 x 256 x 768, memory-mapped; position = 16*row + col).
Writes code/results/r6_position_plane.npz: coords_P, coords_F (256 x 2, same two principal directions of P),
var_share_2 (share of the variance of P explained by them), var_shares, r2_additive.
"""
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FEATS = "/tmp/claude-0/-home-user-MVA-courses/0bf8c9d0-cffb-55d5-b9e4-5992de5f6b3a/scratchpad/lab_cache/feats/trained_postnorm.npy"
OUT = os.path.join(HERE, "..", "results", "r6_position_plane.npz")

X = np.load(FEATS, mmap_mode="r")
n = X.shape[0]
P = np.zeros((256, X.shape[2]), dtype=np.float64)
for s in range(0, n, 100):                      # mean over images, chunked
    P += np.asarray(X[s:s + 100], dtype=np.float64).sum(0)
P /= n
P -= P.mean(0, keepdims=True)                   # centre over positions
T = P.reshape(16, 16, -1)
F = (T.mean(1, keepdims=True) + T.mean(0, keepdims=True)).reshape(256, -1)   # r_i + c_j (T is centred)
r2 = 1 - ((P - F) ** 2).sum() / (P ** 2).sum()
U, S, Vt = np.linalg.svd(P, full_matrices=False)
shares = S ** 2 / (S ** 2).sum()
V = Vt[:2].T
np.savez(OUT, coords_P=P @ V, coords_F=F @ V, var_share_2=shares[:2].sum(), var_shares=shares[:2], r2_additive=r2)
print("R2_add", r2, "shares", shares[:2])
