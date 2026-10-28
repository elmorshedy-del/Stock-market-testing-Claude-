"""Event list (Amendment 1 of the pre-registration). Usage: python events.py <scratch root>  -> out/events.csv"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

S = Path(sys.argv[1]); HERE = Path(__file__).resolve().parent
SYMS = ["TSLA", "AAPL", "NVDA", "AMD", "META", "MSFT", "AMZN", "GOOGL", "AVGO", "NFLX", "MU", "ORCL"]


def ohlc(p):
    r = json.loads(Path(p).read_text())["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    d = pd.DataFrame({k: q[k] for k in ("open", "high", "low", "close")}, index=pd.to_datetime(r["timestamp"], unit="s").normalize())
    return d[~d.index.duplicated(keep="last")].dropna()


def first_hour(p):
    r = json.loads(Path(p).read_text())["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    h = pd.DataFrame({k: q[k] for k in ("open", "high", "low", "close")}, index=pd.to_datetime(r["timestamp"], unit="s", utc=True).tz_convert("America/New_York")).dropna()
    f = h[(h.index.hour == 9) & (h.index.minute == 30)]; f.index = pd.to_datetime(f.index.date); return f


rows = []
for s in SYMS:
    dp = S / "ladder28" / "data" / "TSLA_1d.json" if s == "TSLA" else (S / "long" / f"{s}.json" if (S / "long" / f"{s}.json").exists() else S / "breadth" / f"{s}.json")
    d = ohlc(dp)
    d["prev"] = d.close.shift(1); d["gap"] = d.open / d.prev - 1; d["r2"] = d.prev / d.close.shift(3) - 1
    d["sig"] = np.log(d.close).diff().rolling(20).std().shift(1)
    x = d.join(first_hour(S / "hourly" / f"{s}_60m.json").rename(columns=lambda c: "h_" + c), how="inner")
    x = x[x.gap / x.sig >= 0.5].copy()
    x["up_sig"] = (x.h_high / x.open - 1) / x.sig; x["dn_sig"] = (x.h_low / x.open - 1) / x.sig
    x["cls"] = np.where((x.dn_sig <= -0.75) & (x.up_sig <= 0.25), "VF", np.where((x.up_sig >= 0.75) & (x.dn_sig >= -0.25), "SC", "mid"))
    x["sym"] = s
    rows.append(x.reset_index().rename(columns={"index": "date"})[["date", "sym", "cls", "prev", "open", "gap", "r2", "sig", "up_sig", "dn_sig", "h_close"]])
ev = pd.concat(rows).sort_values(["date", "sym"]).reset_index(drop=True)
foc = pd.DataFrame([{"date": pd.Timestamp("2026-10-27"), "sym": "TSLA", "cls": "focal SC"}, {"date": pd.Timestamp("2026-10-28"), "sym": "TSLA", "cls": "focal VF"},
                    {"date": pd.Timestamp("2026-10-26"), "sym": "TSLA", "cls": "focal news gap"}])
ev = pd.concat([ev, foc], ignore_index=True)
ev.to_csv(HERE / "out" / "events.csv", index=False)
print(ev.cls.value_counts().to_dict(), "| per stock VF/SC:", {s: [int(((ev.sym == s) & (ev.cls == "VF")).sum()), int(((ev.sym == s) & (ev.cls == "SC")).sum())] for s in SYMS})
