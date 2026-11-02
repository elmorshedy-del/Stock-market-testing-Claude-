"""ADHD one-glance version of TSLA's October cycle: 6 boxes (5 phases + now), each with price, a gamma bar and a DIX bar, plus what's next."""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = Path(__file__).resolve().parent
BLUE, ORG, BG, INK, INK2, GRID, GRAY, LG = "#2a78d6", "#eb6834", "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#a9a8a3", "#efeeea"
plt.rcParams.update({"font.family": "DejaVu Sans"})
fig = plt.figure(figsize=(17, 9.6), facecolor=BG); ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off"); ax.set_xlim(0, 100); ax.set_ylim(0, 100)
ax.text(2.5, 94, "TSLA's October run, in 6 boxes", fontsize=26, weight="bold", color=INK)
ax.text(2.5, 89.3, "Bars: gamma = dealer cushion (full = pinned) • DIX = dark-pool buying • crowding = contracts near the price (short = freed). Corrected 09:40 ET.", fontsize=12.5, color=INK2)
B = [("1. RESET", "Oct 14–16", "355", "on the flip", 0.17, 0.02, 0.03, "cushion gone,\nsellers done", ORG),
     ("2. BLOCK 1", "Oct 19–21", "387", "+9%", 0.75, 0.53, 0.25, "gamma rebuilds\nwith price", BLUE),
     ("3. DIP", "Oct 22–23", "372", "near the flip", 0.31, 0.73, 0.04, "flush again,\nbuyers step in", ORG),
     ("4. BLOCK 2", "Oct 26–27", "408", "+9.5%", 0.93, 0.75, 0.18, "bigger leg,\ngamma maxed", BLUE),
     ("5. STALL", "Oct 28–30", "400", "pinned", 0.90, 0.71, 0.29, "gamma maxed,\nfreed closing", GRAY),
     ("NOW", "Mon Nov 2", "402", "6% above flip", 0.65, 0.65, 0.23, "pause,\nnot a top", INK)]
w, gap, x0 = 14.6, 1.6, 2.5
for i, (t, d, px, sub, gm, dx, fr, meaning, col) in enumerate(B):
    x = x0 + i * (w + gap)
    ax.add_patch(FancyBboxPatch((x, 30), w, 54, boxstyle="round,pad=0.3,rounding_size=1.5", fc="white" if t != "NOW" else "#f4f3ef", ec=col, lw=2.6))
    ax.text(x + w / 2, 79.5, t, ha="center", fontsize=16, weight="bold", color=col)
    ax.text(x + w / 2, 75.6, d, ha="center", fontsize=11, color=INK2)
    ax.text(x + w / 2, 66.5, px, ha="center", fontsize=30, weight="bold", color=INK)
    ax.text(x + w / 2, 62.2, sub, ha="center", fontsize=11.5, color=INK2)
    for j, (lab, v, c) in enumerate([("gamma", gm, BLUE), ("DIX", dx, INK), ("crowding (low = freed)", fr, ORG)]):
        y = 54 - j * 6.2
        ax.text(x + 0.8, y + 2.6, lab, fontsize=10.5, color=INK2)
        ax.add_patch(FancyBboxPatch((x + 0.8, y), w - 1.6, 2, boxstyle="round,pad=0,rounding_size=0.8", fc=LG, ec="none"))
        ax.add_patch(FancyBboxPatch((x + 0.8, y), max((w - 1.6) * v, 1.0), 2, boxstyle="round,pad=0,rounding_size=0.8", fc=c, ec="none"))
    ax.text(x + w / 2, 35.3, meaning, ha="center", va="center", fontsize=12, color=INK, weight="bold")
    if i < len(B) - 1: ax.annotate("", (x + w + gap - 0.1, 57), (x + w + 0.1, 57), arrowprops=dict(arrowstyle="-|>", color=GRAY, lw=2))
ax.text(2.5, 23.5, "It lined up: cushion reset at the flip → rebuilt with each leg → maxed at the top. Freed the whole run. Dark-pool buying rose from washed-out to strong.", fontsize=13.5, color=INK, weight="bold")
ax.add_patch(FancyBboxPatch((2.5, 2.5), 45.5, 16, boxstyle="round,pad=0.3,rounding_size=1.5", fc="#eaf2fb", ec=BLUE, lw=1.5))
ax.text(4, 15.3, "NEXT, path A: dip to ~377–381 (the flip)", fontsize=14, weight="bold", color=BLUE)
ax.text(4, 10.8, "flushes the cushion again = the start of the\nnext leg (strongest if 'freed' too). Likely around\nthe Nov 6 or Nov 20 expiries.", fontsize=11.8, color=INK, va="center")
ax.add_patch(FancyBboxPatch((51.5, 2.5), 46, 16, boxstyle="round,pad=0.3,rounding_size=1.5", fc="#f4f3ef", ec=GRAY, lw=1.5))
ax.text(53, 15.3, "NEXT, path B: sideways pause 395–420", fontsize=14, weight="bold", color=INK2)
ax.text(53, 10.8, "Watch DIX: staying in the top third (≥ 67th) = buyers\nstill there. Below the median (50th) = the dark-pool\nbid is done. Now 65th, fading.", fontsize=11.8, color=INK, va="center")
fig.savefig(HERE / "out" / "tsla_cycle_adhd.png", dpi=110, facecolor=BG); print("ok")
