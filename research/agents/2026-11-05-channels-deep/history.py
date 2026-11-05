"""P1 retest, P2 short-break/long-intact history (trailing fits, no look-ahead), P3 calendar of bear markets. Usage: python history.py"""
import json, importlib.util, numpy as np, pandas as pd, statsmodels.api as sm
from pathlib import Path
from scipy import stats
H = Path(__file__).resolve().parent; O = H / "out"
spec = importlib.util.spec_from_file_location("lc", str(H.parent / "2026-11-05-liquidity-cycle" / "common.py")); lc = importlib.util.module_from_spec(spec); spec.loader.exec_module(lc)
out = {}
px = {s: lc.yahoo(s, st).close for s, st in (("^GSPC", "1927-12-01"), ("^NYA", "1965-12-01"), ("RSP", "2003-04-01"), ("QQQ", "1999-03-01"), ("SMH", "2000-05-01"))}
# ---------- P1 ----------
def z_ols(s, start):
    x = s[s.index >= start]; t = np.arange(len(x)); y = np.log(x.values); b, a = np.polyfit(t, y, 1); r = y - (a + b * t); return r[-1] / r.std()
def z_lad(s, start):
    x = s[s.index >= start]; t = np.arange(len(x)); y = np.log(x.values); m = sm.QuantReg(y, sm.add_constant(t)).fit(q=0.5); r = y - m.predict(sm.add_constant(t)); return r[-1] / np.std(r)
def env(s, start):
    x = s[s.index >= start]; lo = np.log(x.rolling(63, min_periods=20).min().values); t = np.arange(len(x)); ok = ~np.isnan(lo); b, a = np.polyfit(t[ok], lo[ok], 1); return 100 * (np.exp(np.log(x.values[-1]) - (a + b * t[-1])) - 1)
def z_trail(s, n):
    x = s.iloc[-n:]; t = np.arange(len(x)); y = np.log(x.values); b, a = np.polyfit(t, y, 1); r = y - (a + b * t); return r[-1] / r.std()
P1 = {}
for s, nm in (("^GSPC", "SPX"), ("QQQ", "QQQ"), ("SMH", "SMH"), ("RSP", "RSP")):
    x = px[s]; P1[nm] = {"long OLS 2009-03-09 / 2010-01-04 / 2012-01-03": [round(z_ols(x, d), 2) for d in ("2009-03-09", "2010-01-04", "2012-01-03")],
        "short OLS 2022-10-12 / 2023-01-03 / 2023-06-01": [round(z_ols(x, d), 2) for d in ("2022-10-12", "2023-01-03", "2023-06-01")],
        "LAD long 2009 / short 2023": [round(z_lad(x, "2009-03-09"), 2), round(z_lad(x, "2023-01-03"), 2)],
        "% above lower envelope long 2009 / short 2023": [round(env(x, "2009-03-09"), 1), round(env(x, "2023-01-03"), 1)],
        "trailing 3y z / trailing 15y z": [round(z_trail(x, 756), 2), round(z_trail(x, 3780), 2) if len(x) >= 3780 else None]}
out["P1 today's readings, robustness"] = P1
# ---------- P2 ----------
def rolling_z(s, n):
    y = np.log(s.values); N = len(y); x = np.arange(N, dtype=float)
    cs = lambda v: np.concatenate([[0.0], np.cumsum(v)])
    Sx, Sy, Sxx, Sxy, Syy = cs(x), cs(y), cs(x * x), cs(x * y), cs(y * y); z = np.full(N, np.nan)
    i = np.arange(n - 1, N); lo = i - n + 1
    sx, sy, sxx, sxy, syy = Sx[i + 1] - Sx[lo], Sy[i + 1] - Sy[lo], Sxx[i + 1] - Sxx[lo], Sxy[i + 1] - Sxy[lo], Syy[i + 1] - Syy[lo]
    b = (n * sxy - sx * sy) / (n * sxx - sx * sx); a = (sy - b * sx) / n
    ssr = syy - 2 * a * sy - 2 * b * sxy + n * a * a + 2 * a * b * sx + b * b * sxx; sd = np.sqrt(np.maximum(ssr, 1e-18) / (n - 2))
    z[i] = (y[i] - (a + b * x[i])) / sd; return pd.Series(z, index=s.index)
spx = px["^GSPC"]; spx = spx[spx.index >= "1950-01-01"]
zs, zl = rolling_z(spx, 756), rolling_z(spx, 3780)
avg = pd.concat([px["^NYA"][px["^NYA"].index < "2007-01-01"], px["RSP"][px["RSP"].index >= "2007-01-01"]])
za_parts = [rolling_z(px["^NYA"], 756)[lambda q: q.index < "2007-01-01"], rolling_z(px["RSP"], 756)[lambda q: q.index >= "2007-01-01"]]
za = pd.concat(za_parts).reindex(spx.index, method="ffill")
cond = (zs <= -1.75) & (zl > -1.0); P = spx.values; N = len(P); ev = []; last = -10**9
for i in np.where(cond.values)[0]:
    if i - last > 120 and not cond.values[max(0, i - 120):i].any(): ev.append(i)
    last = i if cond.values[i] else last
def dd_future(i, h=252):
    pk = P[max(0, i - 251):i + 1].max(); seg = P[i + 1:i + 1 + h]
    if len(seg) == 0: return None, None, None
    rm = np.maximum.accumulate(np.concatenate([[pk], seg]))[1:]; dd = seg / rm - 1
    nh = np.where(P[i + 1:] >= pk)[0]; return float(dd.min()), float(P[i:i + 1 + h].min() / pk - 1), (int(nh[0]) + 1 if len(nh) else None)
rows = {}
for i in ev:
    d = spx.index[i]; mdd, mdd_from_pk, nh = dd_future(i); f = lambda k: round(100 * (P[i + k] / P[i] - 1), 1) if i + k < N else None
    rows[str(d.date())] = {"short z": round(float(zs.iloc[i]), 2), "long z": round(float(zl.iloc[i]), 2), "avg-stock short z": None if np.isnan(za.iloc[i]) else round(float(za.iloc[i]), 2),
        "dd at event %": round(100 * (P[i] / P[max(0, i - 251):i + 1].max() - 1), 1), "max dd next 252 (from running peak) %": None if mdd is None else round(100 * mdd, 1),
        "became >=20% bear": None if mdd is None else bool(mdd <= -0.2), "became >=10% correction": None if mdd is None else bool(mdd <= -0.1),
        "fwd 63/126/252 %": [f(63), f(126), f(252)], "sessions to new high": nh, "complete (252 sessions observed)": bool(i + 252 < N)}
out["P2 events (short z<=-1.75, long z>-1)"] = rows
E = pd.DataFrame(rows).T; done = E[E["complete (252 sessions observed)"] == True]
nar = done[done["avg-stock short z"].apply(lambda v: v is not None and v > -1.0)]; brd = done[done["avg-stock short z"].apply(lambda v: v is not None and v <= -1.0)]
base = []
for i in range(3780, N - 252, 5):
    m, _, _ = dd_future(i); base.append(m <= -0.2)
out["P2 summary"] = {"events": int(len(E)), "completed": int(len(done)), "became >=20% bear": int(done["became >=20% bear"].sum()), "became >=10% correction": int(done["became >=10% correction"].sum()),
    "narrow (avg stock z > -1): n / bears": [int(len(nar)), int(nar["became >=20% bear"].sum())], "broad (avg stock z <= -1): n / bears": [int(len(brd)), int(brd["became >=20% bear"].sum())],
    "base rate: share of days followed by a >=20% bear within 252 sessions": round(float(np.mean(base)), 3),
    "H-P2 (<=30% became bears)": bool(done["became >=20% bear"].mean() <= 0.30) if len(done) else None,
    "today": {"short z (trailing 3y)": round(float(zs.iloc[-1]), 2), "long z (trailing 15y)": round(float(zl.iloc[-1]), 2), "avg-stock short z (RSP trailing 3y)": round(float(za.iloc[-1]), 2), "qualifies": bool(cond.iloc[-1])}}
# ---------- P3 ----------
s28 = px["^GSPC"]
def zigzag(s, th):
    v = s.values; idx = s.index; peaks = []; mode = "up"; ext_i = 0
    for i in range(1, len(v)):
        if mode == "up":
            if v[i] > v[ext_i]: ext_i = i
            elif v[i] <= v[ext_i] * (1 - th): peaks.append(("peak", ext_i)); mode = "down"; ext_i = i
        else:
            if v[i] < v[ext_i]: ext_i = i
            elif v[i] >= v[ext_i] * (1 + th): peaks.append(("trough", ext_i)); mode = "up"; ext_i = i
    peaks.append(("trough" if mode == "down" else "peak", ext_i)); return peaks
def episodes(th):
    z = zigzag(s28, th); res = []
    for k, (typ, i) in enumerate(z):
        if typ == "peak" and k + 1 < len(z):
            j = z[k + 1][1]; res.append({"peak": str(s28.index[i].date()), "trough": str(s28.index[j].date()), "depth %": round(100 * (s28.iloc[j] / s28.iloc[i] - 1), 1), "sessions": int(j - i)})
    return res
def record_episodes(s, th):
    """Pre-registered: peak = last record close before the decline; trough = lowest close before a new record. Keeps declines of >= th."""
    v = s.values; ix = s.index; res = []; rec = 0; lo = 0
    def ep(r, l, closed): return {"peak": str(ix[r].date()), "trough": str(ix[l].date()), "depth %": round(100 * (v[l] / v[r] - 1), 1), "sessions": int(l - r), "closed": closed}
    for i in range(1, len(v)):
        if v[i] > v[rec]:
            if v[lo] <= v[rec] * (1 - th): res.append(ep(rec, lo, True))
            rec = i; lo = i
        elif v[i] < v[lo]: lo = i
    if v[lo] <= v[rec] * (1 - th): res.append(ep(rec, lo, False))
    return res
rec_corr = record_episodes(s28, 0.10); bears = [e for e in rec_corr if e["depth %"] <= -20]; corr = rec_corr
zz_bears = [e for e in episodes(0.20) if e["depth %"] <= -20]; zz_corr = episodes(0.10)
months = pd.Series([pd.Timestamp(e["peak"]).month for e in bears]); nd = int(months.isin([11, 12]).sum())
out["P3 bear markets (>=20% from a record close, pre-registered, 1928-)"] = {"n": int(len(bears)), "peak month counts": {int(m): int(c) for m, c in months.value_counts().sort_index().items()},
    "peaks in Nov-Dec": nd, "share": round(nd / len(bears), 3), "expected share (2/12)": 0.167, "H-P3 binomial p (fewer than chance)": float(stats.binomtest(nd, len(bears), 2 / 12, alternative="less").pvalue),
    "peaks in Jan-Jun": int(months.isin(range(1, 7)).sum()), "list": bears}
cm = pd.DataFrame(corr); cm["month"] = pd.to_datetime(cm.peak).dt.month; cm["bear"] = cm["depth %"] <= -20; cm = cm[cm["closed"]]
son = cm[cm.month.isin([9, 10, 11])]; oth = cm[~cm.month.isin([9, 10, 11])]
out["P3 corrections (>=10% from a record close, pre-registered) by peak month"] = {"n": int(len(cm)), "Sep-Nov peaks: n / became >=20%": [int(len(son)), int(son.bear.sum())], "other months: n / became >=20%": [int(len(oth)), int(oth.bear.sum())],
    "share bear | Sep-Nov": round(float(son.bear.mean()), 3), "share bear | other": round(float(oth.bear.mean()), 3), "Fisher p": float(stats.fisher_exact([[son.bear.sum(), len(son) - son.bear.sum()], [oth.bear.sum(), len(oth) - oth.bear.sum()]])[1]),
    "Sep-Nov list": [f"{r.peak} {r['depth %']}%" for _, r in son.iterrows()], "all corrections": corr}
zm = pd.Series([pd.Timestamp(e["peak"]).month for e in zz_bears]); zc = pd.DataFrame(zz_corr); zc["month"] = pd.to_datetime(zc.peak).dt.month; zc["bear"] = zc["depth %"] <= -20
zs_, zo_ = zc[zc.month.isin([9, 10, 11])], zc[~zc.month.isin([9, 10, 11])]
out["P3 sensitivity: zigzag episodes (first run; includes rallies inside bear markets)"] = {"bears n": int(len(zz_bears)), "bear peaks in Nov-Dec": int(zm.isin([11, 12]).sum()),
    "binomial p (fewer than chance)": float(stats.binomtest(int(zm.isin([11, 12]).sum()), len(zz_bears), 2 / 12, alternative="less").pvalue), "peak month counts": {int(m): int(c) for m, c in zm.value_counts().sort_index().items()},
    "corrections n": int(len(zc)), "Sep-Nov n / bears": [int(len(zs_)), int(zs_.bear.sum())], "other n / bears": [int(len(zo_)), int(zo_.bear.sum())],
    "Fisher p": float(stats.fisher_exact([[zs_.bear.sum(), len(zs_) - zs_.bear.sum()], [zo_.bear.sum(), len(zo_) - zo_.bear.sum()]])[1]), "bear list": zz_bears}
json.dump(out, open(O / "history.json", "w"), indent=1, default=float)
print(json.dumps({k: v for k, v in out.items() if k not in ("P2 events (short z<=-1.75, long z>-1)",)}, indent=1, default=float)[:9000])
print("\nP2 events:"); [print(" ", k, v) for k, v in rows.items()]
