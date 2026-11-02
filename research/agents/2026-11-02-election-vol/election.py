"""Election-vol study (pre-registered @ 3d583b1). Usage: python election.py <ev dir> <poly dir> <yahoo dir> -> out/results.json, out/october.csv"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

HERE = Path(__file__).resolve().parent; EV, PD, YD = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]); rng = np.random.default_rng(41)
HOL = ["2022-11-24", "2024-11-28", "2026-11-26", "2026-12-25", "2024-12-25", "2022-12-26"]


def yfs(t, col="close"):
    r = json.load(open(YD / f"el_{t}.json"))["chart"]["result"][0]
    s = pd.Series(r["indicators"]["quote"][0][col], index=pd.to_datetime(r["timestamp"], unit="s").tz_localize("UTC").tz_convert("America/New_York").normalize().tz_localize(None))
    return s[~s.index.duplicated(keep="last")].dropna()


irx = json.load(open(YD.parent / "yf" / "IRX.json"))["chart"]["result"][0] if (YD.parent / "yf" / "IRX.json").exists() else json.load(open(YD / "IRX.json"))["chart"]["result"][0]
irx = pd.Series(irx["indicators"]["quote"][0]["close"], index=pd.to_datetime(irx["timestamp"], unit="s").normalize()).dropna() / 100


def b76(F, K, T, s, call):
    d1 = (np.log(F / K) + s * s * T / 2) / (s * np.sqrt(T)); d2 = d1 - s * np.sqrt(T)
    return np.where(call, F * norm.cdf(d1) - K * norm.cdf(d2), K * norm.cdf(-d2) - F * norm.cdf(-d1))


def iv(p, F, K, T, call):
    lo, hi = np.full(len(p), .01), np.full(len(p), 3.)
    for _ in range(50):
        m = (lo + hi) / 2; h = b76(F, K, T, m, call) > p; hi, lo = np.where(h, m, hi), np.where(h, lo, m)
    return (lo + hi) / 2


def term(day_df, d):
    """total implied variance w(e) = sigma_ATM^2 * T_cal for each expiry after d"""
    r = float(irx.asof(d)); out = {}
    for e, x in day_df.groupby("expiration"):
        if e <= d: continue
        T = (e - d).days / 365; x = x[(x.bid > 0) & (x.ask > 0)]
        pv = x.pivot_table(index="strike", columns="cp", values="mid").dropna()
        if len(pv) < 4: continue
        k = (pv.C - pv.P).abs().idxmin(); F = k + np.exp(r * T) * (pv.loc[k, "C"] - pv.loc[k, "P"])
        near = pv.iloc[(pv.index - F).to_series().abs().argsort()[:2].to_numpy()]
        Ks = np.r_[near.index, near.index]; prices = np.r_[near.C, near.P] * np.exp(r * T); calls = np.r_[np.ones(len(near), bool), np.zeros(len(near), bool)]
        s = np.nanmean(iv(prices, F, Ks, T, calls)); out[e] = {"T": T, "w": s * s * T, "iv": s, "F": F}
    return pd.DataFrame(out).T.sort_index()


def sessions(a, b):  # sessions in (a, b]
    return int(np.busday_count((a + pd.Timedelta(days=1)).date(), (b + pd.Timedelta(days=1)).date(), holidays=HOL))


def load(tag):
    e = pd.read_csv(EV / f"SPY_eod_{tag}.csv.gz")
    e["date"] = pd.to_datetime(e.created.astype(str).str[:10]); e["expiration"] = pd.to_datetime(e.expiration)
    e["cp"] = np.where(e.right.astype(str).str.upper().str.startswith("C"), "C", "P"); e["mid"] = (e.bid + e.ask) / 2
    return e


def election_excess(tw, d, elec, after_from):
    """excess variance of the results session `elec`; baseline = median per-session variance of pairs starting on/after `after_from`"""
    ex = list(tw.index); res = {}
    base = []
    for a, b in zip(ex[:-1], ex[1:]):
        if a >= after_from:
            n = sessions(a, b)
            if n >= 1: base.append((tw.loc[b, "w"] - tw.loc[a, "w"]) / n)
    if not base: return None
    bl = float(np.median(base))
    before = [e for e in ex if e < elec]; after = [e for e in ex if e >= elec]
    if not before or not after: return None
    e1, e2 = max(before), min(after); n = sessions(e1, e2)
    v = tw.loc[e2, "w"] - tw.loc[e1, "w"]; excess = v - n * bl
    return {"pair": f"{e1.date()}->{e2.date()}", "sessions in pair": n, "pair variance": v, "baseline per session": bl, "excess": excess,
            "implied move of results session %": 100 * np.sqrt(max(bl + excess, 0)), "normal session move %": 100 * np.sqrt(bl)}


res = {}
# ---------- A1 + A2 (2026)
E26 = load("2026"); rows = []; ELEC26 = pd.Timestamp("2026-11-04")
for d, x in E26.groupby("date"):
    tw = term(x, d)
    if tw.empty: continue
    w30 = np.interp(30 / 365, tw["T"].astype(float), tw["w"].astype(float)); iv30 = np.sqrt(w30 / (30 / 365))
    ee = election_excess(tw, d, ELEC26, pd.Timestamp("2026-11-06"))
    row = {"date": d, "IV30 %": 100 * iv30}
    if ee:
        exc = max(ee["excess"], 0) if (ELEC26 - d).days <= 30 else 0.0
        row.update({"pair": ee["pair"], "election excess var": ee["excess"], "results-session move %": ee["implied move of results session %"], "normal session move %": ee["normal session move %"],
                    "IV30 ex-election %": 100 * np.sqrt(max(w30 - exc, 1e-9) / (30 / 365))})
        row["election share of IV30, vol pts"] = row["IV30 %"] - row["IV30 ex-election %"]
    rows.append(row)
O = pd.DataFrame(rows).set_index("date"); O.to_csv(HERE / "out" / "october.csv")
d30 = pd.Timestamp("2026-10-30"); tw = term(E26[E26.date == d30], d30)
sess = []
ex = list(tw.index)
for a, b in zip(ex[:-1], ex[1:]):
    if b <= pd.Timestamp("2026-11-13"):
        n = sessions(a, b); v = tw.loc[b, "w"] - tw.loc[a, "w"]; sess.append({"pair": f"{a.date()}->{b.date()}", "sessions": n, "per-session move %": round(100 * np.sqrt(max(v / n, 0)), 3)})
first = ex[0]; sess.insert(0, {"pair": f"2026-10-30->{first.date()}", "sessions": sessions(d30, first), "per-session move %": round(100 * np.sqrt(tw.loc[first, "w"] / max(sessions(d30, first), 1)), 3)})
A1 = election_excess(tw, d30, ELEC26, pd.Timestamp("2026-11-06"))
res["A1 Oct 30 per-session implied moves (SPY)"] = sess
res["A1 election session (Nov 4)"] = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in A1.items()}
res["A1 verdict (excess > 20% of baseline variance)"] = bool(A1["excess"] > 0.2 * A1["baseline per session"])
o = O.dropna(subset=["election excess var"])
res["A2 October"] = {"IV30 first / Oct 9 / Oct 30 %": [round(float(O["IV30 %"].iloc[0]), 2), round(float(O.loc[:"2026-10-09", "IV30 %"].iloc[-1]), 2), round(float(O["IV30 %"].iloc[-1]), 2)],
                     "election share of IV30 (vol pts) first / Oct 9 / Oct 30": [round(float(o["election share of IV30, vol pts"].iloc[0]), 2), round(float(o.loc[:"2026-10-09", "election share of IV30, vol pts"].iloc[-1]), 2), round(float(o["election share of IV30, vol pts"].iloc[-1]), 2)],
                     "first date with an election estimate": str(o.index[0].date()), "pairs used (first, last)": [o.pair.iloc[0], o.pair.iloc[-1]]}
# ---------- A3 precedents
vix = yfs("%5EVIX"); spy = yfs("SPY")
for tag, vote, results, evald, after_from in (("2022", "2022-11-08", "2022-11-09", "2022-11-03", "2022-11-11"), ("2024", "2024-11-05", "2024-11-06", "2024-10-31", "2024-11-08")):
    E = load(tag); d = pd.Timestamp(evald); tw = term(E[E.date == d], d); ee = election_excess(tw, d, pd.Timestamp(results), pd.Timestamp(after_from))
    R = pd.Timestamp(results); pre = spy.index[spy.index < R][-1]
    iv_pre = term(E[E.date == pre], pre); iv_post = term(E[E.date == R], R)
    def iv30(t): return float(np.sqrt(np.interp(30 / 365, t["T"].astype(float), t["w"].astype(float)) / (30 / 365)))
    post3 = spy.index[spy.index > R][2] if (spy.index > R).sum() > 2 else None
    out = {"evaluated on": evald, "pair": ee["pair"], "sessions in pair": ee["sessions in pair"],
           "implied excess move of election sessions %": round(100 * np.sqrt(max(ee["excess"], 0)), 3), "normal session move %": round(ee["normal session move %"], 3),
           "realised SPY on the results session %": round(float(100 * (spy.loc[R] / spy.loc[pre] - 1)), 2),
           "VIX day before -> results day -> +3 sessions": [round(float(vix.loc[pre]), 2), round(float(vix.loc[R]), 2), round(float(vix.loc[post3]), 2) if post3 is not None else None],
           "SPY IV30 day before -> results day %": [round(100 * iv30(iv_pre), 2), round(100 * iv30(iv_post), 2)]}
    res[f"A3 {tag}"] = out
# 2026 on Oct 29 (T-3 sessions before the vote) for comparability
d29 = pd.Timestamp("2026-10-29"); ee29 = election_excess(term(E26[E26.date == d29], d29), d29, ELEC26, pd.Timestamp("2026-11-06"))
res["A3 2026 (Oct 29, T-3)"] = {"pair": ee29["pair"], "implied excess move of election session %": round(100 * np.sqrt(max(ee29["excess"], 0)), 3), "normal session move %": round(ee29["normal session move %"], 3)}
# ---------- Part B
def poly(key, lab):
    d = json.load(open(PD / f"{key}.json"))[lab]; s = pd.Series(dict(d)); s.index = pd.to_datetime(s.index.astype(int), unit="s", utc=True).tz_convert("America/New_York").tz_localize(None)
    s = s.sort_index(); return s
def at16(s, days): return pd.Series([s.loc[:d + pd.Timedelta(hours=16)].iloc[-1] if len(s.loc[:d + pd.Timedelta(hours=16)]) else np.nan for d in days], index=days)
SECT = ["XLF", "KRE", "IWM", "XLE", "ITA", "XLV", "XBI", "TAN", "ICLN", "XLU", "TLT", "DX-Y.NYB", "BTC-USD", "TSLA", "SPY", "QQQ"]
RET = pd.DataFrame({t: np.log(yfs(t)).diff() for t in SECT}); RET["10y bp"] = yfs("%5ETNX").diff() * 100
def betas(dp, label, win):
    out = {}; raw = {}
    for t in SECT + ["10y bp"]:
        D = pd.concat([RET[t], dp], axis=1).loc[win[0]:win[1]].dropna(); D.columns = ["y", "x"]
        X = np.c_[np.ones(len(D)), D.x / 0.10]; b = np.linalg.lstsq(X, D.y.to_numpy(), rcond=None)[0][1]; n = len(D); bs = []
        for _ in range(2000):
            st = rng.integers(0, n - 5, n // 5 + 1); ii = np.concatenate([np.arange(a, a + 5) for a in st])[:n]; bs.append(np.linalg.lstsq(X[ii], D.y.to_numpy()[ii], rcond=None)[0][1])
        bs = np.array(bs); p = float(2 * min((bs <= 0).mean(), (bs >= 0).mean())); unit = 1 if t == "10y bp" else 100
        out[t] = {"per +10 pts": round(unit * b, 3), "p": round(p, 4)}; raw[t] = p
    ps = sorted(raw.items(), key=lambda kv: kv[1]); run = 0
    for i, (k, p) in enumerate(ps): run = max(run, min(1, (len(ps) - i) * p)); out[k]["Holm"] = round(run, 4)
    return out
days26 = RET.loc["2026-07-31":"2026-10-30"].index; days24 = RET.loc["2024-07-31":"2024-11-05"].index
pH = at16(poly("house26", "Republican Party"), days26); pS = at16(poly("senate26", "Republican Party"), days26); pT = at16(poly("pres24", "Donald Trump"), days24)
res["B2 2026: P(R House) betas"] = betas(pH.diff(), "house", ("2026-08-01", "2026-10-30"))
res["B2 2026: P(R Senate) betas"] = betas(pS.diff(), "senate", ("2026-08-01", "2026-10-30"))
res["B2 2024: P(Trump) betas"] = betas(pT.diff(), "trump", ("2024-08-01", "2024-11-05"))
# validation: 2024 betas x (1 - p_Nov5) vs actual Nov 6 2024 moves
p5 = float(pT.iloc[-1]); B24 = res["B2 2024: P(Trump) betas"]
act = {t: (float(100 * RET.loc["2024-11-06", t]) if t != "10y bp" else float(RET.loc["2024-11-06", t])) for t in SECT + ["10y bp"]}
pred = {t: B24[t]["per +10 pts"] * (1 - p5) / 0.10 for t in SECT + ["10y bp"]}
pa = pd.DataFrame({"predicted": pred, "actual Nov 6 2024": act})
res["B2 2024 validation: predicted vs actual Nov 6 moves"] = {"P(Trump) at Nov 5 16:00": round(p5, 3), "corr across assets": round(float(pa.corr().iloc[0, 1]), 3),
                                                             "sign agreement": f"{int((np.sign(pa.predicted) == np.sign(pa['actual Nov 6 2024'])).sum())} of {len(pa)}", "table": pa.round(2).to_dict("index")}
# B1: closeness vs election excess (October 2026)
cl = pd.DataFrame({"senate closeness": 4 * pS * (1 - pS), "house closeness": 4 * pH * (1 - pH)}).reindex(o.index)
res["B1 corr(election excess var, Senate closeness) Oct 2026"] = round(float(pd.concat([o["election excess var"], cl["senate closeness"]], axis=1).dropna().corr().iloc[0, 1]), 3)
res["B1 n days"] = int(len(o))
# now: outcome odds
bop = json.load(open(PD / "bop26.json")); now = {k: round(float(pd.Series(dict(v)).sort_index().iloc[-1]), 3) for k, v in bop.items()}
res["now: Balance of Power odds"] = now; res["now: P(R House), P(R Senate)"] = [round(float(poly("house26", "Republican Party").iloc[-1]), 3), round(float(poly("senate26", "Republican Party").iloc[-1]), 3)]
json.dump(res, open(HERE / "out" / "results.json", "w"), indent=1, default=str)
print(json.dumps({k: v for k, v in res.items() if "table" not in str(k)}, indent=1, default=str)[:12000])
print(O.round(3).to_string())
