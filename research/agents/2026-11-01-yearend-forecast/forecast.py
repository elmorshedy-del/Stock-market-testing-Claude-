"""Year-end forecast (pre-registered @ 7a2a4ab). Step 1 analog test A1; Step 2 empirical base-rate forecast (B-all,
B-midterm, B-pullback), vol-scaled. Usage: python forecast.py <GSPC_long.json> -> out/forecast.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; rng = np.random.default_rng(5); SPY0 = 755.69
r = json.load(open(sys.argv[1]))["chart"]["result"][0]
P = pd.Series(r["indicators"]["quote"][0]["close"], index=pd.to_datetime(r["timestamp"], unit="s").normalize()).dropna()
P = P[~P.index.duplicated(keep="last")]; lp = np.log(P.to_numpy()); idx = P.index; n = len(P)
me = pd.Series(np.arange(n), index=idx).groupby([idx.year, idx.month]).max()   # month-end positions
res = {}
# ---------- A1 analog test
rows = []
keys = list(me.index)
for q, (y, m) in enumerate(keys):
    if q < 3: continue
    i, j = me[(y, m)], me[keys[q - 3]]
    row = {"y": y, "m": m}
    for h in (20, 40):
        if i + h < n: row[f"f{h}"] = lp[i + h] - lp[i]; row[f"a{h}"] = lp[j + h] - lp[j]
    rows.append(row)
A = pd.DataFrame(rows)
for h in (20, 40):
    X = A.dropna(subset=[f"f{h}", f"a{h}"]); c = np.corrcoef(X[f"f{h}"], X[f"a{h}"])[0, 1]
    yrs = X.y.unique(); g = {y: X[X.y == y] for y in yrs}; bs = []
    for _ in range(5000):
        Z = pd.concat([g[y] for y in rng.choice(yrs, len(yrs))]); bs.append(np.corrcoef(Z[f"f{h}"], Z[f"a{h}"])[0, 1])
    bs = np.array(bs); agree = float((np.sign(X[f"f{h}"]) == np.sign(X[f"a{h}"])).mean())
    O = X[X.m == 10]; co = np.corrcoef(O[f"f{h}"], O[f"a{h}"])[0, 1]
    res[f"A1 analog, next {h} sessions vs the same {h} after the month-end 3 months earlier"] = {
        "corr": round(float(c), 3), "95% CI": np.round(np.quantile(bs, [.025, .975]), 3).tolist(), "p (corr<=0)": round(float((bs <= 0).mean()), 3),
        "sign agreement": round(agree, 3), "n": int(len(X)), "Octobers only (after Oct vs after Jul) corr": round(float(co), 3), "Octobers n": int(len(O))}
use_analog = all(v["corr"] > 0 and v["p (corr<=0)"] < 0.05 for k, v in res.items() if k.startswith("A1"))
res["analog enters forecast?"] = bool(use_analog)
# ---------- B base rates
ret = np.diff(lp); rv = lambda i: float(np.std(ret[i - 20:i]) * np.sqrt(252))
i_now = n - 1; assert idx[i_now] == pd.Timestamp("2026-10-30")
rv_now = rv(i_now); dd_now = float(P.iloc[i_now] / P.iloc[i_now - 251:i_now + 1].max() - 1)
res["today"] = {"S&P close Oct 30": round(float(P.iloc[i_now]), 2), "20d realized vol": round(rv_now, 3), "below 52w high %": round(100 * dd_now, 2)}
Y = []
for y in range(1950, 2026):
    i0 = me[(y, 10)]; inov = me[(y, 11)]; idec = me[(y, 12)]
    f = float(np.clip(rv_now / rv(i0), 0.5, 2.0)); dd = float(P.iloc[i0] / P.iloc[max(0, i0 - 251):i0 + 1].max() - 1)
    path = lp[i0:idec + 1] - lp[i0]
    Y.append({"y": y, "scale": f, "dd": dd, "midterm": y % 4 == 2, "k10": f * (lp[i0 + 10] - lp[i0]), "nov": f * (lp[inov] - lp[i0]), "dec": f * (lp[idec] - lp[i0]),
              "path": (f * path).tolist(), "raw_dec": float(lp[idec] - lp[i0])})
Y = pd.DataFrame(Y)
cls = {"B-all": Y, "B-midterm": Y[Y.midterm], "B-pullback (Oct close 2-8% below 52w high)": Y[(Y.dd <= -0.02) & (Y.dd >= -0.08)]}
for lab, C in cls.items():
    out = {"n": int(len(C)), "years": C.y.tolist() if len(C) <= 30 else "all 1950-2025"}
    for k, nm in (("k10", "Nov 13 (10 sessions)"), ("nov", "Nov 30"), ("dec", "Dec 31")):
        q = np.quantile(C[k], [.1, .25, .5, .75, .9])
        out[nm] = {"P(up)": round(float((C[k] > 0).mean()), 3), "return % 10/25/50/75/90": np.round(100 * (np.exp(q) - 1), 2).tolist(),
                   "SPY 10/25/50/75/90": np.round(SPY0 * np.exp(q), 1).tolist()}
    out["unscaled Dec 31 median %"] = round(100 * (np.exp(C.raw_dec.median()) - 1), 2)
    res[lab] = out
# fan chart data (B-all) and the July analog path (Jul 31 close -> next 42 sessions)
# each year mapped onto 2026's 42-session grid by fraction of the Oct-end -> Dec-end span (years differ in session counts)
L = 43; g = np.linspace(0, 1, L)
M = np.array([np.interp(g, np.linspace(0, 1, len(p)), p) for p in Y.path]); res["_fan"] = {"k": list(range(L)), "q": {str(q): np.round(SPY0 * np.exp(np.quantile(M, q, axis=0)), 2).tolist() for q in (.1, .25, .5, .75, .9)}}
j = int(np.nonzero(idx == pd.Timestamp("2026-07-31"))[0][0]); res["_analog"] = np.round(SPY0 * np.exp(lp[j:j + 43] - lp[j]), 2).tolist()
json.dump(res, open(HERE / "out" / "forecast.json", "w"), indent=1)
print(json.dumps({k: v for k, v in res.items() if not k.startswith("_")}, indent=1))
