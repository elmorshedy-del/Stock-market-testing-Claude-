"""Does SpaceX (SPCX) lead TSLA? The tests pre-registered in README.md (D0, H1, H2, H2r, H3).
Fetches Yahoo bars into data/ (gitignored) unless they are already there; writes out/results.json and out/spcx_tsla.png.
Usage: python spcx_lead.py [--refetch]
"""
import json
import sys
import urllib.request
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).parent
DATA, OUT = HERE / "data", HERE / "out"
SYMS = ("SPCX", "TSLA", "QQQ")
START, END = "2026-06-12", "2026-10-15"          # END inclusive: the last close before this study
ALPHA = 0.05 / 3
C_TSLA, C_SPCX, INK, MUTED, GRID, SURF = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"


def fetch(sym, interval, rng):
    path = DATA / f"{sym}_{interval}.json"
    if path.exists() and "--refetch" not in sys.argv:
        return json.loads(path.read_text())
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range={rng}&interval={interval}&includePrePost=false"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    raw = urllib.request.urlopen(req, timeout=30).read()
    DATA.mkdir(exist_ok=True)
    path.write_bytes(raw)
    return json.loads(raw)


def bars(sym, interval, rng):
    d = fetch(sym, interval, rng)["chart"]["result"][0]
    idx = pd.to_datetime(d["timestamp"], unit="s", utc=True).tz_convert("America/New_York")
    c = pd.Series(d["indicators"]["quote"][0]["close"], index=idx, dtype=float).dropna()
    return c[~c.index.duplicated(keep="last")]


def resid(y, X):
    X = np.column_stack([np.ones(len(y)), X])
    return y - X @ np.linalg.lstsq(X, y, rcond=None)[0]


def pcorr(y, x, ctrl):
    ok = np.isfinite(y) & np.isfinite(x) & np.isfinite(ctrl).all(axis=1)
    if ok.sum() < 10:
        return np.nan
    return float(np.corrcoef(resid(y[ok], ctrl[ok]), resid(x[ok], ctrl[ok]))[0, 1])


def pval(obs, null):
    null = np.asarray([v for v in null if np.isfinite(v)])
    return float((np.sum(np.abs(null) >= abs(obs)) + 1) / (len(null) + 1)), len(null)


def daily():
    c = pd.concat({s: bars(s, "1d", "1y") for s in SYMS}, axis=1)
    c.index = c.index.normalize().tz_localize(None)
    c = c.loc[START:END].dropna()
    return np.log(c).diff().dropna(), c


def intraday():
    c = pd.concat({s: bars(s, "5m", "60d") for s in SYMS}, axis=1)
    c = c[(c.index.time >= pd.Timestamp("09:30").time()) & (c.index.time < pd.Timestamp("16:00").time())]
    c = c[c.index.normalize().tz_localize(None) <= pd.Timestamp(END)].dropna()
    r = np.log(c).groupby(c.index.date).diff()                      # within-session returns; the overnight gap is dropped
    r["day"], r["slot"] = r.index.date, (r.index.hour * 60 + r.index.minute - 570) // 5
    r = r.dropna()
    days = sorted(r.day.unique())
    cube = {s: r.pivot_table(index="day", columns="slot", values=s).reindex(index=days, columns=range(1, 78)).to_numpy() for s in SYMS}
    return cube, days


def lead_stat(cube, lead, lag_sym, shift=0):
    """Partial corr of lag_sym's next bar with lead's current bar, controlling for lag_sym's and QQQ's current bar.
    shift>0 pairs lead's session d with the others' session d+shift (null)."""
    L = np.roll(cube[lead], shift, axis=0)
    y, own, mkt = cube[lag_sym][:, 1:], cube[lag_sym][:, :-1], cube["QQQ"][:, :-1]
    x = L[:, :-1]
    return pcorr(y.ravel(), x.ravel(), np.column_stack([own.ravel(), mkt.ravel()]))


def main():
    OUT.mkdir(exist_ok=True)
    r, c = daily()
    n = len(r)
    res = {"daily returns": n, "first": str(r.index[0].date()), "last": str(r.index[-1].date())}

    # D0 description
    res["D0"] = {"same-day corr SPCX-TSLA": float(r.SPCX.corr(r.TSLA)),
                 "same-day partial corr SPCX-TSLA ex QQQ": pcorr(r.TSLA.to_numpy(), r.SPCX.to_numpy(), r[["QQQ"]].to_numpy()),
                 "same-day corr TSLA-QQQ": float(r.TSLA.corr(r.QQQ)), "same-day corr SPCX-QQQ": float(r.SPCX.corr(r.QQQ)),
                 "beta TSLA on SPCX": float(np.polyfit(r.SPCX, r.TSLA, 1)[0])}
    roll = r.SPCX.rolling(20).corr(r.TSLA)

    # H1 daily lead
    y, x = r.TSLA.shift(-1).to_numpy(), r.SPCX.to_numpy()
    ctrl = r[["TSLA", "QQQ"]].to_numpy()
    obs = pcorr(y, x, ctrl)
    null = [pcorr(y, np.roll(x, k), ctrl) for k in range(10, n - 9)]
    p, m = pval(obs, null)
    res["H1 daily lead"] = {"partial corr": obs, "p": p, "null draws": m, "n": int(np.isfinite(y).sum())}

    # H2 / H2r intraday lead
    cube, days = intraday()
    D = len(days)
    for name, lead, lag in (("H2 intraday SPCX leads TSLA", "SPCX", "TSLA"), ("H2r intraday TSLA leads SPCX", "TSLA", "SPCX")):
        obs = lead_stat(cube, lead, lag)
        null = [lead_stat(cube, lead, lag, k) for k in range(1, D)]
        p, m = pval(obs, null)
        yv, xv = cube[lag][:, 1:].ravel(), cube[lead][:, :-1].ravel()
        ok = np.isfinite(yv) & np.isfinite(xv)
        slope = np.polyfit(xv[ok], yv[ok], 1)[0]
        res[name] = {"partial corr": obs, "p": p, "null draws": m, "bar pairs": int(ok.sum()), "sessions": D,
                     "share of next-bar variance explained %": 100 * obs ** 2,
                     "next-bar move per 1 sd lead move (bp)": float(1e4 * slope * np.nanstd(xv)),
                     "sd of next-bar move (bp)": float(1e4 * np.nanstd(yv))}
    same = np.corrcoef(*[np.nan_to_num(cube[s].ravel()) for s in ("SPCX", "TSLA")])[0, 1]
    res["D0"]["same-bar 5-min corr SPCX-TSLA"] = float(same)
    prof = {}
    for lag in range(-6, 7):                                       # simple cross-correlation profile for the figure
        a, b = cube["SPCX"], cube["TSLA"]
        if lag > 0:
            u, v = a[:, :-lag], b[:, lag:]
        elif lag < 0:
            u, v = a[:, -lag:], b[:, :lag]
        else:
            u, v = a, b
        u, v = u.ravel(), v.ravel()
        ok = np.isfinite(u) & np.isfinite(v)
        prof[lag] = float(np.corrcoef(u[ok], v[ok])[0, 1])
    band = []
    for k in range(1, D):
        u, v = np.roll(cube["SPCX"], k, axis=0)[:, :-1].ravel(), cube["TSLA"][:, 1:].ravel()
        ok = np.isfinite(u) & np.isfinite(v)
        band.append(np.corrcoef(u[ok], v[ok])[0, 1])
    band = float(np.quantile(np.abs(band), 0.95))

    # H3 catch-up
    lc = np.log(c)
    gap = ((lc.SPCX - lc.SPCX.shift(5)) - (lc.TSLA - lc.TSLA.shift(5)))
    fwd = lc.TSLA.shift(-5) - lc.TSLA
    j = pd.concat([gap, fwd], axis=1, keys=["gap", "fwd"]).dropna()
    g, f = j.gap.to_numpy(), j.fwd.to_numpy()
    obs = float(np.corrcoef(g, f)[0, 1])
    null = [np.corrcoef(np.roll(g, k), f)[0, 1] for k in range(10, len(g) - 9)]
    p, m = pval(obs, null)
    res["H3 catch-up"] = {"corr": obs, "p": p, "null draws": m, "n (overlapping)": len(g)}

    res["usable signal"] = {k: res[k]["p"] < ALPHA for k in ("H1 daily lead", "H2 intraday SPCX leads TSLA", "H3 catch-up")}
    (OUT / "results.json").write_text(json.dumps(res, indent=1, default=float))
    figure(c, roll, prof, band, res)
    return res


def figure(c, roll, prof, band, res):
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                         "axes.grid": True, "grid.color": GRID, "axes.spines.top": False, "axes.spines.right": False,
                         "figure.facecolor": SURF, "axes.facecolor": SURF, "legend.frameon": False})
    f = plt.figure(figsize=(14, 8.6))
    gs = f.add_gridspec(2, 2, height_ratios=[1.25, 1], hspace=0.45, wspace=0.22)
    a, b, d = f.add_subplot(gs[0, :]), f.add_subplot(gs[1, 0]), f.add_subplot(gs[1, 1])
    idx = 100 * c / c.iloc[0]
    for s, col in (("TSLA", C_TSLA), ("SPCX", C_SPCX)):
        a.plot(idx.index, idx[s], color=col, lw=2, label=s)
        a.annotate(f"{s} {idx[s].iloc[-1]:.0f}", (idx.index[-1], idx[s].iloc[-1]), xytext=(6, 0), textcoords="offset points",
                   va="center", fontsize=9, color=INK)
    a.set_ylabel(f"price, {c.index[0]:%b %d} = 100")
    a.legend(loc="lower left")
    D0 = res["D0"]
    a.set_title(f"Similar path since the IPO (price-level corr {c.SPCX.corr(c.TSLA):.2f}), but daily moves are only weakly linked: "
                f"{D0['same-day corr SPCX-TSLA']:.2f}, and {D0['same-day partial corr SPCX-TSLA ex QQQ']:.2f} after removing the Nasdaq "
                f"(TSLA vs QQQ {D0['same-day corr TSLA-QQQ']:.2f})", loc="left", color=INK, fontsize=10)
    b.plot(roll.index, roll, color=INK, lw=2)
    b.axhline(0, color=MUTED, lw=0.8)
    b.set_ylim(-1, 1)
    b.set_title(f"Same-day correlation, 20-day rolling: low until mid-September, about {roll.iloc[-1]:.1f} since", loc="left", color=INK, fontsize=10)
    lags = sorted(prof)
    d.bar(lags, [prof[k] for k in lags], color=[C_SPCX if k > 0 else (C_TSLA if k < 0 else MUTED) for k in lags], width=0.7)
    d.axhspan(-band, band, color=MUTED, alpha=0.15, lw=0)
    d.set_xticks(lags)
    d.set_xlabel("lag in 5-minute bars  (right: SPCX first, then TSLA · left: TSLA first)")
    h2, h2r = res["H2 intraday SPCX leads TSLA"], res["H2r intraday TSLA leads SPCX"]
    d.set_title(f"Intraday: only the same bar is large; 5-min leads p {h2['p']:.2f} (SPCX first), {h2r['p']:.2f} (TSLA first)\n"
                "shaded: 95% band when sessions are mismatched", loc="left", color=INK, fontsize=10)
    for ax in (a, b, d):
        ax.set_axisbelow(True)
    for ax in (a, b):
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b %d"))
    h1, h3 = res["H1 daily lead"], res["H3 catch-up"]
    f.suptitle(f"Does SPCX lead TSLA?  Daily lead p {h1['p']:.2f}, catch-up after a gap p {h3['p']:.2f}, "
               f"5-min lead p {h2['p']:.2f}  (usable only if p < {ALPHA:.3f})", x=0.01, ha="left", fontsize=11, color=INK, weight="bold")
    f.savefig(OUT / "spcx_tsla.png", dpi=150, bbox_inches="tight", facecolor=SURF)


if __name__ == "__main__":
    print(json.dumps(main(), indent=1, default=lambda v: round(float(v), 4)))
