"""Oct 28 live read: pre-open flips (incl 0DTE, H1 check), the flip as the day ran down, Thursday's map, and the intraday path.
Positions = OI dated Oct 28 (Oct 27 close); IVs = Oct 27 closing chains; spot = Oct 28 close. Engine code imported unchanged.
Usage: python maps.py <live28/td> <live27/td> <live28/y>  -> out/maps.json"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "2026-10-27-flip-wicks"))
from flipmap import norm, preopen, fine_flip, gex_at, exposures, t       # noqa: E402

td28, td27, y = map(Path, sys.argv[1:4])
D, P = pd.Timestamp("2026-10-28"), pd.Timestamp("2026-10-27")
CLOSE = {"SPY": 772.35, "TSLA": 404.46}


def bars(sym):
    r = json.loads((y / f"{sym}_1m.json").read_text())["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    b = pd.DataFrame({k: q[k] for k in ("open", "high", "low", "close", "volume")}, index=pd.to_datetime(r["timestamp"], unit="s", utc=True).tz_convert("America/New_York")).dropna(subset=["close"])
    return b[b.index.date == D.date()]


out = {}
for sym in ("SPY", "TSLA"):
    e = norm(pd.read_csv(td27 / f"{sym}_eod_20261027.csv.gz")); e = e[e.date == P]
    # the Oct 27 chain was pulled to 60 days only: far expiries come from the Oct 26 chain (IVs one day older; stated)
    far = norm(pd.read_csv(td27 / f"{sym}_eod_20261026.csv.gz")); far = far[~far.expiration.isin(e.expiration.unique())].assign(date=P)
    e = pd.concat([e, far], ignore_index=True)
    o = norm(pd.read_csv(td28 / f"{sym}_oi_20261028.csv.gz"))
    g = preopen(e, o, D); S0 = float(g.underlying_close.median())
    pre_incl, pre_excl = fine_flip(g, S0), fine_flip(g[g.expiration > D], S0)
    b = bars(sym); rth = b.between_time("09:30", "15:59"); ah = b[b.index.strftime("%H:%M") >= "16:00"]
    hi, lo = rth.high.max(), rth.low.min()
    at = lambda hm: float(rth.loc[rth.index.strftime("%H:%M") == hm, "close"].iloc[0])
    res = {"pre-open flip incl 0DTE": round(pre_incl, 2), "pre-open flip excl 0DTE": round(pre_excl, 2), "prior close (parity)": round(S0, 2),
           "open": float(rth.open.iloc[0]), "high": float(hi), "high time": rth.high.idxmax().strftime("%H:%M"), "low": float(lo), "low time": rth.low.idxmin().strftime("%H:%M"),
           "close": float(rth.close.iloc[-1]), "high - flip": round(hi - pre_incl, 2), "low - flip": round(lo - pre_incl, 2), "close - flip": round(rth.close.iloc[-1] - pre_incl, 2),
           "share of minutes above the flip": round(float((rth.close > pre_incl).mean()), 3),
           "path": {"09:30-13:59": round(100 * (at("13:59") / rth.open.iloc[0] - 1), 3), "14:00-14:29 (decision)": round(100 * (at("14:29") / at("13:59") - 1), 3),
                    "14:30-15:49 (press conference)": round(100 * (at("15:49") / at("14:29") - 1), 3), "15:50-close": round(100 * (rth.close.iloc[-1] / at("15:49") - 1), 3)},
           "levels at 13:59 / 14:29 / 15:49": [at("13:59"), at("14:29"), at("15:49")],
           "after hours last": float(ah.close.iloc[-1]) if len(ah) else None, "after hours %": round(100 * (ah.close.iloc[-1] / rth.close.iloc[-1] - 1), 2) if len(ah) else None}
    # the flip as the day ran down (same positions)
    res["flip incl 0DTE by time"] = {hm: round(fine_flip(preopen(e, o, D, hours_left=hl), S0), 2) for hm, hl in (("09:30", 6.5), ("12:00", 4.0), ("14:00", 2.0), ("15:00", 1.0), ("15:45", 0.25))}
    # Thursday map: today's expiry gone, spot = today's close (positions are a day stale until Oct 29 OI)
    S = CLOSE[sym]
    gt = preopen(e, o, pd.Timestamp("2026-10-29"), hours_left=6.5); gt = gt[gt.expiration > D].copy(); gt["underlying_close"] = S
    ex = exposures(gt, S); byk = ex.groupby("K").gex.sum() / 1e9
    near = byk[(byk.index >= 0.94 * S) & (byk.index <= 1.06 * S)]
    grid = np.linspace(0.93 * S, 1.07 * S, 113); tot = np.array([gex_at(gt, s) for s in grid]) / 1e9
    k45 = gt[(gt.expiration - D).dt.days <= 45]
    res["Thursday map"] = {"flip": round(fine_flip(gt, S), 2), "total GEX $bn per 1% at close": round(float(gex_at(gt, S) / 1e9), 2),
                           "call wall": float(k45[k45.cp == "C"].groupby("K").oi.sum().idxmax()), "put wall": float(k45[k45.cp == "P"].groupby("K").oi.sum().idxmax()),
                           "top positive strikes ($bn)": near.sort_values(ascending=False).head(5).round(3).to_dict(),
                           "top negative strikes ($bn)": near.sort_values().head(5).round(3).to_dict(),
                           "most negative total-gamma price": round(float(grid[np.argmin(tot)]), 2), "most positive total-gamma price": round(float(grid[np.argmax(tot)]), 2),
                           "Oct 30 expiry share of |gamma|": round(float(ex[ex.exp == pd.Timestamp('2026-10-30').date()].gex.abs().sum() / ex.gex.abs().sum()), 3)}
    # walls (engine definition: expiries <= 45d, strikes within 0.75-1.25 S)
    w = k45[k45.K.between(0.75 * S, 1.25 * S)]
    res["Thursday map"]["call wall"] = float(w[w.cp == "C"].groupby("K").oi.sum().idxmax()); res["Thursday map"]["put wall"] = float(w[w.cp == "P"].groupby("K").oi.sum().idxmax())
    if sym == "TSLA":                                  # freed from the raw OI file (all expiries <= 120d), vs the engine's trailing year
        h = pd.read_csv(Path(t.__file__).parent / "out" / "td_gamma_TSLA.csv", parse_dates=["date"]).set_index("date").iloc[-251:]
        raw = pd.read_csv(td28 / "TSLA_oi_20261028.csv.gz"); raw["expiration"] = pd.to_datetime(raw.expiration); oc = next(c for c in raw.columns if "open_interest" in c)
        raw = raw[(raw.expiration > D) & ((raw.expiration - D).dt.days <= 120) & (raw[oc] > 0)]
        share = lambda r: r[((r.expiration - D).dt.days <= 45) & r.strike.between(0.95 * S, 1.05 * S)][oc].sum() / r[oc].sum()
        s_now, s_fri = share(raw), share(raw[raw.expiration > pd.Timestamp("2026-10-30")])
        res["freed: near-OI share and pctile, now / after Oct 30"] = [[round(float(s_now), 4), round(float((h.near_oi_share < s_now).mean()), 3)], [round(float(s_fri), 4), round(float((h.near_oi_share < s_fri).mean()), 3)]]
    out[sym] = res
    print(sym, json.dumps(res, indent=1, default=str), flush=True)
(HERE / "out" / "maps.json").write_text(json.dumps(out, indent=1, default=str))
