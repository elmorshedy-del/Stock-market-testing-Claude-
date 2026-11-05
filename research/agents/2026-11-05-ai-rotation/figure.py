"""Rotation analog figure -> out/ai_rotation.png"""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent; O = HERE / "out"; R = pd.read_csv(O / "ratio.csv", index_col=0, parse_dates=True).ratio; J = json.load(open(O / "rotation.json"))
BG, INK, INK2, GRID, GRAY, BLUE, ORANGE, RED, GREEN = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#a9a8a3", "#2a78d6", "#eb6834", "#c8372d", "#2f8f5b"
plt.rcParams.update({"font.size": 10.5, "axes.titleweight": "bold", "axes.edgecolor": GRAY, "xtick.color": INK2, "ytick.color": INK2})
fig, ax = plt.subplots(figsize=(13, 6.2), facecolor=BG); ax.set_facecolor(BG); ax.grid(True, color=GRID); ax.spines[["top", "right"]].set_visible(False)
eps = [e for e in J["past episodes (ratio -15% or more), all"] if e["peak"] >= "2020"]
cols = {"2021-02-16": GRAY, "2021-12-01": BLUE, "2024-07-10": ORANGE, "2026-06-22": RED}
for e in eps:
    s = R.loc[e["peak"]:]; s = s.iloc[:max(e["sessions peak->trough"] + 60, 120)] if e["recovered"] else s
    y = 100 * (s / s.iloc[0] - 1); x = range(len(y)); now = not e["recovered"]
    lab = (f"NOW: peak {e['peak'][:7]}, {e['depth %']:.0f}% so far in {e['sessions peak->trough']} sessions" if now else f"{e['peak'][:7]} → trough {e['trough'][:7]}: {e['depth %']:.0f}% in {e['sessions peak->trough']} sessions")
    ax.plot(x, y.values, color=cols.get(e["peak"], GRAY), lw=3 if now else 1.8, label=lab, zorder=5 if now else 3)
    if e["recovered"]: ax.scatter([e["sessions peak->trough"]], [e["depth %"]], color=cols.get(e["peak"], GRAY), s=40, zorder=4)
ax.scatter([eps[-1]["sessions peak->trough"]], [eps[-1]["depth %"]], color=RED, s=110, zorder=6, edgecolor=INK)
ax.axhspan(-34, -32, color=RED, alpha=0.07); ax.text(250, -31.5, "where the 2022 and 2024-25 rotations bottomed (−32% to −34%)", fontsize=9.5, color=RED)
ax.axhline(0, color=INK2, lw=0.8); ax.set_xlim(0, 300); ax.set_ylim(-40, 8)
ax.set_xlabel("sessions since the chip-vs-average-stock peak"); ax.set_ylabel("chips (SMH) ÷ average stock (RSP), % from peak")
ax.legend(frameon=False, loc="lower right", fontsize=9.5)
a5 = J["after top-1% one-day rotation drops (ratio), excl today"]
ax.set_title(f"Chips vs the average stock: this rotation is already as deep as the two biggest since 2020, and got there 2× faster\n"
             f"Today's {J['today\'s one-day ratio move %']:.1f}% day is a top-1% rotation day; after those, chips bounced vs the average stock {100 * a5['next 5 sessions ratio median % / share up'][1]:.0f}% of the time within 5 sessions", loc="left", fontsize=11.5)
fig.text(0.01, 0.01, f"Yahoo daily + live ({J['as of']}). Episodes = ratio down ≥15% from its high. 2004-13 episode (−56%, 9 years, before SMH's 2011 rebuild) omitted from the chart. Descriptive: 4 modern episodes.", fontsize=8.5, color=INK2)
plt.tight_layout(rect=(0, 0.03, 1, 1)); plt.savefig(O / "ai_rotation.png", dpi=150, facecolor=BG); print("ok")
