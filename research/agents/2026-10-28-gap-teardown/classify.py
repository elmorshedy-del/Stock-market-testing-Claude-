"""Label candidates from Databento XNAS 1-minute bars, 09:30-10:35 ET (Amendment 2). Usage: python classify.py <key>  -> data/first_hour.parquet, out/events.csv
Threaded, cost-capped. Prices are Nasdaq-venue trades (unadjusted); classification uses only same-day ratios."""
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import databento as db
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
c = db.Historical(sys.argv[1])
cand = pd.read_csv(HERE / "out" / "candidates.csv", parse_dates=["date"])
extra = pd.DataFrame([{"date": pd.Timestamp(d), "sym": "TSLA"} for d in ("2026-10-26", "2026-10-27")])


def win(day, a, b):
    f = lambda hm: pd.Timestamp(f"{day.date()} {hm}", tz="America/New_York").tz_convert("UTC")
    return f(a), f(b)


def fetch(row):
    a, b = win(row.date, "09:30", "10:35")
    try:
        df = c.timeseries.get_range(dataset="XNAS.ITCH", symbols=[row.sym], schema="ohlcv-1m", start=a, end=b).to_df()
        if df.empty: return None
        df = df.reset_index()[["ts_event", "open", "high", "low", "close", "volume"]]
        df["sym"] = row.sym; df["date"] = row.date
        return df
    except Exception as e:
        print("err", row.sym, row.date.date(), str(e)[:80], flush=True); return None


todo = pd.concat([cand[["date", "sym"]], extra], ignore_index=True).drop_duplicates()
q = c.metadata.get_cost(dataset="XNAS.ITCH", symbols=["TSLA"], schema="ohlcv-1m", start=win(pd.Timestamp("2026-10-27"), "09:30", "10:35")[0], end=win(pd.Timestamp("2026-10-27"), "09:30", "10:35")[1])
print("cost per symbol-day ~", q, "x", len(todo), "=", round(q * len(todo), 3), flush=True)
with ThreadPoolExecutor(8) as ex:
    parts = [p for p in ex.map(fetch, [r for r in todo.itertuples()]) if p is not None]
fh = pd.concat(parts, ignore_index=True); fh.to_parquet(HERE / "data" / "first_hour.parquet")
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
