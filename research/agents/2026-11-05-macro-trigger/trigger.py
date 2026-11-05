"""Jobs/CPI release days after sharp drops in low gamma (pre-registered, see README). Usage: python trigger.py <DIX.csv>"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "2026-11-05-liquidity-cycle"))
from common import yahoo, gex_pct
O = Path(__file__).resolve().parent / "out"; rng = np.random.default_rng(11)
rd = pd.read_csv(O / "release_dates.csv", parse_dates=["date"]); rd["ym"] = rd.date.dt.to_period("M")
jobs = rd[rd.release == "jobs"].groupby("ym").date.min(); cpi = rd[rd.release == "cpi"].groupby("ym").date.max()
spx = yahoo("^GSPC", "2010-01-01").close; ndx = yahoo("^NDX", "2010-01-01").close
d = pd.DataFrame({"spx": spx, "ndx": ndx.reindex(spx.index)})
d["r"] = d.spx.pct_change(); d["rn"] = d.ndx.pct_change(); d["r5"] = d.spx.shift(-5) / d.spx.shift(1) - 1
d["dd10"] = d.spx / d.spx.rolling(10).max() - 1
g = gex_pct(sys.argv[1]); d["gp"] = g.gp.reindex(d.index)
d["DROP"] = d.dd10.shift(1) <= -0.03; d["LOWG"] = d.gp.shift(1) <= 0.30; d["SETUP"] = d.DROP & d.LOWG
d["jobs"] = d.index.isin(jobs.values); d["cpi"] = d.index.isin(cpi.values); d["rel"] = d.jobs | d.cpi
S = d[d.gp.shift(1).notna() & d.r.notna() & (d.index < "2026-11-05")].copy()
pct = lambda x: round(100 * float(x), 3)
def block(X):
    a, b = X[X.rel], X[~X.rel]
    return {"release n": int(len(a)), "release mean %": pct(a.r.mean()), "release share up": round(float((a.r > 0).mean()), 3),
            "non-release n": int(len(b)), "non-release mean %": pct(b.r.mean()), "non-release share up": round(float((b.r > 0).mean()), 3),
            "release |r| %": pct(a.r.abs().mean()), "non-release |r| %": pct(b.r.abs().mean()),
            "jobs n / mean % / up": [int(a.jobs.sum()), pct(a[a.jobs].r.mean()), round(float((a[a.jobs].r > 0).mean()), 3)] if a.jobs.any() else None,
            "cpi n / mean % / up": [int(a.cpi.sum()), pct(a[a.cpi].r.mean()), round(float((a[a.cpi].r > 0).mean()), 3)] if a.cpi.any() else None,
            "NDX release mean % / non": [pct(a.rn.mean()), pct(b.rn.mean())], "S&P t-1->t+5 release mean % / non": [pct(a.r5.mean()), pct(b.r5.mean())]}
def perm(X):
    lab = X.rel.values; r = X.r.values; obs = r[lab].mean() - r[~lab].mean()
    pr = np.array([(lambda s: r[s].mean() - r[~s].mean())(rng.permutation(lab)) for _ in range(10000)])
    return float(obs), float((pr >= obs).mean())
R = {"span": [str(S.index[0].date()), str(S.index[-1].date())], "all days": block(S)}
ps = {}
for h, c in (("H1", "SETUP"), ("H2", "DROP"), ("H3", "LOWG")):
    X = S[S[c]]; R[f"{h} {c}"] = block(X); obs, p = perm(X); R[f"{h} {c}"].update({"diff %": pct(obs), "p": p, "eligible (>=15 release days)": bool(X.rel.sum() >= 15)}); ps[h] = (p, X.rel.sum() >= 15)
order = sorted(ps, key=lambda k: ps[k][0]); run = 0; R["Holm"] = {}
for i, k in enumerate(order):
    run = max(run, min(1, (len(ps) - i) * ps[k][0])); R["Holm"][k] = {"adj": round(run, 4), "PASS": bool(run < 0.05 and ps[k][1])}
X = S[S.SETUP & S.rel]
R["SETUP release days"] = {str(t.date()): {"what": "jobs" if r.jobs else "cpi", "S&P %": pct(r.r), "NDX %": pct(r.rn), "S&P t-1->t+5 %": pct(r.r5), "dd10 prior %": pct(d.dd10.shift(1)[t]), "GEX pct prior": round(float(d.gp.shift(1)[t]), 3)} for t, r in X.iterrows()}
t = d.index[-1]
R["TODAY (live)"] = {"date": str(t.date()), "S&P dd from 10d high %": pct(d.dd10.iloc[-1]), "DROP at today's close (live)": bool(d.dd10.iloc[-1] <= -0.03),
                     "last GEX date": str(g.index[-1].date()), "last GEX pct": round(float(g.gp.iloc[-1]), 3), "LOWG on last GEX": bool(g.gp.iloc[-1] <= 0.30)}
json.dump(R, open(O / "trigger.json", "w"), indent=1, default=float); print(json.dumps(R, indent=1, default=float))
