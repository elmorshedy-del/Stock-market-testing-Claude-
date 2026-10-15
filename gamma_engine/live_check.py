"""Intraday status check: a stock's own option map with TODAY's open interest at a live price.
Open interest for a day is published before the open (it is the prior close's positions); ThetaData only
serves same-day OI one expiry at a time. IVs come from the last end-of-day chain in data/thetadata.
Needs THETADATA_API_KEY (Value tier) and the thetadata package; writes data/thetadata/{SYM}_live_oi_{DAY}.csv.gz.
Usage: python live_check.py 2026-10-12 379.84 [TSLA] [2026-10-16]     (day, live price, symbol, next monthly expiry)
"""
import os
import sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd

import td_gamma as t
from hd_gamma import day_metrics


def pull_oi(sym, day):
    path = t.DIR / f"{sym}_live_oi_{day:%Y%m%d}.csv.gz"
    if path.exists():
        return pd.read_csv(path)
    from thetadata import ThetaClient
    c = ThetaClient(api_key=os.environ["THETADATA_API_KEY"], dataframe_type="pandas")
    last = t.read(sym, "oi")
    exps = sorted(e for e in last.expiration.dt.date.unique() if e >= day.date())
    get = lambda e: c.option_history_open_interest(symbol=sym, expiration=e, start_date=day.date(), end_date=day.date())
    with ThreadPoolExecutor(2) as ex:                      # Value tier: 2 concurrent requests
        df = pd.concat([p for p in ex.map(get, exps) if p is not None and len(p)], ignore_index=True)
    df.to_csv(path, index=False)
    return df


def status(sym, day, price, expiry):
    eod, oi = t.read(sym, "eod"), t.read(sym, "oi")
    d0 = oi.date.max()
    e = eod[eod.date == d0].copy()
    e["mid"] = (e.bid + e.ask) / 2
    key = ["expiration", "strike", "cp"]
    o0 = oi[oi.date == d0].rename(columns={"open_interest": "oi"})
    g0 = t.chain_day(e.merge(o0[["date"] + key + ["oi"]], on=["date"] + key, how="left").fillna({"oi": 0}))
    n = pull_oi(sym, day)
    n["expiration"] = pd.to_datetime(n.expiration)
    n["cp"] = np.where(n.right.str.upper().str.startswith("C"), "C", "P")
    g = g0.merge(n.rename(columns={"open_interest": "oi_new"})[key + ["oi_new"]], on=key, how="inner")
    g["oi_old"], g["oi"] = g.oi, g.oi_new
    g = g[(g.expiration >= day) & (g.oi > 0)].copy()
    g["date"], g["T"], g["underlying_close"] = day, ((g.expiration - day).dt.days / 365).clip(lower=1 / (365 * 24)), price
    m = pd.read_csv(t.OUT / f"td_gamma_{sym}.csv", parse_dates=["date"]).set_index("date").iloc[-251:]
    gn_hist = m.gex_classic / (m.spot * (m.call_oi + m.put_oi) * 100)
    rows = []
    for lab, x in ((f"{d0:%b %d} close", None), (f"{day:%b %d} at {price:.2f}", g), (f"after {expiry:%b %d} expiry", g[g.expiration > expiry])):
        r = m.iloc[-1].to_dict() if x is None else day_metrics(x, day, {sym: [sym]})[0]
        S = r["spot"] if x is None else price
        gn = r["gex_classic"] / (S * (r["call_oi"] + r["put_oi"]) * 100)
        rows.append({"when": lab, "price": S, "flip": r["flip_classic"], "% above flip": 100 * (S / r["flip_classic"] - 1),
                     "dealer gamma $M/1%": r["gex_classic"] / 1e6, "own-gamma pct": (gn_hist < gn).mean(),
                     "near-OI share": r["near_oi_share"], "near-OI pct": (m.near_oi_share < r["near_oi_share"]).mean(),
                     "call wall": r["call_wall"], "put wall": r["put_wall"]})
    g["bucket"] = np.where(g.expiration <= expiry, f"expires by {expiry:%b %d}",
                           np.where(g.expiration <= expiry + pd.Timedelta(days=35), "next monthly", "later"))
    flow = g.groupby(["cp", "bucket"])[["oi_old", "oi"]].sum()
    flow["change %"] = 100 * (flow.oi / flow.oi_old - 1)
    k = g.groupby(["K", "cp"])[["oi_old", "oi"]].sum().unstack()
    k = k[(k.index >= 0.9 * price) & (k.index <= 1.12 * price) & (k.index % 10 == 0)]
    return pd.DataFrame(rows), flow, k


if __name__ == "__main__":
    pd.set_option("display.width", 200)
    day, price = pd.Timestamp(sys.argv[1]), float(sys.argv[2])
    sym = sys.argv[3] if len(sys.argv) > 3 else "TSLA"
    expiry = pd.Timestamp(sys.argv[4]) if len(sys.argv) > 4 else pd.Timestamp("2026-10-16")
    s, flow, k = status(sym, day, price, expiry)
    print(s.round(3).to_string(index=False))
    print("\nopen interest since the last close, by expiry bucket\n" + flow.round(1).to_string())
    print("\nby strike (old -> new)\n" + k.astype(int).to_string())
