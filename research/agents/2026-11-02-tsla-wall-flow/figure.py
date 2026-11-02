"""TSLA walls + burst-flow card -> out/tsla_wall_flow.png"""
import json
import sys
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

H = Path(__file__).resolve().parent; O = H / "out"
BG, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"; BLUE, ORG, GRN = "#2a78d6", "#eb6834", "#0ca30c"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10.3, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": GRID,
                     "xtick.color": INK2, "ytick.color": INK2})
W = json.load(open(O / "walls.json")); F = json.load(open(O / "flow.json"))
gk = pd.read_csv(O / "gamma_by_strike.csv", index_col=0).iloc[:, 0]; gk = gk[(gk.index >= 370) & (gk.index <= 465)]
fig = plt.figure(figsize=(15.5, 9.8), facecolor=BG)
gs = fig.add_gridspec(2, 3, height_ratios=[1, 1], hspace=0.45, wspace=0.28, left=0.05, right=0.985, top=0.86, bottom=0.07)
fig.text(0.05, 0.955, "TSLA: next wall 420, then 440-455. Buying was aggressive, but history favours a stair-step, not a snap", fontsize=16, weight="bold", color=INK)
fig.text(0.05, 0.918, "Positions from open interest at the Oct 29 close (Friday's trades arrive in Monday's file); spot 399.81.\n"
         "Flow = bulk volume classification on 1-minute bars (a proxy for aggressor side), 70 earlier 2-day bursts of +7% or more since 2020.",
         fontsize=10, color=INK2, va="top")
ax = fig.add_subplot(gs[0, :2]); ax.set_facecolor(BG)
ax.bar(gk.index, gk.to_numpy(), width=1.8, color=np.where(gk.to_numpy() >= 0, BLUE, ORG))
ax.axvline(399.81, color=INK, lw=1.2); ax.text(400.5, gk.max() * 0.98, "spot 399.81", fontsize=9, color=INK)
for k in (420, 440, 450, 455):
    if k in gk.index: ax.text(k, gk.loc[k] + 0.002, f"{k}", ha="center", fontsize=9.5, weight="bold", color=INK)
ax.text(424, -0.0105, "your 430 sits between the 420 wall\nand the 440-455 cluster (430 itself is minor)", fontsize=9, color=INK2)
ax.set_ylabel("dealer gamma, $bn per 1% move"); ax.yaxis.grid(True, color=GRID); ax.set_xlim(370, 466)
ax.set_title("A. Gamma by strike (blue = dealers long: they sell rallies into it)", loc="left", fontsize=12, weight="bold", color=INK)
ax = fig.add_subplot(gs[0, 2]); ax.set_facecolor(BG)
b = pd.Series(W["call OI built Oct 23 close -> Oct 29 close (top 8)"]).astype(float); b.index = b.index.astype(float); b = b.sort_index()
ax.barh([f"{k:g}" for k in b.index], b.to_numpy() / 1000, color=BLUE); ax.invert_yaxis()
for i, v in enumerate(b.to_numpy() / 1000): ax.text(v + 0.3, i, f"+{v:.1f}k", va="center", fontsize=9, color=INK)
ax.set_xlabel("new call open interest during the burst (thousand contracts)"); ax.xaxis.grid(True, color=GRID); ax.set_xlim(0, 32)
ax.set_title("B. Where new calls were added (Oct 23 → 29)", loc="left", fontsize=12, weight="bold", color=INK)
ax = fig.add_subplot(gs[1, :2]); ax.set_facecolor(BG)
B = pd.read_csv(O / "bursts.csv", parse_dates=["date"]); P = B[B.date < "2026-10-27"].dropna(subset=["next 10d max %"])
sn = P["snap (+5% within 3 days)"].astype(bool)
ax.scatter(P.loc[~sn, "burst buy imbalance %"], P.loc[~sn, "next 10d max %"], s=40, color="#9a9994", label="no snap", edgecolor=BG)
ax.scatter(P.loc[sn, "burst buy imbalance %"], P.loc[sn, "next 10d max %"], s=55, color=GRN, label="snapped (+5% within 3 days)", edgecolor=BG)
cur = B[B.date == "2026-10-27"].iloc[0]
ax.axvline(cur["burst buy imbalance %"], color=ORG, lw=2); ax.text(cur["burst buy imbalance %"] + 0.3, P["next 10d max %"].max() * 0.9, "this burst\n(90th pct buying)", color=ORG, fontsize=9.5, weight="bold")
ax.set_xlabel("buying aggression during the burst (net buy share of volume, %)"); ax.set_ylabel("best gain in the next 10 sessions after the pause, %")
ax.yaxis.grid(True, color=GRID); ax.legend(frameon=False, fontsize=9, loc="upper left")
ax.set_title("C. Aggressive buying does not predict a faster follow-through (snaps are ~1 in 4 either way)", loc="left", fontsize=12, weight="bold", color=INK)
ax = fig.add_subplot(gs[1, 2]); ax.axis("off")
c = F["this burst (Oct 26-27) vs earlier: value, percentile among earlier"]
txt = ("This burst vs 70 earlier ones:\n"
       f"• buying aggression {c['burst buy imbalance %'][0]:.0f}%  ({100 * c['burst buy imbalance %'][1]:.0f}th pct)\n"
       f"• volume {c['burst rel. volume'][0]:.2f}x normal  ({100 * c['burst rel. volume'][1]:.0f}th pct)\n"
       f"• pause Oct 28-30: {c['consolidation 3d %'][0]:+.1f}%, net buying on light\n  volume (dips bought, not distribution)\n\n"
       "What followed similar setups:\n"
       "• snap (+5% ≈ 420 in 3 days): 24% overall;\n  0 of the 4 closest look-alikes\n"
       "• all 4 look-alikes cleared the burst high\n  +2% (≈ 416) within 10 sessions,\n  taking 4-9 sessions\n\n"
       "Gamma: dealer long gamma doubles from 400\nto 430 and peaks near 455, so rallies get\nsold into on the way up: stair-steps with\nstalls at 420, then 440-450.\n\n"
       "Caveat: if the new 420/440 calls were bought\nby customers, dealers are short them and the\napproach could squeeze faster.")
ax.text(0.0, 0.98, txt, fontsize=9.8, color=INK, va="top", transform=ax.transAxes, linespacing=1.32)
fig.savefig(O / "tsla_wall_flow.png", dpi=108, facecolor=BG); print("ok")
