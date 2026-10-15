"""Does positioning decide HOW an earnings surprise gets priced?

Event days are detected from prices: per stock and calendar quarter, the
highest-volume day with volume >= 2.5x its 50-day median and a gap >= 2 daily
sigmas. For large caps that is almost always the earnings reaction.
(Index ETFs are excluded.)

Split every reaction into
    R0  = day-0 move (gap + session), sign s = sign(R0)
    D   = market-adjusted drift over days 1..10, signed by s
          (D > 0: the move kept going / was under-priced on day 0;
           D < 0: it faded / was over-priced on day 0)
and test which pre-event microstructure proxies predict D:
    opex_days      trading days from the event to the next monthly opex
                   (OI at nearby strikes still alive vs already expired)
    gex_pct        S&P dealer gamma percentile on day -1 (SqueezeMetrics)
    pre_align      s * prior 40-day return: + = surprise WITH the crowd
                   (beat after a run-up), - = against it (beat after a drawdown)
    rv_pre         20-day realized vol before (proxy for how much was priced)
    surprise_size  |R0| / pre-event daily sigma
    clv0           s * close location on day 0 (closed at the extreme = absorbed)
"""
import numpy as np
import pandas as pd

from backtest import third_fridays
from common import DATA, load_bars
from fetch import UNIVERSE

H = 10
ETFS = {"SPY", "QQQ"}


def gex_pct():
    g = pd.read_csv(DATA / "DIX.csv", parse_dates=["date"]).set_index("date").gex
    return g.rolling(252).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True)


def events():
    spy = np.log(load_bars("SPY").close)
    gp = gex_pct()
    rows = []
    for sym in (s for s in UNIVERSE if s not in ETFS):
        df = load_bars(sym)
        lc = np.log(df.close)
        r = lc.diff()
        sig = r.rolling(60).std().shift(1)
        vol_x = df.volume / df.volume.rolling(50).median().shift(1)
        gap = np.log(df.open / df.close.shift())
        cand = df[(vol_x >= 2.5) & (gap.abs() >= 2 * sig)].index
        opex = pd.DatetimeIndex(sorted(third_fridays(df.index)))
        m = spy.reindex(df.index).ffill()
        for _, days in pd.Series(cand, index=cand).groupby(cand.to_period("Q")):
            d = vol_x.loc[days].idxmax()
            j = df.index.get_loc(d)
            if j < 60 or j + H >= len(df):
                continue
            R0 = r.iloc[j]
            s = np.sign(R0)
            ab = lambda a, b: (lc.iloc[b] - lc.iloc[a]) - (m.iloc[b] - m.iloc[a])
            nxt = opex[opex >= d]
            rng = df.high.iloc[j] - df.low.iloc[j]
            rows.append({
                "sym": sym, "date": d, "R0": R0, "s": s,
                "D1": s * ab(j, j + 1), "D5": s * ab(j, j + 5), "D10": s * ab(j, j + H),
                "opex_days": int(df.index.searchsorted(nxt[0]) - j) if len(nxt) else np.nan,
                "gex_pct": gp.asof(df.index[j - 1]) if df.index[j - 1] >= gp.index[0] else np.nan,
                "pre_align": s * (lc.iloc[j - 1] - lc.iloc[j - 41]),
                "rv_pre": r.iloc[j - 20:j].std() * np.sqrt(252),
                "surprise_size": abs(R0) / sig.iloc[j],
                "clv0": s * (((df.close.iloc[j] - df.low.iloc[j]) - (df.high.iloc[j] - df.close.iloc[j])) / rng if rng else 0),
                "gap_share": gap.iloc[j] / R0 if R0 else np.nan,   # how much happened before the open
            })
    return pd.DataFrame(rows)


def table(e, col, bins, labels=None):
    g = e.groupby(pd.cut(e[col], bins, labels=labels), observed=True)
    rng = np.random.default_rng(0)

    def ci(x):
        b = [rng.choice(x.to_numpy(), len(x)).mean() for _ in range(1000)]
        return f"[{1e4*np.quantile(b, .025):+.0f}, {1e4*np.quantile(b, .975):+.0f}]"
    return pd.DataFrame({"n": g.size(), "D1_bp": 1e4 * g.D1.mean(), "D10_bp": 1e4 * g.D10.mean(),
                         "D10_ci95": g.D10.apply(ci), "p_continue": g.D10.apply(lambda x: (x > 0).mean())}).round(2)


def regression(e, feats):
    x = e.dropna(subset=feats + ["D10"])
    X = (x[feats] - x[feats].mean()) / x[feats].std()
    X = np.c_[np.ones(len(x)), X.clip(-4, 4)]
    y = x.D10.to_numpy()
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    # cluster bootstrap by calendar month
    m = x.date.dt.to_period("M").to_numpy()
    um = np.unique(m)
    rng = np.random.default_rng(1)
    bs = []
    for _ in range(500):
        pick = np.concatenate([np.where(m == u)[0] for u in rng.choice(um, len(um))])
        bs.append(np.linalg.lstsq(X[pick], y[pick], rcond=None)[0])
    se = np.std(bs, axis=0)
    return pd.DataFrame({"coef_bp_per_sd": 1e4 * beta, "t": beta / se}, index=["const"] + feats).round(2), len(x)


if __name__ == "__main__":
    pd.set_option("display.width", 200)
    e = events()
    e.to_csv(DATA.parent / "out" / "earnings_events.csv", index=False)
    print(f"events {len(e)}  stocks {e.sym.nunique()}  {e.date.min().date()}..{e.date.max().date()}")
    print(f"mean signed drift D10 {1e4*e.D10.mean():+.0f} bp, P(continue) {(e.D10 > 0).mean():.2f}")
    print("\nby trading days to next monthly opex\n", table(e, "opex_days", [-1, 2, 5, 10, 30], ["0-2 (opex wk)", "3-5", "6-10", "11+"]))
    print("\nby S&P dealer gamma percentile (day -1)\n", table(e, "gex_pct", [-.01, .2, .5, .8, 1.01]))
    print("\nby alignment with prior 40d trend (s * ret40)\n", table(e, "pre_align", [-9, -.1, -.02, .02, .1, 9],
          ["against, big", "against", "flat", "with", "with, big"]))
    print("\nby day-0 close location (signed)\n", table(e, "clv0", [-1.01, -.3, .3, .6, 1.01], ["faded", "middle", "strong", "at extreme"]))
    print("\nby share of move in the gap\n", table(e, "gap_share", [-9, .5, 1, 1.5, 9], ["<50%", "50-100%", "100-150% (faded intraday)", ">150%"]))
    feats = ["opex_days", "gex_pct", "pre_align", "rv_pre", "surprise_size", "clv0", "gap_share"]
    reg, n = regression(e, feats)
    print(f"\nOLS on D10 (n={n}, month-clustered bootstrap t)\n", reg)
