"""Analog outlook for MSFT (its own options state only) and the S&P (its own gamma/DIX state
plus seasonality). No hand-set cutoffs.

Method
  state     a handful of readings per day, each turned into a z-score over the sample
  analogs   the K days closest to today (Euclidean distance on the z-scores), at least
            GAP sessions apart, excluding the last 30 sessions
  outcomes  forward return over H sessions, best rise within H (run-up), worst fall within H;
            a "big rise" = run-up in the top quarter of all the asset's own days (relative, not set by hand)
  luck      the analog statistics vs 4,000 random sets of K days with the same spacing
  robust    K in (15, 25, 40) and each reading dropped in turn
MSFT readings: % above its own gamma flip, own-gamma percentile, OI-near-price percentile,
  % to the largest call strike, 30-day IV percentile, 20-day return.
S&P readings: SqueezeMetrics gamma percentile, DIX percentile, VIX (log), VIX/VIX3M, 20-day return.
Seasonality: S&P return from Oct 12 to Dec 31 every year since 1990 vs all windows of the same length.
Usage: python outlook.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from burst_gamma import state
from common import OUT, load_bars
from forecast import build as spx_frame
from release import frame as spx_long

C1, C2, C3, INK, MUTED, GRID, SURF = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
                     "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": SURF,
                     "axes.facecolor": SURF, "legend.frameon": False})
GAP, KS, NRAND = 10, (15, 25, 40), 4000
RNG = np.random.default_rng(2026)


def outcomes(c, h):
    lc = np.log(c)
    fwd = lc.shift(-h) - lc
    path = pd.concat([lc.shift(-k) - lc for k in range(1, h + 1)], axis=1)
    return pd.DataFrame({"fwd": fwd, "runup": path.max(axis=1), "dd": path.min(axis=1)})


def spaced_pick(order, pos, k, gap=GAP):
    out = []
    for i in order:
        if all(abs(pos[i] - pos[j]) >= gap for j in out):
            out.append(i)
            if len(out) == k:
                break
    return out


def analogs(X, now, pool, k, cols):
    z = (X[cols] - X.loc[pool, cols].mean()) / X.loc[pool, cols].std()
    d = np.sqrt(((z.loc[pool] - z.loc[now]) ** 2).sum(axis=1))
    order = list(d.sort_values().index)
    pos = {t: i for i, t in enumerate(X.index)}
    return spaced_pick(order, pos, k), d


def random_sets(pool, index, k, n=NRAND):
    pos = np.array([index.get_loc(t) for t in pool])
    sets = []
    for _ in range(n):
        p = RNG.permutation(len(pool))
        chosen = []
        for i in p:
            if all(abs(pos[i] - pos[j]) >= GAP for j in chosen):
                chosen.append(i)
                if len(chosen) == k:
                    break
        sets.append([pool[i] for i in chosen])
    return sets


def study(X, O, now, cols, label, start):
    pool = [t for t in X.dropna(subset=cols).index if t >= pd.Timestamp(start) and t in O.dropna().index
            and t < X.index[-31]]
    big = O.loc[pool, "runup"].quantile(0.75)
    res = {}
    for k in KS:
        picks, d = analogs(X, now, pool, k, cols)
        o = O.loc[picks]
        rs = random_sets(pool, X.index, k, 800 if k != 25 else NRAND)
        rmean = np.array([O.loc[s, "fwd"].mean() for s in rs])
        rbig = np.array([(O.loc[s, "runup"] >= big).mean() for s in rs])
        res[k] = {"picks": picks, "median_fwd": o.fwd.median(), "mean_fwd": o.fwd.mean(), "p_big": (o.runup >= big).mean(),
                  "mean_dd": o.dd.mean(), "p_mean_fwd": float(np.mean(rmean >= o.fwd.mean())),
                  "p_big_more": float(np.mean(rbig >= (o.runup >= big).mean())),
                  "p_big_less": float(np.mean(rbig <= (o.runup >= big).mean()))}
    drop = {}
    for c_ in cols:
        rest = [x for x in cols if x != c_]
        picks, _ = analogs(X, now, pool, 25, rest)
        o = O.loc[picks]
        drop[c_] = {"p_big": (o.runup >= big).mean(), "median_fwd": o.fwd.median()}
    base = {"median_fwd": O.loc[pool, "fwd"].median(), "mean_fwd": O.loc[pool, "fwd"].mean(), "p_big": 0.25,
            "mean_dd": O.loc[pool, "dd"].mean()}
    print(f"\n=== {label}: analogs of {now.date()} (pool {len(pool)} days from {start})")
    print(f"   all days: median fwd {100 * base['median_fwd']:+.1f}%, big-rise share 25% (run-up >= {100 * big:.1f}%), mean worst fall {100 * base['mean_dd']:.1f}%")
    for k, r in res.items():
        print(f"   K={k}: median fwd {100 * r['median_fwd']:+.1f}%, big rise {r['p_big']:.0%} (p more {r['p_big_more']:.2f}, p less {r['p_big_less']:.2f}), "
              f"mean worst fall {100 * r['mean_dd']:.1f}%, p(mean fwd this high by luck) {r['p_mean_fwd']:.2f}")
    print("   drop-one (K=25): " + "; ".join(f"-{c_}: big {v['p_big']:.0%}, med {100 * v['median_fwd']:+.1f}%" for c_, v in drop.items()))
    return res, base, big, pool, drop


def msft():
    c = load_bars("MSFT").close
    st = state("MSFT")
    X = st.join(c.rename("c"), how="inner")
    X["ret20"] = np.log(X.c / X.c.shift(20))
    cols = ["to_flip_pct", "g_pct", "near_pct", "to_call_wall_pct", "iv_pct", "ret20"]
    O = outcomes(X.c, 30)
    now = X.index[-1]
    res, base, big, pool, drop = study(X, O, now, cols, "MSFT, 30 sessions", "2021-01-01")
    jul = pd.Timestamp("2026-07-24")
    pool_j = [t for t in pool if abs((t - jul).days) > 60]
    picks_j, _ = analogs(X, jul, pool_j, 25, cols)
    oj = O.loc[picks_j]
    print(f"   states like Jul 24, 2026 (before the July move): median fwd {100 * oj.fwd.median():+.1f}%, big rise {(oj.runup >= big).mean():.0%}")
    return X, O, res, base, big, picks_j, drop


def spx():
    f = spx_frame()
    X = f.copy()
    X["ret20"] = np.log(X.c / X.c.shift(20))
    X["lvix"] = np.log(X.VIX)
    cols = ["gex_pct", "dix_pct", "lvix", "ts", "ret20"]
    O = outcomes(X.c, 40)
    now = X.index[-1]
    res, base, big, pool, drop = study(X, O, now, cols, "S&P, 40 sessions", "2012-01-01")
    return X, O, res, base, big, drop


def seasonality():
    c = spx_long().c
    rows = []
    for y in range(1990, 2026):
        s = c[f"{y}-10-12":f"{y}-12-31"]
        rows.append({"year": y, "ret": 100 * np.log(s.iloc[-1] / c[:s.index[0]].iloc[-2]) if len(s) else np.nan})
    S = pd.DataFrame(rows).set_index("year")
    n = len(c["2025-10-12":"2025-12-31"])
    lc = np.log(c["1990":"2025"])
    allw = 100 * (lc.shift(-n) - lc).dropna()
    mid = [1994, 1998, 2002, 2006, 2010, 2014, 2018, 2022]
    boot = lambda v: np.percentile([RNG.choice(v, len(v)).mean() for _ in range(4000)], [5, 95])
    out = {}
    for lab, ys in (("all years 1990-2025", S.index), ("2020-2025", [y for y in S.index if y >= 2020]), ("midterm years", mid)):
        v = S.loc[list(ys), "ret"].dropna().to_numpy()
        out[lab] = {"mean": v.mean(), "ci": boot(v), "pos": (v > 0).mean(), "n": len(v)}
    print(f"\n=== S&P Oct 12 -> Dec 31 ({n} sessions) vs any {n}-session window 1990-2025: mean {allw.mean():+.1f}%, positive {(allw > 0).mean():.0%}")
    for k, v in out.items():
        print(f"   {k:20s} n={v['n']:2d}: mean {v['mean']:+.1f}% (90% CI {v['ci'][0]:+.1f}..{v['ci'][1]:+.1f}), positive {v['pos']:.0%}")
    return S, allw, out, mid


def figure(ms, sp, sea):
    X, O, res, base, big, picks_j, drop = ms
    SX, SO, sres, sbase, sbig, sdrop = sp
    S, allw, sout, mid = sea
    f, axs = plt.subplots(2, 2, figsize=(14, 9))

    def paths(a, X, picks, h, color, label):
        lc = np.log(X.c)
        for t in picks:
            i = X.index.get_loc(t)
            p = 100 * (np.exp(lc.iloc[i:i + h + 1].to_numpy() - lc.iloc[i]) - 1)
            a.plot(np.arange(len(p)), p, color=color, lw=0.8, alpha=0.35)
        P = np.array([100 * (np.exp(lc.iloc[X.index.get_loc(t):X.index.get_loc(t) + h + 1].to_numpy() - lc.iloc[X.index.get_loc(t)]) - 1)
                      for t in picks if X.index.get_loc(t) + h < len(X)])
        a.plot(np.arange(h + 1), np.median(P, axis=0), color=color, lw=2.6, label=label)

    def base_band(a, X, h, start):
        lc = np.log(X.c[X.index >= start])
        P = np.array([100 * (np.exp(lc.iloc[i:i + h + 1].to_numpy() - lc.iloc[i]) - 1) for i in range(0, len(lc) - h, 3)])
        a.fill_between(np.arange(h + 1), np.percentile(P, 25, axis=0), np.percentile(P, 75, axis=0), color=MUTED, alpha=0.12, lw=0,
                       label="all days: middle half")
        a.plot(np.arange(h + 1), np.median(P, axis=0), color=MUTED, lw=1.4, ls="--", label="all days: median")

    a = axs[0, 0]
    base_band(a, X, 30, "2021-01-01")
    paths(a, X, res[25]["picks"], 30, C1, "25 days most like today: median")
    a.axhline(0, color=INK, lw=0.7)
    a.set_title("MSFT: what followed the 25 days whose own options state was most like today\n"
                "(far above its gamma flip, very call-heavy, just under the 550 call strike)", loc="left", fontsize=9.5, color=INK)
    a.set_xlabel("sessions ahead")
    a.set_ylabel("% from the analog day")
    a.legend(loc="upper left", fontsize=8)

    b = axs[0, 1]
    rows = [("all MSFT days", base["p_big"], base["median_fwd"], MUTED)]
    for k in KS:
        rows.append((f"like today, K={k}", res[k]["p_big"], res[k]["median_fwd"], C1))
    ojn = O.loc[picks_j]
    rows.append(("like Jul 24 (before July's move)", (ojn.runup >= big).mean(), ojn.fwd.median(), C3))
    ys = np.arange(len(rows))
    b.barh(ys, [100 * r[1] for r in rows], color=[r[3] for r in rows], height=0.55)
    for y, r in zip(ys, rows):
        b.annotate(f"{100 * r[1]:.0f}%   (median 30-session return {100 * r[2]:+.1f}%)", (100 * r[1], y), xytext=(4, 0),
                   textcoords="offset points", va="center", fontsize=8)
    b.set_yticks(ys, [r[0] for r in rows])
    b.invert_yaxis()
    b.set_xlim(0, 100)
    b.set_xlabel(f"% followed by a big rise within 30 sessions (run-up >= {100 * big:.0f}%, MSFT's own top quarter)")
    b.grid(axis="y", visible=False)
    b.set_title(f"MSFT: chance of a big rise (a continuation leg) within 30 sessions\n"
                f"like today: below chance (p = {res[25]['p_big_less']:.2f} vs random days); like Jul 24: above it",
                loc="left", fontsize=9.5, color=INK)

    c_ = axs[1, 0]
    yrs = S.index.to_numpy()
    cols = [C2 if y in mid else (C1 if y >= 2020 else MUTED) for y in yrs]
    c_.bar(yrs, S.ret, color=cols, width=0.8)
    c_.axhline(allw.mean(), color=INK, lw=1, ls="--")
    c_.annotate(f"any {len(SX.c['2025-10-12':'2025-12-31'])}-session window\nof the year: {allw.mean():+.1f}% avg", (2025.6, allw.mean()),
                xytext=(4, 0), textcoords="offset points", fontsize=8, color=INK, va="center")
    c_.set_xlim(1988.5, 2030)
    c_.axhline(0, color=MUTED, lw=0.7)
    txt = "   ".join(f"{k}: {v['mean']:+.1f}% avg, {v['pos']:.0%} up" for k, v in sout.items())
    c_.set_title(f"S&P from Oct 12 to Dec 31, every year since 1990 (orange = midterm years, blue = 2020+)\n{txt}",
                 loc="left", fontsize=9, color=INK)
    c_.set_ylabel("%")
    c_.grid(axis="x", visible=False)

    d = axs[1, 1]
    base_band(d, SX, 40, "2012-01-01")
    paths(d, SX, sres[25]["picks"], 40, C1, "25 days most like today: median")
    d.axhline(0, color=INK, lw=0.7)
    d.set_title("S&P: what followed the 25 days whose gamma / DIX / VIX state was most like today\n"
                "(gamma mid-range after the Sep 28 reset, DIX high, VIX 15)", loc="left", fontsize=9.5, color=INK)
    d.set_xlabel("sessions ahead (40 sessions from Oct 8 is about Dec 4)")
    d.set_ylabel("% from the analog day")
    d.legend(loc="upper left", fontsize=8)
    f.suptitle("MSFT: today's options state does not set up a continuation leg (8% vs 25% normally).\n"
               "S&P: today's state is neutral; the Q4 calendar is the tailwind (+4.9% avg, up 86% of years).",
               x=0.01, ha="left", fontsize=11, color=INK, weight="bold")
    f.tight_layout(rect=(0, 0, 1, 0.95))
    f.savefig(OUT / "outlook_msft_spx.png", dpi=150)


if __name__ == "__main__":
    ms = msft()
    sp = spx()
    sea = seasonality()
    figure(ms, sp, sea)
    print("saved", OUT / "outlook_msft_spx.png")
