"""Automatic log-linear (parallel) channel detection.

Model: log P(t) = a + b*t + e(t), t = trading-bar index (what a TradingView log
chart uses as its x-axis). A channel is three parallel lines in log space:
    mid   = a + b*t
    upper = mid + q_hi(highs residual)
    lower = mid + q_lo(lows residual)
The slope b is chosen to minimise the robust channel width (upper-lower), i.e.
the tightest strip that contains (1-2*q) of the highs/lows. That is what a human
does by eye: rotate a ruler until most wicks touch but few poke through.
The anchor (start bar) is chosen by searching swing lows and scoring
containment * log(length) / width.
"""
from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize_scalar


@dataclass
class Channel:
    start: int          # bar index of anchor (inclusive) relative to the frame
    end: int            # last bar used (inclusive)
    a: float            # log intercept at bar 0 of the frame
    b: float            # log slope per bar
    lo: float           # lower offset (log)
    hi: float           # upper offset (log)
    r2: float

    def mid(self, t):
        return self.a + self.b * np.asarray(t, float)

    def lines(self, t):
        m = self.mid(t)
        return np.exp(m + self.lo), np.exp(m), np.exp(m + self.hi)

    @property
    def halfwidth(self):
        return (self.hi - self.lo) / 2

    def z(self, t, logp):
        """Position in channel: -1 = lower line, 0 = centre, +1 = upper line."""
        c = self.mid(t) + (self.hi + self.lo) / 2
        return (logp - c) / self.halfwidth

    def annual_growth(self, bars_per_year=252):
        return np.exp(self.b * bars_per_year) - 1


def fit_channel(lh, ll, lc, t, q=0.03):
    """Fit tightest robust parallel channel on log high/low/close arrays."""
    def width(b):
        return np.quantile(lh - b * t, 1 - q) - np.quantile(ll - b * t, q)

    b0 = np.polyfit(t, lc, 1)[0]
    span = max(abs(b0), 1e-4) * 3
    b = minimize_scalar(width, bounds=(b0 - span, b0 + span), method="bounded").x
    hi = np.quantile(lh - b * t, 1 - q)
    lo = np.quantile(ll - b * t, q)
    a = (hi + lo) / 2
    resid = lc - (a + b * t)
    r2 = 1 - resid.var() / lc.var()
    return a, b, lo - a, hi - a, r2


def swing_lows(low, k=10):
    lows = []
    for i in range(k, len(low) - k):
        if low[i] == low[i - k:i + k + 1].min():
            lows.append(i)
    return lows


def detect(df, min_bars=120, max_bars=750, q=0.03, end=None):
    """Search anchors over swing lows; return best Channel on df[:end+1]."""
    end = len(df) - 1 if end is None else end
    lh, ll, lc = (np.log(df[c].to_numpy()) for c in ("high", "low", "close"))
    best, best_score = None, -np.inf
    for s in swing_lows(ll[: end + 1]):
        n = end - s + 1
        if n < min_bars or n > max_bars:
            continue
        t = np.arange(s, end + 1, dtype=float)
        a, b, lo, hi, r2 = fit_channel(lh[s:end + 1], ll[s:end + 1], lc[s:end + 1], t, q)
        if b <= 0:
            continue
        # width measured in units of total log move: a channel is "good" when
        # the trend dominates the noise and it has lasted a long time
        trend = b * n
        score = r2 * np.log(n) * trend / (hi - lo)
        if score > best_score:
            best_score, best = score, Channel(s, end, a, b, lo, hi, r2)
    return best


def touches(ch, df, tol=0.12):
    """Bars whose high/low come within tol*halfwidth of a channel line."""
    t = np.arange(len(df), dtype=float)[ch.start:]
    zh = ch.z(t, np.log(df["high"].to_numpy()[ch.start:]))
    zl = ch.z(t, np.log(df["low"].to_numpy()[ch.start:]))
    up = np.where(zh >= 1 - tol)[0] + ch.start
    dn = np.where(zl <= -1 + tol)[0] + ch.start
    return up, dn


def ou_halflife(resid):
    """AR(1) on channel residual -> mean-reversion half-life in bars."""
    x, y = resid[:-1], resid[1:]
    phi = np.polyfit(x, y, 1)[0]
    return np.inf if phi >= 1 or phi <= 0 else -np.log(2) / np.log(phi), phi


if __name__ == "__main__":
    from common import load_bars
    df = load_bars("MU")
    ch = detect(df)
    lo, mid, up = ch.lines([len(df) - 1])
    print("anchor", df.index[ch.start].date(), "bars", ch.end - ch.start + 1,
          "growth/yr %.0f%%" % (100 * ch.annual_growth()), "r2 %.3f" % ch.r2)
    print("width %.1f%%" % (100 * (np.exp(ch.hi - ch.lo) - 1)))
    print("today lower/mid/upper: %.0f / %.0f / %.0f   close %.2f" % (lo[0], mid[0], up[0], df.close.iloc[-1]))
    print("z today %.2f" % ch.z(len(df) - 1, np.log(df.close.iloc[-1])))
