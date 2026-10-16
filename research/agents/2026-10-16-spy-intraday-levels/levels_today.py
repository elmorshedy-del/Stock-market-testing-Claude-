"""One-day test (design in README.md, pre-registered at c0dc8e6): did SPY's Oct 16 intraday turns land on the
option-inferred levels (top-gamma strikes, call/put walls, flip) more than equally round strikes at the same distance?
Usage: OMP_NUM_THREADS=1 python levels_today.py [--k 10] -> out/levels.json, out/turns.csv, out/levels_today.png
Needs: data/SPY_1m.json (Yahoo 1-minute bars, fetched by the command in README) and the Oct 16 SPY OI pulled by
research/microstructure/tsla_live.pull_oi into research/microstructure/data/thetadata/."""
import json
import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT, DATA = HERE / "out", HERE / "data"
MICRO = HERE.parents[1] / "microstructure"
ENGINE = HERE.parents[2] / "engines" / "gamma"
sys.path.insert(0, str(MICRO))
os.chdir(MICRO)
import td_gamma as t                               # noqa: E402  (originals, imported unchanged)
from options_flow import exposures, gex_profile    # noqa: E402
from tsla_live import pull_oi                      # noqa: E402

DAY, PREV_CLOSE = pd.Timestamp("2026-10-16"), 771.79
BAND, NTOP, NSIM = 0.03, 5, 2000
K = int(sys.argv[sys.argv.index("--k") + 1]) if "--k" in sys.argv else 10
RNG = np.random.default_rng(20261016)
BLUE, ORANGE, GREEN, INK, MUTED, GRID, SURF = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"


def option_map():
    eod, oi = t.read("SPY", "eod"), t.read("SPY", "oi")
    d0 = eod.date.max()
    e = eod[eod.date == d0].copy()
    e["mid"] = (e.bid + e.ask) / 2
    key = ["expiration", "strike", "cp"]
    o0 = oi[oi.date == oi.date.max()].rename(columns={"open_interest": "oi"})
    g0 = t.chain_day(e.merge(o0[["date"] + key + ["oi"]], on=["date"] + key, how="left").fillna({"oi": 0}))
    n = pull_oi("SPY", DAY)                        # cached file: positions at the Oct 15 close
    n["expiration"] = pd.to_datetime(n.expiration)
    n["cp"] = np.where(n.right.str.upper().str.startswith("C"), "C", "P")
    g = g0.merge(n.rename(columns={"open_interest": "oi_new"})[key + ["oi_new"]], on=key, how="inner")
    g["oi"] = g.oi_new
    g = g[(g.expiration >= DAY) & (g.oi > 0)].copy()
    g["date"], g["T"] = DAY, ((g.expiration - DAY).dt.days / 365).clip(lower=1 / (365 * 24))
    g["underlying_close"] = PREV_CLOSE
    ex = exposures(g, PREV_CLOSE, "classic")
    by = ex.groupby("K").gex.sum()
    lo, hi = PREV_CLOSE * (1 - BAND), PREV_CLOSE * (1 + BAND)
    near = by[(by.index >= lo) & (by.index <= hi)]
    top = list(near.abs().sort_values(ascending=False).index[:NTOP])
    g45 = g[(g.expiration - DAY).dt.days <= 45]
    w = g45[(g45.K >= lo) & (g45.K <= hi)].groupby(["cp", "K"]).oi.sum()
    call_wall, put_wall = float(w["C"].idxmax()), float(w["P"].idxmax())
    grid, tot, flips = gex_profile(g, PREV_CLOSE, "classic", lo=0.95, hi=1.05, n=401)
    flip = float(min(flips, key=lambda f: abs(f - PREV_CLOSE))) if flips else np.nan
    levels = sorted(set([float(k) for k in top] + [call_wall, put_wall] + ([float(round(flip))] if flip == flip else [])))
    strikes = np.array(sorted(by.index[(by.index >= lo) & (by.index <= hi)]))
    info = {"eod_chain_date": str(d0.date()), "oi_date": str(DAY.date()), "top_gamma_strikes": [float(k) for k in top],
            "top_gamma_values_$M_per_1pct": {str(k): round(float(by[k]) / 1e6, 1) for k in top},
            "call_wall": call_wall, "put_wall": put_wall, "flip_with_expiring": flip, "levels": levels,
            "expiring_today_share_of_abs_gamma": float(ex[ex.exp == DAY.date()].gex.abs().sum() / ex.gex.abs().sum())}
    return info, strikes, by, grid, tot


def bars():
    d = json.loads((DATA / "SPY_1m.json").read_text())["chart"]["result"][0]
    q = d["indicators"]["quote"][0]
    idx = pd.to_datetime(d["timestamp"], unit="s", utc=True).tz_convert("America/New_York").tz_localize(None)
    b = pd.DataFrame({k: q[k] for k in ("open", "high", "low", "close", "volume")}, index=idx).dropna()
    return b[(b.index.time >= pd.Timestamp("09:30").time()) & (b.index.time < pd.Timestamp("16:00").time())]


def turns(b, k):
    hi, lo = b.high.to_numpy(), b.low.to_numpy()
    rows = []
    for i in range(len(b)):
        a, z = max(0, i - k), min(len(b), i + k + 1)
        if i - k < 0 or i + k >= len(b):
            continue
        if hi[i] == hi[a:z].max():
            rows.append((b.index[i], "high", hi[i]))
        if lo[i] == lo[a:z].min():
            rows.append((b.index[i], "low", lo[i]))
    rows += [(b.high.idxmax(), "high", b.high.max()), (b.low.idxmin(), "low", b.low.min())]
    T = pd.DataFrame(rows, columns=["time", "kind", "price"]).drop_duplicates(subset=["time", "kind"]).sort_values("time")
    return T.reset_index(drop=True)


def roundness(k):
    return 2 if k % 10 == 0 else (1 if k % 5 == 0 else 0)


def test(T, levels, strikes):
    lv = np.array(levels)
    dist = lambda L: np.median(np.min(np.abs(T.price.to_numpy()[:, None] - np.asarray(L)[None, :]), axis=1))
    obs = dist(lv)
    dd = np.abs(strikes - PREV_CLOSE)
    dec = pd.qcut(dd, 10, labels=False, duplicates="drop")
    rc = np.array([roundness(k) for k in strikes])
    pools = {}
    for L in lv:
        i = int(np.argmin(np.abs(strikes - L)))
        m = (rc == rc[i]) & (dec == dec[i])
        pools[L] = strikes[m] if m.sum() > 1 else strikes[rc == rc[i]]
    null = np.array([dist([RNG.choice(pools[L]) for L in lv]) for _ in range(NSIM)])
    return {"turns": int(len(T)), "median_distance_obs": float(obs), "null_median_of_median_distance": float(np.median(null)),
            "p_one_sided": float((null <= obs).mean())}, null


def figure(b, T, info, res, null):
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                         "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
    f, (ax, an) = plt.subplots(1, 2, figsize=(15, 6.2), gridspec_kw={"width_ratios": [3, 1], "wspace": 0.10})
    x = np.arange(len(b))
    lo, hi = min(b.low.min(), min(info["levels"])), max(b.high.max(), max(info["levels"]))
    ylo, yhi = max(lo - 1.5, b.low.min() - 6), min(hi + 1.5, b.high.max() + 6)
    ax.vlines(x, b.low, b.high, color=MUTED, lw=0.6, alpha=0.7)
    ax.plot(x, b.close, color=INK, lw=1.2)
    for L in info["levels"]:
        lab = []
        if L in info["top_gamma_strikes"]:
            lab.append(f"top gamma ({info['top_gamma_values_$M_per_1pct'][str(L)]:+.0f}M)")
        if L == info["call_wall"]:
            lab.append("call wall")
        if L == info["put_wall"]:
            lab.append("put wall")
        if info["flip_with_expiring"] == info["flip_with_expiring"] and L == float(round(info["flip_with_expiring"])):
            lab.append("flip")
        col = ORANGE if "flip" in lab else (GREEN if "call wall" in lab else (BLUE if "put wall" in lab else MUTED))
        ax.axhline(L, color=col, lw=1.1, ls="--", alpha=0.85)
        if ylo <= L <= yhi:
            ax.text(318, L + 0.15, f"{L:.0f}  " + ", ".join(lab), va="center", fontsize=7.5, color=col)
    pos = {tm: i for i, tm in enumerate(b.index)}
    for _, r in T.iterrows():
        ax.scatter([pos[r.time]], [r.price], s=26, color=GREEN if r.kind == "low" else ORANGE, zorder=5, edgecolor=INK, lw=0.4)
    ticks = [i for i, tm in enumerate(b.index) if tm.minute == 0]
    ax.set_xticks(ticks, [b.index[i].strftime("%H:%M") for i in ticks])
    ax.set_xlim(-2, 390)                                   # the full session, so the open part of the day shows
    ax.set_ylim(ylo, yhi)
    off = [f"{L:.0f}" for L in info["levels"] if not ylo <= L <= yhi]
    if off:
        ax.text(2, ylo + 0.3, "levels off the chart: " + ", ".join(off), fontsize=7.5, color=MUTED)
    ax.set_ylabel("SPY")
    ax.set_title(f"SPY Oct 16, 1-minute bars to {b.index[-1]:%H:%M}. Dots = turns ({K}-minute window). Dashed = levels from options known before the open",
                 loc="left", fontsize=9.5, color=INK)
    an.hist(null, bins=40, color=MUTED, alpha=0.6)
    an.axvline(res["median_distance_obs"], color=ORANGE, lw=2)
    an.set_xlabel("median $ distance, turn to nearest level")
    an.set_title(f"Luck check: option levels vs\nequally round strikes at the same distance\nobserved {res['median_distance_obs']:.2f} vs luck {res['null_median_of_median_distance']:.2f}, p {res['p_one_sided']:.2f}",
                 loc="left", fontsize=9.5, color=INK)
    an.set_yticks([])
    f.savefig(OUT / f"levels_today_k{K}.png", dpi=145, bbox_inches="tight", facecolor=SURF)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    info, strikes, by, grid, tot = option_map()
    b = bars()
    T = turns(b, K)
    res, null = test(T, info["levels"], strikes)
    T["nearest level"] = [min(info["levels"], key=lambda L: abs(L - p)) for p in T.price]
    T["distance $"] = (T.price - T["nearest level"]).abs().round(2)
    T.to_csv(OUT / f"turns_k{K}.csv", index=False)
    (OUT / f"levels_k{K}.json").write_text(json.dumps({"map": info, "test": res, "bars_to": str(b.index[-1]), "window_minutes": K}, indent=1, default=float))
    figure(b, T, info, res, null)
    print(json.dumps(info, indent=1, default=float))
    print(T.to_string(index=False))
    print(res)
