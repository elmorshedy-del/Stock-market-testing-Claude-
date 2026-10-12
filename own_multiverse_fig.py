"""Figure for REPORT 4z: every specification of the own-positioning multiverse as one dot, by signal
and outcome, for "turn-on" days and "in state" days. Dots are standardized against the shifted null,
so the grey band (+-1.96) is where luck puts 95% of them.
Usage: python own_multiverse_fig.py TSLA MSFT      (after own_multiverse.py)
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import OUT

C1, C2, C3, INK, MUTED, GRID, SURF = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
                     "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": SURF,
                     "axes.facecolor": SURF, "legend.frameon": False})
SIG = [("below flip", "below its own gamma flip"), ("put-heavy", "put-heavy own gamma"), ("freed", "freed (little OI near price)")]
OUTC = [("up", "up-move starts within H", C3), ("down", "down-move starts within H", C2), ("return", "forward return", C1)]


def fig(syms):
    f, axs = plt.subplots(len(syms), 3, figsize=(15, 3.6 * len(syms) + 0.9), sharex=True, squeeze=False)
    rng = np.random.default_rng(0)
    for r, sym in enumerate(syms):
        d = pd.read_csv(OUT / f"own_multiverse_{sym}.csv")
        for c, (dr, lab, col) in enumerate(OUTC):
            a = axs[r, c]
            a.axvspan(-1.96, 1.96, color=MUTED, alpha=0.1, lw=0)
            a.axvline(0, color=INK, lw=0.7)
            ticks, names = [], []
            for i, (sg, sname) in enumerate(SIG):
                for j, days in enumerate(("in state", "turn-on")):
                    y0 = i * 2.6 + j
                    z = d[(d.signal == sg) & (d.direction == dr) & (d.days == days)].z.dropna().clip(-6, 6)
                    a.scatter(z, y0 + rng.uniform(-0.28, 0.28, len(z)), s=7, color=col, alpha=0.45 if days == "in state" else 0.25, lw=0)
                    if len(z):
                        a.plot([z.median()] * 2, [y0 - 0.4, y0 + 0.4], color=INK, lw=2.2)
                        a.annotate(f"{(z > 1.96).mean():.0%} high / {(z < -1.96).mean():.0%} low", (6.1, y0), fontsize=7.5, color=MUTED,
                                   va="center", annotation_clip=False)
                    ticks.append(y0)
                    names.append(f"{sname}, {days}" if j == 0 else days)
            a.set_yticks(ticks, names if c == 0 else [""] * len(ticks), fontsize=8)
            a.invert_yaxis()
            a.set_xlim(-6, 6)
            a.grid(axis="y", visible=False)
            a.set_title(f"{sym}: {lab}", loc="left", fontsize=9.5, color=INK)
    f.suptitle("Own-positioning multiverse, strictly forward: the extra moves after below-flip / put-heavy TSLA days are UP-moves "
               "(snap-backs), freed days move both ways,\nand no reading sets the direction of returns. Each dot = one combination of "
               "threshold, move definition, horizon and era; black tick = median.", x=0.01, ha="left", fontsize=10.5, color=INK, weight="bold")
    f.supxlabel("effect vs the time-shifted null (z score); grey band = where luck puts 95% of specifications", fontsize=9, color=MUTED)
    f.tight_layout(rect=(0, 0, 0.95, 0.95))
    f.savefig(OUT / "own_multiverse.png", dpi=150)
    print("saved", OUT / "own_multiverse.png")


if __name__ == "__main__":
    fig(sys.argv[1:] or ["TSLA", "MSFT"])
