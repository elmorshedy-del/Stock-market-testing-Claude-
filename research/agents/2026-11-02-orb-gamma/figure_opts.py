"""A5 figure: (a) return on premium by structure vs shares; (b) where the option edge goes (mid-to-mid decomposition + spread). -> out/orb_opts.png"""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent; O = HERE / "out"
BG, INK, INK2, GRID, GRAY, BLUE, ORANGE = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#a9a8a3", "#2a78d6", "#eb6834"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": GRAY, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "axes.titleweight": "bold", "axes.titlesize": 11})
it = json.load(open(O / "opts_itm.json")); dg = json.load(open(O / "opts_diag.json"))
fig, ax = plt.subplots(1, 2, figsize=(13.5, 5.4), facecolor=BG, gridspec_kw={"width_ratios": [1.15, 1]})
for a in ax: a.set_facecolor(BG); a.grid(True, axis="y", color=GRID, lw=0.8); a.spines[["top", "right"]].set_visible(False)
a = ax[0]
keys = [("next 0 strikes ITM", "ATM\nnext expiry"), ("next 2 strikes ITM", "2 ITM\nnext"), ("next 4 strikes ITM", "4 ITM\nnext"),
        ("0dte 0 strikes ITM", "ATM\n0DTE"), ("0dte 2 strikes ITM", "2 ITM\n0DTE"), ("0dte 4 strikes ITM", "4 ITM\n0DTE")]
v = [it[k]["mean %"] for k, _ in keys]; md = [it[k]["median %"] for k, _ in keys]; x = np.arange(len(keys))
a.bar(x - 0.2, v, 0.4, color=[BLUE] * 3 + [ORANGE] * 3, label="mean return on premium per trade")
a.bar(x + 0.2, md, 0.4, color=GRAY, label="median (the typical trade)")
for xi, (k, _) in zip(x, keys): a.text(xi - 0.2, it[k]["mean %"] + (1 if it[k]["mean %"] >= 0 else -1), f"{it[k]['mean %']:+.1f}%\nt {it[k]['t-stat']:.1f}", ha="center", va="bottom" if it[k]["mean %"] >= 0 else "top", fontsize=8.5)
a.set_ylim(-56, 26); a.axhline(0, color=INK2, lw=1); a.set_xticks(x, [l for _, l in keys], fontsize=9); a.set_ylabel("% of premium per trade")
a.legend(frameon=False, fontsize=8.5, loc="lower left")
a.set_title("(a) TSLA breakout with options, 2024-26: next-expiry options break even;\n0DTE averages +7 to +12% but not significant and lumpy (2025 only)", loc="left")
a = ax[1]
lev = dg["fit: leverage (option % per 1% stock move)"] * dg["mean directional stock move during the trade %"]
drift = dg["fit: zero-move drift per trade % (time decay + IV change)"]; mid = dg["mean option return, mid to mid %"]; conv = mid - lev - drift; spr = dg["spread cost per round trip (mean fill - mid) %"]
steps = [("stock move x\nleverage (26x)", lev), ("convexity\n(IV falls on\nbig moves)", conv), ("time decay +\nIV drift", drift), ("bid-ask\nspread", spr)]
cum = 0
for i, (nm, val) in enumerate(steps):
    a.bar(i, val, bottom=cum, color=ORANGE if val > 0 else BLUE); a.text(i, cum + val + (0.15 if val >= 0 else -0.15), f"{val:+.1f}%", ha="center", va="bottom" if val >= 0 else "top", fontsize=9)
    cum += val
a.bar(len(steps), cum, color=INK2); a.text(len(steps), cum + 0.15, f"{cum:+.1f}%", ha="center", va="bottom", fontsize=9, fontweight="bold")
a.set_ylim(-0.6, 4.6); a.axhline(0, color=INK2, lw=1); a.set_xticks(range(len(steps) + 1), [s for s, _ in steps] + ["what you\nkeep"], fontsize=8.5); a.set_ylabel("% of premium per trade (ATM, next expiry)")
a.set_title("(b) Where the edge goes: the breakout earns ~+3.7% on premium,\nbut the spread (~2.2%) and big-move IV drop take almost all of it", loc="left")
fig.suptitle("Breakout with calls/puts instead of shares: the share edge does not survive the option costs", x=0.01, ha="left", fontsize=13.5, fontweight="bold", color=INK)
fig.text(0.01, 0.01, "ThetaData 1-min option bars and quotes; buy at ask (next-minute quote), sell at bid at the underlying stop or 15:55. Shares on the same 702 days: +16.8 bp/trade. Pre-registered A5 (ATM); ITM variants exploratory.", fontsize=8, color=INK2)
plt.tight_layout(rect=(0, 0.04, 1, 0.92)); plt.savefig(O / "orb_opts.png", dpi=150, facecolor=BG)
