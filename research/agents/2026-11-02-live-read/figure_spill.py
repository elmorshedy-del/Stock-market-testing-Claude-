"""AS figure: earnings-day spillover to the rest of the market (RSP) per 1% of the stock's move, by stock and era; AAPL up vs down."""
import json
from pathlib import Path

import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent; A = json.load(open(HERE / "out" / "aapl_spill.json"))
BLUE, ORG, BG, INK, INK2, GRID, GRAY = "#2a78d6", "#eb6834", "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#a9a8a3"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False})
fig, axs = plt.subplots(1, 2, figsize=(16, 7), facecolor=BG, gridspec_kw=dict(width_ratios=[1.5, 1], wspace=0.28)); fig.subplots_adjust(top=0.78, bottom=0.12, left=0.07, right=0.97)
fig.text(0.02, 0.93, "Apple's earnings moves have NOT spilled over less than the AI spenders'. If anything, more (2022+)", fontsize=18, weight="bold", color=INK)
fig.text(0.02, 0.86, "Pre-registered AS (10:12 ET). Slope = how much the equal-weight S&P (RSP) moved per 1% of the reporting stock's earnings-day move. 2015–2026 reports.\n"
         "Up reactions co-move more than down ones (as you said), but not significantly. Confound: AAPL's reaction day is often payrolls Friday; tonight's is election day.", fontsize=11, color=INK2)
ax = axs[0]; ax.set_facecolor(BG); names = ["AAPL", "MSFT", "AMZN", "META", "GOOGL", "NVDA"]
for j, (era, col) in enumerate([("2015-26", GRAY), ("2022+", BLUE)]):
    v = [A[era][n]["slope of RSP on the stock's move"] for n in names]
    ax.bar([i + (j - 0.5) * 0.38 for i in range(len(names))], v, 0.36, color=[ORG if n == "AAPL" else col for n in names], alpha=0.55 if j == 0 else 1.0, label=era)
    for i, x in enumerate(v): ax.text(i + (j - 0.5) * 0.38, x + 0.004 if x >= 0 else x - 0.012, f"{x:.2f}", ha="center", fontsize=9.5)
ax.axhline(0, color=INK2, lw=1); ax.set_xticks(range(len(names))); ax.set_xticklabels(names, fontsize=11.5); ax.yaxis.grid(True, color=GRID); ax.set_ylabel("RSP move per 1% of the stock's move")
ax.legend(fontsize=10, frameon=False, title="faded = 2015–26, solid = 2022+"); ax.set_title("Spillover per 1% move", loc="left", fontsize=13.5, weight="bold", color=INK)
p1, p2 = A["2015-26"]["AS1: AAPL slope − AI slope [diff, 95% CI, p]"], A["2022+"]["AS1: AAPL slope − AI slope [diff, 95% CI, p]"]
ax.text(2.2, 0.15, f"AAPL − AI spenders: {p1[0]:+.3f} (p {p1[2]:.2f}) 2015–26\n                         {p2[0]:+.3f} (p {p2[2]:.2f}) 2022+", fontsize=10.5, color=INK)
ax = axs[1]; ax.set_facecolor(BG)
rows = [("2015–26", A["2015-26"]), ("2022+", A["2022+"])]
for j, (lab, r) in enumerate(rows):
    up, dn = r["AS2 AAPL up reactions: n, slope, mean RSP %"], r["AS2 AAPL down reactions: n, slope, mean RSP %"]
    ax.bar([j * 3, j * 3 + 1], [up[1], dn[1]], color=[BLUE, ORG], width=0.8)
    ax.text(j * 3, up[1] + 0.01, f"{up[1]:.2f}\nn {up[0]}", ha="center", fontsize=10); ax.text(j * 3 + 1, dn[1] + 0.01, f"{dn[1]:.2f}\nn {dn[0]}", ha="center", fontsize=10)
    ax.text(j * 3 + 0.5, -0.07, lab, ha="center", fontsize=11.5, weight="bold")
ax.set_xticks([0, 1, 3, 4]); ax.set_xticklabels(["AAPL up", "AAPL down", "AAPL up", "AAPL down"], fontsize=10); ax.set_ylim(-0.1, 0.55); ax.yaxis.grid(True, color=GRID)
a2a, a2b = A["2015-26"]["AS2: up slope − down slope [diff, 95% CI, p]"], A["2022+"]["AS2: up slope − down slope [diff, 95% CI, p]"]
ax.set_title(f"AAPL up vs down (p {a2a[2]:.2f} / {a2b[2]:.2f})", loc="left", fontsize=12.5, weight="bold", color=INK)
fig.savefig(HERE / "out" / "aapl_spill.png", dpi=110, facecolor=BG); print("ok")
