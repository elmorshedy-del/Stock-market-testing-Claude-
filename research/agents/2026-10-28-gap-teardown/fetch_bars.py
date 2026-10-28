"""Amendment 3: TSLA, AAPL, NVDA + QQQ only. Faster labeling fetch (replaces classify.py's per-row loop, same bars): one XNAS ohlcv-1m request per date for all gapped symbols,
09:30-10:35 ET, 16 threads, cached per date. META is requested as FB before 2022-06-09. Usage: python fetch_bars.py <key> -> data/first_hour.parquet"""
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import databento as db
import pandas as pd

HERE = Path(__file__).resolve().parent; P = HERE / "data" / "bars"; P.mkdir(parents=True, exist_ok=True)
c = db.Historical(sys.argv[1])
cand = pd.read_csv(HERE / "out" / "candidates.csv", parse_dates=["date"])
extra = pd.DataFrame([{"date": pd.Timestamp(d), "sym": "TSLA"} for d in ("2026-10-26", "2026-10-27")])
SYMS = ["TSLA", "AAPL", "NVDA", "QQQ"]   # Amendment 3 (owner: "narrow the fetch for big names for now")
todo = pd.concat([cand[["date", "sym"]], extra], ignore_index=True).drop_duplicates()
todo = todo[todo.sym.isin(SYMS)]
api = lambda s, d: "FB" if (s == "META" and d < pd.Timestamp("2022-06-09")) else s


def fetch(item):
    d, syms = item
    f = P / f"{d:%Y%m%d}.parquet"
    if f.exists(): return 0
    et = lambda hm: pd.Timestamp(f"{d.date()} {hm}", tz="America/New_York").tz_convert("UTC")
    amap = {api(s, d): s for s in syms}
    for attempt in range(4):
        if attempt: time.sleep(5 * attempt)
        try:
            df = c.timeseries.get_range(dataset="XNAS.ITCH", symbols=list(amap), schema="ohlcv-1m", start=et("09:30"), end=et("10:35")).to_df()
            if df.empty: return 0
            df = df.reset_index()[["ts_event", "symbol", "open", "high", "low", "close", "volume"]]
            df["sym"] = df.symbol.map(amap); df["date"] = d
            df.drop(columns="symbol").to_parquet(f); return 1
        except Exception as e:
            err = str(e)[:80]
    print("err", d.date(), err, flush=True); return 0


items = [(d, sorted(g.sym)) for d, g in todo.groupby("date")]
with ThreadPoolExecutor(6) as ex:
    n = sum(ex.map(fetch, items))
fh = pd.concat([pd.read_parquet(f) for f in sorted(P.glob("*.parquet"))], ignore_index=True)
fh = fh[fh.sym.isin(SYMS)]
fh.to_parquet(HERE / "data" / "first_hour.parquet")
print("dates", len(items), "fetched now", n, "rows", len(fh), "sym-days", fh.groupby(["sym", "date"]).ngroups, flush=True)
