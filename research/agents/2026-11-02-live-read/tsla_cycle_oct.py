"""TSLA's cycle through October (descriptive map): own-gamma pct, near-price OI pct (freed), flip distance, call wall, from the engine
(history to Oct 14 + the same recipe for Oct 15-30: EOD chain of day t + OI dated t = positions going into t), with TSLA's own DIX (FINRA DPI)
and the S&P GEX/DIX pct. Usage: python tsla_cycle_oct.py <TSLA Oct EOD csv.gz> <OI dir(s) ...> -- <finra rows dir> <DIX.csv> -> out/tsla_cycle_oct.csv"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; MICRO = HERE.parents[1] / "microstructure"
sys.path[:0] = [str(HERE.parent / "2026-10-27-flip-wicks"), str(MICRO)]
from flipmap import norm          # noqa: E402
import td_gamma as t              # noqa: E402
from hd_gamma import day_metrics  # noqa: E402
a = sys.argv[1:]; k = a.index("--"); eodf, oidirs = a[0], a[1:k]; fin, dixf = a[k + 1], a[k + 2]
h = pd.read_csv(MICRO / "out" / "td_gamma_TSLA.csv", parse_dates=["date"]).set_index("date")
ref = h.iloc[-251:]; gn_ref = ref.gex_classic / (ref.spot * (ref.call_oi + ref.put_oi) * 100); near_ref = ref.near_oi_share
E = norm(pd.read_csv(eodf)); E["mid"] = (E.bid + E.ask) / 2
O = pd.concat([norm(pd.read_csv(f)) for d in oidirs for f in sorted(Path(d).glob("TSLA_oi_*.csv.gz"))]).rename(columns=lambda c: "oi" if "open_interest" in c else c)
O = O.drop_duplicates(subset=["date", "expiration", "strike", "cp"], keep="last")
rows = []
for d in sorted(set(E.date) & set(O.date)):
    if d <= h.index[-1]: continue
    e = E[E.date == d].copy(); o = O[O.date == d]
    g = t.chain_day(e.assign(oi=0.0)).drop(columns=["oi"]).merge(o[["expiration", "strike", "cp", "oi"]], on=["expiration", "strike", "cp"], how="left").fillna({"oi": 0})
    g = g[((g.expiration - d).dt.days <= t.MAX_DTE) & (g.oi > 0)]
    m = day_metrics(g, d, {"TSLA": ["TSLA"]})[0]; rows.append(m)
new = pd.DataFrame(rows).set_index("date")
allm = pd.concat([h[["spot", "gex_classic", "call_oi", "put_oi", "flip_classic", "near_oi_share", "call_wall", "put_wall"]], new[["spot", "gex_classic", "call_oi", "put_oi", "flip_classic", "near_oi_share", "call_wall", "put_wall"]]])
allm = allm.loc["2026-09-20":]
gn = allm.gex_classic / (allm.spot * (allm.call_oi + allm.put_oi) * 100)
out = pd.DataFrame({"spot (parity)": allm.spot.round(2), "own gamma pct": gn.apply(lambda v: (gn_ref < v).mean()).round(2),
                    "near-OI pct (freed <= 0.33)": allm.near_oi_share.apply(lambda v: (near_ref < v).mean()).round(2),
                    "% above flip": (100 * (allm.spot / allm.flip_classic - 1)).round(1), "call wall": allm.call_wall, "put wall": allm.put_wall})
rr = []
for f in sorted(Path(fin).glob("*.row")):
    s = f.read_text().strip()
    if s: p = s.split("|"); rr.append((pd.Timestamp(p[0]), float(p[2]) / float(p[4])))
dpi = pd.Series(dict(rr)).sort_index(); d5 = dpi.rolling(5).mean(); d5p = d5.rolling(252, min_periods=120).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True)
g = pd.read_csv(dixf, parse_dates=["date"]).set_index("date"); pct = lambda s: s.rolling(252).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True)
out["TSLA DPI daily"] = dpi.reindex(out.index).round(3); out["TSLA DPI 5d pct"] = d5p.reindex(out.index).round(2)
out["S&P GEX pct"] = pct(g.gex).reindex(out.index).round(2); out["S&P DIX pct"] = pct(g.dix).reindex(out.index).round(2)
out.to_csv(HERE / "out" / "tsla_cycle_oct.csv"); print(out.to_string())
