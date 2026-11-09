"""Dualite lagrangienne de la partie II : theta(lambda) = lambda B + max sur les sommets du pave de E - lambda s.eps."""
import itertools, numpy as np
def E(eps,a): return 1+np.cumprod(a+eps).sum()
g=6; a=np.full(g,0.6); u=1-a
for name,s in {"S2":np.array([2.0,1.7,1.4,1.1,0.8,0.5]),"S3":np.array([0.3,2.5,0.3,0.3,2.5,0.3])}.items():
    B=0.3*s@u
    V=[np.array(v)*u for v in itertools.product([0,1],repeat=g)]
    Ev=np.array([E(v,a) for v in V]); cv=np.array([s@v for v in V])
    lams=np.linspace(0,5,50001)
    theta=np.array([lam*B+np.max(Ev-lam*cv) for lam in lams])
    i=theta.argmin()
    print(name,"borne duale min_lambda theta =",round(theta[i],4),"en lambda =",round(lams[i],4))
