"""The S&P gamma studies with a single stock as the TARGET (default TSLA).

Predictors stay market-wide (S&P dealer gamma GEX and dark-pool DIX from
SqueezeMetrics, VIX), because free single-stock gamma history does not exist.
Outcomes are the stock's own moves:
  up-leg   = top-decile 10-day return OF THE STOCK (its own distribution)
  calls    = priced with an IV proxy: VIX x (stock 60d vol / S&P 60d vol),
             so market vol crushes propagate; real single-name IV and skew
             differ, so compare rungs with "any day", not with zero.
Also: stock beta/idiosyncratic vol by gamma regime, today's option map from
the free chain snapshot, and the auto log channel.
Usage: python single_name.py TSLA
"""
import sys

import numpy as np
import pandas as pd

import ladder as LD
import multiverse as MV
import options_flow as of
from channels import detect
from common import load_bars
from forecast import build


def frames(sym):
    f = build()
    s = load_bars(sym).close.reindex(f.index).ffill()
    t = f.copy()
    t["c"] = s
    rs = np.log(f.c).diff().rolling(60).std()
    rt = np.log(t.c).diff().rolling(60).std()
    t["VIX"] = f.VIX * rt / rs
    t = t.dropna(subset=["c", "VIX"])
    return f.loc[t.index], t


def regime_tables(f, t, sym):
    fwd10 = np.log(t.c.shift(-10) / t.c)
    rv10 = np.log(t.c).diff()[::-1].rolling(10).std()[::-1].shift(-1) * np.sqrt(252)
    top = fwd10.quantile(0.9)
    x = pd.DataFrame({"fwd": fwd10, "rv": rv10, "gq": pd.qcut(f.gex_pct, 5, labels=False), "dix": f.dix_pct}).dropna()
    out = {}
    for lab, a in (("2012+", "2012"), ("2019Q4+", "2019-10-01"), ("2022-05+", "2022-05-11")):
        z = x.loc[a:]
        out[lab] = z.groupby("gq").agg(p_up_leg=("fwd", lambda v: (v > top).mean()), next10d_rv=("rv", "mean"),
                                       n=("fwd", "size"))
    x["g"] = pd.cut(f.gex_pct.reindex(x.index), [-.01, .2, .8, 1.01], labels=["lowGEX", "midGEX", "highGEX"])
    x["d"] = pd.cut(x.dix, [-.01, .5, .8, 1.01], labels=["DIX<50", "DIX50-80", "DIX>80"])
    joint = x.groupby(["g", "d"], observed=True).fwd.agg(lambda s: f"{(s > top).mean():.2f} [{len(s)}]").unstack()
    return out, joint


def beta_by_regime(f, t):
    rs, rt = np.log(f.c).diff(), np.log(t.c).diff()
    g = pd.cut(f.gex_pct, [-.01, .2, .8, 1.01], labels=["lowGEX", "midGEX", "highGEX"])
    rows = {}
    for k in ("lowGEX", "midGEX", "highGEX"):
        m = (g == k) & rs.notna() & rt.notna()
        b = np.polyfit(rs[m], rt[m], 1)[0]
        resid = rt[m] - b * rs[m]
        rows[k] = {"beta": b, "corr": np.corrcoef(rs[m], rt[m])[0, 1], "idio_vol_ann": resid.std() * np.sqrt(252)}
    return pd.DataFrame(rows).T


def stock_multiverse(f, t):
    fwd, leg = MV.prep(t)
    gp, dp = f.gex_pct.to_numpy(), f.dix_pct.to_numpy()
    era = {k: np.asarray(t.index >= v) for k, v in MV.ERAS.items()}
    real = MV.run(gp, dp, fwd, leg, era)
    rng = np.random.default_rng(0)
    null = np.array([MV.run(np.roll(gp, s), np.roll(dp, s), fwd, leg, era).effect.to_numpy()
                     for s in rng.integers(60, len(gp) - 60, MV.N_NULL)])
    real["p"] = (null >= real.effect.to_numpy()).mean(axis=0)
    z = (real.effect - np.nanmean(null, 0)) / np.nanstd(null, 0)
    zn = (null - np.nanmean(null, 0)) / np.nanstd(null, 0)
    joint = (np.nanmedian(zn, axis=1) >= np.nanmedian(z)).mean()
    by = real.groupby("outcome").agg(n_specs=("p", "size"), positive=("effect", lambda v: (v > 0).mean()),
                                     sig_5pct=("p", lambda v: (v < 0.05).mean()), mean_effect=("effect", "mean"))
    return by, joint


def stock_ladder(f, t, sym):
    o = LD.outcomes(t)
    o["spread60"] = LD.call_spread(t, w=0.10)          # wider wings for a high-vol name
    hi10 = t.c.rolling(10).max()
    rungs = LD.rungs(f)
    rungs[f"R4s GEX <= 0.20 + {sym} >= 5% off 10d high"] = (f.gex_pct <= 0.20) & (t.c / hi10 - 1 <= -0.05)
    rungs["R5s R4s + DIX>0.5"] = rungs[f"R4s GEX <= 0.20 + {sym} >= 5% off 10d high"] & (f.dix_pct > 0.5)
    rng = np.random.default_rng(0)
    res = {}
    for start, lab in ((None, "2012+"), ("2019-10-01", "2019Q4+")):
        oo = o if start is None else o[o.index >= start]
        rows = {"any day": LD.summarize(oo, np.ones(len(oo), bool), rng)}
        for name, cond in rungs.items():
            c = cond.reindex(oo.index).fillna(False).to_numpy()
            r = LD.summarize(oo, LD.first_on(pd.Series(c)), rng)
            if r:
                rows[name] = r
        res[lab] = pd.DataFrame(rows).T.rename(columns={"spx20": f"{sym.lower()}20"})
    now = {name: bool(c.iloc[-1]) for name, c in rungs.items()}
    return res, now


def snapshot(sym):
    r, _ = of.summary(sym)
    q = r["classic"]
    daily = load_bars(sym)
    ch = detect(daily, q=0.15)
    lo, mid, up = (float(v[0]) for v in ch.lines([len(daily) - 1]))
    S, _, quote, _ = of.load_chain(sym)
    earn = max(quote.get(k, 0) for k in ("earningsTimestamp", "earningsTimestampStart"))
    return {
        "spot": r["spot"], "asof": r["asof"], "next_earnings": str(pd.Timestamp(earn, unit="s").date()),
        "gex_per_1pct_$M (classic)": round(q["net_gex_per_1pct"] / 1e6), "gex_per_1pct_$M (dealers short both)":
            round(r["short"]["net_gex_per_1pct"] / 1e6), "gamma_flip (classic)": [round(x, 1) for x in q["gamma_flips"]],
        "top_gex_strikes": {k: round(v / 1e6) for k, v in q["top_pos_gex_strikes"].items()},
        "call_oi_top": r["call_oi_top"], "put_oi_top": r["put_oi_top"], "pcr_oi_45d": round(r["pcr_oi_near"], 2),
        "max_pain": r["max_pain"],
        "implied_1sd_move_%": {k: round(v["move_1sd_pct"], 1) for k, v in list(r["implied_move"].items())[:9]},
        "channel": {"anchor": str(daily.index[ch.start].date()), "growth_%yr": round(100 * ch.annual_growth()),
                    "width_%": round(100 * (np.exp(ch.hi - ch.lo) - 1)), "r2": round(ch.r2, 3),
                    "lower_mid_upper": (round(lo), round(mid), round(up)),
                    "z_close": round(float(ch.z(len(daily) - 1, np.log(daily.close.iloc[-1]))), 2)},
    }


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    sym = (sys.argv[1:] or ["TSLA"])[0]
    f, t = frames(sym)
    q, joint = regime_tables(f, t, sym)
    for lab, tab in q.items():
        print(f"\n{sym}: P(own top-decile 10d up-leg) and next-10d realized vol by S&P GEX quintile, {lab}")
        print(tab.round(3).to_string())
    print(f"\n{sym}: P(up-leg next 10d) by S&P GEX x DIX\n{joint.to_string()}")
    print(f"\n{sym} vs S&P by gamma regime\n{beta_by_regime(f, t).round(2).to_string()}")
    by, jp = stock_multiverse(f, t)
    print(f"\nmultiverse with {sym} as target (216 specs, {MV.N_NULL} shifted nulls): joint p = {jp:.3f}\n{by.round(3).to_string()}")
    lad, now = stock_ladder(f, t, sym)
    for lab, tab in lad.items():
        print(f"\n{sym} entry ladder, {lab} (call60 = 60d ATM call, spread60 = ATM/110% call spread, held 20d)")
        print(tab.to_string(float_format=lambda v: f"{v:.3f}"))
    print("\nrungs ON today:", [k for k, v in now.items() if v])
    print("\nsnapshot:")
    for k, v in snapshot(sym).items():
        print(f"  {k}: {v}")
