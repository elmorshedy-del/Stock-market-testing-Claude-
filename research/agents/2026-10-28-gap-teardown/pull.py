"""Microstructure pulls for sampled events (Amendment 2). Usage: python pull.py <key> <cap $> <mbp10 minutes after 09:25>
Per symbol-day: trades 04:00-10:35 ET, mbp-10 09:25-(09:25+m), opening imbalance 09:20-09:31. Writes data/<sym>_<date>_{trades,mbp10,imb}.parquet"""
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import threading
import time

import databento as db
import pandas as pd

HERE = Path(__file__).resolve().parent; D = HERE / "data"
c = db.Historical(sys.argv[1]); CAP = float(sys.argv[2]); MB = int(sys.argv[3])
smp = pd.read_csv(HERE / "out" / "sample.csv", parse_dates=["date"])
smp = pd.concat([smp[smp.focal == 1], smp[smp.focal == 0].sample(frac=1, random_state=0)])   # random order, so a cap stop drops events at random
lock = threading.Lock(); spent = [0.0]
et = lambda day, hm: pd.Timestamp(f"{day.date()} {hm}", tz="America/New_York").tz_convert("UTC")


def job(r):
    tag = f"{r.sym}_{r.date:%Y%m%d}"
    api = "FB" if (r.sym == "META" and r.date < pd.Timestamp("2022-06-09")) else r.sym   # META's Nasdaq ticker before 2022-06-09
    reqs = [("trades", "trades", et(r.date, "04:00"), et(r.date, "10:35")),
            ("mbp10", "mbp-10", et(r.date, "09:25"), et(r.date, "09:25") + pd.Timedelta(minutes=MB)),
            ("imb", "imbalance", et(r.date, "09:20"), et(r.date, "09:31"))]
    for name, schema, a, b in reqs:
        f = D / f"{tag}_{name}.parquet"
        if f.exists(): continue
        for k in range(5):
          try:
            cost = c.metadata.get_cost(dataset="XNAS.ITCH", symbols=[api], schema=schema, start=a, end=b)
            with lock:
                if spent[0] + cost > CAP: return f"cap reached at {tag}"
                spent[0] += cost
            df = c.timeseries.get_range(dataset="XNAS.ITCH", symbols=[api], schema=schema, start=a, end=b).to_df().reset_index()
            keep = [k for k in df.columns if k in ("ts_event", "price", "size", "side", "action", "flags") or k.startswith(("bid_px_", "ask_px_", "bid_sz_", "ask_sz_"))
                    or k in ("ref_price", "paired_qty", "total_imbalance_qty", "auction_type", "cont_book_clr_price", "auct_interest_clr_price")]
            df[keep].to_parquet(f); break
          except Exception as e:
            if k == 4: return f"err {tag} {name} {str(e)[:80]}"
            time.sleep(4 * (k + 1))
    return None


with ThreadPoolExecutor(6) as ex:
    for msg in ex.map(job, list(smp.itertuples())):
        if msg: print(msg, flush=True)
print("SPENT $", round(spent[0], 3), flush=True)
