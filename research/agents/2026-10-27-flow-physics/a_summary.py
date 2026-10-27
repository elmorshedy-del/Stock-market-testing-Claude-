"""A1/A2 summaries: flow vs returns, endogeneity vs move size, liquidity vs dealer gamma; weekly frame.
Usage: python a_summary.py <ladder27 folder (data/DIX.csv)>  -> out/a_summary.json, out/a_weekly.csv"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
d = pd.read_csv(HERE / "out" / "a_daily.csv", parse_dates=["day"])
sm = pd.read_csv(Path(sys.argv[1]) / "data" / "DIX.csv", parse_dates=["date"]).set_index("date")
pct = sm.gex.rolling(252).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True)
res = {}
for sym, x in d.groupby("sym"):
    x = x.sort_values("day").copy()
    r1 = spearmanr(x["ret %"], x["delta % of vol"]); r2 = spearmanr(x["ret %"].abs(), x["hawkes n median"])
    out = {"sessions": int(len(x)), "Spearman(open-close return, delta % of volume)": [round(r1[0], 3), round(r1[1], 3)],
           "Spearman(|return|, Hawkes n)": [round(r2[0], 3), round(r2[1], 3)],
           "Hawkes n median range": [round(float(x["hawkes n median"].min()), 3), round(float(x["hawkes n median"].max()), 3)],
           "Kyle lambda first half / second half of window": [round(float(x["lambda (pts per 1k net)"].iloc[:len(x) // 2].median()), 4), round(float(x["lambda (pts per 1k net)"].iloc[len(x) // 2:].median()), 4)]}
    g = pct.shift(1).reindex(x.day.values)                        # prior close's dealer gamma pctile (SqueezeMetrics, S&P)
    ok = np.isfinite(g.values)
    r3 = spearmanr(g.values[ok], x["lambda (pts per 1k net)"].values[ok])
    out["Spearman(prior-day S&P GEX pctile, Kyle lambda)"] = [round(r3[0], 3), round(r3[1], 3), int(ok.sum())]
    x["week"] = x.day.dt.to_period("W-FRI").astype(str)
    w = x.groupby("week").agg(ret=("ret %", "sum"), delta=("delta", "sum"), volume=("volume", "sum"), lam=("lambda (pts per 1k net)", "median"), n=("hawkes n median", "median"), days=("day", "count"))
    w["delta % of vol"] = 100 * w.delta / w.volume
    w.insert(0, "sym", sym)
    out["weekly"] = w.round(4).reset_index().to_dict(orient="records")
    res[sym] = out
    w.to_csv(HERE / "out" / f"a_weekly_{sym}.csv")
(HERE / "out" / "a_summary.json").write_text(json.dumps(res, indent=1, default=str))
print(json.dumps(res, indent=1, default=str))
