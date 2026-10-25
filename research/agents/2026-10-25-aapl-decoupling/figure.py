"""The AAPL decoupling deep-dive in one picture: out/aapl_decoupling.png
(reads out/daily.csv, out/decoupling.json, out/r3a.json, out/r3b.json, out/posthoc3.json)."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent / "out"
BLUE, ORANGE, GREEN, INK, MUTED, GRID, SURF = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"
D = pd.read_csv(OUT / "daily.csv", index_col=0, parse_dates=True)
r1 = json.loads((OUT / "decoupling.json").read_text())
r3a = json.loads((OUT / "r3a.json").read_text())
r3b = json.loads((OUT / "r3b.json").read_text())
p3 = json.loads((OUT / "posthoc3.json").read_text())
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
f = plt.figure(figsize=(15.5, 10.5))
gs = f.add_gridspec(2, 2, height_ratios=[1, 1.15], width_ratios=[1.45, 1], hspace=0.42, wspace=0.22)
t = f.add_subplot(gs[0, :])
X = D[D.index >= "2011-01-01"]
c = X["corr AAPL"]
t.plot(c.index, c, color=BLUE, lw=0.9)
al = X["alarm AAPL"].astype(bool)
t.fill_between(c.index, -0.6, 1.0, where=al, color=ORANGE, alpha=0.13, lw=0, label="alarm: correlation in the bottom fifth of its last year")
for d in X.index[X.top.astype(bool)]:
    t.axvline(d, color=INK, lw=1, ls=":", alpha=0.8)
t.plot([], [], color=INK, lw=1, ls=":", label="S&P top (252-day high, then a fall of 5% or more)")
t.axvspan(pd.Timestamp("2022-10-13"), X.index[-1], color=GRID, alpha=0.5, lw=0, zorder=0)
t.text(pd.Timestamp("2022-11-01"), -0.55, "the channel: where the idea was found", fontsize=8.5, color=MUTED, va="bottom")
t.scatter([c.index[-1]], [c.iloc[-1]], color=ORANGE, s=40, zorder=5)
t.annotate(f"today {c.iloc[-1]:+.2f}", (c.index[-1], c.iloc[-1]), xytext=(-70, -18), textcoords="offset points", fontsize=9, color=ORANGE, weight="bold")
t.set_ylim(-0.6, 1.0)
t.set_ylabel("AAPL vs S&P, 20-day correlation")
t.legend(loc="lower left", frameon=False, fontsize=8.5, ncol=2)
t.set_title("AAPL's 20-day correlation with the S&P since 2011: alarm days (shaded) and S&P tops (dotted)", loc="left", fontsize=10, color=INK)
a = f.add_subplot(gs[1, 0])
rows = [("1990-2010 (AAPL small, none expected), near-high control", r3a["1990-2010"]["distance-adjusted difference"], r3a["1990-2010"]["p (one-sided, shift)"], MUTED),
        ("2011-2022 out of sample, raw", r1["H1 AAPL, 2011-2022"]["difference"], r1["H1 AAPL, 2011-2022"]["p (one-sided, shift)"], BLUE),
        ("2011-2022 out of sample, near-high control", r3a["2011-2022"]["distance-adjusted difference"], r3a["2011-2022"]["p (one-sided, shift)"], BLUE),
        ("Channel 2022-2026 (discovery), near-high control", r3a["channel 2022-2026 (discovery)"]["distance-adjusted difference"],
         r3a["channel 2022-2026 (discovery)"]["p (one-sided, shift)"], ORANGE),
        ("12 other markets, biggest stock vs its index (fresh)", r3b["PRIMARY average distance-adjusted difference"], r3b["p (one-sided, common shift)"], INK)]
y = np.arange(len(rows))[::-1]
a.axvline(0, color=MUTED, lw=0.8)
for yi, (lab, v, p, col) in zip(y, rows):
    a.plot([0, 100 * v], [yi, yi], color=col, lw=2.2)
    a.scatter([100 * v], [yi], color=col, s=55, zorder=3)
    a.text(100 * v + (1 if v >= 0 else -1), yi + 0.22, f"{100 * v:+.0f} pts   p {p:.2f}", fontsize=8.5, color=col, ha="left" if v >= 0 else "right")
pm = [m["distance-adjusted difference"] for m in r3b["per market"]]
a.scatter(100 * np.array(pm), np.full(len(pm), y[-1]) - 0.28, color=MUTED, s=12, marker="|", zorder=2)
a.text(100 * min(pm), y[-1] - 0.5, "each market", fontsize=7.5, color=MUTED)
a.set_yticks(y, [r[0] for r in rows], fontsize=8.5)
a.set_xlim(-22, 34)
a.set_ylim(-0.9, len(rows) - 0.45)
a.set_xlabel("P(S&P top within 30 sessions | alarm) minus P(... | no alarm), percentage points")
a.set_title("The edge lives in the era it was found in. Out of sample it shrinks to +5 pts once\n"
            "'near the high' is controlled; in 12 other markets it is gone (5 of 12 positive)", loc="left", fontsize=9.5, color=INK)
b = f.add_subplot(gs[1, 1])
eras = ["1990-2026", "2011-2026", "channel 2022-2026"]
w = 0.36
xx = np.arange(len(eras))
on = [p3[e]["P(dip extends to -5% first | alarm)"] for e in eras]
off = [p3[e]["P(dip extends to -5% first | no alarm)"] for e in eras]
b.bar(xx - w / 2, 100 * np.array(on), w, color=ORANGE, label="AAPL alarm on (today)")
b.bar(xx + w / 2, 100 * np.array(off), w, color=MUTED, label="alarm off")
for xi, v, e in zip(xx - w / 2, on, eras):
    b.text(xi, 100 * v + 1, f"{100 * v:.0f}%\n{p3[e]['days, episodes (alarm)'][1]} ep.", ha="center", fontsize=8, color=INK)
for xi, v, e in zip(xx + w / 2, off, eras):
    b.text(xi, 100 * v + 1, f"{100 * v:.0f}%\n{p3[e]['days, episodes (no alarm)'][1]} ep.", ha="center", fontsize=8, color=INK)
b.set_xticks(xx, eras)
b.set_ylim(0, 62)
b.set_ylabel("dips of 1.5-3.5% that reach -5% before a new high, %")
b.legend(loc="upper right", frameon=False, fontsize=8.5)
b.set_title(f"Today's question: the S&P is {p3['today']['distance %']:.1f}% off its high.\n"
            "Does the AAPL alarm make a deeper dip more likely? Barely (post hoc)", loc="left", fontsize=9.5, color=INK)
f.savefig(OUT / "aapl_decoupling.png", dpi=140, bbox_inches="tight", facecolor=SURF)
