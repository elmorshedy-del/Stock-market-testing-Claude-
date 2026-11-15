"""Audit figure: where the 81 studies went and what they found (left); the proposed purpose and path (right)."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Patch

H = Path(__file__).resolve().parent
A = json.load(open(H / "out" / "audit.json"))
SURF, INK, INK2, MUTED, GRID, BASE = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
ROB, LEAN, NUL, NOT = "#184f95", "#86b6ef", "#b4b3ab", "#ecebe5"   # one blue ramp for "found something"; neutral grays for "nothing" / "no test"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10.5, "axes.edgecolor": BASE, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.facecolor": SURF, "figure.facecolor": SURF})
fig = plt.figure(figsize=(17.5, 9.2))
ax = fig.add_axes([0.135, 0.215, 0.30, 0.52]); bx = fig.add_axes([0.50, 0.06, 0.485, 0.72]); bx.axis("off")

# ---- left: studies by topic and outcome ----
T = A["tally by topic"]
order = sorted(T, key=lambda t: (T[t]["R"], T[t]["L"], -T[t]["N"]))
for i, t in enumerate(order):
    left = 0
    for k, col in (("R", ROB), ("L", LEAN), ("N", NUL), ("D", NOT)):
        v = T[t][k]
        if v:
            ax.barh(i, v, left=left, color=col, edgecolor=SURF, linewidth=2, height=0.66)
            ax.text(left + v / 2, i, str(v), ha="center", va="center", fontsize=9.5, color=SURF if k == "R" else INK)
            left += v
ax.set_yticks(range(len(order))); ax.set_yticklabels(order, fontsize=10)
ax.set_xlim(0, 16); ax.set_xlabel("number of studies"); ax.grid(True, axis="x", color=GRID, lw=0.8); ax.set_axisbelow(True)
for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
ax.tick_params(axis="y", length=0)
tot = A["totals"]
ax.legend(handles=[Patch(color=ROB, label=f"robust: replicated or very strong ({tot['R']})"), Patch(color=LEAN, label=f"lean: passed once, partial or one day ({tot['L']})"),
                   Patch(color=NUL, label=f"null: the idea failed ({tot['N']})"), Patch(facecolor=NOT, edgecolor=BASE, label=f"no test: live read, map, reading ({tot['D']})")],
          loc="upper center", bbox_to_anchor=(0.30, -0.13), ncol=2, frameon=False, fontsize=9.3)
ax.set_title("A. Where 81 studies went, and what they found", loc="left", color=INK, fontsize=12.5, pad=10)

# ---- right: purpose and path ----
def box(x, y, w, h, fc, ec=BASE, lw=1.0):
    bx.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.004,rounding_size=0.012", fc=fc, ec=ec, lw=lw, transform=bx.transAxes, clip_on=False))
bx.text(0, 1.0, "B. Proposed purpose, in one sentence", fontsize=12.5, color=INK, va="top", transform=bx.transAxes)
box(0, 0.815, 1.0, 0.125, "#f3f7fd", ec=LEAN)
bx.text(0.015, 0.878, "Each day, know the market's state and what it makes likely (how big, where, how fast).\nTurn that into entry and exit rules for SPY and TSLA calls, "
        "and keep a live score\nagainst the options market's own odds.", fontsize=11.2, color=INK, va="center", transform=bx.transAxes, linespacing=1.45)
bx.text(0, 0.775, "Three things define the state (the theory, kept small)", fontsize=10.5, color=INK2, va="top", transform=bx.transAxes)
cards = [("1  Positioning", "dealer gamma: flip, walls, pocket", "Measured. Our strongest results.", ROB),
         ("2  Liquidity", "how far price moves per unit of selling", "Not measured yet.\nBreaks on crash days.", NUL),
         ("3  Forced flow", "who must trade next: expiries,\nearnings, leveraged funds", "Partly measured. Pushes that revert.", LEAN)]
for j, (h1, h2, h3, col) in enumerate(cards):
    x = j * 0.34
    box(x, 0.575, 0.32, 0.165, SURF)
    bx.add_patch(FancyBboxPatch((x, 0.575), 0.012, 0.165, boxstyle="square,pad=0", fc=col, ec="none", transform=bx.transAxes, clip_on=False))
    bx.text(x + 0.028, 0.722, h1, fontsize=11, color=INK, weight="bold", va="top", transform=bx.transAxes)
    bx.text(x + 0.028, 0.685, h2, fontsize=9.3, color=INK2, va="top", transform=bx.transAxes, linespacing=1.3)
    bx.text(x + 0.028, 0.588, h3, fontsize=9.3, color=INK, va="bottom", transform=bx.transAxes, linespacing=1.3)
bx.text(0, 0.535, "The path", fontsize=10.5, color=INK2, va="top", transform=bx.transAxes)
steps = [("Step 0", "this week · no new tests", "Consolidate: one purpose page, one SPY playbook (TSLA's exists), one scoreboard.\nCut the to-do list from 79 open items to about 10."),
         ("Step 1", "2–3 weeks · free", "Prove or drop the rules you already trade, in real option prices: ladder rungs,\nTSLA full setup, exit at the wall, exit on earnings mornings. Start a daily forward log."),
         ("Step 2", "staged · about $35 first", "Measure liquidity from ES/NQ signed trades: does sensitivity to selling jump before a fall,\ndoes it track gamma, and do floors show absorption?"),
         ("Step 3", "after steps 1–2", "Forced-flow calendar for the trades you actually make: earnings weeks, expiries."),
         ("Parked", "", "Channels, indicators, analogs, politics, single-stock quirks,\nand law replications that change no decision.")]
y = 0.50
for name, when, what in steps:
    hgt = 0.088 if "\n" in what else 0.062
    y -= hgt
    box(0, y, 1.0, hgt - 0.012, SURF if name != "Parked" else NOT)
    bx.text(0.015, y + (hgt - 0.012) / 2, name, fontsize=10.5, color=INK, weight="bold", va="center", transform=bx.transAxes)
    bx.text(0.085, y + (hgt - 0.012) / 2, when, fontsize=8.8, color=MUTED, va="center", transform=bx.transAxes)
    bx.text(0.275, y + (hgt - 0.012) / 2, what, fontsize=9.3, color=INK, va="center", transform=bx.transAxes, linespacing=1.35)

s = A["Nov 2 live-read forecasts"]
fig.text(0.02, 0.955, "Audit: the results cluster in three places, so the work should narrow to them", fontsize=17, weight="bold", color=INK)
fig.text(0.02, 0.915, f"Since Oct 15: 81 studies, {A['tests run']} with a test → {tot['R']} robust, {tot['L']} leans, {tot['N']} nulls. Every robust result sits in dealer positioning, forced flows, "
         "or the physics of big moves (clustering, crashes).\nChannels, indicators, analogs, politics and single-stock quirks produced none. The founding report (Oct 2–15: the gamma ladder and the TSLA burst setup) is not counted here.",
         fontsize=10.5, color=INK2, va="top")
fig.text(0.02, 0.845, f"Live record, scored today: on 12 probability calls for the week of Nov 2, my adjustments scored {s['Brier, my calls (same 12)']:.3f} against {s['Brier, options-implied map']:.3f} for the options "
         "market's own odds (lower is better; a coin flip is 0.250).\nLevel calls did better: the Oct 30 flush low and the Nov 5 crash low both landed inside the mapped SPY zones. The TSLA floor map failed on Nov 5.",
         fontsize=10.5, color=INK, va="top")
fig.text(0.02, 0.012, "Classification is my reading of each study's logged verdict (tally.py). Robust = replicated or out-of-sample, or p ≤ 0.005 with controls. "
         "12 forecasts in one week is a small sample, and their outcomes are correlated.", fontsize=8.8, color=MUTED)
out = H / "out" / "audit_map.png"; fig.savefig(out, dpi=200); print(out)
