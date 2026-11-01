"""July vs October 2026 forensics (pre-registered @ 6822475): F1 similarity vs chance, F2 event-calendar rhythm, pieces table.
Usage: python forensics.py <yahoo json dir> -> out/forensics.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; YF = Path(sys.argv[1]); rng = np.random.default_rng(11)


def yf(t, col="close"):
    r = json.load(open(YF / f"{t}.json"))["chart"]["result"][0]
    s = pd.Series(r["indicators"]["quote"][0][col], index=pd.to_datetime(r["timestamp"], unit="s").tz_localize("UTC").tz_convert("America/New_York").normalize().tz_localize(None))
    return s[~s.index.duplicated(keep="last")].dropna()


px = yf("%5EGSPC"); vix = yf("%5EVIX"); px = px[px.index >= "1992-12-01"]
r = np.log(px).diff().dropna(); td = r.index
z = r / (vix.shift(1).reindex(td, method="ffill") / 100 / np.sqrt(252)); z = z.dropna()
res = {}
# ---------- F1
J = r.loc["2026-07-13":"2026-07-31"].to_numpy(); O = r.loc["2026-10-12":"2026-10-30"].to_numpy(); assert len(J) == len(O) == 15
obs = float(np.corrcoef(J, O)[0, 1])
rr = r.loc[:"2026-06-30"].to_numpy(); W = np.lib.stride_tricks.sliding_window_view(rr, 15)
null = np.array([np.corrcoef(w, O)[0, 1] for w in W])
# look-elsewhere: last 15 sessions of each of the 24 months before October (Oct 2024 .. Sep 2026)
me = [r.loc[str(p)].iloc[-15:].to_numpy() for p in pd.period_range("2024-10", "2026-09", freq="M")]
le = np.array([np.corrcoef(w, O)[0, 1] for w in me]); mx = le.max(); F = (null < mx).mean()
J9, O9 = J[:9], O[:9]; W9 = np.lib.stride_tricks.sliding_window_view(rr, 9); n9 = np.array([np.corrcoef(w, O9)[0, 1] for w in W9])
obs9 = float(np.corrcoef(J9, O9)[0, 1])
res["F1"] = {"corr July vs Oct, 15 aligned sessions": round(obs, 3), "percentile vs all 15-session windows 1993-2026H1": round(float((null < obs).mean()), 3),
             "share of windows at least as similar": round(float((null >= obs).mean()), 3), "n windows": int(len(null)),
             "best of 24 month-end windows (Oct24-Sep26)": round(float(mx), 3), "which month": str(pd.period_range("2024-10", "2026-09", freq="M")[int(le.argmax())]),
             "July rank among the 24": int((le > obs).sum()) + 1, "p look-elsewhere (best of 24 at least this similar by chance)": round(float(1 - F ** 24), 3),
             "post hoc: first 9 sessions corr": round(obs9, 3), "post hoc: 9-session percentile": round(float((n9 < obs9).mean()), 3),
             "daily returns July %": np.round(100 * J, 2).tolist(), "daily returns Oct %": np.round(100 * O, 2).tolist(),
             "_null_hist": np.histogram(null, bins=np.linspace(-1, 1, 41))[0].tolist()}
# ---------- F2a opex rhythm
tds = pd.DatetimeIndex(td)
def third_friday(y, m):
    d = pd.Timestamp(y, m, 15); d = d + pd.Timedelta(days=(4 - d.weekday()) % 7); return d
def on_or_before(d):
    i = tds.searchsorted(d, side="right") - 1; return tds[i] if i >= 0 else None
opex = sorted({on_or_before(third_friday(y, m)) for y in range(1993, 2027) for m in range(1, 13) if third_friday(y, m) <= tds[-1]} - {None})
pos = {d: i for i, d in enumerate(tds)}; zz = z.reindex(tds)
K = range(-5, 11); prof = {k: [] for k in K}; prof_es = {k: [] for k in K}; post = set()
for d in opex:
    i = pos[d]
    for k in K:
        if 0 <= i + k < len(tds):
            v = zz.iloc[i + k]
            if np.isfinite(v):
                prof[k].append(v); (prof_es[k].append(v) if d.month in (1, 4, 7, 10) else None)
            if 1 <= k <= 10: post.add(tds[i + k])
res["F2a profile mean z by session (all months)"] = {k: [round(float(np.mean(prof[k])), 3), round(float(np.std(prof[k]) / np.sqrt(len(prof[k]))), 3), len(prof[k])] for k in K}
res["F2a profile mean z (Jan/Apr/Jul/Oct)"] = {k: [round(float(np.mean(prof_es[k])), 3), round(float(np.std(prof_es[k]) / np.sqrt(len(prof_es[k]))), 3), len(prof_es[k])] for k in K}
Z = pd.DataFrame({"z": zz}).dropna(); Z["post"] = Z.index.isin(post); Z["yr"] = Z.index.year
# ---------- F2b day after VIX expiry
vexp = []
for y in range(2004, 2027):
    for m in range(1, 13):
        ny, nm = (y + (m == 12), m % 12 + 1); f = third_friday(ny, nm)
        f = on_or_before(f) if f <= tds[-1] else f   # future expiries keep their calendar date
        if f is None: continue
        w = on_or_before(f - pd.Timedelta(days=30)) if (f - pd.Timedelta(days=30)) <= tds[-1] else None
        if w is None or w < pd.Timestamp("2004-04-01"): continue
        vexp.append(w)
vexp = sorted(set(vexp)); after = {tds[pos[w] + 1] for w in vexp if pos[w] + 1 < len(tds)}
opex_set = set(opex)
after_wk = {tds[pos[w] + 1] for w in vexp if pos[w] + 1 < len(tds) and any(0 < (w - o).days <= 7 for o in opex_set if abs((w - o).days) < 10)}
Z["after_vx"] = Z.index.isin(after); Z["after_vx_wk"] = Z.index.isin(after_wk)


def boot(stat_fn, B=10000):
    yrs = Z.yr.unique(); g = {y: Z[Z.yr == y] for y in yrs}; out = []
    for _ in range(B):
        out.append(stat_fn(pd.concat([g[y] for y in rng.choice(yrs, len(yrs))])))
    return np.array(out)


f2a = lambda D: D[D.post].z.mean() - D[~D.post].z.mean()
Zb = Z[Z.index >= "2004-04-01"]
f2b = lambda D: D[D.after_vx].z.mean() - D[~D.after_vx].z.mean()
b1 = boot(f2a); e1 = f2a(Z)
Zsave = Z; Z = Zb; b2 = boot(f2b); e2 = f2b(Zb); Z = Zsave
p1 = 2 * min((b1 <= 0).mean(), (b1 >= 0).mean()); p2 = 2 * min((b2 <= 0).mean(), (b2 >= 0).mean())
ps = sorted([(p1, "a"), (p2, "b")]); holm = {ps[0][1]: min(1, 2 * ps[0][0]), ps[1][1]: min(1, max(2 * ps[0][0], ps[1][0]))}
res["F2a post-opex sessions +1..+10 minus other sessions (z)"] = {"estimate": round(float(e1), 4), "95% CI": np.round(np.quantile(b1, [.025, .975]), 4).tolist(), "p": round(float(p1), 4), "Holm": round(holm["a"], 4),
                                                                   "in bp/day at VIX 17": round(float(e1) * 17 / np.sqrt(252) * 100, 1)}
res["F2b day after VIX expiry minus other sessions (z, 2004-26)"] = {"estimate": round(float(e2), 4), "95% CI": np.round(np.quantile(b2, [.025, .975]), 4).tolist(), "p": round(float(p2), 4), "Holm": round(holm["b"], 4),
                                                                      "n": int(Zb.after_vx.sum()), "share negative": round(float((Zb[Zb.after_vx].z < 0).mean()), 3), "share negative other days": round(float((Zb[~Zb.after_vx].z < 0).mean()), 3)}
c = Zb[Zb.after_vx_wk]
res["F2c day after VIX expiry in the week after opex (descriptive)"] = {"n": int(len(c)), "mean z": round(float(c.z.mean()), 3), "share negative": round(float((c.z < 0).mean()), 3),
                                                                         "2026 cases": {str(d.date()): round(float(v), 2) for d, v in c.z.loc["2026"].items()}}
# ---------- pieces
def chg(s, a, b): s = s.loc[:b]; return float(s.loc[b] / s.loc[:a].iloc[-1] - 1) if len(s) else np.nan
rsp, spy, tnx, dxy, qqq, iwm = yf("RSP"), yf("%5EGSPC"), yf("%5ETNX"), yf("DX-Y.NYB"), yf("QQQ"), yf("IWM")
g = pd.read_csv(HERE.parents[1] / "microstructure" / "out" / "td_gamma_SPY.csv", parse_dates=["date"]).set_index("date")
P = {}
for lab, a, b in (("July", "2026-07-10", "2026-07-31"), ("October", "2026-10-09", "2026-10-30")):
    gg = g.loc[a:b]
    P[lab] = {"S&P % (start close to month-end)": round(100 * chg(spy, a, b), 2), "max drawdown in window %": round(100 * float((spy.loc[a:b] / spy.loc[a:b].cummax() - 1).min()), 2),
              "VIX start / max / end": [round(float(vix.loc[:a].iloc[-1]), 2), round(float(vix.loc[a:b].max()), 2), round(float(vix.loc[:b].iloc[-1]), 2)],
              "equal-weight minus cap-weight (RSP - S&P) %": round(100 * (chg(rsp, a, b) - chg(spy, a, b)), 2), "QQQ - IWM %": round(100 * (chg(qqq, a, b) - chg(iwm, a, b)), 2),
              "10y yield change (bp)": round(float(tnx.loc[:b].iloc[-1] - tnx.loc[:a].iloc[-1]) * 100, 1), "dollar index %": round(100 * chg(dxy, a, b), 2),
              "gamma rows on file": int(len(gg)), "share of days spot below flip": round(float((gg.spot < gg.flip_classic).mean()), 2) if len(gg) else None,
              "median GEX classic $bn": round(float(gg.gex_classic.median()) / 1e9, 2) if len(gg) else None}
res["pieces"] = P
# ---------- exploratory (not pre-registered): do the scheduled days carry bigger moves (variance), whatever the sign?
Zv = Z[Z.index >= "2004-04-01"].copy(); Zv["opex"] = Zv.index.isin(opex_set)
me_days = set(pd.Series(tds, index=tds).groupby([tds.year, tds.month]).max())
Zv["month_end"] = Zv.index.isin(me_days); base = Zv.z.abs().mean()
res["exploratory: mean |z| on scheduled days / all days (2004-26)"] = {k: [round(float(Zv[Zv[k]].z.abs().mean() / base), 3), int(Zv[k].sum())] for k in ("opex", "after_vx", "month_end")}
json.dump(res, open(HERE / "out" / "forensics.json", "w"), indent=1, default=str)
print(json.dumps({k: v for k, v in res.items()}, indent=1, default=str).replace('"_null_hist"', '"_null_hist"')[:9000])
