"""Part D3 (pre-registered @ d0d4b8d): post-2020 weeks like Oct 26-30 (rotation + deep tech selling + TSLA holding)
and what followed. Usage: python precedents.py <daily dir with SPY/QQQ/RSP/TSLA.json> -> out/precedents.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; Dd = Path(sys.argv[1])


def load(f):
    r = json.load(open(Dd / f"{f}.json"))["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    c = r["indicators"].get("adjclose", [{}])[0].get("adjclose", q["close"])
    s = pd.Series(c, index=pd.to_datetime(r["timestamp"], unit="s").tz_localize("UTC").tz_convert("America/New_York").normalize().tz_localize(None)).dropna()
    return s[~s.index.duplicated(keep="last")]


px = pd.DataFrame({k: load(k) for k in ("SPY", "QQQ", "RSP", "TSLA")}).dropna().loc["2019-12-01":"2026-10-30"]
W = px.resample("W-FRI").last().dropna(); wr = W.pct_change()
fw = {h: W.shift(-h) / W - 1 for h in (1, 2, 4)}
dd4 = pd.Series([(px.SPY.loc[d:d + pd.Timedelta(days=28)].min() / W.SPY.loc[d] - 1) if d + pd.Timedelta(days=28) <= px.index[-1] else np.nan for d in W.index], index=W.index)
X = pd.DataFrame({"QQQ wk": wr.QQQ, "RSP-QQQ": wr.RSP - wr.QQQ, "TSLA-QQQ": wr.TSLA - wr.QQQ, "SPY wk": wr.SPY, "TSLA wk": wr.TSLA,
                  "QQQ worst day": px.QQQ.pct_change().resample("W-FRI").min()}).loc["2020-01-03":]
now = X.loc["2026-10-30"].round(4).to_dict()
X = X.loc[:"2026-10-23"]
sets = {"PRIMARY (rotation + tech selloff + TSLA holds)": (X["QQQ wk"] <= -0.015) & (X["RSP-QQQ"] >= 0.02) & (X["TSLA-QQQ"] >= 0.05),
        "S1 rotation weeks": (X["QQQ wk"] <= -0.015) & (X["RSP-QQQ"] >= 0.02),
        "S2 TSLA holds in a tech-selloff week": (X["QQQ wk"] <= -0.015) & (X["TSLA-QQQ"] >= 0.05)}


def spaced(idx, weeks=4):
    keep, last = [], None
    for d in idx:
        if last is None or (d - last).days > weeks * 7: keep.append(d); last = d
    return keep


res = {"this week": now, "n weeks in sample": len(X)}
for name, m in sets.items():
    idx = list(X.index[m.fillna(False)]); keep = spaced(idx)
    rows = {}
    for d in idx:
        rows[str(d.date())] = {"QQQ wk %": round(X.loc[d, "QQQ wk"] * 100, 1), "RSP-QQQ": round(X.loc[d, "RSP-QQQ"] * 100, 1), "TSLA-QQQ": round(X.loc[d, "TSLA-QQQ"] * 100, 1),
                               **{f"{s} +{h}w %": round(float(fw[h].loc[d, s] * 100), 1) for h in (1, 2, 4) for s in ("SPY", "QQQ", "TSLA")},
                               "SPY worst within 4w %": round(float(dd4.loc[d] * 100), 1), "in averages": d in keep}
    agg = {}
    if not keep:
        res[name] = {"matches": 0}; continue
    for h in (1, 2, 4):
        for s in ("SPY", "QQQ", "TSLA"):
            v = fw[h].loc[keep, s]; base = fw[h].loc[X.index, s]
            agg[f"{s} +{h}w"] = {"mean %": round(float(v.mean() * 100), 2), "median %": round(float(v.median() * 100), 2), "% up": round(float((v > 0).mean() * 100)),
                                 "base mean %": round(float(base.mean() * 100), 2), "base % up": round(float((base > 0).mean() * 100))}
    agg["SPY worst within 4w"] = {"median %": round(float(dd4.loc[keep].median() * 100), 2), "base median %": round(float(dd4.loc[X.index].median() * 100), 2)}
    res[name] = {"matches": len(idx), "used (non-overlapping)": len(keep), "per match": rows, "summary": agg}
# S3 daily
d1 = px.pct_change(); m3 = (d1.QQQ <= -0.03) & (d1.TSLA >= -0.01)
idx = [d for d in d1.index[m3] if d >= pd.Timestamp("2020-01-01") and d <= pd.Timestamp("2026-10-01")]
f = {h: px.shift(-h) / px - 1 for h in (5, 10, 20)}
rows = {str(d.date()): {"QQQ day %": round(d1.loc[d, "QQQ"] * 100, 1), "TSLA day %": round(d1.loc[d, "TSLA"] * 100, 1),
                        **{f"{s} +{h}d %": round(float(f[h].loc[d, s] * 100), 1) for h in (5, 10, 20) for s in ("SPY", "QQQ", "TSLA")}} for d in idx}
base = {f"{s} +{h}d base mean %": round(float(f[h].loc["2020":"2026-10-01", s].mean() * 100), 2) for h in (5, 10, 20) for s in ("SPY", "QQQ", "TSLA")}
summ = {f"{s} +{h}d": {"mean %": round(float(np.mean([f[h].loc[d, s] for d in idx]) * 100), 2), "% up": round(float(np.mean([f[h].loc[d, s] > 0 for d in idx]) * 100))} for h in (5, 10, 20) for s in ("SPY", "QQQ", "TSLA")}
res["S3 daily (QQQ <= -3%, TSLA >= -1%)"] = {"matches": len(idx), "per match": rows, "summary": summ, "base": base, "Friday": {"QQQ": round(d1.QQQ.iloc[-1] * 100, 2), "TSLA": round(d1.TSLA.iloc[-1] * 100, 2)}}
json.dump(res, open(HERE / "out" / "precedents.json", "w"), indent=1, default=str)
print(json.dumps({k: (v if k in ("this week", "n weeks in sample") else {kk: vv for kk, vv in v.items()}) for k, v in res.items()}, indent=1, default=str))
