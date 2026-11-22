"""Stage 5 lead-lag lens: PCMCI (partial-correlation test) on weekly changes, lags 1-4 weeks, alpha 0.01, 1990-2019,
and separately 1990-2004 and 2005-2019 for stability. Only lagged links are reported (contemporaneous links are not causal direction)."""
import json
from pathlib import Path
import numpy as np, pandas as pd
from tigramite import data_processing as pp
from tigramite.pcmci import PCMCI
from tigramite.independence_tests.parcorr import ParCorr
from features import base_weekly, bond_ret

H = Path(__file__).resolve().parent
if __name__ == "__main__":
    B, _ = base_weekly()
    V = pd.DataFrame({"S&P": np.log(B.SPX).diff(), "VIX": B.VIX.diff(), "10y": B.US10Y.diff(), "Curve": B.CURVE.diff(),
                      "Credit spread": B.CREDIT.diff(), "Dollar": np.log(B.DXY).diff(), "Yen": -np.log(B.USDJPY).diff(),
                      "Oil": np.log(B.OIL).diff(), "Nikkei": np.log(B.NIKKEI).diff()})
    names = list(V.columns); out = {}
    for lab, (a, b) in {"1990-2019": ("1990-01-01", "2019-12-31"), "1990-2004": ("1990-01-01", "2004-12-31"), "2005-2019": ("2005-01-01", "2019-12-31")}.items():
        d = V.loc[a:b].dropna(); d = (d - d.mean()) / d.std()
        pc = PCMCI(dataframe=pp.DataFrame(d.values, var_names=names), cond_ind_test=ParCorr(), verbosity=0)
        r = pc.run_pcmci(tau_min=1, tau_max=4, pc_alpha=0.05, alpha_level=0.01)
        q = pc.get_corrected_pvalues(p_matrix=r["p_matrix"], fdr_method="fdr_bh")
        links = []
        for i in range(len(names)):
            for j in range(len(names)):
                for tau in range(1, 5):
                    if q[i, j, tau] < 0.01:
                        links.append({"from": names[i], "to": names[j], "lag_weeks": tau, "partial_corr": round(float(r["val_matrix"][i, j, tau]), 3), "q": float(q[i, j, tau])})
        links = sorted(links, key=lambda z: -abs(z["partial_corr"])); out[lab] = {"n_weeks": len(d), "links": links}
        print(f"\n== {lab} (n={len(d)} weeks): {len(links)} lagged links at FDR q < 0.01")
        for z in links: print(f"   {z['from']:>13s} → {z['to']:<13s} lag {z['lag_weeks']}w  partial r {z['partial_corr']:+.3f}")
    # stability: links found in both halves
    key = lambda z: (z["from"], z["to"], z["lag_weeks"])
    both = set(map(key, out["1990-2004"]["links"])) & set(map(key, out["2005-2019"]["links"]))
    print("\nlinks present in BOTH halves:", sorted(both)); out["in_both_halves"] = sorted(both)
    json.dump(out, open(H / "out" / "leadlag.json", "w"), indent=1)
