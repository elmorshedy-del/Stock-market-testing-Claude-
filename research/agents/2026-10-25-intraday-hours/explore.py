"""Part B exploration (pre-registered at 8c1dce0): the fixed last-hour menu B1-B8 on the EXPLORATION half only (first 365 SPY sessions).
Usage: python explore.py <hourly folder>  -> out/explore.json"""
import json
import sys

import numpy as np
import pandas as pd

import segments as G

RNG = np.random.default_rng(20261101)
NB = 500
GAMMA = ["SPY", "QQQ", "TSLA", "MSFT", "NVDA", "MU"]
MICRO = G.HERE.parents[1] / "microstructure" / "out"


def split_days(folder):
    spy = G.segments(folder, "SPY")
    d = spy.index
    return d[:365], d[365:]


def cal_flags(days):
    s = pd.Series(days, index=days)
    month = pd.Series(days.month, index=days)
    me = month.ne(month.shift(-1)).reindex(days).fillna(False).to_numpy()
    opex = np.zeros(len(days), bool)
    quad = np.zeros(len(days), bool)
    for y in sorted(set(days.year)):
        for m in range(1, 13):
            fr = pd.date_range(f"{y}-{m:02d}-01", periods=31, freq="D")
            fr = fr[(fr.month == m) & (fr.weekday == 4)]
            c = days[days <= fr[2]]
            if len(c) and (fr[2] - c[-1]).days <= 3 and c[-1].month == m:
                opex[days.get_loc(c[-1])] = True
                quad[days.get_loc(c[-1])] = m in (3, 6, 9, 12)
    gaps = np.r_[(days[1:] - days[:-1]).days, 1]
    preh = (gaps > 1) & ~((pd.Series(days).dt.weekday == 4).to_numpy() & (gaps == 3))
    return {"month end": me, "monthly OPEX (non-quad)": opex & ~quad, "quad witching": quad, "day before holiday": preh}


def pooled_slope(P, syms, xk, yk, rows_by):
    """Ticker-demeaned pooled slope and day-block bootstrap t."""
    def est(ii):
        xs, ys = [], []
        for s in syms:
            x, y = P[s][xk].to_numpy()[ii], P[s][yk].to_numpy()[ii]
            m = np.isfinite(x) & np.isfinite(y)
            xs.append(x[m] - x[m].mean()); ys.append(y[m] - y[m].mean())
        x, y = np.concatenate(xs), np.concatenate(ys)
        return (x * y).sum() / (x ** 2).sum()
    n = rows_by
    o = est(np.arange(n))
    b = np.array([est(G.blocks(RNG, n)) for _ in range(NB)])
    return {"slope": float(o), "t (bootstrap)": float(o / b.std())}


def main(folder):
    syms = sorted(p.name.split("_")[0] for p in __import__("pathlib").Path(folder).glob("*_60m.json"))
    explore, _ = split_days(folder)
    P = {s: G.segments(folder, s).reindex(explore) for s in syms}
    stocks = [s for s in syms if s not in ("SPY", "QQQ", "SMH", "IWM", "RSP", "XLK")]
    n = len(explore)
    res = {"exploration sessions": n, "dates": [str(explore[0].date()), str(explore[-1].date())], "tickers": len(syms)}
    for lab, xk, yk in [("B1 last on open-to-15:30", "rest", "last"), ("B2 last on first hour", "first", "last"),
                        ("B3 last on overnight", "on", "last"), ("B4 next overnight on last", "last", "on_next")]:
        per = {s: G.slope(P[s][xk].to_numpy(), P[s][yk].to_numpy()) for s in syms}
        res[lab] = {"pooled stocks": pooled_slope(P, stocks, xk, yk, n), "SPY": per["SPY"], "QQQ": per["QQQ"],
                    "share of stocks positive": float(np.mean([per[s] > 0 for s in stocks])),
                    "most negative": sorted(per.items(), key=lambda kv: kv[1])[:4], "most positive": sorted(per.items(), key=lambda kv: -kv[1])[:4]}
    fl = cal_flags(explore)
    wd = explore.weekday
    L = np.array([P[s]["last"].to_numpy() for s in stocks])
    Lspy = P["SPY"]["last"].to_numpy()
    stock_mean = np.nanmean(L, axis=0)
    def mean_t(v, mask):
        x = v[mask & np.isfinite(v)]
        return {"days": int(len(x)), "mean bp": float(1e4 * x.mean()), "t": float(x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))) if len(x) > 2 else None}
    res["B5 last half hour by calendar (bp)"] = {
        **{f"weekday {k}": {"stocks": mean_t(stock_mean, wd == k), "SPY": mean_t(Lspy, wd == k)} for k in range(5)},
        **{k: {"stocks": mean_t(stock_mean, v), "SPY": mean_t(Lspy, v)} for k, v in fl.items()},
        "all days": {"stocks": mean_t(stock_mean, np.ones(n, bool)), "SPY": mean_t(Lspy, np.ones(n, bool))}}
    # B6
    def b6(yk):
        xs, ys = [], []
        for s in stocks:
            x, y = np.log(P[s]["abn_share"].to_numpy()), P[s][yk].to_numpy()
            if yk == "on_next":
                y = y * np.sign(P[s]["last"].to_numpy())                 # does a high-volume close's move get given back?
            m = np.isfinite(x) & np.isfinite(y)
            xs.append(x[m] - x[m].mean()); ys.append(y[m] - y[m].mean())
        x, y = np.concatenate(xs), np.concatenate(ys)
        return float(np.corrcoef(x, y)[0, 1])
    res["B6 abnormal last-bar volume share"] = {"corr with last half hour": b6("last"), "corr with next overnight x sign(last)": b6("on_next")}
    # B7
    spy_rest = P["SPY"]["rest"].to_numpy()
    up, dn = spy_rest > 0.01, spy_rest < -0.01
    res["B7 big SPY days (|open to 15:30| > 1%)"] = {"SPY up days: SPY last bp": mean_t(Lspy, up), "SPY down days: SPY last bp": mean_t(Lspy, dn),
                                                    "SPY up days: stocks last bp": mean_t(stock_mean, up), "SPY down days: stocks last bp": mean_t(stock_mean, dn)}
    # B8
    out = {}
    for s in GAMMA:
        g = pd.read_csv(MICRO / f"td_gamma_{s}.csv", parse_dates=["date"]).set_index("date").gex_classic
        low = (g < g.rolling(252, min_periods=120).median()).shift(1).reindex(explore).to_numpy()
        x, y = P[s]["rest"].to_numpy(), P[s]["last"].to_numpy()
        ok = np.isfinite(x) & np.isfinite(y) & pd.notna(low)
        lo = ok & (low == True)
        hi = ok & (low == False)
        out[s] = {"slope low gamma": G.slope(x[lo], y[lo]), "slope high gamma": G.slope(x[hi], y[hi]), "days low / high": [int(lo.sum()), int(hi.sum())]}
    res["B8 B1 slope by dealer gamma"] = out
    # extra, flagged exploratory: per-ticker mean of each segment
    res["extra: mean last half hour by ticker (bp), top/bottom"] = {
        "top": sorted(((s, float(1e4 * np.nanmean(P[s]["last"]))) for s in syms), key=lambda kv: -kv[1])[:6],
        "bottom": sorted(((s, float(1e4 * np.nanmean(P[s]["last"]))) for s in syms), key=lambda kv: kv[1])[:6]}
    res["extra: mean first hour minus overnight by ticker (bp), top/bottom"] = {
        "top": sorted(((s, float(1e4 * np.nanmean(P[s]["first"] - P[s]["on"]))) for s in syms), key=lambda kv: -kv[1])[:6],
        "bottom": sorted(((s, float(1e4 * np.nanmean(P[s]["first"] - P[s]["on"]))) for s in syms), key=lambda kv: kv[1])[:6]}
    (G.OUT / "explore.json").write_text(json.dumps(res, indent=1, default=float))
    return res


if __name__ == "__main__":
    print(json.dumps(main(sys.argv[1]), indent=1, default=float))
