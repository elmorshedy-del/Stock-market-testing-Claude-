"""LQ figure: AI-crowded basket minus the equal-weight S&P (RSP), daily, Jun 1 -> Nov 2 2026, with the reported July unwind and
October's worst days marked; Friday's intraday path."""
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; Y = Path(sys.argv[1]); L = json.load(open(HERE / "out" / "liquidation.json")); I = json.load(open(HERE / "out" / "liquidation_intraday.json"))
B = ["NVDA", "AVGO", "AMD", "MU", "MRVL", "TSM", "SMCI", "ORCL", "CRWV", "NBIS", "VRT", "VST", "CEG", "LITE", "COHR", "ANET", "CLS", "WDC", "STX", "SNDK", "IREN", "CORZ", "PLTR", "ALAB", "CRDO"]
def c(t):
    r = json.load(open(Y / f"{t}.json"))["chart"]["result"][0]; v = r["indicators"]["adjclose"][0]["adjclose"]
    s = pd.Series(v, index=pd.to_datetime(r["timestamp"], unit="s").normalize()); return s[~s.index.duplicated(keep="last")].dropna()
ret = pd.DataFrame({t: c(t).pct_change() for t in B}).mean(1); rsp = c("RSP").pct_change(); sp = (100 * (ret - rsp)).loc["2026-06-01":"2026-10-30"]
BLUE, ORG, BG, INK, INK2, GRID, GRAY = "#2a78d6", "#eb6834", "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#a9a8a3"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False})
fig, axs = plt.subplots(1, 2, figsize=(17, 7.6), facecolor=BG, gridspec_kw=dict(width_ratios=[2.2, 1], wspace=0.18)); fig.subplots_adjust(top=0.79, bottom=0.12, left=0.06, right=0.97)
fig.text(0.02, 0.935, "Friday looks like a de-grossing day, but it can't be pinned on a forced seller: October's worst days were earnings days", fontsize=17, weight="bold", color=INK)
fig.text(0.02, 0.865, "Bars = 25 AI-crowded names (equal weight) minus the equal-weight S&P (RSP), daily. Orange = bottom 2% since 2024. Pre-registered LQ.\n"
         f"Friday: {L['Fri Oct 30 2026']['spread %']:+.1f} pts (1.4th pct), all 25 down, volume 1.33× (90th pct, not extreme). The July unwind ended with a +12.6-pt relief day; no relief yet today ({I['2026-11-02']['spread %']:+.1f} pts at 11:00).", fontsize=11, color=INK2)
ax = axs[0]; ax.set_facecolor(BG); thr = -6.0
ax.bar(range(len(sp)), sp.values, color=[ORG if v <= thr else (BLUE if v > 0 else GRAY) for v in sp.values], width=0.85)
idx = {d: i for i, d in enumerate(sp.index)}
for d, lab, y in [("2026-07-24", "July unwind\n(reported block\nsale ~Jul 29-30)", -9.5), ("2026-07-30", "+12.6\nrelief", 13.2), ("2026-10-14", "Oct 14", -8.6), ("2026-10-22", "Oct 22\n(META report)", -11.8), ("2026-10-29", "Oct 29 GOOGL\nOct 30 AMZN/INTC", -10.4)]:
    ax.annotate(lab, (idx[pd.Timestamp(d)], sp[pd.Timestamp(d)]), (idx[pd.Timestamp(d)] - (22 if d == "2026-10-22" else 8), y), fontsize=9.2, color=INK, arrowprops=dict(arrowstyle="-", color=GRAY))
ax.axhline(0, color=INK2, lw=1); ax.yaxis.grid(True, color=GRID); ax.set_ylabel("AI basket − RSP, % pts"); ax.set_ylim(-12.5, 14.5)
ticks = [i for i, d in enumerate(sp.index) if d.day <= 7 and d.weekday() == 0]; ax.set_xticks(ticks); ax.set_xticklabels([sp.index[i].strftime("%b %d") for i in ticks], fontsize=10)
ax.set_title("AI-crowded basket vs the rest of the market", loc="left", fontsize=13, weight="bold", color=INK)
ax = axs[1]; ax.set_facecolor(BG); f = I["2026-10-30"]["basket at 10:00 / 12:00 / 15:00 / 15:59 %"]
ax.plot([0, 1, 2, 3, 4], [0] + f, color=ORG, lw=2.6, marker="o"); ax.set_xticks(range(5)); ax.set_xticklabels(["prior close", "10:00", "12:00", "15:00", "close"], fontsize=10)
for x, v in zip(range(1, 5), f): ax.text(x, v - 0.6, f"{v:.1f}", ha="center", fontsize=10)
ax.axhline(0, color=INK2, lw=1); ax.yaxis.grid(True, color=GRID); ax.set_ylim(-11, 1.5)
ax.set_title("Friday's basket path (%)", loc="left", fontsize=13, weight="bold", color=INK)
ax.text(0.05, 0.6, "69% of the loss came by 10:00 (overnight AMZN/INTC news),\nthen a bounce into the close: not a closing-auction dump", fontsize=10, color=INK2)
fig.savefig(HERE / "out" / "liquidation.png", dpi=110, facecolor=BG); print("ok")
