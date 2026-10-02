"""Forensics of MSFT's two big up-weeks (2026-04-13, 2026-07-27) with free data,
plus the current MSFT option map ahead of the next earnings.

Free data has no historical open interest, so past positioning is inferred from
the calendar (opex/earnings), the VIX complex (vanna fuel), and price/volume.
Usage: python fetch.py MSFT ^VIX ^VIX9D ^VIX3M ^VVIX ^SKEW ^GSPC QQQ  (or see REPORT.md)
"""
import numpy as np
import pandas as pd

import options_flow as of
from backtest import third_fridays
from common import load_bars

WEEKS = [("2026-04-13", "2026-04-17"), ("2026-07-27", "2026-07-31")]


def daily():
    m = load_bars("MSFT")
    d = pd.DataFrame({"msft": m.close, "spx": load_bars("^GSPC").close, "qqq": load_bars("QQQ").close,
                      **{k[1:]: load_bars(k).close for k in ("^VIX", "^VIX9D", "^VIX3M", "^VVIX")}})
    d = d.dropna(subset=["msft"])
    d["r"] = np.log(d.msft).diff()
    d["gap"] = np.log(m.open / m.close.shift())
    d["vol_x"] = m.volume / m.volume.rolling(50).median()
    d["dd_from_high"] = d.msft / d.msft.rolling(252, min_periods=20).max() - 1
    return d, m


def week_table(d):
    opex = third_fridays(d.index)
    rows = []
    for a, b in WEEKS:
        w = d.loc[a:b]
        pre = d.loc[:a].iloc[-2]
        rows.append({
            "week": a, "msft_%": 100 * w.r.sum(), "qqq_%": 100 * np.log(w.qqq.iloc[-1] / d.qqq.loc[:a].iloc[-2]),
            "contains_opex": any(x in opex for x in w.index),
            "max_gap_%": 100 * w.gap.abs().max(), "max_vol_x": w.vol_x.max(),
            "drawdown_before_%": 100 * pre.dd_from_high,
            "vix_4w_before": d.VIX.loc[:a].iloc[-21], "vix_start": pre.VIX, "vix_end": w.VIX.iloc[-1],
            "vix9d_minus_vix3m_start": pre.VIX9D - pre.VIX3M, "vvix_start": pre.VVIX,
        })
    return pd.DataFrame(rows).round(2)


def earnings_reactions(d):
    """Highest-volume day (>=1.6x) in the back half of Jan/Apr/Jul/Oct = earnings reaction."""
    sel = d[d.index.month.isin([1, 4, 7, 10]) & (d.index.day >= 18)].dropna(subset=["vol_x"])
    rows = []
    for _, g in sel.groupby([sel.index.year, sel.index.month]):
        if g.vol_x.max() < 1.6:
            continue
        j = d.index.get_loc(g.vol_x.idxmax())
        if j + 4 < len(d):
            rows.append({"day": d.index[j].date(), "day_%": 100 * d.r.iloc[j],
                         "5d_%": 100 * np.log(d.msft.iloc[j + 4] / d.msft.iloc[j - 1])})
    return pd.DataFrame(rows).round(1)


def current_map():
    S, t0, q, df = of.load_chain("MSFT")
    near = df[df["T"] * 365 <= 60]
    e = of.exposures(near, S, "classic")
    gex_by_exp = (e.assign(exp=e.exp.astype(str)).groupby("exp").gex.sum() / 1e6).round(0)
    ivs = {str(k): v["atm_iv"] for k, v in of.implied_move(df, S).items()}
    exps = sorted(ivs)
    # event vol: variance of the first post-earnings expiry minus the pre-earnings one
    # earningsTimestamp can be the last report; Start/End hold the upcoming one
    earn = pd.Timestamp(max(q.get(k, 0) for k in ("earningsTimestamp", "earningsTimestampStart")), unit="s").date()
    post = next(x for x in exps if pd.Timestamp(x).date() > earn)
    pre = exps[exps.index(post) - 1]
    T = (pd.Timestamp(post) - pd.Timestamp(pd.Timestamp(t0, unit="s").date())).days / 365
    ev = np.sqrt(max(ivs[post] ** 2 - ivs[pre] ** 2, 0) * T)
    top = near.groupby(["K", "exp", "cp"]).oi.sum().sort_values(ascending=False).head(8)
    return {"spot": S, "earnings": str(earn), "implied_earnings_move_1sd_%": round(100 * ev, 1),
            "gex_by_expiry_$M_per_1%": gex_by_exp.to_dict(),
            "biggest_oi_lines": {f"{k} {e} {c}": int(v) for (k, e, c), v in top.items()},
            "pcr_oi_60d": round(near[near.cp == "P"].oi.sum() / near[near.cp == "C"].oi.sum(), 2)}


if __name__ == "__main__":
    pd.set_option("display.width", 200)
    d, _ = daily()
    print(week_table(d).T.to_string(), "\n")
    er = earnings_reactions(d)
    print(er.tail(10).to_string(index=False))
    print("abs earnings day move: mean %.1f%%, last 4: %s\n" % (er["day_%"].abs().mean(), er["day_%"].tail(4).tolist()))
    for k, v in current_map().items():
        print(k, v)
