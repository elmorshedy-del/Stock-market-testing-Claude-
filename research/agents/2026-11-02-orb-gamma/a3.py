"""A3: C1 (TSLA 2020-23 out of sample, frozen S1_5_close + 4 splits) and C2 (screened candidates 2024-26). -> out/a3.json"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; D = HERE / "data"; O = HERE / "out"; K = "S1_5_close"
SH = lambda N: range(20, N - 20)


def pnl(df, k=K, dirs=None):
    d = df[k + "_dir"].to_numpy() if dirs is None else dirs
    return np.where(d > 0, df[k + "_L"].fillna(0).to_numpy(), np.where(d < 0, df[k + "_S"].fillna(0).to_numpy(), 0.0))


def h1(df):
    d = df[K + "_dir"].to_numpy(); p = pnl(df); a = p.mean()
    null = np.array([pnl(df, dirs=np.roll(d, s)).mean() for s in SH(len(d))])
    t = p[d != 0]; y = df.index.year
    return {"sessions": len(df), "trades": int((d != 0).sum()), "mean bp/day": round(float(a), 2), "shift p": round(float((null >= a).mean()), 4),
            "Sharpe": round(float(p.mean() / p.std() * np.sqrt(252)), 2), "hit": round(float((t > 0).mean()), 3),
            "avg win / loss bp": [round(float(t[t > 0].mean()), 1), round(float(t[t < 0].mean()), 1)], "by year": {int(v): round(float(p[y == v].mean()), 1) for v in sorted(set(y))}}


def split(p, lab, side=+1):
    lab = np.asarray(lab, bool); f = lambda L: p[L].mean() - p[~L].mean(); a = f(lab)
    null = np.array([f(np.roll(lab, s)) for s in SH(len(p))])
    return {"n flag": int(lab.sum()), "flag": round(float(p[lab].mean()), 2), "other": round(float(p[~lab].mean()), 2), "diff": round(float(a), 2),
            "p one-sided": round(float((null >= a).mean() if side > 0 else (null <= a).mean()), 4)}


def splits(lab_name, df):
    d = df[K + "_dir"].to_numpy(); p = pnl(df); tr = d != 0
    A = pd.read_csv(O / f"audit_days_{lab_name}.csv", parse_dates=["date"]).set_index("date").reindex(df.index)
    rv = (df.vol5 / df.vol5.rolling(14).mean().shift(1)).to_numpy()
    q = np.nanquantile(rv, 2 / 3)
    out = {"Mon+Fri minus Tue-Thu": split(p, df.index.dayofweek.isin([0, 4])),
           "longs minus shorts (trade days)": split(p[tr], d[tr] > 0),
           "top-tercile opening rel. volume minus rest": split(p[~np.isnan(rv)], (rv >= q)[~np.isnan(rv)]),
           "auction-gap days (|Yahoo open - first bar| > 5 bp) minus rest": split(p[A.d_open.notna().to_numpy()], (A.d_open.abs() > 5).to_numpy()[A.d_open.notna().to_numpy()])}
    return out


res = {"rule": "S1_5_close: first break of the 09:30-09:34 range, stop at the other side, exit 15:59 close, 1c/side + 1c on stops"}
res["C1 TSLA 2020-23 clean (primary)"] = {**h1(pd.read_parquet(O / "days_TSLA2020.parquet"))}
res["C1 TSLA 2020-23 all complete days"] = {**h1(pd.read_parquet(O / "days_TSLA2020_d2.parquet"))}
res["C1 splits, all complete days"] = splits("TSLA2020", pd.read_parquet(O / "days_TSLA2020_d2.parquet"))
res["C1 splits, clean days"] = splits("TSLA2020", pd.read_parquet(O / "days_TSLA2020.parquet"))
res["C1 PASS (clean: mean > 0, shift p < 0.05)"] = bool(res["C1 TSLA 2020-23 clean (primary)"]["mean bp/day"] > 0 and res["C1 TSLA 2020-23 clean (primary)"]["shift p"] < 0.05)
HI, LO = ["AMD", "NVDA", "NFLX", "META", "AMZN"], ["UNH", "JPM"]
for suf, nm in (("", "clean"), ("_d2", "all complete days")):
    per = {s: h1(pd.read_parquet(O / f"days_{s}{suf}.parquet")) for s in HI + LO + ["TSLA", "SPY", "QQQ"]}
    dfs = {s: pd.read_parquet(O / f"days_{s}{suf}.parquet") for s in HI}
    act = np.mean([pnl(dfs[s]).mean() for s in HI]); N = min(len(v) for v in dfs.values())
    null = np.array([np.mean([pnl(dfs[s], dirs=np.roll(dfs[s][K + "_dir"].to_numpy(), k)).mean() for s in HI]) for k in SH(N)])
    res[f"C2 {nm}"] = {"per name": per, "high-score group mean bp/day (avg of names)": round(float(act), 2), "pooled shift p": round(float((null >= act).mean()), 4),
                       "control group mean bp/day": round(float(np.mean([per[s]["mean bp/day"] for s in LO])), 2), "PASS (a)": bool(act > 0 and (null >= act).mean() < 0.05)}
json.dump(res, open(O / "a3.json", "w"), indent=1, default=str)
for k, v in res.items():
    if k.startswith("C2"):
        print(k, "| HIGH mean", v["high-score group mean bp/day (avg of names)"], "p", v["pooled shift p"], "| CONTROLS", v["control group mean bp/day"])
        for s, x in v["per name"].items(): print(f"    {s:5s} {x['mean bp/day']:+7.2f} bp/day  p {x['shift p']:.3f}  Sharpe {x['Sharpe']:+.2f}  n {x['sessions']}  by year {x['by year']}")
    else: print(k, json.dumps(v))
