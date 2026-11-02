"""The week after past ladder events, in the same terms as today's forecasts: S&P intraday high/low and close over the
next 1 and 5 sessions after R4 (and R5 / R6) first days, in % from the event close; TSLA over the same windows.
Levels are SPY's, translated to % from Friday's close 755.72 (SPY/SPX move ~1:1). Usage: python ladder_week.py <DIX.csv> <^VIX json> <GSPC_long json> <TSLA json>"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
def yf(p, cols=("open", "high", "low", "close")):
    r = json.load(open(p))["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    d = pd.DataFrame({c: q[c] for c in cols}, index=pd.to_datetime(r["timestamp"], unit="s").normalize()); return d[~d.index.duplicated(keep="last")].dropna()
g = pd.read_csv(sys.argv[1], parse_dates=["date"]).set_index("date"); vix = yf(sys.argv[2])["close"]
f = g.rename(columns={"price": "c"}).join(vix.rename("VIX"), how="inner")
pct = lambda s: s.rolling(252).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True)
f["gex_pct"], f["dix_pct"] = pct(f.gex), pct(f.dix); f = f.dropna()
hi10, vmax10 = f.c.rolling(10).max(), f.VIX.rolling(10).max(); low_recent = f.gex_pct.rolling(15).min() <= 0.20
R = {"R4": (f.gex_pct <= .20) & (f.c / hi10 - 1 <= -.02), "R5": (f.gex_pct <= .20) & (f.c / hi10 - 1 <= -.02) & (f.dix_pct > .5), "R6": low_recent & (f.VIX <= .85 * vmax10)}
spx = yf(sys.argv[3]); ts = yf(sys.argv[4])["close"]
SPOT = 755.72; LV = {"hits flip 766.4": 766.43 / SPOT - 1, "hits 774": 774 / SPOT - 1, "hits put wall 750": 750 / SPOT - 1, "hits pocket floor 743.6": 743.63 / SPOT - 1}
TL = {"TSLA hits 420": 420 / 399.81 - 1, "TSLA hits 380": 380 / 399.81 - 1}
def events(m):
    on = m & ~m.shift(1, fill_value=False); ev, lastj = [], None
    for d in on[on].index:
        if lastj is None or f.index.get_loc(d) - f.index.get_loc(lastj) >= 10: ev.append(d); lastj = d
    return ev
out = {}
for k, m in R.items():
    rows = []
    for d in events(m):
        i = spx.index.searchsorted(d)
        if i + 5 >= len(spx) or spx.index[i] != d: continue
        c0 = spx.close.iloc[i]; nx = spx.iloc[i + 1:i + 6]; d1 = spx.iloc[i + 1]
        row = {"date": d, "d1 close": d1.close / c0 - 1, "wk close": nx.close.iloc[-1] / c0 - 1, "wk high": nx.high.max() / c0 - 1, "wk low": nx.low.min() / c0 - 1}
        j = ts.index.searchsorted(d)
        if j + 5 < len(ts) and ts.index[j] == d:
            row["tsla wk close"] = ts.iloc[j + 5] / ts.iloc[j] - 1; row["tsla d1"] = ts.iloc[j + 1] / ts.iloc[j] - 1
            row["tsla wk max close"] = ts.iloc[j + 1:j + 6].max() / ts.iloc[j] - 1; row["tsla wk min close"] = ts.iloc[j + 1:j + 6].min() / ts.iloc[j] - 1
        rows.append(row)
    e = pd.DataFrame(rows)
    res = {}
    for era, s in [("2012-26", "2012-01-01"), ("2019Q4-26", "2019-10-01"), ("2022+", "2022-01-01")]:
        x = e[e.date >= s]
        r = {"n": len(x), "next day up": round(float((x["d1 close"] > 0).mean()), 2), "week close up": round(float((x["wk close"] > 0).mean()), 2),
             "week close median %": round(100 * float(x["wk close"].median()), 2), "week close >= flip (+1.42%)": round(float((x["wk close"] >= LV["hits flip 766.4"]).mean()), 2)}
        for lab, L in LV.items(): r[lab] = round(float(((x["wk high"] >= L) if L > 0 else (x["wk low"] <= L)).mean()), 2)
        t = x.dropna(subset=["tsla wk close"])
        r.update({"TSLA n": len(t), "TSLA next day up": round(float((t["tsla d1"] > 0).mean()), 2), "TSLA week close up": round(float((t["tsla wk close"] > 0).mean()), 2),
                  "TSLA week median %": round(100 * float(t["tsla wk close"].median()), 2),
                  "TSLA closes >= 420 at some point (+5.05%)": round(float((t["tsla wk max close"] >= TL["TSLA hits 420"]).mean()), 2),
                  "TSLA closes <= 380 at some point (-4.96%)": round(float((t["tsla wk min close"] <= TL["TSLA hits 380"]).mean()), 2)})
        res[era] = r
    out[k + " first days"] = res
json.dump(out, open(HERE / "out" / "ladder_week.json", "w"), indent=1); print(json.dumps(out, indent=1))
