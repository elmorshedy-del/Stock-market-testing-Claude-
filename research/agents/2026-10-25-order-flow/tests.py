"""Part 2 tests A1-A4 (pre-registered at 4bbbd47) on out/daily_flow.csv. Usage: python tests.py <etfs folder>  -> out/tests.json, out/panel.csv"""
import json
import sys

import numpy as np
import pandas as pd

import flows as Fl

RNG = np.random.default_rng(20261107)
NB = 4000


def z60(s):
    m, sd = s.shift(1).rolling(60, min_periods=20).mean(), s.shift(1).rolling(60, min_periods=20).std()
    return (s - m) / sd


def ols(X, y):
    X = np.column_stack([np.ones(len(y)), X])
    return np.linalg.lstsq(X, y, rcond=None)[0]


def blocks(n, L=20):
    st = RNG.integers(0, n - L, int(np.ceil(n / L)))
    return np.concatenate([np.arange(s, s + L) for s in st])[:n]


def build(etfs):
    D = pd.read_csv(Fl.OUT / "daily_flow.csv", index_col=0, parse_dates=True)
    spy = Fl.spy_close(etfs)
    D["r_am"] = np.log(D.s1200 / D.s0935)
    D["r_pm"] = np.log(D.s1559 / D.s1200)
    c = spy.reindex(D.index)
    lc = np.log(spy)
    D["r_day"] = lc.diff().reindex(D.index)
    D["r_next"] = lc.diff().shift(-1).reindex(D.index)
    D["zF_am"], D["zF_day"], D["zG_am"] = z60(D.F_am), z60(D.F_day), z60(D.G_am)
    D["absz"] = D.zF_am.abs()
    D["H"] = (D.absz >= D.absz.quantile(0.8)).astype(float)
    D["Gpos"] = (D.zG_am > 0).astype(float)
    D["r_am_H"], D["r_am_G"] = D.r_am * D.H, D.r_am * D.Gpos
    return D


def test(D, ycol, xcols, k, side):
    Z = D.dropna(subset=[ycol] + xcols)
    X, y = Z[xcols].to_numpy(float), Z[ycol].to_numpy(float)
    b = ols(X, y)[1 + k]
    bs = np.array([ols(X[ii], y[ii])[1 + k] for ii in (blocks(len(y)) for _ in range(NB))])
    p = {"pos": float((bs <= 0).mean()), "neg": float((bs >= 0).mean()), "two": float(2 * min((bs <= 0).mean(), (bs >= 0).mean()))}[side]
    yrs = {}
    for yv, g in Z.groupby(Z.index.year):
        yrs[int(yv)] = float(ols(g[xcols].to_numpy(float), g[ycol].to_numpy(float))[1 + k]) if len(g) > 30 else None
    want = {"pos": 1, "neg": -1, "two": np.sign(b)}[side]
    same = sum(1 for v in yrs.values() if v is not None and np.sign(v) == want)
    return {"coef": float(b), "p": p, "days": int(len(y)), "by year": yrs, "years same sign": same,
            "pass": bool(p < 0.05 and same >= 3 and (side == "two" or np.sign(b) == want))}


def main(etfs):
    D = build(etfs)
    res = {"days": int(D.dropna(subset=["zF_am"]).shape[0]), "dates": [str(D.index[0].date()), str(D.index[-1].date())]}
    res["A1 morning flow z -> morning return (bp per 1 z)"] = test(D, "r_am", ["zF_am"], 0, "pos")
    res["A2 morning flow z -> afternoon return (control: morning return)"] = test(D, "r_pm", ["zF_am", "r_am"], 0, "two")
    res["A3 day flow z -> next-day return (control: day return)"] = test(D, "r_next", ["zF_day", "r_day"], 0, "two")
    res["A4a flow-driven morning moves revert (r_am x top-quintile |flow z|)"] = test(D, "r_pm", ["r_am", "r_am_H", "H"], 1, "neg")
    res["A4b customer gamma buying -> continuation (r_am x gamma-flow z > 0)"] = test(D, "r_pm", ["r_am", "r_am_G", "Gpos"], 1, "pos")
    for k in list(res):
        if isinstance(res[k], dict) and "coef" in res[k] and "flow z ->" in k:
            res[k]["coef bp"] = 1e4 * res[k]["coef"]
    Z = D.dropna(subset=["zF_am", "r_am"])
    res["descriptive"] = {"corr(zF_am, r_am)": float(np.corrcoef(Z.zF_am, Z.r_am)[0, 1]),
                          "share of days customers net long delta (F_day > 0)": float((D.F_day > 0).mean()),
                          "corr(put signed am, r_am)": float(np.corrcoef(Z.put_signed_am, Z.r_am)[0, 1]),
                          "corr(call signed am, r_am)": float(np.corrcoef(Z.call_signed_am, Z.r_am)[0, 1])}
    D.to_csv(Fl.OUT / "panel.csv")
    (Fl.OUT / "tests.json").write_text(json.dumps(res, indent=1, default=float))
    return res


if __name__ == "__main__":
    print(json.dumps(main(sys.argv[1]), indent=1, default=float))
