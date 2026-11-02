"""Draw the owner's TSLA 'repeat October' scenario with October's actual shape overlaid (aligned on the monthly expiry)."""
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch

HERE = Path(__file__).resolve().parent; R = json.load(open(HERE / "out" / "tsla_cycle2.json"))
BLUE, ORG, BG, INK, INK2, GRID, GRAY = "#2a78d6", "#eb6834", "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#a9a8a3"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False})
r = json.load(open(sys.argv[1]))["chart"]["result"][0]; px = pd.Series(r["indicators"]["quote"][0]["close"], index=pd.to_datetime(r["timestamp"], unit="s").normalize()).dropna()
px = px[~px.index.duplicated(keep="last")]
hist = px.loc["2026-10-12":"2026-10-30"]; sb = R["storyboard closes"]; fut = pd.to_datetime(list(sb)); allx = list(hist.index) + list(fut); pos = {d: i for i, d in enumerate(allx)}
fig = plt.figure(figsize=(18, 11), facecolor=BG); ax = fig.add_axes([0.05, 0.33, 0.8, 0.53]); ax.set_facecolor(BG)
O = R["options-implied odds (no drift)"]
fig.text(0.02, 0.955, "Your scenario: 440 this week → thick pile-up next week → dip into the Nov 20 monthly → reset → new cycle (like October)", fontsize=18, weight="bold", color=INK)
fig.text(0.02, 0.905, f"A storyboard, NOT a forecast. Gray dotted = October's actual shape (pin → dip into the Oct 16 monthly → reset → new cycle), scaled and aligned on the monthly expiry.\n"
         f"Options-implied odds: 440 by Fri {int(100*O['touch >= 440 by Fri Nov 6'])}%; then Nov 13 close ≥ 420 {int(100*O['...and Fri Nov 13 close >= 420 (consolidating up there)'])}% (joint); given 440, a dip to ≤ 408 into the monthly {int(100*O['dip <= 408 during Nov 16-20, given 440 was touched'])}%.", fontsize=11, color=INK2)
ph = [("2026-11-02", "2026-11-04", "1. PUSH\nto 440", BLUE), ("2026-11-05", "2026-11-13", "2. PILE-UP\nconsolidate 425–440\n(thick OI before the monthly)", GRAY),
      ("2026-11-16", "2026-11-20", "3. DIP into\nthe monthly\n(to ~405)", ORG), ("2026-11-23", "2026-11-27", "4. RESET →\nNEW CYCLE", BLUE)]
for a, b, lab, col in ph:
    ax.axvspan(pos[pd.Timestamp(a)] - 0.45, pos[pd.Timestamp(b)] + 0.45, color=col, alpha=0.09, lw=0)
    ax.text((pos[pd.Timestamp(a)] + pos[pd.Timestamp(b)]) / 2, 456, lab, ha="center", va="top", fontsize=10.5, weight="bold", color=col if col != GRAY else INK2)
ax.plot([pos[d] for d in hist.index], hist.values, color=INK, lw=2.6, marker="o", ms=4)
yv = [sb[str(d.date())] for d in fut]; ax.plot([len(hist) - 1] + [pos[d] for d in fut], [hist.iloc[-1]] + yv, color=BLUE, lw=2.6, ls="--", marker="o", ms=4)
# October template aligned: Oct 16 (monthly) -> Nov 20; scale by top 440 / Oct 9 382.7
oct_ = px.loc["2026-09-25":"2026-10-23"]; k = 440 / float(px.loc["2026-10-09"]); off = pos[pd.Timestamp("2026-11-20")] - list(oct_.index).index(pd.Timestamp("2026-10-16"))
xs = [off + i for i in range(len(oct_))]; m = [0 <= x < len(allx) for x in xs]
ax.plot([x for x, ok in zip(xs, m) if ok], [v * k for v, ok in zip(oct_.values, m) if ok], color=GRAY, lw=1.6, ls=":", label="October's shape, scaled")
for y, lab, col in [(440, "440: call cluster / your channel top", BLUE), (420, "420 wall", BLUE), (410, "410", GRAY), (400, "400", GRAY), (380, "flip now ~377–381 (rises as OI builds)", ORG)]:
    ax.axhline(y, color=col, lw=1, ls="-" if col != GRAY else ":", alpha=0.85); ax.text(len(allx) - 0.4, y, " " + lab, va="center", fontsize=9.6, color=col if col != GRAY else INK2)
ax.set_ylim(350, 460); ax.set_xlim(-0.5, len(allx) - 0.5); ax.yaxis.grid(True, color=GRID); ax.set_ylabel("TSLA", fontsize=13, weight="bold", color=INK)
ax.axvline(len(hist) - 0.5, color=GRAY, lw=1); ax.text(len(hist) - 0.4, 352, "today", fontsize=9.5, color=INK2)
ax.text(0.3, 445, "Oct: reset → block 1 → dip → block 2 → stall", fontsize=10, color=INK2); ax.legend(fontsize=10, frameon=False, loc="lower right")
ev = {"2026-11-03": "vote", "2026-11-04": "results", "2026-11-06": "weekly", "2026-11-13": "weekly", "2026-11-20": "MONTHLY", "2026-10-16": "monthly"}
ax.set_xticks(range(len(allx))); ax.set_xticklabels([d.strftime("%b %d") + ("\n" + ev[str(d.date())] if str(d.date()) in ev else "") for d in allx], rotation=60, fontsize=9)
gx = fig.add_axes([0.03, 0.02, 0.94, 0.2]); gx.axis("off"); gx.set_xlim(0, 100); gx.set_ylim(0, 10)
gx.text(0, 9.2, "How to confirm each phase with our gauges (check them as it unfolds)", fontsize=13, weight="bold", color=INK)
G = [("1. PUSH", "own gamma rising toward the\n90th (pinned); 430–440 reached;\nTSLA DIX ≥ top third", BLUE), ("2. PILE-UP", "near-price OI ≥ 33rd (not freed);\nnew calls at 440+; skew flat =\ntop warning (lean)", GRAY),
     ("3. DIP", "own gamma flushes ≤ 0.30;\nprice back toward the flip;\nDIX falling toward washed-out", ORG), ("4. RESET → NEW CYCLE", "monthly roll-off (28% of near OI):\nfreed ≤ 33rd; Monday up-burst;\nDIX turning up from low", BLUE)]
for i, (t, body, col) in enumerate(G):
    x = 0.5 + i * 25; gx.add_patch(FancyBboxPatch((x, 0.3), 23.5, 7.8, boxstyle="round,pad=0.2,rounding_size=0.8", fc="white", ec=col, lw=2))
    gx.text(x + 1, 6.8, t, fontsize=12, weight="bold", color=col if col != GRAY else INK2); gx.text(x + 1, 3.6, body, fontsize=10.4, color=INK, va="center")
fig.savefig(HERE / "out" / "tsla_cycle2.png", dpi=110, facecolor=BG); print("ok")
