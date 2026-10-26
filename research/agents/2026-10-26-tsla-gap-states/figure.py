"""Live read for Tue Oct 27: SPY and TSLA gamma maps + TSLA gap-fill odds. out/live_read_1027.png"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from pathlib import Path
OUT = Path(__file__).resolve().parent / "out"
GREEN, RED, ORANGE, INK, MUTED, SURF, BLUE = "#1baf7a", "#d64545", "#eb6834", "#0b0b0b", "#52514e", "#fcfcfb", "#2a78d6"
L = json.loads((OUT / "levels_live.json").read_text())
G = json.loads((OUT / "gaps.json").read_text())
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(1, 3, figsize=(17.5, 6.2), gridspec_kw={"width_ratios": [1.15, 1.15, 0.9], "wspace": 0.55})
def gmap(a, sym, lo, hi, marks, title, w):
    K = pd.read_csv(OUT / f"strikes_{sym}.csv", index_col=0)["gex"] / 1e9
    P = pd.read_csv(OUT / f"profile_{sym}.csv")
    k = K[(K.index >= lo) & (K.index <= hi)]
    a.bar(k.index, k.to_numpy(), width=w, color=[GREEN if v > 0 else RED for v in k.to_numpy()], alpha=0.85)
    a2 = a.twinx(); a2.plot(P.price, P["total dealer GEX $bn"], color=INK, lw=1.6); a2.axhline(0, color=INK, lw=0.6, ls=":")
    a2.spines["top"].set_visible(False); a2.set_ylabel("total dealer gamma if price were here ($bn per 1%)")
    a.set_xlim(lo, hi)
    yl = a.get_ylim()
    for x, col, lab, fr in marks:
        a.axvline(x, color=col, lw=1.3, ls="-" if lab.startswith(("close", "flip")) else "--")
        a.text(x, yl[1] * fr, " " + lab, color=col, fontsize=8, va="top")
    a.set_xlabel(f"{sym} price"); a.set_ylabel("dealer gamma at strike ($bn per 1%)")
    a.set_title(title, loc="left", fontsize=9.5, color=INK)
s, t = L["SPY"], L["TSLA"]
gmap(ax[0], "SPY", 738, 806, [(s["spot"], ORANGE, f"close {s['spot']:.0f}", 0.98), (s["flip"], INK, f"flip {s['flip']:.0f}", 0.88), (745, RED, "put wall 745", 0.78),
                             (780, GREEN, "780 magnet", 0.68), (800, GREEN, "call wall 800", 0.58)],
     f"SPY for Tue: {s['spot']:.0f}, still {abs(s['spot vs flip %']):.1f}% BELOW the flip ({s['flip']:.0f})\ndealers short ${abs(s['total GEX $bn per 1%']):.1f}bn per 1% (was -13.9); pocket 744-760, put wall 745-750\n"
     f"Oct 30 (month-end) expiry holds {100 * s['gamma by expiry (top 5)']['2026-10-30']['share']:.0f}% of gamma", 0.8)
gmap(ax[1], "TSLA", 355, 430, [(t["spot"], ORANGE, f"close {t['spot']:.0f}", 0.98), (t["flip"], INK, f"flip {t['flip']:.0f}", 0.88), (372.22, RED, "gap fill 372", 0.78),
                              (400, GREEN, "call wall 400", 0.68)],
     f"TSLA for Tue: {t['spot']:.0f}, {t['spot vs flip %']:.1f}% ABOVE the flip ({t['flip']:.0f}): dealers LONG gamma\nbiggest strike 400 = call wall (38k calls): magnet and lid\nno short-gamma pocket above 365; "
     f"Oct 30 holds {100 * t['gamma by expiry (top 5)']['2026-10-30']['share']:.0f}% of gamma", 2.0)
c = ax[2]
labs = ["all up-gaps\n>=2% (228)", "breakaway\n(160)", "inside\nrange (68)", "unfilled\nday 1 (74)"]
same = [G["base: fill same day"], G["S2 breakaway (open > prior high)"]["fill same day yes / no"][0], G["S2 breakaway (open > prior high)"]["fill same day yes / no"][1], np.nan]
five = [G["base: fill within 5 sessions"], G["S2 breakaway (open > prior high)"]["fill within 5 yes / no"][0], G["S2 breakaway (open > prior high)"]["fill within 5 yes / no"][1], 0.39]
x = np.arange(4); w = 0.38
c.bar(x - w / 2, 100 * np.nan_to_num(same), w, color=MUTED, label="filled the same day")
c.bar(x + w / 2, 100 * np.array(five), w, color=BLUE, label="filled within 5 sessions")
for xi, v in zip(x + w / 2, five):
    c.text(xi, 100 * v + 1.5, f"{100 * v:.0f}%", ha="center", fontsize=9, color=INK)
c.set_xticks(x, labs, fontsize=8)
c.set_ylim(0, 85); c.set_ylabel("share of gaps filled, %")
c.legend(loc="upper left", frameon=False, fontsize=8)
c.set_title("TSLA gaps since 2020: breakaway gaps\nfill less (55% vs 69%, p 0.04). Today: breakaway,\nabove the 50-day, unfilled day 1 -> ~39% odds", loc="left", fontsize=9.5, color=INK)
fig.savefig(OUT / "live_read_1027.png", dpi=140, bbox_inches="tight", facecolor=SURF)
