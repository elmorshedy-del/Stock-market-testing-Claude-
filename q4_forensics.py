"""Forensics of a stock's Q4 catch-up legs vs SPY.

Catch-up years: the stock lagged SPY by > 10 pts (log) at Sep 30. For every
Q4 up-burst (+5% 1d or +9% 2d) and for each year's main catch-up leg (the
10-day window with the largest return relative to SPY), extract:
  calendar   date, weekday, day of month, trading days to/from monthly opex,
             opex-week bucket, earnings reaction (+-1d), US election (+-2d)
  the burst  1d/2d move, share of the move made in the opening gap, next-5d
             follow-through
  the stock  20/40d return, drawdown from 52w high, vs 200d MA, 20d vol,
             vol ratio 20/120, volume vs 50d median, YTD gap vs SPY
  market     S&P GEX pct, DIX pct, VIX, VIX/VIX3M, S&P 20d return and drawdown
All state variables are measured the day BEFORE the burst. Control group:
Q4 up-bursts in years that were not lagging. The stock's own option gamma
history is not available for free, so it cannot be included.
Usage: python q4_forensics.py TSLA
"""
import sys

import numpy as np
import pandas as pd

from common import load_bars
from forecast import build
from stock_now import burst_days

# Tesla Q3 reports were released after the close; these are the next-day reaction sessions
# (public report dates). Other tickers fall back to the volume-based detector.
Q3_REACTION = {"TSLA": ["2012-11-06", "2013-11-06", "2014-11-06", "2015-11-04", "2016-10-27", "2017-11-02",
                        "2018-10-25", "2019-10-24", "2020-10-22", "2021-10-21", "2022-10-20", "2023-10-19",
                        "2024-10-24", "2025-10-23"]}
ELECTIONS = ["2012-11-06", "2014-11-04", "2016-11-08", "2018-11-06", "2020-11-03", "2022-11-08", "2024-11-05"]


def earnings_days(d):
    """Highest-volume day (>= 1.5x) in each reporting window: mid-Jan..mid-Feb, mid-Apr..mid-May,
    mid-Jul..mid-Aug, mid-Oct..mid-Nov (Tesla reported Q3 in early November in 2012-2015)."""
    vx = d.volume / d.volume.rolling(50).median().shift(1)
    out = []
    for y in sorted(set(d.index.year)):
        for m in (1, 4, 7, 10):
            w = vx[f"{y}-{m:02d}-15":f"{y}-{m + 1:02d}-12"]
            if len(w) and w.max() >= 1.5:
                out.append(w.idxmax())
    return out


def stock_state(d, spy):
    c, lc = d.close, np.log(d.close)
    r = lc.diff()
    s = pd.DataFrame(index=d.index)
    s["ret20"], s["ret40"] = lc.diff(20), lc.diff(40)
    s["dd_52w"] = c / c.rolling(252, min_periods=60).max() - 1
    s["vs_200d"] = c / c.rolling(200, min_periods=60).mean() - 1
    s["rv20"] = r.rolling(20).std() * np.sqrt(252)
    s["rv_ratio"] = r.rolling(20).std() / r.rolling(120).std()
    s["vol_x"] = d.volume / d.volume.rolling(50).median()
    ly = spy.reindex(d.index).ffill()
    ytd = []
    for t in d.index:
        y0 = c[:f"{t.year - 1}-12-31"]
        s0 = ly[:f"{t.year - 1}-12-31"]
        ytd.append(np.log(c[t] / y0.iloc[-1]) - np.log(ly[t] / s0.iloc[-1]) if len(y0) and len(s0) else np.nan)
    s["ytd_gap"] = ytd
    return s


def market_state(f):
    m = pd.DataFrame(index=f.index)
    m["spx_gex_pct"], m["dix_pct"], m["vix"], m["vix_vix3m"] = f.gex_pct, f.dix_pct, f.VIX, f.ts
    m["spx_ret20"] = np.log(f.c).diff(20)
    m["spx_dd"] = f.c / f.c.rolling(252).max() - 1
    return m


def calendar(idx):
    opex = pd.date_range(idx[0], idx[-1] + pd.Timedelta(days=60), freq="WOM-3FRI")
    bdays = pd.bdate_range(idx[0], idx[-1] + pd.Timedelta(days=60))
    nxt = [int(bdays.searchsorted(opex[opex >= t][0]) - bdays.searchsorted(t)) for t in idx]
    prv = [int(bdays.searchsorted(t) - bdays.searchsorted(opex[opex <= t][-1])) if (opex <= t).any() else np.nan for t in idx]
    ow = set(opex.to_period("W-FRI"))
    wk = idx.to_period("W-FRI")
    bucket = ["opex week" if p in ow else "week before opex week" if p + 1 in ow else "week after opex" if p - 1 in ow
              else "other weeks" for p in wk]
    return pd.DataFrame({"tdays_to_opex": nxt, "tdays_since_opex": prv, "opex_bucket": bucket}, index=idx)


def events(sym):
    d = load_bars(sym)
    spy = load_bars("SPY").close
    c = d.close
    f = build()
    st, mk, cal = stock_state(d, spy), market_state(f).reindex(d.index).ffill(limit=3), calendar(d.index)
    ed = [pd.Timestamp(x) for x in Q3_REACTION[sym]] if sym in Q3_REACTION else earnings_days(d)
    ub = pd.Series(burst_days(c, 1), index=c.index)
    r = np.log(c).diff()
    rows = []
    for y in range(2012, 2026):
        q = c[f"{y}-10-01":f"{y}-12-31"]
        if len(q) < 50:
            continue
        gap = st.ytd_gap.loc[:f"{y}-09-30"].iloc[-1]
        sp = spy.reindex(c.index).ffill()
        rel = (np.log(c) - np.log(sp)).loc[q.index[0] - pd.Timedelta(days=5):q.index[-1]]
        q4_rel = rel.iloc[-1] - rel.loc[:f"{y}-09-30"].iloc[-1]
        w = (rel.shift(-10) - rel).loc[q.index[0]:q.index[-11]]
        leg0 = w.idxmax()
        legs = [("leg", leg0, w.max())]
        for t in q.index[ub.loc[q.index].to_numpy()]:
            legs.append(("burst", t, np.nan))
        for kind, t, legrel in legs:
            i = c.index.get_loc(t)
            p = c.index[i - 1]
            e = {"year": y, "lagging": gap < -0.10, "kind": kind, "date": t.date(), "weekday": t.day_name()[:3],
                 "dom": t.day, "month": t.month, "q4_rel_pct": 100 * q4_rel, "ytd_gap_sep30_pct": 100 * gap,
                 "move_1d_pct": 100 * r.iloc[i], "move_2d_pct": 100 * np.log(c.iloc[i + 1] / c.iloc[i - 1]),
                 "gap_share": np.log(d.open.iloc[i] / c.iloc[i - 1]) / r.iloc[i] if r.iloc[i] else np.nan,
                 "next5_pct": 100 * np.log(c.iloc[min(i + 5, len(c) - 1)] / c.iloc[i]),
                 "leg10_rel_pct": 100 * legrel if kind == "leg" else np.nan,
                 "earnings_pm1": any(-1 <= c.index.searchsorted(x) - i <= 2 for x in ed if abs((x - t).days) < 10),
                 "election_pm2": any(abs(i - c.index.searchsorted(pd.Timestamp(x))) <= 2 for x in ELECTIONS)}
            e.update(cal.loc[t].to_dict())
            e.update({k: v for k, v in st.loc[p].items()})
            e.update({k: v for k, v in mk.loc[p].items()})
            rows.append(e)
    return pd.DataFrame(rows), st, mk, cal


if __name__ == "__main__":
    pd.set_option("display.width", 260)
    pd.set_option("display.max_columns", 60)
    sym = (sys.argv[1:] or ["TSLA"])[0]
    ev, st, mk, cal = events(sym)
    ev.to_csv(f"out/q4_forensics_{sym}.csv", index=False)
    show = ["year", "kind", "date", "weekday", "dom", "move_1d_pct", "move_2d_pct", "gap_share", "next5_pct", "leg10_rel_pct",
            "opex_bucket", "tdays_to_opex", "tdays_since_opex", "earnings_pm1", "election_pm2"]
    show2 = ["year", "kind", "date", "ret20", "ret40", "dd_52w", "vs_200d", "rv20", "rv_ratio", "vol_x", "ytd_gap",
             "spx_gex_pct", "dix_pct", "vix", "vix_vix3m", "spx_ret20", "spx_dd"]
    lag = ev[ev.lagging]
    print(f"=== {sym} CATCH-UP years (lagging SPY > 10 pts at Sep 30): Q4 legs and bursts")
    print(lag[show].round(2).to_string(index=False))
    print("\nstate the day before:")
    print(lag[show2].round(2).to_string(index=False))
    num = ["dom", "tdays_to_opex", "tdays_since_opex", "gap_share", "next5_pct", "ret20", "ret40", "dd_52w", "vs_200d",
           "rv20", "rv_ratio", "vol_x", "spx_gex_pct", "dix_pct", "vix", "vix_vix3m", "spx_ret20", "spx_dd"]
    grp = ev.assign(group=np.where(ev.lagging, "catch-up yrs", "other yrs"))
    print("\nmedians: catch-up years vs other years (all Q4 legs+bursts)")
    print(grp.groupby("group")[num].median().T.round(2).to_string())
    print("\nshares:")
    sh = grp.groupby("group").agg(n=("kind", "size"), earnings=("earnings_pm1", "mean"), election=("election_pm2", "mean"),
                                  in_opex_week=("opex_bucket", lambda s: (s == "opex week").mean()),
                                  week_before=("opex_bucket", lambda s: (s == "week before opex week").mean()),
                                  week_after=("opex_bucket", lambda s: (s == "week after opex").mean()),
                                  oct=("month", lambda s: (s == 10).mean()), nov=("month", lambda s: (s == 11).mean()),
                                  dec=("month", lambda s: (s == 12).mean()), first_half_month=("dom", lambda s: (s <= 15).mean()))
    print(sh.round(2).to_string())
    now = st.index[-1]
    print(f"\nNOW {now.date()}: " + ", ".join(f"{k}={v:.2f}" for k, v in st.loc[now].items()) + " | " +
          ", ".join(f"{k}={v:.2f}" for k, v in mk.reindex([now]).ffill().iloc[0].items() if v == v) +
          f" | opex bucket {cal.loc[now, 'opex_bucket']}, {cal.loc[now, 'tdays_to_opex']} tdays to opex")
