"""ADHD breadth picture for Mon Nov 2 ~09:50 ET: who pushes SPY, sector spectrum, chips split. -> out/breadth_1102.png"""
import json
from pathlib import Path

import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent; B = json.load(open(HERE / "out" / "breadth_now.json"))
BLUE, ORG, BG, INK, INK2, GRID, GRAY = "#2a78d6", "#eb6834", "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#a9a8a3"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False})
fig = plt.figure(figsize=(17, 10), facecolor=BG); gs = fig.add_gridspec(2, 3, height_ratios=[1, 1], hspace=0.42, wspace=0.42, left=0.07, right=0.98, top=0.83, bottom=0.07)
a, d = B["advancers / decliners"]
fig.text(0.02, 0.945, f"Broad rally, not a megacap one: {int(100*B['share of members up'])}% of the S&P is up; AAPL is the anchor dragging it", fontsize=20, weight="bold", color=INK)
fig.text(0.02, 0.895, f"S&P 500 members, ~09:50 ET (Yahoo, ~4 min delayed). {a} up / {d} down. Average stock {B['equal-weight move %']:+.2f}% vs index {B['cap-weight move % (reconstructed)']:+.2f}% "
         f"(SPY +0.57% live). Top 10 names add {B['top 10 weight: move % / contribution bp']:+.0f} bp, the other 490 add {B['other 490: contribution bp']:+.0f} bp.", fontsize=11.5, color=INK2)
ax = fig.add_subplot(gs[0, 0:2]); S = B["by sector"]; ks = list(S)
ax.bar(range(len(ks)), [S[k]["eq-wt move %"] for k in ks], color=[BLUE if S[k]["eq-wt move %"] > 0 else ORG for k in ks])
for i, k in enumerate(ks): ax.text(i, S[k]["eq-wt move %"] + (0.08 if S[k]["eq-wt move %"] >= 0 else -0.25), f"{int(100*S[k]['share up'])}% up", ha="center", fontsize=9.5, color=INK2)
ax.axhline(0, color=INK2, lw=1); ax.set_xticks(range(len(ks))); ax.set_xticklabels(ks, rotation=25, fontsize=10.5); ax.set_ylabel("average stock move %"); ax.yaxis.grid(True, color=GRID)
ax.set_title("Sector spectrum: cyclicals lead, energy is the only broad loser", loc="left", fontsize=13.5, weight="bold", color=INK)
ax = fig.add_subplot(gs[0, 2]); up, dn = B["biggest pushes up [move %, bp]"], B["biggest drags [move %, bp]"]
items = [(k, v[1]) for k, v in list(up.items())[:6]] + [(k, v[1]) for k, v in list(dn.items())[:6]]; items.sort(key=lambda t: t[1])
ax.barh(range(len(items)), [v for _, v in items], color=[BLUE if v > 0 else ORG for _, v in items]); ax.set_yticks(range(len(items))); ax.set_yticklabels([k for k, _ in items], fontsize=10.5)
for i, (k, v) in enumerate(items): ax.text(v + (0.3 if v > 0 else -0.3), i, f"{v:+.1f}", va="center", ha="left" if v > 0 else "right", fontsize=9.5)
ax.axvline(0, color=INK2, lw=1); ax.set_xlabel("points of the index move (bp)"); ax.xaxis.grid(True, color=GRID); ax.set_xlim(-14, 19)
ax.set_title("Who moves SPY", loc="left", fontsize=13.5, weight="bold", color=INK)
ax = fig.add_subplot(gs[1, 0:2]); C = B["chips & memory [move %]"]; grp = {"AI & memory (last week's drag)": ["NVDA", "AVGO", "AMD", "MU", "MRVL", "WDC", "STX", "SNDK", "INTC", "LRCX", "AMAT"], "Analog & industrial chips": ["TXN", "ADI", "ON", "NXPI", "MCHP", "QCOM", "KLAC", "MPWR"]}
x0 = 0; ticks, labs = [], []
for gname, names in grp.items():
    vals = [(n, C[n]) for n in names if n in C]
    for j, (n, v) in enumerate(vals):
        ax.bar(x0 + j, v, color=BLUE if v > 0 else ORG); ticks.append(x0 + j); labs.append(n)
    ax.text(x0 + (len(vals) - 1) / 2, 4.3, gname, ha="center", fontsize=11.5, weight="bold", color=INK)
    x0 += len(vals) + 1
ax.set_xticks(ticks); ax.set_xticklabels(labs, fontsize=10); ax.axhline(0, color=INK2, lw=1); ax.set_ylim(-6.8, 5); ax.set_ylabel("% move"); ax.yaxis.grid(True, color=GRID)
ax.set_title("Chips split in two: memory and AI-capex still sold (STX −5, MRVL −6, ORCL −6); analog chips rally with cyclicals", loc="left", fontsize=12.5, weight="bold", color=INK)
ax = fig.add_subplot(gs[1, 2]); ax.axis("off"); ax.set_title("Read", loc="left", fontsize=13.5, weight="bold", color=INK)
L = [("Rotation, not liquidation, again: the", INK), ("average stock beats the index.", INK), ("", INK), ("AAPL −1.3% (reports tonight) is the", INK2), ("biggest single drag (−10 bp).", INK2), ("", INK),
     ("AMZN +4.2%, NVDA, GOOGL, MSFT", INK2), ("supply most of the push.", INK2), ("", INK), ("For our cycle: a healthy rebuild is", BLUE), ("price up WITH breadth. Today fits.", BLUE)]
for i, (t, c) in enumerate(L): ax.text(0, 0.95 - i * 0.085, t, fontsize=11.5, color=c, transform=ax.transAxes, weight="bold" if c == BLUE else "normal")
fig.savefig(HERE / "out" / "breadth_1102.png", dpi=110, facecolor=BG); print("ok")
