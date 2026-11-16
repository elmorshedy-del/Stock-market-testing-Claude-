"""Diagram of the derivation (no data): two forces when dealer positioning changes, and what they predict for a call buyer."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

H = Path(__file__).resolve().parent
SURF, INK, INK2, MUTED, GRID, BASE = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
BLUE, BLUE_BG, ORANGE, ORANGE_BG, NEUT = "#184f95", "#eaf2fc", "#b84a1c", "#fdeee7", "#f4f3ef"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10.5, "figure.facecolor": SURF})
fig = plt.figure(figsize=(18, 10.6)); ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)


def box(x, y, w, h, fc, ec=BASE, lw=1.0):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.002,rounding_size=0.008", fc=fc, ec=ec, lw=lw))


def tag(x, y, text, col, bg):
    ax.text(x, y, text, fontsize=10.5, weight="bold", color=col, va="center", ha="left",
            bbox=dict(boxstyle="round,pad=0.35", fc=bg, ec=col, lw=1.1))


# ---------- header ----------
ax.text(0.022, 0.958, "Derived before any data: an option is cheap or dear because of who sold it, more than because of the next move's size",
        fontsize=16.5, weight="bold", color=INK)
ax.text(0.022, 0.925, "From seven papers read in full. These are predictions for you to challenge. They are not results, and no data has been touched.",
        fontsize=11, color=INK2, va="top")

# ---------- panel A: the two forces ----------
AX0, AW = 0.022, 0.392
ax.text(AX0, 0.878, "A. Two forces act at the same time", fontsize=12.5, color=INK, weight="bold", va="center")
rows = [
    (0.545, "Customers BOUGHT options: dealers are short gamma", "typical after a selloff",
     "THE MOVE", "Dealers must sell falls and buy\nrises. Moves get bigger: roughly\n+5% to +15% per standard\ndeviation of gamma.",
     "THE PRICE", "Dealers carry risk they cannot\nhedge, and charge for it: about\n1.7 volatility points on average\nin 1997–2001, and double that\nafter dealer losses.",
     "For a buyer: the bigger move is already in the price,\nand the charge sits on top.", "DEAR", ORANGE, ORANGE_BG, 0.052),
    (0.215, "Customers SOLD options: dealers are long gamma", "typical in calm markets",
     "THE MOVE", "Dealers buy falls and sell rises.\nMoves get smaller. In the S&P,\nmarket makers are long gamma\n88% of the time.",
     "THE PRICE", "Customers' selling pushes it\ndown. S&P options have not\nbeen overpriced on average\nsince about 2012.",
     "For a buyer: small moves, but a price that is lower still.", "FAIR TO CHEAP", BLUE, BLUE_BG, 0.104),
]
for y0, head, sub, h1, t1, h2, t2, net, verdict, col, bg, tw in rows:
    hgt = 0.30
    box(AX0, y0, AW, hgt, SURF)
    ax.add_patch(Rectangle((AX0, y0), 0.006, hgt, fc=col, ec="none"))
    ax.text(AX0 + 0.018, y0 + hgt - 0.027, head, fontsize=11.3, weight="bold", color=INK, va="center")
    ax.text(AX0 + 0.018, y0 + hgt - 0.054, sub, fontsize=9.6, color=MUTED, va="center")
    bw, bh, by = 0.176, 0.142, y0 + 0.078
    for j, (hh, tt) in enumerate(((h1, t1), (h2, t2))):
        bx = AX0 + 0.018 + j * (bw + 0.010)
        box(bx, by, bw, bh, NEUT, ec=GRID)
        ax.text(bx + 0.010, by + bh - 0.020, hh, fontsize=9.2, weight="bold", color=INK2, va="center")
        ax.text(bx + 0.010, by + bh - 0.040, tt, fontsize=9.6, color=INK, va="top", linespacing=1.38)
    ax.text(AX0 + 0.018, y0 + 0.038, net, fontsize=9.9, color=INK, va="center", linespacing=1.4)
    tag(AX0 + AW - tw, y0 + 0.038, verdict, col, bg)
ax.text(AX0, 0.197, "Why the price already knows: the dealer who sets the option's price is the\n"
        "one whose hedging makes the move, and only the dealer sees the position.", fontsize=10, color=INK2, va="top", linespacing=1.45)

# ---------- panel B: predictions by state ----------
BX0, BW = 0.440, 0.540
ax.text(BX0, 0.878, "B. What that predicts for a call buyer, state by state", fontsize=12.5, color=INK, weight="bold", va="center")
cols = [(BX0 + 0.008, "State"), (BX0 + 0.152, "Next move"), (BX0 + 0.212, "Option price"), (BX0 + 0.308, "Derived verdict"), (BX0 + 0.398, "What to do")]
for x, lab in cols:
    ax.text(x, 0.846, lab, fontsize=9.6, color=MUTED, va="center")
ax.plot([BX0, BX0 + BW], [0.830, 0.830], color=BASE, lw=1)
states = [
    ("After a selloff", "low gamma, high fear", "bigger", "much higher", "DEAR", ORANGE, ORANGE_BG,
     "Use a spread, or wait for\nthe volatility crush.", "Our founding table shows it:\nnaked calls −1% to −6%,\ncall spreads +10% to +18%."),
    ("Calm, pinned market", "high gamma", "smaller", "lower still", "FAIR TO CHEAP", BLUE, BLUE_BG,
     "A naked call is acceptable.", "Index options have had no built-in\noverpricing since about 2012."),
    ("Monday after monthly\nexpiry, where customers\nwrite options", "the average stock", "released", "pushed down by\nthe roll: about\n3% of premium", "CHEAPEST", BLUE, BLUE_BG,
     "Buy after the Monday close,\nnot the Thursday before.", "Measured on thousands of stocks,\n1996–2021."),
    ("The same days, where\ncustomers buy calls", "TSLA? unknown", "released", "pushed up by\nthe roll", "DEAR?", ORANGE, ORANGE_BG,
     "The sign is not known.", "Measuring it is the proposed test."),
]
rh = 0.150; y = 0.830
for i, (s1, s2, mv, pr, verdict, col, bg, do, note) in enumerate(states):
    y -= rh; mid = y + rh / 2
    if i >= 2:
        ax.add_patch(Rectangle((BX0, y + 0.004), BW, rh - 0.008, fc="#f8f7f3", ec="none"))
    nl = s1.count("\n")
    ax.text(cols[0][0], mid + 0.014 + 0.004 * nl, s1, fontsize=10.6, weight="bold", color=INK, va="center", linespacing=1.3)
    ax.text(cols[0][0], mid - 0.020 - 0.016 * nl, s2, fontsize=9.3, color=MUTED, va="center")
    ax.text(cols[1][0], mid, mv, fontsize=10.2, color=INK, va="center")
    ax.text(cols[2][0], mid, pr, fontsize=10.2, color=INK, va="center", linespacing=1.35)
    ax.text(cols[3][0], mid, verdict, fontsize=9.6, weight="bold", color=col, va="center", ha="left",
            bbox=dict(boxstyle="round,pad=0.32", fc=bg, ec=col, lw=1.0))
    ax.text(cols[4][0], mid + 0.028, do, fontsize=10.2, color=INK, va="center", linespacing=1.35, weight="bold")
    ax.text(cols[4][0], mid - 0.030, note, fontsize=8.9, color=INK2, va="center", linespacing=1.35)
    ax.plot([BX0, BX0 + BW], [y, y], color=GRID, lw=0.8)
ax.text(BX0 + 0.008, y - 0.020, "Rows 1 and 2: both forces act, and the price side wins. Rows 3 and 4: an expiry changes positioning on a\n"
        "known date with no price move, which separates \"positioning\" from \"we just had a selloff\".", fontsize=9.4, color=INK2, va="top", linespacing=1.45)

# ---------- footer ----------
ax.plot([0.022, 0.980], [0.118, 0.118], color=BASE, lw=1)
ax.text(0.022, 0.098, "Proposed order, once you have challenged this:", fontsize=10.6, weight="bold", color=INK, va="center")
ax.text(0.022, 0.066, "1  Check our measures against the papers' baselines     2  Look at ten individual cases     3  The expiry test on SPY and TSLA (new, cheap, well powered)\n"
        "4  Rows 1 and 2 are then settled in real option prices by the structure table (queue step 2)",
        fontsize=10.2, color=INK, va="center", linespacing=1.6)
ax.text(0.022, 0.018, "Sizes are taken from the seven papers and from my own arithmetic on them; the 3% figure is my conversion of −0.43% of the hedged position. See README.md.",
        fontsize=8.8, color=MUTED, va="center")
out = H / "out" / "derivation.png"; out.parent.mkdir(exist_ok=True); fig.savefig(out, dpi=200); print(out)
