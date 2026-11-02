"""A3 figure: (a) TSLA breakout equity, in-sample 2024-26 vs out-of-sample 2020-23; (b) per name: all days, without the 10 best days, news-gap days. -> out/orb_a3.png"""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; O = HERE / "out"; K = "S1_5_close"
BG, INK, INK2, GRID, GRAY, BLUE, ORANGE = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#a9a8a3", "#2a78d6", "#eb6834"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": GRAY, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "axes.titleweight": "bold", "axes.titlesize": 11})
fig, ax = plt.subplots(1, 2, figsize=(14, 5.6), facecolor=BG, gridspec_kw={"width_ratios": [1, 1.25]})
for a in ax: a.set_facecolor(BG); a.grid(True, color=GRID, lw=0.8); a.spines[["top", "right"]].set_visible(False)

a = ax[0]
for lab, nm, col, ls in [("TSLA2020", "2020-23 OUT OF SAMPLE (clean): +29.5 bp/day, p 0.018", ORANGE, "-"), ("TSLA2020_d2", "2020-23 all complete days: +24.6, p 0.046", ORANGE, ":"),
                         ("TSLA", "2024-26 where it was found (clean): +12.4", BLUE, "-"), ("TSLA_d2", "2024-26 all complete days: +18.5", BLUE, ":")]:
    df = pd.read_parquet(O / f"days_{lab}.parquet"); d = df[K + "_dir"].to_numpy()
    p = pd.Series(np.where(d > 0, df[K + "_L"].fillna(0), np.where(d < 0, df[K + "_S"].fillna(0), 0.0)), index=df.index)
    a.plot(np.arange(len(p)), p.cumsum() / 100, color=col, ls=ls, lw=2, label=nm)
a.axhline(0, color=GRAY, lw=1); a.legend(frameon=False, fontsize=8.5, loc="upper left")
a.set_xlabel("trading days"); a.set_ylabel("cumulative return, % (1x, after costs)")
a.set_title("(a) TSLA 5-min breakout passed out of sample:\npositive in every year 2020-23 (max drawdown -24% at 1x)", loc="left")

a = ax[1]
r = json.load(open(O / "robust.json"))
names = ["TSLA2020_d2", "TSLA_d2", "NFLX_d2", "UNH_d2", "NVDA_d2", "AMD_d2", "JPM_d2", "META_d2", "AMZN_d2", "QQQ_d2", "SPY_d2"]
lbl = ["TSLA\n20-23", "TSLA\n24-26", "NFLX", "UNH*", "NVDA", "AMD", "JPM*", "META", "AMZN", "QQQ", "SPY"]
x = np.arange(len(names)); w = 0.27
v1 = [r[n]["mean bp/day"] for n in names]; v2 = [r[n]["mean without the 10 best days"] for n in names]; v3 = [r[n]["mean with +2c / +5c / +10c per side"][1] for n in names]
a.bar(x - w, v1, w, color=ORANGE, label="all complete days")
a.bar(x, v3, w, color=BLUE, label="with 5c/share/side extra cost")
a.bar(x + w, v2, w, color=GRAY, label="without its 10 best days")
a.axhline(0, color=INK2, lw=1); a.set_xticks(x, lbl, fontsize=9); a.set_ylabel("breakout mean bp/day (2024-26 unless marked)")
a.legend(frameon=False, fontsize=8.5, loc="upper right")
a.set_title("(b) Other names: positive, but mostly a few big news days;\nonly TSLA, NFLX and UNH stay positive under both stress tests", loc="left")
a.text(0.99, -0.16, "* UNH/JPM were the low-volatility controls of the screen. 2024-26 = Databento EQUS.MINI; TSLA 2020-23 = XNAS.ITCH.", transform=a.transAxes, ha="right", fontsize=8, color=INK2)
fig.suptitle("Opening-range breakout, round 2: TSLA confirms out of sample; other stocks are fragile; indices don't work", x=0.01, ha="left", fontsize=13.5, fontweight="bold", color=INK)
plt.tight_layout(rect=(0, 0.03, 1, 0.93)); plt.savefig(O / "orb_a3.png", dpi=150, facecolor=BG)
