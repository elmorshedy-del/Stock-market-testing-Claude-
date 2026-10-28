"""out/flip_expiry_openfade.png: the flip through this week's expiry (SPY, TSLA) and the open-fade test."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent; OUT = HERE / "out"
EC = json.loads((HERE.parent / "2026-10-27-flip-wicks" / "out" / "expiry_cycle.json").read_text())
F = json.loads((OUT / "fade.json").read_text())
GREEN, RED, INK, MUTED, SURF, BLUE, ORANGE, GREY = "#1baf7a", "#d64545", "#0b0b0b", "#52514e", "#fcfcfb", "#2a78d6", "#eb6834", "#c9c8c3"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(2, 2, figsize=(16, 10.5), gridspec_kw={"hspace": 0.55, "wspace": 0.3})
for i, (sym, S) in enumerate((("SPY", 772.35), ("TSLA", 404.46))):
    a = ax[0, i]; p = EC[f"(1) {sym} this week, positions fixed"]; labs = list(p)
    x = np.arange(len(labs)); fl = [p[k]["flip"] for k in labs]; tg = [p[k]["total gamma at today's close $bn/1%"] for k in labs]
    a.plot(x, fl, "o-", color=ORANGE, lw=2, label="flip (positions fixed, time running)")
    a.axhline(S, color=BLUE, lw=1, ls="--"); a.text(len(x) - 1, S, f" Wed close {S}", color=BLUE, fontsize=8, va="bottom", ha="right")
    a.set_xticks(x, [l.replace(" (Oct 30 gone)", "\n(Oct 30 gone)") for l in labs], fontsize=7.5); a.set_ylabel(f"{sym} flip")
    b = a.twinx(); b.bar(x, tg, color=[GREEN if v > 0 else RED for v in tg], alpha=0.35, width=0.5, label="total dealer gamma at Wed's close price"); b.axhline(0, color=MUTED, lw=0.6)
    b.set_ylabel("$bn per 1% at Wed's close"); b.spines["top"].set_visible(False)
    h1, l1 = a.get_legend_handles_labels(); h2, l2 = b.get_legend_handles_labels(); a.legend(h1 + h2, l1 + l2, frameon=False, fontsize=7.5, loc="upper left" if sym == "SPY" else "center left")
    sh = p[labs[0]]["Oct 30 share of |gamma|"]
    if sym == "SPY":
        a.set_title(f"SPY: the flip DRIFTS into Friday's expiry ({100*sh:.0f}% of gamma) and JUMPS after it.\nGamma at the price builds into Friday midday (+$0.8bn: stickier, pin-like), collapses at the bell,\n"
                    f"and on Monday the same price sits in SHORT gamma (-$0.8bn): the release. Flip 772.2 -> 773.6", loc="left", fontsize=9, color=INK)
    else:
        a.set_title(f"TSLA: Friday holds {100*sh:.0f}% of its gamma. Flip stays far below (~370);\nthe 400 magnet strengthens into Friday (+\\$0.15bn) and halves after it (+\\$0.07bn):\nless pull to 400 next week, more room to move (deep freed)", loc="left", fontsize=9, color=INK)
a = ax[1, 0]
pr = F["predictors"]; names = {"P1": "extended 2-day run\n(top fifth)", "P2": "dealers long gamma\n(own >= 70th pct)", "P3": "open at/above\nthe call wall", "P4": "big gap\n(top third)"}
x = np.arange(4); w = 0.38
on = [pr[k]["open->close % on / off"][0] for k in names]; off = [pr[k]["open->close % on / off"][1] for k in names]
a.bar(x - w / 2, on, w, color=ORANGE, label="predictor ON"); a.bar(x + w / 2, off, w, color=GREY, label="OFF")
for i, k in enumerate(names):
    a.text(i, max(on[i], off[i]) + 0.03, f"Holm p {pr[k]['Holm p']:.2f}\n({pr[k]['events on / off'][0]} on)", ha="center", fontsize=7.5)
a.axhline(0, color=INK, lw=0.8); a.set_xticks(x, list(names.values()), fontsize=8); a.set_ylabel("TSLA open -> close %, up-gap days")
a.legend(frameon=False, fontsize=8, loc="lower left"); a.set_ylim(-0.35, 0.45)
a.set_title(f"TEST (pre-registered): on {F['events (TSLA up-gaps >= 0.5%)']} TSLA up-gaps since 2011, NONE of the four mechanisms predicts\n"
            f"the fade. Base rates: closes below the open {100*F['base: mean open->close %, P(red), P(open = high)'][1]:.0f}%, the open is the day's high only "
            f"{100*F['base: mean open->close %, P(red), P(open = high)'][2]:.0f}%.\nAcross 83 stocks the extended-run fade was real in 2000-19 (-0.18 pts, p<0.001) and is gone since 2020", loc="left", fontsize=9, color=INK)
a = ax[1, 1]
o4 = F["O4 first hour (Nov 2023-Oct 2026)"]; ks = list(o4)
dd = [o4[k]["median drop open->first-hour low %"] for k in ks]; fr = [o4[k]["first-hour return %"] for k in ks]
x = np.arange(len(ks))
a.bar(x - w / 2, dd, w, color=RED, label="median drop from the open to the first-hour low")
a.bar(x + w / 2, fr, w, color=BLUE, label="mean first-hour return")
for i, k in enumerate(ks):
    a.text(i, min(dd[i], fr[i]) - 0.25, f"n {o4[k]['events']}", ha="center", fontsize=7.5)
a.axhline(0, color=INK, lw=0.8); a.set_xticks(x, [k.replace(" predictors on", " on") for k in ks]); a.set_ylabel("% from the open")
a.legend(frameon=False, fontsize=8, loc="upper right"); a.set_ylim(-2.8, 1.2)
a.set_title("First hour of TSLA up-gaps (Nov 2023 - Oct 2026): a ~1% dip after the open is NORMAL\n(median -1.1%, so it is not a signal by itself). With 3 of 4 on, like today: -2.1% and a red\nfirst hour, but only 25 events: a lead to re-test, not a rule", loc="left", fontsize=9, color=INK)
fig.savefig(OUT / "flip_expiry_openfade.png", dpi=140, bbox_inches="tight", facecolor=SURF)
