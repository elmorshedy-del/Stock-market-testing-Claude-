"""TSLA's October cycle, one picture: price + flip, own gamma, TSLA DIX (DPI), with the phases shaded. -> out/tsla_cycle_oct.png"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent; x = pd.read_csv(HERE / "out" / "tsla_cycle_oct.csv", parse_dates=["date"]).set_index("date").loc["2026-09-24":]
BLUE, ORG, BG, INK, INK2, GRID, GRAY = "#2a78d6", "#eb6834", "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#a9a8a3"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False})
fig, axs = plt.subplots(3, 1, figsize=(16, 12.5), sharex=True, facecolor=BG, gridspec_kw=dict(height_ratios=[1.35, 1, 1], hspace=0.12))
fig.subplots_adjust(left=0.07, right=0.97, top=0.86, bottom=0.06)
fig.text(0.02, 0.955, "TSLA's October cycle lined up: reset → rebuild with price → dip → bigger block → pinned stall", fontsize=19, weight="bold", color=INK)
fig.text(0.02, 0.915, "Own gamma and freed: engine recipe, positions going into each day. TSLA DIX = FINRA dark-pool index, 5-day mean ranked vs its past year.\n"
         "Descriptive map, not a test. Phases follow REPORT §4v (the named TSLA moves): flush at the flip → first block → dip → bigger block → stall into a pile of OI.", fontsize=11, color=INK2)
idx = list(x.index); pos = {d: i for i, d in enumerate(idx)}; X = range(len(idx))
P = [("RESET", "2026-10-14", "2026-10-16", ORG), ("BLOCK 1\n+9%", "2026-10-19", "2026-10-21", BLUE), ("DIP to\nthe flip", "2026-10-22", "2026-10-23", ORG),
     ("BLOCK 2\n+9.5%", "2026-10-26", "2026-10-27", BLUE), ("PINNED\nstall", "2026-10-28", "2026-10-30", GRAY)]
for ax in axs:
    ax.set_facecolor(BG)
    for lab, a, b, col in P: ax.axvspan(pos[pd.Timestamp(a)] - 0.45, pos[pd.Timestamp(b)] + 0.45, color=col, alpha=0.10, lw=0)
    ax.yaxis.grid(True, color=GRID)
ax = axs[0]; flip = x["spot (parity)"] / (1 + x["% above flip"] / 100)
ax.plot(X, x["spot (parity)"], color=INK, lw=2.4, marker="o", ms=4, label="TSLA"); ax.plot(X, flip, color=ORG, lw=1.6, ls="--", label="own gamma flip")
ax.step(X, x["call wall"], where="mid", color=BLUE, lw=1.3, alpha=0.8, label="call wall"); ax.set_ylabel("price"); ax.legend(fontsize=10, frameon=False, loc="upper left")
for lab, a, b, col in P: ax.text((pos[pd.Timestamp(a)] + pos[pd.Timestamp(b)]) / 2, 342, lab, ha="center", va="bottom", fontsize=11.5, weight="bold", color=col if col != GRAY else INK2)
ax.set_ylim(340, 425); ax.text(len(idx) - 0.6, 399.9, " now 402\n pre-mkt", fontsize=10, color=INK, va="center")
ax = axs[1]; ax.axhspan(0, 0.30, color=ORG, alpha=0.08, lw=0); ax.axhspan(0.90, 1.02, color=BLUE, alpha=0.10, lw=0)
ax.plot(X, x["own gamma pct"], color=BLUE, lw=2.4, marker="o", ms=4); ax.set_ylim(0, 1.02); ax.set_ylabel("own gamma pct")
ax.text(0.2, 0.05, "reset ≤ 0.30", fontsize=10, color=ORG); ax.text(0.2, 0.93, "pinned ≥ 0.90", fontsize=10, color=BLUE)
ax.annotate("0.14: flushed at the flip", (pos[pd.Timestamp("2026-10-16")], 0.14), (pos[pd.Timestamp("2026-10-16")] - 5.5, 0.42), fontsize=10, arrowprops=dict(arrowstyle="-", color=GRAY))
ax.annotate("1.00: pinned", (pos[pd.Timestamp("2026-10-27")], 1.0), (pos[pd.Timestamp("2026-10-27")] - 4.2, 0.72), fontsize=10, arrowprops=dict(arrowstyle="-", color=GRAY))
ax.annotate("0.66 after the\nOct 30 expiry", (pos[pd.Timestamp("2026-10-30")], 0.66), (pos[pd.Timestamp("2026-10-30")] - 2.6, 0.30), fontsize=10, arrowprops=dict(arrowstyle="-", color=GRAY))
ax = axs[2]; ax.plot(X, x["TSLA DPI 5d pct"], color=INK, lw=2.4, marker="o", ms=4, label="TSLA DIX (5-day pct)")
ax.plot(X, x["S&P GEX pct"], color=GRAY, lw=1.4, label="S&P gamma pct (for contrast)"); ax.set_ylim(0, 1.02); ax.set_ylabel("percentile")
ax.axhline(2 / 3, color=BLUE, ls=":", lw=1); ax.text(0.2, 0.69, "top third", fontsize=10, color=BLUE)
ax.annotate("1st pct: dark-pool\nselling washed out", (pos[pd.Timestamp("2026-10-15")], 0.01), (pos[pd.Timestamp("2026-10-15")] - 7, 0.25), fontsize=10, arrowprops=dict(arrowstyle="-", color=GRAY))
ax.annotate("75th: buying peaks\nwith the pin", (pos[pd.Timestamp("2026-10-27")], 0.75), (pos[pd.Timestamp("2026-10-27")] - 6.5, 0.88), fontsize=10, arrowprops=dict(arrowstyle="-", color=GRAY))
ax.legend(fontsize=10, frameon=False, loc="lower left")
ax.set_xticks(list(X)); ax.set_xticklabels([d.strftime("%b %d") for d in idx], rotation=60, fontsize=9)
fig.savefig(HERE / "out" / "tsla_cycle_oct.png", dpi=110, facecolor=BG); print("ok")
