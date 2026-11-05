"""13:10 ET update: paths after the only precedent days as extreme as today (exact counts in out/exact_counts_1310.json)."""
import sys, json, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, pandas as pd
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "2026-11-05-liquidity-cycle")); from common import yahoo
O = Path(__file__).resolve().parent / "out"
fig, ax = plt.subplots(1, 2, figsize=(14, 5.6), dpi=150)
def paths(a, sym, items, title):
    c = yahoo(sym, "1994-01-01").close
    for d, lab, col in items:
        i = c.index.get_loc(pd.Timestamp(d)); x = 100 * (c.iloc[i:i + 61] / c.iloc[i] - 1)
        a.plot(range(len(x)), x.values, color=col, lw=2, label=lab)
    a.axhline(0, color="k", lw=0.8); a.axvline(20, color="#bbb", lw=0.8, ls=":"); a.text(20.5, a.get_ylim()[1] * 0.9 if a.get_ylim()[1] > 0 else 1, "20 days", fontsize=8, color="#777")
    a.set_xlabel("sessions after the day"); a.set_ylabel(f"{sym} % from that day's close"); a.legend(frameon=False, fontsize=8.5, loc="lower left")
    a.set_title(title, loc="left", fontweight="bold", fontsize=10.5); a.spines[["top", "right"]].set_visible(False)
paths(ax[0], "SPY", [("1997-10-27", "1997-10-27 Asian crisis", "#2e7d32"), ("2007-02-27", "2007-02-27 Shanghai crash", "#1565c0"), ("2018-02-05", "2018-02-05 Volmageddon", "#f9a825"), ("2018-10-10", "2018-10-10 Fed hiking + yields up (closest macro)", "#c62828")],
      "TODAY on its own: SPY −6σ has happened only 4 times since 1994.\nAll 4 were higher 20 days later; the lower lows were small and quick.")
paths(ax[1], "QQQ", [("2008-10-10", "2008-10-10 Lehman crash", "#6d4c41"), ("2020-03-12", "2020-03-12 COVID crash", "#7b1fa2")],
      "THE PAST 4 WEEKS: QQQ's 20-day drop (−2.6σ) has been this\nextreme only in Oct 2008 and Mar 2020: crashes, near (not at) the low.")
fig.suptitle("Now at once-a-decade extremes: a bounce is the base case. Oct 2018 (the macro twin) bounced, then fell again into December.", x=0.01, ha="left", fontsize=12, fontweight="bold")
fig.text(0.01, 0.005, "Yahoo daily closes; σ = prior 60-day stdev; 'as extreme' = at least today's live value (~13:10 ET). TSM's 5-day move (−3.9σ) has no precedent since 1997. Descriptive.", fontsize=7.5, color="#555")
plt.tight_layout(rect=(0, 0.03, 1, 0.92)); plt.savefig(O / "extremes_1310.png"); print("ok")
