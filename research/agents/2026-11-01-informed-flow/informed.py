"""Informed-flow test (pre-registered @ e217d7b). Signals: I-opp / I-all (SEC Form 4 open-market trades, Cohen-Malloy-
Pomorski routine filter), A / L (CFTC TFF E-mini S&P 500 asset managers / leveraged funds, 4-week change in net % OI),
D (SqueezeMetrics DIX z). Reflexivity, predictive slopes (block bootstrap), OOS R2, follow rule, eras.
Usage: python informed.py <GSPC json> <unused (was SEC dir)> <tff json> <DIX.csv> <SPY 1m parquet> [<SPY 1m parquet> ...] -> out/informed.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; rng = np.random.default_rng(17)
r = json.load(open(sys.argv[1]))["chart"]["result"][0]
P = pd.Series(r["indicators"]["quote"][0]["close"], index=pd.to_datetime(r["timestamp"], unit="s").normalize()).dropna()
P = P[~P.index.duplicated(keep="last")].loc["2005-01-01":]; td = P.index; lp = np.log(P)
nxt = lambda d: td[td.searchsorted(d, side="right")] if td.searchsorted(d, side="right") < len(td) else pd.NaT   # first session strictly after d
S = pd.DataFrame(index=td)
# ---------- (Amendment 1) SEC insiders dropped at the owner's request; credit and smart-money index added
def yfs(path):
    r = json.load(open(path))["chart"]["result"][0]
    x = pd.Series(r["indicators"]["quote"][0]["close"], index=pd.to_datetime(r["timestamp"], unit="s").normalize()).dropna()
    return x[~x.index.duplicated(keep="last")]
YF = Path(sys.argv[1]).parent
S["C"] = (np.log(yfs(YF / "HYG.json") / yfs(YF / "IEF.json"))).reindex(td).diff(20)
mm = []
for f in sys.argv[5:]:
    m = pd.read_parquet(f, columns=["open", "close"]); m.index = m.index.tz_convert("America/New_York")
    m = m[(m.index.time >= pd.Timestamp("09:30").time()) & (m.index.time < pd.Timestamp("16:00").time())]; mm.append(m)
m = pd.concat(mm); m = m[~m.index.duplicated()]; dd = m.index.normalize().tz_localize(None); hm = m.index.hour * 60 + m.index.minute
g = pd.DataFrame({"o": m.open.to_numpy(), "c": m.close.to_numpy(), "hm": hm, "d": dd})
o930 = g[g.hm == 570].set_index("d").o; c959 = g[g.hm == 599].set_index("d").c; c1459 = g[g.hm == 899].set_index("d").c; c1559 = g[g.hm == 959].set_index("d").c
smi_day = (np.log(c1559 / c1459) - np.log(c959 / o930)).dropna()
S["SMI"] = smi_day.reindex(td).rolling(20, min_periods=18).sum()
cls_counts = "dropped (Amendment 1)"
# ---------- CFTC
T = pd.DataFrame(json.load(open(sys.argv[3]))); T["d"] = pd.to_datetime(T.report_date_as_yyyy_mm_dd)
for c in T.columns[1:-1]: T[c] = pd.to_numeric(T[c])
T["am"] = (T.asset_mgr_positions_long - T.asset_mgr_positions_short) / T.open_interest_all
T["lev"] = (T.lev_money_positions_long - T.lev_money_positions_short) / T.open_interest_all
T = T.sort_values("d").drop_duplicates("d"); T["avail"] = T.d.map(lambda d: nxt(d + pd.Timedelta(days=3)))   # Friday release -> next session
for k, c in (("A", "am"), ("L", "lev")):
    s = pd.Series((T[c] - T[c].shift(4)).to_numpy(), index=T.avail).dropna(); s = s[~s.index.duplicated(keep="last")]
    S[k] = s.reindex(td).ffill(limit=10)
# ---------- DIX
dx = pd.read_csv(sys.argv[4], parse_dates=["date"]).set_index("date").dix.reindex(td)
S["D"] = ((dx - dx.rolling(252).mean()) / dx.rolling(252).std()).shift(1)
S["past20"] = lp.diff(20); S["f20"] = lp.shift(-20) - lp; S["f40"] = lp.shift(-40) - lp; S["f60"] = lp.shift(-60) - lp
S.to_csv(HERE / "out" / "signals.csv")
SIG = ["A", "D", "C", "SMI", "L"]; PRIMARY = ["A", "D", "C", "SMI"]


def ols(y, X):
    X1 = np.c_[np.ones(len(X)), X]; b = np.linalg.lstsq(X1, y, rcond=None)[0]; return b


def slope_boot(D, sig, h, B=2000, block=126):
    D = D[[sig, "past20", h]].dropna(); z = (D[sig] - D[sig].mean()) / D[sig].std()
    y, X = D[h].to_numpy(), np.c_[z.to_numpy(), D.past20.to_numpy()]; b = ols(y, X)[1]; n = len(y); bs = []
    for _ in range(B):
        st = rng.integers(0, n - block, n // block + 1); ii = np.concatenate([np.arange(s, s + block) for s in st])[:n]
        bs.append(ols(y[ii], X[ii])[1])
    bs = np.array(bs); return b, bs, n


def oos(D, sig, h, start_years=5):
    D = D[[sig, "past20", h]].dropna(); idx = D.index; H = int(h[1:]); out_m, out_b = [], []
    t0 = idx[0] + pd.DateOffset(years=start_years)
    for i in range(0, len(D), 21):
        t = idx[i]
        if t < t0: continue
        train = D.iloc[:max(0, i - H)]          # only forward returns already realised by t
        if len(train) < 250: continue
        b = ols(train[h].to_numpy(), train[[sig, "past20"]].to_numpy())
        pred = b[0] + b[1] * D[sig].iloc[i] + b[2] * D.past20.iloc[i]
        out_m.append((D[h].iloc[i] - pred) ** 2); out_b.append((D[h].iloc[i] - train[h].mean()) ** 2)
    return 1 - np.sum(out_m) / np.sum(out_b), len(out_m)


res = {"insider class counts (filings)": cls_counts}; raw_p = {}
for sig in SIG:
    D = S.loc[S[sig].notna()]; R = {"start": str(D.index[0].date()), "end": str(D.index[-1].date())}
    R["reflexivity corr(signal, past 20-session return)"] = round(float(D[[sig, "past20"]].dropna().corr().iloc[0, 1]), 3)
    for h in ("f20", "f40", "f60"):
        b, bs, n = slope_boot(S, sig, h)
        p = 2 * min((bs <= 0).mean(), (bs >= 0).mean())
        R[f"{h} slope (log ret per 1 sd)"] = {"slope %": round(100 * b, 3), "95% CI %": np.round(100 * np.quantile(bs, [.025, .975]), 3).tolist(), "p two-sided": round(float(p), 4), "n days": n}
        if sig in PRIMARY and h == "f40": raw_p[(sig, h)] = p
        r2, m = oos(S, sig, h); R[f"{h} OOS R2 % (vs historical mean)"] = [round(100 * r2, 2), m]
        for lab, a, z in (("R0 <2020", "1900", "2019-12-31"), ("R1 2020-21", "2020-01-01", "2021-12-31"), ("R2 2022+", "2022-01-01", "2100")):
            E = S.loc[a:z, [sig, "past20", h]].dropna()
            if len(E) > 100:
                zz = (E[sig] - S[sig].mean()) / S[sig].std(); R.setdefault(f"{h} slope % by era", {})[lab] = round(100 * ols(E[h].to_numpy(), np.c_[zz, E.past20])[1], 3)
    # follow rule: trailing 3-year terciles
    q1 = S[sig].rolling(756, min_periods=500).quantile(1 / 3); q2 = S[sig].rolling(756, min_periods=500).quantile(2 / 3)
    F = pd.DataFrame({"top": S[sig] >= q2, "bot": S[sig] <= q1, "f20": S.f40}).dropna()
    F = F[(S[sig].notna()) & q1.notna()]
    top, bot = F[F.top].f20, F[F.bot].f20
    yr = F.groupby(F.index.year).apply(lambda g: g[g.top].f20.mean() - g[g.bot].f20.mean() if g.top.any() and g.bot.any() else np.nan).dropna()
    R["follow rule (top vs bottom third of trailing 3y), next 40 sessions"] = {"top mean %": round(100 * top.mean(), 3), "bottom mean %": round(100 * bot.mean(), 3),
                                                                                "all-days mean %": round(100 * F.f20.mean(), 3), "years top>bottom": f"{int((yr > 0).sum())} of {len(yr)}"}
    last = S[sig].dropna(); cur = float(last.iloc[-1]); hist = S[sig].loc[last.index[-1] - pd.Timedelta(days=1100):last.index[-1]].dropna()
    R["now"] = {"date": str(last.index[-1].date()), "value": round(cur, 4), "percentile in trailing 3y": round(float((hist < cur).mean()), 2)}
    res[sig] = R
ps = sorted(raw_p.items(), key=lambda kv: kv[1]); m = len(ps); holm = {}; run = 0
for i, (k, p) in enumerate(ps): run = max(run, min(1, (m - i) * p)); holm[f"{k[0]} {k[1]}"] = round(run, 4)
res["Holm (4 primaries at 40 sessions)"] = holm
json.dump(res, open(HERE / "out" / "informed.json", "w"), indent=1, default=str)
print(json.dumps(res, indent=1, default=str))
