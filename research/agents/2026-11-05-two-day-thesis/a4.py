"""Amendment A4: war-shelter eviction (C1-C4). Usage: python a4.py <dl_dir> <label>"""
import sys, json, importlib.util, numpy as np, pandas as pd, statsmodels.api as sm
from pathlib import Path
from scipy import stats
dl, label = sys.argv[1], sys.argv[2]; H = Path(__file__).resolve().parent; O = H / "out"
spec = importlib.util.spec_from_file_location("lc", str(H.parent / "2026-11-05-liquidity-cycle" / "common.py")); lc = importlib.util.module_from_spec(spec); spec.loader.exec_module(lc)
px = pd.DataFrame({s: lc.yahoo(s, "2025-01-01").close for s in ("RSP", "SMH", "USO", "SPY")}).dropna(); r = px.pct_change().dropna(); r["spread"] = r.SMH - r.RSP
out = {"label": label}
pre = r[(r.index >= "2025-06-02") & (r.index <= "2026-02-27")]; war = r[(r.index >= "2026-03-02") & (r.index <= "2026-10-30")]
c_pre, c_war = stats.pearsonr(pre.USO, pre.spread)[0], stats.pearsonr(war.USO, war.spread)[0]
zf = (np.arctanh(c_war) - np.arctanh(c_pre)) / np.sqrt(1 / (len(war) - 3) + 1 / (len(pre) - 3))
out["C1 corr(USO, SMH-RSP)"] = {"pre-war": round(float(c_pre), 3), "n pre": int(len(pre)), "war": round(float(c_war), 3), "n war": int(len(war)),
    "p war > 0": float(stats.pearsonr(war.USO, war.spread)[1] / 2 if c_war > 0 else 1), "Fisher z (war > pre)": round(float(zf), 2), "p": float(stats.norm.sf(zf))}
m = sm.OLS(war.spread, sm.add_constant(war.USO)).fit(cov_type="HC3")
out["C3/C4 war-period spread on USO"] = {"beta": round(float(m.params.USO), 3), "t": round(float(m.tvalues.USO), 2), "R2": round(float(m.rsquared), 3)}
for d in ("2026-11-02", "2026-11-04", "2026-11-05"):
    t = pd.Timestamp(d)
    if t in r.index:
        pred = float(m.params.const + m.params.USO * r.USO.loc[t]); act = float(r.spread.loc[t])
        out["C3/C4 war-period spread on USO"][d] = {"oil %": round(100 * float(r.USO.loc[t]), 2), "actual spread %": round(100 * act, 2), "oil-predicted spread %": round(100 * pred, 2), "share explained": round(pred / act, 2) if act else None}
peace = war[war.USO <= -0.04]
out["war-period peace days (USO <= -4%)"] = {"n": int(len(peace)), "mean spread %": round(100 * float(peace.spread.mean()), 2), "share spread<0": round(float((peace.spread < 0).mean()), 3), "mean RSP %": round(100 * float(peace.RSP.mean()), 2),
    "days": {str(d.date()): [round(100 * x.USO, 1), round(100 * x.SMH, 1), round(100 * x.RSP, 1)] for d, x in peace.iterrows()}}
# C2: Monday Nov 2 cross-section with the same exposures
X = pd.read_csv(O / f"cross_section_{label}.csv", index_col=0); A = pd.read_parquet(f"{dl}/daily_adj.parquet").sort_index(); A = A[~A.index.duplicated(keep="last")]
pxa = lambda s, d: A[s][A.index <= pd.Timestamp(d)].dropna().iloc[-1]
X["MON"] = [pxa(s, "2026-11-02") / pxa(s, "2026-10-30") - 1 for s in X.index]; X["TUE"] = [pxa(s, "2026-11-03") / pxa(s, "2026-11-02") - 1 for s in X.index]
Z = lambda s: (s - s.mean()) / s.std(); w = lambda s: s.clip(s.quantile(0.01), s.quantile(0.99))
E = pd.DataFrame({"MKT": Z(X.b_MKT), "AI": Z(X.b_AI), "OIL": Z(X.b_OIL), "RATE": Z(X.b_RATE), "GOLD": Z(X.b_GOLD)})
for nm, col in (("Mon Nov 2", "MON"), ("Tue Nov 3 (election day)", "TUE"), ("Wed Nov 4 (Day 1)", "D1"), ("Thu Nov 5 (Day 2)", "D2")):
    mm = sm.OLS(100 * w(X[col]), sm.add_constant(E)).fit(cov_type="HC3")
    out[f"C2 cross-section {nm}"] = {"R2": round(float(mm.rsquared), 3), **{k: [round(float(mm.params[k]), 2), round(float(mm.tvalues[k]), 1)] for k in E.columns}}
c = np.corrcoef(w(X.MON), w(X.D1))[0, 1]; out["corr of stock returns Mon vs Day 1"] = round(float(c), 3); out["corr Mon vs Day 2"] = round(float(np.corrcoef(w(X.MON), w(X.D2))[0, 1]), 3)
json.dump(out, open(O / f"a4_{label}.json", "w"), indent=1, default=float); print(json.dumps(out, indent=1, default=float))
