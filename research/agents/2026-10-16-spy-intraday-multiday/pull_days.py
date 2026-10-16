"""Resumable pull of SPY 0DTE 1-minute option bars and quotes (ThetaData Value tier), one file per day.
Needs THETADATA_API_KEY in the environment. Usage: python pull_days.py 2023-01-03 2026-10-15 [--newest-first]"""
import datetime as dt
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
from thetadata import ThetaClient

HERE = Path(__file__).resolve().parent
OUT = HERE / "data" / "min"
sys.path.insert(0, str(HERE.parents[1] / "microstructure"))
from common import load_bars                       # noqa: E402

R = 15
c = ThetaClient(api_key=os.environ["THETADATA_API_KEY"], dataframe_type="pandas")


def one(day):
    path = OUT / f"{day:%Y%m%d}.csv.gz"
    if path.exists():
        return day, "cached"
    for attempt in range(4):
        try:
            o = c.option_history_ohlc(symbol="SPY", expiration=day, date=day, strike="*", right="both", interval="1m", strike_range=R)
            q = c.option_history_quote(symbol="SPY", expiration=day, date=day, strike="*", right="both", interval="1m", strike_range=R)
            break
        except Exception as e:
            if "PERMISSION" in str(e) or attempt == 3:
                return day, f"error {type(e).__name__}: {str(e)[:120]}"
            time.sleep(2 ** (attempt + 1))
    if o is None or q is None or not len(o):
        return day, "empty"
    key = ["strike", "right", "timestamp"]
    m = o[key + ["volume", "vwap"]].merge(q[key + ["bid", "ask"]], on=key, how="outer")
    m["right"] = m.right.str.upper().str[0]
    m["ts"] = pd.to_datetime(m.timestamp, utc=True).dt.tz_convert("America/New_York").dt.strftime("%H:%M")
    m = m.drop(columns="timestamp")
    m.to_csv(path, index=False, float_format="%.4f")
    return day, f"ok {len(m)}"


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    a, b = pd.Timestamp(sys.argv[1]), pd.Timestamp(sys.argv[2])
    days = [d.date() for d in load_bars("SPY").index if a <= d <= b]
    if "--newest-first" in sys.argv:
        days = days[::-1]
    t0 = time.time()
    with ThreadPoolExecutor(2) as ex:
        for k, (d, status) in enumerate(ex.map(one, days), 1):
            if k % 10 == 0 or not status.startswith(("ok", "cached")):
                print(f"{k}/{len(days)} {d} {status} {time.time() - t0:.0f}s", flush=True)
    print("done", len(days), f"{time.time() - t0:.0f}s", flush=True)
