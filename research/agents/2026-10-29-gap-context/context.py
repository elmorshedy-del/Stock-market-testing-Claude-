"""Context features (known before 09:30) and first-hour outcomes for the 1,512 labeled gap-ups (pre-registered @ 1696818).
Usage: python context.py <scratchpad> -> out/context.csv. C1 and C11 (option chains) come from options_ctx.py."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

S = Path(sys.argv[1]); HERE = Path(__file__).resolve().parent; GT = HERE.parent / "2026-10-28-gap-teardown"
CX = S / "ctx"


def daily(sym):
    for p in (CX / "daily" / f"{sym}.json", S / "ladder28" / "data" / f"{sym}_1d.json", S / "long" / f"{sym}.json", S / "breadth" / f"{sym}.json", S / "etfs" / f"{sym}.json"):
        if p.exists(): break
    r = json.loads(p.read_text())["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    d = pd.DataFrame({k: q[k] for k in ("open", "high", "low", "close", "volume")}, index=pd.to_datetime(r["timestamp"], unit="s").normalize())
    return d[~d.index.duplicated(keep="last")].dropna()


ev = pd.read_csv(GT / "out" / "events.csv", parse_dates=["date"])
fh = pd.read_parquet(GT / "data" / "first_hour.parquet"); fh["hm"] = fh.ts_event.dt.tz_convert("America/New_York").dt.strftime("%H:%M")
c1029 = fh[fh.hm < "10:30"].sort_values("ts_event").groupby(["sym", "date"]).close.last().rename("c1029")
ev = ev.merge(c1029.reset_index(), on=["sym", "date"], how="left")
ev["Y1"] = (ev.c1029 / ev.open1m - 1) / ev.sig
ev["Y2"] = ev.up_sig - ev.dn_sig

spy, tlt, qqq = daily("SPY"), daily("TLT"), daily("QQQ")
td = spy.index[(spy.index >= "2017-01-01")]                       # trading calendar
# extend past the data with weekdays to the end of 2026 (NYSE holidays Nov 26 and Dec 25), so month-end and expiry counts near the data edge are right
fut = pd.bdate_range(td[-1] + pd.Timedelta(days=1), "2026-12-31"); fut = fut[~fut.isin(pd.to_datetime(["2026-11-26", "2026-12-25"]))]
td = td.append(fut)
pos = pd.Series(np.arange(len(td)), index=td)
# monthly expiry: 3rd Friday, or the prior trading day if it is a holiday
opex = []
for m in pd.period_range("2017-01", "2026-12", freq="M"):
    fr = pd.date_range(m.start_time, m.end_time, freq="W-FRI")[2]
    opex.append(td[td <= fr][-1] if len(td[td <= fr]) else fr)
opex = pd.DatetimeIndex(sorted(set(opex)))
op_pos = pos.reindex(opex).dropna().astype(int).to_numpy()


def opex_offset(d):
    p = pos[d]; k = p - op_pos                     # trading days since each expiry
    after = k[k >= 1].min() if (k >= 1).any() else 99
    before = (-k[k <= 0]).min() if (k <= 0).any() else 99   # 0 = expiry day itself
    return after, before


tdm = pd.Series(td, index=td).groupby([td.year, td.month]).cumcount() + 1
tdm_rev = pd.Series(td, index=td).groupby([td.year, td.month]).cumcount(ascending=False) + 1
cpi = set(pd.to_datetime(open(CX / "cpi.txt").read().split())); nfp = set(pd.to_datetime(open(CX / "nfp.txt").read().split()))
fomc = pd.to_datetime(open(CX / "fomc.txt").read().split())
post_fomc = {td[td > f][0] for f in fomc if (td > f).any()}   # the Oct 28 2026 decision's next session is after the data
E = pd.read_csv(CX / "earnings.csv", parse_dates=["report_date", "fq_end"])
E["react"] = [td[td > r][0] if (td > r).any() else pd.NaT for r in E.report_date]
dix = pd.read_csv(S / "late28" / "DIX.csv", parse_dates=["date"]).set_index("date")
dix["gex_pct"] = dix.gex.rolling(252).apply(lambda x: (x[:-1] < x[-1]).mean(), raw=True)

rows = []
D = {s: daily(s) for s in ev.sym.unique()}
for r in ev.itertuples():
    d, s = r.date, r.sym; x = D[s]; prior = x[x.index < d]
    if len(prior) < 70 or d not in pos.index: continue
    o = {"sym": s, "date": d}
    a, b = opex_offset(d); o["days_after_opex"] = a; o["days_to_opex"] = b
    o["C2_after"] = int(1 <= a <= 5); o["C2_before"] = int(b <= 4)
    o["tdm"], o["tdm_rev"] = int(tdm[d]), int(tdm_rev[d])
    o["C3_turn"] = int(o["tdm_rev"] == 1 or o["tdm"] <= 3)
    # month-to-date SPY - TLT through the prior close (C4 applies in the last 4 trading days)
    pm_end = td[(td < d.replace(day=1))][-1]; pc = td[td < d][-1]
    o["mtd_spy_tlt"] = (spy.close[pc] / spy.close[pm_end] - 1) - (tlt.close[pc] / tlt.close[pm_end] - 1)
    o["C4_window"] = int(o["tdm_rev"] <= 4)
    cl = prior.close; sig = r.sig
    o["ext20"] = (cl.iloc[-1] / cl.iloc[-20:].mean() - 1) / sig
    o["above_20d_high"] = int(x.open[d] > prior.high.iloc[-20:].max()) if d in x.index else 0
    o["range10"] = (prior.high.iloc[-10:].max() - prior.low.iloc[-10:].min()) / cl.iloc[-1] / sig
    o["C7_earn"] = int(((E.sym == s) & (E.react == d)).any())
    o["C8_macro"] = int(d in cpi or d in nfp or d in post_fomc)
    if s != "QQQ":
        lr = np.log(prior.close).diff().iloc[-60:]; lq = np.log(qqq.close[qqq.index < d]).diff().iloc[-60:]
        j = lr.index.intersection(lq.index); beta = np.cov(lr[j], lq[j])[0, 1] / np.var(lq[j], ddof=1)
        gq = qqq.open[d] / qqq.close[qqq.index < d].iloc[-1] - 1 if d in qqq.index else np.nan
        o["beta"] = beta; o["qqq_gap"] = gq; o["idio_share"] = (r.gap - beta * gq) / r.gap
    dp = dix[dix.index < d]
    o["gex_pct"] = dp.gex_pct.iloc[-1] if len(dp) else np.nan
    if s in ("AAPL", "NVDA", "TSLA"):
        Es = E[E.sym == s]
        o["blackout"] = int(any((d >= q - pd.Timedelta(days=14)) & (d <= rr) for q, rr in zip(Es.fq_end, Es.react)))
    o["adv_usd"] = float((prior.close * prior.volume).iloc[-20:].mean())
    rows.append(o)
X = pd.DataFrame(rows)
C = ev[["sym", "date", "cls", "scope", "gap", "sig", "open1m", "up_sig", "dn_sig", "Y1", "Y2"]].merge(X, on=["sym", "date"])
# within-stock terciles (C5, C6, C9)
C["ext_top"] = (C.groupby("sym").ext20.rank(pct=True) > 2 / 3).astype(int)
C["base"] = (C.groupby("sym").range10.rank(pct=True) <= 1 / 3).astype(int)
C["C6_breakout"] = (C.above_20d_high.astype(bool) & C.base.astype(bool)).astype(int)
C["idio_top"] = np.where(C.sym == "QQQ", np.nan, (C.groupby("sym").idio_share.rank(pct=True) > 2 / 3).astype(float))
C.to_csv(HERE / "out" / "context.csv", index=False)
print(len(C), "events;", C.cls.value_counts().to_dict())
print(C[["C2_after", "C2_before", "C3_turn", "C4_window", "ext_top", "C6_breakout", "C7_earn", "C8_macro", "idio_top", "blackout"]].sum().to_dict())
print(C[C.date.isin(pd.to_datetime(["2020-09-02", "2026-10-26", "2026-10-27"]))].drop(columns=["scope"]).round(2).T.to_string())
