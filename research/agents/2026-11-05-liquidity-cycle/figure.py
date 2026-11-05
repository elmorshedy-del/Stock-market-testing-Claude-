"""Liquidity-cycle figure -> out/liquidity_cycle.png"""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

HERE = Path(__file__).resolve().parent; O = HERE / "out"
q1, q2, ud = json.load(open(O / "q1.json")), json.load(open(O / "q2.json")), json.load(open(O / "q2_exploratory_updown.json"))
BG, INK, INK2, GRID, GRAY, BLUE, ORANGE, RED, GREEN = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#a9a8a3", "#2a78d6", "#eb6834", "#c8372d", "#2f8f5b"
plt.rcParams.update({"font.size": 10, "axes.titleweight": "bold", "axes.titlesize": 11, "axes.edgecolor": GRAY, "xtick.color": INK2, "ytick.color": INK2})
fig, ax = plt.subplots(1, 3, figsize=(17.5, 6.2), facecolor=BG, gridspec_kw={"width_ratios": [0.9, 1.25, 1]})
for a in ax: a.set_facecolor(BG)
# (a) Q1
a = ax[0]; a.grid(True, axis="y", color=GRID); a.spines[["top", "right"]].set_visible(False)
ks = ["k=1", "k=5", "k=20"]; x = np.arange(3); w = 0.36
for j, (nm, col) in enumerate((("SPY", BLUE), ("TSLA", ORANGE))):
    g = [q1[nm][k]["gain"] for k in ks]; lo = [q1[nm][k]["gain 90% CI"][0] for k in ks]; hi = [q1[nm][k]["gain 90% CI"][1] for k in ks]
    a.bar(x + (j - 0.5) * w, g, w, color=col, label=nm); a.errorbar(x + (j - 0.5) * w, g, yerr=[np.array(g) - lo, np.array(hi) - g], fmt="none", ecolor=INK, capsize=3, lw=1)
a.axhline(0, color=INK, lw=1); a.set_xticks(x, ["next day", "next 5 days", "next 20 days"]); a.set_ylabel("out-of-sample R² gain from adding thinness")
a.set_ylim(-0.45, 0.12); a.legend(frameon=False, loc="lower left")
a.set_title("Q1: book thinness does NOT predict the size\nof the next moves beyond IV + recent range (2024-26)", loc="left")
# (b) cycle diagram
a = ax[1]; a.axis("off"); a.set_xlim(0, 10); a.set_ylim(0, 10)
tm = q2["D1 order"]["transition matrix (row = from)"]; dw = q2["D3 median episode length, sessions (IQR)"]
pos = {"CALM": (1.6, 7.6), "THINNING": (8.0, 7.6), "THIN": (8.0, 2.2), "RECOVERY": (1.6, 2.2)}
cols = {"CALM": GREEN, "THINNING": ORANGE, "THIN": RED, "RECOVERY": BLUE}
for p, (cx, cy) in pos.items():
    a.add_patch(FancyBboxPatch((cx - 1.35, cy - 0.75), 2.7, 1.5, boxstyle="round,pad=0.1", fc=cols[p], alpha=0.15, ec=cols[p], lw=2))
    a.text(cx, cy + 0.2, p, ha="center", fontsize=11, fontweight="bold", color=cols[p]); a.text(cx, cy - 0.35, f"{100 * q2['phase share of days'][p]:.0f}% of days · ~{dw[p][0]:.0f}d", ha="center", fontsize=8.5, color=INK2)
def arr(a_, b_, rad, lab, off):
    (x1, y1), (x2, y2) = pos[a_], pos[b_]
    a.add_patch(FancyArrowPatch((x1, y1), (x2, y2), connectionstyle=f"arc3,rad={rad}", arrowstyle="-|>", mutation_scale=16, lw=1.2 + 4 * tm[a_][b_], color=INK2, shrinkA=38, shrinkB=38))
    a.text((x1 + x2) / 2 + off[0], (y1 + y2) / 2 + off[1], f"{100 * tm[a_][b_]:.0f}%", fontsize=10, fontweight="bold", color=INK, ha="center")
arr("CALM", "THINNING", -0.15, "", (0, 1.0)); arr("THINNING", "THIN", -0.15, "", (1.0, 0)); arr("THIN", "RECOVERY", -0.15, "", (0, -1.0)); arr("RECOVERY", "CALM", -0.15, "", (-1.0, 0))
arr("THINNING", "CALM", -0.15, "", (0, -0.55)); arr("RECOVERY", "THIN", -0.15, "", (0, 0.55))
cy_ = q2["D3 full cycles CALM -> THINNING -> THIN -> RECOVERY -> CALM"]
a.text(4.8, 4.95, f"the order is followed more than chance:\n{100 * q2['D1 order']['share of transitions to the canonical next phase']:.0f}% vs {100 * q2['D1 order']['null mean / 95th pct'][0]:.0f}% random (p<0.001)\n— partly built into the rules —\nfull loop: {cy_['count']} times since 2012,\nmedian {cy_['median sessions']:.0f} sessions (~5-6 weeks)",
       ha="center", va="center", fontsize=9, color=INK2)
a.text(4.8, 9.6, "Q2: the S&P gamma / liquidity cycle (2012-2026)", ha="center", fontsize=11, fontweight="bold")
a.text(4.8, 0.35, f"NOW (Nov 4 close): RECOVERY  ·  S&P gamma pct {q2['today']['GEX pct']:.2f}, VIX {q2['today']['VIX']}", ha="center", fontsize=10, fontweight="bold", color=BLUE)
# (c) up/down legs by phase
a = ax[2]; a.grid(True, axis="y", color=GRID); a.spines[["top", "right"]].set_visible(False)
ph = ["CALM", "THINNING", "THIN", "RECOVERY", "ALL"]; x = np.arange(5)
a.bar(x - 0.19, [ud[p]["up-leg %"] for p in ph], 0.38, color=GREEN, label="up-leg (+3.5% in 10 days) starts within 20 sessions")
a.bar(x + 0.19, [ud[p]["down-leg %"] for p in ph], 0.38, color=RED, label="down-leg (−3.5%), exploratory")
for i, p in enumerate(ph): a.text(i, max(ud[p]["up-leg %"], ud[p]["down-leg %"]) + 2, f"tilt {ud[p]['up minus down']:+.0f}", ha="center", fontsize=9, fontweight="bold")
a.set_xticks(x, ph, fontsize=9); a.set_ylabel("% of days"); a.set_ylim(0, 85); a.legend(frameon=False, fontsize=8.5, loc="upper left")
a.set_title("What each phase predicts (next 20 sessions):\nTHIN = biggest moves, tilted up; CALM = small", loc="left")
fig.suptitle("Liquidity on larger frames: it doesn't forecast size beyond IV, but the gamma cycle is real and its THIN phase is where big (mostly up) moves start",
             x=0.01, ha="left", fontsize=12.5, fontweight="bold", color=INK)
fig.text(0.01, 0.01, "Phases from SqueezeMetrics S&P gamma percentile + VIX (pre-registered rules). Q1: SPY Arca / TSLA Nasdaq+EQUS 1-min bars 2020-26, fit 2020-23, test 2024-26. Down-leg odds were added after seeing results (exploratory).", fontsize=8, color=INK2)
plt.tight_layout(rect=(0, 0.03, 1, 0.93)); plt.savefig(O / "liquidity_cycle.png", dpi=150, facecolor=BG); print("ok")
