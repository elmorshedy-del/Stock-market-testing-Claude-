"""Pre-registered AS (README, 10:12 ET): does an earnings move spill over to the rest of the market (RSP), AAPL vs the AI spenders?
Reaction day = the session after a post-market report. Usage: python aapl_spill.py <dates json> <yahoo dir> -> out/aapl_spill.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; D = json.load(open(sys.argv[1])); Y = Path(sys.argv[2]); rng = np.random.default_rng(5)
def yc(t):
    r = json.load(open(Y / f"{t}.json"))["chart"]["result"][0]
    v = r["indicators"]["adjclose"][0]["adjclose"] if "adjclose" in r["indicators"] else r["indicators"]["quote"][0]["close"]
    s = pd.Series(v, index=pd.to_datetime(r["timestamp"], unit="s").normalize()); return s[~s.index.duplicated(keep="last")].dropna()
R = pd.DataFrame({t: yc(t).pct_change() for t in list(D) + ["RSP"]}).dropna(how="all")
rows = []
for t, ds in D.items():
    for d in ds:
        i = R.index.searchsorted(pd.Timestamp(d), side="right")       # first session after the report date
        if i >= len(R): continue
        day = R.index[i]; rows.append({"sym": t, "day": day, "x": float(R[t].iloc[i]), "y": float(R["RSP"].iloc[i])})
E = pd.DataFrame(rows).dropna()
E["overlap"] = E.groupby("day").sym.transform("count") > 1           # another of the six reacted the same day
def slope(e):
    X = np.c_[np.ones(len(e)), e.x]; return float(np.linalg.lstsq(X, e.y.to_numpy(), rcond=None)[0][1])
def boot(e, f, n=5000):
    a = e.to_numpy(); out = []
    for _ in range(n):
        s = e.iloc[rng.integers(0, len(e), len(e))]; out.append(f(s))
    return np.array(out)
def diff_p(a, b, f):
    da, db = boot(a, f), boot(b, f); d = da - db; return float(f(a) - f(b)), [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))], float(2 * min((d <= 0).mean(), (d >= 0).mean()))
res = {}
for era, s in [("2015-26", "2015-01-01"), ("2022+", "2022-01-01")]:
    e = E[E.day >= s]; aapl = e[e.sym == "AAPL"]; ai = e[e.sym.isin(["MSFT", "AMZN", "META", "GOOGL"])]; nv = e[e.sym == "NVDA"]
    r = {"n AAPL / AI spenders / NVDA": [len(aapl), len(ai), len(nv)]}
    for lab, x in [("AAPL", aapl), ("AI spenders (MSFT, AMZN, META, GOOGL)", ai), ("NVDA", nv)] + [(k, e[e.sym == k]) for k in ["MSFT", "AMZN", "META", "GOOGL"]]:
        r[lab] = {"slope of RSP on the stock's move": round(slope(x), 3), "corr": round(float(x.x.corr(x.y)), 2), "mean |stock move| %": round(100 * float(x.x.abs().mean()), 2), "n": len(x)}
    d, ci, p = diff_p(aapl, ai, slope); r["AS1: AAPL slope − AI slope [diff, 95% CI, p]"] = [round(d, 3), [round(c, 3) for c in ci], round(p, 3)]
    up, dn = aapl[aapl.x > 0], aapl[aapl.x < 0]
    r["AS2 AAPL up reactions: n, slope, mean RSP %"] = [len(up), round(slope(up), 3), round(100 * float(up.y.mean()), 2)]
    r["AS2 AAPL down reactions: n, slope, mean RSP %"] = [len(dn), round(slope(dn), 3), round(100 * float(dn.y.mean()), 2)]
    d2, ci2, p2 = diff_p(up, dn, slope); r["AS2: up slope − down slope [diff, 95% CI, p]"] = [round(d2, 3), [round(c, 3) for c in ci2], round(p2, 3)]
    for lab, x in [("AI up", ai[ai.x > 0]), ("AI down", ai[ai.x < 0])]: r[f"{lab}: n, slope, mean RSP %"] = [len(x), round(slope(x), 3), round(100 * float(x.y.mean()), 2)]
    a2, i2 = aapl[~aapl.overlap], ai[~ai.overlap]
    r["sensitivity (no other megacap reacting the same day): AAPL slope / AI slope / n"] = [round(slope(a2), 3), round(slope(i2), 3), [len(a2), len(i2)]]
    res[era] = r
big = E[(E.sym == "AAPL") & (E.x.abs() >= 0.04)].sort_values("day")
res["AAPL reactions >= 4%: [day, AAPL %, RSP %]"] = [[str(r.day.date()), round(100 * r.x, 1), round(100 * r.y, 2)] for r in big.itertuples()]
json.dump(res, open(HERE / "out" / "aapl_spill.json", "w"), indent=1); print(json.dumps(res, indent=1))
