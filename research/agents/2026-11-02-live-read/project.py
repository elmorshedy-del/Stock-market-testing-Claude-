"""Options-implied week projection (map, not a forecast edge): Gaussian paths, 78 steps per session, per-session sigma
from the Oct 30 term structure (2026-11-02-election-vol). Start = 08:20 ET premarket. Usage: python project.py -> out/project.json"""
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent; rng = np.random.default_rng(7); N = 40000; STEPS = 78
DAYS = ["Mon Nov 2", "Tue Nov 3", "Wed Nov 4", "Thu Nov 5", "Fri Nov 6"]
CFG = {"SPY": {"start": 758.60, "fri": 755.72, "sig": [0.99, 0.98, 1.08, 0.94, 1.06],
               "levels": {"flip 766.4": 766.43, "774": 774.0, "780": 780.0, "put wall 750": 750.0, "pocket floor 743.6": 743.63, "kill line 740.6": 740.6}},
       "TSLA": {"start": 402.22, "fri": 399.81, "sig": [2.57, 3.26, 3.26, 2.48, 2.48],
                "levels": {"410": 410.0, "420": 420.0, "435": 435.0, "450": 450.0, "put wall 380": 380.0, "flip 376.8": 376.8, "350": 350.0}}}
out = {}
for sym, c in CFG.items():
    sig = np.repeat(np.array(c["sig"]) / 100 / np.sqrt(STEPS), STEPS)
    lp = np.log(c["start"]) + np.cumsum(rng.standard_normal((N, len(sig))) * sig - sig ** 2 / 2, axis=1); px = np.exp(lp)
    closes = px[:, STEPS - 1::STEPS]
    o = {"daily close bands (5/16/50/84/95 pct)": {d: np.percentile(closes[:, i], [5, 16, 50, 84, 95]).round(1).tolist() for i, d in enumerate(DAYS)},
         "P(Mon close > Fri close)": round(float((closes[:, 0] > c["fri"]).mean()), 3), "P(Fri Nov 6 close > Fri Oct 30 close)": round(float((closes[:, 4] > c["fri"]).mean()), 3),
         "touch by Fri Nov 6 (intraday)": {}, "Fri Nov 6 close beyond": {}}
    for k, L in c["levels"].items():
        hit = (px.max(axis=1) >= L) if L > c["start"] else (px.min(axis=1) <= L)
        o["touch by Fri Nov 6 (intraday)"][k] = round(float(hit.mean()), 3)
        o["Fri Nov 6 close beyond"][k] = round(float(((closes[:, 4] >= L) if L > c["start"] else (closes[:, 4] <= L)).mean()), 3)
    out[sym] = o
json.dump(out, open(HERE / "out" / "project.json", "w"), indent=1); print(json.dumps(out, indent=1))
