"""S1 (sensitivity, added after the P2 run; not a test). P2's threshold (short z <= -1.75) was set from the in-sample fit; on the trailing fit
today reads -1.68 and does not qualify. Re-run the P2 event rule at -1.50 / -1.65 / -1.75 / -2.00 and give base rates for the same outcomes,
including a base rate for days that were, like today, 2.5-10% below their 252-session high. Usage: python s1_threshold.py"""
import json, importlib.util, numpy as np, pandas as pd
from pathlib import Path
H = Path(__file__).resolve().parent; O = H / "out"
spec = importlib.util.spec_from_file_location("lc", str(H.parent / "2026-11-05-liquidity-cycle" / "common.py")); lc = importlib.util.module_from_spec(spec); spec.loader.exec_module(lc)
def rolling_z(s, n):  # same as history.py
    y = np.log(s.values); N = len(y); x = np.arange(N, dtype=float); cs = lambda v: np.concatenate([[0.0], np.cumsum(v)])
    Sx, Sy, Sxx, Sxy, Syy = cs(x), cs(y), cs(x * x), cs(x * y), cs(y * y); z = np.full(N, np.nan); i = np.arange(n - 1, N); lo = i - n + 1
    sx, sy, sxx, sxy, syy = Sx[i + 1] - Sx[lo], Sy[i + 1] - Sy[lo], Sxx[i + 1] - Sxx[lo], Sxy[i + 1] - Sxy[lo], Syy[i + 1] - Syy[lo]
    b = (n * sxy - sx * sy) / (n * sxx - sx * sx); a = (sy - b * sx) / n
    ssr = syy - 2 * a * sy - 2 * b * sxy + n * a * a + 2 * a * b * sx + b * b * sxx; sd = np.sqrt(np.maximum(ssr, 1e-18) / (n - 2))
    z[i] = (y[i] - (a + b * x[i])) / sd; return pd.Series(z, index=s.index)
spx = lc.yahoo("^GSPC", "1927-12-01").close; spx = spx[spx.index >= "1950-01-01"]; P = spx.values; N = len(P)
zs, zl = rolling_z(spx, 756).values, rolling_z(spx, 3780).values
def dd_future(i, h=252):
    pk = P[max(0, i - 251):i + 1].max(); seg = P[i + 1:i + 1 + h]; rm = np.maximum.accumulate(np.concatenate([[pk], seg]))[1:]; return float((seg / rm - 1).min())
dd_now = lambda i: P[i] / P[max(0, i - 251):i + 1].max() - 1
out = {"today": {"short z": round(float(zs[-1]), 2), "long z": round(float(zl[-1]), 2), "dd from 252-session high %": round(100 * dd_now(N - 1), 2)}}
for T in (-1.50, -1.65, -1.75, -2.00):
    cond = (zs <= T) & (zl > -1.0); ev = []
    for i in np.where(cond)[0]:
        if not cond[max(0, i - 120):i].any(): ev.append(i)
    done = [i for i in ev if i + 252 < N]; m = [dd_future(i) for i in done]
    out[f"threshold {T}"] = {"events": len(ev), "completed": len(done), ">=10%": int(sum(x <= -0.10 for x in m)), ">=20%": int(sum(x <= -0.20 for x in m)),
        "today qualifies": bool(cond[-1]), "list": [f"{spx.index[i].date()} dd {100 * dd_now(i):.1f}% -> {100 * x:.1f}%" for i, x in zip(done, m)]}
grid = range(3780, N - 252, 5); B = np.array([(dd_now(i), dd_future(i)) for i in grid])
like = (B[:, 0] <= -0.025) & (B[:, 0] > -0.10)
out["base rates (every 5th session since 1965)"] = {"all days: n": int(len(B)), "all days >=10%": round(float((B[:, 1] <= -0.10).mean()), 3), "all days >=20%": round(float((B[:, 1] <= -0.20).mean()), 3),
    "days 2.5-10% below the 252-session high: n": int(like.sum()), "those >=10%": round(float((B[like, 1] <= -0.10).mean()), 3), "those >=20%": round(float((B[like, 1] <= -0.20).mean()), 3)}
json.dump(out, open(O / "s1_threshold.json", "w"), indent=1)
print(json.dumps({k: (v if not isinstance(v, dict) or "list" not in v else {kk: vv for kk, vv in v.items() if kk != "list"}) for k, v in out.items()}, indent=1))
for k in ("threshold -1.65", "threshold -1.5"):
    print(k); [print("  ", r) for r in out[k]["list"]]
