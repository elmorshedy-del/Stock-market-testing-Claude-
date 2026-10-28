"""Labeling step of classify.py, re-run on the saved bars plus the META-as-FB refetch. Usage: python label.py -> out/events.csv"""
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
cand = pd.read_csv(HERE / "out" / "candidates.csv", parse_dates=["date"])
cand = cand[cand.sym.isin(["TSLA", "AAPL", "NVDA", "QQQ"])]   # Amendment 3
fh = pd.read_parquet(HERE / "data" / "first_hour.parquet")
fb = HERE / "data" / "first_hour_fb.parquet"   # unused once fetch_bars.py requests FB directly
if fb.exists():
    fh = pd.concat([fh[~((fh.sym == "META") & (fh.date < "2022-06-09"))], pd.read_parquet(fb)], ignore_index=True)
g = fh.groupby(["sym", "date"])
lab = pd.DataFrame({"open1m": g.open.first(), "high60": g.apply(lambda x: x[x.ts_event < x.ts_event.iloc[0] + pd.Timedelta("60min")].high.max()),
                    "low60": g.apply(lambda x: x[x.ts_event < x.ts_event.iloc[0] + pd.Timedelta("60min")].low.min()),
                    "first_bar_et": g.ts_event.first().dt.tz_convert("America/New_York").dt.strftime("%H:%M")}).reset_index()
ev = cand.merge(lab, on=["sym", "date"], how="inner")
ev = ev[ev.first_bar_et == "09:30"].copy()
ev["up_sig"] = (ev.high60 / ev.open1m - 1) / ev.sig; ev["dn_sig"] = (ev.low60 / ev.open1m - 1) / ev.sig
ev["cls"] = np.where((ev.dn_sig <= -0.75) & (ev.up_sig <= 0.25), "VF", np.where((ev.up_sig >= 0.75) & (ev.dn_sig >= -0.25), "SC", "mid"))
# market-wide label
cnt = ev.groupby(["date", "cls"]).sym.nunique().unstack(fill_value=0); ngap = ev[ev.sym != "QQQ"].groupby("date").sym.nunique()
qq = ev[ev.sym == "QQQ"].set_index("date").cls
def mw(r):
    if r.cls not in ("VF", "SC"): return ""
    n = cnt.loc[r.date].get(r.cls, 0) - (1 if (qq.get(r.date) == r.cls) else 0)
    return "market-wide" if (qq.get(r.date) == r.cls) or (n >= max(2, np.ceil(len(ev[(ev.date == r.date) & (ev.sym != "QQQ")]) / 3))) else "single-name"
ev["scope"] = ev.apply(mw, axis=1)
ev.to_csv(HERE / "out" / "events.csv", index=False)
print(ev.cls.value_counts().to_dict()); print(ev[ev.cls.isin(["VF", "SC"])].groupby(["cls", "scope"]).size().to_dict())
print("2020-09-02:", ev[ev.date == "2020-09-02"][["sym", "cls", "up_sig", "dn_sig", "scope"]].round(2).to_dict(orient="records"))
