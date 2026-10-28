"""META traded as FB on Nasdaq until 2022-06-08: refetch those candidate days under FB, stored as META. Usage: python fb.py <key> -> data/first_hour_fb.parquet"""
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import databento as db
import pandas as pd

HERE = Path(__file__).resolve().parent
c = db.Historical(sys.argv[1])
cand = pd.read_csv(HERE / "out" / "candidates.csv", parse_dates=["date"])
todo = cand[(cand.sym == "META") & (cand.date < "2022-06-09")]


def fetch(row):
    f = lambda hm: pd.Timestamp(f"{row.date.date()} {hm}", tz="America/New_York").tz_convert("UTC")
    try:
        df = c.timeseries.get_range(dataset="XNAS.ITCH", symbols=["FB"], schema="ohlcv-1m", start=f("09:30"), end=f("10:35")).to_df()
        if df.empty: return None
        df = df.reset_index()[["ts_event", "open", "high", "low", "close", "volume"]]
        df["sym"] = "META"; df["date"] = row.date
        return df
    except Exception as e:
        print("err", row.date.date(), str(e)[:80], flush=True); return None


with ThreadPoolExecutor(8) as ex:
    parts = [p for p in ex.map(fetch, list(todo.itertuples())) if p is not None]
pd.concat(parts, ignore_index=True).to_parquet(HERE / "data" / "first_hour_fb.parquet")
print("FB days", len(parts), "of", len(todo))
