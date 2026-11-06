"""Post-run checks (labelled, not pre-registered): (1) which shocks the E1<=0 rule dropped; (2) multiverse joint p with
permutations coupled across specifications (same random rank per index-date in every spec); (3) bootstrap CIs for the O4 decay exponents."""
import json, importlib.util, numpy as np, pandas as pd
from pathlib import Path
H = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("t", str(H / "test.py")); t = importlib.util.module_from_spec(spec); spec.loader.exec_module(t)
full = pd.read_pickle(H / "data" / "full.pkl"); d = full[full.complete & (full.cls != "mid")]; res = {}
drop = d[d.P.isna()]; res["(1) dropped by E1<=0, by class"] = drop.cls.value_counts().to_dict(); res["(1) dropped list"] = drop[["index", "date", "cls", "E1", "new leg"]].to_dict("records")
# (2) coupled multiverse: class from a random rank per (index, date), identical across specs
specs = [(m, s, w) for m in (5, 6, 8) for s in (21, 42) for w in (5, 10, 20)]; tabs = {sp: t.classes(pd.concat([t.table(nm, *sp) for nm in t.NAMES], ignore_index=True)) for sp in specs}
def cls_from(df, key):
    df = df.copy(); df["cls"] = "mid"
    for nm, g in df[df.complete].groupby("index"):
        q1, q2 = np.quantile(g[key], [1 / 3, 2 / 3]); df.loc[g.index[g[key] < q1], "cls"] = "abrupt"; df.loc[g.index[g[key] > q2], "cls"] = "build-up"
    return df
obs = {h: [] for h in ("H1", "H3")}
for sp in specs:
    dd = tabs[sp]; o = t.stats(dd[dd.complete & (dd.cls != "mid")]); [obs[h].append(o[h]) for h in obs]
K = 2000; rng = np.random.default_rng(77); keys = sorted({(r["index"], r["date"]) for sp in specs for _, r in tabs[sp].iterrows()}); null = {h: np.zeros((len(specs), K)) for h in obs}
for k in range(K):
    u = dict(zip(keys, rng.random(len(keys))))
    for si, sp in enumerate(specs):
        dd = tabs[sp].copy(); dd["U"] = [u[(a, b)] for a, b in zip(dd["index"], dd["date"])]; dd = cls_from(dd, "U"); o = t.stats(dd[dd.complete & (dd.cls != "mid")])
        for h in obs: null[h][si, k] = o[h]
z = {h: ((np.array(obs[h])[:, None] - null[h].mean(1, keepdims=True)) / null[h].std(1, keepdims=True)) for h in obs}
for h in obs:
    zo = np.mean((np.array(obs[h]) - null[h].mean(1)) / null[h].std(1)); zn = ((null[h] - null[h].mean(1, keepdims=True)) / null[h].std(1, keepdims=True)).mean(0)
    res[f"(2) coupled multiverse joint p {h} (mean z = {zo:.2f})"] = round(float((zn >= zo).mean()), 4)
    res[f"(2) specs positive {h}"] = f"{int((np.array(obs[h]) > 0).sum())} of {len(specs)}"
# (3) O4 bootstrap over shock dates
tt = np.arange(1, 61)
def alpha(g):
    if len(g) < 3: return np.nan
    cm = np.mean(np.vstack(g.cum.values), axis=0); ok = cm > 0
    return 1 - np.polyfit(np.log(tt[ok]), np.log(cm[ok]), 1)[0] if ok.sum() > 10 else np.nan
dates = d.date.unique(); di = d.set_index("date"); B = 4000; out = {}
groups = {"S&P": d["index"] == "S&P 500", "NDX+SOX": d["index"].isin(["Nasdaq-100", "SOX"])}
for gname, sel in groups.items():
    ga = d[sel]; obs_b, obs_a = alpha(ga[ga.cls == "build-up"]), alpha(ga[ga.cls == "abrupt"]); vals = []
    for _ in range(B):
        bb = di.loc[rng.choice(dates, len(dates))].reset_index(); bb = bb[bb["index"].isin(ga["index"].unique())]
        vals.append([alpha(bb[bb.cls == "build-up"]), alpha(bb[bb.cls == "abrupt"])])
    v = np.array(vals); gap = v[:, 1] - v[:, 0]
    out[gname] = {"alpha build-up": round(float(obs_b), 3), "alpha abrupt": round(float(obs_a), 3), "abrupt minus build-up": round(float(obs_a - obs_b), 3),
                  "90% CI of difference": [round(float(np.nanpercentile(gap, 5)), 3), round(float(np.nanpercentile(gap, 95)), 3)], "P(difference > 0)": round(float(np.nanmean(gap > 0)), 3)}
res["(3) O4 decay exponents, cluster bootstrap over dates"] = out
json.dump(res, open(H / "out" / "addendum.json", "w"), indent=1, default=str); print(json.dumps(res, indent=1, default=str))
