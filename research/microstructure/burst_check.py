"""Event-level check: did the ladder conditions precede a stock's 1-2 day bursts,
and how often did they fire with no burst (false positives)?

Burst day: 1-day return >= +5% or 2-day return >= +9% (days within 3 sessions
are one burst; the burst is dated by its first day). A signal "catches" a burst
if its first-on day falls 1..LOOKBACK trading days before the burst.
Precision = share of signal firings followed by a burst within LOOKBACK days,
compared with the same rate for every day (the base rate).
Usage: python burst_check.py TSLA 2024-01-01
"""
import sys

import numpy as np
import pandas as pd

import ladder as LD
from single_name import frames

LOOKBACK = 10
WINDOWS = [("2024-06-01", "2024-07-31"), ("2025-04-15", "2025-05-31"),
           ("2025-09-01", "2025-09-30"), ("2025-10-01", "2025-11-30")]


def bursts(t):
    r = np.log(t.c).diff()
    r2 = np.log(t.c / t.c.shift(2))
    hit = ((r >= 0.05) | (r2 >= 0.09)).to_numpy()
    days, last = [], -99
    for i in np.where(hit)[0]:
        # date a 2-day burst by its first day
        j = i - 1 if (r2.iloc[i] >= 0.09 and r.iloc[i] < 0.05) else i
        if j - last > 3:
            days.append(j)
        last = i
    return np.array(days), r, r2


def signals(f, t, sym):
    rungs = LD.rungs(f)
    hi10 = t.c.rolling(10).max()
    r4s = (f.gex_pct <= 0.20) & (t.c / hi10 - 1 <= -0.05)
    rungs[f"R4s GEX<=0.20 + {sym} 5% dip"] = r4s
    rungs["R5s R4s + DIX>0.5"] = r4s & (f.dix_pct > 0.5)
    return {k: LD.first_on(v.fillna(False)) for k, v in rungs.items()}


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    sym = (sys.argv[1:] or ["TSLA"])[0]
    start = (sys.argv[2:] or ["2024-01-01"])[0]
    f, t = frames(sym)
    b, r, r2 = bursts(t)
    sig = signals(f, t, sym)
    idx = t.index
    s0 = idx.searchsorted(pd.Timestamp(start))
    b = b[b >= s0]
    print(f"{sym} bursts since {start}: {len(b)}")
    rows = []
    for i in b:
        on = [k.split()[0] for k, v in sig.items() if v[max(0, i - LOOKBACK):i].any()]
        rows.append({"burst_day": idx[i].date(), "1d%": round(100 * r.iloc[i], 1),
                     "2d%": round(100 * np.log(t.c.iloc[min(i + 1, len(t) - 1)] / t.c.iloc[i - 1]), 1),
                     "SPX_GEX_pct_day-1": round(f.gex_pct.iloc[i - 1], 2), "DIX_pct_day-1": round(f.dix_pct.iloc[i - 1], 2),
                     "VIX_day-1": round(f.VIX.iloc[i - 1], 1), "signals_fired_in_prior_10d": ",".join(on) or "-"})
    tab = pd.DataFrame(rows)
    in_win = tab.burst_day.apply(lambda d: any(pd.Timestamp(a) <= pd.Timestamp(d) <= pd.Timestamp(z) for a, z in WINDOWS))
    print("\nbursts inside the asked windows:\n" + tab[in_win].to_string(index=False))
    print("\nother bursts:\n" + tab[~in_win].to_string(index=False))
    # precision / recall per signal since start
    bmask = np.zeros(len(t), bool)
    bmask[b] = True
    follow = np.array([bmask[i + 1:i + 1 + LOOKBACK].any() for i in range(len(t))])
    base = follow[s0:len(t) - LOOKBACK].mean()
    print(f"\nbase rate: any day is followed by a burst within {LOOKBACK} days {base:.0%} of the time")
    out = []
    for k, v in sig.items():
        fires = np.where(v[s0:len(t) - LOOKBACK])[0] + s0
        caught = sum(any(v[max(0, i - LOOKBACK):i]) for i in b)
        hits = follow[fires]
        out.append({"signal": k, "fired": len(fires), "followed_by_burst": int(hits.sum()),
                    "false_positives": int((~hits).sum()), "precision": hits.mean() if len(fires) else np.nan,
                    "bursts_caught": f"{caught}/{len(b)}",
                    "false_positive_dates": ", ".join(str(idx[i].date()) for i in fires[~hits])})
    print(pd.DataFrame(out).to_string(index=False, float_format=lambda v: f"{v:.0%}"))
