"""Level-hopping test: from the lower line of an uptrend channel, how often is each
neighbouring level touched within H bars, vs a driftless random walk with
trailing 20-day realized vol (barrier distances account for the rising lines).
Run from this folder after `python fetch.py --universe`.
"""
import sys
sys.path.insert(0, '.')
import numpy as np, pandas as pd
from scipy.stats import norm
from multiprocessing import Pool
from backtest import rolling_channels, zpos
from common import load_bars
from fetch import UNIVERSE
H=20
TARGETS={'mid (z=0)':0.0,'upper (z=+1)':1.0,'next level down (z=-2)':-2.0,'lower-1/2 (z=-1.5)':-1.5}
def run(sym):
    df=load_bars(sym); o,h,l,c=(df[k].to_numpy(float) for k in ('open','high','low','close'))
    P=rolling_channels(o,h,l,c,252); t=np.arange(len(c),dtype=float)
    zc=zpos(P,t,np.log(c)); r=np.diff(np.log(c),prepend=np.nan); rows=[]
    for i in range(300,len(c)-H,5):
        if not np.isfinite(P[i,0]) or P[i,4]<0.75 or P[i,1]<=0: continue   # uptrend channels only
        if not (-1.15<=zc[i]<=-0.85): continue
        hw=(P[i,3]-P[i,2])/2; sig=np.nanstd(r[i-19:i+1])*np.sqrt(H)
        fh=zpos(P[i],t[i+1:i+1+H],np.log(h[i+1:i+1+H])); fl=zpos(P[i],t[i+1:i+1+H],np.log(l[i+1:i+1+H]))
        row={'sym':sym,'date':df.index[i]}
        for name,z in TARGETS.items():
            hit=(fh>=z).any() if z>zc[i] else (fl<=z).any()
            # level moves with the channel slope: distance at mid-horizon
            d=max(abs((z-zc[i])*hw + P[i,1]*H/2),1e-9) if z>zc[i] else max(abs(z-zc[i])*hw - P[i,1]*H/2,0)
            row[name]=hit; row[name+'_bm']=min(1,2*norm.cdf(-d/sig))
        rows.append(row)
    return rows
with Pool(4) as p: d=pd.DataFrame([x for r in p.map(run,UNIVERSE) for x in r])
print('n samples',len(d),'tickers',d.sym.nunique())
for k in TARGETS: print(f'{k:28s} empirical {d[k].mean():.2f}   random-walk (realized vol) {d[k+"_bm"].mean():.2f}')
d['m']=pd.to_datetime(d.date).dt.to_period('M')
rng=np.random.default_rng(0); ms=d.m.unique()
for k in TARGETS:
    g=d.groupby('m')[[k,k+'_bm']].sum(); n=d.groupby('m').size()
    bs=[]
    for _ in range(1000):
        s=rng.choice(len(g),len(g)); bs.append((g[k].values[s].sum()-g[k+'_bm'].values[s].sum())/n.values[s].sum())
    print(f'{k:28s} excess {np.mean(bs):+.3f}  95% CI [{np.quantile(bs,.025):+.3f},{np.quantile(bs,.975):+.3f}]')
