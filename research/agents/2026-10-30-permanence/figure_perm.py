"""Permanence figure. Usage: python figure_perm.py -> out/permanence.png"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; O = HERE / "out"
INK, INK2, GRID, C1, C2 = "#0b0b0b", "#52514e", "#d9d8d4", "#2a78d6", "#eb6834"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2})
R = json.load(open(O / "runs.json"))["tests"]; X = json.load(open(O / "exit_days.json")); E = pd.read_csv(O / "stock_runs.csv", parse_dates=["date"])
fig, ax = plt.subplots(2, 2, figsize=(14.5, 9.5)); plt.subplots_adjust(hspace=0.45, wspace=0.55)


def clean(a, g="x"):
    for s in ("top", "right"): a.spines[s].set_visible(False)
    a.grid(axis=g, color=GRID, lw=0.6); a.set_axisbelow(True)


a = ax[0, 0]; rows = list(R.items()) + [("old proxy: ATM implied vol change (5 names)", R["X4 call-skew (25-delta risk reversal) change during the run"]["old proxy, ATM IV change"] | {"sign_as_predicted": False, "p_holm": float("nan")})]
SH = {"X1": "X1 abnormal volume (42 stocks)", "X2": "X2 thinning liquidity (42 stocks)", "X3": "X3 overnight share (42 stocks)", "X4": "X4 call-skew richening (5 names)",
      "X5": "X5 low dealer gamma (S&P)", "X6": "X6 narrow breadth (S&P)"}
for i, (k, v) in enumerate(rows):
    lo, hi = v["ci95"]; a.plot([lo, hi], [i, i], color=INK2, lw=1.6); a.plot(v["rho"], i, "o", ms=8, mfc=INK if v.get("sign_as_predicted") else "white", mec=INK, mew=1.6)
    a.text(max(hi, 0) + 0.02, i, f"n={v['n']}" + (f", Holm p {v['p_holm']:.2f}" if np.isfinite(v.get("p_holm", np.nan)) else f", p {v['p']:.2f}"), va="center", fontsize=8, color=INK2)
a.set_yticks(range(len(rows))); a.set_yticklabels([SH.get(k[:2], k) for k, _ in rows], color=INK, fontsize=8.5); a.invert_yaxis(); a.axvline(0, color=INK2, lw=0.8); clean(a)
a.set_xlabel("Spearman with permanence P20 (negative = footprint predicts the run fades)\nfilled = sign as predicted"); a.set_xlim(-0.45, 0.5)
a.set_title("(a) Which footprints predict that a rally won't hold?\nNone passes; call-skew richening is the closest (p 0.05)", loc="left", color=INK, fontsize=10)
a = ax[0, 1]; E["vt"] = pd.qcut(E.groupby("sym").X1_abvol.rank(pct=True), 3, labels=["low", "mid", "high"])
g = E.groupby("vt", observed=True); x = np.arange(3)
a.bar(x, 100 * g.cliff.mean(), color=[C2, "#bbbbbb", C1], width=0.6)
for i, (nm, gg) in enumerate(g): a.text(i, 100 * gg.cliff.mean() + 1, f"{100*gg.cliff.mean():.0f}%\nkept {gg.P20.median():.2f} of run\nafter 20 sessions", ha="center", fontsize=8, color=INK)
a.set_xticks(x); a.set_xticklabels(["low-volume runs", "mid", "high-volume runs"], color=INK); a.set_ylim(0, 50); a.set_ylabel("% giving back half within 10 sessions"); clean(a, "y")
a.set_title(f"(b) 5,853 top-decile 10-day runs, 42 stocks 1990-2025:\nlow-volume runs hit the cliff more often (not the predicted direction)", loc="left", color=INK, fontsize=10)
a = ax[1, 0]; K = pd.read_csv(O / "skew.csv", parse_dates=["date"])
import importlib.util
rows4 = []
for s in ("TSLA", "NVDA", "QQQ", "MSFT", "MU"):
    pass
xs = json.load(open(O / "runs.json"))["tests"]["X4 call-skew (25-delta risk reversal) change during the run"]
a.text(0.42, 0.30, f"call skew rose over the run → kept less of it\nρ {xs['rho']:+.2f} [{xs['ci95'][0]:+.2f}, {xs['ci95'][1]:+.2f}], n={xs['n']}, p {xs['p']:.2f}\n\nATM implied vol (yesterday's proxy):\nρ {xs['old proxy, ATM IV change']['rho']:+.2f}, p {xs['old proxy, ATM IV change']['p']:.2f}", transform=a.transAxes, va="top", fontsize=9, color=INK, bbox=dict(facecolor="#fcfcfb", edgecolor=GRID, boxstyle="round,pad=0.4"))
k = K[(K.sym == "TSLA") & (K.date >= "2020-06-01")].set_index("date").rr25
a.plot(k.index, 100 * k.rolling(5).mean(), color=C1, lw=1.2, label="TSLA 25-delta risk reversal (call IV - put IV), 5-day mean")
a.axhline(0, color=INK2, lw=0.8); a.set_ylabel("vol points"); a.set_ylim(-25, 15); a.legend(fontsize=8, frameon=False, loc="upper left"); clean(a, "y")
a.set_title("(c) The convexity footprint: paying up for upside calls (skew rising)", loc="left", color=INK, fontsize=10)
a = ax[1, 1]; D = X["descriptive_not_passing"]; labs = {"X1_abvol": "abnormal volume", "X2_amihud": "thin liquidity", "X3_overnight": "overnight share"}
for i, (kx, v) in enumerate(D.items()):
    a.plot([v["ci95"][0], v["ci95"][1]], [i, i], color=INK2, lw=1.6); a.plot(v["est_sigma"], i, "o", ms=8, color=C2 if kx == "X2_amihud" else INK)
    a.text(max(v["ci95"][1], 0) + 0.01, i, f"median {v['median_oc_pct_top']:+.2f}% vs {v['median_oc_pct_rest']:+.2f}%, p {v['p']:.2f}", va="center", fontsize=8, color=INK2)
a.set_yticks(range(len(D))); a.set_yticklabels([f"top third: {labs[k]}" for k in D], color=INK); a.invert_yaxis(); a.axvline(0, color=INK2, lw=0.8); clean(a)
a.set_xlabel("gap-day open -> close vs other post-run gap-ups, σ (descriptive)")
a.set_title(f"(d) The exit: gap-ups within 3 sessions of a run's end (n={X['n_gap_days']})\nafter thin-liquidity runs the gap day fades (descriptive)", loc="left", color=INK, fontsize=10)
fig.suptitle("Permanent vs transitory rallies: footprints from mechanics, tested on permanence", fontsize=12, color=INK, x=0.01, ha="left")
fig.savefig(O / "permanence.png", dpi=130, bbox_inches="tight", facecolor="#fcfcfb"); print("saved")
