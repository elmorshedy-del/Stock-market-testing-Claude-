"""Options-regime figure. Usage: python figure_regimes.py -> out/regimes.png"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent; O = HERE / "out"; R = json.load(open(O / "regimes.json"))
INK, INK2, GRID = "#0b0b0b", "#52514e", "#d9d8d4"; C0, C1, C2 = "#bbbbbb", "#eb6834", "#2a78d6"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2})
fig, ax = plt.subplots(2, 2, figsize=(14, 9.2)); plt.subplots_adjust(hspace=0.5, wspace=0.3)
D, W = R["descriptive_by_regime"], R["within_options_era"]; eras = ["2018-19", "2020-21", "2022-26"]


def clean(a):
    for s in ("top", "right"): a.spines[s].set_visible(False)
    a.grid(axis="y", color=GRID, lw=0.6); a.set_axisbelow(True)


a = ax[0, 0]; x = np.arange(3)
e = [100 * D[f"earnings-gap VF rate {k}"]["earnings"] for k in eras]; o = [100 * D[f"earnings-gap VF rate {k}"]["other"] for k in eras]; n = [D[f"earnings-gap VF rate {k}"]["n_earnings"] for k in eras]
a.bar(x - 0.2, o, 0.38, color=C0, label="other gap-ups"); a.bar(x + 0.2, e, 0.38, color=C1, label="earnings-morning gap-ups")
for i in range(3): a.text(x[i] + 0.2, e[i] + 0.8, f"{e[i]:.0f}%\nn={n[i]}", ha="center", fontsize=8, color=INK); a.text(x[i] - 0.2, o[i] + 0.8, f"{o[i]:.0f}%", ha="center", fontsize=8, color=INK)
a.set_xticks(x); a.set_xticklabels(eras, color=INK); a.set_ylim(0, 38); a.set_ylabel("% violent first-hour fades"); a.legend(fontsize=8, frameon=False); clean(a)
a.set_title("(a) The earnings-morning fade got stronger in the options era\n(12 stocks)", loc="left", color=INK, fontsize=10)
a = ax[0, 1]; rho = [D[f"09:35 rule {k}"]["rho(first5, next55)"] for k in eras]; pu = [100 * D[f"09:35 rule {k}"]["P(next55 up | first5 >= +0.25 sigma)"] for k in eras]
a.bar(x, rho, 0.55, color=[C0, C1, C2])
for i in range(3): a.text(x[i], rho[i] + 0.004, f"ρ {rho[i]:.2f}\nstrong first 5 min → up {pu[i]:.0f}%", ha="center", fontsize=8, color=INK)
a.set_xticks(x); a.set_xticklabels(eras, color=INK); a.set_ylim(0, 0.16); a.set_ylabel("Spearman, first 5 min vs next 55 min"); clean(a)
a.set_title("(b) The 09:35 read weakened after 2020 (13 names, all gap-ups)", loc="left", color=INK, fontsize=10)
a = ax[1, 0]; keys = [k for k in W if k.startswith("house-of-cards")]
for i, k in enumerate(keys):
    v = W[k]; a.bar(i * 3, v["call7_median_not"], color=C0, width=0.9); a.bar(i * 3 + 1, v["call7_median_forced"], color=C1, width=0.9)
    a.text(i * 3, v["call7_median_not"] + (0.4 if v["call7_median_not"] >= 0 else -1.2), f"{v['call7_median_not']:+.1f}%", ha="center", fontsize=8, color=INK)
    a.text(i * 3 + 1, v["call7_median_forced"] + (0.4 if v["call7_median_forced"] >= 0 else -1.2), f"{v['call7_median_forced']:+.1f}%", ha="center", fontsize=8, color=INK)
    a.text(i * 3 + 0.5, -6.5, f"stock open→close {v['est']:+.2f}σ, p {v['p']:.2f}\nn forced {v['n_forced']}", ha="center", fontsize=8, color=INK2)
a.axhline(0, color=INK2, lw=0.8); a.set_xticks([0.5, 3.5]); a.set_xticklabels(["2020-21 (retail-call boom)", "2022-26 (0DTE era)"], color=INK); a.set_ylim(-8, 13); a.set_ylabel("7-day ATM call, gap open → close, median %"); clean(a)
a.set_title("(c) Gap day after a price-up + implied-vol-up run (orange) vs other gap days (grey):\nthe effect lived mostly in 2020-21", loc="left", color=INK, fontsize=10)
a = ax[1, 1]; ks = [("X4 call skew vs permanence, R1 2020-21", "call skew, 2020-21"), ("X4 call skew vs permanence, R2 2022-26", "call skew, 2022-26"),
                     ("ATM IV proxy vs permanence, R1 2020-21", "ATM IV, 2020-21"), ("ATM IV proxy vs permanence, R2 2022-26", "ATM IV, 2022-26")]
for i, (k, lab) in enumerate(ks):
    v = W[k]; a.plot([i, i], v["ci95"], color=INK2, lw=1.6); a.plot(i, v["est"], "o", ms=9, color=C2 if "skew" in lab else C0, mec=INK)
    a.text(i + 0.08, v["est"], f"ρ {v['est']:+.2f}\np {v['p']:.3f}\nn={v['n']}", fontsize=8, color=INK, va="center")
a.axhline(0, color=INK2, lw=0.8); a.set_xticks(range(4)); a.set_xticklabels([l for _, l in ks], color=INK, fontsize=8.5); a.set_ylabel("Spearman with permanence P20\n(negative = the run fades)"); clean(a)
a.set_title("(d) Call-skew richening predicts that a run fades in the 0DTE era, not in 2020-21\n(TSLA, NVDA, QQQ, MSFT, MU)", loc="left", color=INK, fontsize=10)
fig.suptitle("Options regimes: what changed after 2020 (pre-2020 single-stock options need ThetaData Standard)", fontsize=12, color=INK, x=0.01, ha="left")
fig.savefig(O / "regimes.png", dpi=130, bbox_inches="tight", facecolor="#fcfcfb"); print("saved")
