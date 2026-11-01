"""Part M: Friday Oct 30 SPY dealer hedge flow along the actual path, split into gamma / charm / vanna and into the
Oct 30 expiry vs later expiries. Positions = OI dated Oct 30 (Oct 29 close), IVs = Oct 29 closing smile scaled by
VIX(t)/VIX(Oct 29 close), classic convention, engine code imported unchanged (flipmap.preopen, options_flow.exposures).
Usage: python flow.py <td dir> <1m dir> -> out/flow.json, out/flow_path.csv"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "2026-10-27-flip-wicks"))
from flipmap import norm, preopen, exposures      # noqa: E402

td, y = Path(sys.argv[1]), Path(sys.argv[2])
D = pd.Timestamp("2026-10-30"); VIX0 = 17.20
e = norm(pd.read_csv(td / "SPY_eod_20261029.csv.gz")); e = e[e.date == pd.Timestamp("2026-10-29")]
o = norm(pd.read_csv(td / "SPY_oi_20261030.csv.gz"))
g = preopen(e, o, D)                                   # includes the Oct 30 expiry
g = g[g.K.between(600, 900)].copy()
days = (g.expiration - D).dt.days.to_numpy()


def m1(sym):
    r = json.load(open(y / f"{sym}_1m.json"))["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    b = pd.DataFrame({k: q[k] for k in ("close", "volume")}, index=pd.to_datetime(r["timestamp"], unit="s", utc=True).tz_convert("America/New_York")).dropna(subset=["close"])
    return b[b.index.date == D.date()].between_time("09:30", "15:59")


spy, vix = m1("SPY"), m1("VIX")
path = spy.close.resample("5min").last().dropna(); vol5 = (spy.close * spy.volume).resample("5min").sum().reindex(path.index)
vpath = vix.close.resample("5min").last().reindex(path.index).ffill().bfill()


def dealer_delta(S, minutes_left, vixv, mask=None):
    x = g.copy(); x["T"] = ((days + minutes_left / (60 * 24)) / 365).clip(min=1 / (365 * 24 * 60))
    x["iv"] = g.iv * (vixv / VIX0)
    if mask is not None: x = x[mask]
    return exposures(x, S).dex.sum()


exp0 = (g.expiration == D).to_numpy()
rows = []
t_idx = list(path.index)
for i in range(1, len(t_idx)):
    t0, t1 = t_idx[i - 1], t_idx[i]
    ml0 = (pd.Timestamp(f"{D.date()} 16:00", tz="America/New_York") - t0).total_seconds() / 60 + 5   # bar close time = label + 5 min
    ml1 = ml0 - 5
    S0, S1, v0, v1 = path.iloc[i - 1], path.iloc[i], vpath.iloc[i - 1], vpath.iloc[i]
    rec = {"time": (t1 + pd.Timedelta(minutes=5)).strftime("%H:%M"), "spy": S1, "vix": v1, "spy $vol": float(vol5.iloc[i])}
    for lab, msk in (("all", None), ("0DTE", exp0), ("later", ~exp0)):
        a = dealer_delta(S0, ml0, v0, msk); b_ = dealer_delta(S1, ml0, v0, msk); c_ = dealer_delta(S1, ml1, v0, msk); d_ = dealer_delta(S1, ml1, v1, msk)
        # hedge trade = -(change in dealer delta); positive = dealers BUY
        rec[f"{lab} gamma"], rec[f"{lab} charm"], rec[f"{lab} vanna"] = -(b_ - a), -(c_ - b_), -(d_ - c_)
    rows.append(rec)
P = pd.DataFrame(rows).set_index("time")
P.to_csv(HERE / "out" / "flow_path.csv")
bn = lambda v: round(float(v) / 1e9, 2)
seg = {"open-10:30": ("09:35", "10:30"), "10:30-14:50": ("10:35", "14:50"), "14:50-16:00": ("14:55", "16:00"), "whole day": ("09:35", "16:00")}
out = {"positions": "OI dated 2026-10-30 (Oct 29 close); IVs Oct 29 close scaled by VIX", "0DTE share of contracts' |gamma| at the open": None}
for k, (a, b) in seg.items():
    x = P.loc[a:b]; out[k] = {"SPY move": round(float(x.spy.iloc[-1] - (P.spy.loc[:a].iloc[-2] if a != "09:35" else path.iloc[0])), 2),
                              "SPY $ volume bn": bn(x["spy $vol"].sum())}
    for lab in ("all", "0DTE", "later"):
        for comp in ("gamma", "charm", "vanna"):
            out[k][f"{lab} {comp} $bn"] = bn(x[f"{lab} {comp}"].sum())
        out[k][f"{lab} total $bn"] = bn(x[[f"{lab} gamma", f"{lab} charm", f"{lab} vanna"]].sum().sum())
    out[k]["dealer flow as % of SPY $ volume"] = round(float(-x[["all gamma", "all charm", "all vanna"]].sum().sum() / x["spy $vol"].sum() * 100), 1)
gx = exposures(g.assign(T=((days + 390 / 1440) / 365)), path.iloc[0])
out["0DTE share of contracts' |gamma| at the open"] = round(float(gx[exp0].gex.abs().sum() / gx.gex.abs().sum()), 3)
json.dump(out, open(HERE / "out" / "flow.json", "w"), indent=1)
print(json.dumps(out, indent=1))
