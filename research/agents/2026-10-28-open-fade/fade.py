"""Gap-up fade test (pre-registered @ 082e59d). Usage: python fade.py <ladder28 folder> <hourly folder> <long folder> <breadth folder>
-> out/fade.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
MICRO = HERE.parents[1] / "microstructure"
fresh, hourly, longd, brd = map(Path, sys.argv[1:5])
rng = np.random.default_rng(0)


def ohlc(path):
    r = json.loads(Path(path).read_text())["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    d = pd.DataFrame({k: q[k] for k in ("open", "high", "low", "close")}, index=pd.to_datetime(r["timestamp"], unit="s").normalize())
    d = d[~d.index.duplicated(keep="last")].dropna()
    return d[(d.open > 0) & (d.high >= d.low)]


def boot_diff(on, off, n=2000):
    on, off = np.asarray(on, float), np.asarray(off, float)
    real = on.mean() - off.mean()
    b = np.array([rng.choice(on, len(on)).mean() - rng.choice(off, len(off)).mean() for _ in range(n)])
    return float(real), float(np.mean(b >= 0))                 # one-sided: on fades more (diff < 0)


def holm(ps):
    o = np.argsort(ps); adj = np.empty(len(ps)); m = len(ps); run = 0
    for i, k in enumerate(o):
        run = max(run, (m - i) * ps[k]); adj[k] = min(1, run)
    return adj


t = ohlc(fresh / "data" / "TSLA_1d.json")
t["prev"] = t.close.shift(1); t["gap"] = t.open / t.prev - 1
t["r2"] = t.prev / t.close.shift(3) - 1                         # prior 2-day close-to-close return, known before the open
t["r2_q"] = t.r2.rolling(252, min_periods=120).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True)
ups = t.gap.where(t.gap >= 0.005)
t["gap_q"] = ups.rolling(252, min_periods=40).apply(lambda w: (w[:-1][~np.isnan(w[:-1])] < w[-1]).mean() if np.isfinite(w[-1]) else np.nan, raw=True)
t["oc"] = t.close / t.open - 1; t["red"] = (t.close < t.open).astype(float); t["open_high"] = (t.high <= t.open * 1.002).astype(float)
m = pd.read_csv(MICRO / "out" / "td_gamma_TSLA.csv", parse_dates=["date"]).set_index("date")
gn = m.gex_classic / (m.spot * (m.call_oi + m.put_oi) * 100)
own = gn.rolling(252, min_periods=120).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True)
t["own_pct"] = own.shift(1).reindex(t.index)                    # prior close
t["call_wall"] = m.call_wall.shift(1).reindex(t.index)
t["split_ok"] = True
ev = t[(t.gap >= 0.005) & (t.index >= "2011-01-01") & (t.index <= "2026-10-23")].copy()
ev["P1"] = ev.r2_q >= 0.8; ev["P4"] = ev.gap_q >= 2 / 3
ev["P2"] = ev.own_pct >= 0.70
# call wall is in option-strike (unadjusted) units = current TSLA units after the 2022 split; engine history starts 2021 (pre-split strikes x3)
adj = np.where(ev.index < "2022-08-25", 3.0, 1.0)
ev["P3"] = (ev.open * adj >= ev.call_wall) & ev.call_wall.notna()
res = {"events (TSLA up-gaps >= 0.5%)": int(len(ev)), "base: mean open->close %, P(red), P(open = high)": [round(100 * ev.oc.mean(), 3), round(ev.red.mean(), 3), round(ev.open_high.mean(), 3)]}
ps, rows = [], {}
for P, sample in (("P1", ev[ev.r2_q.notna()]), ("P2", ev[ev.own_pct.notna()]), ("P3", ev[ev.call_wall.notna()]), ("P4", ev[ev.gap_q.notna()])):
    on, off = sample[sample[P]], sample[~sample[P]]
    d, p = boot_diff(on.oc, off.oc); ps.append(p)
    rows[P] = {"events on / off": [int(len(on)), int(len(off))], "open->close % on / off": [round(100 * on.oc.mean(), 3), round(100 * off.oc.mean(), 3)],
               "diff pts": round(100 * d, 3), "p (one-sided)": round(p, 4), "P(red) on / off": [round(on.red.mean(), 3), round(off.red.mean(), 3)],
               "P(open was the high) on / off": [round(on.open_high.mean(), 3), round(off.open_high.mean(), 3)], "sample": f"{sample.index[0].date()} to {sample.index[-1].date()}"}
for (P, r), a in zip(rows.items(), holm(np.array(ps))):
    r["Holm p"] = round(float(a), 4); r["passes"] = bool(a < 0.05 and r["diff pts"] < 0)
res["predictors"] = rows
full = ev.dropna(subset=["r2_q", "own_pct", "gap_q"]).copy(); full = full[full.call_wall.notna()]
full["count"] = full[["P1", "P2", "P3", "P4"]].sum(axis=1)
res["count of predictors on vs open->close (2021-2026)"] = {int(k): {"events": int(len(x)), "open->close %": round(100 * x.oc.mean(), 3), "P(red)": round(x.red.mean(), 3), "P(open = high)": round(x.open_high.mean(), 3)} for k, x in full.groupby("count")}
from scipy.stats import spearmanr
rho = spearmanr(full["count"], full.oc); res["Spearman(count, open->close)"] = [round(float(rho[0]), 3), round(float(rho[1]), 4)]
# O4 first hour (hourly bars)
r = json.loads((hourly / "TSLA_60m.json").read_text())["chart"]["result"][0]; q = r["indicators"]["quote"][0]
h = pd.DataFrame({k: q[k] for k in ("open", "high", "low", "close")}, index=pd.to_datetime(r["timestamp"], unit="s", utc=True).tz_convert("America/New_York")).dropna()
fh = h[(h.index.hour == 9) & (h.index.minute == 30)]; fh.index = pd.to_datetime(fh.index.date)
e4 = full.join(fh.rename(columns=lambda c: "h_" + c), how="inner")
e4["fh_ret"] = e4.h_close / e4.open - 1; e4["fh_dd"] = e4.h_low / e4.open - 1
res["O4 first hour (Nov 2023-Oct 2026)"] = {f"{k} predictors on": {"events": int(len(x)), "first-hour return %": round(100 * x.fh_ret.mean(), 3), "median drop open->first-hour low %": round(100 * x.fh_dd.median(), 3)} for k, x in e4.groupby(np.minimum(e4["count"], 3))}
# today's state
td = t.loc["2026-10-28"] if pd.Timestamp("2026-10-28") in t.index else None
res["today (Oct 28) gap pctile among trailing up-gaps"] = None if td is None else round(float(td.gap_q), 3) if np.isfinite(td.gap_q) else None
# G1: panel
rows_g, frames = {}, []
for folder in (longd, brd):
    for f in sorted(Path(folder).glob("*.json")):
        k = f.stem
        if k.startswith("^") or k in rows_g: continue
        try: d = ohlc(f)
        except Exception: continue
        d = d[d.index >= "2000-01-01"]
        d["prev"] = d.close.shift(1); d["gap"] = d.open / d.prev - 1; d["r2"] = d.prev / d.close.shift(3) - 1
        d["r2_q"] = d.r2.rolling(252, min_periods=120).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True)
        d["oc"] = d.close / d.open - 1
        d = d[(d.gap >= 0.005) & (d.gap < 0.25) & d.r2_q.notna() & (d.open != d.prev)]
        d["sym"] = k; rows_g[k] = True; frames.append(d[["sym", "gap", "r2_q", "oc"]])
g = pd.concat(frames); g["P1"] = g.r2_q >= 0.8
def by_day_boot(x, n=1000):
    days = x.index.unique(); grp = {dd: z for dd, z in x.groupby(level=0)}
    real = x[x.P1].oc.mean() - x[~x.P1].oc.mean(); b = []
    for _ in range(n):
        s = pd.concat([grp[dd] for dd in rng.choice(days, len(days))]); b.append(s[s.P1].oc.mean() - s[~s.P1].oc.mean())
    return float(real), float(np.mean(np.array(b) >= 0))
for lab, x in (("2020-2026 (83 stocks)", g[(g.index >= "2020-01-01") & (g.index <= "2026-10-23")]), ("2000-2019 (stocks with history)", g[(g.index < "2020-01-01")])):
    dd, p = by_day_boot(x)
    res[f"G1 {lab}"] = {"events": int(len(x)), "stocks": int(x.sym.nunique()), "open->close % P1 on / off": [round(100 * x[x.P1].oc.mean(), 3), round(100 * x[~x.P1].oc.mean(), 3)],
                        "diff pts": round(100 * dd, 3), "p (by-day bootstrap)": round(p, 4), "passes": bool(p < 0.05 and dd < 0),
                        "P(red) on / off": [round(float((x[x.P1].oc < 0).mean()), 3), round(float((x[~x.P1].oc < 0).mean()), 3)]}
(HERE / "out" / "fade.json").write_text(json.dumps(res, indent=1))
print(json.dumps(res, indent=1))
