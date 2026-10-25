"""AAPL's quirks since 2020 in one picture: out/aapl_quirks.png. Usage: python figure.py <long folder> <etfs folder>
(reads out/quirks.json, out/round2.json, out/round3.json)"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import quirks as Q

BLUE, ORANGE, GREEN, INK, MUTED, GRID, SURF = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"
long, etfs = sys.argv[1], sys.argv[2]
q1 = json.loads((Q.OUT / "quirks.json").read_text())
q2 = json.loads((Q.OUT / "round2.json").read_text())
spx = Q.load(Path(long) / "GSPC.json")
spx = spx[spx.index >= "2009-01-01"]
idx = spx.index
rs = np.log(spx.close).diff()
names = ["AAPL", "MSFT", "AMZN", "GOOGL", "META", "NVDA"]
S = {s: Q.load(Path(long) / f"{s}.json").reindex(idx) for s in names}
smh, spy = Q.load(Path(etfs) / "SMH.json").reindex(idx), Q.load(Path(etfs) / "SPY.json").reindex(idx)
f = np.log(smh.close).diff() - np.log(spy.close).diff()
E = {}
for s in names:
    r = np.log(S[s].close).diff()
    rm = (rs - Q.W[s] * r.fillna(0)) / (1 - Q.W[s])
    b = (r.rolling(252, min_periods=200).cov(rm) / rm.rolling(252, min_periods=200).var()).shift(1)
    E[s] = r - b * rm
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(2, 2, figsize=(15.5, 10), gridspec_kw={"hspace": 0.38, "wspace": 0.2})
# A: overnight vs intraday
a = ax[0, 0]
A = S["AAPL"][S["AAPL"].index >= "2011-01-01"]
on = np.log(A.open / A.close.shift(1)).fillna(0)
it = np.log(A.close / A.open).fillna(0)
a.plot(on.index, 100 * on.cumsum(), color=MUTED, lw=1.6, label="AAPL overnight (close to next open)")
a.plot(it.index, 100 * it.cumsum(), color=BLUE, lw=1.6, label="AAPL intraday (open to close)")
a.axvline(pd.Timestamp("2020-01-02"), color=INK, lw=0.8, ls=":")
a.axhline(0, color=MUTED, lw=0.6)
a.set_ylabel("cumulative log return, %")
a.legend(loc="upper left", frameon=False, fontsize=8.5)
R = q2["R2a intraday minus overnight (annualized, log %)"]
a.set_title(f"1. AAPL makes its money during the day since 2020 (pass)\nintraday minus overnight {R['AAPL 2020-2026']:+.0f}%/yr vs peers {R['peer average 2020-2026']:+.0f}%/yr "
            f"(it was {R['AAPL 2011-2019']:+.0f}%/yr in 2011-19).\nThe old day-time bid matched Apple's buyback windows; the new one does not",
            loc="left", fontsize=9.5, color=INK)
# B: AI-factor loading
b = ax[0, 1]
def rollb(s, n=250):
    return E[s].rolling(n).cov(f) / f.rolling(n).var()
la = rollb("AAPL")
lp = pd.concat([rollb(s) for s in ["MSFT", "AMZN", "GOOGL", "META"]], axis=1).mean(axis=1)
m = la.index >= "2015-01-01"
b.plot(la.index[m], la[m], color=ORANGE, lw=1.8, label="AAPL")
b.plot(lp.index[m], lp[m], color=MUTED, lw=1.4, label="MSFT, AMZN, GOOGL, META average")
b.axhline(0, color=INK, lw=0.8)
b.axvline(pd.Timestamp("2023-01-03"), color=INK, lw=0.8, ls=":")
b.set_ylabel("AAPL-specific move per 1% semis beat, 250d")
b.legend(loc="lower left", frameon=False, fontsize=8.5)
t2 = q1["T2a AI-factor loading 2023-2026"]
b.set_title(f"2. Since 2023 AAPL is the mega-cap short the AI trade (pass, p {t2['p (>= 0, block bootstrap)']:.3f})\n"
            f"loading {t2['AAPL loading on f']:+.2f} vs peers about {np.mean(list(t2['non-semi peer loadings'].values())):+.2f}; before 2023 it was the opposite.\n"
            "But AI leadership does not tell you WHEN AAPL decouples (T2b fail)", loc="left", fontsize=9.5, color=INK)
# C: decoupling used to be earnings
c = ax[1, 0]
t1a, t1b = q1["T1 contrast 2011-2019"], q1["T1 earnings calendar 2020-2026"]
x = np.arange(2)
w = 0.35
on_ = [t1a["P(earnings in window | alarm)"], t1b["P(earnings in window | alarm)"]]
off_ = [t1a["P(earnings in window | no alarm)"], t1b["P(earnings in window | no alarm)"]]
c.bar(x - w / 2, 100 * np.array(on_), w, color=ORANGE, label="decoupled days (alarm)")
c.bar(x + w / 2, 100 * np.array(off_), w, color=MUTED, label="other days")
for xi, v in zip(list(x - w / 2) + list(x + w / 2), on_ + off_):
    c.text(xi, 100 * v + 1.5, f"{100 * v:.0f}%", ha="center", fontsize=9, color=INK)
c.set_xticks(x, ["2011-2019", "2020-2026"])
c.set_ylim(0, 75)
c.set_ylabel("share with an earnings report inside the 20-day window, %")
c.legend(loc="upper right", frameon=False, fontsize=8.5)
an = q1["anatomy today (AAPL, 1 = normal)"]
c.set_title("3. Decoupling changed nature: it used to be earnings (p < 0.001); since 2020 it is not\n"
            f"Today's is a rotation, not news: 20-day beta has flipped negative ({an['20d beta']:+.2f} x normal)\n"
            f"while AAPL's own news volatility is below normal ({an['idiosyncratic vol']:.2f} x)", loc="left", fontsize=9.5, color=INK)
# D: current episode
d = ax[1, 1]
m = idx >= "2026-09-01"
r_a = np.log(S["AAPL"].close).diff()
rm_a = (rs - Q.W["AAPL"] * r_a.fillna(0)) / (1 - Q.W["AAPL"])
for ser, col, lab in [(r_a, ORANGE, "AAPL"), (rm_a, MUTED, "S&P without AAPL"), (np.log(smh.close).diff(), BLUE, "semis (SMH)")]:
    v = ser[m].fillna(0)
    d.plot(v.index, 100 * (np.exp(v.cumsum()) - 1), color=col, lw=1.8, label=lab)
d.axhline(0, color=MUTED, lw=0.6)
d.axvline(pd.Timestamp("2026-09-15"), color=INK, lw=0.8, ls=":")
d.set_ylabel("return since Sep 1, 2026, %")
import matplotlib.dates as mdates
d.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=0, interval=1))
d.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
d.legend(loc="upper left", frameon=False, fontsize=8.5)
ce = q1["current episode Sep 15 - Oct 23"]
d.set_title(f"Now: money leaving semis, landing in AAPL (Sep 15 - Oct 23)\nAAPL stock-specific {ce['AAPL residual log return %']:+.1f}%, semis vs S&P {ce['SMH minus SPY log return %']:+.1f}%, "
            f"their daily correlation {ce['corr(residual, f)']:+.2f}.\nContext: AAPL passed NVDA as most valuable; foldable iPhone on sale; earnings ~Nov 2",
            loc="left", fontsize=9.5, color=INK)
fig.savefig(Q.OUT / "aapl_quirks.png", dpi=140, bbox_inches="tight", facecolor=SURF)
