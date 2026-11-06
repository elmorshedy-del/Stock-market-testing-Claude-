"""M3 signature test (pre-registered @ f04844b). Usage: python test.py -> out/signature.json, out/shocks.csv"""
import json, importlib.util, numpy as np, pandas as pd
from pathlib import Path
H = Path(__file__).resolve().parent; O = H / "out"; O.mkdir(exist_ok=True)
spec = importlib.util.spec_from_file_location("prep", str(H / "prep.py")); prep = importlib.util.module_from_spec(spec); spec.loader.exec_module(prep)
NAMES = list(prep.SYMS); LONG = {"Nasdaq-100", "SOX"}

def table(nm, mult=6, iso=21, win=10, surrogates=0, rng=None):
    close = prep.load(nm); r = np.log(close).diff().dropna()
    sc = r.abs().rolling(1260, min_periods=1260).median().shift(1); ok = sc.notna(); r, sc = r[ok], sc[ok]
    a, rv, c = r.abs().values, r.values, close.reindex(r.index).values; N = len(rv)
    big, down = a >= mult * sc.values, rv <= -mult * sc.values; rows = []
    for i in np.where(down)[0]:
        if big[max(0, i - iso):i].any() or i < 70: continue
        base = a[i - 70:i - 10].mean(); B = a[i - win:i].mean() / base
        row = {"index": nm, "date": str(r.index[i].date()), "r0 %": round(100 * rv[i], 2), "size x": round(-rv[i] / sc.values[i], 1), "B": round(float(B), 3), "complete": bool(i + 89 < N)}
        if row["complete"]:
            E1 = a[i + 1:i + 21].mean() / base - 1; E2 = a[i + 21:i + 61].mean() / base - 1
            row.update({"E1": round(float(E1), 3), "E2": round(float(E2), 3), "P": round(float(E2 / E1), 3) if E1 > 0 else np.nan})
            j0 = i + int(np.argmin(c[i:i + 6])); low = c[j0]; later = c[i + 6:i + 90]; hit = np.where(later < 0.98 * low)[0]
            row["new leg"] = bool(len(hit)); row["pause"] = int(i + 6 + hit[0] - j0) if len(hit) else np.nan
            row["cum"] = (np.cumsum(a[i + 1:i + 61] / base - 1)).tolist(); row["pre"] = (a[i - 60:i] / base - 1).tolist()
            if surrogates:
                mu = rv[max(0, i - 1260):i].mean(); seg = rv[i + 6:i + 90]; s = rng.choice([-1.0, 1.0], size=(surrogates, len(seg)))
                path = c[i + 5] * np.exp(np.cumsum(mu + s * (seg - mu), axis=1)); row["expected leg"] = round(float((path < 0.98 * low).any(axis=1).mean()), 3)
        rows.append(row)
    return pd.DataFrame(rows)

def classes(df):
    df = df.copy(); df["cls"] = "mid"
    for nm, g in df[df.complete].groupby("index"):
        q1, q2 = np.quantile(g.B, [1 / 3, 2 / 3]); df.loc[g.index[g.B < q1], "cls"] = "abrupt"; df.loc[g.index[g.B > q2], "cls"] = "build-up"
    return df

def stats(d):
    b, ab = d[d.cls == "build-up"], d[d.cls == "abrupt"]
    return {"H1": float(np.nanmedian(b.P) - np.nanmedian(ab.P)), "H3": float(b["new leg"].mean() - ab["new leg"].mean())}

def permute(d, rng):
    d = d.copy()
    for nm, g in d.groupby("index"): d.loc[g.index, "cls"] = rng.permutation(g.cls.values)
    return d

if __name__ == "__main__":
    rng = np.random.default_rng(20261106); res = {"pre-registration": "f04844b"}
    full = pd.concat([table(nm, surrogates=2000, rng=rng) for nm in NAMES], ignore_index=True); full = classes(full)
    d = full[full.complete & (full.cls != "mid")].copy(); allc = full[full.complete]
    res["n complete / build-up / abrupt per index"] = {nm: [int((allc["index"] == nm).sum()), int(((d["index"] == nm) & (d.cls == "build-up")).sum()), int(((d["index"] == nm) & (d.cls == "abrupt")).sum())] for nm in NAMES}
    res["dropped (E1<=0)"] = int(d.P.isna().sum())
    obs = stats(d); perms = [stats(permute(d, rng)) for _ in range(10000)]
    for h in ("H1", "H3"):
        pv = np.array([p[h] for p in perms]); res[h] = {"observed": round(obs[h], 3), "one-sided permutation p": round(float((pv >= obs[h]).mean()), 4)}
    def boot_med(x, y, reps=5000):
        x, y = np.asarray(x, float), np.asarray(y, float); x, y = x[~np.isnan(x)], y[~np.isnan(y)]
        v = [np.median(rng.choice(x, len(x))) - np.median(rng.choice(y, len(y))) for _ in range(reps)]; return [round(float(np.percentile(v, 5)), 3), round(float(np.percentile(v, 95)), 3)]
    res["H1"]["median P build-up / abrupt"] = [round(float(np.nanmedian(d[d.cls == "build-up"].P)), 3), round(float(np.nanmedian(d[d.cls == "abrupt"].P)), 3)]
    res["H1"]["90% bootstrap CI of difference"] = boot_med(d[d.cls == "build-up"].P, d[d.cls == "abrupt"].P)
    res["H3"]["new-leg rate build-up / abrupt / middle"] = [round(float(d[d.cls == "build-up"]["new leg"].mean()), 3), round(float(d[d.cls == "abrupt"]["new leg"].mean()), 3), round(float(allc[allc.cls == "mid"]["new leg"].mean()), 3)]
    # per index
    per = {}
    for nm in NAMES:
        g = d[d["index"] == nm]; b, ab = g[g.cls == "build-up"], g[g.cls == "abrupt"]
        per[nm] = {"median P build-up / abrupt": [round(float(np.nanmedian(b.P)), 3), round(float(np.nanmedian(ab.P)), 3)], "gap": round(float(np.nanmedian(b.P) - np.nanmedian(ab.P)), 3),
                   "new-leg build-up / abrupt": [f"{int(b['new leg'].sum())}/{len(b)}", f"{int(ab['new leg'].sum())}/{len(ab)}"]}
    res["per index"] = per
    # H2: memory condition, cluster bootstrap over shock dates
    def gap(g): return np.nanmedian(g[g.cls == "build-up"].P) - np.nanmedian(g[g.cls == "abrupt"].P)
    lg, sp = d[d["index"].isin(LONG)], d[d["index"] == "S&P 500"]; dobs = gap(lg) - gap(sp); dates = d.date.unique(); vb = []
    for _ in range(10000):
        pick = rng.choice(dates, len(dates)); bb = pd.concat([d[d.date == x] for x in pick]) if False else d.set_index("date").loc[pick].reset_index()
        l2, s2 = bb[bb["index"].isin(LONG)], bb[bb["index"] == "S&P 500"]
        if min((l2.cls == "build-up").sum(), (l2.cls == "abrupt").sum(), (s2.cls == "build-up").sum(), (s2.cls == "abrupt").sum()) == 0: continue
        vb.append(gap(l2) - gap(s2))
    res["H2"] = {"gap long-memory (NDX+SOX) minus gap S&P": round(float(dobs), 3), "90% CI": [round(float(np.nanpercentile(vb, 5)), 3), round(float(np.nanpercentile(vb, 95)), 3)],
                 "gap long-memory / S&P": [round(float(gap(lg)), 3), round(float(gap(sp)), 3)]}
    # O2x: direction beyond volatility
    ex = d["new leg"].astype(float) - d["expected leg"]; eb, ea = ex[d.cls == "build-up"].mean(), ex[d.cls == "abrupt"].mean()
    pe = []
    for _ in range(10000):
        dp = permute(d, rng); e2 = dp["new leg"].astype(float) - dp["expected leg"]; pe.append(e2[dp.cls == "build-up"].mean() - e2[dp.cls == "abrupt"].mean())
    pe = np.array(pe); res["O2x excess new-leg rate over random-sign paths"] = {"build-up": round(float(eb), 3), "abrupt": round(float(ea), 3), "all complete": round(float((allc["new leg"].astype(float) - allc["expected leg"]).mean()), 3),
        "expected rate build-up / abrupt": [round(float(d[d.cls == 'build-up']['expected leg'].mean()), 3), round(float(d[d.cls == 'abrupt']['expected leg'].mean()), 3)],
        "two-sided permutation p (difference)": round(float((np.abs(pe) >= abs(eb - ea)).mean()), 4)}
    # O3 pause length
    res["O3 pause sessions (median, among new legs) build-up / abrupt"] = [float(np.nanmedian(d[(d.cls == "build-up") & d["new leg"]].pause)), float(np.nanmedian(d[(d.cls == "abrupt") & d["new leg"]].pause))]
    # O4 decay exponent from class-average cumulative excess
    t = np.arange(1, 61); o4 = {}
    for cl in ("build-up", "abrupt"):
        for grp, sel in (("all", d.cls == cl), ("S&P", (d.cls == cl) & (d["index"] == "S&P 500")), ("NDX+SOX", (d.cls == cl) & d["index"].isin(LONG))):
            cm = np.mean(np.vstack(d[sel].cum.values), axis=0); okk = cm > 0
            o4[f"{cl} {grp}"] = round(float(1 - np.polyfit(np.log(t[okk]), np.log(cm[okk]), 1)[0]), 3) if okk.sum() > 10 else None
    res["O4 decay exponent alpha (1 - slope of cumulative excess)"] = o4
    # multiverse joint p
    specs = [(m, s, w) for m in (5, 6, 8) for s in (21, 42) for w in (5, 10, 20)]; K = 2000; zs = {"H1": [], "H3": []}; zperm = {"H1": np.zeros((len(specs), K)), "H3": np.zeros((len(specs), K))}; mv = []
    for si, (m, s, w) in enumerate(specs):
        ff = classes(pd.concat([table(nm, m, s, w) for nm in NAMES], ignore_index=True)); dd = ff[ff.complete & (ff.cls != "mid")].copy(); o = stats(dd)
        pp = [stats(permute(dd, np.random.default_rng(10_000 + k))) for k in range(K)]
        row = {"spec": f"{m}x, iso {s}, win {w}", "n": int(len(dd))}
        for h in ("H1", "H3"):
            v = np.array([p[h] for p in pp]); mu, sd = v.mean(), v.std() + 1e-12; zs[h].append((o[h] - mu) / sd); zperm[h][si] = (v - mu) / sd
            row[h] = round(o[h], 3); row[h + " p"] = round(float((v >= o[h]).mean()), 3)
        mv.append(row)
    res["multiverse"] = mv
    res["multiverse joint p (mean z)"] = {h: round(float((zperm[h].mean(axis=0) >= np.mean(zs[h])).mean()), 4) for h in ("H1", "H3")}
    # live forecast: the 2026-11-05 shock
    live = {}
    for nm in NAMES:
        g = full[full["index"] == nm]; cur = g[~g.complete].tail(1); cc = g[g.complete]; q1, q2 = np.quantile(cc.B, [1 / 3, 2 / 3])
        if len(cur):
            B = float(cur.B.iloc[0]); cls = "build-up" if B > q2 else ("abrupt" if B < q1 else "mid"); ref = cc[cc.cls == cls]
            live[nm] = {"date": cur.date.iloc[0], "B": round(B, 3), "tercile cut-offs": [round(float(q1), 3), round(float(q2), 3)], "class": cls,
                        "class base rates: median P / new-leg rate / n": [round(float(np.nanmedian(ref.P)), 3), round(float(ref["new leg"].mean()), 3), int(len(ref))]}
    res["live forecast (score after day 89, ~2027-03)"] = live
    res["named events"] = full[full.date.isin(["1987-10-19", "2001-09-17", "2008-09-29", "2010-05-06", "2011-08-04", "2020-02-24", "2020-03-09", "2025-04-03", "2026-06-05"])][["index", "date", "r0 %", "B", "cls", "P", "new leg"]].to_dict("records")
    full.drop(columns=["cum", "pre"]).to_csv(O / "shocks.csv", index=False)
    pd.to_pickle(full, H / "data" / "full.pkl")
    json.dump(res, open(O / "signature.json", "w"), indent=1, default=str); print(json.dumps(res, indent=1, default=str))
