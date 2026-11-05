"""Fast-drop extremes -> bounce or bottom (pre-registered, see README). Usage: python extremes.py"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "2026-11-05-liquidity-cycle"))
from common import yahoo
O = Path(__file__).resolve().parent / "out"; rng = np.random.default_rng(5)
def rsi(c, n=14):
    d = c.diff(); up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean(); dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean(); return 100 - 100 / (1 + up / dn)
def build(sym, start):
    c = yahoo(sym, start).close; r = c.pct_change(); sig = r.rolling(60).std().shift(1)
    d = pd.DataFrame({"c": c, "z1": r / sig, "z5": (c / c.shift(5) - 1) / (sig * np.sqrt(5)), "rsi": rsi(c), "ma200": c.rolling(200).mean()})
    for k in (5, 10, 20, 60): d[f"f{k}"] = c.shift(-k) / c - 1
    fmin = pd.concat([c.shift(-k) for k in range(1, 21)], axis=1).min(axis=1)
    d["held"] = np.where(fmin.notna() & (c.shift(-20).notna()), (fmin >= c).astype(float), np.nan); d["dd20"] = fmin / c - 1
    return d
def episodes(flag, gap=20):
    idx = np.where(flag.values)[0]; keep, last = [], -10**9
    for i in idx:
        if i - last > gap: keep.append(i)
        last = i
    return keep
def summarize(d, ep):
    E = d.iloc[ep]; Ec = E[E.f10.notna()]
    pct = lambda x: round(100 * float(x), 2)
    out = {"episodes": int(len(E)), "completed": int(len(Ec))}
    for k in (5, 10, 20, 60):
        x = Ec[f"f{k}"].dropna(); out[f"fwd{k}"] = {"median %": pct(x.median()), "mean %": pct(x.mean()), "share up": round(float((x > 0).mean()), 3), "base mean %": pct(d[f"f{k}"].mean()), "base share up": round(float((d[f"f{k}"] > 0).mean()), 3)}
    h = Ec.held.dropna(); b = [rng.choice(h.values, len(h)).mean() for _ in range(5000)]
    out["low held 20s"] = {"share": round(float(h.mean()), 3), "90% CI": [round(float(np.percentile(b, 5)), 3), round(float(np.percentile(b, 95)), 3)], "base": round(float(d.held.mean()), 3)}
    out["further drawdown 20s median %"] = pct(Ec.dd20.median())
    return out
def shift_p(d, ep):
    f = d.f10.values; ok = ~np.isnan(f); obs = np.nanmean(f[ep]) if len(ep) else np.nan; base = np.nanmean(f)
    n = len(f); sims = []
    for _ in range(5000):
        s = rng.integers(60, n - 60); e2 = [(i + s) % n for i in ep]; sims.append(np.nanmean(f[e2]))
    return float(obs - base), float((np.array(sims) >= obs).mean())
R = {}; P = {}
for sym, start, lab in (("^NDX", "1990-01-01", "NDX"), ("^SOX", "1994-05-01", "SOX"), ("^GSPC", "1990-01-01", "SPX")):
    d = build(sym, start); d = d[d.index >= d.index[0] + pd.Timedelta(days=100)]
    hist = d.iloc[:-1]  # exclude today (live) from outcomes
    res = {}
    for nm, flag in (("fast drop: 5d z <= -3", hist.z5 <= -3.0), ("1-day z <= -3.5", hist.z1 <= -3.5), ("RSI14 <= 30", hist.rsi <= 30)):
        ep = episodes(flag); s = summarize(hist, ep)
        if nm.startswith("fast"):
            diff, p = shift_p(hist, ep); s["H1 fwd10 diff vs base %"] = round(100 * diff, 2); s["H1 p (circular shift)"] = p
            if lab in ("NDX", "SOX"): P[lab] = p  # pre-registered: Holm over NDX and SOX only (SPX is context)
            E = hist.iloc[ep]
            above = [i for i in ep if hist.c.iloc[i] >= hist.ma200.iloc[i]]; below = [i for i in ep if hist.c.iloc[i] < hist.ma200.iloc[i]]
            bust = [i for i in ep if hist.index[i].year in (2000, 2001, 2002, 2008)]; rest = [i for i in ep if hist.index[i].year not in (2000, 2001, 2002, 2008)]
            s["split above 200d"] = summarize(hist, above); s["split below 200d"] = summarize(hist, below)
            s["split bust yrs 2000-02,2008"] = summarize(hist, bust); s["split other yrs"] = summarize(hist, rest)
            s["episode list"] = {str(hist.index[i].date()): {"z5": round(float(hist.z5.iloc[i]), 2), "above200": bool(hist.c.iloc[i] >= hist.ma200.iloc[i]),
                                 "fwd10 %": None if np.isnan(hist.f10.iloc[i]) else round(100 * float(hist.f10.iloc[i]), 1),
                                 "fwd60 %": None if np.isnan(hist.f60.iloc[i]) else round(100 * float(hist.f60.iloc[i]), 1),
                                 "low held": None if np.isnan(hist.held.iloc[i]) else bool(hist.held.iloc[i])} for i in ep}
        res[nm] = s
    t = d.iloc[-1]; res["TODAY"] = {"z1": round(float(t.z1), 2), "z5": round(float(t.z5), 2), "rsi": round(float(t.rsi), 1), "above200": bool(t.c >= t.ma200)}
    R[lab] = res
order = sorted(P, key=P.get); run = 0; R["Holm H1 (NDX, SOX)"] = {}
for i, k in enumerate(order): run = max(run, min(1, (len(P) - i) * P[k])); R["Holm H1 (NDX, SOX)"][k] = {"p": round(P[k], 4), "adj": round(run, 4), "PASS": bool(run < 0.05)}
json.dump(R, open(O / "extremes.json", "w"), indent=1, default=float)
for lab in ("NDX", "SOX", "SPX"):
    s = R[lab]["fast drop: 5d z <= -3"]
    print(lab, "fast-drop episodes", s["episodes"], "| fwd10 median", s["fwd10"]["median %"], "up", s["fwd10"]["share up"], "base up", s["fwd10"]["base share up"], "| fwd60 median", s["fwd60"]["median %"], "up", s["fwd60"]["share up"], "base", s["fwd60"]["base share up"], "| low held", s["low held 20s"], "| ddmed", s["further drawdown 20s median %"], "| H1", s.get("H1 fwd10 diff vs base %"), s.get("H1 p (circular shift)"))
    for sp in ("split above 200d", "split below 200d", "split bust yrs 2000-02,2008", "split other yrs"):
        x = s[sp]; print("   ", sp, "n", x["episodes"], "fwd10 med", x["fwd10"]["median %"] if x["completed"] else None, "up", x["fwd10"]["share up"] if x["completed"] else None, "| fwd60 med", x["fwd60"]["median %"] if x["completed"] else None, "up", x["fwd60"]["share up"] if x["completed"] else None, "| held", x["low held 20s"]["share"] if x["completed"] else None)
    for nm in ("1-day z <= -3.5", "RSI14 <= 30"):
        x = R[lab][nm]; print("   ", nm, "n", x["episodes"], "fwd10 med", x["fwd10"]["median %"], "up", x["fwd10"]["share up"], "| held", x["low held 20s"]["share"], "base", x["low held 20s"]["base"])
    print("   TODAY", R[lab]["TODAY"])
print(R["Holm H1 (NDX, SOX)"])
