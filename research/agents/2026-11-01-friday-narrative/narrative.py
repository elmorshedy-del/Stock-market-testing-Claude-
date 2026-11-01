"""Pre-registered chapters C1-C6 (@ 2d8274c) for Fri Oct 30. Usage: python narrative.py <db dir> <td dir> -> out/narrative.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; DB, TD = Path(sys.argv[1]), Path(sys.argv[2])
MICRO = HERE.parents[1] / "microstructure"; sys.path.insert(0, str(MICRO))
DAYS = ["2026-10-23", "2026-10-26", "2026-10-27", "2026-10-28", "2026-10-29"]; FRI = "2026-10-30"
ET = "America/New_York"


def es(day):
    d = pd.read_parquet(DB / f"ES_trades_{day}.parquet"); d = d[d.action == "T"]
    d.index = d.index.tz_convert(ET) if d.index.tz is not None else pd.to_datetime(d.ts_event).dt.tz_convert(ET)
    sz = d["size"].astype("int64"); d["signed"] = np.where(d.side == "B", sz, np.where(d.side == "A", -sz, 0))   # size is unsigned: cast before negating
    m = pd.DataFrame({"flow": d.signed.resample("1min").sum(), "px": d.price.resample("1min").last(), "vol": d["size"].astype("int64").resample("1min").sum()})
    m["px"] = m.px.ffill(); m["ret_bp"] = np.log(m.px).diff() * 1e4
    return m.between_time("09:30", "15:59")


def spy1m(day):
    d = pd.read_parquet(DB / f"SPY_1m_{day}.parquet"); d.index = d.index.tz_convert(ET); d["ret_bp"] = np.log(d.close).diff() * 1e4
    return d


E = {d: es(d) for d in DAYS + [FRI]}; S = {d: spy1m(d) for d in DAYS + [FRI]}
out = {}
w = lambda m, a, b: m.between_time(a, b)
# C1
c1 = {d: float(w(E[d], "09:30", "10:29").flow.sum()) for d in DAYS + [FRI]}
base = np.array([c1[d] for d in DAYS]); z = (c1[FRI] - base.mean()) / base.std(ddof=1)
def leadlag(d):
    e, s = w(E[d], "09:30", "10:29"), w(S[d], "09:30", "10:29")
    j = pd.concat([e.flow, s.ret_bp], axis=1, keys=["flow", "spy"]).dropna()
    return float(j.flow.corr(j.spy.shift(-1))), float(j.spy.corr(j.flow.shift(-1))), float(j.flow.corr(j.spy))
ll = {d: leadlag(d) for d in DAYS + [FRI]}
out["C1 open"] = {"ES signed contracts 09:30-10:30, Fri": int(c1[FRI]), "baseline days": {d: int(c1[d]) for d in DAYS}, "z": round(float(z), 2),
                  "Fri corr(ES flow_t, SPY ret_t+1)": round(ll[FRI][0], 3), "Fri corr(SPY ret_t, ES flow_t+1)": round(ll[FRI][1], 3), "Fri same-minute corr": round(ll[FRI][2], 3),
                  "baseline mean lead / reverse": [round(np.mean([ll[d][0] for d in DAYS]), 3), round(np.mean([ll[d][1] for d in DAYS]), 3)],
                  "ES price 09:30 -> 10:29": [float(w(E[FRI], "09:30", "09:30").px.iloc[0]), float(w(E[FRI], "10:29", "10:29").px.iloc[0])]}
out["C1 open"]["claim passes (z <= -1 and ES leads)"] = bool(z <= -1 and ll[FRI][0] > ll[FRI][1])
# C2
def grind(d):
    e = w(E[d], "10:30", "14:29"); f5 = e.flow.resample("5min").sum(); r5 = e.ret_bp.resample("5min").sum()
    ac = float(f5.autocorr(1)); x = e.flow / 1000; y = e.ret_bp; ok = x.notna() & y.notna()
    lam = float(np.polyfit(x[ok], y[ok], 1)[0])
    return ac, lam, float(e.flow.sum()), float(e.vol.sum())
G = {d: grind(d) for d in DAYS + [FRI]}
out["C2 grind"] = {"Fri lag-1 autocorr of 5-min ES flow": round(G[FRI][0], 3), "baseline": {d: round(G[d][0], 3) for d in DAYS},
                   "Fri Kyle lambda (bp per 1k signed contracts)": round(G[FRI][1], 3), "baseline lambda": {d: round(G[d][1], 3) for d in DAYS},
                   "Fri signed contracts 10:30-14:30": int(G[FRI][2]), "baseline signed": {d: int(G[d][2]) for d in DAYS},
                   "Fri volume": int(G[FRI][3]), "baseline volume mean": int(np.mean([G[d][3] for d in DAYS]))}
a_ok = G[FRI][0] > np.median([G[d][0] for d in DAYS]); b_ok = G[FRI][1] > np.median([G[d][1] for d in DAYS])
out["C2 grind"]["(a) above median"], out["C2 grind"]["(b) above median"] = bool(a_ok), bool(b_ok)
out["C2 grind"]["verdict"] = "pass" if (a_ok and b_ok) else ("falsified (both at/below median)" if not (a_ok or b_ok) else "partial")
# C3a Arca bid depth near 750 vs same distance from price elsewhere
mb = pd.read_parquet(DB / f"SPY_mbp10_{FRI}.parquet", columns=[f"bid_px_{i:02d}" for i in range(10)] + [f"bid_sz_{i:02d}" for i in range(10)] + ["ask_px_00"])
mb.index = mb.index.tz_convert(ET); mb = mb.between_time("09:30", "15:59")
snap = mb.resample("5s").last().dropna()
mid = (snap.bid_px_00 + snap.ask_px_00) / 2
bp = snap[[f"bid_px_{i:02d}" for i in range(10)]].to_numpy(); bs = snap[[f"bid_sz_{i:02d}" for i in range(10)]].to_numpy()
def band_depth(lo, hi):
    lo = np.asarray(lo)[:, None]; hi = np.asarray(hi)[:, None]
    return ((bp >= lo) & (bp <= hi + 1e-9)).astype(float).__mul__(bs).sum(axis=1)
win = (snap.index.time >= pd.Timestamp("14:40").time()) & (snap.index.time < pd.Timestamp("14:55").time())
d750 = band_depth(np.full(len(snap), 750.0), np.full(len(snap), 750.5))
dist_lo = float(np.median((mid[win] - 750.5))); dist_hi = float(np.median((mid[win] - 750.0)))
dsame = band_depth(mid - dist_hi, mid - dist_lo)          # same distance below mid, all day
s750 = pd.Series(d750, index=snap.index)[win].mean()
by15 = pd.Series(dsame, index=snap.index).resample("15min").mean()
rank = float((by15 < s750).mean())
out["C3a 750 bid depth"] = {"band": "750.00-750.50", "median distance below mid in 14:40-14:55": [round(dist_lo, 2), round(dist_hi, 2)],
                            "mean Arca bid shares in band, 14:40-14:55": int(s750), "same-distance band, other 15-min windows: median": int(by15.median()),
                            "pct rank of 14:40-14:55 among the day's windows": round(rank, 2), "claim passes (top quartile)": bool(rank >= 0.75), "falsified (not top half)": bool(rank < 0.5)}
# depth profile: average bid size at each cent level around 750 while visible
lv = {}
for k in np.round(np.arange(749.8, 752.01, 0.1), 2):
    m_ = (np.abs(bp - k) < 0.051); sz = (m_ * bs).sum(axis=1); vis = m_.any(axis=1)
    lv[str(k)] = int(sz[vis & win].mean()) if (vis & win).any() else None
out["C3a 750 bid depth"]["avg bid size by 10-cent bucket when visible (14:40-14:55)"] = lv
tot10 = pd.Series(bs.sum(axis=1), index=snap.index); bb = snap.bid_px_00
near = (bb >= 750.30) & (bb <= 750.55)
w10 = tot10.resample("10min").mean()
out["C3a 750 bid depth"]["DEVIATION: band test degenerate (top 10 levels span ~$0.10)"] = True
out["C3a 750 bid depth"]["alt (post hoc): mean top-10 bid shares when best bid 750.30-750.55"] = int(tot10[near].mean()) if near.any() else None
out["C3a 750 bid depth"]["alt: all-day median of 10-min mean top-10 bid shares"] = int(w10.median())
out["C3a 750 bid depth"]["alt: pct rank of the near-750 mean among 10-min windows"] = round(float((w10 < tot10[near].mean()).mean()), 2) if near.any() else None
out["C3a 750 bid depth"]["alt: seconds with best bid 750.30-750.55 (5s snapshots x5)"] = int(near.sum() * 5)
# C3b exhaustion
e = E[FRI]; pre15 = w(e, "14:37", "14:51").flow.mean(); pre30 = w(e, "14:07", "14:36").flow.mean()
out["C3b exhaustion"] = {"ES signed contracts/min 14:07-14:36": round(float(pre30), 1), "14:37-14:51": round(float(pre15), 1),
                         "claim passes (less negative into the low)": bool(pre15 > pre30), "most negative 5-min ES flow time": str(e.flow.resample("5min").sum().idxmin().time())}
# C4a buyers after the low
post = w(e, "14:52", "15:01").flow.sum(); post30 = w(e, "14:52", "15:21").flow.sum()
out["C4a rebound"] = {"ES signed contracts 14:52-15:02": int(post), "14:52-15:22": int(post30), "claim passes (>0)": bool(post > 0),
                      "ES signed contracts 15:00-15:59": int(w(e, "15:00", "15:59").flow.sum()), "baseline 15:00-15:59 mean": int(np.mean([w(E[d], "15:00", "15:59").flow.sum() for d in DAYS]))}
# C4b Arca closing imbalance
def imb(day):
    d = pd.read_parquet(DB / f"SPY_imb_{day}.parquet"); d.index = d.index.tz_convert(ET); d = d[d.auction_type == "C"]
    r = {}
    for t in ("15:50", "15:55", "15:59"):
        x = d.between_time("15:00", t)
        if len(x): last = x.iloc[-1]; r[t] = {"side": last.side, "imbalance qty": int(last.total_imbalance_qty), "paired": int(last.paired_qty), "ind match": float(last.ind_match_price), "ref": float(last.ref_price)}
    return r
IM = {d: imb(d) for d in DAYS + [FRI]}
f = IM[FRI].get("15:59", IM[FRI].get("15:55"))
out["C4b closing imbalance (Arca)"] = {"Fri": IM[FRI], "baseline 15:59 sides": {d: (IM[d].get("15:59") or {}).get("side") for d in DAYS},
                                      "claim passes (buy side)": bool(f and f["side"] == "B"), "note": "side B = buy imbalance, A = sell imbalance"}
# C5 election premium from the Oct 30 chain
import td_gamma as t
from options_flow import greeks  # noqa: F401
ev = pd.read_csv(TD / "SPY_eod_20261030.csv.gz"); ev["date"] = pd.to_datetime(ev.created.astype(str).str[:10]); ev = ev[ev.date == pd.Timestamp(FRI)]
ev["expiration"] = pd.to_datetime(ev.expiration); ev["cp"] = np.where(ev.right.str.upper().str.startswith("C"), "C", "P"); ev["mid"] = (ev.bid + ev.ask) / 2
Sx = t.spot_from_parity(ev.assign(oi=0.0)) if hasattr(t, "spot_from_parity") else 755.72
rows = []
for exp, x in ev.groupby("expiration"):
    if exp <= pd.Timestamp(FRI) or (exp - pd.Timestamp(FRI)).days > 14: continue
    T = ((exp - pd.Timestamp(FRI)).days) / 365
    k = x.strike.iloc[(x.strike - Sx).abs().argsort().iloc[0]]; q = x[(x.strike == k) & (x.bid > 0)]
    ivs = t.implied_vol(q.mid.to_numpy(), Sx, q.strike.to_numpy(), np.full(len(q), T), (q.cp == "C").to_numpy())
    rows.append({"expiry": str(exp.date()), "T days": int((exp - pd.Timestamp(FRI)).days), "ATM strike": float(k), "ATM IV": float(np.nanmean(ivs)), "total var": float(np.nanmean(ivs) ** 2 * T)})
TS = pd.DataFrame(rows).sort_values("T days")
TS["fwd var to next"] = TS["total var"].shift(-1) - TS["total var"]
TS["fwd vol (ann.) of interval"] = np.sqrt((TS["fwd var to next"] / ((TS["T days"].shift(-1) - TS["T days"]) / 365)).clip(lower=0))
fwd = dict(zip(TS.expiry + "->" + TS.expiry.shift(-1).fillna(""), TS["fwd var to next"]))
def fv(a, b): return fwd.get(f"{a}->{b}")
el = fv("2026-11-03", "2026-11-04"); nb = [v for v in (fv("2026-11-02", "2026-11-03"), fv("2026-11-04", "2026-11-05"), fv("2026-11-05", "2026-11-06")) if v is not None and v > 0]
ratio = el / np.mean(nb) if (el is not None and nb) else None
out["C5 election premium"] = {"spot": round(float(Sx), 2), "term structure": TS.round(5).to_dict("records"),
                              "election-night interval variance / neighbours' mean": round(float(ratio), 2) if ratio else None,
                              "claim passes (>= 1.5x)": bool(ratio and ratio >= 1.5)}
# C6 put trades around the low
p = pd.read_parquet(DB / f"SPY_puts_tcbbo_{FRI}.parquet"); p.index = p.index.tz_convert(ET)
p["size"] = p["size"].astype("int64"); p["mid"] = (p.bid_px_00 + p.ask_px_00) / 2; p["sell"] = p.price <= p.mid - 1e-9; p["buy"] = p.price >= p.mid + 1e-9
p["exp"] = p.symbol.str[6:12]
c6 = {}
for ex, lab in (("261030", "Oct 30 (0DTE) 745-765"), ("261120", "Nov 20 740-760")):
    x = p[p.exp == ex]
    for wl, (a, b) in (("13:30-14:30", ("13:30", "14:29")), ("14:30-15:00", ("14:30", "14:59")), ("15:00-15:30", ("15:00", "15:29"))):
        y = x.between_time(a, b); v = y["size"].sum()
        c6[f"{lab} {wl}"] = {"contracts/min": round(float(v / max(1, (pd.Timestamp(b) - pd.Timestamp(a)).seconds / 60 + 1)), 0),
                             "seller-initiated share": round(float(y.loc[y.sell, "size"].sum() / v), 3) if v else None,
                             "buyer-initiated share": round(float(y.loc[y.buy, "size"].sum() / v), 3) if v else None}
s_low = {k: v for k, v in c6.items() if "14:30-15:00" in k}; s_pre = {k: v for k, v in c6.items() if "13:30-14:30" in k}
passes = all((s_low[k]["seller-initiated share"] or 0) > (s_pre[k.replace("14:30-15:00", "13:30-14:30")]["seller-initiated share"] or 0) for k in s_low)
skew_buy = all((s_low[k]["buyer-initiated share"] or 0) > (s_low[k]["seller-initiated share"] or 0) for k in s_low)
out["C6 put monetization"] = {**c6, "claim passes (more selling at the low in both expiries)": bool(passes), "falsified (put trades skew to buying at the low)": bool(skew_buy)}
json.dump(out, open(HERE / "out" / "narrative.json", "w"), indent=1, default=str)
print(json.dumps(out, indent=1, default=str))
