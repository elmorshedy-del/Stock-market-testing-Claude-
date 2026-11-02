"""S&P ladder (REPORT 4i rungs, same definitions as microstructure/ladder.py) on SqueezeMetrics through Fri Oct 30,
plus this week's switch-on lines and the R4 event history (lead to the leg, first-5-session path).
Usage: python ladder_now.py <DIX.csv> <^VIX daily json> -> out/ladder_now.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
g = pd.read_csv(sys.argv[1], parse_dates=["date"]).set_index("date")
r = json.load(open(sys.argv[2]))["chart"]["result"][0]
vix = pd.Series(r["indicators"]["quote"][0]["close"], index=pd.to_datetime(r["timestamp"], unit="s").normalize()).dropna()
f = g.rename(columns={"price": "c"}).join(vix.rename("VIX"), how="inner")
pct = lambda s: s.rolling(252).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True)
f["gex_pct"], f["dix_pct"] = pct(f.gex), pct(f.dix); f = f.dropna()
hi10, vmax10 = f.c.rolling(10).max(), f.VIX.rolling(10).max(); low_recent = f.gex_pct.rolling(15).min() <= 0.20
R = {"R1 GEX<=30th": f.gex_pct <= .30, "R2 GEX<=30th + DIX>50th": (f.gex_pct <= .30) & (f.dix_pct > .5), "R3 GEX<=20th": f.gex_pct <= .20,
     "R4 GEX<=20th + S&P 2% off 10d high": (f.gex_pct <= .20) & (f.c / hi10 - 1 <= -.02), "R5 R4 + DIX>50th": (f.gex_pct <= .20) & (f.c / hi10 - 1 <= -.02) & (f.dix_pct > .5),
     "R6 low GEX recently + VIX<=0.85x 10d max": low_recent & (f.VIX <= .85 * vmax10), "R7 low GEX recently + VIX<=0.75x 10d max": low_recent & (f.VIX <= .75 * vmax10)}
last = f.index[-1]; w = f.iloc[-252:]
out = {"day": str(last.date()), "SPX": round(float(f.c.iloc[-1]), 2), "VIX": round(float(f.VIX.iloc[-1]), 2),
       "GEX $bn / pct": [round(float(f.gex.iloc[-1] / 1e9), 2), round(float(f.gex_pct.iloc[-1]), 3)], "DIX / pct": [round(float(f.dix.iloc[-1]), 4), round(float(f.dix_pct.iloc[-1]), 3)],
       "rungs on (Fri close)": {k: bool(v.iloc[-1]) for k, v in R.items()},
       "first day on (current episode)": {k: (str(v[v & ~v.shift(1, fill_value=False)].index[-1].date()) if v.iloc[-1] else None) for k, v in R.items()},
       "lines (1-year distributions to Oct 30)": {"GEX 20th pct $bn": round(float(np.quantile(w.gex.iloc[:-1], .20) / 1e9), 2), "GEX 30th pct $bn": round(float(np.quantile(w.gex.iloc[:-1], .30) / 1e9), 2),
                                                 "DIX 50th pct": round(float(np.quantile(w.dix.iloc[:-1], .50)), 4)},
       "GEX pct last 15 sessions min": round(float(f.gex_pct.iloc[-15:].min()), 3)}
# this week's rolling lines: closes/VIX of the 9 prior sessions stay in the window
c9, v9 = list(f.c.iloc[-9:]), list(f.VIX.iloc[-9:]); days = ["Mon Nov 2", "Tue Nov 3", "Wed Nov 4", "Thu Nov 5", "Fri Nov 6"]; lines = {}
for k, d in enumerate(days):
    win_c = c9[k:]; win_v = v9[k:]                      # assume this week's closes stay below the window high / VIX below its max
    lines[d] = {"S&P 10d high (from prior sessions)": round(max(win_c), 2), "R4 needs S&P close <=": round(.98 * max(win_c), 2),
                "VIX 10d max (prior sessions)": round(max(win_v), 2), "R6 needs VIX <=": round(.85 * max(win_v), 2), "R7 needs VIX <=": round(.75 * max(win_v), 2)}
out["this week's lines (if no new 10d high / VIX max)"] = lines
# R4 / R5 / R6 event history: lead to the up-leg, the first 5 sessions
c = f.c.to_numpy(); fwd10 = np.r_[np.log(c[10:] / c[:-10]), np.full(10, np.nan)]; top = np.nanquantile(fwd10, .9)
def events(m):
    on = m & ~m.shift(1, fill_value=False); ev, lastj = [], -99
    for j in np.where(on.to_numpy())[0]:
        if j - lastj >= 10 and j + 21 < len(c): ev.append(j); lastj = j
    return ev
hist = {}
for k in ["R4 GEX<=20th + S&P 2% off 10d high", "R5 R4 + DIX>50th", "R6 low GEX recently + VIX<=0.85x 10d max"]:
    rows = []
    for j in events(R[k]):
        ww = fwd10[j + 1:j + 21]; leg = np.where(ww > top)[0]
        rows.append({"date": f.index[j], "leg": leg.size > 0, "lead": (leg[0] + 1) if leg.size else np.nan, "r5": c[j + 5] / c[j] - 1, "r20": c[j + 20] / c[j] - 1,
                     "low5": c[j:j + 6].min() / c[j] - 1, "low20": c[j:j + 21].min() / c[j] - 1, "high5": c[j:j + 6].max() / c[j] - 1})
    e = pd.DataFrame(rows)
    def summ(x): return {"n": len(x), "P(leg <= 20)": round(float(x.leg.mean()), 2), "P(leg starts <= 5 sessions)": round(float((x.lead <= 5).mean()), 2),
                         "median lead": float(x.lead.median()), "5-session return median %": round(100 * float(x.r5.median()), 2), "P(up after 5)": round(float((x.r5 > 0).mean()), 2),
                         "5-session low median %": round(100 * float(x.low5.median()), 2), "5-session high median %": round(100 * float(x.high5.median()), 2),
                         "20-session return median %": round(100 * float(x.r20.median()), 2), "20-session worst median %": round(100 * float(x.low20.median()), 2)}
    hist[k] = {"2012-26": summ(e[e.date >= "2012-01-01"]), "2019Q4-26": summ(e[e.date >= "2019-10-01"]), "2022+": summ(e[e.date >= "2022-01-01"]),
               "last 6 events": [str(d.date()) for d in e.date.iloc[-6:]]}
out["event history"] = hist
any_lead = [];
for j in range(len(c) - 21):
    ww = fwd10[j + 1:j + 21]; leg = np.where(ww > top)[0]; any_lead.append((leg[0] + 1) if leg.size else np.nan)
al = pd.Series(any_lead, index=f.index[:len(any_lead)])
out["any day"] = {era: {"P(leg <= 20)": round(float(al[al.index >= s].notna().mean()), 2), "P(leg starts <= 5)": round(float((al[al.index >= s] <= 5).mean()), 2)} for era, s in [("2012-26", "2012-01-01"), ("2019Q4-26", "2019-10-01"), ("2022+", "2022-01-01")]}
json.dump(out, open(HERE / "out" / "ladder_now.json", "w"), indent=1, default=str); print(json.dumps(out, indent=1, default=str))
