"""Gaps and walls (pre-registered in README.md at 7b90640).
G1  do the open, the day's high/low and the premarket high/low land on the 3 highest-OI strikes more than on
    equally round strikes (roundness-matched null), and more than on walls built from another day's OI?
G2  on gap days, does the open's side of the dealer gamma flip decide continuation vs being dragged back?
Usage: OMP_NUM_THREADS=1 python gaps_walls.py   -> out/g1.json, out/g2.json, out/g2_cells.csv, out/gaps_walls.png
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

HERE = Path(__file__).resolve().parent
DATA, OUT = HERE / "data", HERE / "out"
MICRO = HERE.parents[1] / "microstructure"
sys.path.insert(0, str(MICRO))
import td_gamma as TG                                    # noqa: E402  (original, imported unchanged)

END = "2026-10-15"
CLASSES = (100, 50, 25, 10, 5, 2.5, 1)
RNG = np.random.default_rng(20261016)
BLUE, ORANGE, INK, MUTED, GRID, SURF = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"


def fetch(sym, params, name):
    path = DATA / name
    if not path.exists():
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?{params}"
        DATA.mkdir(exist_ok=True)
        path.write_bytes(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read())
    return json.loads(path.read_text())["chart"]["result"][0]


def daily(sym):
    d = fetch(sym, "period1=0&period2=9999999999&interval=1d&includePrePost=false&events=div%2Csplit", f"{sym}_1d.json")
    q = d["indicators"]["quote"][0]
    idx = pd.to_datetime(d["timestamp"], unit="s", utc=True).tz_convert("America/New_York").normalize().tz_localize(None)
    df = pd.DataFrame({k: q[k] for k in ("open", "high", "low", "close")}, index=idx)
    df["adj"] = d["indicators"]["adjclose"][0]["adjclose"]
    df = df.dropna()
    df = df[~df.index.duplicated(keep="last") & (df.index <= END)]
    f = df.adj / df.close
    return pd.DataFrame({"open": df.open * f, "high": df.high * f, "low": df.low * f, "close": df.adj})


def premarket(sym):
    d = fetch(sym, "range=60d&interval=5m&includePrePost=true", f"{sym}_5m_prepost.json")
    q = d["indicators"]["quote"][0]
    idx = pd.to_datetime(d["timestamp"], unit="s", utc=True).tz_convert("America/New_York")
    df = pd.DataFrame({k: q[k] for k in ("high", "low")}, index=idx).dropna()
    pm = df[(df.index.time >= pd.Timestamp("04:00").time()) & (df.index.time < pd.Timestamp("09:30").time())]
    g = pm.groupby(pm.index.normalize().tz_localize(None))
    return pd.DataFrame({"pm_high": g.high.max(), "pm_low": g.low.min(), "bars": g.size()})


def roundness(k):
    for c in CLASSES:
        if abs(k / c - round(k / c)) < 1e-6:
            return c
    return 0


def oi_maps(sym="TSLA"):
    oi = TG.read(sym, "oi")
    oi = oi[(oi.expiration >= oi.date) & ((oi.expiration - oi.date).dt.days <= 45)]
    col = next(c for c in oi.columns if "open_interest" in c)
    return oi.groupby(["date", "strike"])[col].sum()


def g1_days(sym="TSLA"):
    """Per day: window strikes, their classes and OI, the 3 walls, the strike spacing, and the raw prices to test."""
    M = oi_maps(sym)
    px = daily(sym)
    g = pd.read_csv(MICRO / "out" / f"td_gamma_{sym}.csv", parse_dates=["date"]).set_index("date")
    ratio = (g.spot / px.close.reindex(g.index)).dropna()                       # raw / adjusted (splits)
    pm = premarket(sym)
    rows = []
    dates = sorted(set(M.index.get_level_values(0)) & set(px.index))
    for i, t in enumerate(dates[1:], 1):
        prev = px.index[px.index.get_loc(t) - 1]
        if t not in ratio.index:
            continue
        f = ratio.loc[t]
        f = min((1.0, 3.0, 15.0), key=lambda x: abs(x - f)) if sym == "TSLA" else f
        pc = px.close.loc[prev] * f
        s = M.loc[t]
        s = s[(s.index >= 0.9 * pc) & (s.index <= 1.1 * pc)]
        if len(s) < 8:
            continue
        ks = np.array(s.index, float)
        spacing = float(np.median(np.diff(np.sort(ks))))
        walls = ks[np.argsort(-s.to_numpy())[:3]]
        rec = {"date": t, "ks": ks, "oi": s.to_numpy(), "cls": np.array([roundness(k) for k in ks]), "walls": walls, "eps": 0.1 * spacing,
               "open": px.open.loc[t] * f, "high": px.high.loc[t] * f, "low": px.low.loc[t] * f, "prev_close": pc,
               "gap": px.open.loc[t] / px.close.loc[prev] - 1}
        if t in pm.index and pm.bars.loc[t] >= 30:
            rec["pm_high"], rec["pm_low"] = pm.pm_high.loc[t] * f, pm.pm_low.loc[t] * f
        rows.append(rec)
    return rows


def hit(x, walls, eps):
    return bool(np.any(np.abs(walls - x) <= eps + 1e-9))


def null_hits(days, keys, reps=2000):
    """Roundness-matched null: replace each day's walls with random strikes of the same classes from its window."""
    tot = np.zeros(reps)
    for d in days:
        xs = [d[k] for k in keys if k in d]
        if not xs:
            continue
        wcls = [d["cls"][np.where(d["ks"] == w)[0][0]] for w in d["walls"]]
        drawn = np.zeros((reps, 0))
        for c in set(wcls):
            pool = d["ks"][d["cls"] == c]
            m = wcls.count(c)
            idx = np.argsort(RNG.random((reps, len(pool))), axis=1)[:, :m]
            drawn = np.hstack([drawn, pool[idx]])
        for x in xs:
            tot += (np.abs(drawn - x) <= d["eps"] + 1e-9).any(axis=1)
    return tot


def shifted_oi_hits(days, keys, n=200):
    """Second null: today's window strikes, but the walls chosen with the OI of a day 20-250 sessions away."""
    lookup = {d["date"]: d for d in days}
    order = [d["date"] for d in days]
    out = []
    for k in RNG.choice(np.arange(20, 251), n):
        h = 0
        for i, d in enumerate(days):
            o = lookup[order[(i - k) % len(order)]]
            m = dict(zip(o["ks"], o["oi"]))
            oi = np.array([m.get(s, 0.0) for s in d["ks"]])
            walls = d["ks"][np.argsort(-oi)[:3]]
            h += sum(hit(d[x], walls, d["eps"]) for x in keys if x in d)
        out.append(h)
    return np.array(out)


def dist_matched(ds, keys, reps=2000):
    """Post-hoc null (added after the run): same roundness AND within 1 percentage point of the wall's distance from the
    prior close. The pre-registered null drew from the whole +-10% window, but walls sit near the price, so it favoured them."""
    tot = np.zeros(reps)
    for d in ds:
        xs = [d[k] for k in keys if k in d]
        dist = np.abs(d["ks"] / d["prev_close"] - 1)
        drawn = []
        for w in d["walls"]:
            c, dw = d["cls"][d["ks"] == w][0], abs(w / d["prev_close"] - 1)
            pool = d["ks"][(d["cls"] == c) & (np.abs(dist - dw) <= 0.01)]
            drawn.append((pool if len(pool) else np.array([w]))[RNG.integers(0, max(len(pool), 1), reps)])
        drawn = np.stack(drawn, 1)
        for x in xs:
            tot += (np.abs(drawn - x) <= d["eps"] + 1e-9).any(axis=1)
    return tot


def g1():
    days = g1_days()
    res = {}
    for name, keys, sub in (("(a) open", ["open"], None), ("(b) day high and low", ["high", "low"], None),
                            ("(c) premarket high and low", ["pm_high", "pm_low"], None)):
        ds = [d for d in days if all(k in d for k in keys)]
        obs = sum(hit(d[k], d["walls"], d["eps"]) for d in ds for k in keys)
        nl = null_hits(ds, keys)
        sh = shifted_oi_hits(ds, keys)
        dm = dist_matched(ds, keys)
        res[name] = {"days": len(ds), "events": len(ds) * len(keys), "hits": int(obs), "hit rate": obs / (len(ds) * len(keys)),
                     "null mean hits (round-matched)": float(nl.mean()), "excess hits": float(obs - nl.mean()),
                     "ratio vs null": float(obs / nl.mean()) if nl.mean() else np.nan, "p (round-matched)": float((np.sum(nl >= obs) + 1) / (len(nl) + 1)),
                     "shifted-OI null mean hits": float(sh.mean()), "p (shifted OI)": float((np.sum(sh >= obs) + 1) / (len(sh) + 1)),
                     "passes (p < 0.0167)": bool((np.sum(nl >= obs) + 1) / (len(nl) + 1) < 0.05 / 3),
                     "post-hoc distance+round-matched null mean hits": float(dm.mean()), "post-hoc ratio": float(obs / dm.mean()) if dm.mean() else np.nan,
                     "post-hoc p (distance+round-matched)": float((np.sum(dm >= obs) + 1) / (len(dm) + 1)),
                     "first": str(ds[0]["date"].date()), "last": str(ds[-1]["date"].date())}
    gp = pd.Series([abs(d["gap"]) for d in days], index=[d["date"] for d in days])
    pct = gp.rolling(252, min_periods=120).rank(pct=True)
    gd = [d for d in days if pct.get(d["date"], np.nan) >= 0.8]
    obs = sum(hit(d["open"], d["walls"], d["eps"]) for d in gd)
    nl = null_hits(gd, ["open"])
    res["(a') open, gap days only"] = {"days": len(gd), "hits": int(obs), "hit rate": obs / len(gd), "null mean hits (round-matched)": float(nl.mean()),
                                       "ratio vs null": float(obs / nl.mean()) if nl.mean() else np.nan, "p (round-matched)": float((np.sum(nl >= obs) + 1) / (len(nl) + 1))}
    return res, days


def g2(sym):
    px = daily(sym)
    g = pd.read_csv(MICRO / "out" / f"td_gamma_{sym}.csv", parse_dates=["date"]).set_index("date")
    D = px.copy()
    D["prev_close"] = D.close.shift(1)
    D["gap"] = D.open / D.prev_close - 1
    D["gap_pct"] = D.gap.abs().rolling(252, min_periods=120).rank(pct=True)
    prev = g.shift(1).reindex(D.index) if False else None
    gi = g.reindex(D.index.union(g.index)).shift(1).reindex(D.index)          # the row from the prior trading day in the gamma file
    ratio = gi.spot / D.prev_close
    D["open_raw"], D["flip_prev"] = D.open * ratio, gi.flip_classic
    D = D[(D.gap_pct >= 0.8) & D.flip_prev.notna() & (D.index >= "2020-01-01")]
    below = (D.open_raw < D.flip_prev).to_numpy()
    cont = (np.sign(D.close - D.open) == np.sign(D.gap)).to_numpy().astype(float)
    filled = np.where(D.gap > 0, D.close < D.prev_close, D.close > D.prev_close).astype(float)
    stat = lambda b: cont[b].mean() - cont[~b].mean()
    obs = stat(below)
    offs = np.arange(10, len(D) - 9)
    null = np.array([stat(np.roll(below, o)) for o in offs])
    p = (np.sum(null >= obs) + 1) / (len(offs) + 1)
    cells = []
    for gl, gm in (("gap up", D.gap.to_numpy() > 0), ("gap down", D.gap.to_numpy() < 0)):
        for sl, sm in (("open below flip", below), ("open above flip", ~below)):
            m = gm & sm
            cells.append({"asset": sym, "gap": gl, "state": sl, "days": int(m.sum()), "continued": float(cont[m].mean()) if m.any() else np.nan,
                          "gap filled by the close": float(filled[m].mean()) if m.any() else np.nan,
                          "median close vs open, in gap direction %": float(100 * np.median((np.sign(D.gap) * (D.close / D.open - 1)).to_numpy()[m])) if m.any() else np.nan})
    return {"asset": sym, "gap days": len(D), "below flip": int(below.sum()), "above flip": int((~below).sum()),
            "P(continue | below)": float(cont[below].mean()), "P(continue | above)": float(cont[~below].mean()), "difference": float(obs),
            "p (one-sided)": float(p), "smallest possible p": float(1 / (len(offs) + 1)),
            "P(fill | below)": float(filled[below].mean()), "P(fill | above)": float(filled[~below].mean()),
            "passes (TSLA, p < 0.05, positive)": bool(sym == "TSLA" and p < 0.05 and obs > 0)}, cells


def figure(r1, r2, cells, days):
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                         "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False})
    f, (a, b) = plt.subplots(1, 2, figsize=(14, 5.4), gridspec_kw={"wspace": 0.35})
    keys = ["(a) open", "(b) day high and low", "(c) premarket high and low"]
    ev = [r1[k]["events"] for k in keys]
    obs = [100 * r1[k]["hit rate"] for k in keys]
    exp = [100 * r1[k]["null mean hits (round-matched)"] / e for k, e in zip(keys, ev)]
    exd = [100 * r1[k]["post-hoc distance+round-matched null mean hits"] / e for k, e in zip(keys, ev)]
    y = np.arange(len(keys))[::-1]
    a.barh(y + 0.27, obs, height=0.25, color=BLUE, label="landed on one of the 3 biggest-OI strikes")
    a.barh(y, exp, height=0.25, color="#bdbcb6", label="expected: equally round strikes anywhere within 10% (pre-registered null)")
    a.barh(y - 0.27, exd, height=0.25, color=MUTED, label="expected: equally round strikes at the same distance (post-hoc null)")
    for yy, k, o in zip(y, keys, obs):
        a.text(o + 0.15, yy + 0.27, f"{o:.1f}%  (p {r1[k]['p (round-matched)']:.3f} pre-reg; {r1[k]['post-hoc p (distance+round-matched)']:.2f} post-hoc)",
               va="center", fontsize=7.5, color=INK)
    a.set_xlim(0, max(obs) * 2.1)
    a.set_yticks(y, [k.split(") ", 1)[1] for k in keys])
    a.set_xlabel("% of events within 1/10 of a strike spacing of a wall")
    a.legend(loc="upper center", bbox_to_anchor=(0.45, -0.13), frameon=False, fontsize=7.5)
    a.set_title("1. Do prices stop at the walls? No: the small excess is because walls sit near the price\nTSLA 2020-2026 (premarket: last ~60 sessions)", loc="left", fontsize=10, color=INK)
    c = pd.DataFrame(cells)
    c = c[c.asset == "TSLA"]
    lab = [f"{g}\n{s.replace('open ', '')}" for g, s in zip(c.gap, c.state)]
    xs = np.arange(len(c))
    cols = [ORANGE if "below" in s else BLUE for s in c.state]
    lite = ["#f6c7b0" if "below" in s else "#bcd3f0" for s in c.state]
    b.bar(xs - 0.2, 100 * c.continued, color=cols, width=0.38)
    b.bar(xs + 0.2, 100 * c["gap filled by the close"], color=lite, width=0.38)
    for i, (v, fl, n) in enumerate(zip(c.continued, c["gap filled by the close"], c.days)):
        b.text(i - 0.2, 100 * v + 1, f"{100 * v:.0f}%", ha="center", va="bottom", fontsize=8, color=INK)
        b.text(i + 0.2, 100 * fl + 1, f"{100 * fl:.0f}%", ha="center", va="bottom", fontsize=8, color=INK)
        b.text(i, -9, f"{n} days", ha="center", va="top", fontsize=7.5, color=MUTED)
    from matplotlib.patches import Patch
    b.legend(handles=[Patch(color=MUTED, label="moved further in the gap's direction (solid)"),
                      Patch(color="#d8d7d2", label="gap fully filled by the close (light)")], loc="upper right", frameon=False, fontsize=8)
    b.axhline(50, color=MUTED, ls=":", lw=1)
    b.set_xticks(xs, lab, fontsize=8.5)
    b.set_ylim(0, 85)
    b.set_ylabel("% of gap days")
    t = r2["TSLA"]
    b.set_title(f"2. Regime at the open: not the textbook way. TSLA gaps ({t['gap days']} days) opening below the flip\n"
                f"continued less ({100 * t['P(continue | below)']:.0f}% vs {100 * t['P(continue | above)']:.0f}%, p {t['p (one-sided)']:.2f}) and were filled more "
                f"({100 * t['P(fill | below)']:.0f}% vs {100 * t['P(fill | above)']:.0f}%)",
                loc="left", fontsize=10, color=INK)
    b.set_axisbelow(True)
    b.grid(axis="y", color=GRID)
    f.savefig(OUT / "gaps_walls.png", dpi=150, bbox_inches="tight", facecolor=SURF)


def main():
    OUT.mkdir(exist_ok=True)
    r1, days = g1()
    r2, cells = {}, []
    for s in ("TSLA", "MSFT", "SPY", "QQQ"):
        r, c = g2(s)
        r2[s] = r
        cells += c
    (OUT / "g1.json").write_text(json.dumps(r1, indent=1, default=float))
    (OUT / "g2.json").write_text(json.dumps(r2, indent=1, default=float))
    pd.DataFrame(cells).to_csv(OUT / "g2_cells.csv", index=False)
    figure(r1, r2, cells, days)
    return r1, r2, cells


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    r1, r2, cells = main()
    print(json.dumps(r1, indent=1, default=lambda v: round(float(v), 4)))
    print(json.dumps(r2, indent=1, default=lambda v: round(float(v), 4)))
    print(pd.DataFrame(cells).round(3).to_string(index=False))
