"""check_02.py -- every number written on page 02_toolbox.html. numpy only (plus the read-only code/rh/aa.py)."""
import sys, heapq, math, itertools
import numpy as np
sys.path.insert(0, "/home/user/MVA_courses/ML_A/Project_Rabbit_Hull/code")
np.set_printoptions(precision=4, suppress=True)
rng = np.random.default_rng(0)

print("== frames: Welch, random, tight ==")
c, d = 32000, 768
welch = lambda c, d: math.sqrt((c - d) / (d * (c - 1)))
print("Welch c=32000 d=768:", welch(c, d), " paper numerical frame 0.065897, ratio", 0.065897 / welch(c, d))
print("Mercedes frame c=3,d=2: Welch", welch(3, 2), " tetrahedron c=4,d=3:", welch(4, 3), " c=6,d=3 icosahedron axes:", welch(6, 3), "=1/sqrt5", 1/math.sqrt(5))
print("1/sqrt(d) =", 1 / math.sqrt(d))
pairs = c * (c - 1) / 2
print("pairs", pairs, " sqrt(2 ln pairs / d) =", math.sqrt(2 * math.log(pairs) / d), " with 2*pairs (|.|):", math.sqrt(2 * math.log(2 * pairs) / d))
# simulation: c=3000, d=768 random unit vectors
cs = 3000
D = rng.standard_normal((cs, d)); D /= np.linalg.norm(D, axis=1, keepdims=True)
G = D @ D.T; off = G[~np.eye(cs, dtype=bool)]
print("sim c=3000: std of inner product", off.std(), "coherence", np.abs(off).max(), " predicted", math.sqrt(2 * math.log(cs * (cs - 1)) / d), " Welch", welch(cs, d))
# small: random c=64,d=16
for (cc, dd) in [(64, 16), (200, 16)]:
    X = rng.standard_normal((cc, dd)); X /= np.linalg.norm(X, axis=1, keepdims=True)
    g = np.abs(X @ X.T - np.eye(cc)).max()
    print(f"random c={cc} d={dd}: coherence {g:.3f}  Welch {welch(cc, dd):.3f}")
# worked example: Mercedes frame
V = np.array([[math.cos(a), math.sin(a)] for a in (math.pi/2, math.pi/2 + 2*math.pi/3, math.pi/2 + 4*math.pi/3)])
print("Mercedes Gram:\n", V @ V.T, "\n S = V^T V =\n", V.T @ V, " sing values", np.linalg.svd(V, compute_uv=False), " sqrt(3/2)=", math.sqrt(1.5))
# sparse readout with interference: z with k atoms, read z_hat = a D^T
for (name, M) in [("Mercedes", V)]:
    z = np.array([1.0, 0.0, 0.0]); a = z @ M; print("read-out of one atom with Mercedes frame:", a @ M.T)
# readout error bound for k-sparse: |<a,D_j> - z_j| <= mu * sum_{i!=j}|z_i|
cs, k = 3000, 8
z = np.zeros(cs); idx = rng.choice(cs, k, replace=False); z[idx] = rng.uniform(0.5, 1.5, k)
Gm = D @ D.T
zh = z @ D @ D.T
err = np.abs(zh - z)
print("k=8 sparse code, c=3000: max read-out error", err.max(), " mu*sum|z| bound", np.abs(Gm - np.eye(cs)).max() * z.sum(), " sum z", z.sum())
# JL cap bound
for eps in [0.0659, 0.0356, 0.1, 0.2, 0.2335, 0.3]:
    print(f"eps {eps}: exp(d eps^2/4) = {math.exp(768 * eps**2 / 4):.3g}")
print("eps needed for c=32000 via exp(d eps^2/4) >= c:", math.sqrt(4 * math.log(32000) / 768))
# Tight frame spectrum
print("sqrt(c/d) =", math.sqrt(c / d), "  MP band:", math.sqrt(c/d) * (1 - math.sqrt(d/c)), math.sqrt(c/d) * (1 + math.sqrt(d/c)), " sqrt(d/c)=", math.sqrt(d / c))
Dm = rng.standard_normal((cs, d)); Dm /= np.linalg.norm(Dm, axis=1, keepdims=True)
sv = np.linalg.svd(Dm, compute_uv=False)
print("random c=3000,d=768 sing values: min,max,sum sq", sv.min(), sv.max(), (sv**2).sum(), " MP band for c=3000:", math.sqrt(cs/d)*(1-math.sqrt(d/cs)), math.sqrt(cs/d)*(1+math.sqrt(d/cs)))
Dm = rng.standard_normal((c, d)); Dm /= np.linalg.norm(Dm, axis=1, keepdims=True)
sv = np.linalg.svd(Dm, compute_uv=False)
print("random c=32000,d=768 sing values: min,max,sum sq", sv.min(), sv.max(), (sv**2).sum())
print("energy fraction of top singular value for sigma1=22.5 (paper Fig 10B), sum sq = c:", 22.5**2 / c)

print("== stable rank ==")
def srank(M): s = np.linalg.svd(M, compute_uv=False); return (s**2).sum() / s[0]**2
print("identity 5:", srank(np.eye(5)), " diag(3,1):", srank(np.diag([3., 1.])), " (9+1)/9 =", 10/9, " diag(1,1):", srank(np.diag([1., 1.])))
print("sv (4,3,2,1): ", (16+9+4+1)/16, " rank-1:", srank(np.outer([1,2,3],[1,0,1])))
print("flat 768:", srank(np.eye(768)), "; random 3000x768 unit rows:", srank(Dm[:3000]) , "; c/d bound? c/sigma1^2 :", 3000 / (np.linalg.svd(Dm[:3000], compute_uv=False)[0]**2))
print("stable rank of Fig10B-like spectrum: sigma1=22.5, sum sq=32000 ->", 32000 / 22.5**2)
print("rank 5 matrix: sr <= rank holds: ", srank(rng.standard_normal((50, 5))), " noise 50x50:", srank(rng.standard_normal((50, 50))))
# two non-zero singular values, equal-ish
print("two sing values (1, 0.8): sr =", (1 + 0.64), " top-1 explains", 1/1.64)

print("== Hoyer ==")
def hoyer(x): n = len(x); return (math.sqrt(n) - np.abs(x).sum() / np.linalg.norm(x)) / (math.sqrt(n) - 1)
print("one-hot", hoyer(np.eye(768)[3]), " constant", hoyer(np.ones(768)), " (1,1,0,0) n=4:", hoyer(np.array([1, 1, 0, 0])), "sym check abs:", hoyer(np.array([1, -1, 0, 0])))
n = 768
print("formula sqrt(n)(1-sqrt(2/pi))/(sqrt(n)-1) =", math.sqrt(n) * (1 - math.sqrt(2 / math.pi)) / (math.sqrt(n) - 1), "  limit 1-sqrt(2/pi) =", 1 - math.sqrt(2/math.pi))
H = [hoyer(rng.standard_normal(n)) for _ in range(2000)]
print("simulation 2000 Gaussian vectors n=768: mean", np.mean(H), "std", np.std(H))
print("exact expectation E|g| =", math.sqrt(2/math.pi))
# non-negative uniform vector, a k-sparse vector
print("hoyer(k=8 equal values, n=768):", hoyer(np.r_[np.ones(8), np.zeros(760)]), " k=1:", 1.0)
print("hoyer of |gaussian| nonneg (half-normal):", np.mean([hoyer(np.abs(rng.standard_normal(n))) for _ in range(500)]))
print("hoyer of vector (1, 0.5, 0.25, ...)/ geometric 768:", hoyer(0.5 ** np.arange(768)))
x = np.array([3., 4., 0., 0.]); print("n=4 x=(3,4,0,0): l1/l2 =", 7/5, " hoyer =", hoyer(x), " (2-1.4)/(2-1)=", (2-1.4)/1)

print("== entropy ==")
def Hn(p): p = np.asarray(p, float); p = p[p > 0] / p.sum(); return float(-(p * np.log(p)).sum())
print("ln261", math.log(261), " ln2", math.log(2), " ln256", math.log(256), " one-hot", Hn([1, 0, 0]), " uniform 4:", Hn([1]*4), math.log(4))
print("(1/2,1/4,1/4):", Hn([.5, .25, .25]), " (0.9,0.1):", Hn([.9, .1]), " exp(H) for (1/2,1/4,1/4):", math.exp(Hn([.5, .25, .25])))
print("bits of 261:", math.log2(261), " uniform on 87 tokens (a third):", math.log(87), " on 16 tokens:", math.log(16), " exp(5.0)=", math.exp(5.0), " exp(5.5)=", math.exp(5.5))
print("half mass on 4 registers, half uniform 256 patches:", Hn(np.r_[[.5/4]*4, [.5/256]*256]))

print("== cosine ==")
a = np.array([1., 2., 2.]); b = np.array([2., 1., -2.]); print("cos((1,2,2),(2,1,-2)) =", a@b/np.linalg.norm(a)/np.linalg.norm(b), "norms", np.linalg.norm(a), np.linalg.norm(b))
print("cos(a,-a) =", -1, " |cos| of pair a, -a: 1; cos(a, 3a)=1")
# cos of random pair in 768
print("std of cos in d=768:", 1/math.sqrt(768), " P(|cos|>0.2):", math.erfc(0.2*math.sqrt(768)/math.sqrt(2)))

print("== PCA ==")
# per-image PCA example 2D
X = np.array([[2., 1.], [-2, -1], [1, 2], [-1, -2], [0, 0.]]) 
Xc = X - X.mean(0); C = Xc.T @ Xc / len(X); w, U = np.linalg.eigh(C); print("toy PCA eig:", w[::-1], "explained", (w[::-1] / w.sum()), "vectors", U[:, ::-1])
# 256 tokens in 768 dims: rank <= 255 after centring; random Gaussian tokens variance explained by 3 comps
T = rng.standard_normal((256, 768)); Tc = T - T.mean(0); s = np.linalg.svd(Tc, compute_uv=False)
print("random 256 tokens, 768 dims: rank of centred", np.linalg.matrix_rank(Tc), " top-3 explained", (s[:3]**2).sum() / (s**2).sum(), " top 15:", (s[:15]**2).sum()/(s**2).sum(), " 3/255 =", 3/255, " 15/255 =", 15/255)
# structured tokens: low-rank + noise
L = rng.standard_normal((256, 5)) * np.array([5, 4, 3, 2, 1]) @ rng.standard_normal((5, 768)) / math.sqrt(768) + 0.05 * rng.standard_normal((256, 768))
s = np.linalg.svd(L - L.mean(0), compute_uv=False); print("low-rank structured tokens: top3, top15 explained", (s[:3]**2).sum() / (s**2).sum(), (s[:15]**2).sum()/(s**2).sum())
print("pca RGB: 3 components -> 3 channels")

print("== convex / barycentric ==")
print("square (0,0),(1,0),(1,1),(0,1): centre = 1/2(v1+v3) = 1/2(v2+v4); also (1/4 each). 1-param family: t(v1+v3)/... ")
Vsq = np.array([[0, 0], [1, 0], [1, 1], [0, 1.]])
for w in ([.5, 0, .5, 0], [0, .5, 0, .5], [.25]*4, [.3, .2, .3, .2]): print(w, np.array(w) @ Vsq)
Tri = np.array([[0, 0], [1, 0], [0, 1.]]); p = np.array([.25, .5])
lam = np.linalg.solve(np.vstack([Tri.T, np.ones(3)]), np.r_[p, 1]); print("barycentric of (0.25,0.5) in triangle (0,0),(1,0),(0,1):", lam)
print("Caratheodory: d+1 =", 3, "in the plane; in d=768:", 769)

print("== high-dim hulls ==")
def hull2d(P):
    P = sorted(map(tuple, P)); 
    def cross(o, a, b): return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lo = []; 
    for p in P:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    up = []
    for p in reversed(P):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0: up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]
def inside2d(H, q):
    for i in range(len(H)):
        a, b = H[i], H[(i+1) % len(H)]
        if (b[0]-a[0])*(q[1]-a[1])-(b[1]-a[1])*(q[0]-a[0]) < 0: return False
    return True
N = 50
vs = []; ins = []
for _ in range(300):
    P = rng.standard_normal((N, 2)); vs.append(len(hull2d(P)) / N)
    H = hull2d(P); ins.append(inside2d(H, rng.standard_normal(2)))
print(f"d=2, N=50 Gaussian: mean fraction of points that are vertices {np.mean(vs):.3f}; new sample inside hull {np.mean(ins):.3f}")
def separated(P, q):
    """certificate that q is outside conv(P): direction u = q - mean(P)."""
    u = q - P.mean(0); return u @ q > (P @ u).max() + 1e-12
print("d, N=200: fraction of points that are certified vertices (u = x_i - mean) | fraction of new samples certified outside conv of 200 (lower bounds)")
for dd in [2, 5, 10, 20, 50, 100, 768]:
    P = rng.standard_normal((200, dd)); nv = np.mean([separated(np.delete(P, i, 0), P[i]) for i in range(200)])
    new = np.mean([separated(P, rng.standard_normal(dd)) for _ in range(200)])
    print(f"d={dd:4d}: vertices >= {nv:.2f}; new outside >= {new:.2f}")
print("2^(d/2) for d=20,40,100,768:", 2**10, 2**20, 2**50, "2^384 ~ 10^", 384 * math.log10(2))

print("== minkowski ==")
def hullpts(P): return np.array(hull2d(P))
def msum(A, B): return hullpts([a + b for a in A for b in B])
def area(P): x, y = P[:, 0], P[:, 1]; return 0.5 * abs((x * np.roll(y, -1) - np.roll(x, -1) * y).sum())
T = np.array([[0, 0], [1, 0], [.5, math.sqrt(3)/2]])
S = msum(T, -T); print("T + (-T): vertices", len(S), " area", area(S), " 6*area(T)=", 6 * area(T), " hexagon side 1: ", 3 * math.sqrt(3) / 2)
seg = lambda ang: np.array([[0, 0], [math.cos(ang), math.sin(ang)]])
Z = msum(msum(seg(0), seg(math.pi/3)), seg(2*math.pi/3)); print("three unit segments at 0,60,120 deg: vertices", len(Z), "area", area(Z))
# same set? compare support functions
us = [np.array([math.cos(t), math.sin(t)]) for t in np.linspace(0, 2*math.pi, 361)]
h = lambda P, u: (P @ u).max()
print("max |h_Z - (h_S + shift)| (translate): ", max(abs(h(Z, u) - (h(S, u) + (Z.mean(0) - S.mean(0)) @ u)) for u in us), " centroid-shifted")
Zs = Z - Z.mean(0); Ss = S - S.mean(0)
print("centred hexagons: max support difference", max(abs(h(Zs, u) - h(Ss, u)) for u in us))
# vertices bounds
A = hullpts(rng.standard_normal((8, 2))); B = hullpts(rng.standard_normal((9, 2))); print("polygons with", len(A), "and", len(B), "vertices: sum has", len(msum(A, B)), " <= ", len(A) + len(B))
sq = np.array([[0, 0], [1, 0], [1, 1], [0, 1.]]); print("square + square rotated 45deg (diag square side sqrt2/2*... ):")
R = np.array([[math.cos(math.pi/4), -math.sin(math.pi/4)], [math.sin(math.pi/4), math.cos(math.pi/4)]]); print(" vertices of sum", len(msum(sq, sq @ R.T)), " <= 8")
print("square + same square:", len(msum(sq, sq)), "vertices (parallel edges merge); = 2*square:", area(msum(sq, sq)), " area 4")
print("segment + segment (orthogonal) = square:", len(msum(seg(0), seg(math.pi/2))), area(msum(seg(0), seg(math.pi/2))))
print("3D: unit cube = sum of 3 segments; 8 vertices = 2^3; zonotope of m generic segments in plane has 2m vertices: m=3 ->", 2*3, " in R^d generic m generators: 2*sum_{i<d} C(m-1,i); m=4,d=3:", 2*(1+3+3))
# unit square + unit square rotated by 45: octagon area
Oct = msum(sq, sq @ R.T); print(" octagon area", area(Oct), " A+A'+2V = 1+1+ mixed")
# conv(A)+conv(B) = conv(A+B)
Apts = rng.standard_normal((6, 2)); Bpts = rng.standard_normal((5, 2))
HA, HB = hullpts(Apts), hullpts(Bpts)
l = hullpts([a + b for a in Apts for b in Bpts]); r = msum(HA, HB); print("conv(A+B) vs conv(A)+conv(B): same area", area(l), area(r))
# support additivity
print("support additivity max error:", max(abs(h(msum(HA, HB), u) - h(HA, u) - h(HB, u)) for u in us))
# worked support example: unit square [0,1]^2, u=(1,1): h=2; u=(1,-1): h=1; segment
print("support of square [0,1]^2: u=(1,1)", h(sq, np.array([1, 1.])), " u=(1,-1)", h(sq, np.array([1, -1.])), " u=(-1,0)", h(sq, np.array([-1., 0])))
print("support of Delta(0,0),(1,0),(0,1) in u=(2,1):", h(Tri, np.array([2, 1.])))
# P = lambda P + (1-lambda) P  (square, lambda=.3)
print("0.3*sq + 0.7*sq equals sq:", area(msum(.3 * sq, .7 * sq)), " vs 1")
# edge directions of sum sorted by angle: triangle (0,0),(2,0),(0,1) + square
Tt = np.array([[0, 0], [2, 0], [0, 1.]]); Q = np.array([[0, 0], [1, 0], [1, 1], [0, 1.]]); Sm = msum(Tt, Q); print("triangle(0,0),(2,0),(0,1) + unit square: vertices"); print(Sm, " edges:", [tuple(np.round(Sm[(i+1) % len(Sm)] - Sm[i], 3)) for i in range(len(Sm))])
print("area:", area(Sm), " area T=", area(Tt), " area Q=", area(Q))
# P = A + B with 'not homothetic' summands? triangle cannot: check triangle plus point only. Edge relation e1+e2+e3=0
e = [Tt[1]-Tt[0], Tt[2]-Tt[1], Tt[0]-Tt[2]]; print("triangle edge vectors", e, "sum", sum(e))
# Minkowski sum is not union: A=(0,0)-(1,0) seg, B=(0,0)-(0,1) seg -> square.   Adding a point: translation
print("hexagon support: h_hex(u) = h_S1+h_S2+h_S3: u=(1,0):", h(Z, np.array([1., 0])))
print("high-dim sums: |V1||V2| bound e.g. 2^m cube from m segments: m=768 ->  2^768 ~ 10^", 768 * math.log10(2))

print("== softmax ==")
sm = lambda x, t=1.0: (lambda e: e / e.sum())(np.exp((np.asarray(x, float) - np.max(x)) / t))
x = np.array([2., 1., 0.]); print("softmax(2,1,0) =", sm(x), " shifted +10:", sm(x + 10), " log p:", np.log(sm(x)), " log p + 2 +lse:", np.log(sm(x)) + math.log(np.exp(x).sum()))
print("tau 0.1:", sm(x, 0.1), " tau .5:", sm(x, .5), " tau 2:", sm(x, 2), " tau 10:", sm(x, 10), " tau 100:", sm(x, 100))
print("gap 2 at tau=0.1: leftover mass exp(-gap/tau) =", math.exp(-2/0.1), " at tau=0.5:", math.exp(-4), " p_min at x=-100 tau=1:", sm([0, -100, -100])[1])
print("softmax(0,0)=", sm([0, 0]), " softmax(log p) for p=(.5,.3,.2):", sm(np.log([.5, .3, .2])))
print("sigmoid: softmax of (x,0)[0] at x=1:", sm([1, 0])[0], 1/(1+math.e**-1))
print("tau->0 with ties: (1,1,0):", sm([1, 1, 0], 0.01))
print("Jacobian check: d softmax rows sum to 0")

print("== AA sandwich ==")
from rh.aa import archetypal_analysis, pca_fvu, kmeans
def mk(N, dim, rank, noise):
    Lx = rng.standard_normal((N, rank)) @ (rng.standard_normal((rank, dim)) * np.linspace(2, 0.5, rank)[:, None]); return Lx + noise * rng.standard_normal((N, dim))
for name, Xd in [("isotropic Gaussian N=256,d=50", rng.standard_normal((256, 50))), ("anisotropic (rank 8 + noise) N=256,d=50", mk(256, 50, 8, 0.3))]:
    print(name)
    for K in [2, 3, 5, 10, 20]:
        res = archetypal_analysis(Xd, K, n_restarts=3, seed=0, n_iter=300)
        pc = float(pca_fvu(Xd, K - 1))
        print(f"  K={K:2d}: PCA(K-1) {pc:.3f} <= AA {res['fvu']:.3f} <= kmeans {res['kmeans_fvu']:.3f}")

print("== kNN geodesics ==")
def knn_path(P, i, j, k=10):
    n = len(P); D2 = ((P[:, None, :] - P[None, :, :])**2).sum(-1); Dm_ = np.sqrt(D2)
    nb = np.argsort(Dm_, 1)[:, 1:k+1]; adj = [set() for _ in range(n)]
    for a in range(n):
        for b in nb[a]: adj[a].add(b); adj[b].add(a)
    dist = np.full(n, np.inf); prev = -np.ones(n, int); dist[i] = 0; pq = [(0, i)]
    while pq:
        dd_, u = heapq.heappop(pq)
        if dd_ > dist[u]: continue
        for v in adj[u]:
            nd = dd_ + Dm_[u, v]
            if nd < dist[v]: dist[v] = nd; prev[v] = u; heapq.heappush(pq, (nd, v))
    path = [j]
    while path[-1] != i: path.append(prev[path[-1]])
    return path[::-1], Dm_
for dd in [2, 10, 50, 200]:
    P = rng.standard_normal((1000, dd)); i, j = 0, 1
    ts = np.linspace(0, 1, 41); line = np.array([(1 - t) * P[i] + t * P[j] for t in ts])
    near = lambda Q: np.sqrt(((Q[:, None, :] - np.delete(P, [], 0)[None, :, :])**2).sum(-1)).min(1)
    path, Dm_ = knn_path(P, i, j)
    dl = near(line).max()
    pts = []
    for a, b in zip(path[:-1], path[1:]):
        for t in np.linspace(0, 1, 11): pts.append((1 - t) * P[a] + t * P[b])
    dg = near(np.array(pts)).max(); maxedge = max(Dm_[a, b] for a, b in zip(path[:-1], path[1:]))
    print(f"d={dd:3d}: |P_i-P_j|={np.linalg.norm(P[i]-P[j]):.2f}; straight line max dist to nearest sample (incl. endpoints) {dl:.2f}; kNN path ({len(path)-1} edges, longest {maxedge:.2f}, half {maxedge/2:.2f}) max dist {dg:.2f}")
    mid = (P[i] + P[j]) / 2; dm = np.sqrt(((P - mid)**2).sum(1)); print("      midpoint: nearest sample distance", dm.min(), " argmin is endpoint:", int(dm.argmin()) in (i, j), " dist to endpoint", np.linalg.norm(P[i]-mid))

print("== attribution ==")
w = np.array([2., -1., 0.5]); x = np.array([1., 3., 4.]); b = 0.7
f = lambda x: w @ x + b
print("f(x)=", f(x), " grad x input:", w * x, " sum:", (w*x).sum(), " f(x)-f(0) =", f(x) - f(np.zeros(3)))
print("occlusion (zero out i):", [f(x) - f(np.where(np.arange(3) == i, 0, x)) for i in range(3)])
al = (np.arange(1000) + .5) / 1000; ig = [(x[i] * np.mean([w[i] for _ in al])) for i in range(3)]; print("IG riemann (1000 steps):", ig)
g = lambda x: float(np.sum(x**2)); xx = np.array([1., 2.]); print("non-linear f=|x|^2 at (1,2): grad x input", 2*xx*xx, "IG", [xx[i] * np.mean([2 * a * xx[i] for a in al]) for i in range(2)], " f(x)-f(0)", g(xx))
print("occlusion nonlinear:", [g(xx) - g(np.where(np.arange(2) == i, 0, xx)) for i in range(2)])
# RISE
print("RISE toy: object = 4 pixels, mask keeps each pixel w.p. 1/2; f = 1[>= 3 of the 4 object pixels kept]")
pk = 0.5
pout = sum(math.comb(4, k) * pk**4 for k in (3, 4)); pin = sum(math.comb(3, k) * pk**3 for k in (2, 3))
print("  outside pixel: E[f | m_i=1] =", pout, " inside pixel: E[f | m_i=1] =", pin, " unconditional E f =", pout)
Nm = 8000; M = rng.random((Nm, 16)) < 0.5; fv = (M[:, 4:8].sum(1) >= 3).astype(float)
est = (fv[:, None] * M).sum(0) / M.sum(0); print("  Monte-Carlo with 8000 masks:", np.round(est, 3))
print("  pixel indices 4..7 object; mean est inside", est[4:8].mean(), "outside", np.r_[est[:4], est[8:]].mean(), " std error ~", math.sqrt(.25 / (Nm / 2)))
print("  RISE normalisation: (1/(p N)) sum f(x*M_k) M_k(i) =", ((fv[:, None] * M).sum(0) / (0.5 * Nm))[:8])

print("== exercises ==")
print("Ex1 Welch c=d+1:", welch(769, 768), " 1/d =", 1/768, " c=d+1=4,d=3:", welch(4, 3))
print("Ex2 hoyer (1,1,1,0):", hoyer(np.array([1, 1, 1, 0.])), " formula k=3,n=4:", (2 - math.sqrt(3)) / (2 - 1), " n=768,k=8:", (math.sqrt(768) - math.sqrt(8)) / (math.sqrt(768) - 1), " k for H=1/2 (n=768):", (0.5 * (math.sqrt(768) - 1) - math.sqrt(768)) ** 2)
print("Ex3 entropy half on cls, half uniform on 256:", Hn(np.r_[.5, [0]*4, [.5/256]*256]), " 5 ln2 =", 5 * math.log(2), " max", math.log(261))
print("Ex4 srank diag(3,2,1):", srank(np.diag([3., 2, 1])), 14 / 9)
Ta = np.array([[0, 0], [1, 0], [0, 1.]]); Sg = np.array([[0, 0], [1, 1.]]); Sx = msum(Ta, Sg); print("Ex6 triangle + segment (0,0)-(1,1): vertices", Sx.tolist(), "area", area(Sx))
print("Ex7 h_P(1,1) for P=conv{(0,0),(2,0),(0,1)}:", h(np.array([[0, 0], [2, 0], [0, 1.]]), np.array([1, 1.])), " h_unit square (1,1):", h(sq, np.array([1, 1.])), " h of sum (1,1):", h(Sm, np.array([1, 1.])), " (-1,-1):", h(Sm, np.array([-1, -1.])))
print("Ex8 tau for 260 wrong tokens with gap 1 and mass <= 0.01:", 1 / math.log(260 / 0.01), " ln26000 =", math.log(26000), " check mass at tau=0.098 :", 260 * math.exp(-1 / 0.098))
print("Ex8b actual: logits one 1 others 0, n=261, tau=0.098:", 1 - sm(np.r_[1., np.zeros(260)], 0.098)[0])
f2 = lambda x: x[0] * x[1]; xx = np.array([2., 3.])
print("Ex9 f=x1x2 at (2,3): gradxinput", [xx[0]*xx[1], xx[1]*xx[0]], " occlusion", [f2(xx) - f2(np.array([0, 3.])), f2(xx) - f2(np.array([2., 0]))], " IG", [xx[0] * xx[1] / 2, xx[1] * xx[0] / 2], " f(x)-f(0)", f2(xx))
print("Ex10 eps for c=1e6, d=768:", math.sqrt(4 * math.log(1e6) / 768), " c=32000:", math.sqrt(4 * math.log(32000) / 768), " d=3072,c=32000:", math.sqrt(4 * math.log(32000) / 3072))
print("Ex5 triangle (0,0),(4,0),(0,2), p=(1,1):", np.linalg.solve(np.vstack([np.array([[0, 0], [4, 0], [0, 2.]]).T, np.ones(3)]), np.r_[1, 1, 1]))
