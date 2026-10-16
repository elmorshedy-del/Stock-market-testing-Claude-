"""Follow-up 3 (descriptive, small n): when the S&P dips 2% under its 10-day high from a state like Oct 15 (5 sessions
earlier: GEX pct 0.35-0.66, VIX in its middle tercile 14.3-18.4), how often do the other conditions line up within the
dip day and the next 3 sessions (GEX <= 0.20, VIX > 18.4, DIX > 0.5), and what followed (tested up-leg within 20)?
Usage: OMP_NUM_THREADS=1 python dip_lineup.py -> out/dip_lineup.csv"""
import os
import sys

import numpy as np
import pandas as pd

import established_rules as E
import spy_channel as S
from ladder import first_on, outcomes            # noqa: E402  (original, imported unchanged)

f = E.build_fresh()
o = outcomes(f)
o["leg"] = o.leg.astype(float)
ev = pd.Series(first_on(f.c / f.c.rolling(10).max() - 1 <= -0.02), index=f.index)
prior = f.shift(5)
like_now = prior.gex_pct.between(0.35, 0.66) & prior.VIX.between(14.3, 18.4)
rows = []
for t in ev.index[ev & like_now]:
    i = f.index.get_loc(t)
    w = f.iloc[i:i + 4]
    rows.append({"dip day": t.date(), "GEX <= 0.20": (w.gex_pct <= 0.20).any(), "VIX > 18.4": (w.VIX > 18.37).any(), "DIX > 0.5": (w.dix_pct > 0.5).any(),
                 "GEX on the dip day": round(f.gex_pct.iloc[i], 2), "VIX on the dip day": round(f.VIX.iloc[i], 1), "DIX on the dip day": round(f.dix_pct.iloc[i], 2),
                 "tested up-leg within 20": o.leg.iloc[i]})
X = pd.DataFrame(rows).dropna(subset=["tested up-leg within 20"])
X["all three"] = X["GEX <= 0.20"] & X["VIX > 18.4"] & X["DIX > 0.5"]
X.to_csv(S.OUT / "dip_lineup.csv", index=False)
if __name__ == "__main__":
    print(X.to_string(index=False))
    print({k: round(float(X[k].mean()), 2) for k in ("GEX <= 0.20", "VIX > 18.4", "DIX > 0.5", "all three", "tested up-leg within 20")})
    print("up-leg | all three:", X[X["all three"]]["tested up-leg within 20"].mean(), "| not:", X[~X["all three"]]["tested up-leg within 20"].mean())
