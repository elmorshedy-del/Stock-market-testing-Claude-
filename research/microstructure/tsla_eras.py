"""Re-run the Tesla options-related tests split at the options-regime change.

Tesla options activity changed character around 2020 (retail inflows, the
Aug-2020 5:1 split, short-dated OTM call buying, then daily-expiry/0DTE era),
so every test is reported for pre-2020 and 2020+ separately:
  1. burst frequency and size
  2. bursts by week relative to monthly opex, and by weekday (weekly expiries)
  3. earnings reactions: up/down burst odds, |day-0| move, 10-day drift vs SPY
  4. Q4 catch-up years by era
  5. grind-up analogs with the analog pool restricted to 2020+
Report reaction days 2020+ are Tesla's published dates (after-close reports ->
next session), each checked against a volume spike.
"""
import numpy as np
import pandas as pd
from scipy.stats import binom

from common import load_bars
from q4_forensics import Q3_REACTION
from stock_now import burst_days, test_grind, test_opex, test_q4_catchup

REACTIONS_2020 = ["2020-01-30", "2020-04-30", "2020-07-23", "2020-10-22", "2021-01-28", "2021-04-27", "2021-07-27",
                  "2021-10-21", "2022-01-27", "2022-04-21", "2022-07-21", "2022-10-20", "2023-01-26", "2023-04-20",
                  "2023-07-20", "2023-10-19", "2024-01-25", "2024-04-24", "2024-07-24", "2024-10-24", "2025-01-30",
                  "2025-04-23", "2025-07-24", "2025-10-23"]
ERAS = (("pre-2020", "2012-01-01", "2019-12-31"), ("2020+", "2020-01-01", "2026-12-31"))


def bursts_by_era(c):
    rows = {}
    for lab, a, b in ERAS:
        cc = c[a:b]
        up, dn = burst_days(cc, 1).sum(), burst_days(cc, -1).sum()
        yrs = len(cc) / 252
        rows[lab] = {"years": round(yrs, 1), "up_per_year": up / yrs, "down_per_year": dn / yrs,
                     "daily_vol": np.log(cc).diff().std() * np.sqrt(252)}
    return pd.DataFrame(rows).T


def weekday_test(d, a, b):
    """Up/down bursts by weekday (Friday = weekly expiry). gap_share = part of the
    burst-day move made in the opening gap (weekend news shows up as gap)."""
    dd = d[a:b]
    cc = dd.close
    r = np.log(cc).diff()
    gap = np.log(dd.open / cc.shift())
    wd = cc.index.day_name()
    out = {}
    for name, sgn in (("up", 1), ("down", -1)):
        b_ = pd.Series(burst_days(cc, sgn), index=cc.index)
        n = int(b_.sum())
        for day in ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday"):
            m = (wd == day)
            k = int(b_[m].sum())
            gs = (gap[b_ & m] / r[b_ & m]).median() if k else np.nan
            out[(name, day)] = {"bursts": k, "lift": (k / n) / m.mean(), "p_more": binom.sf(k - 1, n, m.mean()),
                                "median_gap_share": gs}
    return pd.DataFrame(out).T


def earnings_by_era(d, spy, days):
    c = d.close
    s = spy.reindex(c.index).ffill()
    r = np.log(c).diff()
    vx = d.volume / d.volume.rolling(50).median().shift(1)
    rows = []
    for x in days:
        i = c.index.searchsorted(pd.Timestamp(x))
        if i + 10 >= len(c):
            continue
        day0 = r.iloc[i]
        rel10 = (np.log(c.iloc[i + 9] / c.iloc[i]) - np.log(s.iloc[i + 9] / s.iloc[i]))
        rows.append({"date": c.index[i].date(), "vol_x": vx.iloc[i], "day0": day0,
                     "drift_after_signed": np.sign(day0) * rel10, "rel10_from_eve": np.log(c.iloc[i + 9] / c.iloc[i - 1]) -
                     np.log(s.iloc[i + 9] / s.iloc[i - 1])})
    e = pd.DataFrame(rows)
    return e


def summarize_earn(e):
    return pd.Series({"n": len(e), "mean_abs_day0_%": 100 * e.day0.abs().mean(), "p_day0_up5": (e.day0 >= 0.05).mean(),
                      "p_day0_dn5": (e.day0 <= -0.05).mean(),
                      "mean_drift_after_signed_bp": 1e4 * e.drift_after_signed.mean(),
                      "share_continuing": (e.drift_after_signed > 0).mean()})


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    d, spy = load_bars("TSLA"), load_bars("SPY").close
    c = d.close
    print("1. bursts per year and volatility by era\n" + bursts_by_era(c).round(2).to_string())
    for lab, a, b in ERAS:
        res = test_opex(c[:b], a)
        print(f"\n2. {lab}: up-bursts by week vs monthly opex\n" + res["up"][["bursts", "lift", "p_more"]].round(3).to_string())
        print(f"   {lab}: down-bursts\n" + res["down"][["bursts", "lift", "p_more"]].round(3).to_string())
        print(f"   {lab}: bursts by weekday\n" + weekday_test(d, a, b).round(3).to_string())
    # weekday effects without earnings reactions (Tesla reports Wed after close -> Thursday)
    cc = c["2020-01-01":]
    rx = cc.index.isin([cc.index[cc.index.searchsorted(pd.Timestamp(x))] for x in REACTIONS_2020])
    wd = cc.index.day_name()
    print("\n2b. 2020+ excluding report days")
    for name, sgn in (("up", 1), ("down", -1)):
        b_ = pd.Series(burst_days(cc, sgn), index=cc.index) & ~rx
        n = int(b_.sum())
        for day in ("Monday", "Thursday", "Friday"):
            m = (wd == day) & ~rx
            k, sh = int(b_[m].sum()), m.sum() / (~rx).sum()
            print(f"   {name:4s} {day:9s} {k:2d}/{n}  lift {(k / n) / sh:.2f}  p_more {binom.sf(k - 1, n, sh):.3f}")
    e20 = earnings_by_era(d, spy, REACTIONS_2020)
    print(f"\n3. all quarterly reports 2020+ (volume check: min vol_x {e20.vol_x.min():.2f}, median {e20.vol_x.median():.2f})")
    print(summarize_earn(e20).round(3).to_string())
    x = e20.drift_after_signed
    print(f"   drift t-stat {x.mean() / (x.std() / np.sqrt(len(x))):.2f}; P(>= {int((x > 0).sum())} of {len(x)} continuing | 50%) = "
          f"{binom.sf(int((x > 0).sum()) - 1, len(x), 0.5):.2f}")
    q3 = earnings_by_era(d, spy, Q3_REACTION["TSLA"])
    q3["era"] = np.where(pd.to_datetime(q3.date) < pd.Timestamp("2020-01-01"), "pre-2020", "2020+")
    print("\n   Q3 reports by era\n" + q3.groupby("era").apply(summarize_earn, include_groups=False).round(3).to_string())
    print(q3.assign(day0=lambda x: (100 * x.day0).round(1), rel10_from_eve=lambda x: (100 * x.rel10_from_eve).round(1))
          [["date", "era", "vol_x", "day0", "rel10_from_eve"]].round(2).to_string(index=False))
    q4 = test_q4_catchup(c, spy)
    q4["era"] = np.where(q4.year < 2020, "pre-2020", "2020+")
    print("\n4. Q4 vs SPY by era (gap at Sep 30, Q4 relative)\n" + q4.round(1).to_string(index=False))
    for lab, a, _ in ERAS[1:]:
        g = test_grind(c, "2025-09-10")
        # restrict the analog pool to the era by running on the era slice (keeps a warm-up year)
        g2 = test_grind(c[pd.Timestamp(a) - pd.Timedelta(days=250):], "2025-09-10", k=25)
        print(f"\n5. grind-up analogs, pool {lab} (k=25): P(up-burst 10d) {g2['analog_p_up']:.0%} vs base {g2['base_p_up']:.0%} "
              f"(p={g2['p_value_up']:.2f}); down {g2['analog_p_down']:.0%} vs {g2['base_p_down']:.0%}   "
              f"[full pool: up {g['analog_p_up']:.0%} vs {g['base_p_up']:.0%}]")
