"""P1 (pre-registered at 8266317 / 0277f6c): TSLA gaps over the largest nearby call-OI strike; today's dealer hedge flow; today's open.
Usage: python p1_tsla.py <breadth folder> <live26 folder> <spyg folder> <live23/td folder>  -> out/p1.json, out/p1_events.csv"""
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
MICRO = HERE.parents[1] / "microstructure"
sys.path.insert(0, str(MICRO))
_c = os.getcwd(); os.chdir(MICRO)
import td_gamma as t                               # noqa: E402
from options_flow import exposures                 # noqa: E402
os.chdir(_c)
sys.path.insert(0, str(HERE.parent / "2026-10-26-tsla-gap-states"))
import gap_test as Gt                              # noqa: E402
import levels_live as Ll                           # noqa: E402
RNG = np.random.default_rng(20261112)


def boot(a, b, n=4000):
    a, b = np.asarray(a, float), np.asarray(b, float)
    o = a.mean() - b.mean()
    bs = np.array([RNG.choice(a, len(a)).mean() - RNG.choice(b, len(b)).mean() for _ in range(n)])
    return float(o), float(2 * min((bs <= 0).mean(), (bs >= 0).mean()))


def main(bfold, live, spyg, l23):
    OUT.mkdir(exist_ok=True)
    f = Gt.ohlc(Path(bfold) / "TSLA.json")
    f = pd.concat([f, Gt.ohlc(Path(live) / "daily" / "TSLA.json")]).sort_index(); f = f[~f.index.duplicated(keep="last")]
    eng = pd.read_csv(MICRO / "out" / "td_gamma_TSLA.csv", parse_dates=["date"]).set_index("date")
    scale = (eng.spot / f.close.reindex(eng.index)).round(0)                   # contemporaneous/split-adjusted: 15, 3 or 1
    scale = scale.reindex(f.index).ffill().bfill()
    F = f.mul(scale, axis=0)
    oi = t.read("TSLA", "oi")
    oi = oi.rename(columns={next(c for c in oi.columns if "open_interest" in c): "oi"})
    oi = oi[(oi.cp == "C")]
    oi["dte"] = (oi.expiration - oi.date).dt.days
    oi = oi[(oi.dte >= 0) & (oi.dte <= 45)]
    byday = oi.groupby(["date", "strike"]).oi.sum()
    pc = F.close.shift(1)
    rows = []
    for d in F.index[(F.index >= "2020-02-01") & (F.index <= "2026-10-14")]:
        g = F.open.loc[d] / pc.loc[d] - 1
        if not np.isfinite(g) or g < 0.02 or d not in byday.index.get_level_values(0):
            continue
        s = byday.loc[d]
        p = pc.loc[d]
        w = s[(s.index > p) & (s.index <= 1.10 * p)]
        if w.empty:
            continue
        k = float(w.idxmax())
        i = F.index.get_loc(d)
        rows.append({"date": d, "gap %": 100 * g, "prior close": p, "open": F.open.loc[d], "max call-OI strike": k, "strike OI": int(w.max()),
                     "crossed": bool(F.open.loc[d] > k), "open->close %": 100 * (F.close.loc[d] / F.open.loc[d] - 1),
                     "next 5d from close %": 100 * (F.close.iloc[min(i + 5, len(F) - 1)] / F.close.loc[d] - 1),
                     "filled same day": bool(F.low.loc[d] <= p), "close held above strike": bool(F.close.loc[d] > k)})
    E = pd.DataFrame(rows).set_index("date")
    A, B = E[E.crossed], E[~E.crossed]
    res = {"events (gap >= 2% with a call strike within +10%)": int(len(E)), "crossed / not": [int(len(A)), int(len(B))]}
    for col in ("open->close %", "next 5d from close %"):
        o, p = boot(A[col], B[col])
        res[col] = {"crossed mean": float(A[col].mean()), "not crossed mean": float(B[col].mean()), "difference": o, "p (two-sided)": p,
                    "crossed median": float(A[col].median()), "not median": float(B[col].median())}
    o, p = boot(A["filled same day"].astype(float), B["filled same day"].astype(float))
    res["filled same day"] = {"crossed": float(A["filled same day"].mean()), "not crossed": float(B["filled same day"].mean()), "difference": o, "p": p}
    res["crossed gaps: share closing above the strike"] = float(A["close held above strike"].mean())
    # matched on gap size: compare within gap-size thirds
    E["gq"] = pd.qcut(E["gap %"], 3, labels=False)
    res["open->close by gap-size third (crossed / not)"] = {int(q): [float(x[x.crossed]["open->close %"].mean()), float(x[~x.crossed]["open->close %"].mean()), int(x.crossed.sum()), int((~x.crossed).sum())]
                                                          for q, x in E.groupby("gq")}
    E.to_csv(OUT / "p1_events.csv")
    # ---- today ----
    eod = pd.concat([t.read("TSLA", "eod")] + [Ll.norm(pd.read_csv(Path(l23) / x)) for x in ("TSLA_eod_1015_1022.csv.gz", "TSLA_eod_20261023.csv.gz")]).drop_duplicates(subset=Ll.KEY, keep="last")
    e = eod[eod.date == pd.Timestamp("2026-10-23")].copy(); e["mid"] = (e.bid + e.ask) / 2
    g23 = t.chain_day(e.assign(oi=0.0))
    o26 = Ll.norm(pd.read_csv(Path(spyg) / "TSLA_oi_20261026.csv.gz")).rename(columns=lambda c: "oi" if "open_interest" in c else c)
    day = pd.Timestamp("2026-10-26")
    gg = g23.drop(columns=["oi"]).merge(o26[["expiration", "strike", "cp", "oi"]], on=["expiration", "strike", "cp"], how="left").fillna({"oi": 0})
    gg = gg[(gg.expiration >= day) & (gg.oi > 0)].copy()
    gg["T"] = ((gg.expiration - day).dt.days / 365 + 6.5 / (24 * 365)).clip(lower=1 / (365 * 24))
    def dealer_shares(S, conv):
        x = exposures(gg, S, conv)
        return float((x.dex / S).sum())                                       # dealer delta in shares
    S0, S1 = 372.22, 391.62
    flows = {conv: -(dealer_shares(S1, conv) - dealer_shares(S0, conv)) for conv in ("classic", "short")}
    near = gg[(gg.cp == "C") & ((gg.expiration - day).dt.days <= 45)].groupby("K").oi.sum()
    m5 = json.loads((Path(live) / "TSLA_5m.json").read_text())["chart"]["result"][0]
    idx = pd.to_datetime(m5["timestamp"], unit="s", utc=True).tz_convert("America/New_York")
    q = m5["indicators"]["quote"][0]
    B5 = pd.DataFrame({k: q[k] for k in ("open", "high", "low", "close", "volume")}, index=idx).dropna()
    B5["day"] = B5.index.date
    first = B5.groupby("day").head(6).groupby("day").volume.sum()
    today = B5[B5.day == B5.day.iloc[-1]]
    daily_vol = f.volume if "volume" in f else None
    res["today Oct 26"] = {"gap over": "Friday high $377.32 and the $375 / $380 call strikes",
                           "call OI <=45d at 375 / 380 / 385 / 390 / 395 / 400 (positions at Fri close)": {int(k): int(near.get(k, 0)) for k in (375, 380, 385, 390, 395, 400)},
                           "dealer hedge shares needed, $372.22 -> $391.62 (classic = dealers long calls, short puts)": int(flows["classic"]),
                           "same under all-short (customers long everything)": int(flows["short"]),
                           "first 30 min volume (shares) today vs prior 4-day average": [int(first.iloc[-1]), int(first.iloc[:-1].mean())],
                           "first 30 min path (5-min closes)": today.close.iloc[:6].round(2).tolist(), "day volume (shares)": int(today.volume.sum())}
    (OUT / "p1.json").write_text(json.dumps(res, indent=1, default=float))
    return res


if __name__ == "__main__":
    print(json.dumps(main(*sys.argv[1:5]), indent=1, default=float))
