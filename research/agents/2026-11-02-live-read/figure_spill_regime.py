"""AS-R figure: since the DeepSeek shock, reaction-day stock move vs the equal-weight market (RSP): AI spenders' drops came with the
rest of the market rising (rotation); AAPL days were quiet."""
import json
from pathlib import Path

import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent; A = json.load(open(HERE / "out" / "aapl_spill_regime.json"))
BLUE, ORG, BG, INK, INK2, GRID, GRAY = "#2a78d6", "#eb6834", "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#a9a8a3"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False})
ev = A["event table since 2025-01-27 [day, stock, stock %, RSP %, SPY %]"]; r1, r2 = A["since 2025-01-27 (DeepSeek)"], A["since 2025-10-01 (debt-funded capex scrutiny)"]
fig, axs = plt.subplots(1, 2, figsize=(16, 7.4), facecolor=BG, gridspec_kw=dict(width_ratios=[1.45, 1], wspace=0.25)); fig.subplots_adjust(top=0.79, bottom=0.1, left=0.06, right=0.97)
fig.text(0.02, 0.935, "AI-scrutiny era: Apple report days barely move the rest; AI spenders' report days are rotation, not contagion", fontsize=16, weight="bold", color=INK)
fig.text(0.02, 0.865, f"Every earnings reaction day since the DeepSeek shock (Jan 27 2025): stock move vs the equal-weight S&P (RSP). Amendment AS-R, pre-registered.\n"
         f"When an AI spender fell on earnings, the average stock ROSE (+{r1['AI down / up: n, mean RSP %'][0][1]:.2f}% on {r1['AI down / up: n, mean RSP %'][0][0]} such days): money rotated out of AI into everything else. AAPL: 7 reports, no consistent spill either way.", fontsize=11, color=INK2)
ax = axs[0]; ax.set_facecolor(BG)
for d, s, x, y, spy in ev:
    c = ORG if s == "AAPL" else (GRAY if s == "NVDA" else BLUE); ax.scatter(x, y, s=90 if s == "AAPL" else 55, color=c, edgecolor="white", zorder=3)
    if abs(x) >= 9 or s == "AAPL": ax.text(x + 0.3, y + 0.06, f"{s} {d[2:7]}", fontsize=8.6, color=INK2)
ax.axhline(0, color=INK2, lw=1); ax.axvline(0, color=INK2, lw=1); ax.xaxis.grid(True, color=GRID); ax.yaxis.grid(True, color=GRID)
ax.set_xlabel("reporting stock's earnings-day move %"); ax.set_ylabel("equal-weight S&P (RSP) that day %")
ax.scatter([], [], color=ORG, s=90, label="AAPL"); ax.scatter([], [], color=BLUE, s=55, label="MSFT / AMZN / META / GOOGL"); ax.scatter([], [], color=GRAY, s=55, label="NVDA"); ax.legend(fontsize=10, frameon=False, loc="upper left")
ax.set_title("Each dot = one earnings reaction day (Jan 2025 – Oct 2026)", loc="left", fontsize=13, weight="bold", color=INK)
ax = axs[1]; ax.axis("off"); ax.set_title("The numbers", loc="left", fontsize=13, weight="bold", color=INK)
L = [("Average |move| of the rest of the market (RSP)", INK, True), (f"  on AAPL days: {r1['mean |RSP| on reaction days %: AAPL / AI / NVDA'][0]:.2f}% (since Oct 2025: {r2['mean |RSP| on reaction days %: AAPL / AI / NVDA'][0]:.2f}%)", INK2, False),
     (f"  on AI-spender days: {r1['mean |RSP| on reaction days %: AAPL / AI / NVDA'][1]:.2f}% (since Oct 2025: {r2['mean |RSP| on reaction days %: AAPL / AI / NVDA'][1]:.2f}%)", INK2, False), ("", INK, False),
     ("Spillover slope (RSP per 1% of the stock's move)", INK, True), (f"  AAPL {r1['slope AAPL / AI / NVDA'][0]:+.3f} · AI {r1['slope AAPL / AI / NVDA'][1]:+.3f} · NVDA {r1['slope AAPL / AI / NVDA'][2]:+.3f}", INK2, False),
     (f"  difference p {r1['AAPL − AI slope, 95% CI, p'][2]:.2f}: none of them drags the rest along", INK2, False), ("", INK, False),
     ("For tonight", BLUE, True), ("• AAPL moves SPY through its 7.7% weight:", INK, False), ("  ±3.5% ≈ ±27 bp, either way", INK, False),
     ("• no sign it spreads to the rest, up or down", INK, False), ("  (only 2 up reactions since 2025, n tiny)", INK2, False), ("• the broad rally needs breadth, which today has (71% up)", INK, False)]
for i, (t, c, b) in enumerate(L): ax.text(0, 0.96 - i * 0.068, t, fontsize=11.2, color=c, weight="bold" if b else "normal", transform=ax.transAxes)
fig.savefig(HERE / "out" / "aapl_spill_regime.png", dpi=110, facecolor=BG); print("ok")
