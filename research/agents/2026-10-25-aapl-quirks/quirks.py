"""Why does AAPL decouple? (README.md, pre-registered at 28b34ed): Part 0 scan and anatomy, T1-T5, the 2011-2019 contrast, the current episode.
Usage: python quirks.py <long folder> <etfs folder> <quirks folder>  -> out/quirks.json, out/daily.csv"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
W = {"AAPL": 0.065, "MSFT": 0.06, "NVDA": 0.05, "AMZN": 0.035, "GOOGL": 0.035, "META": 0.025}
PEERS = ["MSFT", "AMZN", "GOOGL", "META", "NVDA"]
NONSEMI = ["MSFT", "AMZN", "GOOGL", "META"]
P20, P11 = ("2020-01-02", "2026-10-23"), ("2011-01-03", "2019-12-31")
NB = 2000
RNG = np.random.default_rng(20261028)


def load(path):
    d = json.loads(Path(path).read_text())["chart"]["result"][0]
    idx = pd.to_datetime(d["timestamp"], unit="s", utc=True).tz_convert("America/New_York").normalize().tz_localize(None)
    q = d["indicators"]["quote"][0]
    f = pd.DataFrame({"open": q["open"], "close": q["close"]}, index=idx, dtype=float)
    f = f[~f.index.duplicated(keep="last")].sort_index()
    return f[(f.close > 0)]


def pct(s, n=252):
    return s.rolling(n, min_periods=120).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True)


def ols(x, y):
    m = np.isfinite(x) & np.isfinite(y)
    X = np.column_stack([np.ones(m.sum()), x[m]])
    return np.linalg.lstsq(X, y[m], rcond=None)[0]


def updown(x, y):
    dn, up = x < 0, x > 0
    return ols(x[dn], y[dn])[1], ols(x[up], y[up])[1]


def blocks(n, L=20):
    st = RNG.integers(0, n - L, int(np.ceil(n / L)))
    return np.concatenate([np.arange(s, s + L) for s in st])[:n]


def earnings_days(path, idx):
    out = []
    for q in json.loads(Path(path).read_text())["quarterlyEarnings"]:
        d = pd.Timestamp(q["reportedDate"])
        after = idx[idx > d] if q.get("reportTime", "post-market") != "pre-market" else idx[idx >= d]
        if len(after):
            out.append(after[0])
    return pd.DatetimeIndex(sorted(set(out)))


def calendar(idx):
    month = pd.Series(idx.month, index=idx)
    me = month.ne(month.shift(-1)).to_numpy()
    qw = np.zeros(len(idx), bool)
    for y in sorted(set(idx.year)):
        for m in (3, 6, 9, 12):
            fr = pd.date_range(f"{y}-{m:02d}-01", periods=31, freq="D")
            fr = fr[(fr.month == m) & (fr.weekday == 4)]
            c = idx[idx <= fr[2]]
            if len(c) and (fr[2] - c[-1]).days <= 3:
                qw[idx.get_loc(c[-1])] = True
    return qw, me


def fiscal_quarter_ends(years):
    out = []
    for y in years:
        for m in (3, 6, 9, 12):
            last = pd.Timestamp(y, m, 1) + pd.offsets.MonthEnd(0)
            out.append(last - pd.Timedelta(days=(last.weekday() - 5) % 7))
    return sorted(out)


def main(long, etfs, qf):
    OUT.mkdir(exist_ok=True)
    spx = load(Path(long) / "GSPC.json")
    spx = spx[spx.index >= "2009-01-01"]
    idx = spx.index
    rs = np.log(spx.close).diff()
    S = {s: load(Path(long) / f"{s}.json").reindex(idx) for s in W}
    r = {s: np.log(S[s].close).diff() for s in W}
    rm = {s: (rs - W[s] * r[s].fillna(0)) / (1 - W[s]) for s in W}
    beta = {s: (r[s].rolling(252, min_periods=200).cov(rm[s]) / rm[s].rolling(252, min_periods=200).var()).shift(1) for s in W}
    e = {s: r[s] - beta[s] * rm[s] for s in W}
    c20 = {s: r[s].rolling(20).corr(rm[s]) for s in W}
    alarm = {s: (pct(c20[s]) <= 0.20) & c20[s].notna() for s in W}
    smh, spy = load(Path(etfs) / "SMH.json").reindex(idx), load(Path(etfs) / "SPY.json").reindex(idx)
    f = np.log(smh.close).diff() - np.log(spy.close).diff()
    win = lambda a, b: (idx >= pd.Timestamp(a)) & (idx <= pd.Timestamp(b))
    res = {"scan": {}}
    # ---------- Part 0 ----------
    def scan(s, a, b):
        m = win(a, b) & np.isfinite(r[s]).to_numpy() & np.isfinite(rm[s]).to_numpy()
        x, y = rm[s].to_numpy()[m], r[s].to_numpy()[m]
        dn, up = updown(x, y)
        o = S[s].open.to_numpy()
        cl = S[s].close.to_numpy()
        on = np.log(o[1:] / cl[:-1])
        intra = np.log(cl / o)[1:]
        mm = m[1:] & np.isfinite(on) & np.isfinite(intra)
        ev = e[s].to_numpy()[m]
        worst = np.argsort(x)[:20]
        return {"beta": float(ols(x, y)[1]), "corr": float(np.corrcoef(x, y)[0, 1]), "downside beta": float(dn), "upside beta": float(up),
                "asymmetry (down - up)": float(dn - up), "overnight log return %": float(100 * on[mm].sum()), "intraday log return %": float(100 * intra[mm].sum()),
                "residual lag-1 autocorr": float(pd.Series(ev).autocorr(1)), "share of days 20d corr < 0.3": float((c20[s].to_numpy()[m] < 0.3).mean()),
                "mean residual on market's 20 worst days %": float(100 * np.nanmean(ev[worst])), "alarm share": float(alarm[s].to_numpy()[m].mean())}
    for s in W:
        res["scan"][f"{s} 2020-2026"] = scan(s, *P20)
    res["scan"]["AAPL 2011-2019"] = scan("AAPL", *P11)
    # anatomy: 20-day beta, market vol, own vol, idio vol relative to their trailing-252 medians
    an = {}
    for s in W:
        b20 = r[s].rolling(20).cov(rm[s]) / rm[s].rolling(20).var()
        sm, sx = rm[s].rolling(20).std(), r[s].rolling(20).std()
        se = (r[s] - b20 * rm[s]).rolling(20).std()
        rel = {k: (v / v.rolling(252, min_periods=120).median()).to_numpy() for k, v in
               {"20d beta": b20, "market vol": sm, "own vol": sx, "idiosyncratic vol": se}.items()}
        m = win(*P20)
        a_ = alarm[s].to_numpy()
        an[s] = {k: {"alarm days (median, 1 = normal)": float(np.nanmedian(v[m & a_])), "other days": float(np.nanmedian(v[m & ~a_]))} for k, v in rel.items()}
        if s == "AAPL":
            res["anatomy today (AAPL, 1 = normal)"] = {k: float(v[-1]) for k, v in rel.items()}
    res["anatomy 2020-2026"] = an
    # ---------- T1 ----------
    qf = Path(qf)
    ed = earnings_days(qf / "earn_AAPL.json", idx)
    react = pd.Series(idx.isin(ed), index=idx)
    inwin = react.astype(int).rolling(20, min_periods=1).max().astype(bool).to_numpy()
    def t1(a, b):
        m = win(a, b) & c20["AAPL"].notna().to_numpy()
        al = alarm["AAPL"].to_numpy()
        st = lambda o: inwin[m & o].mean() - inwin[m & ~o].mean()
        obs = st(al)
        null = np.array([st(np.roll(al, k)) for k in RNG.integers(60, len(al) - 60, NB)])
        return {"P(earnings in window | alarm)": float(inwin[m & al].mean()), "P(earnings in window | no alarm)": float(inwin[m & ~al].mean()),
                "difference": float(obs), "p (one-sided, shift)": float((null >= obs).mean())}
    res["T1 earnings calendar 2020-2026"] = t1(*P20)
    res["T1 contrast 2011-2019"] = t1(*P11)
    res["T1 verdict"] = "pass" if res["T1 earnings calendar 2020-2026"]["difference"] > 0 and res["T1 earnings calendar 2020-2026"]["p (one-sided, shift)"] < 0.05 else "fail"
    # ---------- T2 ----------
    def t2a(a, b):
        m = win(a, b) & np.isfinite(f).to_numpy() & np.all([np.isfinite(e[s]).to_numpy() for s in ["AAPL"] + NONSEMI], axis=0)
        F = f.to_numpy()[m]
        E = {s: e[s].to_numpy()[m] for s in ["AAPL"] + NONSEMI}
        stat = lambda ii: ols(F[ii], E["AAPL"][ii])[1] - np.mean([ols(F[ii], E[s][ii])[1] for s in NONSEMI])
        al = np.arange(len(F))
        obs = stat(al)
        bs = np.array([stat(blocks(len(F))) for _ in range(NB)])
        return {"AAPL loading on f": float(ols(F, E["AAPL"])[1]), "non-semi peer loadings": {s: float(ols(F, E[s])[1]) for s in NONSEMI},
                "AAPL minus peer average": float(obs), "p (>= 0, block bootstrap)": float((bs >= 0).mean()), "days": int(len(F))}
    res["T2a AI-factor loading 2023-2026"] = t2a("2023-01-03", P20[1])
    res["T2a contrast 2011-2022"] = t2a("2011-01-03", "2022-12-30")
    cmf = rm["AAPL"].rolling(20).corr(f)
    def t2b(a, b):
        m = win(a, b) & c20["AAPL"].notna().to_numpy() & cmf.notna().to_numpy()
        x = pd.Series(c20["AAPL"].to_numpy()).rank().to_numpy()
        y = pd.Series(cmf.to_numpy()).rank().to_numpy()
        sp = lambda yy: np.corrcoef(x[m], yy[m])[0, 1]
        obs = sp(y)
        null = np.array([sp(np.roll(y, k)) for k in RNG.integers(60, len(y) - 60, NB)])
        return {"spearman(AAPL 20d corr, corr(S&P ex-AAPL, f))": float(obs), "p (one-sided, shift)": float((null <= obs).mean())}
    res["T2b AI leadership vs AAPL coupling 2020-2026"] = t2b(*P20)
    res["T2b contrast 2011-2019"] = t2b(*P11)
    a2, b2 = res["T2a AI-factor loading 2023-2026"], res["T2b AI leadership vs AAPL coupling 2020-2026"]
    res["T2 verdict"] = "pass" if (a2["AAPL minus peer average"] < 0 and a2["p (>= 0, block bootstrap)"] < 0.05 and
                                   b2["spearman(AAPL 20d corr, corr(S&P ex-AAPL, f))"] < 0 and b2["p (one-sided, shift)"] < 0.05) else "fail"
    # ---------- T3 ----------
    def t3(a, b, peers=PEERS):
        m = win(a, b) & np.all([np.isfinite(r[s]).to_numpy() for s in ["AAPL"] + peers], axis=0)
        X = {s: rm[s].to_numpy()[m] for s in ["AAPL"] + peers}
        Y = {s: r[s].to_numpy()[m] for s in ["AAPL"] + peers}
        asym = lambda s, ii: (lambda d, u: d - u)(*updown(X[s][ii], Y[s][ii]))
        n = m.sum()
        al = np.arange(n)
        ob = asym("AAPL", al)
        od = ob - np.mean([asym(s, al) for s in peers])
        bA, bD = [], []
        for _ in range(NB):
            ii = blocks(n)
            aa = asym("AAPL", ii)
            bA.append(aa)
            bD.append(aa - np.mean([asym(s, ii) for s in peers]))
        return {"AAPL asymmetry (down - up beta)": float(ob), "p (>= 0)": float((np.array(bA) >= 0).mean()),
                "peer asymmetries": {s: float(asym(s, al)) for s in peers}, "AAPL minus peer average": float(od), "p diff (>= 0)": float((np.array(bD) >= 0).mean())}
    res["T3 defensive asymmetry 2020-2026"] = t3(*P20)
    res["T3 contrast 2013-2019 (META listed)"] = t3("2013-01-02", P11[1])
    t3r = res["T3 defensive asymmetry 2020-2026"]
    res["T3 verdict"] = "pass" if (t3r["AAPL asymmetry (down - up beta)"] < 0 and t3r["p (>= 0)"] < 0.05 and
                                   t3r["AAPL minus peer average"] < 0 and t3r["p diff (>= 0)"] < 0.05) else "fail"
    # ---------- T4 ----------
    fqe = [d for d in fiscal_quarter_ends(range(2009, 2027))]
    black = np.zeros(len(idx), bool)
    qid = np.full(len(idx), -1)
    for k, q in enumerate(fqe):
        if q - pd.Timedelta(days=14) > idx[-1]:
            continue
        nxt = ed[ed > q]
        stop = nxt[0] if len(nxt) else idx[-1]                       # quarter not yet reported: blackout runs to the last day of data
        black |= (idx >= q - pd.Timedelta(days=14)) & (idx <= stop)
        qid[(idx > q) & (idx <= (fqe[k + 1] if k + 1 < len(fqe) else idx[-1]))] = k
    def t4(a, b):
        m = win(a, b) & np.isfinite(r["AAPL"]).to_numpy() & (qid >= 0)
        x, y, bl, q = rm["AAPL"].to_numpy(), r["AAPL"].to_numpy(), black, qid
        def stat(rows):
            o, k = rows[~bl[rows]], rows[bl[rows]]
            return updown(x[o], y[o])[0] - updown(x[k], y[k])[0]
        rows = np.nonzero(m)[0]
        obs = stat(rows)
        qs = np.unique(q[rows])
        byq = {k: rows[q[rows] == k] for k in qs}
        bs = np.array([stat(np.concatenate([byq[k] for k in RNG.choice(qs, len(qs))])) for _ in range(NB)])
        o, k = rows[~bl[rows]], rows[bl[rows]]
        return {"downside beta open": float(updown(x[o], y[o])[0]), "downside beta blackout": float(updown(x[k], y[k])[0]),
                "upside beta open / blackout": [float(updown(x[o], y[o])[1]), float(updown(x[k], y[k])[1])],
                "open minus blackout (downside)": float(obs), "p (>= 0, quarter bootstrap)": float((bs >= 0).mean()),
                "mean residual % open / blackout": [float(100 * np.nanmean(e["AAPL"].to_numpy()[o])), float(100 * np.nanmean(e["AAPL"].to_numpy()[k]))],
                "blackout share of days": float(bl[rows].mean())}
    res["T4 buyback windows 2020-2026"] = t4(*P20)
    res["T4 contrast 2011-2019"] = t4(*P11)
    t4r = res["T4 buyback windows 2020-2026"]
    res["T4 verdict"] = "pass" if t4r["open minus blackout (downside)"] < 0 and t4r["p (>= 0, quarter bootstrap)"] < 0.05 else "fail"
    res["today in blackout"] = bool(black[-1])
    # ---------- T5 ----------
    qw, me = calendar(idx)
    ev = e["AAPL"]
    e5 = ev[::-1].rolling(5).sum()[::-1].shift(-1)
    def t5(a, b, flag):
        m = win(a, b) & np.isfinite(ev).to_numpy() & np.isfinite(e5).to_numpy()
        x, y, q = ev.to_numpy()[m], e5.to_numpy()[m], flag[m].astype(float)
        coef = lambda ii: np.linalg.lstsq(np.column_stack([np.ones(len(ii)), x[ii], x[ii] * q[ii], q[ii]]), y[ii], rcond=None)[0][2]
        al = np.arange(len(x))
        obs = coef(al)
        bs = np.array([coef(blocks(len(x))) for _ in range(NB)])
        return {"d (extra give-back slope on flagged days)": float(obs), "p (d >= 0, block bootstrap)": float((bs >= 0).mean()),
                "slope other days": float(ols(x[q == 0], y[q == 0])[1]), "slope flagged days": float(ols(x[q == 1], y[q == 1])[1]),
                "mean |residual| % flagged / other": [float(100 * np.abs(x[q == 1]).mean()), float(100 * np.abs(x[q == 0]).mean())], "flagged days": int(q.sum())}
    res["T5 quad witching 2020-2026"] = t5(*P20, qw)
    res["T5 secondary: month end 2020-2026"] = t5(*P20, me)
    res["T5 contrast quad witching 2011-2019"] = t5(*P11, qw)
    t5r = res["T5 quad witching 2020-2026"]
    res["T5 verdict"] = "pass" if t5r["d (extra give-back slope on flagged days)"] < 0 and t5r["p (d >= 0, block bootstrap)"] < 0.05 else "fail"
    # ---------- current episode ----------
    m = win("2026-09-15", P20[1])
    F, E = f.to_numpy()[m], e["AAPL"].to_numpy()[m]
    b = ols(F, E)
    res["current episode Sep 15 - Oct 23"] = {
        "AAPL log return %": float(100 * np.nansum(r["AAPL"].to_numpy()[m])),
        "S&P ex-AAPL log return %": float(100 * np.nansum(rm["AAPL"].to_numpy()[m])), "SMH minus SPY log return %": float(100 * np.nansum(F)),
        "AAPL residual log return %": float(100 * np.nansum(E)), "residual loading on f": float(b[1]),
        "corr(residual, f)": float(np.corrcoef(F, E)[0, 1]), "AAPL 20d corr today": float(c20["AAPL"].iloc[-1]),
        "corr(S&P ex-AAPL, f) today": float(cmf.iloc[-1]), "AAPL alarm today": bool(alarm["AAPL"].iloc[-1])}
    res["verdicts"] = {k: res[f"{k} verdict"] for k in ("T1", "T2", "T3", "T4", "T5")}
    pd.DataFrame({"AAPL corr20": c20["AAPL"], "AAPL alarm": alarm["AAPL"], "AAPL residual": e["AAPL"], "f (SMH - SPY)": f,
                  "corr(S&P ex-AAPL, f)": cmf, "blackout": black, "earnings reaction": react.to_numpy(),
                  "AAPL close": S["AAPL"].close, "SPX close": spx.close, "SMH close": smh.close}).to_csv(OUT / "daily.csv")
    (OUT / "quirks.json").write_text(json.dumps(res, indent=1, default=float))
    return res


if __name__ == "__main__":
    print(json.dumps(main(*sys.argv[1:4]), indent=1, default=float))
