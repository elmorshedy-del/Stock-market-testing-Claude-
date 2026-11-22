import json, sys
import numpy as np, pandas as pd
import onset as O
W = O.build(); W.to_csv(O.H / "out" / "weekly.csv")
for tg in ("C10", "C7"):
    nh = W[W.near_high & W[tg].notna()]; eps = O.episodes(nh, tg)
    print(f"{tg}: near-high weeks {len(nh)}, event weeks {int(nh[tg].sum())} (base {nh[tg].mean():.1%}), episodes {len(eps)}:", [f"{g[0].date()}→{g[-1].date()}" for g in eps])
R = O.lens1(W); R.to_csv(O.H / "out" / "lens1.csv", index=False)
print(R[["target", "name", "auc", "p", "bh_ok", "episodes_agree", "hindsight"]].head(10).round(3).to_string(index=False))
res = {"lens1": R.to_dict("records")}
for tg in ("C10", "C7"):
    passed = list(R[(R.target == tg) & R.bh_ok]["var"])
    for scheme in ("loyo", "walk"):
        r, df = O.lens2(W, tg, passed, scheme); nul = O.lens2_null(W, tg, passed, scheme, n=int(sys.argv[1]) if len(sys.argv) > 1 else 200)
        r.update({"vars_rule": passed or "top-4 in fold (weak)", "null_auc_p95": float(np.quantile(nul, 0.95)), "p_vs_null": float((1 + np.sum(nul >= r["auc"])) / (1 + len(nul)))})
        res[f"{tg}_{scheme}"] = r; df.to_csv(O.H / "out" / f"lens2_{tg}_{scheme}.csv", index=False)
        print(f"{tg} {scheme}: {r}")
json.dump(res, open(O.H / "out" / "results.json", "w"), indent=1, default=str)
