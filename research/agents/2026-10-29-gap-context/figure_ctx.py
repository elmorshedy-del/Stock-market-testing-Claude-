"""Gap-context figure: effect sizes with 95% CIs for C (trigger) and F (fragility) families, and VF / SC rates for the notable contexts.
Usage: python figure_ctx.py -> out/gap_context.png"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
R = json.load(open(HERE / "out" / "tests_ctx.json"))
INK, INK2, GRID = "#0b0b0b", "#52514e", "#d9d8d4"
VF, SC = "#eb6834", "#2a78d6"          # categorical slots 2 and 1 (validated pair)
plt.rcParams.update({"font.size": 9, "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2})
fig = plt.figure(figsize=(17, 8.2)); gs = fig.add_gridspec(1, 3, width_ratios=[1.15, 1, 1.15], wspace=0.75)


SHORT = {"C1": "C1 above a near-expiry call wall", "C2": "C2 week after monthly expiry (vs week of)", "C3": "C3 turn of the month",
         "C5": "C5 extended above the 20-day mean", "C6": "C6 breakout from a quiet base", "C7": "C7 earnings-reaction gap",
         "C8": "C8 CPI / jobs / day after FOMC", "C9": "C9 mostly the stock's own gap", "C10": "C10 market long gamma (GEX top third)",
         "C12": "C12 buyback blackout (AAPL, NVDA)", "F1": "F1 overnight-up / intraday-down regime", "F2": "F2 thinning liquidity (Amihud)",
         "F3": "F3 air pocket below the open", "F4": "F4 no dealer cushion (freed)", "F5": "F5 fresh call OI above price",
         "F6": "F6 high off-exchange short share", "F7": "F7 narrow market near QQQ high"}


def forest(ax, fam, title, skip=()):
    rows = [(k, v) for k, v in fam.items() if "ci95" in v and k.split(" ")[0] not in skip and "rho" not in k]
    for i, (k, v) in enumerate(rows):
        lo, hi = v["ci95"]; e = v["estimate"]
        ax.plot([lo, hi], [i, i], color=INK2, lw=1.6, solid_capstyle="round")
        ax.plot(e, i, "o", ms=8, mfc=INK if v["sign_as_predicted"] else "white", mec=INK, mew=1.6, zorder=3)
        tag = ("  PASSES Holm" + (" (unit artifact, see text)" if k.startswith("F2") else "")) if v["pass"] else f"  Holm p {v['p_holm']:.2f}"
        ax.text(max(hi, 0) + 0.02, i, tag, va="center", fontsize=8, color=INK if v["pass"] else INK2, fontweight="bold" if v["pass"] else "normal")
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([SHORT.get(k.split(" ")[0], k.split(" (Y")[0]) for k, _ in rows], fontsize=8.5, color=INK); ax.invert_yaxis()
    ax.axvline(0, color=INK2, lw=0.8); ax.grid(axis="x", color=GRID, lw=0.6); ax.set_axisbelow(True)
    ax.set_xlabel("context minus rest, first-hour outcome in σ (stock-demeaned)\nfilled = sign as predicted, hollow = opposite")
    ax.set_title(title, loc="left", fontsize=10.5, color=INK); ax.set_xlim(-0.7, 0.75)
    for s in ("top", "right"): ax.spines[s].set_visible(False)


ax1 = fig.add_subplot(gs[0, 0]); forest(ax1, R["family"], "Trigger: what kind of day (C1–C12)")
c4 = R["family"]["C4 month-end rebalance: MTD SPY-TLT vs Y1, last 4 days (rho, -)"]; c11 = R["family"]["C11 own-dealer hedge pressure vs Y1 (rho, -)"]
ax1.text(-0.7, len([k for k in R["family"] if "rho" not in k]) + 1.4,
         f"Correlations: C4 month-end rebalance ρ {c4['estimate']:+.2f} [{c4['ci95'][0]:+.2f}, {c4['ci95'][1]:+.2f}]; "
         f"C11 dealer hedge pressure ρ {c11['estimate']:+.2f} [{c11['ci95'][0]:+.2f}, {c11['ci95'][1]:+.2f}]. Neither passes.", fontsize=8, color=INK2)
ax2 = fig.add_subplot(gs[0, 1]); forest(ax2, R["fragility"], "Spring: fragility built before the gap (F1–F7)")
# VF / SC rates, context vs rest
ax3 = fig.add_subplot(gs[0, 2])
pick = [("C7 own earnings reaction (Y1, +)", "Earnings-reaction gap"), ("C1 pin pull (Y1, -)", "Above a near-expiry call wall"),
        ("C9 own (idiosyncratic) gap, top tercile (Y1, -)", "Mostly the stock's own gap"), ("F3 air pocket below, bottom tercile (Y1, -)", "Air pocket below the open"),
        ("F1 clientele tug-of-war, top tercile (Y1, -)", "Overnight up / intraday down regime"), ("C10 market GEX top vs bottom tercile (Y2, -)", "Market long gamma (GEX top third)")]
allr = {**R["family"], **R["fragility"]}
for i, (k, lab) in enumerate(pick):
    v = allr[k]; y = i * 3
    for j, (rate, col, nm) in enumerate([("vf", VF, "VF"), ("sc", SC, "SC")]):
        yy = y + j * 1.0; a, b = 100 * v[f"{rate}_rate_rest"], 100 * v[f"{rate}_rate_context"]
        ax3.plot([a, b], [yy, yy], color=col, lw=2, alpha=0.6)
        ax3.plot(a, yy, "o", ms=8, mfc="white", mec=col, mew=1.8); ax3.plot(b, yy, "o", ms=8, color=col, mec="white", mew=2)
        ax3.text(max(a, b) + 0.8, yy, f"{nm} {b:.0f}% vs {a:.0f}%", va="center", fontsize=8, color=INK)
    ax3.text(-0.5, y - 0.75, f"{lab}  (n={v['n_context']})", fontsize=8.5, color=INK, fontweight="bold")
ax3.set_ylim(len(pick) * 3 - 1, -1.6); ax3.set_yticks([]); ax3.set_xlim(0, 36); ax3.grid(axis="x", color=GRID, lw=0.6); ax3.set_axisbelow(True)
ax3.set_xlabel("share of gap-ups, %   (hollow = all other gap-ups, filled = in the context)")
ax3.set_title("How often the first hour is a violent fade (VF) or continuation (SC)", loc="left", fontsize=10.5, color=INK)
for s in ("top", "right", "left"): ax3.spines[s].set_visible(False)
fig.suptitle("Why that day? 1,512 gap-ups ≥ 0.5σ in TSLA / AAPL / NVDA / QQQ, 2018–2026 (base rates: VF 13%, SC 13%). "
             "No calendar, flow, trend or regime context passes; the earnings-gap fade is the lead.", fontsize=11.5, color=INK, x=0.01, ha="left")
fig.savefig(HERE / "out" / "gap_context.png", dpi=130, bbox_inches="tight", facecolor="#fcfcfb")
print("saved")
