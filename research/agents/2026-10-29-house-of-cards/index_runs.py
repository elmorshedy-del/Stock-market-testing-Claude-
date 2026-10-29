"""H1-H3 (pre-registered @ bab7db6): forced (vol-up) vs genuine (vol-down) index runs; give-back within 10 sessions.
Usage: python index_runs.py <scratchpad> -> out/index_runs.json, out/index_events.csv"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

S = Path(sys.argv[1]); HERE = Path(__file__).resolve().parent
rng = np.random.default_rng(0); B = 10000


def close(p):
    r = json.load(open(p))["chart"]["result"][0]
    c = pd.Series(r["indicators"]["quote"][0]["close"], index=pd.to_datetime(r["timestamp"], unit="s").normalize()).dropna()
    return c[~c.index.duplicated(keep="last")]


def events(px, iv, lo, hi):
    d = pd.DataFrame({"c": px, "v": iv}).dropna(); d = d[(d.index >= lo) & (d.index <= hi)]
    c, v = d.c.to_numpy(), d.v.to_numpy(); r10 = np.full(len(c), np.nan); r10[10:] = c[10:] / c[:-10] - 1
    thr = np.nanpercentile(r10, 90); out = []; nxt = 0
    for i in range(10, len(c) - 10):
        if i < nxt or not (r10[i] >= thr and c[i] >= c[i - 10:i + 1].max()): continue
        run = c[i] - c[i - 10]; fut = c[i + 1:i + 11]
        gb = (c[i] - fut.min()) / run
        half = np.flatnonzero(fut <= c[i] - 0.5 * run); t50 = int(half[0] + 1) if len(half) else 11
        out.append({"date": d.index[i], "run_pct": 100 * r10[i], "iv_start": v[i - 10], "iv_chg": v[i] - v[i - 10], "forced": int(v[i] - v[i - 10] > 0),
                    "giveback": gb, "cliff": int(gb >= 0.5), "t50": t50, "next10_pct": 100 * (c[i + 10] / c[i] - 1)})
        nxt = i + 10
    E = pd.DataFrame(out); E["stratum"] = pd.qcut(E.iv_start, 3, labels=["low", "mid", "high"])
    return E, thr


def strat_diff(E, col):
    parts = [(len(g), g[g.forced == 1][col].mean() - g[g.forced == 0][col].mean()) for _, g in E.groupby("stratum", observed=True) if g.forced.nunique() == 2]
    w = np.array([n for n, _ in parts], float); return float(np.sum(w * np.array([x for _, x in parts])) / w.sum())


def boot(E, col):
    est = strat_diff(E, col); groups = [g for _, g in E.groupby("stratum", observed=True)]; bs = np.empty(B)
    for i in range(B):
        bs[i] = strat_diff(pd.concat([g.iloc[rng.integers(0, len(g), len(g))] for g in groups]), col)
    bs = bs[~np.isnan(bs)]
    return {"est": est, "ci95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))], "p": float(min(1, 2 * min((bs <= 0).mean(), (bs >= 0).mean()) + 1 / len(bs)))}


def describe(E):
    g = E.groupby("forced")
    return {("forced" if k else "genuine"): {"n": int(len(x)), "run_pct": float(x.run_pct.mean()), "giveback_mean": float(x.giveback.mean()), "giveback_median": float(x.giveback.median()),
                                             "cliff_rate": float(x.cliff.mean()), "t50_median_censored11": float(x.t50.median()), "next10_pct": float(x.next10_pct.mean())} for k, x in g}


spx = close(S / "ladder28" / "data" / "^GSPC_1d.json"); vix = close(S / "ladder28" / "data" / "^VIX_1d.json")
ndx = close(S / "ctx" / "intl" / "%5ENDX.json"); vxn = close(S / "ctx" / "intl" / "%5EVXN.json")
E1, t1 = events(spx, vix, pd.Timestamp("1990-01-02"), pd.Timestamp("2025-12-31"))
E3, t3 = events(ndx, vxn, pd.Timestamp("2001-01-23"), pd.Timestamp("2025-12-31"))
R = {"H1 S&P give-back, forced minus genuine (fraction of run, VIX-stratified)": boot(E1, "giveback") | {"threshold_10d_pct": 100 * t1},
     "H2 S&P cliff (gave back >= 50% within 10 sessions), forced minus genuine": boot(E1, "cliff"),
     "H3 Nasdaq-100 give-back, forced minus genuine (VXN-stratified)": boot(E3, "giveback") | {"threshold_10d_pct": 100 * t3}}
json.dump({"tests": R, "describe_spx": describe(E1), "describe_ndx": describe(E3),
           "by_stratum_spx": {str(k): describe(g) for k, g in E1.groupby("stratum", observed=True)}}, open(HERE / "out" / "index_runs.json", "w"), indent=1, default=float)
pd.concat([E1.assign(index="SPX"), E3.assign(index="NDX")]).to_csv(HERE / "out" / "index_events.csv", index=False)
for k, v in R.items(): print(k, {a: (np.round(b, 3) if not isinstance(b, list) else np.round(b, 3).tolist()) for a, b in v.items()})
print(json.dumps({"spx": describe(E1), "ndx": describe(E3)}, indent=1, default=lambda x: round(float(x), 3)))
print(E1[(E1.date >= "2020-08-01") & (E1.date <= "2020-09-30")].round(3).to_string())
