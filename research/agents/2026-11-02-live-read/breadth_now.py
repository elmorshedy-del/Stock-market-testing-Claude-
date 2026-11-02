"""Intraday S&P 500 breadth and who is pushing SPY (live read): SPY weights (SSGA, as of Oct 30), sector from the 11 sector-SPDR
holdings, intraday % change per member from the Yahoo spark endpoint (2-5 min delayed; regularMarketTime reported).
Usage: python breadth_now.py <dir with spy_holdings.xlsx and sec_*.xlsx> -> out/breadth_now.json"""
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; D = Path(sys.argv[1])
def hold(p):
    x = pd.read_excel(p, header=None); h = x.iloc[4].tolist(); x = x.iloc[5:]; x.columns = h
    return x.dropna(subset=["Ticker"])[["Ticker", "Weight"]].assign(Weight=lambda d: pd.to_numeric(d.Weight, errors="coerce"))
spy = hold(D / "spy_holdings.xlsx"); spy = spy[spy.Ticker.str.match(r"^[A-Z.]+$")]
SEC = {"xlk": "Tech", "xlc": "Comm", "xly": "Discretionary", "xlp": "Staples", "xle": "Energy", "xlf": "Financials", "xlv": "Health", "xli": "Industrials", "xlb": "Materials", "xlre": "Real estate", "xlu": "Utilities"}
sec = {}
for k, v in SEC.items():
    for t in hold(D / f"sec_{k}.xlsx").Ticker: sec[str(t)] = v
spy["sector"] = spy.Ticker.map(sec).fillna("Other"); spy["yt"] = spy.Ticker.str.replace(".", "-", regex=False)
chg, tm = {}, {}
tick = list(spy.yt)
for i in range(0, len(tick), 20):
    q = ",".join(tick[i:i + 20])
    for k in range(3):
        r = subprocess.run(["curl", "-s", "-m", "30", "-A", "Mozilla/5.0", f"https://query1.finance.yahoo.com/v7/finance/spark?symbols={q}&range=1d&interval=1d"], capture_output=True, text=True).stdout
        try:
            for it in json.loads(r)["spark"]["result"]:
                m = it["response"][0]["meta"]; chg[it["symbol"]] = m.get("regularMarketChangePercent"); tm[it["symbol"]] = m.get("regularMarketTime")
            break
        except Exception: time.sleep(1 + k)
spy["chg"] = spy.yt.map(chg).astype(float); x = spy.dropna(subset=["chg"]).copy(); x["w"] = x.Weight / x.Weight.sum()
x["contrib_bp"] = 100 * x.w * x.chg   # contribution to the index move, in bp
stamp = pd.to_datetime(pd.Series(tm).dropna().astype(int), unit="s", utc=True).dt.tz_convert("America/New_York")
res = {"members with quotes": int(len(x)), "quote time (median, Yahoo spark, delayed)": str(stamp.median().strftime("%H:%M:%S")),
       "share of members up": round(float((x.chg > 0).mean()), 3), "advancers / decliners": [int((x.chg > 0).sum()), int((x.chg < 0).sum())],
       "equal-weight move %": round(float(x.chg.mean()), 2), "median move %": round(float(x.chg.median()), 2), "cap-weight move % (reconstructed)": round(float((x.w * x.chg).sum()), 2),
       "top 10 weight: move % / contribution bp": round(float(x.nlargest(10, "w").contrib_bp.sum()), 1), "other 490: contribution bp": round(float(x.drop(x.nlargest(10, 'w').index).contrib_bp.sum()), 1),
       "top 12 by weight [weight %, move %, contribution bp]": {r.Ticker: [round(float(r.Weight), 2), round(float(r.chg), 2), round(float(r.contrib_bp), 1)] for r in x.nlargest(12, "w").itertuples()},
       "biggest pushes up [move %, bp]": {r.Ticker: [round(float(r.chg), 2), round(float(r.contrib_bp), 1)] for r in x.nlargest(8, "contrib_bp").itertuples()},
       "biggest drags [move %, bp]": {r.Ticker: [round(float(r.chg), 2), round(float(r.contrib_bp), 1)] for r in x.nsmallest(8, "contrib_bp").itertuples()}}
g = x.groupby("sector").apply(lambda s: pd.Series({"weight %": round(float(s.Weight.sum()), 1), "eq-wt move %": round(float(s.chg.mean()), 2), "share up": round(float((s.chg > 0).mean()), 2), "contribution bp": round(float(s.contrib_bp.sum()), 1)}))
res["by sector"] = g.sort_values("contribution bp", ascending=False).to_dict(orient="index")
semis = ["NVDA", "AVGO", "AMD", "MU", "INTC", "QCOM", "TXN", "AMAT", "LRCX", "KLAC", "ADI", "MRVL", "WDC", "STX", "SNDK", "MCHP", "ON", "NXPI", "MPWR", "TER"]
res["chips & memory [move %]"] = {t: round(float(x.set_index("Ticker").chg.get(t, np.nan)), 2) for t in semis if t in set(x.Ticker)}
json.dump(res, open(HERE / "out" / "breadth_now.json", "w"), indent=1, default=float); print(json.dumps(res, indent=1, default=float))
