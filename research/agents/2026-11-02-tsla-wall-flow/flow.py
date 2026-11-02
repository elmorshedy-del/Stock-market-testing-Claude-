"""Descriptive (not a pre-registered test): TSLA's Oct 26-27 burst vs every earlier 2-day burst (>= +7%) since 2020.
Aggressor proxy = bulk volume classification (Easley, Lopez de Prado & O'Hara 2012) on 1-minute bars: buy share of a bar =
Phi(dP / sigma), sigma = std of 1-minute price changes over the prior 5 sessions. Also: relative volume, how much of the move
came overnight (gaps) vs in-session, dip-buying in the 3-session consolidation, and what followed (snap vs slow).
Usage: python flow.py <TSLA 1m parquet> -> out/flow.json, out/bursts.csv"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
m = pd.read_parquet(sys.argv[1], columns=["open", "close", "volume"]); m.index = m.index.tz_convert("America/New_York")
m = m[(m.index.time >= pd.Timestamp("09:30").time()) & (m.index.time < pd.Timestamp("16:00").time())]
m["day"] = m.index.normalize().tz_localize(None); m["dp"] = m.groupby("day").close.diff()
sd = m.groupby("day").dp.std().shift(1).rolling(5, min_periods=3).mean()          # prior-5-session 1-minute sigma
m["sig"] = m.day.map(sd); m["buy"] = norm.cdf(m.dp / m.sig)
m["net"] = m.volume * (2 * m.buy - 1)
D = m.groupby("day").agg(o=("open", "first"), c=("close", "last"), v=("volume", "sum"), net=("net", "sum"))
D = D[D.v > 0].dropna(); D["ret"] = np.log(D.c / D.c.shift(1)); D["gap"] = np.log(D.o / D.c.shift(1)); D["intra"] = np.log(D.c / D.o)
D["rvol"] = D.v / D.v.rolling(20).mean().shift(1); D["imb"] = D.net / D.v
two = D.ret.rolling(2).sum()
cand = two[two >= np.log(1.07)].index; bursts = []; last = None
for d in cand:
    i = D.index.get_loc(d)
    if last is not None and i - last < 10: continue
    last = i; bursts.append(i)
rows = []
for i in bursts:
    if i < 22: continue
    b = D.iloc[i - 1:i + 1]; cons = D.iloc[i + 1:i + 4]; nxt = D.iloc[i + 4:i + 14]
    hi = b.c.max(); base = cons.c.iloc[-1] if len(cons) == 3 else np.nan
    r = {"date": D.index[i].date(), "burst %": 100 * (np.exp(b.ret.sum()) - 1), "gap share of move": b.gap.sum() / b.ret.sum(),
         "burst rel. volume": b.rvol.mean(), "burst buy imbalance %": 100 * b.net.sum() / b.v.sum(),
         "consolidation 3d %": 100 * (np.exp(cons.ret.sum()) - 1) if len(cons) == 3 else np.nan,
         "consolidation imbalance %": 100 * cons.net.sum() / cons.v.sum() if len(cons) == 3 else np.nan,
         "consolidation rel. volume": cons.rvol.mean() if len(cons) == 3 else np.nan}
    if len(nxt) == 10 and np.isfinite(base):
        path = nxt.c / base - 1
        r["next 10d max %"] = 100 * path.max(); r["next 10d end %"] = 100 * path.iloc[-1]
        above = np.nonzero((nxt.c > hi * 1.02).to_numpy())[0]
        r["days to clear burst high +2%"] = int(above[0]) + 1 if len(above) else np.nan
        r["snap (+5% within 3 days)"] = bool((path.iloc[:3] >= 0.05).any())
    rows.append(r)
B = pd.DataFrame(rows); B.to_csv(HERE / "out" / "bursts.csv", index=False)
cur = B[B.date == pd.Timestamp("2026-10-27").date()].iloc[0]; prev = B[B.date < pd.Timestamp("2026-10-27").date()]
cols = ["burst %", "gap share of move", "burst rel. volume", "burst buy imbalance %", "consolidation 3d %", "consolidation imbalance %", "consolidation rel. volume"]
res = {"n earlier bursts (2-day >= +7%, 2020-2026)": int(len(prev)),
       "this burst (Oct 26-27) vs earlier: value, percentile among earlier": {c: [round(float(cur[c]), 2), round(float((prev[c] < cur[c]).mean()), 2)] for c in cols},
       "earlier bursts: share that snapped (+5% within 3 days after the 3-day pause)": round(float(prev["snap (+5% within 3 days)"].mean()), 2),
       "earlier bursts: median days to clear the burst high +2% (NaN = not within 10)": float(prev["days to clear burst high +2%"].median()),
       "earlier bursts: share clearing the burst high +2% within 10 days": round(float(prev["days to clear burst high +2%"].notna().mean()), 2)}
# look-alikes: low gap share, consolidation held (>-3%) with buying (imbalance > 0)
for lab, msk in (("pause held with net buying (cons > -3%, cons imbalance > 0)", (prev["consolidation 3d %"] > -3) & (prev["consolidation imbalance %"] > 0)),
                 ("pause with net selling (cons imbalance <= 0)", prev["consolidation imbalance %"] <= 0),
                 ("high-aggression burst (imbalance above median)", prev["burst buy imbalance %"] > prev["burst buy imbalance %"].median()),
                 ("low-aggression burst (imbalance below median)", prev["burst buy imbalance %"] <= prev["burst buy imbalance %"].median())):
    P = prev[msk]
    res[f"after: {lab}"] = {"n": int(len(P)), "snap share": round(float(P["snap (+5% within 3 days)"].mean()), 2) if len(P) else None,
                            "median next-10d max %": round(float(P["next 10d max %"].median()), 1) if len(P) else None,
                            "median next-10d end %": round(float(P["next 10d end %"].median()), 1) if len(P) else None}
json.dump(res, open(HERE / "out" / "flow.json", "w"), indent=1, default=str)
print(json.dumps(res, indent=1, default=str))
print(B.round(2).tail(12).to_string())
