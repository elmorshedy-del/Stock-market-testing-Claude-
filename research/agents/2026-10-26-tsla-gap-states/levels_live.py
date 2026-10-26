"""Gamma maps for Tuesday Oct 27: Oct 23 closing chains (IVs), OI dated Oct 26 (positions at the Oct 23 close), Monday's close as spot,
Oct 26 expiries removed. Engine code path imported unchanged. Usage: python levels_live.py <spyg folder> <live23/td folder>  -> out/levels_live.json"""
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
MICRO = HERE.parents[1] / "microstructure"
sys.path.insert(0, str(MICRO))
_c = os.getcwd(); os.chdir(MICRO)
import td_gamma as t                               # noqa: E402
from hd_gamma import day_metrics                   # noqa: E402
from options_flow import exposures                 # noqa: E402
os.chdir(_c)
KEY = ["date", "expiration", "strike", "cp"]
SPOT = {"SPY": 765.29, "TSLA": 391.62}             # Monday Oct 26 closes (Yahoo)


def norm(d):
    dcol = next(c for c in ("date", "created", "timestamp") if c in d.columns)
    d["date"] = pd.to_datetime(d[dcol].astype(str).str[:10])
    d["expiration"] = pd.to_datetime(d.expiration)
    d["cp"] = np.where(d.right.str.upper().str.startswith("C"), "C", "P")
    return d


def build(sym, eod_files, oi_today):
    eod = pd.concat([t.read(sym, "eod")] + [norm(pd.read_csv(f)) for f in eod_files]).drop_duplicates(subset=KEY, keep="last")
    e = eod[eod.date == pd.Timestamp("2026-10-23")].copy(); e["mid"] = (e.bid + e.ask) / 2
    oi = norm(pd.read_csv(oi_today)).rename(columns=lambda c: "oi" if "open_interest" in c else c)
    g23 = t.chain_day(e.assign(oi=0.0))
    day = pd.Timestamp("2026-10-26")
    g = g23.drop(columns=["oi"]).merge(oi[["expiration", "strike", "cp", "oi"]], on=["expiration", "strike", "cp"], how="left").fillna({"oi": 0})
    g = g[(g.expiration > day) & ((g.expiration - day).dt.days <= t.MAX_DTE) & (g.oi > 0)].copy()
    g["date"], g["T"] = day, ((g.expiration - day).dt.days / 365).clip(lower=1 / (365 * 24))
    S = SPOT[sym]
    g["underlying_close"] = S
    m = day_metrics(g, day, {sym: [sym]})[0]
    ex = exposures(g, S, "classic")
    byk = ex.groupby("K").gex.sum()
    near = byk[(byk.index >= 0.93 * S) & (byk.index <= 1.07 * S)]
    grid = np.linspace(0.92 * S, 1.08 * S, 129)
    tot = np.array([exposures(g, s, "classic").gex.sum() for s in grid])
    pd.DataFrame({"price": grid, "total dealer GEX $bn": tot / 1e9}).to_csv(OUT / f"profile_{sym}.csv", index=False)
    byk.to_frame("gex").to_csv(OUT / f"strikes_{sym}.csv")
    exp = ex.assign(a=ex.gex.abs()).groupby("exp").agg(net=("gex", "sum"), a=("a", "sum"))
    exp["share"] = exp.a / exp.a.sum()
    callk = g[(g.cp == "C") & ((g.expiration - day).dt.days <= 45)].groupby("K").oi.sum()
    putk = g[(g.cp == "P") & ((g.expiration - day).dt.days <= 45)].groupby("K").oi.sum()
    lo_zone = grid[np.argmin(tot)]
    return {"spot": S, "flip": m["flip_classic"], "spot vs flip %": 100 * (S / m["flip_classic"] - 1), "total GEX $bn per 1%": m["gex_classic"] / 1e9,
            "call wall": m["call_wall"], "put wall": m["put_wall"],
            "top call OI <=45d": callk.sort_values(ascending=False).head(5).astype(int).to_dict(), "top put OI <=45d": putk.sort_values(ascending=False).head(5).astype(int).to_dict(),
            "largest positive strikes within 7% ($bn)": (near.sort_values(ascending=False).head(6) / 1e9).round(3).to_dict(),
            "largest negative strikes within 7% ($bn)": (near.sort_values().head(6) / 1e9).round(3).to_dict(),
            "price where total GEX is most negative": float(lo_zone), "price where total GEX is most positive": float(grid[np.argmax(tot)]),
            "gamma by expiry (top 5)": {str(k): {"share": round(float(v.share), 3), "net $bn": round(float(v.net) / 1e9, 3)} for k, v in exp.sort_values("share", ascending=False).head(5).iterrows()},
            "OI change vs Oct 23 file (contracts)": None}


def main(spyg, l23):
    OUT.mkdir(exist_ok=True)
    res = {"SPY": build("SPY", [Path(spyg) / "SPY_eod_1015_1023.csv.gz"], Path(spyg) / "SPY_oi_20261026.csv.gz"),
           "TSLA": build("TSLA", [Path(l23) / "TSLA_eod_1015_1022.csv.gz", Path(l23) / "TSLA_eod_20261023.csv.gz"], Path(spyg) / "TSLA_oi_20261026.csv.gz")}
    (OUT / "levels_live.json").write_text(json.dumps(res, indent=1, default=float))
    return res


if __name__ == "__main__":
    print(json.dumps(main(*sys.argv[1:3]), indent=1, default=float))
