"""Download daily option chains (end-of-day quotes + open interest) from ThetaData,
one request per symbol per month with an expiration wildcard, resumable.

Free tier: EOD quotes for ~the last year only, no open interest.
Value tier ($40/mo): open interest and EOD quotes from Jan 2020.
Files: data/thetadata/{SYM}_{YYYY-MM}_{eod|oi}.csv.gz (gitignored).

Needs the `thetadata` package (Python >= 3.12) and THETADATA_API_KEY in the environment.
Usage: python td_pull.py 2020-01 2026-10 TSLA MSFT MU NVDA SPY QQQ   (TD_MAX_DTE overrides the 120-day cap)
"""
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
from thetadata import ThetaClient

DIR = Path(__file__).resolve().parent / "data" / "thetadata"
MAX_DTE = int(os.environ.get("TD_MAX_DTE", 120))   # >120 DTE adds <1% to the gamma signal (checked on the 2022 sample)


def month_ranges(a, b):
    last = (pd.Timestamp.today().normalize() - pd.offsets.BDay(1)).date()   # today's EOD isn't final yet
    for m in pd.period_range(a, b, freq="M"):
        if m.start_time.date() <= last:
            yield m, m.start_time.date(), min(m.end_time.date(), last)


def pull(c, sym, m, start, end, kind):
    path = DIR / f"{sym}_{m}_{kind}.csv.gz"
    current = m == pd.Timestamp.today().to_period("M")             # the running month is always refreshed
    if path.exists() and not current:
        return "cached"
    for attempt in range(4):
        try:
            if kind == "eod":
                df = c.option_history_eod(start_date=start, end_date=end, symbol=sym, expiration="*", max_dte=MAX_DTE)
            else:
                df = c.option_history_open_interest(symbol=sym, expiration="*", start_date=start, end_date=end, max_dte=MAX_DTE)
            df.to_csv(path, index=False)
            return f"ok {len(df)}"
        except Exception as e:
            msg = str(e)
            if "PERMISSION_DENIED" in msg or "subscription" in msg:
                return "needs a higher ThetaData tier"
            if "NO_DATA" in msg or "No data" in msg:
                return "no data"
            time.sleep(2 ** attempt)
    return f"failed: {msg[:120]}"


if __name__ == "__main__":
    a, b, *syms = sys.argv[1:]
    DIR.mkdir(parents=True, exist_ok=True)
    c = ThetaClient(api_key=os.environ["THETADATA_API_KEY"], dataframe_type="pandas")
    with ThreadPoolExecutor(2) as ex:                      # Value tier allows 2 concurrent requests per session
        for sym in syms:
            for m, start, end in month_ranges(a, b):
                fut = {k: ex.submit(pull, c, sym, m, start, end, k) for k in ("eod", "oi")}
                print(sym, m, {k: f.result() for k, f in fut.items()}, flush=True)
