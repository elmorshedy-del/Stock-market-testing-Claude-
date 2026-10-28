"""out/live_read_1029.png: Oct 28 intraday paths vs the pre-open flips (Fed at 14:00/14:30), and Thursday's maps.
Usage: python figure.py <live28/y> <live28/td> <live27/td>"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; OUT = HERE / "out"
M = json.loads((OUT / "maps.json").read_text())
y = Path(sys.argv[1])
sys.path.insert(0, str(HERE.parent / "2026-10-27-flip-wicks"))
from flipmap import norm, preopen, exposures                      # noqa: E402
GREEN, RED, INK, MUTED, SURF, BLUE, ORANGE, GREY = "#1baf7a", "#d64545", "#0b0b0b", "#52514e", "#fcfcfb", "#2a78d6", "#eb6834", "#c9c8c3"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})


def bars(sym):
    r = json.loads((y / f"{sym}_1m.json").read_text())["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    b = pd.DataFrame({k: q[k] for k in ("high", "low", "close")}, index=pd.to_datetime(r["timestamp"], unit="s", utc=True).tz_convert("America/New_York")).dropna()
    b = b[b.index.date == pd.Timestamp("2026-10-28").date()]
    return b[(b.index.strftime("%H:%M") >= "09:30") & (b.index.strftime("%H:%M") <= "16:15")]


fig, ax = plt.subplots(2, 2, figsize=(17, 11), gridspec_kw={"width_ratios": [1.5, 1], "hspace": 0.5, "wspace": 0.22})
for row, (sym, lv) in enumerate((("SPY", [(M["SPY"]["pre-open flip incl 0DTE"], f"pre-open flip {M['SPY']['pre-open flip incl 0DTE']:.2f}", ORANGE), (M["SPY"]["Thursday map"]["flip"], f"Thursday flip {M['SPY']['Thursday map']['flip']:.2f}", ORANGE), (775, "775 (first big + strike)", GREEN), (770, "770", MUTED)]),
                                 ("TSLA", [(400, "400 call wall / floor", GREEN), (410, "410", MUTED), (420, "420 magnet", GREEN), (395, "395", RED)]))):
    a = ax[row, 0]; b = bars(sym)
    x = (b.index.hour - 9.5) + b.index.minute / 60
    a.fill_between(x, b.low, b.high, color=GREY, lw=0); a.plot(x, b.close, color=INK, lw=1)
    a.axvspan(6.5, x.max() + 0.05, color=BLUE, alpha=0.06); a.text(6.55, b.high.max(), " after hours", fontsize=7.5, color=BLUE, va="top")
    for tt, lab in ((4.5, "14:00 Fed decision"), (5.0, "14:30 press conf.")):
        a.axvline(tt, color=BLUE, lw=0.8, ls=":"); a.text(tt, b.low.min(), " " + lab, rotation=90, fontsize=7.5, color=BLUE, va="bottom")
    for yv, lab, c in lv:
        a.axhline(yv, color=c, lw=1, ls="--"); a.text(0.02, yv, lab, fontsize=7.5, color=c, va="bottom", transform=a.get_yaxis_transform())
    a.set_xticks([0, 1.5, 3.5, 4.5, 5.5, 6.5], ["09:30", "11:00", "13:00", "14:00", "15:00", "16:00"]); a.set_ylabel(f"{sym}, 1-minute range and close")
    m = M[sym]
    if sym == "SPY":
        a.set_title(f"SPY Oct 28: below its pre-open flip ({m['pre-open flip incl 0DTE']:.2f}) for 88% of the day, dipped into the decision, rallied on\n"
                    f"Warsh to {m['high']:.2f} (14:37), closed {m['close']:.2f}: ABOVE the flip (+{m['close - flip']:.2f}) for the first close since Oct 21.\n"
                    f"After hours {m['after hours %']:+.2f}% (GOOGL -8.5%, MSFT +4.2%). Thursday's flip {m['Thursday map']['flip']:.2f}: gamma ~0 at the close", loc="left", fontsize=9, color=INK)
    else:
        a.set_title(f"TSLA Oct 28: opened at the high {m['open']:.2f}, sold to {m['low']:.2f} by 10:12 (just under the 400 floor), held 402-404\n"
                    f"through the Fed, closed {m['close']:.2f} (-0.7%) after +9% in two days. Megacaps sold, chips bought.\n"
                    f"Flip far below ({m['Thursday map']['flip']:.0f}); long gamma; after Friday DEEPLY freed (0.4th pctile)", loc="left", fontsize=9, color=INK)
# Thursday maps
for row, sym, lo, hi, step in ((0, "SPY", 740, 805, 5), (1, "TSLA", 360, 440, 5)):
    a = ax[row, 1]; S = M[sym]["close"]
    e = norm(pd.read_csv(Path(sys.argv[3]) / f"{sym}_eod_20261027.csv.gz")); e = e[e.date == pd.Timestamp("2026-10-27")]
    far = norm(pd.read_csv(Path(sys.argv[3]) / f"{sym}_eod_20261026.csv.gz")); far = far[~far.expiration.isin(e.expiration.unique())].assign(date=pd.Timestamp("2026-10-27"))
    o = norm(pd.read_csv(Path(sys.argv[2]) / f"{sym}_oi_20261028.csv.gz"))
    g = preopen(pd.concat([e, far]), o, pd.Timestamp("2026-10-29")); g = g[g.expiration > pd.Timestamp("2026-10-28")]
    k = exposures(g, S).groupby("K").gex.sum() / 1e9; k = k[(k.index >= lo) & (k.index <= hi) & (k.index % step == 0)]
    a.barh(k.index, k.values, height=step * 0.8, color=[GREEN if v > 0 else RED for v in k.values])
    a.axhline(S, color=BLUE, lw=1.6); a.text(a.get_xlim()[1] if a.get_xlim()[1] > 0 else 0, S, f" close {S:.2f}", color=BLUE, fontsize=8, va="bottom", ha="right")
    a.axhline(M[sym]["Thursday map"]["flip"], color=ORANGE, ls="--", lw=1.2); a.text(a.get_xlim()[0], M[sym]["Thursday map"]["flip"], f" flip {M[sym]['Thursday map']['flip']:.1f}", color=ORANGE, fontsize=8, va="bottom")
    a.set_ylim(lo, hi); a.set_xlabel("dealer gamma by strike, $bn per 1% (positions at the Oct 27 close)")
    tm = M[sym]["Thursday map"]
    a.set_title(f"{sym} map for Thursday: call wall {tm['call wall']:.0f}, put wall {tm['put wall']:.0f};\n"
                f"Oct 30 expiry = {100*tm['Oct 30 expiry share of |gamma|']:.0f}% of gamma (released Friday)", loc="left", fontsize=9, color=INK)
fig.savefig(OUT / "live_read_1029.png", dpi=140, bbox_inches="tight", facecolor=SURF)
