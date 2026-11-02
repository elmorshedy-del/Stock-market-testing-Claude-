"""Gamma cycle figure: S&P GEX percentile 2026 (reset <= 0.30, pinned >= 0.90, this week's 'ran' line 0.56) with the S&P, and TSLA's own
rebuild (freed pct, own-gamma pct by OI file). -> out/cycle_1102.png"""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent; x = pd.read_csv(HERE / "out" / "gex_cycle_2026.csv", parse_dates=["date"]).set_index("date").loc["2026-06-01":]
C = json.load(open(HERE / "out" / "cycle_now.json"))["history"]
BLUE, ORG, BG, INK, INK2, GRID, GRAY = "#2a78d6", "#eb6834", "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#a9a8a3"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False})
fig = plt.figure(figsize=(18, 10.5), facecolor=BG)
gs = fig.add_gridspec(2, 2, width_ratios=[1.7, 1], height_ratios=[1, 1], hspace=0.35, wspace=0.22, left=0.05, right=0.95, top=0.86, bottom=0.07)
fig.text(0.02, 0.95, "The gamma cycle: a reset starts a leg only if price rallies while gamma rebuilds. October rebuilt without price, three times", fontsize=18, weight="bold", color=INK)
fig.text(0.02, 0.905, "S&P dealer gamma (SqueezeMetrics GEX) ranked vs its past year. Reset ≤ 30th pct; pinned ≥ 90th. 'Rebuilt without price' = GEX up ≥ 50 pct-points from its 7-day low while the S&P\n"
         "moves −1% to +2.5% over 7 sessions (REPORT §4p). TSLA: freed = little open interest near the price (bottom third of its year); own gamma = TSLA dealer gamma pct.", fontsize=10.8, color=INK2)
ax = fig.add_subplot(gs[0, :]); ax.set_facecolor(BG)
ax.axhspan(0, 0.30, color=ORG, alpha=0.10, lw=0); ax.axhspan(0.90, 1.0, color=BLUE, alpha=0.10, lw=0)
ax.plot(x.index, x.pct, color=INK, lw=1.6); ax.set_ylim(0, 1.0); ax.set_ylabel("GEX percentile"); ax.yaxis.grid(True, color=GRID)
ax.axhline(0.56, color=ORG, lw=1.2, ls="--"); ax.text(x.index[2], 0.585, "this week's warning line: back to ≥ 56th pct (≈ $6.1bn) without a rally = 'rebuilt without price'", fontsize=9.5, color=ORG, bbox=dict(fc=BG, ec="none", alpha=0.9))
ax.text(x.index[2], 0.04, "reset (free): legs start here", fontsize=9.5, color=ORG); ax.text(x.index[2], 0.93, "pinned: legs pause here", fontsize=9.5, color=BLUE)
a2 = ax.twinx(); a2.plot(x.index, x.spx, color=BLUE, lw=1.4, alpha=0.8); a2.set_ylabel("S&P 500", color=BLUE); a2.tick_params(axis="y", colors=BLUE); a2.spines["top"].set_visible(False)
for d, t, y in [("2026-07-30", "reset 7,438 →\nAug 5 pin 7,724", 0.75), ("2026-09-28", "reset 7,684 →\nOct 6 pin 7,819", 0.75), ("2026-10-22", "Oct 16, 22, 30:\nthree resets, no pin\n(rebuilt to 0.45-0.53, dropped)", 0.62)]:
    ax.annotate(t, (pd.Timestamp(d), x.pct.asof(pd.Timestamp(d))), (pd.Timestamp(d) - pd.Timedelta(days=13), y), fontsize=9.2, color=INK, arrowprops=dict(arrowstyle="-", color=GRAY), bbox=dict(fc=BG, ec="none", alpha=0.9))
ax.set_title("A. S&P gamma cycle, Jun–Oct 2026 (black = GEX pct, blue = S&P)", loc="left", fontsize=13.5, weight="bold", color=INK)

ax = fig.add_subplot(gs[1, 0]); ax.set_facecolor(BG)
lab = ["Oct 28 OI\n(after Oct 30 expiry)", "Oct 30 OI\n(Thu positions)", "Nov 2 OI\n(Fri positions)"]
fr, og = [0.6, 4, 23], [None, 60, 65]
ax.plot(range(3), fr, "o-", color=ORG, lw=2, ms=8, label="freed: near-price OI pct (lower = freer)")
ax.plot([1, 2], og[1:], "s-", color=BLUE, lw=2, ms=8, label="TSLA own-gamma pct")
ax.axhline(33, color=ORG, ls="--", lw=1); ax.text(2.05, 34.5, "freed ends ≥ 33rd", fontsize=9.3, color=ORG)
for i, v in enumerate(fr): ax.text(i, v + 3, f"{v:g}", ha="center", fontsize=10, color=ORG)
for i, v in [(1, 60), (2, 65)]: ax.text(i, v + 3, f"{v}", ha="center", fontsize=10, color=BLUE)
ax.set_xticks(range(3)); ax.set_xticklabels(lab, fontsize=9.6); ax.set_ylim(0, 80); ax.set_xlim(-0.3, 2.8); ax.yaxis.grid(True, color=GRID); ax.set_ylabel("percentile vs past year")
ax.legend(fontsize=9.3, frameon=False, loc="upper left")
ax.set_title("B. TSLA is rebuilding: +96k calls, +57k puts on Friday", loc="left", fontsize=13.5, weight="bold", color=INK)

ax = fig.add_subplot(gs[1, 1]); ax.axis("off"); ax.set_title("C. What the cycle says for the trend", loc="left", fontsize=13.5, weight="bold", color=INK)
h1, h2 = C["2012-26"], C["2019Q4-26"]
L = [("S&P (tested, REPORT §4p)", True), ("• Legs need a reset first: 88% / 90% had one. We have it (6th pct).", False),
     ("• Rebuild WITH a rally = the leg, ending pinned (a pause).", False), (f"• Rebuild WITHOUT a rally: leg odds {int(100*h1[chr(39)+'ran'+chr(39)+' first days: n, P(leg within 20)'][1])}% vs 50%", False),
     (f"• After R4: odds {int(100*h1['R4 without '+chr(39)+'ran'+chr(39)+': n, P(leg within 20 of R4)'][1])}% if no such rebuild,", False),
     (f"   {int(100*h1['R4 then '+chr(39)+'ran'+chr(39)+' within 7 sessions: n, P(leg within 20 of R4)'][1])}% if it comes within 7 sessions (34% of cases)", False),
     ("• GEX builds into opex (Nov 20), drops ~17 pts that day.", False),
     ("TSLA", True), ("• Deep-freed states rebuild past 33rd in a median 4 sessions:", False),
     ("   the up-burst window (1.8×) likely closes by ~Wed–Thu.", False), ("• Freed + above flip: 27% up / 19% down bursts (3 sessions)", False),
     ("   vs not freed: 17% / 17% (post hoc).", False)]
y = 0.97
for t, b in L: ax.text(0, y, t, fontsize=10.3 if not b else 11, weight="bold" if b else "normal", color=INK if b else INK2, transform=ax.transAxes, va="top"); y -= 0.083
fig.savefig(HERE / "out" / "cycle_1102.png", dpi=110, facecolor=BG); print("ok")
