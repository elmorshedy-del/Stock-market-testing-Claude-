"""Amendment 2 (pre-registered at b218820): R3a AAPL run into earnings (significance, years, fiscal quarters), R3b vs peers on their own calendars,
R3c where in the window. Usage: python round3.py <long folder> <quirks folder>  -> out/round3.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import quirks as Q

NB = 2000
RNG = np.random.default_rng(20261030)
P20, P11 = Q.P20, Q.P11
ann = lambda x: float(252 * 100 * x)


def blocks(n, L=20):
    st = RNG.integers(0, n - L, int(np.ceil(n / L)))
    return np.concatenate([np.arange(s, s + L) for s in st])[:n]


def fqe_for(s, years):
    out = []
    for y in years:
        if s == "AAPL":
            return Q.fiscal_quarter_ends(years)
        if s == "NVDA":
            for m in (1, 4, 7, 10):
                last = pd.Timestamp(y, m, 1) + pd.offsets.MonthEnd(0)
                out.append(last - pd.Timedelta(days=(last.weekday() - 6) % 7))
        else:
            out += [pd.Timestamp(y, m, 1) + pd.offsets.MonthEnd(0) for m in (3, 6, 9, 12)]
    return sorted(out)


def windows(s, idx, ed):
    fqe = fqe_for(s, range(2009, 2027))
    black, qid, before, ftype = np.zeros(len(idx), bool), np.full(len(idx), -1), np.zeros(len(idx), bool), np.full(len(idx), -1)
    for k, q in enumerate(fqe):
        if q - pd.Timedelta(days=14) > idx[-1]:
            continue
        nxt = ed[ed > q]
        w = (idx >= q - pd.Timedelta(days=14)) & (idx <= (nxt[0] if len(nxt) else idx[-1]))
        black |= w
        before |= w & (idx <= q)
        ftype[w] = q.month
        qid[(idx > q - pd.Timedelta(days=14)) & (idx <= (fqe[k + 1] - pd.Timedelta(days=14) if k + 1 < len(fqe) else idx[-1]))] = k
    return black, qid, before, ftype


def main(long, qf):
    spx = Q.load(Path(long) / "GSPC.json")
    spx = spx[spx.index >= "2009-01-01"]
    idx = spx.index
    rs = np.log(spx.close).diff()
    names = ["AAPL"] + Q.PEERS
    e, W_, react = {}, {}, {}
    for s in names:
        c = Q.load(Path(long) / f"{s}.json").reindex(idx).close
        r = np.log(c).diff()
        rm = (rs - Q.W[s] * r.fillna(0)) / (1 - Q.W[s])
        b = (r.rolling(252, min_periods=200).cov(rm) / rm.rolling(252, min_periods=200).var()).shift(1)
        e[s] = (r - b * rm).to_numpy()
        ed = Q.earnings_days(Path(qf) / f"earn_{s}.json", idx)
        react[s] = idx.isin(ed)
        W_[s] = windows(s, idx, ed)
    win = lambda a, b: (idx >= pd.Timestamp(a)) & (idx <= pd.Timestamp(b))
    res = {}
    black, qid, before, ftype = W_["AAPL"]
    def r3a(a, b):
        rows = np.nonzero(win(a, b) & np.isfinite(e["AAPL"]) & (qid >= 0) & ~react["AAPL"])[0]
        x = e["AAPL"]
        stat = lambda rr: x[rr][black[rr]].mean() - x[rr][~black[rr]].mean()
        obs = stat(rows)
        qs = np.unique(qid[rows])
        byq = {k: rows[qid[rows] == k] for k in qs}
        bs = np.array([stat(np.concatenate([byq[k] for k in RNG.choice(qs, len(qs))])) for _ in range(NB)])
        yrs = {int(y): ann(stat(rows[idx[rows].year == y])) for y in sorted(set(idx[rows].year))}
        openm = x[rows][~black[rows]].mean()
        fq = {f"FQE {m}": ann(x[rows][black[rows] & (ftype[rows] == m)].mean() - openm) for m in (12, 3, 6, 9)}
        return {"blackout residual (annualized %)": ann(x[rows][black[rows]].mean()), "open residual (annualized %)": ann(openm),
                "blackout minus open (annualized %)": ann(obs), "p (<= 0, quarter bootstrap)": float((bs <= 0).mean()),
                "by year": yrs, "years positive": int(sum(v > 0 for v in yrs.values())), "by fiscal quarter (blackout minus open)": fq,
                "quarters positive": int(sum(v > 0 for v in fq.values())),
                "R3c: before quarter end / quarter end to report / open (annualized %)": [ann(x[rows][black[rows] & before[rows]].mean()),
                                                                                          ann(x[rows][black[rows] & ~before[rows]].mean()), ann(openm)]}
    res["R3a AAPL 2020-2026 (earnings days excluded)"] = r3a(*P20)
    res["R3a contrast 2011-2019"] = r3a(*P11)
    ra = res["R3a AAPL 2020-2026 (earnings days excluded)"]
    res["R3a verdict"] = "pass" if (ra["blackout minus open (annualized %)"] > 0 and ra["p (<= 0, quarter bootstrap)"] < 0.05
                                    and ra["years positive"] >= 5 and ra["quarters positive"] >= 3) else "fail"
    def r3b(a, b):
        rows = np.nonzero(win(a, b) & np.all([np.isfinite(e[s]) for s in names], axis=0))[0]
        def st(s, rr):
            bl, rc = W_[s][0][rr], react[s][rr]
            x = e[s][rr]
            return x[bl & ~rc].mean() - x[~bl & ~rc].mean()
        per = {s: ann(st(s, rows)) for s in names}
        obs = st("AAPL", rows) - np.mean([st(s, rows) for s in Q.PEERS])
        bs = []
        for _ in range(NB):
            ii = rows[blocks(len(rows))]
            bs.append(st("AAPL", ii) - np.mean([st(s, ii) for s in Q.PEERS]))
        return {"blackout minus open per stock (annualized %)": per, "AAPL minus peer average (annualized %)": ann(obs),
                "p (<= 0, block bootstrap)": float((np.array(bs) <= 0).mean())}
    res["R3b vs peers 2020-2026"] = r3b(*P20)
    res["R3b contrast 2013-2019"] = r3b("2013-01-02", P11[1])
    rb = res["R3b vs peers 2020-2026"]
    res["R3b verdict"] = "pass" if rb["AAPL minus peer average (annualized %)"] > 0 and rb["p (<= 0, block bootstrap)"] < 0.05 else "fail"
    m = win("2026-09-12", P20[1])
    res["current blackout so far (Sep 12 - Oct 23)"] = {"AAPL residual sum %": float(100 * np.nansum(e["AAPL"][m])), "sessions": int(m.sum())}
    res["R3d live check"] = "pending: AAPL residual summed Oct 26 - Nov 2, 2026; predicted > 0"
    res["verdicts"] = {"R3a": res["R3a verdict"], "R3b": res["R3b verdict"]}
    (Q.OUT / "round3.json").write_text(json.dumps(res, indent=1, default=float))
    return res


if __name__ == "__main__":
    print(json.dumps(main(*sys.argv[1:3]), indent=1, default=float))
