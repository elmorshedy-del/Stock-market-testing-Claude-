"""Dealer hedge book per day from the ThetaData chains: the hedging flow that is already scheduled.

Convention (classic, the one that matched SqueezeMetrics for the S&P): dealers are short the puts
customers hold and long the calls customers sell. A dealer short a put is long its delta and hedges
by shorting stock; that short is bought back as the put loses delta.

Per day, with spot S and every contract's IV from td_gamma.chain_day:
  put_hedge     $ of stock dealers are short against customer puts (sum of OI x 100 x |delta| x S)
  decay_put     $ dealers buy (+) or sell (-) over the next 20 sessions if spot and IV stay where
                they are: delta now vs delta 20 sessions later, expired contracts at payoff delta
  release_put   $ dealers buy (+) or sell (-) if implied vol moves to the vol the stock is
                actually realising (20-day), every IV scaled by realised / 30-day ATM IV
  decay_call, release_call   the same for the call side (sign depends on the convention, kept apart)
  atm_iv, rv20, adv          30-day ATM IV, 20-day realised vol, 20-day average $ volume
  near2, near5               share of all OI within +-2% / +-5% of spot in expiries <= 45 days
Usage: python mech_book.py SPY MSFT      -> out/mech_book_{SYM}.csv
"""
import sys
from multiprocessing import Pool

import numpy as np
import pandas as pd
from scipy.stats import norm

import td_gamma as t
from common import OUT, load_bars

H = 20          # sessions ahead


def delta(S, K, T, s, call):
    d1 = (np.log(S / K) + (t.R + 0.5 * s * s) * T) / (s * np.sqrt(T))
    return np.where(call, norm.cdf(d1), norm.cdf(d1) - 1)


def day_book(g, rv):
    g = t.chain_day(g)
    g = g[g.oi > 0]
    if g.empty:
        return None
    S, day = float(g.underlying_close.iloc[0]), g.date.iloc[0]
    K, T, iv = g.K.to_numpy(float), g["T"].to_numpy(float), g.iv.to_numpy(float)
    call = (g.cp == "C").to_numpy()
    n = g.oi.to_numpy(float) * 100 * np.where(call, 1.0, -1.0)
    d0 = delta(S, K, T, iv, call)
    dt = (day + pd.offsets.BDay(H) - day).days / 365
    T1 = T - dt
    alive = T1 > 0
    payoff = np.where(call, (S > K).astype(float), -(S < K).astype(float))
    d1 = np.where(alive, delta(S, K, np.where(alive, T1, 1.0), iv, call), payoff)
    atm = g[(g.K / S).between(0.97, 1.03) & (g["T"] * 365).between(20, 45)]
    atm_iv = float(atm.iv.median()) if len(atm) else float(g.iv[(g.K / S).between(0.97, 1.03)].median())
    d2 = delta(S, K, T, iv * rv / atm_iv, call) if np.isfinite(rv) and atm_iv > 0 else np.full(len(g), np.nan)
    out = {"date": day, "spot": S, "atm_iv": atm_iv, "rv20": rv}
    short = (g["T"] * 365 <= 45).to_numpy()
    for k in (2, 5):    # share of all OI within +-k% of spot in expiries <= 45 days (the "freed" gauge, as hd_gamma)
        out[f"near{k}"] = float(g.oi[short & (np.abs(K / S - 1) <= k / 100)].sum() / g.oi.sum())
    for side, m in (("put", ~call), ("call", call)):
        out[f"{side}_hedge"] = float(np.sum(np.abs(n[m] * d0[m])) * S)
        out[f"decay_{side}"] = float(-np.sum(n[m] * (d1[m] - d0[m])) * S)
        out[f"release_{side}"] = float(-np.sum(n[m] * (d2[m] - d0[m])) * S)
    return out


def _month(args):
    f_eod, f_oi, rv = args
    e, o = pd.read_csv(f_eod), pd.read_csv(f_oi)
    for d, col in ((e, "created"), (o, "timestamp")):
        d["date"] = pd.to_datetime(d[col].astype(str).str[:10])
        d["expiration"] = pd.to_datetime(d.expiration)
        d["cp"] = np.where(d.right.str.upper().str.startswith("C"), "C", "P")
    e["mid"] = (e.bid + e.ask) / 2
    key = ["date", "expiration", "strike", "cp"]
    d = e.merge(o[key + ["open_interest"]].rename(columns={"open_interest": "oi"}), on=key, how="left")
    d["oi"] = d.oi.fillna(0)
    d = d[(d.expiration - d.date).dt.days <= t.MAX_DTE]
    rows = []
    for day, g in d.groupby("date"):
        r = day_book(g, rv.get(day, np.nan))
        if r:
            rows.append(r)
    return rows


def build(sym, procs=4):
    px = load_bars(sym)
    rv = (np.log(px.close).diff().rolling(20).std() * np.sqrt(252)).to_dict()
    jobs = []
    for f in sorted(t.DIR.glob(f"{sym}_*_eod.csv.gz")):
        fo = f.with_name(f.name.replace("_eod", "_oi"))
        if fo.exists():
            jobs.append((f, fo, rv))
    with Pool(procs) as p:
        rows = [r for m in p.map(_month, jobs) for r in m]
    b = pd.DataFrame(rows).set_index("date").sort_index()
    b["adv"] = (px.close * px.volume).rolling(20).mean().reindex(b.index)
    return b


if __name__ == "__main__":
    for sym in sys.argv[1:] or ["SPY"]:
        b = build(sym)
        b.to_csv(OUT / f"mech_book_{sym}.csv")
        print(sym, len(b), "days ->", OUT / f"mech_book_{sym}.csv")
        print(b.tail(3).to_string())
