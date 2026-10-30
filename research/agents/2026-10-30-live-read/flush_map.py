"""out/flush_map_1030.png: SPY Friday Oct 30 flush map: the dealer-gamma pocket drawn on a price axis (zones, extremes),
the owner's flush-and-rebound scenario as an illustration, and the S&P/SPY closing levels that make R2 likely
(out/r2_price.json). Usage: python flush_map.py"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent; OUT = HERE / "out"
C = json.loads((OUT / "curves.json").read_text()); R = json.loads((OUT / "r2_price.json").read_text())
GREEN, RED, INK, MUTED, SURF, BLUE, ORANGE, AMBER = "#1baf7a", "#d64545", "#0b0b0b", "#52514e", "#fcfcfb", "#2a78d6", "#eb6834", "#e8a33d"
plt.rcParams.update({"font.size": 10.5, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED, "text.parse_math": False,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
YLO, YHI = 722, 776
fig, (a, b, c) = plt.subplots(1, 3, figsize=(18, 11), sharey=True, gridspec_kw={"width_ratios": [1.25, 1.35, 0.8], "wspace": 0.04})

# --- left: the pocket on a price axis
fr = C["SPY | Friday Oct 30 (incl. the expiry) | close Oct 29"]; mo = C["SPY | Monday Nov 2 (after the expiry) | close Oct 29"]
a.plot(fr["total gamma $bn"], fr["price"], color=INK, lw=2.4, label="Friday (with the Oct 30 expiry)")
a.plot(mo["total gamma $bn"], mo["price"], color=BLUE, lw=1.6, ls="--", label="Monday (expiry gone): shallower")
p, g = np.array(fr["price"]), np.array(fr["total gamma $bn"])
a.fill_betweenx(p, g, 0, where=g < 0, color=RED, alpha=0.10)
a.axvline(0, color=MUTED, lw=0.8); a.set_xlim(-22, 4); a.set_ylim(YLO, YHI)
a.set_xlabel("dealer gamma, $bn per 1% move\n(more negative = dealers sell more into a drop)")
a.set_ylabel("SPY price"); a.legend(loc="lower left", frameon=False, fontsize=9.5)
a.set_title("1. The pocket", loc="left", color=INK, fontsize=13, weight="bold")

ZONES = [(771.7, 776, GREEN, "ABOVE THE FLIP: dealers damp moves"),
         (754, 771.7, AMBER, "RAMP 772 → 754: each $ lower adds selling fast"),
         (728, 754, RED, "CORE 754 → 728: deepest, peak at 743"),
         (YLO, 728, MUTED, "BELOW 728: amplification fades")]
for lo, hi, col, lab in ZONES:
    for ax in (a, b, c):
        ax.axhspan(lo, hi, color=col, alpha=0.06, lw=0)
    b.text(0.99, (lo + hi) / 2, lab, transform=b.get_yaxis_transform(), ha="right", va="center", fontsize=10, color=col, weight="bold")

LEVELS = [(771.7, "771.7 flip: reclaim = green light B", GREEN, "-"), (769.36, "769.36 Thu close", INK, ":"),
          (765, "765 biggest negative strike", RED, "--"), (762, "~762 ES-implied open", RED, ":"),
          (760, "760 accelerant", RED, "--"), (752.7, "752.7 = 2-sigma day (VIX 17.2)", MUTED, ":"),
          (750, "750 put wall (most puts)", RED, "-"), (743.2, "743 pocket peak = 3-sigma day", RED, "-"), (728, "728 core ends", MUTED, "--")]
for y, lab, col, ls in LEVELS:
    for ax in (a, b):
        ax.axhline(y, color=col, lw=1.1 if ls != "-" else 1.6, ls=ls, alpha=0.9)
    a.text(-21.6, y + 0.25, lab, fontsize=9, color=col, va="bottom")

# --- middle: the scenario (illustration)
t = np.array([0, 0.6, 1.4, 2.0, 2.8, 4.2, 5.6, 6.5])
path = np.array([762.0, 759.5, 755.0, 751.0, 753.5, 757.5, 760.5, 761.5])
b.plot(t, path, color=INK, lw=2.6)
b.scatter([0, 2.0, 6.5], [762, 751, 761.5], color=[RED, RED, BLUE], zorder=5, s=55)
b.annotate("open ~762\n(already in the ramp)", (0, 762), xytext=(0.15, 766.5), fontsize=9.5, color=RED, arrowprops=dict(arrowstyle="-", color=RED, lw=0.8))
b.annotate("flush low: 750–754 is the realistic floor\n(put wall + core edge + 2-sigma);\n743 only on a 3-sigma day", (2.0, 751), xytext=(2.4, 731.5), fontsize=9.5, color=RED,
           arrowprops=dict(arrowstyle="->", color=RED, lw=1))
b.annotate("rebound: 760 / 765 first,\n772 is where it stalls", (5.6, 760.5), xytext=(4.3, 766.3), fontsize=9.5, color=BLUE, arrowprops=dict(arrowstyle="->", color=BLUE, lw=1))
b.set_xticks([0, 1, 2, 3, 4, 5, 6.5]); b.set_xticklabels(["9:30", "10:30", "11:30", "12:30", "13:30", "14:30", "16:00"])
b.set_xlim(-0.2, 7.6); b.tick_params(axis="y", left=False)
b.set_title("2. Flush and rebound (illustration)", loc="left", color=INK, fontsize=13, weight="bold")

# --- right: the R2 thermometer by CLOSING level
lo_fit, hi_fit = (R["fits"][k]["table"] for k in ("last 2 years", "last 2 years, start GEX $3.5-8bn"))
spy = np.array([r["SPY"] for r in lo_fit]); p_lo = np.array([r["P(R2)"] for r in lo_fit]); p_hi = np.array([r["P(R2)"] for r in hi_fit])
g_lo = np.array([r["P(GEX low)"] for r in lo_fit]); g_hi = np.array([r["P(GEX low)"] for r in hi_fit])
mid = (p_lo + p_hi) / 2
c.barh(spy, mid, height=1.6, color=[GREEN if m >= 0.5 else AMBER if m >= 0.3 else MUTED for m in mid], alpha=0.85)
spx = [r["SPX"] for r in lo_fit]
for s, x, l, h, gl, gh in zip(spy, spx, p_lo, p_hi, g_lo, g_hi):
    if YLO < s < YHI:
        c.text(max(l, h) + 0.02, s, f"{min(l, h):.0%}–{max(l, h):.0%}  · SPY {s:.1f} / SPX {x:,}", va="center", fontsize=8.6, color=INK)
c.axvline(0.6, color=MUTED, lw=0.8, ls=":"); c.text(0.6, YHI - 0.5, " cap ~60–65%:\n DIX is a coin flip", fontsize=8.5, color=MUTED, va="top")
c.set_xlim(0, 1.25); c.set_xticks([0, 0.25, 0.5]); c.set_xticklabels(["0", "25%", "50%"]); c.tick_params(axis="y", left=False)
c.set_xlabel("chance R2 turns on, by where SPY CLOSES")
c.set_title("3. Close needed for R2", loc="left", color=INK, fontsize=13, weight="bold")

fig.suptitle("SPY Friday Oct 30: flush map. The pocket, its edges, and the close that makes R2 likely", x=0.01, ha="left", fontsize=15, color=INK, weight="bold")
fig.text(0.01, 0.015, "Key: a V-shaped rebound that closes back near 765 leaves R2 unlikely (~10%). GEX is set by the CLOSE. "
         "The GEX half is very likely at a close ≤ ~758 (SPX ≤ ~7,605); the DIX half stays ~60/40 whatever the price does.\n"
         "Positions: OI dated Oct 28 (Oct 27 close), so treat levels as ±1 strike. R2 odds: GEX/DIX daily changes regressed on the S&P return over 2 years, joint residuals resampled. Descriptive.",
         fontsize=9.5, color=MUTED)
fig.savefig(OUT / "flush_map_1030.png", dpi=125, bbox_inches="tight")
print("ok")
