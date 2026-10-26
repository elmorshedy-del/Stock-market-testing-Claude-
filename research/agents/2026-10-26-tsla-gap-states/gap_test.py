"""TSLA up-gap fill rates by state (README.md, pre-registered at 4476060). Usage: python gap_test.py <breadth folder> <live26 folder>  -> out/gaps.json, out/gaps.csv"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
MICRO = HERE.parents[1] / "microstructure"
RNG = np.random.default_rng(20261111)


def ohlc(path):
    d = json.loads(Path(path).read_text())["chart"]["result"][0]
    idx = pd.to_datetime(d["timestamp"], unit="s", utc=True).tz_convert("America/New_York").normalize().tz_localize(None)
    q = d["indicators"]["quote"][0]
    f = pd.DataFrame({k: q[k] for k in ("open", "high", "low", "close")}, index=idx, dtype=float).dropna()
    return f[~f.index.duplicated(keep="last")].sort_index()


def boot_diff(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    obs = a.mean() - b.mean()
    bs = np.array([RNG.choice(a, len(a)).mean() - RNG.choice(b, len(b)).mean() for _ in range(4000)])
    return float(obs), float(2 * min((bs <= 0).mean(), (bs >= 0).mean()))


def main(bfold, live):
    OUT.mkdir(exist_ok=True)
    f = ohlc(Path(bfold) / "TSLA.json")
    today = ohlc(Path(live) / "daily" / "TSLA.json")
    f = pd.concat([f, today]).sort_index(); f = f[~f.index.duplicated(keep="last")]
    g = pd.read_csv(MICRO / "out" / "td_gamma_TSLA.csv", parse_dates=["date"]).set_index("date").flip_classic
    f["flip_prev"] = g.reindex(f.index).ffill(limit=3).shift(1)
    f["prev_close"], f["prev_high"] = f.close.shift(1), f.high.shift(1)
    f["ma50_prev"] = f.close.rolling(50).mean().shift(1)
    f["gap"] = f.open / f.prev_close - 1
    lows5 = pd.concat([f.low.shift(-k) for k in range(0, 5)], axis=1).min(axis=1)       # gap day plus the next 4 sessions
    f["fill_same_day"] = f.low <= f.prev_close
    f["fill_5"] = lows5 <= f.prev_close
    f["ret5_from_open %"] = 100 * (f.close.shift(-4) / f.open - 1)
    E = f[(f.index >= "2020-02-01") & (f.gap >= 0.02)].copy()
    E["S1 flip crossing"] = (E.prev_close < E.flip_prev) & (E.open > E.flip_prev)
    E["S2 breakaway (open > prior high)"] = E.open > E.prev_high
    E["S3 prior close above 50-day"] = E.prev_close > E.ma50_prev
    done = E[E.index <= f.index[-6]]
    res = {"events (gap >= 2%)": int(len(done)), "base: fill same day": float(done.fill_same_day.mean()), "base: fill within 5 sessions": float(done.fill_5.mean()),
           "base: mean 5-session return from the open %": float(done["ret5_from_open %"].mean())}
    big = done[done.gap >= 0.03]
    res["gap >= 3%: events, fill same day, fill 5"] = [int(len(big)), float(big.fill_same_day.mean()), float(big.fill_5.mean())]
    for s in ["S1 flip crossing", "S2 breakaway (open > prior high)", "S3 prior close above 50-day"]:
        x = done[done.flip_prev.notna()] if s.startswith("S1") else done
        a, b = x[x[s]], x[~x[s]]
        d5, p5 = boot_diff(a.fill_5.astype(float), b.fill_5.astype(float)) if len(a) > 2 and len(b) > 2 else (np.nan, np.nan)
        res[s] = {"events yes / no": [int(len(a)), int(len(b))], "fill same day yes / no": [float(a.fill_same_day.mean()), float(b.fill_same_day.mean())],
                  "fill within 5 yes / no": [float(a.fill_5.mean()), float(b.fill_5.mean())], "difference in 5-session fill": d5, "p (two-sided)": p5,
                  "5-session return from open % yes / no": [float(a["ret5_from_open %"].mean()), float(b["ret5_from_open %"].mean())]}
    t = f.iloc[-1]
    res["today (Oct 26)"] = {"gap %": float(100 * t.gap), "open": float(t.open), "prior close": float(t.prev_close), "prior high": float(t.prev_high),
                             "flip at prior close (engine, if available)": None if pd.isna(t.flip_prev) else float(t.flip_prev),
                             "exact flip at Oct 23 close (from the Oct 23 exact run)": 364.97, "50-day (prior)": float(t.ma50_prev),
                             "breakaway (open > prior high)": bool(t.open > t.prev_high), "prior close above 50-day": bool(t.prev_close > t.ma50_prev),
                             "filled today": bool(t.low <= t.prev_close), "day low": float(t.low), "close": float(t.close)}
    E.to_csv(OUT / "gaps.csv")
    (OUT / "gaps.json").write_text(json.dumps(res, indent=1, default=float))
    return res


if __name__ == "__main__":
    print(json.dumps(main(*sys.argv[1:3]), indent=1, default=float))
