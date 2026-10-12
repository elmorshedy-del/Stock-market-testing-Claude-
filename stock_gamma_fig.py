"""Figure for REPORT 4s: a stock's own gamma vs its bursts, and where it stands now.
Usage: python stock_gamma_fig.py TSLA      (after stock_gamma.py SYM)
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import OUT, load_bars

C1, C2, C3, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e6e5e0"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True,
                     "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
                     "legend.frameon": False})


def main(sym):
    x = pd.read_csv(OUT / f"stock_gamma_frame_{sym}.csv", index_col=0, parse_dates=True)
    x = x[x.index >= "2021-01-01"].dropna(subset=["g_pct"])
    above = x[~x.below.astype(bool)]
    x["bucket"] = "below own flip"
    x.loc[above.index, "bucket"] = pd.qcut(above.g_pct, 3, labels=["put-heavy", "balanced", "call-heavy"]).astype(str)
    order = ["below own flip", "put-heavy", "balanced", "call-heavy"]
    t = x.groupby("bucket").agg(days=("up3", "size"), up=("up3", "mean"), dn=("dn3", "mean")).reindex(order)

    fig, ax = plt.subplots(1, 2, figsize=(12, 4.8), gridspec_kw={"width_ratios": [1, 1.25]})
    a = ax[0]
    xs = np.arange(len(t))
    a.bar(xs - 0.2, 100 * t.dn, width=0.38, color=C2, label="down-burst in the next 3 sessions")
    a.bar(xs + 0.2, 100 * t.up, width=0.38, color=C3, label="up-burst in the next 3 sessions")
    for i, (d, u) in enumerate(zip(t.dn, t.up)):
        a.annotate(f"{100 * d:.0f}%", (i - 0.2, 100 * d), ha="center", va="bottom", fontsize=8, color=INK, xytext=(0, 2), textcoords="offset points")
        a.annotate(f"{100 * u:.0f}%", (i + 0.2, 100 * u), ha="center", va="bottom", fontsize=8, color=INK, xytext=(0, 2), textcoords="offset points")
    a.axhline(100 * x.dn3.mean(), color=C2, lw=1, ls=":")
    a.axhline(100 * x.up3.mean(), color=C3, lw=1, ls=":")
    a.set_xticks(xs, [f"{b}\n({n} days)" for b, n in zip(order, t.days)])
    a.set_ylabel("chance of a burst (+-5% day or +-9% in 2 days), %")
    a.set_ylim(0, 100 * max(t.dn.max(), t.up.max()) * 1.25)
    a.legend(loc="upper right", fontsize=8)
    a.grid(axis="x", visible=False)
    a.set_title(f"{sym} 2021-2026: its own option gamma vs bursts in the NEXT 3 sessions\nbelow the flip -> more up-bursts (snap-backs), "
                "not more down-bursts; calls don't 'squeeze' it up", loc="left", fontsize=9.5, color=INK)
    a.annotate("above-flip days split into terciles of own-gamma percentile; dotted = all days", (0, -0.2),
               xycoords="axes fraction", fontsize=7.5, color=MUTED)

    a = ax[1]
    z = x[x.index >= x.index[-1] - pd.Timedelta(days=180)]
    c = load_bars(sym).close.reindex(z.index)
    a.plot(z.index, c, color=INK, lw=2, label=f"{sym} close")
    a.plot(z.index, z.flip, color=C2, lw=2, label="own gamma flip (below = bigger moves, more snap-backs)")
    a.step(z.index, z.call_wall, where="post", color=C3, lw=1.5, label="call wall (largest near-term call OI)")
    a.step(z.index, z.put_wall, where="post", color=C1, lw=1.5, label="put wall (largest near-term put OI)")
    a.fill_between(z.index, c, z.flip, where=c < z.flip, color=C2, alpha=0.12, lw=0)
    last = z.index[-1]
    for y, lab, col in ((c.iloc[-1], f"{c.iloc[-1]:.0f}", INK), (z.flip.iloc[-1], f"flip {z.flip.iloc[-1]:.0f}", C2),
                        (z.call_wall.iloc[-1], f"{z.call_wall.iloc[-1]:.0f}", C3), (z.put_wall.iloc[-1], f"{z.put_wall.iloc[-1]:.0f}", C1)):
        a.annotate(lab, (last, y), xytext=(4, 0), textcoords="offset points", va="center", fontsize=8, color=col)
    a.set_title(f"{sym} last 6 months vs its own gamma levels (data to {last.date()})\n"
                f"now {100 * (c.iloc[-1] / z.flip.iloc[-1] - 1):+.1f}% above the flip; own gamma percentile {z.g_pct.iloc[-1]:.2f}",
                loc="left", fontsize=9.5, color=INK)
    a.legend(loc="upper center", bbox_to_anchor=(0.5, -0.09), ncol=2, fontsize=7.5)
    fig.tight_layout()
    fig.savefig(OUT / f"stock_gamma_{sym}.png", dpi=150)
    print("saved", OUT / f"stock_gamma_{sym}.png")


if __name__ == "__main__":
    main((sys.argv[1:] or ["TSLA"])[0])
