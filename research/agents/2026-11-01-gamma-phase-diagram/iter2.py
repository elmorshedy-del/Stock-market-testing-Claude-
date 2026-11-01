"""Iteration 2 (pre-registered @ f09c68a): I-a/I-b/I-c (dealer gamma vs stress), II (VIX x gamma continuation, SPY + QQQ check),
III (09:45 rest-of-day range nowcast, fit 2020-23, test 2024-26). Usage: python iter2.py <SPY 1m> <QQQ 1m> <VIX json>"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; ET = "America/New_York"; rng = np.random.default_rng(1)
X = pd.read_csv(HERE / "out" / "days.csv", index_col=0, parse_dates=True)
r = json.load(open(sys.argv[3]))["chart"]["result"][0]
vix = pd.Series(r["indicators"]["quote"][0]["close"], index=pd.to_datetime(r["timestamp"], unit="s").tz_localize("UTC").tz_convert(ET).normalize().tz_localize(None)).dropna()
vix = vix[~vix.index.duplicated(keep="last")]


def intraday(path):
    m = pd.read_parquet(path, columns=["open", "high", "low", "close"]); m.index = m.index.tz_convert(ET)
    m = m[(m.index.time >= pd.Timestamp("09:30").time()) & (m.index.time < pd.Timestamp("16:00").time())]
    m["day"] = m.index.normalize().tz_localize(None); m["mins"] = (m.index.hour - 9) * 60 + m.index.minute - 30
    f = m.groupby("day").mins.min(); m = m[m.day.isin(f[f == 0].index)]
    g = m.groupby("day"); first15 = m[m.mins < 15].groupby("day"); rest = m[m.mins >= 15].groupby("day")
    out = pd.DataFrame({"open": g.open.first(), "close": g.close.last(), "high": g.high.max(), "low": g.low.min(), "n": g.close.size(),
                        "h15": first15.high.max(), "l15": first15.low.min(), "p0945": m[m.mins <= 14].groupby("day").close.last(),
                        "hrest": rest.high.max(), "lrest": rest.low.min()})
    return out[out.n >= 200]


S = intraday(sys.argv[1]); X = X.join(S[["h15", "l15", "hrest", "lrest"]], how="left")
X["R15"] = (X.h15 - X.l15) / X.open / X.sig; X["Orest"] = (X.hrest - X.lrest) / X.p0945 / X.sig
X["short"] = (X.open < X.flip_incl).astype(float)
res = {}


def ols(y, Z):
    Z = np.c_[np.ones(len(Z)), Z]; b = np.linalg.lstsq(Z, y, rcond=None)[0]; return b


def block_boot(fn, n, block=20, B=2000):
    starts = np.arange(n); out = []
    for _ in range(B):
        idx = np.concatenate([np.arange(s, min(s + block, n)) for s in rng.choice(starts, n // block + 1)])[:n]; out.append(fn(idx))
    return np.array(out)


# ---- I-a controls
P = X.copy()
P["prev_close"] = P.close.shift(1); P["prev2_close"] = P.close.shift(2)
P["abs_prev_ret"] = (np.log(P.prev_close / P.prev2_close)).abs() / P.sig
P["prev_O1"] = P.O1.shift(1); P["abs_gap"] = (np.log(P.open / P.prev_close)).abs() / P.sig
vx = vix.reindex(P.index, method="ffill"); P["dvix_prev"] = (vx.shift(1) - vx.shift(2))
P["ret5"] = np.log(P.prev_close / P.close.shift(6)) / P.sig
cols = ["short", "abs_prev_ret", "prev_O1", "abs_gap", "dvix_prev", "ret5"]
Q = P.dropna(subset=cols + ["O1"]); y = Q.O1.to_numpy(); Z = Q[cols].to_numpy()
b_raw = ols(y, Q[["short"]].to_numpy())[1]; b_full = ols(y, Z)
bb = block_boot(lambda idx: ols(y[idx], Z[idx])[1], len(Q))
res["I-a controls"] = {"n": len(Q), "raw below-flip coef": round(float(b_raw), 3), "with controls": round(float(b_full[1]), 3),
                       "kept share": round(float(b_full[1] / b_raw), 2), "block-bootstrap 90% CI": np.round(np.quantile(bb, [.05, .95]), 3).tolist(),
                       "p (coef <= 0)": round(float((bb <= 0).mean()), 4), "control coefs": dict(zip(cols[1:], np.round(b_full[2:], 3).tolist())),
                       "pass (p<0.05 and kept >= 0.5)": bool((bb <= 0).mean() < 0.05 and b_full[1] / b_raw >= 0.5)}
# ---- I-b natural experiment: price part vs flip part of the change in distance to flip
P["price_part"] = (P.open - P.open.shift(1)) / (P.sig * P.open); P["flip_part"] = -(P.flip_incl - P.flip_incl.shift(1)) / (P.sig * P.open)
P["dO1"] = P.O1 - P.O1.shift(1)
consec = (P.index.to_series().diff().dt.days <= 4)
Qb = P[consec].dropna(subset=["price_part", "flip_part", "dO1", "dvix_prev"])
Qb = Qb[(Qb.price_part.abs() < 5) & (Qb.flip_part.abs() < 5)]
yb = Qb.dO1.to_numpy(); Zb = Qb[["price_part", "flip_part"]].to_numpy()
bfull = ols(yb, Zb); bbb = block_boot(lambda idx: ols(yb[idx], Zb[idx]), len(Qb))
res["I-b natural experiment"] = {"n": len(Qb), "coef price part": round(float(bfull[1]), 3), "coef flip part": round(float(bfull[2]), 3),
    "90% CI price part": np.round(np.quantile(bbb[:, 1], [.05, .95]), 3).tolist(), "90% CI flip part": np.round(np.quantile(bbb[:, 2], [.05, .95]), 3).tolist(),
    "p flip coef >= 0": round(float((bbb[:, 2] >= 0).mean()), 4),
    "sd price part / flip part": [round(float(Qb.price_part.std()), 3), round(float(Qb.flip_part.std()), 3)],
    "corr(flip part, dVIX prev)": round(float(Qb.flip_part.corr(Qb.dvix_prev)), 3), "corr(flip part, price part)": round(float(Qb.flip_part.corr(Qb.price_part)), 3),
    "pass (flip coef < 0, p < 0.05)": bool(bfull[2] < 0 and (bbb[:, 2] >= 0).mean() < 0.05)}
# opex-Monday subset (flip moved by expiry roll-off)
def third_friday(ts): d = pd.Timestamp(ts.year, ts.month, 15); return d + pd.Timedelta(days=(4 - d.weekday()) % 7)
opx_next = set()
for ym in pd.period_range("2020-01", "2026-10", freq="M"):
    tf = third_friday(ym.to_timestamp()); nxt = P.index[P.index > tf]
    if len(nxt): opx_next.add(nxt[0])
Qo = Qb[Qb.index.isin(opx_next)]
if len(Qo) > 20:
    bo = ols(Qo.dO1.to_numpy(), Qo[["price_part", "flip_part"]].to_numpy())
    res["I-b day after monthly opex"] = {"n": len(Qo), "coef price part": round(float(bo[1]), 3), "coef flip part": round(float(bo[2]), 3), "sd flip part": round(float(Qo.flip_part.std()), 3)}
# ---- I-c magnitude at fixed distance (below-flip days): partial Spearman of O1 with (1 - gpct) controlling d
Sd = P[(P.short == 1)].dropna(subset=["gpct", "d", "O1"])
rk = lambda s: s.rank().to_numpy()
def partial(a, b, c):
    ra, rb, rc = rk(a), rk(b), rk(c); ea = ra - np.polyval(np.polyfit(rc, ra, 1), rc); eb = rb - np.polyval(np.polyfit(rc, rb, 1), rc); return float(np.corrcoef(ea, eb)[0, 1])
pc = partial(Sd.O1, 1 - Sd.gpct, Sd.d)
bpc = block_boot(lambda idx: partial(Sd.O1.iloc[idx], 1 - Sd.gpct.iloc[idx], Sd.d.iloc[idx]), len(Sd), B=1000)
res["I-c magnitude"] = {"n": len(Sd), "partial Spearman(O1, more short gamma | d)": round(pc, 3), "90% CI": np.round(np.quantile(bpc, [.05, .95]), 3).tolist(),
                        "p <= 0": round(float((bpc <= 0).mean()), 4), "pass (> 0, p < 0.05)": bool(pc > 0 and (bpc <= 0).mean() < 0.05)}
# ---- II exploratory: VIX x state continuation with CIs, SPY and QQQ
def cont_table(D, state):
    D = D.copy(); D["cont"] = (np.sign(D.ro15) == np.sign(D.rest15)).astype(float)
    D["vt"] = pd.cut(D.vpct, [-0.01, 1 / 3, 2 / 3, 1.01], labels=["low", "mid", "high"]); D["st"] = np.where(state, "below", "above")
    out = {}
    for (v, s), g in D.groupby(["vt", "st"], observed=True):
        bsv = [g.cont.sample(len(g), replace=True, random_state=i).mean() for i in range(500)]
        out[f"{v} VIX | {s} flip"] = {"cont": round(float(g.cont.mean()), 3), "90% CI": np.round(np.quantile(bsv, [.05, .95]), 3).tolist(), "n": len(g)}
    return out
res["II SPY continuation (exploratory)"] = cont_table(X, X.short == 1)
qg = pd.read_csv(HERE.parents[1] / "microstructure" / "out" / "td_gamma_QQQ.csv", parse_dates=["date"]).set_index("date")
Qd = intraday(sys.argv[2]); Qd = Qd.join(qg.flip_classic.shift(1).rename("flip_prev"), how="inner")
Qd["sig"] = vix.shift(1).reindex(Qd.index, method="ffill") / 100 / np.sqrt(252) * 1.25      # NDX moves ~1.25x SPX; scale only matters for O1 units
Qd = Qd.dropna(subset=["flip_prev", "sig"])
Qd["ro15"] = np.log(Qd.p0945 / Qd.open); Qd["rest15"] = np.log(Qd.close / Qd.p0945)
Qd["vpct"] = X.vpct.reindex(Qd.index); Qd["O1"] = (Qd.high - Qd.low) / Qd.open / Qd.sig
qs = Qd.open < Qd.flip_prev
res["II QQQ check (own prior-close flip; NOT independent dates)"] = {"n": len(Qd), "share below flip": round(float(qs.mean()), 3),
    "H1 range ratio below/above": round(float(Qd.O1[qs].mean() / Qd.O1[~qs].mean()), 3), "continuation table": cont_table(Qd.dropna(subset=["vpct"]), qs[Qd.vpct.notna()] if False else (Qd.dropna(subset=["vpct"]).open < Qd.dropna(subset=["vpct"]).flip_prev))}
# ---- III nowcast of rest-of-day range at 09:45
N = X.dropna(subset=["Orest", "R15", "d", "vpct"]).copy(); N["absr15"] = N.ro15.abs(); N["dclip"] = N.d.clip(-4, 4)
N["y"] = np.log(N.Orest)
train, test = N[N.index < "2024-01-01"], N[N.index >= "2024-01-01"]
specs = {"VIX only (constant in sigma units)": [], "first-15 range only": ["R15"], "state only (short, d)": ["short", "dclip"],
         "all (short, d, R15, |r15|, VIX pct)": ["short", "dclip", "R15", "absr15", "vpct"]}
def fit_pred(cols):
    Ztr = np.c_[np.ones(len(train))] if not cols else np.c_[np.ones(len(train)), train[cols].to_numpy()]
    Zte = np.c_[np.ones(len(test))] if not cols else np.c_[np.ones(len(test)), test[cols].to_numpy()]
    b = np.linalg.lstsq(Ztr, train.y, rcond=None)[0]; resid = train.y - Ztr @ b
    return Zte @ b, resid
base_pred, _ = fit_pred([]); sst = ((test.y - test.y.mean()) ** 2).sum()
nc = {}
for name, cols in specs.items():
    pr, resid = fit_pred(cols); sse = ((test.y - pr) ** 2).sum()
    r2 = 1 - sse / ((test.y - base_pred) ** 2).sum()
    qs_ = np.quantile(resid, [0.2, 0.5, 0.8]); cover = [float((test.y <= pr + q).mean()) for q in qs_]
    nc[name] = {"OOS R2 vs VIX-only": round(float(r2), 3), "coverage of 20/50/80% quantiles": np.round(cover, 3).tolist()}
pr_all, resid_all = fit_pred(specs["all (short, d, R15, |r15|, VIX pct)"]); pr_r15, _ = fit_pred(["R15"])
def gain(idx, a, b): yy = test.y.to_numpy()[idx]; return 1 - ((yy - a[idx]) ** 2).sum() / ((yy - b[idx]) ** 2).sum()
g_all = block_boot(lambda idx: gain(idx, np.asarray(pr_all), np.asarray(base_pred)), len(test), B=1000)
g_state = block_boot(lambda idx: gain(idx, np.asarray(pr_all), np.asarray(pr_r15)), len(test), B=1000)
# calibration of P(rest range > 1 sigma) via the lognormal residual distribution
from math import erf, sqrt
sd = float(np.std(resid_all)); p_gt1 = 0.5 * (1 - np.vectorize(lambda z: erf(z / sqrt(2)))((0 - pr_all) / sd))
dec = pd.qcut(p_gt1, 5, labels=False, duplicates="drop"); calib = {}
for i in sorted(set(dec)):
    msk = dec == i; calib[int(i)] = {"forecast": round(float(p_gt1[msk].mean()), 3), "observed": round(float((test.Orest.to_numpy()[msk] > 1).mean()), 3), "n": int(msk.sum())}
res["III nowcast (fit 2020-23, test 2024-26)"] = {"n train/test": [len(train), len(test)], "models": nc,
    "R2 gain all vs VIX-only, 90% CI": np.round(np.quantile(g_all, [.05, .95]), 3).tolist(),
    "R2 gain all vs first-15-range-only (what state adds), 90% CI": np.round(np.quantile(g_state, [.05, .95]), 3).tolist(),
    "calibration P(rest range > 1 sigma) by forecast quintile": calib,
    "pass (gain CI > 0 and calibration within 5 pts)": bool(np.quantile(g_all, 0.05) > 0 and all(abs(v["forecast"] - v["observed"]) <= 0.05 for v in calib.values()))}
json.dump(res, open(HERE / "out" / "iter2.json", "w"), indent=1, default=str)
print(json.dumps(res, indent=1, default=str))
