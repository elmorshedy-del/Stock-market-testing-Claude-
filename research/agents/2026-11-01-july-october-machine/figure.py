"""Side-by-side gauges (July vs October, aligned by session from the high) + ledger + conditional forecasts -> out/machine.png"""
import json
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

H = Path(__file__).resolve().parent; O = H / "out"
BG, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"; CJ, CO = "#2a78d6", "#eb6834"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9.8, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": GRID,
                     "xtick.color": INK2, "ytick.color": INK2})
G = pd.read_csv(O / "gauges.csv", index_col=0, parse_dates=True)
tg = pd.read_csv(H.parents[1] / "microstructure" / "out" / "td_gamma_SPY.csv", parse_dates=["date"]).set_index("date")
G["engine"] = 100 * (tg.spot / tg.flip_classic - 1).reindex(G.index)
live = {"2026-10-09": 100 * (778.53 / 775.37 - 1), "2026-10-23": 100 * (759.89 / 774.0 - 1), "2026-10-26": 100 * (765.29 / 773.0 - 1), "2026-10-27": 100 * (769.66 / 772.5 - 1),
        "2026-10-28": 100 * (772.31 / 771.60 - 1), "2026-10-29": 100 * (769.52 / 772.24 - 1), "2026-10-30": 100 * (755.69 / 774.06 - 1)}
J = G.loc["2026-07-10":"2026-08-14"].copy(); Oc = G.loc["2026-10-09":"2026-10-30"].copy()
J["x"] = np.arange(len(J)); Oc["x"] = np.arange(len(Oc))
panels = [("SPY % from the high", lambda D: 100 * (D.SPY / D.SPY.iloc[0] - 1)), ("Dealer gamma: GEX $bn (SqueezeMetrics)", lambda D: D["G1 GEX $bn (SqueezeMetrics)"]),
          ("SPY vs gamma flip % (our engine)", None), ("Dark-pool buying: DIX %", lambda D: D["G2 DIX %"]), ("VIX", lambda D: D["G3 VIX"]),
          ("VIX / VIX3M (>1 = panic curve)", lambda D: D["G3 VIX/VIX3M (inverted >1)"]), ("Tech vs small caps: QQQ/IWM (pts from start)", lambda D: D["G4 QQQ/IWM (log x100)"] - D["G4 QQQ/IWM (log x100)"].iloc[0]),
          ("Credit: HYG/IEF (pts from start)", lambda D: D["G5 HYG/IEF (log x100)"] - D["G5 HYG/IEF (log x100)"].iloc[0]), ("10-year yield (bp from start)", lambda D: 100 * (D["G6 10y yield %"] - D["G6 10y yield %"].iloc[0]))]
fig = plt.figure(figsize=(15.5, 13.2), facecolor=BG)
gs = fig.add_gridspec(4, 3, height_ratios=[1, 1, 1, 1.35], hspace=0.55, wspace=0.18, left=0.045, right=0.985, top=0.885, bottom=0.015)
fig.text(0.045, 0.962, "Same machine on the way down; October is missing the part that turned July around", fontsize=17, weight="bold", color=INK)
fig.text(0.045, 0.93, "Blue = July (from the Jul 10 high, through the Aug 4 rebound); orange = October (from the Oct 9 high to Oct 30). Same session count from the high; "
         "dotted line = July's low (Jul 29).\nThe gauges track each other for 13 sessions, then split exactly when the megacap reports landed: July's beats turned the machine, October's misses pushed it further.",
         fontsize=10.2, color=INK2, va="top")
for i, (title, f) in enumerate(panels):
    ax = fig.add_subplot(gs[i // 3, i % 3]); ax.set_facecolor(BG)
    if f is None:
        ax.plot(J.x, J.engine, color=CJ, lw=2); xs = [Oc.index.get_loc(pd.Timestamp(d)) for d in live]; vs = list(live.values()); ax.plot(xs[1:], vs[1:], color=CO, lw=2, marker="o", ms=4); ax.plot(xs[0], vs[0], "o", color=CO, ms=4)
        ax.axhline(0, color=INK2, lw=0.8); ax.text(0.3, 0.3, "flip", color=INK2, fontsize=8.5)
    else:
        ax.plot(J.x, f(J), color=CJ, lw=2); ax.plot(Oc.x, f(Oc), color=CO, lw=2)
    ax.axvline(13, color=INK2, lw=0.8, ls=":"); ax.set_title(title, loc="left", fontsize=10.5, weight="bold", color=INK)
    ax.yaxis.grid(True, color=GRID); ax.set_xlim(0, 25); ax.tick_params(labelsize=8.5)
    if i == 0:
        ax.text(13.3, ax.get_ylim()[1] * 0.85 if ax.get_ylim()[1] > 0 else 0, "July low", fontsize=8.5, color=INK2)
        ax.text(15.3, float(f(Oc).iloc[-1]), "Oct 30", fontsize=8.5, color=CO, va="center")
    if i == 2: ax.text(15.4, live["2026-10-30"], "Oct 30\n(live maps)", fontsize=8, color=CO, va="center")
    if i // 3 == 2: ax.set_xlabel("sessions from the high", fontsize=8.5)
L = json.load(open(O / "ledger.json"))
ax = fig.add_subplot(gs[3, :2]); ax.axis("off")
ax.set_title("The ledger: what pushed down, what turned July, is it there now?", loc="left", fontsize=12.3, weight="bold", color=INK)
rows = [("PUSHED DOWN", "", "", ""),
        ("Dealer gamma lost (amplifier on)", "yes (GEX 9.0 → 6.2bn)", "yes (GEX 12.8 → 1.1bn)", "same, worse"),
        ("Fear premium + near-term event kink", "yes (VIX 20.7)", "yes (VIX 19.4; election Nov 3)", "same"),
        ("Rotation out of megacap tech", "yes", "yes, 1.3-2x stronger", "same, worse"),
        ("Dark-pool dip buying low", "DIX 42.5", "DIX 43.8", "same"),
        ("Bonds / credit", "yields +18bp, credit flat", "yields −32bp, credit softer", "DIFFERENT (risk-off tone)"),
        ("TURNED JULY (JUL 29 → AUG 4)", "", "", "OCTOBER NOW"),
        ("Vol event passed → VIX −4, curve normal", "FOMC Jul 29", "", "SCHEDULED: election Nov 3"),
        ("Megacap tech took the lead again", "GOOGL/AMZN beat; +1.7% Jul 30", "", "ABSENT: GOOGL/AMZN missed"),
        ("SPY reclaimed the gamma flip", "in 3 sessions (Aug 3)", "", "needs +2.4% (774)"),
        ("Buyback windows reopen after reports", "yes", "", "YES (mechanical, now)"),
        ("Turn-of-month inflows", "Jul 31-Aug 4", "", "YES (Nov 2-4)")]
cols = [0.0, 0.33, 0.545, 0.765]; hd = ["", "July", "October", "Same?"]
for j, h in enumerate(hd): ax.text(cols[j], 0.97, h, fontsize=10, weight="bold", color=INK2, transform=ax.transAxes)
for i, r in enumerate(rows):
    y = 0.9 - i * 0.078; bold = r[1] == "" and r[2] == ""
    ax.text(cols[0], y, r[0], fontsize=9.6, weight="bold" if bold else "normal", color=INK if not bold else INK2, transform=ax.transAxes)
    for j in (1, 2, 3):
        c = INK
        if j == 3 and any(k in r[3] for k in ("ABSENT", "DIFFERENT")): c = "#d03b3b"
        if j == 3 and any(k in r[3] for k in ("YES", "same")): c = "#0a7d0a"
        if j == 3 and "SCHEDULED" in r[3] or (j == 3 and "needs" in r[3]): c = "#a86b00"
        ax.text(cols[j], y, r[j], fontsize=9.4, color=c, transform=ax.transAxes, weight="bold" if bold else "normal")
ax = fig.add_subplot(gs[3, 2]); ax.axis("off")
ax.set_title("So: will the product be the same?", loc="left", fontsize=12.3, weight="bold", color=INK)
txt = ("Half of it: the July-like BOUNCE is set up;\nthe July-like BREAKOUT is not (yet).\n\n"
       "Written now, scored later:\n"
       "1. If VIX closes ≤ 16.5 by Nov 6 (the July-size\n   crush), SPY closes ≥ 774 (the flip) by Nov 13.\n"
       "2. If VIX stays > 17 through Nov 6, SPY does\n   not reclaim 774 by Nov 13.\n"
       "3. If tech does not retake the lead (QQQ/IWM\n   no higher than Oct 30 on Nov 13), no new SPY\n   closing high (> 779.14) by Nov 20.\n"
       "4. If QQQ/IWM recovers ≥ 4.5 pts (July's turn\n   size) by Nov 13, a new closing high by Nov 20.")
ax.text(0.0, 0.94, txt, fontsize=9.8, color=INK, va="top", transform=ax.transAxes, linespacing=1.33)
fig.savefig(O / "machine.png", dpi=105, facecolor=BG); print("ok")
