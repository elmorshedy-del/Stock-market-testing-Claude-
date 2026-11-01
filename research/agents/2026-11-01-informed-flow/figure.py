"""Figure: (A) who is informed? reflexivity vs 40-session predictive slope for timely flows; (B) Kimbal Musk's TSLA sales on
the price path, coloured by what followed; (C) his sales vs matched random days. -> out/informed.png"""
import json
import sys
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

O = Path(__file__).resolve().parent / "out"; F = json.load(open(O / "informed.json")); K = json.load(open(O / "insider_tsla.json"))
BG, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"; BLUE, ORG, RED, GRN = "#2a78d6", "#eb6834", "#d03b3b", "#0ca30c"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10.3, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": GRID,
                     "xtick.color": INK2, "ytick.color": INK2})
fig = plt.figure(figsize=(15.5, 10.4), facecolor=BG)
gs = fig.add_gridspec(2, 3, height_ratios=[1, 1.05], width_ratios=[1.1, 1, 1], hspace=0.42, wspace=0.28, left=0.055, right=0.985, top=0.86, bottom=0.07)
fig.text(0.055, 0.955, "Following the 'smart money': none of the visible flows called the next two months", fontsize=17, weight="bold", color=INK)
fig.text(0.055, 0.918, "Timely flows we can see (futures positioning, dark pools, credit, the close vs the open) either chase price or carry no forecast.\n"
         "Kimbal Musk's famous top-ticks are real, but so are his sales before big rallies; across all 48 sales he did no better than random days.", fontsize=10.5, color=INK2, va="top")
# A
ax = fig.add_subplot(gs[0, 0]); ax.set_facecolor(BG)
lab = {"A": "Asset managers\n(futures, 4-wk change)", "L": "Hedge funds / CTAs\n(futures)", "D": "Dark-pool buying\n(DIX)", "C": "Credit investors\n(HYG vs Treasuries)", "SMI": "'Smart money'\n(close vs open)"}
for k, t in lab.items():
    x = F[k]["reflexivity corr(signal, past 20-session return)"]; s = F[k]["f40 slope (log ret per 1 sd)"]; y = s["slope %"]; lo, hi = s["95% CI %"]
    ax.errorbar(x, y, yerr=[[y - lo], [hi - y]], fmt="o", color=BLUE, ms=8, mec=BG, mew=1.5, elinewidth=1.4, capsize=3)
    off = {"A": (0.03, 0, "left"), "L": (0.0, -1.15, "center"), "D": (0.03, -0.45, "left"), "C": (-0.03, 0.45, "right"), "SMI": (0.03, 0.55, "left")}[k]
    ax.text(x + off[0], y + off[1], t, fontsize=8.6, color=INK, va="center", ha=off[2])
ax.axhline(0, color=INK2, lw=0.8); ax.axvline(0, color=INK2, lw=0.8, ls=":")
ax.set_xlim(-0.45, 1.05); ax.set_ylim(-3.2, 2.6); ax.yaxis.grid(True, color=GRID)
ax.set_xlabel("← buy weakness      reflexivity (corr with past 20-day move)      chase price →", fontsize=8.8)
ax.set_ylabel("S&P next 40 sessions, % per 1 sd of the flow")
ax.text(-0.43, 2.35, "informed would sit here: high, near the dotted line", fontsize=8.5, color=GRN)
ax.set_title("A. Who forecasts? (bars = 95% CI; all cross 0)", loc="left", fontsize=12, weight="bold", color=INK)
# B
ax = fig.add_subplot(gs[0, 1:]); ax.set_facecolor(BG)
r = json.load(open(sys.argv[1]))["chart"]["result"][0]
P = pd.Series(r["indicators"]["adjclose"][0]["adjclose"], index=pd.to_datetime(r["timestamp"], unit="s").normalize()).dropna().loc["2019-01-01":]
ax.plot(P.index, P.to_numpy(), color=INK2, lw=1.2)
E = pd.read_csv(O / "kimbal_episodes.csv", parse_dates=["date"]); E = E[E.date >= "2019-01-01"]
for _, e in E.iterrows():
    if not np.isfinite(e.O1_60): continue
    y = P.asof(e.date); col = RED if e.O1_60 < 0 else GRN
    ax.scatter(e.date, y, s=30 + 6 * e["value $m"], color=col, alpha=0.75, edgecolor=BG, lw=1, zorder=3)
    ax.text(e.date, y * (1.12 if e.O1_60 < 0 else 0.86), f"{100 * (np.exp(e.O1_60) - 1):+.0f}%", fontsize=8.3, color=col, ha="center")
ax.set_yscale("log"); ax.yaxis.grid(True, color=GRID); ax.set_ylabel("TSLA (log scale)")
ax.set_title("B. Kimbal Musk's TSLA sales since 2019 (dot size = $; label = TSLA over the next 60 sessions)", loc="left", fontsize=12, weight="bold", color=INK)
ax.text(pd.Timestamp("2023-06-01"), 25, "red = TSLA fell after (the famous ones)\ngreen = TSLA rose after (the forgotten ones)", fontsize=9, color=INK2)
# C
ax = fig.add_subplot(gs[1, 0]); ax.set_facecolor(BG)
k = K["Kimbal Musk"]; o = K["Other TSLA insiders"]
items = [("TSLA 60d after\nfiling, avg %", "O2_60"), ("Sold near the\nlocal top, %", "O3a"), ("20% drop in\n60d, %", "O3b")]
y = np.arange(len(items))[::-1]
ax.barh(y + 0.2, [k[c]["observed"] for _, c in items], 0.36, color=BLUE, label="Kimbal Musk (48 sales)")
ax.barh(y - 0.2, [k[c]["matched random days"] for _, c in items], 0.36, color="#c9c8c3", label="matched random days")
for yi, (_, c) in zip(y, items):
    ax.text(k[c]["observed"] + 0.8, yi + 0.2, f"{k[c]['observed']:.0f}", va="center", fontsize=9.5, color=INK)
    ax.text(k[c]["matched random days"] + 0.8, yi - 0.2, f"{k[c]['matched random days']:.0f}", va="center", fontsize=9.5, color=INK2)
ax.set_yticks([]); ax.set_xlim(0, 42)
for yi, (t, _) in zip(y, items): ax.text(0.3, yi + 0.47, t.replace(chr(10), " "), fontsize=9.3, color=INK, weight="bold", va="bottom"); ax.xaxis.grid(True, color=GRID)
ax.legend(frameon=False, fontsize=9, loc="upper right"); ax.set_title("C. Kimbal vs chance: no edge", loc="left", fontsize=12, weight="bold", color=INK, pad=18)
# D, E text
ax = fig.add_subplot(gs[1, 1]); ax.axis("off")
ax.set_title("D. What each flow reads now (Oct 30)", loc="left", fontsize=12, weight="bold", color=INK)
now = [("Asset managers", F["A"]["now"]["percentile in trailing 3y"], "cutting longs (contrarian-bullish at best)"), ("Hedge funds / CTAs", F["L"]["now"]["percentile in trailing 3y"], "middling"),
       ("Dark-pool buying", F["D"]["now"]["percentile in trailing 3y"], "middling"), ("Credit", F["C"]["now"]["percentile in trailing 3y"], "worst 3% in 3 years (tracks stocks)"),
       ("'Smart money' close", F["SMI"]["now"]["percentile in trailing 3y"], "strong closes vs opens")]
for i, (a, pct, t) in enumerate(now):
    yy = 0.86 - i * 0.14
    ax.text(0.0, yy, a, fontsize=10.2, weight="bold", color=INK, transform=ax.transAxes)
    ax.text(0.47, yy, (lambda v: f"{v}{'st' if v % 10 == 1 and v != 11 else 'nd' if v % 10 == 2 and v != 12 else 'rd' if v % 10 == 3 and v != 13 else 'th'} pct")(int(round(100 * pct))), fontsize=10.2, color=INK, transform=ax.transAxes)
    ax.text(0.0, yy - 0.06, t, fontsize=9, color=INK2, transform=ax.transAxes)
ax.text(0.0, 0.08, "None passed the test, so none of these\nreadings is a forecast.", fontsize=9.8, color=RED, transform=ax.transAxes)
ax = fig.add_subplot(gs[1, 2]); ax.axis("off")
ax.set_title("E. So who can we piggyback?", loc="left", fontsize=12, weight="bold", color=INK)
txt = ("Visible, timely flows: no one. Each group\neither reacts to price (asset managers +0.39,\ncredit +0.74) or carries no signal.\n\n"
       "The groups with published edges are slow:\n• short sellers (aggregate short interest)\n• insiders' non-routine buying\n• firms issuing vs buying back stock\n"
       "They forecast months to years, not the\nnext 40 sessions, and arrive with a lag.\n\n"
       "Other TSLA insiders: a small tilt (TSLA\n2 pts weaker over 60 sessions, p 0.04),\ntoo small to trade.")
ax.text(0.0, 0.95, txt, fontsize=9.8, color=INK, va="top", transform=ax.transAxes, linespacing=1.33)
fig.savefig(O / "informed.png", dpi=108, facecolor=BG); print("ok")
