"""TSLA politics study (pre-registered @ 3711f29).
Usage: python politics.py <scratch dir: yf/, poly/, poly_races/, n2/td/, n3/eod/> -> out/results.json, out/daily26.csv"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

HERE = Path(__file__).resolve().parent; S = Path(sys.argv[1]); rng = np.random.default_rng(43)
HOL = ["2024-11-28", "2024-12-25", "2026-11-26", "2026-12-25"]


def ycl(f):
    r = json.load(open(S / "yf" / f))["chart"]["result"][0]
    v = r["indicators"]["adjclose"][0]["adjclose"] if "adjclose" in r["indicators"] else r["indicators"]["quote"][0]["close"]
    s = pd.Series(v, index=pd.to_datetime(r["timestamp"], unit="s", utc=True).tz_convert("America/New_York").normalize().tz_localize(None))
    return s[~s.index.duplicated(keep="last")].dropna()


R = pd.concat([ycl("TSLA.json").pct_change(), ycl("QQQ.json").pct_change()], axis=1).dropna(); R.columns = ["T", "Q"]


def beta_to(end):
    est = R.loc[:end].iloc[-250:]; return float(np.polyfit(est.Q, est["T"], 1)[0])


def pser(path, lab):
    d = json.load(open(path))[lab]; s = pd.Series({int(t): p for t, p in d})
    s.index = pd.to_datetime(s.index, unit="s", utc=True).tz_convert("America/New_York").tz_localize(None); return s.sort_index()


def at16(s, days): return pd.Series([s.loc[:d + pd.Timedelta(hours=16)].iloc[-1] if len(s.loc[:d + pd.Timedelta(hours=16)]) else np.nan for d in days], index=days)


def slope(y, x, reps=2000):
    D = pd.concat([y, x], axis=1).dropna(); D.columns = ["y", "x"]; n = len(D)
    X = np.c_[np.ones(n), D.x / 0.10]; Y = D.y.to_numpy(); b = np.linalg.lstsq(X, Y, rcond=None)[0][1]; bs = []
    for _ in range(reps):
        st = rng.integers(0, n - 5, n // 5 + 1); ii = np.concatenate([np.arange(a, a + 5) for a in st])[:n]
        bs.append(np.linalg.lstsq(X[ii], Y[ii], rcond=None)[0][1])
    bs = np.array(bs); se = float(bs.std())
    return {"per +10 pts %": round(100 * b, 2), "p": round(float(2 * min((bs <= 0).mean(), (bs >= 0).mean())), 4), "SE %": round(100 * se, 2),
            "detectable at 80% power, per +10 pts %": round(100 * 2.8 * se, 2), "95% CI %": [round(100 * float(np.percentile(bs, 2.5)), 2), round(100 * float(np.percentile(bs, 97.5)), 2)],
            "n": n, "_b": b, "_lo": float(np.percentile(bs, 2.5)), "_hi": float(np.percentile(bs, 97.5))}


def holm(d):
    ps = sorted(((k, v["p"]) for k, v in d.items()), key=lambda kv: kv[1]); run = 0
    for i, (k, p) in enumerate(ps): run = max(run, min(1, (len(ps) - i) * p)); d[k]["Holm"] = round(run, 4)


res = {}
# ---- P1-P3: 2026 ----
b26 = beta_to("2026-08-07"); days = R.loc["2026-08-07":"2026-10-30"].index; win = R.loc["2026-08-10":"2026-10-30"]
res26 = (win["T"] - b26 * win.Q); res["TSLA beta to QQQ (250 sessions to Aug 7 2026)"] = round(b26, 3)
PD = S / "poly"; RD = S / "poly_races"
MK = {"Texas Senate: Paxton (R) [P1]": (RD / "tx_sen.json", "Paxton"), "House: Republicans": (PD / "house26.json", "Republican Party"),
      "Senate: Republicans": (PD / "senate26.json", "Republican Party"), "Texas governor: Abbott (R)": (RD / "tx_gov.json", "Abbott"),
      "Nevada governor: Lombardo (R)": (RD / "nv_gov.json", "Lombardo"), "Arizona governor: Biggs (R)": (RD / "az_gov.json", "Biggs"),
      "Michigan Senate: Rogers (R)": (RD / "mi_sen.json", "Rogers"), "California governor: Hilton (R)": (RD / "ca_gov.json", "Hilton")}
out, daily = {}, pd.DataFrame({"TSLA residual %": 100 * res26})
for k, (f, lab) in MK.items():
    p = at16(pser(f, lab), days); dp = p.diff().loc["2026-08-10":]; daily[k] = 100 * dp
    s = slope(res26, dp); tot = float(p.iloc[-1] - p.iloc[0])
    s.update({"P Aug 7 -> Oct 30": [round(float(p.iloc[0]), 3), round(float(p.iloc[-1]), 3)], "sd of daily change, pts": round(100 * float(dp.std()), 2),
              "days with |change| >= 3 pts": int((dp.abs() >= .03).sum()),
              "attributed TSLA move from the total odds change %": [round(100 * s["_b"] * tot / .10, 1), round(100 * min(s["_lo"] * tot / .10, s["_hi"] * tot / .10), 1), round(100 * max(s["_lo"] * tot / .10, s["_hi"] * tot / .10), 1)]})
    top = dp.abs().nlargest(3).index; s["TSLA residual z on the 3 biggest odds days"] = {str(d.date()): [round(100 * float(dp[d]), 1), round(float(res26[d] / R.loc[:d].iloc[-61:-1].pipe(lambda x: x["T"] - b26 * x.Q).std()), 2)] for d in top}
    out[k] = s
holm(out)
for v in out.values(): [v.pop(z) for z in ("_b", "_lo", "_hi")]
res["P1-P3 2026 (Aug 10 -> Oct 30)"] = out
res["TSLA cumulative residual Aug 10 -> Oct 30 2026 %"] = round(100 * float(res26.sum()), 1)
res["TSLA raw return Aug 7 -> Oct 30 2026 %"] = round(100 * float((1 + R.loc["2026-08-10":"2026-10-30", "T"]).prod() - 1), 1)
x = out["Texas Senate: Paxton (R) [P1]"]
# sensitivity: drop the Q3 earnings reaction day (Oct 22)
s2 = slope(res26.drop(pd.Timestamp("2026-10-22"), errors="ignore"), daily["Texas Senate: Paxton (R) [P1]"].div(100)); [s2.pop(z) for z in ("_b", "_lo", "_hi")]
res["P1 sensitivity: without the Q3 earnings reaction day (Oct 22)"] = s2
daily.round(3).to_csv(HERE / "out" / "daily26.csv")
# ---- P4: 2024 calibration ----
b24 = beta_to("2024-07-31"); d24 = R.loc["2024-07-31":"2024-11-04"].index; w24 = R.loc["2024-08-01":"2024-11-04"]; r24 = w24["T"] - b24 * w24.Q
pT = at16(pser(PD / "pres24.json", "Donald Trump"), d24); s = slope(r24, pT.diff().loc["2024-08-01":]); [s.pop(z) for z in ("_b", "_lo", "_hi")]
nov6 = R.loc["2024-11-06"]; rr = float(nov6["T"] - b24 * nov6.Q); sd60 = float((R.loc[:"2024-11-05"].iloc[-60:]["T"] - b24 * R.loc[:"2024-11-05"].iloc[-60:].Q).std())
s.update({"P(Trump) Jul 31 -> Nov 4 (16:00)": [round(float(pT.iloc[0]), 3), round(float(pT.iloc[-1]), 3)], "sd of daily change, pts": round(100 * float(pT.diff().std()), 2),
          "Nov 6 2024: TSLA raw / residual %": [round(100 * float(nov6["T"]), 2), round(100 * rr, 2)], "Nov 6 residual z": round(rr / sd60, 2),
          "method's predicted Nov 6 residual from the daily slope %": round(s["per +10 pts %"] * (1 - float(pT.iloc[-1])) / .10 * 1, 1)})
res["P4 2024 calibration (Aug 1 -> Nov 4 2024)"] = s
# ---- P5: options, Friday close before each vote, like-for-like weekly pairs ----
irx = json.load(open(S / "yf" / "IRX.json"))["chart"]["result"][0]; irx = pd.Series(irx["indicators"]["quote"][0]["close"], index=pd.to_datetime(irx["timestamp"], unit="s").normalize()).dropna() / 100
def b76(F, K, T, s, c):
    d1 = (np.log(F / K) + s * s * T / 2) / (s * np.sqrt(T)); d2 = d1 - s * np.sqrt(T)
    return np.where(c, F * norm.cdf(d1) - K * norm.cdf(d2), K * norm.cdf(-d2) - F * norm.cdf(-d1))
def iv(p, F, K, T, c):
    lo, hi = np.full(len(p), .01), np.full(len(p), 4.)
    for _ in range(50):
        m = (lo + hi) / 2; h = b76(F, K, T, m, c) > p; hi, lo = np.where(h, m, hi), np.where(h, lo, m)
    return (lo + hi) / 2
def sess(a, b): return int(np.busday_count((a + pd.Timedelta(days=1)).date(), (b + pd.Timedelta(days=1)).date(), holidays=HOL))
def premium(path, d, exps):
    e = pd.read_csv(path); e["date"] = pd.to_datetime(e.created.astype(str).str[:10]); e["expiration"] = pd.to_datetime(e.expiration)
    e = e[(e.date == d) & e.expiration.isin(exps) & (e.bid > 0) & (e.ask > 0)].copy(); e["cp"] = np.where(e.right.astype(str).str.upper().str.startswith("C"), "C", "P"); e["mid"] = (e.bid + e.ask) / 2
    r = float(irx.asof(d)); W = {}
    for ex, x in e.groupby("expiration"):
        T = (ex - d).days / 365; pv = x.pivot_table(index="strike", columns="cp", values="mid").dropna()
        k = (pv.C - pv.P).abs().idxmin(); F = k + np.exp(r * T) * (pv.loc[k, "C"] - pv.loc[k, "P"]); near = pv.iloc[(pv.index - F).to_series().abs().argsort()[:2].to_numpy()]
        sg = np.nanmean(iv(np.r_[near.C, near.P] * np.exp(r * T), F, np.r_[near.index, near.index], T, np.r_[np.ones(len(near), bool), np.zeros(len(near), bool)])); W[ex] = sg * sg * T
    ex = sorted(W); n0 = sess(d, ex[0]); base = [(W[b] - W[a]) / sess(a, b) for a, b in zip(ex[:-1], ex[1:])]; bl = float(np.median(base)); exc = W[ex[0]] - n0 * bl
    return {"window": f"{d.date()} -> {ex[0].date()} ({n0} sessions)", "normal-day move %": round(100 * np.sqrt(bl), 2), "window per-session move %": round(100 * np.sqrt(W[ex[0]] / n0), 2),
            "excess, in normal days": round(exc / bl, 2), "excess move-equivalent %": round(100 * np.sign(exc) * np.sqrt(abs(exc)), 2)}
T = pd.Timestamp
res["P5 options 2024 (Fri Nov 1 close; window has FOMC Nov 7)"] = premium(S / "n3" / "eod" / "TSLA_2024-11_eod.csv.gz", T("2024-11-01"), [T("2024-11-08"), T("2024-11-15"), T("2024-11-22"), T("2024-11-29")])
res["P5 options 2026 like-for-like (Fri Oct 30 close; window has AAPL reaction, payrolls)"] = premium(S / "n2" / "td" / "TSLA_eod_20261030.csv.gz", T("2026-10-30"), [T("2026-11-06"), T("2026-11-13"), T("2026-11-20"), T("2026-11-27")])
# ---- P6: Musk-White House days ----
ev = {"2024-11-06 Trump wins": "2024-11-06", "2025-06-05 Trump-Musk feud public": "2025-06-05", "2025-07-07 America Party (first session)": "2025-07-07"}
p6 = {}
for k, d in ev.items():
    d = T(d); b = beta_to(d - pd.Timedelta(days=1)); h = R.loc[:d].iloc[-61:-1]; sd = float((h["T"] - b * h.Q).std()); x = R.loc[d]
    p6[k] = {"TSLA raw %": round(100 * float(x["T"]), 2), "QQQ %": round(100 * float(x.Q), 2), "residual %": round(100 * float(x["T"] - b * x.Q), 2), "z": round(float((x["T"] - b * x.Q) / sd), 2)}
res["P6 Musk-White House days"] = p6
json.dump(res, open(HERE / "out" / "results.json", "w"), indent=1); print(json.dumps(res, indent=1))
