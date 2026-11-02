"""ADHD figure: (a) breakout equity by asset, (b) gamma regime (H2) both SPY periods, (c) TSLA what worked, (d) ML overfit. -> out/orb_gamma.png"""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; O = HERE / "out"
BG, INK, INK2, GRID, GRAY, BLUE, ORANGE = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#a9a8a3", "#2a78d6", "#eb6834"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": GRAY, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "axes.titleweight": "bold", "axes.titlesize": 11})


def pnl(df, k):
    d = df[k + "_dir"].to_numpy(); return pd.Series(np.where(d > 0, df[k + "_L"].fillna(0), np.where(d < 0, df[k + "_S"].fillna(0), 0.0)), index=df.index), d


fig, ax = plt.subplots(2, 2, figsize=(13, 8.6), facecolor=BG)
for a in ax.flat: a.set_facecolor(BG); a.grid(True, color=GRID, lw=0.8); a.spines[["top", "right"]].set_visible(False)

# (a) cumulative bp, classic 5-min breakout held to the close
a = ax[0, 0]
sets = [("SPY2020", "SPY 2020-23", GRAY, "-", 8), ("SPY", "SPY 2024-26", INK2, "-", -4), ("QQQ", "QQQ 2024-26", BLUE, "-", 6), ("TSLA", "TSLA 2024-26", ORANGE, "-", 0), ("TSLA_d2", "TSLA, all complete days", ORANGE, ":", 0)]
for lab, nm, col, ls, dy in sets:
    p, _ = pnl(pd.read_parquet(O / f"days_{lab}.parquet"), "S1_5_close")
    x = np.arange(len(p)); a.plot(x, p.cumsum() / 100, color=col, ls=ls, lw=2 if "TSLA" in lab else 1.6, label=f"{nm}: {p.mean():+.1f} bp/day")
a.axhline(0, color=GRAY, lw=1)
a.legend(frameon=False, fontsize=8.5, loc="center right", bbox_to_anchor=(1.0, 0.38)); a.set_xlim(0, 1000); a.set_ylabel("cumulative return, % (1x, after costs)"); a.set_xlabel("trading days")
a.set_title("(a) 5-min opening-range breakout, held to the close:\nonly TSLA makes real money; SPY and QQQ are about flat", loc="left")

# (b) H2: gamma regime, SPY both periods
a = ax[0, 1]
h = {k: json.load(open(O / f"h1h2_{k}.json"))["H2 gamma regime (S0 5-min 10R)"]["primary: 09:35 price < flip_incl"] for k in ["SPY2020", "SPY"]}
lbl = ["2020-23", "2024-26"]; xb = np.arange(2)
a.bar(xb - 0.18, [h[k]["mean bp/day below"] for k in h], 0.36, color=ORANGE, label="SPY below its flip (dealers amplify)")
a.bar(xb + 0.18, [h[k]["mean bp/day above"] for k in h], 0.36, color=BLUE, label="SPY above its flip (dealers damp)")
for i, k in enumerate(h):
    a.text(i, min(h[k]["mean bp/day below"], h[k]["mean bp/day above"]) - 0.9, f"p = {h[k]['shift-null p (one-sided, below > above)']:.2f}\n(predicted below > above)", ha="center", va="top", fontsize=8.5, color=INK2)
a.axhline(0, color=GRAY, lw=1); a.set_xticks(xb, lbl); a.set_ylim(-7.5, 3); a.set_ylabel("ORB (5-min, 10R) mean bp/day")
a.legend(frameon=False, fontsize=8.5, loc="upper right")
a.set_title("(b) Our gamma idea failed: below the flip, SPY breakouts\ndo WORSE (whipsaw), not better", loc="left")

# (c) TSLA: what worked (all complete days, classic breakout)
a = ax[1, 0]
c = json.load(open(O / "tsla_conditions.json"))["TSLA_d2"]
items = [("Mon", c["weekday"]["0"]), ("Tue", c["weekday"]["1"]), ("Wed", c["weekday"]["2"]), ("Thu", c["weekday"]["3"]), ("Fri", c["weekday"]["4"]),
         ("", [np.nan, 0]), ("long", c["side"]["long"]), ("short", c["side"]["short"]), ("", [np.nan, 0]),
         ("low\nvol", c["rvol5 tercile"]["low"]), ("mid\nvol", c["rvol5 tercile"]["mid"]), ("high\nvol", c["rvol5 tercile"]["high"]), ("", [np.nan, 0]),
         ("auction\ngap", c["audit status"]["bad_D2"]), ("other", c["audit status"]["clean"])]
vals = [v[0] for _, v in items]; xs = np.arange(len(items))
a.bar(xs, vals, color=[ORANGE if (v == v and v > 25) else (GRAY if v == v and v < 5 else BLUE) for v in vals])
for x_, (nm, v) in zip(xs, items):
    if v[0] == v[0]: a.text(x_, v[0] + (1.5 if v[0] >= 0 else -1.5), f"{v[0]:+.0f}", ha="center", va="bottom" if v[0] >= 0 else "top", fontsize=8.5, color=INK)
a.set_xticks(xs, [n for n, _ in items], fontsize=7.8); a.axhline(0, color=GRAY, lw=1); a.set_ylabel("TSLA breakout, mean bp/day")
a.set_title("(c) TSLA: best on Mondays/Fridays, longs, heavy\nopening volume (vs 14-day) and auction-gap days (exploratory)", loc="left")

# (d) ML overfit
a = ax[1, 1]
ml = [("SPY", "S0_5_10R", "SPY"), ("TSLA", "S0_5_10R", "TSLA paper rule"), ("TSLA_d2", "S1_5_close", "TSLA breakout")]
for j, (lab, k, nm) in enumerate(ml):
    r = json.load(open(O / f"ml_{lab}_{k}.json"))["gradient boosting d3"]["AUC train/val/test"]
    a.bar(j * 4 + np.arange(3), r, color=[INK2, BLUE, ORANGE]); a.text(j * 4 + 1, 1.03, nm, ha="center", fontsize=9, color=INK)
a.axhline(0.5, color=GRAY, ls="--", lw=1); a.set_xlim(-0.6, 12.4); a.text(11.2, 0.51, "coin\nflip", fontsize=8.5, color=INK2, ha="left", va="bottom")
a.set_xticks([0, 1, 2, 4, 5, 6, 8, 9, 10], ["train", "val", "test"] * 3, fontsize=8.5); a.set_ylim(0.3, 1.1); a.set_ylabel("AUC (win prediction)")
a.set_title("(d) ML learned the training days (AUC ~1.0) and\nnothing that carries forward (test ~0.5)", loc="left")
fig.suptitle("Opening-range breakout: dead in SPY, alive in TSLA, gamma and ML don't sharpen it", x=0.01, ha="left", fontsize=14, fontweight="bold", color=INK)
fig.text(0.01, 0.005, "Databento 1-minute bars (SPY ARCX 2020-23; EQUS.MINI 2024-26). Costs: 1c/share/side + 1c on stops. Shift-null p-values. Pre-registered at fbca5c8; amendments A1/A2.", fontsize=8, color=INK2)
plt.tight_layout(rect=(0, 0.02, 1, 0.95)); plt.savefig(O / "orb_gamma.png", dpi=150, facecolor=BG)
