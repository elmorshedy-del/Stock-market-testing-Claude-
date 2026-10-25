"""Amendment 2 (pre-registered at 0f3aa41): R3a the near-the-high control on US/AAPL; R3b largest-stock decoupling in 12 other markets.
Usage: python round3.py <US data folder> <international data folder>  -> out/r3a.json, out/r3b.json, out/r3b_markets.csv"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import decoupling as Dc

PAIRS = [("KS11", "005930.KS"), ("TWII", "2330.TW"), ("SSMI", "NESN.SW"), ("AEX", "ASML.AS"), ("GDAXI", "SAP.DE"), ("FCHI", "MC.PA"),
         ("HSI", "0700.HK"), ("NSEI", "RELIANCE.NS"), ("AXJO", "CBA.AX"), ("GSPTSE", "RY.TO"), ("N225", "9983.T"), ("FTSE", "AZN.L")]
START, END = pd.Timestamp("2000-01-01"), Dc.EVAL_END
NSHIFT = 2000
RNG = np.random.default_rng(20261027)


def close_local(folder, name):
    d = json.loads((Path(folder) / f"{name}.json").read_text())["chart"]["result"][0]
    tz = d["meta"]["exchangeTimezoneName"]
    idx = pd.to_datetime(d["timestamp"], unit="s", utc=True).tz_convert(tz).normalize().tz_localize(None)
    s = pd.Series(d["indicators"]["quote"][0]["close"], index=idx, dtype=float).dropna()
    s = s[~s.index.duplicated(keep="last")].sort_index()
    return s[s > 0]


def distance(ix):
    return (ix / ix.rolling(252, min_periods=60).max() - 1).to_numpy()


def bins(dist, ok):
    b = np.full(len(dist), -1)
    q = pd.qcut(pd.Series(dist[ok]).rank(method="first"), 5, labels=False).to_numpy()
    b[np.nonzero(ok)[0]] = q
    return b


def adj_diff(on, ahead, ok, b):
    tot, w = 0.0, 0
    for q in range(5):
        mq = ok & (b == q)
        a, f = mq & on, mq & ~on
        na = a.sum()
        if na and f.sum():
            tot += na * (ahead[a].mean() - ahead[f].mean())
            w += na
    return tot / w if w else np.nan


def plain_diff(on, ahead, ok):
    return ahead[ok & on].mean() - ahead[ok & ~on].mean()


def shift_test(on, ahead, ok, b):
    obs = adj_diff(on, ahead, ok, b)
    null = np.array([adj_diff(np.roll(on, s), ahead, ok, b) for s in RNG.integers(60, len(on) - 60, NSHIFT)])
    return {"days": int(ok.sum()), "alarm days": int((ok & on).sum()), "distance-adjusted difference": float(obs),
            "plain difference": float(plain_diff(on, ahead, ok)), "p (one-sided, shift)": float((null >= obs).mean())}


def logit(X, y, it=50):
    b = np.zeros(X.shape[1])
    for _ in range(it):
        p = 1 / (1 + np.exp(-X @ b))
        Hm = (X * (p * (1 - p))[:, None]).T @ X + 1e-6 * np.eye(X.shape[1])
        b += np.linalg.solve(Hm, X.T @ (y - p))
    return b


def r3a(us):
    D = pd.read_csv(Dc.OUT / "daily.csv", index_col=0, parse_dates=True)
    spx = Dc.close(us, "GSPC").reindex(D.index)
    dist = distance(spx)
    alarm, ahead = D["alarm AAPL"].astype(bool).to_numpy(), D.ahead.astype(bool).to_numpy()
    base = ~D.inside.astype(bool).to_numpy() & D["corr AAPL"].notna().to_numpy() & np.isfinite(dist)
    res = {}
    for lab, (a, z) in {"2011-2026 (R3a primary)": ("2011-01-03", END), "2011-2022": ("2011-01-03", "2022-10-12"),
                        "channel 2022-2026 (discovery)": ("2022-10-13", END), "1990-2022": ("1990-01-02", "2022-10-12"),
                        "1990-2010": ("1990-01-02", "2010-12-31")}.items():
        ok = base & (D.index >= pd.Timestamp(a)) & (D.index <= pd.Timestamp(z))
        b = bins(dist, ok)
        res[lab] = shift_test(alarm, ahead, ok, b)
        res[lab]["by distance quintile (alarm days, P on, P off)"] = [
            [int((ok & (b == q) & alarm).sum()), float(ahead[ok & (b == q) & alarm].mean()) if (ok & (b == q) & alarm).any() else None,
             float(ahead[ok & (b == q) & ~alarm].mean())] for q in range(5)]
        res[lab]["distance quintile edges %"] = [float(100 * np.quantile(dist[ok], k / 5)) for k in range(6)]
    ok = base & (D.index >= "2011-01-03") & (D.index <= END) & D["avg pairwise corr"].notna().to_numpy()
    b = bins(dist, ok)
    X = np.column_stack([np.ones(ok.sum()), alarm[ok].astype(float)] + [(b[ok] == q).astype(float) for q in range(1, 5)] +
                        [D["alarm dispersion"].astype(bool).to_numpy()[ok].astype(float)])
    y = ahead[ok].astype(float)
    coef = logit(X, y)
    n = len(y)
    bs = []
    for _ in range(NSHIFT):
        st = RNG.integers(0, n - 20, int(np.ceil(n / 20)))
        ii = np.concatenate([np.arange(s, s + 20) for s in st])[:n]
        bs.append(logit(X[ii], y[ii])[1])
    res["logistic 2011-2026: ahead ~ AAPL alarm + distance quintiles + dispersion alarm"] = {
        "coef AAPL": float(coef[1]), "p (coef <= 0, 20-day block bootstrap)": float((np.array(bs) <= 0).mean())}
    p = res["2011-2026 (R3a primary)"]
    res["verdict"] = "pass" if p["distance-adjusted difference"] > 0 and p["p (one-sided, shift)"] < 0.05 else "fail"
    bt = bins(dist, base & (D.index >= "2011-01-03"))
    res["today"] = {"date": str(D.index[-1].date()), "AAPL alarm": bool(alarm[-1]), "S&P distance to 252d high %": float(100 * dist[-1]),
                    "distance quintile (0 = farthest from high, 4 = at the high)": int(bt[-1]) if bt[-1] >= 0 else None}
    return res


def market(intl, ix_name, st_name):
    ix, st = close_local(intl, ix_name), close_local(intl, st_name)
    st = st.reindex(ix.index)
    ri, rs = np.log(ix).diff(), np.log(st).diff()
    corr = Dc.roll_corr(rs, ri)
    full = corr.notna().cumsum() >= 252
    alarm = (Dc.pct(corr) <= 0.20).to_numpy() & corr.notna().to_numpy()
    tops, inside, ahead = Dc.tops_and_labels(ix)
    dist = distance(ix)
    ok = (ix.index >= START) & (ix.index <= END) & ~inside & full.to_numpy() & np.isfinite(dist)
    quality = {"index days |r| > 12%": int((ri.abs() > 0.12).sum()), "stock days |r| > 25%": int((rs.abs() > 0.25).sum())}
    ntops = int(sum(1 for t in tops if ix.index[t] >= START and ix.index[t] <= END and ok[max(t - 1, 0)]))
    return pd.DataFrame({"alarm": alarm, "ahead": ahead, "ok": ok, "dist": dist}, index=ix.index), ntops, quality


def r3b(intl):
    cal = pd.bdate_range(START, END)
    M, rows = {}, []
    for ix_name, st_name in PAIRS:
        try:
            f, ntops, q = market(intl, ix_name, st_name)
        except Exception as e:                                                # pre-registered: drop and list, no replacement
            rows.append({"index": ix_name, "name": st_name, "dropped": repr(e)})
            continue
        ok = f.ok.to_numpy()
        b = pd.Series(bins(f.dist.to_numpy(), ok), index=f.index)
        g = pd.DataFrame({"alarm": f.alarm.reindex(cal).ffill().fillna(False).astype(bool),
                          "ahead": f.ahead.reindex(cal).fillna(False).astype(bool),
                          "ok": f.ok.reindex(cal).fillna(False).astype(bool), "b": b.reindex(cal).fillna(-1).astype(int)})
        M[ix_name] = g
        own = shift_test(f.alarm.to_numpy(), f.ahead.to_numpy(), ok, b.to_numpy())
        rows.append({"index": ix_name, "name": st_name, "first day": str(f.index[ok][0].date()), "tops": ntops, **own, **q})
    arr = {k: (g.alarm.to_numpy(), g.ahead.to_numpy(), g.ok.to_numpy(), g.b.to_numpy()) for k, g in M.items()}
    avg = lambda k, fn: float(np.nanmean([fn(np.roll(a, k), h, o, b) for a, h, o, b in arr.values()]))
    obs = avg(0, adj_diff)
    obs_plain = avg(0, lambda a, h, o, b: plain_diff(a, h, o))
    shifts = RNG.integers(60, len(cal) - 60, NSHIFT)
    null = np.array([avg(k, adj_diff) for k in shifts])
    null_plain = np.array([avg(k, lambda a, h, o, b: plain_diff(a, h, o)) for k in shifts])
    T = pd.DataFrame(rows)
    T.to_csv(Dc.OUT / "r3b_markets.csv", index=False)
    res = {"markets used": list(M), "dropped": T[T.get("dropped", pd.Series(dtype=str)).notna()]["index"].tolist() if "dropped" in T else [],
           "total tops": int(T.tops.sum()),
           "PRIMARY average distance-adjusted difference": obs, "p (one-sided, common shift)": float((null >= obs).mean()),
           "markets positive (adjusted)": int((T["distance-adjusted difference"] > 0).sum()),
           "average plain difference": obs_plain, "p plain (common shift)": float((null_plain >= obs_plain).mean()),
           "per market": T.drop(columns=[c for c in T.columns if c == "dropped"]).round(4).to_dict("records")}
    res["verdict"] = "pass" if obs > 0 and res["p (one-sided, common shift)"] < 0.05 else "fail"
    return res


if __name__ == "__main__":
    a = r3a(sys.argv[1])
    (Dc.OUT / "r3a.json").write_text(json.dumps(a, indent=1, default=float))
    print("R3A", json.dumps(a, indent=1, default=float))
    b = r3b(sys.argv[2])
    (Dc.OUT / "r3b.json").write_text(json.dumps(b, indent=1, default=float))
    print("R3B", json.dumps(b, indent=1, default=float))
    v = (a["verdict"], b["verdict"])
    overall = ("the decoupling warning is real and general" if b["verdict"] == "pass" else
               "US/AAPL-only, unconfirmed" if a["verdict"] == "pass" else "near-the-high artifact")
    (Dc.OUT / "r3_overall.json").write_text(json.dumps({"R3a": v[0], "R3b": v[1], "overall": overall}, indent=1))
    print("OVERALL", v, overall)
