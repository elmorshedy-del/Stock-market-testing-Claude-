"""Amendment 2 (pre-registered at bcd499a): R3a robustness of the transitory-impact law in single names,
R3b generalization to calendar forced-flow days on the S&P.
Usage: python round3.py <GSPC_max.json>  -> out/r3a.json, out/r3b.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import followup as F
import test_a as A
import test_bcd as B

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
RNG = np.random.default_rng(20261026)


def r3a():
    D = F.f1_frame("names")
    res = {}
    for lab, m in (("2020-2022", D.index < "2023-01-01"), ("2023-2026", D.index >= "2023-01-01")):
        X = D[m]
        bs = A.block_boot(X, lambda Z: F.fit(Z)[2], "sym")
        res[f"b2 {lab}"] = {"b2": float(F.fit(X)[2]), "p (b2 <= 0)": float((bs <= 0).mean()), "days": int(len(X))}
    res["b2 per ticker"] = {s: float(F.fit(D[D.sym == s])[2]) for s in A.TICKERS}
    lo, hi = D.p < 0.5, D.p >= 0.5
    gap = lambda Z: A.slope(Z.x[Z.p < 0.5], Z.c10[Z.p < 0.5]) - A.slope(Z.x[Z.p >= 0.5], Z.c10[Z.p >= 0.5])
    Dn = D.dropna(subset=["c10"])
    bs = A.block_boot(Dn, gap, "sym")
    res["day-10 gap (low - high gamma)"] = {"gap": float(gap(Dn)), "p (gap >= 0)": float((bs >= 0).mean()),
                                            "ci95": [float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))]}
    checks = [all(v["b2"] > 0 and v["p (b2 <= 0)"] < 0.10 for k, v in res.items() if k.startswith("b2 20")),
              sum(v > 0 for v in res["b2 per ticker"].values()) >= 5,
              res["day-10 gap (low - high gamma)"]["p (gap >= 0)"] < 0.05]
    res["checks (halves, tickers, day-10 gap)"] = checks
    res["verdict"] = "robust" if all(checks) else "not robust"
    return res


def forced_days(idx):
    s = pd.Series(idx, index=idx)
    month = pd.Series(idx.month, index=idx)
    last = month.ne(month.shift(-1)).to_numpy()
    quad, russell = np.zeros(len(idx), bool), np.zeros(len(idx), bool)
    for y in sorted(set(idx.year)):
        for m in (3, 6, 9, 12):
            fr = pd.date_range(f"{y}-{m:02d}-01", periods=31, freq="D")
            fr = fr[(fr.month == m) & (fr.weekday == 4)]
            if len(fr) >= 3:
                c = idx[idx <= fr[2]]
                if len(c) and (fr[2] - c[-1]).days <= 1:
                    quad[idx.get_loc(c[-1])] = True
        fr = pd.date_range(f"{y}-06-01", f"{y}-06-30", freq="D")
        fr = fr[fr.weekday == 4]
        c = idx[idx <= fr[-1]]
        if len(c) and (fr[-1] - c[-1]).days <= 1 and c[-1].month == 6:
            russell[idx.get_loc(c[-1])] = True
    return {"quad witching": quad, "month end": last, "Russell reconstitution": russell}


def r3b(c):
    c = c[c.index >= "1989-01-01"]
    r = np.log(c).diff()
    sd = r.rolling(20).std()
    D = pd.DataFrame({"x": r / sd.shift(1)})
    for h in (5, 10):
        D[f"c{h}"] = r[::-1].rolling(h).sum()[::-1].shift(-1) / sd.shift(1)
    fd = forced_days(c.index)
    for k, v in fd.items():
        D[k] = v.astype(float)
    D["F"] = np.clip(sum(D[k] for k in fd), 0, 1)
    D = D[D.index >= "1990-01-01"].dropna()
    def coef(Z, col="F", y="c5"):
        X = np.column_stack([np.ones(len(Z)), Z.x, Z.x * Z[col], Z[col]])
        return np.linalg.lstsq(X, Z[y].to_numpy(), rcond=None)[0][2]
    res = {"days": int(len(D)), "forced days": int(D.F.sum())}
    bs = A.block_boot(D, lambda Z: coef(Z))
    res["d (x * forced day), next 5 days"] = {"d": float(coef(D)), "p (d >= 0)": float((bs >= 0).mean()),
                                              "ci95": [float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))]}
    res["d next 10 days"] = float(coef(D, y="c10"))
    for k in fd:
        res[f"{k}: days, d (5d), d (10d)"] = [int(D[k].sum()), float(coef(D, k)), float(coef(D, k, "c10"))]
    res["slope of c5 on x, other days / forced days"] = [A.slope(D.x[D.F == 0], D.c5[D.F == 0]), A.slope(D.x[D.F == 1], D.c5[D.F == 1])]
    res["verdict"] = "pass" if (res["d (x * forced day), next 5 days"]["d"] < 0 and res["d (x * forced day), next 5 days"]["p (d >= 0)"] < 0.05) else "fail"
    return res


if __name__ == "__main__":
    c = B.gspc(sys.argv[1])
    for name, fn in (("r3a", r3a), ("r3b", lambda: r3b(c))):
        out = fn()
        (OUT / f"{name}.json").write_text(json.dumps(out, indent=1, default=float))
        print(name.upper(), json.dumps(out, indent=1, default=float))
