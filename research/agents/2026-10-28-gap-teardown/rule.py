"""Practical read (exploratory, weighted back to the population of all gap-ups >= 0.5 sigma in TSLA/AAPL/NVDA/QQQ):
the 09:35 -> 10:30 return by the first 5 minutes' move, and where the focal days sit. Usage: python rule.py -> out/rule.json"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
F = pd.read_csv(HERE / "out" / "features.csv", parse_dates=["date"])
ev = pd.read_csv(HERE / "out" / "events.csv", parse_dates=["date"])
F["w"] = F.cls.map(ev.cls.value_counts() / F.cls.value_counts())
R5, Y = "ret 09:30->09:35 (sig)", "ret 09:35->10:30 (sig)"
F["b"] = pd.cut(F[R5], [-9, -0.25, 0, 0.25, 9], labels=["<= -0.25", "-0.25..0", "0..+0.25", ">= +0.25"])
rows = []
for b, g in F.groupby("b", observed=True):
    w = g.w / g.w.sum()
    rows.append({"first 5 min (sig)": str(b), "n": len(g), "pop share": float(g.w.sum() / F.w.sum()), "mean next (sig)": float((w * g[Y]).sum()),
                 "P(next < 0)": float((w * (g[Y] < 0)).sum()), "P(next < -0.5 sig)": float((w * (g[Y] < -0.5)).sum()), "P(next > +0.5 sig)": float((w * (g[Y] > 0.5)).sum())})
T = pd.DataFrame(rows)
foc = F[(F.date == "2020-09-02") | ((F.sym == "TSLA") & (F.date >= "2026-10-20"))][["sym", "date", "cls", R5, "M6 first-5m delta %", "M7b first-5m ask depth $", "M7c first-5m bid depth $", Y]]
json.dump({"table": rows, "focal": foc.astype({"date": str}).to_dict(orient="records")}, open(HERE / "out" / "rule.json", "w"), indent=1, default=float)
pd.set_option("display.width", 200); print(T.round(3).to_string(index=False)); print(foc.round(3).to_string(index=False))
