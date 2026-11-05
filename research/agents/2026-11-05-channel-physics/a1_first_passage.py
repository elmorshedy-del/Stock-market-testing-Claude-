"""A1 (pre-registered @ 77b4866): volatility first-passage model. P(close falls by a within T sessions) for Brownian motion with drift mu and
per-session vol k*VIX/100/sqrt(252). Fit (k, mu) on 1990-2007, test 2008->. Also H-A2 (does channel z add anything?), NDX/VXN, today's odds.
Usage: python a1_first_passage.py -> out/a1.json"""
import json, importlib.util, numpy as np, pandas as pd
from pathlib import Path
from scipy.stats import norm
from scipy.optimize import minimize
H = Path(__file__).resolve().parent; O = H / "out"
spec = importlib.util.spec_from_file_location("lc", str(H.parent / "2026-11-05-liquidity-cycle" / "common.py")); lc = importlib.util.module_from_spec(spec); spec.loader.exec_module(lc)
spec2 = importlib.util.spec_from_file_location("ph", str(H / "physics.py")); src = open(H / "physics.py").read()
exec(src[src.index("def rolling_z_log"):src.index("def betas")])  # reuse the exact rolling_z_log from physics.py
CELLS = [(0.05, 21), (0.05, 63), (0.10, 21), (0.10, 63)]; rng = np.random.default_rng(7)
def fp(a, T, sig, mu):
    s = sig * np.sqrt(T); return np.clip(norm.cdf((-a - mu * T) / s) + np.exp(np.clip(-2 * mu * a / sig ** 2, -50, 50)) * norm.cdf((-a + mu * T) / s), 1e-6, 1 - 1e-6)
def build(px, vol):
    d = pd.concat([px.rename("p"), vol.rename("v")], axis=1, join="inner").dropna(); P = d.p.values; N = len(P); out = {}
    for x, T in CELLS:
        mn = pd.Series(P[::-1]).rolling(T, min_periods=T).min().values[::-1]  # min of P[t..t+T-1]
        fut = np.full(N, np.nan); fut[:N - T] = mn[1:N - T + 1]; y = np.where(np.isnan(fut), np.nan, (fut <= P * (1 - x)).astype(float)); out[(x, T)] = y
    return d, out
def nll(theta, d, Y, mask):
    k, mu = np.exp(theta[0]), theta[1]; sig = k * d.v.values / 100 / np.sqrt(252); tot = 0.0
    for (x, T), y in Y.items():
        m = mask & ~np.isnan(y); p = fp(-np.log(1 - x), T, sig[m], mu); tot -= np.sum(y[m] * np.log(p) + (1 - y[m]) * np.log(1 - p))
    return tot
def evaluate(d, Y, fit_end, test_start, label):
    idx = d.index; ins = idx <= fit_end; oos = idx >= test_start
    r = minimize(nll, x0=[np.log(0.8), 0.0003], args=(d, Y, ins), method="Nelder-Mead", options={"xatol": 1e-6, "fatol": 1e-4, "maxiter": 4000})
    k, mu = float(np.exp(r.x[0])), float(r.x[1]); sig = k * d.v.values / 100 / np.sqrt(252); cells = {}
    for (x, T), y in Y.items():
        mi, mo = ins & ~np.isnan(y), oos & ~np.isnan(y); p = fp(-np.log(1 - x), T, sig, mu); clim = y[mi].mean()
        yo, po = y[mo], p[mo]; bs_m, bs_c = np.mean((po - yo) ** 2), np.mean((clim - yo) ** 2); bss = 1 - bs_m / bs_c
        n = len(yo); B = 252; nb = int(np.ceil(n / B)); bs = []
        for _ in range(2000):
            st = rng.integers(0, n - B, size=nb); ii = np.concatenate([np.arange(s0, s0 + B) for s0 in st])[:n]
            bs.append(1 - np.mean((po[ii] - yo[ii]) ** 2) / np.mean((clim - yo[ii]) ** 2))
        q = pd.qcut(po, 10, labels=False, duplicates="drop"); rel = [[round(float(po[q == b].mean()), 3), round(float(yo[q == b].mean()), 3), int((q == b).sum())] for b in sorted(set(q))]
        cells[f"-{int(100*x)}% within {T}"] = {"BSS": round(float(bss), 3), "BSS 90% CI": [round(float(np.percentile(bs, 5)), 3), round(float(np.percentile(bs, 95)), 3)],
            "mean predicted": round(float(po.mean()), 3), "observed rate": round(float(yo.mean()), 3), "climatology (in-sample rate)": round(float(clim), 3), "n test days": int(n),
            "reliability (pred, obs, n) by decile": rel}
    return {"label": label, "k": round(k, 3), "mu per session": round(mu, 6), "mu annualized %": round(100 * (np.exp(252 * mu) - 1), 1), "cells": cells}, k, mu
spx, vix = lc.yahoo("^GSPC", "1989-01-01").close, lc.yahoo("^VIX", "1990-01-01").close
d, Y = build(spx, vix); main, k, mu = evaluate(d, Y, "2007-12-31", "2008-01-01", "S&P 500 / VIX")
passed = [c["BSS"] > 0 and c["BSS 90% CI"][0] > 0 for c in main["cells"].values()]; main["H-A1 pass (>=3 of 4 cells with BSS>0 and CI low>0)"] = bool(sum(passed) >= 3)
# ---- H-A2: does the trailing channel position add anything beyond volatility?
z = pd.Series(rolling_z_log(np.log(spx.values), 756), index=spx.index).reindex(d.index).values; sig = k * d.v.values / 100 / np.sqrt(252)
ins, oos = d.index <= "2007-12-31", d.index >= "2008-01-01"; A2 = {}
lg = lambda p: np.log(p / (1 - p)); ex = lambda u: 1 / (1 + np.exp(-u))
for (x, T), y in Y.items():
    p = fp(-np.log(1 - x), T, sig, mu); mi, mo = ins & ~np.isnan(y) & ~np.isnan(z), oos & ~np.isnan(y) & ~np.isnan(z)
    def ll(g, m, use_z): q = np.clip(ex(lg(p[m]) + g[0] + (g[1] * z[m] if use_z else 0)), 1e-6, 1 - 1e-6); return -np.mean(y[m] * np.log(q) + (1 - y[m]) * np.log(1 - q))
    g0 = minimize(lambda g: ll([g[0], 0], mi, False), [0.0], method="Nelder-Mead").x; g1 = minimize(lambda g: ll(g, mi, True), [0.0, 0.0], method="Nelder-Mead").x
    base, withz = ll([g0[0], 0], mo, False), ll(g1, mo, True)
    A2[f"-{int(100*x)}% within {T}"] = {"oos log loss, vol model + intercept": round(float(base), 4), "oos log loss, + channel z": round(float(withz), 4), "improvement %": round(100 * (base - withz) / base, 2), "gamma_z (in-sample)": round(float(g1[1]), 3)}
main["H-A2 (channel z adds <= 0.5% log-loss improvement in every cell)"] = {"cells": A2, "holds": bool(all(v["improvement %"] <= 0.5 for v in A2.values()))}
# ---- NDX / VXN (descriptive)
ndx, vxn = lc.yahoo("^NDX", "2000-01-01").close, lc.yahoo("^VXN", "2001-01-01").close
dn, Yn = build(ndx, vxn); nres, kn, mun = evaluate(dn, Yn, "2007-12-31", "2008-01-01", "Nasdaq-100 / VXN")
# ---- today's odds for the same-rule lines (lines rise with the trend, so use drift mu - g)
today = {}
for nm, px, vol, kk, mm, g, lines in (("S&P 500", spx, vix, k, mu, np.log(1.197) / 252, {"line through the 2026 low": 7076.2, "line through the 2025 low": 6616.1}),
                                      ("QQQ (Nasdaq-100 model, VXN)", lc.yahoo("QQQ", "2026-01-01").close, vxn, kn, mun, np.log(1.257) / 252, {"line through the 2026 low": 641.6, "line through the 2025 low": 596.8})):
    p0, v0 = float(px.iloc[-1]), float(vol.iloc[-1]); sg = kk * v0 / 100 / np.sqrt(252)
    today[nm] = {"close": round(p0, 2), "implied vol index": round(v0, 2), **{f"{ln} ({lv:,.1f})": {f"touch within {T}": round(float(fp(np.log(p0 / lv), T, sg, mm - g)), 3) for T in (5, 21, 63)} for ln, lv in lines.items()}}
out = {"S&P 500 (primary)": main, "Nasdaq-100 (descriptive)": nres, "today (same-rule lines)": today}
json.dump(out, open(O / "a1.json", "w"), indent=1)
print(json.dumps({"k": main["k"], "mu ann %": main["mu annualized %"], "cells": {c: {kk: v[kk] for kk in ("BSS", "BSS 90% CI", "mean predicted", "observed rate", "climatology (in-sample rate)")} for c, v in main["cells"].items()},
                  "H-A1": main["H-A1 pass (>=3 of 4 cells with BSS>0 and CI low>0)"], "H-A2": main["H-A2 (channel z adds <= 0.5% log-loss improvement in every cell)"],
                  "NDX": {"k": nres["k"], "cells": {c: v["BSS"] for c, v in nres["cells"].items()}}, "today": today}, indent=1))
