"""MSFT level map figure: (a) price since Oct 1 with gamma levels; (b) dealer gamma curve and call/put OI by strike (<=45d).
Usage: python figure.py <td dir> -> out/msft_levels.png (reads out/msft_read.json)"""
import datetime as dt
import json
import sys
import urllib.request
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; O = HERE / "out"; M = json.load(open(O / "msft_read.json"))
sys.path[:0] = [str(HERE.parent / "2026-10-27-flip-wicks")]
from flipmap import norm, preopen, gex_at   # noqa: E402
BG, INK, INK2, GRID, GRAY, BLUE, ORANGE, RED, GREEN = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#a9a8a3", "#2a78d6", "#eb6834", "#c8372d", "#2f8f5b"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": GRAY, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "axes.titleweight": "bold", "axes.titlesize": 11})
td = Path(sys.argv[1]); P, D = pd.Timestamp("2026-11-03"), pd.Timestamp("2026-11-04"); S = M["ref price"]
e = norm(pd.read_csv(td / "MSFT_eod_20261103.csv.gz")); e = e[e.date == P]; o = norm(pd.read_csv(td / "MSFT_oi_20261104.csv.gz"))
g = preopen(e, o, D); g["underlying_close"] = S; grid = np.arange(470, 640.5, 1.0); tot = np.array([gex_at(g, s) for s in grid]) / 1e9
k45 = g[((g.expiration - D).dt.days <= 45)].groupby(["K", "cp"]).oi.sum().unstack().fillna(0); k45 = k45[(k45.index >= 480) & (k45.index <= 640)]
u = "https://query1.finance.yahoo.com/v8/finance/chart/MSFT?range=3mo&interval=1d"
r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=20))["chart"]["result"][0]
px = pd.Series(r["indicators"]["quote"][0]["close"], index=pd.to_datetime([dt.datetime.utcfromtimestamp(t).date() for t in r["timestamp"]])).dropna()
px = px[px.index >= "2026-09-15"]
fig, ax = plt.subplots(1, 2, figsize=(15, 6.2), facecolor=BG, gridspec_kw={"width_ratios": [1.15, 1]}, sharey=True)
for a in ax: a.set_facecolor(BG); a.grid(True, color=GRID, lw=0.8); a.spines[["top", "right"]].set_visible(False)
a = ax[0]; a.plot(px.index, px.values, color=INK, lw=2); a.scatter([px.index[-1]], [px.iloc[-1]], color=INK, zorder=5)
lv = [(575, "575: call wall (148k calls) + peak dealer gamma = ceiling / magnet", GREEN, "-"), (557.25, "557.25: today's high", INK2, ":"),
      (550, "550: big strike + round number", BLUE, "--"), (543.5, "543.5: old record close (Oct 13) ≈ today's open", ORANGE, "--"),
      (521, "521: Tue close (gap fill)", GRAY, ":"), (500, "500: put wall", RED, "--")]
for y, lab, col, ls in lv:
    a.axhline(y, color=col, lw=1.3, ls=ls); a.text(px.index[0], y + 1.2, lab, color=col, fontsize=8.5)
a.set_ylim(485, 600); a.set_ylabel("MSFT")
a.set_title(f"(a) MSFT broke to a record (+{(S / 520.99 - 1) * 100:.1f}% today, {S:.2f}).\nLevels from Tuesday's closing option positions", loc="left")
a = ax[1]; w = 2.0
a.barh(k45.index, k45.get("C", 0) / 1e3, height=w, color=GREEN, alpha=0.75, label="call OI, ≤45 days (k)")
a.barh(k45.index, -k45.get("P", 0) / 1e3, height=w, color=RED, alpha=0.75, label="put OI, ≤45 days (k)")
a.axvline(0, color=INK2, lw=1); a.set_xlabel("open interest, thousands (puts left, calls right)")
b = a.twiny(); b.plot(tot, grid, color=INK, lw=2, label="dealer gamma, $bn per 1%"); b.set_xlabel("total dealer gamma, $bn per 1% (black line)", color=INK)
b.axvline(0, color=GRAY, lw=0.8, ls=":"); b.spines[["top"]].set_color(INK)
a.axhline(S, color=INK, lw=1, ls=":"); a.text(a.get_xlim()[1] * 0.98, S + 1.5, f"now {S:.1f}", ha="right", fontsize=8.5)
a.legend(frameon=False, fontsize=8.5, loc="lower right")
a.set_title(f"(b) Deep long gamma: ${M['gamma at ref']:.1f}bn per 1% at the price, flip far below ({M['flip']:.0f}).\nDealers damp moves; 575 holds the biggest call pile", loc="left", pad=28)
fig.suptitle("MSFT levels, Wed Nov 4: record breakout into a call-heavy, long-gamma zone (550–575)", x=0.01, ha="left", fontsize=13.5, fontweight="bold", color=INK)
fig.text(0.01, 0.01, "OI dated Nov 4 (Tuesday's closing positions) and Tuesday's closing IVs (ThetaData); classic dealer convention. Price: Yahoo daily + live.", fontsize=8, color=INK2)
plt.tight_layout(rect=(0, 0.03, 1, 0.93)); plt.savefig(O / "msft_levels.png", dpi=150, facecolor=BG); print("ok")
