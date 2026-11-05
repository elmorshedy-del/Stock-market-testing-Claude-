"""Q1: does yesterday's thinness predict the size of the next 1/5/20 days beyond IV + recent range? (pre-registered)
Usage: python size.py <orb-gamma data dir> <DIX.csv> -> out/q1.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from common import daily_from_bars, pct_trailing, yahoo, gex_pct

HERE = Path(__file__).resolve().parent; B = Path(sys.argv[1]); MICRO = HERE.parents[1] / "microstructure"
rng = np.random.default_rng(0)
vix = yahoo("%5EVIX").close; gx = gex_pct(sys.argv[2]).gp
h = pd.read_csv(MICRO / "out" / "td_gamma_TSLA.csv", parse_dates=["date"]).set_index("date")
assets = {"SPY": ([B / "SPY2020_rth_d2.parquet", B / "SPYarcx_rth_d2.parquet"], vix, gx), "TSLA": ([B / "TSLA2020_rth_d2.parquet", B / "TSLA_rth_d2.parquet"], h.atm_iv_30d * 100, pct_trailing(h.near_oi_share))}


def frame(name):
    files, iv, st = assets[name]; d = daily_from_bars(files)
    d["Lp"] = pct_trailing(d.L_raw.rolling(5).mean()); d["iv"] = np.log(iv.reindex(d.index).ffill()); d["st"] = st.reindex(d.index).ffill()
    lr = np.log(d.rng.clip(lower=1e-4)); d["r1"] = lr; d["r5"] = np.log(d.rng.rolling(5).mean()); d["r20"] = np.log(d.rng.rolling(20).mean())
    for k in (1, 5, 20):
        d[f"y{k}"] = np.log(d.rng[::-1].rolling(k).mean()[::-1].shift(-1))
    return d


def fit(d, k, extra):
    cols = ["iv", "r1", "r5", "r20"] + extra; z = d.dropna(subset=["iv", "r1", "r5", "r20", "Lp", "st", f"y{k}"])   # same rows for every model
    tr, te = z[z.index <= "2023-12-31"], z[z.index >= "2024-01-01"]
    X = lambda q: np.column_stack([np.ones(len(q))] + [q[c].to_numpy() for c in cols])
    b = np.linalg.lstsq(X(tr), tr[f"y{k}"].to_numpy(), rcond=None)[0]
    return te.index, te[f"y{k}"].to_numpy(), X(te) @ b, dict(zip(["const"] + cols, np.round(b, 3)))


def r2(y, p): return 1 - np.sum((y - p) ** 2) / np.sum((y - y.mean()) ** 2)


def boot_gain(y, pb, pf, blk=20, n=2000):
    N = len(y); out = []
    for _ in range(n):
        idx = np.concatenate([np.arange(s, min(s + blk, N)) for s in rng.integers(0, N, N // blk + 1)])[:N]
        out.append(r2(y[idx], pf[idx]) - r2(y[idx], pb[idx]))
    return np.array(out)


res, keep = {}, {}
for name in assets:
    d = frame(name); res[name] = {"days": int(d.dropna(subset=["Lp", "iv", "r20"]).shape[0])}
    for k in (1, 5, 20):
        i0, y, pb, cb = fit(d, k, []); i1, y1, pf, cf = fit(d, k, ["Lp"]); i2, y2, pg, cg = fit(d, k, ["Lp", "st"])
        assert (i0 == i1).all()
        g = boot_gain(y, pb, pf); keep[(name, k)] = pd.DataFrame({"y": y, "pb": pb, "pf": pf}, index=i0)
        res[name][f"k={k}"] = {"test days": int(len(y)), "R2 baseline (IV + ranges)": round(r2(y, pb), 3), "R2 + thinness": round(r2(y, pf), 3),
                               "gain": round(r2(y, pf) - r2(y, pb), 4), "gain 90% CI": [round(float(np.quantile(g, 0.05)), 4), round(float(np.quantile(g, 0.95)), 4)],
                               "coef on thinness pct (train)": cf["Lp"], "R2 + thinness + gamma state": round(r2(y2, pg), 3) if len(y2) == len(y) else round(r2(y2, pg), 3),
                               "coef on gamma state (train)": cg["st"]}
# Q1-split: SPY gain minus TSLA gain on common test dates, joint block bootstrap
for k in (1, 5, 20):
    a, b = keep[("SPY", k)], keep[("TSLA", k)]; ix = a.index.intersection(b.index); a, b = a.loc[ix], b.loc[ix]
    N = len(ix); out = []
    for _ in range(2000):
        idx = np.concatenate([np.arange(s, min(s + 20, N)) for s in rng.integers(0, N, N // 20 + 1)])[:N]
        ga = r2(a.y.values[idx], a.pf.values[idx]) - r2(a.y.values[idx], a.pb.values[idx]); gb = r2(b.y.values[idx], b.pf.values[idx]) - r2(b.y.values[idx], b.pb.values[idx]); out.append(ga - gb)
    obs = (r2(a.y.values, a.pf.values) - r2(a.y.values, a.pb.values)) - (r2(b.y.values, b.pf.values) - r2(b.y.values, b.pb.values))
    res[f"split k={k} (SPY gain - TSLA gain)"] = {"common days": int(N), "diff": round(float(obs), 4), "90% CI": [round(float(np.quantile(out, 0.05)), 4), round(float(np.quantile(out, 0.95)), 4)]}
s5 = res["SPY"]["k=5"]; sp5 = res["split k=5 (SPY gain - TSLA gain)"]
res["VERDICT Q1-SPY (k=5 gain > 0, CI above 0)"] = bool(s5["gain"] > 0 and s5["gain 90% CI"][0] > 0)
res["VERDICT Q1-split (k=5 SPY - TSLA > 0, CI above 0)"] = bool(sp5["diff"] > 0 and sp5["90% CI"][0] > 0)
json.dump(res, open(HERE / "out" / "q1.json", "w"), indent=1, default=float); print(json.dumps(res, indent=1, default=float))
