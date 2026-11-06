"""Figure for the M3 signature test: fade by class (S&P vs NDX+SOX) and second legs vs random signs."""
import json, numpy as np, pandas as pd
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
H = Path(__file__).resolve().parent; full = pd.read_pickle(H / "data" / "full.pkl"); R = json.load(open(H / "out" / "signature.json"))
A = json.load(open(H / "out" / "addendum.json"))["(3) O4 decay exponents, cluster bootstrap over dates"]
d = full[full.complete & (full.cls != "mid")]
SURF, INK, INK2, MUTED, GRID, BASE = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
BUILD, ABR = "#eb6834", "#2a78d6"   # validated pair (slots 2 and 1)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10.5, "axes.edgecolor": BASE, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.facecolor": SURF, "figure.facecolor": SURF})
fig, axs = plt.subplots(1, 3, figsize=(16, 7.0), gridspec_kw={"width_ratios": [1, 1, 0.9], "wspace": 0.28})
fig.subplots_adjust(left=0.05, right=0.985, top=0.73, bottom=0.2)
t = np.arange(1, 61)
for ax, (gname, sel, title) in zip(axs[:2], [("S&P", d["index"] == "S&P 500", "A. S&P 500 (short memory): both kinds fade alike"),
                                           ("NDX+SOX", d["index"].isin(["Nasdaq-100", "SOX"]), "B. Nasdaq-100 + chips (long memory):\nbuild-up shocks fade more slowly")]):
    for cl, col, lab in (("build-up", BUILD, "build-up before the shock"), ("abrupt", ABR, "abrupt (no build-up)")):
        g = d[sel & (d.cls == cl)]; cm = np.mean(np.vstack(g.cum.values), axis=0)
        ax.plot(t, cm, color=col, lw=2, label=f"{lab} (n={len(g)})")
        a = A[gname]["alpha " + cl]; ax.text(t[-1] * 1.03, cm[-1], f"decay\nexponent {a:.2f}", color=INK, fontsize=9.5, va="center")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(1, 140)
    ax.set_xlabel("sessions after the shock (log scale)"); ax.set_ylabel("cumulative excess volatility (log scale)")
    ax.grid(True, which="major", color=GRID, lw=0.8); ax.set_axisbelow(True)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.set_title(title, loc="left", color=INK, fontsize=12, pad=8)
    ci = A[gname]["90% CI of difference"]
    ax.text(0.03, 0.04, f"steeper curve = slower fade\ngap in exponent {A[gname]['abrupt minus build-up']:+.2f}, 90% CI [{ci[0]:+.2f}, {ci[1]:+.2f}]",
            transform=ax.transAxes, fontsize=9.5, color=INK2, va="bottom")
    ax.legend(loc="upper left", frameon=False, fontsize=9.5)
# panel C: second legs
ax = axs[2]; x = np.arange(2); w = 0.36
act = [R["H3"]["new-leg rate build-up / abrupt / middle"][0], R["H3"]["new-leg rate build-up / abrupt / middle"][1]]
exp_ = R["O2x excess new-leg rate over random-sign paths"]["expected rate build-up / abrupt"]
nb = (d.cls == "build-up").sum(); na = (d.cls == "abrupt").sum()
b1 = ax.bar(x - w / 2, act, w, color=[BUILD, ABR], label="actual")
b2 = ax.bar(x + w / 2, exp_, w, color=SURF, edgecolor=[BUILD, ABR], linewidth=2, label="random signs, same volatility")
for xi, v in zip(x - w / 2, act): ax.text(xi, v + 0.015, f"{v:.0%}", ha="center", fontsize=10, color=INK)
for xi, v in zip(x + w / 2, exp_): ax.text(xi, v + 0.015, f"{v:.0%}", ha="center", fontsize=10, color=INK2)
ax.set_xticks(x); ax.set_xticklabels([f"build-up\n(n={nb})", f"abrupt\n(n={na})"]); ax.set_ylim(0, 0.8)
ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0)); ax.set_ylabel("shocks followed by a second leg down")
ax.grid(True, axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True)
for s in ("top", "right"): ax.spines[s].set_visible(False)
ax.set_title("C. Second legs: about 50% either way,\nthe same as random signs would give", loc="left", color=INK, fontsize=12, pad=8)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=MUTED, label="actual"), Patch(facecolor=SURF, edgecolor=MUTED, linewidth=2, label="random signs, same volatility")],
          loc="upper right", frameon=False, fontsize=9.5)
lv = R["live forecast (score after day 89, ~2027-03)"]
fig.text(0.05, 0.94, "The shock's signature predicts how long the storm lasts, not whether a second leg comes", fontsize=16, weight="bold", color=INK)
fig.text(0.05, 0.9, "Down shocks (6x normal, isolated): S&P 1955-2026 (n=53), Nasdaq-100 1990- (30), SOX 1999- (18). Signature = volatility in the 10 days before vs the 60 before that,\n"
         "using only pre-shock data. Top third = build-up, bottom third = abrupt.", fontsize=10, color=INK2, va="top")
fig.text(0.05, 0.835, f"Nov 5, 2026 shock: build-up signature in all three (S&P {lv['S&P 500']['B']:.2f}, NDX {lv['Nasdaq-100']['B']:.2f}, SOX {lv['SOX']['B']:.2f}; "
         f"build-up cut-off about 1.2). Expect the volatility to fade slowly, most of all in NDX and chips; second-leg odds about 50%.", fontsize=10, color=INK)
fig.text(0.05, 0.05, "Fade test (pre-registered H1): build-up shocks keep more excess volatility a month later, median 0.32 vs 0.15 of the early excess, p = 0.049. All 18 variants point the same way; corrected joint p = 0.08. "
         "Memory condition (H2):\nsame direction as theory, not significant. Second legs (H3): no difference, p = 0.68. All 13 shocks dropped by the pre-registered rule were abrupt shocks whose volatility "
         "was already below normal within 20 days, i.e. the fastest fades.", fontsize=9, color=MUTED)
out = H / "out" / "signature_test.png"; fig.savefig(out, dpi=200); print(out)
