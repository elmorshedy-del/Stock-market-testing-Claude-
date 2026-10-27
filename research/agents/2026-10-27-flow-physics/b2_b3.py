"""B2 conditional ensembles (SPY/S&P and TSLA) and B3 November base rate. Pre-registered @ bdc698c.
Usage: python b2_b3.py <ladder27 folder (data/^GSPC,^VIX,TSLA _1d.json + DIX.csv)> <GSPC_1mo.json>  -> out/b2.json, out/b2_fans.csv"""
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
MICRO = HERE.parents[1] / "microstructure"
fresh, monthly = sys.argv[1], sys.argv[2]
sys.path.insert(0, str(MICRO))
import common                                           # noqa: E402
common.DATA = Path(fresh) / "data"
_c = os.getcwd(); os.chdir(fresh)
from forecast import build                              # noqa: E402
import ladder as LD                                     # noqa: E402
f = build(); os.chdir(_c)
from common import load_bars                            # noqa: E402


def fan(close, mask, H):
    c = close.to_numpy(); idx = np.where(mask)[0]; idx = idx[idx + H < len(c)]
    paths = np.array([c[i + 1:i + H + 1] / c[i] - 1 for i in idx])
    q = np.quantile(paths, [0.05, 0.25, 0.5, 0.75, 0.95], axis=0)
    return idx, paths, q


def first_hit(close, idx, up, dn, H):
    c = close.to_numpy(); out = []
    for i in idx:
        w = c[i + 1:i + H + 1] / c[i] - 1
        u = np.where(w >= up)[0]; d = np.where(w <= -dn)[0]
        fu = u[0] if len(u) else 10**9; fd = d[0] if len(d) else 10**9
        out.append(1.0 if fu < fd else (0.0 if fd < fu else np.nan))
    o = np.array(out); return float(np.nanmean(o)), int(np.isfinite(o).sum())


def episodes(idx, gap=10):
    n, last = 0, -10**9
    for i in idx:
        if i - last > gap: n += 1
        last = i
    return n


res, rows = {}, []
# ---- SPY / S&P
spx = f.c; vix = f.VIX
r2 = pd.Series(LD.first_on((f.gex_pct <= 0.30) & (f.dix_pct > 0.5)), index=f.index)
r2_recent = r2.rolling(10, min_periods=1).max() > 0
near = f.c / f.c.rolling(252).max() >= 0.98
state = r2_recent & near & vix.between(15, 20)
H = 20
idx, paths, q = fan(spx, state.to_numpy(), H)
idx0, paths0, q0 = fan(spx, np.ones(len(spx), bool), H)
p33, n33 = first_hit(spx, idx, 0.03, 0.03, 60); p33b, n33b = first_hit(spx, idx0, 0.03, 0.03, 60)
res["SPX analog (R2 within 10 sessions, within 2% of 52w high, VIX 15-20)"] = {
    "days": int(len(idx)), "episodes (gap>10)": episodes(idx), "sample": f"{f.index[0].date()} to {f.index[-1].date()}",
    "today in state": bool(state.iloc[-1]), "last date in data": str(f.index[-1].date()),
    "fwd median % at 1/3/5/10/20d": [round(100 * q[2][h - 1], 2) for h in (1, 3, 5, 10, 20)],
    "fwd 5%/95% at 10d": [round(100 * q[0][9], 2), round(100 * q[4][9], 2)], "fwd 5%/95% at 20d": [round(100 * q[0][19], 2), round(100 * q[4][19], 2)],
    "all days median at 10/20d": [round(100 * q0[2][9], 2), round(100 * q0[2][19], 2)],
    "all days 5%/95% at 20d": [round(100 * q0[0][19], 2), round(100 * q0[4][19], 2)],
    "P(+3% before -3%, closes, within 60d)": [round(p33, 3), n33], "P(+3% before -3%), all days": [round(p33b, 3), n33b],
    "P(close <= -2% at any point within 10d)": round(float(np.mean((paths[:, :10] <= -0.02).any(axis=1))), 3),
    "P(close <= -2% within 10d), all days": round(float(np.mean((paths0[:, :10] <= -0.02).any(axis=1))), 3)}
for h in range(H):
    rows.append({"asset": "SPX", "h": h + 1, **{f"q{p}": q[j][h] for j, p in enumerate((5, 25, 50, 75, 95))}, **{f"all_q{p}": q0[j][h] for j, p in enumerate((5, 25, 50, 75, 95))}})
# ---- TSLA
m = pd.read_csv(MICRO / "out" / "td_gamma_TSLA.csv", parse_dates=["date"]).set_index("date")
m["near_pct"] = m.near_oi_share.rolling(252, min_periods=120).rank(pct=True)
tc = load_bars("TSLA").close
tc = tc[tc.index >= "2021-01-01"]
st = ((m.near_pct <= 1 / 3) & (m.spot / m.flip_classic - 1 > 0.05)).reindex(tc.index).fillna(False)
H2 = 10
idx, paths, q = fan(tc, st.to_numpy(), H2)
idx0, paths0, q0 = fan(tc, np.ones(len(tc), bool), H2)
res["TSLA analog (freed, >5% above own flip), 2021-Oct 14 2026"] = {
    "days": int(len(idx)), "episodes (gap>10)": episodes(idx),
    "fwd median % at 1/3/5/10d": [round(100 * q[2][h - 1], 2) for h in (1, 3, 5, 10)],
    "fwd 5%/95% at 10d": [round(100 * q[0][9], 2), round(100 * q[4][9], 2)],
    "all days median / 5% / 95% at 10d": [round(100 * q0[2][9], 2), round(100 * q0[0][9], 2), round(100 * q0[4][9], 2)],
    "P(close <= -5% at any point within 10d)": round(float(np.mean((paths <= -0.05).any(axis=1))), 3),
    "same, all days": round(float(np.mean((paths0 <= -0.05).any(axis=1))), 3),
    "P(close >= +10% at any point within 10d)": round(float(np.mean((paths >= 0.10).any(axis=1))), 3),
    "same, all days ": round(float(np.mean((paths0 >= 0.10).any(axis=1))), 3)}
for h in range(H2):
    rows.append({"asset": "TSLA", "h": h + 1, **{f"q{p}": q[j][h] for j, p in enumerate((5, 25, 50, 75, 95))}, **{f"all_q{p}": q0[j][h] for j, p in enumerate((5, 25, 50, 75, 95))}})
# ---- B3 November
r = json.loads(Path(monthly).read_text())["chart"]["result"][0]
mo = pd.Series(r["indicators"]["quote"][0]["close"], index=pd.to_datetime(r["timestamp"], unit="s")).dropna()
mo.index = mo.index.to_period("M"); mo = mo[~mo.index.duplicated(keep="last")]
ret = mo.pct_change()
hi12 = mo.rolling(12).max()
nov = pd.DataFrame({"ret": ret[ret.index.month == 11]})
nov["oct_near_high"] = [(mo.get(p - 1, np.nan) / hi12.get(p - 1, np.nan)) >= 0.97 for p in nov.index]
nov = nov[(nov.index.year >= 1950) & (nov.index.year <= 2025)]
allm = ret[(ret.index.year >= 1950) & (ret.index.year <= 2025)]
res["B3 November S&P (Yahoo monthly; years available)"] = {"years": int(len(nov)), "first year": int(nov.index.year.min()), "mean %": round(100 * nov.ret.mean(), 2), "median %": round(100 * nov.ret.median(), 2),
                                   "share up": round(float((nov.ret > 0).mean()), 3), "all months mean % / share up": [round(100 * allm.mean(), 2), round(float((allm > 0).mean()), 3)],
                                   "Oct close within 3% of 12m high: years / mean % / share up": [int(nov.oct_near_high.sum()), round(100 * nov[nov.oct_near_high].ret.mean(), 2), round(float((nov[nov.oct_near_high].ret > 0).mean()), 3)],
                                   "Nov rank among 12 months by mean": int((allm.groupby(allm.index.month).mean().rank(ascending=False))[11])}
(HERE / "out" / "b2.json").write_text(json.dumps(res, indent=1))
pd.DataFrame(rows).to_csv(HERE / "out" / "b2_fans.csv", index=False)
print(json.dumps(res, indent=1))
