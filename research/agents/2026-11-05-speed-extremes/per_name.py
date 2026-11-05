"""A1: per-name episodes (own thresholds = today's own values), plus today's index-level signature. No pooling across names."""
import json, sys, runpy, io, contextlib
from pathlib import Path
import numpy as np, pandas as pd
H = Path(__file__).resolve().parent; O = H / "out"
with contextlib.redirect_stdout(io.StringIO()): ns = runpy.run_path(str(H / "dashboard.py"))
F = ns["F"]; yahoo = ns["yahoo"]
def closes(s): return yahoo(s, "1994-01-01").close
def episodes(flag, gap=20):
    idx = np.where(flag.values)[0]; keep, last = [], -10**9
    for i in idx:
        if i - last > gap: keep.append(i)
        last = i
    return keep
def outcomes(c, i):
    n = len(c); e = c.iloc[i]
    f20 = c.iloc[i + 20] / e - 1 if i + 20 < n else np.nan; f60 = c.iloc[i + 60] / e - 1 if i + 60 < n else np.nan
    w = c.iloc[i + 1:i + 21]
    ll = bool((w < e).any()) if len(w) == 20 else None; best = float(w.max() / e - 1) if len(w) else np.nan
    return {"fwd20 %": None if np.isnan(f20) else round(100 * f20, 1), "fwd60 %": None if np.isnan(f60) else round(100 * f60, 1),
            "lower close within 20": ll, "best bounce within 20 %": None if np.isnan(best) else round(100 * best, 1)}
R = {"weeks": {}, "today": {}}
for s, f in F.items():
    c = closes(s).reindex(f.index); t = f.iloc[-1]; hist = f.iloc[:-1]
    for kind, col, gate in (("weeks", "z20", -1.5), ("today", "z1", -2.5)):
        if t[col] > gate: continue
        ep = episodes(hist[col] <= t[col])
        R[kind][s] = {"today value": round(float(t[col]), 2), "episodes": {str(hist.index[i].date()): {col: round(float(hist[col].iloc[i]), 2), **outcomes(c, i)} for i in ep}}
# today's index-level signature
spx = closes("^GSPC"); sox = closes("^SOX")
def z1(c): r = c.pct_change(); return r / r.rolling(60).std().shift(1)
J = pd.DataFrame({"spx": spx, "sox": sox}).dropna(); J["zs"] = z1(J.spx); J["zx"] = z1(J.sox)
sig = J.iloc[:-1][(J.zs <= -4.0) & (J.zx <= -3.0)]
R["index signature (S&P z<=-4 & SOX z<=-3)"] = {}
for t_ in sig.index:
    i = J.index.get_loc(t_); g = lambda col, k: round(100 * (J[col].iloc[i + k] / J[col].iloc[i] - 1), 1) if i + k < len(J) else None
    R["index signature (S&P z<=-4 & SOX z<=-3)"][str(t_.date())] = {"S&P day %": round(100 * (J.spx.iloc[i] / J.spx.iloc[i - 1] - 1), 1), "SOX day %": round(100 * (J.sox.iloc[i] / J.sox.iloc[i - 1] - 1), 1),
        "S&P z": round(float(J.zs.iloc[i]), 1), "SOX z": round(float(J.zx.iloc[i]), 1), "S&P +1/+5/+20/+60 %": [g("spx", k) for k in (1, 5, 20, 60)], "SOX +1/+5/+20/+60 %": [g("sox", k) for k in (1, 5, 20, 60)]}
R["TODAY index"] = {"S&P z": round(float(J.zs.iloc[-1]), 2), "SOX z": round(float(J.zx.iloc[-1]), 2), "date": str(J.index[-1].date())}
json.dump(R, open(O / "per_name.json", "w"), indent=1, default=float)
# print compact per-name lines
for kind in ("weeks", "today"):
    print(f"\n=== {kind.upper()} (own threshold = today's own value) ===")
    for s, v in R[kind].items():
        e = v["episodes"]; done = [x for x in e.values() if x["lower close within 20"] is not None]
        nb = sum(1 for x in done if x["best bounce within 20 %"] is not None and x["best bounce within 20 %"] >= 5); nll = sum(1 for x in done if x["lower close within 20"])
        up20 = sum(1 for x in done if x["fwd20 %"] is not None and x["fwd20 %"] > 0)
        print(f"{s:6s} today {v['today value']:+.2f} | past episodes {len(e)} (done {len(done)}): bounced >=5% within 20d {nb}/{len(done)}, lower close within 20d {nll}/{len(done)}, up after 20d {up20}/{len(done)} | dates: {', '.join(list(e)[-6:])}")
print("\n=== TODAY'S INDEX SIGNATURE ===", R["TODAY index"])
for k, v in R["index signature (S&P z<=-4 & SOX z<=-3)"].items(): print(k, v)
