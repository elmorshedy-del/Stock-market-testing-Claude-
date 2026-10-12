"""Event by event: each up-burst since 2021 and the stock's OWN option positioning the
day before (from the ThetaData open-interest history, td_gamma_{SYM}.csv).

Burst = +5% in a day or +9% in two days, dated by its first day (as in burst_check.py).
Day-before state: own-gamma percentile (classic, vs trailing year), side of and
distance to the own gamma flip, distance to the call wall (largest near-term call
OI within 25% of spot), share of gamma expiring within 5 trading days, total
near-money gamma (short-both convention, percentile), weekday, report day.
After: did the burst close above the prior call wall; where the call wall sat 5 days later.
The 'before' profile of all bursts is compared with all days (base rates).
Usage: python burst_gamma.py TSLA
"""
import sys

import numpy as np
import pandas as pd

from common import OUT, load_bars
from stock_now import burst_days
from tsla_eras import REACTIONS_2020

START = "2021-01-01"
FLAGGED = {"2024-07-01": "missed by S&P signals (4l)", "2025-09-11": "missed by S&P signals (4l)",
           "2025-10-06": "missed by S&P signals (4l)", "2025-10-13": "missed by S&P signals (4l)",
           "2025-04-23": "caught by S&P signals (4l)", "2025-05-27": "caught by S&P signals (4l)",
           "2025-11-24": "caught by S&P signals (4l)", "2025-05-12": "weak S&P signal (4l)"}


def state(sym):
    m = pd.read_csv(OUT / f"td_gamma_{sym}.csv", parse_dates=["date"]).set_index("date").sort_index()
    s = pd.DataFrame(index=m.index)
    s["spot"] = m.spot
    s["g_pct"] = (m.gex_classic / (m.spot * (m.call_oi + m.put_oi) * 100)).rolling(252, min_periods=120).rank(pct=True)
    s["tot_pct"] = (-m.gex_short / (m.spot * (m.call_oi + m.put_oi) * 100)).rolling(252, min_periods=120).rank(pct=True)
    s["flip"], s["call_wall"], s["put_wall"] = m.flip_classic, m.call_wall, m.put_wall
    # no flip within +-20% of spot: the whole local profile has one sign -> far above (+20) or far below (-20)
    s["to_flip_pct"] = (100 * (m.spot / m.flip_classic - 1)).fillna(pd.Series(np.where(m.gex_classic > 0, 20.0, -20.0), index=m.index))
    s["to_call_wall_pct"] = 100 * (m.call_wall / m.spot - 1)
    s["exp5_share"] = m.gamma_share_5d
    if "near_oi_share" in m:
        s["near_pct"] = m.near_oi_share.rolling(252, min_periods=120).rank(pct=True)
        s["iv_pct"] = m.atm_iv_30d.rolling(252, min_periods=120).rank(pct=True)
    return s


def events(sym):
    c = load_bars(sym).close
    s = state(sym)
    r = np.log(c).diff()
    up = pd.Series(burst_days(c, 1), index=c.index)
    rx = {c.index[c.index.searchsorted(pd.Timestamp(d))] for d in REACTIONS_2020} if sym == "TSLA" else set()
    rows = []
    for t in up.index[up.to_numpy() & (up.index >= START)]:
        i = c.index.get_loc(t)
        prev = c.index[i - 1]
        if prev not in s.index:
            continue
        b = s.loc[prev]
        two = np.log(c.iloc[min(i + 1, len(c) - 1)] / c.iloc[i - 1])
        after = s.index[s.index > t][4] if (s.index > t).sum() > 4 else s.index[-1]
        rows.append({"burst": t.date(), "weekday": t.day_name()[:3], "move_1d": 100 * r.iloc[i], "move_2d": 100 * two,
                     "report": t in rx, "note": FLAGGED.get(str(t.date()), ""),
                     "own_g_pct": b.g_pct, "total_gamma_pct": b.tot_pct, "above_flip": b.to_flip_pct > 0,
                     "to_flip_pct": b.to_flip_pct, "call_wall": b.call_wall, "to_call_wall_pct": b.to_call_wall_pct,
                     "exp5_share": b.exp5_share, "near_oi_pct": b.get("near_pct", np.nan), "iv_pct": b.get("iv_pct", np.nan),
                     "closed_above_wall": c.iloc[min(i + 1, len(c) - 1)] > b.call_wall,
                     "call_wall_5d_later": s.loc[after, "call_wall"]})
    return pd.DataFrame(rows), s


def profile(e, s):
    base = s[s.index >= START].dropna(subset=["g_pct"])
    q = lambda v: pd.cut(v, [0, 1 / 3, 2 / 3, 1], labels=["put-heavy", "balanced", "call-heavy"], include_lowest=True)
    out = pd.DataFrame({
        "before up-bursts": [len(e), (e.above_flip).mean(), e.to_flip_pct.median(), e.to_call_wall_pct.median(),
                             (q(e.own_g_pct) == "put-heavy").mean(), (q(e.own_g_pct) == "balanced").mean(),
                             (q(e.own_g_pct) == "call-heavy").mean(), e.total_gamma_pct.median(), e.exp5_share.median()],
        "all days": [len(base), (base.to_flip_pct > 0).mean(), base.to_flip_pct.median(), base.to_call_wall_pct.median(),
                     (q(base.g_pct) == "put-heavy").mean(), (q(base.g_pct) == "balanced").mean(),
                     (q(base.g_pct) == "call-heavy").mean(), base.tot_pct.median(), base.exp5_share.median()]},
        index=["n", "share above own flip", "median % above flip", "median % below call wall", "share put-heavy",
               "share balanced", "share call-heavy", "median total-gamma pct", "median share expiring <=5d"])
    if "near_pct" in s:
        out.loc["share with low near-money OI (bottom third)"] = [(e.near_oi_pct <= 1 / 3).mean(), (base.near_pct <= 1 / 3).mean()]
        out.loc["median IV percentile"] = [e.iv_pct.median(), base.iv_pct.median()]
    return out


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    pd.set_option("display.max_rows", 200)
    sym = (sys.argv[1:] or ["TSLA"])[0]
    e, s = events(sym)
    e.to_csv(OUT / f"burst_gamma_{sym}.csv", index=False)
    print(e.round(2).to_string(index=False))
    print("\nprofile the day before an up-burst vs all days (2021+)\n" + profile(e, s).round(3).to_string())
    nr = e[~e.report]
    print(f"\nexcluding report days (n={len(nr)}): share above flip {nr.above_flip.mean():.0%}, put-heavy "
          f"{(nr.own_g_pct <= 1 / 3).mean():.0%}, median % below call wall {nr.to_call_wall_pct.median():.1f}")
