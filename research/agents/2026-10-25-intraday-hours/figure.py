"""Intraday hours in one picture: out/intraday_hours.png. Usage: python figure.py <hourly folder> (reads out/part_a.json, out/confirm.json)"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm

import explore as X
import segments as G

BLUE, ORANGE, GREEN, INK, MUTED, GRID, SURF = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"
folder = sys.argv[1]
pa = json.loads((G.OUT / "part_a.json").read_text())
cf = json.loads((G.OUT / "confirm.json").read_text())
syms = sorted(p.name.split("_")[0] for p in Path(folder).glob("*_60m.json"))
explore, held = X.split_days(folder)
full = {s: G.segments(folder, s) for s in syms}
sig = lambda days, s: 1e4 * float(np.nanmean((full[s]["first"] - full[s]["on"]).reindex(days)))
a = {s: sig(explore, s) for s in syms}
h = {s: sig(held, s) for s in syms}
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(1, 3, figsize=(17, 6.2), gridspec_kw={"width_ratios": [1, 1.25, 1], "wspace": 0.3})
p = ax[0]
seg = ["on", "first", "mid", "last"]
labs = ["overnight", "first hour\n9:30-10:30", "midday\n10:30-15:30", "last 30 min\n+ close"]
A1 = pa["A1 segment means (annualized %)"]
x = np.arange(4)
w = 0.38
va = [A1[k]["AAPL"] for k in seg]
vp = [A1[k]["peer average"] for k in seg]
p.bar(x - w / 2, va, w, color=ORANGE, label="AAPL")
p.bar(x + w / 2, vp, w, color=MUTED, label="MSFT, AMZN, GOOGL, META, NVDA average")
for xi, k in zip(x, seg):
    pv = A1[k]["p (two-sided)"]
    p.text(xi, max(A1[k]["AAPL"], A1[k]["peer average"], 0) + 1.5, f"p {pv:.2f}", ha="center", fontsize=8, color=INK if pv < 0.05 else MUTED)
p.axhline(0, color=INK, lw=0.8)
p.set_xticks(x, labs, fontsize=8.5)
p.set_ylabel("average return, % per year")
p.set_ylim(-7, 30)
p.legend(loc="lower left", frameon=False, fontsize=8)
p.set_title("Who buys AAPL during the day? Not the close.\nIt is bought in the FIRST hour (+24%/yr year 1, +18%/yr year 2);\nits weak overnight vanished in year 2 (-21 -> +18%/yr)", loc="left", fontsize=9.5, color=INK)
q = ax[1]
semis = set(["NVDA", "AVGO", "AMD", "MU", "AMAT", "QCOM", "TXN", "INTC", "SMH"])
for s in syms:
    col = BLUE if s in semis else (ORANGE if s in ("AAPL", "TSLA") else MUTED)
    q.scatter(a[s], h[s], s=22 if col == MUTED else 34, color=col, alpha=0.85, zorder=3)
for s in ["AAPL", "TSLA", "NVDA", "AVGO", "MU", "ORCL", "T", "IBM", "BAC", "UNH", "SPY", "BA", "CAT", "ADBE"]:
    q.annotate(s, (a[s], h[s]), xytext=(4, 3), textcoords="offset points", fontsize=8, color=INK)
lim = [-45, 30]
q.plot(lim, lim, color=GRID, lw=1, zorder=1)
q.axhline(0, color=MUTED, lw=0.6); q.axvline(0, color=MUTED, lw=0.6)
q.set_xlim(lim); q.set_ylim(lim)
q.set_xlabel("year 1 (explored): first hour minus overnight, bp per day")
q.set_ylabel("year 2 (held out): first hour minus overnight, bp per day")
f4 = cf["F4 persistence of (first hour - overnight) across 51 tickers"]
q.text(-43, 27, "opens cheap, bought in the first hour", fontsize=8, color=MUTED, va="top")
q.text(28, -43, "gaps up overnight, fades in the first hour", fontsize=8, color=MUTED, ha="right")
q.scatter([], [], color=BLUE, label="semiconductors"); q.scatter([], [], color=ORANGE, label="AAPL, TSLA"); q.scatter([], [], color=MUTED, label="other stocks / ETFs")
q.legend(loc="upper left", bbox_to_anchor=(0.0, 0.93), frameon=False, fontsize=8)
q.set_title(f"CONFIRMED: every stock has a lasting 'open personality'\nyear-1 ranking predicts year 2 across 51 tickers (Spearman {f4['spearman exploration vs held-out']:.2f}, "
            f"Holm p {cf['confirmations']['F4 persistence of (first hour - overnight) across 51 tickers']['Holm p']:.3f})", loc="left", fontsize=9.5, color=INK)
r = ax[2]
items = [("F1 first hour predicts\nlast half hour", "F1 first hour -> last half hour, pooled stocks", +1),
         ("F2 month-end last half\nhour is up", "F2 month-end last half hour, stock average", +1),
         ("F3 AAPL gap predicts its\nlast half hour (negative)", "F3 AAPL overnight -> last half hour", +1),
         ("F4 open personality\npersists", "F4 persistence of (first hour - overnight) across 51 tickers", +1),
         ("F5 semis gap up\nand fade", "F5 semis minus rest, (first hour - overnight)", +1)]
y = np.arange(len(items))[::-1]
for yi, (lab, k, _) in zip(y, items):
    c = cf["confirmations"][k]
    z = norm.ppf(1 - min(max(c["raw p"], 1e-4), 1 - 1e-4))
    col = GREEN if c["confirmed"] else (MUTED if z < 1.645 else BLUE)
    r.barh(yi, z, color=col, height=0.55)
    r.text(max(z, 0) + 0.08, yi, f"p {c['raw p']:.3g}, Holm {c['Holm p']:.2g}" + ("  CONFIRMED" if c["confirmed"] else ""), va="center", fontsize=8, color=INK)
r.axvline(norm.ppf(0.95), color=MUTED, lw=0.8, ls=":")
r.axvline(0, color=INK, lw=0.8)
r.set_yticks(y, [i[0] for i in items], fontsize=8.5)
r.set_xlim(-1.6, 5.2)
r.set_xlabel("held-out strength in the predicted direction (z); dotted = p 0.05")
r.set_title("Last-hour ideas found in year 1, tested on year 2:\nthe last-hour patterns die; only the open personality survives", loc="left", fontsize=9.5, color=INK)
fig.savefig(G.OUT / "intraday_hours.png", dpi=140, bbox_inches="tight", facecolor=SURF)
print("TSLA year1/year2:", round(a["TSLA"], 1), round(h["TSLA"], 1), "AAPL:", round(a["AAPL"], 1), round(h["AAPL"], 1), "SPY:", round(a["SPY"], 1), round(h["SPY"], 1), "QQQ:", round(a["QQQ"], 1), round(h["QQQ"], 1))
