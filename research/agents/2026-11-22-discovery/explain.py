"""Stage 5 explanation: out-of-sample SHAP values from the CLEAN walk-forward (refit per test year), ranked by feature and by family;
then SHAP interaction values from one model on the top-25 features (1990-2019) to find variables that matter only in some environments."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
import lightgbm as lgb, shap
from model import data, PARAMS

H = Path(__file__).resolve().parent
def family(c):
    if c.startswith("corr("): return "co-movement (rolling correlations)"
    if c.startswith("absorption"): return "system (one common factor)"
    if c.startswith("SPXvol") or c.startswith("VIX-minus"): return "S&P volatility state"
    s = c.split("|")[1]
    if s in ("level", "z3y", "from52wHigh"): return "level / position vs history"
    if s.startswith("speed"): return "speed (change ÷ normal size)"
    if s.startswith("chg"): return "change"
    if s.startswith("accel"): return "acceleration"
    return "other"

def run(tg):
    Xa, t, h = data(tg); Xa = Xa[[c for c in Xa.columns if not c.startswith("NFCI")]]; y = t[tg].values.astype(float)
    cols = list(Xa.columns); S = []; dates = Xa.index
    for yr in range(2000, 2020):
        a = pd.Timestamp(f"{yr}-01-01"); b = pd.Timestamp(f"{yr + 1}-01-01")
        tr = dates < a - pd.Timedelta(weeks=h); te = (dates >= a) & (dates < b)
        M = (lgb.LGBMClassifier if tg == "crash13" else lgb.LGBMRegressor)(**PARAMS).fit(Xa.values[tr], y[tr])
        sv = shap.TreeExplainer(M).shap_values(Xa.values[te]); sv = sv[1] if isinstance(sv, list) else sv
        S.append(sv)
    S = np.vstack(S); imp = pd.Series(np.abs(S).mean(0), index=cols).sort_values(ascending=False)
    fam = imp.groupby(imp.index.map(family)).sum().sort_values(ascending=False); fam = fam / fam.sum()
    base = imp.groupby(imp.index.map(lambda c: c.split("|")[0])).sum().sort_values(ascending=False); base = base / base.sum()
    top = list(imp.index[:25]); Xt = Xa[top]
    M = (lgb.LGBMClassifier if tg == "crash13" else lgb.LGBMRegressor)(**PARAMS).fit(Xt.values, y)
    iv = shap.TreeExplainer(M).shap_interaction_values(Xt.values); iv = iv[1] if isinstance(iv, list) else iv
    A = np.abs(iv).mean(0); np.fill_diagonal(A, 0)
    pairs = sorted(((A[i, j], top[i], top[j]) for i in range(len(top)) for j in range(i + 1, len(top))), reverse=True)[:10]
    main = np.abs(iv).mean(0).diagonal().sum(); inter = A.sum()
    return {"top_features": imp.head(15).round(5).to_dict(), "families_share": fam.round(3).to_dict(), "base_variables_share": base.head(10).round(3).to_dict(),
            "top_interactions": [{"a": a, "b": b, "strength": round(float(v), 5)} for v, a, b in pairs],
            "interaction_share_of_total": round(float(inter / (inter + main)), 3)}

if __name__ == "__main__":
    out = {}
    for tg in (sys.argv[1:] or ["vol4", "mdd13", "crash13", "ret4", "ret13"]):
        out[tg] = r = run(tg)
        print(f"\n===== {tg}"); print("families:", r["families_share"]); print("base variables:", r["base_variables_share"])
        print("top features:", list(r["top_features"].items())[:10]); print("interaction share:", r["interaction_share_of_total"])
        for z in r["top_interactions"][:6]: print(f"   {z['a']}  ×  {z['b']}   {z['strength']}")
        json.dump(out, open(H / "out" / "explain.json", "w"), indent=1)
