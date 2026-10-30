"""Family E (pre-registered @ e2971b7): gap-ups >= 0.5 sigma in the 3 sessions after a stock-run end; open -> close (sigma) in the footprint's
transitory tercile vs the rest, for each panel footprint that passed (others reported as descriptive). Month-cluster bootstrap; Holm across passing ones.
Also: Sept 2, 2020 and the current state. Usage: python exit_days.py <scratchpad> -> out/exit_days.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

S = Path(sys.argv[1]); HERE = Path(__file__).resolve().parent; CX = S / "ctx"
rng = np.random.default_rng(0); B = 10000
R = json.load(open(HERE / "out" / "runs.json"))["tests"]
EV = pd.read_csv(HERE / "out" / "stock_runs.csv", parse_dates=["date"])


def load(p):
    r = json.load(open(p))["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    d = pd.DataFrame({k: q[k] for k in ("open", "close", "volume")}, index=pd.to_datetime(r["timestamp"], unit="s").normalize())
    return d[~d.index.duplicated(keep="last")].dropna()


rows = []
for s, g in EV.groupby("sym"):
    d = load(S / "long" / f"{s}.json"); d = d[d.close > 0]; lr = np.log(d.close).diff(); sig = lr.rolling(20).std().shift(1)
    gap = d.open / d.close.shift(1) - 1; idx = d.index
    for r in g.itertuples():
        if r.date not in idx: continue
        i = idx.get_loc(r.date)
        for j in range(i + 1, min(i + 4, len(idx))):
            if gap.iloc[j] / sig.iloc[j] >= 0.5:
                rows.append({"sym": s, "run_end": r.date, "date": idx[j], "oc_sig": (d.close.iloc[j] / d.open.iloc[j] - 1) / sig.iloc[j], "oc_pct": 100 * (d.close.iloc[j] / d.open.iloc[j] - 1),
                             "X1_abvol": r.X1_abvol, "X2_amihud": r.X2_amihud, "X3_overnight": r.X3_overnight}); break
G = pd.DataFrame(rows)


def contrast(D, x):
    D = D[D[x].notna()].copy(); D["top"] = (D.groupby("sym")[x].rank(pct=True) > 2 / 3).astype(int); D["yd"] = D.oc_sig - D.groupby("sym").oc_sig.transform("mean")
    est = D[D.top == 1].yd.mean() - D[D.top == 0].yd.mean(); D["m"] = D.date.dt.to_period("M"); ms = D.m.unique(); idx = {m: np.flatnonzero(D.m.to_numpy() == m) for m in ms}
    yd, t = D.yd.to_numpy(), D.top.to_numpy(); bs = np.empty(B)
    for k in range(B):
        j = np.concatenate([idx[m] for m in rng.choice(ms, len(ms))]); bs[k] = yd[j][t[j] == 1].mean() - yd[j][t[j] == 0].mean()
    return {"n_top": int(D.top.sum()), "n_rest": int((D.top == 0).sum()), "est_sigma": float(est), "ci95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
            "p": float(min(1, 2 * min((bs <= 0).mean(), (bs >= 0).mean()) + 1 / B)), "median_oc_pct_top": float(D[D.top == 1].oc_pct.median()), "median_oc_pct_rest": float(D[D.top == 0].oc_pct.median())}


names = {"X1_abvol": "X1 abnormal volume during the run", "X2_amihud": "X2 thinning liquidity (Amihud ratio)", "X3_overnight": "X3 overnight share of the run"}
passing = [x for x, nm in names.items() if R[nm]["pass"]]
fam = {x: contrast(G, x) for x in passing}
if fam:
    ps = [v["p"] for v in fam.values()]; o = np.argsort(ps); run = 0; adj = np.empty(len(ps))
    for j, k in enumerate(o): run = max(run, (len(ps) - j) * ps[k]); adj[k] = min(1, run)
    for (k, v), h in zip(fam.items(), adj): v["p_holm"] = float(h); v["pass"] = bool(h < 0.05 and v["est_sigma"] < 0)
desc = {x: contrast(G, x) for x in names if x not in passing}
json.dump({"n_gap_days": len(G), "family_E": fam, "descriptive_not_passing": desc}, open(HERE / "out" / "exit_days.json", "w"), indent=1, default=float)
print("gap days after run ends:", len(G)); print("family E:", json.dumps(fam, indent=1, default=float)); print("descriptive:", json.dumps(desc, indent=1, default=float))
