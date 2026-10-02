"""Where does dealer gamma go from today's state, and how fast?

1. Opex cycle: average GEX percentile by trading day relative to monthly opex.
2. Analogs: historical days most like today (GEX pct, VIX, VIX/VIX3M, DIX pct,
   distance from 50d MA, days since opex) -> distribution of days until GEX
   reaches the bottom quintile, what SPX did on the way there, and whether an
   up-leg (top-decile 10d return) started within the next 30 trading days.
3. Extra confirmations measured on their own: DIX, midterm-year seasonality.
"""
import numpy as np
import pandas as pd

from backtest import third_fridays
from common import load_bars
from release import frame as rframe

K = 80          # analogs
HORIZON = 30    # trading days to look ahead


def build():
    d = rframe()
    g = pd.read_csv("data/DIX.csv", parse_dates=["date"]).set_index("date")
    # recompute pct on the full sample so the most recent days (no fwd yet) are kept
    full = d.join(g[["gex", "dix"]], how="inner")
    pct = lambda s: s.rolling(252).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True)
    full["gex_pct"], full["dix_pct"] = pct(full.gex), pct(full.dix)
    full["ts"] = full.VIX / full.VIX3M
    full["ma50"] = np.log(full.c / full.c.rolling(50).mean())
    opex = sorted(third_fridays(full.index))
    pos = np.searchsorted(np.array(opex, dtype="datetime64[ns]"), full.index.values, side="right") - 1
    last = np.array(opex, dtype="datetime64[ns]")[np.clip(pos, 0, None)]
    full["days_since_opex"] = [full.index.searchsorted(i) - full.index.searchsorted(l) for i, l in zip(full.index, last)]
    return full.dropna(subset=["gex_pct", "dix_pct", "ts", "ma50"])


def opex_cycle(f, start=None):
    f = f if start is None else f[f.index >= start]
    opex = [o for o in sorted(third_fridays(f.index)) if o in f.index]
    idx = {o: f.index.get_loc(o) for o in opex}
    rows = []
    for o, i in idx.items():
        for k in range(-10, 11):
            if 0 <= i + k < len(f):
                rows.append((k, f.gex_pct.iloc[i + k]))
    return pd.DataFrame(rows, columns=["day_vs_opex", "gex_pct"]).groupby("day_vs_opex").gex_pct.mean()


def analogs(f, feats=("gex_pct", "VIX", "ts", "dix_pct", "ma50", "days_since_opex")):
    feats = list(feats)
    now = f.iloc[-1]
    hist = f.iloc[:-HORIZON - 1]
    z = (hist[feats] - hist[feats].mean()) / hist[feats].std()
    zn = (now[feats] - hist[feats].mean()) / hist[feats].std()
    dist = np.sqrt(((z - zn) ** 2).sum(axis=1))
    picks, used = [], []
    for t in dist.sort_values().index:            # de-cluster: >= 10 days apart
        if all(abs((t - u).days) > 14 for u in used):
            picks.append(t); used.append(t)
        if len(picks) == K:
            break
    top = (np.log(f.c.shift(-10) / f.c)).quantile(0.9)
    rows = []
    for t in picks:
        i = f.index.get_loc(t)
        w = f.iloc[i + 1:i + 1 + HORIZON]
        hit = np.where(w.gex_pct.to_numpy() <= 0.2)[0]
        fwd10 = np.log(f.c.shift(-10) / f.c).iloc[i + 1:i + 1 + HORIZON]
        leg = np.where(fwd10.to_numpy() > top)[0]
        rows.append({"date": t, "days_to_low_gex": hit[0] + 1 if len(hit) else np.nan,
                     "spx_to_low_gex": np.log(w.c.iloc[hit[0]] / f.c.iloc[i]) if len(hit) else np.nan,
                     "leg_start_day": leg[0] + 1 if len(leg) else np.nan,
                     "leg_after_low_gex": bool(len(hit) and len(leg) and leg[0] >= hit[0]),
                     "spx_30d": np.log(f.c.iloc[min(i + HORIZON, len(f) - 1)] / f.c.iloc[i]),
                     "max_30d": np.log(w.c.max() / f.c.iloc[i]), "min_30d": np.log(w.c.min() / f.c.iloc[i])})
    return now, pd.DataFrame(rows)


def midterm_q4(f_spx):
    c = f_spx.c
    out = []
    for y in range(1970, 2026):
        a, b = c.loc[f"{y}-09-25":f"{y}-10-01"], c.loc[f"{y}-12-24":f"{y}-12-31"]
        if len(a) and len(b):
            out.append((y, (y - 1970) % 4 == 0 and y % 4 == 2, np.log(b.iloc[-1] / a.iloc[-1])))
    q = pd.DataFrame(out, columns=["year", "midterm", "q4"])
    return q.groupby("midterm").q4.agg(["size", "mean", "median", lambda s: (s > 0).mean()]), q[q.midterm]


if __name__ == "__main__":
    pd.set_option("display.width", 200)
    f = build()
    print("GEX percentile around monthly opex (all / 2022-05+):")
    cyc = pd.DataFrame({"all": opex_cycle(f), "0dte_era": opex_cycle(f, "2022-05-11")}).round(2)
    print(cyc.T.to_string())
    now, a = analogs(f)
    print("\nNOW", f.index[-1].date(), now[["c", "gex_pct", "VIX", "ts", "dix_pct", "ma50", "days_since_opex"]].round(3).to_dict())
    print(f"\n{len(a)} analogs, {a.date.min().date()}..{a.date.max().date()}")
    reached = a.days_to_low_gex.notna()
    print(f"P(GEX pct <= 0.20 within {HORIZON}d) = {reached.mean():.2f}; days to get there: median {a.days_to_low_gex.median():.0f}, "
          f"IQR {a.days_to_low_gex.quantile(.25):.0f}-{a.days_to_low_gex.quantile(.75):.0f}")
    print(f"SPX on the way to low GEX: median {100*a.spx_to_low_gex.median():+.1f}%, share negative {(a.spx_to_low_gex < 0)[reached].mean():.2f}")
    print(f"P(up-leg starts within {HORIZON}d) = {a.leg_start_day.notna().mean():.2f} (compare random days below)")
    print(f"  given GEX reached low first: {a[reached].leg_start_day.notna().mean():.2f}; leg began after the low-GEX date: {a.leg_after_low_gex[reached].mean():.2f}")
    print(f"  leg start day: median {a.leg_start_day.median():.0f}, IQR {a.leg_start_day.quantile(.25):.0f}-{a.leg_start_day.quantile(.75):.0f}")
    print(f"SPX 30d: median {100*a.spx_30d.median():+.1f}%, P(>0) {(a.spx_30d > 0).mean():.2f}, median max {100*a.max_30d.median():+.1f}%, median min {100*a.min_30d.median():+.1f}%")
    # unconditional comparison
    rng = np.random.default_rng(0)
    top = (np.log(f.c.shift(-10) / f.c)).quantile(0.9)
    fwd10 = np.log(f.c.shift(-10) / f.c).to_numpy()
    lowg = (f.gex_pct <= 0.2).to_numpy()
    idx = rng.choice(np.arange(len(f) - HORIZON - 11), 4000)
    print(f"\nrandom days: P(up-leg within {HORIZON}d) {np.mean([(fwd10[i+1:i+1+HORIZON] > top).any() for i in idx]):.2f}, "
          f"P(low GEX within {HORIZON}d) {np.mean([lowg[i+1:i+1+HORIZON].any() for i in idx]):.2f}")
    # DIX + GEX joint
    f2 = f.assign(fwd=np.log(f.c.shift(-10) / f.c)).dropna(subset=["fwd"])
    f2["g"] = pd.cut(f2.gex_pct, [-.01, .2, .8, 1.01], labels=["lowGEX", "midGEX", "highGEX"])
    f2["dq"] = pd.cut(f2.dix_pct, [-.01, .5, .8, 1.01], labels=["DIX<50", "DIX50-80", "DIX>80"])
    print("\nP(up-leg next 10d) by GEX x DIX (cell n in brackets)")
    t = f2.groupby(["g", "dq"], observed=True).fwd.agg(lambda s: f"{(s > top).mean():.2f} [{len(s)}]").unstack()
    print(t.to_string())
    s, mt = midterm_q4(pd.DataFrame({"c": load_bars("^GSPC").close}))
    print("\nSPX Oct1->Dec31, midterm years vs others (1970-2025):\n", s.round(3).to_string())
    print(mt.round(3).to_string(index=False))
