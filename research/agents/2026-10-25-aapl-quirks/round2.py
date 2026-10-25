"""Amendment 1 (pre-registered at 4f48a77): R2a overnight/intraday quirk, R2b buyback execution, R2c residual persistence, R2d stick or fade.
Usage: python round2.py <long folder> <quirks folder>  -> out/round2.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import quirks as Q

NB = 2000
RNG = np.random.default_rng(20261029)
P20, P11, P13 = Q.P20, Q.P11, ("2013-01-02", "2019-12-31")


def blocks(n, L=20):
    st = RNG.integers(0, n - L, int(np.ceil(n / L)))
    return np.concatenate([np.arange(s, s + L) for s in st])[:n]


def main(long, qf):
    spx = Q.load(Path(long) / "GSPC.json")
    spx = spx[spx.index >= "2009-01-01"]
    idx = spx.index
    rs = np.log(spx.close).diff()
    names = ["AAPL"] + Q.PEERS
    S = {s: Q.load(Path(long) / f"{s}.json").reindex(idx) for s in names}
    r = {s: np.log(S[s].close).diff() for s in names}
    g = {s: (np.log(S[s].close / S[s].open) - np.log(S[s].open / S[s].close.shift(1))).to_numpy() for s in names}   # intraday minus overnight
    rm = {s: (rs - Q.W[s] * r[s].fillna(0)) / (1 - Q.W[s]) for s in names}
    beta = {s: (r[s].rolling(252, min_periods=200).cov(rm[s]) / rm[s].rolling(252, min_periods=200).var()).shift(1) for s in names}
    e = {s: (r[s] - beta[s] * rm[s]).to_numpy() for s in names}
    win = lambda a, b: (idx >= pd.Timestamp(a)) & (idx <= pd.Timestamp(b))
    res = {}
    # R2a
    m20 = win(*P20) & np.all([np.isfinite(g[s]) for s in names], axis=0)
    rows20 = np.nonzero(m20)[0]
    A20, Pm = g["AAPL"][rows20], np.mean([g[s][rows20] for s in Q.PEERS], axis=0)
    rows11 = np.nonzero(win(*P11) & np.isfinite(g["AAPL"]))[0]
    A11 = g["AAPL"][rows11]
    d1 = A20.mean() - Pm.mean()
    d2 = A20.mean() - A11.mean()
    b1, b2 = [], []
    for _ in range(NB):
        ii, jj = blocks(len(rows20)), blocks(len(rows11))
        b1.append(A20[ii].mean() - Pm[ii].mean())
        b2.append(A20[ii].mean() - A11[jj].mean())
    ann = lambda x: float(252 * 100 * x)
    res["R2a intraday minus overnight (annualized, log %)"] = {
        "AAPL 2020-2026": ann(A20.mean()), "peer average 2020-2026": ann(Pm.mean()), "AAPL 2011-2019": ann(A11.mean()),
        "per peer 2020-2026": {s: ann(np.nanmean(g[s][rows20])) for s in Q.PEERS},
        "(i) AAPL minus peers": ann(d1), "p (i)": float((np.array(b1) <= 0).mean()),
        "(ii) AAPL 2020-26 minus 2011-19": ann(d2), "p (ii)": float((np.array(b2) <= 0).mean())}
    R = res["R2a intraday minus overnight (annualized, log %)"]
    res["R2a verdict"] = "pass" if d1 > 0 and R["p (i)"] < 0.05 and d2 > 0 and R["p (ii)"] < 0.05 else "fail"
    # R2b
    ed = Q.earnings_days(Path(qf) / "earn_AAPL.json", idx)
    fqe = Q.fiscal_quarter_ends(range(2009, 2027))
    black, qid = np.zeros(len(idx), bool), np.full(len(idx), -1)
    for k, q in enumerate(fqe):
        if q - pd.Timedelta(days=14) > idx[-1]:
            continue
        nxt = ed[ed > q]
        black |= (idx >= q - pd.Timedelta(days=14)) & (idx <= (nxt[0] if len(nxt) else idx[-1]))
        qid[(idx > q) & (idx <= (fqe[k + 1] if k + 1 < len(fqe) else idx[-1]))] = k
    def r2b(a, b):
        rows = np.nonzero(win(a, b) & np.isfinite(g["AAPL"]) & (qid >= 0))[0]
        stat = lambda rr: g["AAPL"][rr][~black[rr]].mean() - g["AAPL"][rr][black[rr]].mean()
        obs = stat(rows)
        qs = np.unique(qid[rows])
        byq = {k: rows[qid[rows] == k] for k in qs}
        bs = np.array([stat(np.concatenate([byq[k] for k in RNG.choice(qs, len(qs))])) for _ in range(NB)])
        on = lambda rr: np.log(S["AAPL"].open / S["AAPL"].close.shift(1)).to_numpy()[rr]
        it = lambda rr: np.log(S["AAPL"].close / S["AAPL"].open).to_numpy()[rr]
        o, k = rows[~black[rows]], rows[black[rows]]
        return {"open windows: intraday / overnight (annualized %)": [ann(np.nanmean(it(o))), ann(np.nanmean(on(o)))],
                "blackout: intraday / overnight (annualized %)": [ann(np.nanmean(it(k))), ann(np.nanmean(on(k)))],
                "open minus blackout (intraday - overnight, annualized %)": ann(obs), "p (<= 0, quarter bootstrap)": float((bs <= 0).mean())}
    res["R2b buyback execution 2020-2026"] = r2b(*P20)
    res["R2b contrast 2013-2019"] = r2b(*P13)
    rb = res["R2b buyback execution 2020-2026"]
    res["R2b verdict"] = "pass" if rb["open minus blackout (intraday - overnight, annualized %)"] > 0 and rb["p (<= 0, quarter bootstrap)"] < 0.05 else "fail"
    # R2c
    m = win(*P20) & np.all([np.isfinite(e[s]) for s in names], axis=0)
    rows = np.nonzero(m)[0]
    rows = rows[rows + 5 < len(idx)]
    def acsum(s, rr):
        x = e[s] - np.nanmean(e[s][rows])
        den = (x[rr] ** 2).sum()
        return sum(np.nansum(x[rr] * x[rr + k]) / den for k in range(1, 6))
    al = rows
    obs = acsum("AAPL", al) - np.mean([acsum(s, al) for s in Q.PEERS])
    bs = []
    for _ in range(NB):
        ii = rows[blocks(len(rows))]
        bs.append(acsum("AAPL", ii) - np.mean([acsum(s, ii) for s in Q.PEERS]))
    res["R2c residual autocorrelation, lags 1-5 summed, 2020-2026"] = {
        "AAPL": float(acsum("AAPL", al)), "peers": {s: float(acsum(s, al)) for s in Q.PEERS},
        "AAPL minus peer average": float(obs), "p (<= 0, block bootstrap)": float((np.array(bs) <= 0).mean())}
    rc = res["R2c residual autocorrelation, lags 1-5 summed, 2020-2026"]
    res["R2c verdict"] = "pass" if obs > 0 and rc["p (<= 0, block bootstrap)"] < 0.05 else "fail"
    # R2d
    def frame(s):
        r20 = pd.Series(e[s], index=idx).rolling(20).sum()
        sig = (Q.pct(r20) >= 0.9).to_numpy() & r20.notna().to_numpy()
        return r20, sig, r20.shift(-20).to_numpy()
    def r2d(stocks):
        F = [frame(s) for s in stocks]
        mm = win(*P20) & np.all([np.isfinite(o) for _, _, o in F], axis=0)
        rws = np.nonzero(mm)[0]
        def stat(rr):
            sig = np.concatenate([F[k][1][rr] for k in range(len(F))])
            out = np.concatenate([F[k][2][rr] for k in range(len(F))])
            return out[sig].mean() - out.mean(), out[sig].mean(), sig.sum()
        obs, mo, n = stat(rws)
        bs = np.array([stat(rws[blocks(len(rws))])[0] for _ in range(NB)])
        return {"signal days": int(n), "mean next-20d residual on signal days %": float(100 * mo), "minus all days %": float(100 * obs),
                "p (two-sided, block bootstrap)": float(2 * min((bs <= 0).mean(), (bs >= 0).mean()))}
    res["R2d AAPL after a top-tenth 20-day residual run-up"] = r2d(["AAPL"])
    res["R2d contrast: peers pooled"] = r2d(Q.PEERS)
    d = res["R2d AAPL after a top-tenth 20-day residual run-up"]
    res["R2d reading"] = ("neither" if d["p (two-sided, block bootstrap)"] >= 0.05 else "stick" if d["minus all days %"] > 0 else "fade")
    r20, sig, _ = frame("AAPL")
    res["today"] = {"AAPL 20-day residual %": float(100 * r20.iloc[-1]), "top-tenth signal on": bool(sig[-1]), "in blackout": bool(black[-1])}
    res["verdicts"] = {k: res[f"{k} verdict"] for k in ("R2a", "R2b", "R2c")} | {"R2d": res["R2d reading"]}
    (Q.OUT / "round2.json").write_text(json.dumps(res, indent=1, default=float))
    return res


ann = lambda x: float(252 * 100 * x)

if __name__ == "__main__":
    print(json.dumps(main(*sys.argv[1:3]), indent=1, default=float))
