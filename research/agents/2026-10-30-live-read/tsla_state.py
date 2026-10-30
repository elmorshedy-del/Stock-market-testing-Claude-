"""TSLA on its own-options ladder (REPORT 4t/4w/4z) at the Oct 29 close: freed? below flip? own-gamma percentile.
Same recipe as 2026-10-26-ladder-status/status.py:tsla_state (original modules imported unchanged), with
positions = OI dated Oct 28 and IVs = Oct 28 closing chain, spot = Oct 29 close and after-hours.
Usage: python tsla_state.py <live28/td> <live29/td> -> out/tsla_state.json"""
import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
MICRO = HERE.parents[1] / "microstructure"
sys.path[:0] = [str(MICRO), str(HERE.parent / "2026-10-26-tsla-gap-states")]
import levels_live as L                                                    # noqa: E402
import td_gamma as t                                                       # noqa: E402
from hd_gamma import day_metrics                                           # noqa: E402

oi_dir, eod_dir = map(Path, sys.argv[1:3])
day = pd.Timestamp("2026-10-29")
e = L.norm(pd.read_csv(eod_dir / "TSLA_eod_20261028.csv.gz")); e = e[e.date == pd.Timestamp("2026-10-28")].copy(); e["mid"] = (e.bid + e.ask) / 2
o = L.norm(pd.read_csv(oi_dir / "TSLA_oi_20261028.csv.gz")).rename(columns=lambda c: "oi" if "open_interest" in c else c)
g0 = t.chain_day(e.assign(oi=0.0)).drop(columns=["oi"]).merge(o[["expiration", "strike", "cp", "oi"]], on=["expiration", "strike", "cp"], how="left").fillna({"oi": 0})
h = pd.read_csv(MICRO / "out" / "td_gamma_TSLA.csv", parse_dates=["date"]).set_index("date").iloc[-251:]
gn_hist = h.gex_classic / (h.spot * (h.call_oi + h.put_oi) * 100)
out = {"history ends": str(h.index[-1].date())}
for slab, S0 in (("close 403.30", 403.30), ("after hours 397.45", 397.45)):
    g = g0[(g0.expiration > day) & ((g0.expiration - day).dt.days <= t.MAX_DTE) & (g0.oi > 0)].copy()
    g["date"], g["T"], g["underlying_close"] = day, ((g.expiration - day).dt.days / 365).clip(lower=1 / (365 * 24)), S0
    for lab, x in (("Friday (incl. Oct 30)", g), ("after Oct 30 expiry", g[g.expiration > pd.Timestamp("2026-10-30")])):
        m = day_metrics(x, day, {"TSLA": ["TSLA"]})[0]
        gn = m["gex_classic"] / (S0 * (m["call_oi"] + m["put_oi"]) * 100)
        near_pct = float((h.near_oi_share < m["near_oi_share"]).mean())
        out[f"{lab} @ {slab}"] = {"flip": round(float(m["flip_classic"]), 1), "% above flip": round(float(100 * (S0 / m["flip_classic"] - 1)), 2),
            "near-OI share": round(float(m["near_oi_share"]), 4), "near-OI pct": round(near_pct, 3), "freed (<= 1/3)": near_pct <= 1 / 3,
            "below flip": bool(S0 < m["flip_classic"]), "own-gamma pct": round(float((gn_hist < gn).mean()), 3),
            "call wall": float(m["call_wall"]), "put wall": float(m["put_wall"])}
json.dump(out, open(HERE / "out" / "tsla_state.json", "w"), indent=1)
print(json.dumps(out, indent=1))
