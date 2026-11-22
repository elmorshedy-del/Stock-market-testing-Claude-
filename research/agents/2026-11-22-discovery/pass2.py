"""Pass 2 (protocol in README): what adds to the current-stress model S? Nested selection inside each fold, ridge and a small
LightGBM on S's inputs + the 10 features most related to S's training residual; skill vs S; null from 40 circular shifts."""
import json, sys, time
from collections import Counter
from pathlib import Path
import numpy as np, pandas as pd
import lightgbm as lgb
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge
from model import data

H = Path(__file__).resolve().parent
ZC = ["VIX|level", "SPXvol|20d", "SPXvol|63d"]
SMALL = dict(n_estimators=200, learning_rate=0.03, num_leaves=4, min_child_samples=80, colsample_bytree=0.8, subsample=0.8,
             subsample_freq=1, reg_lambda=1.0, verbose=-1, n_jobs=4, random_state=7)

def walk(Xa, y, h, tg, record=False):
    dates = Xa.index; cand = [c for c in Xa.columns if c not in ZC]
    out = {"S": [], "ridge": [], "boost": [], "y": [], "idx": []}; picks = Counter(); per_fold = {}
    for yr in range(2000, 2020):
        a = pd.Timestamp(f"{yr}-01-01"); b = pd.Timestamp(f"{yr + 1}-01-01")
        tr = dates < a - pd.Timedelta(weeks=h); te = (dates >= a) & (dates < b)
        if te.sum() == 0: continue
        Xtr, Xte, ytr = Xa[tr], Xa[te], y[tr]
        med = Xtr.median()
        Ztr, Zte = Xtr[ZC].fillna(med[ZC]), Xte[ZC].fillna(med[ZC])
        if tg == "crash13":
            S = LogisticRegression(max_iter=2000).fit(Ztr, ytr); s_tr = S.predict_proba(Ztr)[:, 1]; s_te = S.predict_proba(Zte)[:, 1]
        else:
            S = LinearRegression().fit(Ztr, ytr); s_tr = S.predict(Ztr); s_te = S.predict(Zte)
        e = pd.Series(ytr - s_tr, index=Xtr.index)
        cov = Xtr[cand].notna().mean(); ok = [c for c in cand if cov[c] >= 0.6]
        rho = Xtr[ok].corrwith(e, method="spearman").abs().sort_values(ascending=False)
        top = list(rho.index[:10]); picks.update(top)
        if record: per_fold[yr] = top
        cols = ZC + top
        A_tr = Xtr[cols].fillna(med[cols]); A_te = Xte[cols].fillna(med[cols])
        mu, sd = A_tr.mean(), A_tr.std().replace(0, 1)
        A_tr, A_te = (A_tr - mu) / sd, (A_te - mu) / sd
        if tg == "crash13":
            r_te = LogisticRegression(C=1.0, max_iter=2000).fit(A_tr, ytr).predict_proba(A_te)[:, 1]
            b_te = lgb.LGBMClassifier(**SMALL).fit(A_tr.values, ytr).predict_proba(A_te.values)[:, 1]
        else:
            r_te = Ridge(alpha=1.0).fit(A_tr, ytr).predict(A_te)
            b_te = lgb.LGBMRegressor(**SMALL).fit(A_tr.values, ytr).predict(A_te.values)
        out["S"].append(s_te); out["ridge"].append(r_te); out["boost"].append(b_te); out["y"].append(y[te]); out["idx"].append(dates[te])
    o = {k: np.concatenate(v) for k, v in out.items()}
    sk = {m: 1 - np.mean((o[m] - o["y"]) ** 2) / np.mean((o["S"] - o["y"]) ** 2) for m in ("ridge", "boost")}
    return sk, picks, per_fold, o

def run(tg, n_null):
    Xa, t, h = data(tg); Xa = Xa[[c for c in Xa.columns if not c.startswith("NFCI")]]; y = t[tg].values.astype(float)
    sk, picks, per_fold, o = walk(Xa, y, h, tg, record=True)
    rng = np.random.default_rng(23); null = {"ridge": [], "boost": []}
    for k in rng.integers(52, len(y) - 52, size=n_null):
        s, *_ = walk(Xa, np.roll(y, k), h, tg)
        for m in null: null[m].append(s[m])
    res = {"target": tg}
    for m in ("ridge", "boost"):
        res[m] = {"skill_vs_S": float(sk[m]), "null_p95": float(np.quantile(null[m], 0.95)), "null_median": float(np.median(null[m])),
                  "p": float((1 + np.sum(np.array(null[m]) >= sk[m])) / (1 + n_null)),
                  "passes": bool(sk[m] > 0 and sk[m] > np.quantile(null[m], 0.95))}
    res["selected_in_folds_of_20"] = dict(picks.most_common(20)); res["per_fold_top10"] = {str(k): v for k, v in per_fold.items()}
    pd.DataFrame({"date": o["idx"], "y": o["y"], "S": o["S"], "ridge": o["ridge"], "boost": o["boost"]}).to_csv(H / "out" / f"pass2_oos_{tg}.csv", index=False)
    return res

if __name__ == "__main__":
    n_null = int(sys.argv[1]) if len(sys.argv) > 1 else 40; allr = []
    for tg in ("vol4", "mdd13", "crash13"):
        t0 = time.time(); r = run(tg, n_null); r["seconds"] = round(time.time() - t0); allr.append(r)
        print(f"\n== {tg} ({r['seconds']}s)")
        for m in ("ridge", "boost"): print(f"   {m:5s} skill vs S {r[m]['skill_vs_S']:+.3f}   null 95th {r[m]['null_p95']:+.3f}   p {r[m]['p']:.3f}   passes {r[m]['passes']}")
        print("   most often selected (folds of 20):", r["selected_in_folds_of_20"])
        json.dump(allr, open(H / "out" / "pass2.json", "w"), indent=1)
