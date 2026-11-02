"""Live-read figure Nov 2: week fans (options-implied), gamma profiles, forecasts. Usage: python figure.py -> out/live_read_1102.png"""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent; P = json.load(open(HERE / "out" / "project.json")); C = json.load(open(HERE / "out" / "curves_ext.json"))
BLUE, ORG, BG, INK, INK2, GRID, GRAY = "#2a78d6", "#eb6834", "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#a9a8a3"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False})
fig = plt.figure(figsize=(18, 12.2), facecolor=BG)
gs = fig.add_gridspec(2, 3, width_ratios=[2.5, 0.8, 1.6], hspace=0.32, wspace=0.12, left=0.05, right=0.985, top=0.885, bottom=0.05)
fig.text(0.02, 0.955, "SPY sits 1% under its flip with a deep pocket below; TSLA is cushioned, with a lighter stretch at 420–440", fontsize=19, weight="bold", color=INK)
fig.text(0.02, 0.91, "Mon Nov 2, 08:20 ET pre-market. Bands = options-implied range (Oct 30 chains, no drift). Gamma = dealer total gamma from Friday-close positions (Nov 2 OI), $bn per 1% move.\n"
         "Orange = dealers amplify moves (short gamma); blue = they damp them. Forecasts were pushed to git before the open; scored Mon close and Fri Nov 6.", fontsize=11, color=INK2)
X = ["Fri\nclose", "Mon\npre", "Mon", "Tue\nvote", "Wed\nresults", "Thu", "Fri\njobs"]


def fan(ax, sym, fri, pre, lv, pocket, ylim, scen):
    b = P[sym]["daily close bands (5/16/50/84/95 pct)"]; d = list(b.values()); xs = np.arange(2, 7)
    p = np.array(d)
    ax.fill_between(np.r_[1, xs], np.r_[pre, p[:, 0]], np.r_[pre, p[:, 4]], color=BLUE, alpha=0.12, lw=0)
    ax.fill_between(np.r_[1, xs], np.r_[pre, p[:, 1]], np.r_[pre, p[:, 3]], color=BLUE, alpha=0.25, lw=0)
    ax.plot([0, 1], [fri, pre], color=INK, lw=2); ax.plot(np.r_[1, xs], np.r_[pre, p[:, 2]], color=BLUE, lw=1.6, ls="--")
    if pocket: ax.axhspan(*pocket, color=ORG, alpha=0.13, lw=0); ax.text(0.05, pocket[0] + 0.6 * (ylim[1] - ylim[0]) / 100, "pocket: dealers amplify most", fontsize=9, color=ORG)
    for name, y, col in lv:
        ax.axhline(y, color=col, lw=1.1, ls=":" if col == GRAY else "-", alpha=0.9); ax.text(6.95, y, f" {name}", va="bottom", fontsize=9.3, color=col)
    for k, (lab, lo, hi, col) in enumerate(scen):
        xx = 9.0 + 0.42 * k; ax.plot([xx, xx], [lo, hi], color=col, lw=6, solid_capstyle="butt", alpha=0.85); ax.text(xx, hi + 0.012 * (ylim[1] - ylim[0]), lab, ha="center", fontsize=8.8, color=INK)
    ax.set_xticks(range(7)); ax.set_xticklabels(X, fontsize=9.6); ax.set_xlim(-0.2, 10.2); ax.set_ylim(*ylim); ax.yaxis.grid(True, color=GRID); ax.set_facecolor(BG)
    ax.text(0.0, p[4, 4], "90% range", fontsize=8.6, color=BLUE, alpha=0.8)


def prof(ax, sym, ylim, spot):
    c = C[sym]; y = np.array(c["price"]); g = np.array(c["total gamma $bn per 1%"]); m = (y >= ylim[0]) & (y <= ylim[1]); y, g = y[m], g[m]
    ax.fill_betweenx(y, 0, g, where=g < 0, color=ORG, alpha=0.75, lw=0); ax.fill_betweenx(y, 0, g, where=g >= 0, color=BLUE, alpha=0.75, lw=0)
    ax.axvline(0, color=INK2, lw=1); ax.axhline(spot, color=INK, lw=1.2); ax.set_ylim(*ylim); ax.set_yticklabels([]); ax.xaxis.grid(True, color=GRID); ax.set_facecolor(BG)
    ax.set_xlabel("dealer gamma, $bn per 1%", fontsize=9.5)


ax = fig.add_subplot(gs[0, 0]); yl = (724, 792)
fan(ax, "SPY", 755.72, 758.60, [("call-side 780", 780, GRAY), ("774 (old flip)", 774, GRAY), ("flip 766.4", 766.43, BLUE), ("put wall 750", 750, ORG), ("kill line 740.6", 740.6, GRAY)],
    (730, 745), yl, [("A 40%", 765, 778, BLUE), ("B 38%", 750, 765, GRAY), ("C 22%", 736, 748, ORG)])
ax.set_title("SPY: 758.6 pre-market, 1.0% below the flip", loc="left", fontsize=14, weight="bold", color=INK)
ax2 = fig.add_subplot(gs[0, 1]); prof(ax2, "SPY", yl, 758.6); ax2.set_title("SPY gamma by price", loc="left", fontsize=12, weight="bold", color=INK)
ax2.text(1.0, 736, "−21 in the\npocket", fontsize=9, color=ORG); ax2.text(-20, 783, "+8.5 at 780\n(stall zone)", fontsize=9, color=BLUE)

ax = fig.add_subplot(gs[1, 0]); yl = (352, 462)
fan(ax, "TSLA", 399.81, 402.22, [("450: damping peak", 450, GRAY), ("440", 440, GRAY), ("420: next wall", 420, BLUE), ("410", 410, GRAY), ("call wall 400 (pin)", 400, BLUE), ("put wall 380, flip ~377-381", 380, ORG)],
    None, yl, [("A 40%", 410, 425, BLUE), ("B 35%", 395, 410, GRAY), ("C 25%", 380, 390, ORG)])
ax.axhspan(420, 440, color=BLUE, alpha=0.07, lw=0); ax.text(0.05, 431, "420–440 plateau: damping stops rising, lighter travel", fontsize=9, color=BLUE)
ax.axhspan(352, 381, color=ORG, alpha=0.10, lw=0); ax.text(0.05, 362, "below ~381: the only amplifying zone", fontsize=9, color=ORG)
ax.set_title("TSLA: 402.2 pre-market, 6% above its flip (cushioned)", loc="left", fontsize=14, weight="bold", color=INK)
ax2 = fig.add_subplot(gs[1, 1]); prof(ax2, "TSLA", yl, 402.22); ax2.set_title("TSLA gamma by price", loc="left", fontsize=12, weight="bold", color=INK)

for r, (title, rows) in enumerate([("SPY forecasts (map → my call)", [("Mon close > 755.72", "65", "65"), ("Mon close 751–766", "68", "70"), ("Hits 766.4 (flip) by Fri", "62", "65"), ("Fri close ≥ 766.4", "32", "35"),
                                                                       ("Hits 750 (put wall) by Fri", "60", "50"), ("Fri close > 755.72", "56", "60"), ("Fri close ≤ 740.6", "15", "12"), ("VIX close ≤ 16.5 by Fri", "–", "25")]),
                                    ("TSLA forecasts (map → my call)", [("Mon close > 399.81", "59", "62"), ("Mon close 395–410 (pin)", "–", "60"), ("Hits 420 by Fri", "46", "45"), ("Fri close ≥ 420", "24", "20"),
                                                                        ("Hits 380 by Fri", "37", "30"), ("Fri close > 399.81", "52", "57")])]):
    ax = fig.add_subplot(gs[r, 2]); ax.axis("off"); ax.set_title(title, loc="left", fontsize=13, weight="bold", color=INK)
    ax.text(0.0, 0.97, "forecast", fontsize=9.6, color=INK2, transform=ax.transAxes); ax.text(0.66, 0.97, "map %", fontsize=9.6, color=INK2, transform=ax.transAxes); ax.text(0.83, 0.97, "my %", fontsize=9.6, color=INK2, transform=ax.transAxes)
    for i, (f, m, c) in enumerate(rows):
        y = 0.88 - i * 0.075; ax.text(0.0, y, f, fontsize=10.2, color=INK, transform=ax.transAxes); ax.text(0.68, y, m, fontsize=10.2, color=INK2, transform=ax.transAxes); ax.text(0.85, y, c, fontsize=10.2, color=INK, weight="bold", transform=ax.transAxes)
    note = ("Pocket in reverse? Yes. Below its flip SPY's big up-days are 2.8× more\nlikely (p<0.001); big down-days are not raised. But today the push is\nlopsided: −21 in the pocket vs −8 → 0 on the way up to 766."
            if r == 0 else "Upside pockets? No amplifying pocket above. Damping thickens 400→420\n(grind), then plateaus 420→440 (lighter run). Monday up-bursts 1.95×\n(p<0.001); freed state on (23rd pct): up-bursts 1.8×.")
    ax.text(0.0, 0.88 - len(rows) * 0.075 - 0.05, note, fontsize=9.6, color=INK2, transform=ax.transAxes, va="top")
fig.savefig(HERE / "out" / "live_read_1102.png", dpi=110, facecolor=BG); print("ok")
