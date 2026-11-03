"""A5 data: TSLA option 1-min OHLC + quotes (ThetaData Value) for the nearest expiry >= 1 day out and for 0DTE when listed,
strikes around the money, every tradable day in the given window. Sequential (ThetaData dislikes parallel calls), resumable.
Usage: THETADATA_API_KEY=... python pull_opts.py 2024-01-02 2026-10-30"""
import datetime as dt
import os
import sys
import time
from pathlib import Path

import pandas as pd
from thetadata import ThetaClient

HERE = Path(__file__).resolve().parent; P = HERE / "data" / "opt"; P.mkdir(parents=True, exist_ok=True)
a, b = sys.argv[1], sys.argv[2]
c = ThetaClient(api_key=os.environ["THETADATA_API_KEY"], dataframe_type="pandas")
exps = sorted(pd.to_datetime(c.option_list_expirations(symbol="TSLA").expiration).dt.date.unique())
days = sorted(set(pd.read_parquet(HERE / "data" / ("TSLA_rth_d2.parquet" if a >= "2024" else "TSLA2020_rth_d2.parquet")).date.dt.date))
days = [d for d in days if pd.Timestamp(a).date() <= d <= pd.Timestamp(b).date()]
n = 0
for d in days:
    nxt = [e for e in exps if e > d][0]; zero = d if d in exps else None
    for tag, e in (("next", nxt), ("0dte", zero)):
        if e is None: continue
        f = P / f"{d:%Y%m%d}_{tag}.parquet"
        if f.exists(): continue
        for attempt in range(3):
            try:
                o = c.option_history_ohlc(symbol="TSLA", expiration=e, date=d, strike="*", right="both", interval="1m", strike_range=8)
                q = c.option_history_quote(symbol="TSLA", expiration=e, date=d, strike="*", right="both", interval="1m", strike_range=8)
                m = o.merge(q[["strike", "right", "timestamp", "bid", "ask"]], on=["strike", "right", "timestamp"], how="left")
                m.to_parquet(f); n += 1; break
            except Exception as ex:
                err = str(ex)[:120]; time.sleep(3 * (attempt + 1))
        else:
            print("fail", d, tag, err, flush=True)
    if n and n % 50 == 0: print("done", n, d, flush=True)
print("finished", n, flush=True)
