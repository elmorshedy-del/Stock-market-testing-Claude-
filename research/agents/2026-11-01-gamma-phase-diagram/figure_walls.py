"""Figure for iteration 3/3b: the prior-day call wall as a soft ceiling. Reads out/walls_b.json, out/walls_b_events_*.csv,
out/walls_exit.json, out/walls_exit_sigma.json -> out/walls_fig.png"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; O = HERE / "out"
WALL, ORD = "#2a78d6", "#eb6834"; INK, INK2, GRID, BG = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10.5, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False})
b = json.load(open(O / "walls_b.json")); ex = json.load(open(O / "walls_exit.json")); es = json.load(open(O / "walls_exit_sigma.json"))
fig = plt.figure(figsize=(15, 10.4), facecolor=BG)
gs = fig.add_gridspec(2, 3, height_ratios=[1, 1.05], hspace=0.42, wspace=0.28, left=0.05, right=0.985, top=0.86, bottom=0.06)
fig.text(0.05, 0.955, "The prior day's call wall is a soft ceiling for the day's high (SPY, replicated in QQQ)", fontsize=17, weight="bold", color=INK)
fig.text(0.05, 0.918, "Once the high reaches the wall it stops there ~1.4x as often as at an ordinary $5 strike the same distance away, and big runs past it are rarer.\n"
         "2020-2026 one-minute bars; walls = largest call/put OI strike (<=45 days) from the prior session, known before the open. The put wall did not behave like a floor.",
         fontsize=10.5, color=INK2, va="top")

# A: stall rates
ax = fig.add_subplot(gs[0, 0]); ax.set_facecolor(BG)
rows = [("SPY", b["SPY"]["iter3 design: call wall stall"]), ("QQQ", b["QQQ"]["iter3 design: call wall stall"])]
x = np.arange(2); w = 0.36
for i, (u, r) in enumerate(rows):
    ax.bar(i - w / 2 - 0.01, 100 * r["treated mean"], w, color=WALL, zorder=3)
    ax.bar(i + w / 2 + 0.01, 100 * r["control mean (raw)"], w, color=ORD, zorder=3)
    ax.text(i - w / 2 - 0.01, 100 * r["treated mean"] + 1, f"{100 * r['treated mean']:.0f}%", ha="center", color=INK, weight="bold")
    ax.text(i + w / 2 + 0.01, 100 * r["control mean (raw)"] + 1, f"{100 * r['control mean (raw)']:.0f}%", ha="center", color=INK2)
    lo, hi = r["90% CI"]
    ax.text(i, -9.5, f"matched gap +{100 * r['MH diff']:.0f} pts\n(90% CI +{100 * lo:.0f} to +{100 * hi:.0f}; n {r['n treated']})", ha="center", va="top", fontsize=9, color=INK2)
ax.set_xticks(x, ["SPY", "QQQ"], fontsize=12, color=INK); ax.set_ylim(0, 55); ax.set_ylabel("% of touches where that was the day's high (±0.1%)")
ax.yaxis.grid(True, color=GRID, zorder=0); ax.tick_params(axis="x", length=0, pad=4)
ax.set_title("A. The high stops at the wall more often", loc="left", fontsize=12.5, weight="bold", color=INK)
ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=WALL), plt.Rectangle((0, 0), 1, 1, color=ORD)], labels=["prior call wall", "ordinary $5 strike"],
          frameon=False, loc="upper right", fontsize=9.5)

# B: by sigma distance
ax = fig.add_subplot(gs[0, 1]); ax.set_facecolor(BG)
for u, ls, mk in (("SPY", "-", "o"), ("QQQ", "--", "s")):
    T = pd.read_csv(O / f"walls_b_events_{u}.csv"); T = T[(T.side == "up") & (T.ds < 1.5)]
    T["sb"] = (T.ds // 0.5) * 0.5
    g = T.groupby(["sb", "wall"]).stall.agg(["size", "mean"]).unstack()
    xs = g.index.to_numpy() + 0.25
    for wv, col in ((1, WALL), (0, ORD)):
        ax.plot(xs, 100 * g[("mean", wv)], ls=ls, marker=mk, ms=8, lw=2, color=col, mec=BG, mew=1.5, zorder=3)
    ax.text(xs[-1] + 0.06, 100 * g[("mean", 1)].iloc[-1], u, color=INK2, fontsize=9.5, va="center")
ax.set_xticks([0.25, 0.75, 1.25], ["0-0.5σ", "0.5-1σ", "1-1.5σ"]); ax.set_xlim(0.05, 1.55); ax.set_ylim(0, 75)
ax.set_xlabel("strike's distance above the open (σ = prior VIX/√252)"); ax.set_ylabel("% stopping at the strike")
ax.yaxis.grid(True, color=GRID, zorder=0)
ax.set_title("B. Higher at every distance", loc="left", fontsize=12.5, weight="bold", color=INK)
ax.text(1.5, 3, "solid = SPY, dashed = QQQ", fontsize=9.5, color=INK2, ha="right", va="bottom")

# C: exit translation, overshoot CDF in % (SPY)
ax = fig.add_subplot(gs[0, 2]); ax.set_facecolor(BG)
cd = ex["SPY"]["CDF of overshoot (% past K) for figure"]; wo = np.array(ex["SPY"]["ordinary weights for figure"])
xw = np.array(cd["wall"]); xo = np.array(cd["ordinary"])
ax.step(np.r_[0, xw], 100 * np.r_[0, np.arange(1, len(xw) + 1) / len(xw)], where="post", color=WALL, lw=2.2)
ax.step(np.r_[0, xo], 100 * np.r_[0, np.cumsum(wo) / wo.sum()], where="post", color=ORD, lw=2.2)
ax.set_xlim(0, 1.5); ax.set_ylim(0, 100); ax.yaxis.grid(True, color=GRID); ax.xaxis.grid(True, color=GRID)
ax.set_xlabel("how far the high ran past the strike (% of price)"); ax.set_ylabel("% of touch days with the run at or below x")
s1, s2 = ex["SPY"]["call wall touches"], ex["SPY"]["ordinary $5 strikes (reweighted)"]
ax.text(0.55, 30, f"runs > 0.5% past:  wall {100 * s1['P(runs > 0.5% past K)']:.0f}%  vs  {100 * s2['P(runs > 0.5% past K)']:.0f}%\n"
        f"runs > 1% past:     wall {100 * s1['P(runs > 1% past K)']:.0f}%   vs  {100 * s2['P(runs > 1% past K)']:.0f}%\n"
        f"close back below:  wall {100 * s1['P(close below K)']:.0f}%  vs  {100 * s2['P(close below K)']:.0f}%", fontsize=9.3, color=INK, va="top",
        bbox=dict(boxstyle="round,pad=0.4", fc=BG, ec=GRID))
ax.text(0.03, 94, "prior call wall", color=WALL, fontsize=9.5, weight="bold"); ax.text(0.78, 60, "ordinary $5 strike", color=ORD, fontsize=9.5, weight="bold")
ax.set_title("C. Upside left after SPY tags the wall", loc="left", fontsize=12.5, weight="bold", color=INK)

# D: checks scorecard
ax = fig.add_subplot(gs[1, :2]); ax.axis("off")
S, Q = b["SPY"], b["QQQ"]
def pts(r): return f"{100 * r['MH diff']:+.0f} pts (CI {100 * r['90% CI'][0]:+.0f} to {100 * r['90% CI'][1]:+.0f})"
checks = [
    ("PASS", "Registered (iter. 3)", pts(S["iter3 design: call wall stall"]), "call wall vs matched ordinary strikes, SPY"),
    ("PASS", "A1 volatility", pts(S["A1 sigma bins x VIX tercile: call wall stall"]), "VIX tercile and σ-distance held fixed"),
    ("PASS", "A2 prior highs", pts(S["A2i call wall stall, walls near prior highs dropped"]), "walls near the prior 1-/5-day high removed (82 left)"),
    ("MIXED", "A2 stale walls", pts(S["A2ii stale call wall (t-10, not current) stall"]), "wall from 10 sessions ago: weaker (dose or memory?)"),
    ("PASS", "R  QQQ", pts(Q["iter3 design: call wall stall"]), "own chain and strikes, same design"),
    ("PASS", "M2 pinning time", pts(S["M2 pinning share after first touch: call wall"]), "time spent near the wall after the touch"),
    ("FAIL", "B  bunching", "excess −0.19 (p 0.68)", "raw density; underpowered (~40 touches in sample)"),
    ("FAIL", "Put wall = floor?", "QQQ " + pts(Q["iter3 design: put wall stall"]), "SPY lows ran through (2/29 stopped); QQQ did not"),
]
ax.set_title("D. Did it survive the artefact checks? (pre-registered before running)", loc="left", fontsize=12.5, weight="bold", color=INK)
mark = {"PASS": ("✓ pass", "#0ca30c"), "MIXED": ("~ mixed", "#b07900"), "FAIL": ("✗ fail", "#d03b3b")}
for i, (st, name, val, desc) in enumerate(checks):
    y = 0.92 - i * 0.118
    lab, col = mark[st]
    ax.text(0.0, y, lab, color=col, fontsize=10.5, weight="bold", va="center", transform=ax.transAxes)
    ax.text(0.08, y, name, color=INK, fontsize=10.5, weight="bold", va="center", transform=ax.transAxes)
    ax.text(0.28, y, val, color=INK, fontsize=9.8, va="center", transform=ax.transAxes)
    ax.text(0.53, y, desc, color=INK2, fontsize=9.6, va="center", transform=ax.transAxes)

# E: how to use it
ax = fig.add_subplot(gs[1, 2]); ax.axis("off")
ax.set_title("E. Using it for call exits (a tilt, not a wall)", loc="left", fontsize=12.5, weight="bold", color=INK)
txt = ("When: the prior day's call wall sits within ~1% above\nthe open, and the high tags it (±0.1%).\n\n"
       "Then (SPY 2020-26, 159 days):\n"
       f"• that's the day's high {100 * s1['P(high stops within +-0.1% of K)']:.0f}% of the time ({100 * s2['P(high stops within +-0.1% of K)']:.0f}% ordinary)\n"
       f"• 90% of days the run past it is ≤ {s1['overshoot % quantiles 50/75/90'][2]:.1f}% ({s2['overshoot % quantiles 50/75/90'][2]:.1f}%)\n"
       f"• holding VIX fixed: > 0.5σ past it {100 * es['SPY']['call wall']['P(> 0.5 sigma past)']:.0f}% vs {100 * es['SPY']['ordinary (A1-reweighted)']['P(> 0.5 sigma past)']:.0f}%\n\n"
       "Rule of thumb: trim calls into the first tag;\nkeep a runner only with a stop just under it.\n\n"
       "Caveats: smaller since 2022 after the VIX adjustment\n(SPY +8 pts, CI −1 to +16); 57% of the time it still\nbreaks. Today: SPY 755.72, call wall 800 (+5.9%),\nnot in play Monday; it is in play when the wall\nsits within ~1% of the open.")
ax.text(0.0, 0.97, txt, fontsize=9.9, color=INK, va="top", transform=ax.transAxes, linespacing=1.35)
fig.savefig(O / "walls_fig.png", dpi=110, facecolor=BG)
print("saved")
