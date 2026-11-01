"""Amendment 2 (pre-registered @ 1e41092): does Kimbal Musk sell TSLA near intermediate tops? Episodes vs random sessions
matched on calendar year and past-60-session return tercile; Elon Musk and other TSLA insiders as comparison groups.
Usage: python insider_tsla.py <sec parquet dir> <TSLA yahoo json> -> out/insider_tsla.json, out/kimbal_episodes.csv"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; rng = np.random.default_rng(23); TSLA = "0001318605"
KIMBAL, ELON = "0001494731", "0001494730"
r = json.load(open(sys.argv[2]))["chart"]["result"][0]
P = pd.Series(r["indicators"]["adjclose"][0]["adjclose"], index=pd.to_datetime(r["timestamp"], unit="s").normalize()).dropna()
P = P[~P.index.duplicated(keep="last")]; td = P.index; lp = np.log(P.to_numpy()); n = len(P)
pos_on_after = lambda d: int(td.searchsorted(d))                       # first session on/after d
pos_after = lambda d: int(td.searchsorted(d, side="right"))              # first session strictly after d
past60 = pd.Series(lp, index=td).diff(60); terc = pd.qcut(past60, 3, labels=False)
I = pd.concat([pd.read_parquet(f) for f in sorted(Path(sys.argv[1]).glob("*.parquet"))], ignore_index=True)
I = I[(I.ISSUERCIK == TSLA) & (I.TRANS_CODE == "S")].copy()
I["t"] = pd.to_datetime(I.tdate, format="%d-%b-%Y", errors="coerce"); I["f"] = pd.to_datetime(I.FILING_DATE, format="%d-%b-%Y", errors="coerce")
I = I.dropna(subset=["t", "f"]); I = I[I.t >= td[0]]


def episodes(D):
    D = D.sort_values("t"); out = []; cur = None
    for _, x in D.iterrows():
        pt = pos_on_after(x.t)
        if cur and pt - cur["last"] <= 10:
            cur["last"] = pt; cur["val"] += x.val if np.isfinite(x.val) else 0; continue
        if cur: out.append(cur)
        cur = {"t": x.t, "first_pos": pt, "last": pt, "act_pos": pos_after(x.f), "val": x.val if np.isfinite(x.val) else 0}
    if cur: out.append(cur)
    return out


def outcomes(i, a):
    o = {}
    if i + 60 < n and i >= 20:
        o["O1_20"], o["O1_60"] = lp[i + 20] - lp[i], lp[i + 60] - lp[i]
        o["O3a"] = float(P.iloc[i] >= 0.9 * P.iloc[i - 20:i + 61].max()); o["O3b"] = float(P.iloc[i + 1:i + 61].min() <= 0.8 * P.iloc[i])
    if a + 60 < n:
        o["O2_20"], o["O2_60"] = lp[a + 20] - lp[a], lp[a + 60] - lp[a]
    return o


def matched_pool(i):
    d = td[i]; t = terc.iloc[i]
    cand = np.nonzero((td.year == d.year) & (terc.to_numpy() == t))[0]
    return cand[(cand >= 20) & (cand + 60 < n)]


groups = {"Kimbal Musk": I[I.RPTOWNERCIK == KIMBAL], "Elon Musk": I[I.RPTOWNERCIK == ELON], "Other TSLA insiders": I[~I.RPTOWNERCIK.isin([KIMBAL, ELON])]}
res = {}
for g, D in groups.items():
    eps = []
    if g == "Other TSLA insiders":
        for _, Dd in D.groupby("RPTOWNERCIK"): eps += episodes(Dd)
    else:
        eps = episodes(D)
    rows = []
    for e in eps:
        o = outcomes(e["first_pos"], e["act_pos"]); o.update({"date": td[e["first_pos"]].date(), "value $m": round(e["val"] / 1e6, 1), "pos": e["first_pos"]}); rows.append(o)
    E = pd.DataFrame(rows)
    if g == "Kimbal Musk": E.drop(columns="pos").to_csv(HERE / "out" / "kimbal_episodes.csv", index=False)
    R = {"episodes": int(len(E)), "with 60 sessions of follow-up": int(E.O1_60.notna().sum()) if "O1_60" in E else 0}
    if R["with 60 sessions of follow-up"] == 0: res[g] = R; continue
    V = E.dropna(subset=["O1_60", "O2_60"]); pools = [matched_pool(int(p)) for p in V.pos]
    obs = {k: float(V[k].mean()) for k in ("O1_20", "O1_60", "O2_20", "O2_60", "O3a", "O3b")}
    sims = {k: [] for k in obs}
    for _ in range(10000):
        pick = [rng.choice(pl) for pl in pools]
        for k in obs:
            if k.startswith("O3a"): v = [float(P.iloc[i] >= 0.9 * P.iloc[i - 20:i + 61].max()) for i in pick]
            elif k.startswith("O3b"): v = [float(P.iloc[i + 1:i + 61].min() <= 0.8 * P.iloc[i]) for i in pick]
            else:
                h = int(k.split("_")[1]); v = [lp[i + h] - lp[i] for i in pick]   # matched days used for both O1 and O2
            sims[k].append(np.mean(v))
        if _ == 1999: break   # 2,000 draws is plenty for these sample sizes; stated in the README results
    for k in obs:
        s = np.array(sims[k])
        lower_is_hyp = not k.startswith("O3")
        p = float((s <= obs[k]).mean()) if lower_is_hyp else float((s >= obs[k]).mean())
        unit = 100
        R[k] = {"observed": round(unit * obs[k], 2), "matched random days": round(unit * s.mean(), 2), "p (one-sided, owner's hypothesis)": round(p, 4)}
    R["share of episodes followed by a 60-session decline (O1_60 < 0)"] = round(float((V.O1_60 < 0).mean()), 2)
    res[g] = R
res["_note"] = "O1/O2 in % log return; O3a = sold within 10% of the [-20,+60] peak (% of episodes); O3b = a 20% drop within 60 sessions (%). Null: 2,000 draws of matched random sessions (same year, same past-60 tercile)."
json.dump(res, open(HERE / "out" / "insider_tsla.json", "w"), indent=1, default=str)
print(json.dumps(res, indent=1, default=str))
