"""Pull SPY 1-minute bars (Databento EQUS.MINI ohlcv-1m) 2024-01-01 -> 2026-10-31 into data/, one request (quoted $0.227).
Usage: DATABENTO_API_KEY=... python fetch.py [SYMBOL] [DATASET] [START]"""
import os
import sys
from pathlib import Path

import databento as db

HERE = Path(__file__).resolve().parent; D = HERE / "data"; D.mkdir(exist_ok=True)
sym = sys.argv[1] if len(sys.argv) > 1 else "SPY"
ds = sys.argv[2] if len(sys.argv) > 2 else "EQUS.MINI"
start = sys.argv[3] if len(sys.argv) > 3 else "2024-01-01"; end = sys.argv[4] if len(sys.argv) > 4 else "2026-10-31"
c = db.Historical(os.environ["DATABENTO_API_KEY"])
kw = dict(dataset=ds, symbols=[sym], schema="ohlcv-1m", start=start, end=end)
print("cost $%.3f" % c.metadata.get_cost(**kw))
df = c.timeseries.get_range(**kw).to_df().reset_index()
out = D / f"{sym}_{ds.replace('.', '_')}_1m.parquet"
df[["ts_event", "open", "high", "low", "close", "volume"]].to_parquet(out)
print(out, len(df), df.ts_event.min(), df.ts_event.max())
