"""First-hour Nasdaq bars for the 9 parked names (gap-teardown candidates), one request per date, cached; then label all 13 names
with the gap-teardown rules (VF/SC from the 09:30-10:30 bars in units of the 20-day sigma). Usage: python label13.py <key> -> out/events13.csv"""
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import databento as db
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; GT = HERE.parent / "2026-10-28-gap-teardown"
P = HERE / "data" / "bars9"; P.mkdir(parents=True, exist_ok=True)
c = db.Historical(sys.argv[1])
cand = pd.read_csv(GT / "out" / "candidates.csv", parse_dates=["date"])
NINE = ["AMD", "META", "MSFT", "AMZN", "GOOGL", "AVGO", "NFLX", "MU", "ORCL"]
todo = cand[cand.sym.isin(NINE)][["date", "sym"]]
api = lambda s, d: "FB" if (s == "META" and d < pd.Timestamp("2022-06-09")) else s


def fetch(item):
    d, syms = item
    f = P / f"{d:%Y%m%d}.parquet"
    if f.exists(): return 0
    old = GT / "data" / "bars" / f"{d:%Y%m%d}.parquet"          # dates cached during the 13-name run already hold these symbols
    if old.exists():
        o = pd.read_parquet(old); o = o[o.sym.isin(syms)]
        if set(o.sym) >= set(syms): o.to_parquet(f); return 0
    et = lambda hm: pd.Timestamp(f"{d.date()} {hm}", tz="America/New_York").tz_convert("UTC")
    amap = {api(s, d): s for s in syms}
    for k in range(5):
        if k: time.sleep(5 * k)
        try:
            df = c.timeseries.get_range(dataset="XNAS.ITCH", symbols=list(amap), schema="ohlcv-1m", start=et("09:30"), end=et("10:35")).to_df()
            if df.empty: pd.DataFrame().to_parquet(f); return 0
            df = df.reset_index()[["ts_event", "symbol", "open", "high", "low", "close", "volume"]]
            df["sym"] = df.symbol.map(amap); df["date"] = d; df.drop(columns="symbol").to_parquet(f); return 1
        except Exception as e:
            err = str(e)[:80]
    print("err", d.date(), err, flush=True); return 0


items = [(d, sorted(g.sym)) for d, g in todo.groupby("date")]
with ThreadPoolExecutor(6) as ex:
    n = sum(ex.map(fetch, items))
parts = [pd.read_parquet(f) for f in sorted(P.glob("*.parquet")) if f.stat().st_size > 0]
fh9 = pd.concat([p for p in parts if len(p)], ignore_index=True)
fh4 = pd.read_parquet(GT / "data" / "first_hour.parquet")
fh = pd.concat([fh4, fh9[fh9.sym.isin(NINE)]], ignore_index=True)
fh["hm"] = fh.ts_event.dt.tz_convert("America/New_York").dt.strftime("%H:%M")
g = fh.sort_values("ts_event").groupby(["sym", "date"])
lab = pd.DataFrame({"open1m": g.open.first(), "first_bar_et": g.hm.first(),
                    "high60": fh[fh.hm < "10:30"].groupby(["sym", "date"]).high.max(), "low60": fh[fh.hm < "10:30"].groupby(["sym", "date"]).low.min(),
                    "c1029": fh[fh.hm < "10:30"].sort_values("ts_event").groupby(["sym", "date"]).close.last()}).reset_index()
ev = cand.merge(lab, on=["sym", "date"], how="inner"); ev = ev[ev.first_bar_et == "09:30"].copy()
ev["up_sig"] = (ev.high60 / ev.open1m - 1) / ev.sig; ev["dn_sig"] = (ev.low60 / ev.open1m - 1) / ev.sig
ev["cls"] = np.where((ev.dn_sig <= -0.75) & (ev.up_sig <= 0.25), "VF", np.where((ev.up_sig >= 0.75) & (ev.dn_sig >= -0.25), "SC", "mid"))
ev["Y1"] = (ev.c1029 / ev.open1m - 1) / ev.sig; ev["Y2"] = ev.up_sig - ev.dn_sig
ev.to_csv(HERE / "out" / "events13.csv", index=False)
print("fetched", n, "dates;", len(ev), "events;", ev.groupby("sym").cls.value_counts().unstack(fill_value=0).to_string())
