"""Part 3 (pre-registered at 4bbbd47, unsigned measures per Amendment 2 at 24a01ef): order-flow / liquidity measures at the start of the
channel's dips. Usage: python dips_flow.py <etfs folder>  -> out/dips_flow.json, out/dips_flow_features.csv"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import flows as Fl

CT = Fl.HERE.parent / "2026-10-25-channel-correction-theory"
sys.path.insert(0, str(CT))
import dossier as Dz                               # noqa: E402
import multivar as Mv                              # noqa: E402

FINRA = Fl.HERE.parents[1] / "microstructure" / "data" / "finra"
RNG = np.random.default_rng(20261108)
NEW = ["SPY Amihud illiquidity (pct)", "SPY relative volume (5d/60d)", "SPY FINRA short ratio (pct)", "0DTE put/call volume (pct)", "0DTE activity (5d/60d)"]


def spy_daily(etfs):
    d = json.loads((Path(etfs) / "SPY.json").read_text())["chart"]["result"][0]
    idx = pd.to_datetime(d["timestamp"], unit="s", utc=True).tz_convert("America/New_York").normalize().tz_localize(None)
    q = d["indicators"]["quote"][0]
    f = pd.DataFrame({"close": q["close"], "volume": q["volume"]}, index=idx, dtype=float).dropna()
    return f[~f.index.duplicated(keep="last")].sort_index()


def finra_spy():
    rows = []
    for p in sorted(FINRA.glob("*.csv")):
        for line in p.read_text().splitlines():
            if line.startswith(p.stem + "|SPY|"):
                x = line.split("|")
                rows.append((pd.Timestamp(x[0]), float(x[2]) / float(x[4])))
    return pd.Series(dict(rows)).sort_index()


def zero_dte_pc():
    rows = {}
    for p in sorted(Fl.SRC.glob("*.csv.gz")):
        m = pd.read_csv(p, usecols=["right", "volume"])
        v = m.groupby("right").volume.sum()
        rows[pd.Timestamp(p.name[:8])] = (float(v.get("P", 0)), float(v.get("C", 0)))
    return pd.DataFrame(rows, index=["put", "call"]).T.sort_index()


def main(etfs):
    spy = spy_daily(etfs)
    r = np.log(spy.close).diff()
    amihud = (r.abs() / (spy.close * spy.volume)).rolling(20, min_periods=15).mean()
    X = pd.DataFrame(index=spy.index)
    X[NEW[0]] = Dz.pct(amihud)
    X[NEW[1]] = spy.volume.rolling(5).mean() / spy.volume.rolling(60).mean()
    fr = finra_spy().reindex(spy.index)
    X[NEW[2]] = Dz.pct(fr.rolling(5, min_periods=3).mean().ffill(limit=5))
    pc = zero_dte_pc().reindex(spy.index)
    X[NEW[3]] = Dz.pct((pc.put.rolling(5, min_periods=3).sum() / pc.call.rolling(5, min_periods=3).sum()).ffill(limit=5))
    tot = pc.put + pc.call
    X[NEW[4]] = (tot.rolling(5, min_periods=3).mean() / tot.rolling(60, min_periods=40).mean()).ffill(limit=5)
    E = pd.read_csv(CT / "out" / "dips.csv", parse_dates=["high date", "start"])
    feats = {f"{r_.outcome[:4]} {r_['high date'].date()}": X.loc[r_.start] for _, r_ in E.iterrows()}
    F = pd.DataFrame(feats).T
    old = pd.read_csv(CT / "out" / "multivar_features.csv", index_col=0)
    A = old.join(F)
    dec = [k for k in A.index if not k.startswith("open")]
    tk = [k for k in A.index if k.startswith("open")][0]
    y = np.array([k.startswith("corr") for k in dec]).astype(int)
    M = A.loc[dec].astype(float)
    res = {"new measures": {}}
    for k in NEW:
        v = M[k].to_numpy()
        ok = np.isfinite(v)
        a = Mv.auc(v[ok], y[ok])
        res["new measures"][k] = {"AUC (either direction)": max(a, 1 - a), "direction in corrections": "higher" if a >= 0.5 else "lower",
                                  "corrections mean": float(np.nanmean(v[y == 1])), "bounces mean": float(np.nanmean(v[y == 0])),
                                  "dips with data": int(ok.sum()), "today": float(A.loc[tk, k]) if pd.notna(A.loc[tk, k]) else None,
                                  "today percentile among dips": float((v[ok] < A.loc[tk, k]).mean()) if pd.notna(A.loc[tk, k]) else None}
    W = M.fillna(M.median()).to_numpy(float)
    def best(yy):
        return max(max(Mv.auc(W[:, j], yy), 1 - Mv.auc(W[:, j], yy)) for j in range(W.shape[1]))
    null = np.array([best(RNG.permutation(y)) for _ in range(3000)])
    obsA = {c: max(Mv.auc(W[:, j], y), 1 - Mv.auc(W[:, j], y)) for j, c in enumerate(M.columns)}
    res["best-of-all luck check"] = {"indicators": int(W.shape[1]),
                                     "family-wise p": {c: float((null >= obsA[c]).mean()) for c in ["share of panel above 50-day"] + NEW}}
    jb = list(M.columns).index("share of panel above 50-day")
    base, _ = Mv.loo(W[:, [jb]], y, 1.0)
    res["leave-one-dip-out AUC"] = {"breadth alone": base}
    for k in NEW:
        j = list(M.columns).index(k)
        res["leave-one-dip-out AUC"][f"breadth + {k}"] = Mv.loo(W[:, [jb, j]], y, 1.0)[0]
    F.round(4).to_csv(Fl.OUT / "dips_flow_features.csv")
    (Fl.OUT / "dips_flow.json").write_text(json.dumps(res, indent=1, default=float))
    return res


if __name__ == "__main__":
    print(json.dumps(main(sys.argv[1]), indent=1, default=float))
