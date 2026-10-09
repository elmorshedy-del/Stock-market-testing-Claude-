"""Where a stock stands today, plus tests of three trader observations.

  A. Opex timing: do bursts cluster in the week INTO monthly opex vs after?
  B. Catch-up: does the stock make its year in one or two bursts, and does one
     usually come late in the year?
  C. Grind-up analog: does a quiet, steady 40-day climb (like Jul-Aug 2025
     before the 2025-09-11 burst) raise burst odds over the next 10 days?
  D. Today's state: S&P gamma ladder rungs, earnings, option map for the next
     monthly expiry.
Burst = +5% in 1 day or +9% in 2 days (down-bursts mirrored). Stats compare
with the share of trading days in each bucket (binomial tests).
Usage: python stock_now.py TSLA
"""
import sys

import numpy as np
import pandas as pd
from scipy.stats import binom

import options_flow as of
from backtest import third_fridays
from burst_check import signals
from common import load_bars
from single_name import frames

LOOK = 10


def burst_days(c, sign=1):
    r = np.log(c).diff() * sign
    r2 = np.log(c / c.shift(2)) * sign
    hit = ((r >= 0.05) | (r2 >= 0.09)).to_numpy()
    out, last = np.zeros(len(c), bool), -99
    for i in np.where(hit)[0]:
        j = i - 1 if (r2.iloc[i] >= 0.09 and r.iloc[i] < 0.05) else i
        if j - last > 3:
            out[j] = True
        last = i
    return out


def opex_buckets(idx):
    opex = sorted(third_fridays(idx))
    wk = idx.to_period("W-FRI")
    ow = {pd.Timestamp(o).to_period("W-FRI"): k for k, o in enumerate(opex)}
    lab = []
    for p in wk:
        if p in ow:
            lab.append("opex week")
        elif p + 1 in ow:
            lab.append("week before opex week")
        elif p - 1 in ow:
            lab.append("week after opex")
        else:
            lab.append("other weeks")
    return np.array(lab)


def test_opex(c, start):
    c = c[c.index >= start]
    lab = opex_buckets(c.index)
    res = {}
    for name, sgn in (("up", 1), ("down", -1)):
        b = burst_days(c, sgn)
        rows = {}
        for k in ("week before opex week", "opex week", "week after opex", "other weeks"):
            share = (lab == k).mean()
            n = int(b[lab == k].sum())
            rows[k] = {"bursts": n, "share_of_bursts": n / b.sum(), "share_of_days": share,
                       "lift": (n / b.sum()) / share, "p_more": binom.sf(n - 1, int(b.sum()), share)}
        res[name] = pd.DataFrame(rows).T
    return res


def test_catchup(c, spy):
    rows = []
    for y in range(2012, 2026):
        cy, sy = c[str(y)], spy[str(y)]
        if len(cy) < 200:
            continue
        r2 = np.log(cy / cy.shift(2)).dropna()
        top, used = [], []
        for d, v in r2.sort_values(ascending=False).items():
            if all(abs((d - u).days) > 5 for u in used):
                top.append((d, v)); used.append(d)
            if len(top) == 2:
                break
        yr = np.log(cy.iloc[-1] / c[:f"{y - 1}-12-31"].iloc[-1])
        rows.append({"year": y, "tsla_pct": 100 * yr, "spy_pct": 100 * np.log(sy.iloc[-1] / spy[:f"{y - 1}-12-31"].iloc[-1]),
                     "top2_bursts_pct": 100 * sum(v for _, v in top),
                     "rest_of_year_pct": 100 * (yr - sum(v for _, v in top)),
                     "biggest_burst": top[0][0].date(), "q4_burst_in_top2": any(d.month >= 10 for d, _ in top)})
    return pd.DataFrame(rows)


def test_q4_catchup(c, spy):
    rows = []
    for y in range(2011, 2026):
        e0, s0 = c[:f"{y - 1}-12-31"].iloc[-1], spy[:f"{y - 1}-12-31"].iloc[-1]
        cs, ss = c[:f"{y}-09-30"].iloc[-1], spy[:f"{y}-09-30"].iloc[-1]
        ce, se = c[:f"{y}-12-31"].iloc[-1], spy[:f"{y}-12-31"].iloc[-1]
        rows.append({"year": y, "gap_at_sep30": 100 * (np.log(cs / e0) - np.log(ss / s0)),
                     "q4_rel_to_spy": 100 * (np.log(ce / cs) - np.log(se / ss)), "q4": 100 * np.log(ce / cs)})
    return pd.DataFrame(rows)


def earnings_bursts(d):
    """Earnings reaction ~ highest-volume day (>=1.5x) in the 2nd half of Jan/Apr/Jul/Oct."""
    c = d.close
    vx = d.volume / d.volume.rolling(50).median().shift(1)
    sel = d[d.index.month.isin([1, 4, 7, 10]) & (d.index.day >= 15) & (d.index.year >= 2012)]
    ed = [vx.loc[g.index].idxmax() for _, g in sel.groupby([sel.index.year, sel.index.month]) if vx.loc[g.index].max() >= 1.5]
    ub, db = pd.Series(burst_days(c, 1), index=c.index), pd.Series(burst_days(c, -1), index=c.index)
    win = [i for e in ed for i in c.index[max(0, c.index.get_loc(e) - 1):c.index.get_loc(e) + 2]]
    days = (c.index >= "2012-01-01").sum()
    r = np.log(c).diff()
    return {"n_reports": len(ed), "p_up_burst_pm1d": ub[win].sum() / len(ed), "p_down_burst_pm1d": db[win].sum() / len(ed),
            "base_p_up_any_3d": 3 * ub["2012":].sum() / days,
            "october_reactions_%": {str(e.date()): round(100 * r.loc[e], 1) for e in ed if e.month == 10}}


def features(c):
    lc = np.log(c)
    r = lc.diff()
    f = pd.DataFrame(index=c.index)
    f["ret20"], f["ret40"] = lc.diff(20), lc.diff(40)
    f["rv20"] = r.rolling(20).std() * np.sqrt(252)
    f["rv_ratio"] = r.rolling(20).std() / r.rolling(120).std()
    f["dd40"] = c / c.rolling(40).max() - 1
    t = np.arange(40.0)
    f["r2_40"] = lc.rolling(40).apply(lambda w: np.corrcoef(t, w)[0, 1] ** 2, raw=True)
    f["upshare20"] = (r > 0).rolling(20).mean()
    return f


def test_grind(c, ref_date, k=40):
    f = features(c).dropna()
    up = pd.Series(burst_days(c, 1), index=c.index).reindex(f.index)
    dn = pd.Series(burst_days(c, -1), index=c.index).reindex(f.index)
    fw = lambda s: pd.Series([s.iloc[i + 1:i + 1 + LOOK].any() for i in range(len(s))], index=s.index)
    fu, fd = fw(up), fw(dn)
    hist = f.iloc[:-LOOK - 1]
    hist = hist[hist.index >= "2012-01-01"]
    z = (hist - hist.mean()) / hist.std()
    now = (f.iloc[-1] - hist.mean()) / hist.std()
    dist = np.sqrt(((z - now) ** 2).sum(axis=1)).sort_values()
    picks = []
    for d in dist.index:
        if all(abs((d - p).days) > 14 for p in picks):
            picks.append(d)
        if len(picks) == k:
            break
    ref = f.loc[:ref_date].iloc[-1]
    return {"now": f.iloc[-1], "ref (day before 2025-09-11 burst)": ref,
            "analog_p_up": fu.loc[picks].mean(), "analog_p_down": fd.loc[picks].mean(),
            "base_p_up": fu.loc[hist.index].mean(), "base_p_down": fd.loc[hist.index].mean(),
            "analog_dates": [p.date() for p in sorted(picks)][-12:],
            "p_value_up": binom.sf(int(fu.loc[picks].sum()) - 1, k, fu.loc[hist.index].mean())}


def next_expiry_map(sym):
    S, t0, q, df = of.load_chain(sym)
    opex = [o for o in sorted(third_fridays(pd.date_range("2026-01-01", "2027-12-31"))) if o.date() >= pd.Timestamp(t0, unit="s").date()][0]
    g = df[df.exp == opex.date()]
    oi = g.pivot_table(index="K", columns="cp", values="oi", aggfunc="sum").fillna(0)
    near = oi[(oi.index > 0.85 * S) & (oi.index < 1.2 * S)]
    e = of.exposures(g, S, "classic").groupby("K").gex.sum() / 1e6
    return {"expiry": str(opex.date()), "spot": S, "max_pain": of.max_pain(g),
            "top_call_oi": near.C.nlargest(5).astype(int).to_dict(), "top_put_oi": near.P.nlargest(5).astype(int).to_dict(),
            "top_gamma_strikes_$M": e.reindex(near.index).nlargest(5).round(0).to_dict(),
            "share_of_45d_call_oi_in_this_expiry": round(g[g.cp == "C"].oi.sum() / df[(df.cp == "C") & (df["T"] * 365 <= 45)].oi.sum(), 2)}


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    sym = (sys.argv[1:] or ["TSLA"])[0]
    c, spy = load_bars(sym).close, load_bars("SPY").close
    for start in ("2012-01-01", "2019-10-01"):
        res = test_opex(c, start)
        for k, v in res.items():
            print(f"\nA. {sym} {k}-bursts by week vs monthly opex, {start}+")
            print(v.round(3).to_string())
    cu = test_catchup(c, spy)
    print(f"\nB. {sym} year vs SPY and its two biggest 2-day bursts\n" + cu.round(1).to_string(index=False))
    upy = cu.tsla_pct > 0
    print(f"up years where the top-2 bursts made >= half the gain: {(upy & (cu.top2_bursts_pct >= 0.5 * cu.tsla_pct)).sum()} of {upy.sum()}; "
          f"top-2 includes a Q4 burst: {cu.q4_burst_in_top2.sum()} of {len(cu)} years (25% expected by chance)")
    ytd_t = 100 * np.log(c.iloc[-1] / c[:"2025-12-31"].iloc[-1])
    ytd_s = 100 * np.log(spy.iloc[-1] / spy[:"2025-12-31"].iloc[-1])
    print(f"2026 YTD (log): {sym} {ytd_t:+.1f}%  SPY {ytd_s:+.1f}%  gap {ytd_t - ytd_s:+.1f} pts")
    q4 = test_q4_catchup(c, spy)
    lag = q4.gap_at_sep30 < -10
    print("\nB2. Q4 after lagging SPY by >10 pts at Sep 30:\n" + q4[lag].round(1).to_string(index=False))
    print(f"lagging years beating SPY in Q4: {(q4.q4_rel_to_spy[lag] > 0).sum()} of {lag.sum()} "
          f"(all years: {(q4.q4_rel_to_spy > 0).mean():.0%}); mean Q4 rel {q4.q4_rel_to_spy[lag].mean():+.1f} vs {q4.q4_rel_to_spy[~lag].mean():+.1f}")
    print("\nB3. earnings reactions:", earnings_bursts(load_bars(sym)))
    g = test_grind(c, "2025-09-10")
    print("\nC. grind-up analogs (40 nearest by ret20/ret40/rv20/rv-ratio/drawdown/trend R2/up-day share)")
    print(pd.DataFrame({"now": g["now"], "before 2025-09-11": g["ref (day before 2025-09-11 burst)"]}).round(3).to_string())
    print(f"P(up-burst within {LOOK}d): analogs {g['analog_p_up']:.0%} vs base {g['base_p_up']:.0%} (p={g['p_value_up']:.2f}); "
          f"down-burst: analogs {g['analog_p_down']:.0%} vs base {g['base_p_down']:.0%}")
    print("most recent analog dates:", g["analog_dates"])
    f, t = frames(sym)
    sig = signals(f, t, sym)
    last = {k.split()[0]: bool(v[-LOOK:].any()) for k, v in sig.items()}
    print(f"\nD. state {t.index[-1].date()}: {sym} {t.c.iloc[-1]:.2f}, S&P GEX pct {f.gex_pct.iloc[-1]:.2f}, "
          f"DIX pct {f.dix_pct.iloc[-1]:.2f}, VIX {f.VIX.iloc[-1]:.1f}; rungs fired in last {LOOK}d: "
          f"{[k for k, v in last.items() if v] or 'none'}")
    for k, v in next_expiry_map(sym).items():
        print(f"  {k}: {v}")
