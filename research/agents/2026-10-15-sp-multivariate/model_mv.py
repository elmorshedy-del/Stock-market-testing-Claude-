"""Pre-registered walk-forward models (README). Writes data/preds.pkl and out/results_mv.json.

python model_mv.py
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

warnings.filterwarnings("ignore")
HERE = Path(__file__).parent
DATA, OUT = HERE / "data", HERE / "out"
H_WEEKS = {"Y_CORR": 13, "Y_BEAR": 52, "Y_CHAN": 26}
ERA_ZC = pd.Timestamp("2019-10-04")
START = pd.Timestamp("1992-01-01")
YEARS = list(range(2000, 2027))
SPECS = ["VOL", "FULL", "FULL-M", "FULL-O", "FULL-R", "FULL-S", "V+M", "V+O", "V+R", "V+S", "FULL_RECENT", "FULL_NO_NFCI"]


def spec_cols(spec, cols):
    lay = {k: [c for c in cols if c.startswith(k + "_")] for k in ("V", "M", "O", "R", "S")}
    era = [c for c in cols if c.startswith("ERA_")]
    full = lay["V"] + lay["M"] + lay["O"] + lay["R"] + lay["S"] + era
    if spec == "VOL":
        return lay["V"]
    if spec in ("FULL", "FULL_RECENT"):
        return full
    if spec == "FULL_NO_NFCI":
        return [c for c in full if "NFCI" not in c]
    if spec.startswith("FULL-"):
        drop = spec[-1]
        return [c for c in full if not c.startswith(drop + "_")]
    add = spec[-1]
    return lay["V"] + lay[add] + (era if add == "O" else [])


def logit_matrix(X, train_mask):
    """Missing -> 0 plus a flag per column with any missing in training; options features x zero-commission era."""
    Z = X.copy()
    for c in X.columns:
        if X.loc[train_mask, c].isna().any():
            Z[c + "_miss"] = X[c].isna().astype(float)
    Z = Z.fillna(0.0)
    if "ERA_ZC" in X.columns:
        for c in [c for c in X.columns if c.startswith("O_")]:
            Z[c + "_xZC"] = Z[c] * Z["ERA_ZC"]
    return Z


def fit_predict(args):
    outcome, spec, model = args
    X = pd.read_pickle(DATA / "features_X.pkl")
    raw = pd.read_pickle(DATA / "features_raw.pkl")
    y = raw[outcome]
    last = raw.last_day
    cols = spec_cols(spec, list(X.columns))
    Xs = X[cols]
    H = H_WEEKS[outcome]
    rows = []
    for Y in YEARS + ["now"]:
        if Y == "now":
            cut = raw.last_day.dropna().iloc[-1]
            test = raw.index == raw.index[-1]
        else:
            cut = pd.Timestamp(f"{Y}-01-01")
            test = (raw.index >= cut) & (raw.index < pd.Timestamp(f"{Y + 1}-01-01"))
        train = (raw.index >= START) & y.notna().to_numpy() & ((last + pd.Timedelta(weeks=H)) < cut).to_numpy()
        train &= Xs.notna().any(axis=1).to_numpy()
        if train.sum() < 150 or y[train].nunique() < 2 or test.sum() == 0:
            continue
        w = np.where(raw.index[train] >= ERA_ZC, 2.0, 1.0) if spec == "FULL_RECENT" else None
        if model == "GBM":
            m = HistGradientBoostingClassifier(max_depth=3, max_iter=150, learning_rate=0.05, min_samples_leaf=40,
                                               l2_regularization=1.0, random_state=0)
            # columns with no variation in the training years (feature not yet born, era flag still 0) carry no
            # information and crash the binner: leave them out for that year
            use = [c for c in cols if Xs.loc[train, c].nunique(dropna=True) > 1]
            m.fit(Xs.loc[train, use], y[train], sample_weight=w)
            p = m.predict_proba(Xs.loc[test, use])[:, 1]
        else:
            Z = logit_matrix(Xs, train)
            m = LogisticRegression(C=0.3, max_iter=5000)
            m.fit(Z[train], y[train], sample_weight=w)
            p = m.predict_proba(Z[test])[:, 1]
        base = float(y[train].mean())
        for t, pv in zip(raw.index[test], p):
            rows.append({"week": t, "year": Y, "p": float(pv), "clim": base})
    df = pd.DataFrame(rows)
    df["outcome"], df["spec"], df["model"] = outcome, spec, model
    return df


def events(y):
    """Distinct events: runs of positive weeks separated by 4+ negative weeks."""
    s = y.dropna()
    n, gap, prev_on = 0, 99, False
    for v in s.to_numpy():
        if v == 1 and gap >= 4:
            n += 1
        gap = 0 if v == 1 else gap + 1
    return n


def evaluate(P, raw):
    res = {}
    rng = np.random.default_rng(20261015)
    for (outcome, model), g in P[P.year != "now"].groupby(["outcome", "model"]):
        y = raw[outcome]
        piv = g.pivot_table(index="week", columns="spec", values="p")
        clim = g[g.spec == "VOL"].set_index("week").clim
        yy = y.reindex(piv.index)
        ok = yy.notna()
        piv, yy, clim = piv[ok], yy[ok], clim.reindex(piv.index)[ok]
        yrs = piv.index.year.to_numpy()
        uy = np.unique(yrs)
        by_year = {u: np.nonzero(yrs == u)[0] for u in uy}
        boot_idx = [np.concatenate([by_year[u] for u in rng.choice(uy, len(uy))]) for _ in range(1000)]
        out = {"weeks": int(len(yy)), "base_rate": float(yy.mean()), "events": events(yy),
               "brier_clim": float(((clim - yy) ** 2).mean())}
        Yv = yy.to_numpy()
        for spec in piv.columns:
            pv = piv[spec].to_numpy()
            okk = ~np.isnan(pv)
            auc = roc_auc_score(Yv[okk], pv[okk])
            br = float(((pv[okk] - Yv[okk]) ** 2).mean())
            out[spec] = {"auc": float(auc), "brier": br, "bss_vs_clim": float(1 - br / out["brier_clim"])}
        vol = piv["VOL"].to_numpy()
        for spec in piv.columns:
            if spec == "VOL":
                continue
            pv = piv[spec].to_numpy()
            d_auc, d_br = [], []
            for idx in boot_idx:
                yb = Yv[idx]
                if yb.min() == yb.max():
                    continue
                d_auc.append(roc_auc_score(yb, pv[idx]) - roc_auc_score(yb, vol[idx]))
                d_br.append(((pv[idx] - yb) ** 2).mean() - ((vol[idx] - yb) ** 2).mean())
            out[spec]["d_auc_vs_vol"] = out[spec]["auc"] - out["VOL"]["auc"]
            out[spec]["d_auc_ci95"] = [float(np.quantile(d_auc, 0.025)), float(np.quantile(d_auc, 0.975))]
            out[spec]["bss_vs_vol"] = float(1 - out[spec]["brier"] / out["VOL"]["brier"])
            out[spec]["d_brier_ci95"] = [float(np.quantile(d_br, 0.025)), float(np.quantile(d_br, 0.975))]
        # by option regime
        for lab, msk in (("old_2000_2019Q3", piv.index < ERA_ZC), ("new_2019Q4_on", piv.index >= ERA_ZC)):
            sub = {}
            ys = Yv[msk]
            if ys.min() == ys.max():
                continue
            for spec in ("VOL", "FULL", "FULL_RECENT", "V+O", "FULL-O"):
                pv = piv[spec].to_numpy()[msk]
                sub[spec] = {"auc": float(roc_auc_score(ys, pv)), "brier": float(((pv - ys) ** 2).mean())}
            sub["weeks"], sub["events"], sub["base_rate"] = int(msk.sum()), events(yy[msk]), float(ys.mean())
            out[lab] = sub
        f = out["FULL"]
        out["passes"] = bool(f["d_auc_vs_vol"] >= 0.05 and f["d_auc_ci95"][0] > 0 and f["bss_vs_vol"] > 0)
        nf = out["FULL_NO_NFCI"]
        out["passes_without_nfci"] = bool(nf["d_auc_vs_vol"] >= 0.05 and nf["d_auc_ci95"][0] > 0 and nf["bss_vs_vol"] > 0)
        out["underpowered"] = out["events"] < 8
        res[f"{outcome}|{model}"] = out
    return res


def main():
    jobs = [(o, s, m) for o in H_WEEKS for s in SPECS for m in ("GBM", "LOGIT")]
    with Pool(2) as pool:
        P = pd.concat(pool.map(fit_predict, jobs))
    P.to_pickle(DATA / "preds.pkl")
    raw = pd.read_pickle(DATA / "features_raw.pkl")
    res = evaluate(P, raw)
    now = P[P.year == "now"].pivot_table(index=["outcome", "model"], columns="spec", values="p")
    res["now"] = {f"{o}|{m}": now.loc[(o, m)].round(4).to_dict() for o, m in now.index}
    res["now_week"] = str(raw.index[-1].date())

    def clean(o):
        if isinstance(o, dict):
            return {str(k): clean(v) for k, v in o.items()}
        if isinstance(o, list):
            return [clean(v) for v in o]
        if isinstance(o, (np.floating, float)):
            return None if np.isnan(o) else round(float(o), 4)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, np.bool_):
            return bool(o)
        return o
    (OUT / "results_mv.json").write_text(json.dumps(clean(res), indent=1))
    for k, v in res.items():
        if "|" in k and "FULL" in v:
            print(k, "AUC VOL %.3f FULL %.3f dAUC %.3f CI [%.3f, %.3f] BSSvsVOL %.3f events %d pass %s" % (
                v["VOL"]["auc"], v["FULL"]["auc"], v["FULL"]["d_auc_vs_vol"], *v["FULL"]["d_auc_ci95"],
                v["FULL"]["bss_vs_vol"], v["events"], v["passes"]))


if __name__ == "__main__":
    main()
