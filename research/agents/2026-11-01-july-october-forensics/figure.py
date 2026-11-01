"""Figure: July vs October 2026 aligned 13 weeks apart, with the shared calendar and the tests.
Usage: python figure.py <SPY 1m parquet> -> out/forensics.png"""
import json
import sys
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

O = Path(__file__).resolve().parent / "out"; R = json.load(open(O / "forensics.json"))
BG, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"; CJ, CO = "#2a78d6", "#eb6834"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10.5, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": GRID,
                     "xtick.color": INK2, "ytick.color": INK2})
m = pd.read_parquet(sys.argv[1], columns=["close"]); m.index = m.index.tz_convert("America/New_York")
m = m[(m.index.time >= pd.Timestamp("09:30").time()) & (m.index.time < pd.Timestamp("16:00").time())]
fig = plt.figure(figsize=(15.5, 10.6), facecolor=BG)
gs = fig.add_gridspec(2, 2, height_ratios=[1.25, 1], width_ratios=[1.35, 1], hspace=0.38, wspace=0.12, left=0.055, right=0.985, top=0.835, bottom=0.05)
fig.text(0.055, 0.955, "July and October 2026: the same calendar 13 weeks apart, not the same pattern", fontsize=17, weight="bold", color=INK)
fig.text(0.055, 0.92, "Every matching day is a scheduled event on the same weekday (opex, VIX expiry plus TSLA/IBM earnings). Both selloffs started from the same state (VIX ~15 at a high,\n"
         "then below the gamma flip, money rotating out of megacap tech). The endings split on the earnings news: July's big-tech reports beat, October's missed.",
         fontsize=10.5, color=INK2, va="top")
ax = fig.add_subplot(gs[0, :]); ax.set_facecolor(BG)
for lab, a, days, col in (("July (Jul 13-31)", "2026-07-10", pd.bdate_range("2026-07-13", "2026-07-31"), CJ), ("October (Oct 12-30)", "2026-10-09", pd.bdate_range("2026-10-12", "2026-10-30"), CO)):
    base = m.loc[a].close.iloc[-1]; xs, ys = [0], [0.0]
    for i, d in enumerate(days):
        x = m.loc[str(d.date())].close.resample("30min").last().dropna()
        xs += list(i + 0.08 + 0.84 * np.arange(len(x)) / (len(x) - 1)); ys += list(100 * (x.to_numpy() / base - 1))
    ax.plot(xs, ys, color=col, lw=2.3, label=lab, zorder=3)
    ax.text(xs[-1] + 0.1, ys[-1], f"{lab.split(' ')[0]} {ys[-1]:+.1f}%", color=col, fontsize=10.5, weight="bold", va="center")
ev = {5: ("monthly\nopex", "both −1.0/−1.1%"), 8: ("VIX expiry +\nTSLA/IBM\nreport night", ""), 9: ("gap-down\nThursday", "both −1.2%"),
      13: ("FOMC +\nMSFT/META", "Jul −1.5%\nOct +0.3%"), 14: ("AAPL/\nAMZN", ""), 15: ("month-\nend Fri", "Jul +0.7%\nOct −1.8%")}
for k, (t, sub) in ev.items():
    ax.axvspan(k - 1, k, color="#f1f0ec", zorder=0)
    ax.text(k - 0.5, 1.25, t, ha="center", va="bottom", fontsize=8.8, color=INK)
    if sub: ax.text(k - 0.5, -4.15, sub, ha="center", va="bottom", fontsize=8.6, color=INK2)
dl = [f"{a}\n{b}" for a, b in zip(pd.bdate_range("2026-07-13", "2026-07-31").strftime("%a %d"), pd.bdate_range("2026-10-12", "2026-10-30").strftime("%d"))]
ax.set_xticks(np.arange(15) + 0.5, [f"{x.split(chr(10))[0]}\nOct {x.split(chr(10))[1]}" for x in dl], fontsize=8.3)
ax.set_xlim(-0.2, 16.4); ax.set_ylim(-4.3, 2.9); ax.axhline(0, color=INK2, lw=0.8); ax.yaxis.grid(True, color=GRID)
ax.set_ylabel("SPY % from the prior Friday close (30-min)"); ax.text(-0.1, -3.4, "top tick row = July date (Jul 13…31), bottom = October", fontsize=8.5, color=INK2)
ax.set_title("A. Aligned by weekday, exactly 13 weeks apart (shaded = scheduled-event days)", loc="left", fontsize=12.5, weight="bold", color=INK, pad=8)
# B pieces
ax = fig.add_subplot(gs[1, 0]); ax.axis("off")
P = R["pieces"]; J, Oc = P["July"], P["October"]
rows = [("✓", "Same calendar, same weekdays", "opex Fri, VIX-expiry Wed + TSLA/IBM night, FOMC Wed, Fri month-end"),
        ("✓", "Same start", f"VIX {J['VIX start / max / end'][0]:.0f} at a fresh high after an early-month rally (both)"),
        ("✓", "Same amplifier: short gamma", f"July {100 * J['share of days spot below flip']:.0f}% of days below flip; Oct below flip from Oct 14"),
        ("✓", "Same fear peak", f"VIX max {J['VIX start / max / end'][1]:.1f} vs {Oc['VIX start / max / end'][1]:.1f}"),
        ("✓", "Same rotation out of tech", f"QQQ−IWM {J['QQQ - IWM %']:+.1f} vs {Oc['QQQ - IWM %']:+.1f} pts (Oct 2x stronger)"),
        ("✗", "Different news at the end", "GOOGL EPS surprise +216% vs −28%; AMZN +2.7% vs −6.0%"),
        ("✗", "Different FOMC reaction", "Jul 29 −1.5% vs Oct 28 +0.3%"),
        ("–", "Not rates, not the dollar", f"10y {J['10y yield change (bp)']:+.0f} / {Oc['10y yield change (bp)']:+.0f} bp; dollar {J['dollar index %']:+.1f} / {Oc['dollar index %']:+.1f}%")]
ax.set_title("B. The pieces: what matched and what did not", loc="left", fontsize=12.5, weight="bold", color=INK)
col = {"✓": "#0ca30c", "✗": "#d03b3b", "–": INK2}
for i, (mk, a, b) in enumerate(rows):
    y = 0.9 - i * 0.118
    ax.text(0.0, y, mk, color=col[mk], fontsize=13, weight="bold", va="center", transform=ax.transAxes)
    ax.text(0.04, y, a, color=INK, fontsize=10.3, weight="bold", va="center", transform=ax.transAxes)
    ax.text(0.40, y, b, color=INK2, fontsize=9.6, va="center", transform=ax.transAxes)
# C verdict
ax = fig.add_subplot(gs[1, 1]); ax.axis("off")
f1 = R["F1"]; a2 = R["F2a post-opex sessions +1..+10 minus other sessions (z)"]; b2 = R["F2b day after VIX expiry minus other sessions (z, 2004-26)"]
vr = R["exploratory: mean |z| on scheduled days / all days (2004-26)"]
ax.set_title("C. Is it more than coincidence? (tests since 1993)", loc="left", fontsize=12.5, weight="bold", color=INK)
txt = (f"Whole 3 weeks, day by day: correlation {f1['corr July vs Oct, 15 aligned sessions']:+.2f}\n"
       f"   → no more alike than two random windows ({100 * f1['percentile vs all 15-session windows 1993-2026H1']:.0f}th pct).\n"
       f"   July is only #{f1['July rank among the 24']} of the last 24 months for likeness.\n"
       f"First 9 days (to the Thursday gap): {f1['post hoc: first 9 sessions corr']:+.2f} ({100 * f1['post hoc: 9-session percentile']:.0f}th pct).\n\n"
       f"Does the calendar itself push prices down?\n"
       f"   10 days after opex: no ({a2['estimate']:+.3f}σ, p {a2['p']:.2f}).\n"
       f"   Day after VIX expiry: slightly ({b2['estimate']:+.2f}σ ≈ −0.09%, p {b2['p']:.2f},\n   misses the multiple-test bar).\n"
       f"   Bigger moves on those days? no (opex {vr['opex'][0]:.2f}x, VIX-exp+1 {vr['after_vx'][0]:.2f}x).\n\n"
       "Reading: the calendar decided WHEN the news hit;\nthe state (short gamma, rotation) decided HOW HARD;\nthe earnings decided WHICH WAY at the end.")
ax.text(0.0, 0.93, txt, fontsize=10.2, color=INK, va="top", transform=ax.transAxes, linespacing=1.35)
fig.savefig(O / "forensics.png", dpi=110, facecolor=BG); print("ok")
