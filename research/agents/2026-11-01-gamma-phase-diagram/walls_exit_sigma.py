"""Descriptive: the call-wall overshoot in sigma units with controls reweighted to the A1 strata (sigma-distance bin x
prior-VIX tercile x roundness), so the comparison holds the day's volatility fixed. Reads out/walls_b_events_*.csv and
out/walls_exit.json inputs; usage: python walls_exit_sigma.py <SPY 1m parquet> <QQQ 1m parquet> -> out/walls_exit_sigma.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; ET = "America/New_York"; res = {}
for und, path in (("SPY", sys.argv[1]), ("QQQ", sys.argv[2])):
    m = pd.read_parquet(path, columns=["high"]); m.index = m.index.tz_convert(ET)
    m = m[(m.index.time >= pd.Timestamp("09:30").time()) & (m.index.time < pd.Timestamp("16:00").time())]
    hi = m.groupby(m.index.normalize().tz_localize(None)).high.max()
    T = pd.read_csv(HERE / "out" / f"walls_b_events_{und}.csv", parse_dates=["day"]); T = T[(T.side == "up") & (T.sbin >= 0)].copy()
    sig = (T.dist / T.ds)                                   # daily sigma as a fraction of the open
    T["over_s"] = (hi.reindex(T.day).to_numpy() / T.K - 1) / sig
    T["st"] = T.sbin.astype(str) + "_" + T.vt.astype(str) + "_" + T.round10.astype(str)
    nw, nc = T[T.wall == 1].st.value_counts(), T[T.wall == 0].st.value_counts()
    T["w"] = np.where(T.wall == 1, 1.0, T.st.map(nw / nc).fillna(0.0))
    out = {}
    for lab, S in (("call wall", T[T.wall == 1]), ("ordinary (A1-reweighted)", T[(T.wall == 0) & (T.w > 0)])):
        x, w = S.over_s.to_numpy(), S.w.to_numpy(); o = np.argsort(x); cw = np.cumsum(w[o]) / w.sum()
        out[lab] = {"n": int(len(S)), "overshoot quantiles 50/75/90 (sigma)": [round(float(np.interp(q, cw, x[o])), 3) for q in (.5, .75, .9)],
                    "P(> 0.25 sigma past)": round(float(np.average(x > .25, weights=w)), 3), "P(> 0.5 sigma past)": round(float(np.average(x > .5, weights=w)), 3),
                    "P(> 1 sigma past)": round(float(np.average(x > 1, weights=w)), 3), "_cdf": [np.round(x[o], 3).tolist(), np.round(cw, 4).tolist()]}
    res[und] = out
json.dump(res, open(HERE / "out" / "walls_exit_sigma.json", "w"), indent=1)
print(json.dumps({u: {k: {kk: vv for kk, vv in v.items() if kk != "_cdf"} for k, v in R.items()} for u, R in res.items()}, indent=1))
