"""The owner's named TSLA bursts (research/microstructure/burst_compare.NAMED, burst day = day 0) vs the Oct 26-27 burst:
buying aggression (bulk volume classification on 1-minute bars), relative volume, gap share, and how FAST the price went
up afterwards (gain at +3/+5/+10/+20 sessions after the burst's second day; sessions to +10%). Descriptive, n = 11.
Usage: python named.py <TSLA 1m parquet> -> out/named.json, out/named_paths.csv"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
NAMED = {"2024-06-17": "Jun '24", "2024-07-01": "Jul '24 (call-wall break)", "2024-10-24": "Oct '24 report", "2024-11-06": "Nov '24 election",
         "2025-04-23": "Apr '25 report", "2025-05-12": "May '25", "2025-05-27": "late May '25", "2025-09-11": "Sep '25", "2025-10-06": "Oct '25 a",
         "2025-10-13": "Oct '25 b", "2025-11-24": "Nov '25", "2026-10-26": "NOW: Oct 26-27 '26"}
m = pd.read_parquet(sys.argv[1], columns=["open", "close", "volume"]); m.index = m.index.tz_convert("America/New_York")
m = m[(m.index.time >= pd.Timestamp("09:30").time()) & (m.index.time < pd.Timestamp("16:00").time())]
m["day"] = m.index.normalize().tz_localize(None); m["dp"] = m.groupby("day").close.diff()
sd = m.groupby("day").dp.std().shift(1).rolling(5, min_periods=3).mean(); m["sig"] = m.day.map(sd)
m["net"] = m.volume * (2 * norm.cdf(m.dp / m.sig) - 1)
D = m.groupby("day").agg(o=("open", "first"), c=("close", "last"), v=("volume", "sum"), net=("net", "sum")).dropna()
D["rvol"] = D.v / D.v.rolling(20).mean().shift(1)
rows, paths = [], {}
for d, lab in NAMED.items():
    i = D.index.searchsorted(pd.Timestamp(d)); b = D.iloc[i:i + 2]; p0 = D.c.iloc[i - 1]; base = b.c.iloc[-1]
    after = D.c.iloc[i + 1:i + 22] / base - 1                     # sessions 0..20 after the burst's 2nd day
    paths[lab] = (100 * after.to_numpy()).round(2).tolist()
    r = {"burst": lab, "day 0": str(D.index[i].date()), "2-day move %": 100 * (base / p0 - 1), "gap share %": 100 * (np.log(b.o.iloc[0] / p0) + np.log(b.o.iloc[1] / b.c.iloc[0])) / np.log(base / p0),
         "buying aggression % (net buy share)": 100 * b.net.sum() / b.v.sum(), "rel. volume": b.rvol.mean()}
    for h in (3, 5, 10, 20):
        r[f"+{h} sessions %"] = 100 * after.iloc[h] if len(after) > h else np.nan
    hit = np.nonzero((after.to_numpy() >= 0.10))[0]; r["sessions to +10%"] = int(hit[0]) if len(hit) else np.nan
    r["best within 10 %"] = 100 * after.iloc[:11].max() if len(after) > 1 else np.nan
    r["worst dip within 5 %"] = 100 * after.iloc[:6].min() if len(after) > 1 else np.nan
    rows.append(r)
T = pd.DataFrame(rows); T.to_csv(HERE / "out" / "named.csv", index=False)
pd.DataFrame({k: pd.Series(v) for k, v in paths.items()}).to_csv(HERE / "out" / "named_paths.csv", index_label="session")
past = T[~T.burst.str.startswith("NOW")]
fast = past["+5 sessions %"] >= 5
res = {"table": T.round(2).to_dict("records"),
       "named bursts that kept going up fast (>= +5% within 5 sessions after the burst)": f"{int(fast.sum())} of {len(past)}",
       "aggression: fast vs not (median %)": [round(float(past[fast]["buying aggression % (net buy share)"].median()), 1), round(float(past[~fast]["buying aggression % (net buy share)"].median()), 1)],
       "rel. volume: fast vs not (median)": [round(float(past[fast]["rel. volume"].median()), 2), round(float(past[~fast]["rel. volume"].median()), 2)],
       "+3 sessions: fast group vs not (median %)": [round(float(past[fast]["+3 sessions %"].median()), 1), round(float(past[~fast]["+3 sessions %"].median()), 1)],
       "spearman aggression vs +10 sessions": round(float(past[["buying aggression % (net buy share)", "+10 sessions %"]].corr(method="spearman").iloc[0, 1]), 2)}
json.dump(res, open(HERE / "out" / "named.json", "w"), indent=1, default=str)
pd.set_option("display.width", 250); print(T.round(1).to_string(index=False)); print({k: v for k, v in res.items() if k != "table"})
