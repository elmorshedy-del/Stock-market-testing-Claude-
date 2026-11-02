"""Draw the bull-case storyboard: SPY and TSLA paths with time, phases, strong strikes, events, and the options-implied 68% cone.
Usage: python figure_scenario.py <SPY yahoo json> <TSLA yahoo json> -> out/scenario_1102.png"""
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; R = json.load(open(HERE / "out" / "scenario.json"))
BLUE, ORG, BG, INK, INK2, GRID, GRAY = "#2a78d6", "#eb6834", "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#a9a8a3"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False})
def yc(p):
    r = json.load(open(p))["chart"]["result"][0]; s = pd.Series(r["indicators"]["quote"][0]["close"], index=pd.to_datetime(r["timestamp"], unit="s").normalize()); return s[~s.index.duplicated(keep="last")].dropna()
hist = {"SPY": yc(sys.argv[1]).loc["2026-10-16":"2026-10-30"], "TSLA": yc(sys.argv[2]).loc["2026-10-16":"2026-10-30"]}
sb = R["storyboard"]; fut = pd.to_datetime(list(sb)); allx = list(hist["SPY"].index) + list(fut); pos = {d: i for i, d in enumerate(allx)}
fig, axs = plt.subplots(2, 1, figsize=(18, 12.5), sharex=True, facecolor=BG, gridspec_kw=dict(hspace=0.16))
fig.subplots_adjust(left=0.06, right=0.88, top=0.87, bottom=0.1)
fig.text(0.02, 0.955, "One clean bull case: SPY's leg starts as TSLA pauses; both top out together at the Nov 20 monthly expiry", fontsize=19, weight="bold", color=INK)
fig.text(0.02, 0.905, "A storyboard built from our maps and tested rules, NOT a forecast. Solid = actual closes; dashed = the scenario; shaded = options-implied 68% range.\n"
         f"Options-implied odds of the key waypoints: SPY ≥ 780 by Nov 20 {int(100*R['options-implied odds of the waypoints (no drift)']['SPY trades >= 780 by Fri Nov 20'])}%, TSLA ≥ 450 by Nov 20 {int(100*R['options-implied odds of the waypoints (no drift)']['TSLA trades >= 450 by Fri Nov 20'])}%, both {int(100*R['options-implied odds of the waypoints (no drift)']['both: SPY >= 780 and TSLA >= 450 by Nov 20'])}%.", fontsize=11.2, color=INK2)
cfg = {"SPY": dict(sig=0.010, lv=[(800, "800 call wall (ceiling)", GRAY), (780, "780: pin zone / temp top", BLUE), (766.43, "766.4 flip", BLUE), (750, "750 put wall", ORG), (740.6, "740.6 kill line", ORG)],
               yl=(730, 805), ph=[("2026-11-02", "2026-11-06", "1. SHAKEOUT\nvote, AAPL, results:\ntag 750, hold", ORG), ("2026-11-09", "2026-11-13", "2. LEG STARTS\nreclaim 766, gamma\nrebuilds WITH price", BLUE),
                                  ("2026-11-16", "2026-11-20", "3. PIN / TEMP TOP\ngamma maxed into\nopex, 778–781", GRAY), ("2026-11-23", "2026-11-27", "4. RESET\nopex roll-off,\ndip to ~770", ORG)]),
       "TSLA": dict(sig=0.026, lv=[(455, "450–455 damping peak", GRAY), (440, "440 (big call adds)", GRAY), (420, "420 wall", BLUE), (410, "410 (today's 0DTE calls)", GRAY), (400, "400 floor", BLUE), (380, "380 put wall / flip zone", ORG)],
                    yl=(350, 462), ph=[("2026-11-02", "2026-11-06", "1. POP & FADE\n413–416 by Wed,\nfade into Nov 6 pin", GRAY), ("2026-11-09", "2026-11-13", "2. FREED AGAIN\nMon after the weekly:\nthrough 420 → 431", BLUE),
                                       ("2026-11-16", "2026-11-20", "3. RUN & TEMP TOP\n440 → 450 at the\ndamping peak, opex", BLUE), ("2026-11-23", "2026-11-27", "4. RESET\nmonthly roll-off,\nflush to ~420", ORG)])}
ev = [("2026-11-03", "vote"), ("2026-11-04", "results"), ("2026-11-06", "jobs"), ("2026-11-18", "NVDA ~"), ("2026-11-20", "monthly opex"), ("2026-11-26", "")]
for ax, sym in zip(axs, ("SPY", "TSLA")):
    c = cfg[sym]; ax.set_facecolor(BG); h = hist[sym]; start = R["start"][sym]
    for a, b, lab, col in c["ph"]:
        ax.axvspan(pos[pd.Timestamp(a)] - 0.45, pos[pd.Timestamp(b)] + 0.45, color=col, alpha=0.08, lw=0)
        ax.text((pos[pd.Timestamp(a)] + pos[pd.Timestamp(b)]) / 2, c["yl"][1] - 0.5, lab, ha="center", va="top", fontsize=10.2, weight="bold", color=col if col != GRAY else INK2)
    xs = np.arange(len(h), len(allx)); k = np.arange(1, len(fut) + 1)
    ax.fill_between(xs, start * np.exp(-c["sig"] * np.sqrt(k)), start * np.exp(c["sig"] * np.sqrt(k)), color=BLUE, alpha=0.07, lw=0)
    ax.plot([pos[d] for d in h.index], h.values, color=INK, lw=2.6, marker="o", ms=4)
    yv = [sb[str(d.date())][sym] for d in fut]; ax.plot([len(h) - 1] + list(xs), [h.iloc[-1]] + yv, color=BLUE, lw=2.6, ls="--", marker="o", ms=4)
    for y, lab, col in c["lv"]:
        ax.axhline(y, color=col, lw=1, ls=":" if col == GRAY else "-", alpha=0.85); ax.text(len(allx) - 0.4, y, " " + lab, va="center", fontsize=9.6, color=col if col != GRAY else INK2)
    ax.set_ylim(*c["yl"]); ax.yaxis.grid(True, color=GRID); ax.set_ylabel(sym, fontsize=14, weight="bold", color=INK); ax.set_xlim(-0.5, len(allx) - 0.5)
    pk = max(yv) if sym == "TSLA" else max(yv); pd_ = fut[int(np.argmax(yv))]
    ax.annotate(f"temp top {pk:g}", (pos[pd_], pk), (pos[pd_] - 3.2, pk + 6) if sym == "SPY" else (pos[pd_] + 0.8, pk - 16), fontsize=11, weight="bold", color=INK, arrowprops=dict(arrowstyle="-", color=GRAY))
    ax.axvline(len(h) - 0.5, color=GRAY, lw=1); ax.text(len(h) - 0.4, c["yl"][0] + 1, "today", fontsize=9.5, color=INK2)
axs[0].annotate("shakeout low 751", (pos[pd.Timestamp("2026-11-04")], 751), (pos[pd.Timestamp("2026-11-04")] - 4, 741), fontsize=10.5, color=ORG, arrowprops=dict(arrowstyle="-", color=GRAY))
axs[1].text(0.3, 455, "Oct: reset → block 1 → dip → block 2 → pinned stall", fontsize=10, color=INK2)
axs[0].text(0.3, 798, "Oct: three failed rebuilds (no pin since Oct 9)", fontsize=10, color=INK2)
ticks = list(range(len(allx))); axs[1].set_xticks(ticks)
lab = [d.strftime("%b %d") + ("\n" + dict(ev).get(str(d.date()), "") if str(d.date()) in dict(ev) else "") for d in allx]
axs[1].set_xticklabels(lab, rotation=60, fontsize=9)
fig.savefig(HERE / "out" / "scenario_1102.png", dpi=110, facecolor=BG); print("ok")
