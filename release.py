"""What 'frees' the index? Event study on the S&P 500, 1990-2026.

Outcome at day t: forward 10-day log return of ^GSPC, and whether it lands in
the top decile of all 10-day windows (an "elevator" leg like Apr / Aug 2026).

Candidate releases (all known at the close of day t, no look-ahead):
  vix_crush    VIX first closes <= 75% of its 20-day max         (vanna fuel)
  ts_flip      VIX/VIX3M back below 0.95 after >1 in last 10d     (backwardation ends)
  rv_release   20d realized vol first < 60% of its 60-day max     (vol-control re-leveraging)
  post_opex    first day after monthly opex                       (gamma roll-off)
  post_quad    first day after quarterly opex (Mar/Jun/Sep/Dec)
  vix_exp      VIX settlement Wednesday                            (VIX hedges roll off)
Plus a quarter-phase table (buyback blackout ~ last 2 weeks of a quarter
until earnings; reopens through the first month).
"""
import numpy as np
import pandas as pd

from backtest import third_fridays
from common import DATA, load_bars

H = 10
GAP = 10   # de-duplicate: an event must be >= GAP days after the previous one


def frame():
    s = load_bars("^GSPC")
    d = pd.DataFrame({"c": s.close})
    for k in ("^VIX", "^VIX3M", "^VIX9D"):
        d[k[1:]] = load_bars(k).close
    d = d[d.index >= "1990-01-02"].ffill()
    d["r"] = np.log(d.c).diff()
    d["fwd"] = np.log(d.c.shift(-H) / d.c)
    d["rv20"] = d.r.rolling(20).std() * np.sqrt(252)
    return d


def first(cond, gap=GAP):
    cond = cond.fillna(False).to_numpy()
    out, last = np.zeros(len(cond), bool), -10**9
    for i in np.where(cond & ~np.r_[False, cond[:-1]])[0]:
        if i - last >= gap:
            out[i], last = True, i
    return out


def triggers(d):
    idx = d.index
    opex = sorted(third_fridays(idx))
    quad = [x for x in opex if x.month in (3, 6, 9, 12)]
    nxt = lambda days: np.isin(np.arange(len(idx)), idx.searchsorted(days, side="right"))
    # VIX settles on the Wednesday 30 days before the following month's SPX opex
    fr = pd.date_range(idx[0], idx[-1] + pd.Timedelta(days=60), freq="WOM-3FRI")
    vexp = pd.DatetimeIndex(fr - pd.Timedelta(days=30))
    T = pd.DataFrame(index=idx)
    T["vix_crush"] = first(d.VIX <= 0.75 * d.VIX.rolling(20).max())
    ratio = d.VIX / d.VIX3M
    T["ts_flip"] = first((ratio < 0.95) & (ratio.rolling(10).max() > 1.0))
    T["rv_release"] = first(d.rv20 < 0.6 * d.rv20.rolling(60).max())
    T["post_opex"] = nxt(opex)
    T["post_quad"] = nxt(quad)
    T["vix_exp"] = idx.isin(vexp)
    return T


def study(d, T, start=None):
    dd, TT = (d, T) if start is None else (d[d.index >= start], T[T.index >= start])
    ok = dd.fwd.notna()
    top = dd.fwd.quantile(0.9)
    big = dd.fwd.abs().quantile(0.9)   # "freed": a top-decile move in either direction
    base = {"n": int(ok.sum()), "mean_fwd_bp": 1e4 * dd.fwd.mean(), "p_elevator": float((dd.fwd > top).mean()),
            "p_big": float((dd.fwd.abs() > big).mean())}
    rows = {}
    rng = np.random.default_rng(0)
    for k in TT:
        f = dd.fwd[TT[k].to_numpy() & ok.to_numpy()]
        if len(f) < 8:
            continue
        bs = [rng.choice(f.to_numpy(), len(f)).mean() for _ in range(2000)]
        rows[k] = {"n": len(f), "mean_fwd_bp": 1e4 * f.mean(),
                   "ci95_bp": (1e4 * np.quantile(bs, 0.025), 1e4 * np.quantile(bs, 0.975)),
                   "p_elevator": float((f > top).mean()), "lift": float((f > top).mean() / 0.1),
                   "p_big": float((f.abs() > big).mean())}
    # stacking: 2+ distinct releases within 5 trading days
    hits = TT.rolling(5, min_periods=1).max().sum(axis=1)
    for n in (2, 3):
        f = dd.fwd[first(hits >= n).astype(bool) & ok.to_numpy()]
        rows[f"stack>={n}"] = {"n": len(f), "mean_fwd_bp": 1e4 * f.mean(),
                               "p_elevator": float((f > top).mean()), "lift": float((f > top).mean() / 0.1),
                               "p_big": float((f.abs() > big).mean())}
    return base, pd.DataFrame(rows).T


def quarter_phase(d):
    q = d.copy()
    q["m_in_q"] = (q.index.month - 1) % 3          # 0 = first month of quarter
    q["half"] = np.where(q.index.day <= 15, "1-15", "16-31")
    g = q.groupby(["m_in_q", "half"]).fwd
    return pd.DataFrame({"mean_fwd_bp": 1e4 * g.mean(), "p_up": g.apply(lambda x: (x > 0).mean()),
                         "n": g.size()}).round(2)


def timeline(d, T, a, b):
    x = T.loc[a:b]
    ev = {k: [i.strftime("%m-%d") for i in x.index[x[k]]] for k in T}
    return {k: v for k, v in ev.items() if v}


if __name__ == "__main__":
    pd.set_option("display.width", 200)
    d = frame()
    T = triggers(d)
    for start, lab in ((None, "1990-2026"), ("2007-01-01", "2007-2026 (VIX3M era)")):
        base, tab = study(d, T, start)
        print(f"\n== {lab}  base: {base}")
        print(tab.round(3).to_string())
    print("\nQuarter phase (fwd 10d SPX):\n", quarter_phase(d).to_string())
    for a, b in (("2026-03-01", "2026-04-30"), ("2026-06-20", "2026-08-31")):
        print(f"\nreleases {a}..{b}:", timeline(d, T, a, b))
    fr = pd.date_range("2026-10-01", "2026-12-31", freq="WOM-3FRI")
    print("\nupcoming: monthly opex", [x.strftime("%m-%d") for x in fr],
          "| VIX settlement", [(x - pd.Timedelta(days=30)).strftime("%m-%d") for x in fr[1:]])


# ---------------------------------------------------------------- dealer gamma (SqueezeMetrics, free CSV)
def gex_study(d):
    """GEX = SqueezeMetrics' estimate of S&P dealer gamma ($ per 1%); DIX = dark-pool buy ratio."""
    g = pd.read_csv(DATA / "DIX.csv", parse_dates=["date"]).set_index("date")
    x = d.join(g[["gex", "dix"]], how="inner")
    x["absfwd"] = x.fwd.abs()
    x["fwd_rv"] = x.r[::-1].rolling(H).std()[::-1].shift(-1) * np.sqrt(252)   # realized vol of next H days
    # rank vs trailing year: GEX grows with market cap, so levels must be normalised
    x["gex_pct"] = x.gex.rolling(252).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True)
    x["gex_chg5"] = x.gex.rolling(252).rank(pct=True).diff(5)
    x["dix_pct"] = x.dix.rolling(252).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True)
    x = x.dropna(subset=["gex_pct", "fwd"])
    big, top = x.absfwd.quantile(0.9), x.fwd.quantile(0.9)
    agg = lambda gr: pd.DataFrame({
        "n": gr.size(), "fwd_bp": 1e4 * gr.fwd.mean(), "abs_move_bp": 1e4 * gr.absfwd.mean(),
        "next10d_rv": gr.fwd_rv.mean(), "p_big": gr.absfwd.apply(lambda v: (v > big).mean()),
        "p_elevator": gr.fwd.apply(lambda v: (v > top).mean())}).round(3)
    out = {
        "by_gex_quintile": agg(x.groupby(pd.qcut(x.gex_pct, 5, labels=False, duplicates="drop"))),
        "gex_negative": agg(x.groupby(x.gex < 0)),
        "by_gex_5d_change": agg(x.groupby(pd.qcut(x.gex_chg5, 5, labels=False, duplicates="drop"))),
        "by_dix_quintile": agg(x.groupby(pd.qcut(x.dix_pct, 5, labels=False, duplicates="drop"))),
    }
    return out, x


if __name__ == "__main__":
    out, x = gex_study(d)
    for k, v in out.items():
        print(f"\n{k}\n{v.to_string()}")
    show = x.loc["2026-03-16":"2026-04-24", ["c", "gex", "gex_pct", "dix"]]
    show2 = x.loc["2026-07-13":"2026-08-14", ["c", "gex", "gex_pct", "dix"]]
    for s_ in (show, show2, x[["c", "gex", "gex_pct", "dix"]].tail(8)):
        print(s_.assign(gex=lambda t: (t.gex / 1e9).round(2)).round(3).to_string())
