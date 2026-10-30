"""Breadth (83 large caps) at the Oct 29 close + descriptive S&P 500 calendar stats for the window ahead:
last trading day of October, first trading days of November, November as a month, midterm-year November-December,
election week. Descriptive only (no tests; these are context, not rules). Usage: python context.py <breadth dir> <GSPC long json> <fresh ^GSPC daily json>"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
bdir, long_p, spx_p = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])


def load(p):
    r = json.load(open(p))["chart"]["result"][0]
    q = r["indicators"]["quote"][0]; c = r["indicators"].get("adjclose", [{}])[0].get("adjclose", q["close"])
    s = pd.Series(c, index=pd.to_datetime(r["timestamp"], unit="s").tz_localize("UTC").tz_convert("America/New_York").normalize().tz_localize(None))
    return s.dropna()[lambda x: ~x.index.duplicated(keep="last")]


out = {}
# breadth
px = pd.DataFrame({p.stem: load(p) for p in bdir.glob("*.json") if p.stem not in ("GSPC", "SPY", "QQQ", "VIX")}).sort_index()
px = px.loc[:"2026-10-29"]; last = px.index[-1]
r1 = px.pct_change().iloc[-1]; r5 = px.iloc[-1] / px.iloc[-6] - 1
b = {"date": str(last.date()), "n names": int(px.iloc[-1].notna().sum()), "share up today": round(float((r1 > 0).mean()), 3),
     "median return today %": round(float(r1.median() * 100), 2), "median 5-day return %": round(float(r5.median() * 100), 2)}
for w in (20, 50, 100, 200):
    ma = px.rolling(w).mean().iloc[-1]; b[f"% above {w}-day avg"] = round(float((px.iloc[-1] > ma).mean() * 100), 1)
hi = px.rolling(252, min_periods=200).max().iloc[-1]; lo = px.rolling(252, min_periods=200).min().iloc[-1]
b["% within 2% of 52-week high"] = round(float((px.iloc[-1] >= 0.98 * hi).mean() * 100), 1)
b["% within 2% of 52-week low"] = round(float((px.iloc[-1] <= 1.02 * lo).mean() * 100), 1)
# breadth trend: % above 50-day over the last 15 sessions
ab50 = (px > px.rolling(50).mean()).mean(axis=1) * 100
b["% above 50-day, last 15 sessions"] = ab50.iloc[-15:].round(0).astype(int).tolist()
eq = px.pct_change().mean(axis=1); gs = load(spx_p).pct_change()
b["equal-weight 83 vs S&P, last 20 sessions, pts"] = round(float(((1 + eq.iloc[-20:]).prod() - (1 + gs.loc[eq.index[-20:]]).prod()) * 100), 2)
out["breadth"] = b

# calendar stats (S&P 500 price index, 1950+)
s = load(long_p).loc["1950":"2025-12-31"]; r = s.pct_change().dropna() * 100
df = pd.DataFrame({"r": r}); df["y"], df["m"] = df.index.year, df.index.month
ym = df.groupby(["y", "m"])
df["td"] = ym.cumcount() + 1; df["tdr"] = ym.cumcount(ascending=False) + 1      # trading day of month, from start / from end
def desc(x):
    x = pd.Series(x).dropna(); return {"n": int(len(x)), "mean %": round(float(x.mean()), 3), "median %": round(float(x.median()), 3), "% up": round(float((x > 0).mean() * 100), 1)}
cal = {}
for era, lo_ in (("1950-2025", 1950), ("2000-2025", 2000), ("2020-2025", 2020)):
    d = df[df.y >= lo_]
    cal[era] = {"all days": desc(d.r), "last trading day of October": desc(d[(d.m == 10) & (d.tdr == 1)].r),
                "first 3 trading days of November (sum)": desc(d[(d.m == 11) & (d.td <= 3)].groupby("y").r.sum()),
                "turn of month (last day + first 3), all months, sum": desc(pd.concat([d[d.tdr == 1].groupby(["y", "m"]).r.sum(), d[d.td <= 3].groupby(["y", "m"]).r.sum()]).groupby(level=[0, 1]).sum()),
                "November month (sum of daily %)": desc(d[d.m == 11].groupby("y").r.sum()),
                "November first half (td 1-10, sum)": desc(d[(d.m == 11) & (d.td <= 10)].groupby("y").r.sum()),
                "November second half (td 11+, sum)": desc(d[(d.m == 11) & (d.td > 10)].groupby("y").r.sum())}
mid = [y for y in range(1950, 2026) if y % 4 == 2]
d = df[df.y.isin(mid)]
m = s.resample("ME").last(); mr = m.pct_change() * 100
cal["midterm years"] = {"years": mid, "November month %": desc(mr[(mr.index.month == 11) & mr.index.year.isin(mid)]),
                        "Nov+Dec %": desc([(m[f"{y}-12"].iloc[-1] / m[f"{y}-10"].iloc[-1] - 1) * 100 for y in mid]),
                        "Oct close -> next Apr close %": desc([(m[f"{y+1}-04"].iloc[-1] / m[f"{y}-10"].iloc[-1] - 1) * 100 for y in mid]),
                        "all years Oct close -> next Apr close %": desc([(m[f"{y+1}-04"].iloc[-1] / m[f"{y}-10"].iloc[-1] - 1) * 100 for y in range(1950, 2025)])}
# election week: Mon before election day -> Friday after, midterm and presidential (election day = Tue after first Mon of Nov)
def eday(y):
    d0 = pd.Timestamp(f"{y}-11-01"); return d0 + pd.Timedelta(days=(7 - d0.weekday()) % 7 + 1)   # first Monday + 1
ew = {}
for lab, ys in (("midterm", mid), ("presidential", [y for y in range(1952, 2025, 4)])):
    v = []
    for y in ys:
        e = eday(y); pre = s.loc[:e - pd.Timedelta(days=1)].iloc[-1]; post = s.loc[:e + pd.Timedelta(days=3)].iloc[-1]; v.append((post / pre - 1) * 100)
    ew[lab + " (close before election day -> Friday after)"] = desc(v)
cal["election week"] = ew
out["calendar"] = cal
json.dump(out, open(HERE / "out" / "context.json", "w"), indent=1)
print(json.dumps(out, indent=1))

# conditioning check: the midterm Oct->Apr record mostly started from an autumn low. How far below the 52-week high was each Oct close?
dd = {}
for y in mid:
    oc = s.loc[:f"{y}-10-31"].iloc[-1]; hi52 = s.loc[f"{y-1}-11-01":f"{y}-10-31"].max()
    fwd = (m[f"{y+1}-04"].iloc[-1] / m[f"{y}-10"].iloc[-1] - 1) * 100
    dd[y] = {"Oct close vs 52w high %": round(float((oc / hi52 - 1) * 100), 1), "Oct->Apr %": round(float(fwd), 1),
             "Nov %": round(float(mr[f"{y}-11"].iloc[-1]), 1)}
near = [v for v in dd.values() if v["Oct close vs 52w high %"] >= -5]
out["midterm conditioning"] = {"by year": dd, "years with Oct close within 5% of 52w high": {"n": len(near),
    "Oct->Apr mean %": round(float(np.mean([v["Oct->Apr %"] for v in near])), 1) if near else None,
    "Nov mean %": round(float(np.mean([v["Nov %"] for v in near])), 1) if near else None},
    "2026 Oct 29 close vs 52w high %": round(float((load(spx_p).iloc[-1] / load(spx_p).loc["2025-10-30":].max() - 1) * 100), 2)}
json.dump(out, open(HERE / "out" / "context.json", "w"), indent=1)
print(json.dumps(out["midterm conditioning"], indent=0))
