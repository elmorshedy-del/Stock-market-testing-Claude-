"""Pull 1-minute option OHLC (volume, VWAP) and 1-minute NBBO quotes from ThetaData (Value tier) for SPY options
near the money. Needs THETADATA_API_KEY in the environment. Writes data/flow_{DAY}_{kind}.csv.gz (gitignored).
Usage: python pull_flow.py 2026-10-16 2026-10-16 2026-10-19"""
import datetime as dt
import os
import sys
from pathlib import Path

import pandas as pd
from thetadata import ThetaClient

DATA = Path(__file__).resolve().parent / "data"
day = dt.date.fromisoformat(sys.argv[1])
exps = [dt.date.fromisoformat(e) for e in sys.argv[2:]]
c = ThetaClient(api_key=os.environ["THETADATA_API_KEY"], dataframe_type="pandas")
for kind, fn in (("ohlc", c.option_history_ohlc), ("quote", c.option_history_quote)):
    parts = []
    for e in exps:
        df = fn(symbol="SPY", expiration=e, date=day, strike="*", right="both", interval="1m", strike_range=25)
        print(kind, e, 0 if df is None else len(df))
        if df is not None and len(df):
            parts.append(df)
    pd.concat(parts, ignore_index=True).to_csv(DATA / f"flow_{day:%Y%m%d}_{kind}.csv.gz", index=False)
