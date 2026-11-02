"""Options-information card -> out/options_signal.png"""
import json
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

O = Path(__file__).resolve().parent / "out"; R = json.load(open(O / "results.json")); X = pd.read_csv(O / "signals.csv", index_col=0, parse_dates=True)
BG, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"; BLUE, ORG, GRN, RED = "#2a78d6", "#eb6834", "#0ca30c", "#d03b3b"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10.3, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": GRID,
                     "xtick.color": INK2, "ytick.color": INK2})
names = {"O1": "Calls vs puts\n(IV spread)", "O2": "Put skew", "O3": "Put/call\nvolume", "O4": "Put/call\nopen interest"}
fig = plt.figure(figsize=(15.5, 9.4), facecolor=BG)
gs = fig.add_gridspec(2, 3, hspace=0.45, wspace=0.42, left=0.1, right=0.985, top=0.85, bottom=0.08)
H = R["Holm (10 sessions, O1-O4)"]
best = min(H, key=H.get)
fig.text(0.06, 0.95, R.get("_headline", "TSLA calls and puts: what they add beyond gamma"), fontsize=16.5, weight="bold", color=INK)
fig.text(0.06, 0.91, "Each signal from end-of-day option quotes, 2020-07 to 2026-10. Tested on TSLA's next 10 sessions after controlling for momentum and our gamma state (flip, GEX).",
         fontsize=10.2, color=INK2, va="top")
ax = fig.add_subplot(gs[0, 0]); ax.set_facecolor(BG)
ks = ["O1", "O2", "O3", "O4"]; y = np.arange(4)[::-1]
for yi, k in zip(y, ks):
    s = R[k]["f10"]; v = s["slope % per sd (beyond momentum + gamma)"]; lo, hi = s["95% CI"]
    ax.errorbar(v, yi, xerr=[[v - lo], [hi - v]], fmt="o", color=BLUE, ms=8, capsize=3, mec=BG, mew=1.5)
    ax.text(v, yi + 0.22, f"p {s['p']:.2f}", ha="center", fontsize=8.8, color=INK2)
ax.axvline(0, color=INK2, lw=0.8); ax.set_ylim(-0.5, 3.55); ax.set_yticks(y, [names[k] for k in ks], fontsize=9.3)
ax.set_xlabel("TSLA next 10 sessions, % per 1 sd of the signal"); ax.xaxis.grid(True, color=GRID)
ax.set_title("A. Does each signal predict? (95% CI)", loc="left", fontsize=12, weight="bold", color=INK)
ax = fig.add_subplot(gs[0, 1]); ax.set_facecolor(BG)
w = 0.38
for i, k in enumerate(ks):
    t, b, nt, nb = R[k]["next 10 sessions: top third vs bottom third (trailing year)"]
    ax.bar(i - w / 2, t, w, color=BLUE); ax.bar(i + w / 2, b, w, color="#c9c8c3")
    ax.text(i - w / 2, t + (0.2 if t >= 0 else -0.6), f"{t:+.1f}", ha="center", fontsize=8.8); ax.text(i + w / 2, b + (0.2 if b >= 0 else -0.6), f"{b:+.1f}", ha="center", fontsize=8.8, color=INK2)
ax.set_xticks(range(4), [names[k].replace("\n", " ").replace(" (IV spread)", "") for k in ks], fontsize=8.6, rotation=12); ax.axhline(0, color=INK2, lw=0.8); ax.yaxis.grid(True, color=GRID)
ax.set_ylabel("avg TSLA next 10 sessions, %"); ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=BLUE), plt.Rectangle((0, 0), 1, 1, color="#c9c8c3")],
                                                          labels=["signal in its top third", "bottom third"], frameon=False, fontsize=8.8)
ax.set_ylim(-1.5, 3.0); ax.set_title("B. Top vs bottom third of each signal", loc="left", fontsize=12, weight="bold", color=INK)
ax = fig.add_subplot(gs[0, 2]); ax.set_facecolor(BG)
for i, k in enumerate(ks):
    o = R[k]["OOS R2 % 2023-26 (10 sessions)"]
    ax.bar(i - w / 2, o["signal+controls"], w, color=BLUE); ax.bar(i + w / 2, o["controls only"], w, color="#c9c8c3")
ax.axhline(0, color=INK2, lw=0.8); ax.set_xticks(range(4), [names[k].replace("\n", " ").replace(" (IV spread)", "") for k in ks], fontsize=8.6, rotation=12); ax.yaxis.grid(True, color=GRID)
ax.set_ylabel("out-of-sample R², % (2023-26)"); ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=BLUE), plt.Rectangle((0, 0), 1, 1, color="#c9c8c3")],
                                                        labels=["with the signal", "gamma + momentum only"], frameon=False, fontsize=8.8)
ax.set_title("C. Forecasting 2023-26 without peeking", loc="left", fontsize=12, weight="bold", color=INK)
ax = fig.add_subplot(gs[1, :2]); ax.set_facecolor(BG)
z = X["O1"].rolling(5).mean().loc["2024-01-01":]
ax.plot(z.index, 100 * z.to_numpy(), color=BLUE, lw=1.4); ax.axhline(0, color=INK2, lw=0.8)
for d in R["named bursts: percentile the day before (O1 IVS, O2 SKEW)"]:
    ax.axvline(pd.Timestamp(d), color=GRN, lw=1, alpha=0.7)
for d in R["named tops: percentile on the top day (O1, O2)"]:
    if pd.Timestamp(d) >= z.index[0]: ax.axvline(pd.Timestamp(d), color=RED, lw=1.2, ls="--", alpha=0.8)
ax.set_ylabel("call IV − put IV, vol points (5-day avg)"); ax.yaxis.grid(True, color=GRID)
ax.set_title("D. Calls vs puts pricing since 2024 (green = your named bursts, red dashed = named tops)", loc="left", fontsize=12, weight="bold", color=INK)
ax = fig.add_subplot(gs[1, 2]); ax.axis("off")
ax.set_title("E. Reading", loc="left", fontsize=12, weight="bold", color=INK)
ax.text(0.0, 0.95, R.get("_reading", ""), fontsize=9.8, color=INK, va="top", transform=ax.transAxes, linespacing=1.33)
fig.savefig(O / "options_signal.png", dpi=108, facecolor=BG); print("ok")
