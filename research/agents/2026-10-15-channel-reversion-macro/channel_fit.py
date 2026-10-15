"""fit_channel copied verbatim from research/microstructure/channels.py @ 2c6250c (owner's study; not edited).

Tightest robust parallel channel in log space: slope b minimises q-quantile width of (log high - b t) and
(log low - b t). Returns intercept a (channel centre at t=0), slope b, lower and upper offsets from the centre, and the
R^2 of log close on the centre line.
"""
import numpy as np
from scipy.optimize import minimize_scalar


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
