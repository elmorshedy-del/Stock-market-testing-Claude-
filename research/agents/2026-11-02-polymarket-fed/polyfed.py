"""Polymarket December-Fed digestion test (pre-registered @ 16f95cf). Usage: python polyfed.py <poly dir> <yahoo dir> -> out/results.json, out/daily_2026.csv"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; PD, YD = Path(sys.argv[1]), Path(sys.argv[2]); rng = np.random.default_rng(31)
BPS = {"2026": {"50+ bps decrease": -50, "25 bps decrease": -25, "No change": 0, "25 bps increase": 25, "50+ bps increase": 50},
       "2025": {"50+ bps decrease": -50, "25 bps decrease": -25, "No change": 0, "25+ bps increase": 25},
       "2024": {"75+ bps decrease": -75, "50 bps decrease": -50, "25 bps decrease": -25, "No Change": 0, "25+ bps increase": 25}}
WIN = {"2026": ("2026-07-31", "2026-10-30"), "2025": ("2025-08-01", "2025-12-09"), "2024": ("2024-08-07", "2024-12-17")}
STRESS = ["TLT", "REM", "ITB", "XLRE", "XLU", "KRE", "IWM", "ARKK", "XBI"]; RATES = ["%5EIRX", "%5EFVX", "%5ETNX"]; CROSS = ["SPY", "QQQ", "XLF", "GLD", "DX-Y.NYB", "BTC-USD", "TSLA"]


def yf(t, col="close"):
    r = json.load(open(YD / f"pf_{t}.json"))["chart"]["result"][0]
    s = pd.Series(r["indicators"]["quote"][0][col], index=pd.to_datetime(r["timestamp"], unit="s").tz_localize("UTC").tz_convert("America/New_York").normalize().tz_localize(None))
    return s[~s.index.duplicated(keep="last")].dropna()


spy = yf("SPY"); td = spy.index
A = pd.DataFrame(index=td)
for t in STRESS + CROSS:
    s = yf(t); A[t] = np.log(s).diff().reindex(td)
for t in RATES:
    A[t] = (yf(t).diff() * 100).reindex(td)      # bps change
V = pd.DataFrame({t: yf(t, "volume").reindex(td) for t in STRESS + ["SPY"]})


def poly(yr):
    d = json.load(open(PD / f"poly_{yr}.json"))["markets"]; P = {}
    for k, v in d.items():
        if k in BPS[yr]: P[k] = pd.Series(dict(v))
    P = pd.DataFrame(P); P.index = pd.to_datetime(P.index.astype(int), unit="s", utc=True).tz_convert("America/New_York").tz_localize(None)
    P = P.sort_index().ffill().dropna(); Pn = P.div(P.sum(axis=1), axis=0)
    E = (Pn * pd.Series(BPS[yr])).sum(axis=1)
    at16 = [E.loc[:d + pd.Timedelta(hours=16)].iloc[-1] if len(E.loc[:d + pd.Timedelta(hours=16)]) else np.nan for d in td]
    return pd.Series(at16, index=td)


def slope_boot(y, x, B=2000, block=5, ctrl=None):
    D = pd.concat([y.rename("y"), x.rename("x")] + ([ctrl.rename("c")] if ctrl is not None else []), axis=1).dropna()
    X = np.c_[np.ones(len(D)), D.x] if ctrl is None else np.c_[np.ones(len(D)), D.x, D.c]
    b = np.linalg.lstsq(X, D.y.to_numpy(), rcond=None)[0][1]; n = len(D); bs = []
    for _ in range(B):
        st = rng.integers(0, max(1, n - block), n // block + 1); ii = np.concatenate([np.arange(a, min(a + block, n)) for a in st])[:n]
        bs.append(np.linalg.lstsq(X[ii], D.y.to_numpy()[ii], rcond=None)[0][1])
    bs = np.array(bs); return b, float(2 * min((bs <= 0).mean(), (bs >= 0).mean())), n, np.quantile(bs, [.025, .975])


res = {}; dE = {}
for yr in ("2026", "2025", "2024"):
    E = poly(yr); a, z = WIN[yr]; dE[yr] = E.diff().loc[a:z]
    if yr == "2026": pd.DataFrame({"E_bps": E.loc[a:z], "dE": dE[yr]}).join(A.loc[a:z]).to_csv(HERE / "out" / "daily_2026.csv")
    res[f"{yr} market: days, sd of daily dE (bps), E start -> end"] = [int(dE[yr].notna().sum()), round(float(dE[yr].std()), 2), round(float(E.loc[a:z].iloc[0]), 1), round(float(E.loc[a:z].iloc[-1]), 1)]
# H1
H1 = {}; raw = {}
for t in STRESS + RATES + CROSS:
    row = {}
    for yr in ("2026", "2025", "2024"):
        x = dE[yr] / 5; y = A[t].reindex(x.index)
        b, p, n, ci = slope_boot(y, x)
        unit = 1 if t in RATES else 100
        row[yr] = {"per +5bps hawkish shift": round(unit * b, 3), "p": round(p, 4), "n": n}
        if yr == "2026" and t in STRESS: raw[t] = p
    row["unit"] = "bps of yield" if t in RATES else "% return"
    s26, s25, s24 = (np.sign(row[y]["per +5bps hawkish shift"]) for y in ("2026", "2025", "2024"))
    row["same sign in all 3 markets"] = bool(s26 == s25 == s24)
    H1[t] = row
ps = sorted(raw.items(), key=lambda kv: kv[1]); run = 0; holm = {}
for i, (k, p) in enumerate(ps): run = max(run, min(1, (len(ps) - i) * p)); holm[k] = round(run, 4)
res["H1 same-day sensitivity"] = H1; res["H1 Holm (2026, stress panel)"] = holm
# H2
H2 = {}
for yr in ("2026", "2025", "2024"):
    x = dE[yr]; idx = x.index; out = {}
    for lag in (1, 2):
        y = A[STRESS].mean(axis=1).shift(-lag).reindex(idx); b, p, n, _ = slope_boot(y, x / 5)
        out[f"stress-panel avg return at t+{lag} on dE_t (% per +5bps)"] = [round(100 * b, 3), round(p, 4)]
    f5 = A["%5EFVX"].reindex(idx); b, p, n, _ = slope_boot(x.shift(-1), f5, ctrl=x)
    out["dE_{t+1} on 5y yield change_t (bps of E per bp of yield; controls dE_t)"] = [round(b, 3), round(p, 4)]
    b2, p2, _, _ = slope_boot(f5.shift(-1), x, ctrl=f5)
    out["5y yield change_{t+1} on dE_t (controls yield_t)"] = [round(b2, 3), round(p2, 4)]
    H2[yr] = out
res["H2 digestion and lead-lag"] = H2
# H3: beyond yields
H3 = {}
for t in STRESS + ["SPY", "QQQ", "TSLA"]:
    row = {}
    for yr in ("2026", "2025", "2024"):
        x = dE[yr] / 5; y = A[t].reindex(x.index); c = A["%5EFVX"].reindex(x.index)
        b, p, n, _ = slope_boot(y, x, ctrl=c); row[yr] = [round(100 * b, 3), round(p, 4)]
    H3[t] = row
res["H3 Polymarket coefficient after controlling for the 5y yield (% per +5bps; p)"] = H3
cor = {yr: round(float(pd.concat([dE[yr], A['%5EFVX'].reindex(dE[yr].index)], axis=1).dropna().corr().iloc[0, 1]), 3) for yr in dE}
res["corr(dE, 5y yield change) same day"] = cor
x = dE["2026"]; f5 = A["%5EFVX"].reindex(x.index); big = x.abs() >= x.abs().quantile(0.9)
dis = x[big & (np.sign(x) != np.sign(f5)) & (f5.abs() > 0)]
res["H3 disagreement days 2026 (top-decile |dE|, 5y moved the other way)"] = {str(d.date()): {"dE": round(float(dE["2026"].loc[d]), 1), "5y bps": round(float(f5.loc[d]), 1),
                                                                                               "stress avg %": round(float(100 * A.loc[d, STRESS].mean()), 2), "SPY %": round(float(100 * A.loc[d, "SPY"]), 2)} for d in dis.index}
# H4: rolling 40-session beta to the 5y yield change
H4 = {}
for t in STRESS + ["SPY", "QQQ", "TSLA"]:
    D = pd.concat([A[t], A["%5EFVX"]], axis=1).dropna(); D.columns = ["y", "x"]
    beta = D.y.rolling(40).cov(D.x) / D.x.rolling(40).var()
    now = beta.loc[:"2026-10-30"].iloc[-1]; hist = beta.loc["2020-03-01":"2026-10-30"].dropna()
    win = D.loc["2026-09-01":"2026-10-30"]; bw = np.polyfit(win.x, win.y, 1)[0]
    H4[t] = {"beta Sep-Oct 2026 (% per +10bp of 5y)": round(1000 * bw, 3), "40d beta now (% per +10bp)": round(1000 * now, 3),
             "percentile of now vs 2020-26 (0 = most negative)": round(float((hist < now).mean()), 2), "2020-26 median": round(1000 * float(hist.median()), 3)}
res["H4 rate sensitivity now vs history"] = H4
# H5: activity on big-shift days (2026)
rv = V.div(V.rolling(20).mean().shift(1)); sig = A[STRESS + ["SPY"]].rolling(20).std().shift(1); zabs = (A[STRESS + ["SPY"]] / sig).abs()
idx = dE["2026"].dropna().index; big = dE["2026"].loc[idx].abs() >= dE["2026"].loc[idx].abs().quantile(0.9)
res["H5 big-shift days 2026 (top decile |dE|): n, dates"] = [int(big.sum()), [str(d.date()) for d in idx[big]]]
res["H5 relative volume big vs other days (stress avg, SPY)"] = [round(float(rv.loc[idx[big], STRESS].mean().mean()), 2), round(float(rv.loc[idx[~big], STRESS].mean().mean()), 2),
                                                               round(float(rv.loc[idx[big], "SPY"].mean()), 2), round(float(rv.loc[idx[~big], "SPY"].mean()), 2)]
res["H5 |return| in sigma, big vs other (stress avg, SPY)"] = [round(float(zabs.loc[idx[big], STRESS].mean().mean()), 2), round(float(zabs.loc[idx[~big], STRESS].mean().mean()), 2),
                                                             round(float(zabs.loc[idx[big], "SPY"].mean()), 2), round(float(zabs.loc[idx[~big], "SPY"].mean()), 2)]
json.dump(res, open(HERE / "out" / "results.json", "w"), indent=1, default=str)
print(json.dumps(res, indent=1, default=str))
