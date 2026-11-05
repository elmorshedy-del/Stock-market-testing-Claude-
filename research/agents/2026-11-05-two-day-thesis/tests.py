"""H1-H6 (pre-registered, see README). Usage: python tests.py <dl_dir> <label>   (label = preview | final)"""
import sys, json, numpy as np, pandas as pd, statsmodels.api as sm
from scipy import stats
dl, label = sys.argv[1], sys.argv[2]
from pathlib import Path
O = Path(__file__).resolve().parent / "out"; O.mkdir(exist_ok=True)
A = pd.read_parquet(f"{dl}/daily_adj.parquet").sort_index(); A = A[~A.index.duplicated(keep="last")]
cons = pd.read_csv(f"{dl}/sp500.csv"); cons["sym"] = cons.Symbol.str.replace(".", "-", regex=False); sec = cons.set_index("sym")["GICS Sector"]; sub = cons.set_index("sym")["GICS Sub-Industry"]
R = A.pct_change()
F = pd.DataFrame({"MKT": R.SPY, "AI": R.SMH - R.SPY, "OIL": R.USO, "RATE": R.TLT, "GOLD": R.GLD})
est = (R.index >= "2025-11-03") & (R.index <= "2026-10-30")
names = [s for s in A.columns if s in sec.index]
def px(s, d): x = A[s][A.index <= pd.Timestamp(d)].dropna(); return x.iloc[-1] if len(x) else np.nan
rows = {}
for s in names:
    y = R.loc[est, s]; X = F.loc[est]; ok = y.notna() & X.notna().all(axis=1)
    if ok.sum() < 150: continue
    b = sm.OLS(y[ok], sm.add_constant(X[ok])).fit().params
    rows[s] = {**{f"b_{k}": b[k] for k in F.columns}, "MOM": px(s, "2026-09-30") / px(s, "2025-10-31") - 1, "STR": px(s, "2026-10-30") / px(s, "2026-09-30") - 1,
               "D1": px(s, "2026-11-04") / px(s, "2026-11-03") - 1, "D2": px(s, "2026-11-05") / px(s, "2026-11-04") - 1, "sector": sec[s], "sub": sub[s]}
X = pd.DataFrame(rows).T
for c in X.columns:
    if c not in ("sector", "sub"): X[c] = X[c].astype(float)
X = X.dropna(subset=["D1", "D2", "MOM", "STR"])
w = lambda s: s.clip(s.quantile(0.01), s.quantile(0.99))
for c in ("D1", "D2", "MOM", "STR"): X[c + "_w"] = w(X[c])
Z = lambda s: (s - s.mean()) / s.std()
ex = {"MKT": Z(X.b_MKT), "AI": Z(X.b_AI), "OIL": Z(X.b_OIL), "RATE": Z(X.b_RATE), "GOLD": Z(X.b_GOLD), "MOM": Z(X.MOM_w), "STR": Z(X.STR_w)}
E = pd.DataFrame(ex)
MA = ["MKT", "AI", "OIL", "RATE", "GOLD"]; MB = MA + ["MOM", "STR"]
def fit(y, cols, idx=None, huber=False, demean=False):
    yy, XX = y.copy(), E[cols].copy()
    if idx is not None: yy, XX = yy[idx], XX[idx]
    if demean:
        g = X.loc[yy.index, "sector"]; yy = yy - yy.groupby(g).transform("mean"); XX = XX - XX.groupby(g).transform("mean")
    Xc = sm.add_constant(XX)
    m = sm.RLM(100 * yy, Xc, M=sm.robust.norms.HuberT()).fit() if huber else sm.OLS(100 * yy, Xc).fit(cov_type="HC3")
    return m
def one_sided(m, k, sign):  # sign -1: predict < 0
    t = m.tvalues[k]; return float(stats.norm.sf(-t) if sign < 0 else stats.norm.sf(t))
out = {"label": label, "n stocks": int(len(X)), "Day1": "2026-11-04", "Day2": "2026-11-05 (" + label + ")"}
for d in ("D1", "D2"):
    for nm, cols in (("A", MA), ("B", MB)):
        m = fit(X[d + "_w"], cols)
        out[f"{d} model {nm}"] = {"R2": round(m.rsquared, 3), "coef % per 1 SD (t)": {k: [round(float(m.params[k]), 2), round(float(m.tvalues[k]), 1)] for k in cols}}
mA1, mB1, mB2 = fit(X.D1_w, MA), fit(X.D1_w, MB), fit(X.D2_w, MB)
low = X.b_AI < X.b_AI.quantile(0.70); mB2low = fit(X.D2_w, MB, idx=low)
p = {"H1": max(one_sided(mA1, "AI", -1), one_sided(mA1, "OIL", -1), one_sided(mA1, "RATE", +1)),
     "H2": one_sided(mB1, "MOM", -1), "H3": one_sided(mB2low, "MOM", -1), "H4": one_sided(mB2, "MKT", -1)}
rA1 = fit(X.D1_w, MA).resid; rA2 = fit(X.D2_w, MA).resid
r5, p5 = stats.pearsonr(rA1, rA2); p["H5"] = float(p5 / 2 if r5 < 0 else 1 - p5 / 2)
out["H details"] = {"H1 Day1 A: AI, OIL, RATE (coef, t)": {k: [round(float(mA1.params[k]), 2), round(float(mA1.tvalues[k]), 1)] for k in ("AI", "OIL", "RATE")},
                    "H2 Day1 B: MOM": [round(float(mB1.params.MOM), 2), round(float(mB1.tvalues.MOM), 1)],
                    "H3 Day2 B, AI below 70th pct: MOM": [round(float(mB2low.params.MOM), 2), round(float(mB2low.tvalues.MOM), 1), int(low.sum())],
                    "H4 Day2 B: MKT": [round(float(mB2.params.MKT), 2), round(float(mB2.tvalues.MKT), 1)],
                    "H5 corr(resid D1, resid D2), Model A": [round(float(r5), 3), "spearman", round(float(stats.spearmanr(rA1, rA2)[0]), 3)]}
order = sorted(p, key=p.get); run = 0; out["Holm"] = {}
for i, k in enumerate(order): run = max(run, min(1, (len(p) - i) * p[k])); out["Holm"][k] = {"p": round(p[k], 5), "adj": round(run, 5), "PASS": bool(run < 0.05)}
rob = {}
for tag, kw in (("Huber", dict(huber=True)), ("sector-demeaned", dict(demean=True))):
    a1, b1, b2, b2l = fit(X.D1_w, MA, **kw), fit(X.D1_w, MB, **kw), fit(X.D2_w, MB, **kw), fit(X.D2_w, MB, idx=low, **kw)
    rob[tag] = {"H1 AI/OIL/RATE t": [round(float(a1.tvalues[k]), 1) for k in ("AI", "OIL", "RATE")], "H2 MOM t": round(float(b1.tvalues.MOM), 1),
                "H3 MOM t (low AI)": round(float(b2l.tvalues.MOM), 1), "H4 MKT t": round(float(b2.tvalues.MKT), 1)}
out["robustness"] = rob
# H6 timing
M5 = pd.read_parquet(f"{dl}/m5.parquet"); M5 = M5.reset_index(); M5 = M5[M5.ts.dt.date == pd.Timestamp("2026-11-05").date()]
M5 = M5[(M5.ts.dt.time >= pd.Timestamp("09:30").time()) & (M5.ts.dt.time < pd.Timestamp("16:00").time())]
tl = M5.loc[M5.groupby("sym").low.idxmin()].set_index("sym").ts; mins = ((tl.dt.hour * 60 + tl.dt.minute) - 570).rename("min_low")
X = X.join(mins); terc = pd.qcut(X.b_AI, 3, labels=["low AI", "mid AI", "high AI"]); X["AI_terc"] = terc
hi_, lo_ = X.loc[terc == "high AI", "min_low"].dropna(), X.loc[terc == "low AI", "min_low"].dropna()
u = stats.mannwhitneyu(hi_, lo_, alternative="less")
out["H6 time of Day-2 low (min after 09:30)"] = {"high AI median": float(hi_.median()), "low AI median": float(lo_.median()), "mid AI median": float(X.loc[terc == "mid AI", "min_low"].median()),
                                                "p (Mann-Whitney, high earlier)": float(u.pvalue), "n": [int(len(hi_)), int(len(lo_))], "last bar": str(M5.ts.max())}
# descriptives
out["corr raw D1,D2"] = round(float(stats.pearsonr(X.D1_w, X.D2_w)[0]), 3)
out["sector means %"] = (100 * X.groupby("sector")[["D1", "D2"]].mean()).round(2).sort_values("D1").to_dict(orient="index")
out["sector median time of low"] = X.groupby("sector").min_low.median().sort_values().to_dict()
grp = {"suppliers": ["NVDA", "AVGO", "AMD", "MU", "AMAT", "LRCX", "KLAC", "VRT", "ETN", "GEV", "VST", "CEG", "DELL", "SMCI", "ANET"], "spenders": ["MSFT", "AMZN", "GOOGL", "META", "AAPL"],
       "software AI winners": ["PLTR", "CRWD", "PANW", "ORCL", "NET", "DDOG", "APP"], "software AI losers": ["CRM", "ADBE", "NOW", "INTU", "WDAY"]}
out["groups %"] = {g: {s: [round(100 * X.loc[s, "D1"], 1), round(100 * X.loc[s, "D2"], 1), round(100 * X.loc[s, "MOM"], 0)] for s in L if s in X.index} for g, L in grp.items()}
X.to_csv(O / f"cross_section_{label}.csv")
json.dump(out, open(O / f"tests_{label}.json", "w"), indent=1, default=float)
print(json.dumps({k: v for k, v in out.items() if k not in ("sector means %", "groups %", "sector median time of low")}, indent=1, default=float))
print("sector means %:"); [print(f"  {k:24s} D1 {v['D1']:+.2f}  D2 {v['D2']:+.2f}") for k, v in out["sector means %"].items()]
print("sector median minute of Day-2 low:", {k: v for k, v in out["sector median time of low"].items()})
for g, v in out["groups %"].items(): print(g, v)
