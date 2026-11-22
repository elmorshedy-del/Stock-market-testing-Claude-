"""Long-history data for correlation regimes and the slow state before big falls. Raw data stays in data/ (gitignored)."""
import datetime as dt, io, json, time, urllib.request
from pathlib import Path
import pandas as pd

H = Path(__file__).resolve().parent; D = H / "data"; D.mkdir(exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0"}

def chart(sym, start):
    p1 = int(dt.datetime.fromisoformat(start).replace(tzinfo=dt.timezone.utc).timestamp()); p2 = int(time.time()) + 86400
    u = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.request.quote(sym)}?period1={p1}&period2={p2}&interval=1d"
    r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60))["chart"]["result"][0]
    idx = pd.to_datetime([dt.datetime.fromtimestamp(t, dt.timezone.utc).date() for t in r["timestamp"]])
    s = pd.Series(r["indicators"]["quote"][0]["close"], index=idx, name=sym)
    return s[~s.index.duplicated(keep="last")].dropna()

def fred(sid):
    x = pd.read_csv(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"); x.columns = ["d", sid]
    x["d"] = pd.to_datetime(x.d); return x.set_index("d")[sid].replace(".", pd.NA).astype(float).dropna()

if __name__ == "__main__":
    Y = {"SPX": ("^GSPC", "1927-12-01"), "GOLDF": ("GC=F", "2000-01-01"), "BTC": ("BTC-USD", "2014-09-01"), "VIX": ("^VIX", "1990-01-01"),
         "NIKKEI": ("^N225", "1965-01-01"), "DXY": ("DX-Y.NYB", "1971-01-01"), "HYG": ("HYG", "2007-04-01"), "TNX": ("^TNX", "1962-01-01")}
    for k, (s, a) in Y.items():
        try:
            x = chart(s, a); x.to_csv(D / f"Y_{k}.csv"); print(f"Y {k:7s} {x.index[0].date()} → {x.index[-1].date()} n={len(x)}")
        except Exception as e: print(f"Y {k} FAILED {e}")
        time.sleep(0.4)
    for sid in ["DGS10", "DGS2", "TB3MS", "BAA", "AAA", "BAA10Y", "CPILFESL", "CPIAUCSL", "DEXJPUS", "DTWEXBGS", "TWEXMMTH", "DFII10",
                "VIXCLS", "NFCI", "NFCILEVERAGE", "NFCICREDIT", "NFCIRISK", "BOGZ1FL663067003Q", "GDP"]:
        try:
            x = fred(sid); x.to_csv(D / f"F_{sid}.csv"); print(f"F {sid:18s} {x.index[0].date()} → {x.index[-1].date()} n={len(x)}")
        except Exception as e: print(f"F {sid} FAILED {type(e).__name__}")
    # long monthly gold (London) and Shiller CAPE / earnings
    for name, url in {"gold_monthly": "https://datahub.io/core/gold-prices/r/monthly.csv",
                      "shiller": "https://datahub.io/core/s-and-p-500/r/data.csv"}.items():
        try:
            raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
            x = pd.read_csv(io.BytesIO(raw)); x.to_csv(D / f"{name}.csv", index=False); print(name, x.shape, list(x.columns)[:8], x.iloc[0, 0], x.iloc[-1, 0])
        except Exception as e: print(name, "FAILED", type(e).__name__, str(e)[:100])
