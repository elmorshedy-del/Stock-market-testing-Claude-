"""Election-vol card -> out/election_vol.png"""
import json
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

O = Path(__file__).resolve().parent / "out"; R = json.load(open(O / "results.json")); T = json.load(open(O / "tsla_event.json")); Oc = pd.read_csv(O / "october.csv", index_col=0, parse_dates=True)
BG, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"; BLUE, ORG, GRAY, RED = "#2a78d6", "#eb6834", "#a9a8a3", "#d03b3b"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10.2, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": GRID,
                     "xtick.color": INK2, "ytick.color": INK2})
fig = plt.figure(figsize=(15.5, 10.4), facecolor=BG)
gs = fig.add_gridspec(2, 3, hspace=0.5, wspace=0.34, left=0.05, right=0.985, top=0.84, bottom=0.07)
fig.text(0.05, 0.955, "October's vol spike is not an election premium for SPY (null); TSLA does price one", fontsize=16.5, weight="bold", color=INK)
fig.text(0.05, 0.915, "Each session's priced-in move from consecutive daily expiries (Friday Oct 30 close). The election results land Wed Nov 4 (vote Tue Nov 3; AAPL reports Mon after the close).\n"
         "Party odds from Polymarket; sector sensitivities from daily odds changes (2026 midterms; 2024 presidential as a check).", fontsize=10, color=INK2, va="top")
ax = fig.add_subplot(gs[0, 0]); ax.set_facecolor(BG)
s = R["A1 Oct 30 per-session implied moves (SPY)"]; lab = [p["pair"][-5:] for p in s]; v = [p["per-session move %"] for p in s]
cols = [ORG if l == "11-04" else BLUE for l in lab]
ax.bar(range(len(v)), v, color=cols); ax.axhline(R["A1 election session (Nov 4)"]["normal session move %"], color=INK2, ls="--", lw=1)
ax.set_xticks(range(len(v)), [l.replace("11-", "Nov ") for l in lab], rotation=45, fontsize=8.6); ax.set_ylabel("priced-in 1-day move, %"); ax.yaxis.grid(True, color=GRID); ax.set_ylim(0, 1.4)
ax.text(2, 1.18, "results day 1.08%\nvs normal 0.99%", ha="center", fontsize=9, color=ORG, weight="bold")
ax.set_title("A. SPY: election day priced like a normal day", loc="left", fontsize=12, weight="bold", color=INK)
ax = fig.add_subplot(gs[0, 1]); ax.set_facecolor(BG)
s = T["sessions"]; lab = [p["pair"][5:10] + "→" + p["pair"][-5:] for p in s]; v = [p["per-session move %"] for p in s]
ax.bar(range(len(v)), v, color=[ORG if "11-02→11-04" in l else BLUE for l in lab]); ax.axhline(T["baseline session move % (Nov 6-20 pairs)"], color=INK2, ls="--", lw=1)
ax.set_xticks(range(len(v)), [l.replace("11-", "Nov ").replace("10-", "Oct ") for l in lab], rotation=45, fontsize=8); ax.set_ylabel("priced-in move per session, %"); ax.yaxis.grid(True, color=GRID); ax.set_ylim(0, 4)
ax.text(1, 3.45, "vote + results: 3.26%/day\nvs normal 2.57%", ha="center", fontsize=9, color=ORG, weight="bold")
ax.set_title("B. TSLA: an election premium (~1.2 extra days)", loc="left", fontsize=12, weight="bold", color=INK)
ax = fig.add_subplot(gs[0, 2]); ax.set_facecolor(BG)
ax.plot(Oc.index, Oc["IV30 %"], color=BLUE, lw=2.2, label="SPY 30-day ATM IV"); ax.plot(Oc.index, Oc["IV30 ex-election %"], color=ORG, lw=1.6, ls="--", label="without the election day")
ax.yaxis.grid(True, color=GRID); ax.set_ylabel("%"); ax.legend(frameon=False, fontsize=9, loc="upper left"); ax.tick_params(axis="x", labelsize=8.5)
import matplotlib.dates as mdates; ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
ax.text(Oc.index[11], 12.05, "rise Oct 9 → 30: +3.0 pts\nelection's part: ≤ 0.2 pts", fontsize=9, color=INK2)
ax.set_title("C. October's IV rise is not the election", loc="left", fontsize=12, weight="bold", color=INK)
ax = fig.add_subplot(gs[1, 0]); ax.axis("off")
a22, a24, a26 = R["A3 2022"], R["A3 2024"], R["A3 2026 (Oct 29, T-3)"]
ax.set_title("D. Precedents (3 sessions before the vote)", loc="left", fontsize=12, weight="bold", color=INK)
rows = [("", "2022 mid", "2024 pres", "2026 mid"),
        ("extra priced move", f"{a22['implied excess move of election sessions %']:.1f}%", f"{a24['implied excess move of election sessions %']:.1f}%", f"{a26['implied excess move of election session %']:.1f}%"),
        ("normal day", f"{a22['normal session move %']:.1f}%", f"{a24['normal session move %']:.1f}%", f"{a26['normal session move %']:.1f}%"),
        ("SPY on results day", f"{a22['realised SPY on the results session %']:+.1f}%", f"{a24['realised SPY on the results session %']:+.1f}%", "Wed Nov 4"),
        ("VIX before → results", f"{a22['VIX day before -> results day -> +3 sessions'][0]:.1f} → {a22['VIX day before -> results day -> +3 sessions'][1]:.1f}", f"{a24['VIX day before -> results day -> +3 sessions'][0]:.1f} → {a24['VIX day before -> results day -> +3 sessions'][1]:.1f}", "?"),
        ("crush on the day?", "no*", "yes, −4.2", "little to crush")]
for i, r in enumerate(rows):
    for j, c in enumerate(r):
        ax.text([0.0, 0.40, 0.64, 0.88][j], 0.86 - i * 0.13, c, fontsize=9.2 if i else 9.6, weight="bold" if (i == 0 or j == 0) else "normal", color=INK if j else INK2, transform=ax.transAxes)
ax.text(0.0, 0.0, "* 2022: VIX fell only after CPI two days later.\nExtra priced move = the results session over a normal day.", fontsize=8.6, color=INK2, transform=ax.transAxes)
ax = fig.add_subplot(gs[1, 1]); ax.set_facecolor(BG)
b = R["now: Balance of Power odds"]; items = [("Democrats sweep", b["Democrats Sweep"]), ("D House, R Senate", b["R Senate, D House"]), ("Republicans sweep", b["Republicans Sweep"]), ("R House, D Senate", b["D Senate, R House"])]
ax.barh(range(4), [100 * i[1] for i in items][::-1], color=[GRAY, GRAY, ORG, BLUE], height=0.55); ax.xaxis.grid(True, color=GRID); ax.set_yticks([])
for k, (n, p) in enumerate(items[::-1]): ax.text(100 * p + 1, k, f"{100 * p:.1f}%", va="center", fontsize=9.5); ax.text(0.5, k + 0.36, n, fontsize=9.3, color=INK, weight="bold")
ax.set_xlim(0, 85); ax.set_xlabel("Polymarket probability now, %")
ax.set_title("E. What the market expects (Balance of Power)", loc="left", fontsize=12, weight="bold", color=INK)
ax = fig.add_subplot(gs[1, 2]); ax.axis("off")
ax.set_title("F. The surprise case: R keeps the Senate", loc="left", fontsize=12, weight="bold", color=INK)
bs = R["B2 2026: P(R Senate) betas"]; val = R["B2 2024 validation: predicted vs actual Nov 6 moves"]
txt = (f"2026 daily odds → sectors (per +10 pts R Senate):\n• clean energy (ICLN) {bs['ICLN']['per +10 pts']:+.1f}%  (p {bs['ICLN']['p']:.3f}, Holm {bs['ICLN']['Holm']:.2f})\n"
       f"• long bonds (TLT) {bs['TLT']['per +10 pts']:+.1f}%  (p {bs['TLT']['p']:.2f})\n• others: no reliable link\n\n"
       f"Does this method work? 2024 check: odds-based\nbetas vs the actual day after the vote:\ncorr {val['corr across assets']:+.2f}, right direction {val['sign agreement']}.\n"
       "Caught: solar −11.5%, regional banks +12.6%,\nTSLA +13.8%. Missed: financials, energy.\n\n"
       "So: the base case (D sweep, 72%) is priced;\nthe market-moving surprise is an R Senate,\nhitting clean energy and lifting yields.")
ax.text(0.0, 0.95, txt, fontsize=9.6, color=INK, va="top", transform=ax.transAxes, linespacing=1.32)
fig.savefig(O / "election_vol.png", dpi=108, facecolor=BG); print("ok")
