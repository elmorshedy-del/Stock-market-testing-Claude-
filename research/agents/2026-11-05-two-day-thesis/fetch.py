"""Pull Yahoo daily closes (2025-09 → now) and 5-min bars (last 5 sessions) for the S&P 500 list + factor ETFs.
Usage: python fetch.py <constituents.csv> <outdir>"""
import sys, json, time, random, requests, pandas as pd
from concurrent.futures import ThreadPoolExecutor
H = {"User-Agent": "Mozilla/5.0"}
cons = pd.read_csv(sys.argv[1]); out = sys.argv[2]
syms = sorted(set(cons.Symbol.str.replace(".", "-", regex=False)) | {"SPY", "SMH", "USO", "TLT", "GLD", "RSP", "QQQ", "IWM", "^VIX"})
p1 = int(pd.Timestamp("2025-09-01").timestamp())
def get(url):
    for k in range(5):
        try:
            r = requests.get(url, headers=H, timeout=25)
            if r.status_code == 429: time.sleep(2 + 2 * k + random.random()); continue
            return r.json()["chart"]["result"][0]
        except Exception: time.sleep(1 + k)
    return None
def one(s):
    d = get(f"https://query1.finance.yahoo.com/v8/finance/chart/{s}?period1={p1}&period2={int(time.time()) + 86400}&interval=1d&events=split")
    m = get(f"https://query1.finance.yahoo.com/v8/finance/chart/{s}?range=5d&interval=5m")
    res = {}
    if d:
        q = d["indicators"]["quote"][0]; adj = d["indicators"].get("adjclose", [{}])[0].get("adjclose")
        df = pd.DataFrame({"close": q["close"], "adj": adj if adj else q["close"], "volume": q["volume"]}, index=pd.to_datetime(d["timestamp"], unit="s").normalize())
        res["daily"] = df[~df.index.duplicated(keep="last")].dropna(subset=["close"])
    if m:
        q = m["indicators"]["quote"][0]
        mf = pd.DataFrame({k: q[k] for k in ("open", "high", "low", "close", "volume")}, index=pd.to_datetime(m["timestamp"], unit="s", utc=True).tz_convert("America/New_York")).dropna(subset=["close"])
        res["m5"] = mf
    return s, res
t0 = time.time(); D, M = {}, {}
with ThreadPoolExecutor(8) as ex:
    for s, res in ex.map(one, syms):
        if "daily" in res: D[s] = res["daily"]
        if "m5" in res: M[s] = res["m5"]
pd.concat({s: v.adj for s, v in D.items()}, axis=1).to_parquet(f"{out}/daily_adj.parquet")
pd.concat({s: v.close for s, v in D.items()}, axis=1).to_parquet(f"{out}/daily_close.parquet")
pd.concat({s: v.volume for s, v in D.items()}, axis=1).to_parquet(f"{out}/daily_vol.parquet")
pd.concat(M, names=["sym", "ts"]).to_parquet(f"{out}/m5.parquet")
print(f"daily {len(D)}/{len(syms)}, 5-min {len(M)}/{len(syms)} in {time.time() - t0:.0f}s; missing daily: {sorted(set(syms) - set(D))[:20]}")
