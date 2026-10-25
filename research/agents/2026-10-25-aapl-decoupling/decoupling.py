"""AAPL decoupling deep-dive (README.md, pre-registered at d60f8dc): H1 out of sample, H2 other mega-caps,
H3 earnings-jump robustness, H4 beyond dispersion.
Usage: python decoupling.py <folder with Yahoo chart JSONs: GSPC.json, AAPL.json, ...>  -> out/decoupling.json, out/daily.csv"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
EVAL_END = pd.Timestamp("2026-08-14")
MEGA = ["AAPL", "MSFT", "AMZN", "GOOGL", "META", "NVDA"]
PANEL = ["AAPL", "MSFT", "AMZN", "GOOGL", "META", "NVDA", "ADBE", "AMAT", "AMD", "BA", "CAT", "COST", "CSCO", "DIS", "GE", "IBM", "INTC", "JNJ",
         "JPM", "KO", "LLY", "MCD", "MMM", "MRK", "MU", "ORCL", "PEP", "PFE", "PG", "QCOM", "T", "TXN", "UNH", "WMT", "XOM", "HD", "CVX",
         "BAC", "C", "WFC", "VZ"]
W, NSHIFT, NBOOT, HORIZON = 20, 2000, 2000, 30
RNG = np.random.default_rng(20261025)


def close(folder, name):
    d = json.loads((Path(folder) / f"{name}.json").read_text())["chart"]["result"][0]
    idx = pd.to_datetime(d["timestamp"], unit="s", utc=True).tz_convert("America/New_York").normalize().tz_localize(None)
    s = pd.Series(d["indicators"]["quote"][0]["close"], index=idx, dtype=float).dropna()
    s = s[~s.index.duplicated(keep="last")].sort_index()
    return s[s > 0]


def pct(s, n=252):
    return s.rolling(n, min_periods=120).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True)


def tops_and_labels(spx):
    """Tops: a 252-day-high close followed by a close >= 5% below it before any close above it."""
    v = spx.to_numpy()
    hi252 = spx.rolling(252, min_periods=60).max().to_numpy()
    tops, inside = [], np.zeros(len(v), bool)
    i = 0
    while i < len(v):
        if v[i] >= hi252[i] - 1e-9:
            j = i + 1
            while j < len(v) and v[j] <= v[i] and v[j] > 0.95 * v[i]:
                j += 1
            if j < len(v) and v[j] <= 0.95 * v[i]:
                k = j
                while k + 1 < len(v) and v[k + 1] <= v[i]:
                    k += 1
                low = i + 1 + int(np.argmin(v[i + 1:k + 1]))
                tops.append(i)
                inside[i + 1:low + 1] = True
                i = low + 1
                continue
        i += 1
    ahead = np.zeros(len(v), bool)
    for t in tops:
        ahead[max(0, t - HORIZON + 1):t + 1] = True
    return tops, inside, ahead


def roll_corr(a, b, w=W):
    return a.rolling(w).corr(b)


def corr_drop2(ra, rm, w=W):
    """20-day correlation with the 2 days of largest |ra - rm| removed from each window."""
    A, M = ra.to_numpy(), rm.to_numpy()
    out = np.full(len(A), np.nan)
    for t in range(w - 1, len(A)):
        a, m = A[t - w + 1:t + 1], M[t - w + 1:t + 1]
        if np.isnan(a).any() or np.isnan(m).any():
            continue
        keep = np.argsort(np.abs(a - m))[:-2]
        out[t] = np.corrcoef(a[keep], m[keep])[0, 1]
    return pd.Series(out, index=ra.index)


def corr_rank(ra, rm, w=W):
    """Rolling Spearman correlation: ranks taken within each window."""
    A, M = ra.to_numpy(), rm.to_numpy()
    out = np.full(len(A), np.nan)
    for t in range(w - 1, len(A)):
        a, m = A[t - w + 1:t + 1], M[t - w + 1:t + 1]
        if np.isnan(a).any() or np.isnan(m).any():
            continue
        out[t] = np.corrcoef(pd.Series(a).rank(), pd.Series(m).rank())[0, 1]
    return pd.Series(out, index=ra.index)


def diff_test(on, ahead, ok):
    on = np.asarray(on, bool)
    f = lambda o: ahead[ok & o].mean() - ahead[ok & ~o].mean()
    obs = f(on)
    null = np.array([f(np.roll(on, s)) for s in RNG.integers(60, len(on) - 60, NSHIFT)])
    return {"days": int(ok.sum()), "alarm share": float(on[ok].mean()), "P(top within 30 | on)": float(ahead[ok & on].mean()),
            "P(top within 30 | off)": float(ahead[ok & ~on].mean()), "difference": float(obs), "p (one-sided, shift)": float((null >= obs).mean())}


def main(folder):
    OUT.mkdir(exist_ok=True)
    spx = close(folder, "GSPC")
    spx = spx[spx.index >= "1985-01-01"]
    rm = np.log(spx).diff()
    tops, inside, ahead = tops_and_labels(spx)
    idx = spx.index
    D = pd.DataFrame(index=idx)
    stocks = {s: close(folder, s).reindex(idx) for s in PANEL}
    rets = {s: np.log(stocks[s]).diff() for s in PANEL}
    for s in MEGA:
        D[f"corr {s}"] = roll_corr(rets[s], rm)
        D[f"alarm {s}"] = pct(D[f"corr {s}"]) <= 0.20
    D["corr mega avg"] = D[[f"corr {s}" for s in MEGA]].mean(axis=1, skipna=False)
    D["alarm mega avg"] = pct(D["corr mega avg"]) <= 0.20
    D["corr AAPL drop2"] = corr_drop2(rets["AAPL"], rm)
    D["alarm AAPL drop2"] = pct(D["corr AAPL drop2"]) <= 0.20
    D["corr AAPL rank"] = corr_rank(rets["AAPL"], rm)
    D["alarm AAPL rank"] = pct(D["corr AAPL rank"]) <= 0.20
    R = pd.DataFrame(rets)
    pair = []
    for t in range(W - 1, len(idx)):
        X = R.iloc[t - W + 1:t + 1].dropna(axis=1)
        if X.shape[1] < 10:
            pair.append(np.nan)
            continue
        C = np.corrcoef(X.to_numpy().T)
        pair.append(C[np.triu_indices_from(C, 1)].mean())
    D["avg pairwise corr"] = np.r_[np.full(W - 1, np.nan), pair]
    D["alarm dispersion"] = pct(D["avg pairwise corr"]) <= 0.20
    D["ahead"], D["inside"] = ahead, inside
    D["top"] = False
    D.iloc[tops, D.columns.get_loc("top")] = True
    D.to_csv(OUT / "daily.csv")
    res = {"tops (all, 1985-2026)": int(len(tops)), "tops by era": {}}
    def window(a, b):
        return (idx >= pd.Timestamp(a)) & (idx <= pd.Timestamp(b)) & ~inside & D["corr AAPL"].notna().to_numpy()
    for lab, (a, b) in {"1990-2022 (H1 primary)": ("1990-01-02", "2022-10-12"), "1990-2010": ("1990-01-02", "2010-12-31"),
                        "2011-2022": ("2011-01-03", "2022-10-12"), "channel 2022-2026 (discovery)": ("2022-10-13", str(EVAL_END.date()))}.items():
        m = window(a, b)
        res["tops by era"][lab] = int(sum(1 for t in tops if pd.Timestamp(a) <= idx[t] <= pd.Timestamp(b)))
        res[f"H1 AAPL, {lab}"] = diff_test(D["alarm AAPL"].to_numpy(), ahead, m)
    m13 = window("2013-01-02", str(EVAL_END.date())) & D["corr META"].notna().to_numpy()
    for s in MEGA:
        res[f"H2 {s}, 2013-2026"] = diff_test(D[f"alarm {s}"].to_numpy(), ahead, m13)
    res["H2 mega-cap average, 2013-2026"] = diff_test(D["alarm mega avg"].to_numpy(), ahead, m13)
    m11 = window("2011-01-03", str(EVAL_END.date()))
    res["H3 AAPL plain, 2011-2026"] = diff_test(D["alarm AAPL"].to_numpy(), ahead, m11)
    res["H3 AAPL drop-2 largest gaps, 2011-2026"] = diff_test(D["alarm AAPL drop2"].to_numpy(), ahead, m11)
    res["H3 AAPL rank correlation, 2011-2026"] = diff_test(D["alarm AAPL rank"].to_numpy(), ahead, m11)
    res["H4 dispersion alarm alone, 2011-2026"] = diff_test(D["alarm dispersion"].to_numpy(), ahead, m11)
    Z = D[m11].dropna(subset=["avg pairwise corr"])
    y = Z.ahead.astype(float).to_numpy()
    X = np.column_stack([np.ones(len(Z)), Z["alarm AAPL"].astype(float), Z["alarm dispersion"].astype(float)])
    def logit(X, y, it=50):
        b = np.zeros(X.shape[1])
        for _ in range(it):
            p = 1 / (1 + np.exp(-X @ b))
            g = X.T @ (y - p)
            Hm = (X * (p * (1 - p))[:, None]).T @ X + 1e-6 * np.eye(X.shape[1])
            b += np.linalg.solve(Hm, g)
        return b
    b = logit(X, y)
    n = len(y)
    bs = []
    for _ in range(NBOOT):
        starts = RNG.integers(0, n - 20, int(np.ceil(n / 20)))
        ii = np.concatenate([np.arange(s, s + 20) for s in starts])[:n]
        bs.append(logit(X[ii], y[ii])[1])
    bs = np.array(bs)
    res["H4 logistic: AAPL alarm coefficient (with dispersion alarm)"] = {"coef AAPL": float(b[1]), "coef dispersion": float(b[2]),
                                                                          "p (AAPL coef <= 0, block bootstrap)": float((bs <= 0).mean()),
                                                                          "corr of the two alarms": float(np.corrcoef(X[:, 1], X[:, 2])[0, 1])}
    v = {"H1": res["H1 AAPL, 1990-2022 (H1 primary)"]["difference"] > 0 and res["H1 AAPL, 1990-2022 (H1 primary)"]["p (one-sided, shift)"] < 0.05,
         "H1 mechanism (2011-22 > 1990-2010)": res["H1 AAPL, 2011-2022"]["difference"] > res["H1 AAPL, 1990-2010"]["difference"],
         "H2": sum(res[f"H2 {s}, 2013-2026"]["difference"] > 0 for s in MEGA[1:]) >= 3 and res["H2 mega-cap average, 2013-2026"]["p (one-sided, shift)"] < 0.05,
         "H3": res["H3 AAPL drop-2 largest gaps, 2011-2026"]["difference"] > 0 and res["H3 AAPL drop-2 largest gaps, 2011-2026"]["p (one-sided, shift)"] < 0.05,
         "H4": res["H4 logistic: AAPL alarm coefficient (with dispersion alarm)"]["coef AAPL"] > 0 and
               res["H4 logistic: AAPL alarm coefficient (with dispersion alarm)"]["p (AAPL coef <= 0, block bootstrap)"] < 0.05}
    res["verdicts"] = v
    res["overall"] = ("real and explained" if v["H1"] and sum([v["H2"], v["H3"], v["H4"]]) >= 2 else
                      "AAPL-specific but unexplained" if v["H1"] and not v["H2"] else
                      "channel coincidence" if not v["H1"] else "real, partly explained")
    res["today"] = {"AAPL corr": float(D["corr AAPL"].iloc[-1]), "AAPL drop-2 corr": float(D["corr AAPL drop2"].iloc[-1]),
                    "mega avg corr": float(D["corr mega avg"].iloc[-1]), "avg pairwise corr": float(D["avg pairwise corr"].iloc[-1]),
                    "alarms on": [k for k in D.columns if k.startswith("alarm") and bool(D[k].iloc[-1])], "date": str(idx[-1].date())}
    (OUT / "decoupling.json").write_text(json.dumps(res, indent=1, default=float))
    return res


if __name__ == "__main__":
    print(json.dumps(main(sys.argv[1]), indent=1, default=float))
