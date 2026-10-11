"""Daily dealer-gamma history from ThetaData chains pulled by td_pull.py.

ThetaData EOD rows carry quotes but no IV, so per day and expiry:
  spot  = put-call parity at the strike where |call mid - put mid| is smallest
          (nearest expiry >= 2 days out; raw, split-unadjusted like the strikes)
  IV    = Black-Scholes IV solved from OTM mids (vectorised bisection), then
          applied to both rights at each strike, interpolated across strikes
Open interest (Value tier) is merged by contract and date; it is the prior
day's close, so a row dated t describes positioning going INTO session t.
The metrics are those of hd_gamma.day_metrics (GEX, vanna, charm, flip, walls).

Usage: python td_gamma.py TSLA [SPY ...]      -> out/td_gamma_{SYM}.csv
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

from common import DATA, OUT
from hd_gamma import day_metrics

DIR = DATA / "thetadata"
R = 0.04


def read(sym, kind):
    files = sorted(DIR.glob(f"{sym}_*_{kind}.csv.gz"))
    if not files:
        return pd.DataFrame()
    d = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    dcol = next(c for c in ("date", "created", "timestamp") if c in d.columns)
    d["date"] = pd.to_datetime(d[dcol].astype(str).str[:10])
    d["expiration"] = pd.to_datetime(d.expiration)
    d["cp"] = np.where(d.right.str.upper().str.startswith("C"), "C", "P")
    return d


def bs_price(S, K, T, s, call):
    sq = np.sqrt(T)
    d1 = (np.log(S / K) + (R + 0.5 * s * s) * T) / (s * sq)
    d2 = d1 - s * sq
    c = S * norm.cdf(d1) - K * np.exp(-R * T) * norm.cdf(d2)
    return np.where(call, c, c - S + K * np.exp(-R * T))


def implied_vol(price, S, K, T, call, lo=0.01, hi=5.0, n=50):
    lo, hi = np.full(len(price), lo), np.full(len(price), hi)
    for _ in range(n):
        mid = (lo + hi) / 2
        too_high = bs_price(S, K, T, mid, call) > price
        hi, lo = np.where(too_high, mid, hi), np.where(too_high, lo, mid)
    iv = (lo + hi) / 2
    return np.where((iv > 0.011) & (iv < 4.99), iv, np.nan)


def spot_from_parity(g):
    exps = sorted(e for e in g.expiration.unique() if (e - g.date.iloc[0]).days >= 2)
    for e in exps[:3]:
        x = g[g.expiration == e].pivot_table(index="strike", columns="cp", values="mid").dropna()
        if len(x) >= 3:
            par = x["C"] - x["P"]
            k = par.abs().nsmallest(3).index
            return float(np.median(k + par[k]))
    return np.nan


def chain_day(g):
    """One day's chain in the schema hd_gamma.day_metrics expects."""
    g = g.copy()
    S = spot_from_parity(g)
    g["T"] = ((g.expiration - g.date).dt.days / 365).clip(lower=1 / (365 * 24))
    g = g[g.expiration > g.date]
    otm = ((g.cp == "C") & (g.strike >= S)) | ((g.cp == "P") & (g.strike < S))
    ok = otm & (g.bid > 0) & (g.ask > 0)
    iv = pd.Series(np.nan, index=g.index)
    if ok.any():
        q = g[ok]
        iv[ok] = implied_vol(q.mid.to_numpy(), S, q.strike.to_numpy(), q["T"].to_numpy(), (q.cp == "C").to_numpy())
    g["iv_otm"] = iv
    out = []
    for e, x in g.groupby("expiration"):
        pts = x.dropna(subset=["iv_otm"]).groupby("strike").iv_otm.median()
        x = x.copy()
        if len(pts) >= 3:
            x["iv"] = np.interp(x.strike, pts.index, pts.rolling(3, center=True, min_periods=1).median())
        else:
            x["iv"] = np.nan
        out.append(x)
    g = pd.concat(out)
    g["iv"] = g.iv.fillna(g.groupby("expiration").iv.transform("median")).fillna(g.iv.median())
    g["underlying"], g["underlying_close"], g["K"], g["exp"] = g.symbol, S, g.strike, g.expiration.dt.date
    return g.dropna(subset=["iv"])


def build(sym):
    eod, oi = read(sym, "eod"), read(sym, "oi")
    if oi.empty:
        raise SystemExit(f"{sym}: no open-interest files in {DIR} (needs the ThetaData Value tier; run td_pull.py)")
    eod["mid"] = (eod.bid + eod.ask) / 2
    oic = next(c for c in oi.columns if "open_interest" in c)
    key = ["date", "expiration", "strike", "cp"]
    d = eod.merge(oi[key + [oic]].rename(columns={oic: "oi"}), on=key, how="left")
    d["oi"] = d.oi.fillna(0)
    rows = []
    for day, g in d.groupby("date"):
        rows += day_metrics(chain_day(g), day, {sym: [sym]})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    for sym in sys.argv[1:] or ["TSLA"]:
        m = build(sym)
        m.to_csv(OUT / f"td_gamma_{sym}.csv", index=False)
        print(sym, len(m), "days ->", OUT / f"td_gamma_{sym}.csv")
