"""Figure for test #4 (crash law): the volume bound, the five crashes, the Nov 5 close check."""
import json
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

H = Path(__file__).resolve().parent
R = json.load(open(H / "out" / "crash.json")); B = pd.read_csv(H / "out" / "days.csv")
SURF, INK, INK2, MUTED, GRID, BASE, SHADE = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#f1f0ec"
SQ, NOW, LIN = "#2a78d6", "#1baf7a", "#eb6834"   # validated slots 1, 3, 2 (all pairs pass; aqua needs labels -> labelled)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10.5, "axes.edgecolor": BASE, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.facecolor": SURF, "figure.facecolor": SURF})
fig, axs = plt.subplots(1, 3, figsize=(17, 7.6), gridspec_kw={"width_ratios": [1.05, 1.15, 0.95], "wspace": 0.42})
fig.subplots_adjust(left=0.055, right=0.985, top=0.75, bottom=0.22)


def tidy(ax):
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.set_axisbelow(True)


# ---- A: volume bound ----
ax = axs[0]
cols = [("F_sqrt", SQ, "Square root,\nnormal month"), ("F_now", NOW, "Square root,\nweek before"), ("F_lin", LIN, "Linear\n(Kyle–Obizhaeva)")]
ax.axhspan(1, 300, color=SHADE, zorder=0)
ax.axhline(1, color=INK2, lw=1.2, zorder=1)
ax.text(2.55, 1.15, "the day's entire volume,\nall of it net selling", fontsize=9, color=INK2, va="bottom", ha="right")
ax.text(-0.45, 150, "impossible: needs more\nselling than all trading", fontsize=9.5, color=INK2, va="top")
jit = (np.arange(len(B)) % 9 - 4) * 0.035
for i, (c, col, lab) in enumerate(cols):
    ax.scatter(i + jit, B[c], s=34, color=col, edgecolor=SURF, linewidth=0.9, zorder=3)
    m = B[c].median()
    ax.plot([i - 0.25, i + 0.25], [m, m], color=INK, lw=2, zorder=4)
    txt = f"median {m:.1f}×" if m >= 1 else f"median {100*m:.0f}%"
    ax.text(i, m / 2.1, txt, fontsize=9.5, color=INK, va="center", ha="center", zorder=6,
            bbox=dict(boxstyle="round,pad=0.15", fc=SURF, ec="none", alpha=0.9))
nov = B[B.date == "2026-11-05"].iloc[0]
for i, (c, _, _) in enumerate(cols):
    ax.scatter(i + jit[B.index[B.date == "2026-11-05"][0]], nov[c], s=120, facecolor="none", edgecolor=INK, linewidth=1.3, zorder=5)
ax.annotate("Nov 5, 2026", (jit[B.index[B.date == "2026-11-05"][0]], nov["F_sqrt"]), xytext=(-0.42, 40), fontsize=9, color=INK,
            arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))
ax.set_yscale("log"); ax.set_ylim(0.01, 300); ax.set_xlim(-0.5, 2.9)
ax.set_xticks(range(3)); ax.set_xticklabels([c[2] for c in cols])
ax.set_yticks([0.01, 0.1, 1, 10, 100]); ax.set_yticklabels(["1%", "10%", "1×", "10×", "100×"])
ax.set_ylabel("net selling the law needs, as a share of the day's total volume")
ax.grid(True, axis="y", which="major", color=GRID, lw=0.8); tidy(ax)
ax.set_title("A. Every big S&P down day since 1955 (54):\nthe square-root law needs impossible selling", loc="left", color=INK, fontsize=12, pad=8)

# ---- B: five documented crashes ----
ax = axs[1]
A = R["Part A"]
names = ["1929 crash", "1987 crash", "1987 Soros", "2008 SocGen", "2010 flash crash"]
lab = {"1929 crash": "1929 crash\n(margin sales)", "1987 crash": "1987 crash\n(portfolio insurance)", "1987 Soros": "Oct 22, 1987\n(Soros futures sale)",
       "2008 SocGen": "2008 SocGen\n(Kerviel unwind)", "2010 flash crash": "2010 flash crash\n(75,000 E-minis)"}
y = np.arange(len(names))[::-1]
for yi, nm in zip(y, names):
    a = next(e for e in A if e["event"] == nm)
    vals = [a["SQRT %"], a["SQRT-now %"], a["LIN %"], a["actual %"]]
    ax.plot([min(vals), max(vals)], [yi, yi], color=GRID, lw=2, zorder=1)
    ax.scatter(a["SQRT %"], yi + 0.12, s=60, color=SQ, edgecolor=SURF, linewidth=1.2, zorder=3)
    ax.scatter(a["SQRT-now %"], yi - 0.12, s=60, color=NOW, edgecolor=SURF, linewidth=1.2, zorder=3)
    ax.scatter(a["LIN %"], yi, s=60, color=LIN, edgecolor=SURF, linewidth=1.2, zorder=3)
    ax.scatter(a["actual %"], yi, s=95, marker="D", color=INK, edgecolor=SURF, linewidth=1.2, zorder=4)
    ax.text(a["actual %"] * 1.25, yi + 0.18, f"{a['actual %']:g}% actual", fontsize=9, color=INK, va="bottom")
    lo, hi = sorted([a['SQRT-now sale needed (x documented)'], a['SQRT sale needed (x documented)']])
    ax.text(0.105, yi - 0.36, f"square root needs {lo:.0f}–{hi:.0f}× the documented sale; linear {a['LIN sale needed (x documented)']:.1f}×",
            fontsize=8.3, color=INK2, va="center")
ax.set_xscale("log"); ax.set_xlim(0.1, 150); ax.set_ylim(-0.7, len(names) - 0.4)
ax.set_yticks(y); ax.set_yticklabels([lab[n] for n in names], fontsize=9.5)
ax.set_xticks([0.1, 1, 10, 100]); ax.set_xticklabels(["0.1%", "1%", "10%", "100%"])
ax.set_xlabel("price fall (log scale)")
ax.grid(True, axis="x", color=GRID, lw=0.8); tidy(ax)
ax.legend(handles=[Line2D([], [], marker="D", ls="", color=INK, ms=8, label="actual fall"),
                   Line2D([], [], marker="o", ls="", color=LIN, ms=8, label="linear law (Kyle–Obizhaeva)"),
                   Line2D([], [], marker="o", ls="", color=SQ, ms=8, label="square root, normal month"),
                   Line2D([], [], marker="o", ls="", color=NOW, ms=8, label="square root, week before")],
          loc="upper center", bbox_to_anchor=(0.45, -0.1), ncol=2, frameon=False, fontsize=9.3)
ax.set_title("B. Five crashes with documented selling:\nonly the linear law gets the size", loc="left", color=INK, fontsize=12, pad=8)

# ---- C: Nov 5 close check ----
ax = axs[2]
Cc = R["Part C"]["Nov 5 check (predicted close move % from the LETF flow vs actual 15:30->close)"]
rows = [("S&P 500\n(whole market)", abs(Cc["whole market (3 complexes summed)"]["actual SPX"]), abs(Cc["whole market (3 complexes summed)"]["SQRT market"]), abs(Cc["whole market (3 complexes summed)"]["LIN market"])),
        ("Nasdaq-100", abs(Cc["NDX"]["actual"]), abs(Cc["NDX"]["SQRT complex"]), abs(Cc["NDX"]["LIN complex"])),
        ("Semis", abs(Cc["SEMIS"]["actual"]), abs(Cc["SEMIS"]["SQRT complex"]), abs(Cc["SEMIS"]["LIN complex"]))]
y = np.arange(len(rows))[::-1]
for yi, (nm, act, sq, li) in zip(y, rows):
    ax.plot([min(act, sq, li), max(act, sq, li)], [yi, yi], color=GRID, lw=2, zorder=1)
    ax.scatter(sq, yi + 0.1, s=60, color=SQ, edgecolor=SURF, linewidth=1.2, zorder=3)
    ax.scatter(li, yi, s=60, color=LIN, edgecolor=SURF, linewidth=1.2, zorder=3)
    ax.scatter(act, yi, s=95, marker="D", color=INK, edgecolor=SURF, linewidth=1.2, zorder=4)
    ax.text(li * 1.2, yi, f"linear {li:.1f}%", fontsize=9, color=INK2, va="center")
    ax.text(act, yi - 0.28, f"actual {act:.2f}%  ·  square root {sq:.2f}%", fontsize=9, color=INK, va="center", ha="center")
ax.set_xscale("log"); ax.set_xlim(0.05, 120); ax.set_ylim(-0.6, len(rows) - 0.4)
ax.set_yticks(y); ax.set_yticklabels([r[0] for r in rows])
ax.set_xticks([0.1, 1, 10, 100]); ax.set_xticklabels(["0.1%", "1%", "10%", "100%"])
ax.set_xlabel("fall from 15:30 to the close, Nov 5 (log scale)")
ax.grid(True, axis="x", color=GRID, lw=0.8); tidy(ax)
ax.set_title("C. But a known forced sale (leveraged-ETF\nrebalancing, Nov 5 close) moved price\nlike the square-root law, not the linear one", loc="left", color=INK, fontsize=12, pad=8)

fig.text(0.055, 0.945, "Selling alone can't make a crash at normal liquidity: sensitivity to selling must jump during the day, or the fall is news", fontsize=15.5, weight="bold", color=INK)
fig.text(0.055, 0.905, "Three impact laws from the literature, constants fixed in advance (Kyle & Obizhaeva 2016/2023; Bucci et al. 2019; Donier & Bonart 2015). "
         "For each fall: how much net selling would the law need to cause it?", fontsize=10.5, color=INK2, va="top")
fig.text(0.055, 0.87, "Normal-liquidity square root can't make index shocks (needs 1.4–113× the whole day's volume as net selling); the stress in the week before doesn't rescue it. "
         "The linear law can (median 14% of the day's volume),\nbut it over-predicts the one forced flow we can compute exactly. Neither fixed law fits both: liquidity must break within the crash day, or the fall is news.", fontsize=10.5, color=INK, va="top")
fig.text(0.055, 0.025, "Pre-registered (commit 77fea8a). HB1: square root needs more than the day's volume on 54/54 days (baseline, near-certain by construction). HB2: still true with the week-before "
         "liquidity state, 54/54 (build-up shocks need less: median 5.2× vs 12.8× abrupt).\nHB3: linear needs ≤ 25% of the day's volume on 80% of days (90% CI 70–89%; 63–87% across sensitivities). "
         "Part A reproduces Kyle & Obizhaeva's published predictions within 0.1 pp.\nThe volume proxy failed its 1987 cross-check, so the pre-registered fallback (their 1987 and 2010 whole-market volumes) was used. "
         "Panel C assumes the leveraged-ETF flow hit at the close; if dealers hedged it during the day, the close is the wrong window.",
         fontsize=8.8, color=MUTED)
out = H / "out" / "crash_law.png"; fig.savefig(out, dpi=200); print(out)
