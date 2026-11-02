"""Anatomy of a TSLA top: event-time medians around 16 mechanical tops -> out/breaking_point.png"""
import json
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

O = Path(__file__).resolve().parent / "out"; R = json.load(open(O / "results.json")); D = pd.read_csv(O / "daily.csv", index_col=0, parse_dates=True)
BG, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"; BLUE, ORG, RED = "#2a78d6", "#eb6834", "#d03b3b"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10.2, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": GRID,
                     "xtick.color": INK2, "ytick.color": INK2})
tops = [pd.Timestamp(t["date"]) for t in R["tops"]]; K = range(-20, 11)
def path(col, f=lambda s, i, k: s.iloc[i + k]):
    rows = []
    for t in tops:
        i = D.index.get_loc(t)
        if i - 20 < 0 or i + 10 >= len(D): continue
        rows.append([f(D[col], i, k) for k in K])
    a = np.array(rows, dtype=float); return np.nanmedian(a, axis=0), np.nanpercentile(a, 25, axis=0), np.nanpercentile(a, 75, axis=0)
D["px"] = 100 * np.log(D.close)
D["iv"] = 100 * D.ATM_IV
D["aggr"] = 100 * D.F4_buy_aggr_change
D["share"] = 100 * D.F2_call_share5
D["skew"] = 100 * D.F3_skew_pct
D["coig"] = 100 * D.F1_callOI_growth5.clip(-0.5, 0.5)
panels = [("Price (% from the top)", "px", lambda s, i, k: s.iloc[i + k] - s.iloc[i]), ("ATM implied vol (vol pts vs top day)", "iv", lambda s, i, k: s.iloc[i + k] - s.iloc[i]),
          ("Put skew percentile (low = no one hedging)", "skew", None), ("Stock buying: last 5d minus prior 10d (%)", "aggr", None),
          ("Call share of option volume (%)", "share", None), ("New call OI, 5-day growth (%)", "coig", None)]
fig = plt.figure(figsize=(15.5, 9.6), facecolor=BG)
gs = fig.add_gridspec(2, 4, width_ratios=[1, 1, 1, 1.05], hspace=0.42, wspace=0.32, left=0.05, right=0.985, top=0.85, bottom=0.08)
fig.text(0.05, 0.955, "Anatomy of a TSLA top: fear vanishes and implied vol rises with price; after the break, implied vol collapses", fontsize=15.5, weight="bold", color=INK)
fig.text(0.05, 0.915, "Median (line) and middle half (band) around 16 mechanical tops, 2020-26 (peaks after +30% legs, 15% reversal). Day 0 = the top.\n"
         "No single gauge separated tops from strong-rally days that kept going (all p ≥ 0.10): these are the shapes, not a trigger.", fontsize=10, color=INK2, va="top")
for j, (title, col, f) in enumerate(panels):
    ax = fig.add_subplot(gs[j // 3, j % 3]); ax.set_facecolor(BG)
    med, lo, hi = path(col, f) if f else path(col)
    ax.fill_between(list(K), lo, hi, color=BLUE, alpha=0.15, lw=0); ax.plot(list(K), med, color=BLUE, lw=2.2)
    ax.axvline(0, color=RED, lw=1.2, ls="--"); ax.yaxis.grid(True, color=GRID); ax.set_title(title, loc="left", fontsize=10.6, weight="bold", color=INK)
    ax.set_xlabel("sessions from the top", fontsize=8.8)
ax = fig.add_subplot(gs[:, 3]); ax.axis("off")
c = R
txt = ("The sequence (medians, 16 tops):\n\n"
       "~9 days before: stock buying peaks\n~5-7 days before: new call buying and\n  call share peak; put skew bottoms\n  (almost no one hedging)\n"
       "last days: price still rising on fading\n  buying; implied vol rising with price\n  (calls bid: +3.5 pts vs +1.2 on days\n  that kept going)\n"
       "day 0: the top, often near the call wall\n  with dealers long gamma; 6 of 16 tops\n  ≤ 4 sessions before monthly opex\n\n"
       "AFTER, the options drop:\n• implied vol −6.3 pts in 10 sessions\n• call share falls, but call OI still\n  rises (+6.9%): dip-buying with calls\n• TSLA −11% median in 10 sessions\n\n"
       "Caveats: buying is estimated from price\nchanges, so part of its fade is the price\nslowing. Vs strong days that kept going,\nno gauge passed (all p ≥ 0.10).\n\n"
       "Now (Oct 30): skew 88th pct, buying\nrising, Nov opex 15 sessions away.\nOnly top-like feature: price at the 400\ncall wall. Not a breaking-point setup.")
ax.text(0.0, 0.99, txt, fontsize=9.6, color=INK, va="top", transform=ax.transAxes, linespacing=1.3)
fig.savefig(O / "breaking_point.png", dpi=108, facecolor=BG); print("ok")
