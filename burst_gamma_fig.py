"""Figure for REPORT 4t: every up-burst since 2021 on the price chart, coloured by how much
open interest sat near the price the day before; and, per stock, burst odds in the
'freed' state (little OI near the price) split by whether positioning is supportive
(not put-heavy and above the own flip).
Usage: python burst_gamma_fig.py TSLA MSFT MU NVDA     (first symbol gets the timeline)
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from burst_gamma import events, state
from common import OUT, load_bars

C1, C2, C3, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e6e5e0"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True,
                     "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
                     "legend.frameon": False})
LEVELS = [("low", C3, "little OI near the price (bottom third)"), ("mid", MUTED, "middle third"),
          ("high", C2, "lots of OI near the price (top third)")]


def bucket(v):
    return np.select([v <= 1 / 3, v >= 2 / 3], ["low", "high"], "mid")


def main(syms):
    sym = syms[0]
    e, s = events(sym)
    e["lvl"] = bucket(e.near_oi_pct)
    c = load_bars(sym).close
    c = c[c.index >= "2021-01-01"]
    fig = plt.figure(figsize=(12, 7.6))
    gs = fig.add_gridspec(2, len(syms), height_ratios=[1.35, 1])
    a = fig.add_subplot(gs[0, :])
    a.set_yscale("log")
    a.plot(c.index, c, color=INK, lw=1.2, label=f"{sym} close")
    lo = (s.near_pct <= 1 / 3).reindex(c.index).fillna(False)
    a.fill_between(c.index, c.min() * 0.9, c.max() * 1.1, where=lo, color=C3, alpha=0.10, lw=0,
                   label="days with little OI near the price")
    for key, col, lab in LEVELS:
        z = e[e.lvl == key]
        d = pd.to_datetime(z.burst)
        a.scatter(d, c.reindex(d) * 0.9, marker="^", s=70, color=col, edgecolor="#fcfcfb", lw=1.2, zorder=4,
                  label=f"up-burst after {lab} ({len(z)})")
    a.set_ylim(c.min() * 0.75, c.max() * 1.15)
    a.legend(loc="lower right", fontsize=8)
    share = (e.lvl == "low").mean()
    base = (s.near_pct[s.index >= "2021-01-01"] <= 1 / 3).mean()
    a.set_title(f"{sym} up-bursts since 2021 and the open interest sitting near the price the day before\n"
                f"{share:.0%} of up-bursts started from 'little OI near the price' vs {base:.0%} of all days",
                loc="left", fontsize=10, color=INK)

    for k, sy in enumerate(syms):
        b = fig.add_subplot(gs[1, k])
        x = pd.read_csv(OUT / f"stock_gamma_frame_{sy}.csv", index_col=0, parse_dates=True)
        x = x.join(state(sy)[["near_pct"]])
        x = x[x.index >= "2021-01-01"].dropna(subset=["near_pct", "g_pct"])
        freed = x.near_pct <= 1 / 3
        ok = (x.g_pct > 1 / 3) & ~x.below.astype(bool)
        groups = [("freed +\nsupportive", freed & ok), ("freed +\nput-heavy\nor below flip", freed & ~ok), ("not freed", ~freed)]
        xs = np.arange(len(groups))
        up = [100 * x.loc[m, "sup3"].mean() for _, m in groups]
        dn = [100 * x.loc[m, "sdn3"].mean() for _, m in groups]
        b.bar(xs - 0.2, up, width=0.38, color=C3, label="up-burst")
        b.bar(xs + 0.2, dn, width=0.38, color=C2, label="down-burst")
        for i, (u, d) in enumerate(zip(up, dn)):
            b.annotate(f"{u:.0f}", (i - 0.2, u), ha="center", va="bottom", fontsize=7.5, xytext=(0, 1), textcoords="offset points")
            b.annotate(f"{d:.0f}", (i + 0.2, d), ha="center", va="bottom", fontsize=7.5, xytext=(0, 1), textcoords="offset points")
        b.set_xticks(xs, [g for g, _ in groups], fontsize=7.5)
        b.set_ylim(0, max(up + dn) * 1.2)
        b.set_title(sy, loc="left", fontsize=9.5, color=INK)
        b.grid(axis="x", visible=False)
        if k == 0:
            b.set_ylabel("% chance within 3 sessions\n(day beyond 2x own 60d vol)")
            b.legend(loc="upper right", fontsize=7.5)
    fig.tight_layout()
    fig.savefig(OUT / f"burst_gamma_{sym}.png", dpi=150)
    print("saved", OUT / f"burst_gamma_{sym}.png")


if __name__ == "__main__":
    main(sys.argv[1:] or ["TSLA", "MSFT", "MU", "NVDA"])
