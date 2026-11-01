"""Equity curves for the pre-registered wall-short test -> out/wall_short.png"""
import json
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
O = Path(__file__).resolve().parent / "out"; BG, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
r = json.load(open(O / "wall_short.json"))
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": GRID,
                     "xtick.color": INK2, "ytick.color": INK2})
fig, ax = plt.subplots(figsize=(12, 6.2), facecolor=BG); ax.set_facecolor(BG)
for f, col, lab in (("trades_spy_chosen.csv", "#2a78d6", "SPY: short at the call wall"), ("trades_qqq_chosen.csv", "#eb6834", "QQQ: same rules")):
    T = pd.read_csv(O / f, parse_dates=["day"]); ax.step(T.day, 100 * T.ret.cumsum(), where="post", lw=2.4, color=col)
    ax.text(T.day.iloc[-1] + pd.Timedelta(days=12), 100 * T.ret.sum(), lab, color=col, va="center", fontsize=11, weight="bold")
ax.axvspan(pd.Timestamp("2024-01-01"), pd.Timestamp("2026-10-31"), color="#eeeeea", zorder=0)
ax.text(pd.Timestamp("2024-02-01"), 8.3, "untouched test period\n(rules picked before this)", color=INK2, fontsize=10, va="top")
ax.axhline(0, color=INK2, lw=1)
ax.text(pd.Timestamp("2020-03-01"), 4.2, "2022 bear market alone:\n+5.0 of the +6.0 total", color=INK2, fontsize=10)
ax.set_ylabel("cumulative profit, % of price (1 share-unit per trade, after costs)", color=INK2); ax.yaxis.grid(True, color=GRID)
ax.set_xlim(pd.Timestamp("2020-01-01"), pd.Timestamp("2027-09-01")); ax.set_ylim(-3.6, 8.6)
s, q, p = r["SPY full 2020-26"], r["T2 QQQ 2020-26 (same config)"], r["T3 placebo ordinary strike, SPY 2020-26"]
fig.text(0.06, 0.95, "Shorting at the call wall: small and not reliable (fails 3 of 3 untouched tests)", fontsize=16, weight="bold", color=INK)
fig.text(0.06, 0.905, f"Rules (chosen on 2020-23): sell at the wall, stop 0.25% above, exit at the close.  SPY {s['n']} trades: {s['mean % per trade']:+.3f}% per trade "
         f"(≈ ${0.01 * s['mean % per trade'] * 760:.2f}/share), \nwin rate {100 * s["win rate"]:.0f}%, p {s["p (mean<=0)"]:.2f}.  "
         f"QQQ {q['mean % per trade']:+.3f}% per trade (loses).  Ordinary-strike short {p['mean % per trade']:+.3f}% (loses).  "
         f"The wall stops the rise; it does not push price down.", fontsize=10.5, color=INK2, va="top")
fig.subplots_adjust(top=0.83, left=0.08, right=0.86, bottom=0.08)
fig.savefig(O / "wall_short.png", dpi=110, facecolor=BG)
