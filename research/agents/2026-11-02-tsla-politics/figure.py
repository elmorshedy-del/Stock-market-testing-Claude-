"""Figure for the TSLA politics study. Usage: python figure.py -> out/tsla_politics.png"""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent; R = json.load(open(HERE / "out" / "results.json"))
BLUE, ORG, BG, INK, INK2, GRID, GRAY = "#2a78d6", "#eb6834", "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#a9a8a3"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False})
fig = plt.figure(figsize=(17, 11.2), facecolor=BG)
gs = fig.add_gridspec(2, 3, height_ratios=[1, 1], width_ratios=[1, 1, 0.9], hspace=0.42, wspace=0.45, left=0.17, right=0.97, top=0.86, bottom=0.06)
fig.text(0.02, 0.955, "TSLA tracks Musk's Texas Senate bet a little; his standing with the White House moves it far more", fontsize=19, weight="bold", color=INK)
fig.text(0.02, 0.905, "TSLA's own daily move (net of 1.56 × QQQ) vs the daily change in each Republican's Polymarket odds at 16:00 ET, Aug 10 → Oct 30 2026 (59 sessions).\n"
         "5-day block bootstrap, Holm across 8 markets. 2024 row = the same test on P(Trump), Aug 1 → Nov 4 2024, as a calibration.", fontsize=11, color=INK2)

# A: forest
ax = fig.add_subplot(gs[0, 0:2]); ax.set_facecolor(BG)
P = R["P1-P3 2026 (Aug 10 -> Oct 30)"]; rows = list(P.items()); P4 = R["P4 2024 calibration (Aug 1 -> Nov 4 2024)"]
rows.append(("2024 check: Trump (president)", P4))
for i, (k, v) in enumerate(rows[::-1]):
    lo, hi = v["95% CI %"]; b = v["per +10 pts %"]; h = v.get("Holm", None)
    col = ORG if (h is not None and h < 0.05) else (BLUE if "Paxton" in k else GRAY if "2024" not in k else INK2)
    ax.plot([lo, hi], [i, i], color=col, lw=2.4, solid_capstyle="round"); ax.plot(b, i, "o", color=col, ms=8)
    lab = f"{b:+.1f}%  p {v['p']:.3f}" + (f" (Holm {h:.2f})" if h is not None else "  (Nov 6: +10.3%)")
    ax.text(14.5, i, lab, va="center", fontsize=9.4, color=INK2)
ax.set_yticks(range(len(rows))); ax.set_yticklabels([k.replace(" [P1]", "  (primary)") for k, _ in rows[::-1]], fontsize=10.2)
ax.axvline(0, color=INK2, lw=1); ax.set_xlim(-23, 29); ax.set_xticks(range(-20, 15, 5)); ax.xaxis.grid(True, color=GRID)
ax.set_xlabel("TSLA's own move per +10 pts of the Republican's odds, % (dot = estimate, line = 95% range)")
ax.set_title("A. Which races TSLA's own moves track", loc="left", fontsize=13.5, weight="bold", color=INK)
ax.set_ylim(-0.6, 9.1); ax.text(-22.5, 8.65, "orange = passes Holm (opposite to 'red is better')   blue = primary test", fontsize=9.2, color=INK2)

# D: options
ax = fig.add_subplot(gs[0, 2]); ax.set_facecolor(BG)
o24 = R["P5 options 2024 (Fri Nov 1 close; window has FOMC Nov 7)"]; o26 = R["P5 options 2026 like-for-like (Fri Oct 30 close; window has AAPL reaction, payrolls)"]
ax.bar([0, 1], [o24["excess, in normal days"], o26["excess, in normal days"]], color=[INK2, BLUE], width=0.55); ax.yaxis.grid(True, color=GRID); ax.set_axisbelow(True)
for x, o in [(0, o24), (1, o26)]: ax.text(x, o["excess, in normal days"] + 0.08, f"{o['excess, in normal days']:.1f} extra days\n(+{o['excess move-equivalent %']:.1f}% move)", ha="center", fontsize=9.8, color=INK)
ax.set_xticks([0, 1]); ax.set_xticklabels(["2024 (Trump)\nFri Nov 1 → Nov 8", "2026 (midterms)\nFri Oct 30 → Nov 6"], fontsize=9.8); ax.set_ylim(0, 4.3)
ax.set_ylabel("extra normal days priced")
ax.set_title("D. TSLA options price less now", loc="left", fontsize=13.5, weight="bold", color=INK)
ax.text(0.5, 3.75, "2024 priced ~6% total for the vote;\nNov 6 delivered +14.8%", fontsize=9.4, color=INK2, ha="center")

# B: attribution
ax = fig.add_subplot(gs[1, 0]); ax.set_facecolor(BG)
it = [("TSLA's own move\nAug 10 → Oct 30", R["TSLA cumulative residual Aug 10 -> Oct 30 2026 %"], None, INK2)]
for k, lab in [("Texas Senate: Paxton (R) [P1]", "from Paxton's odds\n52% → 29%"), ("House: Republicans", "from R House odds\n14% → 7%"), ("Texas governor: Abbott (R)", "from Abbott's odds\n87% → 62%")]:
    a = P[k]["attributed TSLA move from the total odds change %"]; it.append((lab, a[0], (a[1], a[2]), BLUE if "Paxton" in k else ORG if "Abbott" in k else GRAY))
for i, (lab, v, ci, col) in enumerate(it[::-1]):
    ax.barh(i, v, color=col, height=0.55)
    if ci: ax.plot(ci, [i, i], color=INK, lw=1.2)
    ax.text(v + (1 if v >= 0 else -1), i + 0.3, f"{v:+.1f}%", fontsize=10, ha="left" if v >= 0 else "right", color=INK)
ax.set_yticks(range(len(it))); ax.set_yticklabels([x[0] for x in it[::-1]], fontsize=9.6); ax.axvline(0, color=INK2, lw=1); ax.xaxis.grid(True, color=GRID); ax.set_xlim(-19, 33)
ax.set_xlabel("% (black line = 95% range)")
ax.set_title("B. Politics explains a sliver of the rally", loc="left", fontsize=13.5, weight="bold", color=INK)

# C: z strip
ax = fig.add_subplot(gs[1, 1]); ax.set_facecolor(BG)
zs = []
for k, v in P.items():
    for d, (dp, z) in v["TSLA residual z on the 3 biggest odds days"].items(): zs.append(z)
ax.scatter(zs, np.random.default_rng(1).uniform(-0.15, 0.15, len(zs)), color=GRAY, s=30, zorder=3)
ev = R["P6 Musk-White House days"]; names = {"2024-11-06 Trump wins": "Trump wins\nNov 6 2024", "2025-06-05 Trump-Musk feud public": "Trump–Musk feud\nJun 5 2025", "2025-07-07 America Party (first session)": "'America Party'\nJul 7 2025"}
for j, (k, v) in enumerate(ev.items()):
    ax.scatter(v["z"], 1, color=ORG, s=70, zorder=3); ax.text(v["z"], 1.18 + 0.22 * (j % 2), f"{names[k]}\n{v['residual %']:+.1f}%", ha="center", fontsize=8.8, color=INK)
ax.set_yticks([0, 1]); ax.set_yticklabels(["biggest daily odds\nswings, 8 races (24)", "Musk–White\nHouse days"], fontsize=9.6); ax.set_ylim(-0.5, 2.0); ax.set_xlim(-5.5, 5.5)
ax.axvline(0, color=INK2, lw=1); ax.xaxis.grid(True, color=GRID); ax.set_xlabel("TSLA's own move that day, in typical-day units (z)")
ax.set_title("C. What actually moves TSLA", loc="left", fontsize=13.5, weight="bold", color=INK)

# E: business map
ax = fig.add_subplot(gs[1, 2]); ax.axis("off")
ax.set_title("E. What is at stake for Tesla", loc="left", fontsize=13.5, weight="bold", color=INK)
lines = [("Already lost (Trump's veto holds to 2029):", True),
         ("• \\$7,500 EV credit: ended Sep 30 2025", False), ("• regulatory credits: \\$113M in Q3 vs \\$417M (−73%)", False),
         ("Still at stake:", True),
         ("• federal AV law (exemption cap 2,500 → ~90-100k;", False), ("   Cybercab volume): stuck since Feb", False),
         ("• D House (≈94%): probes of Musk, DOGE, contracts", False),
         ("• Texas Senate: Musk's ~\\$168M bet on Paxton (25%)", False),
         ("• Texas gov. Abbott (62%): SpaceX grants,", False), ("   Terafab tax breaks, robotaxi rules", False),
         ("• robotaxi states: NV D 78%, AZ D 94%, CA D 98%", False)]
y = 0.97
for t, b in lines: ax.text(0.0, y, t, fontsize=9.6, color=INK if b else INK2, weight="bold" if b else "normal", transform=ax.transAxes, va="top"); y -= 0.085
fig.savefig(HERE / "out" / "tsla_politics.png", dpi=110, facecolor=BG); print("ok")
