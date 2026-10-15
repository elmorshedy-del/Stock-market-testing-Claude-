"""Does a stock's OWN dealer gamma (from its option open interest) explain its moves?
Run after td_pull.py + td_gamma.py. Analysis window 2021+ (2020 = percentile warm-up).

Gamma state going INTO session t (OI is the prior day's close):
  g_norm   net GEX (classic convention) / (spot * total OI * 100), comparable across splits
  g_pct    g_norm percentile vs its trailing year
  below    spot below the stock's own gamma flip
  share1   share of |gamma| expiring within 1 trading day (Fridays: what rolls off)

Tests
  1. next-session |move| vs g_pct, with controls (past 5/20d vol, past 20d return,
     S&P gamma percentile) and a circularly shifted null
  2. bursts (+-5% 1d / +-9% 2d) within the next 3 sessions by gamma tercile and flip side
  3. Monday effect: Monday up-bursts vs the gamma that expired the Friday before
  4. cross-checks: SPY gamma vs SqueezeMetrics GEX; TSLA vs the HistoricalData.net sample
Usage: python stock_gamma.py TSLA [MSFT MU NVDA ...]
"""
import sys

import numpy as np
import pandas as pd
from numpy.linalg import lstsq
from scipy.stats import binom

from common import DATA, OUT, load_bars
from forecast import build as spx_frame
from stock_now import burst_days

START = "2021-01-01"


def frame(sym):
    m = pd.read_csv(OUT / f"td_gamma_{sym}.csv", parse_dates=["date"]).set_index("date").sort_index()
    b = load_bars(sym)
    c = b.close
    r = np.log(c).diff()
    x = pd.DataFrame(index=m.index.intersection(c.index))
    m = m.reindex(x.index)
    x["spot"] = m.spot
    x["g_norm"] = m.gex_classic / (m.spot * (m.call_oi + m.put_oi) * 100)
    x["g_pct"] = x.g_norm.rolling(252, min_periods=120).rank(pct=True)
    x["below"] = (m.spot < m.flip_classic) | (m.flip_classic.isna() & (m.gex_classic <= 0))   # no flip in range + negative gamma
    x["flip"], x["call_wall"], x["put_wall"] = m.flip_classic, m.call_wall, m.put_wall
    x["share1"] = m.gamma_share_1d
    x["ret0"] = r.reindex(x.index)
    x["abs0"] = x.ret0.abs()
    x["abs1"] = x.abs0.shift(-1)          # next session's |move|: the state is read at the close of t
    up, dn = pd.Series(burst_days(c, 1), index=c.index), pd.Series(burst_days(c, -1), index=c.index)
    x["up0"], x["dn0"] = up.reindex(x.index), dn.reindex(x.index)
    # bursts in sessions t+1..t+k only: the state uses day t's close, so a burst ON day t is what put it there
    fwd = lambda s, k: s.shift(-1)[::-1].rolling(k, min_periods=1).max()[::-1].reindex(x.index).fillna(0)
    x["up3"], x["dn3"] = fwd(up, 3).astype(bool), fwd(dn, 3).astype(bool)
    x["any3"] = x.up3 | x.dn3
    # volatility-scaled bursts: a day beyond 2x the stock's own prior 60-day daily vol (comparable across tickers)
    sig = r.rolling(60).std().shift(1)
    sup, sdn = (r >= 2 * sig).astype(float), (r <= -2 * sig).astype(float)
    x["sup3"], x["sdn3"] = fwd(sup, 3).astype(bool), fwd(sdn, 3).astype(bool)
    # controls known at the close of t (outcomes start at t+1)
    x["rv5_past"] = (r.rolling(5).std() * np.sqrt(252)).reindex(x.index)
    x["rv20_past"] = (r.rolling(20).std() * np.sqrt(252)).reindex(x.index)
    x["ret20_past"] = np.log(c).diff(20).reindex(x.index)
    x["abs5_past"] = np.log(c).diff(5).abs().reindex(x.index)
    f = spx_frame()
    x["spx_gex_pct"] = f.gex_pct.reindex(x.index).ffill(limit=3)
    x["weekday"] = x.index.day_name()
    return x


def partial_corr(rk, f, y, ctrl):
    A = np.c_[np.ones(len(rk)), rk[ctrl]]
    a = rk[f] - A @ lstsq(A, rk[f], rcond=None)[0]
    b = rk[y] - A @ lstsq(A, rk[y], rcond=None)[0]
    return float(np.corrcoef(a, b)[0, 1]), a, b


def shifted_null(a, b, n=2000, seed=1):
    rng = np.random.default_rng(seed)
    obs = np.corrcoef(a, b)[0, 1]
    null = np.array([np.corrcoef(np.roll(a, s), b)[0, 1] for s in rng.integers(60, len(a) - 60, n)])
    return float(np.mean(null <= obs))


def test_moves(x):
    ctrl = CTRL
    z = x[x.index >= START].dropna(subset=["g_pct", "abs1"] + ctrl)
    rk = z[["g_pct", "abs1"] + ctrl].rank()
    raw = rk.g_pct.corr(rk.abs1)
    pc, a, b = partial_corr(rk, "g_pct", "abs1", ctrl)
    return {"days": len(z), "raw_rank_corr": raw, "controlled": pc, "shifted_null_p": shifted_null(a.to_numpy(), b.to_numpy())}


def burst_table(x):
    z = x[x.index >= START].dropna(subset=["g_pct"]).copy()
    z["gamma"] = pd.qcut(z.g_pct, 3, labels=["low own gamma", "mid", "high own gamma"])
    t = z.groupby("gamma", observed=True).agg(days=("abs1", "size"), avg_move_pct=("abs1", lambda s: 100 * s.mean()),
                                              p_up_burst_3d=("up3", "mean"), p_dn_burst_3d=("dn3", "mean"))
    f = z.groupby(np.where(z.below, "below own flip", "above own flip")).agg(
        days=("abs1", "size"), avg_move_pct=("abs1", lambda s: 100 * s.mean()), p_up_burst_3d=("up3", "mean"),
        p_dn_burst_3d=("dn3", "mean"))
    # binomial: are bursts over-represented on low-gamma days?
    for col in ("up3", "dn3"):
        n_b = int(z[col].sum())
        k = int(z.loc[z.gamma == "low own gamma", col].sum())
        share = (z.gamma == "low own gamma").mean()
        t.loc["low own gamma", f"p_more_{col}"] = binom.sf(k - 1, n_b, share) if n_b else np.nan
    return t, f


CTRL = ["rv5_past", "rv20_past", "ret20_past", "abs5_past", "spx_gex_pct"]


def burst_logit(x, target, feature, seed=2, n=500, ctrl=CTRL):
    """Logit of a burst in the next 3 sessions on an own-gamma feature with controls (5/20d vol and
    |5d| move through day t, past 20d return, S&P gamma pct); p from circular shifts of the feature."""
    from backtest import logit_fit
    z = x[x.index >= START].dropna(subset=[feature] + ctrl)
    C = z[ctrl].to_numpy()
    C = (C - C.mean(0)) / C.std(0)
    f = z[feature].to_numpy(float)
    y = z[target].to_numpy(float)
    coef = lambda ff: logit_fit(np.c_[ff, C], y, lam=1e-6)[1]
    obs = coef(f)
    rng = np.random.default_rng(seed)
    null = np.array([coef(np.roll(f, s)) for s in rng.integers(60, len(z) - 60, n)])
    p = float(np.mean(null >= obs)) if obs > 0 else float(np.mean(null <= obs))
    return {"odds_ratio": float(np.exp(obs)), "shifted_null_p": p}


def monday_test(x):
    """Share of gamma that expires on Friday, measured on the Thursday row (contracts within
    1 trading day), vs the following Monday."""
    z = x[x.index >= START].copy()
    idx = z.index
    rows = []
    for i, d in enumerate(idx[:-2]):
        if d.day_name() == "Thursday" and idx[i + 1].day_name() == "Friday" and idx[i + 2].day_name() == "Monday":
            mon = z.loc[idx[i + 2]]
            rows.append({"thursday": d, "fri_share1": z.share1.iloc[i], "mon_up": bool(mon.up0), "mon_dn": bool(mon.dn0),
                         "mon_ret": mon.ret0, "mon_g_pct": mon.g_pct})
    m = pd.DataFrame(rows).dropna(subset=["fri_share1"])
    m["expiring"] = pd.qcut(m.fri_share1, 3, labels=["little gamma expired Fri", "mid", "lots of gamma expired Fri"])
    return m.groupby("expiring", observed=True).agg(mondays=("mon_up", "size"), up_bursts=("mon_up", "sum"),
                                                   p_up=("mon_up", "mean"), dn_bursts=("mon_dn", "sum"),
                                                   avg_mon_ret_pct=("mon_ret", lambda s: 100 * s.mean()),
                                                   avg_abs_mon_pct=("mon_ret", lambda s: 100 * s.abs().mean()))


def cross_checks():
    out = {}
    try:
        spy = pd.read_csv(OUT / "td_gamma_SPY.csv", parse_dates=["date"]).set_index("date").gex_classic
        dix = pd.read_csv(DATA / "DIX.csv", parse_dates=["date"]).set_index("date").gex
        j = pd.concat([spy, dix], axis=1, keys=["spy", "sqz"]).dropna()
        out["SPY gamma vs SqueezeMetrics GEX"] = f"corr {j.spy.corr(j.sqz):.2f}, daily changes {j.spy.diff().corr(j.sqz.diff()):.2f}, n={len(j)}"
    except FileNotFoundError:
        pass
    return out


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print(cross_checks())
    for sym in sys.argv[1:] or ["TSLA"]:
        x = frame(sym)
        x.to_csv(OUT / f"stock_gamma_frame_{sym}.csv")
        print(f"\n===== {sym}  ({START} .. {x.index[-1].date()})")
        print("1. next-session |move| vs own gamma percentile:", {k: round(v, 3) if isinstance(v, float) else v for k, v in test_moves(x).items()})
        t, f = burst_table(x)
        print("2. bursts within 3 sessions by own-gamma tercile\n" + t.round(3).to_string())
        print("   by side of the stock's own gamma flip\n" + f.round(3).to_string())
        x["low_g"] = (x.g_pct <= 1 / 3).astype(float)
        for tgt in ("dn3", "up3", "sdn3", "sup3"):
            for feat in ("below", "low_g"):
                x[feat] = x[feat].astype(float)
                r = burst_logit(x, tgt, feat)
                print(f"2b. {tgt} ~ {feat} + past vol + past 20d return + S&P gamma: odds ratio {r['odds_ratio']:.2f}, "
                      f"shifted-null p {r['shifted_null_p']:.3f}")
        z = x[x.index >= START].dropna(subset=["g_pct"])
        print("2c. vol-scaled bursts (day beyond 2x own 60d vol) within 3 sessions:\n" +
              z.groupby(np.where(z.below.astype(bool), "below own flip", "above own flip")).agg(
                  days=("sup3", "size"), p_up=("sup3", "mean"), p_dn=("sdn3", "mean")).round(3).to_string())
        print("3. Monday after Friday expiry, by share of gamma that expired Friday\n" + monday_test(x).round(3).to_string())
        now = x.iloc[-1]
        print(f"NOW {x.index[-1].date()}: spot {now.spot:.2f}, own gamma pct {now.g_pct:.2f}, flip {now.flip:.1f} "
              f"({'BELOW' if now.below else 'above'}), call wall {now.call_wall:.0f}, put wall {now.put_wall:.0f}")
