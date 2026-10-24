"""The forced-flow results in one picture: out/forced_flow.png (reads out/f1.json, out/r3a.json, out/r3b.json)."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parent / "out"
BLUE, ORANGE, GREEN, INK, MUTED, GRID, SURF = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"
f1 = json.loads((OUT / "f1.json").read_text())["6 names pooled (z-returns)"]
r3a = json.loads((OUT / "r3a.json").read_text())
r3b = json.loads((OUT / "r3b.json").read_text())
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
f, (a, z) = plt.subplots(1, 2, figsize=(15.5, 5.8), gridspec_kw={"width_ratios": [1.2, 1], "wspace": 0.25})
days = np.arange(0, 11)
lo = [0] + f1["cumulative response low-gamma half, days 1..10"]
hi = [0] + f1["cumulative response high-gamma half, days 1..10"]
a.axhline(0, color=MUTED, lw=0.8)
a.plot(days, 100 * np.array(lo), "-o", color=ORANGE, lw=2, ms=4, label="move made on a LOW dealer-gamma day (dealers short: forced to chase)")
a.plot(days, 100 * np.array(hi), "-o", color=BLUE, lw=2, ms=4, label="move made on a HIGH dealer-gamma day (dealers long: damping)")
a.set_xlabel("sessions after the move")
a.set_ylabel("share of the day's move added (+) or given back (-), %")
a.legend(loc="lower left", frameon=False, fontsize=8.5)
g = r3a["day-10 gap (low - high gamma)"]
a.set_title(f"Forced moves fade, unforced moves stick\n6 stocks/ETFs with own dealer gamma, 2020-2026 (9,494 days)\n"
            f"day-10 gap {100 * g['gap']:.0f} pts (p {g['p (gap >= 0)']:.3f}); both halves, 5 of 6 tickers; not volatility", loc="left", fontsize=9.5, color=INK)
labels = ["other days", "month end", "Russell\nreconstitution", "quad witching", "all forced\ncalendar days"]
base = r3b["slope of c5 on x, other days / forced days"][0]
vals = [base, base + r3b["month end: days, d (5d), d (10d)"][1], base + r3b["Russell reconstitution: days, d (5d), d (10d)"][1],
        base + r3b["quad witching: days, d (5d), d (10d)"][1], r3b["slope of c5 on x, other days / forced days"][1]]
ns = [r3b["days"] - r3b["forced days"], r3b["month end: days, d (5d), d (10d)"][0], r3b["Russell reconstitution: days, d (5d), d (10d)"][0],
      r3b["quad witching: days, d (5d), d (10d)"][0], r3b["forced days"]]
cols = [MUTED, ORANGE, ORANGE, ORANGE, INK]
x = np.arange(len(labels))
z.bar(x, 100 * np.array(vals), color=cols, width=0.6, edgecolor=SURF)
for xi, v, n in zip(x, vals, ns):
    z.text(xi, 100 * v - 1.5, f"{100 * v:.0f}%\nn={n:,}", ha="center", va="top", fontsize=8, color=INK)
z.axhline(0, color=INK, lw=0.8)
z.set_xticks(x, labels, fontsize=8.5)
z.set_ylim(-85, 10)
z.set_ylabel("share of the day's S&P move given back over the next 5 sessions, %")
d = r3b["d (x * forced day), next 5 days"]
z.set_title(f"The same fingerprint from a different forced actor: S&P 1990-2026\n"
            f"moves on calendar forced-flow days are given back more (difference {100 * d['d']:.0f} pts, p {d['p (d >= 0)']:.3f})",
            loc="left", fontsize=9.5, color=INK)
f.savefig(OUT / "forced_flow.png", dpi=140, bbox_inches="tight", facecolor=SURF)
