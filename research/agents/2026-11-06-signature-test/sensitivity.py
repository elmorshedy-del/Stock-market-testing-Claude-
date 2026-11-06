"""Post-hoc sensitivity (labelled): keep the 13 abrupt shocks the E1<=0 rule dropped, ranked as the fastest fades (rank test)."""
import json, numpy as np, pandas as pd
from pathlib import Path
H = Path(__file__).resolve().parent; full = pd.read_pickle(H / "data" / "full.pkl"); d = full[full.complete & (full.cls != "mid")].copy()
d["Pr"] = d.P.fillna(-np.inf); rng = np.random.default_rng(5)
def stat(x):  # mean rank of build-up minus mean rank of abrupt, ranks within index (fastest fade = lowest)
    v = []
    for nm, g in x.groupby("index"):
        rk = g.Pr.rank(); v.append((rk[g.cls == "build-up"].mean() - rk[g.cls == "abrupt"].mean()) / len(g))
    return float(np.mean(v))
obs = stat(d); null = []
for _ in range(10000):
    p = d.copy()
    for nm, g in p.groupby("index"): p.loc[g.index, "cls"] = rng.permutation(g.cls.values)
    null.append(stat(p))
out = {"rank effect (build-up minus abrupt, scaled)": round(obs, 3), "one-sided permutation p": round(float((np.array(null) >= obs).mean()), 4),
       "share with sub-baseline volatility in days 1-20: build-up / abrupt": [f"{int(((d.cls=='build-up') & d.P.isna()).sum())}/{int((d.cls=='build-up').sum())}", f"{int(((d.cls=='abrupt') & d.P.isna()).sum())}/{int((d.cls=='abrupt').sum())}"]}
json.dump(out, open(H / "out" / "sensitivity.json", "w"), indent=1); print(json.dumps(out, indent=1))
