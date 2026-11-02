"""TSLA breaking-point event study (pre-registered @ 0bdce7d). Tops = 15%-reversal zigzag peaks after >= +30% legs; controls =
in-leg days >= 5 sessions before the top with prior 20-session return >= +15%. Features F1-F8 at t; post-top drift of IV/calls.
Usage: python breaking.py <TSLA yahoo json> <TSLA 1m parquet> <eod dir> <IRX json> -> out/results.json, out/features.csv"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, norm

HERE = Path(__file__).resolve().parent; AG = HERE.parent
r = json.load(open(sys.argv[1]))["chart"]["result"][0]
C = pd.Series(r["indicators"]["adjclose"][0]["adjclose"], index=pd.to_datetime(r["timestamp"], unit="s").normalize()).dropna()
C = C[~C.index.duplicated(keep="last")].loc["2020-06-01":]
# zigzag 15%
piv = []; mode = None; ext_i = 0
for i in range(1, len(C)):
    if mode is None:
        if C.iloc[i] >= C.iloc[ext_i] * 1.15: mode = "up"
        elif C.iloc[i] <= C.iloc[ext_i] * 0.85: mode = "down"
        if mode: piv.append((ext_i, "low" if mode == "up" else "high")); ext_i = i
        elif (C.iloc[i] < C.iloc[ext_i]) == True: pass
        continue
    if mode == "up":
        if C.iloc[i] > C.iloc[ext_i]: ext_i = i
        elif C.iloc[i] <= C.iloc[ext_i] * 0.85: piv.append((ext_i, "high")); mode = "down"; ext_i = i
    else:
        if C.iloc[i] < C.iloc[ext_i]: ext_i = i
        elif C.iloc[i] >= C.iloc[ext_i] * 1.15: piv.append((ext_i, "low")); mode = "up"; ext_i = i
tops, legs = [], []
for k in range(1, len(piv)):
    (i0, t0), (i1, t1) = piv[k - 1], piv[k]
    if t0 == "low" and t1 == "high" and C.iloc[i1] / C.iloc[i0] - 1 >= 0.30 and C.index[i1] >= pd.Timestamp("2020-08-01"):
        tops.append(i1); legs.append((i0, i1))
# features
D = pd.DataFrame(index=C.index)
g = pd.read_csv(AG.parents[0] / "microstructure" / "out" / "td_gamma_TSLA.csv", parse_dates=["date"]).set_index("date")
D["F1_callOI_growth5"] = np.log(g.call_oi / g.call_oi.shift(5)).reindex(D.index)
sig = pd.read_csv(AG / "2026-11-02-tsla-options-signal" / "out" / "signals.csv", index_col=0, parse_dates=True)
D["F2_call_share5"] = (sig.callvol.rolling(5).sum() / (sig.callvol + sig.putvol).rolling(5).sum()).reindex(D.index)
D["F3_skew_pct"] = sig.O2.rolling(252, min_periods=120).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True).reindex(D.index)
m = pd.read_parquet(sys.argv[2], columns=["close", "volume"]); m.index = m.index.tz_convert("America/New_York")
m = m[(m.index.time >= pd.Timestamp("09:30").time()) & (m.index.time < pd.Timestamp("16:00").time())]
m["day"] = m.index.normalize().tz_localize(None); m["dp"] = m.groupby("day").close.diff()
sd = m.groupby("day").dp.std().shift(1).rolling(5, min_periods=3).mean(); m["sig"] = m.day.map(sd); m["net"] = m.volume * (2 * norm.cdf(m.dp / m.sig) - 1)
B = m.groupby("day").agg(net=("net", "sum"), v=("volume", "sum")); imb = (B.net.rolling(5).sum() / B.v.rolling(5).sum()) - (B.net.shift(5).rolling(10).sum() / B.v.shift(5).rolling(10).sum())
D["F4_buy_aggr_change"] = imb.reindex(D.index)
gz = (g.gex_classic - g.gex_classic.rolling(252, min_periods=120).mean()) / g.gex_classic.rolling(252, min_periods=120).std(); D["F5_gex_z"] = gz.reindex(D.index)
D["F6_spot_vs_callwall_pct"] = (100 * (g.spot / g.call_wall - 1)).reindex(D.index)
def opex_after(d):
    for k in range(0, 3):
        y, mth = (d.year + (d.month + k - 1) // 12, (d.month + k - 1) % 12 + 1); f = pd.Timestamp(y, mth, 15); f += pd.Timedelta(days=(4 - f.weekday()) % 7)
        if f >= d: return f
D["F7_sessions_to_opex"] = [int(np.busday_count(d.date(), opex_after(d).date())) for d in D.index]
# F8 ATM IV (30d) from EOD chains
irx = json.load(open(sys.argv[4]))["chart"]["result"][0]; irx = pd.Series(irx["indicators"]["quote"][0]["close"], index=pd.to_datetime(irx["timestamp"], unit="s").normalize()).dropna() / 100
raw = m.groupby("day").close.last()
def bs(S, K, T, rr, s, call):
    d1 = (np.log(S / K) + (rr + s * s / 2) * T) / (s * np.sqrt(T)); d2 = d1 - s * np.sqrt(T)
    return np.where(call, S * norm.cdf(d1) - K * np.exp(-rr * T) * norm.cdf(d2), K * np.exp(-rr * T) * norm.cdf(-d2) - S * norm.cdf(-d1))
def iv(p, S, K, T, rr, call):
    lo, hi = np.full(len(p), .01), np.full(len(p), 5.)
    for _ in range(40):
        mid = (lo + hi) / 2; h = bs(S, K, T, rr, mid, call) > p; hi, lo = np.where(h, mid, hi), np.where(h, lo, mid)
    return (lo + hi) / 2
atm = {}
for f in sorted(Path(sys.argv[3]).glob("TSLA_*_eod.csv.gz")):
    e = pd.read_csv(f, usecols=["expiration", "strike", "right", "created", "bid", "ask"])
    e["date"] = pd.to_datetime(e.created.astype(str).str[:10]); e["expiration"] = pd.to_datetime(e.expiration); e["mid"] = (e.bid + e.ask) / 2
    for d, x in e.groupby("date"):
        if d not in raw.index: continue
        S = raw.loc[d]; x = x[(x.bid > 0) & (x.ask > 0)]; x = x.assign(dte=(x.expiration - d).dt.days); x = x[(x.dte >= 14) & (x.dte <= 60)]
        if x.empty: continue
        ex = x.expiration.iloc[(x.dte - 30).abs().argmin()]; y = x[(x.expiration == ex) & ((x.strike / S - 1).abs() <= 0.03)]
        if len(y) < 2: continue
        T = (ex - d).days / 365; rr = float(irx.asof(d)) if len(irx.loc[:d]) else 0.02
        atm[d] = float(np.nanmean(iv(y.mid.to_numpy(), S, y.strike.to_numpy(), np.full(len(y), T), rr, y.right.astype(str).str.upper().str.startswith("C").to_numpy())))
A = pd.Series(atm).sort_index(); D["ATM_IV"] = A.reindex(D.index); D["F8_atmIV_change5"] = D.ATM_IV - D.ATM_IV.shift(5)
D["past20"] = np.log(C).diff(20)
# events
ev = []
for (i0, i1) in legs:
    ev.append({"date": C.index[i1], "type": "top", "leg %": 100 * (C.iloc[i1] / C.iloc[i0] - 1)})
    for j in range(i0 + 20, i1 - 4):
        if D.past20.iloc[j] >= np.log(1.15): ev.append({"date": C.index[j], "type": "control", "leg %": np.nan})
E = pd.DataFrame(ev).set_index("date").join(D)
E.to_csv(HERE / "out" / "features.csv"); D.assign(close=C).to_csv(HERE / "out" / "daily.csv")
FEAT = ["F1_callOI_growth5", "F2_call_share5", "F3_skew_pct", "F4_buy_aggr_change", "F5_gex_z", "F6_spot_vs_callwall_pct", "F7_sessions_to_opex", "F8_atmIV_change5"]
PRED = {"F1_callOI_growth5": "less", "F3_skew_pct": "less", "F4_buy_aggr_change": "less", "F5_gex_z": "greater", "F7_sessions_to_opex": "less"}
res = {"tops": [{"date": str(d.date()), "leg %": round(float(v), 1)} for d, v in E[E.type == "top"]["leg %"].items()], "n tops": int((E.type == "top").sum()), "n control days": int((E.type == "control").sum())}
T, K = E[E.type == "top"], E[E.type == "control"]; raw_p = {}
for f in FEAT:
    a, b = T[f].dropna(), K[f].dropna()
    alt = PRED.get(f, "two-sided"); p = mannwhitneyu(a, b, alternative=alt).pvalue if len(a) > 2 and len(b) > 2 else np.nan
    res[f] = {"top median": round(float(a.median()), 4), "control median": round(float(b.median()), 4), "n tops with data": int(len(a)), "p (" + alt + ")": round(float(p), 4)}
    if f in PRED: raw_p[f] = p
ps = sorted(raw_p.items(), key=lambda kv: kv[1]); run = 0; holm = {}
for i, (k, p) in enumerate(ps): run = max(run, min(1, (len(ps) - i) * p)); holm[k] = round(run, 4)
res["Holm (5 directional)"] = holm
# post-top drift (descriptive): ATM IV, call share, call-OI growth over next 10 sessions
post = []
for d in T.index:
    i = D.index.get_loc(d)
    if i + 10 < len(D): post.append({"ATM IV change 10d (vol pts)": 100 * (D.ATM_IV.iloc[i + 10] - D.ATM_IV.iloc[i]), "call share change 10d (pts)": 100 * (D.F2_call_share5.iloc[i + 10] - D.F2_call_share5.iloc[i]),
                                     "call OI change 10d %": 100 * (np.exp(np.log(g.call_oi.reindex(D.index).iloc[i + 10] / g.call_oi.reindex(D.index).iloc[i])) - 1), "TSLA 10d %": 100 * (C.iloc[i + 10] / C.iloc[i] - 1)})
P = pd.DataFrame(post); res["after the top (median over tops)"] = P.median().round(2).to_dict()
cpost = []
for d in K.index:
    i = D.index.get_loc(d)
    if i + 10 < len(D): cpost.append({"ATM IV change 10d (vol pts)": 100 * (D.ATM_IV.iloc[i + 10] - D.ATM_IV.iloc[i]), "call share change 10d (pts)": 100 * (D.F2_call_share5.iloc[i + 10] - D.F2_call_share5.iloc[i])})
res["after control days (median)"] = pd.DataFrame(cpost).median().round(2).to_dict()
now = D.iloc[-1]; res["now (Oct 30)"] = {f: (round(float(now[f]), 4) if pd.notna(now[f]) else None) for f in FEAT}
json.dump(res, open(HERE / "out" / "results.json", "w"), indent=1, default=str)
print(json.dumps(res, indent=1, default=str))
print(T[FEAT].round(3).to_string())
