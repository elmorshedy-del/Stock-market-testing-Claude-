"""Review figure for arXiv:2601.23172: (A) the one-parameter claim, (B) the paper's own H0 evidence vs the 3/4 edge."""
import json, pathlib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import norm

HERE = pathlib.Path(__file__).resolve().parent
V = json.load(open(HERE / "out" / "fig_values.json"))

# palette (validated: blue, orange, aqua; aqua < 3:1 contrast -> every line is direct-labelled)
SURF, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
GRID, BASE, ZONE = "#e1e0d9", "#c3c2b7", "#efeeea"
BLUE, ORANGE, AQUA, BAND = "#2a78d6", "#eb6834", "#1baf7a", "#b7d3f6"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10.5, "axes.edgecolor": BASE,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.facecolor": SURF, "figure.facecolor": SURF})

fig, (a, b) = plt.subplots(1, 2, figsize=(15, 7.6), gridspec_kw={"width_ratios": [1, 1.12], "wspace": 0.2})
fig.subplots_adjust(left=0.055, right=0.985, top=0.79, bottom=0.25)
for ax in (a, b):
    ax.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
    for s in ("top", "right"): ax.spines[s].set_visible(False)

f4 = V["fig4_mixed_fbm_H0"]; f3 = V["fig3_naive_fbm_H"]; f5 = V["fig5_volume_H1"]
m4, lo4, hi4 = map(np.array, (f4["mean"], f4["lo"], f4["hi"]))
x4 = np.array(f4["x"]) / 60.0; x3 = np.array(f3["x"]) / 60.0; m3 = np.array(f3["mean"])
sig = (hi4 - lo4) / (2 * norm.ppf(0.95)); share = norm.cdf((0.75 - m4) / sig)
avg_lo, avg_hi = m4.min(), m4.max(); stk_lo, stk_hi = lo4.min(), hi4.max()
vol_lo, vol_hi = min(f5["mean"]), max(f5["mean"])

# ---------- Panel A: the claim ----------
a.axvspan(0.5, 0.75, color=ZONE, lw=0)
a.text(0.625, 0.93, "H0 below 3/4:\nthe price side breaks\n(no impact or volatility law)", ha="center", va="top",
       color=INK2, fontsize=10)
h = np.linspace(0.5, 1.0, 200); h2 = np.linspace(0.75, 1.0, 100)
a.axvspan(avg_lo, avg_hi, color=BAND, alpha=0.55, lw=0)
l1, = a.plot(h, h - 0.5, color=BLUE, lw=2, label="Volume roughness = H0 - 1/2")
l2, = a.plot(h2, 2 - 2 * h2, color=ORANGE, lw=2, label="Impact exponent = 2 - 2 H0")
l3, = a.plot(h2, 2 * h2 - 1.5, color=AQUA, lw=2, label="Volatility roughness = 2 H0 - 3/2")
# direct labels (text in ink, mark carries the colour)
# the 'sweet spot' the authors point to
for y, c in ((0.5, ORANGE), (0.0, AQUA), (0.25, BLUE)):
    a.plot([0.75], [y], "o", ms=8, mfc=SURF, mec=c, mew=2, zorder=5)
a.annotate("At H0 = 3/4 exactly:\nimpact = 1/2 (square-root law)\nvolume roughness = 1/4\nvolatility roughness = 0",
           xy=(0.75, 0.5), xytext=(0.80, 0.80), fontsize=9.5, color=INK, va="top",
           arrowprops=dict(arrowstyle="-", color=MUTED, lw=1))
# where the data put H0
a.plot([stk_lo, stk_hi], [-0.10, -0.10], color=BLUE, lw=6, alpha=0.35, solid_capstyle="butt")
a.plot([avg_lo, avg_hi], [-0.10, -0.10], color=BLUE, lw=6, solid_capstyle="butt")
a.text(0.505, -0.10, "data:", color=INK, fontsize=9.5, va="center")
a.text(stk_lo, -0.14, f"individual stocks 5-95%: {stk_lo:.2f}-{stk_hi:.2f}; dark = average {avg_lo:.2f}-{avg_hi:.2f}", color=INK2, fontsize=9, va="top")
a.set_xlim(0.5, 1.0); a.set_ylim(-0.19, 1.0)
a.set_xlabel("H0 = memory of the slow 'core' order flow  (0.5 = no memory)")
a.set_ylabel("Exponent the theory predicts")
a.set_title("A. The claim: one number, H0, sets three other market laws", loc="left", color=INK, fontsize=12, pad=10)
a.legend(handles=[l1, l2, l3], loc="upper left", bbox_to_anchor=(-0.01, -0.13), ncol=2, frameon=False, fontsize=9.5,
         handlelength=1.6, columnspacing=1.4)

# ---------- Panel B: the evidence ----------
b.axhspan(0.45, 0.75, color=ZONE, lw=0)
bb = b.fill_between(x4, lo4, hi4, color=BAND, alpha=0.75, lw=0, label="Individual stocks, 5-95% (Fig. 4)")
lm, = b.plot(x4, m4, color=BLUE, lw=2, label="Average H0, mixed estimator (Fig. 4)")
ln, = b.plot(x3, m3, color=MUTED, lw=2, label="Naive estimator (Fig. 3)")
b.axhline(0.75, color=INK2, lw=1)
b.text(81.2, 0.744, "3/4 edge", color=INK, fontsize=9.5, va="top")
b.text(99, 0.47, "below 3/4:\nthe price side breaks", color=INK2, fontsize=9.5, ha="right", va="bottom")
b.text(x4[-1] + 1.2, m4[-1], "average H0", color=INK, fontsize=9.5, va="center")
b.text(x3[-1] + 1.2, m3[-1], "naive estimate:\nthe text's \"0.65\"", color=INK, fontsize=9.5, va="center")
b.text(28, 0.905, "individual stocks (5-95%)", color=INK2, fontsize=9.5, ha="center")
b.text(42, 0.535,
       f"Average {m4.mean():.3f}: about 1 standard error above 3/4\n"
       f"About {np.median(share)*100:.0f}% of stock estimates fall below 3/4\n"
       f"({share.min()*100:.0f}-{share.max()*100:.0f}% depending on bin size, normal approximation)",
       color=INK, fontsize=9.5, ha="center", va="center",
       bbox=dict(boxstyle="round,pad=0.45", fc=SURF, ec=BASE, lw=0.8))
b.set_xlim(0, 100); b.set_ylim(0.45, 0.95)
b.set_xticks([0, 10, 20, 30, 40, 50, 60, 70, 80])
b.set_xlabel("Sampling interval (minutes); the paper stops at 80 minutes")
b.set_ylabel("Estimated H0")
b.set_title("B. The evidence: H0 sits on the 3/4 edge, and stocks straddle it", loc="left", color=INK, fontsize=12, pad=10)
b.legend(handles=[lm, bb, ln], loc="upper left", bbox_to_anchor=(-0.01, -0.13), ncol=2, frameon=False, fontsize=9.5,
         handlelength=1.6, columnspacing=1.4)

fig.text(0.055, 0.955, "A clean theory balanced on one number, and the paper's own data sit right at its edge",
         fontsize=15.5, color=INK, weight="bold", ha="left")
fig.text(0.055, 0.905, "Muhle-Karbe, Ouazzani Chahdi, Rosenbaum, Szymanski (2026), \"A unified theory of order flow, market impact, "
         "and volatility\", arXiv:2601.23172 (preprint).\nData: trades of 40 large caps (20 Paris, 20 NYSE), 2021-2024.",
         fontsize=10, color=INK2, ha="left", va="top")
fig.text(0.055, 0.025, "Panel B values read from the vector files of the paper's Figures 3 and 4. The share below 3/4 uses a normal "
         "approximation to the plotted 5-95% band; it mixes estimation noise with real differences between stocks. "
         f"The paper's volume data (Fig. 5, mean {vol_lo:.2f}-{vol_hi:.2f}) imply H0 {vol_lo+0.5:.2f}-{vol_hi+0.5:.2f}, consistent with panel B.",
         fontsize=8.6, color=MUTED, ha="left", wrap=True)
fig.canvas.draw()
def inline_label(ax, f, x, dy, text):
    p0 = ax.transData.transform((x - 0.01, f(x - 0.01))); p1 = ax.transData.transform((x + 0.01, f(x + 0.01)))
    ang = np.degrees(np.arctan2(p1[1] - p0[1], p1[0] - p0[0]))
    ax.text(x, f(x) + dy, text, rotation=ang, rotation_mode="anchor", ha="center", va="center", color=INK, fontsize=9.5)
inline_label(a, lambda q: q - 0.5, 0.60, 0.04, "volume roughness")
inline_label(a, lambda q: 2 - 2 * q, 0.815, 0.045, "impact exponent")
inline_label(a, lambda q: 2 * q - 1.5, 0.85, -0.05, "volatility roughness")
out = HERE / "out" / "paper_review_h0_edge.png"
fig.savefig(out, dpi=200)
print(out)
