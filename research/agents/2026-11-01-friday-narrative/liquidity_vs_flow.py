"""out/liquidity_vs_flow.png: refresher. Whole-day net aggression vs whole-day move for ES (SPY) and TSLA (flow-physics
A1 data, Oct 5-26), with Friday Oct 30 added; plus Friday's ES tape. Usage: python liquidity_vs_flow.py <db dir>"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; OUT = HERE / "out"; DB = Path(sys.argv[1]); ET = "America/New_York"
A = pd.read_csv(HERE.parent / "2026-10-27-flow-physics" / "out" / "a_daily.csv")
GREEN, RED, INK, MUTED, SURF, BLUE, AMBER = "#1baf7a", "#d64545", "#0b0b0b", "#52514e", "#fcfcfb", "#2a78d6", "#e8a33d"
plt.rcParams.update({"font.size": 11, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED, "text.parse_math": False,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})


def day(f, act=True):
    d = pd.read_parquet(DB / f)
    if act and "action" in d: d = d[d.action == "T"]
    d.index = d.index.tz_convert(ET); d = d.between_time("09:30", "15:58"); sz = d["size"].astype("int64")
    buy, sell = sz[d.side == "B"].sum(), sz[d.side == "A"].sum()
    return d, (buy - sell) / sz.sum() * 100, (d.price.iloc[-1] / d.price.iloc[0] - 1) * 100


esd, es_delta, es_ret = day("ES_trades_2026-10-30.parquet"); tsd, ts_delta, ts_ret = day("TSLA_trades_2026-10-30.parquet")
fig = plt.figure(figsize=(18, 12)); gs = fig.add_gridspec(2, 2, height_ratios=[1, 1], hspace=0.38, wspace=0.22)
for j, (sym, fd, fr, col, lab) in enumerate((("ES", es_delta, es_ret, BLUE, "SPY (S&P futures): LIQUIDITY-LED"), ("TSLA", ts_delta, ts_ret, AMBER, "TSLA: FLOW-LED"))):
    a = fig.add_subplot(gs[0, j]); g = A[A.sym == sym]
    a.scatter(g["delta % of vol"], g["ret %"], color=col, s=40, alpha=0.85, label=f"Oct 5-26 sessions (n {len(g)})")
    if len(g) > 2:
        b = np.polyfit(g["delta % of vol"], g["ret %"], 1); xx = np.linspace(g["delta % of vol"].min(), g["delta % of vol"].max(), 10); a.plot(xx, np.polyval(b, xx), color=col, lw=1.5)
    a.scatter([fd], [fr], color=RED, s=110, marker="*", zorder=5, label=f"Fri Oct 30: net {fd:+.1f}% of volume, move {fr:+.1f}%")
    a.axhline(0, color=MUTED, lw=0.5); a.axvline(0, color=MUTED, lw=0.5)
    rho = g["ret %"].corr(g["delta % of vol"], method="spearman")
    a.set_xlabel("whole-day net aggressive buying, % of volume"); a.set_ylabel("whole-day move (open → close), %")
    a.legend(frameon=False, loc="upper left", fontsize=9.5)
    a.set_title(f"{lab}\nwhole-day link between net buying and the day's move: ρ {rho:+.2f}", loc="left", fontsize=12.5, weight="bold", color=col)
a = fig.axes[0]; a.text(0.03, 0.05, "No line-up: SPY can fall on net buying (Oct 14, and Friday)\nbecause the day's move depends on how thin the book is", transform=a.transAxes, fontsize=10, color=INK)
a = fig.axes[1]; a.text(0.03, 0.05, "Clear line-up in the October sessions: the side that kept hitting won.\nFriday did NOT fit: Nasdaq net flow ~0, yet TSLA rose from the open\n(the 400-strike expiry pin is the untested lead, TODO WR1)", transform=a.transAxes, fontsize=10, color=INK)
# bottom-left: Friday ES tape
a = fig.add_subplot(gs[1, 0]); sz = esd["size"].astype("int64"); fl = (sz.where(esd.side == "B", 0) - sz.where(esd.side == "A", 0)).resample("1min").sum(); px = esd.price.resample("1min").last().ffill()
x = (fl.index.hour - 9.5) + fl.index.minute / 60
a.plot(x, px, color=INK, lw=1.3); a.set_ylabel("ES price")
a2 = a.twinx(); a2.plot(x, fl.cumsum() / 1000, color=GREEN, lw=2); a2.set_ylabel("net aggressive buying, cumulative (k)", color=GREEN); a2.spines["right"].set_visible(True)
a.set_xticks([0, 1, 2, 3, 4, 5, 6.5]); a.set_xticklabels(["9:30", "10:30", "11:30", "12:30", "13:30", "14:30", "16:00"])
a.set_title("Friday's S&P futures: net buying rose (green), price fell (black)", loc="left", fontsize=12.5, weight="bold", color=BLUE)
# bottom-right: rule card
b = fig.add_subplot(gs[1, 1]); b.axis("off")
rows = [("", "SPY / S&P futures", "TSLA"),
        ("What decides\nthe day's move", "how thin the book is\n(liquidity)", "who keeps pushing\n(aggressive flow)"),
        ("Why", "one giant central book; makers\nand dealers set the depth. In low\ngamma they post less, so normal\nflow moves price further", "a crowd of directional traders\n(retail, momentum, options);\nthe side that keeps hitting wins"),
        ("What to watch", "depth, VIX, dealer gamma:\nis liquidity coming back?", "net aggressive buying vs selling,\nand whether it keeps up"),
        ("Minute by minute", "both: every hit moves price (Friday 5-min link ES +0.70, TSLA +0.21)", "")]
xs = [0.0, 0.3, 0.68]
for i, r in enumerate(rows):
    y = 0.97 - i * 0.2
    for k, txt in enumerate(r):
        b.text(xs[k], y, txt, fontsize=10.5 if i else 12, weight="bold" if (i == 0 or k == 0) else "normal", color=[INK, BLUE, AMBER][k] if i == 0 else (MUTED if k == 0 else INK), va="top", transform=b.transAxes)
    if i: b.plot([0, 1], [y + 0.02, y + 0.02], color="#e5e4e0", lw=0.8, transform=b.transAxes)
b.set_title("The rule (flow-physics, Oct 2026)", loc="left", fontsize=12.5, weight="bold", color=INK)
fig.suptitle("Refresher: over a whole day, SPY is moved by liquidity and TSLA by flow (Friday fit SPY, not TSLA)", x=0.01, ha="left", fontsize=15.5, weight="bold", color=INK)
fig.savefig(OUT / "liquidity_vs_flow.png", dpi=115, bbox_inches="tight"); print("ok", round(es_delta, 2), round(es_ret, 2), round(ts_delta, 2), round(ts_ret, 2))
