"""Registered ML step (SPY) + exploratory re-run (TSLA, per A2). Features known by 09:35; target = trade win.
Split: train 2024-01-02..2025-06-30, validate 2025-07-01..2025-12-31 (threshold), test 2026 (touched once).
Usage: python ml.py LABEL [VARIANT] -> out/ml_<LABEL>_<VARIANT>.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

HERE = Path(__file__).resolve().parent; D = HERE / "data"; O = HERE / "out"
lab = sys.argv[1] if len(sys.argv) > 1 else "SPY"; K = sys.argv[2] if len(sys.argv) > 2 else "S0_5_10R"
days = pd.read_parquet(O / f"days_{lab}.parquet"); C = 0.01
d = days[K + "_dir"].to_numpy(); p = np.where(d > 0, days[K + "_L"].fillna(0), np.where(d < 0, days[K + "_S"].fillna(0), 0.0))
y = pd.read_csv(D / f"{lab.split('_')[0]}_yahoo_daily.csv", index_col=0, parse_dates=True)
spyd = pd.read_parquet(O / "days_SPY_d2.parquet"); spyy = pd.read_csv(D / "SPY_yahoo_daily.csv", index_col=0, parse_dates=True)
vix = pd.read_csv(D / "vix_daily.csv", index_col=0, parse_dates=True)
pl = pd.read_csv(HERE.parent / "2026-10-27-flip-wicks" / "out" / "preopen_levels.csv", parse_dates=["date"]).set_index("date")
sm = pd.read_csv(D / "squeeze_dix.csv", parse_dates=["date"]).set_index("date")
pr = lambda s: s.rolling(252).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True)
tr = pd.concat([y.high - y.low, (y.high - y.close.shift()).abs(), (y.low - y.close.shift()).abs()], axis=1).max(axis=1)
atr = (tr.rolling(14).mean().shift(1) / y.close.shift(1) * 1e4).reindex(days.index)
X = pd.DataFrame(index=days.index)
X["dir"] = d
X["gap_bp"] = (days.open / y.close.shift(1).reindex(days.index) - 1) * 1e4
X["gap_x_dir"] = X.gap_bp * d
X["r5_atr"] = (np.log(days.px935 / days.open) * 1e4) / atr
X["or_width_atr"] = ((days.or5_hi - days.or5_lo) / days.open * 1e4) / atr
X["rvol5"] = days.vol5 / days.vol5.rolling(14).mean().shift(1)
X["atr_bp"] = atr
X["prior_ret_bp"] = (y.close.pct_change().shift(1) * 1e4).reindex(days.index)
X["dow"] = days.index.dayofweek
X["opex_week"] = [any((t + pd.Timedelta(days=i)).weekday() == 4 and 15 <= (t + pd.Timedelta(days=i)).day <= 21 for i in range(0, 5 - t.weekday())) for t in days.index]
X["vix_prev"] = vix.c.shift(1).reindex(days.index); X["vix_overnight"] = (vix.o - vix.c.shift(1)).reindex(days.index)
X["spy_gap_bp"] = (spyd.open / spyy.close.shift(1).reindex(spyd.index) - 1).reindex(days.index) * 1e4
X["spy_dist_flip_bp"] = (spyd.px935 / pl.flip_incl.reindex(spyd.index) - 1).reindex(days.index) * 1e4
X["spy_below_x_dir"] = np.sign(-X.spy_dist_flip_bp) * d
X["share_0dte"] = pl.share_0dte.reindex(days.index)
X["gex_pct_prev"] = pr(sm.gex.astype(float)).shift(1).reindex(days.index); X["dix_pct_prev"] = pr(sm.dix.astype(float)).shift(1).reindex(days.index)
X = X.astype(float); target = (p > 0).astype(int)
tr_m = (days.index <= "2025-06-30"); va_m = (days.index >= "2025-07-01") & (days.index <= "2025-12-31"); te_m = days.index >= "2026-01-02"
trade = d != 0
sh = lambda x: float(x.mean() / x.std() * np.sqrt(252)) if x.std() > 0 else 0.0


def boot_ci(a, b, n=2000, blk=10, seed=0):
    """10-day block bootstrap of Sharpe(a) - Sharpe(b) over the same days."""
    rng = np.random.default_rng(seed); N = len(a); out = []
    for _ in range(n):
        idx = np.concatenate([np.arange(s, min(s + blk, N)) for s in rng.integers(0, N, N // blk + 1)])[:N]
        out.append(sh(a[idx]) - sh(b[idx]))
    return [round(float(np.quantile(out, 0.05)), 2), round(float(np.quantile(out, 0.95)), 2)]


res = {"label": lab, "variant": K, "n train/val/test": [int(tr_m.sum()), int(va_m.sum()), int(te_m.sum())], "features": list(X.columns), "note": "SPY = registered; others exploratory (A2)"}
models = {"logistic L2": make_pipeline(StandardScaler(), LogisticRegression(C=0.5, max_iter=2000)),
          "gradient boosting d3": HistGradientBoostingClassifier(max_depth=3, max_iter=200, learning_rate=0.05, min_samples_leaf=20, random_state=0)}
med = X[tr_m].median()
for nm, m in models.items():
    Xf = X.fillna(med) if nm.startswith("logistic") else X
    fit_m = tr_m & trade; m.fit(Xf[fit_m], target[fit_m])
    prob = m.predict_proba(Xf)[:, 1]
    best = None
    for q in [0.0, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]:   # keep the top (1-q) of validation days by predicted P(win)
        cut = np.quantile(prob[va_m & trade], q) if q > 0 else -1
        pv = np.where(va_m & trade & (prob >= cut), p, 0.0)[va_m]
        if (pv != 0).sum() >= 30 and (best is None or pv.mean() > best[1]): best = (cut, pv.mean(), q)
    cut = best[0]
    filt = np.where(trade & (prob >= cut), p, 0.0); base = p
    te_f, te_b = filt[te_m], base[te_m]
    imp = permutation_importance(m, Xf[va_m & trade], target[va_m & trade], n_repeats=20, random_state=0, scoring="roc_auc")
    from sklearn.metrics import roc_auc_score
    res[nm] = {"val: kept share, mean bp/day": [1 - best[2], round(float(best[1]), 2)],
               "AUC train/val/test": [round(float(roc_auc_score(target[tr_m & trade], prob[tr_m & trade])), 3), round(float(roc_auc_score(target[va_m & trade], prob[va_m & trade])), 3), round(float(roc_auc_score(target[te_m & trade], prob[te_m & trade])), 3)],
               "TEST unfiltered: mean bp/day, Sharpe, trades": [round(float(te_b.mean()), 2), round(sh(te_b), 2), int((te_b != 0).sum())],
               "TEST ML-filtered: mean bp/day, Sharpe, trades": [round(float(te_f.mean()), 2), round(sh(te_f), 2), int((te_f != 0).sum())],
               "TEST Sharpe diff 90% CI (10-day blocks)": boot_ci(te_f, te_b),
               "top features (val permutation AUC drop)": dict(sorted({c: round(float(v), 4) for c, v in zip(X.columns, imp.importances_mean)}.items(), key=lambda kv: -kv[1])[:6])}
    res[nm]["ML PASS (test Sharpe > unfiltered, CI excludes 0)"] = bool(sh(te_f) > sh(te_b) and res[nm]["TEST Sharpe diff 90% CI (10-day blocks)"][0] > 0)
# simple filter for comparison: E1 regime-aligned (SPY flip)
al = np.where(((X.spy_below_x_dir > 0) & trade), p, 0.0)
res["TEST E1 regime-aligned filter: mean bp/day, Sharpe, trades"] = [round(float(al[te_m].mean()), 2), round(sh(al[te_m]), 2), int((al[te_m] != 0).sum())]
json.dump(res, open(O / f"ml_{lab}_{K}.json", "w"), indent=1, default=str); print(json.dumps(res, indent=1, default=str))
