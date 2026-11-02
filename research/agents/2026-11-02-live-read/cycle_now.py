"""Where the S&P gamma cycle stands (REPORT 4d/4p definitions, as in microstructure/reset.py) and this week's lines:
'ran' = GEX pct up >= 0.50 from its 7-day low while the S&P 7-session log return is in [-1%, +2.5%] (gamma rebuilt without price).
History: after R4 first days, P(up-leg within 20 sessions) split by whether 'ran' fired in the next 7 sessions, and 'ran' overall.
Usage: python cycle_now.py <DIX.csv> <^VIX json> -> out/cycle_now.json"""
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
lc = np.log(f.c); fwd10 = lc.shift(-10) - lc; top = fwd10.quantile(0.9); legday = fwd10 > top
f["leg20"] = [bool(legday.iloc[i + 1:i + 21].any()) if i + 21 <= len(f) else np.nan for i in range(len(f))]
f["rise7"] = f.gex_pct - f.gex_pct.rolling(7).min(); f["ret7"] = lc - lc.shift(7)
f["ran"] = (f.rise7 >= 0.5) & f.ret7.between(-0.01, 0.025); f["ran_up"] = (f.rise7 >= 0.5) & (f.ret7 > 0.025)
hi10 = f.c.rolling(10).max(); r4 = (f.gex_pct <= .20) & (f.c / hi10 - 1 <= -.02)
w = f.iloc[-252:]; out = {}
out["GEX pct, last 12 sessions"] = {str(d.date()): [round(float(x.gex / 1e9), 2), round(float(x.gex_pct), 3)] for d, x in f.tail(12).iterrows()}
q = lambda p: round(float(np.quantile(w.gex.iloc[:-1], p) / 1e9), 2)
out["GEX $bn at pct 0.30 / 0.50 / 0.56 / 0.70 / 0.90"] = [q(.30), q(.50), q(.56), q(.70), q(.90)]
c = f.c; days = ["Mon Nov 2", "Tue Nov 3", "Wed Nov 4", "Thu Nov 5", "Fri Nov 6"]; lines = {}
for k, d in enumerate(days):
    base = float(c.iloc[-7 + k]); mn = float(f.gex_pct.iloc[-6 + k:].min())   # prior 6 sessions in window (+ the day itself, assumed not lower)
    lines[d] = {"7-session-ago S&P": round(base, 2), "'no price' band for the S&P close": [round(base * np.exp(-0.01), 1), round(base * np.exp(0.025), 1)],
                "GEX pct needed (7-day low + 0.50)": round(mn + 0.5, 3), "≈ GEX $bn needed": round(float(np.quantile(w.gex.iloc[:-1], min(mn + 0.5, 0.999)) / 1e9), 2)}
out["this week's 'ran' lines"] = lines
def first(m, gap=10):
    on = m & ~m.shift(1, fill_value=False); idx, last = [], -99
    for i in np.where(on.to_numpy())[0]:
        if i - last >= gap: idx.append(i); last = i
    return idx
hist = {}
for era, s in [("2012-26", "2012-01-01"), ("2019Q4-26", "2019-10-01")]:
    x = f[f.index >= s]; base = float(x.leg20.dropna().mean())
    ran_ev = [i for i in first(x.ran) if not np.isnan(x.leg20.iloc[i])]
    r4_ev = [i for i in first(r4.loc[x.index]) if i + 28 < len(x)]
    with_ran = [i for i in r4_ev if x.ran.iloc[i + 1:i + 8].any()]; without = [i for i in r4_ev if i not in with_ran]
    hist[era] = {"any day P(leg within 20)": round(base, 2),
                 "'ran' first days: n, P(leg within 20)": [len(ran_ev), round(float(x.leg20.iloc[ran_ev].mean()), 2)],
                 "R4 first days: n": len(r4_ev),
                 "R4 then 'ran' within 7 sessions: n, P(leg within 20 of R4)": [len(with_ran), round(float(x.leg20.iloc[with_ran].mean()), 2) if with_ran else None],
                 "R4 without 'ran': n, P(leg within 20 of R4)": [len(without), round(float(x.leg20.iloc[without].mean()), 2) if without else None],
                 "R4 then gamma rebuilt WITH price (rise >= 0.5, S&P 7d > +2.5%) within 7: n": sum(bool(x.ran_up.iloc[i + 1:i + 8].any()) for i in r4_ev)}
out["history"] = hist
json.dump(out, open(HERE / "out" / "cycle_now.json", "w"), indent=1); print(json.dumps(out, indent=1))
