"""out/flip_wicks.png. Usage: python figure.py <live27/m1 folder with SPY_1m.json>"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; OUT = HERE / "out"
R, H1, H2 = (json.loads((OUT / f).read_text()) for f in ("recent.json", "h1.json", "h2.json"))
GREEN, RED, INK, MUTED, SURF, BLUE, ORANGE, GREY = "#1baf7a", "#d64545", "#0b0b0b", "#52514e", "#fcfcfb", "#2a78d6", "#eb6834", "#c9c8c3"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(2, 2, figsize=(16, 11), gridspec_kw={"hspace": 0.55, "wspace": 0.28})
# A: today
r = json.loads((Path(sys.argv[1]) / "SPY_1m.json").read_text())["chart"]["result"][0]; q = r["indicators"]["quote"][0]
m = pd.DataFrame({k: q[k] for k in ("high", "low", "close")}, index=pd.to_datetime(r["timestamp"], unit="s", utc=True).tz_convert("America/New_York")).dropna()
m = m[m.index.date == m.index.date.max()].between_time("09:30", "15:59")
x = (m.index.hour - 9.5) + m.index.minute / 60
a = ax[0, 0]; a.fill_between(x, m.low, m.high, color=GREY, lw=0); a.plot(x, m.close, color=INK, lw=1)
fl = [(int(e["time"][:2]) + int(e["time"][3:]) / 60 - 9.5, e["flip incl 0DTE"]) for e in R["Oct 27 intraday"]]
a.step([f[0] for f in fl] + [6.5], [f[1] for f in fl] + [fl[-1][1]], where="post", color=ORANGE, lw=1.8, label="flip incl. 0DTE (same positions, clock running down)")
a.axhline(R["days"][-1]["flip excl 0DTE"], color=ORANGE, lw=1, ls=":", label=f"flip excl. 0DTE {R['days'][-1]['flip excl 0DTE']:.1f} (our earlier map)")
a.axhline(770, color=GREEN, lw=0.8, ls="--"); a.text(0.05, 769.72, "770: biggest 0DTE call strike (9.0k)", fontsize=7.5, color=GREEN)
a.set_xticks([0.5, 2.5, 4.5, 6.4], ["10:00", "12:00", "14:00", "15:55"]); a.set_ylabel("SPY, 1-minute range and close")
a.legend(frameon=False, fontsize=7.5, loc="lower right")
a.set_title("Oct 27: SPY rallied to the pre-open flip (770.3), topped at 771.14 twice (12:00, 15:35-45),\n"
            "and closed 769.72. Into the close the 0DTE options' gamma grew, the flip slid below price\n"
            "(769.6 at 15:45) and dealer gamma at 770 turned positive (+$1.5bn): late session = damping", loc="left", fontsize=9, color=INK)
# B: motivating days
b = ax[0, 1]; d = [e for e in R["days"] if "high" in e]
lab = [e["day"][5:] for e in d]; hv = [e["high - flip"] for e in d]; cv = [e["close - flip"] for e in d]
xx = np.arange(len(d))
b.bar(xx, hv, color=[ORANGE if abs(v) <= 1 else GREY for v in hv], width=0.55, label="day's high minus pre-open flip")
b.scatter(xx, cv, color=INK, s=18, zorder=3, label="close minus flip")
b.axhline(0, color=ORANGE, lw=1); b.axhspan(-1, 1, color=ORANGE, alpha=0.08)
b.set_xticks(xx, lab, fontsize=8); b.set_ylabel("$ vs the pre-open flip (incl. 0DTE)"); b.set_ylim(-12.5, 3.5)
b.legend(frameon=False, fontsize=7.5, loc="lower left")
b.set_title("The motivating days (EXCLUDED from the test): 6 of the 7 days that reached\n"
            "the flip topped within $0.84 of it; 5 of those closed back below.\n"
            "Striking, but 10 days chosen after the fact prove nothing", loc="left", fontsize=9, color=INK)
# C: H1 multiverse, incl 0DTE
c = ax[1, 0]; bands = ["0.05%", "0.10%", "0.15%", "0.25%", "0.40%"]
series = [("up stall", "high STOPS at the flip from below", ORANGE), ("up reject", "close back BELOW after reaching it", GREY),
          ("down stall", "low STOPS at the flip from above", GREEN), ("down hold", "close stays ABOVE after reaching it", BLUE)]
w = 0.2
for j, (k, txt, col) in enumerate(series):
    vals = [100 * H1["cells"][f"flip_incl b={bb} {k}"]["diff"] for bb in bands]; ps = [H1["cells"][f"flip_incl b={bb} {k}"]["p"] for bb in bands]
    pos = np.arange(5) + (j - 1.5) * w
    c.bar(pos, vals, w, color=col, label=txt)
    for p_, v_, ps_ in zip(pos, vals, ps):
        if ps_ < 0.05:
            c.text(p_, v_ + (0.3 if v_ >= 0 else -0.9), "*", ha="center", fontsize=10, color=INK)
c.axhline(0, color=INK, lw=0.8); c.set_xticks(range(5), [f"band ±{bb}" for bb in bands], fontsize=8)
c.set_ylabel("percentage points vs the shifted-level null"); c.legend(frameon=False, fontsize=7.5, loc="upper left")
pr = H1["PRIMARY (incl 0DTE, b 0.15%, up-approach)"]
c.set_title(f"TEST H1, 1,700 days 2020-Oct 12 2026 (pre-registered): the flip IS a real stall level\n"
            f"(40 versions, joint p < 0.002; * = p < 0.05). Highs stop there +{100*pr['up stall']['diff']:.1f} pts (p {pr['up stall']['p']:.2f}), lows +9-12 pts.\n"
            f"But closing back below is chance ({100*pr['up reject']['real']:.0f}% vs {100*pr['up reject']['null mean']:.0f}%): primary fails on that half", loc="left", fontsize=9, color=INK)
# D: split + H2
dd = ax[1, 1]
sp = H1["splits"]
items = [("short gamma\nat the open", sp["dealers short gamma at the open (incl 0DTE)"]), ("long gamma\nat the open", sp["dealers long gamma at the open"]),
         ("flip not near\na $5 strike", sp["flip NOT near a $5 multiple"]), ("2023-26", sp["2023-26"])]
for i, (lb, v) in enumerate(items):
    re_, nu_ = v["up stall real / null"]
    dd.bar(i - 0.18, 100 * re_, 0.34, color=ORANGE); dd.bar(i + 0.18, 100 * nu_, 0.34, color=GREY)
    dd.text(i, 100 * max(re_, nu_) + 1.2, ("p < 0.01" if v["p stall"] < 0.01 else f"p {v['p stall']:.2f}") + f"\n({v['up-reach events']} days)", ha="center", fontsize=7.5)
b0 = H2["by bucket (K* hit / others hit / K* n)"]["0"]
dd.bar(4.6 - 0.18, 100 * b0[0], 0.34, color=GREEN); dd.bar(4.6 + 0.18, 100 * b0[1], 0.34, color=GREY)
dd.text(4.6, 100 * max(b0[:2]) + 1.2, f"p {H2['p (diff <= 0)']:.2f}\n({H2['days']} days)", ha="center", fontsize=7.5)
dd.set_xticks(list(range(4)) + [4.6], [i[0] for i in items] + ["H2: close within $0.50\nof the biggest 0DTE strike\n(vs other strikes, <$1 away)"], fontsize=7.5)
dd.set_ylim(0, 62); dd.set_ylabel("% of days")
from matplotlib.patches import Patch
dd.legend(handles=[Patch(color=ORANGE, label="H1 up stall at the flip"), Patch(color=GREY, label="same, shifted-level null / other strikes"), Patch(color=GREEN, label="H2 biggest 0DTE strike")], frameon=False, fontsize=7.5, loc="upper right")
dd.set_title("Where the stall lives: mornings that START short gamma (43% vs 31%, p < 0.001);\n"
             "nothing when dealers start long. Not a round-number effect.\n"
             "H2: NO closing pin to the big 0DTE strike (31% vs 35%): the close is not explained", loc="left", fontsize=9, color=INK)
fig.savefig(OUT / "flip_wicks.png", dpi=140, bbox_inches="tight", facecolor=SURF)
