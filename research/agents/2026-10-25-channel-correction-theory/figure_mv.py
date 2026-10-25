"""Amendment 3 in one picture: out/multivariate.png, plus the post hoc 'latest week' readings (Oct 19-23) -> out/latest_week.json.
Usage: python figure_mv.py <etfs folder>"""
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import dossier as Dz
import multivar as Mv

BLUE, ORANGE, GREEN, RED, INK, MUTED, GRID, SURF = "#2a78d6", "#eb6834", "#1baf7a", "#d64545", "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"
etfs = sys.argv[1]
R = json.loads((Dz.OUT / "multivar.json").read_text())
D, dist, oil = Mv.frame(etfs)
idx = D.index
ref = (idx >= Dz.CH0) & (idx <= Dz.CH1) & (dist >= -0.03).to_numpy()
mu, sd = D[ref].mean(), D[ref].std()
z_now = ((D.iloc[-5:].mean() - mu) / sd)
for k in Mv.EVENTVARS:
    z_now[k] = ((D[k].iloc[-1] - mu[k]) / sd[k])
F = pd.read_csv(Dz.OUT / "multivar_features.csv", index_col=0)
dec = [k for k in F.index if not k.startswith("open")]
y = np.array([k.startswith("corr") for k in dec]).astype(int)
feats = list(F.columns)
X = F.loc[dec].fillna(0).to_numpy(float)
jb = [feats.index("share of panel above 50-day")]
p0, _ = Mv.fit_predict(X[:, jb], y, z_now[feats].fillna(0).to_numpy(float)[None, jb], 1.0)
comp_now = sum(s * z_now[k] for k, s in Mv.M1.items())
cvals = sum(s * F.loc[dec, k] for k, s in Mv.M1.items()).to_numpy(float)
latest = {"M0 breadth P(correction), latest week": float(p0[0]), "M1 composite percentile among 21 dips, latest week": float((cvals < comp_now).mean()),
          "M1 terms, latest week": {k: round(float(s * z_now[k]), 2) for k, s in Mv.M1.items()},
          "raw": {"breadth (share above 50-day)": float(D["share of panel above 50-day"].iloc[-1]), "WTI": float(oil.iloc[-1]),
                  "WTI 20-day %": float(100 * D["oil 20-day"].iloc[-1]), "gold 20-day %": float(100 * D["gold (20d)"].iloc[-1]),
                  "TLT 20-day %": float(100 * D["bonds TLT (20d)"].iloc[-1]), "USD/JPY 20-day %": float(100 * D["yen 20-day (USD/JPY change)"].iloc[-1])}}
(Dz.OUT / "latest_week.json").write_text(json.dumps(latest, indent=1))
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
fig, (a, b) = plt.subplots(1, 2, figsize=(15.5, 6), gridspec_kw={"width_ratios": [1, 1.15], "wspace": 0.45})
L = R["leave-one-dip-out AUC"]["lambda 1.0"]
names = ["M0 breadth alone", "M1 theory composite\n(7 drivers, no fitting)", "M3 best-3 stack", "M2 everything (34)"]
vals = [L["M0 breadth alone"], R["M1 theory composite AUC (no fitting)"], L["M3 best-3 stack"], L["M2 ridge, all 34"]]
cols = [RED, BLUE, MUTED, MUTED]
yy = np.arange(4)[::-1]
a.barh(yy, vals, color=cols, height=0.6)
for yi, v in zip(yy, vals):
    a.text(v + 0.01, yi, f"{v:.2f}", va="center", fontsize=9, color=INK)
a.axvline(0.5, color=INK, lw=0.8)
a.set_yticks(yy, names)
a.set_xlim(0.45, 1)
a.set_xlabel("accuracy on dips the model did NOT see (leave-one-out AUC; 0.5 = coin flip)")
a.set_title("Adding variables makes it WORSE: with 21 dips, more inputs = more overfitting.\nBreadth alone stays the best model (same lesson as the earlier S&P multivariate)", loc="left", fontsize=9.5, color=INK)
show = ["share of panel above 50-day", "bonds TLT (20d)", "yen 20-day (USD/JPY change)", "oil 20-day", "gold (20d)", "FOMC within next 10 sessions", "margin debt vs prices"]
lab = ["breadth (crowded)", "bonds falling (rates)", "yen firming (carry)", "oil rising", "gold rising", "Fed decision within 10 sessions", "margin debt vs prices"]
zs = [Mv.M1[k] * z_now[k] for k in show]
au = R["univariate: new variables"]
ar = {k: v for k, v in R["univariate: top 6 of all 34 (AUC, best-of-34 p)"].items()}
yy = np.arange(len(show))[::-1]
b.barh(yy, zs, color=[RED if v > 0 else GREEN for v in zs], height=0.6)
b.axvline(0, color=INK, lw=0.8)
b.set_yticks(yy, lab)
for yi, k, v in zip(yy, show, zs):
    hist = {"share of panel above 50-day": "AUC 0.90", "bonds TLT (20d)": "AUC 0.70 (wrong way)", "yen 20-day (USD/JPY change)": "AUC 0.78",
            "oil 20-day": f"AUC {au['oil 20-day']['AUC (either direction)']:.2f}", "gold (20d)": f"AUC {au['gold (20d)']['AUC (either direction)']:.2f}",
            "FOMC within next 10 sessions": f"AUC {au['FOMC within next 10 sessions']['AUC (either direction)']:.2f}", "margin debt vs prices": "AUC 0.57"}[k]
    b.text(v + (0.06 if v >= 0 else -0.06), yi, hist, va="center", ha="left" if v >= 0 else "right", fontsize=8, color=MUTED)
b.set_xlim(-3.2, 3.2)
b.set_xlabel("this week's push toward CORRECTION (red, right) or BOUNCE (green, left), z")
rw = latest["raw"]
b.set_title(f"This week's drivers (Oct 19-23): oil +{rw['WTI 20-day %']:.0f}% (WTI ${rw['WTI']:.0f}), gold {rw['gold 20-day %']:+.0f}%, Fed Wed.\n"
            f"The ones that never separated dips (oil, gold, Fed timing) are pushing; breadth, the one that did, says bounce\n"
            f"Breadth model P(correction): {100 * latest['M0 breadth P(correction), latest week']:.0f}% (base rate 38%)", loc="left", fontsize=9.5, color=INK)
fig.savefig(Dz.OUT / "multivariate.png", dpi=140, bbox_inches="tight", facecolor=SURF)
print(json.dumps(latest, indent=1))
