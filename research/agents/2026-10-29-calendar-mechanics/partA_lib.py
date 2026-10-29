"""Helpers shared by partA.py and figdata.py (copied verbatim from partA.py)."""
import json

import numpy as np
import pandas as pd


def yahoo(p):
    r = json.load(open(p))["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    c = pd.Series(q["close"], index=pd.to_datetime(r["timestamp"], unit="s").normalize()).dropna()
    c = c[~c.index.duplicated(keep="last")]; c = c[c > 0]
    return np.log(c).diff().dropna()


def nth_friday(y, m, n):
    return pd.date_range(f"{y}-{m:02d}-01", periods=31, freq="D").to_series().loc[lambda s: (s.dt.month == m) & (s.dt.dayofweek == 4)].iloc[n - 1]


def tag(lr):
    d = pd.DataFrame({"r": lr}); d["yr"] = d.index.year; d["m"] = d.index.month
    tf = {(y, m): nth_friday(y, m, 3) for y in range(d.yr.min(), d.yr.max() + 1) for m in range(1, 13)}
    d["tf"] = [tf[(y, m)] for y, m in zip(d.yr, d.m)]
    d["late_sep"] = (d.m == 9) & (d.index > d.tf)
    return d


