"""Part C, hemisphere test (Amendment 1 @ 8d8be48). 10-session windows from the equinox dates (Mar 20, Sep 22); year-block bootstrap; Holm across C1-C4.
Usage: python partC.py <scratchpad> -> out/partC.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

S = Path(sys.argv[1]); HERE = Path(__file__).resolve().parent; CX = S / "ctx"
sys.path.insert(0, str(HERE))
from partA_lib import yahoo, tag   # noqa: E402
rng = np.random.default_rng(0); B = 10000


def windows(lr, lo, hi):
    d = pd.DataFrame({"r": lr}); d = d[(d.index.year >= lo) & (d.index.year <= hi)]; d["yr"] = d.index.year; d["w"] = ""
    for y in range(lo, hi + 1):
        for lab, md in (("mar", f"{y}-03-20"), ("sep", f"{y}-09-22")):
            ix = d.index[d.index >= pd.Timestamp(md)][:10]
            d.loc[ix, "w"] = lab
    return d


def holm(ps):
    ps = np.asarray(ps, float); o = np.argsort(ps); adj = np.empty_like(ps); run = 0
    for i, k in enumerate(o):
        run = max(run, (len(ps) - i) * ps[k]); adj[k] = min(1, run)
    return adj


def test(d, autumn, spring):
    f = lambda x: 1e4 * (x[x.w == autumn].r.mean() - x[x.w == spring].r.mean())
    yrs = d.yr.unique(); G = {y: d[d.yr == y] for y in yrs}
    bs = np.array([f(pd.concat([G[y] for y in rng.choice(yrs, len(yrs))])) for _ in range(B)])
    return {"est": f(d), "ci95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))], "p": float(min(1, 2 * min((bs <= 0).mean(), (bs >= 0).mean()) + 1 / B)),
            "autumn_bp": 1e4 * d[d.w == autumn].r.mean(), "spring_bp": 1e4 * d[d.w == spring].r.mean(), "all_days_bp": 1e4 * d.r.mean(), "years": int(len(yrs))}


SO = CX / "south"; au = yahoo(SO / "%5EAORD.json"); nz = yahoo(SO / "%5ENZ50.json"); za = yahoo(SO / "%5EJ203.JO.json")
spx = yahoo(S / "long" / "GSPC.json")
R = {}
A = windows(au, 1985, 2025)
R["C1 Australia: late-Mar minus late-Sep (bp/day)"] = test(A, "mar", "sep")
# C2: remove the prior US session's move (Australia trades after the US close)
us_prev = spx.reindex(spx.index.union(au.index)).shift(1).reindex(au.index)       # last US session before each Sydney date
us_prev = pd.Series([spx[spx.index < d].iloc[-1] if (spx.index < d).any() else np.nan for d in au.index], index=au.index)
ok = us_prev.notna(); beta = np.polyfit(us_prev[ok], au[ok], 1)
local = (au - np.polyval(beta, us_prev)).dropna()
R["C2 Australia local component (prior US session removed): late-Mar minus late-Sep (bp/day)"] = test(windows(local, 1985, 2025), "mar", "sep") | {"beta_on_prior_US": float(beta[0])}
P = pd.concat([windows(au, 1985, 2025).assign(idx="AU"), windows(nz, 2003, 2025).assign(idx="NZ"), windows(za, 2012, 2025).assign(idx="ZA")])
R["C3 southern pooled (AU, NZ, ZA): late-Mar minus late-Sep (bp/day)"] = test(P, "mar", "sep") | {"by_index": {k: 1e4 * (g[g.w == "mar"].r.mean() - g[g.w == "sep"].r.mean()) for k, g in P.groupby("idx")}}
N = pd.concat([windows(spx, 1950, 2025).assign(idx="SPX"), windows(yahoo(CX / "intl" / "%5EGDAXI.json"), 1988, 2025).assign(idx="DAX"),
               windows(yahoo(CX / "intl" / "%5EFTSE.json"), 1984, 2025).assign(idx="FTSE"), windows(yahoo(CX / "intl" / "%5EN225.json"), 1970, 2025).assign(idx="N225")])
R["C4 northern control: late-Sep minus late-Mar (bp/day)"] = test(N, "sep", "mar") | {"by_index": {k: 1e4 * (g[g.w == "sep"].r.mean() - g[g.w == "mar"].r.mean()) for k, g in N.groupby("idx")}}
for (k, v), h in zip(R.items(), holm([v["p"] for v in R.values()])):
    v["p_holm"] = float(h); v["pass"] = bool(h < 0.05)
# descriptive: Australia's late-September (after the US 3rd Friday) contrast, as in Part A
ta = tag(au); ta = ta[(ta.yr >= 1985) & (ta.yr <= 2025)]
R["descriptive: Australia late-Sep (after US 3rd Fri) minus other days (bp/day)"] = {"est": 1e4 * (ta[ta.late_sep].r.mean() - ta[~ta.late_sep].r.mean())}
json.dump(R, open(HERE / "out" / "partC.json", "w"), indent=1, default=float)
for k, v in R.items(): print(k, {a: (round(b, 2) if isinstance(b, float) else b) for a, b in v.items()})
