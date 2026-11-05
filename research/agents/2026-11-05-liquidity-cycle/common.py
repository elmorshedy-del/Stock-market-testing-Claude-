"""Shared loaders: daily features from 1-minute RTH bars, Yahoo daily, SqueezeMetrics GEX percentile."""
import datetime as dt
import json
import urllib.request

import numpy as np
import pandas as pd


def daily_from_bars(files):
    x = pd.concat([pd.read_parquet(f) for f in files]).sort_values(["date", "hm"])
    x = x[x.groupby("date").hm.transform("count") >= 300]
    x["t5"] = x.hm.str[:3] + (x.hm.str[3:].astype(int) // 5 * 5).astype(str).str.zfill(2)
    b = x.groupby(["date", "t5"]).agg(c=("close", "last"), v=("volume", "sum"), px=("close", "mean"))
    b["r"] = np.log(b.c).groupby(level=0).diff().abs()
    b["dv"] = b.v * b.px
    g = b.groupby(level=0); d = x.groupby("date").agg(h=("high", "max"), l=("low", "min"), c=("close", "last"), v=("volume", "sum"))
    d["L_raw"] = g.r.sum() / g.dv.sum() * 1e9
    d["rng"] = np.log(d.h / d.l)
    return d[~d.index.duplicated()]


def pct_trailing(s, n=252, minp=120):
    return s.rolling(n, min_periods=minp).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True)


def yahoo(sym, start="2010-01-01"):
    """Daily bars via explicit period1/period2: range=max silently returns MONTHLY bars (bug caught 2026-11-05)."""
    p1 = int(pd.Timestamp(start).timestamp()); p2 = int(pd.Timestamp.now().timestamp()) + 86400
    u = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?period1={p1}&period2={p2}&interval=1d"
    r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=30))["chart"]["result"][0]
    q = r["indicators"]["quote"][0]
    d = pd.DataFrame({k: q[k] for k in ("open", "high", "low", "close")}, index=pd.to_datetime([dt.datetime.utcfromtimestamp(t).date() for t in r["timestamp"]]))
    d = d[~d.index.duplicated(keep="last")].dropna()
    assert d.index.to_series().diff().dt.days.median() <= 3, f"{sym}: not daily bars"
    return d


def gex_pct(dixf):
    g = pd.read_csv(dixf, parse_dates=["date"]).set_index("date")
    g["gp"] = pct_trailing(g.gex, 252, 252)
    return g
