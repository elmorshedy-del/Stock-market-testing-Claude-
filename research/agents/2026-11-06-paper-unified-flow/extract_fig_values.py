# Reads the plotted values from a matplotlib figure exported as SVG (arXiv HTML figures).
# Usage: python -I extract_fig_values.py FIG.svg x_first_tick x_last_tick n_xticks y_first_tick y_last_tick n_yticks
# Gridlines (#b0b0b0) give the axis mapping; the longest #0000ff 1.5px path is the data line; the .25-opacity polygon is the 5-95% band.
import re, sys, json, numpy as np
from math import erf, sqrt
def parse(d):
    toks = re.findall(r'[MLHVCZmlhvcz]|-?[\d.]+(?:e[-+]?\d+)?', d)
    pts=[]; cmd=None; x=y=0; i=0
    while i < len(toks):
        t = toks[i]
        if re.match(r'[A-Za-z]', t): cmd=t; i+=1; continue
        if cmd in ("M","L"): x=float(toks[i]); y=float(toks[i+1]); pts.append((x,y)); i+=2
        elif cmd=="H": x=float(t); pts.append((x,y)); i+=1
        elif cmd=="V": y=float(t); pts.append((x,y)); i+=1
        elif cmd=="C": x=float(toks[i+4]); y=float(toks[i+5]); pts.append((x,y)); i+=6
        else: i+=1
    return pts
f, xt0, xt1, nx, yt0, yt1, ny = sys.argv[1], *map(float, sys.argv[2:8])
svg = open(f, encoding="utf-8").read()
paths = re.findall(r'<path([^>]*)/>', svg)
H=[];V=[];line=None;band=None
for a in paths:
    d = re.search(r' d="([^"]*)"', a); 
    if not d: continue
    st = dict(re.findall(r'(fill|stroke|stroke-width|fill-opacity)="([^"]*)"', a))
    tr = re.search(r'transform="([^"]*)"', a); tr = tr.group(1) if tr else ""
    if not tr.startswith("matrix(1,0,0,-1,0,"): continue
    p = parse(d.group(1))
    if st.get("stroke")=="#b0b0b0" and len(p)==2:
        (x0,y0),(x1,y1)=p
        if abs(y0-y1)<1e-6: H.append(y0)
        elif abs(x0-x1)<1e-6: V.append(x0)
    if st.get("stroke")=="#0000ff" and st.get("stroke-width")=="1.5" and (line is None or len(p)>len(line)): line=p
    if st.get("fill-opacity")==".25" and len(p)>10: band=p
H=sorted(set(H)); V=sorted(set(V))
assert len(V)==int(nx) and len(H)==int(ny), (len(V),len(H))
xv=np.linspace(xt0,xt1,int(nx)); yv=np.linspace(yt0,yt1,int(ny))
ax=np.polyfit(V,xv,1); ay=np.polyfit(H,yv,1)
X=lambda q: np.polyval(ax,q); Y=lambda q: np.polyval(ay,q)
lx=X(np.array([p[0] for p in line])); ly=Y(np.array([p[1] for p in line]))
res={"x":lx.round(1).tolist(),"mean":ly.round(4).tolist()}
if band:
    bx=X(np.array([p[0] for p in band])); by=Y(np.array([p[1] for p in band]))
    lo=[];hi=[]
    for x in lx:
        m=np.abs(bx-x)<max(1e-3,(xt1-xt0)*1e-3)
        lo.append(by[m].min()); hi.append(by[m].max())
    res["lo"]=np.round(lo,4).tolist(); res["hi"]=np.round(hi,4).tolist()
print(json.dumps(res))
