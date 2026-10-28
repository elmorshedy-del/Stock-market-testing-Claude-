"""Why TSLA becomes 'deeply freed' after the Oct 30 expiry, how fast freed states rebuild, and TSLA's own dark-pool index (DPI).
Descriptive live read (no new test). Usage: python freed_dpi.py <live27/td> <live28/finra> <ladder28 folder>  -> out/freed_dpi.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
MICRO = HERE.parents[1] / "microstructure"
td, fin, fresh = map(Path, sys.argv[1:4])
sys.path.insert(0, str(MICRO))
import common                                              # noqa: E402
common.DATA = fresh / "data"
from common import load_bars                               # noqa: E402

res = {}
# (a) what the expiry removes: OI dated Oct 27 = positions at the Oct 26 close; price = Oct 27 close
S, D = 407.46, pd.Timestamp("2026-10-27")
oi = pd.read_csv(td / "TSLA_oi_20261027.csv.gz"); oi["expiration"] = pd.to_datetime(oi.expiration)
oc = next(c for c in oi.columns if "open_interest" in c)
oi = oi[(oi.expiration > D) & ((oi.expiration - D).dt.days <= 120) & (oi[oc] > 0)]
near = oi[((oi.expiration - D).dt.days <= 45) & oi.strike.between(0.95 * S, 1.05 * S)]
by = near.groupby(near.expiration.dt.date)[oc].sum()
tot = oi.groupby(oi.expiration.dt.date)[oc].sum()
late = oi.expiration > pd.Timestamp("2026-10-30")
res["(a) near-price OI (+-5%, <=45d) by expiry, contracts"] = {str(k): int(v) for k, v in by.items()}
res["(a) share of near-price OI in Oct 28 + Oct 30 expiries"] = round(float(by[[d for d in by.index if d <= pd.Timestamp('2026-10-30').date()]].sum() / by.sum()), 3)
res["(a) share of ALL OI (<=120d) in Oct 28 + Oct 30"] = round(float(tot[[d for d in tot.index if d <= pd.Timestamp('2026-10-30').date()]].sum() / tot.sum()), 3)
res["(a) near-OI share now / after Friday (same positions)"] = [round(float(near[oc].sum() / oi[oc].sum()), 4), round(float(near[near.expiration > pd.Timestamp("2026-10-30")][oc].sum() / oi[late][oc].sum()), 4)]
k = near.groupby(["strike"])[oc].sum().sort_values(ascending=False).head(6)
k30 = near[near.expiration <= pd.Timestamp("2026-10-30")].groupby("strike")[oc].sum()
res["(a) biggest near-price strikes: total OI / of which expiring by Fri"] = {str(s): [int(v), int(k30.get(s, 0))] for s, v in k.items()}
# (b) history: how deep freed states behave and how fast they rebuild (engine series 2021-Oct 14 2026)
m = pd.read_csv(MICRO / "out" / "td_gamma_TSLA.csv", parse_dates=["date"]).set_index("date")
m["near_pct"] = m.near_oi_share.rolling(252, min_periods=120).rank(pct=True)
c = load_bars("TSLA").close; c = c[c.index >= "2021-01-01"]
r1 = c.pct_change(); r2 = c.pct_change(2)
up = ((r1 >= 0.05) | (r2 >= 0.09)).astype(float); dn = ((r1 <= -0.05) | (r2 <= -0.09)).astype(float)
fwd = lambda s, h: pd.concat([s.shift(-j) for j in range(1, h + 1)], axis=1).max(axis=1)
x = pd.DataFrame({"pct": m.near_pct, "above_flip": m.spot > m.flip_classic}).join(pd.DataFrame({"up3": fwd(up, 3), "dn3": fwd(dn, 3), "r10": c.shift(-10) / c - 1}), how="inner").dropna()
rows = {}
for lab, msk in (("deeply freed (<= 5th pct)", x.pct <= 0.05), ("freed (5th-33rd pct)", (x.pct > 0.05) & (x.pct <= 1 / 3)), ("not freed", x.pct > 1 / 3)):
    for fl, fm in (("above own flip", x.above_flip), ("below own flip", ~x.above_flip)):
        z = x[msk & fm]
        if len(z) >= 10:
            rows[f"{lab}, {fl}"] = {"days": int(len(z)), "up-burst within 3 sessions": round(float(z.up3.mean()), 3), "down-burst within 3": round(float(z.dn3.mean()), 3), "10d return median %": round(100 * float(z.r10.median()), 2)}
res["(b) burst odds by freed depth (TSLA 2021-Oct 14 2026)"] = rows
p = m.near_pct.dropna(); deep = p <= 0.05; starts = p.index[deep & ~deep.shift(1, fill_value=False)]
dur = []
for s0 in starts:
    after = p[p.index > s0]; back = after[after > 1 / 3]
    if len(back): dur.append(int(p.index.get_loc(back.index[0]) - p.index.get_loc(s0)))
res["(b) deep-freed episodes and sessions until back above the 33rd pct (median, IQR)"] = [len(starts), float(np.median(dur)), [float(np.percentile(dur, 25)), float(np.percentile(dur, 75))]]
# (c) TSLA's own dark-pool index: FINRA short share of off-exchange volume
hist = []
for f in sorted((MICRO / "data" / "finra").glob("*.csv")):
    z = pd.read_csv(f, sep="|"); z = z[z.symbol == "TSLA"]
    if len(z): hist.append((pd.Timestamp(f.stem), float(z.short.iloc[0]), float(z.total.iloc[0])))
for f in sorted(fin.glob("*.txt")):
    z = pd.read_csv(f, sep="|"); z = z[z.Symbol == "TSLA"]
    if len(z): hist.append((pd.Timestamp(f.stem), float(z.ShortVolume.iloc[0]), float(z.TotalVolume.iloc[0])))
h = pd.DataFrame(hist, columns=["date", "short", "total"]).drop_duplicates("date", keep="last").set_index("date").sort_index()
h["dpi"] = h.short / h.total; h["dpi5"] = h.dpi.rolling(5).mean()
h["pct5"] = h.dpi5.rolling(252, min_periods=120).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True)
t = h.tail(12)
res["(c) TSLA DPI daily (short share of off-exchange volume), last 12 days"] = {str(i.date()): [round(float(r.dpi), 3), round(float(r.total) / 1e6, 1)] for i, r in t.iterrows()}
res["(c) 5-day DPI and its pctile vs the trailing year"] = {str(i.date()): [round(float(r.dpi5), 3), round(float(r.pct5), 3)] for i, r in t.tail(6).iterrows()}
yr = h.dpi[h.index >= h.index[-1] - pd.Timedelta(days=365)]
res["(c) one-year range / median of daily DPI"] = [round(float(yr.min()), 3), round(float(yr.max()), 3), round(float(yr.median()), 3)]
(HERE / "out" / "freed_dpi.json").write_text(json.dumps(res, indent=1))
print(json.dumps(res, indent=1))
