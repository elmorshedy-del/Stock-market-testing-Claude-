"""Amendment AS-R: AS1/AS2 in the AI-capex scrutiny regime (since 2025-01-27 and since 2025-10-01) + the event table.
Usage: python aapl_spill_regime.py <dates json> <yahoo dir> -> out/aapl_spill_regime.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; D = json.load(open(sys.argv[1])); Y = Path(sys.argv[2]); rng = np.random.default_rng(6)
def yc(t):
    r = json.load(open(Y / f"{t}.json"))["chart"]["result"][0]
    v = r["indicators"]["adjclose"][0]["adjclose"] if "adjclose" in r["indicators"] else r["indicators"]["quote"][0]["close"]
    s = pd.Series(v, index=pd.to_datetime(r["timestamp"], unit="s").normalize()); return s[~s.index.duplicated(keep="last")].dropna()
R = pd.DataFrame({t: yc(t).pct_change() for t in list(D) + ["RSP", "SPY"]}).dropna(how="all")
rows = []
for t, ds in D.items():
    for d in ds:
        i = R.index.searchsorted(pd.Timestamp(d), side="right")
        if i < len(R): rows.append({"sym": t, "day": R.index[i], "x": float(R[t].iloc[i]), "rsp": float(R["RSP"].iloc[i]), "spy": float(R["SPY"].iloc[i])})
E = pd.DataFrame(rows).dropna(); AI = ["MSFT", "AMZN", "META", "GOOGL"]
def slope(e): return float(np.linalg.lstsq(np.c_[np.ones(len(e)), e.x], e.rsp.to_numpy(), rcond=None)[0][1]) if len(e) >= 3 else np.nan
res = {}
for lab, s in [("since 2025-01-27 (DeepSeek)", "2025-01-27"), ("since 2025-10-01 (debt-funded capex scrutiny)", "2025-10-01")]:
    e = E[E.day >= s]; a = e[e.sym == "AAPL"]; ai = e[e.sym.isin(AI)]; nv = e[e.sym == "NVDA"]
    bd = []
    for _ in range(5000):
        sa, si = a.iloc[rng.integers(0, len(a), len(a))], ai.iloc[rng.integers(0, len(ai), len(ai))]; bd.append(slope(sa) - slope(si))
    bd = np.array(bd); bd = bd[~np.isnan(bd)]
    res[lab] = {"n AAPL / AI / NVDA": [len(a), len(ai), len(nv)], "slope AAPL / AI / NVDA": [round(slope(a), 3), round(slope(ai), 3), round(slope(nv), 3)],
                "AAPL − AI slope, 95% CI, p": [round(slope(a) - slope(ai), 3), [round(float(np.percentile(bd, 2.5)), 3), round(float(np.percentile(bd, 97.5)), 3)], round(float(2 * min((bd <= 0).mean(), (bd >= 0).mean())), 3)],
                "mean |RSP| on reaction days %: AAPL / AI / NVDA": [round(100 * float(a.rsp.abs().mean()), 2), round(100 * float(ai.rsp.abs().mean()), 2), round(100 * float(nv.rsp.abs().mean()), 2)],
                "same-sign share (RSP moves with the stock): AAPL / AI / NVDA": [round(float((np.sign(a.x) == np.sign(a.rsp)).mean()), 2), round(float((np.sign(ai.x) == np.sign(ai.rsp)).mean()), 2), round(float((np.sign(nv.x) == np.sign(nv.rsp)).mean()), 2)],
                "AAPL up / down: n, mean RSP %": [[int((a.x > 0).sum()), round(100 * float(a[a.x > 0].rsp.mean()), 2) if (a.x > 0).any() else None], [int((a.x < 0).sum()), round(100 * float(a[a.x < 0].rsp.mean()), 2) if (a.x < 0).any() else None]],
                "AI down / up: n, mean RSP %": [[int((ai.x < 0).sum()), round(100 * float(ai[ai.x < 0].rsp.mean()), 2)], [int((ai.x > 0).sum()), round(100 * float(ai[ai.x > 0].rsp.mean()), 2)]]}
ev = E[E.day >= "2025-01-27"].sort_values("day")
res["event table since 2025-01-27 [day, stock, stock %, RSP %, SPY %]"] = [[str(r.day.date()), r.sym, round(100 * r.x, 1), round(100 * r.rsp, 2), round(100 * r.spy, 2)] for r in ev.itertuples()]
json.dump(res, open(HERE / "out" / "aapl_spill_regime.json", "w"), indent=1); print(json.dumps({k: v for k, v in res.items() if not k.startswith("event")}, indent=1))
for r in res["event table since 2025-01-27 [day, stock, stock %, RSP %, SPY %]"]: print(r)
