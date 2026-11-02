"""TSLA's weekly rhythm (descriptive): (a) near-price OI share going into each day Oct 15 -> Nov 2 from OI files alone (full <= 120-day
denominator, spot = prior close), ranked vs the engine's trailing year; share of near OI expiring by that week's Friday;
(b) engine history 2023-Oct 14 2026: near-OI pct and own-gamma pct by weekday; (c) TSLA daily returns by weekday, last 3 weeks.
Usage: python weekly_rhythm.py <TSLA yahoo json> <OI dirs ...> -> out/weekly_rhythm.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; MICRO = HERE.parents[1] / "microstructure"
r = json.load(open(sys.argv[1]))["chart"]["result"][0]
px = pd.Series(r["indicators"]["quote"][0]["close"], index=pd.to_datetime(r["timestamp"], unit="s").normalize()).dropna()
O = pd.concat([pd.read_csv(f) for d in sys.argv[2:] for f in sorted(Path(d).glob("TSLA_oi_*.csv.gz"))])
O["date"] = pd.to_datetime(O.timestamp.astype(str).str[:10]); O["exp"] = pd.to_datetime(O.expiration)
O = O.drop_duplicates(subset=["date", "expiration", "strike", "right"], keep="last")
h = pd.read_csv(MICRO / "out" / "td_gamma_TSLA.csv", parse_dates=["date"]).set_index("date"); ref = h.near_oi_share.iloc[-251:]
rows = {}
for d, x in O.groupby("date"):
    x = x[(x.exp >= d) & ((x.exp - d).dt.days <= 120)]; S = float(px[px.index < d].iloc[-1])
    near = x[((x.exp - d).dt.days <= 45) & x.strike.between(0.95 * S, 1.05 * S)]
    fri = d + pd.Timedelta(days=(4 - d.weekday()) % 7)
    share = near.open_interest.sum() / x.open_interest.sum()
    rows[str(d.date())] = {"weekday": d.strftime("%a"), "prior close": round(S, 2), "near share": round(float(share), 4), "near pct": round(float((ref < share).mean()), 2),
                           "near OI expiring by this Friday": round(float(near[near.exp <= fri].open_interest.sum() / near.open_interest.sum()), 2)}
res = {"(a) going into each day (OI files only)": rows}
hh = h.loc["2023-01-01":].copy(); hh["near_pct"] = hh.near_oi_share.rolling(252, min_periods=120).rank(pct=True)
gn = hh.gex_classic / (hh.spot * (hh.call_oi + hh.put_oi) * 100); hh["own_pct"] = gn.rolling(252, min_periods=120).rank(pct=True)
hh = hh.dropna(subset=["near_pct", "own_pct"]); hh["wd"] = hh.index.dayofweek
res["(b) engine 2023-Oct 2026, mean pct by weekday [near-OI pct, own-gamma pct, n]"] = {["Mon", "Tue", "Wed", "Thu", "Fri"][k]: [round(float(g.near_pct.mean()), 2), round(float(g.own_pct.mean()), 2), len(g)] for k, g in hh.groupby("wd")}
ret = px.pct_change().loc["2026-10-12":"2026-10-30"]
res["(c) TSLA daily returns %, Oct 12-30"] = {str(d.date()) + " " + d.strftime("%a"): round(100 * float(v), 2) for d, v in ret.items()}
wk = pd.DataFrame({"r": ret, "wk": ret.index.to_period("W"), "half": np.where(ret.index.dayofweek <= 2, "Mon-Wed", "Thu-Fri")})
res["(c) by week, compounded % [Mon-Wed, Thu-Fri]"] = {str(k.start_time.date()): [round(100 * float((1 + g[g.half == 'Mon-Wed'].r).prod() - 1), 1), round(100 * float((1 + g[g.half == 'Thu-Fri'].r).prod() - 1), 1)] for k, g in wk.groupby("wk")}
# (d) longer history: TSLA Mon-Wed vs Thu-Fri compounded returns per week, 2023-2026 (descriptive)
r2 = px.pct_change().loc["2023-01-01":"2026-10-30"]; w2 = pd.DataFrame({"r": r2, "wk": r2.index.to_period("W"), "h": np.where(r2.index.dayofweek <= 2, 0, 1)})
t = w2.groupby(["wk", "h"]).r.apply(lambda s: (1 + s).prod() - 1).unstack().dropna()
res["(d) 2023-26 weeks (n, mean Mon-Wed %, mean Thu-Fri %, share of weeks up-then-down)"] = [len(t), round(100 * float(t[0].mean()), 2), round(100 * float(t[1].mean()), 2), round(float(((t[0] > 0) & (t[1] < 0)).mean()), 2)]
up = t[t[0] > 0.05]
res["(d) weeks with Mon-Wed > +5%: n, mean Thu-Fri %, share Thu-Fri down"] = [len(up), round(100 * float(up[1].mean()), 2), round(float((up[1] < 0).mean()), 2)]
json.dump(res, open(HERE / "out" / "weekly_rhythm.json", "w"), indent=1); print(json.dumps(res, indent=1))
