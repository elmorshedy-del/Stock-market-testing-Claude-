"""Unwind-low signature (pre-registered @ 52c1460). Usage: python unwind.py <DIX.csv> -> out/unwind.json"""
import datetime as dt
import json
import sys
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE.parent / "2026-11-05-liquidity-cycle")); from common import yahoo   # noqa: E402
rng = np.random.default_rng(0)


def live(sym):
    u = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym.replace('^', '%5E')}?range=1d&interval=1m"
    m = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=20))["chart"]["result"][0]["meta"]
    return float(m["regularMarketPrice"]), dt.datetime.utcfromtimestamp(m["regularMarketTime"]) - dt.timedelta(hours=5)


S = {"SMH": "SMH", "RSP": "RSP", "VIX": "^VIX", "HYG": "HYG", "IEF": "IEF"}
px = {}; today = pd.Timestamp(dt.date.today()); stamp = None
for k, s in S.items():
    c = yahoo(s.replace("^", "%5E"), "2004-01-01").close; c = c[c.index < today]; p, t = live(s); c.loc[today] = p; px[k] = c; stamp = stamp or t
f = pd.DataFrame(px).dropna()
R = f.SMH / f.RSP; r1 = np.log(R).diff()
f["D"] = R / R.rolling(252, min_periods=200).max() - 1 <= -0.25
q02 = r1.rolling(1000, min_periods=500).apply(lambda w: np.quantile(w[:-1], 0.02), raw=True)
f["V"] = r1 <= q02
f["B"] = (f.RSP.pct_change() >= -0.01) & (f.SMH.pct_change() <= -0.03)
f["F"] = (f.VIX.pct_change() <= 0.10) & (f.VIX <= 25)
f["C"] = (f.HYG / f.IEF).pct_change() >= -0.003
f["core"] = f.D & f.V & f.B; f["full"] = f.core & f.F & f.C
n = len(f); lr = np.log(R.to_numpy()); ls = np.log(f.SMH.to_numpy())
fw = lambda x, k: np.r_[x[k:] - x[:-k], np.full(k, np.nan)] * 100
O = {"ratio fwd 5": fw(lr, 5), "ratio fwd 10": fw(lr, 10), "SMH fwd 5": fw(ls, 5), "SMH fwd 10": fw(ls, 10)}
low = np.array([(R.iloc[i] <= 1.02 * R.iloc[max(0, i - 10):min(n, i + 11)].min()) if i + 10 < n else np.nan for i in range(n)], float)


def episodes(mask):
    idx = np.where(mask.to_numpy())[0]; out, last = [], -99
    for i in idx:
        if i - last > 5: out.append(i)
        last = i
    return np.array(out, int)


res = {"as of": f"{stamp:%Y-%m-%d %H:%M} ET (today's row is LIVE intraday, provisional)", "days": n, "span": [str(f.index[0].date()), str(f.index[-1].date())]}
deep = f.D.to_numpy()
for lab in ("core", "full"):
    ep = episodes(f[lab]); ep = ep[ep < n - 10]
    blk = {"episodes (completed)": int(len(ep)), "dates": [str(f.index[i].date()) for i in ep]}
    for nm, y in O.items():
        blk[nm] = {"event mean": round(float(np.nanmean(y[ep])), 2) if len(ep) else None, "share > 0": round(float(np.nanmean(y[ep] > 0)), 2) if len(ep) else None,
                   "deep-rotation days mean": round(float(np.nanmean(y[deep])), 2), "all days mean": round(float(np.nanmean(y)), 2)}
    blk["low marker share (within 2% of the t-10..t+10 min)"] = [round(float(np.nanmean(low[ep])), 2) if len(ep) else None, "deep days " + str(round(float(np.nanmean(low[deep])), 2))]
    # null: circular shift of the event indicator, statistic = mean ratio fwd 10 at episodes minus deep-day baseline
    y = O["ratio fwd 10"]; stat = np.nanmean(y[ep]) - np.nanmean(y[deep]) if len(ep) else np.nan; nul = []
    ev = np.zeros(n, bool); ev[ep] = True
    for _ in range(5000):
        s = rng.integers(60, n - 60); e2 = np.where(np.roll(ev, s))[0]; e2 = e2[e2 < n - 10]
        nul.append(np.nanmean(y[e2]) - np.nanmean(y[deep]) if len(e2) else np.nan)
    nul = np.array(nul); p = float(np.nanmean(nul >= stat)) if len(ep) else np.nan
    blk["ratio fwd 10 vs deep baseline"] = {"diff": round(float(stat), 2) if len(ep) else None, "p (one-sided, circular shift)": round(p, 4) if len(ep) else None,
                                            "PASS (p<0.05 and >=8 episodes)": bool(len(ep) >= 8 and p < 0.05)}
    res[lab] = blk
for d in ["2026-07-27", "2026-07-28", "2026-07-29", "2026-07-30", "2026-07-31"]:
    if pd.Timestamp(d) in f.index:
        r = f.loc[d]; res.setdefault("July check", {})[d] = {k: bool(r[k]) for k in ("D", "V", "B", "F", "C")} | {"ratio dd %": round(float(100 * (R.loc[d] / R.rolling(252, min_periods=200).max().loc[d] - 1)), 1), "ratio 1d %": round(float(100 * r1.loc[d]), 2)}
t = f.iloc[-1]
res["TODAY (live, provisional)"] = {k: bool(t[k]) for k in ("D", "V", "B", "F", "C", "core", "full")} | {"ratio dd %": round(float(100 * (R.iloc[-1] / R.rolling(252, min_periods=200).max().iloc[-1] - 1)), 1),
    "ratio 1d %": round(float(100 * r1.iloc[-1]), 2), "RSP 1d %": round(float(100 * f.RSP.pct_change().iloc[-1]), 2), "SMH 1d %": round(float(100 * f.SMH.pct_change().iloc[-1]), 2),
    "VIX 1d %": round(float(100 * f.VIX.pct_change().iloc[-1]), 1), "HYG/IEF 1d %": round(float(100 * (f.HYG / f.IEF).pct_change().iloc[-1]), 2)}
json.dump(res, open(HERE / "out" / "unwind.json", "w"), indent=1, default=str); print(json.dumps(res, indent=1, default=str))
