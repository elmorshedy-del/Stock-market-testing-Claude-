"""Your named bursts: what came next, vs now -> out/named_bursts.png"""
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

O = Path(__file__).resolve().parent / "out"
BG, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"; GRN, BLUE, GRAY, ORG = "#0ca30c", "#2a78d6", "#a9a8a3", "#eb6834"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10.5, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": GRID,
                     "xtick.color": INK2, "ytick.color": INK2})
T = pd.read_csv(O / "named.csv"); P = pd.read_csv(O / "named_paths.csv", index_col=0)
fig = plt.figure(figsize=(15.5, 8.6), facecolor=BG)
gs = fig.add_gridspec(1, 2, width_ratios=[1.55, 1], wspace=0.08, left=0.05, right=0.985, top=0.83, bottom=0.09)
fig.text(0.05, 0.95, "Your 11 named TSLA bursts: the fast ones were up 5%+ by day 3. Now is −1.9%: a dip-then-run or a fade", fontsize=16, weight="bold", color=INK)
fig.text(0.05, 0.905, "Each line = TSLA after the burst's second day (0 = that close). Green = up fast (≥ +5% by day 3). Blue = dipped by day 3, then ran (≥ +15% by day 10).\n"
         "Grey = slower grind or faded. Orange = now (Oct 27 close → Oct 30). Buying aggression = net buy share of volume on the burst days (1-minute bars).",
         fontsize=10, color=INK2, va="top")
ax = fig.add_subplot(gs[0, 0]); ax.set_facecolor(BG)
kind = {}
for _, r in T.iterrows():
    if r.burst.startswith("NOW"): continue
    k = "fast" if r["+3 sessions %"] >= 5 else ("dip-run" if (r["+3 sessions %"] < 0 and r["+10 sessions %"] >= 15) else "faded")
    kind[r.burst] = k
    col = {"fast": GRN, "dip-run": BLUE, "faded": GRAY}[k]; y = P[r.burst].dropna()
    ax.plot(y.index, y.to_numpy(), color=col, lw=2 if k != "faded" else 1.4, alpha=0.9)
    ax.text(y.index[-1] + 0.2, y.iloc[-1], r.burst, fontsize=8.3, color=col, va="center")
now = P["NOW: Oct 26-27 '26"].dropna(); ax.plot(now.index, now.to_numpy(), color=ORG, lw=4, marker="o", ms=6)
ax.text(now.index[-1] + 0.3, now.iloc[-1] - 2.2, "NOW", color=ORG, fontsize=11, weight="bold")
ax.axhline(0, color=INK2, lw=0.8); ax.axvline(3, color=INK2, lw=0.8, ls=":"); ax.text(3.15, 33, "day 3\n(where we are)", fontsize=9, color=INK2)
ax.set_xlim(0, 24.5); ax.set_xlabel("sessions after the burst"); ax.set_ylabel("% from the burst close"); ax.yaxis.grid(True, color=GRID)
ax = fig.add_subplot(gs[0, 1]); ax.axis("off")
ax.set_title("Burst buying and what followed", loc="left", fontsize=12.3, weight="bold", color=INK)
hdr = ["burst", "buying", "volume", "day 3", "day 10"]; xs = [0.0, 0.42, 0.57, 0.72, 0.87]
for j, h in enumerate(hdr): ax.text(xs[j], 0.95, h, fontsize=9.8, weight="bold", color=INK2, transform=ax.transAxes)
T2 = T.copy(); T2["k"] = T2.burst.map(kind).fillna("now")
T2 = T2.sort_values("buying aggression % (net buy share)", ascending=False)
for i, (_, r) in enumerate(T2.iterrows()):
    y = 0.89 - i * 0.068; col = {"fast": GRN, "dip-run": BLUE, "faded": GRAY, "now": ORG}[r.k]
    vals = [r.burst.replace(" (call-wall break)", " (wall break)").replace("NOW: ", "NOW "), f"{r['buying aggression % (net buy share)']:.0f}%", f"{r['rel. volume']:.1f}x",
            f"{r['+3 sessions %']:+.1f}%", "?" if np.isnan(r["+10 sessions %"]) else f"{r['+10 sessions %']:+.0f}%"]
    for j, v in enumerate(vals):
        ax.text(xs[j], y, v, fontsize=9.6, color=col if j == 0 else INK, weight="bold" if r.k in ("now",) or j == 0 else "normal", transform=ax.transAxes)
ax.text(0.0, 0.0, "Of the 4 that dipped by day 3: the 2 on above-normal volume ran\n(Jun '24 1.2x, Oct '24 2.5x); the 2 on normal volume faded (late May '25,\nOct '25 a). Now: 1.5x volume, 13% buying. n = 11: a lean, not proof.",
        fontsize=9.4, color=INK2, transform=ax.transAxes)
fig.savefig(O / "named_bursts.png", dpi=108, facecolor=BG); print("ok")
