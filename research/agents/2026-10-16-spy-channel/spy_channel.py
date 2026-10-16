"""The owner's SPY daily channel (screenshot, Oct 16 2026) against S&P dealer gamma, VIX and the Q4 record.
Descriptive (README.md). Lines are read from the screenshot's pixels, not by eye.
Usage: OMP_NUM_THREADS=1 python spy_channel.py -> out/lines.json, out/touches.csv, out/q4.csv, out/spy_channel.png
Fresh bars: data/SPY_1d.json, data/VIX_1d.json (Yahoo) and data/DIX.csv (SqueezeMetrics); the committed copies
in research/microstructure/data are used if these are missing (data/ is gitignored, see README for the fetch commands)."""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

HERE = Path(__file__).resolve().parent
OUT, DATA = HERE / "out", HERE / "data"
MICRO = HERE.parents[1] / "microstructure"
sys.path.insert(0, str(MICRO))
from common import load_bars                       # noqa: E402  (originals, imported unchanged)

SHOT = DATA / "owner_spy_channel_screenshot.png"
# axis calibration read off the screenshot: gridline rows (price labels) and month-label columns (first bar of the month)
GRID_Y = {404: 860, 548: 840, 695: 820, 846: 800, 1001: 780, 1159: 760, 1322: 740, 1447: 725, 1575: 710, 1679: 698,
          1785: 686, 1893: 674, 1984: 664, 2077: 654, 2171: 644, 2267: 634, 2359: 624.5}
MONTH_X = {"2026-05-01": 213, "2026-07-01": 474, "2026-09-01": 746, "2026-11-02": 1019}
HOLIDAYS = ["2026-11-26", "2026-12-25"]
LAST_CLOSE = pd.Timestamp("2026-10-15")            # Oct 16 is intraday in the fresh bars; stats use closes to here
REPORTS_2024_2025 = (0.2331, 0.1636)              # SPY price return 2024, 2025 (computed below and checked)
BLUE, ORANGE, GREEN, INK, MUTED, GRID, SURF, CHAN = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb", "#3b5bdb"


def bars(name, fallback):
    p = DATA / f"{name}_1d.json"
    if not p.exists():
        return load_bars(fallback)
    d = json.loads(p.read_text())["chart"]["result"][0]
    q = d["indicators"]["quote"][0]
    idx = pd.to_datetime(d["timestamp"], unit="s", utc=True).tz_convert("America/New_York").normalize().tz_localize(None)
    df = pd.DataFrame({k: q[k] for k in ("open", "high", "low", "close")}, index=idx).dropna()
    return df[~df.index.duplicated(keep="last")]


def detect_lines():
    """Blue pixels of the three drawn lines -> three straight lines in pixel space (top to bottom: upper, mid, lower)."""
    im = np.asarray(Image.open(SHOT).convert("RGB")).astype(int)
    R, G, B = im[..., 0], im[..., 1], im[..., 2]
    blue = (B > 200) & (R < 110) & (G < 130) & (B - R > 120)
    pts = {0: [], 1: [], 2: []}
    for x in range(30, 1106):
        col = np.nonzero(blue[600:2250, x])[0] + 600
        runs, start = [], None
        for i, y in enumerate(col):
            start = y if start is None else start
            if i == len(col) - 1 or col[i + 1] != y + 1:
                if y - start >= 6:
                    runs.append((start + y) / 2)
                start = None
        if len(runs) == 3:
            for k, yc in enumerate(sorted(runs)):
                pts[k].append((x, yc))
    fits = {}
    for k, name in enumerate(("upper", "mid", "lower")):
        a = np.array(pts[k])
        m, c = np.polyfit(a[:, 0], a[:, 1], 1)
        fits[name] = {"slope": m, "intercept": c, "columns": len(a), "resid_sd_px": float((a[:, 1] - (m * a[:, 0] + c)).std())}
    gy, gp = np.array(list(GRID_Y)), np.array(list(GRID_Y.values()))
    b1, b0 = np.polyfit(gy, np.log(gp), 1)
    cal = {"log_slope": b1, "log_icpt": b0, "max_err_pct_log": float(100 * np.abs(np.exp(b1 * gy + b0) / gp - 1).max()),
           "max_err_pct_linear": float(100 * np.abs(np.polyval(np.polyfit(gy, gp, 1), gy) / gp - 1).max())}
    return fits, cal


def frame():
    fits, cal = detect_lines()
    spy = bars("SPY", "SPY")
    idx = spy.index[(spy.index >= "2026-03-01") & (spy.index <= LAST_CLOSE)]
    fut = pd.bdate_range(LAST_CLOSE + pd.Timedelta(days=1), "2026-12-31")
    fut = fut[~fut.isin(pd.to_datetime(HOLIDAYS))]
    allidx = idx.append(fut)
    bi = np.array([allidx.get_loc(pd.Timestamp(d)) for d in MONTH_X])
    px_per_bar, x0 = np.polyfit(bi, np.array(list(MONTH_X.values())), 1)
    cal["px_per_bar"], cal["month_label_resid_px"] = px_per_bar, (np.array(list(MONTH_X.values())) - (x0 + px_per_bar * bi)).round(2).tolist()
    X = x0 + px_per_bar * np.arange(len(allidx))
    L = pd.DataFrame({k: np.exp(cal["log_slope"] * (f["slope"] * X + f["intercept"]) + cal["log_icpt"]) for k, f in fits.items()}, index=allidx)
    D = spy.loc[idx, ["high", "low", "close"]].join(L)
    D = D[D.index >= D.index[D.close >= D.lower][0]]          # from the first close inside the channel
    D["pos"] = np.log(D.close / D.lower) / np.log(D.upper / D.lower)
    dix = pd.read_csv(DATA / "DIX.csv" if (DATA / "DIX.csv").exists() else MICRO / "data" / "DIX.csv", parse_dates=["date"]).set_index("date")
    pct = lambda s: s.rolling(252).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True)       # same ranking as forecast.build
    dix["gex_pct"], dix["dix_pct"] = pct(dix.gex), pct(dix.dix)
    vix = bars("VIX", "^VIX").close.rename("VIX")
    g = pd.read_csv(MICRO / "out" / "td_gamma_SPY.csv", parse_dates=["date"]).set_index("date")
    D = D.join(dix[["gex_pct", "dix_pct"]]).join(vix).join(g[["flip_classic"]])
    D["vs_flip"] = 100 * (D.close / D.flip_classic - 1)
    return D, L, spy, vix, dix, fits, cal


def touches(D):
    """A touch: the day's low at or under the lower line, after a close at or above the mid line (or the first day)."""
    eps, armed = [], True
    for t, r in D.iterrows():
        armed = armed or r.close >= r["mid"]
        if r.low <= r.lower and armed:
            eps.append(t)
            armed = False
    rows = []
    for k, t in enumerate(eps):
        end = eps[k + 1] if k + 1 < len(eps) else D.index[-1] + pd.Timedelta(days=1)
        w = D[(D.index >= t) & (D.index < end)]
        hit = w[w.high >= w.upper]
        r = D.loc[t]
        rows.append({"first touch": t.date(), "close": round(r.close, 2), "S&P GEX pct": r.gex_pct, "lowest GEX pct, first 5 sessions": D.gex_pct.loc[t:].iloc[:5].min(),
                     "VIX": r.VIX, "DIX pct": r.dix_pct, "SPY vs own flip %": r.vs_flip,
                     "reached the upper line": hit.index[0].date() if len(hit) else None,
                     "sessions to the upper line": D.index.get_loc(hit.index[0]) - D.index.get_loc(t) if len(hit) else None,
                     "highest channel position before the next touch": w.pos.max(), "sessions in episode": len(w), "ongoing": k == len(eps) - 1})
    return pd.DataFrame(rows)


def q4(spy):
    x = load_bars("^GSPC").close
    rows = []
    for y in range(1971, 2026):
        a, e, p = x[:f"{y}-10-16"].iloc[-1], x[str(y)].iloc[-1], x[:f"{y - 1}-12-31"].iloc[-1]
        rows.append({"year": y, "Oct 16 to Dec 31 %": 100 * (e / a - 1), "YTD at Oct 16 %": 100 * (a / p - 1), "midterm": (y - 1970) % 4 == 0})
    Q = pd.DataFrame(rows).set_index("year")
    long = load_bars("SPY").close                          # committed long history for the 2023-2025 year-ends
    ye = long.groupby(long.index.year).last()
    ret = {y: ye[y] / ye[y - 1] - 1 for y in (2024, 2025)}
    assert all(abs(ret[y] - v) < 0.002 for y, v in zip((2024, 2025), REPORTS_2024_2025))
    return Q, ye, ret


def figure(D, L, spy, vix, dix, T, Q, ye, ret):
    """Plotted on a trading-day axis, as TradingView draws it, so the lines stay straight."""
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                         "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
    f = plt.figure(figsize=(16, 15.5))
    gs = f.add_gridspec(4, 1, height_ratios=[3.3, 1.1, 0.9, 1.5], hspace=0.24)
    ax, ag, av, aq = (f.add_subplot(gs[i]) for i in range(4))
    now_t, now_p = spy.index[-1], spy.close.iloc[-1]
    Lf = L[L.index >= D.index[0]]
    X = lambda idx: Lf.index.get_indexer(pd.DatetimeIndex(idx))          # date -> trading-day position
    xd, xe, xn = X(D.index), len(Lf) - 1, X([now_t])[0]
    for k, lw in (("upper", 2.2), ("mid", 1.5), ("lower", 2.2)):
        i0 = X([LAST_CLOSE])[0]
        ax.plot(np.arange(i0 + 1), Lf[k].iloc[:i0 + 1], color=CHAN, lw=lw, alpha=0.8)
        ax.plot(np.arange(i0, xe + 1), Lf[k].iloc[i0:], color=CHAN, lw=lw, alpha=0.8, ls=(0, (5, 3)))
        ax.text(xe + 2, Lf[k].iloc[-1], f"{k}  ${Lf[k].iloc[-1]:.0f}  ({100 * (Lf[k].iloc[-1] / ye[2025] - 1):+.1f}% on the year)",
                va="center", fontsize=8.5, color=CHAN)
    fl = D.flip_classic.rolling(3, center=True, min_periods=1).median()
    ok = fl.notna().to_numpy()
    ax.fill_between(xd, D.close, fl, where=ok & (D.close < fl).to_numpy(), interpolate=True, color=BLUE, alpha=0.28, lw=0)
    ax.fill_between(xd, D.close, fl, where=ok & (D.close >= fl).to_numpy(), interpolate=True, color=ORANGE, alpha=0.14, lw=0)
    ax.plot(xd[ok], fl[ok], color=ORANGE, lw=1.6)
    ax.vlines(xd, D.low, D.high, color=MUTED, lw=0.8, alpha=0.6)
    ax.plot(xd, D.close, color=INK, lw=1.8)
    ax.plot([xd[-1], xn], [D.close.iloc[-1], now_p], color=INK, lw=1.8, ls=":")
    ax.scatter([xn], [now_p], s=30, color=INK, zorder=6)
    ax.text(xn + 1.5, now_p * 1.006, f"Oct 16 ${now_p:.0f}\n(intraday)", ha="left", va="bottom", fontsize=8, color=INK)
    for _, r in T.iterrows():
        t = pd.Timestamp(r["first touch"])
        col = GREEN if r["reached the upper line"] is not None else (INK if r.ongoing else MUTED)
        ax.scatter(X([t]), [D.low.loc[t]], s=60, color=col, zorder=6, edgecolor=INK, lw=0.6)
        ax.text(X([t])[0], D.low.loc[t] * 0.989, f"GEX pct {r['S&P GEX pct']:.2f}\nVIX {r.VIX:.1f}", ha="center", va="top", fontsize=7.5, color=INK)
    Qs = Q["Oct 16 to Dec 31 %"]
    for qq, dx, col in ((Qs, -6, MUTED), (Qs[Q["YTD at Oct 16 %"] > 0], -2, GREEN)):
        lo, md, hi = (now_p * (1 + qq.quantile(p) / 100) for p in (0.25, 0.5, 0.75))
        ax.vlines(xe + dx, lo, hi, color=col, lw=5, alpha=0.6)
        ax.scatter([xe + dx], [md], color=INK, s=40, zorder=6, marker="_")
    ax.text(xe - 4, now_p * (1 + Qs.quantile(0.25) / 100) * 0.994, "Q4 record from today's price:\nmiddle half of years, dash = median\n(grey all years, green up-years)",
            ha="center", va="top", fontsize=7.5, color=MUTED)
    for y, r in ret.items():
        lvl = ye[2025] * (1 + r)
        ax.hlines(lvl, X([LAST_CLOSE])[0], xe, color=MUTED, lw=0.8, ls=":")
        ax.text(X([LAST_CLOSE])[0] + 2, lvl * 1.002, f"a {y}-like year ({100 * r:+.1f}%): ${lvl:.0f}", fontsize=8, color=MUTED, va="bottom")
    ax.set_yscale("log")
    ax.set_yticks([700, 725, 750, 775, 800, 825, 850], ["700", "725", "750", "775", "800", "825", "850"])
    ax.minorticks_off()
    ax.set_ylim(682, 860)
    ax.set_ylabel("SPY (log)")
    ax.set_title("Your SPY channel (read from the screenshot's pixels). Dots = touches of the lower line: green went on to the upper line, grey did not. "
                 "Orange = SPY's own gamma flip (to Oct 9)", loc="left", fontsize=9.5, color=INK)
    gp, dp = dix.gex_pct.reindex(Lf.index), dix.dix_pct.reindex(Lf.index)
    xi = np.arange(len(Lf))
    ag.axhspan(0, 0.2, color=BLUE, alpha=0.12, lw=0)
    ag.plot(xi, gp, color=INK, lw=1.5, label="S&P dealer gamma (GEX), percentile of its year")
    ag.plot(xi, dp, color=GREEN, lw=1, alpha=0.8, label="dark-pool buying (DIX), percentile")
    ag.set_ylim(0, 1)
    ag.set_ylabel("percentile")
    ag.text(xe + 2, 0.1, "bottom fifth: tested 24% chance of a\ntop-decile 10-day rally vs 10% base (4d)", fontsize=8, color=BLUE, va="center")
    ag.legend(loc="lower left", bbox_to_anchor=(0, 1.0), frameon=False, fontsize=8, ncol=2)
    av.plot(xi, vix.reindex(Lf.index), color=INK, lw=1.4)
    av.set_ylabel("VIX")
    months = Lf.index.to_series().groupby(Lf.index.to_period("M")).first()
    for axx in (ax, ag, av):
        axx.set_xlim(-2, xe + 48)
        axx.set_xticks(X(months.values), [d.strftime("%b") for d in months])
        axx.grid(axis="x", color=GRID, lw=0.6)
    for axx in (ax, ag):
        axx.tick_params(labelbottom=False)
    groups = [("all years 1971-2025", Qs), ("S&P up on the year at Oct 16", Qs[Q["YTD at Oct 16 %"] > 0]),
              ("midterm years (2026 is one)", Qs[Q.midterm]), ("1990-2025", Qs[Qs.index >= 1990])]
    for i, (lab, qq) in enumerate(groups[::-1]):
        aq.hlines(i, qq.quantile(0.25), qq.quantile(0.75), color=MUTED, lw=7, alpha=0.5)
        aq.hlines(i, qq.quantile(0.1), qq.quantile(0.9), color=MUTED, lw=1.2)
        aq.scatter([qq.median()], [i], color=INK, s=34, zorder=5)
        aq.text(12.5, i, f"n {len(qq)}   up {100 * (qq > 0).mean():.0f}%   median {qq.median():+.1f}%", va="center", fontsize=8.5, color=INK)
    for y, r in ret.items():
        need = 100 * (ye[2025] * (1 + r) / now_p - 1)
        aq.axvline(need, color=ORANGE if y == 2024 else GREEN, lw=1.4, ls="--")
        aq.text(need + 0.15, len(groups) - 0.45, f"a {y}-like year needs {need:+.1f}%\n({100 * (Qs >= need).mean():.0f}% of years did it)", fontsize=8, color=INK, va="bottom")
    aq.axvline(0, color=INK, lw=0.8)
    aq.set_yticks(range(len(groups)), [g[0] for g in groups[::-1]])
    aq.set_xlim(-9, 20)
    aq.set_ylim(-0.6, len(groups) + 0.5)
    aq.set_xlabel("S&P from the Oct 16 close to Dec 31, %  (bar = middle half of years, line = middle 80%, dot = median)")
    aq.set_title("The Q4 record", loc="left", fontsize=10, color=INK)
    f.suptitle("SPY in your channel, with S&P dealer gamma and the Q4 record (descriptive; the GEX result is the tested one)",
               x=0.01, ha="left", fontsize=12, color=INK, weight="bold", y=0.905)
    f.savefig(OUT / "spy_channel.png", dpi=140, bbox_inches="tight", facecolor=SURF)


def main():
    OUT.mkdir(exist_ok=True)
    D, L, spy, vix, dix, fits, cal = frame()
    T = touches(D)
    Q, ye, ret = q4(spy)
    (OUT / "lines.json").write_text(json.dumps({"fits_px": fits, "calibration": cal,
                                                "levels": {d: {k: round(float(L.loc[pd.Timestamp(d), k]), 2) for k in L} for d in ("2026-10-15", "2026-11-30", "2026-12-31")},
                                                "mid position (lower 0, upper 1)": float((np.log(L["mid"] / L["lower"]) / np.log(L["upper"] / L["lower"])).mean()),
                                                "share of closes inside the channel": float(((D.close >= D.lower) & (D.close <= D.upper)).mean())}, indent=1, default=float))
    T.to_csv(OUT / "touches.csv", index=False)
    Q.to_csv(OUT / "q4.csv")
    figure(D, L, spy, vix, dix, T, Q, ye, ret)
    return D, L, T, Q, ye, ret, spy, dix


if __name__ == "__main__":
    D, L, T, Q, ye, ret, spy, dix = main()
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 20)
    print(json.dumps(json.loads((OUT / "lines.json").read_text())["levels"], indent=1))
    print(T.round(2).to_string(index=False))
    print("latest GEX/DIX:", dix[["gex", "gex_pct", "dix", "dix_pct"]].tail(3).round(3).to_string())
    print("SPY", spy.close.tail(2).round(2).to_dict(), "| 2024 %.1f%% 2025 %.1f%% YTD %.1f%%" % (100 * ret[2024], 100 * ret[2025], 100 * (spy.close.iloc[-1] / ye[2025] - 1)))
