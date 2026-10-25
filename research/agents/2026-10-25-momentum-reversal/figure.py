"""Momentum and reversal by regime in one picture: out/momentum_regimes.png (reads out/cells.csv, out/m1.json, out/momentum.json)."""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import momentum as Mo

BLUE, ORANGE, GREEN, RED, INK, MUTED, GRID, SURF = "#2a78d6", "#eb6834", "#1baf7a", "#d64545", "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"
C = pd.read_csv(Mo.OUT / "cells.csv")
M1 = json.loads((Mo.OUT / "m1.json").read_text())["12m lookback"]
J = json.loads((Mo.OUT / "momentum.json").read_text())
today = {"low vol", "bull (24m up)", "above 10m avg", "above 200d", "not rebound", "channel 2022-26"}
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(2, 2, figsize=(15.5, 11), gridspec_kw={"hspace": 0.42, "wspace": 0.45})
def dots(a, rows, unit, title):
    y = np.arange(len(rows))[::-1]
    for yi, r in zip(y, rows):
        col = ORANGE if r["cell"] in today else (INK if r["cell"] == "all" else MUTED)
        sig = (r["lo90"] > 0) or (r["hi90"] < 0)
        a.plot([r["lo90"], r["hi90"]], [yi, yi], color=col, lw=2 if sig else 1, alpha=0.9)
        a.scatter([r["mean"]], [yi], color=col, s=55 if sig else 30, zorder=3, edgecolor=INK if sig else col)
        a.text(max(r["hi90"], r["mean"]) + 0.02 * (a.get_xlim()[1] - a.get_xlim()[0] if False else 0), yi, "", fontsize=7)
    a.axvline(0, color=INK, lw=0.8)
    a.set_yticks(y, [f"{r['cell']}  (n {r['n']})" for r in rows], fontsize=8)
    a.set_xlabel(unit)
    a.set_title(title, loc="left", fontsize=9.5, color=INK)
order = lambda d, test, cells: [d[(d.test.str.startswith(test)) & (d.cell == c)].iloc[0].to_dict() for c in cells if ((d.test.str.startswith(test)) & (d.cell == c)).any()]
m1rows = [{"cell": "all", "n": sum(M1["months long / short"]), "mean": M1["long minus short, %/month"], "lo90": np.nan, "hi90": np.nan}]
for c in M1["cells"]:
    m1rows.append({"cell": c["cell"], "n": sum(c["months long / short"]), "mean": c["long minus short %/month"], "lo90": c["lo90"], "hi90": c["hi90"]})
m1rows[0]["lo90"], m1rows[0]["hi90"] = m1rows[0]["mean"], m1rows[0]["mean"]
dots(ax[0, 0], m1rows, "next-month S&P return when trend is up minus when down, %/month",
     f"M1 Trend-following on the S&P (1928-2026): +{M1['long minus short, %/month']:.2f}%/month (p 0.03, Holm 0.10)\nWorks in bull states and mid volatility; flat in low vol and 1980-99. Orange = today's regime")
cells2 = ["all", "bull (24m up)", "bear (24m down)", "not rebound", "rebound month", "low vol", "mid vol", "high vol", "above 10m avg", "below 10m avg", "1980-99", "2000-22", "channel 2022-26"]
dots(ax[0, 1], order(C, "M2", cells2), "winners minus losers (12-1 month), next month %",
     "M2 Cross-sectional momentum, large caps 1990-2026: +0.46%/month (Holm 0.10)\nWorks in CALM uptrends (low vol +0.90%); CRASHES in bear-market rebounds (-0.87%)")
cells3 = ["all", "low vol", "mid vol", "high vol", "above 200d", "below 200d", "bull (24m up)", "bear (24m down)", "1980-99", "2000-22", "channel 2022-26"]
dots(ax[1, 0], order(C, "M3", cells3), "last week's losers minus winners, next week, bp gross (costs about 20 bp)",
     "M3 Weekly reversal, large caps 1990-2026: +21 bp/week gross (Holm p < 0.001), about 0 after costs\nOnly pays in HIGH VOL (+43 bp) or below the 200-day (+45 bp); dead in the channel era (-5 bp)")
m4 = J["M4 cells"]
keys4 = ["all", "phase: uptrend", "phase: downtrend", "phase: mixed", "52w: near high (>=95%)", "52w: far (<80%)", "market vol: low vol", "market vol: mid vol", "market vol: high vol",
         "market trend: above 200d", "market trend: below 200d"]
rows4 = [{"cell": k.replace("market vol: ", "").replace("market trend: ", ""), "n": m4[k]["stock-days"], "mean": m4[k]["slope"], "lo90": m4[k]["lo90"], "hi90": m4[k]["hi90"]} for k in keys4]
dots(ax[1, 1], rows4, "slope of next 5 days on last 5 days (z); negative = reversal",
     "M4 Each stock's own weekly reversal: the stock's PHASE does not matter\n(uptrend = downtrend = mixed, about -0.026); the MARKET regime does (high vol -0.038 vs low -0.019)")
fig.savefig(Mo.OUT / "momentum_regimes.png", dpi=140, bbox_inches="tight", facecolor=SURF)
