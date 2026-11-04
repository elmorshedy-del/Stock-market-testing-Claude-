"""MSFT live read, Wed Nov 4 (a map + state check, not a test).
(1) Gamma map: OI dated Nov 4 (Tue close positions) + Tue Nov 3 closing chains, engine imported unchanged (flip-wicks flipmap).
(2) Burst conditions already on file: REPORT §4aa release setup (MSFT 20-day lead vs SPY in its top third AND SqueezeMetrics
    S&P GEX in its bottom third, trailing 252 days) and §4c July pattern (~30% drawdown, falling vol, forced-flow date).
Usage: python msft_read.py <td dir> <DIX.csv> <live MSFT> -> out/msft_read.json"""
import json
import sys
import urllib.request
import datetime as dt
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent / "2026-10-27-flip-wicks")]
from flipmap import norm, preopen, fine_flip, gex_at, exposures   # noqa: E402

td, dixf, S = Path(sys.argv[1]), sys.argv[2], float(sys.argv[3]); P, D = pd.Timestamp("2026-11-03"), pd.Timestamp("2026-11-04")
e = norm(pd.read_csv(td / "MSFT_eod_20261103.csv.gz")); e = e[e.date == P]; o = norm(pd.read_csv(td / "MSFT_oi_20261104.csv.gz"))
g = preopen(e, o, D); g["underlying_close"] = S
grid = np.arange(440, 640.5, 0.5); tot = np.array([gex_at(g, s) for s in grid]) / 1e9
k45 = g[((g.expiration - D).dt.days <= 45) & g.K.between(0.75 * S, 1.25 * S)]
ex = exposures(g, S); byk = ex.groupby("K").gex.sum() / 1e9; near = byk[(byk.index >= 0.92 * S) & (byk.index <= 1.08 * S)]
oi_k = k45.groupby(["K", "cp"]).oi.sum().unstack().fillna(0)
i0 = int(np.argmin(tot)); neg = grid[tot < 0]
exp_share = (exposures(g, S).assign(exp=g.expiration.values).groupby("exp").gex.apply(lambda x: x.abs().sum()) / ex.gex.abs().sum()).sort_values(ascending=False).head(4)
out = {"ref price": S, "flip": round(fine_flip(g, S), 2),
       "call wall (max call OI, <=45d)": float(oi_k.C.idxmax()), "put wall (max put OI, <=45d)": float(oi_k.P.idxmax()),
       "top call OI strikes <=45d": {f"{k:g}": int(v) for k, v in oi_k.C.sort_values(ascending=False).head(5).items()},
       "top put OI strikes <=45d": {f"{k:g}": int(v) for k, v in oi_k.P.sort_values(ascending=False).head(5).items()},
       "total gamma $bn/1% at": {f"{s:g}": round(float(np.interp(s, grid, tot)), 3) for s in range(480, 621, 10)},
       "gamma at ref": round(float(np.interp(S, grid, tot)), 3), "most negative point": [float(grid[i0]), round(float(tot[i0]), 3)],
       "short-gamma zone": [float(neg.min()), float(neg.max())] if len(neg) else None,
       "peak positive gamma": [float(grid[int(np.argmax(tot))]), round(float(tot.max()), 3)],
       "biggest strikes by dealer gamma near price ($bn)": near.reindex(near.abs().sort_values(ascending=False).index).head(6).round(3).to_dict(),
       "share of |gamma| by expiry": {str(k.date()): round(float(v), 3) for k, v in exp_share.items()}}


def ych(s, rng="2y"):
    u = f"https://query1.finance.yahoo.com/v8/finance/chart/{s}?range={rng}&interval=1d"
    r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=20))["chart"]["result"][0]
    return pd.Series([c for c in r["indicators"]["quote"][0]["close"]], index=pd.to_datetime([dt.datetime.utcfromtimestamp(t).date() for t in r["timestamp"]])).dropna()


m, spy, vix = ych("MSFT"), ych("SPY"), ych("%5EVIX")
m = m[m.index <= P]; spy = spy[spy.index <= P]
st = {}
for L in (10, 20, 40):
    lead = (m.pct_change(L) - spy.pct_change(L)).dropna(); w = lead.iloc[-252:]
    st[f"MSFT {L}-day lead vs SPY (Tue close) pct of trailing year"] = round(float((w < w.iloc[-1]).mean()), 2)
    st[f"MSFT {L}-day lead value %"] = round(float(100 * w.iloc[-1]), 2)
dix = pd.read_csv(dixf, parse_dates=["date"]).set_index("date"); gx = dix.gex.iloc[-252:]
st["S&P GEX (SqueezeMetrics) last"] = [str(gx.index[-1].date()), round(float(gx.iloc[-1] / 1e9), 2)]
st["S&P GEX pct of trailing year"] = round(float((gx < gx.iloc[-1]).mean()), 2)
st["DIX last / pct"] = [round(float(dix.dix.iloc[-1]), 3), round(float((dix.dix.iloc[-252:] < dix.dix.iloc[-1]).mean()), 2)]
hi = m.iloc[-252:].max(); st["MSFT 52w closing high"] = [str(m.iloc[-252:].idxmax().date()), round(float(hi), 2)]
st["drawdown from 52w high at ref %"] = round(float(100 * (S / hi - 1)), 1)
st["MSFT 2026 low close"] = [str(m[m.index >= "2026-01-01"].idxmin().date()), round(float(m[m.index >= "2026-01-01"].min()), 2)]
st["VIX 10 sessions ago / Tue close"] = [round(float(vix[vix.index <= P].iloc[-11]), 2), round(float(vix[vix.index <= P].iloc[-1]), 2)]
st["MSFT closes since Oct 20"] = {str(k.date()): round(float(v), 2) for k, v in m[m.index >= "2026-10-20"].items()}
out["state"] = st
json.dump(out, open(HERE / "out" / "msft_read.json", "w"), indent=1, default=float); print(json.dumps(out, indent=1, default=float))
