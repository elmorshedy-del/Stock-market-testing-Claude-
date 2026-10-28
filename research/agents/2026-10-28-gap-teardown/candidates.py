"""Candidates (Amendment 2): gap >= 0.5 sigma, May 2018 - Oct 27 2026, 13 symbols, from Yahoo daily. -> out/candidates.csv"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

S = Path(sys.argv[1]); HERE = Path(__file__).resolve().parent
SYMS = ["QQQ", "TSLA", "AAPL", "NVDA", "AMD", "META", "MSFT", "AMZN", "GOOGL", "AVGO", "NFLX", "MU", "ORCL"]


def ohlc(p):
    r = json.loads(Path(p).read_text())["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    d = pd.DataFrame({k: q[k] for k in ("open", "high", "low", "close")}, index=pd.to_datetime(r["timestamp"], unit="s").normalize())
    return d[~d.index.duplicated(keep="last")].dropna()


rows = []
for s in SYMS:
    for p in (S / "ladder28" / "data" / f"{s}_1d.json", S / "long" / f"{s}.json", S / "breadth" / f"{s}.json", S / "etfs" / f"{s}.json"):
        if p.exists(): break
    d = ohlc(p)
    d["prev"] = d.close.shift(1); d["gap"] = d.open / d.prev - 1; d["r2"] = d.prev / d.close.shift(3) - 1
    d["sig"] = np.log(d.close).diff().rolling(20).std().shift(1)
    x = d[(d.index >= "2018-05-01") & (d.index <= "2026-10-27") & (d.gap / d.sig >= 0.5)].copy()
    x["sym"] = s; x["src"] = p.name
    rows.append(x.reset_index().rename(columns={"index": "date"})[["date", "sym", "prev", "open", "gap", "r2", "sig", "src"]])
c = pd.concat(rows).sort_values(["date", "sym"]).reset_index(drop=True)
c.to_csv(HERE / "out" / "candidates.csv", index=False)
print(len(c), "candidates;", c.groupby("sym").size().to_dict(), "| 2020-09-02 rows:", c[c.date == "2020-09-02"].sym.tolist())
