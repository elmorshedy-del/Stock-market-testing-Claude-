"""The anatomy of TSLA's multi-week up-legs as testable stages, checked on ALL days 2021+.

  stage 1 base      within +-3% of the own gamma flip, own gamma <= 0.45, IV pct <= 0.40
  stage 2 lead-in   3-10% above the flip, own gamma turned from <= 0.45 to >= 0.60 within 10 sessions
  stage 3 wall test largest near-term call strike 0-2% above spot, own gamma >= 0.75, >= 5% above the flip
  top               >= 15% above the flip and 30-day IV pct >= 0.90 (spot-up / vol-up exhaustion)
Outcomes: +15% at some point within 15 sessions, -10% at some point within 10 sessions,
10-session return. Episodes = runs of consecutive flagged days; significance is counted
on episodes (binomial vs the all-day rate), not days.
Usage: python leg_stages.py TSLA
"""
import sys

import numpy as np
import pandas as pd
from scipy.stats import binom

from burst_gamma import state
from common import OUT, load_bars
from forecast import build as spx_frame
from legs import find_legs
from tsla_eras import REACTIONS_2020


def daily(sym):
    c = load_bars(sym).close
    st = state(sym)
    m = pd.read_csv(OUT / f"td_gamma_{sym}.csv", parse_dates=["date"]).set_index("date")
    x = st.join(c.rename("c"), how="inner")
    x = x[x.index >= "2020-06-01"].copy()
    x["flip"] = x.to_flip_pct
    lc = np.log(x.c)
    x["f10"] = lc.shift(-10) - lc
    x["max15"] = pd.concat([lc.shift(-k) for k in range(1, 16)], axis=1).max(axis=1) - lc
    x["min10"] = pd.concat([lc.shift(-k) for k in range(1, 11)], axis=1).min(axis=1) - lc
    x["past10"] = lc - lc.shift(10)
    x["g_min10"] = x.g_pct.rolling(10).min()
    x["g_max5"] = x.g_pct.rolling(5).max()
    x["call_oi_10d"] = 100 * np.log(m.call_oi / m.call_oi.shift(10)).reindex(x.index)
    spx = spx_frame()
    x["spx_gex"] = spx.gex_pct.reindex(x.index).ffill(limit=3)
    x["dix"] = spx.dix_pct.reindex(x.index).ffill(limit=3)
    rx = pd.DatetimeIndex([c.index[c.index.searchsorted(pd.Timestamp(d))] for d in REACTIONS_2020]) if sym == "TSLA" else pd.DatetimeIndex([])
    pos = np.searchsorted(x.index.values, rx.values)             # index of each report reaction session
    x["sessions_to_report"] = [int(min((p - i for p in pos if p > i), default=99)) for i in range(len(x))]
    legs = find_legs(c[c.index >= "2020-06-01"])
    x["in_leg"] = False
    for s, e in legs:
        x.loc[s:e, "in_leg"] = True
    x["s1"] = x.flip.between(-3, 3) & (x.g_pct <= 0.45) & (x.iv_pct <= 0.40) & ~x.in_leg
    x["s2"] = x.flip.between(3, 10) & (x.g_pct >= 0.6) & (x.g_min10 <= 0.45)
    x["s3"] = x.to_call_wall_pct.between(0, 2) & (x.g_pct >= 0.75) & (x.flip >= 5)
    x["top"] = (x.flip >= 15) & (x.iv_pct >= 0.90)
    return x, legs


def episodes(z, flag):
    m = flag.astype(bool)
    first = m & ~m.shift(1, fill_value=False)
    return z[first]


def summary(z, flag, lab):
    e = episodes(z, flag)
    up, dn = (z.max15 >= np.log(1.15)), (z.min10 <= np.log(0.9))
    ku, kd, n = int(up[e.index].sum()), int(dn[e.index].sum()), len(e)
    return {"stage": lab, "days": int(flag.sum()), "episodes": n,
            "P(+15% in 15d)": up[e.index].mean(), "all days +15%": up.mean(), "p_up": binom.sf(ku - 1, n, up.mean()),
            "P(-10% in 10d)": dn[e.index].mean(), "all days -10%": dn.mean(), "p_dn": binom.sf(kd - 1, n, dn.mean()),
            "mean 10d %": 100 * z.f10[e.index].mean()}


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    sym = (sys.argv[1:] or ["TSLA"])[0]
    x, legs = daily(sym)
    x.to_csv(OUT / f"legs_daily_{sym}.csv")
    z = x[x.index >= "2021-01-01"].dropna(subset=["f10", "max15", "min10", "g_pct", "iv_pct"])
    t = pd.DataFrame([summary(z, z[k], k) for k in ("s1", "s2", "s3", "top")])
    print(t.round(3).to_string(index=False))
    # what separated wall breaks from wall holds
    e3 = episodes(z, z.s3).copy()
    e3["broke"] = z.max15[e3.index] >= np.log(1.15)
    cols = ["flip", "g_pct", "iv_pct", "near_pct", "past10", "call_oi_10d", "spx_gex", "dix", "sessions_to_report"]
    print("\nstage-3 episodes: wall broke (+15% within 15d) vs held")
    print(e3.groupby("broke")[cols].median().T.round(2).to_string())
    print(e3.assign(year=e3.index.year).groupby("year").broke.agg(["sum", "size"]).T.to_string())
    et = episodes(z, z.top).copy()
    et["fell"] = z.min10[et.index] <= np.log(0.9)
    print("\ntop-signal episodes: fell 10% vs not")
    print(et.groupby("fell")[["flip", "g_pct", "g_max5", "iv_pct", "near_pct", "past10"]].median().T.round(2).to_string())
    now = x.iloc[-1]
    print(f"\nNOW {x.index[-1].date()}: s1 {bool(now.s1)}, s2 {bool(now.s2)}, s3 {bool(now.s3)}, top {bool(now.top)} | flip {now.flip:+.1f}%, "
          f"own g {now.g_pct:.2f}, IV {now.iv_pct:.2f}, call wall {now.call_wall:.0f} ({now.to_call_wall_pct:+.1f}%), "
          f"S&P gamma {now.spx_gex:.2f}, DIX {now.dix:.2f}, sessions to report {now.sessions_to_report}")
