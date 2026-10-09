"""After a leg: what makes the S&P stall, and does gamma have to 'reset' first?

Leg       = first day of a run of top-decile 10-day forward S&P returns (>= 10d apart).
Leg end   = leg start + 10 trading days.
Reset     = GEX percentile falls to <= 0.30.
Built     = 'gamma built without price': 10-day mean GEX pct >= 0.70 while the
            S&P moved < 1.5% (abs) over those 10 days.
Consolidation (next 20d) = 20-day close range in the bottom 30% of all 20-day ranges.

A. At the end of a leg: what follows, split by GEX pct at the leg end (pinned vs not)?
B. Before a leg starts: was there a reset in the prior 20 days (vs random days)?
C. From a 'built' state: odds of another leg, consolidation, and whether legs come
   before or after a reset; time to reset.
"""
import numpy as np
import pandas as pd
from scipy.stats import binom

from forecast import build

H, W = 10, 20


def prep(f):
    c = f.c
    lc = np.log(c)
    x = pd.DataFrame(index=f.index)
    x["fwd10"] = lc.shift(-H) - lc
    x["fwd20"] = lc.shift(-W) - lc
    top = x.fwd10.quantile(0.9)
    x["leg_day"] = x.fwd10 > top
    rng = (c[::-1].rolling(W).max()[::-1].shift(-1) - c[::-1].rolling(W).min()[::-1].shift(-1)) / c
    x["range20"] = rng
    x["consol"] = rng < rng.quantile(0.3)
    x["dd20"] = c[::-1].rolling(W).min()[::-1].shift(-1) / c - 1
    x["gex_pct"], x["dix_pct"], x["vix"] = f.gex_pct, f.dix_pct, f.VIX
    x["gex10"] = f.gex_pct.rolling(10).mean()
    x["ret10_past"] = lc - lc.shift(10)
    x["built"] = (x.gex10 >= 0.70) & (x.ret10_past.abs() < 0.015)
    x["reset"] = f.gex_pct <= 0.30
    # gamma ran up from its 7-day low by >= 0.5 while the S&P moved little over the same 7 days
    x["gex_rise7"] = f.gex_pct - f.gex_pct.rolling(7).min()
    x["ret7_past"] = lc - lc.shift(7)
    x["ran"] = (x.gex_rise7 >= 0.5) & x.ret7_past.between(-0.01, 0.025)
    leg = x.leg_day.to_numpy()
    starts, last = [], -99
    for i in np.where(leg & ~np.r_[False, leg[:-1]])[0]:
        if i - last >= H:
            starts.append(i)
            last = i
    x["leg_start"] = False
    x.iloc[starts, x.columns.get_loc("leg_start")] = True
    # leg within next W days (starting day 1..W)
    ls = x.leg_start.to_numpy()
    x["leg_next20"] = [ls[i + 1:i + 1 + W].any() for i in range(len(x))]
    x["reset_prev20"] = x.reset.rolling(W, min_periods=1).max().shift(1).astype(bool)
    return x


def leg_end_table(x):
    idx = np.where(x.leg_start)[0] + H
    idx = idx[idx < len(x) - W]
    e = x.iloc[idx].copy()
    e["pinned"] = np.where(e.gex_pct >= 0.9, "GEX>=0.90 at leg end", "GEX<0.90 at leg end")
    return e.groupby("pinned").agg(n=("fwd20", "size"), next_leg_20d=("leg_next20", "mean"),
                                   fwd20_pct=("fwd20", lambda s: 100 * s.mean()), consolidation=("consol", "mean"),
                                   median_dd20_pct=("dd20", lambda s: 100 * s.median()))


def reset_before_legs(x):
    legs = x[x.leg_start & x.reset_prev20.notna()]
    base = x.reset_prev20.mean()
    k, n = int(legs.reset_prev20.sum()), len(legs)
    return {"legs": n, "share_with_reset_in_prior_20d": k / n, "random_day_share": base,
            "p_more": binom.sf(k - 1, n, base)}


def from_built(x):
    b = x.built.to_numpy() & ~np.r_[False, x.built.to_numpy()[:-1]]
    ev, last = [], -99
    for i in np.where(b)[0]:
        if i - last >= H and i < len(x) - 40:
            ev.append(i)
            last = i
    rows = []
    rs, ls = x.reset.to_numpy(), x.leg_start.to_numpy()
    for i in ev:
        r_ = np.where(rs[i + 1:i + 41])[0]
        l_ = np.where(ls[i + 1:i + 41])[0]
        rows.append({"date": x.index[i], "days_to_reset": r_[0] + 1 if len(r_) else np.nan,
                     "days_to_leg": l_[0] + 1 if len(l_) else np.nan,
                     "leg_before_reset": bool(len(l_) and (not len(r_) or l_[0] < r_[0])),
                     "leg_after_reset": bool(len(l_) and len(r_) and l_[0] >= r_[0]),
                     "leg_next20": x.leg_next20.iloc[i], "consol": x.consol.iloc[i], "fwd20": x.fwd20.iloc[i],
                     "dd20": x.dd20.iloc[i]})
    return pd.DataFrame(rows)


def first_days(mask, gap=H):
    m = mask.to_numpy()
    out, last = np.zeros(len(m), bool), -99
    for i in np.where(m & ~np.r_[False, m[:-1]])[0]:
        if i - last >= gap:
            out[i], last = True, i
    return out


def ran_table(x):
    ev = x[first_days(x.ran)]
    k, n = int(ev.leg_next20.sum()), len(ev)
    return {"episodes": n, "p_leg_20d": k / n, "base": x.leg_next20.mean(),
            "p_less": binom.cdf(k, n, x.leg_next20.mean()), "consolidation": ev.consol.mean(),
            "consol_base": x.consol.mean(), "fwd20_pct": 100 * ev.fwd20.mean(), "median_dd20_pct": 100 * ev.dd20.median()}


def summarize_built(e, x, lab):
    base_leg, base_con = x.leg_next20.mean(), x.consol.mean()
    print(f"\nC. 'gamma built, price flat' events, {lab}: n={len(e)}")
    print(f"   P(up-leg starts within 20d) {e.leg_next20.mean():.0%} vs any day {base_leg:.0%} "
          f"(p_less={binom.cdf(int(e.leg_next20.sum()), len(e), base_leg):.2f})")
    print(f"   P(consolidation next 20d) {e.consol.mean():.0%} vs any day {base_con:.0%} "
          f"(p_more={binom.sf(int(e.consol.sum()) - 1, len(e), base_con):.2f})")
    print(f"   S&P next 20d mean {100 * e.fwd20.mean():+.2f}% (any day {100 * x.fwd20.mean():+.2f}%), median worst dip {100 * e.dd20.median():.1f}%")
    print(f"   reset (GEX<=0.30) within 40d: {e.days_to_reset.notna().mean():.0%}, median {e.days_to_reset.median():.0f} days "
          f"(IQR {e.days_to_reset.quantile(.25):.0f}-{e.days_to_reset.quantile(.75):.0f})")
    with_leg = e[e.days_to_leg.notna()]
    print(f"   of {len(with_leg)} events followed by a leg within 40d: leg came AFTER a reset {with_leg.leg_after_reset.mean():.0%}, "
          f"BEFORE any reset {with_leg.leg_before_reset.mean():.0%}; median days to leg {with_leg.days_to_leg.median():.0f}")


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    f = build()
    x = prep(f)
    for start, lab in (("2012-01-01", "2012+"), ("2019-10-01", "2019Q4+")):
        xx = x[x.index >= start].dropna(subset=["fwd20"])
        print(f"\n===== {lab}")
        print("A. what follows a leg, by gamma at the leg end\n" + leg_end_table(xx).round(3).to_string())
        print(f"   any day: next leg 20d {xx.leg_next20.mean():.0%}, consolidation {xx.consol.mean():.0%}")
        print("B. legs preceded by a reset (GEX<=0.30) in the prior 20 days:", {k: round(v, 3) for k, v in reset_before_legs(xx).items()})
        summarize_built(from_built(xx), xx, lab)
        print("D. gamma ran +0.5 from its 7-day low with the S&P 7d in [-1%, +2.5%]:",
              {k: round(v, 3) for k, v in ran_table(xx).items()})
    now = x.iloc[-1]
    print(f"\nNOW {x.index[-1].date()}: GEX pct {now.gex_pct:.2f}, 10d mean {now.gex10:.2f}, S&P 10d {100 * now.ret10_past:+.2f}%, "
          f"DIX pct {now.dix_pct:.2f}, VIX {now.vix:.1f}; built={bool(now.built)}; last reset "
          f"{x.index[x.reset.to_numpy()][-1].date()}; last 'built' day {x.index[x.built.to_numpy()][-1].date()}; "
          f"'ran' days in last 10: {[d.strftime('%m-%d') for d in x.index[-10:][x.ran.to_numpy()[-10:]]]}")
