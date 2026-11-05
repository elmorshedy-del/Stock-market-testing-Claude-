"""Amendment A1 tests B1-B3 (pre-registered, see README). Usage: python a1.py <dl_dir> <label>"""
import sys, json, importlib.util, numpy as np, pandas as pd, statsmodels.api as sm
from pathlib import Path
from scipy import stats
dl, label = sys.argv[1], sys.argv[2]; H = Path(__file__).resolve().parent; O = H / "out"; rng = np.random.default_rng(3)
spec = importlib.util.spec_from_file_location("lc", str(H.parent / "2026-11-05-liquidity-cycle" / "common.py")); lc = importlib.util.module_from_spec(spec); spec.loader.exec_module(lc)
A = pd.read_parquet(f"{dl}/daily_adj.parquet").sort_index(); A = A[~A.index.duplicated(keep="last")]; R = A.pct_change()
X = pd.read_csv(O / f"cross_section_{label}.csv", index_col=0)
out = {"label": label}
est = (R.index >= "2025-11-03") & (R.index <= "2026-10-30"); days = {"Day1": pd.Timestamp("2026-11-04"), "Day2": pd.Timestamp("2026-11-05")}
rest_names = X.index[X.b_AI < X.b_AI.quantile(0.70)]; ai_names = X.index[X.b_AI >= X.b_AI.quantile(0.90)]
EW_rest = R[rest_names].mean(axis=1)
for tag, y in (("RSP", R.RSP), ("EW S&P stocks with AI exposure < 70th pct", EW_rest)):
    Xf = R[["SMH", "USO", "TLT", "GLD"]]; ok = est & y.notna() & Xf.notna().all(axis=1)
    m = sm.OLS(y[ok], sm.add_constant(Xf[ok])).fit(); sd = float(np.std(m.resid, ddof=5))
    res = {"betas": {k: round(float(v), 3) for k, v in m.params.items()}, "R2": round(m.rsquared, 3), "resid sd %": round(100 * sd, 3)}
    for dn, d in days.items():
        pred = float(m.predict(sm.add_constant(Xf, has_constant="add").loc[[d]]).iloc[0]); act = float(y.loc[d])
        res[dn] = {"actual %": round(100 * act, 2), "predicted %": round(100 * pred, 2), "residual %": round(100 * (act - pred), 2), "z": round((act - pred) / sd, 2),
                   "factor moves %": {k: round(100 * float(Xf.loc[d, k]), 2) for k in Xf.columns}}
    out[f"B1 {tag}"] = res
# B2 intraday lead-lag on Day 2
M5 = pd.read_parquet(f"{dl}/m5.parquet").reset_index(); M5 = M5[M5.ts.dt.date == days["Day2"].date()]
M5 = M5[(M5.ts.dt.time >= pd.Timestamp("09:30").time()) & (M5.ts.dt.time < pd.Timestamp("16:00").time())]
C = M5.pivot_table(index="ts", columns="sym", values="close"); O5 = M5.pivot_table(index="ts", columns="sym", values="open")
lr = np.log(C).diff(); lr.iloc[0] = np.log(C.iloc[0] / O5.iloc[0])
ai = lr[[s for s in ai_names if s in lr]].mean(axis=1); rs = lr[[s for s in rest_names if s in lr]].mean(axis=1)
def L(a, b):
    f = lambda x, y, k: np.corrcoef(x[:-k], y[k:])[0, 1]
    return sum(f(a, b, k) for k in (1, 2, 3)) - sum(f(b, a, k) for k in (1, 2, 3))
a_, b_ = ai.values, rs.values; Lobs = L(a_, b_); n = len(a_); B = []
for _ in range(2000):
    idx = np.concatenate([np.arange(s, min(s + 6, n)) for s in rng.integers(0, n - 6, n // 6 + 1)])[:n]; B.append(L(a_[idx], b_[idx]))
cum_ai, cum_rs = ai.cumsum(), rs.cumsum()
def half(c): lo = c.min(); return str(c.index[np.argmax((c <= lo / 2).values)].strftime("%H:%M")), str(c.idxmin().strftime("%H:%M")), round(100 * float(lo), 2)
out["B2 Day-2 lead-lag (5-min, EW)"] = {"L (AI leads rest > 0)": round(float(Lobs), 3), "bootstrap 90% CI": [round(float(np.percentile(B, 5)), 3), round(float(np.percentile(B, 95)), 3)],
    "corr lag0": round(float(np.corrcoef(a_, b_)[0, 1]), 3), "n bars": int(n), "n AI / rest": [int(len(ai_names)), int(len(rest_names))],
    "AI decile: half-decline at, low at, low %": half(cum_ai), "rest: half-decline at, low at, low %": half(cum_rs),
    "cum % at 10:00 / 10:50 / 12:00 / 13:00 / last": {g: [round(100 * float(c[c.index.strftime("%H:%M") <= t].iloc[-1]), 2) for t in ("10:00", "10:50", "12:00", "13:00", "23:59")] for g, c in (("AI", cum_ai), ("rest", cum_rs))}}
pd.DataFrame({"AI_cum": cum_ai, "rest_cum": cum_rs}).to_csv(O / f"intraday_paths_{label}.csv")
# B3 rotation-day history
smh = lc.yahoo("SMH", "2003-05-01").close; rsp = lc.yahoo("RSP", "2003-05-01").close
h = pd.DataFrame({"smh": smh.pct_change(), "rsp": rsp.pct_change(), "rsp_c": rsp}).dropna()
h["n1"] = h.rsp_c.shift(-1) / h.rsp_c - 1; h["n3"] = h.rsp_c.shift(-3) / h.rsp_c - 1
rot = h[(h.smh - h.rsp <= -0.03) & (h.rsp >= 0.01) & (h.index < "2026-11-04")]
out["B3 rotation days (SMH-RSP <= -3%, RSP >= +1%), since 2003"] = {"n": int(len(rot)), "next-day RSP share negative": round(float((rot.n1 < 0).mean()), 3), "base share negative": round(float((h.n1 < 0).mean()), 3),
    "next-day RSP mean %": round(100 * float(rot.n1.mean()), 2), "next-3-day share negative": round(float((rot.n3 < 0).mean()), 3), "base 3-day share negative": round(float((h.n3 < 0).mean()), 3),
    "days": {str(d.date()): [round(100 * r.smh, 1), round(100 * r.rsp, 1), round(100 * r.n1, 1), round(100 * r.n3, 1)] for d, r in rot.iterrows()}}
json.dump(out, open(O / f"a1_{label}.json", "w"), indent=1, default=float); print(json.dumps(out, indent=1, default=float))
