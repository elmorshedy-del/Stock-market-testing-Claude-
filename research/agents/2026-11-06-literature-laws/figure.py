"""Foundation map: the laws of price formation in our three layers, with evidence grade and the owner's ideas."""
import pathlib, textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

HERE = pathlib.Path(__file__).resolve().parent
SURF, INK, INK2, MUTED, BASE = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#c3c2b7"
GOOD, MID, OPEN, TINT = "#0ca30c", "#c98500", "#2a78d6", "#eef4fc"
MARK = {"E": ("●", GOOD), "C": ("◐", MID), "O": ("○", OPEN)}
plt.rcParams.update({"font.family": "DejaVu Sans", "figure.facecolor": SURF})

cols = [
    ("SLOW: the push", "what creates the flow", [
        ("E", "S1", "Inelastic markets: $1 into stocks lifts market value by about $5"),
        ("E", "S1", "Even predictable flows move prices on the day (about 1.9x)"),
        ("E", "S2", "Forced selling pushes prices away, then they come back"),
        ("E", "S2", "Dealer gamma: short gamma gives momentum, long gamma gives reversals (modest)"),
        ("E", "S2", "Expiring index-option hedges move the last 30 minutes"),
        ("C", "S3", "Fat tails come from the sizes of the biggest investors"),
        ("C", "S4", "Crash size = sell imbalance measured in business time"),
    ], "Your idea: options show the move in advance.\nPartly true: the gamma sign and expiry hedges\nmatter (S2)."),
    ("MEDIUM: the rhythm", "when and how fast it plays out", [
        ("E", "M1", "The market's clock runs on trading activity, not hours"),
        ("E", "M2", "Activity begets activity, near the tipping point"),
        ("E", "M2", "Aftershocks fade by Omori's law; bigger shocks have more"),
        ("C", "M3", "News shocks hit and fade fast; self-made shocks build up, then fade slowly"),
        ("E", "M4", "Liquidity flees volatility, which feeds the next move"),
        ("E", "M4", "Falls raise volatility more than rises, strongest for indices"),
    ], "Your idea: each move's volatility signature sets\nits speed (M1) and how long the quiet lasts (M3).\nOpen; free to test first."),
    ("FAST: the mechanics", "how flow becomes price", [
        ("E", "F1", "Impact grows as the square root of order size, in every market"),
        ("E", "F2", "Short-run price change = flow imbalance / depth"),
        ("E", "F3", "Big orders are split: flow persists, yet price stays random"),
        ("E", "F4", "Big moves are holes in liquidity, not big orders"),
        ("C", "F4", "One-sided flow pins the price at a level (absorption)"),
        ("C", "F5", "Profit targets cluster at round numbers, stops just beyond"),
        ("E", "F6", "When a big order ends, about 1/3 of its impact reverts"),
        ("E", "F7", "Volatility per trade is proportional to the spread"),
    ], "Your ideas: motion through liquidity, confirmed.\nAbsorption must complete, and exhaustion:\nopen; needs order-flow data."),
]

fig = plt.figure(figsize=(16, 10))
fig.text(0.03, 0.962, "The market as a machine: what is established, what is contested, and where your ideas sit",
         fontsize=17, weight="bold", color=INK)
fig.text(0.03, 0.928, "16 laws from about 75 verified papers, arranged in our three layers.", fontsize=11, color=INK2)
x = 0.03
for key, lab in (("E", "established across many markets"), ("C", "supported, but contested or few studies"),
                 ("O", "open: not yet tested well (most of your ideas)")):
    g, c = MARK[key]
    fig.text(x, 0.898, g, fontsize=13, color=c, va="center")
    fig.text(x + 0.016, 0.898, lab, fontsize=10.5, color=INK2, va="center")
    x += 0.016 + 0.0062 * len(lab) + 0.03

W, GAP, TOP, BOT = 0.296, 0.026, 0.865, 0.175
for i, (title, sub, laws, idea) in enumerate(cols):
    x0 = 0.03 + i * (W + GAP)
    fig.patches.append(FancyBboxPatch((x0, BOT), W, TOP - BOT, boxstyle="round,pad=0.004,rounding_size=0.008",
                                      transform=fig.transFigure, fc=SURF, ec=BASE, lw=1.0))
    fig.text(x0 + 0.012, TOP - 0.03, title, fontsize=13.5, weight="bold", color=INK)
    fig.text(x0 + 0.012, TOP - 0.057, sub, fontsize=10.5, color=INK2, style="italic")
    y = TOP - 0.095
    for grade, code, txt in laws:
        g, c = MARK[grade]
        lines = textwrap.wrap(txt, 44)
        fig.text(x0 + 0.012, y, g, fontsize=12, color=c, va="top")
        fig.text(x0 + 0.030, y - 0.002, code, fontsize=9.5, color=INK2, va="top", weight="bold")
        fig.text(x0 + 0.054, y - 0.002, "\n".join(lines), fontsize=10.3, color=INK, va="top", linespacing=1.15)
        y -= 0.023 * len(lines) + 0.011
    # owner's ideas strip
    fig.patches.append(FancyBboxPatch((x0 + 0.008, BOT + 0.012), W - 0.016, 0.100,
                                      boxstyle="round,pad=0.003,rounding_size=0.006", transform=fig.transFigure,
                                      fc=TINT, ec="none"))
    fig.text(x0 + 0.016, BOT + 0.062, "○", fontsize=12, color=OPEN, va="center")
    fig.text(x0 + 0.034, BOT + 0.062, idea, fontsize=10, color=INK, va="center", linespacing=1.3)
    if i < 2:
        xa = x0 + W + 0.002
        fig.patches.append(FancyArrowPatch((xa, 0.53), (xa + GAP - 0.004, 0.53), transform=fig.transFigure,
                                           arrowstyle="-|>", mutation_scale=16, color=INK2, lw=1.4))
        fig.text(xa + GAP / 2 - 0.001, 0.555, ("flow", "activity")[i], fontsize=9, color=INK2, ha="center", rotation=90)

# constraint bar
fig.patches.append(FancyBboxPatch((0.03, 0.085), 0.94, 0.06, boxstyle="round,pad=0.004,rounding_size=0.008",
                                  transform=fig.transFigure, fc="#f0efec", ec="none"))
fig.text(0.042, 0.115, "●", fontsize=12, color=GOOD, va="center")
fig.text(0.058, 0.115, "C1  Constraint under all three layers: predictable drift gets traded away, so impact must decay. "
         "Our channel and random-walk tests agree.", fontsize=10.8, color=INK, va="center")
fig.text(0.03, 0.04, "Next (free): test M3 on our own shocks (which of the 54 past drops started a new leg?), then the M1 clock test. "
         "Paid order-flow data is for the fast layer.", fontsize=10.5, color=INK2)
fig.text(0.03, 0.015, "Sources and evidence grades: research/agents/FOUNDATION.md and 2026-11-06-literature-laws/README.md.",
         fontsize=9, color=MUTED)
out = HERE / "out" / "foundation_map.png"
fig.savefig(out, dpi=200)
print(out)
