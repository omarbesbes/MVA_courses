"""Numbers of page 5 (MRH). numpy only. Run: python3 checks/check_05.py"""
import numpy as np, itertools
np.set_printoptions(precision=4, suppress=True)
def hull(P):
    P = sorted(map(tuple, P)); 
    def cr(o,a,b): return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lo=[]; up=[]
    for p in P:
        while len(lo)>=2 and cr(lo[-2],lo[-1],p)<=1e-12: lo.pop()
        lo.append(p)
    for p in reversed(P):
        while len(up)>=2 and cr(up[-2],up[-1],p)<=1e-12: up.pop()
        up.append(p)
    return lo[:-1]+up[:-1]
def msum(A,B): return hull([(a[0]+b[0],a[1]+b[1]) for a in A for b in B])
def h(P,u): return max(p[0]*u[0]+p[1]*u[1] for p in P)

print("== 1. worked example in the plane")
T=np.array([[0,0],[4,0],[0,2]],float); S=np.array([[0,0],[1,2]],float)  # triangle, segment
z1=np.array([.5,.25,.25]); z2=np.array([.25,.75])
p1=z1@T; p2=z2@S; print("p1",p1,"p2",p2,"x",p1+p2)
print("vertices of sum:",hull([tuple(a+b) for a in T for b in S]))
print("sum of all 6 pair sums:"); [print(a,b,a+b) for a in T for b in S]
print("area T",.5*4*2,"area sum approx",None)
V=hull([tuple(a+b) for a in T for b in S]);
ar=lambda P:0.5*abs(sum(P[i][0]*P[(i+1)%len(P)][1]-P[(i+1)%len(P)][0]*P[i][1] for i in range(len(P))))
print("area sum",ar(V),"area T",ar(hull(T)))
# mixed-area check: area(T+S)=area T + area S + 2V(T,S); area S=0. 
# a point not in sum:  (5,0)? 
q=np.array([5,0.]); 
def inP(P,q): 
    P=hull(P); return all((P[(i+1)%len(P)][0]-P[i][0])*(q[1]-P[i][1])-(P[(i+1)%len(P)][1]-P[i][1])*(q[0]-P[i][0])>=-1e-9 for i in range(len(P)))
print("(5,0) in sum?",inP(V,q),"(4,2)?",inP(V,np.array([4,2.])),"(5,2)",inP(V,np.array([5,2.])))
print("support h_T(1,1)",h(T,(1,1)),"h_S(1,1)",h(S,(1,1)),"h_sum",h(V,(1,1)))

print("== 2. attention in the hull, reach")
Vv=np.array([[0,0],[4,0],[1,3.]]); x=np.array([1.,0.,-1.])
for tau in [1,.5,.1,.05]:
    a=np.exp(x/tau); a/=a.sum(); print("tau",tau,"alpha",a,"y",a@Vv)
print("m=261 rank<=64 -> 65 <261; K logits dim<=",64+1)
# logit-inverse example: alpha=(.5,.3,.2) -> logits log alpha
al=np.array([.5,.3,.2]); u=np.log(al); print("log alpha",u,"softmax(u+7)",np.exp(u+7)/np.exp(u+7).sum())
print("ex: y for alpha",al@Vv)

print("== 3. low-temperature bound")
rng=np.random.default_rng(0); worst=0
for _ in range(20000):
    m=rng.integers(2,8); X=rng.normal(size=m)*rng.uniform(.2,3); V=rng.normal(size=(m,3))*rng.uniform(.2,3); tau=rng.uniform(.05,3)
    a=np.exp((X-X.max())/tau); a/=a.sum(); j=X.argmax(); Dl=X[j]-X
    lhs=np.linalg.norm(a@V-V[j]); diam=max(np.linalg.norm(p-q) for p in V for q in V)
    rhs=diam*sum(np.exp(-Dl[k]/tau) for k in range(m) if k!=j)
    if rhs>1e-9: worst=max(worst,lhs/rhs)
    assert lhs<=rhs+1e-12
print("bound holds on 20000 random cases, max lhs/rhs =",worst)
# exercise: V=(0,0),(4,0),(1,3), logits (1,0,-1), tau .5
X=np.array([1,0,-1.]); tau=.5; a=np.exp(X/tau); a/=a.sum(); y=a@Vv
diam=max(np.linalg.norm(p-q) for p in Vv for q in Vv)
print("tau .5 alpha",a,"y",y,"dist",np.linalg.norm(y-Vv[0]),"diam",diam,"bound",diam*(np.exp(-1/tau)+np.exp(-2/tau)))
for tau in [1,.5,.25,.1]:
    a=np.exp(X/tau); a/=a.sum(); y=a@Vv; print(tau,np.linalg.norm(y-Vv[0]),diam*(np.exp(-1/tau)+np.exp(-2/tau)))
print("tau for bound<=0.01: need diam*2e^{-1/tau}<=.01 ->",1/np.log(2*diam/.01))

print("== 4. steering")
xx=np.array([0,0.]); a=np.array([3,4.]); v=np.array([1,0.])
ts=[0,1,2,3,4,6]
print("directional: t, dist, prox"); 
for t in ts: d=np.linalg.norm(xx+t*v-a); print(t,d,np.exp(-d))
print("archetypal: t, dist, prox")
for t in [0,.25,.5,.75,1]: d=np.linalg.norm(xx+t*(a-xx)-a); print(t,d,np.exp(-d))
print("t*",-(v@(xx-a))/(v@v),"min dist",np.linalg.norm((xx-a)-((xx-a)@v)/(v@v)*v), "e^-4",np.exp(-4))

print("== 5. identifiability")
Tr=[(0,0),(1,0),(0,1)]; 
hX=lambda u:max(0,u[0],u[1]); s=lambda u:max(0,.2*(u[0]+u[1])); g=lambda u:hX(u)-s(u)
u=(1,1); v=(-1,0); w=(0,1)
print("g(u)",g(u),"g(v)",g(v),"g(u+v)",g(w),"subadd fails:",g(w)>g(u)+g(v)+1e-12)
rng=np.random.default_rng(1); bad=0; ok_s=True
for _ in range(100000):
    p=rng.normal(size=2); q=rng.normal(size=2)
    if g(p+q)>g(p)+g(q)+1e-12: bad+=1
    if not (0<=s(p)<=hX(p)+1e-12): ok_s=False
print("0<=s<=hX everywhere:",ok_s,"; subadditivity violations among 1e5 random pairs:",bad)
# hexagon
l=1.0; ang=[0,60,120]
segs=[np.array([[-.5*l*np.cos(np.radians(t)),-.5*l*np.sin(np.radians(t))],[.5*l*np.cos(np.radians(t)),.5*l*np.sin(np.radians(t))]]) for t in ang]
H1=hull([tuple(a+b+c) for a in segs[0] for b in segs[1] for c in segs[2]])
Tt=np.array([[0,0],[1,0],[.5,np.sqrt(3)/2]]); Tt=Tt-Tt.mean(0)
H2=hull([tuple(a-b) for a in Tt for b in Tt])
H3=hull([tuple(a+b) for a in Tt for b in -Tt])
sortp=lambda P:sorted((round(p[0],9),round(p[1],9)) for p in P)
print("hexagon (3 segs):",len(H1),"vertices; T+(-T):",len(H3)); 
# compare as vertex sets up to centring
c1=np.mean(H1,0); c3=np.mean(H3,0)
print("vertex sets equal after centring:",sortp(np.array(H1)-c1)==sortp(np.array(H3)-c3))
print("sides H1",[round(np.hypot(*(np.array(H1[(i+1)%6])-np.array(H1[i]))),6) for i in range(6)])
print("circumradius",[round(np.hypot(*(np.array(p)-c1)),6) for p in H1])
us=[(np.cos(t),np.sin(t)) for t in np.linspace(0,2*np.pi,721)]
print("max |h diff|:",max(abs(h(H1,u)-h(H3,u)) for u in us), "h hex(1,0)=",h(H1,(1,0)),"h_T(1,0)+h_-T(1,0)",h(Tt,(1,0))+h(-Tt,(1,0)))
# a point with two decompositions: x=(0.5,0) 
x0=np.array([0.5,0.0]); print("x0 in hexagon (centred)?",inP(H1,x0+0)) 
# decomposition 1 : segments t_k in [-1/2,1/2] coeffs x=sum t_k d_k ; solve underdetermined, 3 unknowns 2 equations
D=np.array([[np.cos(np.radians(t)),np.sin(np.radians(t))] for t in ang])
# x = sum_k t_k d_k, t_k in [-.5,.5]  : family t = t0 + s*n  with n null vector of D^T
Mx=D.T; 
print("D^T",Mx)
n=np.array([1,-1,1.])  # d0 - d1 + d2 = 0 (since d1=d0+d2 for 60/0/120)
print("null vec check",Mx@n)
tp=np.linalg.lstsq(Mx,x0,rcond=None)[0]; print("min-norm t",tp, "in box:",np.all(np.abs(tp)<=.5+1e-12))
# explicit: x0=(0.5,0): t=(.5,0,0)?  t=(.5,0,0) -> .5*d0=(.5,0) ok; also t=(0,-.5,... )
for t in [np.array([.5,0,0]),np.array([0,.5,-.5]),np.array([.25,.25,-.25])]:
    print(t,"->",Mx@t,"in box",np.all(np.abs(t)<=.5+1e-12))
# triangle+reflection decomposition of x0 (centred triangle Tt, vertices Tt[i]) : x0 = p - q, p in T, q in T
print("Tt vertices",Tt)
# find p,q: x0 = p - q ; pick p = vertex mix
# barycentric: p = sum lam_i Tt_i, q = sum mu_i Tt_i
for lam,mu in [((1,0,0),None)]:
    pass
# search small rational: solve lam-mu with constraint x0 = (lam-mu) @ Tt; (lam-mu) = w with sum 0
# vertices Tt: use w = lam - mu with sum zero; Tt^T w = x0 (2 eq) + sum w=0 -> unique w
A=np.vstack([Tt.T,np.ones(3)]); w=np.linalg.solve(A,np.array([x0[0],x0[1],0])); print("w=lam-mu",w)
# nonneg split: lam=max(w,0)+e, mu=max(-w,0)+e with e s.t. sums 1 : sum max(w,0)=r; e=(1-r)/3
r=np.maximum(w,0).sum(); e=(1-r)/3; lam=np.maximum(w,0)+e; mu=np.maximum(-w,0)+e
print("lam",lam,"mu",mu,"sums",lam.sum(),mu.sum(),"check",lam@Tt-mu@Tt)
# a second decomposition for the same point
e2=e*0.5
print("hex area",0.5*abs(sum(H1[i][0]*H1[(i+1)%6][1]-H1[(i+1)%6][0]*H1[i][1] for i in range(6))), "3sqrt3/2 =",3*np.sqrt(3)/2)
# rectangle
a,b=2,1; print("rectangle a,b",a,b)
# indecomposability: triangle -- parallel edges: none
print("== 6. dimension counts: m=261; K rank<=64 -> logit images dimension<=65; simplex dim m-1=260; heads H=12, d_k=64, 12*64=768")
print("Minkowski sum of two triangles in R^2 : vertices count <= 6")
