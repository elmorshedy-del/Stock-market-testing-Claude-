"""out/dip_or_wait_card.png: one-page decision card for SPY calls on Fri Oct 30 (dip rule + entry signals). Text only, numbers from README."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

plt.rcParams["text.usetex"] = False; plt.rcParams["text.parse_math"] = False
OUT = Path(__file__).resolve().parent / "out"
GREEN, RED, INK, MUTED, SURF, BLUE, AMBER = "#1baf7a", "#d64545", "#0b0b0b", "#52514e", "#fcfcfb", "#2a78d6", "#e8a33d"
fig = plt.figure(figsize=(11, 15)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 100); ax.set_ylim(0, 150); ax.axis("off"); fig.patch.set_facecolor(SURF)


def box(y, h, color, title, lines, x=3, w=94):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.5", fc=color + "18", ec=color, lw=2))
    ax.text(x + 2, y + h - 2.2, title, fontsize=14, weight="bold", color=color, va="top")
    for i, s in enumerate(lines):
        ax.text(x + 2.5, y + h - 7 - i * 3.6, s, fontsize=11.2, color=INK, va="top")


ax.text(3, 147, "SPY calls for the November trend: buy Friday's dip, or wait?", fontsize=17, weight="bold", color=INK, va="top")
ax.text(3, 142.5, "Short answer: the dip looks like the BOUNCE kind, but don't buy the open. Enter on a signal.", fontsize=12.5, color=INK, va="top")
box(112, 27, BLUE, "1  The dip rule (is this dip a bounce or a correction?)", [
    "Check breadth when the dip STARTED (share of big stocks above their 50-day average).",
    "•  Narrow breadth at the start  →  dip gets bought: 13 of 15",
    "•  Broad breadth at the start   →  becomes a correction: 6 of 6",
    "This dip started Oct 16 at 39% (2nd narrowest of 22)  →  BOUNCE side ✓",
    "Rotation still on: 79% of stocks rose Thursday while the megacaps fell ✓",
    "Kill line: S&P closes at or below 7,428 before a new high above 7,819."])
box(70, 38, GREEN, "2  Green lights (any one = entry)", [
    "A. R2 fires at Friday's close  (best payoff since 2019)",
    "     SqueezeMetrics GEX ≤ $4.5bn  AND  DIX ≥ 45.4%   (now $5.6bn / 45.8%)",
    "     →  up-leg within 20 sessions 79% vs 58%; call spread +16% vs +12%",
    "     Odds it fires: ~46% if the S&P closes −1% or worse; ~24% if −0.5 to −1%",
    "B. SPY reclaims 772–774 (the flip) and holds  →  dealers start damping;",
    "     buy the first pullback that holds above it. Targets 780, then 800.",
    "C. Deeper flush: S&P close ≤ 7,602 (SPY ~758) + GEX ≤ $3.35bn  →  R5,",
    "     83% odds, but since 2019 the spread paid no more than an ordinary day.",
    "No rush: the R2 up-leg typically starts about 5 days after it fires."])
box(38, 28, RED, "3  Don't", [
    "✗  Naked calls at the open: SPY starts below its flip, dealers amplify the move,",
    "     and VIX rises on the dip, so you'd be paying for expensive volatility.",
    "✗  Chasing puts into the close: month-end moves are ~1/3 given back in 5 days.",
    "✗  Reading 765 / 760 / 750 breaks as the trend: they are hedging accelerants;",
    "     Friday is the day that pocket is deepest (27% of gamma expires)."])
box(4, 30, AMBER, "4  How to hold it", [
    "Structure: 60-day call spread, ATM / +5%  (e.g. ~760 / 800; 800 is the call wall).",
    "First profit zone if you bought below: 772–774 (the flip stalls price).",
    "Tailwinds (descriptive, not signals): midterm election week +1.5%, 74% up;",
    "     November +1.9%, 71% up; first half of the month stronger.",
    "Biggest risk: a rates shock (the only narrow-breadth corrections, both shallow).",
    "Exit / rethink if the S&P closes at or below 7,428."])
fig.savefig(OUT / "dip_or_wait_card.png", dpi=120, facecolor=SURF)
print("ok")
