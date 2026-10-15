"""Is a leader held back by a pinned market, and released once the market is freed? (REPORT 4aa)
The thesis (Oct 12): MSFT wants to break up but SPY holds it back; once SPY is freed the move carries.

  leader     the stock's return minus SPY's over L sessions (L in 10 / 20 / 40) is in the top third
             of its own trailing year
  SPY state  freed = bottom third of its trailing year on one gauge, pinned = the rest:
               SPY OI near its price (+-2% or +-5%, expiries <= 45 days; ThetaData 2021+, mech_book.py)
               S&P dealer gamma (SqueezeMetrics GEX percentile, 2012+)
  outcome    the stock's up-leg starts within H (a 10-day return in its own top decile), its down-leg,
             its forward return, and SPY's forward return (does it carry on to SPY?);  H in 5 / 10 / 20
  days       in state (every day) | turn-on (first day SPY is freed while the stock leads, >= 10 apart)
  era        three per gauge (full, first part, second part)
Two statistics per specification:
  release    outcome(leader, SPY freed) - outcome(leader, SPY pinned)
  specific   release minus the same contrast on non-leader days (a freed SPY may simply move everything)
Null: slide the SPY gauges in time against the stock (keeps both series' persistence), 300 times.
Usage: python held_back.py MSFT [AAPL NVDA ...]
"""
import itertools
import sys

import numpy as np
import pandas as pd

from common import OUT, load_bars
from forecast import build as spx_frame
from own_multiverse import first_on, within

LS, HS, N_NULL = (10, 20, 40), (5, 10, 20), 300
GAUGES = {"SPY OI near price +-2%": "near2", "SPY OI near price +-5%": "near5", "S&P dealer gamma (GEX)": "gex"}
ERAS = {"near2": [("2021+", "2021-01-01", "2100"), ("2021-23", "2021-01-01", "2023-12-31"), ("2024+", "2024-01-01", "2100")],
        "gex": [("2012+", "2012-01-01", "2100"), ("2012-20", "2012-01-01", "2020-12-31"), ("2021+", "2021-01-01", "2100")]}
ERAS["near5"] = ERAS["near2"]
pct = lambda v: v.rolling(252, min_periods=120).rank(pct=True)


def spy_state():
    b = pd.read_csv(OUT / "mech_book_SPY.csv", parse_dates=["date"]).set_index("date")
    g = pd.DataFrame({"near2": pct(b.near2), "near5": pct(b.near5)})
    gex = spx_frame().gex_pct
    return g.join(gex.rename("gex"), how="outer")


def frame(sym):
    c, s = load_bars(sym).close, load_bars("SPY").close
    idx = c.index.intersection(s.index)
    X = pd.DataFrame({"c": c.reindex(idx), "s": s.reindex(idx)})
    lc, ls = np.log(X.c), np.log(X.s)
    for L in LS:
        X[f"lead{L}"] = pct((lc - lc.shift(L)) - (ls - ls.shift(L))) >= 2 / 3
    X = X.join(spy_state().reindex(idx))
    return X[X.index >= "2012-01-01"]


def outcomes(X):
    lc, ls = np.log(X.c.to_numpy()), np.log(X.s.to_numpy())
    f10 = np.r_[lc[10:] - lc[:-10], np.full(10, np.nan)]
    lo, hi = np.nanquantile(f10, [0.1, 0.9])
    Y = {}
    for h in HS:
        Y[("up-leg", h)] = within(np.nan_to_num(f10 >= hi).astype(bool), h)
        Y[("down-leg", h)] = within(np.nan_to_num(f10 <= lo).astype(bool), h)
        Y[("return", h)] = np.r_[lc[h:] - lc[:-h], np.full(h, np.nan)]
        Y[("SPY return", h)] = np.r_[ls[h:] - ls[:-h], np.full(h, np.nan)]
    return Y


def run(X, G, Y):
    rows = []
    for (gname, col), L in itertools.product(GAUGES.items(), LS):
        lead = X[f"lead{L}"].to_numpy()
        g = G[col]
        ok = ~np.isnan(g)
        free, pin = ok & (g <= 1 / 3), ok & (g > 1 / 3)
        for (era, a, b), days in itertools.product(ERAS[col], ("in state", "turn-on")):
            m = np.asarray((X.index >= a) & (X.index <= b))
            cells = {}
            for who, w in (("lead", lead), ("rest", ~lead)):
                on = w & free & m
                cells[who] = (first_on(on) if days == "turn-on" else on, w & pin & m)
            for (oc, h), y in Y.items():
                v = ~np.isnan(y)
                mean = lambda k: y[k & v].mean() if (k & v).sum() >= 5 else np.nan
                rel = mean(cells["lead"][0]) - mean(cells["lead"][1])
                rest = mean(cells["rest"][0]) - mean(cells["rest"][1])
                rows.append((gname, L, era, days, oc, h, int((cells["lead"][0] & v).sum()), rel, rel - rest))
    return pd.DataFrame(rows, columns=["gauge", "L", "era", "days", "outcome", "H", "n_events", "release", "specific"])


def study(sym, seed=0):
    X = frame(sym)
    Y = outcomes(X)
    G = {col: X[col].to_numpy(float) for col in GAUGES.values()}
    real = run(X, G, Y)
    rng = np.random.default_rng(seed)
    nulls = [run(X, {k: np.roll(v, s) for k, v in G.items()}, Y) for s in rng.integers(60, len(X) - 60, N_NULL)]
    fam = []
    for stat in ("release", "specific"):
        null = np.array([n[stat].to_numpy() for n in nulls])
        e = real[stat].to_numpy()
        mu, sd = np.nanmean(null, 0), np.nanstd(null, 0)
        z, zn = (e - mu) / sd, (null - mu) / sd
        real[f"p_hi_{stat}"] = np.where(np.isnan(e), np.nan, (null >= e).mean(0))
        real[f"p_lo_{stat}"] = np.where(np.isnan(e), np.nan, (null <= e).mean(0))
        for (ga, oc, dy), g in real.groupby(["gauge", "outcome", "days"], sort=False):
            i = g.index.to_numpy()
            med, nmed = np.nanmedian(z[i]), np.nanmedian(zn[:, i], axis=1)
            fam.append({"statistic": stat, "gauge": ga, "outcome": oc, "days": dy, "specs": int(np.isfinite(e[i]).sum()),
                        "median_effect": np.nanmedian(e[i]), "beyond_hi_5%": np.mean(real.loc[i, f"p_hi_{stat}"] < 0.05),
                        "beyond_lo_5%": np.mean(real.loc[i, f"p_lo_{stat}"] < 0.05),
                        "joint_p": float(np.mean(np.abs(nmed - np.nanmean(nmed)) >= abs(med - np.nanmean(nmed))))})
    return X, real, pd.DataFrame(fam)


def cells(X, L=20, col="near5", h=10, start="2021-01-01"):
    """The plain 2x2 behind one specification: P(up-leg within h), P(down-leg), mean return, n."""
    Y = outcomes(X)
    z = X.index >= start
    lead, g = X[f"lead{L}"].to_numpy(), X[col].to_numpy(float)
    rows = []
    for who, w in (("stock leading SPY", lead), ("not leading", ~lead)):
        for st, k in (("SPY freed", g <= 1 / 3), ("SPY pinned", g > 1 / 3)):
            m = w & k & z & ~np.isnan(g)
            rows.append({"stock": who, "SPY": st, "days": int(m.sum()),
                         "up-leg %": 100 * np.nanmean(Y[("up-leg", h)][m]), "down-leg %": 100 * np.nanmean(Y[("down-leg", h)][m]),
                         "return %": 100 * np.nanmean(Y[("return", h)][m]), "SPY return %": 100 * np.nanmean(Y[("SPY return", h)][m])})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    for sym in sys.argv[1:] or ["MSFT"]:
        X, real, fam = study(sym)
        real.to_csv(OUT / f"held_back_{sym}.csv", index=False)
        print(f"\n=== {sym} held back by SPY? {len(real)} specs, {N_NULL} shifted nulls, {X.index[0].date()} .. {X.index[-1].date()}")
        fam.to_csv(OUT / f"held_back_families_{sym}.csv", index=False)
        for stat in ("release", "specific"):
            f = fam[fam.statistic == stat].drop(columns="statistic")
            print(f"\n[{stat}]")
            print(f.round(3).to_string(index=False))
        print("\nby gauge, in state (median release, pct points):")
        sub = real[real.days == "in state"]
        print((100 * sub.groupby(["outcome", "gauge"]).release.median()).unstack().round(2).to_string())
        print("\n2x2 for L=20, SPY OI near price +-5%, H=10, 2021+:")
        print(cells(X).round(2).to_string(index=False))
        print("2x2 for L=20, S&P GEX, H=10, 2012+:")
        print(cells(X, col="gex", start="2012-01-01").round(2).to_string(index=False))
        last = X.iloc[-1]
        gx = X.gex.dropna()
        print(f"\nnow ({X.index[-1].date()}): leader L10/20/40 = {bool(last.lead10)}/{bool(last.lead20)}/{bool(last.lead40)}; "
              f"SPY near2 pct {last.near2:.2f}, near5 pct {last.near5:.2f}; S&P GEX pct {gx.iloc[-1]:.2f} ({gx.index[-1].date()})")
