"""P2 secondary (pre-registered): SPY below the engine's flip (2020-2026) with 81-stock correlation; plus a post hoc split of the primary by period.
Usage: python p2_robust.py <long> <breadth> <etfs>  -> out/p2_robust.json"""
import json
import sys

import numpy as np
import pandas as pd

import p2_p3 as P

def corr_series(C):
    r = np.log(C).diff(); idx = C.index; vals = []
    for t_ in range(10, len(idx)):
        X = r.iloc[t_ - 9:t_ + 1].dropna(axis=1); cc = np.corrcoef(X.to_numpy().T); vals.append(cc[np.triu_indices_from(cc, 1)].mean())
    return pd.Series(np.r_[np.full(10, np.nan), vals], index=idx)


def main(long, bfold, etfs):
    Dz, Mo = P.Dz, __import__("momentum")
    spx = Dz.close(etfs, "%5EGSPC")
    names = Dz.PANEL + Mo.EXTRA
    C = pd.DataFrame({s: (Dz.close(long, s) if s in Dz.PANEL else Dz.close(bfold, s)) for s in names}).reindex(spx.index)
    C = C[C.index >= "2019-06-01"]
    corr = corr_series(C)
    d5 = corr.diff(5)
    rising = d5.rolling(252, min_periods=120).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True) >= 2 / 3
    eng = pd.read_csv(P.MICRO / "out" / "td_gamma_SPY.csv", parse_dates=["date"]).set_index("date")
    below = (eng.spot < eng.flip_classic).reindex(C.index)
    s = spx.reindex(C.index); r10 = np.log(s.shift(-10) / s)
    D = pd.DataFrame({"below": below, "rise": rising, "r10": r10}).loc["2020-06-01":"2026-09-25"].dropna()
    D["below"] = D.below.astype(bool); D["rise"] = D.rise.astype(bool)
    out = {"secondary 2020-2026 (SPY below flip, 81-stock corr)": {}}
    for g in (True, False):
        Z = D[D.below == g].reset_index(drop=True)
        o = Z.r10[Z.rise].mean() - Z.r10[~Z.rise].mean()
        bs = np.array([(lambda Q: Q.r10[Q.rise].mean() - Q.r10[~Q.rise].mean())(Z.iloc[P.blocks(len(Z))]) for _ in range(3000)])
        out["secondary 2020-2026 (SPY below flip, 81-stock corr)"][f"{'below' if g else 'above'} flip"] = {
            "days rising / not": [int(Z.rise.sum()), int((~Z.rise).sum())], "next 10d % rising / not": [float(100 * Z.r10[Z.rise].mean()), float(100 * Z.r10[~Z.rise].mean())],
            "difference %": float(100 * o), "p (diff >= 0)": float(np.nanmean(bs >= 0))}
    # post hoc: primary split by period
    spx2 = spx
    C41 = pd.DataFrame({s: Dz.close(long, s) for s in Dz.PANEL}).reindex(spx2.index); C41 = C41[C41.index >= "2009-06-01"]
    c41 = corr_series(C41); r41 = c41.diff(5).rolling(252, min_periods=120).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True) >= 2 / 3
    gex = pd.read_csv(f"{etfs}/DIX.csv", parse_dates=["date"]).set_index("date").gex; gex = gex[~gex.index.duplicated()].reindex(C41.index)
    s2 = spx2.reindex(C41.index); rr = np.log(s2.shift(-10) / s2)
    E = pd.DataFrame({"neg": gex < 0, "rise": r41, "r10": rr}).loc["2011-06-01":"2026-09-25"].dropna()
    E = E[gex.reindex(E.index).notna()]
    per = {}
    for lab, a, b in (("2011-2019", "2011", "2019-12-31"), ("2020-2022", "2020", "2022-12-31"), ("2023-2026", "2023", "2026-12-31")):
        Z = E[(E.index >= a) & (E.index <= b) & E.neg]
        per[lab] = {"GEX<0 days rising / not": [int(Z.rise.sum()), int((~Z.rise).sum())],
                    "next 10d % rising / not": [float(100 * Z.r10[Z.rise].mean()) if Z.rise.any() else None, float(100 * Z.r10[~Z.rise].mean()) if (~Z.rise).any() else None]}
    out["post hoc: primary by period"] = per
    ep = E[E.neg & E.rise]
    out["post hoc: GEX<0 & rising, distinct episodes (gap > 10 sessions)"] = int((np.diff(np.r_[-99, np.searchsorted(spx2.index, ep.index)]) > 10).sum())
    out["today (Oct 26, 81-stock corr)"] = {"corr": float(corr.iloc[-1]) if len(corr) else None, "rising": bool(rising.iloc[-1]) if len(rising) else None,
                                            "SPY below engine flip": True}
    (P.OUT / "p2_robust.json").write_text(json.dumps(out, indent=1, default=float))
    return out


if __name__ == "__main__":
    sys.path.insert(0, str(P.AG / "2026-10-25-momentum-reversal"))
    print(json.dumps(main(*sys.argv[1:4]), indent=1, default=float))
