"""Aftershocks (pre-registered @ 0273b35): discrete Hawkes on big-move days (power-law vs exponential vs constant), Omori mainshock stacking,
forward forecast. Usage: python hawkes.py -> out/hawkes.json"""
import json, importlib.util, numpy as np, pandas as pd
from pathlib import Path
from scipy.optimize import minimize
H = Path(__file__).resolve().parent; O = H / "out"
spec = importlib.util.spec_from_file_location("lc", str(H.parent / "2026-11-05-liquidity-cycle" / "common.py")); lc = importlib.util.module_from_spec(spec); spec.loader.exec_module(lc)
rng = np.random.default_rng(1106); L = 252; SPLIT = pd.Timestamp("2008-01-01"); J = np.arange(1, L + 1, dtype=float)
def prep(sym, start):
    s = lc.yahoo(sym, start).close.dropna(); s = s[s > 0]; r = np.diff(np.log(s.values)); idx = s.index[1:]
    sc = pd.Series(np.abs(r), index=idx).rolling(1260, min_periods=1260).median().shift(1); ok = sc.notna().values
    r, idx, sc = r[ok], idx[ok], sc.values[ok]; x = (np.abs(r) >= 3 * sc).astype(float); big = np.abs(r) >= 8 * sc
    main = [int(i) for i in np.where(big)[0] if not big[max(0, i - 63):i].any()]
    return idx, r, sc, x, main
def kern(kind, th):
    k = (J + np.exp(th[2])) ** (-np.exp(th[3])) if kind == "pow" else np.exp(-J / np.exp(th[2])); return k / k.sum()
def probs(kind, th, x):
    mu = np.exp(th[0])
    if kind == "const": return np.full(len(x), np.clip(mu, 1e-6, 1 - 1e-6))
    h = np.convolve(x, np.concatenate([[0.0], kern(kind, th)]))[:len(x)]; return np.clip(mu + np.exp(th[1]) * h, 1e-6, 1 - 1e-6)
def ll_t(kind, th, x): p = probs(kind, th, x); return x * np.log(p) + (1 - x) * np.log(1 - p)
def fit(kind, x, mask):
    x0 = {"const": [np.log(x[mask].mean())], "exp": [np.log(0.03), np.log(0.8), np.log(20.0)], "pow": [np.log(0.02), np.log(0.85), np.log(2.0), np.log(0.9)]}[kind]
    f = lambda th: -ll_t(kind, th, x)[mask].sum(); best = None
    for jit in range(4):
        start = np.array(x0) + (rng.normal(0, 0.3, len(x0)) if jit else 0)
        r = minimize(f, start, method="Nelder-Mead", options={"maxiter": 6000, "xatol": 1e-6, "fatol": 1e-6})
        if best is None or r.fun < best.fun: best = r
    return best.x
def describe(kind, th):
    d = {"mu (background prob/day)": round(float(np.exp(th[0])), 4)}
    if kind != "const": d["n (branching ratio)"] = round(float(np.exp(th[1])), 3)
    if kind == "pow": d.update({"c": round(float(np.exp(th[2])), 2), "p (Omori exponent)": round(float(np.exp(th[3])), 3)})
    if kind == "exp": d["tau (days)"] = round(float(np.exp(th[2])), 1)
    return d
def block_ci(v, B=252, reps=2000):
    n = len(v); nb = int(np.ceil(n / B)); out = []
    for _ in range(reps):
        st = rng.integers(0, n - B, size=nb); ii = np.concatenate([np.arange(s0, s0 + B) for s0 in st])[:n]; out.append(v[ii].sum())
    return [round(float(np.percentile(out, 5)), 2), round(float(np.percentile(out, 95)), 2)]
res = {}
for nm, (sym, st) in {"S&P 500": ("^GSPC", "1950-01-01"), "Nasdaq-100": ("^NDX", "1985-10-01"), "SOX": ("^SOX", "1994-05-01")}.items():
    idx, r, sc, x, main = prep(sym, st); N = len(x); ins = (idx < SPLIT) & (np.arange(N) >= L); oos = idx >= SPLIT
    th = {k: fit(k, x, ins) for k in ("const", "exp", "pow")}; lt = {k: ll_t(k, th[k], x) for k in th}
    d_pe, d_pc, d_ec = lt["pow"][oos] - lt["exp"][oos], lt["pow"][oos] - lt["const"][oos], lt["exp"][oos] - lt["const"][oos]
    R = {"sample": f"{idx[0].date()} to {idx[-1].date()}", "event threshold now (3 x 5y median |r|) %": round(float(300 * sc[-1]), 2), "events in-sample / oos": [int(x[ins].sum()), int(x[oos].sum())],
         "fits (in-sample <2008)": {k: describe(k, th[k]) for k in th},
         "oos log-lik: pow, exp, const": [round(float(lt[k][oos].sum()), 1) for k in ("pow", "exp", "const")],
         "oos dLL pow-exp [90% CI]": [round(float(d_pe.sum()), 2), block_ci(d_pe)], "oos dLL pow-const [90% CI]": [round(float(d_pc.sum()), 2), block_ci(d_pc)],
         "oos dLL exp-const [90% CI]": [round(float(d_ec.sum()), 2), block_ci(d_ec)]}
    pw = probs("pow", th["pow"], x); trig = (pw - np.exp(th["pow"][0])) / pw; R["share of oos event days attributed to triggering (pow)"] = round(float(trig[oos & (x == 1)].mean()), 3)
    # ---- Omori, mainshock-stacked (lags 1..120)
    T = 120; rows = [(i, t, x[i + t]) for i in main for t in range(1, T + 1) if i + t < N]; M = np.array(rows, float)
    mi_in = np.array([idx[int(i)] < SPLIT for i in M[:, 0]]); lag, y = M[:, 1], M[:, 2]
    def lam(kind, th):
        b = np.exp(th[0])
        if kind == "const": return np.clip(np.full(len(lag), b), 1e-6, 1 - 1e-6)
        if kind == "pow": return np.clip(b + np.exp(th[1]) * (lag + np.exp(th[2])) ** (-np.exp(th[3])), 1e-6, 1 - 1e-6)
        return np.clip(b + np.exp(th[1]) * np.exp(-lag / np.exp(th[2])), 1e-6, 1 - 1e-6)
    def omll(kind, th): p = lam(kind, th); return y * np.log(p) + (1 - y) * np.log(1 - p)
    x0s = {"const": [np.log(0.1)], "exp": [np.log(0.08), np.log(0.4), np.log(15.0)], "pow": [np.log(0.05), np.log(0.6), np.log(1.0), np.log(0.8)]}; tho = {}
    for k in x0s:
        best = None
        for jit in range(4):
            r0 = minimize(lambda t_: -omll(k, t_)[mi_in].sum(), np.array(x0s[k]) + (rng.normal(0, 0.3, len(x0s[k])) if jit else 0), method="Nelder-Mead", options={"maxiter": 6000})
            if best is None or r0.fun < best.fun: best = r0
        tho[k] = best.x
    lo = {k: omll(k, tho[k]) for k in tho}; oo = ~mi_in; ms_ids = M[oo, 0]; uniq = np.unique(ms_ids); dd = lo["pow"][oo] - lo["exp"][oo]
    per = np.array([dd[ms_ids == u].sum() for u in uniq]); boot = [per[rng.integers(0, len(per), len(per))].sum() for _ in range(4000)]
    R["Omori mainshocks"] = {"mainshocks in-sample / oos": [int(len(set(M[mi_in, 0]))), int(len(uniq))], "oos mainshock dates": [str(idx[int(u)].date()) for u in uniq],
        "in-sample pow fit": {"b": round(float(np.exp(tho['pow'][0])), 4), "K": round(float(np.exp(tho['pow'][1])), 3), "c": round(float(np.exp(tho['pow'][2])), 2), "p": round(float(np.exp(tho['pow'][3])), 3)},
        "in-sample exp fit": {"b": round(float(np.exp(tho['exp'][0])), 4), "K": round(float(np.exp(tho['exp'][1])), 3), "tau": round(float(np.exp(tho['exp'][2])), 1)},
        "oos dLL pow-exp [90% CI]": [round(float(dd.sum()), 2), [round(float(np.percentile(boot, 5)), 2), round(float(np.percentile(boot, 95)), 2)]],
        "oos dLL pow-const": round(float((lo["pow"][oo] - lo["const"][oo]).sum()), 2)}
    if nm == "S&P 500":
        # ---- refit on all data and simulate forward 63 sessions (forecast logged now, scored later)
        allm = np.arange(N) >= L; tf = fit("pow", x, allm); k = kern("pow", tf); mu, n = np.exp(tf[0]), np.exp(tf[1]); P = 10000
        hist = np.tile(x[-L:][::-1], (P, 1)); cnt = np.zeros((P, 63))
        for step in range(63):
            p = np.clip(mu + n * hist @ k, 0, 1); e = (rng.random(P) < p).astype(float); cnt[:, step] = e; hist = np.concatenate([e[:, None], hist[:, :-1]], axis=1)
        cs = np.cumsum(cnt, axis=1)
        R["full-sample pow fit"] = describe("pow", tf); R["today's event probability (Nov 6)"] = round(float(np.clip(mu + n * (x[-L:][::-1] @ k), 0, 1)), 3)
        R["forward forecast from 2026-11-05 (S&P days with |r| >= threshold)"] = {f"next {h} sessions": {"expected": round(float(cs[:, h - 1].mean()), 2), "80% interval": [int(np.percentile(cs[:, h - 1], 10)), int(np.percentile(cs[:, h - 1], 90))],
            "constant-rate expectation": round(float(h * x[allm].mean()), 2)} for h in (5, 21, 63)}
        R["last 10 sessions: date, |r| %, event"] = [[str(idx[i].date()), round(float(100 * abs(r[i])), 2), int(x[i])] for i in range(N - 10, N)]
        R["Nov 5 2026 is a mainshock"] = bool((N - 1) in main)
    res[nm] = R; print(nm, json.dumps({k: v for k, v in R.items() if k.startswith(("fits", "oos", "Omori", "share", "full", "today", "forward", "Nov"))}, indent=0)[:3000])
json.dump(res, open(O / "hawkes.json", "w"), indent=1)
