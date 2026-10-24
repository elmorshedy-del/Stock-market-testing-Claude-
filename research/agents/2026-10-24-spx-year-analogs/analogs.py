"""Year-shape analogs for the S&P's 2026 and a walk-forward skill test (README.md, pre-registered at 8c1c59b).
Usage: python analogs.py <GSPC_max.json>  -> out/analogs.json, out/analogs.csv, out/analogs.png
Data: Yahoo ^GSPC daily since 1927 (chart API, period1=-1325635200), kept outside the repo."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
NOW_YEAR, K, RECENT, TEST_FROM = 2026, 5, 21, 1950
NPERM = 5000
RNG = np.random.default_rng(20261024)
BLUE, ORANGE, GREEN, INK, MUTED, GRID, SURF = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"
SOFT = ["#2a78d6", "#eb6834", "#1baf7a", "#8e5bd6", "#c9a227"]


def load(path):
    d = json.loads(Path(path).read_text())["chart"]["result"][0]
    idx = pd.to_datetime(d["timestamp"], unit="s", utc=True).tz_convert("America/New_York").normalize().tz_localize(None)
    c = pd.Series(d["indicators"]["quote"][0]["close"], index=idx).dropna()
    return c[~c.index.duplicated(keep="last")].sort_index()


def years(c):
    """Per year: log path vs the prior year's last close (trading-day index), dates, closes."""
    Y = {}
    for y in range(1928, NOW_YEAR + 1):
        s = c[c.index.year == y]
        prev = c[c.index.year == y - 1]
        if len(s) == 0 or len(prev) == 0:
            continue
        Y[y] = {"path": np.log(s.to_numpy() / prev.iloc[-1]), "dates": s.index, "close": s.to_numpy()}
    return Y


def outcomes(Y, y, n0):
    s = Y[y]
    i = n0 - 1
    nov = np.nonzero(s["dates"].month == 11)[0]
    a = np.log(s["close"][nov[-1]] / s["close"][i]) if len(nov) and nov[-1] > i else np.nan
    b = np.log(s["close"][-1] / s["close"][i])
    return a, b


def scores(Y, target, n0, cands):
    p = Y[target]["path"][:n0]
    r = p[n0 - RECENT:] - p[n0 - RECENT]
    rows = []
    for y in cands:
        q = Y[y]["path"]
        if len(q) < n0 + 30:
            continue
        qq = q[:n0]
        rr = qq[n0 - RECENT:] - qq[n0 - RECENT]
        rows.append({"year": y, "shape": float(np.corrcoef(p, qq)[0, 1]), "recent": float(np.corrcoef(r, rr)[0, 1]),
                     "rmse": float(np.sqrt(np.mean((p - qq) ** 2)))})
    return pd.DataFrame(rows).set_index("year")


def calendar_years(Y):
    """Post-hoc robustness (not pre-registered): put every year on 2026's calendar (day of year) instead of trading-day count,
    because exchanges traded on Saturdays until 1952, which shifts the trading-day index against the calendar."""
    grid = np.array([d.dayofyear for d in Y[NOW_YEAR]["dates"]])
    Z = {}
    for y, s in Y.items():
        doy = np.array([d.dayofyear for d in s["dates"]])
        if y == NOW_YEAR:
            Z[y] = dict(s)
            continue
        if doy[-1] < 335:
            continue
        idx = np.searchsorted(doy, grid, side="right") - 1          # last session on or before the same calendar day
        idx = np.clip(idx, 0, len(doy) - 1)
        n0 = len(grid)
        Z[y] = {"path": np.r_[s["path"][idx], s["path"][idx[-1] + 1:]], "dates": s["dates"][np.r_[idx, np.arange(idx[-1] + 1, len(doy))]],
                "close": np.r_[s["close"][idx], s["close"][idx[-1] + 1:]]}
    return Z


def walk_forward(Y, n0, k=K, by="shape", outcome=0):
    rows = []
    for y in range(TEST_FROM, NOW_YEAR):
        if y not in Y or len(Y[y]["path"]) < n0 + 30:
            continue
        S = scores(Y, y, n0, [c for c in Y if c < y])
        out = {c: outcomes(Y, c, n0)[outcome] for c in S.index}
        S["out"] = pd.Series(out)
        S = S.dropna(subset=["out"])
        top = S.sort_values(by, ascending=(by == "rmse")).head(k)
        rows.append({"year": y, "pred": top.out.mean(), "naive": S.out.mean(), "actual": outcomes(Y, y, n0)[outcome],
                     "analogs": list(top.index)})
    W = pd.DataFrame(rows).set_index("year").dropna(subset=["actual"])
    cr = float(np.corrcoef(W.pred, W.actual)[0, 1])
    null = np.array([np.corrcoef(RNG.permutation(W.pred.to_numpy()), W.actual)[0, 1] for _ in range(NPERM)])
    ex = float(np.corrcoef(W.pred - W.naive, W.actual - W.naive)[0, 1])
    q = pd.qcut(W.pred.rank(method="first"), 3, labels=["bottom third", "middle", "top third"])
    res = {"test years": int(len(W)), "corr(pred, actual)": cr, "p (permutation)": float((null >= cr).mean()),
           "corr(pred - naive, actual - naive)": ex,
           "hit rate analog": float(np.mean(np.sign(W.pred) == np.sign(W.actual))),
           "hit rate naive": float(np.mean(np.sign(W.naive) == np.sign(W.actual))),
           "actual by prediction third %": {str(k_): float(100 * v) for k_, v in W.actual.groupby(q, observed=False).mean().items()},
           "up share by prediction third": {str(k_): float(v) for k_, v in (W.actual > 0).groupby(q, observed=False).mean().items()}}
    res["verdict"] = "pass" if (cr > 0 and res["p (permutation)"] < 0.05 and res["hit rate analog"] > res["hit rate naive"]) else "fail"
    return res, W


def figure(c, Y, Z, n0, S, top, wf, W):
    """Drawn on 2026's calendar (day of year): Saturday sessions before 1952 would otherwise stretch the old years."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                         "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
    f, (a, z) = plt.subplots(1, 2, figsize=(16.5, 6.8), gridspec_kw={"width_ratios": [2.1, 1], "wspace": 0.18})
    base = c[c.index.year == NOW_YEAR - 1].iloc[-1]
    p26 = Y[NOW_YEAR]["path"]
    now = float(c.iloc[-1])
    x26 = np.array([d.dayofyear for d in Y[NOW_YEAR]["dates"]])
    ends = []
    for j, y in enumerate(top):
        q = Z[y]["path"]
        xq = np.r_[x26, [d.dayofyear for d in Z[y]["dates"][n0:]]]
        bb, aa = np.polyfit(q[:n0], p26, 1)                      # rhyme scaling: 2026 ~ aa + bb * year y, fitted on Jan 1 - Oct 23
        a.plot(xq[:n0], base * np.exp(aa + bb * q[:n0]), color=SOFT[j], lw=1.0, alpha=0.5)
        cont = now * np.exp(q[n0 - 1:] - q[n0 - 1])             # what that year did next, in % terms, from today's level
        a.plot(xq[n0 - 1:], cont, color=SOFT[j], lw=1.9)
        ends.append([cont[-1], y, SOFT[j]])
    ends.sort()
    for i in range(1, len(ends)):                                # keep the end labels from overlapping
        ends[i][0] = max(ends[i][0], ends[i - 1][0] + 75)
    for v, y, col in ends:
        a.text(370, v, f"{y}: {now * np.exp(Z[y]['path'][-1] - Z[y]['path'][n0 - 1]):,.0f}", color=col, fontsize=8.5, va="center", weight="bold")
    a.plot(x26, base * np.exp(p26), color=INK, lw=2.4)
    a.scatter([x26[-1]], [now], s=40, color=INK, zorder=5)
    a.text(x26[-1] - 3, now - 160, f"Oct 23: {now:,.0f}", ha="right", fontsize=8.5, color=INK)
    a.axvspan(x26[-1], 334, color=GRID, alpha=0.6, lw=0, zorder=0)
    lo = a.get_ylim()[0]
    a.text((x26[-1] + 334) / 2, lo + 40, "to end of Nov", ha="center", fontsize=8, color=MUTED)
    ticks = {"Jan": 1, "Mar": 60, "May": 121, "Jul": 182, "Sep": 244, "Nov": 305, "Dec 31": 365}
    a.set_xticks(list(ticks.values()), list(ticks.keys()))
    a.set_xlim(0, 400)
    a.set_ylabel("S&P 500")
    a.set_title(f"2026 (black) rhymes most with {', '.join(str(y) for y in top[:-1])} and {top[-1]} "
                f"(shape correlation {S.loc[top, 'shape'].min():.2f}-{S.loc[top, 'shape'].max():.2f})\n"
                f"thin: each year's path fitted to 2026's shape   bold: what each did next, applied to today's {now:,.0f}",
                loc="left", fontsize=9.5, color=INK)
    z.axhline(0, color=MUTED, lw=0.8)
    z.axvline(0, color=MUTED, lw=0.8)
    z.scatter(100 * W.pred, 100 * W.actual, s=22, color=BLUE, alpha=0.7, edgecolor=SURF, lw=0.5)
    m, b0 = np.polyfit(100 * W.pred, 100 * W.actual, 1)
    xx = np.linspace(100 * W.pred.min(), 100 * W.pred.max(), 10)
    z.plot(xx, m * xx + b0, color=ORANGE, lw=1.6)
    z.set_xlabel("what that year's five analogs said, late Oct to end of Nov, %")
    z.set_ylabel("what that year actually did, %")
    z.set_title(f"Has a rhyme ever predicted the next month?\n{wf['test years']} years (1950-2025), analogs picked only from earlier years\n"
                f"correlation {wf['corr(pred, actual)']:+.2f} (p {wf['p (permutation)']:.2f}); right sign {wf['hit rate analog']:.0%} "
                f"vs {wf['hit rate naive']:.0%} for the season", loc="left", fontsize=9.5, color=INK)
    f.savefig(OUT / "analogs.png", dpi=140, bbox_inches="tight", facecolor=SURF)


def main(path):
    OUT.mkdir(exist_ok=True)
    c = load(path)
    Y = years(c)
    n0 = len(Y[NOW_YEAR]["path"])
    S = scores(Y, NOW_YEAR, n0, [y for y in Y if y < NOW_YEAR])
    for y in S.index:
        S.loc[y, "to end of Nov %"], S.loc[y, "to year end %"] = (100 * v for v in outcomes(Y, y, n0))
        S.loc[y, "date of day n0"] = str(Y[y]["dates"][n0 - 1].date())
        S.loc[y, "year %"] = 100 * (np.exp(Y[y]["path"][-1]) - 1)
    S = S.sort_values("shape", ascending=False)
    S.round(4).to_csv(OUT / "analogs.csv")
    top = list(S.index[:K])
    wf, W = walk_forward(Y, n0)
    sec = {}
    for lab, kw in (("year-end outcome", {"outcome": 1}), ("K=3", {"k": 3}), ("K=10", {"k": 10}), ("recent-month selector", {"by": "recent"}),
                    ("rmse selector", {"by": "rmse"})):
        sec[lab] = {k_: v for k_, v in walk_forward(Y, n0, **kw)[0].items() if k_ not in ("actual by prediction third %", "up share by prediction third")}
    allyrs = S.dropna(subset=["to end of Nov %"])
    Z = calendar_years(Y)
    SZ = scores(Z, NOW_YEAR, n0, [y for y in Z if y < NOW_YEAR])
    for y in SZ.index:
        SZ.loc[y, "to end of Nov %"], SZ.loc[y, "to year end %"] = (100 * v for v in outcomes(Z, y, n0))
    SZ = SZ.sort_values("shape", ascending=False)
    wfz = walk_forward(Z, n0)[0]
    cal = {"top analogs": {int(y): {"shape": float(SZ.loc[y, "shape"]), "to end of Nov %": float(SZ.loc[y, "to end of Nov %"]),
                                    "to year end %": float(SZ.loc[y, "to year end %"])} for y in SZ.index[:K]},
           "walk-forward": {k_: v for k_, v in wfz.items()}}
    res = {"n0 (2026 sessions)": n0, "2026 YTD %": float(100 * (np.exp(Y[NOW_YEAR]["path"][-1]) - 1)),
           "top analogs": {int(y): {k_: (float(v) if not isinstance(v, str) else v) for k_, v in S.loc[y].items()} for y in top},
           "analog mean to end of Nov %": float(S.loc[top, "to end of Nov %"].mean()),
           "all years mean to end of Nov %": float(allyrs["to end of Nov %"].mean()),
           "all years up share to end of Nov": float((allyrs["to end of Nov %"] > 0).mean()),
           "top by recent-month shape": [int(y) for y in S.sort_values("recent", ascending=False).index[:K]],
           "top by rmse": [int(y) for y in S.sort_values("rmse").index[:K]],
           "walk-forward (pre-registered)": wf, "walk-forward secondary": sec,
           "post-hoc: calendar-day alignment (Saturday sessions before 1952)": cal}
    (OUT / "analogs.json").write_text(json.dumps(res, indent=1))
    figure(c, Y, Z, n0, S, top, wf, W)
    return res, S


if __name__ == "__main__":
    res, S = main(sys.argv[1])
    pd.set_option("display.width", 200)
    print(S.head(12).round(3).to_string())
    print(json.dumps({k: v for k, v in res.items() if k != "top analogs"}, indent=1))
