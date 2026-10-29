"""Part B, single names (pre-registered @ 89dcdd6): B1 post-quarterly-expiry gap-ups, B2 earnings fade (9 parked names),
B3 call-wall cap (MSFT, MU), B4 earnings unwind pressure (TSLA, NVDA, MSFT, MU), B5 pre-earnings last 30 minutes (12 stocks, 60m bars).
Holm across B1-B5. Usage: python partB.py <scratchpad> -> out/partB.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

S = Path(sys.argv[1]); HERE = Path(__file__).resolve().parent; CX = S / "ctx"
sys.path.insert(0, str(HERE.parent / "2026-10-27-flip-wicks"))
from flipmap import norm, t      # noqa: E402
rng = np.random.default_rng(0); B = 5000
NINE = ["AMD", "META", "MSFT", "AMZN", "GOOGL", "AVGO", "NFLX", "MU", "ORCL"]
E = pd.read_csv(CX / "earnings_all.csv", parse_dates=["report_date"])
spy = json.load(open(CX / "daily" / "SPY.json"))["chart"]["result"][0]
td = pd.DatetimeIndex(sorted(set(pd.to_datetime(spy["timestamp"], unit="s").normalize())))
E["react"] = [td[td > r][0] if (td > r).any() else pd.NaT for r in E.report_date]


def holm(ps):
    ps = np.asarray(ps, float); o = np.argsort(ps); adj = np.empty_like(ps); run = 0
    for i, k in enumerate(o):
        run = max(run, (len(ps) - i) * ps[k]); adj[k] = min(1, run)
    return adj


def pboot(bs):
    bs = bs[~np.isnan(bs)]; return float(min(1, 2 * min((bs <= 0).mean(), (bs >= 0).mean()) + 1 / len(bs)))


def contrast(df, flag, y):
    df = df.copy(); df["g"] = flag.astype(int).to_numpy(); df["yd"] = df[y] - df.groupby("sym")[y].transform("mean")
    est = df[df.g == 1].yd.mean() - df[df.g == 0].yd.mean()
    dates = df.date.unique(); idx = {d: np.flatnonzero(df.date.to_numpy() == d) for d in dates}; yd, g = df.yd.to_numpy(), df.g.to_numpy(); bs = np.empty(B)
    for i in range(B):
        k = np.concatenate([idx[d] for d in rng.choice(dates, len(dates))])
        bs[i] = yd[k][g[k] == 1].mean() - yd[k][g[k] == 0].mean() if (g[k] == 1).any() and (g[k] == 0).any() else np.nan
    o = {"n_context": int(df.g.sum()), "n_rest": int((df.g == 0).sum()), "est": float(est), "ci95": [float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5))], "p": pboot(bs)}
    if "cls" in df:
        o.update({"vf_context": float((df[df.g == 1].cls == "VF").mean()), "vf_rest": float((df[df.g == 0].cls == "VF").mean()),
                  "sc_context": float((df[df.g == 1].cls == "SC").mean()), "sc_rest": float((df[df.g == 0].cls == "SC").mean())})
    return o


def spear(x, y, dates):
    est = stats.spearmanr(x, y)[0]; bs = np.empty(B); n = len(x)
    for i in range(B):
        k = rng.integers(0, n, n); bs[i] = stats.spearmanr(x[k], y[k])[0]
    return {"n": int(n), "est": float(est), "ci95": [float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5))], "p": pboot(bs)}


f13 = HERE / "out" / "events13.csv"
ev = pd.read_csv(f13 if f13.exists() else HERE.parent / "2026-10-29-gap-context" / "out" / "context.csv", parse_dates=["date"])
ev["react"] = ev.merge(E[["sym", "react"]].assign(flag=1), left_on=["sym", "date"], right_on=["sym", "react"], how="left").flag.fillna(0).to_numpy()
tf = {(y, m): pd.date_range(f"{y}-{m:02d}-01", periods=31).to_series().loc[lambda s: (s.dt.month == m) & (s.dt.dayofweek == 4)].iloc[2] for y in range(2017, 2027) for m in (3, 6, 9, 12)}
post_q = set()
for d in tf.values():
    post_q.update(td[td > d][:5])
ev["post_qexp"] = ev.date.isin(post_q).astype(int)
T = {}
T["B1 gap-ups in the 5 sessions after a quarterly expiry (Y1, -)"] = contrast(ev, ev.post_qexp == 1, "Y1") | {"symbols": int(ev.sym.nunique())}
nine = ev[ev.sym.isin(NINE)]
if len(nine):
    T["B2 earnings-reaction gap-ups, 9 parked names (Y1, -)"] = contrast(nine, nine.react == 1, "Y1")
# B3 + B4 need chains
_c = {}


def month(sym, ym, kind):
    k = (sym, ym, kind)
    if k not in _c:
        f = t.DIR / f"{sym}_{ym}_{kind}.csv.gz"; _c[k] = norm(pd.read_csv(f)) if f.exists() else pd.DataFrame()
    return _c[k]


b3 = []
for r in ev[ev.sym.isin(["MSFT", "MU"]) & (ev.date >= "2020-01-15") & (ev.date <= "2026-10-14")].itertuples():
    oi = month(r.sym, f"{r.date:%Y-%m}", "oi"); oi = oi[oi.date == r.date] if len(oi) else oi
    if not len(oi): continue
    oc = next(c for c in oi.columns if "open_interest" in c); lim = pd.bdate_range(r.date, periods=3)[-1]
    near = oi[(oi.cp == "C") & (oi.expiration >= r.date) & (oi.expiration <= lim)]
    pin = 0
    if len(near):
        K = float(near.groupby("strike")[oc].sum().idxmax()); pin = int(r.open1m > K and (r.open1m - K) / r.open1m / r.sig <= 1.5)
    b3.append({"sym": r.sym, "date": r.date, "Y1": r.Y1, "cls": r.cls, "pin": pin})
b3 = pd.DataFrame(b3)
if len(b3) and b3.pin.sum() >= 3:
    T["B3 call-wall cap, MSFT+MU (Y1, -)"] = contrast(b3, b3.pin == 1, "Y1")
# B4 unwind pressure on earnings-reaction gap-ups
SPLITS = {"TSLA": [("2020-08-31", 5), ("2022-08-25", 3)], "NVDA": [("2021-07-20", 4), ("2024-06-10", 10)]}


def daily(sym):
    r = json.load(open(CX / "daily" / f"{sym}.json"))["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    d = pd.DataFrame({"close": q["close"], "volume": q["volume"]}, index=pd.to_datetime(r["timestamp"], unit="s").normalize()); return d[~d.index.duplicated(keep="last")].dropna()


def atm_iv(sym, day):
    e = month(sym, f"{day:%Y-%m}", "eod"); e = e[e.date == day] if len(e) else e
    if not len(e): return np.nan
    e = e.copy(); e["mid"] = (e.bid + e.ask) / 2
    g = t.chain_day(e); S0 = float(g.underlying_close.iloc[0])
    g = g[(g.expiration - day).dt.days >= 5]
    if not len(g): return np.nan
    x = g[g.expiration == g.expiration.min()]; k = x.iloc[(x.strike - S0).abs().argsort()[:4]]
    return float(k.iv.mean())


rows = []
for r in ev[(ev.react == 1) & ev.sym.isin(["TSLA", "NVDA", "MSFT", "MU"]) & (ev.date >= "2020-01-15") & (ev.date <= "2026-10-14")].itertuples():
    rep = td[td < r.date][-1]
    oi = month(r.sym, f"{r.date:%Y-%m}", "oi"); oi = oi[oi.date == r.date] if len(oi) else oi
    if not len(oi): continue
    oc = next(c for c in oi.columns if "open_interest" in c); pc = r.open1m / (1 + r.gap)
    calls = oi[(oi.cp == "C") & oi.strike.between(pc, 1.10 * pc) & (oi.expiration >= r.date) & ((oi.expiration - r.date).dt.days <= 45)][oc].sum()
    dd = daily(r.sym); dd = dd[dd.index < r.date].iloc[-20:]
    adj = np.prod([f for s, f in SPLITS.get(r.sym, []) if pd.Timestamp(s) > r.date]) if r.sym in SPLITS else 1.0
    adv = dd.volume.mean() / adj                                   # Yahoo volume is split-adjusted; OI is in pre-split contracts
    ivd = atm_iv(r.sym, rep) - atm_iv(r.sym, r.date)
    rows.append({"sym": r.sym, "date": r.date, "Y1": r.Y1, "cls": r.cls, "call_oi_per_adv": 100 * calls / adv, "iv_drop": ivd, "unwind": 100 * calls / adv * ivd})
b4 = pd.DataFrame(rows).dropna()
if len(b4) >= 8:
    T["B4 earnings unwind pressure vs Y1 (rho, -)"] = spear(b4.unwind.to_numpy(), b4.Y1.to_numpy(), b4.date.to_numpy()) | {"by_part": {"rho call_oi": float(stats.spearmanr(b4.call_oi_per_adv, b4.Y1)[0]), "rho iv_drop": float(stats.spearmanr(b4.iv_drop, b4.Y1)[0])}}
# B5 last 30 minutes on the report day (report after that day's close)
rows = []
for s in E.sym.unique():
    p = S / "hourly" / f"{s}_60m.json"
    if not p.exists(): continue
    r = json.load(open(p))["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    h = pd.DataFrame({"o": q["open"], "c": q["close"]}, index=pd.to_datetime(r["timestamp"], unit="s", utc=True).tz_convert("America/New_York")).dropna()
    last = h[h.index.strftime("%H:%M") == "15:30"]
    x = pd.DataFrame({"sym": s, "date": last.index.normalize().tz_localize(None), "r30": 100 * (last.c / last.o - 1).to_numpy()})
    rep = set(E[E.sym == s].report_date); x["report_day"] = x.date.isin(rep).astype(int); rows.append(x)
b5 = pd.concat(rows)
T["B5 last 30 minutes on the report day (%, -)"] = contrast(b5, b5.report_day == 1, "r30")
for (k, v), h in zip(T.items(), holm([v["p"] for v in T.values()])):
    v["p_holm"] = float(h); v["pass"] = bool(h < 0.05); v["sign_as_predicted"] = bool(np.sign(v["est"]) == -1)
json.dump({"family": T, "events_file": f13.name if f13.exists() else "gap-context 4 names", "b4_rows": b4.astype({"date": str}).round(4).to_dict(orient="records")},
          open(HERE / "out" / "partB.json", "w"), indent=1, default=float)
pd.set_option("display.width", 250); print(pd.DataFrame(T).T.drop(columns=[c for c in ("by_part",) if c in pd.DataFrame(T).T]).to_string())
if "B4 earnings unwind pressure vs Y1 (rho, -)" in T: print("B4 parts", T["B4 earnings unwind pressure vs Y1 (rho, -)"]["by_part"])
