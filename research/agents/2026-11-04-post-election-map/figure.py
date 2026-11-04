"""ADHD map for Wed Nov 4: SPY gamma pocket with critical levels; TSLA levels mapped from SPY (2x on down days) + TSLA flip/freed. -> out/post_election_map.png"""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent; m = json.load(open(HERE / "out" / "map.json"))
BG, INK, INK2, GRID, GRAY, BLUE, ORANGE = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#a9a8a3", "#2a78d6", "#eb6834"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": GRAY, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2})
fig, ax = plt.subplots(1, 2, figsize=(14, 6.4), facecolor=BG, gridspec_kw={"width_ratios": [1.25, 1]})
for a in ax: a.set_facecolor(BG); a.grid(True, color=GRID, lw=0.8); a.spines[["top", "right"]].set_visible(False)
a = ax[0]; c = m["SPY curve"]; p = np.array(c["price"]); tot = np.array(c["total incl 0DTE"]); k = (p >= 715) & (p <= 775)
a.plot(tot[k], p[k], color=INK2, lw=2.2); a.fill_betweenx(p[k], tot[k], 0, where=tot[k] < 0, color=BLUE, alpha=0.12)
a.axvline(0, color=GRAY, lw=1)
lv = [(768.8, "769  FLIP: above here dealers damp moves (regime change)", INK2), (754.35, "754.4  Tue close", GRAY),
      (750, "750  TRIGGER: biggest put strike + triple bottom (748.8-750.4).\n         Losing it = 'almost breaking' scare", ORANGE),
      (745.9, "745.9  futures-implied open", BLUE), (740, "740  PUT WALL (moved down from 750)", ORANGE),
      (734.5, "734.5  POCKET TROUGH: max dealer selling (-$20bn per 1%)", BLUE), (729.5, "729-730  BIG FLOOR: 200-day 729.5 + July low 729.1;\n         pocket bottom, amplification fades below 725", ORANGE)]
for y, t, col in lv:
    a.axhline(y, color=col, lw=1.2, ls="--" if col != ORANGE else "-"); a.text(-21.5, y + 0.5, t, fontsize=8.6, color=col, va="bottom")
a.axhspan(725, 745, color=BLUE, alpha=0.07)
a.set_ylim(718, 774); a.set_xlim(-22, 2); a.set_xlabel("dealer total gamma, $bn per 1% move (negative = dealers amplify)"); a.set_ylabel("SPY")
a.set_title("SPY Wed map: open ~746 is already in the pocket's upper edge;\ncore pocket 725-745, trough 734.5, big floor 729-730", loc="left", fontweight="bold")
b = ax[1]
sp = [754.35, 750, 745.9, 740, 734.5, 730, 725]; ts = [398.5 * (1 + 2 * (s / 754.35 - 1)) for s in sp]
st = m["TSLA state at hypothetical Wed closes (Mon positions)"]
b.plot(sp, ts, color=ORANGE, lw=2, marker="o")
for s, t_ in zip(sp, ts): b.text(s, t_ + 1.2, f"{t_:.0f}", ha="center", fontsize=9)
b.axhline(376.8, color=INK2, lw=1.5); b.text(754.5, 376.2, "TSLA flip 376.8 (Mon positions)", fontsize=8.6, color=INK2, va="top", ha="left")
b.axhspan(366, 376.8, color=ORANGE, alpha=0.10); b.text(754.5, 367, "FULL SETUP zone: close < flip AND freed\n(freed at 380 = 4th pct, 375 = 6th pct)", fontsize=8.6, color=ORANGE, ha="left")
b.axhspan(376.8, 380.6, color=GRAY, alpha=0.15); b.text(754.5, 379.2, "practical trigger: freed + within 1% of flip", fontsize=8.6, color=INK2, ha="left")
b.invert_xaxis(); b.set_xlabel("SPY level"); b.set_ylabel("TSLA (2x SPY on S&P down days)")
odds = m["TSLA implied odds by Wed close (lognormal, from 391.64)"]
b.set_title(f"TSLA ~2x SPY down: SPY trough 734.5 = TSLA ~377 (its flip)\nP(TSLA closes <= 375 Wed) {odds['P(close <= 375) at IV / IV+10pts'][0]:.0%} implied, {odds['P(close <= 375) at IV / IV+10pts'][1]:.0%} if vol +10", loc="left", fontweight="bold")
fig.text(0.01, 0.01, "Positions = OI dated Nov 3 (Mon close); IVs = Tue Nov 3 closing chains; classic dealer convention. Tue positions publish ~6-7am ET: refresh before the open. TSLA mapping uses the proven 2x rule on S&P down days.", fontsize=8, color=INK2)
plt.tight_layout(rect=(0, 0.03, 1, 1)); plt.savefig(HERE / "out" / "post_election_map.png", dpi=150, facecolor=BG)
