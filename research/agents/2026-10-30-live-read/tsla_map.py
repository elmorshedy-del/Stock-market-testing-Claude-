"""out/tsla_400_map.png: does TSLA's structure pull it back to 400? Total dealer gamma on a price axis (Friday with the
Oct 30 expiry vs Monday), the key levels, and how much of the 400 'glue' leaves with Friday's expiry. Usage: python tsla_map.py"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent; OUT = HERE / "out"
C = json.loads((OUT / "curves.json").read_text()); M = json.loads((OUT / "maps.json").read_text())
GREEN, RED, INK, MUTED, SURF, BLUE, AMBER = "#1baf7a", "#d64545", "#0b0b0b", "#52514e", "#fcfcfb", "#2a78d6", "#e8a33d"
plt.rcParams.update({"font.size": 10.5, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED, "text.parse_math": False,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
fig, (a, b) = plt.subplots(1, 2, figsize=(16, 10), gridspec_kw={"width_ratios": [1.5, 1], "wspace": 0.25})
YLO, YHI = 345, 432
fr = C["TSLA | Friday Oct 30 (incl. the expiry) | close Oct 29"]; mo = C["TSLA | Monday Nov 2 (after the expiry) | close Oct 29"]
a.plot(fr["total gamma $bn"], fr["price"], color=INK, lw=2.4, label="Friday (with the Oct 30 expiry)")
a.plot(mo["total gamma $bn"], mo["price"], color=BLUE, lw=1.8, ls="--", label="Monday (expiry gone)")
a.fill_betweenx(fr["price"], fr["total gamma $bn"], 0, color=GREEN, alpha=0.10)
a.axvline(0, color=MUTED, lw=0.8); a.set_xlim(-0.05, 1.45); a.set_ylim(YLO, YHI)
ZONES = [(400, YHI, GREEN, "ABOVE 400: strongest damping\n(total-gamma peak ~420)"),
         (371, 400, AMBER, "371–400: still cushioned (dealers buy dips),\nbut the cushion thins as price falls"),
         (YLO, 371, RED, "BELOW 371 (flip): cushion gone")]
for lo, hi, col, lab in ZONES:
    a.axhspan(lo, hi, color=col, alpha=0.05, lw=0); a.text(1.43, (lo + hi) / 2, lab, ha="right", va="center", fontsize=10, color=col, weight="bold")
LEV = [(420, "420 total-gamma peak (magnet)", GREEN, "--"), (400, "400: biggest + strike, call wall, round number", GREEN, "-"),
       (397.45, "397.45 after hours", RED, ":"), (395, "395", MUTED, ":"), (388.7, "~389 old triple top (stops sat here)", MUTED, "--"),
       (371, "371 flip", RED, "-"), (350, "350 put wall", RED, "--")]
for y, lab, col, ls in LEV:
    a.axhline(y, color=col, lw=1.5 if ls == "-" else 1.0, ls=ls); a.text(0.0, y + 0.5, " " + lab, fontsize=9.2, color=col, va="bottom")
a.set_xlabel("dealer gamma, $bn per 1% move (positive = dealers sell rips, buy dips)"); a.set_ylabel("TSLA price")
a.legend(loc="lower right", frameon=False, fontsize=9.5)
a.set_title("1. TSLA dealers are long gamma everywhere above 371", loc="left", fontsize=13, weight="bold", color=INK)

# right: how much glue leaves Friday
lab = ["400 strike\nalone", "total gamma\nat 400", "total gamma\nat 395", "total gamma\nat 389"]
p, g = np.array(fr["price"]), np.array(fr["total gamma $bn"]); pm, gm = np.array(mo["price"]), np.array(mo["total gamma $bn"])
fri = [M["TSLA"]["Friday Oct 30 (incl. the expiry) @ close Oct 29 403.3"]["top positive strikes"]["400.0"], np.interp(400, p, g), np.interp(395, p, g), np.interp(389, p, g)]
mon = [M["TSLA"]["Monday Nov 2 (after the expiry) @ close Oct 29 403.3"]["top positive strikes"]["400.0"], np.interp(400, pm, gm), np.interp(395, pm, gm), np.interp(389, pm, gm)]
x = np.arange(len(lab)); b.bar(x - 0.2, fri, 0.38, color=INK, label="Friday"); b.bar(x + 0.2, mon, 0.38, color=BLUE, label="Monday")
for i in range(len(lab)):
    b.text(x[i] - 0.2, fri[i] + 0.01, f"{fri[i]:.2f}", ha="center", fontsize=9); b.text(x[i] + 0.2, mon[i] + 0.01, f"{mon[i]:.2f}", ha="center", fontsize=9, color=BLUE)
    b.text(x[i], max(fri[i], mon[i]) + 0.07, f"−{1 - mon[i] / fri[i]:.0%}", ha="center", fontsize=10.5, color=RED, weight="bold")
b.set_xticks(x); b.set_xticklabels(lab); b.set_ylabel("$bn per 1% move"); b.legend(frameon=False); b.set_ylim(0, 0.8)
b.set_title("2. The 400 'glue' mostly leaves with Friday's expiry", loc="left", fontsize=13, weight="bold", color=INK)
fig.suptitle("TSLA: does the structure pull it back to 400?  Friday: yes, it's sticky.  Monday on: much weaker, and TSLA is 'freed'", x=0.01, ha="left", fontsize=14.5, weight="bold", color=INK)
fig.text(0.01, 0.01, "Tested: TSLA call gamma damps next-day ranges (p < 0.001; weaker since 2023, p 0.10). Day highs cluster just under round numbers and lows just above them (p 2e-15 / 5e-5).\n"
         "Not tested on TSLA: a closing pin. SPY 0DTE showed none. If SPY flushes, TSLA trades as S&P beta (correlation 0.62 at low S&P gamma vs 0.35). Positions: OI dated Oct 28, ±1 strike.", fontsize=9.5, color=MUTED)
fig.savefig(OUT / "tsla_400_map.png", dpi=125, bbox_inches="tight"); print("ok")
