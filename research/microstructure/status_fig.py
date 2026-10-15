"""Status figure for the two live setups (REPORT 4ae and later updates), from the latest data on disk.
  TSLA  price vs its own gamma flip with the freed state shaded (end-of-day), plus an optional live
        point from today's open interest (tsla_live.status) and the flip after the next monthly expiry
  MSFT  the release setup of §4aa: MSFT's 20-day lead over SPY vs S&P dealer gamma, both as percentiles
Usage: python status_fig.py [DAY PRICE EXPIRY]      e.g. python status_fig.py 2026-10-15 362.58 2026-10-16
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from burst_gamma import state
from common import OUT, load_bars
from forecast import build
from held_back import pct

C1, C2, C3, INK, MUTED, SURF = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#fcfcfb"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.grid": True, "grid.color": "#e6e5e0", "axes.spines.top": False, "axes.spines.right": False,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "legend.frameon": False})


def main(live=None, start="2026-09-15"):
    f, (a, b) = plt.subplots(2, 1, figsize=(13, 9.5), gridspec_kw={"hspace": 0.38})
    st = state("TSLA").loc[start:]
    flip = st.spot / (1 + st.to_flip_pct / 100)
    freed = st.near_pct <= 1 / 3
    for d, on in freed.items():
        if on:
            a.axvspan(d - pd.Timedelta(hours=12), d + pd.Timedelta(hours=12), color=C3, alpha=0.15, lw=0)
    a.plot(st.index, st.spot, color=INK, lw=2, marker="o", ms=3, label="TSLA close (option-implied)")
    a.plot(st.index, flip, color=C2, lw=2, label="own gamma flip (end of day)")
    a.plot([], [], color=C3, alpha=0.4, lw=8, label="freed (near-price OI in its bottom third)")
    title2 = ""
    if live is not None:
        s, day, price, expiry = live
        now, after = s.iloc[1], s.iloc[2]
        a.scatter([day], [price], color=INK, s=60, zorder=5, edgecolor=SURF)
        a.scatter([day], [now["flip"]], color=C2, s=60, zorder=5, edgecolor=SURF)
        a.annotate(f"live {price:.2f}\nflip {now['flip']:.1f} ({now['% above flip']:+.1f}%)\nnear-OI pct {now['near-OI pct']:.2f}",
                   (day, price), xytext=(8, -34), textcoords="offset points", fontsize=8.5, color=INK)
        a.hlines(after["flip"], day, day + pd.Timedelta(days=5), color=C2, ls="--", lw=1.6)
        a.annotate(f"after {expiry:%b %d} expiry: flip {after['flip']:.0f}, near-OI pct {after['near-OI pct']:.2f}",
                   (day + pd.Timedelta(days=5), after["flip"]), xytext=(-4, -14), textcoords="offset points", ha="right",
                   fontsize=8.5, color=C2)
        a.axvline(expiry, color=MUTED, lw=1, ls=":")
        a.annotate(f"{expiry:%b %d}\nexpiry", (expiry, a.get_ylim()[1]), xytext=(3, -4), textcoords="offset points", va="top",
                   fontsize=8, color=MUTED)
        on_b, on_f = now["% above flip"] < 0, now["near-OI pct"] <= 1 / 3
        title2 = f"   Now: below flip {'ON' if on_b else 'off'}, freed {'ON' if on_f else 'off'}."
    a.set_xlim(pd.Timestamp(start), (live[1] if live else st.index[-1]) + pd.Timedelta(days=6))
    a.set_ylabel("TSLA")
    a.legend(loc="upper left", fontsize=8)
    a.set_title("TSLA vs its own gamma flip. The burst-up setup (§4w, §4ad) is freed AND below the flip: "
                f"39% vs 17% up/down-bursts within 3 sessions.{title2}", loc="left", fontsize=9.5, color=INK)

    g = build().gex_pct
    m, s_ = load_bars("MSFT").close, load_bars("SPY").close
    idx = m.index.intersection(s_.index)
    lm, ls = np.log(m.reindex(idx)), np.log(s_.reindex(idx))
    rs = pct((lm - lm.shift(20)) - (ls - ls.shift(20)))
    g, rs = g.loc[start:].dropna(), rs.loc[start:].dropna()
    b.axhspan(0, 1 / 3, color=C1, alpha=0.08, lw=0)
    b.axhspan(2 / 3, 1, color=C3, alpha=0.08, lw=0)
    b.plot(g.index, g, color=C1, lw=2.2, marker="o", ms=3, label="S&P dealer gamma percentile (low = market unpinned)")
    b.plot(rs.index, rs, color=C3, lw=2.2, marker="o", ms=3, label="MSFT 20-day lead over SPY, percentile")
    both = (rs.reindex(g.index) >= 2 / 3) & (g <= 1 / 3)
    b.scatter(g.index[both], g[both], color=INK, s=50, zorder=5, label="release setup ON")
    b.set_ylim(0, 1.02)
    b.set_xlim(a.get_xlim())
    b.set_ylabel("percentile vs trailing year")
    b.legend(loc="lower left", fontsize=8, ncol=3)
    last = g.index[-1]
    b.set_title(f"MSFT release (§4aa): S&P gamma {g.iloc[-1]:.2f} on {last:%b %d}, MSFT lead {rs.reindex([last]).iloc[0]:.2f}. "
                f"Setup {'ON' if both.iloc[-1] else 'off'}. Historically: up-leg within 10 sessions 50% vs 24%, +2.7% avg",
                loc="left", fontsize=9.5, color=INK)
    for ax in (a, b):
        ax.xaxis.set_major_locator(matplotlib.dates.WeekdayLocator(byweekday=0))
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b %d"))
    f.savefig(OUT / "status.png", dpi=150, bbox_inches="tight")
    print("saved", OUT / "status.png")


if __name__ == "__main__":
    live = None
    if len(sys.argv) > 3:
        import tsla_live as L
        day, price, expiry = pd.Timestamp(sys.argv[1]), float(sys.argv[2]), pd.Timestamp(sys.argv[3])
        s, _, _ = L.status("TSLA", day, price, expiry)
        live = (s, day, price, expiry)
    main(live)
