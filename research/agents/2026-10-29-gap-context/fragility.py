"""Fragility F1-F7 (Amendment 1 @ 0ac6f73), using only sessions before D. Usage: python fragility.py <scratchpad> -> out/fragility.csv"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

S = Path(sys.argv[1]); HERE = Path(__file__).resolve().parent; CX = S / "ctx"
sys.path.insert(0, str(HERE.parent / "2026-10-27-flip-wicks"))
from flipmap import norm, t       # noqa: E402


def daily(p):
    r = json.loads(Path(p).read_text())["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    d = pd.DataFrame({k: q[k] for k in ("open", "high", "low", "close", "volume")}, index=pd.to_datetime(r["timestamp"], unit="s").normalize())
    return d[~d.index.duplicated(keep="last")].dropna()


C = pd.read_csv(HERE / "out" / "context.csv", parse_dates=["date"])
D = {s: daily(CX / "daily" / f"{s}.json") for s in C.sym.unique()}
# F7 panel: % of ~50 large caps above their 50-day average at each close
panel = {}
for p in sorted((S / "long").glob("*.json")):
    if p.stem in ("GSPC",): continue
    x = daily(p); panel[p.stem] = (x.close > x.close.rolling(50).mean()).astype(float).where(x.close.rolling(50).count() == 50)
breadth = pd.DataFrame(panel).loc["2017-01-01":].mean(axis=1)
qqq = D["QQQ"]; qhi = qqq.close.rolling(252).max()
# F6 FINRA consolidated short volume
fin = pd.concat([pd.read_csv(f, sep="|", header=None, names=["Date", "Symbol", "ShortVolume", "ShortExemptVolume", "TotalVolume", "Market"], dtype={"Date": str})
                 for f in sorted((CX / "finra").glob("*.txt")) if f.stat().st_size > 0])
fin["date"] = pd.to_datetime(fin.Date); fin = fin.groupby(["Symbol", "date"])[["ShortVolume", "TotalVolume"]].sum()
SPLITS = {"TSLA": ["2020-08-31", "2022-08-25"], "NVDA": ["2021-07-20", "2024-06-10"]}
_cache = {}


def oi_day(sym, d):
    k = (sym, f"{d:%Y-%m}")
    if k not in _cache:
        f = t.DIR / f"{sym}_{d:%Y-%m}_oi.csv.gz"; _cache[k] = norm(pd.read_csv(f)) if f.exists() else pd.DataFrame()
    o = _cache[k]; return o[o.date == d] if len(o) else o


rows = []
for r in C.sort_values("date").itertuples():
    x = D[r.sym]; pr = x[x.index < r.date]
    if len(pr) < 61 or r.date not in x.index: continue
    o = {"sym": r.sym, "date": r.date}; sig = r.sig; p20 = pr.iloc[-20:]
    on = np.log(p20.open / pr.close.shift(1).iloc[-20:]); intra = np.log(p20.close / p20.open)
    o["F1_tow"] = (on.sum() - intra.sum()) / (sig * np.sqrt(20))
    am = (np.log(pr.close).diff().abs() / (pr.close * pr.volume)).replace([np.inf], np.nan)
    o["F2_illiq_ratio"] = am.iloc[-5:].mean() / am.iloc[-60:].mean()
    op = x.open[r.date]; lo, hi = op * (1 - sig), op
    ov = (np.minimum(p20.high, hi) - np.maximum(p20.low, lo)).clip(lower=0) / (p20.high - p20.low).replace(0, np.nan)
    o["F3_vol_below"] = float((ov.fillna(0) * p20.volume).sum() / p20.volume.sum())
    if r.sym in fin.index.get_level_values(0):
        f = fin.loc[r.sym]; f = f[f.index < r.date].iloc[-5:]
        o["F6_dpi5"] = float(f.ShortVolume.sum() / f.TotalVolume.sum()) if len(f) == 5 else np.nan
    b = breadth[breadth.index < r.date]; q = qqq[qqq.index < r.date]
    o["breadth50"] = float(b.iloc[-1]) if len(b) else np.nan
    o["qqq_near_high"] = int(q.close.iloc[-1] >= 0.97 * qhi[q.index[-1]]) if len(q) else 0
    if r.sym in ("TSLA", "NVDA", "QQQ") and pd.Timestamp("2020-01-15") <= r.date <= pd.Timestamp("2026-10-14"):
        oi = oi_day(r.sym, r.date)
        if len(oi):
            oc = next(c for c in oi.columns if "open_interest" in c); pc = r.open1m / (1 + r.gap)
            dte = (oi.expiration - r.date).dt.days
            near = oi[(oi.strike.between(0.95 * pc, 1.05 * pc)) & (dte >= 0) & (dte <= 45)][oc].sum(); tot = oi[(dte >= 0) & (dte <= 120)][oc].sum()
            o["F4_near_share"] = near / tot if tot else np.nan
            d5 = pr.index[-5]
            if not any(d5 < pd.Timestamp(s) <= r.date for s in SPLITS.get(r.sym, [])):
                o5 = oi_day(r.sym, d5)
                if len(o5):
                    w = lambda z: z[(z.cp == "C") & z.strike.between(pc, 1.10 * pc) & (z.expiration >= r.date) & ((z.expiration - r.date).dt.days <= 45)][oc].sum()
                    a, b0 = w(oi), w(o5); o["F5_call_oi_chg"] = (a - b0) / b0 if b0 else np.nan
    rows.append(o)
F = pd.DataFrame(rows)
F.to_csv(HERE / "out" / "fragility.csv", index=False)
print(len(F), "rows;", F.notna().sum().to_dict())
