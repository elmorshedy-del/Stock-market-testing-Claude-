"""Refresh (v2) of the Nov 4 map with Tuesday's closing positions (OI dated Nov 4) and Wed 08:00 ET premarket references.
Original map.py is untouched. Positions = OI dated Nov 4 (Tue close),
IVs = Tue Nov 3 closing chains. Engine code imported unchanged (flip-wicks flipmap, microstructure hd_gamma/td_gamma).
Usage: python map.py <td dir> -> out/map.json"""
import json
import sys
from math import erf, log, sqrt
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; MICRO = HERE.parents[1] / "microstructure"
sys.path[:0] = [str(HERE.parent / "2026-10-27-flip-wicks"), str(MICRO)]
from flipmap import norm, preopen, fine_flip, gex_at, exposures   # noqa: E402
import td_gamma as t                                              # noqa: E402
from hd_gamma import day_metrics                                  # noqa: E402

td = Path(sys.argv[1]); P, D = pd.Timestamp("2026-11-03"), pd.Timestamp("2026-11-04")
REF = {"SPY": 760.1, "TSLA": 376.0}; AH = {"SPY": 752.16, "TSLA": 391.64}; FUT = {}
RNG = {"SPY": (700, 790, 0.5), "TSLA": (340, 440, 0.5)}
out = {"as of": "Tue Nov 3 close chains + OI dated Nov 4 (Tue close positions); references = Wed 08:00 ET premarket (Yahoo): SPY 760.1, TSLA 376.0"}
for sym in ("SPY", "TSLA"):
    e = norm(pd.read_csv(td / f"{sym}_eod_20261103.csv.gz")); e = e[e.date == P]; o = norm(pd.read_csv(td / f"{sym}_oi_20261104.csv.gz"))
    S = REF[sym]; g = preopen(e, o, D); g["underlying_close"] = S; gx = g[g.expiration > D].copy()
    a, b, st = RNG[sym]; grid = np.arange(a, b + st, st)
    tot = np.array([gex_at(g, s) for s in grid]) / 1e9; totx = np.array([gex_at(gx, s) for s in grid]) / 1e9
    i0 = int(np.argmin(tot)); mn = tot[i0]
    band = np.where(tot <= 0.5 * mn)[0]; band = band[(band >= band[band <= i0].min())]   # half-depth band around the trough
    lo_i, hi_i = i0, i0
    while lo_i > 0 and tot[lo_i - 1] <= 0.5 * mn: lo_i -= 1
    while hi_i < len(grid) - 1 and tot[hi_i + 1] <= 0.5 * mn: hi_i += 1
    slope = np.gradient(tot, grid)   # $bn per 1% per $1 of price; most positive above the trough = where falling adds selling fastest
    above = (grid > grid[i0]) & (grid < S + 5)
    trap = float(grid[above][np.argmax(slope[above])]) if above.any() else None
    neg = grid[tot < 0]
    k45 = g[((g.expiration - D).dt.days <= 45) & g.K.between(0.75 * S, 1.25 * S)]
    ex = exposures(g, S); byk = ex.groupby("K").gex.sum() / 1e9; near = byk[(byk.index >= 0.95 * S) & (byk.index <= 1.05 * S)]
    z = g[g.expiration == D]; zoi = z[z.K.between(0.97 * S, 1.03 * S)].groupby(["K", "cp"]).oi.sum().unstack().fillna(0)
    out[sym] = {"reference close": S, "after-hours": AH[sym], **({"futures-implied open": FUT[sym]} if sym in FUT else {}),
                "flip incl. Wed 0DTE": round(fine_flip(g, S), 2), "flip excl. 0DTE": round(fine_flip(gx, S), 2),
                "call wall": float(k45[k45.cp == "C"].groupby("K").oi.sum().idxmax()), "put wall": float(k45[k45.cp == "P"].groupby("K").oi.sum().idxmax()),
                "pocket trough (most negative total gamma)": [float(grid[i0]), round(float(mn), 2)],
                "pocket half-depth band [bottom, top]": [float(grid[lo_i]), float(grid[hi_i])],
                "short-gamma zone (total < 0)": [float(neg.min()), float(neg.max())] if len(neg) else None,
                "trapdoor (steepest gamma drop above the trough)": trap,
                "total gamma $bn/1% at": {f"{s:g}": round(float(np.interp(s, grid, tot)), 2) for s in np.arange(round(grid[lo_i]) - 10, S + 15, 5 if sym == "SPY" else 5)},
                "top negative strikes near spot ($bn)": near.sort_values().head(5).round(3).to_dict(), "top positive strikes near spot ($bn)": near.sort_values(ascending=False).head(4).round(3).to_dict(),
                "Wed 0DTE OI near spot (calls, puts)": {f"{k:g}": [int(r.get("C", 0)), int(r.get("P", 0))] for k, r in zoi.sort_values(by=list(zoi.columns), ascending=False).head(6).iterrows()},
                "Wed 0DTE share of |gamma| at spot": round(float(exposures(z, S).gex.abs().sum() / ex.gex.abs().sum()), 3) if len(z) else 0.0}
    out[f"{sym} curve"] = {"price": grid.tolist(), "total incl 0DTE": tot.round(3).tolist(), "total excl 0DTE": totx.round(3).tolist()}

# TSLA state at hypothetical Wed closes (engine recipe from live-read maps_now; positions = Tue close)
e = norm(pd.read_csv(td / "TSLA_eod_20261103.csv.gz")); e = e[e.date == P].copy(); e["mid"] = (e.bid + e.ask) / 2
o = norm(pd.read_csv(td / "TSLA_oi_20261104.csv.gz")).rename(columns=lambda c: "oi" if "open_interest" in c else c)
g0 = t.chain_day(e.assign(oi=0.0)).drop(columns=["oi"]).merge(o[["expiration", "strike", "cp", "oi"]], on=["expiration", "strike", "cp"], how="left").fillna({"oi": 0})
h = pd.read_csv(MICRO / "out" / "td_gamma_TSLA.csv", parse_dates=["date"]).set_index("date").iloc[-251:]
gn_hist = h.gex_classic / (h.spot * (h.call_oi + h.put_oi) * 100); st = {}
for S0 in (395, 390, 385, 382, 380, 378, 376, 374, 372, 370, 367, 365, 360):
    gg = g0[(g0.expiration > D) & ((g0.expiration - D).dt.days <= t.MAX_DTE) & (g0.oi > 0)].copy()
    gg["date"], gg["T"], gg["underlying_close"] = D, ((gg.expiration - D).dt.days / 365).clip(lower=1 / (365 * 24)), S0
    m = day_metrics(gg, D, {"TSLA": ["TSLA"]})[0]; gn = m["gex_classic"] / (S0 * (m["call_oi"] + m["put_oi"]) * 100)
    npct = float((h.near_oi_share < m["near_oi_share"]).mean())
    st[f"{S0:g}"] = {"flip": round(float(m["flip_classic"]), 1), "% vs flip": round(float(100 * (S0 / m["flip_classic"] - 1)), 2), "near-OI pct": round(npct, 2),
                     "freed": bool(npct <= 1 / 3), "own-gamma pct": round(float((gn_hist < gn).mean()), 2)}
out["TSLA state at hypothetical Wed closes (Tue positions)"] = st
# implied odds of reaching levels by Wed close, from TSLA ATM IV (Nov 6 expiry), start = after-hours 391.64
c6 = g0[(g0.expiration == pd.Timestamp("2026-11-06"))]; c6 = c6[(c6.K - 376.0).abs() == (c6.K - 376.0).abs().min()]
iv = float(c6.iv.mean()) if "iv" in c6 else np.nan
Phi = lambda x: 0.5 * (1 + erf(x / sqrt(2)))
out["TSLA implied odds by Wed close (lognormal, from 376.0)"] = {"ATM IV Nov 6": round(iv, 3), **{f"P(close <= {L:g}) at IV / IV+10pts": [round(Phi(log(L / 376.0) / (iv / sqrt(252))), 3), round(Phi(log(L / 376.0) / ((iv + 0.10) / sqrt(252))), 3)] for L in (385, 380, 376, 372, 370, 365, 360)}}
json.dump(out, open(HERE / "out" / "map_v2.json", "w"), indent=1, default=float)
for k in ("SPY", "TSLA"): print(k, json.dumps(out[k], default=float))
print(json.dumps(out["TSLA state at hypothetical Wed closes (Tue positions)"])); print(json.dumps(out["TSLA implied odds by Wed close (lognormal, from 376.0)"]))
