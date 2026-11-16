"""The two laws drawn from their formulas (no data).
Law B (square-root impact): x = 0.5*(sqrt(m*^2 + 4 m0^2) - s m*).  Law A (linear impact): x = m0/(1 - n)."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

H = Path(__file__).resolve().parent
SURF, INK, INK2, MUTED, GRID, BASE = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
BLUE, ORANGE, GRAY = "#2a78d6", "#eb6834", "#898781"      # validated pair (validate_palette.js, light surface)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10.5, "axes.edgecolor": BASE, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.facecolor": SURF, "figure.facecolor": SURF})
N_LIN = 0.3                                                # illustrative feedback share for Law A

fig = plt.figure(figsize=(17, 9.2))
ax = fig.add_axes([0.055, 0.165, 0.385, 0.545]); bx = fig.add_axes([0.575, 0.165, 0.385, 0.545])
for a in (ax, bx):
    for s in ("top", "right"): a.spines[s].set_visible(False)
    a.grid(True, color=GRID, lw=0.8); a.set_axisbelow(True); a.tick_params(length=0)

# ---------- A: the move against the push (Law B), in units of the gamma move ----------
x = np.linspace(0, 3, 400)
short = 0.5 * (np.sqrt(1 + 4 * x**2) + 1); long_ = 0.5 * (np.sqrt(1 + 4 * x**2) - 1)
ax.plot(x, x, color=GRAY, lw=1.6)
ax.plot(x, short, color=ORANGE, lw=2.2, solid_capstyle="round")
ax.plot(x, long_, color=BLUE, lw=2.2, solid_capstyle="round")
ax.set_xlim(0, 3); ax.set_ylim(0, 3.7)
ax.set_xlabel("the move the outside push would make alone  (1 = the gamma move, m*)")
ax.set_ylabel("the move that happens  (same unit)")
ax.text(3.05, 3.54, "negative\ngamma", ha="left", va="center", fontsize=9.8, color=INK, linespacing=1.25, clip_on=False)
ax.text(3.05, 3.00, "no forced\ntraders", ha="left", va="center", fontsize=9.8, color=INK2, linespacing=1.25, clip_on=False)
ax.text(3.05, 2.54, "positive\ngamma", ha="left", va="center", fontsize=9.8, color=INK, linespacing=1.25, clip_on=False)
ax.annotate("A floor: no move smaller than\nthe gamma move can hold", xy=(0.03, 1.0), xytext=(0.30, 1.95), fontsize=9.8, color=INK, linespacing=1.3,
            arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.9), va="center")
ax.annotate("Small pushes die here\n(pinning)", xy=(0.42, 0.155), xytext=(0.95, 0.24), fontsize=9.8, color=INK, linespacing=1.3,
            arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.9), va="center")
ax.annotate("", xy=(2.6, 3.147), xytext=(2.6, 2.6), arrowprops=dict(arrowstyle="<->", color=MUTED, lw=0.9))
ax.annotate("On a big day the gap is a fixed\namount: half the gamma move", xy=(2.57, 2.90), xytext=(0.32, 3.22), fontsize=9.8, color=INK, linespacing=1.3,
            arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.9), va="center")
ax.set_title("A. Law B (square-root impact): what the forced traders do to the move", loc="left", color=INK, fontsize=12.3, pad=12)

# ---------- B: the multiplier against the size of the push: where the two laws disagree ----------
xb = np.logspace(-1, np.log10(30), 400); beta = 1 / xb
r_short = 0.5 * (np.sqrt(beta**2 + 4) + beta); r_long = 0.5 * (np.sqrt(beta**2 + 4) - beta)
bx.axhline(1, color=GRAY, lw=1.6)
bx.plot(xb, r_short, color=ORANGE, lw=2.2, solid_capstyle="round"); bx.plot(xb, r_long, color=BLUE, lw=2.2, solid_capstyle="round")
bx.axhline(1 / (1 - N_LIN), color=ORANGE, lw=2.0, ls=(0, (5, 3))); bx.axhline(1 / (1 + N_LIN), color=BLUE, lw=2.0, ls=(0, (5, 3)))
bx.set_xscale("log"); bx.set_yscale("log"); bx.set_xlim(0.1, 30); bx.set_ylim(0.09, 11)
bx.set_xticks([0.1, 0.3, 1, 3, 10, 30]); bx.set_xticklabels(["0.1", "0.3", "1", "3", "10", "30"])
bx.set_yticks([0.1, 0.2, 0.5, 1, 2, 5, 10]); bx.set_yticklabels(["0.1×", "0.2×", "0.5×", "1×", "2×", "5×", "10×"])
bx.minorticks_off()
bx.set_xlabel("size of the outside push  (1 = a push that alone makes the gamma move)")
bx.set_ylabel("the move that happens ÷ the move the push would make alone")
bx.text(0.0, -0.118, "quiet days", fontsize=9.6, color=MUTED, va="center", ha="left", transform=bx.transAxes)
bx.text(1.0, -0.118, "big days", fontsize=9.6, color=MUTED, va="center", ha="right", transform=bx.transAxes)
bx.text(0.34, 5.2, "Law B: the effect is large\non quiet days…", fontsize=9.8, color=INK, va="center", linespacing=1.3)
bx.text(26, 1 / (1 - N_LIN) * 1.07, "…and fades to nothing on big days", fontsize=9.8, color=INK, va="bottom", ha="right")
bx.text(0.115, 1 / (1 - N_LIN) * 1.07, "Law A: the same multiple every day", fontsize=9.8, color=INK, va="bottom")
bx.annotate("The two laws agree at one\nsize of push and nowhere else", xy=(1.93, 0.762), xytext=(4.2, 0.36), fontsize=9.6, color=INK, linespacing=1.3,
            arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.9), va="center")
bx.set_title("B. Where the two laws disagree: the same picture as a multiplier", loc="left", color=INK, fontsize=12.3, pad=12)

# ---------- legend, header, footer ----------
handles = [Line2D([0], [0], color=ORANGE, lw=2.2, label="negative gamma: forced traders follow the move"),
           Line2D([0], [0], color=BLUE, lw=2.2, label="positive gamma: forced traders lean against it"),
           Line2D([0], [0], color=GRAY, lw=1.6, label="no forced traders"),
           Line2D([0], [0], color=INK2, lw=2.0, label="solid: Law B, square-root impact"),
           Line2D([0], [0], color=INK2, lw=2.0, ls=(0, (5, 3)), label=f"dashed: Law A, linear impact (drawn for a feedback share of {N_LIN})")]
fig.legend(handles=handles[:3], loc="upper left", bbox_to_anchor=(0.016, 0.848), ncol=3, frameon=False, fontsize=9.6, handlelength=2.2, columnspacing=2.0)
fig.legend(handles=handles[3:], loc="upper left", bbox_to_anchor=(0.016, 0.818), ncol=2, frameon=False, fontsize=9.6, handlelength=2.2, columnspacing=2.0)
fig.text(0.022, 0.955, "A price move is an outside push divided by the market's capacity. Traders who are forced to trade change the capacity.",
         fontsize=16.5, weight="bold", color=INK)
fig.text(0.022, 0.915, "Three postulates give one equation. Solved with the two known impact laws it gives two different predictions. These curves are formulas, not data: nothing has been measured yet.",
         fontsize=10.8, color=INK2, va="top")
fig.text(0.022, 0.880, "The gamma move  m* = Y² · σ² · |G| / V   (σ daily volatility, V daily dollar volume, G forced flow per unit of return, Y ≈ 1).   First estimate for the S&P 500: about 1% of an ordinary daily move.",
         fontsize=10.8, color=INK, va="top")
fig.text(0.022, 0.066, "What would settle it:  compare low-gamma and high-gamma days by size of day. A constant multiple at every size supports Law A, and with it a runaway from positioning alone.\n"
         "A constant amount that fades on big days supports Law B, and with it the reading that a crash needs liquidity itself to collapse.",
         fontsize=10.2, color=INK, va="center", linespacing=1.55)
fig.text(0.022, 0.018, "Law A is from the 1990s literature. Law B is my own algebra on the square-root impact law. See README.md for the derivation.", fontsize=8.8, color=MUTED, va="center")
out = H / "out" / "price_law.png"; out.parent.mkdir(exist_ok=True); fig.savefig(out, dpi=200); print(out)
