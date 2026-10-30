"""Amendment 1 @ 67fa742: options regimes. G1-G5 (Holm) + within-options-era contrasts + earlier option-linked results by regime (descriptive).
Usage: python regimes.py <scratchpad> -> out/regimes.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

S = Path(sys.argv[1]); HERE = Path(__file__).resolve().parent; A = HERE.parent; CX = S / "ctx"
rng = np.random.default_rng(0); B = 5000
EV = pd.read_csv(HERE / "out" / "stock_runs.csv", parse_dates=["date"]); E5 = pd.read_csv(HERE / "out" / "spx_runs.csv", parse_dates=["date"])


def mboot_rho(D, x, y="P20"):
    D = D[D[x].notna() & D[y].notna() & np.isfinite(D[x])].copy(); D["xr"] = D.groupby("sym")[x].rank(pct=True)
    est = stats.spearmanr(D.xr, D[y])[0]; D["m"] = D.date.dt.to_period("M"); ms = D.m.unique(); idx = {m: np.flatnonzero(D.m.to_numpy() == m) for m in ms}
    xr, yy = D.xr.to_numpy(), D[y].to_numpy(); bs = np.empty(B)
    for k in range(B):
        j = np.concatenate([idx[m] for m in rng.choice(ms, len(ms))]); bs[k] = stats.spearmanr(xr[j], yy[j])[0]
    return est, bs, len(D)


def summ(est, bs, n=None):
    bs = bs[~np.isnan(bs)]; o = {"est": float(est), "ci95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))], "p": float(min(1, 2 * min((bs <= 0).mean(), (bs >= 0).mean()) + 1 / len(bs)))}
    if n is not None: o["n"] = int(n)
    return o


def period_diff(D, x, a, b, y="P20"):
    e1, b1, n1 = mboot_rho(D[a], x, y); e2, b2, n2 = mboot_rho(D[b], x, y)
    return summ(e2 - e1, b2 - b1) | {"rho_early": summ(e1, b1, n1), "rho_late": summ(e2, b2, n2)}


pre, post = EV.date < "2020-01-01", EV.date >= "2020-01-01"
T = {"G1 X1 abnormal volume: rho(2020-25) - rho(1990-2019)": period_diff(EV, "X1_abvol", pre, post),
     "G2 X2 thinning liquidity: rho(2020-25) - rho(1990-2019)": period_diff(EV, "X2_amihud", pre, post),
     "G3 X3 overnight share: rho(2020-25) - rho(1990-2019)": period_diff(EV, "X3_overnight", pre, post)}
E5["sym"] = "SPX"
T["G4 X5 low dealer gamma (S&P): rho(2020-25) - rho(2011-19)"] = period_diff(E5, "X5_lowgamma_share", (E5.date >= "2011-06-01") & (E5.date < "2020-01-01"), E5.date >= "2020-01-01")


def series(p):
    r = json.load(open(p))["chart"]["result"][0]; c = pd.Series(r["indicators"]["quote"][0]["close"], index=pd.to_datetime(r["timestamp"], unit="s").normalize()).dropna(); return c[~c.index.duplicated(keep="last")]


vix = series(S / "ladder28" / "data" / "^VIX_1d.json"); spx = series(S / "ladder28" / "data" / "^GSPC_1d.json")
E5["forced"] = [int(vix.asof(d) > vix[vix.index < d].iloc[-10]) if (vix.index < d).sum() > 10 else np.nan for d in E5.date]


def gdiff(D):
    return D[D.forced == 1].G10.mean() - D[D.forced == 0].G10.mean()


def boot_gdiff(D):
    est = gdiff(D); n = len(D); bs = np.array([gdiff(D.iloc[rng.integers(0, n, n)]) for _ in range(B)]); return est, bs


ea, ba = boot_gdiff(E5[E5.date < "2020-01-01"]); eb, bb = boot_gdiff(E5[E5.date >= "2020-01-01"])
T["G5 S&P price-up+VIX-up give-back contrast: 2020-25 minus 1990-2019"] = summ(eb - ea, bb - ba) | {"early": summ(ea, ba), "late": summ(eb, bb),
    "n_forced_early": int((E5[E5.date < "2020-01-01"].forced == 1).sum()), "n_forced_late": int((E5[E5.date >= "2020-01-01"].forced == 1).sum()), "n_late": int((E5.date >= "2020-01-01").sum())}
pred = {"G1": -1, "G2": -1, "G3": -1, "G4": -1, "G5": 1}
ps = [v["p"] for v in T.values()]; o = np.argsort(ps); run = 0; adj = np.empty(len(ps))
for j, k in enumerate(o): run = max(run, (len(ps) - j) * ps[k]); adj[k] = min(1, run)
for (k, v), h in zip(T.items(), adj): v["p_holm"] = float(h); v["sign_as_predicted"] = bool(np.sign(v["est"]) == pred[k[:2]]); v["pass"] = bool(h < 0.05 and v["sign_as_predicted"])
# ---- within the options era: R1 (2020-21) vs R2 (2022-25)
W = {}
hc = pd.read_csv(A / "2026-10-29-house-of-cards" / "out" / "gap_events.csv", parse_dates=["date"])
for nm, m in (("R1 2020-21", hc.date < "2022-01-01"), ("R2 2022-26", hc.date >= "2022-01-01")):
    D = hc[m].copy(); D["yd"] = D.oc_sig - D.groupby("sym").oc_sig.transform("mean"); f = D.forced.to_numpy(); y = D.yd.to_numpy(); n = len(D)
    est = y[f == 1].mean() - y[f == 0].mean(); bs = []
    for _ in range(B):
        k = rng.integers(0, n, n); bs.append(y[k][f[k] == 1].mean() - y[k][f[k] == 0].mean())
    W[f"house-of-cards H5 (gap day after a price-up+IV-up run, open->close sigma), {nm}"] = summ(est, np.array(bs)) | {"n_forced": int(f.sum()), "n": int(n),
        "call7_median_forced": float(D[D.forced == 1].call7_open_to_close_pct.median()), "call7_median_not": float(D[D.forced == 0].call7_open_to_close_pct.median())}
# X4 call skew by R1 / R2 (recompute the 5-name runs, same rule as runs.py)
sys.argv = [sys.argv[0], str(S)]
K = pd.read_csv(HERE / "out" / "skew.csv", parse_dates=["date"])


def load(p):
    r = json.load(open(p))["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    d = pd.DataFrame({k: q[k] for k in ("open", "high", "low", "close", "volume")}, index=pd.to_datetime(r["timestamp"], unit="s").normalize())
    return d[~d.index.duplicated(keep="last")].dropna()


rows = []
for s in ("TSLA", "NVDA", "QQQ", "MSFT", "MU"):
    d = load(CX / "daily" / f"{s}.json"); c = d.close.to_numpy(); idx = d.index; n = len(c); r10 = np.full(n, np.nan); r10[10:] = c[10:] / c[:-10] - 1
    win = (idx >= "2020-02-01") & (idx <= "2026-10-14"); thr = np.nanpercentile(r10[win], 90); k = K[K.sym == s].set_index("date"); nxt = 0
    for i in range(70, n - 20):
        if not win[i] or i < nxt or not (r10[i] >= thr and c[i] >= c[i - 10:i + 1].max()): continue
        if idx[i] in k.index and idx[i - 10] in k.index:
            rows.append({"sym": s, "date": idx[i], "P20": (c[i + 20] - c[i - 10]) / (c[i] - c[i - 10]), "rr": k.rr25[idx[i]] - k.rr25[idx[i - 10]], "atm": k.atm_iv[idx[i]] - k.atm_iv[idx[i - 10]]})
        nxt = i + 20
E4 = pd.DataFrame(rows)
for nm, m in (("R1 2020-21", E4.date < "2022-01-01"), ("R2 2022-26", E4.date >= "2022-01-01")):
    for x in ("rr", "atm"):
        e, b, n = mboot_rho(E4[m], x); W[f"{'X4 call skew' if x == 'rr' else 'ATM IV proxy'} vs permanence, {nm}"] = summ(e, b, n)
# ---- earlier option-linked results by regime (descriptive)
Dsc = {}
ev13 = pd.read_csv(A / "2026-10-29-calendar-mechanics" / "out" / "events13.csv", parse_dates=["date"])
E = pd.read_csv(CX / "earnings_all.csv", parse_dates=["report_date"]); td = spx.index
E["react"] = [td[td > r][0] if (td > r).any() else pd.NaT for r in E.report_date]
ev13 = ev13.merge(E[["sym", "react"]].rename(columns={"react": "date"}).assign(earn=1), on=["sym", "date"], how="left").fillna({"earn": 0})
for nm, lo, hi in (("2018-19", "2018-01-01", "2019-12-31"), ("2020-21", "2020-01-01", "2021-12-31"), ("2022-26", "2022-01-01", "2026-12-31")):
    x = ev13[(ev13.date >= lo) & (ev13.date <= hi) & (ev13.sym != "QQQ")]
    Dsc[f"earnings-gap VF rate {nm}"] = {"earnings": float((x[x.earn == 1].cls == "VF").mean()), "other": float((x[x.earn == 0].cls == "VF").mean()), "n_earnings": int(x.earn.sum()),
                                          "Y1 earnings minus other (sigma)": float(x[x.earn == 1].Y1.mean() - x[x.earn == 0].Y1.mean())}
# 09:35 rule by regime, from the first-hour bars of all 13 names
GT = A / "2026-10-28-gap-teardown"; CM = A / "2026-10-29-calendar-mechanics"
fh = pd.concat([pd.read_parquet(GT / "data" / "first_hour.parquet")] + [pd.read_parquet(f) for f in sorted((CM / "data" / "bars9").glob("*.parquet")) if f.stat().st_size > 0], ignore_index=True)
fh = fh.drop_duplicates(["sym", "date", "ts_event"]); fh["hm"] = fh.ts_event.dt.tz_convert("America/New_York").dt.strftime("%H:%M")
c934 = fh[fh.hm < "09:35"].sort_values("ts_event").groupby(["sym", "date"]).close.last().rename("c934").reset_index()
z = ev13.merge(c934, on=["sym", "date"]); z["r5"] = (z.c934 / z.open1m - 1) / z.sig; z["nxt"] = (z.c1029 / z.c934 - 1) / z.sig
for nm, lo, hi in (("2018-19", "2018-01-01", "2019-12-31"), ("2020-21", "2020-01-01", "2021-12-31"), ("2022-26", "2022-01-01", "2026-12-31")):
    x = z[(z.date >= lo) & (z.date <= hi)]
    Dsc[f"09:35 rule {nm}"] = {"P(next55 up | first5 >= +0.25 sigma)": float((x[x.r5 >= 0.25].nxt > 0).mean()), "P(next55 down | first5 <= -0.25 sigma)": float((x[x.r5 <= -0.25].nxt < 0).mean()),
                               "rho(first5, next55)": float(stats.spearmanr(x.r5, x.nxt, nan_policy="omit")[0]), "n": int(len(x))}
# forced-flow law: next-10-day give-back slope after S&P days, low-gamma quintile vs the rest, by period
dix = pd.read_csv(S / "late28" / "DIX.csv", parse_dates=["date"]).set_index("date"); r = np.log(spx).diff()
f10 = np.log(spx).shift(-10) - np.log(spx); dd = pd.DataFrame({"r": r, "f10": f10, "gex": dix.gex}).dropna(); dd["low"] = dd.gex < dd.gex.rolling(252).quantile(0.2)
for nm, lo, hi in (("2011-19", "2011-06-01", "2019-12-31"), ("2020-26", "2020-01-01", "2026-12-31")):
    x = dd[(dd.index >= lo) & (dd.index <= hi)]
    sl = lambda q: float(np.polyfit(q.r, q.f10, 1)[0])
    Dsc[f"forced-flow give-back slope (next 10d on today's move) {nm}"] = {"low-gamma days": sl(x[x.low]), "other days": sl(x[~x.low]), "n_low": int(x.low.sum())}
json.dump({"family_G": T, "within_options_era": W, "descriptive_by_regime": Dsc}, open(HERE / "out" / "regimes.json", "w"), indent=1, default=float)
for k, v in T.items(): print(k, {a: (round(b, 3) if isinstance(b, float) else b) for a, b in v.items() if a not in ("rho_early", "rho_late", "early", "late")}, "| early", round(v.get("rho_early", v.get("early"))["est"], 3), "late", round(v.get("rho_late", v.get("late"))["est"], 3))
print(json.dumps(W, indent=1, default=lambda q: round(float(q), 3))); print(json.dumps(Dsc, indent=1, default=lambda q: round(float(q), 3)))
