"""SPY dealer gamma (README.md, pre-registered at 55152bf). td_gamma / hd_gamma / options_flow imported unchanged.
Usage: python spy_gamma.py <scratch folder with SPY_oi_1015_1023 / SPY_eod_1015_1023>  -> out/levels.json, out/daily.csv, out/profile.csv, out/strikes.csv"""
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
MICRO = HERE.parents[1] / "microstructure"
CT = HERE.parent / "2026-10-25-channel-correction-theory"
sys.path.insert(0, str(MICRO))
_cwd = os.getcwd(); os.chdir(MICRO)
import td_gamma as t                               # noqa: E402
from hd_gamma import day_metrics                   # noqa: E402
from options_flow import exposures                 # noqa: E402
os.chdir(_cwd)
KEY = ["date", "expiration", "strike", "cp"]


def norm(d):
    dcol = next(c for c in ("date", "created", "timestamp") if c in d.columns)
    d["date"] = pd.to_datetime(d[dcol].astype(str).str[:10])
    d["expiration"] = pd.to_datetime(d.expiration)
    d["cp"] = np.where(d.right.str.upper().str.startswith("C"), "C", "P")
    return d


def main(td):
    OUT.mkdir(exist_ok=True)
    eod = pd.concat([t.read("SPY", "eod"), norm(pd.read_csv(Path(td) / "SPY_eod_1015_1023.csv.gz"))]).drop_duplicates(subset=KEY, keep="last")
    oi = pd.concat([t.read("SPY", "oi"), norm(pd.read_csv(Path(td) / "SPY_oi_1015_1023.csv.gz"))]).drop_duplicates(subset=KEY, keep="last")
    oi = oi.rename(columns={next(c for c in oi.columns if "open_interest" in c): "oi"})
    def chain(day):
        e = eod[eod.date == day].copy(); e["mid"] = (e.bid + e.ask) / 2
        o = oi[oi.date == day][["expiration", "strike", "cp", "oi"]]
        g = t.chain_day(e.merge(o, on=["expiration", "strike", "cp"], how="left").fillna({"oi": 0}))
        return g[(g.expiration - g.date).dt.days <= t.MAX_DTE]
    eng = pd.read_csv(t.OUT / "td_gamma_SPY.csv", parse_dates=["date"]).set_index("date")
    res = {"verify vs stored engine rows": {}}
    for d in ("2026-10-08", "2026-10-09"):
        r = day_metrics(chain(pd.Timestamp(d)), pd.Timestamp(d), {"SPY": ["SPY"]})[0]
        s = eng.loc[d]
        res["verify vs stored engine rows"][d] = {"flip": [r["flip_classic"], float(s.flip_classic)], "spot": [r["spot"], float(s.spot)],
                                                  "gex $bn": [r["gex_classic"] / 1e9, float(s.gex_classic) / 1e9]}
    days = sorted(d for d in eod.date.unique() if d >= pd.Timestamp("2026-10-12"))
    rows = [day_metrics(chain(pd.Timestamp(d)), pd.Timestamp(d), {"SPY": ["SPY"]})[0] for d in days]
    R = pd.DataFrame(rows).set_index("date")
    R["spot vs flip %"] = 100 * (R.spot / R.flip_classic - 1)
    R[["spot", "flip_classic", "spot vs flip %", "gex_classic", "call_wall", "put_wall", "gamma_share_1d", "gamma_share_5d", "near_oi_share"]].to_csv(OUT / "daily.csv")
    # ---- the map after Friday's close ----
    g = chain(pd.Timestamp("2026-10-23"))
    g = g[g.oi > 0]
    S = float(g.underlying_close.median())
    e = exposures(g, S, "classic")
    byk = e.groupby("K").gex.sum()
    near = byk[(byk.index >= 0.95 * S) & (byk.index <= 1.05 * S)]
    grid = np.linspace(0.94 * S, 1.06 * S, 97)
    tot = np.array([exposures(g, s, "classic").gex.sum() for s in grid])
    pd.DataFrame({"price": grid, "total dealer GEX $bn per 1%": tot / 1e9}).to_csv(OUT / "profile.csv", index=False)
    byk.to_frame("dealer GEX $").to_csv(OUT / "strikes.csv")
    crosses = [float(grid[i] - tot[i] * (grid[i + 1] - grid[i]) / (tot[i + 1] - tot[i])) for i in range(len(grid) - 1) if np.sign(tot[i]) != np.sign(tot[i + 1])]
    ex = e.assign(absg=e.gex.abs()).groupby("exp").agg(gex=("gex", "sum"), absg=("absg", "sum"))
    ex["share of |gamma|"] = ex.absg / ex.absg.sum()
    top_ex = ex.sort_values("share of |gamma|", ascending=False).head(8)
    call_oi = g[(g.cp == "C") & ((g.expiration - pd.Timestamp("2026-10-23")).dt.days <= 45)].groupby("K").oi.sum()
    put_oi = g[(g.cp == "P") & ((g.expiration - pd.Timestamp("2026-10-23")).dt.days <= 45)].groupby("K").oi.sum()
    m = day_metrics(chain(pd.Timestamp("2026-10-23")), pd.Timestamp("2026-10-23"), {"SPY": ["SPY"]})[0]
    res["after Friday Oct 23 close (OI positions at Oct 22 close)"] = {
        "spot (parity)": S, "flip": m["flip_classic"], "spot vs flip %": 100 * (S / m["flip_classic"] - 1), "total dealer GEX $bn per 1%": m["gex_classic"] / 1e9,
        "all zero-crossings on +-6% grid": crosses, "call wall (<=45d)": m["call_wall"], "put wall (<=45d)": m["put_wall"],
        "top call OI strikes <=45d": call_oi.sort_values(ascending=False).head(6).astype(int).to_dict(),
        "top put OI strikes <=45d": put_oi.sort_values(ascending=False).head(6).astype(int).to_dict(),
        "largest positive dealer GEX strikes within 5% ($bn)": (near.sort_values(ascending=False).head(6) / 1e9).round(3).to_dict(),
        "largest negative dealer GEX strikes within 5% ($bn)": (near.sort_values().head(6) / 1e9).round(3).to_dict(),
        "gamma by expiry (top 8)": {str(k): {"share of |gamma|": round(float(v["share of |gamma|"]), 3), "net $bn": round(float(v.gex) / 1e9, 2)} for k, v in top_ex.iterrows()},
        "GEX if SPY at (profile, $bn)": {f"{p:.0f}": float(np.interp(p, grid, tot) / 1e9) for p in (S * 0.97, S * 0.98, S * 0.99, S, S * 1.01, S * 1.02, S * 1.03)}}
    # ---- channel check: distance to the flip at each dip's start ----
    hist = pd.concat([eng[["spot", "flip_classic"]], R[["spot", "flip_classic"]]])
    hist = hist[~hist.index.duplicated(keep="last")].sort_index()
    dist = 100 * (hist.spot / hist.flip_classic - 1)
    E = pd.read_csv(CT / "out" / "dips.csv", parse_dates=["high date", "start"])
    rows = []
    for _, r in E.iterrows():
        v = dist[dist.index <= r.start].iloc[-5:].mean()
        rows.append({"episode": f"{r.outcome[:4]} {r['high date'].date()}", "outcome": r.outcome, "spot vs flip % (5-day mean)": float(v)})
    X = pd.DataFrame(rows)
    dec = X[X.outcome != "open"]
    y = (dec.outcome == "correction").to_numpy()
    v = dec["spot vs flip % (5-day mean)"].to_numpy()
    auc_low = float(((v[y][:, None] < v[~y][None, :]).mean()))
    res["channel check"] = {"AUC (corrections closer to/below flip)": auc_low, "corrections mean %": float(v[y].mean()), "bounces mean %": float(v[~y].mean()),
                            "corrections below flip": f"{int((v[y] < 0).sum())} of {int(y.sum())}", "bounces below flip": f"{int((v[~y] < 0).sum())} of {int((~y).sum())}",
                            "today (open dip) %": float(X[X.outcome == "open"]["spot vs flip % (5-day mean)"].iloc[0]),
                            "per episode": dict(zip(X.episode, X["spot vs flip % (5-day mean)"].round(2)))}
    (OUT / "levels.json").write_text(json.dumps(res, indent=1, default=float))
    return R, res


if __name__ == "__main__":
    R, res = main(sys.argv[1])
    pd.set_option("display.width", 220)
    print(R[["spot", "flip_classic", "spot vs flip %", "gex_classic", "call_wall", "put_wall", "gamma_share_1d"]].round(3).to_string())
    print(json.dumps(res, indent=1, default=float))
