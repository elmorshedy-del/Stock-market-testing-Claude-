"""Figure for REPORT.md section 4r: what the free/cheap data checks showed.

Inputs live outside the repo (licensed or bulky): the daily gamma table from
hd_gamma.py and the per-series calibration table from the Databento/Cboe check.
Usage: python data_checks_fig.py <hd_gamma_daily.csv> <calib_series.csv>
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import DATA, OUT, load_bars
from earnings_implied import past_reports, upcoming

C1, C2, C3, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e6e5e0"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True,
                     "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
                     "legend.frameon": False})


def z(s):
    return (s - s.mean()) / s.std()


def main(hd_csv, calib_csv):
    m = pd.read_csv(hd_csv, parse_dates=["date"])
    dix = pd.read_csv(DATA / "DIX.csv", parse_dates=["date"]).set_index("date")
    spx = m[m.und == "SPX"].set_index("date").gex_classic
    j = pd.DataFrame({"mine": spx, "sqz": dix.gex.reindex(spx.index)}).dropna()

    t = m[m.und == "TSLA"].set_index("date")
    r = np.log(load_bars("TSLA").close).diff()
    tx = pd.DataFrame({"g": t.gex_classic / (t.spot * (t.call_oi + t.put_oi) * 100), "abs0": r.reindex(t.index).abs()}).dropna()
    tx["q"] = pd.qcut(tx.g, 3, labels=["low", "mid", "high"])
    tb = tx.groupby("q", observed=True).agg(move=("abs0", lambda s: 100 * s.mean()), big=("abs0", lambda s: int((s > 0.05).sum())),
                                            n=("abs0", "size"))

    cb = pd.read_csv(calib_csv)
    cb = cb[cb.total_exchange_vol > 0]
    cal = cb.groupby(["und", "cp"]).agg(true=("cust_net", "sum"), rebuilt=("net_lr_XCBO", "sum"))

    e = past_reports().dropna(subset=["implied_pct"])
    nxt = upcoming("TSLA", "2026-10-09", "2026-10-22")

    fig, ax = plt.subplots(2, 2, figsize=(11, 8))
    a = ax[0, 0]
    a.plot(j.index, z(j.sqz), color=C2, lw=2, label="SqueezeMetrics GEX (published)")
    a.plot(j.index, z(j.mine), color=C1, lw=2, label="rebuilt from open interest (SPX+SPXW)")
    a.axhline(0, color=MUTED, lw=0.8)
    a.set_title(f"1. S&P dealer gamma rebuilt from OI matches the published series\n"
                f"Jul-Dec 2022, both standardised; corr {j.mine.corr(j.sqz):.2f}, daily changes "
                f"{j.mine.diff().corr(j.sqz.diff()):.2f}", loc="left", fontsize=9.5, color=INK)
    a.set_ylabel("standard deviations from the period mean")
    a.legend(loc="upper left", fontsize=8)

    a = ax[0, 1]
    xs = np.arange(len(tb))
    bars = a.bar(xs, tb.move, color=[C2, MUTED, C1], width=0.6)
    for x, (mv, big, n) in zip(xs, tb[["move", "big", "n"]].itertuples(index=False)):
        a.annotate(f"{mv:.1f}%\n{big} days > 5% (of {n})", (x, mv), ha="center", va="bottom", fontsize=8, color=INK,
                   xytext=(0, 3), textcoords="offset points")
    a.set_xticks(xs, ["low TSLA gamma", "mid", "high TSLA gamma"])
    a.set_ylabel("average size of the next session's move, %")
    a.set_ylim(0, tb.move.max() * 1.35)
    a.set_title("2. TSLA's own gamma (going into the session) vs that session's move\n"
                "Jul-Dec 2022; survives controls for past vol, trend, S&P gamma", loc="left", fontsize=9.5, color=INK)
    a.grid(axis="x", visible=False)

    a = ax[1, 0]
    labels = [f"{u} {'calls' if cp == 'C' else 'puts'}" for u, cp in cal.index]
    ys = np.arange(len(cal))
    a.barh(ys + 0.2, cal.true / 1e3, height=0.38, color=C3, label="true (Cboe Open-Close)")
    a.barh(ys - 0.2, cal.rebuilt / 1e3, height=0.38, color=MUTED, label="rebuilt from ticks")
    a.axvline(0, color=INK, lw=0.8)
    a.set_yticks(ys, labels)
    a.invert_yaxis()
    a.set_xlabel("net contracts bought by customers on Cboe, thousands (2025-03-28)")
    a.set_title("3. Inferring buy/sell from ticks does not recover customer direction\n"
                "TSLA calls: customers net BOUGHT, the tick rebuild says they sold", loc="left", fontsize=9.5, color=INK)
    a.legend(loc="lower left", fontsize=8)
    a.grid(axis="y", visible=False)

    a = ax[1, 1]
    lim = max(e.implied_pct.max(), e.actual_pct.abs().max()) * 1.1
    a.plot([0, lim], [0, lim], color=MUTED, lw=1, ls="--")
    a.annotate("moved exactly as priced", (lim * 0.62, lim * 0.66), rotation=33, color=MUTED, fontsize=8)
    up = e.actual_pct > 0
    a.scatter(e.implied_pct[up], e.actual_pct[up].abs(), s=46, color=C3, edgecolor="#fcfcfb", lw=1.5, label="report day up", zorder=3)
    a.scatter(e.implied_pct[~up], e.actual_pct[~up].abs(), s=46, color=C2, edgecolor="#fcfcfb", lw=1.5, label="report day down", zorder=3)
    for _, rw in e.iterrows():
        if str(rw.reaction) in ("2024-10-24", "2024-01-25", "2025-01-30", "2025-10-23"):
            a.annotate(pd.Timestamp(rw.reaction).strftime("%b '%y"), (rw.implied_pct, abs(rw.actual_pct)), fontsize=7.5,
                       color=INK, xytext=(4, 2), textcoords="offset points")
    a.axvline(nxt["implied_pct"], color=C1, lw=2)
    a.annotate(f"next report (Oct 21, 2026)\npriced at {nxt['implied_pct']:.1f}%", (nxt["implied_pct"], lim * 0.74), color=C1, fontsize=8,
               xytext=(5, 0), textcoords="offset points", ha="left", va="top")
    a.set_xlim(0, lim); a.set_ylim(0, lim)
    a.set_xlabel("options-implied earnings-day move, %")
    a.set_ylabel("actual earnings-day move, %")
    a.set_title(f"4. Tesla reports since 2021: priced vs actual move (n={len(e)})\n"
                f"median actual/priced {e.ratio.median():.2f}: fairly priced on average", loc="left", fontsize=9.5, color=INK)
    a.legend(loc="lower right", fontsize=8)

    fig.tight_layout()
    fig.savefig(OUT / "data_checks.png", dpi=150)
    print("saved", OUT / "data_checks.png")


if __name__ == "__main__":
    main(*sys.argv[1:3])
