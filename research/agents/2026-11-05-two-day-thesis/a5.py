"""Amendment A5: did AI become the funding leg after the October peak? Usage: python a5.py <label>"""
import sys, json, importlib.util, numpy as np, pandas as pd
from pathlib import Path
from scipy import stats
label = sys.argv[1]; H = Path(__file__).resolve().parent; O = H / "out"
spec = importlib.util.spec_from_file_location("lc", str(H.parent / "2026-11-05-liquidity-cycle" / "common.py")); lc = importlib.util.module_from_spec(spec); spec.loader.exec_module(lc)
px = pd.DataFrame({s: lc.yahoo(s, "2025-01-01").close for s in ("RSP", "SMH")}).dropna(); r = px.pct_change().dropna(); r["spread"] = r.SMH - r.RSP
a = r[(r.index >= "2026-03-02") & (r.index <= "2026-10-02")]; b = r[(r.index >= "2026-10-05") & (r.index <= "2026-11-03")]
ca, cb = stats.pearsonr(a.RSP, a.spread)[0], stats.pearsonr(b.RSP, b.spread)[0]
z = (np.arctanh(cb) - np.arctanh(ca)) / np.sqrt(1 / (len(a) - 3) + 1 / (len(b) - 3))
roll = r.RSP.rolling(20).corr(r.spread)
out = {"label": label, "D1 corr(RSP, SMH-RSP)": {"war, pre-peak (Mar 2 - Oct 2)": round(float(ca), 3), "n": int(len(a)), "post-peak (Oct 5 - Nov 3)": round(float(cb), 3), "n post": int(len(b)),
       "Fisher z (post < pre)": round(float(z), 2), "p one-sided": float(stats.norm.cdf(z)), "post-peak p (corr < 0)": float(stats.pearsonr(b.RSP, b.spread)[1] / 2 if cb < 0 else 1)},
       "rolling 20d corr, month-end": {str(d.date()): round(float(v), 2) for d, v in roll[roll.index >= "2026-01-01"].resample("ME").last().items()},
       "rolling 20d corr at Nov 3 / Nov 4 / Nov 5": [round(float(roll.get(pd.Timestamp(d), np.nan)), 2) for d in ("2026-11-03", "2026-11-04", "2026-11-05")],
       "post-peak days (RSP, spread) %": {str(d.date()): [round(100 * x.RSP, 2), round(100 * x.spread, 2)] for d, x in r[(r.index >= "2026-10-05")].iterrows()}}
json.dump(out, open(O / f"a5_{label}.json", "w"), indent=1, default=float); print(json.dumps(out, indent=1, default=float))
