"""Shared order-flow tools: market-order merging, signing, Kyle lambda, Hawkes MLE (exponential kernel), propagator."""
import numpy as np
import pandas as pd
from numba import njit
from scipy.optimize import minimize


def load_trades(path, tick_rule_for_unsigned=True):
    d = pd.read_parquet(path, columns=["ts_event", "price", "size", "side"])
    d = d[d["size"] > 0].copy()
    d["size"] = d["size"].astype(np.int64)
    s = np.where(d.side == "B", 1, np.where(d.side == "A", -1, 0)).astype(np.int8)
    if tick_rule_for_unsigned and (s == 0).any():
        p = d.price.to_numpy(); dp = np.sign(np.diff(p, prepend=p[0]))
        tr = pd.Series(np.where(dp == 0, np.nan, dp)).ffill().fillna(0).to_numpy()
        s = np.where(s == 0, tr, s).astype(np.int8)
    d = d.assign(sign=s)
    return d


def merge_orders(d):
    """One aggressive order that sweeps several resting orders prints several trades with one timestamp and side."""
    key = (d.ts_event.astype("int64").to_numpy(), d.sign.to_numpy())
    g = d.groupby([key[0], key[1]], sort=False)
    m = pd.DataFrame({"t": g.ts_event.first(), "sign": g.sign.first(), "size": g["size"].sum(), "price": g.price.last()}).reset_index(drop=True)
    return m.sort_values("t", kind="stable").reset_index(drop=True)


def kyle_lambda(d, freq="5min"):
    x = d.set_index("ts_event")
    sv = (x["size"] * x.sign).resample(freq).sum(); px = x.price.resample(freq).last().ffill()
    dp = px.diff().iloc[1:]; sv = sv.iloc[1:]
    if len(dp) < 10 or sv.std() == 0:
        return np.nan, np.nan
    b = np.polyfit(sv.to_numpy(), dp.to_numpy(), 1)[0]
    r2 = np.corrcoef(sv, dp)[0, 1] ** 2
    return float(b), float(r2)


@njit(cache=True)
def _hawkes_nll(t, mu, n, beta, T):
    # lambda(t) = mu + n*beta*sum exp(-beta (t - t_i)); compensator = mu T + n sum (1 - exp(-beta (T - t_i)))
    A = 0.0; ll = 0.0
    for i in range(len(t)):
        if i > 0:
            A = np.exp(-beta * (t[i] - t[i - 1])) * (1.0 + A)
        lam = mu + n * beta * A
        if lam <= 0:
            return 1e100
        ll += np.log(lam)
    comp = mu * T
    for i in range(len(t)):
        comp += n * (1.0 - np.exp(-beta * (T - t[i])))
    return -(ll - comp)


def hawkes_fit(t, T):
    """t: event times in seconds from window start (sorted). Returns (mu, n, beta)."""
    t = np.asarray(t, float)
    if len(t) < 200:
        return np.nan, np.nan, np.nan
    rate = len(t) / T
    best = None
    for n0, b0 in ((0.5, 1.0), (0.8, 5.0), (0.3, 20.0)):
        x0 = np.array([np.log(rate * (1 - n0)), np.log(n0 / (1 - n0)), np.log(b0)])
        f = lambda x: _hawkes_nll(t, np.exp(x[0]), 1 / (1 + np.exp(-x[1])), np.exp(x[2]), T)
        r = minimize(f, x0, method="Nelder-Mead", options={"maxiter": 600, "xatol": 1e-4, "fatol": 1e-3})
        if best is None or r.fun < best.fun:
            best = r
    x = best.x
    return float(np.exp(x[0])), float(1 / (1 + np.exp(-x[1]))), float(np.exp(x[2]))


def hawkes_day(m, start, minutes=30):
    """Fit per window; m has column t (Timestamp, UTC)."""
    secs = (m.t - start).dt.total_seconds().to_numpy()
    out = []
    for w0 in range(0, 390, minutes):
        a, b = w0 * 60, (w0 + minutes) * 60
        x = secs[(secs >= a) & (secs < b)] - a
        x = np.unique(x)                      # same-nanosecond events -> one (they are one burst)
        mu, n, beta = hawkes_fit(x, b - a)
        out.append((w0, len(x), mu, n, beta))
    return pd.DataFrame(out, columns=["window_min", "events", "mu", "n", "beta"])


def sign_acf(eps, lags):
    e = eps.astype(float); e = e - e.mean(); v = (e * e).mean()
    return np.array([(e[:-L] * e[L:]).mean() / v for L in lags])


def response(eps, p, lags):
    return np.array([np.mean(eps[:-L] * (p[L:] - p[:-L])) for L in lags])


def propagator(eps, p, edges):
    """Delta p_n = sum_k g_k eps_{n-k}; lags grouped in [edges[j], edges[j+1]); returns G(ell) at the bin ends (cumulative)."""
    dp = np.diff(p); e = eps[:-1].astype(float)
    N = len(dp); K = edges[-1]
    cs = np.concatenate([[0.0], np.cumsum(e)])
    X = np.zeros((N - K, len(edges) - 1))
    idx = np.arange(K, N)
    for j in range(len(edges) - 1):
        lo, hi = edges[j], edges[j + 1]
        X[:, j] = (cs[idx - lo + 1] - cs[idx - hi + 1]) / (hi - lo)     # mean sign over lags [lo, hi)
    y = dp[K:]
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    g_per_lag = coef / 1.0                                              # coefficient on the mean = sum of g over the bin
    G = np.cumsum(g_per_lag)
    return np.array(edges[1:]), G
