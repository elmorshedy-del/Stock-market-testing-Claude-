"""TSLA state at the Nov 4 close by the engine's own definition (OI dated Nov 4 = Tue close positions, Nov 4 closing chain),
plus: (a) the same with Tue's IVs (to isolate today's IV move), (b) scenarios adding a share of today's volume as new OI
(OI dated Nov 5 publishes ~6-7am Nov 5). Descriptive. Usage: python tsla_close_state.py <td dir> -> out/tsla_close_state.json"""
import datetime as dt
import json
import sys
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; MICRO = HERE.parents[1] / "microstructure"
sys.path[:0] = [str(HERE.parent / "2026-10-27-flip-wicks"), str(MICRO)]
from flipmap import norm   # noqa: E402
import td_gamma as t       # noqa: E402
from hd_gamma import day_metrics   # noqa: E402
td = Path(sys.argv[1]); D = pd.Timestamp("2026-11-04"); S_CLOSE = 385.19
h = pd.read_csv(MICRO / "out" / "td_gamma_TSLA.csv", parse_dates=["date"]).set_index("date").iloc[-251:]
gn_hist = h.gex_classic / (h.spot * (h.call_oi + h.put_oi) * 100)
o = norm(pd.read_csv(td / "TSLA_oi_20261104.csv.gz")).rename(columns=lambda c: "oi" if "open_interest" in c else c)
vol = norm(pd.read_csv(td / "TSLA_eod_20261104.csv.gz")); vol = vol[vol.date == D][["expiration", "strike", "cp", "volume"]]


def state(chain_day, S0, add_vol=0.0, side="both"):
    e = norm(pd.read_csv(td / f"TSLA_eod_{chain_day:%Y%m%d}.csv.gz")); e = e[e.date == chain_day].copy(); e["mid"] = (e.bid + e.ask) / 2
    oo = o[["expiration", "strike", "cp", "oi"]].merge(vol, on=["expiration", "strike", "cp"], how="outer").fillna(0)
    if add_vol:
        msk = (oo.cp == "P") if side == "P" else ((oo.cp == "C") if side == "C" else np.ones(len(oo), bool))
        oo.loc[msk, "oi"] = oo.loc[msk, "oi"] + add_vol * oo.loc[msk, "volume"]
    g0 = t.chain_day(e.assign(oi=0.0)).drop(columns=["oi"]).merge(oo[["expiration", "strike", "cp", "oi"]], on=["expiration", "strike", "cp"], how="left").fillna({"oi": 0})
    gg = g0[(g0.expiration > D) & ((g0.expiration - D).dt.days <= t.MAX_DTE) & (g0.oi > 0)].copy()
    gg["date"], gg["T"], gg["underlying_close"] = D, ((gg.expiration - D).dt.days / 365).clip(lower=1 / (365 * 24)), S0
    m = day_metrics(gg, D, {"TSLA": ["TSLA"]})[0]; g_n = m["gex_classic"] / (S0 * (m["call_oi"] + m["put_oi"]) * 100)
    return {"flip": round(float(m["flip_classic"]), 1), "close vs flip %": round(float(100 * (S0 / m["flip_classic"] - 1)), 2),
            "near-OI pct": round(float((h.near_oi_share < m["near_oi_share"]).mean()), 2), "freed": bool((h.near_oi_share < m["near_oi_share"]).mean() <= 1 / 3),
            "own-gamma pct": round(float((gn_hist < g_n).mean()), 2), "ATM IV 30d": round(float(m.get("atm_iv_30d", np.nan)), 3)}


out = {"official state at Nov 4 close (OI dated Nov 4 + Nov 4 chain)": state(D, S_CLOSE),
       "same positions with Tue Nov 3 IVs (isolates today's IV move)": state(pd.Timestamp("2026-11-03"), S_CLOSE)}
for k in (0.25, 0.5, 1.0):
    out[f"+{int(k * 100)}% of today's volume as new OI (all)"] = state(D, S_CLOSE, k)
    out[f"+{int(k * 100)}% of today's PUT volume as new OI"] = state(D, S_CLOSE, k, "P")
v = vol.merge(o[["expiration", "strike", "cp", "oi"]], on=["expiration", "strike", "cp"], how="left")
near = v[(v.strike.between(360, 410)) & (v.expiration > D)]
out["today's volume, strikes 360-410, expiries after today"] = {"calls": int(near[near.cp == "C"].volume.sum()), "puts": int(near[near.cp == "P"].volume.sum()),
    "top put strikes by volume": near[near.cp == "P"].groupby("strike").volume.sum().sort_values(ascending=False).head(5).astype(int).to_dict(),
    "top call strikes by volume": near[near.cp == "C"].groupby("strike").volume.sum().sort_values(ascending=False).head(5).astype(int).to_dict()}
# other playbook conditions
u = "https://query1.finance.yahoo.com/v8/finance/chart/TSLA?range=2y&interval=1d"
r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=20))["chart"]["result"][0]; q = r["indicators"]["quote"][0]
b = pd.DataFrame({k: q[k] for k in ("high", "low", "close")}, index=[dt.datetime.utcfromtimestamp(x).date() for x in r["timestamp"]]).dropna()
c = b.close; d_ = c.diff(); up = d_.clip(lower=0).ewm(alpha=1 / 14).mean(); dn = (-d_.clip(upper=0)).ewm(alpha=1 / 14).mean(); rsi = 100 - 100 / (1 + up / dn)
tr = pd.concat([b.high - b.low, (b.high - c.shift()).abs(), (b.low - c.shift()).abs()], axis=1).max(axis=1); atrp = tr.rolling(14).mean() / c
pc = lambda s: round(float((s.iloc[-253:-1] < s.iloc[-1]).mean()), 2)
out["other conditions"] = {"close": round(float(c.iloc[-1]), 2), "RSI14 / pct of year": [round(float(rsi.iloc[-1]), 1), pc(rsi)], "RSI needed for washed-out (bottom tenth)": round(float(np.quantile(rsi.iloc[-253:-1], 0.10)), 1),
    "ATR% 14 / pct of year": [round(float(100 * atrp.iloc[-1]), 2), pc(atrp)], "20-day closing low (excl today)": round(float(c.iloc[-21:-1].min()), 2)}
json.dump(out, open(HERE / "out" / "tsla_close_state.json", "w"), indent=1, default=float); print(json.dumps(out, indent=1, default=float))
