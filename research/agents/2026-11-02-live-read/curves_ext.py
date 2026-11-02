"""Extended total-gamma curves (map, not a test): SPY 700-820, TSLA 340-480, positions = OI dated Nov 2 (Fri close), IVs = Oct 30 chains.
Also new OI by strike Oct 30 -> Nov 2 for TSLA (calls/puts, Nov-Dec expiries). Usage: python curves_ext.py <td dir> <TSLA oi Oct20-30 file>"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent / "2026-10-27-flip-wicks")]
from flipmap import norm, preopen, gex_at   # noqa: E402

td = Path(sys.argv[1]); P, MON = pd.Timestamp("2026-10-30"), pd.Timestamp("2026-11-02")
RNG = {"SPY": (700, 820, 241), "TSLA": (340, 480, 141)}; SPOT = {"SPY": 755.72, "TSLA": 399.81}; out = {}
for sym, (a, b, n) in RNG.items():
    e = norm(pd.read_csv(td / f"{sym}_eod_20261030.csv.gz")); e = e[e.date == P]; o = norm(pd.read_csv(td / f"{sym}_oi_20261102.csv.gz"))
    g = preopen(e, o, MON); g = g[g.expiration >= MON].copy(); g["underlying_close"] = SPOT[sym]
    grid = np.linspace(a, b, n); tot = np.array([gex_at(g, s) for s in grid]) / 1e9
    out[sym] = {"price": grid.round(2).tolist(), "total gamma $bn per 1%": tot.round(3).tolist()}
    pk = grid[np.argmax(tot)]; print(sym, "peak", round(pk, 1), "| values:", {round(x): round(y, 2) for x, y in zip(grid[::10], tot[::10])})
# TSLA new OI by strike, Oct 30 file (Oct 29 close) -> Nov 2 file (Oct 30 close)
old = norm(pd.read_csv(sys.argv[2])); new = norm(pd.read_csv(td / "TSLA_oi_20261102.csv.gz"))
oc = [c for c in old.columns if "open_interest" in c or c == "oi"][0]; nc = [c for c in new.columns if "open_interest" in c or c == "oi"][0]
print(old.columns.tolist()[:12])
old = old[old.date == old.date.max()]
def agg(x, c):
    x = x[(pd.to_datetime(x.expiration) >= MON) & (pd.to_datetime(x.expiration) <= pd.Timestamp("2026-12-31"))]
    return x.groupby(["strike", "cp"])[c].sum()
d = (agg(new, nc) - agg(old, oc)).dropna().unstack().fillna(0)
d = d[(d.index >= 340) & (d.index <= 480)]
out["TSLA new OI Oct 29 close -> Oct 30 close (Nov-Dec expiries), thousand contracts"] = {
    "old file date": str(old.date.max().date()),
    "top call adds": (d.C.sort_values(ascending=False).head(6) / 1e3).round(1).to_dict(), "top put adds": (d.P.sort_values(ascending=False).head(6) / 1e3).round(1).to_dict(),
    "net calls / puts": [round(float(d.C.sum() / 1e3), 1), round(float(d.P.sum() / 1e3), 1)]}
print(json.dumps(out["TSLA new OI Oct 29 close -> Oct 30 close (Nov-Dec expiries), thousand contracts"], default=float))
json.dump(out, open(HERE / "out" / "curves_ext.json", "w"), default=float)
