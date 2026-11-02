"""A3 candidate screen on 2023 daily data only (before the 2024-26 test window). -> out/screen_2023.csv/json"""
import json
import time
import urllib.request
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent; O = HERE / "out"
U = ["NVDA", "AMD", "AVGO", "MU", "TSM", "SMCI", "PLTR", "COIN", "MSTR", "HOOD", "RIVN", "SOFI", "MARA", "RIOT", "AFRM", "UPST", "RBLX", "SHOP", "ARM", "MRVL", "INTC", "CRWD",
     "SNOW", "NFLX", "UBER", "ABNB", "BA", "AAPL", "MSFT", "GOOGL", "AMZN", "META", "ORCL", "JPM", "XOM", "UNH", "LLY", "COST", "WMT", "TSLA"]
rows = []
for s in U:
    u = f"https://query1.finance.yahoo.com/v8/finance/chart/{s}?period1=1669852800&period2=1704067200&interval=1d"   # 2022-12-01 .. 2023-12-31
    try:
        r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=30))["chart"]["result"][0]
    except Exception as e:
        rows.append({"sym": s, "error": str(e)[:50]}); continue
    q = r["indicators"]["quote"][0]
    d = pd.DataFrame({k: q[k] for k in ["high", "low", "close", "volume"]}, index=pd.to_datetime(r["timestamp"], unit="s")).dropna()
    tr = pd.concat([d.high - d.low, (d.high - d.close.shift()).abs(), (d.low - d.close.shift()).abs()], axis=1).max(axis=1)
    atrp = (tr.rolling(14).mean() / d.close * 100); y = d.index.year == 2023
    rows.append({"sym": s, "days_2023": int(y.sum()), "atr_pct_2023": round(float(atrp[y].mean()), 2), "dollar_vol_bn_2023": round(float((d.close * d.volume)[y].mean() / 1e9), 2)})
    time.sleep(0.3)
S = pd.DataFrame(rows).set_index("sym")
liq = S[(S.dollar_vol_bn_2023 >= 1.5) & (S.index != "TSLA")].sort_values("atr_pct_2023", ascending=False)
picks = {"high (in play)": list(liq.index[:5]), "controls (low)": list(liq.index[-2:])}
S.sort_values("atr_pct_2023", ascending=False).to_csv(O / "screen_2023.csv")
json.dump({"liquid names ranked": liq.reset_index().to_dict("records"), "picks": picks, "TSLA reference": S.loc["TSLA"].to_dict()}, open(O / "screen_2023.json", "w"), indent=1)
print(S.sort_values("atr_pct_2023", ascending=False).to_string()); print("PICKS", picks)
