"""Stage 5-6 models: LightGBM per target, purged expanding walk-forward (test years 2000-2019), skill against the pre-registered
benchmark, and a null from 40 circular shifts of the target. Feature sets: ALL, and CLEAN (no NFCI: its history is revised and
backcast before 2011, so it is not point-in-time; deviation logged in the README). Also an ADDED stricter benchmark (labelled)."""
import json, sys, time
from pathlib import Path
import numpy as np, pandas as pd
import lightgbm as lgb
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import roc_auc_score

H = Path(__file__).resolve().parent; LOCK = pd.Timestamp("2020-01-01")
PARAMS = dict(n_estimators=300, learning_rate=0.03, num_leaves=15, min_child_samples=40, colsample_bytree=0.5, subsample=0.8,
              subsample_freq=1, reg_lambda=1.0, verbose=-1, n_jobs=4, random_state=7)
TG = {"vol4": ("end4", 4), "mdd13": ("end13", 13), "crash13": ("end13", 13), "ret4": ("end4", 4), "ret13": ("end13", 13)}

def data(tg):
    X = pd.read_parquet(H / "data" / "features.parquet"); T = pd.read_parquet(H / "data" / "targets.parquet")
    endc, h = TG[tg]
    t = T.loc["1990-01-01":].dropna(subset=[tg, endc]); t = t[pd.to_datetime(t[endc]) < LOCK]
    return X.reindex(t.index), t, h

def walk(Xa, y, bench_fn, h, tg, extra=None):
    """Returns OOS predictions, benchmark predictions and an optional added-benchmark prediction for test years 2000-2019."""
    P, Bm, Ex, idx = [], [], [], []
    dates = Xa.index
    for yr in range(2000, 2020):
        a = pd.Timestamp(f"{yr}-01-01"); b = pd.Timestamp(f"{yr + 1}-01-01")
        tr = dates < a - pd.Timedelta(weeks=h); te = (dates >= a) & (dates < b)
        if te.sum() == 0: continue
        if tg == "crash13":
            m = lgb.LGBMClassifier(**PARAMS).fit(Xa.values[tr], y[tr]); p = m.predict_proba(Xa.values[te])[:, 1]
        else:
            m = lgb.LGBMRegressor(**PARAMS).fit(Xa.values[tr], y[tr]); p = m.predict(Xa.values[te])
        P.append(p); Bm.append(bench_fn(tr, te)); idx.append(dates[te])
        if extra is not None: Ex.append(extra(tr, te))
    cat = lambda L: np.concatenate(L) if L else None
    return cat(P), cat(Bm), cat(Ex), np.concatenate(idx)

def skill(tg, y, p, b):
    if tg == "crash13":
        bs = np.mean((p - y) ** 2); bb = np.mean((b - y) ** 2)
        return {"skill": 1 - bs / bb, "auc": roc_auc_score(y, p) if len(np.unique(y)) > 1 else np.nan}
    return {"skill": 1 - np.mean((p - y) ** 2) / np.mean((b - y) ** 2)}

def run(tg, fset, n_null):
    Xa, t, h = data(tg)
    if fset == "CLEAN": Xa = Xa[[c for c in Xa.columns if not c.startswith("NFCI")]]
    y = t[tg].values.astype(float)
    def bench_factory(yv):
        if tg == "vol4":
            bv = t["bench_vol4"].values
            return lambda tr, te: bv[te]
        return lambda tr, te: np.full(te.sum(), yv[tr].mean())
    # added stricter benchmark: linear (or logistic) on VIX level and 20d/63d realized vol only
    Z = Xa[["VIX|level", "SPXvol|20d", "SPXvol|63d"]].copy()
    def extra(tr, te):
        zt = Z[tr].dropna(); yt = pd.Series(y, index=Xa.index)[zt.index]
        ze = Z[te].fillna(Z[tr].median())
        if tg == "crash13":
            return LogisticRegression(max_iter=1000).fit(zt, yt).predict_proba(ze)[:, 1]
        return LinearRegression().fit(zt, yt).predict(ze)
    p, b, ex, idx = walk(Xa, y, bench_factory(y), h, tg, extra)
    yo = pd.Series(y, index=Xa.index).loc[idx].values
    res = {"target": tg, "features": fset, "n_features": Xa.shape[1], "n_oos": len(yo), **{f"{k}": v for k, v in skill(tg, yo, p, b).items()}}
    sx = skill(tg, yo, ex, b); res["added_bench_skill_vs_prereg_bench"] = sx["skill"]
    sm = skill(tg, yo, p, ex); res["model_skill_vs_added_bench"] = sm["skill"]
    if tg == "crash13": res["auc_added_bench"] = sx["auc"]
    # null: shift the target (and its benchmark inputs) against the features
    rng = np.random.default_rng(11); null = []
    n = len(y)
    for k in rng.integers(52, n - 52, size=n_null):
        ys = np.roll(y, k)
        if tg == "vol4":
            bvs = np.roll(t["bench_vol4"].values, k); bf = lambda tr, te, bvs=bvs: bvs[te]
        else:
            bf = lambda tr, te, ys=ys: np.full(te.sum(), ys[tr].mean())
        pn, bn, _, idn = walk(Xa, ys, bf, h, tg)
        yon = pd.Series(ys, index=Xa.index).loc[idn].values
        null.append(skill(tg, yon, pn, bn)["skill"])
    if null:
        res["null_p95"] = float(np.quantile(null, 0.95)); res["null_median"] = float(np.median(null))
        res["p_vs_null"] = float((1 + np.sum(np.array(null) >= res["skill"])) / (1 + len(null)))
    pd.DataFrame({"date": idx, "y": yo, "model": p, "bench": b, "added_bench": ex}).to_csv(H / "out" / f"oos_{tg}_{fset}.csv", index=False)
    return res

if __name__ == "__main__":
    n_null = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    out = []
    for tg in TG:
        for fset, nn in (("ALL", 0), ("CLEAN", n_null)):
            t0 = time.time(); r = run(tg, fset, nn); r["seconds"] = round(time.time() - t0)
            out.append(r); print(json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()}), flush=True)
            json.dump(out, open(H / "out" / "models.json", "w"), indent=1, default=float)
