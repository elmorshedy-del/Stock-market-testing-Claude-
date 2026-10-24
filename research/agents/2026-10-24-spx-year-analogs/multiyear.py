"""Amendment 3 (pre-registered at 493d1d7): multi-year shape mirrors with a walk-forward test, and bull-market-age mirrors.
Usage: python multiyear.py <GSPC_max.json>  -> out/multiyear.json, out/bulls.csv, out/multiyear.png"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from analogs import load, NPERM, BLUE, ORANGE, GREEN, INK, MUTED, GRID, SURF, SOFT

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
WS, PRIMARY_W, K, SPACING = (24, 36, 48, 60), 48, 5, 12
HORIZONS = (1, 3, 12)
RNG = np.random.default_rng(20261024)


def monthly(c):
    m = c.resample("ME").last().dropna()
    return m.index, np.log(m.to_numpy())


def mirrors(lm, T, W, metric="rmse"):
    """Best K windows (ending >= SPACING months apart) for the W-month window ending at index T; no overlap with it."""
    cur = lm[T - W:T + 1] - lm[T - W]
    rows = []
    for e in range(W, T - W + 1):
        if e + max(HORIZONS) >= len(lm):
            continue
        p = lm[e - W:e + 1] - lm[e - W]
        rows.append((e, float(np.sqrt(np.mean((cur - p) ** 2))), float(np.corrcoef(cur, p)[0, 1])))
    R = pd.DataFrame(rows, columns=["end", "rmse", "corr"])
    R = R.sort_values(metric, ascending=(metric == "rmse"))
    pick = []
    for e in R.end:
        if all(abs(e - q) >= SPACING for q in pick):
            pick.append(e)
        if len(pick) == K:
            break
    return pick, R


def walk_forward(dates, lm, W, h, metric="rmse"):
    rows = []
    for T in [i for i, d in enumerate(dates) if d.month == 10 and 1955 <= d.year]:
        if T + h >= len(lm):
            continue
        pick, R = mirrors(lm[:T + 1], T, W, metric)          # only data known at T; candidates need e + 12 <= T (inside mirrors)
        R = R[R.end + h <= T]
        pick = [e for e in pick if e + h <= T]
        if len(pick) < 3 or R.empty:
            continue
        rows.append({"date": dates[T], "pred": np.mean([lm[e + h] - lm[e] for e in pick]),
                     "naive": float(np.mean([lm[e + h] - lm[e] for e in R.end])), "actual": lm[T + h] - lm[T]})
    Wf = pd.DataFrame(rows).set_index("date")
    cr = float(np.corrcoef(Wf.pred, Wf.actual)[0, 1])
    null = np.array([np.corrcoef(RNG.permutation(Wf.pred.to_numpy()), Wf.actual)[0, 1] for _ in range(NPERM)])
    res = {"test dates": int(len(Wf)), "corr(pred, actual)": cr, "p (permutation)": float((null >= cr).mean()),
           "hit rate mirror": float(np.mean(np.sign(Wf.pred) == np.sign(Wf.actual))),
           "hit rate naive": float(np.mean(np.sign(Wf.naive) == np.sign(Wf.actual)))}
    res["verdict"] = "pass" if (cr > 0 and res["p (permutation)"] < 0.05 and res["hit rate mirror"] > res["hit rate naive"]) else "fail"
    return res


def bulls(c):
    """Zigzag on closes with a 20% threshold: bear = -20% from the running peak, bull confirmed at +20% from the trough."""
    v, d = c.to_numpy(), c.index
    mode, ext, ext_i, troughs = "up", v[0], 0, []
    for i in range(1, len(v)):
        if mode == "up":
            if v[i] > ext:
                ext, ext_i = v[i], i
            elif v[i] <= 0.8 * ext:
                mode, ext, ext_i = "down", v[i], i
        else:
            if v[i] < ext:
                ext, ext_i = v[i], i
            elif v[i] >= 1.2 * ext:
                troughs.append(ext_i)
                mode, ext, ext_i = "up", v[i], i
    if mode == "down":
        troughs.append(ext_i)
    return troughs


def bull_table(c, troughs, age):
    """age: calendar time since the current bull's low (calendar, not trading days: Saturday sessions until 1952)."""
    v, d = c.to_numpy(), c.index
    rows = []
    for t in troughs:
        a = int(d.searchsorted(d[t] + age))
        if a >= len(v):
            continue
        seg = v[t:a + 1]
        dd = float((seg / np.maximum.accumulate(seg) - 1).min())
        alive = dd > -0.2
        r = {"low date": str(d[t].date()), "low": float(v[t]), "age date": str(d[a].date()), "alive at age": bool(alive),
             "gain at age %": 100 * (v[a] / v[t] - 1), "worst drawdown so far %": 100 * dd}
        for h in (1, 3, 12):
            b = int(d.searchsorted(d[a] + pd.DateOffset(months=h)))
            r[f"next {h}m %"] = 100 * (v[b] / v[a] - 1) if b < len(v) else np.nan
        rows.append(r)
    return pd.DataFrame(rows)


def age_vs_return(c, troughs):
    """Across month-ends inside bulls (before the bull's next -20%): age in months vs the next 12 months."""
    m = c.resample("ME").last()
    out = []
    for j, t in enumerate(troughs):
        start = c.index[t]
        seg = c[c.index >= start]
        run = seg / seg.cummax() - 1
        end = run.index[run <= -0.2][0] if (run <= -0.2).any() else seg.index[-1]
        mm = m[(m.index > start) & (m.index <= end)]
        for dt, val in mm.items():
            nxt = m[m.index > dt]
            if len(nxt) >= 12:
                out.append(((dt - start).days / 30.44, np.log(nxt.iloc[11] / val), np.log(val / c.iloc[t])))
    A = np.array(out)
    return {"months": int(len(A)), "corr(age, next 12m)": float(np.corrcoef(A[:, 0], A[:, 1])[0, 1]),
            "corr(gain so far, next 12m)": float(np.corrcoef(A[:, 2], A[:, 1])[0, 1]),
            "next 12m mean %, age < 24m": float(100 * np.expm1(A[A[:, 0] < 24, 1]).mean()),
            "next 12m mean %, age 24-48m": float(100 * np.expm1(A[(A[:, 0] >= 24) & (A[:, 0] < 48), 1]).mean()),
            "next 12m mean %, age >= 48m": float(100 * np.expm1(A[A[:, 0] >= 48, 1]).mean()),
            "share up, age >= 48m": float((A[A[:, 0] >= 48, 1] > 0).mean())}


def figure(c, dates, lm, troughs, now_t, T, pick, tab, wf):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                         "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
    f, (a, z) = plt.subplots(1, 2, figsize=(17, 6.8), gridspec_kw={"width_ratios": [1.25, 1], "wspace": 0.2})
    v, d = c.to_numpy(), c.index
    al = tab[tab["alive at age"]].copy()
    gain_now = 100 * (v[-1] / v[now_t] - 1)
    al["gap"] = (al["gain at age %"] - gain_now).abs()
    near = list(al.sort_values("gap")["low date"][:3])                  # the three bulls with the most similar gain at this age
    labels = []
    for t in troughs[:-1]:
        e = int(d.searchsorted(d[t] + pd.DateOffset(months=72)))
        seg = v[t:e + 1]
        x = (d[t:e + 1] - d[t]).days.to_numpy() / 30.44
        run = seg / np.maximum.accumulate(seg) - 1
        cut = np.argmax(run <= -0.2) if (run <= -0.2).any() else len(seg)
        g = 100 * (seg / seg[0] - 1)
        key = str(d[t].date())
        if key in near:
            col = (BLUE, ORANGE, GREEN)[near.index(key)]
            a.plot(x[:cut], g[:cut], color=col, lw=1.8, label=f"{d[t]:%b %Y} bull: +{g[min(int(np.searchsorted(x, (d[-1] - d[now_t]).days / 30.44)), len(g) - 1)]:.0f}% at month 48")
            a.plot(x[cut:], g[cut:], color=col, lw=0.9, alpha=0.5, ls=":")
            i48 = int(np.searchsorted(x, (d[-1] - d[now_t]).days / 30.44))
            pass
        elif key in set(al["low date"]):
            a.plot(x[:cut], g[:cut], color=MUTED, lw=0.9, alpha=0.55)
        else:
            a.plot(x[:cut], g[:cut], color=GRID, lw=0.8)
    cur = v[now_t:]
    xc = (d[now_t:] - d[now_t]).days.to_numpy() / 30.44
    a.plot(xc, 100 * (cur / cur[0] - 1), color=INK, lw=2.8, label=f"Oct 2022 bull (now): +{100 * (cur[-1] / cur[0] - 1):.0f}% at month 48")
    a.plot([], [], color=MUTED, lw=0.9, alpha=0.55, label="other bulls alive at month 48")
    a.plot([], [], color=GRID, lw=0.8, label="bulls that died earlier")
    a.legend(loc="upper left", frameon=False, fontsize=8)

    a.axvline(xc[-1], color=MUTED, lw=0.8, ls="--")
    a.set_xlim(0, 75)
    a.set_ylim(-20, 330)
    a.set_xlabel("months since the bear-market low")
    a.set_ylabel("gain from the low, %")
    a.set_title("Every S&P bull market since 1928, lined up from its bear-market low\n"
                "colour: the 3 bulls with the most similar gain at month 48 (dotted = after a new -20% bear)",
                loc="left", fontsize=9.5, color=INK)
    W = PRIMARY_W
    curp = lm[T - W:T + 1] - lm[T - W]
    xs = np.arange(-W, 1)
    for k, e in enumerate(pick):
        p = lm[e - W:e + 13] - lm[e - W]
        z.plot(np.arange(-W, 13)[:len(p)], 100 * np.expm1(p), color=SOFT[k], lw=1.4, label=f"{dates[e - W]:%b %Y} - {dates[e]:%b %Y}")
    z.plot(xs, 100 * np.expm1(curp), color=INK, lw=2.8, label=f"{dates[T - W]:%b %Y} - now")
    z.axvline(0, color=MUTED, lw=0.8, ls="--")
    z.set_xlabel("months (0 = end of the 4-year window; right of 0 = what came next)")
    z.set_ylabel("gain from the window's start, %")
    z.legend(loc="upper left", frameon=False, fontsize=8)
    w = wf[f"W={W}, next 12m (primary)"]
    z.set_title(f"The 4-year mirrors: closest past 4-year paths (shape and size) and their next 12 months\n"
                f"has it ever worked? {w['test dates']} Octobers since 1955: correlation {w['corr(pred, actual)']:+.2f} "
                f"(p {w['p (permutation)']:.2f}), right sign {w['hit rate mirror']:.0%} vs {w['hit rate naive']:.0%} naive",
                loc="left", fontsize=9.5, color=INK)
    f.savefig(OUT / "multiyear.png", dpi=140, bbox_inches="tight", facecolor=SURF)


def main(path):
    OUT.mkdir(exist_ok=True)
    c = load(path)
    dates, lm = monthly(c)
    T = len(lm) - 1
    res = {"now": str(dates[T].date()), "3a shape mirrors": {}, "3a walk-forward": {}}
    for W in WS:
        pick, R = mirrors(lm, T, W)
        pc, _ = mirrors(lm, T, W, "corr")
        res["3a shape mirrors"][f"W={W}"] = {
            "rmse mirrors": [{"window": f"{dates[e - W]:%Y-%m} to {dates[e]:%Y-%m}", "rmse": float(R.set_index('end').loc[e, 'rmse']),
                              "window gain %": float(100 * np.expm1(lm[e] - lm[e - W])),
                              **{f"next {h}m %": float(100 * np.expm1(lm[e + h] - lm[e])) for h in HORIZONS}} for e in pick],
            "corr mirrors": [f"{dates[e - W]:%Y-%m} to {dates[e]:%Y-%m}" for e in pc],
            "current window gain %": float(100 * np.expm1(lm[T] - lm[T - W]))}
        for h in (12, 1):
            lab = f"W={W}, next {h}m" + (" (primary)" if (W == PRIMARY_W and h == 12) else "")
            res["3a walk-forward"][lab] = walk_forward(dates, lm, W, h)
        res["3a walk-forward"][f"W={W}, next 12m, corr metric"] = walk_forward(dates, lm, W, 12, "corr")
    troughs = bulls(c)
    now_t = troughs[-1]
    age = c.index[-1] - c.index[now_t]
    tab = bull_table(c, troughs[:-1], age)
    tab.round(2).to_csv(OUT / "bulls.csv", index=False)
    cur = c.to_numpy()[now_t:]
    res["3b bull age"] = {"current bull low": str(c.index[now_t].date()), "current low close": float(c.iloc[now_t]),
                          "age (months)": float(age.days / 30.44), "gain %": float(100 * (cur[-1] / cur[0] - 1)),
                          "worst drawdown so far %": float(100 * (cur / np.maximum.accumulate(cur) - 1).min()),
                          "past bulls reaching this age alive": tab[tab["alive at age"]].round(2).to_dict("records"),
                          "past bulls that died earlier": tab[~tab["alive at age"]]["low date"].tolist(),
                          "age vs next 12 months (all bull months)": age_vs_return(c, troughs[:-1])}
    pick, _ = mirrors(lm, T, PRIMARY_W)
    (OUT / "multiyear.json").write_text(json.dumps(res, indent=1, default=float))
    figure(c, dates, lm, troughs, now_t, T, pick, tab, res["3a walk-forward"])
    return res


if __name__ == "__main__":
    print(json.dumps(main(sys.argv[1]), indent=1, default=float))
