import json
from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).parent / "data"
OUT = Path(__file__).parent / "out"


def load_bars(sym, interval="1d"):
    d = json.loads((DATA / f"{sym}_{interval}.json").read_text())["chart"]["result"][0]
    q = d["indicators"]["quote"][0]
    idx = pd.to_datetime(d["timestamp"], unit="s", utc=True).tz_convert("America/New_York")
    df = pd.DataFrame({k: q[k] for k in ("open", "high", "low", "close", "volume")}, index=idx)
    df = df.dropna()
    df = df[(df["high"] > 0) & (df["low"] > 0)]
    if interval == "1d":
        df.index = df.index.normalize().tz_localize(None)
        df = df[~df.index.duplicated(keep="last")]
    return df


def clv_delta(df):
    """Close-location-value volume split: crude daily buy-minus-sell proxy."""
    rng = (df["high"] - df["low"]).replace(0, np.nan)
    return (((df["close"] - df["low"]) - (df["high"] - df["close"])) / rng).fillna(0) * df["volume"]
