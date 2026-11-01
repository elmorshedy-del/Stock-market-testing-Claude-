"""Pre-registered @ 9a3edb8: dealer gamma as the control parameter of SPY intraday dynamics (H1 range, H2 autocorrelation,
H3 first-15-minute continuation). Vectorized implementation of the registered design.
Usage: python phase.py <SPY 1m parquet> <VIX json> -> out/phase.json, out/days.csv"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; ET = "America/New_York"
rng = np.random.default_rng(0)
m = pd.read_parquet(sys.argv[1], columns=["open", "high", "low", "close"]); m.index = m.index.tz_convert(ET)
m = m[(m.index.time >= pd.Timestamp("09:30").time()) & (m.index.time < pd.Timestamp("16:00").time())]
r = json.load(open(sys.argv[2]))["chart"]["result"][0]
vix = pd.Series(r["indicators"]["quote"][0]["close"], index=pd.to_datetime(r["timestamp"], unit="s").tz_localize("UTC").tz_convert(ET).normalize().tz_localize(None)).dropna()
vix = vix[~vix.index.duplicated(keep="last")]
lv = pd.read_csv(HERE.parent / "2026-10-27-flip-wicks" / "out" / "preopen_levels.csv", parse_dates=["date", "prior"])

m["day"] = m.index.normalize().tz_localize(None); m["mins"] = (m.index.hour - 9) * 60 + m.index.minute - 30   # 0 = 09:30 bar
first = m.groupby("day").mins.min(); good = first[first == 0].index
m = m[m.day.isin(good)]
agg = m.groupby("day").agg(open=("open", "first"), high=("high", "max"), low=("low", "min"), close=("close", "last"), n=("close", "size"))
def px_at(t):            # close of the last bar starting at or before minute t
    x = m[m.mins <= t].groupby("day").close.last(); return x
agg["p0935"], agg["p0945"], agg["p1000"] = px_at(4), px_at(14), px_at(29)
agg = agg[agg.n >= 200]
# k-minute bar closes and within-day demeaned log returns -> per-day sufficient stats for pooled lag-1 autocorrelation
SUFF = {}
for k in (5, 10, 15, 30):
    b = m.assign(bk=m.mins // k).groupby(["day", "bk"]).close.last()
    lr = np.log(b).groupby(level=0).diff().dropna()
    lr = lr - lr.groupby(level=0).transform("mean")
    nxt = lr.groupby(level=0).shift(-1)
    cross = (lr * nxt).groupby(level=0).sum(); sq = (lr ** 2).groupby(level=0).sum(); var = lr.groupby(level=0).var()
    SUFF[k] = pd.DataFrame({"cross": cross, "sq": sq, "var": var})
X = agg.join(lv.set_index("date")[["flip_incl", "gex_open", "share_0dte"]], how="inner")
vp = vix.shift(1).reindex(X.index, method="ffill")
X["sig"] = vp / 100 / np.sqrt(252); X["vixp"] = vp
X = X.dropna(subset=["sig", "flip_incl"])
X["O1"] = (X.high - X.low) / X.open / X.sig
X["d"] = (X.open - X.flip_incl) / (X.sig * X.open)
X["gpct"] = X.gex_open.rolling(252, min_periods=120).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True)
X["vpct"] = X.vixp.rolling(252, min_periods=120).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True)
X["vr6"] = (SUFF[30]["var"] / (6 * SUFF[5]["var"])).reindex(X.index)
for w, col in ((5, "p0935"), (15, "p0945"), (30, "p1000")):
    X[f"ro{w}"] = np.log(X[col] / X.open) / X.sig; X[f"rest{w}"] = np.log(X.close / X[col]) / X.sig
STATES = {"flip": (X.open < X.flip_incl).astype(float).to_numpy(), "gexsign": (X.gex_open < 0).astype(float).to_numpy(),
          "gexpct": np.where(X.gpct <= 1 / 3, 1.0, np.where(X.gpct >= 2 / 3, 0.0, np.nan))}
O1 = X.O1.to_numpy(); CR = {k: SUFF[k].cross.reindex(X.index).to_numpy() for k in (5, 10, 15)}; SQ = {k: SUFF[k].sq.reindex(X.index).to_numpy() for k in (5, 10, 15)}
RO = {w: X[f"ro{w}"].to_numpy() for w in (5, 15, 30)}; RS = {w: X[f"rest{w}"].to_numpy() for w in (5, 15, 30)}


def stats(s, k=5, w=15, extra=False):
    sh = s == 1; lo = s == 0
    h1 = np.nanmean(O1[sh]) - np.nanmean(O1[lo])
    rho_s = np.nansum(CR[k][sh]) / np.nansum(SQ[k][sh]); rho_l = np.nansum(CR[k][lo]) / np.nansum(SQ[k][lo])
    ro, rs = RO[w], RS[w]; v = (sh | lo) & np.isfinite(ro) & np.isfinite(rs)
    A = np.c_[np.ones(v.sum()), ro[v], ro[v] * s[v], s[v]]; beta = np.linalg.lstsq(A, rs[v], rcond=None)[0]
    cont = np.sign(ro) == np.sign(rs)
    cs, cl = cont[sh & v].mean(), cont[lo & v].mean()
    o = np.array([h1, rho_s - rho_l, beta[2], cs - cl])
    if not extra: return o
    return o, {"rho_short": rho_s, "rho_long": rho_l, "cont_short": cs, "cont_long": cl, "O1_short": np.nanmean(O1[sh]), "O1_long": np.nanmean(O1[lo]),
               "n_short": int(sh.sum()), "n_long": int(lo.sum()), "b (all-state slope)": beta[1], "c": beta[2]}


def shift_null(s, k=5, w=15):
    n = len(s); return np.array([stats(np.roll(s, off), k, w) for off in range(20, n - 20, 3)])


res = {"n days": len(X), "span": [str(X.index.min().date()), str(X.index.max().date())], "share of days open below flip": round(float(np.nanmean(STATES["flip"])), 3)}
s0 = STATES["flip"]; obs, info = stats(s0, extra=True); null = shift_null(s0)
p_shift = [float((null[:, i] >= obs[i]).mean()) for i in range(4)]
bs = []
for _ in range(2000):
    idx = rng.integers(0, len(X), len(X)); bs.append(stats(s0[idx] if False else s0, 5, 15) if False else None)
# day-block bootstrap (resample days, keep each day's state)
B = []
for _ in range(2000):
    idx = rng.integers(0, len(X), len(X)); s = s0[idx]; sh = s == 1; lo = s == 0
    B.append([np.nanmean(O1[idx][sh]) - np.nanmean(O1[idx][lo]), np.nansum(CR[5][idx][sh]) / np.nansum(SQ[5][idx][sh]) - np.nansum(CR[5][idx][lo]) / np.nansum(SQ[5][idx][lo]),
              (np.sign(RO[15][idx]) == np.sign(RS[15][idx]))[sh].mean() - (np.sign(RO[15][idx]) == np.sign(RS[15][idx]))[lo].mean()])
B = np.array(B)
names = ["H1 range diff (sigma units)", "H2 rho diff (5-min)", "H3 interaction c", "H3 continuation diff"]
res["primary (state = 09:30 open vs pre-open flip)"] = {**{k: round(float(v), 4) for k, v in info.items()},
    **{names[i]: {"obs": round(float(obs[i]), 4), "p circular shift": round(p_shift[i], 4)} for i in range(4)},
    "bootstrap 90% CI H1": np.round(np.quantile(B[:, 0], [.05, .95]), 3).tolist(), "bootstrap 90% CI H2": np.round(np.quantile(B[:, 1], [.05, .95]), 4).tolist(),
    "bootstrap 90% CI H3 cont diff": np.round(np.quantile(B[:, 2], [.05, .95]), 3).tolist(), "n shifts": len(null)}
pp = sorted([(p_shift[0], "H1"), (p_shift[1], "H2"), (min(p_shift[2], p_shift[3]), "H3")]); holm = {}; run = 0
for i, (p, h) in enumerate(pp): run = max(run, min(1, p * (3 - i))); holm[h] = round(run, 4)
res["Holm (H3 uses the smaller of its two p; conservative note: not doubled)"] = holm
q = pd.qcut(X.d, 5, labels=False).to_numpy(); cont15 = np.sign(RO[15]) == np.sign(RS[15])
res["dose-response by quintile of distance to flip (q0 = furthest below)"] = {int(i): {"d median": round(float(np.median(X.d.to_numpy()[q == i])), 2), "O1 mean": round(float(np.nanmean(O1[q == i])), 3),
    "rho5": round(float(np.nansum(CR[5][q == i]) / np.nansum(SQ[5][q == i])), 4), "cont15": round(float(cont15[q == i].mean()), 3), "n": int((q == i).sum())} for i in range(5)}
res["Spearman(d, O1)"] = round(float(X.d.corr(X.O1, method="spearman")), 3)
res["VR6 mean short/long"] = [round(float(np.nanmean(X.vr6.to_numpy()[s0 == 1])), 3), round(float(np.nanmean(X.vr6.to_numpy()[s0 == 0])), 3)]
for lab, rr in (("implied VR6 from rho_short", info["rho_short"]), ("implied VR6 from rho_long", info["rho_long"])):
    res[lab] = round(float(1 + 2 * sum((1 - j / 6) * rr ** j for j in range(1, 6))), 3)
mv = {}
for sn, s in STATES.items():
    for k in (5, 10, 15):
        for w in (5, 15, 30):
            o, inf = stats(s, k, w, extra=True); nl = shift_null(s, k, w); z = (o - nl.mean(0)) / nl.std(0)
            mv[f"{sn}|{k}m|open{w}"] = {"H1 z": round(float(z[0]), 2), "H2 z": round(float(z[1]), 2), "H3 c z": round(float(z[2]), 2), "H3 cont z": round(float(z[3]), 2),
                                        "rho_s": round(float(inf["rho_short"]), 4), "rho_l": round(float(inf["rho_long"]), 4), "cont_s": round(float(inf["cont_short"]), 3), "cont_l": round(float(inf["cont_long"]), 3)}
res["multiverse"] = mv
res["multiverse median z"] = {h: round(float(np.median([v[h] for v in mv.values()])), 2) for h in ("H1 z", "H2 z", "H3 c z", "H3 cont z")}
ctrl = {}
for lab, msk in (("R1 2020-21", X.index < "2022-01-01"), ("R2 2022+", X.index >= "2022-01-01"),
                 ("VIX low third", X.vpct <= 1 / 3), ("VIX mid third", (X.vpct > 1 / 3) & (X.vpct < 2 / 3)), ("VIX high third", X.vpct >= 2 / 3)):
    s = np.where(np.asarray(msk), s0, np.nan); o, inf = stats(s, extra=True)
    ctrl[lab] = {"H1 diff": round(float(o[0]), 3), "H2 rho diff": round(float(o[1]), 4), "H3 c": round(float(o[2]), 4), "cont s/l": [round(float(inf["cont_short"]), 3), round(float(inf["cont_long"]), 3)],
                 "rho s/l": [round(float(inf["rho_short"]), 4), round(float(inf["rho_long"]), 4)], "O1 s/l": [round(float(inf["O1_short"]), 3), round(float(inf["O1_long"]), 3)], "n s/l": [inf["n_short"], inf["n_long"]]}
res["controls"] = ctrl
X.to_csv(HERE / "out" / "days.csv")
json.dump(res, open(HERE / "out" / "phase.json", "w"), indent=1, default=str)
print(json.dumps({k: v for k, v in res.items() if k != "multiverse"}, indent=1, default=str))
