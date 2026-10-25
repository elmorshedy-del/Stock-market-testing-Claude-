"""Daily intraday segments from Yahoo 60-minute bars (README.md). overnight, first hour, midday (10:30-15:30), last half hour (15:30-close)."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
LABELS = ["09:30", "10:30", "11:30", "12:30", "13:30", "14:30", "15:30"]
PEERS = ["MSFT", "AMZN", "GOOGL", "META", "NVDA"]


def bars(folder, sym):
    d = json.loads((Path(folder) / f"{sym}_60m.json").read_text())["chart"]["result"][0]
    idx = pd.to_datetime(d["timestamp"], unit="s", utc=True).tz_convert("America/New_York")
    q = d["indicators"]["quote"][0]
    f = pd.DataFrame({k: q[k] for k in ("open", "high", "low", "close", "volume")}, index=idx).dropna(subset=["open", "close"])
    f = f[f.index.strftime("%H:%M") != "16:00"]
    return f


def segments(folder, sym):
    f = bars(folder, sym)
    f["day"] = f.index.tz_localize(None).normalize()
    f["lab"] = f.index.strftime("%H:%M")
    rows = []
    for day, g in f.groupby("day"):
        full = list(g.lab) == LABELS
        rows.append({"date": day, "full": full, "close": g.close.iloc[-1],
                     "open": g.open.iloc[0] if full else np.nan, "h1": g.close.iloc[0] if full else np.nan,
                     "c1530": g.close.iloc[5] if full else np.nan, "vol_last": g.volume.iloc[-1] if full else np.nan,
                     "vol_day": g.volume.sum() if full else np.nan})
    D = pd.DataFrame(rows).set_index("date")
    pc = D.close.shift(1)
    D["on"] = np.log(D.open / pc)
    D["first"] = np.log(D.h1 / D.open)
    D["mid"] = np.log(D.c1530 / D.h1)
    D["last"] = np.log(D.close / D.c1530)
    D["rest"] = D["first"] + D["mid"]                                      # open to 15:30
    D["on_next"] = D["on"].shift(-1)
    share = D.vol_last / D.vol_day
    D["abn_share"] = share / share.rolling(20, min_periods=10).mean().shift(1)
    return D[D.full]


def panel(folder, syms):
    return {s: segments(folder, s) for s in syms}


def blocks(rng, n, L=20):
    st = rng.integers(0, n - L, int(np.ceil(n / L)))
    return np.concatenate([np.arange(s, s + L) for s in st])[:n]


def slope(x, y):
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    x = x - x.mean()
    return float((x * (y - y.mean())).sum() / (x ** 2).sum())
