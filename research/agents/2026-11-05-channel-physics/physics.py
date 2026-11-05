"""Channel-physics T1-T3, pre-registered @ 1922c56. Null M0 = sign-randomized surrogates (keeps every |daily move|, destroys direction
predictability). Usage: python physics.py -> out/physics.json, out/surrogates.npz"""
import json, importlib.util, numpy as np, pandas as pd
from pathlib import Path
H = Path(__file__).resolve().parent; O = H / "out"
spec = importlib.util.spec_from_file_location("lc", str(H.parent / "2026-11-05-liquidity-cycle" / "common.py")); lc = importlib.util.module_from_spec(spec); spec.loader.exec_module(lc)
rng = np.random.default_rng(20261105); NS = 2000; Q = [21, 63, 126, 252, 504, 756]; HZ = [21, 63, 252]; W = 756
IDX = {"S&P 500": ("^GSPC", "1950-01-01"), "Nasdaq-100": ("^NDX", "1985-10-01"), "SOX": ("^SOX", "1994-05-01")}
def vr(r):
    r = r - r.mean(); c = np.concatenate([[0.0], np.cumsum(r)]); v1 = r.var(ddof=1)
    return np.array([(c[q:] - c[:-q]).var(ddof=1) / (q * v1) for q in Q])
def rolling_z_log(y, n):
    N = len(y); x = np.arange(N, dtype=float); cs = lambda v: np.concatenate([[0.0], np.cumsum(v)])
    Sx, Sy, Sxx, Sxy, Syy = cs(x), cs(y), cs(x * x), cs(x * y), cs(y * y); z = np.full(N, np.nan); i = np.arange(n - 1, N); lo = i - n + 1
    sx, sy, sxx, sxy, syy = Sx[i + 1] - Sx[lo], Sy[i + 1] - Sy[lo], Sxx[i + 1] - Sxx[lo], Sxy[i + 1] - Sxy[lo], Syy[i + 1] - Syy[lo]
    b = (n * sxy - sx * sy) / (n * sxx - sx * sx); a = (sy - b * sx) / n
    ssr = syy - 2 * a * sy - 2 * b * sxy + n * a * a + 2 * a * b * sx + b * b * sxx; sd = np.sqrt(np.maximum(ssr, 1e-18) / (n - 2))
    z[i] = (y[i] - (a + b * x[i])) / sd; return z
def betas(y, z):
    out = []
    for h in HZ:
        f = y[h:] - y[:-h]; zz = z[:len(f)]; ok = ~np.isnan(zz); zv, fv = zz[ok], f[ok]
        out.append(float(np.cov(zv, fv)[0, 1] / zv.var(ddof=1)))
    return np.array(out)
def holm(ps):
    ps = np.asarray(ps, float); o = np.argsort(ps); m = len(ps); adj = np.empty(m); run = 0.0
    for k, i in enumerate(o): run = max(run, min(1.0, (m - k) * ps[i])); adj[i] = run
    return adj
res = {}; store = {}
for nm, (sym, st) in IDX.items():
    s = lc.yahoo(sym, st).close.dropna(); s = s[s > 0]; y = np.log(s.values); r = np.diff(y); mu = r.mean()
    vr_obs = vr(r); z = rolling_z_log(y, W); b_obs = betas(y, z)
    VR = np.empty((NS, len(Q))); B = np.empty((NS, len(HZ)))
    for k in range(NS):
        sg = rng.choice([-1.0, 1.0], size=len(r)); rs = mu + sg * (r - mu); ys = np.concatenate([[y[0]], y[0] + np.cumsum(rs)])
        VR[k] = vr(rs); B[k] = betas(ys, rolling_z_log(ys, W))
    p_vr = [(1 + int((VR[:, j] <= vr_obs[j]).sum())) / (1 + NS) for j in range(len(Q))]
    p_b = [(1 + int((B[:, j] <= b_obs[j]).sum())) / (1 + NS) for j in range(len(HZ))]
    res[nm] = {"symbol": sym, "start": str(s.index[0].date()), "end": str(s.index[-1].date()), "n days": int(len(r)), "daily mean %": round(100 * mu, 4), "daily sd %": round(100 * r.std(), 3),
               "VR observed": dict(zip(map(str, Q), np.round(vr_obs, 3).tolist())), "VR surrogate 2.5/50/97.5": {str(q): np.round(np.percentile(VR[:, j], [2.5, 50, 97.5]), 3).tolist() for j, q in enumerate(Q)},
               "VR one-sided p (below)": dict(zip(map(str, Q), np.round(p_vr, 4).tolist())),
               "beta observed (fwd log return per 1 sigma of z)": dict(zip(map(str, HZ), np.round(b_obs, 5).tolist())), "beta surrogate 2.5/50/97.5": {str(h): np.round(np.percentile(B[:, j], [2.5, 50, 97.5]), 5).tolist() for j, h in enumerate(HZ)},
               "beta one-sided p (below)": dict(zip(map(str, HZ), np.round(p_b, 4).tolist())), "z today": round(float(z[-1]), 2)}
    store[nm + "_VR"] = VR; store[nm + "_B"] = B; print(nm, "done", res[nm]["VR observed"], res[nm]["beta observed (fwd log return per 1 sigma of z)"])
names = list(IDX); p1 = [res[n]["VR one-sided p (below)"]["756"] for n in names]; a1 = holm(p1)
p2 = [res[n]["beta one-sided p (below)"]["63"] for n in names]; a2 = holm(p2)
p9 = [res[n]["beta one-sided p (below)"][str(h)] for n in names for h in HZ]; a9 = holm(p9)
res["H-T1 (VR(756) below surrogates, Holm over 3; pass if >=2 of 3 at 0.05)"] = {"raw p": dict(zip(names, p1)), "Holm p": dict(zip(names, np.round(a1, 4).tolist())), "pass": bool((a1 < 0.05).sum() >= 2)}
res["H-T2 (beta_63 below surrogates, Holm over 3; pass if >=2 of 3 at 0.05)"] = {"raw p": dict(zip(names, p2)), "Holm p": dict(zip(names, np.round(a2, 4).tolist())), "pass": bool((a2 < 0.05).sum() >= 2)}
res["T2 secondary (all 9 cells, Holm over 9)"] = {f"{n} h{h}": round(float(a9[k]), 4) for k, (n, h) in enumerate([(n, h) for n in names for h in HZ])}
# ---- T3: how tight is each current (2023->today) channel vs sign-randomized versions of the same returns
T3 = {}
for nm, sym in (("S&P 500", "^GSPC"), ("QQQ", "QQQ"), ("SMH", "SMH")):
    s = lc.yahoo(sym, "2022-06-01").close; x = s[s.index >= "2023-01-03"]; y = np.log(x.values); t = np.arange(len(y))
    sdres = lambda yy: float(np.std(yy - np.polyval(np.polyfit(t, yy, 1), t), ddof=2)); obs = sdres(y); r = np.diff(y); mu = r.mean()
    sur = np.array([sdres(np.concatenate([[y[0]], y[0] + np.cumsum(mu + rng.choice([-1.0, 1.0], size=len(r)) * (r - mu))])) for _ in range(NS)])
    T3[nm] = {"residual SD % (observed)": round(100 * obs, 2), "random-walk median %": round(100 * float(np.median(sur)), 2), "ratio": round(obs / float(np.median(sur)), 2),
              "percentile of observed among surrogates": round(100 * float((sur <= obs).mean()), 1)}
res["T3 current-channel tightness (2023-01-03 to today)"] = T3
json.dump(res, open(O / "physics.json", "w"), indent=1); np.savez_compressed(O / "surrogates.npz", **store)
print(json.dumps({k: v for k, v in res.items() if k.startswith(("H-", "T2", "T3"))}, indent=1))
