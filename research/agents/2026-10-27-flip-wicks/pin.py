"""H2: does SPY's close pin to the largest 0DTE OI strike near the 15:30 price? (pre-registered @ ffed9e4)
Usage: python pin.py <folder with SPY_1d.json, SPY_60m.json>  -> out/h2.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
from h1 import daily                                  # noqa: E402


def p1530(folder):
    r = json.loads((Path(folder) / "SPY_60m.json").read_text())["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    h = pd.DataFrame({"open": q["open"]}, index=pd.to_datetime(r["timestamp"], unit="s", utc=True).tz_convert("America/New_York")).dropna()
    h = h[(h.index.hour == 15) & (h.index.minute == 30)]
    return pd.Series(h.open.to_numpy(), index=pd.to_datetime(h.index.date))


def table(od, px, close):
    rows = []
    for D, z in od.groupby("date"):
        if D not in px.index or D not in close.index:
            continue
        P, C = px[D], close[D]
        z = z.set_index("strike"); z = z[(z.index % 1 == 0)]
        ks = [k for k in z.index if abs(k - P) <= 3]
        if len(ks) < 4:
            continue
        tot = (z.loc[ks, "C"] + z.loc[ks, "P"])
        kstar = float(tot.idxmax())
        for k in ks:
            rows.append({"date": D, "K": k, "star": k == kstar, "bucket": int(min(2, abs(k - P) // 1)), "hit": abs(C - k) <= 0.5,
                         "call_heavy": bool(z.loc[k, "C"] > z.loc[k, "P"]), "toward": abs(C - k) < abs(P - k), "oi": float(tot[k])})
    return pd.DataFrame(rows)


def stat(t):
    s = t[t.star]; o = t[~t.star]
    w = s.bucket.value_counts()
    diffs = {b: s[s.bucket == b].hit.mean() - o[o.bucket == b].hit.mean() for b in w.index if (o.bucket == b).any()}
    return sum(diffs[b] * w[b] for b in diffs) / sum(w[b] for b in diffs)


def boot(t, n=2000, seed=0):
    rng = np.random.default_rng(seed); days = t.date.unique(); g = {d: x for d, x in t.groupby("date")}
    real = stat(t); bs = []
    for _ in range(n):
        bs.append(stat(pd.concat([g[d] for d in rng.choice(days, len(days))], ignore_index=True)))
    bs = np.array(bs)
    return float(real), float(np.mean(bs <= 0)), [float(np.quantile(bs, 0.05)), float(np.quantile(bs, 0.95))]


if __name__ == "__main__":
    folder = sys.argv[1]
    od = pd.read_csv(HERE / "data" / "odte_oi.csv.gz", parse_dates=["date"])
    for c in ("C", "P"):
        if c not in od:
            od[c] = 0
    px, close = p1530(folder), daily(folder).close
    t = table(od[(od.date >= "2023-11-27") & (od.date <= "2026-10-12")], px, close)
    s = t[t.star]
    real, p, ci = boot(t)
    res = {"days": int(t.date.nunique()), "candidate rows": int(len(t)),
           "PRIMARY: K* hit rate minus same-bucket others (close within $0.50)": round(real, 4), "p (diff <= 0)": round(p, 4), "90% CI": [round(x, 4) for x in ci],
           "passes (p < 0.05)": p < 0.05,
           "by bucket (K* hit / others hit / K* n)": {int(b): [round(float(s[s.bucket == b].hit.mean()), 3), round(float(t[(~t.star) & (t.bucket == b)].hit.mean()), 3), int((s.bucket == b).sum())] for b in sorted(s.bucket.unique())},
           "share of days close moved toward K*": round(float(s.toward.mean()), 3), "same for other candidates": round(float(t[~t.star].toward.mean()), 3)}
    for lab, m in (("K* call-heavy", s.call_heavy), ("K* put-heavy", ~s.call_heavy)):
        days = set(s[m].date)
        tt = t[t.date.isin(days)]
        r2, p2, ci2 = boot(tt, n=1000, seed=1)
        res[f"split {lab}"] = {"days": len(days), "diff": round(r2, 4), "p": round(p2, 4), "90% CI": [round(x, 4) for x in ci2]}
    (HERE / "out" / "h2.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))
