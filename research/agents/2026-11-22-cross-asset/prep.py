"""Daily cross-asset data for the Oct-Nov 2026 selloff (Yahoo chart API; FRED CSV). Raw data stays in data/ (gitignored)."""
import datetime as dt, json, time, urllib.request
from pathlib import Path
import pandas as pd

H = Path(__file__).resolve().parent; D = H / "data"; D.mkdir(exist_ok=True)

def chart(sym, start):
    t0 = dt.datetime.fromisoformat(start).replace(tzinfo=dt.timezone.utc)
    p1 = int(t0.timestamp()); p2 = int(dt.datetime.now(dt.timezone.utc).timestamp()) + 86400
    u = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.request.quote(sym)}?period1={p1}&period2={p2}&interval=1d"
    r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60))["chart"]["result"][0]
    q = r["indicators"]["quote"][0]
    idx = pd.to_datetime([dt.datetime.fromtimestamp(t, dt.timezone.utc).date() for t in r["timestamp"]])
    d = pd.DataFrame({k: q[k] for k in ("open", "high", "low", "close", "volume")}, index=idx)
    return d[~d.index.duplicated(keep="last")].dropna(subset=["close"])

YAHOO = {"SPX": "^GSPC", "NDX": "^NDX", "SOX": "^SOX", "NVDA": "NVDA", "GOLD": "GC=F", "BTC": "BTC-USD", "SILVER": "SI=F",
         "US10Y": "^TNX", "US5Y": "^FVX", "US30Y": "^TYX", "US3M": "^IRX", "USDJPY": "JPY=X", "AUDJPY": "AUDJPY=X", "DXY": "DX-Y.NYB",
         "VIX": "^VIX", "MOVE": "^MOVE", "HYG": "HYG", "LQD": "LQD", "TLT": "TLT", "OIL": "CL=F", "NIKKEI": "^N225", "KOSPI": "^KS11"}
FRED = ["DGS2", "DGS10", "DFII10", "T10YIE", "THREEFYTP10", "BAMLH0A0HYM2", "IRLTLT01JPM156N", "SOFR", "RRPONTSYD", "WRESBAL"]

if __name__ == "__main__":
    out = {}
    for k, s in YAHOO.items():
        try:
            d = chart(s, "2019-06-01"); d.to_csv(D / f"{k}.csv"); out[k] = d.close
            print(f"{k:7s} {s:10s} {d.index[0].date()} → {d.index[-1].date()}  n={len(d):4d}  last={d.close.iloc[-1]:.4g}")
        except Exception as e:
            print(f"{k:7s} {s:10s} FAILED {type(e).__name__}: {e}")
        time.sleep(0.4)
    for f in FRED:
        try:
            x = pd.read_csv(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={f}&cosd=2019-06-01")
            x.to_csv(D / f"FRED_{f}.csv", index=False); v = x.iloc[:, 1].replace(".", pd.NA).dropna()
            print(f"FRED {f:16s} {x.iloc[0,0]} → {x.iloc[-1,0]}  last={v.iloc[-1]}")
        except Exception as e:
            print(f"FRED {f:16s} FAILED {type(e).__name__}: {e}")
    pd.DataFrame(out).to_csv(D / "closes.csv")
