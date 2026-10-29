"""Post-hoc diagnostics (labelled exploratory): (1) is F2's pass a sigma-scaling artifact? Re-test with the first-hour range in %
and with recent volatility (5-day RV / 20-day sigma) controlled; (2) the earnings-gap fade (C7) by symbol and gap size.
Usage: python diag_ctx.py <scratchpad> -> out/diag_ctx.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

S = Path(sys.argv[1]); HERE = Path(__file__).resolve().parent
C = pd.read_csv(HERE / "out" / "context.csv", parse_dates=["date"]).merge(pd.read_csv(HERE / "out" / "fragility.csv", parse_dates=["date"]), on=["sym", "date"])


def daily(sym):
    r = json.load(open(S / "ctx" / "daily" / f"{sym}.json"))["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    d = pd.DataFrame({"close": q["close"]}, index=pd.to_datetime(r["timestamp"], unit="s").normalize()); return d[~d.index.duplicated(keep="last")].dropna()


rv = []
for s in C.sym.unique():
    lr = np.log(daily(s).close).diff()
    for d in C[C.sym == s].date:
        x = lr[lr.index < d]; rv.append({"sym": s, "date": d, "rv5": x.iloc[-5:].std() * np.sqrt(1)})
C = C.merge(pd.DataFrame(rv), on=["sym", "date"]); C["rv5_over_sig"] = C.rv5 / C.sig
C["Y2pct"] = C.Y2 * C.sig * 100
top = C.groupby("sym").F2_illiq_ratio.rank(pct=True) > 2 / 3
dm = lambda col: C[col] - C.groupby("sym")[col].transform("mean")
out = {"F2 top vs rest, Y2 in sigma": float(dm("Y2")[top].mean() - dm("Y2")[~top].mean()),
       "F2 top vs rest, Y2 in %": float(dm("Y2pct")[top].mean() - dm("Y2pct")[~top].mean()),
       "corr(F2 rank, rv5/sigma rank)": float(stats.spearmanr(C.F2_illiq_ratio, C.rv5_over_sig)[0]),
       "corr(rv5/sigma, Y2 in sigma)": float(stats.spearmanr(C.rv5_over_sig, C.Y2)[0])}
# partial: residualize Y2 (sigma) on rv5/sigma rank within stock, then contrast
z = C.groupby("sym").rv5_over_sig.rank(pct=True); y = dm("Y2"); b = np.polyfit(z, y, 1); res = y - np.polyval(b, z)
out["F2 top vs rest, Y2 in sigma after removing rv5/sigma"] = float(res[top].mean() - res[~top].mean())
# volume side of Amihud: 5-day vs 60-day dollar volume
E = C[(C.C7_earn == 1)]
out["earnings gap-ups"] = E.groupby("sym").agg(n=("cls", "size"), vf=("cls", lambda x: int((x == "VF").sum())), sc=("cls", lambda x: int((x == "SC").sum())), Y1_mean=("Y1", "mean")).round(2).reset_index().to_dict(orient="records")
out["earnings gap-ups list"] = E.sort_values("date")[["sym", "date", "gap", "cls", "Y1"]].assign(date=lambda d: d.date.astype(str), gap=lambda d: (100 * d.gap).round(1), Y1=lambda d: d.Y1.round(2)).to_dict(orient="records")
json.dump(out, open(HERE / "out" / "diag_ctx.json", "w"), indent=1, default=float)
for k, v in out.items():
    if k != "earnings gap-ups list": print(k, ":", v)
print(pd.DataFrame(out["earnings gap-ups list"]).tail(20).to_string(index=False))
