"""check_04.py -- every number written on page 04_statistics_geometry.html. numpy only."""
import numpy as np
np.set_printoptions(precision=4, suppress=True)
rng = np.random.default_rng(0)
c, d, k = 32000, 768, 8

print("== occurrence (our estimate) ==")
n_img, t = 1.4e6, 261
tok = n_img * t
print("tokens", tok, " activations total k*tokens", k * tok)
for f in (0.95e8, 1.05e8, 1.15e8):
    print(f"dense concept firing {f:.2e}: fraction of tokens {f/tok:.3f}")
print("three dense, 1.05e8 each: share of all k*tokens activations", 3 * 1.05e8 / (k * tok), " range", 3*0.95e8/(k*tok), 3*1.15e8/(k*tok))
print("typical concept firing 2e6: fraction", 2e6 / tok)
print("mean firings per concept k*tok/c =", k * tok / c, " fraction", k * tok / c / tok)
print("a token has k=8 slots; a dense concept at 0.29 occupies it with prob ~0.29 -> expected number of dense concepts per token 3*0.29 =", 3*1.05e8/tok)
print("slots left for the other concepts on average:", k - 3*1.05e8/tok)

print("\n== frames ==")
welch = np.sqrt((c - d) / (d * (c - 1)))
print("Welch", welch, " Grassmannian 0.065897 / Welch =", 0.065897 / welch)
P = c * (c - 1) / 2
print("pairs", P, " std inner product 1/sqrt(d)", 1 / np.sqrt(d), " typical max sqrt(2 ln P / d)", np.sqrt(2 * np.log(P) / d))
print("tight frame level sqrt(c/d)", np.sqrt(c / d), " MP band", np.sqrt(c / d) * (1 - np.sqrt(d / c)), np.sqrt(c / d) * (1 + np.sqrt(d / c)))
print("sum of squares of sing. values = c if rows unit:", c, "; d * (c/d) =", d * c / d)
print("Welch for c=3,d=2:", np.sqrt((3 - 2) / (2 * (3 - 1))), " 3 unit vectors at 120 deg: |cos|=", 0.5)
# empirical random dictionary, smaller to be cheap: c=32000 is ok for svd (32000x768)
H = rng.standard_normal((c, d)); H /= np.linalg.norm(H, axis=1, keepdims=True)
s = np.linalg.svd(H, compute_uv=False); print("random D singular values min/max/mean", s.min(), s.max(), s.mean(), " sum sq", (s**2).sum())
G = H[:4000] @ H[:4000].T; off = G[np.triu_indices(4000, 1)]; print("random inner products (4000 atoms): std", off.std(), "max|.|", np.abs(off).max())
def hoyer(x):
    n = x.size; l1 = np.abs(x).sum(); l2 = np.linalg.norm(x); return (np.sqrt(n) - l1 / l2) / (np.sqrt(n) - 1)
print("Hoyer: gaussian d=768:", np.mean([hoyer(rng.standard_normal(d)) for _ in range(500)]), " 1-sqrt(2/pi) =", 1 - np.sqrt(2 / np.pi), " one-hot", hoyer(np.eye(d)[0]), " constant", hoyer(np.ones(d)))
print("Hoyer of a vector with 77 equal non-zeros (10%):", hoyer(np.r_[np.ones(77), np.zeros(d - 77)]))
print("JL: exp(m eps^2) with m=768, eps=0.0659^... e.g. eps=0.2: exp(m eps^2)=", np.exp(768*0.04), " (up to the unspecified constant in the O)")

print("\n== antipodal toy ==")
u = np.array([1.0, 0.0]); D2 = np.array([u, -u])
for x in (-1.5, 0.7, 2.0):
    z = np.array([max(x, 0), max(-x, 0)]); print("x =", x, " z =", z, " zD =", z @ D2)
print("cos of D_i, D_j antipodal:", D2[0] @ D2[1], " cosine similarity of the two features |x|", 1.0)
# cosine pitfall: a feature and its opposite have cosine -1 but are the same line
print("coherence mu counts |<Di,Dj>|: =", abs(D2[0] @ D2[1]), " maximal possible")

print("\n== trace identity ==")
n, cc, dd = 50, 12, 7
Z = np.abs(rng.standard_normal((n, cc))) * (rng.random((n, cc)) < 0.3); D = rng.standard_normal((cc, dd))
G = Z.T @ Z; K = D @ D.T
print("tr[Z^T Z D D^T] =", np.trace(G @ K), "  ||ZD||_F^2 =", np.linalg.norm(Z @ D) ** 2, "  <G,K>_F =", (G * K).sum(), " tr[D^T Z^T Z D] =", np.trace(D.T @ G @ D))
print("trace vs pearson: independent random Z and D at scale (c=300 atoms, d=64)")
c2, d2, n2 = 300, 64, 4000
Z2 = np.abs(rng.standard_normal((n2, c2))) * (rng.random((n2, c2)) < 8 / c2)
D2_ = rng.standard_normal((c2, d2)); D2_ /= np.linalg.norm(D2_, axis=1, keepdims=True)
G2 = Z2.T @ Z2; K2 = D2_ @ D2_.T
iu = np.triu_indices(c2, 1)
print("<G,K>_F =", (G2 * K2).sum(), " = ||ZD||^2 =", np.linalg.norm(Z2 @ D2_) ** 2, " >0 ; diagonal part", np.trace(G2), " off-diagonal part", (G2 * K2).sum() - np.trace(G2))
print("pearson corr of off-diagonal entries (G vs K):", np.corrcoef(G2[iu], K2[iu])[0, 1])
print("pearson incl. diagonal:", np.corrcoef(G2.ravel(), K2.ravel())[0, 1])
print("r=0.28 -> r^2 =", 0.28 ** 2)

print("\n== PCA ==")
print("image of a segment under linear map: x(t)=(1-t)a+tb -> (1-t)Pa+tPb: segment or point (if Pa=Pb)")
Pm = rng.standard_normal((3, 768)); a, b = rng.standard_normal(768), rng.standard_normal(768)
tt = 0.37; print("P((1-t)a+tb) - ((1-t)Pa+tPb) max abs:", np.abs(Pm @ ((1 - tt) * a + tt * b) - ((1 - tt) * Pm @ a + tt * Pm @ b)).max())
print("per-image PCA: 256 tokens, rank <= min(255, 768) = 255 ; 15/255 =", 15 / 255)
print("RGB values: 3 components of 768 ->", 3 / 768)

print("\n== position ==")
sr = [9.0, 8.1, 5.4, 7.2, 5.6, 5.4, 4.9, 4.4, 4.4, 2.8, 2.6, 2.7]
r2 = [0.63, 0.75, 0.83, 0.77, 0.81, 0.86, 0.90, 0.94, 0.96, 0.99, 1.00, 1.00]
print("sr <= 2/R^2 when R^2 is the share of the top two singular values (centred matrix):")
for i, (a, b) in enumerate(zip(sr, r2)):
    print(f" index {i} (layer {i+1} in left plot / {i} in right plot): sr={a}  R2={b}  bound 2/R2 = {2/b:.2f}  violated={a > 2/b + 1e-9}")
# example: sigma^2 = (1, 0.98, tiny) -> R2 ~ 0.99+, sr
sv2 = np.array([1.0, 0.95, 0.01]); print("example sigma^2 (1, .95, .01): R2 =", sv2[:2].sum() / sv2.sum(), " stable rank =", sv2.sum() / sv2.max())
sv2 = np.array([1.0, 1.0]); print("two equal sing. values: sr = 2, R2 = 1")
# place code vs axis code: 16x16 grid
ii, jj = np.meshgrid(np.arange(16), np.arange(16), indexing="ij")
Ppl = np.eye(256)                      # place code: one unit per position
Pax = np.stack([ii.ravel() / 15.0, jj.ravel() / 15.0], 1)  # axis code: x, y coordinates
def srank(P, centre=True):
    if centre: P = P - P.mean(0)
    s = np.linalg.svd(P, compute_uv=False); return (s ** 2).sum() / s[0] ** 2, (s[:2] ** 2).sum() / (s ** 2).sum()
print("place code (identity 256x256), centred: stable rank, R2(top2):", srank(Ppl))
print("axis code (2 columns), centred:", srank(Pax))
print("stable rank of the uncentred axis code:", srank(Pax, False))
print("15 components / 81%: per-image PCA; cos 0.19, 0.24 -> angle deg", np.degrees(np.arccos(0.19)), np.degrees(np.arccos(0.24)))
print("random cosine in d=768: std", 1 / np.sqrt(768), "; 0.24 / std =", 0.24 * np.sqrt(768))
# 16x16 tokens with row+col additive: P_ij = r_i + c_j
print("decoding chance level 1/256 =", 1 / 256)

print("\n== baselines of App. E (small simulation) ==")
cs, rho = 600, 0.1
Zs = np.abs(rng.standard_normal((5000, cs))) * (rng.random((5000, cs)) < 8 / cs)
# add structure: 20 blocks of 30 concepts that co-fire
blk = rng.integers(0, 20, 5000); Zs = Zs * 0.3 + np.abs(rng.standard_normal((5000, cs))) * ((np.arange(cs) // 30)[None, :] == blk[:, None]) * (rng.random((5000, cs)) < 0.2)
Gs = Zs.T @ Zs
iu = np.triu_indices(cs, 1)
S = np.zeros_like(Gs); S[iu] = rng.permutation(Gs[iu]); S = S + S.T; S[np.diag_indices(cs)] = np.diag(Gs)
print("shuffle keeps trace:", np.trace(S), np.trace(Gs), " Frobenius:", np.linalg.norm(S), np.linalg.norm(Gs))
ev = lambda M: np.sort(np.linalg.eigvalsh(M))[::-1]
eg, es = ev(Gs), ev(S)
print("top eigenvalue share of trace: G", eg[0] / eg.sum(), " shuffled", es[0] / es.sum())
print("sum of squares of eigenvalues (= Frobenius^2) equal:", (eg**2).sum(), (es**2).sum())
print("eigenvalues 1,2,10,100 of G (normalised by first):", (eg / eg[0])[[0, 1, 9, 99]], " shuffled:", (es / es[0])[[0, 1, 9, 99]])
Rm = rng.random((cs, cs)) * (rng.random((cs, cs)) < rho); Rs = (Rm + Rm.T) / 2
Rt = Rs / np.linalg.norm(Rm + Rm.T) * np.linalg.norm(Gs)
print("random baseline: ||R~||_F / ||G||_F =", np.linalg.norm(Rt) / np.linalg.norm(Gs), "(expected 1/2: the factor 2 in the formula)")
er = ev(Rt); print("random baseline eigenvalues normalised by first: 1,2,10,100:", (er / er[0])[[0, 1, 9, 99]])
print("\n== singular values of a unit-row dictionary ==")
print("sigma1=22.5 -> sigma1^2 =", 22.5**2, " average sigma^2 = c/d =", c / d, " ratio", 22.5**2 / (c / d), " share of the trace", 22.5**2 / c)
print("sigma at index 200 ~7 -> 49 ; index 760 ~3.5 -> 12.25")
print("MP band relative: 1 -/+ sqrt(d/c) =", 1 - np.sqrt(d/c), 1 + np.sqrt(d/c))
print("2*ln(P)/d for c=32000:", 2*np.log(P)/d)
