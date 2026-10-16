"""Part B (pre-registered at 8662915): minute-level signed options flow for SPY on Oct 16, and whether it led SPY.
Usage: OMP_NUM_THREADS=1 python flow_today.py -> out/flow.json, out/flow_buckets.csv, out/flow_today.png
Needs data/flow_20261016_{ohlc,quote}.csv.gz (pull_flow.py) and data/SPY_1m.json (Yahoo, refetched)."""
import json
import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
OUT, DATA = HERE / "out", HERE / "data"
MICRO = HERE.parents[1] / "microstructure"
sys.path.insert(0, str(MICRO))
import td_gamma as t                               # noqa: E402  (original, imported unchanged)
from levels_today import bars                      # noqa: E402

DAY = "20261016"
BUCKET, MINSHIFT, NSIM = 5, 6, 2000
RNG = np.random.default_rng(20261016)
BLUE, ORANGE, GREEN, INK, MUTED, GRID, SURF = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"


def minute_flow(spy):
    o = pd.read_csv(DATA / f"flow_{DAY}_ohlc.csv.gz")
    q = pd.read_csv(DATA / f"flow_{DAY}_quote.csv.gz")
    for d in (o, q):
        d["ts"] = pd.to_datetime(d.timestamp, utc=True).dt.tz_convert("America/New_York").dt.tz_localize(None)
    key = ["expiration", "strike", "right"]
    q = q.sort_values(key + ["ts"])
    q["mid0"] = np.where((q.bid > 0) & (q.ask > 0), (q.bid + q.ask) / 2, np.nan)
    q["half0"] = np.where((q.bid > 0) & (q.ask > 0), (q.ask - q.bid) / 2, np.nan)
    q["mid1"] = q.groupby(key).mid0.shift(-1)
    q["half1"] = q.groupby(key).half0.shift(-1)
    m = o.merge(q[key + ["ts", "mid0", "mid1", "half0", "half1"]], on=key + ["ts"], how="left")
    m = m[(m.volume > 0) & (m.vwap > 0)].copy()
    m["mid"] = m[["mid0", "mid1"]].mean(axis=1)
    m["half"] = m[["half0", "half1"]].mean(axis=1)
    m = m[(m.half > 0) & m.mid.notna()]
    m["s"] = ((m.vwap - m.mid) / m.half).clip(-1, 1)
    m["S"] = spy.close.reindex(m.ts).to_numpy()
    m = m[m.S.notna()]
    exp_close = pd.to_datetime(m.expiration) + pd.Timedelta(hours=16)
    m["T"] = ((exp_close - (m.ts + pd.Timedelta(minutes=1))).dt.total_seconds() / (365 * 24 * 3600)).clip(lower=1 / (365 * 24 * 60))
    call = (m.right.str.upper().str[0] == "C").to_numpy()
    m["iv"] = t.implied_vol(m.mid.to_numpy(), m.S.to_numpy(), m.strike.to_numpy(), m["T"].to_numpy(), call)
    m = m[np.isfinite(m.iv) & (m.iv > 0)]
    call = (m.right.str.upper().str[0] == "C").to_numpy()
    d1 = (np.log(m.S / m.strike) + 0.5 * m.iv ** 2 * m["T"]) / (m.iv * np.sqrt(m["T"]))
    m["delta"] = np.where(call, norm.cdf(d1), norm.cdf(d1) - 1)
    m["flow"] = m.s * m.volume * m.delta * 100            # signed delta bought, in SPY shares
    m["dte"] = np.where(pd.to_datetime(m.expiration).dt.date == pd.Timestamp(DAY).date(), "0DTE", "next day")
    return m


def tests(f, spy):
    end = spy.index[-1]
    full = f[f.index <= end - pd.Timedelta(minutes=BUCKET - 1)]
    b = full.resample(f"{BUCKET}min", origin="start_day", offset="9h30min").sum()
    px = spy.close.resample(f"{BUCKET}min", origin="start_day", offset="9h30min").last()
    first = spy.open.resample(f"{BUCKET}min", origin="start_day", offset="9h30min").first()
    ret = np.log(px / first)
    B = pd.DataFrame({"flow": b, "ret": ret}).dropna()
    B = B[B.index + pd.Timedelta(minutes=BUCKET) <= end + pd.Timedelta(minutes=1)]
    x, y = B.flow.to_numpy(), B.ret.to_numpy()
    n = len(B)
    lead = np.corrcoef(x[:-1], y[1:])[0, 1]
    same = np.corrcoef(x, y)[0, 1]
    shifts = RNG.integers(MINSHIFT, n - MINSHIFT, NSIM)
    null_lead = np.array([np.corrcoef(np.roll(x, s)[:-1], y[1:])[0, 1] for s in shifts])
    null_same = np.array([np.corrcoef(np.roll(x, s), y)[0, 1] for s in shifts])
    res = {"buckets": int(n), "distinct_shifts": int(n - 2 * MINSHIFT + 1),
           "H1 flow leads next bucket: corr": float(lead), "H1 p (one-sided)": float((null_lead >= lead).mean()),
           "H2 same bucket: corr": float(same), "H2 p (one-sided)": float((null_same >= same).mean()),
           "net delta bought today, shares": float(x.sum())}
    return B, res


def figure(spy, m, B, res):
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                         "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
    f, (a, b, c) = plt.subplots(3, 1, figsize=(14, 10), sharex=True, gridspec_kw={"height_ratios": [2, 1.4, 1.2], "hspace": 0.12})
    a.plot(spy.index, spy.close, color=INK, lw=1.3)
    a.set_ylabel("SPY")
    a.set_title(f"SPY Oct 16 to {spy.index[-1]:%H:%M} with net options delta bought (0DTE and next-day, 25 strikes either side; 1-minute ThetaData bars and quotes)",
                loc="left", fontsize=9.5, color=INK)
    for lab, col in (("0DTE", ORANGE), ("next day", BLUE)):
        s = m[m.dte == lab].groupby("ts").flow.sum().reindex(spy.index).fillna(0).cumsum() / 1e6
        b.plot(s.index, s, color=col, lw=1.6, label=f"{lab} options")
    tot = m.groupby("ts").flow.sum().reindex(spy.index).fillna(0).cumsum() / 1e6
    b.plot(tot.index, tot, color=INK, lw=2, label="total")
    b.axhline(0, color=MUTED, lw=0.8)
    b.set_ylabel("cumulative net delta\nbought, M SPY shares")
    b.legend(loc="lower left", frameon=False, fontsize=8)
    w = pd.Timedelta(minutes=BUCKET * 0.8)
    b5 = B.flow / 1e6
    c.bar(B.index + pd.Timedelta(minutes=BUCKET / 2), b5, width=w, color=np.where(b5 >= 0, GREEN, ORANGE), alpha=0.8)
    c.axhline(0, color=MUTED, lw=0.8)
    c.set_ylabel(f"net delta bought\nper {BUCKET} min, M shares")
    c.set_title(f"Flow leads the next {BUCKET} minutes? corr {res['H1 flow leads next bucket: corr']:+.2f}, p {res['H1 p (one-sided)']:.2f}.   "
                f"Same {BUCKET} minutes: corr {res['H2 same bucket: corr']:+.2f}, p {res['H2 p (one-sided)']:.2f}  ({res['buckets']} buckets)",
                loc="left", fontsize=9.5, color=INK)
    import matplotlib.dates as mdates
    c.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    f.savefig(OUT / "flow_today.png", dpi=140, bbox_inches="tight", facecolor=SURF)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    spy = bars()
    m = minute_flow(spy)
    fl = m.groupby("ts").flow.sum().reindex(spy.index).fillna(0)
    B, res = tests(fl, spy)
    res["contract-minutes signed"] = int(len(m))
    res["share of volume printed above mid"] = float((m.volume * (m.s > 0)).sum() / m.volume.sum())
    res["0DTE share of signed volume"] = float(m[m.dte == "0DTE"].volume.sum() / m.volume.sum())
    B.to_csv(OUT / "flow_buckets.csv")
    (OUT / "flow.json").write_text(json.dumps(res, indent=1))
    figure(spy, m, B, res)
    print(json.dumps(res, indent=1))
