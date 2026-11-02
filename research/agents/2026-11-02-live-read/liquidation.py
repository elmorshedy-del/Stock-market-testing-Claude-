"""Pre-registered LQ: forced-liquidation footprints on Fri Oct 30 2026 vs every day since 2024, calibrated on the reported July unwind.
Usage: python liquidation.py <yahoo dir> -> out/liquidation.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; Y = Path(sys.argv[1])
B = ["NVDA", "AVGO", "AMD", "MU", "MRVL", "TSM", "SMCI", "ORCL", "CRWV", "NBIS", "VRT", "VST", "CEG", "LITE", "COHR", "ANET", "CLS", "WDC", "STX", "SNDK", "IREN", "CORZ", "PLTR", "ALAB", "CRDO"]
def load(t):
    r = json.load(open(Y / f"{t}.json"))["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    v = r["indicators"]["adjclose"][0]["adjclose"] if "adjclose" in r["indicators"] else q["close"]
    d = pd.DataFrame({"c": v, "close": q["close"], "vol": q["volume"]}, index=pd.to_datetime(r["timestamp"], unit="s").normalize()); return d[~d.index.duplicated(keep="last")].dropna()
D = {t: load(t) for t in B + ["RSP"]}
ret = pd.DataFrame({t: D[t].c.pct_change() for t in B}); rsp = D["RSP"].c.pct_change()
dv = pd.DataFrame({t: D[t].close * D[t].vol for t in B}); dvr = dv.sum(1, min_count=10) / dv.sum(1, min_count=10).rolling(20).mean().shift(1)
f = pd.DataFrame({"basket": ret.mean(1, skipna=True), "n": ret.notna().sum(1), "share_down": (ret < 0).sum(1) / ret.notna().sum(1), "rsp": rsp, "dvol_ratio": dvr}).loc["2024-01-01":].dropna(subset=["basket", "rsp"])
f["spread"] = f.basket - f.rsp; f["next2"] = f.spread.shift(-1) + f.spread.shift(-2)
pct = lambda s, v: round(float((s < v).mean()), 4)
def day(d):
    x = f.loc[d]
    return {"basket %": round(100 * float(x.basket), 2), "RSP %": round(100 * float(x.rsp), 2), "spread %": round(100 * float(x.spread), 2), "spread pct (low = worse)": pct(f.spread, x.spread),
            "share of basket down": round(float(x.share_down), 2), "RSP pct": pct(f.rsp, x.rsp), "dollar volume vs 20d": round(float(x.dvol_ratio), 2), "volume pct": pct(f.dvol_ratio.dropna(), x.dvol_ratio),
            "next 2 sessions spread %": (round(100 * float(x.next2), 2) if not np.isnan(x.next2) else None), "n names": int(x.n)}
res = {"days since 2024": len(f), "Fri Oct 30 2026": day(pd.Timestamp("2026-10-30")),
       "Mon Oct 26 to Thu Oct 29 (context)": {str(d.date()): day(d) for d in f.loc["2026-10-26":"2026-10-29"].index},
       "July unwind window (calibration)": {str(d.date()): day(d) for d in f.loc["2026-07-22":"2026-08-04"].index}}
w = f.nsmallest(12, "spread")
res["12 worst spread days since 2024 [date, spread %, share down, RSP %, dvol ratio]"] = [[str(d.date()), round(100 * float(r.spread), 2), round(float(r.share_down), 2), round(100 * float(r.rsp), 2), round(float(r.dvol_ratio), 2) if not np.isnan(r.dvol_ratio) else None] for d, r in w.iterrows()]
worst = f[f.spread <= f.spread.quantile(0.02)]
res["after the worst 2% spread days: mean next-2 spread %, share positive, n"] = [round(100 * float(worst.next2.mean()), 2), round(float((worst.next2 > 0).mean()), 2), int(worst.next2.notna().sum())]
json.dump(res, open(HERE / "out" / "liquidation.json", "w"), indent=1, default=str); print(json.dumps(res, indent=1, default=str))
