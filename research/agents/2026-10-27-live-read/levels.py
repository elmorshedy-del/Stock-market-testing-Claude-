"""Gamma maps at the Oct 27 close: OI dated Oct 27 (positions at the Oct 26 close), Oct 26 closing chains (IVs),
Tuesday's close as spot, expiries after Oct 27 only. Same engine path as 2026-10-26-tsla-gap-states/levels_live.py
(imported), with the dates as parameters. Also: open-interest change Oct 26 -> Oct 27 file (what Monday built), and the
freed / own-gamma percentiles vs the engine's trailing year.
Usage: python levels.py <live27/td> <spyg>  -> out/levels.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
GAPS = HERE.parent / "2026-10-26-tsla-gap-states"
sys.path.insert(0, str(GAPS))
import levels_live as L                             # noqa: E402  (sets up the engine imports)
t, day_metrics, exposures = L.t, L.day_metrics, L.exposures
SPOT = {"SPY": 769.71, "TSLA": 407.46}              # Tuesday Oct 27 closes (Yahoo)
DAY, IVDAY = pd.Timestamp("2026-10-27"), pd.Timestamp("2026-10-26")


def chain(sym, td, spyg):
    e = L.norm(pd.read_csv(Path(td) / f"{sym}_eod_20261026.csv.gz")); e["mid"] = (e.bid + e.ask) / 2
    e = e[e.date == IVDAY]
    oi = L.norm(pd.read_csv(Path(td) / f"{sym}_oi_20261027.csv.gz")).rename(columns=lambda c: "oi" if "open_interest" in c else c)
    old = L.norm(pd.read_csv(Path(spyg) / f"{sym}_oi_20261026.csv.gz")).rename(columns=lambda c: "oi_old" if "open_interest" in c else c)
    g = t.chain_day(e.assign(oi=0.0)).drop(columns=["oi"]).merge(oi[["expiration", "strike", "cp", "oi"]], on=["expiration", "strike", "cp"], how="left").fillna({"oi": 0})
    g = g[(g.expiration > DAY) & ((g.expiration - DAY).dt.days <= t.MAX_DTE) & (g.oi > 0)].copy()
    g["date"], g["T"] = DAY, ((g.expiration - DAY).dt.days / 365).clip(lower=1 / (365 * 24))
    g["underlying_close"] = SPOT[sym]
    return g, oi, old


def build(sym, td, spyg):
    S = SPOT[sym]
    g, oi, old = chain(sym, td, spyg)
    m = day_metrics(g, DAY, {sym: [sym]})[0]
    ex = exposures(g, S, "classic")
    byk = ex.groupby("K").gex.sum()
    near = byk[(byk.index >= 0.93 * S) & (byk.index <= 1.07 * S)]
    grid = np.linspace(0.92 * S, 1.08 * S, 129)
    tot = np.array([exposures(g, s, "classic").gex.sum() for s in grid])
    pd.DataFrame({"price": grid, "total dealer GEX $bn": tot / 1e9}).to_csv(HERE / "out" / f"profile_{sym}.csv", index=False)
    byk.to_frame("gex").to_csv(HERE / "out" / f"strikes_{sym}.csv")
    exp = ex.assign(a=ex.gex.abs()).groupby("exp").agg(net=("gex", "sum"), a=("a", "sum")); exp["share"] = exp.a / exp.a.sum()
    k45 = g[(g.expiration - DAY).dt.days <= 45]
    callk, putk = k45[k45.cp == "C"].groupby("K").oi.sum(), k45[k45.cp == "P"].groupby("K").oi.sum()
    key = ["expiration", "strike", "cp"]
    ch = oi[key + ["oi"]].merge(old[key + ["oi_old"]], on=key, how="outer").fillna(0)
    ch = ch[(ch.expiration > DAY) & ((ch.expiration - DAY).dt.days <= 45) & (ch.strike.between(0.9 * S, 1.1 * S))]
    ch["d"] = ch.oi - ch.oi_old
    dk = ch.groupby(["cp", "strike"]).d.sum()
    res = {"spot": S, "flip": m["flip_classic"], "spot vs flip %": 100 * (S / m["flip_classic"] - 1), "total GEX $bn per 1%": m["gex_classic"] / 1e9,
           "call wall": m["call_wall"], "put wall": m["put_wall"], "near-OI share": m["near_oi_share"],
           "top call OI <=45d": callk.sort_values(ascending=False).head(6).astype(int).to_dict(),
           "top put OI <=45d": putk.sort_values(ascending=False).head(6).astype(int).to_dict(),
           "largest positive strikes within 7% ($bn)": (near.sort_values(ascending=False).head(6) / 1e9).round(3).to_dict(),
           "largest negative strikes within 7% ($bn)": (near.sort_values().head(6) / 1e9).round(3).to_dict(),
           "price where total GEX is most negative": float(grid[np.argmin(tot)]), "price where total GEX is most positive": float(grid[np.argmax(tot)]),
           "gamma by expiry (top 5)": {str(k)[:10]: {"share": round(float(v.share), 3), "net $bn": round(float(v.net) / 1e9, 3)} for k, v in exp.sort_values("share", ascending=False).head(5).iterrows()},
           "OI built Monday, calls +-10%, <=45d (top 6)": dk.loc["C"].sort_values(ascending=False).head(6).astype(int).to_dict(),
           "OI cut Monday, calls (top 4)": dk.loc["C"].sort_values().head(4).astype(int).to_dict(),
           "OI built Monday, puts (top 6)": dk.loc["P"].sort_values(ascending=False).head(6).astype(int).to_dict(),
           "OI cut Monday, puts (top 4)": dk.loc["P"].sort_values().head(4).astype(int).to_dict(),
           "net OI change calls / puts (+-10%, <=45d)": [int(dk.loc["C"].sum()), int(dk.loc["P"].sum())]}
    hp = L.MICRO / "out" / f"td_gamma_{sym}.csv"
    h = pd.read_csv(hp, parse_dates=["date"]).set_index("date").iloc[-251:]
    gn_hist = h.gex_classic / (h.spot * (h.call_oi + h.put_oi) * 100)
    res["own-gamma pct"] = float((gn_hist < m["gex_classic"] / (S * (m["call_oi"] + m["put_oi"]) * 100)).mean())
    if "near_oi_share" in h:
        res["near-OI pct (freed <= 0.33)"] = float((h.near_oi_share < m["near_oi_share"]).mean())
        m2 = day_metrics(g[g.expiration > pd.Timestamp("2026-10-30")], DAY, {sym: [sym]})[0]
        res["after Oct 30 expiry"] = {"flip": m2["flip_classic"], "near-OI pct": float((h.near_oi_share < m2["near_oi_share"]).mean()),
                                      "call wall": m2["call_wall"], "put wall": m2["put_wall"]}
    return res


if __name__ == "__main__":
    td, spyg = sys.argv[1:3]
    (HERE / "out").mkdir(exist_ok=True)
    res = {s: build(s, td, spyg) for s in ("SPY", "TSLA")}
    (HERE / "out" / "levels.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res, indent=1, default=float))
