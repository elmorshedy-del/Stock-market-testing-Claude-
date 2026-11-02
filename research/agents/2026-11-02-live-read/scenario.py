"""Bull-case storyboard for SPY and TSLA to Nov 27 (a scenario built from our maps and rules, NOT a forecast), plus the
options-implied odds of its waypoints (correlated Gaussian paths, rho 0.6, SPY 1.0%/day, TSLA 2.6%/day, 78 steps/session).
Usage: python scenario.py <spot SPY> <spot TSLA> -> out/scenario.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; s0, t0 = float(sys.argv[1]), float(sys.argv[2])
days = pd.bdate_range("2026-11-02", "2026-11-27", freq="C", holidays=["2026-11-26"])
# storyboard closes (SPY, TSLA) by session, with the phase each belongs to
path = {"2026-11-02": (760, 406), "2026-11-03": (757, 413), "2026-11-04": (751, 416), "2026-11-05": (758, 410), "2026-11-06": (763, 405),
        "2026-11-09": (767, 417), "2026-11-10": (769, 423), "2026-11-11": (772, 431), "2026-11-12": (774, 429), "2026-11-13": (776, 427),
        "2026-11-16": (778, 438), "2026-11-17": (780, 446), "2026-11-18": (781, 451), "2026-11-19": (779, 445), "2026-11-20": (777, 437),
        "2026-11-23": (772, 428), "2026-11-24": (770, 421), "2026-11-25": (773, 424), "2026-11-27": (775, 426)}
assert all(pd.Timestamp(d) in days for d in path)
rng = np.random.default_rng(11); N, ST = 40000, 78
n = days.get_loc(pd.Timestamp("2026-11-20")) + 1
z1 = rng.standard_normal((N, n * ST)); z2 = 0.6 * z1 + np.sqrt(1 - 0.36) * rng.standard_normal((N, n * ST))
ss, ts = 0.010 / np.sqrt(ST), 0.026 / np.sqrt(ST)
S = s0 * np.exp(np.cumsum(z1 * ss - ss ** 2 / 2, axis=1)); T = t0 * np.exp(np.cumsum(z2 * ts - ts ** 2 / 2, axis=1))
idx = lambda d: (days.get_loc(pd.Timestamp(d)) + 1) * ST
res = {"start": {"SPY": s0, "TSLA": t0}, "storyboard": {d: {"SPY": v[0], "TSLA": v[1]} for d, v in path.items()},
       "options-implied odds of the waypoints (no drift)": {
           "SPY trades <= 751 by Wed Nov 4 (the shakeout)": round(float((S[:, :idx("2026-11-04")].min(1) <= 751).mean()), 2),
           "SPY trades >= 766.4 (flip) by Wed Nov 11": round(float((S[:, :idx("2026-11-11")].max(1) >= 766.43).mean()), 2),
           "SPY trades >= 780 by Fri Nov 20": round(float((S.max(1) >= 780).mean()), 2),
           "TSLA trades >= 420 by Wed Nov 11": round(float((T[:, :idx("2026-11-11")].max(1) >= 420).mean()), 2),
           "TSLA trades >= 450 by Fri Nov 20": round(float((T.max(1) >= 450).mean()), 2),
           "both: SPY >= 780 and TSLA >= 450 by Nov 20": round(float(((S.max(1) >= 780) & (T.max(1) >= 450)).mean()), 2)}}
json.dump(res, open(HERE / "out" / "scenario.json", "w"), indent=1); print(json.dumps(res["options-implied odds of the waypoints (no drift)"], indent=1))
