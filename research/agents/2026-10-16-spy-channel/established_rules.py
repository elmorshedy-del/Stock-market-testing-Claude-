"""Follow-up: the S&P rules this repository already tested (REPORT §4f, §4i, §4p), applied day by day under the owner's
SPY channel, the way TSLA's full setup was. No new rule, threshold or test: rung definitions come from ladder.rungs,
reset/built/ran from reset.prep, ARMED/IGNITION from §4f's chosen parameters. The odds are recomputed with the original
code on today's data (both eras) so they can be checked against the report.
Usage: OMP_NUM_THREADS=1 python established_rules.py -> out/rules_daily.csv, out/rules_odds.csv, out/rules_touches.csv, out/spy_rules.png"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import spy_channel as S

sys.path.insert(0, str(S.MICRO))
os.chdir(S.MICRO)                                   # forecast/reset read data/ by relative path
from backtest import third_fridays                 # noqa: E402  (originals, imported unchanged)
from ladder import call_spread, first_on, outcomes, rungs, summarize   # noqa: E402
from release import frame as rframe                 # noqa: E402
from reset import prep                             # noqa: E402

ARM, K, PIN = 0.05, 0.25, 0.95                     # §4f: chosen on 2012-2018, tested 2019-2026
RNG = np.random.default_rng(0)


def build_fresh():
    """forecast.build() with the committed history topped up by the fresh bars and DIX in this folder's data/."""
    d = rframe()
    for name, col in (("GSPC", "c"), ("VIX", "VIX"), ("VIX3M", "VIX3M"), ("VIX9D", "VIX9D")):
        if (S.DATA / f"{name}_1d.json").exists():
            fresh = S.bars(name, "^" + name).close
            d = d.reindex(d.index.union(fresh.index))
            d.loc[fresh.index, col] = fresh
    d = d.ffill()
    g = pd.read_csv(S.DATA / "DIX.csv" if (S.DATA / "DIX.csv").exists() else S.MICRO / "data" / "DIX.csv", parse_dates=["date"]).set_index("date")
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


def states(f):
    R = pd.DataFrame(rungs(f))
    x = prep(f)
    R["reset in the prior 20 days (GEX <= 0.30)"] = x.reset_prev20
    R["gamma ran with no price"] = x.ran
    R["pinned (GEX >= 0.90)"] = f.gex_pct >= 0.90
    armed = f.gex_pct.rolling(15).min() <= ARM
    R["ARMED (GEX <= 0.05 within 15 days)"] = armed
    R["IGNITION while armed (VIX >= 25% off its 10-day max)"] = armed & (f.VIX <= (1 - K) * f.VIX.rolling(10).max())
    return R.fillna(False).astype(bool), x


def odds(f, R):
    """P(up-leg starts within 20 sessions) per rule, first-on events >= 10 days apart, as ladder.py measures it."""
    o = outcomes(f)
    o["spread60"] = call_spread(f)
    rows = []
    for start, lab in ((None, "2012-2026"), ("2019-10-01", "2019Q4-2026")):
        m = np.ones(len(f), bool) if start is None else (f.index >= start)
        oo, RR = o[m], R[m]
        base = summarize(oo, np.ones(len(oo), bool), RNG)
        rows.append({"rule": "any day", "era": lab, "events": base["n"], "P(up-leg within 20)": base["p_leg"]})
        for name in RR:
            if name.startswith(("reset in", "pinned")):
                continue
            r = summarize(oo, first_on(RR[name]), RNG)
            if r:
                rows.append({"rule": name, "era": lab, "events": r["n"], "P(up-leg within 20)": r["p_leg"]})
    return pd.DataFrame(rows).pivot(index="rule", columns="era", values=["P(up-leg within 20)", "events"])


def touches(T, R, x, f):
    rows = []
    for _, t in T.iterrows():
        d0 = pd.Timestamp(t["first touch"])
        hit = pd.Timestamp(t["reached the upper line"]) if t["reached the upper line"] is not None else None
        end = hit if hit is not None else d0 + pd.offsets.BDay(int(t["sessions in episode"]))
        w = R.loc[d0 - pd.offsets.BDay(10):end]
        legs = x.loc[d0 - pd.offsets.BDay(10):end]
        on = [c.split(" ")[0] if c[0] == "R" else c.split(" (")[0] for c in R if w[c].any() and not c.startswith(("pinned", "gamma ran"))]
        rows.append({"touch": d0.date(), "reached the upper line": t["reached the upper line"],
                     "rules on from 10 sessions before to the outcome": ", ".join(on) or "none",
                     "tested up-leg started": ", ".join(str(i.date()) for i in legs.index[legs.leg_start]) or "none",
                     "GEX pct at the upper line": round(float(f.gex_pct.loc[hit]), 2) if hit is not None else None,
                     "gamma ran with no price in window": bool(w["gamma ran with no price"].any())})
    return pd.DataFrame(rows)


def figure(D, L, spy, T, R, x, f, odd):
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": S.MUTED, "axes.labelcolor": S.MUTED, "xtick.color": S.MUTED, "ytick.color": S.MUTED,
                         "figure.facecolor": S.SURF, "axes.facecolor": S.SURF, "axes.spines.top": False, "axes.spines.right": False})
    show = [("reset in the prior 20 days (GEX <= 0.30)", "Reset in the prior 20 days: 88-90% of legs had one (vs 71-73% of days)", S.MUTED),
            ("R1 GEX pct <= 0.30", "R1  GEX <= 30th pct", S.BLUE),
            ("R2 GEX pct <= 0.30 + DIX>0.5", "R2  GEX <= 30th + DIX > 50th", S.BLUE),
            ("R3 GEX pct <= 0.20", "R3  GEX <= 20th pct", S.BLUE),
            ("R5 GEX <= 0.20 + 2% dip + DIX>0.5", "R5  GEX <= 20th + 2% dip + DIX > 50th", S.BLUE),
            ("R7 low GEX recently + VIX 25% off 10d max", "R7  low GEX recently + VIX 25% off its high", S.GREEN),
            ("ARMED (GEX <= 0.05 within 15 days)", "4f ARMED: GEX <= 5th pct within 15 days", S.ORANGE),
            ("IGNITION while armed (VIX >= 25% off its 10-day max)", "4f IGNITION (entry)", S.ORANGE),
            ("R0 today-like: mid GEX (0.35-0.55) + DIX>0.8", "R0  mid GEX + DIX > 80th", S.MUTED),
            ("gamma ran with no price", "Gamma ran with no price: lowers the odds (27% vs 44%)", S.INK),
            ("pinned (GEX >= 0.90)", "Pinned: leg ends here; a pause, not a top", S.INK)]
    f_ = plt.figure(figsize=(16, 14))
    gs = f_.add_gridspec(2, 1, height_ratios=[2.2, 2.0], hspace=0.06)
    ax, ar = f_.add_subplot(gs[0]), f_.add_subplot(gs[1])
    start = pd.Timestamp("2026-03-20")              # earlier than the channel, to show the run-up to the April leg
    Lf = L[(L.index >= start) & (L.index <= S.LAST_CLOSE + pd.offsets.BDay(10))]
    X = lambda idx: Lf.index.get_indexer(pd.DatetimeIndex(idx))
    P = spy[(spy.index >= start)]
    xp = X(P.index)
    drawn = Lf.index >= pd.Timestamp("2026-03-25")   # where the owner's lines begin
    for k, lw in (("upper", 2.0), ("mid", 1.3), ("lower", 2.0)):
        ax.plot(np.arange(len(Lf))[drawn], Lf[k][drawn], color=S.CHAN, lw=lw, alpha=0.8)
    ax.vlines(xp, P.low, P.high, color=S.MUTED, lw=0.8, alpha=0.6)
    ax.plot(xp[:-1], P.close.iloc[:-1], color=S.INK, lw=1.8)
    ax.plot(xp[-2:], P.close.iloc[-2:], color=S.INK, lw=1.8, ls=":")
    for _, t in T.iterrows():
        if t["reached the upper line"] is not None:
            h = pd.Timestamp(t["reached the upper line"])
            ax.annotate(f"upper line {h:%b %d}\nGEX pct {f.gex_pct.loc[h]:.2f}: pinned", xy=(X([h])[0], P.high.loc[h]), xytext=(X([h])[0], P.high.loc[h] * 1.035),
                        ha="center", fontsize=8, color=S.INK, arrowprops=dict(arrowstyle="-", color=S.MUTED, lw=0.8))
    legs = x.index[x.leg_start & (x.index >= start)]
    for t in legs:
        ax.scatter(X([t]), [P.low.loc[t] * 0.992], marker="^", s=70, color=S.GREEN, zorder=6, edgecolor=S.INK, lw=0.6)
    for _, t in T.iterrows():
        d0 = pd.Timestamp(t["first touch"])
        ax.axvline(X([d0])[0], color=S.MUTED, ls=":", lw=1)
        ax.text(X([d0])[0] + 0.5, 845, f"touch {d0:%b %d}", fontsize=7.5, color=S.MUTED, rotation=90, va="top")
    ax.set_yscale("log")
    ax.set_yticks([650, 675, 700, 725, 750, 775, 800, 825], ["650", "675", "700", "725", "750", "775", "800", "825"])
    ax.minorticks_off()
    ax.set_ylim(625, 848)
    ax.set_ylabel("SPY (log)")
    ax.set_title("Your SPY channel. Green triangles = start of a tested S&P up-leg (a top-decile 10-day rise, about +3.5%)",
                 loc="left", fontsize=10, color=S.INK)
    Rr = R.reindex(Lf.index).fillna(False)
    for j, (col, lab, colr) in enumerate(show):
        y = len(show) - 1 - j
        on = Rr[col].to_numpy()
        for i in np.where(on)[0]:
            ar.add_patch(plt.Rectangle((i - 0.5, y - 0.36), 1, 0.72, color=colr, alpha=0.75 if col.startswith(("R", "ARMED", "IGN")) else 0.45, lw=0))
        key = next((r for r in odd.index if r == col), None)
        tail = ""
        if key is not None:
            a, b = odd.loc[key, ("P(up-leg within 20)", "2012-2026")], odd.loc[key, ("P(up-leg within 20)", "2019Q4-2026")]
            tail = f"   up-leg within 20: {100 * a:.0f}% / {100 * b:.0f}%"
        ar.text(len(Lf) + 0.5, y, lab + tail, va="center", fontsize=8, color=S.INK)
    a, b = odd.loc["any day", ("P(up-leg within 20)", "2012-2026")], odd.loc["any day", ("P(up-leg within 20)", "2019Q4-2026")]
    ar.text(len(Lf) + 0.5, -1.1, f"any day: {100 * a:.0f}% / {100 * b:.0f}%   (2012-2026 / 2019Q4-2026, the original ladder code on today's data)",
            va="center", fontsize=8, color=S.MUTED)
    for t in legs:
        ar.axvline(X([t])[0], color=S.GREEN, lw=1.2, alpha=0.7)
    ar.set_ylim(-1.6, len(show) - 0.4)
    ar.set_yticks([])
    for axx in (ax, ar):
        months = Lf.index.to_series().groupby(Lf.index.to_period("M")).first()
        axx.set_xticks(X(months.values), [d.strftime("%b") for d in months])
        axx.set_xlim(-1, len(Lf) + 1)
        axx.grid(axis="x", color=S.GRID, lw=0.6)
    ax.tick_params(labelbottom=False)
    ar.spines["left"].set_visible(False)
    f_.suptitle("The tested S&P rules, day by day, under your SPY channel (each strip = days the rule was on)",
                x=0.01, ha="left", fontsize=12, color=S.INK, weight="bold", y=0.915)
    f_.savefig(S.OUT / "spy_rules.png", dpi=140, bbox_inches="tight", facecolor=S.SURF)


def main():
    D, L, spy, vix, dix, fits, cal = S.frame()
    T = S.touches(D)
    f = build_fresh()
    R, x = states(f)
    odd = odds(f, R)
    TT = touches(T, R, x, f)
    keep = R[R.index >= "2026-04-01"].copy()
    keep[["gex_pct", "dix_pct", "VIX", "spx"]] = f.loc[keep.index, ["gex_pct", "dix_pct", "VIX", "c"]]
    keep["tested up-leg starts"] = x.leg_start.reindex(keep.index)
    keep.to_csv(S.OUT / "rules_daily.csv")
    odd.to_csv(S.OUT / "rules_odds.csv")
    TT.to_csv(S.OUT / "rules_touches.csv", index=False)
    figure(D, L, spy, T, R, x, f, odd)
    return f, R, x, odd, TT


if __name__ == "__main__":
    f, R, x, odd, TT = main()
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 20)
    pd.set_option("display.max_colwidth", 80)
    print(odd.round(2).to_string())
    print(TT.to_string(index=False))
    print("tested up-leg starts 2026:", [str(t.date()) for t in x.index[x.leg_start & (x.index >= "2026-01-01")]])
    last = f.index[-1]
    print("\nNOW", last.date(), {k: round(float(f.loc[last, k]), 3) for k in ("gex_pct", "dix_pct", "VIX", "c")},
          "| S&P vs 10d high %.1f%%" % (100 * (f.c.iloc[-1] / f.c.iloc[-10:].max() - 1)))
    for c in R:
        print(f"  {'ON ' if R[c].iloc[-1] else 'off'}  {c}")
    print("GEX pct last 10:", f.gex_pct.iloc[-10:].round(2).tolist())
