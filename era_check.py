"""Does the gamma evidence survive the options-market structure breaks?

Eras (break dates from industry/academic sources, see REPORT.md 4g):
  2012-05 .. 2019-09  pre-retail: commissions, weekly/monthly expiries
  2019-10 .. 2022-05  zero commissions (Oct 2019) + retail boom (Mar 2020)
  2022-05 .. now      SPX expiries every weekday (Tue/Thu added Apr/May 2022): 0DTE era

Note: SqueezeMetrics GEX is built from end-of-day open interest, so same-day
(0DTE) positions, now ~60% of SPX volume, are invisible to it in the last era.
"""
import itertools

import numpy as np
import pandas as pd

from release import frame as rframe, gex_study
from strategy import frame, stats, trades

ERAS = [("2012-05-01", "2019-09-30", "pre-retail 2012-2019Q3"),
        ("2019-10-01", "2022-05-10", "zero-commission + retail boom"),
        ("2022-05-11", "2026-12-31", "daily expiries / 0DTE era")]
GRID = list(itertools.product((0.05, 0.10, 0.20), (0.10, 0.15, 0.20, 0.25), (0.80, 0.90, 0.95), (10, 20)))


if __name__ == "__main__":
    _, x = gex_study(rframe())
    x["gq"] = pd.qcut(x.gex_pct, 5, labels=False)
    top = x.fwd.quantile(0.9)
    for a, b, lab in ERAS:
        z = x.loc[a:b]
        t = z.groupby("gq").agg(n=("fwd", "size"), p_elevator=("fwd", lambda v: (v > top).mean()),
                                next10d_rv=("fwd_rv", "mean"))
        print(f"\n{lab}: corr(GEX pct, next-10d RV) = {np.corrcoef(z.gex_pct, z.fwd_rv)[0, 1]:.2f}")
        print(t.round(3).to_string())
    s = frame()
    print("\nfixed rule (arm .05, k .25, pin .95, 20d) and parameter grid, per era")
    for a, b, lab in ERAS:
        part = s.loc[a:b]
        st = stats(trades(part, 0.05, 0.25, 0.95, 20), part)
        g = [(p, stats(trades(part, *p), part)) for p in GRID]
        g = [(p, q) for p, q in g if q["n"]]
        pos = np.mean([q["excess"] > 0 for _, q in g])
        k25 = np.mean([q["excess"] for p, q in g if p[1] == 0.25])
        print(f"{lab}: n={st['n']} hit={st['hit']:.2f} excess={st['excess']:+.4f} "
              f"call mean/median={st['call_mean']:+.2f}/{st['call_median']:+.2f} | "
              f"grid share positive={pos:.2f}, k=.25 mean excess={k25:+.4f}")
