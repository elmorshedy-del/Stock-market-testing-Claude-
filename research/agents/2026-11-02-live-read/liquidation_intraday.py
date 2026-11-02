"""LQ follow-up (descriptive): Friday Oct 30 intraday shape of the AI-crowded basket (when the loss happened; the closing
auction share) vs Thursday and vs RSP; and Monday Nov 2 so far (basket vs RSP). Yahoo 1-minute bars. Usage: python liquidation_intraday.py <dir>"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; Y = Path(sys.argv[1])
B = ["NVDA", "AVGO", "AMD", "MU", "MRVL", "TSM", "SMCI", "ORCL", "CRWV", "NBIS", "VRT", "VST", "CEG", "LITE", "COHR", "ANET", "CLS", "WDC", "STX", "SNDK", "IREN", "CORZ", "PLTR", "ALAB", "CRDO"]
def bars(t):
    r = json.load(open(Y / f"{t}.json"))["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    s = pd.Series(q["close"], index=pd.to_datetime(r["timestamp"], unit="s", utc=True).tz_convert("America/New_York").tz_localize(None)).dropna(); return s
out = {}
for day in ["2026-10-29", "2026-10-30", "2026-11-02"]:
    seg = {}
    for t in B + ["RSP"]:
        s = bars(t); x = s[s.index.normalize() == pd.Timestamp(day)]
        x = x.between_time("09:30", "16:00")
        if len(x) < 30: continue
        prev = s[s.index.normalize() < pd.Timestamp(day)]
        if not len(prev): continue
        pc = float(prev.iloc[-1]); seg[t] = (x / pc - 1)
    if not seg: continue
    path = pd.DataFrame(seg).ffill(); b = path[[c for c in path.columns if c != "RSP"]].mean(1); r = path["RSP"]
    tot = float(b.iloc[-1])
    def at(hhmm): z = b[b.index.time <= pd.Timestamp(f"{day} {hhmm}").time()]; return float(z.iloc[-1]) if len(z) else np.nan
    o = {"basket so far / close %": round(100 * tot, 2), "RSP %": round(100 * float(r.iloc[-1]), 2), "spread %": round(100 * (tot - float(r.iloc[-1])), 2), "last bar": str(b.index[-1].time())}
    if day != "2026-11-02":
        o.update({"basket at 10:00 / 12:00 / 15:00 / 15:59 %": [round(100 * at("10:00"), 2), round(100 * at("12:00"), 2), round(100 * at("15:00"), 2), round(100 * at("15:59"), 2)],
                  "share of the day's move made after 15:00": round((tot - at("15:00")) / tot, 2) if tot else None,
                  "share made in the first 30 min": round(at("10:00") / tot, 2) if tot else None})
    out[day] = o
json.dump(out, open(HERE / "out" / "liquidation_intraday.json", "w"), indent=1); print(json.dumps(out, indent=1))
