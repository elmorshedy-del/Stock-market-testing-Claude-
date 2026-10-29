"""'How late is 09:35?' (owner, Oct 29; descriptive). For every labeled gap-up (all 1,512, from the Nasdaq 1-minute bars, no sampling):
the % move 09:30 open -> 09:35, then 09:35 -> 10:30, the lowest low and highest high after 09:35. Usage: python late.py -> out/late.json"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
fh = pd.read_parquet(HERE / "data" / "first_hour.parquet")
fh["hm"] = fh.ts_event.dt.tz_convert("America/New_York").dt.strftime("%H:%M")
ev = pd.read_csv(HERE / "out" / "events.csv", parse_dates=["date"])
rows = []
for (s, d), g in fh.groupby(["sym", "date"]):
    g = g.sort_values("ts_event"); f5 = g[g.hm < "09:35"]; rest = g[(g.hm >= "09:35") & (g.hm < "10:30")]
    if not len(f5) or not len(rest) or f5.hm.iloc[0] != "09:30": continue
    o, p5 = f5.open.iloc[0], f5.close.iloc[-1]
    rows.append({"sym": s, "date": d, "first5 %": 100 * (p5 / o - 1), "first5 low %": 100 * (f5.low.min() / o - 1),
                 "next to 10:30 %": 100 * (rest.close.iloc[-1] / p5 - 1), "low after 09:35 %": 100 * (rest.low.min() / p5 - 1),
                 "high after 09:35 %": 100 * (rest.high.max() / p5 - 1), "first-hour low %": 100 * (min(f5.low.min(), rest.low.min()) / o - 1)})
L = pd.DataFrame(rows).merge(ev[["sym", "date", "cls", "gap", "sig"]], on=["sym", "date"])
L["gap %"] = 100 * L.gap
L["share of fade done by 09:35"] = (L["first5 %"] / L["first-hour low %"]).clip(upper=1)
vf = L[L.cls == "VF"]
cols = ["gap %", "first5 %", "next to 10:30 %", "low after 09:35 %", "high after 09:35 %", "first-hour low %", "share of fade done by 09:35"]
by = vf.groupby("sym")[cols].median().round(2); by["n"] = vf.groupby("sym").size()
# all days whose first 5 minutes were down by at least 0.25 sigma, whatever the class: the warning, including false alarms
w = L[L["first5 %"] / 100 / L.sig <= -0.25]
wb = w.groupby("sym").agg(n=("sym", "size"), first5=("first5 %", "median"), next=("next to 10:30 %", "median"),
                         p_lower=("next to 10:30 %", lambda x: (x < 0).mean()), p_fall1=("low after 09:35 %", lambda x: (x <= -1).mean()),
                         p_rebound1=("high after 09:35 %", lambda x: (x >= 1).mean())).round(2)
ex = vf.sort_values("date").groupby("sym").tail(4)
json.dump({"vf_median": by.reset_index().to_dict(orient="records"), "down5_warning": wb.reset_index().to_dict(orient="records"),
           "examples": ex.astype({"date": str}).round(2).to_dict(orient="records")}, open(HERE / "out" / "late.json", "w"), indent=1)
pd.set_option("display.width", 250)
print("VF days, medians\n", by.to_string())
print("\nAll gap-ups with first 5 min <= -0.25 sigma\n", wb.to_string())
print("\nRecent VF examples\n", ex[["sym", "date", "gap %"] + cols[1:6]].round(2).to_string(index=False))
print("\n2020-09-02\n", L[L.date == "2020-09-02"][["sym", "cls", "gap %"] + cols[1:6]].round(2).to_string(index=False))
