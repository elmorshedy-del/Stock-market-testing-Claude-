"""TSLA options-information test (pre-registered @ 6f0babf). O1 IV spread (Cremers-Weinbaum), O2 skew (Xing-Zhang-Zhao),
O3 put/call volume, O4 put/call OI; forward returns controlled for momentum and our gamma state.
Usage: python options_signal.py <eod dir> <TSLA 1m parquet> <TSLA yahoo json> <IRX yahoo json> -> out/signals.csv, out/results.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

HERE = Path(__file__).resolve().parent; rng = np.random.default_rng(29)


def yf(path, adj=False):
    r = json.load(open(path))["chart"]["result"][0]
    v = r["indicators"]["adjclose"][0]["adjclose"] if adj else r["indicators"]["quote"][0]["close"]
    s = pd.Series(v, index=pd.to_datetime(r["timestamp"], unit="s").normalize()).dropna(); return s[~s.index.duplicated(keep="last")]


def bs(S, K, T, r, sig, call):
    d1 = (np.log(S / K) + (r + sig ** 2 / 2) * T) / (sig * np.sqrt(T)); d2 = d1 - sig * np.sqrt(T)
    return np.where(call, S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2), K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1))


def iv(price, S, K, T, r, call, n=45):
    lo, hi = np.full(len(price), 0.01), np.full(len(price), 5.0)
    for _ in range(n):
        mid = (lo + hi) / 2; hi_ = bs(S, K, T, r, mid, call) > price; hi, lo = np.where(hi_, mid, hi), np.where(hi_, lo, mid)
    out = (lo + hi) / 2; out[(out < 0.02) | (out > 4.9)] = np.nan; return out


m = pd.read_parquet(sys.argv[2], columns=["close"]); m.index = m.index.tz_convert("America/New_York")
raw = m[m.index.time <= pd.Timestamp("15:59").time()].groupby(m.index[m.index.time <= pd.Timestamp("15:59").time()].normalize().tz_localize(None)).close.last()
adj = yf(sys.argv[3], adj=True); irx = yf(sys.argv[4]) / 100
rows = []
for f in sorted(Path(sys.argv[1]).glob("TSLA_*_eod.csv.gz")):
    e = pd.read_csv(f)
    e["date"] = pd.to_datetime(e.created.astype(str).str[:10]); e["expiration"] = pd.to_datetime(e.expiration)
    e["cp"] = np.where(e.right.astype(str).str.upper().str.startswith("C"), "C", "P"); e["mid"] = (e.bid + e.ask) / 2
    for d, g in e.groupby("date"):
        if d not in raw.index: continue
        S = float(raw.loc[d]); r = float(irx.asof(d)) if len(irx.loc[:d]) else 0.02
        g = g[(g.expiration > d)].copy(); g["dte"] = (g.expiration - d).dt.days; g["T"] = g.dte / 365
        vol = g[g.dte <= 60].groupby("cp").volume.sum()
        q = g[(g.bid > 0) & (g.ask > 0) & (g.mid >= 0.05) & (g.dte >= 7) & (g.dte <= 60) & (np.abs(np.log(g.strike / S)) <= 0.2)].copy()
        if len(q) < 10: continue
        q["iv"] = iv(q.mid.to_numpy(), S, q.strike.to_numpy(), q["T"].to_numpy(), r, (q.cp == "C").to_numpy())
        pv = q[(q.dte >= 10) & (np.abs(np.log(q.strike / S)) <= 0.10)].pivot_table(index=["expiration", "strike"], columns="cp", values="iv").dropna()
        o1 = float((pv["C"] - pv["P"]).mean()) if len(pv) else np.nan
        x = q[(q.dte >= 14)]; o2 = np.nan
        if len(x):
            ex = x.expiration.iloc[(x.dte - 30).abs().argmin()]; y = x[x.expiration == ex]
            pu = y[(y.cp == "P")].assign(mn=lambda z: (z.strike / S - 0.90).abs()); ca = y[(y.cp == "C")].assign(mn=lambda z: (z.strike / S - 1.0).abs())
            if len(pu) and len(ca) and pu.mn.min() <= 0.05 and ca.mn.min() <= 0.03:
                o2 = float(pu.loc[pu.mn.idxmin(), "iv"] - ca.loc[ca.mn.idxmin(), "iv"])
        rows.append({"date": d, "O1": o1, "O2": o2, "callvol": float(vol.get("C", 0)), "putvol": float(vol.get("P", 0)), "S": S})
X = pd.DataFrame(rows).set_index("date").sort_index()
X["O3"] = np.log(X.putvol.rolling(5).sum() / X.callvol.rolling(5).sum())
g = pd.read_csv(HERE.parents[1] / "microstructure" / "out" / "td_gamma_TSLA.csv", parse_dates=["date"]).set_index("date")
X["O4"] = np.log(g.put_oi / g.call_oi).reindex(X.index)
X["to_flip"] = (g.spot / g.flip_classic - 1).reindex(X.index)
gz = (g.gex_classic - g.gex_classic.rolling(252, min_periods=120).mean()) / g.gex_classic.rolling(252, min_periods=120).std(); X["gexz"] = gz.reindex(X.index)
la = np.log(adj).reindex(X.index)
X["past5"], X["past20"] = la.diff(5), la.diff(20)
for h in (5, 10, 20): X[f"f{h}"] = la.shift(-(1 + h)) - la.shift(-1)
X = X.loc["2020-07-01":]; X.to_csv(HERE / "out" / "signals.csv")
CTRL = ["past5", "past20", "to_flip", "gexz"]; SIG = ["O1", "O2", "O3", "O4"]


def ols(y, A): A1 = np.c_[np.ones(len(A)), A]; return np.linalg.lstsq(A1, y, rcond=None)[0]


res = {"n days": int(len(X)), "start": str(X.index[0].date()), "end": str(X.index[-1].date())}; raw_p = {}
for s in SIG:
    R = {}
    for h in ("f5", "f10", "f20"):
        D = X[[s, h] + CTRL].dropna(); z = (D[s] - D[s].mean()) / D[s].std()
        A = np.c_[z, D[CTRL].to_numpy()]; y = D[h].to_numpy(); b = ols(y, A)[1]; n = len(y); bs_ = []
        for _ in range(2000):
            st = rng.integers(0, n - 60, n // 60 + 1); ii = np.concatenate([np.arange(a, a + 60) for a in st])[:n]; bs_.append(ols(y[ii], A[ii])[1])
        bs_ = np.array(bs_); p = 2 * min((bs_ <= 0).mean(), (bs_ >= 0).mean())
        R[h] = {"slope % per sd (beyond momentum + gamma)": round(100 * b, 3), "95% CI": np.round(100 * np.quantile(bs_, [.025, .975]), 3).tolist(), "p": round(float(p), 4), "n": n}
        if h == "f10": raw_p[s] = p
        for lab, a, zz in (("R1 2020-21", "2020", "2021"), ("R2 2022+", "2022", "2027")):
            E = D.loc[a:zz]; ze = (E[s] - D[s].mean()) / D[s].std()
            R.setdefault(f"{h} slope by era", {})[lab] = round(100 * ols(E[h].to_numpy(), np.c_[ze, E[CTRL].to_numpy()])[1], 3)
    # OOS, 10 sessions: signal+controls vs controls only vs mean
    D = X[[s, "f10"] + CTRL].dropna(); idx = D.index; e_s, e_c, e_m = [], [], []
    for i in range(len(D)):
        if idx[i] < pd.Timestamp("2023-01-01") or i % 5: continue
        tr = D.iloc[:max(0, i - 11)]
        if len(tr) < 250: continue
        bs1 = ols(tr.f10.to_numpy(), tr[[s] + CTRL].to_numpy()); bc = ols(tr.f10.to_numpy(), tr[CTRL].to_numpy())
        y = D.f10.iloc[i]; e_s.append((y - bs1[0] - bs1[1:] @ D[[s] + CTRL].iloc[i].to_numpy()) ** 2); e_c.append((y - bc[0] - bc[1:] @ D[CTRL].iloc[i].to_numpy()) ** 2); e_m.append((y - tr.f10.mean()) ** 2)
    R["OOS R2 % 2023-26 (10 sessions)"] = {"signal+controls": round(100 * (1 - sum(e_s) / sum(e_m)), 2), "controls only": round(100 * (1 - sum(e_c) / sum(e_m)), 2), "n forecasts": len(e_s)}
    q1 = X[s].rolling(252, min_periods=150).quantile(1 / 3); q2 = X[s].rolling(252, min_periods=150).quantile(2 / 3)
    top, bot = X.loc[X[s] >= q2, "f10"].dropna(), X.loc[X[s] <= q1, "f10"].dropna()
    R["next 10 sessions: top third vs bottom third (trailing year)"] = [round(100 * top.mean(), 2), round(100 * bot.mean(), 2), int(len(top)), int(len(bot))]
    cur = X[s].dropna(); R["now (Oct 30)"] = {"value": round(float(cur.iloc[-1]), 4), "percentile vs trailing year": round(float((cur.iloc[-253:-1] < cur.iloc[-1]).mean()), 2)}
    res[s] = R
ps = sorted(raw_p.items(), key=lambda kv: kv[1]); run = 0; holm = {}
for i, (k, p) in enumerate(ps): run = max(run, min(1, (len(ps) - i) * p)); holm[k] = round(run, 4)
res["Holm (10 sessions, O1-O4)"] = holm
# owner's named bursts (day before) and named-move tops
NAMED = ["2024-06-17", "2024-07-01", "2024-10-24", "2024-11-06", "2025-04-23", "2025-05-12", "2025-05-27", "2025-09-11", "2025-10-06", "2025-10-13", "2025-11-24"]
TOPS = pd.read_csv(HERE.parent / "2026-10-16-named-moves-gamma" / "out" / "named_moves_table.csv").top.tolist()
def pct(s, d):
    d = pd.Timestamp(d); w = X[s].loc[:d].dropna()
    if len(w) < 60: return np.nan
    return round(float((w.iloc[-253:-1] < w.iloc[-1]).mean()), 2)
def daybefore(d): i = X.index.searchsorted(pd.Timestamp(d)); return X.index[i - 1]
res["named bursts: percentile the day before (O1 IVS, O2 SKEW)"] = {d: [pct("O1", daybefore(d)), pct("O2", daybefore(d))] for d in NAMED}
res["named tops: percentile on the top day (O1, O2)"] = {d: [pct("O1", d), pct("O2", d)] for d in TOPS if pd.Timestamp(d) >= X.index[0]}
json.dump(res, open(HERE / "out" / "results.json", "w"), indent=1, default=str)
print(json.dumps(res, indent=1, default=str))
