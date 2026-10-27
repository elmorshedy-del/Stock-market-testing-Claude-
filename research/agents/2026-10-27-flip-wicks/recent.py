"""Descriptive (the motivating days): pre-open flips Oct 13-27 vs each day's high/close, and Oct 27 intraday.
Usage: python recent.py <spyg> <live27/td> <live27/m1>  -> out/recent.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from flipmap import norm, preopen, fine_flip, gex_at, t, exposures

HERE = Path(__file__).resolve().parent
spyg, td27, m1 = map(Path, sys.argv[1:4])
eod = pd.concat([t.read("SPY", "eod")[lambda d: d.date >= "2026-10-08"], norm(pd.read_csv(spyg / "SPY_eod_1015_1023.csv.gz")),
                 norm(pd.read_csv(td27 / "SPY_eod_20261026.csv.gz"))]).drop_duplicates(subset=["date"] + ["expiration", "strike", "cp"], keep="last")
oi = pd.concat([t.read("SPY", "oi")[lambda d: d.date >= "2026-10-08"], norm(pd.read_csv(spyg / "SPY_oi_1015_1023.csv.gz")),
                norm(pd.read_csv(spyg / "SPY_oi_20261026.csv.gz")), norm(pd.read_csv(td27 / "SPY_oi_20261027.csv.gz"))]
               ).drop_duplicates(subset=["date", "expiration", "strike", "cp"], keep="last")
r = json.loads((m1 / "SPY_5m_60d.json").read_text())["chart"]["result"][0]; q = r["indicators"]["quote"][0]
b = pd.DataFrame({k: q[k] for k in ("open", "high", "low", "close")}, index=pd.to_datetime(r["timestamp"], unit="s", utc=True).tz_convert("America/New_York")
                 ).dropna(subset=["close"]).between_time("09:30", "15:59")
daily = b.groupby(b.index.date).agg(open=("open", "first"), high=("high", "max"), low=("low", "min"), close=("close", "last"))
days = sorted(d for d in oi.date.unique() if d >= pd.Timestamp("2026-10-13"))
rows = []
for D in days:
    P = max(x for x in eod.date.unique() if x < D)
    e = eod[eod.date == P]; o = oi[oi.date == D]
    g = preopen(e, o, D); S = float(g.underlying_close.median())
    f_all, f_ex = fine_flip(g, S), fine_flip(g[g.expiration > D], S)
    dd = daily.loc[D.date()] if D.date() in daily.index else None
    rows.append({"day": str(D.date()), "prior close (parity)": round(S, 2), "flip incl 0DTE": round(f_all, 2), "flip excl 0DTE": round(f_ex, 2),
                 "0DTE share of |gamma| at open": round(float(exposures(g[g.expiration == D], S).gex.abs().sum() / exposures(g, S).gex.abs().sum()), 3),
                 **({} if dd is None else {"open": round(dd.open, 2), "high": round(dd.high, 2), "close": round(dd.close, 2),
                                           "high - flip": round(dd.high - f_all, 2), "close - flip": round(dd.close - f_all, 2)})})
    print(rows[-1], flush=True)
# Oct 27 intraday: the flip and the 0DTE strike map as the day runs down
D = pd.Timestamp("2026-10-27"); P = pd.Timestamp("2026-10-26")
e, o = eod[eod.date == P], oi[oi.date == D]
intr = []
for clock, hl in (("09:30", 6.5), ("12:00", 4.0), ("15:00", 1.0), ("15:30", 0.5), ("15:45", 0.25), ("15:55", 1 / 12)):
    g = preopen(e, o, D, hours_left=hl); S = 770.0
    k = exposures(g, S).groupby("K").gex.sum() / 1e9
    k0 = exposures(g[g.expiration == D], S).groupby("K").gex.sum() / 1e9
    intr.append({"time": clock, "flip incl 0DTE": round(fine_flip(g, S), 2), "total GEX at 770 $bn": round(gex_at(g, S) / 1e9, 2),
                 "total GEX at 772 $bn": round(gex_at(g, 772.0) / 1e9, 2), "total GEX at 768 $bn": round(gex_at(g, 768.0) / 1e9, 2),
                 "0DTE gamma by strike 766-775 $bn": {str(int(K)): round(float(v), 3) for K, v in k0.loc[766:775].items()},
                 "all-expiry gamma by strike 766-775 $bn": {str(int(K)): round(float(v), 3) for K, v in k.loc[766:775].items()}})
    print(clock, intr[-1]["flip incl 0DTE"], intr[-1]["total GEX at 770 $bn"], flush=True)
z = o[o.expiration == D]
oc = next(c for c in z.columns if "open_interest" in c)
odte = z[z.strike.between(760, 780)].pivot_table(index="strike", columns="cp", values=oc, aggfunc="sum").fillna(0).astype(int)
res = {"days": rows, "Oct 27 intraday": intr}          # raw per-strike OI is licensed: printed, not saved
(HERE / "out" / "recent.json").write_text(json.dumps(res, indent=1, default=str))
print(odte.loc[764:776].to_string())
