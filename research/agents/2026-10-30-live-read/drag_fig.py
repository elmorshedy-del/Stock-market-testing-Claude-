"""out/tsla_drag.png: TSLA vs S&P on S&P down days <= -1% (2020-2026-10-14), colored by TSLA's own gamma state (D1),
plus Friday's translator: SPY close -> TSLA at beta 2.0 (event-day average) and 2.65 (60-day beta to Oct 29). Usage: python drag_fig.py"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; OUT = HERE / "out"
E = pd.read_csv(OUT / "d1_events.csv", index_col=0, parse_dates=True)
GREEN, RED, INK, MUTED, SURF, BLUE, AMBER = "#1baf7a", "#d64545", "#0b0b0b", "#52514e", "#fcfcfb", "#2a78d6", "#e8a33d"
plt.rcParams.update({"font.size": 10.5, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED, "text.parse_math": False,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
fig, (a, b) = plt.subplots(1, 2, figsize=(16, 8.5), gridspec_kw={"width_ratios": [1.2, 1], "wspace": 0.22})
for st, col, lab in (("low", MUTED, "TSLA own gamma LOW"), ("mid", AMBER, "own gamma mid"), ("high", GREEN, "own gamma HIGH (like Friday)")):
    x = E[E.own_state == st]; a.scatter(x.s * 100, x.t * 100, s=28, color=col, alpha=0.8, label=f"{lab} (n {len(x)}): TSLA {x.t.mean()*100:+.1f}% avg")
xx = np.linspace(-6, -1, 10); a.plot(xx, 2 * xx, color=INK, lw=1.2, ls="--"); a.text(-5.9, -11.2, "TSLA = 2 × S&P", fontsize=9.5, color=INK)
a.axhline(0, color=MUTED, lw=0.6); a.set_xlim(-6.2, -0.8); a.set_ylim(-22, 12)
a.set_xlabel("S&P 500 that day, %"); a.set_ylabel("TSLA that day, %"); a.legend(frameon=False, fontsize=9.3, loc="upper left")
a.set_title("1. On S&P −1% days TSLA falls ~2× the S&P,\n    whatever its own dealer cushion (195 days, 2020–26)", loc="left", fontsize=12.5, weight="bold", color=INK)

rows = [(767, "SPY 767"), (765, "SPY 765"), (762, "SPY 762"), (760, "SPY 760"), (758, "SPY 758"), (754, "SPY 754"), (750, "SPY 750")]
y = np.arange(len(rows))[::-1]
for yi, (spy, lab) in zip(y, rows):
    r = spy / 769.36 - 1; lo, hi = 403.30 * (1 + 2.65 * r), 403.30 * (1 + 2.0 * r)
    b.plot([lo, hi], [yi, yi], color=INK, lw=7, solid_capstyle="round", alpha=0.85)
    b.text(hi + 0.8, yi, f"{lo:.0f}–{hi:.0f}", va="center", fontsize=10.5, color=INK)
for lv, txt, col in ((400, "400", GREEN), (395, "395", MUTED), (388.7, "389 triple top", MUTED), (371, "371 flip", RED)):
    b.axvline(lv, color=col, lw=1.3 if lv in (400, 371) else 0.9, ls="-" if lv in (400, 371) else "--"); b.text(lv, len(rows) - 0.4, txt, rotation=90, fontsize=9, color=col, ha="right", va="top")
b.set_yticks(y); b.set_yticklabels([r[1] for r in rows]); b.set_xlim(366, 410); b.set_ylim(-0.7, len(rows) - 0.3)
b.set_xlabel("TSLA close implied by the SPY close (beta 2.0 to 2.65, from Thursday's 403.30)")
b.set_title("2. Friday translator: where SPY closes → where TSLA lands", loc="left", fontsize=12.5, weight="bold", color=INK)
fig.suptitle("SPY drags TSLA: on market selloff days, TSLA's own dealer cushion doesn't show up", x=0.01, ha="left", fontsize=14.5, weight="bold", color=INK)
fig.text(0.01, 0.005, "D1 (pre-registered @ 7f12ecb): cushion and override both fail (Holm 0.71). Hint, secondary: with S&P gamma not low, high own gamma → next-day TSLA +1.1 pts vs low (p 0.08).\n"
         "Translator ignores TSLA news; TSLA after hours was already 397.45 with NQ −2%. Beta 2.65 = 60-day to Oct 29 (corr 0.62); 2.0 = average on S&P −1% days.", fontsize=9.3, color=MUTED)
fig.savefig(OUT / "tsla_drag.png", dpi=125, bbox_inches="tight"); print("ok")
