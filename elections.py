"""Do US elections release the market? S&P 500, VIX, S&P dealer gamma and TSLA around
election day, presidential vs midterm, before vs after the retail-options era (2020+).

Windows are measured from the election-day close (results come overnight):
  S&P return to +1/+5/+10/+20 sessions, VIX change (points and %), VIX run-up into the
  election (close 10 sessions before -> election day), S&P gamma percentile before/after
  (SqueezeMetrics, 2011+), TSLA return and TSLA's own gamma (2020+).
Baseline: the same windows starting on every other trading day of October-November in
non-election years, so the seasonal Q4 tendency is not credited to elections.
Usage: python elections.py
"""
import numpy as np
import pandas as pd

from burst_gamma import state
from common import load_bars
from forecast import build as spx_frame
from release import frame

PRES = ["1992-11-03", "1996-11-05", "2000-11-07", "2004-11-02", "2008-11-04", "2012-11-06", "2016-11-08", "2020-11-03", "2024-11-05"]
MID = ["1994-11-08", "1998-11-03", "2002-11-05", "2006-11-07", "2010-11-02", "2014-11-04", "2018-11-06", "2022-11-08"]
NEXT = "2026-11-03"


def window_stats(c, v, t):
    i = c.index.searchsorted(pd.Timestamp(t))
    if i + 20 >= len(c):
        return None
    lc = np.log(c.to_numpy())
    out = {f"spx_{h}d_%": 100 * (np.exp(lc[i + h] - lc[i]) - 1) for h in (1, 5, 10, 20)}
    out.update({"vix_on_day": v.iloc[i], "vix_runup_10d_pts": v.iloc[i] - v.iloc[i - 10],
                "vix_1d_pts": v.iloc[i + 1] - v.iloc[i], "vix_5d_pts": v.iloc[i + 5] - v.iloc[i], "vix_10d_pts": v.iloc[i + 10] - v.iloc[i],
                "vix_10d_%": 100 * (v.iloc[i + 10] / v.iloc[i] - 1)})
    return out


def table():
    f = frame()                                   # S&P (c) + VIX family since 1990
    c, v = f.c, f.VIX
    g = spx_frame()
    tsla = load_bars("TSLA").close
    try:
        own = state("TSLA")
    except FileNotFoundError:
        own = None
    rows = []
    for kind, dates in (("presidential", PRES), ("midterm", MID)):
        for d in dates:
            s = window_stats(c, v, d)
            if s is None:
                continue
            t = pd.Timestamp(d)
            s.update({"date": d, "kind": kind, "era": "2020+" if t.year >= 2020 else "pre-2020",
                      "spx_gamma_pct_on_day": g.gex_pct.asof(t) if t >= g.index[0] else np.nan,
                      "spx_gamma_pct_10d_later": g.gex_pct.asof(c.index[c.index.searchsorted(t) + 10]) if t >= g.index[0] else np.nan})
            if t >= tsla.index[0] + pd.Timedelta(days=30):
                j = tsla.index.searchsorted(t)
                s["tsla_5d_%"] = 100 * (tsla.iloc[j + 5] / tsla.iloc[j] - 1)
                s["tsla_20d_%"] = 100 * (tsla.iloc[j + 20] / tsla.iloc[j] - 1)
            if own is not None and t >= own.index[0]:
                p = own.index[own.index.searchsorted(t)]
                s.update({"tsla_own_g_pct": own.g_pct.get(p), "tsla_near_oi_pct": own.near_pct.get(p),
                          "tsla_flip_%": own.to_flip_pct.get(p), "tsla_iv_pct": own.iv_pct.get(p)})
            rows.append(s)
    E = pd.DataFrame(rows).set_index("date")
    # baseline: every Oct-Nov trading day in non-election (odd) years
    base = []
    for t in c.index[(c.index.month.isin([10, 11])) & (c.index.year % 2 == 1) & (c.index.year >= 1991)]:
        s = window_stats(c, v, t)
        if s:
            base.append(s)
    B = pd.DataFrame(base)
    return E, B, f


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 40)
    E, B, f = table()
    E.to_csv("out/elections.csv")
    show = ["kind", "era", "vix_on_day", "vix_runup_10d_pts", "vix_1d_pts", "vix_5d_pts", "vix_10d_pts", "spx_1d_%", "spx_5d_%", "spx_10d_%",
            "spx_20d_%", "spx_gamma_pct_on_day", "spx_gamma_pct_10d_later", "tsla_5d_%", "tsla_20d_%"]
    print(E[show].round(2).to_string())
    cols = ["vix_runup_10d_pts", "vix_1d_pts", "vix_5d_pts", "vix_10d_pts", "vix_10d_%", "spx_5d_%", "spx_10d_%", "spx_20d_%"]
    print("\nmeans by kind and era (n)")
    print(E.groupby(["kind", "era"])[cols].mean().round(2).assign(n=E.groupby(["kind", "era"]).size()).to_string())
    print("\nOct-Nov days in non-election years (baseline)")
    print(B[cols].mean().round(2).to_string())
    print(f"share of elections with VIX lower 5 sessions later: {(E.vix_5d_pts < 0).mean():.0%} "
          f"(baseline days {(B.vix_5d_pts < 0).mean():.0%}); S&P higher 20 sessions later: {(E['spx_20d_%'] > 0).mean():.0%} "
          f"(baseline {(B['spx_20d_%'] > 0).mean():.0%})")
    own_cols = [c for c in ("tsla_own_g_pct", "tsla_near_oi_pct", "tsla_flip_%", "tsla_iv_pct") if c in E]
    if own_cols:
        print("\nTSLA's own positioning on election day (2020+)")
        print(E[own_cols].dropna().round(2).to_string())
