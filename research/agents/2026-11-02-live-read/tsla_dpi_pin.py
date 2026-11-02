"""TSLA's own dark-pool index (FINRA short share of off-exchange volume; same recipe as 2026-10-28-tsla-freed-dpi) through Oct 30,
and how much of the 400 strike's gamma expires today. Usage: python tsla_dpi_pin.py <finra row dir> <td dir>"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent / "2026-10-27-flip-wicks")]
from flipmap import norm, preopen, exposures   # noqa: E402
rows = []
for f in sorted(Path(sys.argv[1]).glob("*.row")):
    t = f.read_text().strip()
    if t: p = t.split("|"); rows.append((pd.Timestamp(p[0]), float(p[2]), float(p[4])))
h = pd.DataFrame(rows, columns=["date", "short", "total"]).set_index("date").sort_index()
h["dpi"] = h.short / h.total; h["dpi5"] = h.dpi.rolling(5).mean()
h["pct5"] = h.dpi5.rolling(252, min_periods=120).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True)
yr = h.dpi.iloc[-252:]
res = {"days": len(h), "last 8 days [daily DPI, off-exchange volume M]": {str(i.date()): [round(float(r.dpi), 3), round(float(r.total) / 1e6, 1)] for i, r in h.tail(8).iterrows()},
       "5-day DPI and pct (last 5 days)": {str(i.date()): [round(float(r.dpi5), 3), round(float(r.pct5), 3)] for i, r in h.tail(5).iterrows()},
       "one-year daily range / median / terciles": [round(float(yr.min()), 3), round(float(yr.max()), 3), round(float(yr.median()), 3), [round(float(x), 3) for x in yr.quantile([1 / 3, 2 / 3])]],
       "5-day DPI bottom-tenth line": round(float(h.dpi5.iloc[-252:].quantile(.10)), 3)}
td = Path(sys.argv[2]); P, MON = pd.Timestamp("2026-10-30"), pd.Timestamp("2026-11-02")
e = norm(pd.read_csv(td / "TSLA_eod_20261030.csv.gz")); e = e[e.date == P]; o = norm(pd.read_csv(td / "TSLA_oi_20261102.csv.gz"))
g = preopen(e, o, MON); g = g[g.expiration >= MON].copy(); g["underlying_close"] = 399.81
ex = exposures(g, 402.22); k = ex[ex.K.between(395, 410)].copy(); k["today"] = k.exp == MON.date()
tab = k.groupby(["K", "today"]).gex.sum().unstack().fillna(0) / 1e9
res["gamma by strike near 400 ($bn per 1%): [expires today, later, today's share]"] = {float(K): [round(float(r.get(True, 0)), 3), round(float(r.get(False, 0)), 3), round(float(r.get(True, 0) / (r.get(True, 0) + r.get(False, 0))) if (r.get(True, 0) + r.get(False, 0)) else 0, 2)] for K, r in tab.iterrows()}
oi = o[(pd.to_datetime(o.expiration) == MON) & o.strike.between(395, 410)]
c = [c for c in oi.columns if "open_interest" in c or c == "oi"][0]
res["Nov 2 expiry OI near 400 (calls / puts, thousands)"] = {float(K): [round(float(x[x.cp == "C"][c].sum() / 1e3), 1), round(float(x[x.cp == "P"][c].sum() / 1e3), 1)] for K, x in oi.groupby("strike")}
json.dump(res, open(HERE / "out" / "tsla_dpi_pin.json", "w"), indent=1); print(json.dumps(res, indent=1))
