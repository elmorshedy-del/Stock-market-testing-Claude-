"""Monday Nov 2 maps for SPY and TSLA after the Oct 30 expiry. Positions = OI dated Oct 30 (Oct 29 close; Friday's
trading is not in it), IVs = Oct 30 closing chains, spot = Oct 30 close. Engine code imported unchanged.
Also TSLA own-options state (freed / flip / own-gamma pct) and TSLA 25-delta risk reversal + ATM IV on Oct 30.
Usage: python maps_mon.py <live31/td> -> out/maps_mon.json, out/curves_mon.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
MICRO = HERE.parents[1] / "microstructure"
sys.path[:0] = [str(HERE.parent / "2026-10-27-flip-wicks"), str(HERE.parent / "2026-10-30-permanence"), str(MICRO), str(HERE.parent / "2026-10-26-tsla-gap-states")]
from flipmap import norm, preopen, fine_flip, gex_at, exposures       # noqa: E402
from skew import one_month                                             # noqa: E402
import td_gamma as t                                                   # noqa: E402
from hd_gamma import day_metrics                                       # noqa: E402

td = Path(sys.argv[1]); P, MON = pd.Timestamp("2026-10-30"), pd.Timestamp("2026-11-02")
SPOT = {"SPY": 755.72, "TSLA": 399.81}
out, curves = {}, {}
for sym in ("SPY", "TSLA"):
    e = norm(pd.read_csv(td / f"{sym}_eod_20261030.csv.gz")); e = e[e.date == P]
    o = norm(pd.read_csv(td / f"{sym}_oi_20261030.csv.gz"))
    S = SPOT[sym]; g = preopen(e, o, MON); g = g[g.expiration >= MON].copy(); g["underlying_close"] = S
    ex = exposures(g, S); byk = ex.groupby("K").gex.sum() / 1e9
    near = byk[(byk.index >= 0.94 * S) & (byk.index <= 1.06 * S)]
    grid = np.linspace(0.93 * S, 1.07 * S, 141); tot = np.array([gex_at(g, s) for s in grid]) / 1e9
    k45 = g[((g.expiration - MON).dt.days <= 45) & g.K.between(0.75 * S, 1.25 * S)]
    neg = grid[tot < 0]
    first = g.expiration.min(); exf = ex[ex.exp == first.date()]
    out[sym] = {"spot (Oct 30 close)": S, "flip": round(fine_flip(g, S), 2), "total gamma $bn per 1% at spot": round(float(gex_at(g, S) / 1e9), 2),
                "call wall": float(k45[k45.cp == "C"].groupby("K").oi.sum().idxmax()), "put wall": float(k45[k45.cp == "P"].groupby("K").oi.sum().idxmax()),
                "top positive strikes": near.sort_values(ascending=False).head(4).round(3).to_dict(), "top negative strikes": near.sort_values().head(4).round(3).to_dict(),
                "most negative total-gamma price": round(float(grid[np.argmin(tot)]), 2), "most positive total-gamma price": round(float(grid[np.argmax(tot)]), 2),
                "short-gamma zone": [round(float(neg.min()), 1), round(float(neg.max()), 1)] if len(neg) else None,
                f"nearest expiry {first.date()} share of |gamma|": round(float(exf.gex.abs().sum() / ex.gex.abs().sum()), 3)}
    curves[sym] = {"spot": S, "price": grid.round(2).tolist(), "total gamma $bn": tot.round(3).tolist()}
# TSLA own-options state (same recipe as 2026-10-30-live-read/tsla_state.py)
e = norm(pd.read_csv(td / "TSLA_eod_20261030.csv.gz")); e = e[e.date == P].copy(); e["mid"] = (e.bid + e.ask) / 2
o = norm(pd.read_csv(td / "TSLA_oi_20261030.csv.gz")).rename(columns=lambda c: "oi" if "open_interest" in c else c)
g0 = t.chain_day(e.assign(oi=0.0)).drop(columns=["oi"]).merge(o[["expiration", "strike", "cp", "oi"]], on=["expiration", "strike", "cp"], how="left").fillna({"oi": 0})
h = pd.read_csv(MICRO / "out" / "td_gamma_TSLA.csv", parse_dates=["date"]).set_index("date").iloc[-251:]
gn_hist = h.gex_classic / (h.spot * (h.call_oi + h.put_oi) * 100)
S0 = SPOT["TSLA"]; gg = g0[(g0.expiration > P) & ((g0.expiration - P).dt.days <= t.MAX_DTE) & (g0.oi > 0)].copy()
gg["date"], gg["T"], gg["underlying_close"] = P, ((gg.expiration - P).dt.days / 365).clip(lower=1 / (365 * 24)), S0
m = day_metrics(gg, P, {"TSLA": ["TSLA"]})[0]; gn = m["gex_classic"] / (S0 * (m["call_oi"] + m["put_oi"]) * 100)
out["TSLA state"] = {"flip": round(float(m["flip_classic"]), 1), "% above flip": round(float(100 * (S0 / m["flip_classic"] - 1)), 2),
                     "near-OI pct": round(float((h.near_oi_share < m["near_oi_share"]).mean()), 3), "own-gamma pct": round(float((gn_hist < gn).mean()), 3),
                     "call wall": float(m["call_wall"]), "put wall": float(m["put_wall"])}
sk = one_month(("TSLA", td / "TSLA_eod_20261030.csv.gz"))
out["TSLA skew Oct 30"] = {k: (round(v, 4) if isinstance(v, float) else str(v)) for k, v in sk[-1].items()} if sk else None
json.dump(out, open(HERE / "out" / "maps_mon.json", "w"), indent=1, default=float)
json.dump(curves, open(HERE / "out" / "curves_mon.json", "w"))
print(json.dumps(out, indent=1, default=float))
