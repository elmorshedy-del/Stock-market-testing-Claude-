"""Part R: SPY RSI(14) (Wilder) on 1h, 4h, daily, weekly, monthly bars + trailing percentiles, the 1-ATR bounce level,
and daily bullish-divergence state. Usage: python rsi.py <dir with SPY_60m/1d/1wk/1mo.json> -> out/rsi.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; Y = Path(sys.argv[1])


def bars(iv):
    r = json.load(open(Y / f"SPY_{iv}.json"))["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    b = pd.DataFrame({k: q[k] for k in ("open", "high", "low", "close")}, index=pd.to_datetime(r["timestamp"], unit="s", utc=True).tz_convert("America/New_York")).dropna()
    return b[~b.index.duplicated(keep="last")]


def rsi(c, n=14):
    d = c.diff(); up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean(); dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn)


out = {}
h = bars("60m"); h = h[(h.index.time >= pd.Timestamp("09:30").time()) & (h.index.time < pd.Timestamp("16:00").time())]
h4 = h.close.groupby([h.index.date, (h.index.hour * 60 + h.index.minute - 570) // 240]).last()   # two 4-hour blocks per session (09:30-13:30, 13:30-16:00)
frames = {"1-hour": h.close, "4-hour": pd.Series(h4.values), "daily": bars("1d").close, "weekly": bars("1wk").close, "monthly": bars("1mo").close}
look = {"1-hour": 1638, "4-hour": 504, "daily": 252 * 5, "weekly": 260, "monthly": 240}
for k, c in frames.items():
    r = rsi(c).dropna(); w = r.iloc[-look[k]:]
    out[k] = {"RSI": round(float(r.iloc[-1]), 1), "trailing pct": round(float((w < r.iloc[-1]).mean()), 3), "window bars": int(len(w)),
              "last 6": [round(float(x), 1) for x in r.iloc[-6:]], "classic zone": "oversold <30" if r.iloc[-1] < 30 else "overbought >70" if r.iloc[-1] > 70 else "neutral"}
# weekly RSI third (sp-multivariate reading uses trailing 260-week percentile)
wk = rsi(bars("1wk").close).dropna(); p = float((wk.iloc[-260:] < wk.iloc[-1]).mean())
out["weekly RSI third (sp-multivariate)"] = "weakest third" if p < 1 / 3 else "strongest third" if p > 2 / 3 else "middle third"
# 1-ATR bounce level and divergence on daily bars
d = bars("1d"); tr = pd.concat([d.high - d.low, (d.high - d.close.shift()).abs(), (d.low - d.close.shift()).abs()], axis=1).max(axis=1)
atr = tr.ewm(alpha=1 / 14, adjust=False).mean(); low20 = d.close.rolling(20).min()
i_low = d.close.iloc[-20:].idxmin()
out["daily"]["20-session closing low"] = {"date": str(i_low.date()), "close": round(float(d.close.loc[i_low]), 2)}
out["daily"]["ATR14"] = round(float(atr.iloc[-1]), 2)
out["daily"]["1-ATR bounce trigger (close at or above)"] = round(float(d.close.loc[i_low] + atr.iloc[-1]), 2)
out["daily"]["Friday close"] = round(float(d.close.iloc[-1]), 2)
dr = rsi(d.close)
prev = d.close.iloc[-30:-5]; j = prev.idxmin()
out["daily"]["bullish divergence"] = {"earlier 20d-type low": str(j.date()), "earlier close": round(float(prev.min()), 2), "earlier RSI": round(float(dr.loc[j]), 1),
                                      "now close": round(float(d.close.iloc[-1]), 2), "now RSI": round(float(dr.iloc[-1]), 1),
                                      "on": bool(d.close.iloc[-1] < prev.min() and dr.iloc[-1] > dr.loc[j])}
out["daily"]["SPY vs 50/100/200-day avg %"] = {w: round(float((d.close.iloc[-1] / d.close.rolling(w).mean().iloc[-1] - 1) * 100), 2) for w in (50, 100, 200)}
json.dump(out, open(HERE / "out" / "rsi.json", "w"), indent=1)
print(json.dumps(out, indent=1))
