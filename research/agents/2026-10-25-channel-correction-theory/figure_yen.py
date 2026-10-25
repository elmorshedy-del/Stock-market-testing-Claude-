"""Yen amendment in one picture: out/yen_carry.png (reads out/dip_profiles.csv, out/yen.json, out/shock_types.json)."""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import dossier as Dz

BLUE, ORANGE, GREEN, RED, PURPLE, INK, MUTED, GRID, SURF = "#2a78d6", "#eb6834", "#1baf7a", "#d64545", "#7a5cc7", "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"
P = pd.read_csv(Dz.OUT / "dip_profiles.csv", index_col=0)
Yj = json.loads((Dz.OUT / "yen.json").read_text())
S = json.loads((Dz.OUT / "shock_types.json").read_text())
yz = Yj["(a) spark: dip anatomy"]["yen 20-day (USD/JPY change)"]["per episode"]
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
fig, (a, b) = plt.subplots(1, 2, figsize=(15.5, 6.3), gridspec_kw={"width_ratios": [1.1, 1], "wspace": 0.25})
kcol = {"yen shock": PURPLE, "rates shock": BLUE, "other": MUTED}
for c, yv in yz.items():
    x = P.loc["share of panel above 50-day", c]
    if c.startswith("corr"):
        k = S[c]["kind"]
        a.scatter(x, yv, color=RED, s=95, zorder=3, edgecolor=kcol[k], lw=2.5)
        a.annotate(c.split(" ")[1][:7], (x, yv), xytext=(6, 4), textcoords="offset points", fontsize=8, color=RED)
    else:
        a.scatter(x, yv, color=GREEN, s=55, zorder=3, alpha=0.85)
tx = P.loc["share of panel above 50-day", [c for c in P.columns if c.startswith("open")][0]]
ty = Yj["(a) spark: dip anatomy"]["yen 20-day (USD/JPY change)"]["today (open episode)"]
a.scatter(tx, ty, color=ORANGE, s=130, marker="D", zorder=4)
a.annotate("today", (tx, ty), xytext=(8, -4), textcoords="offset points", fontsize=9.5, color=ORANGE, weight="bold")
a.axvline(0.2, color=MUTED, lw=0.8, ls=":")
a.axhline(0, color=MUTED, lw=0.6)
a.set_xlabel("breadth at the dip's start (z)  ->  broader")
a.set_ylabel("yen over the prior 20 days (z)  <-  yen strengthening")
a.scatter([], [], color=RED, s=60, label="became a correction"); a.scatter([], [], color=GREEN, s=45, label="bought")
a.scatter([], [], facecolor=SURF, edgecolor=PURPLE, lw=2.5, s=60, label="ring: yen-shock correction")
a.scatter([], [], facecolor=SURF, edgecolor=BLUE, lw=2.5, s=60, label="ring: rates-shock correction")
a.legend(loc="lower left", frameon=False, fontsize=8)
fw = Yj["best-of-29 luck check"]["family-wise p"]
a.set_title(f"Spark? Corrections started after the yen had firmed (7 of 8, rule passes, AUC 0.78)\n"
            f"but that is within luck (best-of-29 p {fw['yen 20-day (USD/JPY change)']:.2f}); breadth still does the separating (p {fw['share of panel above 50-day']:.2f})",
            loc="left", fontsize=9.5, color=INK)
names = list(S)
y = np.arange(len(names))[::-1]
vals = [S[k]["USD/JPY %"] for k in names]
b.barh(y, vals, color=[kcol[S[k]["kind"]] for k in names], height=0.6)
for yi, k in zip(y, names):
    v = S[k]["USD/JPY %"]
    b.text(v + (0.25 if v >= 0 else -0.25), yi, f"S&P {S[k]['S&P depth %']:.0f}%, bonds {S[k]['TLT %']:+.0f}%", va="center", ha="left" if v >= 0 else "right", fontsize=8, color=INK)
b.axvline(0, color=INK, lw=0.8)
b.set_yticks(y, [k.split(" ")[1] for k in names])
b.set_xlim(-19, 13)
b.set_xlabel("USD/JPY from the S&P high to the trough, %  (negative = yen up)")
b.set_title("Fuel? Mostly not: the yen rose in only 3 of 8 corrections (Dec 2022 BoJ,\nAug 2024 carry unwind, spring 2025). Most were rates shocks, with the yen FALLING",
            loc="left", fontsize=9.5, color=INK)
fig.savefig(Dz.OUT / "yen_carry.png", dpi=140, bbox_inches="tight", facecolor=SURF)
