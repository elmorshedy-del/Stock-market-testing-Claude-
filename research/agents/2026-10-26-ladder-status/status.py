"""Where SPY (S&P entry ladder R0-R7, REPORT 4i) and TSLA (own-options states, REPORT 4t/4w/4z) sit on Oct 26.
Original code imported unchanged from research/microstructure (ladder.py, forecast.py, release.py) and
2026-10-26-tsla-gap-states/levels_live.py; only the data folder is swapped for a fresh copy.
Usage: python status.py <fresh folder holding data/{^GSPC,^VIX,^VIX3M,^VIX9D}_1d.json + data/DIX.csv> <spyg folder> <live23/td folder>
-> out/status.json"""
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
MICRO = HERE.parents[1] / "microstructure"
GAPS = HERE.parent / "2026-10-26-tsla-gap-states"
sys.path[:0] = [str(MICRO), str(GAPS)]


def spx_ladder(fresh):
    import common
    common.DATA = Path(fresh) / "data"
    os.chdir(fresh)                                   # forecast.build reads data/DIX.csv relative to cwd
    import ladder as LD
    from forecast import build
    from release import frame
    f = build()                                       # last row = last SqueezeMetrics day
    on = {k: bool(v.iloc[-1]) for k, v in LD.rungs(f).items()}
    hist = {k: [round(float(f.gex_pct.loc[d]), 3) for d in f.index[-8:]] for k in ("gex",)}
    d = frame()                                       # prices run one day past SqueezeMetrics
    hi10, vmax10 = d.c.rolling(10).max(), d.VIX.rolling(10).max()
    return {"squeeze day": str(f.index[-1].date()), "gex_pct": round(float(f.gex_pct.iloc[-1]), 3),
            "dix_pct": round(float(f.dix_pct.iloc[-1]), 3), "rungs on": on,
            "gex_pct last 8 sessions": dict(zip([str(x.date()) for x in f.index[-8:]], hist["gex"])),
            "price day": str(d.index[-1].date()), "SPX": round(float(d.c.iloc[-1]), 2),
            "SPX 10d high": round(float(hi10.iloc[-1]), 2), "SPX vs 10d high %": round(float(100 * (d.c.iloc[-1] / hi10.iloc[-1] - 1)), 2),
            "VIX": round(float(d.VIX.iloc[-1]), 2), "VIX 10d max": round(float(vmax10.iloc[-1]), 2),
            "R6 needs VIX <=": round(float(0.85 * vmax10.iloc[-1]), 2), "R7 needs VIX <=": round(float(0.75 * vmax10.iloc[-1]), 2),
            "R4 needs SPX <=": round(float(0.98 * hi10.iloc[-1]), 2)}


def tsla_state(spyg, l23):
    import levels_live as L
    import td_gamma as t
    from hd_gamma import day_metrics
    sym, day, S0 = "TSLA", pd.Timestamp("2026-10-26"), L.SPOT["TSLA"]
    eod = pd.concat([t.read(sym, "eod")] + [L.norm(pd.read_csv(Path(l23) / f)) for f in ("TSLA_eod_1015_1022.csv.gz", "TSLA_eod_20261023.csv.gz")]
                    ).drop_duplicates(subset=L.KEY, keep="last")
    e = eod[eod.date == pd.Timestamp("2026-10-23")].copy(); e["mid"] = (e.bid + e.ask) / 2
    o = L.norm(pd.read_csv(Path(spyg) / "TSLA_oi_20261026.csv.gz")).rename(columns=lambda c: "oi" if "open_interest" in c else c)
    g = t.chain_day(e.assign(oi=0.0)).drop(columns=["oi"]).merge(o[["expiration", "strike", "cp", "oi"]], on=["expiration", "strike", "cp"], how="left").fillna({"oi": 0})
    g = g[(g.expiration > day) & ((g.expiration - day).dt.days <= t.MAX_DTE) & (g.oi > 0)].copy()
    g["date"], g["T"], g["underlying_close"] = day, ((g.expiration - day).dt.days / 365).clip(lower=1 / (365 * 24)), S0
    h = pd.read_csv(MICRO / "out" / "td_gamma_TSLA.csv", parse_dates=["date"]).set_index("date").iloc[-251:]
    gn_hist = h.gex_classic / (h.spot * (h.call_oi + h.put_oi) * 100)
    out = {"price": S0, "history ends": str(h.index[-1].date())}
    for lab, x in (("Oct 26 positions", g), ("after Oct 30 expiry", g[g.expiration > pd.Timestamp("2026-10-30")])):
        m = day_metrics(x, day, {sym: [sym]})[0]
        gn = m["gex_classic"] / (S0 * (m["call_oi"] + m["put_oi"]) * 100)
        near_pct = float((h.near_oi_share < m["near_oi_share"]).mean())
        out[lab] = {"flip": round(float(m["flip_classic"]), 1), "% above flip": round(float(100 * (S0 / m["flip_classic"] - 1)), 2),
                    "near-OI share": round(float(m["near_oi_share"]), 4), "near-OI pct": round(near_pct, 3), "freed (<= 1/3)": near_pct <= 1 / 3,
                    "below flip": bool(S0 < m["flip_classic"]), "own-gamma pct": round(float((gn_hist < gn).mean()), 3),
                    "call wall": float(m["call_wall"]), "put wall": float(m["put_wall"])}
    return out


if __name__ == "__main__":
    fresh, spyg, l23 = sys.argv[1:4]
    res = {"TSLA": tsla_state(spyg, l23)}
    res["S&P ladder"] = spx_ladder(fresh)
    (HERE / "out").mkdir(exist_ok=True)
    (HERE / "out" / "status.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))
