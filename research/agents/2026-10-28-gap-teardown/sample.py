"""Stratified sample for the microstructure pulls (Amendments 2-3): within each class, years in proportion to their counts, seed 0.
Focal days always in: 2020-09-02 (every symbol that gapped), TSLA 2026-10-26/27. Usage: python sample.py <n VF> <n SC> <n mid> -> out/sample.csv"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ev = pd.read_csv(HERE / "out" / "events.csv", parse_dates=["date"])
want = dict(zip(["VF", "SC", "mid"], map(int, sys.argv[1:4])))
rng = np.random.default_rng(0)
focal = ev[(ev.date == "2020-09-02") | ((ev.sym == "TSLA") & ev.date.isin(pd.to_datetime(["2026-10-26", "2026-10-27"])))]
rest = ev.drop(focal.index)
picks = [focal.assign(focal=1)]
for cls, n in want.items():
    pool = rest[rest.cls == cls]
    if n >= len(pool): picks.append(pool.assign(focal=0)); continue
    yr = pool.date.dt.year
    quota = (yr.value_counts() / len(pool) * n).round().astype(int)
    for y, k in quota.items():
        g = pool[yr == y]
        picks.append(g.iloc[rng.choice(len(g), min(k, len(g)), replace=False)].assign(focal=0))
s = pd.concat(picks).drop_duplicates(["sym", "date"]).sort_values(["date", "sym"])
s.to_csv(HERE / "out" / "sample.csv", index=False)
print(s.groupby(["cls", "scope"], dropna=False).size().to_dict(), "total", len(s))
print(s.groupby([s.date.dt.year, "cls"]).size().unstack(fill_value=0))
