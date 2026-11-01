"""out/phase_iter1.png: iteration 1 results: H1 range dose-response (pass), H2 autocorrelation by horizon (fail, tiny right-signed),
H3 continuation (fail), and the exploratory VIX x gamma continuation pattern. Usage: python figure1.py <SPY 1m parquet>"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; OUT = HERE / "out"
X = pd.read_csv(OUT / "days.csv", index_col=0, parse_dates=True); R = json.loads((OUT / "phase.json").read_text())
GREEN, RED, INK, MUTED, SURF, BLUE, AMBER, GREY = "#1baf7a", "#d64545", "#0b0b0b", "#52514e", "#fcfcfb", "#2a78d6", "#e8a33d", "#c9c8c3"
plt.rcParams.update({"font.size": 10.5, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED, "text.parse_math": False,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
short = X.open < X.flip_incl
m = pd.read_parquet(sys.argv[1], columns=["close"]); m.index = m.index.tz_convert("America/New_York")
m = m[(m.index.time >= pd.Timestamp("09:30").time()) & (m.index.time < pd.Timestamp("16:00").time())]
m["day"] = m.index.normalize().tz_localize(None); m["mins"] = (m.index.hour - 9) * 60 + m.index.minute - 30; m = m[m.day.isin(X.index)]
ac = {}
for k in (1, 5, 10, 15, 30):
    b = m.assign(bk=m.mins // k).groupby(["day", "bk"]).close.last(); lr = np.log(b).groupby(level=0).diff().dropna(); nx = lr.groupby(level=0).shift(-1); ok = nx.notna()
    cr = (lr * nx)[ok].groupby(level=0).sum(); sq = (lr ** 2).groupby(level=0).sum()
    ac[k] = (cr.reindex(short[short].index).sum() / sq.reindex(short[short].index).sum(), cr.reindex(short[~short].index).sum() / sq.reindex(short[~short].index).sum())
fig = plt.figure(figsize=(18, 11)); gs = fig.add_gridspec(2, 2, hspace=0.36, wspace=0.22)
a = fig.add_subplot(gs[0, 0]); q = pd.qcut(X.d, 5, labels=False)
mu = [X.O1[q == i].mean() for i in range(5)]; se = [X.O1[q == i].std() / np.sqrt((q == i).sum()) for i in range(5)]
a.bar(range(5), mu, yerr=1.64 * np.array(se), color=[RED, RED, AMBER, GREEN, GREEN], alpha=0.85, capsize=4)
for i in range(5): a.text(i, mu[i] + 0.04, f"{mu[i]:.2f}", ha="center", fontsize=10)
a.set_xticks(range(5)); a.set_xticklabels([f"{X.d[q == i].median():+.1f}σ" for i in range(5)]); a.set_xlabel("09:30 open vs pre-open flip (distance in expected-daily-move units)")
a.set_ylabel("day's range ÷ expected daily move (from VIX)"); a.set_ylim(0, 1.35)
a.set_title(f"H1 PASS: the further below the flip, the bigger the day (×{R['primary (state = 09:30 open vs pre-open flip)']['O1_short']/R['primary (state = 09:30 open vs pre-open flip)']['O1_long']:.2f} below vs above;\nz ≈ 7; every year, both eras, every VIX third)", loc="left", fontsize=12, weight="bold", color=GREEN)
a = fig.add_subplot(gs[0, 1]); ks = list(ac)
a.plot(ks, [ac[k][0] for k in ks], "o-", color=RED, lw=2, label="opened below flip (dealers short gamma)")
a.plot(ks, [ac[k][1] for k in ks], "o-", color=GREEN, lw=2, label="opened above flip (dealers long gamma)")
a.axhspan(0.02, 0.08, color=RED, alpha=0.07); a.text(31, 0.05, "predicted\n(short)", fontsize=8.5, color=RED, va="center")
a.axhspan(-0.08, -0.02, color=GREEN, alpha=0.07); a.text(31, -0.05, "predicted\n(long)", fontsize=8.5, color=GREEN, va="center")
a.axhline(0, color=MUTED, lw=0.6); a.set_xscale("log"); a.set_xticks(ks); a.set_xticklabels([f"{k}m" for k in ks]); a.set_xlim(0.8, 45)
a.set_ylabel("lag-1 autocorrelation of returns (raw, no demeaning)"); a.legend(frameon=False, fontsize=9, loc="lower left")
a.set_title("H2 FAIL: the sign is right (short trends a bit more) but the\nsize is ~5-10x smaller than predicted: no regime switch in persistence", loc="left", fontsize=12, weight="bold", color=RED)
a = fig.add_subplot(gs[1, 0]); X["cont15"] = np.sign(X.ro15) == np.sign(X.rest15)
vals = [X.cont15[short].mean(), X.cont15[~short].mean()]
a.bar([0, 1], vals, color=[RED, GREEN], width=0.5); a.axhline(0.5, color=MUTED, ls="--", lw=0.8)
for i, v in enumerate(vals): a.text(i, v + 0.01, f"{v:.1%}", ha="center", fontsize=11, weight="bold")
a.set_xticks([0, 1]); a.set_xticklabels(["opened below flip", "opened above flip"]); a.set_ylim(0.3, 0.65)
a.set_ylabel("P(rest of day continues the 09:30-09:45 move)")
a.set_title("H3 FAIL: the first 15 minutes say nothing about the rest\nof the day on their own, in either regime (coin flip)", loc="left", fontsize=12, weight="bold", color=RED)
a = fig.add_subplot(gs[1, 1]); X["vt"] = pd.cut(X.vpct, [-0.01, 1 / 3, 2 / 3, 1.01], labels=["low VIX", "mid VIX", "high VIX"])
T = X.groupby(["vt", short.map({True: "below flip", False: "above flip"})], observed=True).cont15.agg(["mean", "size"]).unstack()
im = a.imshow(T["mean"].to_numpy(), cmap="RdYlGn", vmin=0.40, vmax=0.60)
for i in range(T.shape[0]):
    for j in range(2):
        a.text(j, i, f"{T['mean'].iloc[i, j]:.0%}\n(n {int(T['size'].iloc[i, j])})", ha="center", va="center", fontsize=11, color=INK)
a.set_xticks([0, 1]); a.set_xticklabels(T["mean"].columns); a.set_yticks(range(3)); a.set_yticklabels(T.index)
a.set_title("EXPLORATORY (found in passing): continuation depends on VIX x gamma.\nBelow flip + calm = reverts (45%); below flip + stressed = continues (53-56%)", loc="left", fontsize=12, weight="bold", color=AMBER)
fig.suptitle("Iteration 1: dealer gamma sets the SIZE of SPY's day, not its persistence (2020-2026, 1,701 days, pre-registered)", x=0.01, ha="left", fontsize=15, weight="bold", color=INK)
fig.savefig(OUT / "phase_iter1.png", dpi=115, bbox_inches="tight"); print("ok", {k: (round(v[0], 4), round(v[1], 4)) for k, v in ac.items()})
