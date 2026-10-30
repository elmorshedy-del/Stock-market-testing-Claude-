"""Oct 29 close -> Friday Oct 30 (month-end, heavy expiry) and Monday Nov 2 (post-expiry) maps for SPY and TSLA.
Positions = OI dated Oct 28 (Oct 27 close; Oct 29 OI not yet published), IVs = Oct 28 closing chains. Engine code unchanged.
Evaluated at two spots each: the Oct 29 close and the after-hours level. Usage: python maps.py <live28/td> <live29/td> -> out/maps.json, out/curves.json (total-gamma profiles, aggregates only)"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "2026-10-27-flip-wicks"))
from flipmap import norm, preopen, fine_flip, gex_at, exposures, t       # noqa: E402

oi_dir, eod_dir = map(Path, sys.argv[1:3])
P, FRI, MON = pd.Timestamp("2026-10-28"), pd.Timestamp("2026-10-30"), pd.Timestamp("2026-11-02")
SPOTS = {"SPY": {"close Oct 29": 769.36, "after hours": 764.73}, "TSLA": {"close Oct 29": 403.30, "after hours": 397.45}}
out, curves = {}, {}
for sym in ("SPY", "TSLA"):
    e = norm(pd.read_csv(eod_dir / f"{sym}_eod_20261028.csv.gz")); e = e[e.date == P]
    o = norm(pd.read_csv(oi_dir / f"{sym}_oi_20261028.csv.gz"))
    res = {}
    for nm, D in (("Friday Oct 30 (incl. the expiry)", FRI), ("Monday Nov 2 (after the expiry)", MON)):
        g = preopen(e, o, D); g = g[g.expiration >= D]
        for lab, S in SPOTS[sym].items():
            g2 = g.copy(); g2["underlying_close"] = S
            ex = exposures(g2, S); byk = ex.groupby("K").gex.sum() / 1e9
            near = byk[(byk.index >= 0.94 * S) & (byk.index <= 1.06 * S)]
            grid = np.linspace(0.93 * S, 1.07 * S, 141); tot = np.array([gex_at(g2, s) for s in grid]) / 1e9
            k45 = g2[((g2.expiration - D).dt.days <= 45) & g2.K.between(0.75 * S, 1.25 * S)]   # engine wall definition
            neg = grid[tot < 0]
            curves[f"{sym} | {nm} | {lab}"] = {"spot": S, "price": grid.round(2).tolist(), "total gamma $bn": tot.round(3).tolist()}
            res[f"{nm} @ {lab} {S}"] = {"flip": round(fine_flip(g2, S), 2), "total gamma $bn per 1% at spot": round(float(gex_at(g2, S) / 1e9), 2),
                "call wall": float(k45[k45.cp == "C"].groupby("K").oi.sum().idxmax()), "put wall": float(k45[k45.cp == "P"].groupby("K").oi.sum().idxmax()),
                "top positive strikes": near.sort_values(ascending=False).head(4).round(3).to_dict(), "top negative strikes": near.sort_values().head(4).round(3).to_dict(),
                "most negative total-gamma price (pocket centre)": round(float(grid[np.argmin(tot)]), 2), "short-gamma zone": [round(float(neg.min()), 1), round(float(neg.max()), 1)] if len(neg) else None}
        exq = exposures(g.assign(underlying_close=SPOTS[sym]["close Oct 29"]), SPOTS[sym]["close Oct 29"])
        if D == FRI:
            res["Oct 30 expiry share of |gamma|"] = round(float(exq[exq.exp == FRI.date()].gex.abs().sum() / exq.gex.abs().sum()), 3)
    # TSLA 'freed': near-price OI share (+-5%, <=45d) before vs after Friday
    S = SPOTS[sym]["close Oct 29"]; oc = next(c for c in o.columns if "open_interest" in c); dte = (o.expiration - P).dt.days
    base = o[(dte >= 0) & (dte <= 120)][oc].sum(); nearoi = lambda m: o[m & o.strike.between(0.95 * S, 1.05 * S) & ((o.expiration - P).dt.days <= 45)][oc].sum()
    res["near-price OI share now"] = round(float(nearoi(o.expiration >= FRI) / base), 4)
    res["near-price OI share after Friday"] = round(float(nearoi(o.expiration > FRI) / o[(o.expiration > FRI) & ((o.expiration - P).dt.days <= 120)][oc].sum()), 4)
    out[sym] = res
json.dump(out, open(HERE / "out" / "maps.json", "w"), indent=1, default=float)
json.dump(curves, open(HERE / "out" / "curves.json", "w"))
print(json.dumps(out, indent=1, default=float))
