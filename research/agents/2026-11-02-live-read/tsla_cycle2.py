"""TSLA 'repeat October' storyboard (owner's scenario, NOT a forecast): push to 440 this week, thick-OI consolidation next week,
dip into the Nov 20 monthly, reset, new cycle from Nov 23. October template: pin Oct 6-9 -> dip -7% into the Oct 16 monthly -> reset at
the flip -> new cycle Oct 19. Options-implied odds of the waypoints from 413.5 (no drift; per-session sigma from the Oct 30 term structure).
Usage: python tsla_cycle2.py -> out/tsla_cycle2.json"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; rng = np.random.default_rng(21); N, ST = 40000, 78; S0 = 413.5
days = pd.bdate_range("2026-11-03", "2026-11-27", freq="C", holidays=["2026-11-26"])
sig = np.array([3.26, 3.26, 2.48, 2.48] + [2.5] * (len(days) - 4)) / 100        # Tue-Fri from the chain, then ~normal
path = np.cumsum(rng.standard_normal((N, len(days) * ST)) * np.repeat(sig / np.sqrt(ST), ST) - np.repeat((sig / np.sqrt(ST)) ** 2 / 2, ST), axis=1)
P = S0 * np.exp(path); di = {d: i for i, d in enumerate(days)}
def win(a, b): return slice(di[pd.Timestamp(a)] * ST, (di[pd.Timestamp(b)] + 1) * ST)
hit440 = P[:, win("2026-11-03", "2026-11-06")].max(1) >= 440
held = P[:, (di[pd.Timestamp("2026-11-13")] + 1) * ST - 1] >= 420   # Fri Nov 13 close >= 420
dip = P[:, win("2026-11-16", "2026-11-20")].min(1) <= 408
story = {"2026-11-02": 412, "2026-11-03": 422, "2026-11-04": 437, "2026-11-05": 432, "2026-11-06": 428,
         "2026-11-09": 435, "2026-11-10": 438, "2026-11-11": 433, "2026-11-12": 429, "2026-11-13": 427,
         "2026-11-16": 423, "2026-11-17": 417, "2026-11-18": 412, "2026-11-19": 407, "2026-11-20": 404,
         "2026-11-23": 416, "2026-11-24": 424, "2026-11-25": 431, "2026-11-27": 433}
res = {"start": S0, "storyboard closes": story,
       "options-implied odds (no drift)": {"touch >= 440 by Fri Nov 6": round(float(hit440.mean()), 2),
                                           "...and Fri Nov 13 close >= 420 (consolidating up there)": round(float((hit440 & held).mean()), 2),
                                           "...and dip <= 408 during Nov 16-20 (the whole storyboard)": round(float((hit440 & held & dip).mean()), 2),
                                           "dip <= 408 during Nov 16-20, given 440 was touched": round(float(dip[hit440].mean()), 2)},
       "October template (actual)": {"pin": "Oct 6 381.0 (own gamma 0.89)", "high": "Oct 9 382.7", "dip into the Oct 16 monthly": "354.7 (-7.3% from Oct 9)",
                                     "reset": "Oct 16 own gamma 0.17, at the flip, freed 0.03, TSLA DIX 2nd pct", "new cycle": "Oct 19 +3.8%, then +9% Mon-Wed"}}
json.dump(res, open(HERE / "out" / "tsla_cycle2.json", "w"), indent=1); print(json.dumps(res["options-implied odds (no drift)"], indent=1))
