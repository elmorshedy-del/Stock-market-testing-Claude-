"""A4: footprint of the run into each session's high (ES): exhaustion vs absorption; flip-wick days vs other days.
MBO Oct 20: do offers refill at the high? Pre-registered @ bdc698c.  -> out/a4.json"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from flowlib import load_trades

HERE = Path(__file__).resolve().parent; DATA = HERE / "data"
FLIP_DAYS = {"20261014", "20261015", "20261016", "20261019", "20261020"}      # SPY high within +-0.15% of the pre-open flip


def segment(x, a, b):
    s = x[(x.ts_event >= a) & (x.ts_event <= b)]
    mins = max((b - a).total_seconds() / 60, 0.5)
    bv = s["size"][s.sign > 0].sum(); sv = s["size"][s.sign < 0].sum()
    prog = (s.price.iloc[-1] - s.price.iloc[0]) if len(s) else np.nan
    return {"minutes": mins, "buy/min": bv / mins, "sell/min": sv / mins, "delta/min": (bv - sv) / mins, "progress pts": prog,
            "pts per 1k bought": 1000 * prog / bv if bv else np.nan}


rows = []
for f in sorted(DATA.glob("ES_trades_*.parquet")):
    tag = f.stem.split("_")[-1]
    x = load_trades(f)
    H = x.price.max(); th = x.loc[x.price.idxmax(), "ts_event"]; t0 = x.ts_event.iloc[0]
    if (th - t0).total_seconds() < 20 * 60:
        rows.append({"day": tag, "flip day": tag in FLIP_DAYS, "note": "high within 20 min of the open: no run-up", "high time ET": th.tz_convert("America/New_York").strftime("%H:%M")})
        continue
    pre = x[x.ts_event <= th]
    below = pre[pre.price < H * (1 - 0.001)]
    if not len(below):
        rows.append({"day": tag, "flip day": tag in FLIP_DAYS, "note": "never 0.1% below the high before it", "high time ET": th.tz_convert("America/New_York").strftime("%H:%M")})
        continue
    tb = below.ts_event.iloc[-1]                                    # start of the final continuous stay within 0.1% of the high
    a = max(t0, tb - pd.Timedelta("30min"))
    if (tb - a).total_seconds() < 10 * 60:
        rows.append({"day": tag, "flip day": tag in FLIP_DAYS, "note": "less than 10 min of run-up before the final 0.1%", "high time ET": th.tz_convert("America/New_York").strftime("%H:%M")})
        continue
    e, fz = segment(x, a, tb), segment(x, tb, th)
    after = segment(x, th, th + pd.Timedelta("10min"))
    rows.append({"day": tag, "flip day": tag in FLIP_DAYS, "high": H, "high time ET": th.tz_convert("America/New_York").strftime("%H:%M"),
                 "buy/min ratio (final 0.1% vs earlier run)": fz["buy/min"] / e["buy/min"],
                 "delta/min earlier, final": [round(e["delta/min"], 1), round(fz["delta/min"], 1)],
                 "progress per 1k bought: earlier, final": [round(e["pts per 1k bought"], 3), round(fz["pts per 1k bought"], 3)],
                 "absorption ratio (final/earlier progress per buy)": fz["pts per 1k bought"] / e["pts per 1k bought"] if e["pts per 1k bought"] else np.nan,
                 "sell/min next 10 min vs earlier run": after["sell/min"] / e["sell/min"], "final segment minutes": round(fz["minutes"], 1)})
df = pd.DataFrame(rows)
ok = df[df.get("note").isna()] if "note" in df else df
summ = {}
for lab, m in (("flip-wick days", ok["flip day"]), ("other days", ~ok["flip day"])):
    z = ok[m]
    summ[lab] = {"n": int(len(z)), "median buy/min ratio": round(float(z["buy/min ratio (final 0.1% vs earlier run)"].median()), 3),
                 "median absorption ratio": round(float(z["absorption ratio (final/earlier progress per buy)"].median()), 3),
                 "share exhaustion (buy/min ratio < 1)": round(float((z["buy/min ratio (final 0.1% vs earlier run)"] < 1).mean()), 3),
                 "median sell/min after high vs run": round(float(z["sell/min next 10 min vs earlier run"].median()), 3)}
# MBO Oct 20: refills at the high
mbo = pd.read_parquet(DATA / "ES_mbo_20261020.parquet", columns=["ts_event", "action", "side", "price", "size", "order_id"])
mbo = mbo[mbo.ts_event >= pd.Timestamp("2026-10-20 13:30", tz="UTC")]
tr = mbo[mbo.action == "T"]
Hm = tr.price.max(); thm = tr.loc[tr.price.idxmax(), "ts_event"]


def refill(t_c, P, win="5min"):
    """Offer supply at the high and 1 tick above, +-win: contracts added minus cancelled per minute (net new resting supply)."""
    w = mbo[(mbo.ts_event >= t_c - pd.Timedelta(win)) & (mbo.ts_event <= t_c + pd.Timedelta(win)) & (mbo.side == "A") & (mbo.price.between(P - 0.001, P + 0.251))]
    mins = 2 * pd.Timedelta(win).total_seconds() / 60
    added = int(w.loc[w.action == "A", "size"].sum()); canc = int(w.loc[w.action == "C", "size"].sum()); filled = int(w.loc[w.action == "F", "size"].sum())
    return {"added/min": round(added / mins, 1), "cancelled/min": round(canc / mins, 1), "filled/min": round(filled / mins, 1),
            "refill ratio (added/filled contracts)": round(added / max(filled, 1), 2), "net new offers/min": round((added - canc) / mins, 1)}


mb = {"Oct 20 day high": float(Hm), "time ET": thm.tz_convert("America/New_York").strftime("%H:%M:%S"), "at the high (price and 1 tick above)": refill(thm, Hm)}
px = tr.set_index("ts_event").price.resample("5min").max().dropna()
sw = px[(px.shift(1) < px) & (px.shift(-1) < px)].sort_values(ascending=False)
sw = sw[(abs(sw.index - thm) > pd.Timedelta("20min"))].head(10)
pl = [refill(t + pd.Timedelta("2min30s"), P) for t, P in sw.items()]
rr = [p["net new offers/min"] for p in pl]
mb["placebo: 10 other 5-min swing highs that day, median net new offers/min"] = round(float(np.median(rr)), 2) if rr else None
mb["placebo net new offers/min"] = rr; mb["placebo filled/min"] = [p["filled/min"] for p in pl]
res = {"per day": df.round(4).to_dict(orient="records"), "summary": summ, "MBO Oct 20": mb}
(HERE / "out" / "a4.json").write_text(json.dumps(res, indent=1, default=str))
print(df.drop(columns=[c for c in df.columns if "delta/min" in c or "progress per" in c]).round(3).to_string()); print(json.dumps(summ, indent=1)); print(json.dumps(mb, indent=1))
