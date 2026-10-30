"""Translate R2 (SqueezeMetrics GEX <= 30th pct, DIX > 50th) into an S&P closing level for Fri Oct 30, since GEX/DIX
are only published after the close. Thresholds: GEX <= $4.53bn, DIX >= 45.43% (ranked vs the prior 251 days).
Model: daily change in GEX ($bn) and DIX (pts) regressed on the S&P daily return over the last 2 years,
with the joint residuals resampled (keeps their correlation). Descriptive; not a pre-registered test.
Usage: python r2_price.py <DIX.csv> -> out/r2_price.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
d = pd.read_csv(sys.argv[1], parse_dates=["date"]).set_index("date")
w = d.gex.iloc[-251:]; wd = d.dix.iloc[-251:]
GT, DT = float(np.quantile(w, 0.30) / 1e9), float(np.median(wd) * 100)
G0, D0, P0 = d.gex.iloc[-1] / 1e9, d.dix.iloc[-1] * 100, float(d.price.iloc[-1])
d["r"] = d.price.pct_change() * 100; d["dG"] = d.gex.diff() / 1e9; d["dD"] = d.dix.diff() * 100
out = {"GEX threshold $bn": round(GT, 2), "DIX threshold %": round(DT, 2), "GEX now": round(G0, 2), "DIX now": round(D0, 2), "SPX close": P0, "fits": {}}
for lab, x in (("last 2 years", d.loc["2024-10-01":].dropna()),
               ("last 2 years, start GEX $3.5-8bn", d.loc["2024-10-01":].dropna()[lambda z: (d.gex.shift().loc[z.index] / 1e9).between(3.5, 8.0)])):
    bG = np.polyfit(x.r, x.dG, 1); bD = np.polyfit(x.r, x.dD, 1)
    res = np.c_[x.dG - np.polyval(bG, x.r), x.dD - np.polyval(bD, x.r)]
    rows = []
    for r in np.round(np.arange(-3.0, 0.01, 0.25), 2):
        g = G0 + np.polyval(bG, r) + res[:, 0]; dd = D0 + np.polyval(bD, r) + res[:, 1]
        rows.append({"S&P day %": float(r), "SPX": round(P0 * (1 + r / 100)), "SPY": round(769.36 * (1 + r / 100), 1),
                     "P(GEX low)": round(float(np.mean(g <= GT)), 2), "P(DIX ok)": round(float(np.mean(dd >= DT)), 2), "P(R2)": round(float(np.mean((g <= GT) & (dd >= DT))), 2)})
    out["fits"][lab] = {"n": len(x), "GEX $bn per 1% S&P": round(float(bG[0]), 2), "DIX pts per 1% S&P": round(float(bD[0]), 2), "table": rows}
json.dump(out, open(HERE / "out" / "r2_price.json", "w"), indent=1)
for lab, v in out["fits"].items():
    print(lab, "n", v["n"], "| GEX per 1%:", v["GEX $bn per 1% S&P"], "| DIX per 1%:", v["DIX pts per 1% S&P"])
    print(pd.DataFrame(v["table"]).to_string(index=False))
print({k: v for k, v in out.items() if k != "fits"})
