"""Knowledge map: the work refiled under the seven questions a call buyer asks."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch

H = Path(__file__).resolve().parent
C = json.load(open(H / "out" / "catalog.json")); T = C["tally"]
SURF, INK, INK2, MUTED, GRID, BASE = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
ROB, LEAN, NUL, NOT, HI = "#184f95", "#86b6ef", "#b4b3ab", "#ecebe5", "#f3f7fd"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10.5, "figure.facecolor": SURF})
ROWS = [
 ("SIZE", "1  How big?", "Low dealer gamma → bigger moves. Call gamma damps, put gamma amplifies.\nBig days cluster. For TSLA use its own positioning, not the S&P's.",
  "Best answered. One input is missing:\nliquidity (step 5)."),
 ("LEVEL", "2  Where?", "The call wall is a soft ceiling; round numbers matter; the short-gamma pocket\ncaught the Oct 30 and Nov 5 lows. Channels and drawn lines: dead.",
  "Floors need trade data (step 5).\nOne test left: TSLA's call wall."),
 ("DIR", "3  Which way?", "Broad direction: nothing. Narrow tilts only: TSLA freed and full setup,\nRSI washout, the S&P ladder's odds.",
  "Stop hunting predictors.\nAsk whether the tilts are priced (steps 1–2)."),
 ("TIME", "4  When?", "The ladder leads by about 5 days. Gamma builds into monthly expiry, then resets.\nThe calendar sets when, not which way. No robust result yet.",
  "One free lead: a price low that implied\nvolatility does not confirm. Rest closed."),
 ("PRICE", "5  Is it priced?\n    Which structure?", "Only 4 studies. On rough estimates: naked calls bought early lose,\ncall spreads gain, naked calls pay only after the volatility crush.",
  "THE GAP. Step 1: realized vs implied move\nby gamma state. Step 2: structure and exits."),
 ("EXIT", "6  When to get out?", "Earnings gap-ups fade at the open. Moves made on low-gamma days give back.\nTrim at the call wall. Footprint ideas: dead.",
  "Measure exits in option P&L (step 2).\nYour own fills, if you share them (step 4)."),
 ("RISK", "7  What breaks it?", "Crash days are a liquidity regime change. SPY drags TSLA about 2×.\nMy tilts missed Nov 5; the pocket map caught where it stopped.",
  "Liquidity pilot, about $35 (step 5)."),
]
fig = plt.figure(figsize=(18, 10.2)); ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
X0, XB, XK, XN = 0.022, 0.165, 0.375, 0.735     # question, bar, know, next
top, rh = 0.775, 0.092; unit = 0.185 / 33
for x, lab in ((X0, "Question"), (XB, "Studies and what they found"), (XK, "What we know"), (XN, "What comes next")):
    ax.text(x, top + 0.022, lab, fontsize=10, color=MUTED, va="bottom")
ax.plot([X0, 0.985], [top + 0.012, top + 0.012], color=BASE, lw=1)
for i, (b, q, know, nxt) in enumerate(ROWS):
    y = top - (i + 1) * rh
    if b == "PRICE": ax.add_patch(Rectangle((0.012, y + 0.004), 0.976, rh - 0.008, fc=HI, ec=LEAN, lw=1.2))
    ax.text(X0, y + rh / 2, q, fontsize=12.5, color=INK, weight="bold", va="center", linespacing=1.3)
    x = XB
    for k, col in (("R", ROB), ("L", LEAN), ("N", NUL), ("D", NOT)):
        v = T[b][k]
        if v:
            ax.add_patch(Rectangle((x, y + rh / 2 - 0.017), v * unit, 0.034, fc=col, ec=SURF, lw=1.5))
            ax.text(x + v * unit / 2, y + rh / 2, str(v), ha="center", va="center", fontsize=9, color=SURF if k == "R" else INK)
            x += v * unit
    ax.text(x + 0.006, y + rh / 2, f"{sum(T[b].values())}", fontsize=9, color=MUTED, va="center")
    ax.text(XK, y + rh / 2, know, fontsize=10, color=INK, va="center", linespacing=1.4)
    ax.text(XN, y + rh / 2, nxt, fontsize=10, color=INK, va="center", linespacing=1.4, weight="bold" if b == "PRICE" else "normal")
    ax.plot([X0, 0.985], [y, y], color=GRID, lw=0.8)
ax.legend(handles=[Patch(color=ROB, label="robust"), Patch(color=LEAN, label="lean"), Patch(color=NUL, label="null"), Patch(facecolor=NOT, edgecolor=BASE, label="no test")],
          loc="lower left", bbox_to_anchor=(XB - 0.005, 0.085), ncol=4, frameon=False, fontsize=9.3, handlelength=1.2, columnspacing=1.2)
ax.text(X0, 0.955, "Refiled by the question a call buyer asks: 33 studies went to “which way?”, 4 to “is it priced?”", fontsize=17, weight="bold", color=INK)
ax.text(X0, 0.915, f"{C['n']} pieces of work since Oct 2 (35 founding-report sections and 81 studies). 94 are filed under the decision they inform; "
        "the other 22 are live reads, reading and tools.", fontsize=10.8, color=INK2, va="top")
ax.text(X0, 0.882, "The strongest results say how big and where. For an options buyer those only pay if the option does not already charge for them, "
        "and that is the one question we have barely asked.", fontsize=10.8, color=INK, va="top")
ax.text(X0, 0.062, "Next, in order:", fontsize=10.5, color=INK, weight="bold", va="top")
ax.text(X0 + 0.085, 0.062, "1  Is the state priced? (free)     2  Structure and exit table in real option prices (free)     3  Daily state card and scoreboard (build)\n"
        "4  Your own fills, if you share them (optional)     5  Liquidity pilot (about $35)     6  Earnings: is the move priced, given positioning?",
        fontsize=10.2, color=INK, va="top", linespacing=1.6)
out = H / "out" / "knowledge_map.png"; fig.savefig(out, dpi=200); print(out)
