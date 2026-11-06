"""Test #4 data: Yahoo ^GSPC daily OHLCV (with volume) from 1927, ^STOXX50E closes from 2007, FRED GDPDEF. Writes data/ (gitignored)."""
import json, urllib.request, datetime as dt
from pathlib import Path
import pandas as pd

H = Path(__file__).resolve().parent
D = H / "data"; D.mkdir(exist_ok=True)


def chart(sym, start):
    t0 = dt.datetime.fromisoformat(start).replace(tzinfo=dt.timezone.utc)
    p1 = int((t0 - dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc)).total_seconds())
    p2 = int(dt.datetime.now(dt.timezone.utc).timestamp()) + 86400
    u = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?period1={p1}&period2={p2}&interval=1d"
    r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60))["chart"]["result"][0]
    q = r["indicators"]["quote"][0]
    idx = pd.to_datetime([dt.datetime.fromtimestamp(t, dt.timezone.utc).date() for t in r["timestamp"]])
    d = pd.DataFrame({k: q[k] for k in ("open", "high", "low", "close", "volume")}, index=idx)
    d = d[~d.index.duplicated(keep="last")].dropna(subset=["close"])
    assert d.index.to_series().diff().dt.days.median() <= 3, f"{sym}: not daily bars"
    return d


if __name__ == "__main__":
    g = chart("^GSPC", "1927-12-01"); g.to_csv(D / "GSPC_ohlcv.csv")
    print("^GSPC", g.index[0].date(), g.index[-1].date(), len(g), "first nonzero volume:", g[g.volume > 0].index[0].date())
    s = chart("^STOXX50E", "2007-01-01"); s.to_csv(D / "STOXX50E.csv")
    print("^STOXX50E", s.index[0].date(), s.index[-1].date(), len(s))
    f = pd.read_csv("https://fred.stlouisfed.org/graph/fredgraph.csv?id=GDPDEF"); f.to_csv(D / "GDPDEF.csv", index=False)
    print("GDPDEF", f.iloc[0, 0], f.iloc[-1, 0], len(f))
    # sanity: absurd daily moves
    r = g.close.pct_change().abs()
    print("largest |daily move| ^GSPC:", r.nlargest(3).round(3).to_dict())
