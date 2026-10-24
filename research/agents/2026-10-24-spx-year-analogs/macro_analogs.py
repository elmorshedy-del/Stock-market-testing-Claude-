"""Amendment 2 (pre-registered at 6b42a42): which years had a macro and valuation backdrop like September 2026,
what came next, and does a macro analog say anything (walk-forward)?
Usage: python macro_analogs.py <GSPC_max.json> <cape_monthly.csv> <shiller.csv>  -> out/macro.json, out/macro.png
cape_monthly.csv: multpl.com monthly Shiller PE table (date,cape); shiller.csv: Shiller ie_data.xls 'Data' sheet as CSV."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from analogs import load, NOW_YEAR, K, NPERM, BLUE, ORANGE, GREEN, INK, MUTED, GRID, SURF, SOFT

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
PANEL = HERE.parent / "2026-10-15-channel-reversion-macro" / "out" / "macro_monthly.csv"
RNG = np.random.default_rng(20261024)
PRIMARY = ["fed funds", "fed funds 12m change", "CPI yoy", "10y yield", "curve 10y-3m", "CAPE", "S&P Jan-Sep %"]
SECONDARY = ["CAPE", "10y yield", "CPI yoy", "10y 12m change", "S&P Jan-Sep %"]


def features(c, cape_path, shiller_path):
    p = pd.read_csv(PANEL, parse_dates=["month"]).set_index("month")
    cape = pd.read_csv(cape_path)
    cape["date"] = pd.to_datetime(cape.date, format="%b %d, %Y")
    cape = cape.set_index("date").cape
    sh = pd.read_csv(shiller_path)
    sh = sh[pd.to_numeric(sh.Date, errors="coerce").notna()].copy()
    sh["y"], sh["m"] = sh.Date.astype(float).astype(int), np.round((sh.Date.astype(float) % 1) * 100).astype(int)
    sh = sh.set_index(["y", "m"])
    rows = []
    for y in range(1900, NOW_YEAR + 1):
        r = {"year": y}
        sep, prev = c[(c.index.year == y) & (c.index.month <= 9)], c[c.index.year == y - 1]
        if len(sep) == 0 or len(prev) == 0:
            continue
        r["S&P Jan-Sep %"] = 100 * (sep.iloc[-1] / prev.iloc[-1] - 1)
        cs = cape[(cape.index.year == y) & (cape.index.month == 9)]
        r["CAPE"] = float(cs.iloc[0]) if len(cs) else np.nan
        if y >= 1982:
            s, s0 = p[(p.index.year == y) & (p.index.month == 9)], p[(p.index.year == y - 1) & (p.index.month == 9)]
            if len(s) and len(s0):
                s, s0 = s.iloc[0], s0.iloc[0]
                r.update({"fed funds": s.ff, "fed funds 12m change": s.ff - s0.ff, "CPI yoy": s.cpi_yoy, "10y yield": s.gs10,
                          "curve 10y-3m": s.gs10 - s.gs3m, "10y 12m change": s.gs10 - s0.gs10})
        else:
            try:
                g, g0 = float(sh.loc[(y, 9), "Rate GS10"]), float(sh.loc[(y - 1, 9), "Rate GS10"])
                r.update({"10y yield": g, "10y 12m change": g - g0,
                          "CPI yoy": 100 * (float(sh.loc[(y, 9), "CPI"]) / float(sh.loc[(y - 1, 9), "CPI"]) - 1)})
            except KeyError:
                pass
        rows.append(r)
    return pd.DataFrame(rows).set_index("year")


def outcomes(c, y):
    s = c[c.index.year == y]
    d0 = s[s.index <= pd.Timestamp(f"{y}-10-23")]
    if len(d0) == 0:
        return {}
    x0 = d0.iloc[-1]
    nov, octs, nxt = s[s.index.month == 11], s[s.index.month == 10], c[(c.index.year == y + 1) & (c.index.month == 10)]
    return {"to end of Nov %": 100 * (nov.iloc[-1] / x0 - 1) if len(nov) else np.nan,
            "to year end %": 100 * (s.iloc[-1] / x0 - 1) if s.index[-1].month == 12 else np.nan,
            "next 12 months %": 100 * (nxt.iloc[-1] / octs.iloc[-1] - 1) if len(nxt) and len(octs) and nxt.index[-1].day >= 20 else np.nan}


def nearest(F, cols, target, cands, k=K):
    X = F.loc[cands, cols].dropna()
    mu, sd = X.mean(), X.std()
    z = (X - mu) / sd
    t = (F.loc[target, cols] - mu) / sd
    d = np.sqrt(((z - t) ** 2).sum(axis=1)).sort_values()
    return d.head(k), d


def walk_forward(F, O, cols, first, outcome):
    rows = []
    for y in range(first, NOW_YEAR):
        if y not in F.index or F.loc[y, cols].isna().any() or np.isnan(O.get(y, {}).get(outcome, np.nan)):
            continue
        cands = [c_ for c_ in F.index if c_ < y and not F.loc[c_, cols].isna().any() and not np.isnan(O.get(c_, {}).get(outcome, np.nan))]
        if outcome == "next 12 months %":
            cands = [c_ for c_ in cands if c_ < y - 1]               # its 12-month outcome must be known by year y
        if len(cands) < 10:
            continue
        top, _ = nearest(F, cols, y, cands)
        rows.append({"year": y, "pred": np.mean([O[c_][outcome] for c_ in top.index]), "naive": np.mean([O[c_][outcome] for c_ in cands]),
                     "actual": O[y][outcome]})
    W = pd.DataFrame(rows).set_index("year")
    cr = float(np.corrcoef(W.pred, W.actual)[0, 1])
    null = np.array([np.corrcoef(RNG.permutation(W.pred.to_numpy()), W.actual)[0, 1] for _ in range(NPERM)])
    res = {"test years": int(len(W)), "first": int(W.index[0]), "corr(pred, actual)": cr, "p (permutation)": float((null >= cr).mean()),
           "hit rate analog": float(np.mean(np.sign(W.pred) == np.sign(W.actual))),
           "hit rate naive": float(np.mean(np.sign(W.naive) == np.sign(W.actual)))}
    res["verdict"] = "pass" if (cr > 0 and res["p (permutation)"] < 0.05 and res["hit rate analog"] > res["hit rate naive"]) else "fail"
    return res, W


def figure(F, O, top, top2, wf):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                         "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
    f, (a, z) = plt.subplots(1, 2, figsize=(16, 6.4), gridspec_kw={"width_ratios": [1.5, 1], "wspace": 0.28})
    X = F.loc[[y for y in F.index if 1982 <= y <= NOW_YEAR], PRIMARY].dropna()
    mu, sd = X.loc[X.index < NOW_YEAR].mean(), X.loc[X.index < NOW_YEAR].std()
    zz = (X - mu) / sd
    yy = np.arange(len(PRIMARY))[::-1]
    for i, col in enumerate(PRIMARY):
        a.scatter(zz[col].drop(NOW_YEAR), np.full(len(zz) - 1, yy[i]), s=12, color=GRID, zorder=1)
    for j, y in enumerate(top.index):
        a.scatter(zz.loc[y, PRIMARY], yy + 0.12 * (j - 2) / 2, s=34, color=SOFT[j], zorder=3, label=str(y), edgecolor=SURF, lw=0.5)
    a.scatter(zz.loc[NOW_YEAR, PRIMARY], yy, s=110, color=INK, marker="D", zorder=4, label="2026")
    labels = [f"{col}\n2026: {F.loc[NOW_YEAR, col]:.1f}" for col in PRIMARY]
    a.set_yticks(yy, labels)
    a.axvline(0, color=MUTED, lw=0.6, ls=":")
    a.set_xlabel("standard deviations from the 1982-2025 average (grey dots: every year)")
    a.legend(loc="upper left", bbox_to_anchor=(0.0, -0.1), frameon=False, fontsize=8.5, ncol=6)
    a.set_title("The macro fingerprint of September 2026 (black) and the five nearest years since 1982\n"
                "Fed easing, inflation above 3%, 10-year near 5%, valuations near records, stocks up double digits",
                loc="left", fontsize=10, color=INK)
    yrs = list(top.index)
    x = np.arange(len(yrs))
    sets = (("to end of November", "to end of Nov %", -0.27, MUTED), ("to year end", "to year end %", 0.0, "#b9b8b3"),
            ("next 12 months (end of Oct to end of Oct)", "next 12 months %", 0.27, None))
    for lab, key, off, col in sets:
        vals = [O[y][key] for y in yrs]
        z.bar(x + off, vals, width=0.25, color=col if col else [SOFT[j] for j in range(len(yrs))], label=lab, edgecolor=SURF, lw=0.5)
        for xi, v, y in zip(x, vals, yrs):
            t = f"{v:+.0f}" + ("*" if key == "next 12 months %" and y == NOW_YEAR - 1 else "")
            z.text(xi + off, v + (0.5 if v >= 0 else -0.5), t, ha="center", va="bottom" if v >= 0 else "top", fontsize=7.5, color=INK)
    z.axhline(0, color=INK, lw=0.8)
    z.set_xticks(x, [f"{y}{chr(10) + 'midterm' if y % 4 == 2 else ''}" for y in yrs], fontsize=8.5)
    z.set_ylabel("S&P 500 return, %")
    z.legend(loc="upper left", frameon=False, fontsize=8)
    z.text(0.0, -0.16, "* 2025's next 12 months runs only to Oct 23, 2026 (today)", transform=z.transAxes, fontsize=7.5, color=MUTED)
    w12 = wf["primary: next 12 months"]
    z.set_title(f"What came next in those years\nhas a macro twin ever predicted the next 12 months? {w12['test years']} years: "
                f"correlation {w12['corr(pred, actual)']:+.2f}, right sign {w12['hit rate analog']:.0%} vs {w12['hit rate naive']:.0%} naive",
                loc="left", fontsize=10, color=INK)
    f.savefig(OUT / "macro.png", dpi=140, bbox_inches="tight", facecolor=SURF)


def main(gspc, cape, shiller):
    c = load(gspc)
    F = features(c, cape, shiller)
    O = {y: outcomes(c, y) for y in F.index}
    cands1 = [y for y in F.index if 1982 <= y < NOW_YEAR]
    top, d1 = nearest(F, PRIMARY, NOW_YEAR, cands1)
    cands2 = [y for y in F.index if y < NOW_YEAR]
    top2, d2 = nearest(F, SECONDARY, NOW_YEAR, cands2)
    wf = {"primary: next 12 months": walk_forward(F, O, PRIMARY, 1991, "next 12 months %")[0],
          "primary: to end of Nov": walk_forward(F, O, PRIMARY, 1991, "to end of Nov %")[0],
          "secondary (1900+): next 12 months": walk_forward(F, O, SECONDARY, 1930, "next 12 months %")[0],
          "secondary (1900+): to end of Nov": walk_forward(F, O, SECONDARY, 1930, "to end of Nov %")[0]}
    show = lambda tp, cols: {int(y): {"distance": float(tp[y]), **{k_: float(F.loc[y, k_]) for k_ in cols}, **{k_: float(v) for k_, v in O[y].items()},
                                      "midterm": bool(y % 4 == 2)} for y in tp.index}
    res = {"2026": {k_: float(F.loc[NOW_YEAR, k_]) for k_ in PRIMARY + ["10y 12m change"]},
           "primary nearest (1982-2025)": show(top, PRIMARY), "secondary nearest (1900-2025)": show(top2, SECONDARY),
           "primary distance ranking": {int(y): round(float(v), 2) for y, v in d1.head(10).items()},
           "walk-forward": wf}
    (OUT / "macro.json").write_text(json.dumps(res, indent=1))
    F.round(3).to_csv(OUT / "macro_features.csv")
    figure(F, O, top, top2, wf)
    return res


if __name__ == "__main__":
    print(json.dumps(main(*sys.argv[1:4]), indent=1))
