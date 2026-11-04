"""G1 / gap-teardown T4: TSLA Oct 28 features with features.feats unchanged (its data dir pointed here), placed on T1/T3.
Usage: python run_g1.py -> out/g1.json"""
import datetime as dt
import json
import sys
import urllib.request
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; GT = HERE.parent / "2026-10-28-gap-teardown"
sys.path.insert(0, str(GT)); import features as F   # noqa: E402
F.D = HERE / "data"


def yb(sym, iv, rng):
    u = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range={rng}&interval={iv}"
    r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=20))["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    return pd.DataFrame({k: q[k] for k in ("open", "high", "low", "close")}, index=pd.to_datetime(r["timestamp"], unit="s", utc=True).tz_convert("America/New_York")).dropna()


d = yb("TSLA", "1d", "6mo"); d.index = pd.to_datetime(d.index.date)
d["prev"] = d.close.shift(1); d["gap"] = d.open / d.prev - 1; d["r2"] = d.prev / d.close.shift(3) - 1; d["sig"] = np.log(d.close).diff().rolling(20).std().shift(1)
h = yb("TSLA", "60m", "2mo"); fh = h[(h.index.date == dt.date(2026, 10, 28)) & (h.index.hour == 9)].iloc[0]
R = d.loc["2026-10-28"]; up = (fh.high / R.open - 1) / R.sig; dn = (fh.low / R.open - 1) / R.sig
cls = "VF" if (dn <= -0.75 and up <= 0.25) else ("SC" if (up >= 0.75 and dn >= -0.25) else "mid")
r = SimpleNamespace(sym="TSLA", date=pd.Timestamp("2026-10-28"), cls=cls, scope="single-name", sig=float(R.sig), gap=float(R.gap), r2=float(R.r2))
f28, _ = F.feats(r)
fe = pd.read_csv(GT / "out" / "features.csv", parse_dates=["date"]); ts = fe[(fe.sym == "TSLA") & (fe.date < "2026-10-26")]
M = ["M6 first-5m delta %", "M8 first-5m progress per 1k bought (sig)", "M7 first-5m book imbalance", "M9 first-5m spread bp", "M10 first-5m retail-size share",
     "ret 09:30->09:35 (sig)", "ret 09:35->10:30 (sig)", "M3 opening imbalance / paired", "M2a premarket buy share"]
pl = lambda v, ref: round(float((ref.dropna() < v).mean()), 2)
out = {"Oct 28 inputs": {"gap (sig)": round(float(R.gap / R.sig), 2), "sig (20d)": round(float(R.sig), 4), "first-hour up/down (sig)": [round(float(up), 2), round(float(dn), 2)], "class by shape": cls,
                         "note": "gap below the 0.5 sig setup, so outside the tested population (as stated in the original T4)"}}
for lab, row in (("Oct 28", f28), ("Oct 27", fe[(fe.sym == "TSLA") & (fe.date == "2026-10-27")].iloc[0].to_dict()), ("Oct 26", fe[(fe.sym == "TSLA") & (fe.date == "2026-10-26")].iloc[0].to_dict())):
    out[lab] = {m: {"value": round(float(row[m]), 3) if row.get(m) is not None and np.isfinite(row[m]) else None,
                    "TSLA pctile (all gap-ups)": pl(row[m], ts[m]) if row.get(m) is not None and np.isfinite(row[m]) else None,
                    "VF median / SC median (TSLA)": [round(float(ts.loc[ts.cls == "VF", m].median()), 3), round(float(ts.loc[ts.cls == "SC", m].median()), 3)]} for m in M}
v = out["Oct 28"]["ret 09:30->09:35 (sig)"]["value"]
out["Oct 28 on the practical table"] = ("<= -0.25 sig row: next 55 min mean -0.08 sig, P(down) 58%, P(down > 0.5 sig) 20%, P(up > 0.5 sig) 18%" if v is not None and v <= -0.25 else f"first 5 min {v} sig")
json.dump(out, open(HERE / "out" / "g1.json", "w"), indent=1, default=str); print(json.dumps(out, indent=1, default=str))
