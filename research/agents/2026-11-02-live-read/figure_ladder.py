"""Ladder board for Nov 2: rung status + lines, the week after past R4 first-days vs map vs my call, trigger table. -> out/ladder_1102.png"""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent; W = json.load(open(HERE / "out" / "ladder_week.json"))["R4 first days"]
BLUE, ORG, BG, INK, INK2, GRID, GRAY, LG = "#2a78d6", "#eb6834", "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#a9a8a3", "#efeeea"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False})
fig = plt.figure(figsize=(18, 11.5), facecolor=BG)
gs = fig.add_gridspec(2, 2, width_ratios=[1.25, 1], height_ratios=[1.05, 1], hspace=0.28, wspace=0.12, left=0.03, right=0.98, top=0.88, bottom=0.04)
fig.text(0.02, 0.955, "Per the ladder: R4 fired Friday. History says this week tests 750 first, then reaches for the 766 flip", fontsize=19, weight="bold", color=INK)
fig.text(0.02, 0.913, "S&P ladder (REPORT §4i) on SqueezeMetrics through Fri Oct 30: GEX $1.06bn (6th pct), DIX 43.8% (22nd pct), VIX 19.42, S&P 7,580. Up-leg = a top-decile 10-session S&P rise.\n"
         "History = the 5 sessions after every past R4 first-day (S&P highs/lows), mapped to SPY from Friday's 755.72. Calls registered pre-open (08:26, revised 08:35 ET).", fontsize=11, color=INK2)

ax = fig.add_subplot(gs[:, 0]); ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
ax.text(0.0, 0.985, "The ladder now", fontsize=14, weight="bold", color=INK)
rungs = [("R7", "VIX ≤ 0.75× its 10-day max", "needs VIX ≤ 14.59", "46% / 52%; naked calls pay here", False),
         ("R6", "low GEX recently + VIX ≤ 0.85× 10-day max", "needs VIX ≤ 16.53 (post-vote relief)", "55% / 66%", False),
         ("R5", "R4 + DIX > 50th (45.36%)", "a weak day (S&P ≤ 7,602 Mon–Tue, ≤ 7,589 Wed–Fri) with DIX > 45.36%", "73% / 83%", False),
         ("R4", "GEX ≤ 20th + S&P ≥ 2% off its 10-day high", "FIRED Fri Oct 30: lead ~4 sessions, window to ~Nov 27", "70% / 74%", True),
         ("R3", "GEX ≤ 20th pct ($3.35bn)", "on: GEX $1.06bn", "65% / 73%", True),
         ("R2", "GEX ≤ 30th + DIX > 50th", "needs DIX > 45.36% (was 45.8% Thu, 43.8% Fri)", "65% / 79%", False),
         ("R1", "GEX ≤ 30th pct ($4.53bn)", "on", "61% / 72%", True)]
ax.text(0.80, 0.94, "up-leg in 20 sessions\n2012–26 / 2019Q4–26", fontsize=9.5, color=INK2, ha="center")
for i, (r, cond, line, odds, on) in enumerate(rungs):
    y = 0.85 - i * 0.118
    if r == "R5": ax.plot([0.0, 0.98], [y + 0.056, y + 0.056], color=GRID, lw=1); ax.text(0.98, y + 0.061, "crush family (fires in recoveries) ↑   dip family (fires in selloffs) ↓", fontsize=9, color=INK2, ha="right")
    ax.add_patch(plt.Rectangle((0.0, y - 0.04), 0.09, 0.07, color=BLUE if on else LG, ec=BLUE if on else GRAY, lw=1.2))
    ax.text(0.045, y - 0.005, r, ha="center", va="center", fontsize=13, weight="bold", color="white" if on else INK2)
    ax.text(0.11, y + 0.012, cond, fontsize=11, color=INK, weight="bold" if on else "normal")
    ax.text(0.11, y - 0.028, line, fontsize=9.8, color=BLUE if on else INK2)
    ax.text(0.80, y - 0.005, odds, fontsize=10.5, color=INK if on else INK2, ha="center", weight="bold" if r == "R4" else "normal")
ax.text(0.0, 0.0, "Structure for R4/R5: 60-DTE ATM/+5% SPX/SPY call spread (odds edge yes; payoff edge not in 2019Q4–26). TSLA calls on a TSLA dip in R4 = worst entry (T5).", fontsize=9.5, color=INK2)

ax = fig.add_subplot(gs[0, 1]); ax.set_facecolor(BG)
labs = [("hits flip 766.4", "hits flip 766.4", 62, 60), ("hits 774", "hits 774", 35, None), ("hits put wall 750", "hits put wall 750", 60, 65), ("hits pocket floor 743.6", "hits pocket floor 743.6", 37, 45)]
eras = [("2012-26", GRAY), ("2019Q4-26", INK2), ("2022+", BLUE)]; y0 = np.arange(len(labs))[::-1]
for j, (era, col) in enumerate(eras):
    ax.barh(y0 + 0.25 - j * 0.25, [100 * W[era][k] for _, k, _, _ in labs], height=0.22, color=col, label=f"R4 weeks {era} (n {W[era]['n']})")
for yy, (_, _, m, c) in zip(y0, labs):
    ax.plot(m, yy + 0.42, "v", color=INK, ms=7); 
    if c: ax.plot(c, yy + 0.42, "v", color=ORG, ms=9)
ax.set_yticks(y0); ax.set_yticklabels(["Hits the flip 766.4", "Hits 774", "Hits the put wall 750", "Hits the pocket floor 743.6"], fontsize=10.5)
ax.set_xlim(0, 100); ax.xaxis.grid(True, color=GRID); ax.set_xlabel("% of weeks (by Fri Nov 6)"); ax.legend(fontsize=9, frameon=False, loc="lower right")
ax.text(0.0, -0.2, "▼ black = options map   ▼ orange = my revised call (08:35 ET)", fontsize=9.3, color=INK2, transform=ax.transAxes)
ax.set_title("SPY this week: what R4 weeks did", loc="left", fontsize=14, weight="bold", color=INK)

ax = fig.add_subplot(gs[1, 1]); ax.axis("off"); ax.set_title("Trigger table, today's lines", loc="left", fontsize=14, weight="bold", color=INK)
T = [("S1", "SPY at the flip 766.4: trim calls; a hold above = damped to 780/800", BLUE), ("S2", "Pocket 730–745: amplified, but don't chase puts (snap-backs 2.8×)", ORG),
     ("S3", "R4 fired Fri; R5 = weak day + DIX > 45.36% → call spread", BLUE), ("S4", "VIX ≤ 16.53 = R6, ≤ 14.59 = R7 (naked calls pay); now 19.4", GRAY),
     ("S5", "Fri −1.82% → about a third back in 5 sessions (+0.6%)", BLUE), ("T1", "TSLA 400 = call wall, today's pin (+15.6k calls Fri)", BLUE),
     ("T2", "TSLA freed (23rd pct): up-bursts 1.8×; IV 41% no longer cheap", BLUE), ("T3", "Risk reversal −4.8 (puts bid): fragile-run trigger off", GRAY),
     ("T4", "TSLA < ~377–381 while freed = full setup (39% up / 17% down)", GRAY), ("T5", "LIVE: S&P in R4 → no TSLA calls on a TSLA dip; use SPY spreads", ORG),
     ("T6", "TSLA own gamma 65th pct: rallies made now hold better", BLUE), ("C1/C2", "VIX ≤ 16.5 thru Nov 6 → SPY ≥ 774 by Nov 13; VIX > 17 all week → no", GRAY)]
for i, (k, t, col) in enumerate(T):
    y = 0.95 - i * 0.083; ax.add_patch(plt.Circle((0.012, y + 0.012), 0.009, color=col, transform=ax.transAxes))
    ax.text(0.035, y, k, fontsize=10.5, weight="bold", color=INK, transform=ax.transAxes); ax.text(0.11, y, t, fontsize=10.3, color=INK2, transform=ax.transAxes)
ax.text(0.0, -0.04, "● blue = live/supportive   ● orange = live caution   ● gray = not triggered", fontsize=9.2, color=INK2, transform=ax.transAxes)
fig.savefig(HERE / "out" / "ladder_1102.png", dpi=110, facecolor=BG); print("ok")
