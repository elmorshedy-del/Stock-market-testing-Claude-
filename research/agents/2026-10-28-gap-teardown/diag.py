"""Diagnostics on T3 (not pre-registered; labelled exploratory in the README):
(1) inverse-sampling-weighted Spearman with a date-block bootstrap CI; (2) the same after removing the 09:30-09:35 return
(rank-regression residuals), i.e. does flow or book add anything beyond the first 5 minutes' price move;
(3) VF vs SC medians at 09:35; (4) splits by period and symbol. Usage: python diag.py -> out/diag.json"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
F = pd.read_csv(HERE / "out" / "features.csv", parse_dates=["date"])
F = F.merge(pd.read_csv(HERE / "out" / "options_m5.csv", parse_dates=["date"]), on=["sym", "date"], how="left")
ev = pd.read_csv(HERE / "out" / "events.csv", parse_dates=["date"])
w_all = F.cls.map(ev.cls.value_counts() / F.cls.value_counts()).to_numpy()
Y, R5 = "ret 09:35->10:30 (sig)", "ret 09:30->09:35 (sig)"
EARLY = ["M6 first-5m delta %", "M7 first-5m book imbalance", "M7b first-5m ask depth $", "M7c first-5m bid depth $",
         "M8 first-5m progress per 1k bought (sig)", "M9 first-5m spread bp", "M10 first-5m retail-size share", R5,
         "M3x mean imbalance 09:25-09:30 / paired (exploratory)"]
rng = np.random.default_rng(1)


def wcorr(a, b, w):
    ma, mb = np.average(a, weights=w), np.average(b, weights=w)
    return np.sum(w * (a - ma) * (b - mb)) / np.sqrt(np.sum(w * (a - ma) ** 2) * np.sum(w * (b - mb) ** 2))


def resid(a, z, w):           # weighted least-squares residual of ranks a on ranks z
    X = np.c_[np.ones_like(z), z]; W = np.diag(w)
    beta = np.linalg.solve(X.T @ W @ X, X.T @ W @ a); return a - X @ beta


def one(df, c, w, partial):
    x = df.groupby("sym")[c].rank(pct=True).to_numpy(); y = df[Y].to_numpy(); z = df.groupby("sym")[R5].rank(pct=True).to_numpy()
    ok = ~np.isnan(x) & ~np.isnan(y)
    x, y, z, w, d = x[ok], y[ok], z[ok], w[ok], df.date.to_numpy()[ok]
    rx, ry, rz = stats.rankdata(x), stats.rankdata(y), stats.rankdata(z)

    def stat(idx):
        a, b, ww = rx[idx], ry[idx], w[idx]
        if partial: a, b = resid(a, rz[idx], ww), resid(b, rz[idx], ww)
        return wcorr(a, b, ww)
    est = stat(np.arange(len(x)))
    ud = np.unique(d); bs = []
    for _ in range(1000):
        pick = rng.choice(ud, len(ud)); idx = np.concatenate([np.flatnonzero(d == q) for q in pick])
        bs.append(stat(idx))
    bs = np.array(bs); p = min(1, 2 * min((bs <= 0).mean(), (bs >= 0).mean()) + 1 / 1000)
    return {"rho": float(est), "ci95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))], "p_boot": float(p), "n": int(ok.sum())}


out = {"weighted": {}, "weighted_partial_on_first5m_return": {}}
for c in EARLY:
    out["weighted"][c] = one(F, c, w_all, False)
    if c != R5: out["weighted_partial_on_first5m_return"][c] = one(F, c, w_all, True)
med = F[F.cls.isin(["VF", "SC"])].groupby("cls")[EARLY + ["gamma 1 sig below open, $bn", "open vs flip (sig)", "gamma at open, $bn", "opening paired shares"]].median().T
out["medians_09:35"] = med.to_dict()
for nm, msk in {"2018-2021": F.date < "2022-01-01", "2022-2026": F.date >= "2022-01-01"}.items():
    out[f"M6 weighted {nm}"] = one(F[msk].reset_index(drop=True), "M6 first-5m delta %", w_all[msk.to_numpy()], False)
    out[f"M6 partial {nm}"] = one(F[msk].reset_index(drop=True), "M6 first-5m delta %", w_all[msk.to_numpy()], True)
for s in ("TSLA", "AAPL", "NVDA", "QQQ"):
    m = (F.sym == s).to_numpy(); out[f"M6 partial {s}"] = one(F[m].reset_index(drop=True), "M6 first-5m delta %", w_all[m], True)
json.dump(out, open(HERE / "out" / "diag.json", "w"), indent=1)
pd.set_option("display.width", 220)
for k in ("weighted", "weighted_partial_on_first5m_return"):
    print(k); print(pd.DataFrame(out[k]).T.round(3).to_string())
print(med.round(3).to_string())
for k, v in out.items():
    if k.startswith("M6"): print(k, {a: (np.round(b, 3) if not isinstance(b, list) else np.round(b, 3).tolist()) for a, b in v.items()})
