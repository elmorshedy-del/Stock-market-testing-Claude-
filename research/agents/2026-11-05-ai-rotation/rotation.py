"""AI/chip rotation map (descriptive live read, not a test): SMH / RSP ratio since 2004, past drawdown episodes of the ratio,
where the current episode sits, and what followed the biggest one-day rotation days. Usage: python rotation.py -> out/rotation.json"""
import datetime as dt
import json
import sys
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE.parent / "2026-11-05-liquidity-cycle")); from common import yahoo   # noqa: E402


def live(sym):
    u = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=1d&interval=1m"
    m = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=20))["chart"]["result"][0]["meta"]
    return float(m["regularMarketPrice"]), dt.datetime.utcfromtimestamp(m["regularMarketTime"]) - dt.timedelta(hours=5)


px = {s: yahoo(s, "2004-01-01").close for s in ("SMH", "RSP", "SPY")}
today = pd.Timestamp(dt.date.today()); lv = {s: live(s) for s in px}
for s in px:
    px[s] = px[s][px[s].index < today]; px[s].loc[today] = lv[s][0]
R = (px["SMH"] / px["RSP"]).dropna(); R2 = (px["SMH"] / px["SPY"]).dropna()
dd = R / R.cummax() - 1
# episodes: ratio drawdown from its running high reaching >= 15%; peak = last high before it, trough = min before a new high
eps, i, n = [], 0, len(R)
hi_i = 0
while i < n:
    if R.iloc[i] >= R.iloc[hi_i]: hi_i = i
    if dd.iloc[i] <= -0.15:
        j = i
        while j < n and R.iloc[j] < R.iloc[hi_i]: j += 1
        seg = R.iloc[hi_i:j]; t_i = hi_i + int(np.argmin(seg.values))
        eps.append({"peak": str(R.index[hi_i].date()), "trough": str(R.index[t_i].date()), "depth %": round(100 * (R.iloc[t_i] / R.iloc[hi_i] - 1), 1),
                    "sessions peak->trough": int(t_i - hi_i), "recovered": bool(j < n), "sessions to new high": int(j - hi_i) if j < n else None,
                    "_hi": hi_i, "_tr": t_i})
        i = j; hi_i = j if j < n else hi_i
    i += 1
cur = eps[-1] if not eps[-1]["recovered"] else None
pk = R.cummax().iloc[-1]; pk_i = int(np.where(R.values == pk)[0][-1]); now_dd = float(R.iloc[-1] / pk - 1); age = n - 1 - pk_i
past = [e for e in eps if e["recovered"]]
deeper = [e for e in past if e["depth %"] <= 100 * now_dd]
res = {"as of": f"{lv['SMH'][1]:%Y-%m-%d %H:%M} ET (live Yahoo)", "SMH / RSP ratio now vs its peak": {"peak date": str(R.index[pk_i].date()), "drawdown %": round(100 * now_dd, 1), "sessions since peak": int(age)},
       "today's one-day ratio move %": round(float(100 * (R.iloc[-1] / R.iloc[-2] - 1)), 2),
       "past episodes (ratio -15% or more), all": [{k: v for k, v in e.items() if not k.startswith("_")} for e in eps],
       "past completed episodes": len(past),
       "of those, reached at least today's depth": len(deeper),
       "their final depth % (median, range)": [float(np.median([e["depth %"] for e in deeper])), [float(min(e["depth %"] for e in deeper)), float(max(e["depth %"] for e in deeper))]] if deeper else None,
       "their sessions peak->trough (median, range)": [float(np.median([e["sessions peak->trough"] for e in deeper])), [int(min(e["sessions peak->trough"] for e in deeper)), int(max(e["sessions peak->trough"] for e in deeper))]] if deeper else None}
# extra downside from today's depth in those episodes, in ratio terms
if deeper:
    extra = [100 * ((1 + e["depth %"] / 100) / (1 + now_dd) - 1) for e in deeper]
    res["further ratio drop from here in those episodes % (median, 25-75%)"] = [round(float(np.median(extra)), 1), [round(float(np.quantile(extra, .25)), 1), round(float(np.quantile(extra, .75)), 1)]]
    res["share of those episodes whose trough was within 5% of today's depth"] = round(float(np.mean([x >= -5 for x in extra])), 2)
# biggest one-day rotation days (ratio down), what followed
r1 = np.log(R).diff(); thr = r1.iloc[:-1].quantile(0.01)
big = r1[(r1 <= thr)].index[:-1] if r1.index[-1] in r1[(r1 <= thr)].index else r1[(r1 <= thr)].index
fw = lambda d, k: float(np.log(R.shift(-k) / R).loc[d])
rows = [(d, fw(d, 5), fw(d, 20)) for d in big if R.index.get_loc(d) + 20 < n]
res["after top-1% one-day rotation drops (ratio), excl today"] = {"days": len(rows), "threshold %": round(float(100 * thr), 2),
    "next 5 sessions ratio median % / share up": [round(float(100 * np.median([x[1] for x in rows])), 2), round(float(np.mean([x[1] > 0 for x in rows])), 2)],
    "next 20 sessions ratio median % / share up": [round(float(100 * np.median([x[2] for x in rows])), 2), round(float(np.mean([x[2] > 0 for x in rows])), 2)]}
pd.DataFrame({"ratio": R, "dd": dd}).to_csv(HERE / "out" / "ratio.csv")
json.dump(res, open(HERE / "out" / "rotation.json", "w"), indent=1, default=str); print(json.dumps(res, indent=1, default=str))
