"""SPY gamma map after Friday Oct 23: out/spy_gamma_map.png (reads out/profile.csv, out/strikes.csv, out/daily.csv, out/levels.json)."""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import spy_gamma as G

BLUE, ORANGE, GREEN, RED, INK, MUTED, GRID, SURF = "#2a78d6", "#eb6834", "#1baf7a", "#d64545", "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"
P = pd.read_csv(G.OUT / "profile.csv")
K = pd.read_csv(G.OUT / "strikes.csv", index_col=0)["dealer GEX $"] / 1e9
D = pd.read_csv(G.OUT / "daily.csv", index_col=0, parse_dates=True)
eng = pd.read_csv(G.t.OUT / "td_gamma_SPY.csv", parse_dates=["date"]).set_index("date")
L = json.loads((G.OUT / "levels.json").read_text())["after Friday Oct 23 close (OI positions at Oct 22 close)"]
S, F = L["spot (parity)"], L["flip"]
ratio = S / 7623.68
hi_spy, lo_spy = 7818.93 * ratio, 7427.98 * ratio
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
fig, (a, b) = plt.subplots(1, 2, figsize=(15.5, 6.6), gridspec_kw={"width_ratios": [1.45, 1], "wspace": 0.32})
k = K[(K.index >= 0.95 * S) & (K.index <= 1.06 * S)]
a.bar(k.index, k.to_numpy(), width=0.8, color=[GREEN if v > 0 else RED for v in k.to_numpy()], alpha=0.85, label="dealer gamma at each strike ($bn per 1%)")
a2 = a.twinx()
a2.plot(P.price, P["total dealer GEX $bn per 1%"], color=INK, lw=1.8, label="total dealer gamma if SPY were here ($bn per 1%)")
a2.axhline(0, color=INK, lw=0.6, ls=":")
a2.spines["top"].set_visible(False)
for x, col, lab, yy in [(S, ORANGE, f"SPY {S:.0f}", 0.97), (F, INK, f"flip {F:.0f}", 0.90), (750, RED, "put wall 750", 0.83), (hi_spy, GREEN, f"S&P new high = SPY {hi_spy:.0f}", 0.76),
                        (lo_spy, RED, f"S&P -5% = SPY {lo_spy:.0f}", 0.69)]:
    a.axvline(x, color=col, lw=1.4 if lab.startswith(("SPY", "flip")) else 1, ls="-" if lab.startswith(("SPY", "flip")) else "--")
    a.text(x + 0.4, a.get_ylim()[1] * yy if False else 0, "", fontsize=8)
ymax = max(abs(k.min()), k.max()) * 1.15
a.set_ylim(-ymax, ymax * 0.55)
for x, col, lab, frac in [(S, ORANGE, f"SPY {S:.0f}", 0.47), (F, INK, f"flip {F:.0f}", 0.47), (750, RED, "put wall 750", 0.40), (hi_spy, GREEN, f"S&P new high\n= SPY {hi_spy:.0f}", 0.33),
                          (lo_spy, RED, f"S&P -5%\n= SPY {lo_spy:.0f}", 0.33)]:
    a.text(x + 0.5, ymax * frac, lab, fontsize=8, color=col, va="top")
a.set_xlabel("SPY price")
a.set_ylabel("dealer gamma at strike, $bn per 1% move")
a2.set_ylabel("total dealer gamma, $bn per 1% move")
h1, l1 = a.get_legend_handles_labels(); h2, l2 = a2.get_legend_handles_labels()
a.legend(h1 + h2, l1 + l2, loc="lower right", frameon=False, fontsize=8)
a.set_title(f"SPY after Friday's close: {S:.0f}, {abs(L['spot vs flip %']):.1f}% BELOW the flip ({F:.0f}); dealers short ${abs(L['total dealer GEX $bn per 1%']):.0f}bn per 1%\n"
            "745-760: dealers most short gamma, so moves get amplified. Above 774 they turn long gamma\n"
            "(moves damped); 780 = biggest positive-gamma strike = where the S&P makes a new high", loc="left", fontsize=9.5, color=INK)
h = pd.concat([eng[["spot", "flip_classic"]], D[["spot", "flip_classic"]]])
h = h[~h.index.duplicated(keep="last")].sort_index()
h = h[h.index >= "2026-08-01"]
b.plot(h.index, h.spot, color=ORANGE, lw=1.8, label="SPY close")
b.plot(h.index, h.flip_classic, color=INK, lw=1.4, ls="--", label="gamma flip")
b.fill_between(h.index, h.spot, h.flip_classic, where=h.spot < h.flip_classic, color=RED, alpha=0.15, label="below flip (dealers short gamma)")
b.legend(loc="lower left", frameon=False, fontsize=8)
b.set_ylabel("SPY")
import matplotlib.dates as mdates
b.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
cc = json.loads((G.OUT / "levels.json").read_text())["channel check"]
b.set_title(f"Below the flip since Oct 14, sinking further below it\nAt channel dip starts the flip does NOT tell corrections from bounces (AUC {cc['AUC (corrections closer to/below flip)']:.2f}):\n"
            f"almost every dip starts below it (corrections {cc['corrections below flip']}, bounces {cc['bounces below flip']})", loc="left", fontsize=9.5, color=INK)
fig.savefig(G.OUT / "spy_gamma_map.png", dpi=140, bbox_inches="tight", facecolor=SURF)
print("SPY equivalents:", round(hi_spy, 1), round(lo_spy, 1))
