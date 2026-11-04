"""D4: Oct 27 in flow-physics, measurements unchanged (flowlib imported; A4/A5 logic copied from a4_wicks.py / a5_imbalance.py).
Usage: python run_d4.py -> out/d4.json"""
import datetime as dt
import json
import sys
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent; D = HERE / "data"; FP = HERE.parent / "2026-10-27-flow-physics"
sys.path.insert(0, str(FP))
from flowlib import load_trades, merge_orders, kyle_lambda, hawkes_day   # noqa: E402
base = pd.read_csv(FP / "out" / "a_daily.csv"); res = {}
pctl = lambda v, ref: round(float((np.asarray(ref) < v).mean()), 2)

# ---- A1/A2 (a_flow.py recipe) ----
for sym in ("ES", "TSLA"):
    d = load_trades(D / f"{sym}_trades_20261027.parquet"); m = merge_orders(d)
    o, c = d.price.iloc[0], d.price.iloc[-1]; bv, sv = d["size"][d.sign > 0].sum(), d["size"][d.sign < 0].sum()
    lam, r2 = kyle_lambda(d); hw = hawkes_day(m, pd.Timestamp("2026-10-27 13:30", tz="UTC"))
    b = base[base.sym == sym]
    row = {"ret %": round(float(100 * (c / o - 1)), 2), "delta % of vol": round(float(100 * (bv - sv) / (bv + sv)), 2), "lambda (pts per 1k net)": round(float(lam * 1000), 4),
           "hawkes n median": round(float(hw.n.median()), 3)}
    row["pctile vs baseline (delta, lambda, n)"] = [pctl(row["delta % of vol"], b["delta % of vol"]), pctl(row["lambda (pts per 1k net)"], b["lambda (pts per 1k net)"]), pctl(row["hawkes n median"], b["hawkes n median"])]
    row["baseline sessions"] = int(len(b)); row["baseline median (delta, lambda, n)"] = [round(float(b["delta % of vol"].median()), 2), round(float(b["lambda (pts per 1k net)"].median()), 4), round(float(b["hawkes n median"].median()), 3)]
    # ES: same-sign-as-return check from A1 ("driven" = delta with the move)
    res[f"A1/A2 {sym}"] = row
    if sym == "ES":
        x = d
    else:
        tt = d

# ---- A4 wicks (a4_wicks.py segment logic) ----
def segment(x, a, b):
    s = x[(x.ts_event >= a) & (x.ts_event <= b)]; mins = max((b - a).total_seconds() / 60, 0.5)
    bv = s["size"][s.sign > 0].sum(); sv = s["size"][s.sign < 0].sum(); prog = (s.price.iloc[-1] - s.price.iloc[0]) if len(s) else np.nan
    return {"minutes": mins, "buy/min": bv / mins, "sell/min": sv / mins, "delta/min": (bv - sv) / mins, "pts per 1k bought": 1000 * prog / bv if bv else np.nan}


H = x.price.max(); th = x.loc[x.price.idxmax(), "ts_event"]; t0 = x.ts_event.iloc[0]
pre = x[x.ts_event <= th]; below = pre[pre.price < H * (1 - 0.001)]; tb = below.ts_event.iloc[-1]; a = max(t0, tb - pd.Timedelta("30min"))
e, fz, after = segment(x, a, tb), segment(x, tb, th), segment(x, th, th + pd.Timedelta("10min"))
a4b = json.load(open(FP / "out" / "a4.json"))
res["A4 ES Oct 27 (flip-wick day)"] = {"high": float(H), "high time ET": th.tz_convert("America/New_York").strftime("%H:%M:%S"), "final segment minutes": round(fz["minutes"], 1),
    "buy/min ratio (final 0.1% vs earlier run)": round(fz["buy/min"] / e["buy/min"], 3), "exhaustion (ratio < 1)": bool(fz["buy/min"] / e["buy/min"] < 1),
    "absorption ratio": round(fz["pts per 1k bought"] / e["pts per 1k bought"], 3) if e["pts per 1k bought"] else None,
    "sell/min next 10 min vs earlier run": round(after["sell/min"] / e["sell/min"], 3), "registered prediction": "exhaustion (buy/min ratio < 1)",
    "prior summary (flip days / other days)": a4b["summary"]}
# MBO refill at the high (a4_wicks.refill, unchanged)
mbo = pd.read_parquet(D / "ES_mbo_20261027.parquet", columns=["ts_event", "action", "side", "price", "size"])
mbo = mbo[mbo.ts_event >= pd.Timestamp("2026-10-27 13:30", tz="UTC")]; tr = mbo[mbo.action == "T"]
Hm = tr.price.max(); thm = tr.loc[tr.price.idxmax(), "ts_event"]


def refill(t_c, P, win="5min"):
    w = mbo[(mbo.ts_event >= t_c - pd.Timedelta(win)) & (mbo.ts_event <= t_c + pd.Timedelta(win)) & (mbo.side == "A") & (mbo.price.between(P - 0.001, P + 0.251))]
    mins = 2 * pd.Timedelta(win).total_seconds() / 60
    added = int(w.loc[w.action == "A", "size"].sum()); canc = int(w.loc[w.action == "C", "size"].sum()); filled = int(w.loc[w.action == "F", "size"].sum())
    return {"added/min": round(added / mins, 1), "cancelled/min": round(canc / mins, 1), "filled/min": round(filled / mins, 1),
            "refill ratio (added/filled contracts)": round(added / max(filled, 1), 2), "net new offers/min": round((added - canc) / mins, 1)}


px = tr.set_index("ts_event").price.resample("5min").max().dropna()
sw = px[(px.shift(1) < px) & (px.shift(-1) < px)].sort_values(ascending=False); sw = sw[(abs(sw.index - thm) > pd.Timedelta("20min"))].head(10)
rr = [refill(t + pd.Timedelta("2min30s"), P)["net new offers/min"] for t, P in sw.items()]
res["A4 MBO Oct 27"] = {"day high": float(Hm), "time ET": thm.tz_convert("America/New_York").strftime("%H:%M:%S"), "at the high": refill(thm, Hm),
                        "placebo median net new offers/min (10 other swing highs)": round(float(np.median(rr)), 2), "placebo values": rr,
                        "Oct 20 for comparison": a4b["MBO Oct 20"]["at the high (price and 1 tick above)"]}
# the 15:50 drop in ES: signed flow by minute 15:45-16:00 vs the day's per-minute baseline
xe = x.set_index("ts_event"); dm = (xe["size"] * xe.sign).resample("1min").sum(); pm = xe.price.resample("1min").last().ffill()
etm = dm.index.tz_convert("America/New_York").strftime("%H:%M")
win = (etm >= "15:45") & (etm <= "15:59")
res["ES 15:45-16:00 by minute (net aggressive contracts, last price)"] = {k: [int(v), float(p)] for k, v, p in zip(etm[win], dm[win], pm[win])}
res["ES day per-minute net aggression sd"] = round(float(dm.std()), 1)

# ---- A5 closing imbalance (a5_imbalance.py recipe) ----
SYMS = ["SPY", "TSLA", "GOOGL", "AMZN", "NVDA", "AVGO", "MSFT", "AAPL", "META", "QQQ"]
imb = pd.concat([pd.read_parquet(D / "SPY_imbalance_20261027.parquet"), pd.read_parquet(D / "NAS_imbalance_20261027.parquet")], ignore_index=True)
imb["et"] = pd.to_datetime(imb.ts_event, utc=True).dt.tz_convert("America/New_York")
imb = imb[(imb.auction_type == "C") & (imb.et.dt.strftime("%H:%M:%S") >= "15:50:00")]
first = imb.sort_values("et").groupby("symbol").head(1)


def yb(sym, iv, rng):
    u = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range={rng}&interval={iv}"
    r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=20))["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    idx = pd.to_datetime(r["timestamp"], unit="s", utc=True).tz_convert("America/New_York")
    return pd.DataFrame({k: q[k] for k in ("open", "close", "volume")}, index=idx).dropna(subset=["close"])


rows = []
for sym in SYMS:
    r = first[first.symbol == sym]
    if not len(r): continue
    r = r.iloc[0]; b5 = yb(sym, "5m", "1mo").between_time("09:30", "15:59"); bd = yb(sym, "1d", "3mo"); bd.index = bd.index.date
    day = dt.date(2026, 10, 27); t = b5[b5.index.date == day]; p50 = t.loc[t.index.strftime("%H:%M") == "15:50", "open"]
    if not len(p50) or day not in bd.index: continue
    sgn = 1 if r.side == "B" else (-1 if r.side == "A" else 0); dollars = sgn * float(r.total_imbalance_qty) * float(r.ref_price)
    dvol = float(bd.loc[day, "volume"] * bd.loc[day, "close"])
    rows.append({"sym": sym, "day": str(day), "imb $m": dollars / 1e6, "imb % of day $vol": 100 * dollars / dvol, "ret 15:50-close %": 100 * (t.close.iloc[-1] / p50.iloc[0] - 1), "msg time": r.et.strftime("%H:%M:%S")})
new = pd.DataFrame(rows); old = pd.read_csv(FP / "out" / "a5_rows.csv"); allr = pd.concat([old, new], ignore_index=True)
rho = spearmanr(allr["imb % of day $vol"], allr["ret 15:50-close %"])[0]
rng = np.random.default_rng(0); days = allr.day.unique(); g = {d_: z for d_, z in allr.groupby("day")}
bs = np.array([spearmanr(*pd.concat([g[d_] for d_ in rng.choice(days, len(days))])[["imb % of day $vol", "ret 15:50-close %"]].T.to_numpy())[0] for _ in range(2000)])
res["A5 Oct 27 rows"] = new.round(4).to_dict(orient="records")
res["A5 pooled with Oct 27"] = {"symbol-days": int(len(allr)), "Spearman rho": round(float(rho), 3), "p (bootstrap by day, rho <= 0)": round(float(np.mean(bs <= 0)), 4),
                                "passes (rho > 0, p < 0.05)": bool(rho > 0 and np.mean(bs <= 0) < 0.05), "Oct 27 alone: share moving with the imbalance": round(float((np.sign(new["imb % of day $vol"]) == np.sign(new["ret 15:50-close %"])).mean()), 2) if len(new) else None}

# ---- A6 TSLA round-dollar crosses (registered definition) ----
mt = merge_orders(tt); t_ = mt.t; buy = mt[mt.sign > 0].t
cross = []
for L in range(int(np.floor(tt.price.min())) + 1, int(np.ceil(tt.price.max())) + 1):
    hit = tt[tt.price > L - 0.10]
    if not len(hit) or tt.price.iloc[0] > L - 0.10: continue      # an upward first cross after trading below
    tc = hit.ts_event.iloc[0]
    nb = ((buy > tc - pd.Timedelta("60s")) & (buy <= tc)).sum(); na = ((buy > tc) & (buy <= tc + pd.Timedelta("60s"))).sum()
    cross.append({"level": L, "time ET": tc.tz_convert("America/New_York").strftime("%H:%M:%S"), "buy events/s before": round(nb / 60, 2), "after": round(na / 60, 2), "after/before": round(na / max(nb, 1), 2)})
cx = pd.DataFrame(cross); c400 = cx[cx.level == 400]
res["A6 TSLA Oct 27 round-dollar crosses"] = {"400 cross": c400.to_dict(orient="records"), "other crosses: median after/before": round(float(cx[cx.level != 400]["after/before"].median()), 2),
                                             "400 pctile among the day's crosses": pctl(float(c400["after/before"].iloc[0]), cx["after/before"]) if len(c400) else None, "n crosses": int(len(cx)),
                                             "all crosses": cx.to_dict(orient="records")}
json.dump(res, open(HERE / "out" / "d4.json", "w"), indent=1, default=str)
print(json.dumps({k: v for k, v in res.items() if k not in ("A6 TSLA Oct 27 round-dollar crosses",)}, indent=1, default=str)[:6000])
print(json.dumps({k: v for k, v in res["A6 TSLA Oct 27 round-dollar crosses"].items() if k != "all crosses"}, indent=1))
