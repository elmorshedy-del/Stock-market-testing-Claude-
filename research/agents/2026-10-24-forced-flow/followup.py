"""Amendment 1 follow-ups (README.md, pre-registered at e3988f2): F1 A1 dissection, F2 echo mechanism checks,
F3 expiry size law, F4 cleaner leverage.
Usage: python followup.py <GSPC_max.json>  -> out/f1.json .. out/f4.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import test_a as A
import test_bcd as B

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
RNG = np.random.default_rng(20261025)
NBOOT = 2000


def fit(D):
    X = np.column_stack([np.ones(len(D)), D.x, D.x * D.Hc, D.x * D.RVc, D.Hc, D.RVc])
    return np.linalg.lstsq(X, D.y.to_numpy(), rcond=None)[0]


def f1_frame(kind):
    if kind == "sp":
        D = A.a1_sp()
        r = np.log(A.load_bars("^GSPC").close).diff()
        D["RVp"] = A.pct(r.rolling(20).std()).reindex(D.index)
        fwd = {h: r[::-1].rolling(h).sum()[::-1].shift(-1).reindex(D.index) for h in range(1, 11)}
        D["sym"] = "S&P"
    else:
        parts = []
        for sym in A.TICKERS:
            b = A.load_bars(sym)
            b = b[b.index <= A.END]
            r = np.log(b.close).diff()
            sd = r.rolling(20).std()
            g = pd.read_csv(A.MICRO / "out" / f"td_gamma_{sym}.csv", parse_dates=["date"]).set_index("date")
            dv = (b.close * b.volume).rolling(20).mean()
            X = pd.DataFrame({"H": g.gex_classic / dv.reindex(g.index)})
            X["p"] = A.pct(X.H)
            X["x"], X["y"] = (r / sd).reindex(X.index), (r.shift(-1) / sd).reindex(X.index)
            X["RVp"] = A.pct(sd).reindex(X.index)
            for h in range(1, 11):
                X[f"c{h}"] = (r[::-1].rolling(h).sum()[::-1].shift(-1) / sd).reindex(X.index)
            X["sym"] = sym
            parts.append(X)
        D = pd.concat(parts)
        fwd = None
    if fwd is not None:
        for h, s in fwd.items():
            D[f"c{h}"] = s
    D = D.dropna(subset=["x", "y", "p", "RVp"])
    D["Hc"], D["RVc"] = D.p - 0.5, D.RVp - 0.5
    return D


def f1():
    res = {}
    for kind, lab in (("names", "6 names pooled (z-returns)"), ("sp", "S&P")):
        D = f1_frame(kind)
        b = fit(D)
        bs = A.block_boot(D, lambda X: fit(X)[2], None if kind == "sp" else "sym")
        r = {"days": int(len(D)), "b1 (x)": float(b[1]), "b2 (x*gamma pct)": float(b[2]), "b3 (x*vol pct)": float(b[3]),
             "p (b2 <= 0, block bootstrap)": float((bs <= 0).mean()), "b2 ci95": [float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))],
             "corr(gamma pct, vol pct)": float(np.corrcoef(D.p, D.RVp)[0, 1])}
        for sgn, m in (("up days", D.x > 0), ("down days", D.x < 0)):
            lo, hi = m & (D.p < 0.5), m & (D.p >= 0.5)
            r[f"beta {sgn}: low-gamma half / high-gamma half"] = [A.slope(D.x[lo], D.y[lo]), A.slope(D.x[hi], D.y[hi])]
        lo, hi = D.p < 0.5, D.p >= 0.5
        gap = []
        for h in range(1, 11):
            ok = D[f"c{h}"].notna()
            gap.append(A.slope(D.x[lo & ok], D[f"c{h}"][lo & ok]) - A.slope(D.x[hi & ok], D[f"c{h}"][hi & ok]))
        r["cumulative response gap (low - high gamma), days 1..10"] = [round(g, 4) for g in gap]
        r["cumulative response low-gamma half, days 1..10"] = [round(A.slope(D.x[lo & D[f"c{h}"].notna()], D[f"c{h}"][lo & D[f"c{h}"].notna()]), 4) for h in range(1, 11)]
        r["cumulative response high-gamma half, days 1..10"] = [round(A.slope(D.x[hi & D[f"c{h}"].notna()], D[f"c{h}"][hi & D[f"c{h}"].notna()]), 4) for h in range(1, 11)]
        r["verdict"] = "ordering survives the volatility control" if r["p (b2 <= 0, block bootstrap)"] < 0.05 else "explained by volatility (or too weak)"
        res[lab] = r
    return res


def f2(c):
    r = np.log(c).diff()
    a, rv, lc = r.abs().to_numpy(), r.to_numpy(), np.log(c.to_numpy())
    sd = r.rolling(20).std().shift(1).to_numpy()
    idx = c.index
    base3 = pd.Series(lc[3:] - lc[:-3], index=idx[:-3])
    post = idx >= pd.Timestamp("2008-01-01")
    mu = base3[base3.index >= "2008-01-01"].mean()
    qual, nonq = [], []
    for s in range(21, len(a) - 21 - 30):
        if not post[s] or not np.isfinite(sd[s]) or a[s] < 2.5 * sd[s]:
            continue
        (qual if a[s] > a[s + 1:s + 21].max() else nonq).append(s)
    ex = lambda s, L: lc[s + L - 1 + 3] - lc[s + L - 1] - mu
    E = pd.DataFrame({L: [ex(s, L) for s in qual] for L in range(15, 28)}, index=idx[qual])
    plac = E[[15, 16, 17, 18, 24, 25, 26, 27]].mean(axis=1)
    d = (E[21] - plac).to_numpy()
    bs = np.array([RNG.choice(d, len(d)).mean() for _ in range(NBOOT)])
    nq = np.array([ex(s, 21) for s in nonq])
    q21 = E[21].to_numpy()
    bs2 = np.array([RNG.choice(q21, len(q21)).mean() - RNG.choice(nq, len(nq)).mean() for _ in range(NBOOT)])
    shock = pd.Series([rv[s] for s in qual], index=idx[qual])
    month = pd.Series(idx.month, index=idx)
    last_day = month.ne(month.shift(-1))
    first3 = month.ne(month.shift(1)) | month.ne(month.shift(2)) | month.ne(month.shift(3))
    tom = (last_day | first3).to_numpy()
    keep = np.array([not tom[s + 21 - 1 + 1:s + 21 - 1 + 4].any() for s in qual])
    k21 = q21[keep]
    bs3 = np.array([RNG.choice(k21, len(k21)).mean() for _ in range(NBOOT)])
    res = {"qualifying events (post-2008)": len(qual), "non-qualifying shocks": len(nonq),
           "1 lag profile: mean excess % by start lag 15..27": {int(L): round(float(100 * E[L].mean()), 3) for L in E},
           "1 excess at 21 minus placebo lags %": float(100 * d.mean()), "1 p (one-sided)": float((bs <= 0).mean()),
           "2 qualifying minus non-qualifying at lag 21 %": float(100 * (q21.mean() - nq.mean())), "2 p (one-sided)": float((bs2 <= 0).mean()),
           "2 non-qualifying excess %": float(100 * nq.mean()),
           "3 up-shocks: events, mean excess %": [int((shock > 0).sum()), float(100 * q21[(shock > 0).to_numpy()].mean())],
           "3 down-shocks: events, mean excess %": [int((shock < 0).sum()), float(100 * q21[(shock < 0).to_numpy()].mean())],
           "4 excluding turn-of-month echo windows: events, mean excess %, p": [int(keep.sum()), float(100 * k21.mean()), float((bs3 <= 0).mean())]}
    checks = [res["1 p (one-sided)"] < 0.05, res["2 p (one-sided)"] < 0.05,
              res["3 up-shocks: events, mean excess %"][1] > 0 and res["3 down-shocks: events, mean excess %"][1] > 0,
              res["4 excluding turn-of-month echo windows: events, mean excess %, p"][1] > 0]
    res["checks passed (1, 2, 3, 4)"] = checks
    res["verdict"] = "mechanism stands" if all(checks) else "mechanism not established"
    E.to_csv(OUT / "f2_lag_profile_events.csv")
    return res


def f3():
    Bv = pd.read_csv(OUT / "b_events.csv", parse_dates=["expiry"])
    rows = []
    for sym in A.TICKERS:
        g = pd.read_csv(A.MICRO / "out" / f"td_gamma_{sym}.csv", parse_dates=["date"]).set_index("date")
        b = A.load_bars(sym)
        dv = (b.close * b.volume).rolling(20).mean()
        for _, e in Bv[Bv.sym == sym].iterrows():
            i = b.index.get_loc(e.expiry)
            prev = b.index[i - 1]
            rows.append(e.x * abs(g.loc[prev, "gex_classic"]) / dv.loc[prev])
    Bv["x2"] = rows
    n0 = len(Bv)
    Bv = Bv[Bv.x2 > 0].reset_index(drop=True)                 # a zero expiring share has no released hedge to log
    Bv["lx2"] = np.log(Bv.x2)
    dm = lambda s: s - Bv.groupby("sym")[s.name].transform("mean")
    x, y = dm(Bv.lx2).to_numpy(), dm(Bv.y).to_numpy()
    sl = lambda xx: float((xx * y).sum() / (xx ** 2).sum())
    obs = sl(x)
    groups = [np.nonzero((Bv.sym == s).to_numpy())[0] for s in A.TICKERS]
    null = np.empty(B.NPERM)
    for k in range(B.NPERM):
        xx = x.copy()
        for gi in groups:
            xx[gi] = RNG.permutation(x[gi])
        null[k] = sl(xx)
    q = pd.qcut(Bv.lx2.rank(method="first"), 3, labels=["low", "mid", "high"])
    res = {"events": int(len(Bv)), "dropped (zero expiring share)": int(n0 - len(Bv)), "slope of vol change on log(released hedge / dollar volume), within ticker": obs,
           "p (one-sided, permutation)": float((null >= obs).mean()),
           "mean vol change by third (log)": {str(k): float(v) for k, v in Bv.y.groupby(q, observed=False).mean().items()},
           "per ticker slope": {s: float(np.polyfit(Bv.lx2[Bv.sym == s], Bv.y[Bv.sym == s], 1)[0]) for s in A.TICKERS}}
    res["verdict"] = "pass" if (obs > 0 and res["p (one-sided, permutation)"] < 0.05) else "fail"
    return res


def f4(c):
    Dv = pd.read_csv(OUT / "d_events.csv", parse_dates=["date"]).set_index("date")
    m = c.resample("ME").last()
    lev = []
    for d in Dv.index:
        mm = d - pd.offsets.MonthEnd(2)
        yoy = Dv.loc[d, "margin yoy %"] / 100
        spx = np.log(m[m.index <= mm].iloc[-1] / m[m.index <= mm - pd.offsets.MonthEnd(12)].iloc[-1])
        lev.append(np.log1p(yoy) - spx)
    x, y = np.array(lev), Dv["max drawdown 20d %"].to_numpy()
    sl = lambda xx: float(np.polyfit(xx, y, 1)[0])
    obs = sl(x)
    null = np.array([sl(RNG.permutation(x)) for _ in range(B.NPERM)])
    hi = x >= np.median(x)
    res = {"events": int(len(x)), "slope of drawdown on 12m change in log(margin/S&P)": obs,
           "p (one-sided, slope >= 0)": float((null <= obs).mean()), "corr": float(np.corrcoef(x, y)[0, 1]),
           "mean drawdown high / low half %": [float(y[hi].mean()), float(y[~hi].mean())]}
    res["verdict"] = "pass" if (obs < 0 and res["p (one-sided, slope >= 0)"] < 0.05) else "fail"
    return res


if __name__ == "__main__":
    c = B.gspc(sys.argv[1])
    todo = sys.argv[2].split(",") if len(sys.argv) > 2 else ["f1", "f2", "f3", "f4"]
    for name, fn in [(k, v) for k, v in (("f1", f1), ("f2", lambda: f2(c)), ("f3", f3), ("f4", lambda: f4(c))) if k in todo]:
        r = fn()
        (OUT / f"{name}.json").write_text(json.dumps(r, indent=1, default=float))
        print(name.upper(), json.dumps(r, indent=1, default=float))
