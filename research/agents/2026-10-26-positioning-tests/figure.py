"""Positioning tests in one picture: out/positioning_tests.png"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parent / "out"
GREEN, RED, ORANGE, INK, MUTED, SURF, BLUE = "#1baf7a", "#d64545", "#eb6834", "#0b0b0b", "#52514e", "#fcfcfb", "#2a78d6"
P2 = json.loads((OUT / "p2.json").read_text()); P3 = json.loads((OUT / "p3.json").read_text()); P4 = json.loads((OUT / "p4.json").read_text())
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(2, 2, figsize=(16, 11.5), gridspec_kw={"hspace": 0.55, "wspace": 0.32})
a = ax[0, 0]
c = P2["cells 2011-2026"]
keys = ["GEX <0, corr rising", "GEX <0, corr not rising", "GEX >0, corr rising", "GEX >0, corr not rising"]
v = [c[k]["next 10d %"] for k in keys]
a.bar(range(4), v, color=[RED, GREEN, MUTED, MUTED], width=0.6)
for i, k in enumerate(keys):
    a.text(i, v[i] + (0.08 if v[i] >= 0 else -0.08), f"{v[i]:+.1f}%\n{c[k]['days']} days", ha="center", va="bottom" if v[i] >= 0 else "top", fontsize=8.5, color=INK)
a.axhline(0, color=INK, lw=0.8)
a.set_ylim(-1.7, 3.4)
a.set_xticks(range(4), ["dealers short gamma\n+ correlation RISING", "dealers short gamma\n+ correlation calm", "long gamma\n+ rising", "long gamma\n+ calm"], fontsize=8)
a.set_ylabel("S&P next 10 sessions, %")
a.set_title("P2 The letter's correlation rule HOLDS, but only in true short gamma\n"
            "(SqueezeMetrics GEX < 0): rising correlation turns the usual short-gamma\n"
            "bounce (+2.6%) into a drop (-0.8%). -3.4 pts, p < 0.001, 35 episodes.\n"
            "Same sign in 2011-19, 2020-22, 2023-26, but most of it is 2020-22.\n"
            "Today: SqueezeMetrics GEX +\\$4bn, so the rule is OFF", loc="left", fontsize=9, color=INK)
b = ax[0, 1]
labs, w_, wo = [], [], []
for sym in ("SPY", "QQQ"):
    r = P3[sym]
    for h in (5, 10, 20):
        x = r[f"next {h}d %: with / without / diff / p"]
        labs.append(f"{sym}\n{h}d"); w_.append(x[0]); wo.append(x[1])
xx = np.arange(len(labs)); ww = 0.38
b.bar(xx - ww / 2, w_, ww, color=GREEN, label="selloff days WITH a 40k+ put close")
b.bar(xx + ww / 2, wo, ww, color=MUTED, label="selloff days without")
b.set_xticks(xx, labs, fontsize=8)
b.set_ylabel("forward return, %")
b.legend(loc="upper left", frameon=False, fontsize=8)
b.set_title(f"P3 Big put closes during selloffs came near lows\n"
            f"(SPY {P3['SPY']['with a large put close (de-duplicated)']} events, QQQ {P3['QQQ']['with a large put close (de-duplicated)']}; e.g. Oct 27 2023, Apr 7 2025),\n"
            "but too few events to separate from noise (p 0.22-0.57).\n"
            "The letter's QQQ Oct 30 \\$700 puts: build confirmed (+65k OI),\n"
            "close only partly visible (-32k)", loc="left", fontsize=9, color=INK)
cc = ax[1, 0]
hb, ha_ = P4["P4b highs just below / just above a round level"][:2]
la, lb = P4["P4b lows just above / just below a round level"][:2]
cc.bar([0, 1], [100 * hb / (hb + ha_), 100 * ha_ / (hb + ha_)], color=[ORANGE, MUTED], width=0.6)
cc.bar([3, 4], [100 * la / (la + lb), 100 * lb / (la + lb)], color=[ORANGE, MUTED], width=0.6)
for x_, n_, tot in ((0, hb, hb + ha_), (1, ha_, hb + ha_), (3, la, la + lb), (4, lb, la + lb)):
    cc.text(x_, 100 * n_ / tot + 0.2, f"{100 * n_ / tot:.1f}%\n({n_:,})", ha="center", fontsize=8.5, color=INK)
cc.axhline(50, color=INK, lw=0.8, ls=":")
cc.set_ylim(44, 55)
cc.set_xticks([0, 1, 3, 4], ["day's HIGH just\nBELOW a round $", "day's high just\nabove it", "day's LOW just\nABOVE a round $", "day's low just\nbelow it"], fontsize=8)
cc.set_ylabel("share of days, % (50% = no clustering)")
cc.set_title("P4b Resting orders at round numbers are REAL (Osler):\n"
             "day highs stall just BELOW round levels (p < 1e-14), lows just ABOVE (p 5e-5).\n"
             "81 stocks + SPY. Monday: TSLA high \\$397.27, just under \\$400", loc="left", fontsize=9, color=INK)
d = ax[1, 1]
names = ["A crossed & closed above", "B crossed, closed back below", "C near miss (within 0.5%)"]
for i, (k, lab) in enumerate(zip(names, ["broke the 20-day high\nand held", "broke it, closed\nback below (stop run)", "came within 0.5%\nbut failed"])):
    for j, h in enumerate(("P4a next day (z units; coef, lo90, hi90, p)", "P4a next 5 days")):
        co, lo, hi, p = P4[h][k]
        x_ = i + (j - 0.5) * 0.3
        d.plot([lo, hi], [x_, x_], color=BLUE if j == 0 else INK, lw=2)
        d.scatter([co], [x_], color=BLUE if j == 0 else INK, s=40, zorder=3)
        d.text(hi + 0.005, x_, f"{'next day' if j == 0 else 'next 5d'} " + ("p < 0.01" if p < 0.01 else f"p {p:.2f}"), va="center", fontsize=7.5, color=MUTED)
d.axvline(0, color=INK, lw=0.8)
d.set_yticks(range(3), ["broke the 20-day high\nand held", "broke it, closed\nback below (stop run)", "came within 0.5%\nbut failed"], fontsize=8)
d.set_xlabel("next-day / next-5-day return beyond normal, in units of daily volatility")
d.set_title("P4a Breaking the 20-day high: no reliable follow-through over days\n"
            "(stop cascades play out intraday). Failed breaks bounce a little\n"
            "next day (p < 0.01, but tiny: 0.06 of a day's move)", loc="left", fontsize=9, color=INK)
fig.savefig(OUT / "positioning_tests.png", dpi=140, bbox_inches="tight", facecolor=SURF)
