"""POST-HOC (after seeing results_mv.json): is the momentum/RSI layer's gain real, and what drives it?
Writes out/posthoc_mv.json.

P1  family-wise shift null over the four add-one layers (V+M, V+O, V+R, V+S): each layer's feature block is shifted
    in time (each column circularly within its own non-missing window, same fraction for every column and layer in a
    draw), the walk-forward GBM is refit, and the max over layers of dAUC vs VOL is compared with the real max
P2  which momentum/RSI features carry it: V + each single R feature, and V+R minus each R feature (walk-forward GBM)
P3  stability: V+R vs VOL by era and by decade, with event counts
P4  direction: 10%-fall rate by tercile of each R feature, 2000-2026 (descriptive), and logistic signs on V+R
"""
import json
import warnings
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

import model_mv as M

warnings.filterwarnings("ignore")
HERE = Path(__file__).parent
DATA, OUT = HERE / "data", HERE / "out"
X = pd.read_pickle(DATA / "features_X.pkl")
RAW = pd.read_pickle(DATA / "features_raw.pkl")
Y = RAW.Y_CORR
H = 13
V = [c for c in X.columns if c.startswith("V_")]
LAY = {k: [c for c in X.columns if c.startswith(k + "_")] for k in ("M", "O", "R", "S")}
ERA = [c for c in X.columns if c.startswith("ERA_")]
EVAL = (RAW.index >= "2000-01-01") & Y.notna().to_numpy()


def shift_cols(Xs, cols, f):
    Z = Xs.copy()
    if f == 0:
        return Z
    for c in cols:
        s = Z[c]
        ok = s.notna().to_numpy()
        if not ok.any():
            continue
        i0, i1 = np.argmax(ok), len(ok) - np.argmax(ok[::-1])
        vals = s.to_numpy(float)[i0:i1]
        k = int(round(f * len(vals)))
        out = s.to_numpy(float).copy()
        out[i0:i1] = np.roll(vals, k)
        Z[c] = out
    return Z


def walk_gbm(Xs):
    preds = pd.Series(np.nan, index=RAW.index)
    for Yr in M.YEARS:
        cut = pd.Timestamp(f"{Yr}-01-01")
        test = (RAW.index >= cut) & (RAW.index < pd.Timestamp(f"{Yr + 1}-01-01"))
        train = (RAW.index >= M.START) & Y.notna().to_numpy() & ((RAW.last_day + pd.Timedelta(weeks=H)) < cut).to_numpy()
        train &= Xs.notna().any(axis=1).to_numpy()
        use = [c for c in Xs.columns if Xs.loc[train, c].nunique(dropna=True) > 1]
        m = HistGradientBoostingClassifier(max_depth=3, max_iter=150, learning_rate=0.05, min_samples_leaf=40,
                                           l2_regularization=1.0, random_state=0)
        m.fit(Xs.loc[train, use], Y[train])
        preds[test] = m.predict_proba(Xs.loc[test, use])[:, 1]
    return preds


def auc(p, mask=None):
    m = EVAL if mask is None else (EVAL & mask)
    return float(roc_auc_score(Y[m], p[m]))


def p1_job(f):
    out = {}
    for k in ("M", "O", "R", "S"):
        cols = V + LAY[k] + (ERA if k == "O" else [])
        Z = shift_cols(X[cols], LAY[k], f)
        out[k] = auc(walk_gbm(Z))
    return out


def single_job(args):
    kind, feat = args
    cols = V + ([feat] if kind == "add" else [c for c in LAY["R"] if c != feat])
    return kind, feat, auc(walk_gbm(X[cols]))


def main():
    res = {}
    p_vol = walk_gbm(X[V])
    auc_vol = auc(p_vol)
    real = p1_job(0)
    res["P1_real_auc"] = {**real, "VOL": auc_vol}
    fr = np.random.default_rng(20261016).uniform(0.1, 0.9, 200)
    with Pool(2) as pool:
        nulls = pool.map(p1_job, fr)
    D = np.array([[n[k] - auc_vol for k in ("M", "O", "R", "S")] for n in nulls])
    real_d = np.array([real[k] - auc_vol for k in ("M", "O", "R", "S")])
    res["P1"] = {"layers": ["M", "O", "R", "S"], "real_dauc": real_d.round(4).tolist(),
                 "per_layer_p": [float((1 + (D[:, j] >= real_d[j]).sum()) / (1 + len(D))) for j in range(4)],
                 "familywise_p_max": float((1 + (D.max(axis=1) >= real_d.max()).sum()) / (1 + len(D))),
                 "null_dauc_R_mean_sd": [float(D[:, 2].mean()), float(D[:, 2].std())], "n_draws": len(D)}
    print("P1", res["P1"])

    jobs = [("add", f) for f in LAY["R"]] + [("drop", f) for f in LAY["R"]]
    with Pool(2) as pool:
        single = pool.map(single_job, jobs)
    res["P2"] = {"vol_auc": auc_vol, "V+R_auc": real["R"],
                 "V_plus_one": {f: a for k, f, a in single if k == "add"},
                 "V+R_minus_one": {f: a for k, f, a in single if k == "drop"}}
    print("P2 done")

    p_vr = walk_gbm(X[V + LAY["R"]])
    eras = {"2000-2009": (RAW.index < "2010-01-01"), "2010-2019Q3": (RAW.index >= "2010-01-01") & (RAW.index < M.ERA_ZC),
            "2019Q4-2026": RAW.index >= M.ERA_ZC}
    res["P3"] = {}
    for lab, msk in eras.items():
        m = EVAL & msk
        res["P3"][lab] = {"weeks": int(m.sum()), "events": M.events(Y[m]), "base": float(Y[m].mean()),
                          "VOL": auc(p_vol, msk), "V+R": auc(p_vr, msk)}
    yr = []
    for Yr in M.YEARS:
        m = EVAL & (RAW.index.year == Yr)
        if m.sum() and Y[m].nunique() == 2:
            yr.append({"year": Yr, "events_weeks": int(Y[m].sum()), "VOL": auc(p_vol, RAW.index.year == Yr),
                       "V+R": auc(p_vr, RAW.index.year == Yr)})
    res["P3"]["by_year_with_events"] = yr

    R = RAW.loc[EVAL]
    terc = {}
    for c in LAY["R"]:
        v = RAW.loc[EVAL, c]
        if v.nunique() < 3:
            terc[c] = R.groupby(v).Y_CORR.mean().round(3).to_dict()
            continue
        q = pd.qcut(v, 3, labels=["low", "mid", "high"], duplicates="drop")
        terc[c] = R.groupby(q, observed=True).Y_CORR.mean().round(3).to_dict()
    res["P4_rate_by_tercile"] = terc
    tr = (RAW.index >= M.START) & Y.notna().to_numpy()
    Z = X.loc[tr, V + LAY["R"]].fillna(0)
    lg = LogisticRegression(C=0.3, max_iter=5000).fit(Z, Y[tr])
    res["P4_logit_coef_all_data"] = dict(zip(Z.columns, np.round(lg.coef_[0], 3)))
    res["now"] = {"V+R_gbm": float(M.HistGradientBoostingClassifier is not None)}
    now_X = X.iloc[[-1]][V + LAY["R"]]
    full_train = tr & ((RAW.last_day + pd.Timedelta(weeks=H)) < RAW.last_day.dropna().iloc[-1]).to_numpy()
    use = [c for c in V + LAY["R"] if X.loc[full_train, c].nunique(dropna=True) > 1]
    m = HistGradientBoostingClassifier(max_depth=3, max_iter=150, learning_rate=0.05, min_samples_leaf=40,
                                       l2_regularization=1.0, random_state=0).fit(X.loc[full_train, use], Y[full_train])
    res["now"] = {"week": str(RAW.index[-1].date()), "V+R_gbm": float(m.predict_proba(now_X[use])[:, 1][0]),
                  "base_rate_1992_on": float(Y[tr].mean()),
                  "R_raw_now": RAW.iloc[-1][LAY["R"]].astype(float).round(4).to_dict()}

    def clean(o):
        if isinstance(o, dict):
            return {str(k): clean(v) for k, v in o.items()}
        if isinstance(o, list):
            return [clean(v) for v in o]
        if isinstance(o, (np.floating, float)):
            return None if np.isnan(o) else round(float(o), 4)
        if isinstance(o, np.integer):
            return int(o)
        return o
    (OUT / "posthoc_mv.json").write_text(json.dumps(clean(res), indent=1))
    print(json.dumps(clean({k: res[k] for k in ("P2", "P3", "P4_rate_by_tercile", "P4_logit_coef_all_data", "now")}), indent=1))


if __name__ == "__main__":
    main()
