"""Amendment 3 (pre-registered at 118e3ca): oil + FOMC timing, then the leave-one-dip-out multivariate (M0 breadth, M1 theory composite,
M2 ridge on all, M3 best-3 stack). Usage: python multivar.py <etfs folder>  -> out/multivar.json, out/multivar_episodes.csv"""
import json
import sys

import numpy as np
import pandas as pd

import dips as Dp
import dossier as Dz
import yen as Yn

RNG = np.random.default_rng(20261105)
FOMC = pd.to_datetime([
    "2022-01-26", "2022-03-16", "2022-05-04", "2022-06-15", "2022-07-27", "2022-09-21", "2022-11-02", "2022-12-14",
    "2023-02-01", "2023-03-22", "2023-05-03", "2023-06-14", "2023-07-26", "2023-09-20", "2023-11-01", "2023-12-13",
    "2024-01-31", "2024-03-20", "2024-05-01", "2024-06-12", "2024-07-31", "2024-09-18", "2024-11-07", "2024-12-18",
    "2025-01-29", "2025-03-19", "2025-05-07", "2025-06-18", "2025-07-30", "2025-09-17", "2025-10-29", "2025-12-10",
    "2026-01-28", "2026-03-18", "2026-04-29", "2026-06-17", "2026-07-29", "2026-09-16", "2026-10-28", "2026-12-09"])
NEW = ["oil 20-day", "oil volatility percentile", "FOMC within next 10 sessions", "sessions to next FOMC", "sessions since last FOMC"]
EVENTVARS = NEW[2:]
M1 = {"share of panel above 50-day": 1, "bonds TLT (20d)": -1, "yen 20-day (USD/JPY change)": -1, "oil 20-day": 1, "gold (20d)": 1,
      "FOMC within next 10 sessions": 1, "margin debt vs prices": 1}


def frame(etfs):
    D = pd.read_csv(Dz.OUT / "daily.csv", index_col=0, parse_dates=True)
    spx = Dz.close(etfs, "%5EGSPC").reindex(D.index)
    D["margin debt growth"], D["margin debt vs prices"] = Dp.margin_daily(D.index, spx)
    lj = np.log(Yn.usdjpy(etfs).reindex(D.index, method="ffill"))
    D[Yn.YEN[0]], D[Yn.YEN[1]] = lj.diff(20), lj.diff(5)
    D[Yn.YEN[2]] = Dz.pct(lj.diff().rolling(20).std())
    oil = Dz.close(etfs, "CL=F").reindex(D.index).ffill()
    lo = np.log(oil)
    D["oil 20-day"] = lo.diff(20)
    D["oil volatility percentile"] = Dz.pct(lo.diff().rolling(20).std())
    idx = D.index
    pos = np.arange(len(idx))
    fpos = np.array([idx.searchsorted(d) for d in FOMC])                  # session index of each decision (or next session)
    nxt = np.array([fpos[fpos > i].min() - i if (fpos > i).any() else 999 for i in pos])
    prv = np.array([i - fpos[fpos <= i].max() if (fpos <= i).any() else 999 for i in pos])
    D["FOMC within next 10 sessions"] = (nxt <= 10).astype(float)
    D["sessions to next FOMC"] = nxt.astype(float)
    D["sessions since last FOMC"] = prv.astype(float)
    dist = D.pop("dist")
    D = D.drop(columns=["similarity"], errors="ignore")
    return D, dist, oil


def auc(score, y):
    c, b = score[y == 1], score[y == 0]
    return float((c[:, None] > b[None, :]).mean() + 0.5 * (c[:, None] == b[None, :]).mean())


def ridge_logit(X, y, lam, it=100):
    Xb = np.column_stack([np.ones(len(X)), X])
    beta = np.zeros(Xb.shape[1])
    P = lam * np.eye(Xb.shape[1]); P[0, 0] = 0
    for _ in range(it):
        p = 1 / (1 + np.exp(-Xb @ beta))
        g = Xb.T @ (y - p) - P @ beta
        H = (Xb * (p * (1 - p))[:, None]).T @ Xb + P
        beta += np.linalg.solve(H, g)
    return beta


def fit_predict(Xtr, ytr, Xte, lam, top=None):
    cols = np.arange(Xtr.shape[1])
    if top:
        a = np.array([max(auc(Xtr[:, j], ytr), 1 - auc(Xtr[:, j], ytr)) for j in cols])
        cols = np.argsort(-a)[:top]
    mu, sd = Xtr[:, cols].mean(0), Xtr[:, cols].std(0) + 1e-9
    b = ridge_logit((Xtr[:, cols] - mu) / sd, ytr, lam)
    z = (Xte[:, cols] - mu) / sd
    return 1 / (1 + np.exp(-(b[0] + z @ b[1:]))), cols


def loo(X, y, lam, top=None):
    p = np.zeros(len(y))
    for i in range(len(y)):
        m = np.arange(len(y)) != i
        p[i] = fit_predict(X[m], y[m], X[i:i + 1], lam, top)[0][0]
    return auc(p, y), p


def main(etfs):
    D, dist, oil = frame(etfs)
    idx = D.index
    ref = (idx >= Dz.CH0) & (idx <= Dz.CH1) & (dist >= -0.03).to_numpy()
    mu, sd = D[ref].mean(), D[ref].std()
    Z5 = (D.rolling(5, min_periods=4).mean() - mu) / sd
    Z1 = (D - mu) / sd
    for k in EVENTVARS:
        Z5[k] = Z1[k]                                                     # calendar variables: the start day's value, not a 5-day mean
    E = pd.read_csv(Dz.OUT / "dips.csv", parse_dates=["high date", "start"])
    feats = list(D.columns)
    rows = {f"{r.outcome[:4]} {r['high date'].date()}": Z5.loc[r.start, feats] for _, r in E.iterrows()}
    F = pd.DataFrame(rows).T
    dec = [k for k in F.index if not k.startswith("open")]
    today_key = [k for k in F.index if k.startswith("open")][0]
    X = F.loc[dec].fillna(0).to_numpy(float)
    y = np.array([k.startswith("corr") for k in dec]).astype(int)
    xt = F.loc[[today_key]].fillna(0).to_numpy(float)
    res = {"dips": len(dec), "corrections": int(y.sum()), "indicators": len(feats)}
    uni = {}
    for k in NEW + ["gold (20d)"]:
        j = feats.index(k)
        a = auc(X[:, j], y)
        uni[k] = {"AUC (either direction)": max(a, 1 - a), "direction in corrections": "higher" if a >= 0.5 else "lower",
                  "mean z corrections / bounces": [float(X[y == 1, j].mean()), float(X[y == 0, j].mean())], "today z": float(xt[0, j])}
    A = np.array([max(auc(X[:, j], y), 1 - auc(X[:, j], y)) for j in range(X.shape[1])])
    def best_null():
        yy = RNG.permutation(y)
        return max(max(auc(X[:, j], yy), 1 - auc(X[:, j], yy)) for j in range(X.shape[1]))
    best = np.array([best_null() for _ in range(3000)])
    order = np.argsort(-A)
    res["univariate: new variables"] = uni
    res["univariate: top 6 of all 34 (AUC, best-of-34 p)"] = {feats[j]: [float(A[j]), float((best >= A[j]).mean())] for j in order[:6]}
    jb = [feats.index("share of panel above 50-day")]
    out = {}
    for lam in (0.3, 1.0, 3.0):
        a0, p0 = loo(X[:, jb], y, lam)
        a2, p2 = loo(X, y, lam)
        a3, p3 = loo(X, y, lam, top=3)
        out[f"lambda {lam}"] = {"M0 breadth alone": a0, "M2 ridge, all 34": a2, "M3 best-3 stack": a3}
        if lam == 1.0:
            P0, P2, P3 = p0, p2, p3
    comp = sum(s * F[k] for k, s in M1.items())
    m1_auc = auc(comp.loc[dec].fillna(0).to_numpy(float), y)
    res["leave-one-dip-out AUC"] = out
    res["M1 theory composite AUC (no fitting)"] = m1_auc
    base = out["lambda 1.0"]["M0 breadth alone"]
    best_mv = max(m1_auc, out["lambda 1.0"]["M2 ridge, all 34"], out["lambda 1.0"]["M3 best-3 stack"])
    res["verdict"] = "multivariate adds" if best_mv >= base + 0.05 else "breadth alone"
    picks = {}
    for i in range(len(y)):
        m = np.arange(len(y)) != i
        _, cols = fit_predict(X[m], y[m], X[i:i + 1], 1.0, top=3)
        for c in cols:
            picks[feats[c]] = picks.get(feats[c], 0) + 1
    res["M3: indicators picked across the 21 folds"] = dict(sorted(picks.items(), key=lambda kv: -kv[1]))
    pt = {}
    for name, cols, top in (("M0 breadth alone", jb, None), ("M2 ridge, all 34", list(range(X.shape[1])), None), ("M3 best-3 stack", list(range(X.shape[1])), 3)):
        p, used = fit_predict(X[:, cols], y, xt[:, cols], 1.0, top)
        pt[name] = {"P(correction)": float(p[0]), "uses": [feats[cols[c]] for c in used] if top else None}
    cvals = comp.loc[dec].to_numpy(float)
    pt["M1 theory composite"] = {"score": float(comp.loc[today_key]), "percentile among 21 dips": float((cvals < comp.loc[today_key]).mean()),
                                 "terms today": {k: round(float(s * F.loc[today_key, k]), 2) for k, s in M1.items()}}
    res["today (open dip, started 2026-10-16)"] = pt
    res["base rate"] = float(y.mean())
    res["context today"] = {"WTI": float(oil.iloc[-1]), "WTI 20-day %": float(100 * D["oil 20-day"].iloc[-1]), "gold 20-day %": float(100 * D["gold (20d)"].iloc[-1]),
                            "next FOMC decision": "2026-10-28", "sessions to it from Oct 23": int(D["sessions to next FOMC"].iloc[-1])}
    pd.DataFrame({"episode": dec, "correction": y, "M0 LOO p": P0, "M2 LOO p": P2, "M3 LOO p": P3, "M1 score": cvals}).round(3).to_csv(Dz.OUT / "multivar_episodes.csv", index=False)
    F.round(3).to_csv(Dz.OUT / "multivar_features.csv")
    (Dz.OUT / "multivar.json").write_text(json.dumps(res, indent=1, default=float))
    return res


if __name__ == "__main__":
    print(json.dumps(main(sys.argv[1]), indent=1, default=float))
