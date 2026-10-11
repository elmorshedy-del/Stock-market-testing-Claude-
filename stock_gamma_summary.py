"""Cross-stock summary of own-gamma effects (REPORT 4s): controlled odds ratios of
volatility-scaled bursts (a day beyond 2x the stock's own 60-day vol, within 3 sessions)
when the stock's own gamma is put-heavy (bottom third of its trailing-year percentile)
or price is below its own gamma flip. Run stock_gamma.py for each ticker first.
Usage: python stock_gamma_summary.py TSLA MSFT MU NVDA
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import OUT
from stock_gamma import burst_logit

C1, C2, C3, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e6e5e0"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True,
                     "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
                     "legend.frameon": False})


def summary(syms):
    rows = []
    for sym in syms:
        x = pd.read_csv(OUT / f"stock_gamma_frame_{sym}.csv", index_col=0, parse_dates=True)
        x["low_g"] = (x.g_pct <= 1 / 3).astype(float)
        x["below"] = x.below.astype(float)
        for feat, lab in (("low_g", "put-heavy own gamma"), ("below", "below own flip")):
            for tgt, d in (("sdn3", "down-burst"), ("sup3", "up-burst")):
                r = burst_logit(x, tgt, feat)
                z = x[x.index >= "2021-01-01"].dropna(subset=["g_pct"])
                rows.append({"sym": sym, "condition": lab, "burst": d, "odds_ratio": r["odds_ratio"], "p": r["shifted_null_p"],
                             "rate_if": z.loc[z[feat] == 1, tgt].mean(), "rate_else": z.loc[z[feat] == 0, tgt].mean()})
    return pd.DataFrame(rows)


def fig(s):
    f, ax = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
    syms = list(dict.fromkeys(s.sym))
    for a, cond in zip(ax, ("put-heavy own gamma", "below own flip")):
        t = s[s.condition == cond]
        ys = np.arange(len(syms))
        for off, burst, col in ((-0.18, "down-burst", C2), (0.18, "up-burst", C3)):
            v = t[t.burst == burst].set_index("sym").reindex(syms)
            a.barh(ys + off, np.log2(v.odds_ratio), height=0.34, color=col, label=f"{burst} odds")
            for y, (o, p) in zip(ys + off, v[["odds_ratio", "p"]].itertuples(index=False)):
                star = "**" if p < 0.01 else "*" if p < 0.05 else ""
                a.annotate(f"x{o:.1f}{star}", (np.log2(o), y), xytext=(4 if o >= 1 else -4, 0), textcoords="offset points",
                           ha="left" if o >= 1 else "right", va="center", fontsize=8, color=INK)
        a.axvline(0, color=INK, lw=0.8)
        a.set_yticks(ys, syms)
        a.invert_yaxis()
        ticks = [0.25, 0.5, 1, 2, 4]
        a.set_xticks(np.log2(ticks), [f"x{t:g}" for t in ticks])
        a.set_xlim(np.log2(0.2), np.log2(5))
        a.set_xlabel("change in odds of a burst within 3 sessions (controlled)")
        a.set_title(f"when the stock is {cond}", loc="left", fontsize=9.5, color=INK)
        a.grid(axis="y", visible=False)
    ax[1].legend(loc="upper right", fontsize=8)
    f.suptitle("Each stock's own option gamma, 2021-2026: put-heavy positioning raises down-burst odds and lowers up-burst odds\n"
               "burst = a day beyond 2x the stock's own 60-day vol; controls: past 5/20d vol, past 20d return, S&P gamma; "
               "* p<0.05, ** p<0.01 (shifted null)", x=0.01, ha="left", fontsize=9.5, color=INK)
    f.tight_layout()
    f.savefig(OUT / "stock_gamma_summary.png", dpi=150)
    print("saved", OUT / "stock_gamma_summary.png")


if __name__ == "__main__":
    s = summary(sys.argv[1:] or ["TSLA", "MSFT", "MU", "NVDA"])
    s.to_csv(OUT / "stock_gamma_summary.csv", index=False)
    pd.set_option("display.width", 200)
    print(s.round(3).to_string(index=False))
    fig(s)
