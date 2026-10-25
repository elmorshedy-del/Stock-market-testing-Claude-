"""The channel's dips in one picture: out/channel_dips.png. Usage: python figure.py <etfs folder> (reads out/dips.csv, out/dip_profiles.csv, out/luck_auc.json)"""
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import dossier as Dz

BLUE, ORANGE, GREEN, RED, INK, MUTED, GRID, SURF = "#2a78d6", "#eb6834", "#1baf7a", "#d64545", "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"
spx = Dz.close(sys.argv[1], "%5EGSPC")
E = pd.read_csv(Dz.OUT / "dips.csv", parse_dates=["start", "high date"])
P = pd.read_csv(Dz.OUT / "dip_profiles.csv", index_col=0)
A = pd.read_csv(Dz.OUT / "dip_separation.csv")
D = pd.read_csv(Dz.OUT / "daily.csv", index_col=0, parse_dates=True)
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
fig = plt.figure(figsize=(15.5, 10))
gs = fig.add_gridspec(2, 2, height_ratios=[1.05, 1], width_ratios=[1.1, 1], hspace=0.38, wspace=0.25)
t = fig.add_subplot(gs[0, :])
s = spx[spx.index >= "2022-10-01"]
t.plot(s.index, s, color=INK, lw=1.1)
b = P.loc["share of panel above 50-day"]
for _, r in E.iterrows():
    key = f"{r.outcome[:4]} {r['high date'].date()}"
    col = RED if r.outcome == "correction" else (GREEN if r.outcome == "bounce" else ORANGE)
    y = spx.loc[r.start]
    t.scatter([r.start], [y], color=col, s=55, zorder=4, edgecolor=SURF, lw=0.8)
    t.annotate(f"{b[key]:+.1f}", (r.start, y), xytext=(0, -15 if r.outcome != "bounce" else 9), textcoords="offset points", ha="center", fontsize=7.5, color=col)
t.scatter([], [], color=RED, s=40, label="dip that became a correction (-5% before a new high)")
t.scatter([], [], color=GREEN, s=40, label="dip the channel bought (new high first)")
t.scatter([], [], color=ORANGE, s=40, label="today's dip (open, started Oct 16)")
t.legend(loc="upper left", frameon=False, fontsize=8.5)
t.set_ylabel("S&P 500")
t.set_title("Every 2% dip in the channel since Oct 2022 (21 decided). Numbers = breadth when the dip started\n"
            "(share of 41 large caps above their 50-day average, z vs normal near-high days)", loc="left", fontsize=10, color=INK)
a = fig.add_subplot(gs[1, 0])
cols = [c for c in P.columns if not c.startswith("open")]
for c in cols:
    corr = c.startswith("corr")
    x = 1 if corr else 0
    a.scatter(x + np.random.default_rng(abs(hash(c)) % 2**32).uniform(-0.12, 0.12), b[c], color=RED if corr else GREEN, s=60, alpha=0.9, zorder=3)
today = b[[c for c in P.columns if c.startswith("open")][0]]
a.scatter([2], [today], color=ORANGE, s=110, zorder=4, marker="D")
a.annotate(f"today {today:+.1f}", (2, today), xytext=(-20, -18), textcoords="offset points", fontsize=9, color=ORANGE, weight="bold")
a.axhline(0.2, color=MUTED, lw=0.8, ls=":")
a.text(2.45, 0.28, "above: 6 of 6 became corrections", fontsize=8, color=RED, ha="right")
a.text(2.45, 0.02, "below: 13 of 15 were bought", fontsize=8, color=GREEN, ha="right", va="top")
a.set_xticks([0, 1, 2], ["bounces (13)", "corrections (8)", "today"])
a.set_xlim(-0.5, 2.5)
a.set_ylabel("breadth at the dip's start (z)")
a.set_title("The one thing that separates them: a dip that starts from BROAD strength\nturns into a correction; a dip from narrow breadth gets bought (AUC 0.89)",
            loc="left", fontsize=9.5, color=INK)
q = fig.add_subplot(gs[1, 1])
L = json.loads((Dz.OUT / "luck_auc.json").read_text())
V = pd.read_csv(Dz.OUT / "dip_profiles.csv", index_col=0)
V = V[[c for c in V.columns if not c.startswith("open")]].dropna()
lab = np.array([c.startswith("corr") for c in V.columns])
au = {}
for k in V.index:
    v = V.loc[k].to_numpy(float)
    x = (v[lab][:, None] > v[~lab][None, :]).mean()
    au[k] = max(x, 1 - x)
au = pd.Series(au).sort_values()
show = list(au.index[-9:])
for extra in ["margin debt growth", "margin debt vs prices"]:
    if extra not in show:
        show = [extra] + show
au = au[show]
cl = [RED if k == "share of panel above 50-day" else (BLUE if k.startswith("margin") else MUTED) for k in au.index]
q.barh(range(len(au)), au.to_numpy(), color=cl, height=0.6)
q.axvline(0.5, color=INK, lw=0.8)
q.set_yticks(range(len(au)), [k.replace("share of panel above 50-day", "BREADTH (share above 50-day)") for k in au.index], fontsize=8.5)
q.set_xlim(0.45, 1)
for i, v in enumerate(au.to_numpy()):
    q.text(v + 0.005, i, f"{v:.2f}", va="center", fontsize=8, color=INK)
fw = L["family-wise p (best of all indicators by chance >= observed)"]["share of panel above 50-day"]
q.set_xlabel("how well it separates corrections from bounces (AUC; 0.5 = coin flip)")
q.set_title(f"Only breadth beats luck (best-of-26 by chance: p {fw:.2f}).\nMargin debt (blue) does not separate them inside the channel", loc="left", fontsize=9.5, color=INK)
fig.savefig(Dz.OUT / "channel_dips.png", dpi=140, bbox_inches="tight", facecolor=SURF)
print("today raw breadth (share above 50-day):", round(float(D["share of panel above 50-day"].iloc[-1]), 3), "on Oct 16:", round(float(D.loc["2026-10-16", "share of panel above 50-day"]), 3),
      "near-high normal:", round(float(D[(D.index >= Dz.CH0) & (D.dist >= -0.03)]["share of panel above 50-day"].mean()), 3))
