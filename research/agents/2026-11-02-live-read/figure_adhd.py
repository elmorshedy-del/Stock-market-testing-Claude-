"""One-glance picture for the owner: where SPY and TSLA sit in the gamma cycle, the ladder checklist, TSLA's rebuild meters,
and the three things to watch. -> out/where_1102.png"""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = Path(__file__).resolve().parent
BLUE, ORG, BG, INK, INK2, GRID, GRAY, LG = "#2a78d6", "#eb6834", "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#a9a8a3", "#efeeea"
plt.rcParams.update({"font.family": "DejaVu Sans"})
fig = plt.figure(figsize=(16, 11), facecolor=BG); ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off"); ax.set_xlim(0, 100); ax.set_ylim(0, 100)
ax.text(3, 95.5, "Where we are in the gamma cycle (Mon Nov 2, pre-open)", fontsize=24, weight="bold", color=INK)
ax.text(3, 91.6, "Cycle: RESET (free) → REBUILD with a rally (the leg) → PIN (pause) → DROP → RESET", fontsize=14, color=INK2)


def track(y, name, here, label, col, ha="center"):
    st = [("RESET", 12, ORG), ("REBUILD\nwith rally", 37, BLUE), ("PIN", 62, BLUE), ("DROP", 82, GRAY)]
    ax.plot([8, 92], [y, y], color=GRID, lw=14, solid_capstyle="round", zorder=1)
    for t, x, c in st:
        ax.scatter(x, y, s=500, color=c, zorder=2, alpha=0.9); ax.text(x, y - 5.2, t, ha="center", va="top", fontsize=12.5, color=INK2, weight="bold")
    ax.annotate("", (here, y + 1.6), (here, y + 7.8), arrowprops=dict(arrowstyle="-|>", color=col, lw=3.5, mutation_scale=28), zorder=3)
    ax.text(here - (4 if ha == "left" else 0), y + 8.5, label, ha=ha, fontsize=14.5, weight="bold", color=col)
    ax.text(3, y, name, fontsize=20, weight="bold", color=INK, va="center")


track(75, "SPY", 12, "SPY IS HERE: fresh reset (GEX 6th pct)", ORG, ha="left")
track(42, "TSLA", 40, "TSLA IS HERE: rebuilding, about halfway", BLUE)

# SPY ladder chips
chips = [("R1", True, ""), ("R3", True, ""), ("R4", True, "fired Fri"), ("R2", False, "DIX > 45.4%"), ("R5", False, "weak day + DIX"), ("R6", False, "VIX ≤ 16.5"), ("R7", False, "VIX ≤ 14.6")]
x0 = 8
for r, on, note in chips:
    ax.add_patch(FancyBboxPatch((x0, 57.5), 8.6, 5.2, boxstyle="round,pad=0.3,rounding_size=0.8", fc=BLUE if on else LG, ec=BLUE if on else GRAY, lw=1.5))
    ax.text(x0 + 4.3, 60.9, ("✓ " if on else "") + r, ha="center", fontsize=15, weight="bold", color="white" if on else INK2)
    ax.text(x0 + 4.3, 58.6, note, ha="center", fontsize=9.6, color="white" if on else INK2)
    x0 += 12
ax.text(8, 54.8, "R2 is NOT on yet: S&P DIX was 43.8% Friday (needs > 45.4%; it was 45.8% Thursday). It's one number away.", fontsize=12.5, color=ORG, weight="bold")


def meter(y, x, w, val, lo, hi, line, title, sub, col):
    ax.text(x, y + 4.4, title, fontsize=13.5, weight="bold", color=INK)
    ax.add_patch(FancyBboxPatch((x, y), w, 2.6, boxstyle="round,pad=0,rounding_size=1.2", fc=LG, ec=GRID))
    ax.add_patch(FancyBboxPatch((x, y), w * (val - lo) / (hi - lo), 2.6, boxstyle="round,pad=0,rounding_size=1.2", fc=col, ec=col))
    lx = x + w * (line - lo) / (hi - lo); ax.plot([lx, lx], [y - 0.8, y + 3.4], color=INK, lw=2)
    ax.text(x + w * (val - lo) / (hi - lo) + 0.8, y + 1.3, f"{val:g}", ha="left", va="center", fontsize=13, weight="bold", color=col)
    ax.text(x, y - 5.2, sub, fontsize=11, color=INK2)


meter(26, 8, 26, 23, 0, 50, 33, "Freed window (near-price OI pct)", "0.6 → 4 → 23. Shuts at 33 (line):\nlikely by Wed–Thu", ORG)
meter(26, 39, 26, 65, 0, 100, 90, "Own gamma (pct) → pin at 90", "Gamma nearly doubles 402 → 420:\n420 is the pin / stall zone", BLUE)
meter(26, 70, 26, 65, 0, 100, 10, "TSLA's own DIX (dark-pool, 5-day pct)", "0.512 = 65th pct; warning line at 10th: off.\nMildly supportive (lean)", BLUE)
ax.text(8, 16.0, "Freed again soon? Yes, usually: the next freed spell starts a median 3 sessions after one ends (73% within 5).", fontsize=12.2, color=INK, weight="bold")
ax.text(8, 13.3, "Roll-offs that free it (if nobody adds): Fri Nov 6 weekly (30% of near OI) → ~4th pct on Mon Nov 9  •  Fri Nov 20 monthly (28%) → ~0 pct", fontsize=11.2, color=INK2)

ax.add_patch(FancyBboxPatch((3, 0.6), 94, 10.4, boxstyle="round,pad=0.4,rounding_size=1.5", fc="#f4f3ef", ec=GRID))
ax.text(5, 8.9, "Watch 3 things", fontsize=14, weight="bold", color=INK)
ax.text(5, 6.6, "1. Tonight's GEX ≥ $6.1bn with no rally = October's failed rebuild again (leg odds 75% → 61%)", fontsize=11.8, color=INK)
ax.text(5, 4.3, "2. S&P DIX > 45.4% = R2 on (and R5 if the S&P is still weak) → higher-odds call-spread entry", fontsize=11.8, color=INK)
ax.text(5, 2.0, "3. SPY close > 766.4 = rebuild WITH price (healthy leg, grind to 780)   •   TSLA at 420 = pin zone, expect a stall", fontsize=11.8, color=INK)
fig.savefig(HERE / "out" / "where_1102.png", dpi=110, facecolor=BG); print("ok")
