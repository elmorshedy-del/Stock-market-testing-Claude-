"""Data audit D1-D4 (pre-registered): completeness, accuracy vs Yahoo daily, timestamps, half days.
Writes data/rth.parquet (clean regular-session bars, ET) and out/audit.json. Usage: python audit.py [SYMBOL]"""
import json
import sys
import urllib.request
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent; D = HERE / "data"; O = HERE / "out"; O.mkdir(exist_ok=True)
sym = sys.argv[1] if len(sys.argv) > 1 else "SPY"
ds = sys.argv[2] if len(sys.argv) > 2 else "EQUS.MINI"; lab = sys.argv[3] if len(sys.argv) > 3 else sym
S0, S1 = (sys.argv[4], sys.argv[5]) if len(sys.argv) > 5 else ("2024-01-02", "2026-10-30")
b = pd.read_parquet(D / f"{sym}_{ds.replace('.', '_')}_1m.parquet")
b["t"] = pd.to_datetime(b.ts_event, utc=True).dt.tz_convert("America/New_York")
b["date"] = b.t.dt.tz_localize(None).dt.normalize(); b["hm"] = b.t.dt.strftime("%H:%M")
rth = b[(b.hm >= "09:30") & (b.hm <= "15:59")].copy()

# Yahoo daily (unadjusted OHLC from the chart endpoint's quote block)
u = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?period1=1575158400&period2=1793750400&interval=1d"
r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=30))["chart"]["result"][0]
q = r["indicators"]["quote"][0]
y = pd.DataFrame({k: q[k] for k in ["open", "high", "low", "close", "volume"]}, index=pd.to_datetime(r["timestamp"], unit="s").tz_localize("UTC").tz_convert("America/New_York").tz_localize(None).normalize())
y = y[~y.index.duplicated(keep="last")].dropna(); y.to_csv(D / f"{lab}_yahoo_daily.csv")

# D4 half days: Yahoo sessions whose last bar in our data is <= 13:00, or known NYSE early closes
last_hm = b.groupby("date").hm.max(); first_rth = rth.groupby("date").hm.min()
n = rth.groupby("date").size(); n30 = rth[rth.hm < "10:00"].groupby("date").size()
early = [d for d in y.index if d in n.index and rth[(rth.date == d)].hm.max() <= "13:00"]
sess = [d for d in y.index if d >= pd.Timestamp(S0) and d <= pd.Timestamp(S1)]
rows = []
for d in sess:
    if d not in n.index:
        rows.append(dict(date=d, status="missing_day")); continue
    g = rth[rth.date == d]
    o, h, l, c = g.open.iloc[0], g.high.max(), g.low.min(), g.close.iloc[-1]
    yy = y.loc[d]
    dev = max(abs(o / yy.open - 1), abs(h / yy.high - 1), abs(l / yy.low - 1), abs(c / yy.close - 1)) * 100
    half = d in early
    miss30 = 30 - int(n30.get(d, 0)); miss = 390 - int(n[d])
    st = "half_day" if half else ("bad_D1" if (miss30 > 5 or miss > 20) else ("bad_D3" if first_rth[d] != "09:30" else ("bad_D2" if dev > 0.05 else "clean")))
    rows.append(dict(date=d, status=st, bars=int(n[d]), miss_first30=miss30, max_dev_pct=round(dev, 4),
                     d_open=round((o / yy.open - 1) * 1e4, 2), d_high=round((h / yy.high - 1) * 1e4, 2), d_low=round((l / yy.low - 1) * 1e4, 2), d_close=round((c / yy.close - 1) * 1e4, 2)))
A = pd.DataFrame(rows); A.to_csv(O / ("audit_days.csv" if lab == "SPY" else f"audit_days_{lab}.csv"), index=False)
full = A[A.status != "half_day"]
res = {"symbol": sym, "dataset": ds, "label": lab, "window": [S0, S1], "sessions (Yahoo)": len(A), "status counts": A.status.value_counts().to_dict(),
       "clean share of full sessions": round(float((full.status == "clean").mean()), 4),
       "PASS (>= 95% clean)": bool((full.status == "clean").mean() >= 0.95),
       "median |dev| bp open/high/low/close": {k: float(A[k].abs().median()) for k in ["d_open", "d_high", "d_low", "d_close"]},
       "p95 |dev| bp open/high/low/close": {k: float(A[k].abs().quantile(0.95)) for k in ["d_open", "d_high", "d_low", "d_close"]},
       "median bars per full session": float(full.bars.median()), "days with any missing RTH minute": int((full.bars < 390).sum())}
rth[rth.date.isin(A[A.status.isin(["clean", "bad_D2"])].date)][["date", "hm", "open", "high", "low", "close", "volume"]].to_parquet(D / f"{lab}_rth_d2.parquet")   # robustness set
keep = A[A.status == "clean"].date
rth[rth.date.isin(keep)][["date", "hm", "open", "high", "low", "close", "volume"]].to_parquet(D / f"{lab}_rth.parquet")
json.dump(res, open(O / f"audit_{lab}.json", "w"), indent=1, default=str); print(json.dumps(res, indent=1, default=str))
print(A[A.status != "clean"].head(20).to_string())
