"""Pre-registration E (@ a16fbee): confirm anomaly E on the never-used May 2018 - Dec 2019 holdout.
E1 QQQ continuation > SPY; E2 on disagreement days SPY rest sign follows QQQ's opening sign; E3 SPY from 09:35 > from 09:30.
Usage: python holdout_e.py <SPY 1m 2018-19> <QQQ 1m 2018-19> -> out/holdout_e.json"""
import json
import sys
from math import erf, sqrt
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; ET = "America/New_York"; rng = np.random.default_rng(2)


def daily(path):
    m = pd.read_parquet(path, columns=["open", "close"]); m.index = m.index.tz_convert(ET)
    m = m[(m.index.time >= pd.Timestamp("09:30").time()) & (m.index.time < pd.Timestamp("16:00").time())]
    m["day"] = m.index.normalize().tz_localize(None); m["mins"] = (m.index.hour - 9) * 60 + m.index.minute - 30
    f = m.groupby("day").mins.min(); m = m[m.day.isin(f[f == 0].index)]
    g = m.groupby("day"); out = pd.DataFrame({"open": g.open.first(), "close": g.close.last(), "n": g.close.size()})
    for t in (4, 14, 19): out[f"p{t}"] = m[m.mins <= t].groupby("day").close.last()
    return out[out.n >= 200]


S, Q = daily(sys.argv[1]), daily(sys.argv[2]); common = S.index.intersection(Q.index); S, Q = S.loc[common], Q.loc[common]
so, sr = np.sign(np.log(S.p14 / S.open)), np.sign(np.log(S.close / S.p14)); qo, qr = np.sign(np.log(Q.p14 / Q.open)), np.sign(np.log(Q.close / Q.p14))
ok = (so != 0) & (qo != 0) & (sr != 0) & (qr != 0); so, sr, qo, qr = so[ok], sr[ok], qo[ok], qr[ok]
cs, cq = (so == sr).astype(float), (qo == qr).astype(float)
d1 = cq - cs; b1 = np.array([d1.sample(len(d1), replace=True, random_state=i).mean() for i in range(5000)])
dis = so != qo; k = int((sr[dis] == qo[dis]).sum()); n = int(dis.sum()); phat = k / n
z2 = (phat - 0.5) / sqrt(0.25 / n); p2 = 0.5 * (1 - erf(z2 / sqrt(2)))
# E3: SPY from 09:35: first window 09:35->09:50 (p4 -> p19), rest 09:50->close
s35o, s35r = np.sign(np.log(S.p19 / S.p4)), np.sign(np.log(S.close / S.p19)); c35 = (s35o == s35r).astype(float)
c30 = (np.sign(np.log(S.p14 / S.open)) == np.sign(np.log(S.close / S.p14))).astype(float)
d3 = c35 - c30; b3 = np.array([d3.sample(len(d3), replace=True, random_state=i).mean() for i in range(5000)])
res = {"days": int(ok.sum()), "span": [str(common.min().date()), str(common.max().date())],
       "E1": {"SPY continuation": round(float(cs.mean()), 3), "QQQ continuation": round(float(cq.mean()), 3), "diff": round(float(d1.mean()), 4),
              "p (diff <= 0)": round(float((b1 <= 0).mean()), 4), "in-sample diff": 0.033},
       "E2": {"disagreement days": n, "P(SPY rest sign = QQQ opening sign)": round(phat, 3), "z": round(z2, 2), "p one-sided": round(p2, 4), "in-sample": 0.551,
              "also P(QQQ rest = QQQ open sign) on these days": round(float((qr[dis] == qo[dis]).mean()), 3),
              "decision": "falsified (<= 48%)" if phat <= 0.48 else ("extend sequentially (>= 52%)" if phat >= 0.52 else "inconclusive (48-52%): stop, report")},
       "E3": {"SPY continuation from 09:30": round(float(c30.mean()), 3), "from 09:35": round(float(c35.mean()), 3), "diff": round(float(d3.mean()), 4),
              "p (diff <= 0)": round(float((b3 <= 0).mean()), 4)},
       "agreement rate of opening signs": round(float((so == qo).mean()), 3)}
json.dump(res, open(HERE / "out" / "holdout_e.json", "w"), indent=1)
print(json.dumps(res, indent=1))
