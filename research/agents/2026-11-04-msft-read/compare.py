"""Was MSFT set up on Tue Nov 3 the way it was on Wed Jul 29 (the close before the July burst)? Descriptive, not a test.
Release setup recomputed with the REPORT §4aa definitions (held_back.frame / forecast.build): lead = rolling-252 rank pct of the
20-day log-return gap vs SPY >= 2/3; S&P GEX pct = share of the prior 251 days below today, <= 1/3. Own options state: td_gamma
CSV for July; Nov 3 computed with the same td_gamma/hd_gamma recipe (OI dated Nov 3, Nov 3 chains).
Usage: python compare.py <td dir> <DIX.csv> -> out/compare.json"""
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
td, dixf = Path(sys.argv[1]), sys.argv[2]


def ych(s):
    u = f"https://query1.finance.yahoo.com/v8/finance/chart/{s}?range=3y&interval=1d"
    r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=20))["chart"]["result"][0]
    return pd.Series(r["indicators"]["quote"][0]["close"], index=pd.to_datetime([dt.datetime.utcfromtimestamp(x).date() for x in r["timestamp"]])).dropna()


m, s, vix = ych("MSFT"), ych("SPY"), ych("%5EVIX"); idx = m.index.intersection(s.index); m, s = m[idx], s[idx]
X = pd.DataFrame({"c": m, "s": s})
for L in (10, 20, 40):
    X[f"lead{L}"] = ((np.log(m) - np.log(m.shift(L))) - (np.log(s) - np.log(s.shift(L)))).rolling(252, min_periods=120).rank(pct=True)
g = pd.read_csv(dixf, parse_dates=["date"]).set_index("date")
g["gex_pct"] = g.gex.rolling(252).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True); X = X.join(g[["gex", "gex_pct"]])
X["setup"] = (X.lead20 >= 2 / 3) & (X.gex_pct <= 1 / 3)
X["ma200"] = m / m.rolling(200).mean() - 1; X["dd"] = m / m.rolling(252, min_periods=1).max() - 1
d = m.diff(); up = d.clip(lower=0).ewm(alpha=1 / 14).mean(); dn = (-d.clip(upper=0)).ewm(alpha=1 / 14).mean(); X["rsi"] = 100 - 100 / (1 + up / dn)
X["vix"] = vix.reindex(X.index); X["vix_chg10"] = X.vix - X.vix.shift(10)
on = X[(X.index >= "2026-06-01") & X.setup].index
runs, cur = [], [on[0]] if len(on) else []
for a, b in zip(on[:-1], on[1:]):
    if (X.index.get_loc(b) - X.index.get_loc(a)) == 1: cur.append(b)
    else: runs.append(cur); cur = [b]
if cur: runs.append(cur)
h = pd.read_csv(MICRO / "out" / "td_gamma_MSFT.csv", parse_dates=["date"]).set_index("date")
own = lambda r: {"spot": round(float(r.spot), 2), "flip": round(float(r.flip_classic), 1), "% above flip": round(float(100 * (r.spot / r.flip_classic - 1)), 1),
                 "dealer gamma $bn/1%": round(float(r.gex_classic * r.spot * 0.01 / 1e9 if r.gex_classic > 1e8 else r.gex_classic), 2) if False else round(float(r.gex_classic / 1e9), 2),
                 "put/call OI": round(float(r.put_oi / r.call_oi), 2), "near-price OI share pct": None, "call wall": float(r.call_wall), "put wall": float(r.put_wall)}
hn = h.near_oi_share; pctl = lambda v, ref: round(float((ref < v).mean()), 2)
J = h.loc["2026-07-29"]; oj = own(J); oj["near-price OI share pct"] = pctl(J.near_oi_share, hn.loc[:"2026-07-29"].iloc[-252:])
oj["ATM IV 30d"] = round(float(J.atm_iv_30d), 3)
# Nov 3, same recipe
P = pd.Timestamp("2026-11-03"); e = norm(pd.read_csv(td / "MSFT_eod_20261103.csv.gz")); e = e[e.date == P].copy(); e["mid"] = (e.bid + e.ask) / 2
o = norm(pd.read_csv(td / "MSFT_oi_20261103.csv.gz")).rename(columns=lambda c: "oi" if "open_interest" in c else c)
g0 = t.chain_day(e.assign(oi=0.0)).drop(columns=["oi"]).merge(o[["expiration", "strike", "cp", "oi"]], on=["expiration", "strike", "cp"], how="left").fillna({"oi": 0})
S0 = float(m.loc[P]); gg = g0[(g0.expiration > P) & ((g0.expiration - P).dt.days <= t.MAX_DTE) & (g0.oi > 0)].copy()
gg["date"], gg["T"], gg["underlying_close"] = P, ((gg.expiration - P).dt.days / 365).clip(lower=1 / (365 * 24)), S0
mm = day_metrics(gg, P, {"MSFT": ["MSFT"]})[0]
N = pd.Series({**mm, "spot": S0}); on3 = own(N); on3["near-price OI share pct"] = pctl(mm["near_oi_share"], hn.iloc[-252:])
on3["ATM IV 30d"] = round(float(mm.get("atm_iv_30d", np.nan)), 3)
row = lambda dte: {"MSFT close": round(float(X.c[dte]), 2), "20-day lead pct (needs >= 0.67)": round(float(X.lead20[dte]), 2),
                   "10 / 40-day lead pct": [round(float(X.lead10[dte]), 2), round(float(X.lead40[dte]), 2)],
                   "S&P GEX pct (needs <= 0.33)": round(float(X.gex_pct[dte]), 2), "RELEASE SETUP ON": bool(X.setup[dte]),
                   "drawdown from 52w high %": round(float(100 * X.dd[dte]), 1), "vs 200-day avg %": round(float(100 * X.ma200[dte]), 1),
                   "RSI14": round(float(X.rsi[dte]), 0), "VIX / 10-day change": [round(float(X.vix[dte]), 1), round(float(X.vix_chg10[dte]), 1)]}
out = {"Jul 29 (close before the July burst)": {**row("2026-07-29"), "own options": oj, "next forced-flow event": "earnings that night (Jul 29 after the close)"},
       "Nov 3 (yesterday)": {**row("2026-11-03"), "own options": on3, "next forced-flow event": "none scheduled; Nov 20 monthly expiry (earnings were Oct 28)"},
       "setup ON runs since Jun 1": [[str(r[0].date()), str(r[-1].date()), len(r)] for r in runs]}
pj = m[(m.index >= "2026-07-29") & (m.index <= "2026-08-14")]
out["July path after Jul 29 close"] = {str(k.date()): round(float(100 * (v / pj.iloc[0] - 1)), 1) for k, v in pj.items()}
po = m[m.index >= "2026-10-28"]; out["since Oct 28 report (close 531.01)"] = {str(k.date()): round(float(100 * (v / 531.01 - 1)), 1) for k, v in po.items()}
json.dump(out, open(HERE / "out" / "compare.json", "w"), indent=1, default=float); print(json.dumps(out, indent=1, default=float))
