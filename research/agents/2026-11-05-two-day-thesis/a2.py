"""Amendment A2 tests B4, B5 + B2 fix (pre-registered, see README). Usage: python a2.py <dl_dir> <label>"""
import sys, json, time, random, importlib.util, requests, numpy as np, pandas as pd, statsmodels.api as sm
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
dl, label = sys.argv[1], sys.argv[2]; H = Path(__file__).resolve().parent; O = H / "out"; rng = np.random.default_rng(11)
spec = importlib.util.spec_from_file_location("lc", str(H.parent / "2026-11-05-liquidity-cycle" / "common.py")); lc = importlib.util.module_from_spec(spec); spec.loader.exec_module(lc)
out = {"label": label}; D1, D2 = pd.Timestamp("2026-11-04"), pd.Timestamp("2026-11-05")
# B4 piecewise tail model
px = pd.DataFrame({s: lc.yahoo(s, "2003-06-01").close for s in ("RSP", "SMH", "USO", "TLT", "GLD")}).dropna()
r = px.pct_change().dropna(); k = -0.04
r["SMH_up"] = r.SMH.where(r.SMH > k, k); r["SMH_tail"] = (r.SMH - k).where(r.SMH <= k, 0.0)  # continuous kink at -4%
def b4(start):
    w = r[(r.index >= start) & (r.index <= "2026-10-30")]; Xc = sm.add_constant(w[["SMH_up", "SMH_tail", "USO", "TLT", "GLD"]])
    m = sm.OLS(w.RSP, Xc).fit(cov_type="HC3"); sd = float(np.std(m.resid, ddof=6)); res = {"n": int(len(w)), "slope above -4%": round(float(m.params.SMH_up), 3), "extra slope below -4%": round(float(m.params.SMH_tail), 3),
        "t extra": round(float(m.tvalues.SMH_tail), 2), "n tail days": int((w.SMH <= k).sum()), "resid sd %": round(100 * sd, 3)}
    for nm, d in (("Day1", D1), ("Day2", D2)):
        if d in r.index:
            xr = sm.add_constant(r[["SMH_up", "SMH_tail", "USO", "TLT", "GLD"]], has_constant="add").loc[[d]]; pred = float(m.predict(xr).iloc[0]); act = float(r.RSP.loc[d])
            res[nm] = {"actual %": round(100 * act, 2), "predicted %": round(100 * pred, 2), "z": round((act - pred) / sd, 2), "SMH %": round(100 * float(r.SMH.loc[d]), 2)}
    # empirical: RSP on days with SMH within +-1.5pt of Day 2's SMH
    near = w[(w.SMH - float(r.SMH.loc[D2])).abs() <= 0.015] if D2 in r.index else w.iloc[:0]
    res["days with SMH within 1.5pt of Day 2"] = {"n": int(len(near)), "RSP mean %": round(100 * float(near.RSP.mean()), 2) if len(near) else None, "RSP median %": round(100 * float(near.RSP.median()), 2) if len(near) else None,
        "dates": {str(d.date()): [round(100 * x.SMH, 1), round(100 * x.RSP, 1)] for d, x in near.iterrows()}}
    return res
out["B4 full 2004-2026"] = b4("2004-01-01"); out["B4 recent 2023-2026"] = b4("2023-01-01")
# B5 basket-selling signature: avg pairwise corr of 5-min returns among 150 non-AI names
X = pd.read_csv(O / f"cross_section_{label}.csv", index_col=0); rest = sorted(X.index[X.b_AI < X.b_AI.quantile(0.70)]); random.seed(7); samp = random.sample(rest, 150)
Hh = {"User-Agent": "Mozilla/5.0"}
def get(s):
    for i in range(5):
        try:
            j = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{s}?range=60d&interval=5m", headers=Hh, timeout=25)
            if j.status_code == 429: time.sleep(2 + 2 * i); continue
            j = j.json()["chart"]["result"][0]; q = j["indicators"]["quote"][0]
            return s, pd.Series(q["close"], index=pd.to_datetime(j["timestamp"], unit="s", utc=True).tz_convert("America/New_York"))
        except Exception: time.sleep(1 + i)
    return s, None
with ThreadPoolExecutor(8) as ex: S = dict(x for x in ex.map(get, samp) if x[1] is not None)
C = pd.DataFrame(S); C = C[(C.index.time >= pd.Timestamp("09:30").time()) & (C.index.time < pd.Timestamp("16:00").time())]
C = C[~C.index.duplicated()]; dates = sorted(set(C.index.date)); rows = {}
for d in dates:
    x = C[C.index.date == d]; lr = np.log(x).diff().iloc[1:]; lr = lr.dropna(axis=1, thresh=int(0.8 * len(lr))).dropna(axis=0, how="any")
    if len(lr) < 30 or lr.shape[1] < 100: continue
    cm = np.corrcoef(lr.values.T); n = cm.shape[0]; rows[d] = (cm.sum() - n) / (n * (n - 1))
s = pd.Series(rows); base = s[[d for d in s.index if d < D1.date()]]
out["B5 avg pairwise 5-min corr, 150 non-AI names"] = {"n baseline days": int(len(base)), "baseline median": round(float(base.median()), 3), "baseline 95th pct": round(float(base.quantile(0.95)), 3),
    **{nm: ({"corr": round(float(s[d.date()]), 3), "percentile vs baseline": round(float((base < s[d.date()]).mean()), 3), "z": round(float((s[d.date()] - base.mean()) / base.std()), 2)} if d.date() in s.index else None) for nm, d in (("Day1", D1), ("Day2", D2))},
    "top 5 baseline days": {str(k): round(float(v), 3) for k, v in base.sort_values(ascending=False).head(5).items()}}
# B2 fix
P = pd.read_csv(O / f"intraday_paths_{label}.csv", index_col=0, parse_dates=True).dropna(); a_, b_ = P.AI_cum.diff().dropna().values, P.rest_cum.diff().dropna().values
def L(a, b):
    f = lambda x, y, kk: np.corrcoef(x[:-kk], y[kk:])[0, 1]
    return sum(f(a, b, kk) for kk in (1, 2, 3)) - sum(f(b, a, kk) for kk in (1, 2, 3))
n = len(a_); Bs = []
for _ in range(2000):
    idx = np.concatenate([np.arange(st, min(st + 6, n)) for st in rng.integers(0, n - 6, n // 6 + 1)])[:n]; Bs.append(L(a_[idx], b_[idx]))
out["B2 lead-lag fixed"] = {"L": round(float(L(a_, b_)), 3), "bootstrap 90% CI": [round(float(np.nanpercentile(Bs, 5)), 3), round(float(np.nanpercentile(Bs, 95)), 3)], "n bars": int(n), "corr lag0": round(float(np.corrcoef(a_, b_)[0, 1]), 3)}
json.dump(out, open(O / f"a2_{label}.json", "w"), indent=1, default=float); print(json.dumps(out, indent=1, default=float))
