"""Part A1-1 (descriptive): how extreme is the move across horizons and names, each vs its own history."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "2026-11-05-liquidity-cycle"))
from common import yahoo
O = Path(__file__).resolve().parent / "out"
NAMES = ["NVDA", "AMD", "AVGO", "MU", "TSM", "ASML", "AMAT", "LRCX", "KLAC", "MRVL", "INTC", "QCOM", "ARM", "SMCI", "ORCL", "CRWV", "META", "MSFT", "GOOGL", "AMZN", "AAPL", "TSLA", "PLTR", "ANET", "VRT", "DELL", "^SOX", "SMH", "QQQ", "SPY", "RSP"]
def rsi(c, n=14):
    d = c.diff(); up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean(); dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean(); return 100 - 100 / (1 + up / dn)
def feats(c):
    r = c.pct_change(); sig = r.rolling(60).std().shift(1)
    f = pd.DataFrame(index=c.index)
    f["z1"] = r / sig; f["z5"] = (c / c.shift(5) - 1) / (sig * np.sqrt(5)); f["z20"] = (c / c.shift(20) - 1) / (sig * np.sqrt(20))
    hi = c.rolling(60).max(); age = c.rolling(60).apply(lambda w: len(w) - 1 - np.argmax(w), raw=True).clip(lower=1)
    f["ddz"] = np.log(c / hi) / (sig * np.sqrt(age)); f["dd60"] = c / hi - 1
    f["rsi_d"] = rsi(c); wk = c.resample("W-FRI").last(); f["rsi_w"] = rsi(wk).reindex(c.index, method="ffill")
    return f
rows = {}; F = {}
for s in NAMES:
    try: c = yahoo(s, "1994-01-01").close
    except Exception as e: print("fail", s, e); continue
    f = feats(c); F[s] = f; t = f.iloc[-1]
    pr = lambda col: round(float((f[col].iloc[:-1].dropna() < t[col]).mean() * 100), 1)
    rows[s] = {"1d z": round(t.z1, 1), "1d pct": pr("z1"), "5d z": round(t.z5, 1), "5d pct": pr("z5"), "20d z": round(t.z20, 1), "20d pct": pr("z20"),
               "from 60d high %": round(100 * t.dd60, 1), "peak-drop z": round(t.ddz, 1), "peak-drop pct": pr("ddz"), "RSI d": round(t.rsi_d, 0), "RSI d pct": pr("rsi_d"),
               "RSI w": round(t.rsi_w, 0), "RSI w pct": pr("rsi_w"), "history from": int(c.index[0].year)}
T = pd.DataFrame(rows).T
pd.set_option("display.width", 250); print(T.to_string())
ai = T.drop(index=["^SOX", "SMH", "QQQ", "SPY", "RSP"], errors="ignore")
med = ai[["1d z", "5d z", "20d z", "peak-drop z", "RSI d", "RSI w"]].astype(float).median().round(2)
print("\nAI-complex medians (26 names):", med.to_dict())
br = {k: round(float((ai[k].astype(float) <= v).mean()), 2) for k, v in (("1d pct", 1), ("5d pct", 1), ("20d pct", 5), ("peak-drop pct", 5), ("RSI d pct", 5))}
print("share of 26 AI names in own extreme tail (1d/5d <=1st pct; 20d/peak-drop/RSI <=5th pct):", br)
print("AI names with daily RSI <= 30:", int((ai["RSI d"].astype(float) <= 30).sum()), "of", len(ai))
json.dump({"table": T.to_dict(orient="index"), "ai medians": med.to_dict(), "breadth": br}, open(O / "dashboard.json", "w"), indent=1, default=float)
