"""Polymarket December-Fed card -> out/polymarket_fed.png"""
import json
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

O = Path(__file__).resolve().parent / "out"; R = json.load(open(O / "results.json")); D = pd.read_csv(O / "daily_2026.csv", index_col=0, parse_dates=True)
BG, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"; BLUE, ORG, GRAY = "#2a78d6", "#eb6834", "#a9a8a3"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10.3, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": GRID,
                     "xtick.color": INK2, "ytick.color": INK2})
fig = plt.figure(figsize=(15.5, 10), facecolor=BG)
gs = fig.add_gridspec(2, 3, height_ratios=[1, 1.1], width_ratios=[1, 1.15, 1], hspace=0.5, wspace=0.3, left=0.085, right=0.985, top=0.83, bottom=0.07)
fig.text(0.05, 0.955, "When December hike odds jump, bond proxies fall the same day; in 2026 that link is unusually strong", fontsize=16, weight="bold", color=INK)
fig.text(0.05, 0.915, "Polymarket 'Fed Decision in December?' read at 16:00 ET each day (Jul 31 → Oct 30, 2026), with the 2024 and 2025 December markets as replications.\n"
         "Sensitivity = same-day return per +5bp hawkish shift in the expected decision. Free data (Polymarket, Yahoo).", fontsize=10, color=INK2, va="top")
ax = fig.add_subplot(gs[0, 0]); ax.set_facecolor(BG)
ax.plot(D.index, D.E_bps, color=BLUE, lw=2.2); ax.set_ylabel("expected December move, bp", color=INK2); ax.yaxis.grid(True, color=GRID)
ax.axvline(pd.Timestamp("2026-09-01"), color=INK2, lw=0.8, ls=":"); ax.text(pd.Timestamp("2026-09-03"), 4, "Sep 1", fontsize=9, color=INK2)
ax.text(D.index[2], 19, "+5bp ≈ 30% hike odds (mid-Aug)\n+20bp ≈ 78% (mid-Oct)", fontsize=9, color=INK2, va="top")
ax.set_title("A. The shift: from +5bp to +18-20bp", loc="left", fontsize=12, weight="bold", color=INK)
ax.tick_params(axis="x", labelsize=8.5); import matplotlib.dates as mdates; ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d")); ax.xaxis.set_major_locator(mdates.MonthLocator())
ax = fig.add_subplot(gs[0, 1:]); ax.set_facecolor(BG)
assets = ["ITB", "XLU", "XBI", "REM", "ARKK", "IWM", "XLRE", "TLT", "KRE", "GLD", "TSLA", "SPY", "QQQ", "DX-Y.NYB"]
lab = {"ITB": "Homebuilders", "XLU": "Utilities", "XBI": "Biotech", "REM": "Mortgage REITs", "ARKK": "ARKK", "IWM": "Small caps", "XLRE": "REITs", "TLT": "Long Treasuries",
       "KRE": "Regional banks", "GLD": "Gold", "TSLA": "TSLA", "SPY": "SPY", "QQQ": "QQQ", "DX-Y.NYB": "Dollar"}
H = R["H1 same-day sensitivity"]; x = np.arange(len(assets))
v26 = [H[a]["2026"]["per +5bps hawkish shift"] for a in assets]; p26 = [H[a]["2026"]["p"] for a in assets]
ax.bar(x, v26, 0.6, color=[BLUE if p < 0.05 else "#9fc3ec" for p in p26], zorder=2)
for yr, mk, col in (("2025", "o", ORG), ("2024", "s", GRAY)):
    ax.scatter(x, [H[a][yr]["per +5bps hawkish shift"] for a in assets], marker=mk, s=34, color=col, zorder=3, label=f"{yr} market", edgecolor=BG)
ax.axhline(0, color=INK2, lw=0.8); ax.set_xticks(x, [lab[a] for a in assets], rotation=35, ha="right", fontsize=9); ax.yaxis.grid(True, color=GRID)
ax.set_ylabel("same-day return per +5bp hawkish shift, %")
ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=BLUE), plt.Rectangle((0, 0), 1, 1, color="#9fc3ec")] + ax.get_legend_handles_labels()[0],
          labels=["2026 (p < 0.05)", "2026 (not significant)", "2025 market", "2024 market"], frameon=False, fontsize=8.8, ncol=2, loc="upper left")
ax.set_title("B. Who reacts to a hawkish shift (bars = 2026; dots = the same test in 2024/2025)", loc="left", fontsize=12, weight="bold", color=INK)
ax = fig.add_subplot(gs[1, :2]); ax.set_facecolor(BG)
H4 = R["H4 rate sensitivity now vs history"]; a4 = ["ITB", "REM", "XLU", "TLT", "XLRE", "KRE", "XBI", "IWM", "SPY", "QQQ", "ARKK", "TSLA"]
y = np.arange(len(a4))[::-1]
for yi, a in zip(y, a4):
    med, now = H4[a]["2020-26 median"], H4[a]["40d beta now (% per +10bp)"]
    ax.annotate("", xy=(now, yi), xytext=(med, yi), arrowprops=dict(arrowstyle="->", color=ORG if abs(now) > abs(med) * 1.5 or np.sign(now) != np.sign(med) else GRAY, lw=2))
    ax.plot(med, yi, "o", color=GRAY, ms=7); ax.plot(now, yi, "o", color=ORG, ms=8)
    pc = H4[a]["percentile of now vs 2020-26 (0 = most negative)"]
    ax.text(2.6, yi, f"{100 * pc:.0f}th pct", va="center", fontsize=8.8, color=INK2)
ax.axvline(0, color=INK2, lw=0.8); ax.set_yticks(y, [lab.get(a, a) for a in a4], fontsize=9.3); ax.set_xlim(-2.6, 3.1); ax.xaxis.grid(True, color=GRID)
ax.set_xlabel("return per +10bp rise in the 5-year yield, % (grey = normal 2020-26, orange = last 40 sessions)")
ax.set_title("C. The aberration: how rate-sensitive each asset is now vs normal", loc="left", fontsize=12, weight="bold", color=INK)
ax = fig.add_subplot(gs[1, 2]); ax.axis("off")
ax.set_title("D. What it means", loc="left", fontsize=12, weight="bold", color=INK)
txt = ("Replicated across 3 December markets:\nhawkish shift → utilities, REITs, mortgage\nREITs, homebuilders, long bonds down;\ndollar up. SPY/QQQ barely move.\n\n"
       "2026 aberrations:\n• the 5-year yield moves ~2.5x more per\n  shift than in 2024/25 (13.5bp vs ~5):\n  bonds price a hiking path, not one move\n"
       "• bond proxies 2-3x more rate-sensitive\n  than normal (utilities: most since 2020)\n• regional banks flipped: now fall when\n  yields rise (normally rise)\n"
       "• tech and TSLA move WITH yields lately\n  (risk-on/off days), not against them\n• gold turned rate-sensitive (−2.2%)\n\n"
       "Digestion: no lead or lag at the daily\nlevel; Polymarket adds nothing beyond\nthe 5-year yield in 2026.")
ax.text(0.0, 0.96, txt, fontsize=9.6, color=INK, va="top", transform=ax.transAxes, linespacing=1.3)
fig.savefig(O / "polymarket_fed.png", dpi=108, facecolor=BG); print("ok")
