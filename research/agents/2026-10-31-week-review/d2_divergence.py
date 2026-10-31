"""D2 (pre-registered @ a60ae3a): S&P and QQQ after a record RSP-vs-QQQ 20-session divergence with RSP near its high.
Usage: python d2_divergence.py <long dir with RSP.json QQQ.json GSPC.json> -> out/d2.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; L = Path(sys.argv[1])


def load(f):
    r = json.load(open(L / f))["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    c = r["indicators"].get("adjclose", [{}])[0].get("adjclose", q["close"])
    s = pd.Series(c, index=pd.to_datetime(r["timestamp"], unit="s").tz_localize("UTC").tz_convert("America/New_York").normalize().tz_localize(None)).dropna()
    return s[~s.index.duplicated(keep="last")]


df = pd.DataFrame({"rsp": load("RSP.json"), "qqq": load("QQQ.json"), "spx": load("GSPC.json")}).dropna().loc[:"2026-10-30"]
df["spread"] = df.rsp.pct_change(20) - df.qqq.pct_change(20)
thr = df.spread.expanding(500).quantile(0.975).shift(1)
df["near_hi"] = df.rsp >= 0.98 * df.rsp.rolling(252, min_periods=200).max()
c = df.spx.to_numpy(); n = len(c)
fwd10 = np.r_[np.log(c[10:] / c[:-10]), np.full(10, np.nan)]; top = np.nanquantile(fwd10, 0.9)
df["spx20"] = df.spx.shift(-20) / df.spx - 1; df["qqq20"] = df.qqq.shift(-20) / df.qqq - 1
df["leg"] = [np.any(fwd10[i + 1:i + 21] > top) if i + 21 <= n else np.nan for i in range(n)]
df["dip"] = df.spx <= 0.98 * df.spx.rolling(10).max()
raw = (df.spread >= thr) & df.near_hi


def spaced(mask, gap=20):
    idx, last = [], -10**9
    for i in np.where(mask.to_numpy())[0]:
        if i - last >= gap: idx.append(i); last = i
    return df.index[idx]


ev = spaced(raw); evd = df.loc[ev].dropna(subset=["spx20"])
rng = np.random.default_rng(0)


def base_draw(pool, k):
    pool = np.array(sorted(pool)); out = []
    while len(out) < k:
        cand = rng.choice(pool)
        if all(abs((cand - o).days) > 28 for o in out): out.append(cand)
    return out


res = {"events (all)": [str(d.date()) for d in ev], "n with outcomes": len(evd), "up-leg threshold (10d log)": round(float(top), 4),
       "today": {"spread": round(float(df.spread.iloc[-1]), 4), "threshold": round(float(thr.iloc[-1]), 4), "RSP near high": bool(df.near_hi.iloc[-1]),
                 "event today": bool(raw.iloc[-1]), "spread pct rank (all history)": round(float((df.spread.dropna() < df.spread.iloc[-1]).mean()), 4)}}
for bname, bmask in (("all days", df.spx20.notna()), ("dip days", df.spx20.notna() & df.dip)):
    pool = df.index[bmask]; B = df.loc[pool]
    out = {"base n": int(bmask.sum())}
    for col in ("spx20", "qqq20", "leg"):
        e = evd[col].astype(float).mean(); b = B[col].astype(float).mean()
        draws = np.array([df.loc[base_draw(pool, len(evd)), col].astype(float).mean() for _ in range(2000)])
        bs = np.array([evd[col].astype(float).sample(len(evd), replace=True, random_state=i).mean() for i in range(2000)])
        out[col] = {"events": round(float(e), 4), "base": round(float(b), 4), "p (events > base)": round(float((draws >= e).mean()), 3),
                    "events 90% CI": [round(float(np.quantile(bs, .05)), 4), round(float(np.quantile(bs, .95)), 4)]}
    res[bname] = out
res["per event"] = {str(d.date()): {"spx20 %": round(float(r.spx20 * 100), 2), "qqq20 %": round(float(r.qqq20 * 100), 2), "leg": bool(r.leg), "spread": round(float(r.spread), 3)} for d, r in evd.iterrows()}
for lab, lo, hi in (("pre-2020", "1900", "2019-12-31"), ("2020-21", "2020", "2021-12-31"), ("2022+", "2022", "2026-12-31")):
    x = evd.loc[lo:hi]; res[f"regime {lab}"] = {"n": len(x), "spx20 mean %": round(float(x.spx20.mean() * 100), 2) if len(x) else None, "P(leg)": round(float(x.leg.astype(float).mean()), 2) if len(x) else None}
json.dump(res, open(HERE / "out" / "d2.json", "w"), indent=1)
print(json.dumps(res, indent=1))
