"""Order-flow study in one picture: out/order_flow.png (reads out/panel_v1.csv, out/sign_check.json, out/dips_flow.json)."""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import flows as Fl

BLUE, ORANGE, GREEN, RED, INK, MUTED, GRID, SURF = "#2a78d6", "#eb6834", "#1baf7a", "#d64545", "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"
P = pd.read_csv(Fl.OUT / "panel_v1.csv", index_col=0, parse_dates=True).dropna(subset=["zF_am", "r_am"])
S = json.loads((Fl.OUT / "sign_check.json").read_text())
J = json.loads((Fl.OUT / "dips_flow.json").read_text())
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
fig, (a, b) = plt.subplots(1, 2, figsize=(15.5, 6.2), gridspec_kw={"width_ratios": [1, 1.1], "wspace": 0.42})
a.scatter(P.zF_am.clip(-5, 5), 100 * P.r_am, s=8, color=BLUE, alpha=0.45)
a.axhline(0, color=MUTED, lw=0.6); a.axvline(0, color=MUTED, lw=0.6)
a.set_xlabel("'customer' net delta flow from minute-bar signing, morning (z)")
a.set_ylabel("SPY morning return, %")
c = np.corrcoef(P.zF_am, P.r_am)[0, 1]
sc = S["centred (t-1,t) [Amendment 1]"]
a.set_title(f"Signed 0DTE flow from minute bars is BACKWARDS (corr {c:+.2f}, 930 days)\n"
            f"Each trade's sign disagrees with its own option's price move on {sc['days negative']} of {sc['days']} days checked.\n"
            "Real signing needs tick data with the quote at each trade (higher ThetaData tier)", loc="left", fontsize=9.5, color=INK)
nm = J["new measures"]
lab = {"SPY Amihud illiquidity (pct)": "SPY illiquidity (Amihud)", "SPY relative volume (5d/60d)": "SPY relative volume",
       "SPY FINRA short ratio (pct)": "SPY off-exchange short ratio (FINRA)", "0DTE put/call volume (pct)": "0DTE put/call volume",
       "0DTE activity (5d/60d)": "0DTE activity"}
keys = list(lab)
vals = [nm[k]["AUC (either direction)"] for k in keys]
order = np.argsort(vals)
names = ["BREADTH (from before)"] + [lab[keys[i]] for i in order[::-1]]
v = [0.899] + [vals[i] for i in order[::-1]]
fw = J["best-of-all luck check"]["family-wise p"]
pv = [fw["share of panel above 50-day"]] + [fw[keys[i]] for i in order[::-1]]
y = np.arange(len(names))[::-1]
b.barh(y, v, color=[RED] + [MUTED] * (len(v) - 1), height=0.6)
for yi, vi, p in zip(y, v, pv):
    b.text(vi + 0.008, yi, f"{vi:.2f}  (luck p {p:.2f})", va="center", fontsize=8.5, color=INK)
b.axvline(0.5, color=INK, lw=0.8)
b.set_yticks(y, names)
b.set_xlim(0.45, 1.05)
b.set_xlabel("separates channel corrections from bounces at the dip's start (AUC)")
L = J["leave-one-dip-out AUC"]
b.set_title(f"Order-flow and liquidity measures that need no trade sign add nothing beyond breadth\n"
            f"(best-of-39 luck check; breadth alone {L['breadth alone']:.2f} on unseen dips, every 'breadth + X' lower).\n"
            f"Today: SPY off-exchange short ratio at its highest of all 22 dip starts (dark-pool buying), bounce side", loc="left", fontsize=9.5, color=INK)
fig.savefig(Fl.OUT / "order_flow.png", dpi=140, bbox_inches="tight", facecolor=SURF)
