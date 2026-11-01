"""Forecast card: SPY fan to Dec 31 (B-all), gamma levels, volatility calendar, class table -> out/forecast.png"""
import json
import sys
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

O = Path(__file__).resolve().parent / "out"; R = json.load(open(O / "forecast.json"))
BG, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"; BLUE, ORG = "#2a78d6", "#eb6834"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10.5, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": GRID,
                     "xtick.color": INK2, "ytick.color": INK2})
m = pd.read_csv(sys.argv[1], index_col=0, parse_dates=True).c.loc["2026-09-01":]
cal = pd.bdate_range("2026-10-30", "2026-12-31"); cal = cal[~cal.isin(pd.to_datetime(["2026-11-26", "2026-12-25"]))]
fan = R["_fan"]; L = len(fan["k"]); x = cal[:L]
fig = plt.figure(figsize=(15.5, 9.6), facecolor=BG)
gs = fig.add_gridspec(1, 2, width_ratios=[2.15, 1], wspace=0.05, left=0.05, right=0.99, top=0.83, bottom=0.22)
fig.text(0.05, 0.95, "SPY to year-end: odds favour higher, but the 13-week July analog has no forecasting power", fontsize=16.5, weight="bold", color=INK)
fig.text(0.05, 0.91, "Forecast = what the S&P did from the end of October to year-end in every year since 1950 (76 years), scaled to today's volatility. "
         "Scored on Nov 13, Nov 30, Dec 31.\nThe July→August path (dashed) is shown for curiosity only: across 900+ months, 'what came 3 months earlier' predicts nothing (corr +0.05, p 0.13).",
         fontsize=10.3, color=INK2, va="top")
ax = fig.add_subplot(gs[0, 0]); ax.set_facecolor(BG)
q = {k: np.array(v) for k, v in fan["q"].items()}
ax.fill_between(x, q["0.1"], q["0.9"], color=BLUE, alpha=0.12, lw=0); ax.fill_between(x, q["0.25"], q["0.75"], color=BLUE, alpha=0.22, lw=0)
ax.plot(x, q["0.5"], color=BLUE, lw=2.4); ax.plot(m.index, m.to_numpy(), color=INK, lw=1.8)
an = np.array(R["_analog"])[:L]; ax.plot(x, an, color=ORG, lw=1.6, ls="--")
ax.text(pd.Timestamp("2026-10-08"), 792, "dashed: July→Aug analog\n(no predictive value)", color=ORG, fontsize=9, ha="left")
for lv, lab in ((800, "call wall 800"), (774.06, "gamma flip 774"), (750, "put wall 750 (not a floor in our tests)"), (740, "deepest pocket ~740")):
    ax.axhline(lv, color=INK2, lw=0.8, ls=":"); ax.text(pd.Timestamp("2026-09-02"), lv + 1.2, lab, color=INK2, fontsize=8.8)
B = R["B-all"]
for d, key in ((pd.Timestamp("2026-11-13"), "Nov 13 (10 sessions)"), (pd.Timestamp("2026-11-30"), "Nov 30"), (pd.Timestamp("2026-12-31"), "Dec 31")):
    v = B[key]["SPY 10/25/50/75/90"]; xx = d if d in x else x[-1]
    ax.plot([xx, xx], [v[0], v[4]], color=BLUE, lw=1); ax.plot(xx, v[2], "o", color=BLUE, ms=7, mec=BG, mew=1.5)
    ax.text(xx, v[4] + 3, f"{d.strftime('%b %d')}\nmedian {v[2]:.0f}\nP(up) {100 * B[key]['P(up)']:.0f}%", ha="center", fontsize=9, color=INK)
ax.set_ylim(722, 838); ax.yaxis.grid(True, color=GRID); ax.set_ylabel("SPY")
ax.set_xlim(pd.Timestamp("2026-09-01"), pd.Timestamp("2027-01-04"))
ax.text(pd.Timestamp("2026-10-31"), 726, "  dark band 25-75%, light 10-90%", color=INK2, fontsize=8.8)
# calendar strip
pos = ax.get_position(); cx = fig.add_axes([pos.x0, 0.02, pos.width, 0.12]); cx.set_xlim(ax.get_xlim()); cx.set_ylim(0, 1); cx.axis("off")
evs = [("2026-11-03", "Election\n(Tue)"), ("2026-11-06", "Jobs"), ("2026-11-12", "CPI\n~Nov 10-13"), ("2026-11-18", "VIX exp +\nNVDA ~est."), ("2026-11-20", "Nov opex"),
       ("2026-11-26", "Thanks-\ngiving"), ("2026-12-04", "Jobs"), ("2026-12-09", "FOMC\nDec 8-9"), ("2026-12-16", "VIX exp"), ("2026-12-18", "Quarterly\nopex (big)"), ("2026-12-31", "Year-end")]
for i, (d, t) in enumerate(evs):
    dd = pd.Timestamp(d); cx.plot([dd, dd], [0.75, 1.0], color=INK2, lw=1)
    cx.text(dd, 0.7 if i % 2 == 0 else 0.33, t, ha="center", va="top", fontsize=8.4, color=INK)
cx.text(pd.Timestamp("2026-09-02"), 0.6, "When moves are likely\n(scheduled; not a direction)", fontsize=9.5, color=INK2, va="center", weight="bold")
# side panel
sx = fig.add_subplot(gs[0, 1]); sx.axis("off")
sx.set_title("Odds SPY is above 755.69 (Oct 30 close)", loc="left", fontsize=12, weight="bold", color=INK)
cls = [("All years (76)", R["B-all"]), ("Midterm years (19)", R["B-midterm"]), ("Pullback years (30)", R["B-pullback (Oct close 2-8% below 52w high)"])]
sx.text(0.0, 0.93, "", transform=sx.transAxes)
hdr = ["", "Nov 13", "Nov 30", "Dec 31"]
for j, h in enumerate(hdr): sx.text([0.0, 0.5, 0.68, 0.86][j], 0.92, h, fontsize=10, weight="bold", color=INK2, transform=sx.transAxes)
for i, (lab, C) in enumerate(cls):
    y = 0.85 - i * 0.07
    sx.text(0.0, y, lab, fontsize=10, color=INK, transform=sx.transAxes, weight="bold" if i == 0 else "normal")
    for j, k in enumerate(("Nov 13 (10 sessions)", "Nov 30", "Dec 31")):
        sx.text([0.5, 0.68, 0.86][j], y, f"{100 * C[k]['P(up)']:.0f}%", fontsize=10.5, color=INK, transform=sx.transAxes)
d = R["B-all"]["Dec 31"]["SPY 10/25/50/75/90"]
txt = (f"Dec 31, all years: median {d[2]:.0f}\n   middle half {d[1]:.0f}-{d[3]:.0f}, 8 in 10 years {d[0]:.0f}-{d[4]:.0f}\n\n"
       "Signals already firing (earlier studies):\n"
       "• R4 (Oct 30): 70-74% odds of a 3.5%+ up-leg\n   within ~4 weeks (scored ~Nov 27)\n"
       "• Moves made below the flip fade ~18%\n   in 10 sessions (forced-flow law)\n"
       "• Election VIX premium: fit −3.8 pts\n   in the 5 sessions after Nov 3\n\n"
       "Warning: VIX 19.4 implies wider swings than\nthese bands (realized vol 11.5% was used):\n"
       "±1σ to Dec 31 ≈ ±7.9% (≈ 696-815).\n\n"
       "Week 1 map: below flip 774 = short gamma,\nmoves run; reclaiming 774 calms it;\n740 is the air pocket under 750.")
sx.text(0.0, 0.6, txt, fontsize=9.9, color=INK, va="top", transform=sx.transAxes, linespacing=1.35)
fig.savefig(O / "forecast.png", dpi=110, facecolor=BG); print("ok")
