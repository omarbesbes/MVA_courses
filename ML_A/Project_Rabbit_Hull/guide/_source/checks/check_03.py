"""check_03.py -- every number written on page 03_concepts_tasks.html. numpy only."""
import numpy as np
np.set_printoptions(precision=4, suppress=True)
def H(w):
    w = np.asarray(w, float); p = w[w > 0] / w.sum(); return float(-(p * np.log(p)).sum())

print("== entropy of footprints (nats) ==")
for name, n in [("one token", 1), ("cls + 4 registers? no: 4 registers uniform", 4), ("5 special tokens uniform", 5),
                ("one grid column (16 patches)", 16), ("left third: 5 columns x 16 rows = 80 patches", 80),
                ("a third of 261 tokens = 87", 87), ("256 patches", 256), ("all 261 tokens", 261)]:
    print(f"{name:55s} ln n = {np.log(n):.3f}")
print("ln 261 =", np.log(261), " ln 256 =", np.log(256), " ln 4 =", np.log(4), " bits 261:", np.log2(261))
# footprint with a "dominant" pattern: 50% of mass on registers, rest uniform on patches
w = np.r_[0, [0.5/4]*4, [0.5/256]*256]; print("half the mass on registers, half uniform on patches:", H(w))
# cls twice as big as the average patch, others uniform
w = np.r_[3, [1]*4, [1]*256]; print("cls weight 3, rest 1:", H(w))
print("max entropy / entropy fraction of ln261 for 80 patches:", np.log(80)/np.log(261))
# uniform on spatial only but the 5 specials zero
print("exp(H) for 80 patches", 80, " 'effective number of tokens' = exp(H)")

print("\n== importance toy example ==")
Ez = np.array([0.5, 0.2, 0.05])
Wp = np.array([[2.0, -1.0], [0.5, 1.0], [-3.0, 4.0]])
contrib = Ez[:, None] * Wp
print("contributions E[Z_i] W'_ij:\n", contrib)
print("sum over concepts (= E[Y]):", contrib.sum(0))
print("ranking on output 1:", np.argsort(-np.abs(contrib[:, 0])), "output 2:", np.argsort(-np.abs(contrib[:, 1])))
print("max over outputs of |score|:", np.abs(contrib).max(1), " mean over outputs:", contrib.mean(1))
print("L1 over outputs:", np.abs(contrib).sum(1))
# dense but weak vs sparse but strong
print("a concept with E[Z]=0.05 firing 1 time in 10 at 0.5; mean over tokens = ", 0.1*0.5)

print("\n== LRH toy d=2 ==")
D = np.array([[1, 0], [0, 1], [1/np.sqrt(2), 1/np.sqrt(2)]])
G = D @ D.T; print("Gram:\n", G, "\ncoherence mu =", np.abs(G - np.eye(3)).max())
z = np.array([1.5, 0, 2.0]); a = z @ D; print("a = zD =", a, " |supp z| =", (z > 0).sum())
z2 = np.array([0, 1.0, 1.0]); print("zD for z=(0,1,1)", z2 @ D)
print("Welch bound c=3,d=2:", np.sqrt((3-2)/(2*(3-1))), " ; for c=32000,d=768:", np.sqrt((32000-768)/(768*(32000-1))))
print("random: 1/sqrt(768) =", 1/np.sqrt(768))
# the same a with a different code (non unique): a = 1.5 d1 + 2 d3 ; also = (1.5+2/sqrt2... ) d1 + (2/sqrt2) d2
print("a as 2-atom code on d1,d2:", a, " same vector: z=(%.4f, %.4f, 0)" % (a[0], a[1]))
print("compression: c/d =", 32000/768, "; k/d =", 8/768, "; 8 of 32000 =", 8/32000)
print("R^2 > 88% means relative residual", 1-0.88)
print("tokens per image:", 1+4+256, " 16*16 =", 16*16, " 224/14 =", 224/14)
print("nt per 1.4M images =", 1.4e6*261)
print("size of W' for ImageNet o=1000: c x o =", 32000*1000, " for d x o:", 768*1000)

print("\n== Gram spectrum references (Fig. 3 right) ==")
rng = np.random.default_rng(0)
for trial in range(3):
    V = rng.standard_normal((100, 768)); V /= np.linalg.norm(V, axis=1, keepdims=True)
    ev = np.linalg.eigvalsh(V @ V.T)[::-1] / 100
    print("random unit vectors: top %.4f  50th %.4f  min %.4f  sum %.3f" % (ev[0], ev[49], ev[-1], ev.sum()))
r = 100/768
print("Marchenko-Pastur ends (x 0.01): (1-sqrt r)^2 = %.3f, (1+sqrt r)^2 = %.3f" % ((1-np.sqrt(r))**2, (1+np.sqrt(r))**2))
print("flat spectrum: 1/100 = 0.01; one direction: 1.0")
print("cosines: random pair std", 1/np.sqrt(768), "; density peak of N(0,s) =", 1/(np.sqrt(2*np.pi)/ (np.sqrt(768))), "(paper's all-pairs peak ~9)")
print("spectrum sum of first 50 for tasks if 0.11..0.0035 -> not recomputed")
# partial sums: low-dim subspace meaning: fraction of variance in top 5 for a spectrum 0.14 decaying geometrically to 0.0035 over 50 indices

print("\n== exercises ==")
print("Ex3: E[Z]=(0.4,0.1,0.5), W' same ->"); Ez3=np.array([0.4,0.1,0.5]); C3=Ez3[:,None]*Wp; print(C3, C3.sum(0))
w = np.r_[np.zeros(5), [0.8/80]*80, [0.2/176]*176]; print("Ex6: 80 patches carry 80% of the mass, 176 carry 20%: H =", H(w), " exp(H) =", np.exp(H(w)))
w = np.r_[[0.2]*5, np.zeros(256)]; print("Ex5: five special tokens equal:", H(w))
w = np.r_[[0.5], np.zeros(4), [0.5/256]*256]; print("Ex5b: half on cls, half uniform on patches:", H(w))
lam = np.r_[0.15, [0.85/99]*99]; print("Ex7: top eigenvalue 0.15, others equal:", lam[1], " exp(entropy) =", np.exp(-(lam*np.log(lam)).sum()), " top-5 share if 0.15 + 4 x 0.1?", )
print("Ex7: flat exp(H)=100; ratio top/flat =", 0.15/0.01)
# Ex8: mean pooling over 16 patches, concept weight 2 on the logit, code 1 on m patches
for m in (12, 4, 0):
    print("Ex8: concept fires with code 1 on", m, "of 16 patches, weight 2 -> mean-pooled contribution", 2*m/16)
print("Ex1: nonzeros per token", 8, "per image", 8*261, " W' entries", 32000*1000)
print("Ex-grad: Y_j = sum_i z_i W'_ij ; dY/dz_i =", "W'_ij")
