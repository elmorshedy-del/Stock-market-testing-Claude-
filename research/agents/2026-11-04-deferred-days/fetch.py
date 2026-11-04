"""Quote, then pull, the deferred days. Key from env DATABENTO_API_KEY only. Usage: python fetch.py quote|pull <cap $>"""
import os
import sys
from pathlib import Path

import databento as db
import pandas as pd

HERE = Path(__file__).resolve().parent; D = HERE / "data"; D.mkdir(exist_ok=True)
c = db.Historical(os.environ["DATABENTO_API_KEY"]); mode, CAP = sys.argv[1], float(sys.argv[2])
et = lambda day, hm: pd.Timestamp(f"{day} {hm}", tz="America/New_York").tz_convert("UTC")
NAS = ["TSLA", "GOOGL", "AMZN", "NVDA", "AVGO", "MSFT", "AAPL", "META", "QQQ"]
REQ = [  # (file, dataset, symbols, schema, start, end, stype)
    ("ES_trades_20261027", "GLBX.MDP3", ["ESZ6"], "trades", et("2026-10-27", "09:30"), et("2026-10-27", "16:00"), "raw_symbol"),
    ("TSLA_trades_20261027", "XNAS.ITCH", ["TSLA"], "trades", et("2026-10-27", "09:30"), et("2026-10-27", "16:00"), "raw_symbol"),
    ("SPY_imbalance_20261027", "ARCX.PILLAR", ["SPY"], "imbalance", et("2026-10-27", "15:45"), et("2026-10-27", "16:00"), "raw_symbol"),
    ("NAS_imbalance_20261027", "XNAS.ITCH", NAS, "imbalance", et("2026-10-27", "15:45"), et("2026-10-27", "16:00"), "raw_symbol"),
    ("TSLA_20261028_trades", "XNAS.ITCH", ["TSLA"], "trades", et("2026-10-28", "04:00"), et("2026-10-28", "10:35"), "raw_symbol"),
    ("TSLA_20261028_mbp10", "XNAS.ITCH", ["TSLA"], "mbp-10", et("2026-10-28", "09:25"), et("2026-10-28", "10:35"), "raw_symbol"),
    ("TSLA_20261028_imb", "XNAS.ITCH", ["TSLA"], "imbalance", et("2026-10-28", "09:20"), et("2026-10-28", "09:31"), "raw_symbol"),
]
if len(sys.argv) > 3:   # MBO window around the ES high, passed as "HH:MM:SS" ET (after the trades are in)
    t = pd.Timestamp(f"2026-10-27 {sys.argv[3]}", tz="America/New_York").tz_convert("UTC")
    REQ = [("ES_mbo_20261027", "GLBX.MDP3", ["ESZ6"], "mbo", et("2026-10-27", "09:30"), et("2026-10-27", "16:00"), "raw_symbol")]
tot = 0.0
for f, ds, sy, sc, a, b, st in REQ:
    cost = c.metadata.get_cost(dataset=ds, symbols=sy, schema=sc, start=a, end=b, stype_in=st); tot += cost
    print(f"{f:26s} {ds:12s} {sc:9s} ${cost:.3f}", flush=True)
print("TOTAL quote $", round(tot, 3))
if mode == "pull":
    assert tot <= CAP, f"quote {tot} above cap {CAP}"
    for f, ds, sy, sc, a, b, st in REQ:
        p = D / f"{f}.parquet"
        if p.exists(): continue
        df = c.timeseries.get_range(dataset=ds, symbols=sy, schema=sc, start=a, end=b, stype_in=st).to_df().reset_index()
        df.to_parquet(p); print("pulled", f, len(df), flush=True)
