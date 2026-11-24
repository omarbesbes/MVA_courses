"""Numbers of page 6 (critical reading). numpy only. Run: python3 checks/check_06.py"""
import numpy as np, itertools, math
np.set_printoptions(precision=4, suppress=True)

print("== 1. nested proposition, signed/positive example")
d1=np.array([1.,0]); d2=np.array([.6,.8]); M=2.; z=np.array([1.5,.5])
x=z[0]*d1+z[1]*d2; lam=z/M
x2=lam[0]*(M*d1)+(1-lam[0])*0+lam[1]*(M*d2)
print("x",x,"via tiles",x2,"lambda",lam)
print("signed: z=-0.5 on d1: lambda=(z+M)/(2M)=",(-0.5+M)/(2*M))

print("== 2. box vs simplex, tile a=(0,0), b=(2,0), c=(0,2)")
a=np.array([0,0.]);b=np.array([2,0.]);c=np.array([0,2.])
for lb,lc in [(.75,.75),(.5,.25),(1,1)]:
    xx=a+lb*(b-a)+lc*(c-a); print((lb,lc),"sum",lb+lc,"x",xx,"in triangle",lb+lc<=1)
print("area triangle",.5*2*2,"area square",4,"ratio",4/2)
# fraction of box points that satisfy simplex constraint, uniform: 1/2
print("unit budget: P(z1+z2<=1) uniform box = 0.5")

print("== 3. LayerNorm example, d=3")
x=np.array([1.,2,6]); mu=x.mean(); var=((x-mu)**2).mean(); sig=math.sqrt(var)
u=(x-mu)/sig; print("mu",mu,"var",var,"sigma",sig,"u",u,"sum u",u.sum(),"|u|^2",u@u)
u2=(2*x-(2*x).mean())/math.sqrt((((2*x)-(2*x).mean())**2).mean()); print("LN(2x) u",u2)
g=np.array([1,2,.5]); be=np.array([.1,0,-.1]); y=g*u+be; print("y",y)
x3=np.array([4.,1,1]); mu3=x3.mean(); u3=(x3-mu3)/math.sqrt(((x3-mu3)**2).mean()); print("u'",u3,"|u'|^2",u3@u3)
m=(u+u3)/2; print("midpoint of u,u'",m,"|m|^2",m@m,"|m|",math.sqrt(m@m),"sqrt d",math.sqrt(3),"gap",math.sqrt(3)-math.sqrt(m@m))
cosang=u@u3/3; ang=math.degrees(math.acos(cosang)); print("cos",cosang,"angle",ang,"depth (1-cos(theta/2))sqrt d",(1-math.cos(math.radians(ang/2)))*math.sqrt(3))
print("chord |u-u'|",np.linalg.norm(u-u3),"half",np.linalg.norm(u-u3)/2,"depth/half-chord tan(theta/4)",math.tan(math.radians(ang/4)))

print("== 4. depth of a chord")
for th in (56,60,77.6,90,180): 
    print(th,"depth/sqrt d",1-math.cos(math.radians(th/2)),"depth/half-chord",math.tan(math.radians(th/4)))
print("56 deg: depth/half chord", math.tan(math.radians(56/4)))
print("check |m|^2 identity: |m|^2 = d cos^2(theta/2)")
print("polygon n: depth ratio tan(pi/2n)",[round(math.tan(math.pi/(2*n)),4) for n in (3,4,6,8)])
print("proof: ||(1-s)u+su'||^2 =",)
print("  = (1-s)^2 d + s^2 d + 2s(1-s) u.u' = d - 2s(1-s)(d-u.u')  ; at s=1/2:",3-0.5*(3-u@u3))

print("== 5. subadditivity gap, triangle side 1 centred")
V=np.array([[-.5,-math.sqrt(3)/6],[.5,-math.sqrt(3)/6],[0,math.sqrt(3)/3]])
hX=lambda w:(V@w).max()
for eps in (.1,.2,.3):
    s=lambda w:eps*abs(w[0]); f=lambda w:hX(w)-s(w)
    uu=np.array([.5,math.sqrt(3)/2]); vv=np.array([-.5,math.sqrt(3)/2])
    print("eps",eps,"f(u)",f(uu),"f(v)",f(vv),"f(u+v)",f(uu+vv),"sum",f(uu)+f(vv),"violation",f(uu+vv)-f(uu)-f(vv))
# other segment: vertical Q=[0,eps] direction e=(0,1)
for eps in (.1,):
    s=lambda w:eps*abs(w[1]); f=lambda w:hX(w)-s(w)
    best=0;arg=None
    for t1 in np.linspace(0,2*np.pi,361):
        for t2 in np.linspace(0,2*np.pi,361):
            a1=np.array([math.cos(t1),math.sin(t1)]);a2=np.array([math.cos(t2),math.sin(t2)])
            v_=f(a1+a2)-f(a1)-f(a2)
            if v_>best+1e-12: best=v_;arg=(math.degrees(t1),math.degrees(t2))
    print("vertical Q, eps",eps,"grid max violation",best,arg)
print("Q=[-eps,eps]x{0}: grid max for eps .1 (report t4: 0.1732)")
best=0
s=lambda w:.1*abs(w[0]); f=lambda w:hX(w)-s(w)
for t1 in np.linspace(0,2*np.pi,361):
    for t2 in np.linspace(0,2*np.pi,361):
        a1=np.array([math.cos(t1),math.sin(t1)]);a2=np.array([math.cos(t2),math.sin(t2)])
        best=max(best,f(a1+a2)-f(a1)-f(a2))
print(best)

print("== 6. sandwich on a tiny data set: 5 points in R^2, K=2 (errors = sums of squares)")
X=np.array([[0,0],[2,0],[4,0],[1,1.5],[3,1.5]])
mu=X.mean(0); Xc=X-mu
S=np.linalg.svd(Xc,compute_uv=False); pca1=(S[1:]**2).sum()
print("mean",mu,"PCA_1 error",pca1)
best=1e9
for lab in itertools.product([0,1],repeat=5):
    lab=np.array(lab)
    if lab.min()==lab.max(): continue
    e=sum(((X[lab==k]-X[lab==k].mean(0))**2).sum() for k in (0,1))
    if e<best: best=e;bl=lab.copy(); cent=[X[lab==k].mean(0) for k in (0,1)]
print("k-means_2 best",best,bl,cent)
# AA_2: archetypes A,B in conv(X); each point projected on segment [A,B]. Archetypes = convex combinations of data (weights w)
def aa_err(w):
    w=np.abs(w).reshape(2,5); w=w/w.sum(1,keepdims=True); A,B=w@X
    d=B-A; dd=d@d
    if dd<1e-12: return ((X-A)**2).sum()
    t=np.clip(((X-A)@d)/dd,0,1); R=A+t[:,None]*d; return ((X-R)**2).sum()
rng=np.random.RandomState(0); bestA=1e9
for r in range(60):
    w=rng.rand(10); e=aa_err(w); step=.3
    for it in range(4000):
        w2=np.abs(w+step*rng.randn(10)*(rng.rand(10)<.4)); e2=aa_err(w2)
        if e2<e: w,e=w2,e2
        if it%500==499: step*=.5
    if e<bestA: bestA=e; bw=w.copy()
ww=np.abs(bw).reshape(2,5); ww/=ww.sum(1,keepdims=True)
print("AA_2 (hill climbing, 60 restarts)",bestA,"archetypes",ww@X)
print("ordering PCA<=AA<=kmeans:",pca1<=bestA+1e-9<=best+1e-9)
print("k-means as an AA solution: archetypes = centroids, error",best)

print("== 7. Minkowski sum vs union: co-activation")
al=np.array([.7,.3]); be_=np.array([.6,.4]); w=np.kron(al,be_); print("weights alpha_i beta_j",w, w.sum())
C=np.outer(w,w); print("co-activation w w^T\n",C); print("all entries >0:",(C>0).all())
wu=np.concatenate([al,[0,0]]); Cu=np.outer(wu,wu); print("union token (tile 1 only) block:\n",Cu)
print("kron check", np.allclose(C,np.kron(np.outer(al,al),np.outer(be_,be_))))
print("share of off-diagonal mass in blocks {1,2},{3,4} for sum token (archetypes ordered a1b1,a1b2,a2b1,a2b2): blocks by a-index")
off=C-np.diag(np.diag(C)); blk=np.zeros((4,4),bool); blk[:2,:2]=True; blk[2:,2:]=True
print(off[blk].sum()/off.sum())

print("== 8. additive table")
P=np.array([[1,2,4],[3,4,6.]]); Pn=np.array([[1,2,4],[3,5,6.]])
def r2add(P):
    Pc=P-P.mean(); r=P.mean(1,keepdims=True)-P.mean(); c=P.mean(0,keepdims=True)-P.mean(); F=r+c
    return 1-((Pc-F)**2).sum()/(Pc**2).sum()
print("additive table R2",r2add(P),"non-additive",r2add(Pn))
print("residual of non-additive:",(Pn-Pn.mean())-((Pn.mean(1,keepdims=True)-Pn.mean())+(Pn.mean(0,keepdims=True)-Pn.mean())))
print("generic table 16x16: dof additive (centred) =",15+15,"of",255,"=",30/255)
print("position: 97.4 held-out 94.7 ceiling 95.2 generic 11.8 (from results/r6_position_additive.json)")
print("== 9. stable rank bound")
for R2 in (.99,1.0,.9): print("R2",R2,"stable rank <= 2/R2 =",2/R2)
print("== 10. identifiability counter-example: values",.5-.05,.5-.05,1.0, "sum",.9)
print("== 11. hexagon: support in direction 0deg is 1; three segments of length 1: sum half-lengths =",sum(abs(math.cos(math.radians(a)))*.5 for a in (0,60,120)))
print("   T + (-T) support in direction 0: h_T(0)+h_{-T}(0) =",(V@np.array([1,0])).max()+(-V@np.array([1,0])).max())

print("== 12. distance concentration, Gaussian N(0,I_d): third sample vs endpoint")
for d in (2,10,50,100):
    chord=math.sqrt(2*d); mid=math.sqrt(d/2); third=math.sqrt(d+d/2)
    print("d",d,"chord",round(chord,2),"half-chord",round(chord/2,2),"endpoint-to-mid",round(chord/2,2),"third sample to mid ~",round(third,2),"ratio to chord",round(third/chord,3))
rng=np.random.RandomState(1)
for d in (2,50):
    Xs=rng.randn(20000,d); idx=rng.randint(0,20000,(200,2)); r=[]
    for i,j in idx:
        if i==j: continue
        m=(Xs[i]+Xs[j])/2; dd=np.linalg.norm(Xs-m,axis=1); r.append(dd.min()/np.linalg.norm(Xs[i]-Xs[j]))
    print("d",d,"mean rho (N=20000, 200 pairs)",np.mean(r))
print("== 13. k-means error check of tiny example")
print(((np.array([[0,0],[2,0],[1,1.5]])-np.array([1,.5]))**2).sum(), ((np.array([[4,0],[3,1.5]])-np.array([3.5,.75]))**2).sum())

print("== 14. exercises")
d=768; R=math.sqrt(d); 
for th in (90,56): print("theta",th,"sqrt d",R,"depth",(1-math.cos(math.radians(th/2)))*R,"half chord",R*math.sin(math.radians(th/2)),"ratio",math.tan(math.radians(th/4)))
X=np.array([[0,0],[2,0],[4,0],[1,1.5],[3,1.5]])
A_=np.array([.5,.5]);B_=np.array([3.5,.5]); d_=B_-A_; t=np.clip(((X-A_)@d_)/(d_@d_),0,1); Rr=A_+t[:,None]*d_; print("AA candidate error",((X-Rr)**2).sum(), "per point",((X-Rr)**2).sum(1))
print("A=(0.5,0.5) in hull: left edge x=2y/3 ->",2*0.5/3,"; B right edge x=4-2y/3 ->",4-2*.5/3)
print("exercise 4 weights",np.kron([.5,.5],[.25,.75]))
print("exercise 5 vertical Q eps=.1: f(u),f(v),f(u+v)")
eps=.1; s=lambda w:eps*abs(w[1]); f=lambda w:hX(w)-s(w)
uu=np.array([math.cos(math.radians(30)),.5]); vv=np.array([0,-1.]); print(f(uu),f(vv),f(uu+vv),f(uu+vv)-f(uu)-f(vv))
