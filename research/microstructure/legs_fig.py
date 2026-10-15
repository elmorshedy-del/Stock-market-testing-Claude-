"""Figures for REPORT 4v: the hand-picked TSLA moves (episodes.EPISODES) next to today, price vs own gamma
flip and call wall, and the path each move takes through (distance above own flip, own gamma percentile).
Usage: python legs_fig.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import OUT
from episodes import EPISODES, TODAY_START, panel

C1, C2, C3, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e6e5e0"
SURF = "#fcfcfb"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True,
                     "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.facecolor": SURF, "axes.facecolor": SURF,
                     "legend.frameon": False})
CASES = [(n, a, b) for n, a, b, _ in EPISODES]


def anatomy(x):
    f, axs = plt.subplots(2, 4, figsize=(16, 7.4))
    panels = CASES + [("TODAY (to Oct 9 close)", None, None)]
    for a, (name, s, e) in zip(axs.ravel(), panels):
        if s:
            s, e = pd.Timestamp(s), pd.Timestamp(e)
            w = x.loc[s - pd.Timedelta(days=35):e + pd.Timedelta(days=21)]
        else:
            w = x.loc[pd.Timestamp(TODAY_START) - pd.Timedelta(days=35):]
            a.axvline(pd.Timestamp(TODAY_START), color=C1, lw=1, ls=":")
        spot = w.spot
        flip = spot / (1 + w.flip / 100)
        a.plot(w.index, spot, color=INK, lw=1.6, label="TSLA (option-implied spot)")
        a.plot(w.index, flip, color=C2, lw=1.6, label="own gamma flip")
        a.step(w.index, w.call_wall.rolling(3, min_periods=1).median(), where="post", color=C3, lw=1.3,
               label="call wall (3-day median)")
        if s:
            a.axvspan(s, e, color=C3, alpha=0.08, lw=0)
        a.tick_params(axis="x", labelsize=7.5, rotation=0)
        a.xaxis.set_major_locator(matplotlib.dates.AutoDateLocator(maxticks=4))
        a.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b %d\n%Y"))
        a.set_title(name, loc="left", fontsize=9.5, color=C1 if not s else INK, weight="bold" if not s else "normal")
        if not s:
            for sp in a.spines.values():
                sp.set_edgecolor(C1)
            n = w.iloc[-1]
            a.annotate(f"flip {flip.iloc[-1]:.0f}  ·  wall {n.call_wall:.0f}\nown gamma {n.g_pct:.2f}  ·  IV pct {n.iv_pct:.2f}",
                       (0.02, 0.04), xycoords="axes fraction", fontsize=8, color=C1)
    h, l = axs[0, 0].get_legend_handles_labels()
    f.legend(h, l, loc="lower center", ncol=6, fontsize=8, bbox_to_anchor=(0.5, -0.005))
    f.suptitle("The TSLA moves you named (green band = start to top, picked by hand), underneath: price vs its own gamma flip "
               "and largest call strike. Today in blue (dotted = the Sep 29 base).", x=0.01, ha="left", fontsize=10.5, color=INK)
    f.tight_layout(rect=(0, 0.04, 1, 1))
    f.savefig(OUT / "legs_anatomy_TSLA.png", dpi=150)


def path_map(x):
    """Each named move as a path in (% above own flip, own gamma percentile), 3-day smoothed, from 10 sessions
    before its start to its top; today's path from 10 sessions before the Sep 29 base."""
    f, a = plt.subplots(figsize=(9.5, 6))
    offs = {"Oct 2021": (4, -10), "Jan 2023": (-34, 6), "May 2023": (-14, 6), "Jun-Jul 2024": (-34, 6),
            "Oct-Nov 2024": (4, -10), "Apr-May 2025": (4, -10), "Sep 2025": (-16, -12)}
    for name, s_, e in CASES:
        i0, it = x.index.searchsorted(pd.Timestamp(s_)), x.index.searchsorted(pd.Timestamp(e))
        w = x.iloc[i0 - 10:it + 1]
        px, py = w.flip.clip(-15, 25).rolling(3, min_periods=1).mean(), w.g_pct.rolling(3, min_periods=1).mean()
        a.plot(px, py, color=MUTED, lw=1, alpha=0.7)
        a.scatter(px.iloc[0], py.iloc[0], s=18, color=MUTED, zorder=3)
        k0 = 10 if len(px) > 10 else 0
        a.scatter(px.iloc[k0], py.iloc[k0], s=34, marker="o", facecolor=SURF, edgecolor=MUTED, lw=1.4, zorder=3)
        a.scatter(px.iloc[-1], py.iloc[-1], s=26, marker="s", color=MUTED, zorder=3)
        a.annotate(name, (px.iloc[-1], py.iloc[-1]), xytext=offs.get(name, (3, 3)), textcoords="offset points", fontsize=7, color=MUTED)
    i0 = x.index.searchsorted(pd.Timestamp(TODAY_START))
    t = x.iloc[i0 - 10:]
    px, py = t.flip.clip(-15, 25).rolling(3, min_periods=1).mean(), t.g_pct.rolling(3, min_periods=1).mean()
    a.plot(px, py, color=C1, lw=2.4, label="TSLA from 10 sessions before the Sep 29 base to now")
    a.scatter(px.iloc[10], py.iloc[10], s=50, facecolor=SURF, edgecolor=C1, lw=1.8, zorder=5)
    a.scatter(px.iloc[-1], py.iloc[-1], s=60, color=C1, edgecolor=SURF, lw=1.5, zorder=5)
    a.annotate("today", (px.iloc[-1], py.iloc[-1]), xytext=(-34, -4), textcoords="offset points", color=C1, fontsize=9, weight="bold")
    a.set_xlim(-15, 25)
    a.set_ylim(0, 1)
    a.set_xlabel("% above TSLA's own gamma flip (3-day smoothed)")
    a.set_ylabel("own gamma percentile (low = put-heavy, high = call-heavy)")
    a.legend(loc="upper left", fontsize=8)
    a.set_title("Each named move (grey): small dot = 2 weeks before, open circle = the start, square = the top.\n"
                "They start near the flip and finish stretched and call-heavy; today in blue", loc="left", fontsize=9.5, color=INK)
    f.tight_layout()
    f.savefig(OUT / "legs_path_TSLA.png", dpi=150)


if __name__ == "__main__":
    x = panel()
    x["flip"] = x.to_flip_pct
    anatomy(x)
    path_map(x)
    print("saved legs_anatomy_TSLA.png, legs_path_TSLA.png")
