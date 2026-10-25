"""Amendment 1 in one picture: out/rallies_flip.png (reads out/rallies.json, out/reclaims.csv)."""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import spy_gamma as G

GREEN, RED, INK, MUTED, SURF = "#1baf7a", "#d64545", "#0b0b0b", "#52514e", "#fcfcfb"
R = json.loads((G.OUT / "rallies.json").read_text())
C = pd.read_csv(G.OUT / "reclaims.csv")
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
fig, (a, b) = plt.subplots(1, 2, figsize=(15, 6), gridspec_kw={"width_ratios": [1.2, 1], "wspace": 0.28})
k1, k2 = "above flip: share of day's move added (+) / given back (-) by day 10", "below flip"
groups = [("Up days\n2020-2026", R["PRIMARY up days, 2020-2026"]), ("Up days\n2023-2026 (channel)", R["up days, 2023-2026 (channel era)"]),
          ("Down days\n2020-2026", R["down days, 2020-2026"])]
x = np.arange(len(groups)); w = 0.36
va = [100 * g[k1] for _, g in groups]; vb = [100 * g[k2] for _, g in groups]
a.bar(x - w / 2, va, w, color=GREEN, label="day closed ABOVE the flip (dealers long gamma)")
a.bar(x + w / 2, vb, w, color=RED, label="day closed BELOW the flip (dealers short gamma)")
for xi, v in zip(list(x - w / 2) + list(x + w / 2), va + vb):
    a.text(xi, v + (3 if v >= 0 else -3), f"{v:+.0f}%", ha="center", va="bottom" if v >= 0 else "top", fontsize=9, color=INK)
for xi, (_, g) in zip(x, groups):
    a.text(xi, -118, f"p {g['p (A - B <= 0)']:.2f}", ha="center", fontsize=8.5, color=MUTED)
a.axhline(0, color=INK, lw=0.8)
a.set_xticks(x, [n for n, _ in groups])
a.set_ylim(-125, 105)
a.set_ylabel("share of the day's move ADDED (+) or GIVEN BACK (-) over the next 10 sessions, %")
a.legend(loc="lower right", bbox_to_anchor=(1.0, 0.12), frameon=False, fontsize=8.5)
a.set_title("Rallies above the flip tend to hold (+13%); rallies below it give back about half (-53%)\n"
            "Down days ABOVE the flip keep going (+79%): a selloff that beats dealer damping is real\n"
            "Direction is clear in every era, but p 0.05-0.24, so suggestive, not proven", loc="left", fontsize=9.5, color=INK)
fr = R["flip reclaims (first close above after >= 3 below)"]
b.hist(C["next 10-day return %"], bins=24, color=GREEN, alpha=0.75, edgecolor=SURF)
b.axvline(fr["mean next 10-day return %"], color=INK, lw=1.4, label=f"after a reclaim: mean {fr['mean next 10-day return %']:+.2f}%")
b.axvline(fr["all days: mean next 10-day return %"], color=MUTED, lw=1.2, ls="--", label=f"all days: mean {fr['all days: mean next 10-day return %']:+.2f}%")
b.axvline(0, color=INK, lw=0.6, ls=":")
b.legend(loc="upper left", frameon=False, fontsize=8.5)
b.set_xlabel("SPY return over the 10 sessions after the first close back above the flip, %")
b.set_ylabel("events")
b.set_title(f"Flip reclaims ({fr['events']} since 2020): {100 * fr['still above after 10 sessions']:.0f}% still above the flip 10 sessions later\n"
            f"Today the flip is 774 (SPY 761): a close above it is the gamma 'all clear' for the bounce", loc="left", fontsize=9.5, color=INK)
fig.savefig(G.OUT / "rallies_flip.png", dpi=140, bbox_inches="tight", facecolor=SURF)
