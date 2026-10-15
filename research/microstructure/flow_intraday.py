"""Order-flow proxies from 5-minute bars (no tick/L2 data is free, so these are
approximations, labelled as such):

* Bulk volume classification (Easley, Lopez de Prado, O'Hara 2012):
  buy share of a bar = Phi(dP / sigma_dP). Gives a signed-volume (delta)
  series and cumulative volume delta (CVD) without trade-level data.
* Volume-at-price profile -> point of control (POC) and 70% value area.
* "Block" candidates: 5m bars with volume > 4 robust sigmas above the
  time-of-day norm; where they print vs strikes and channel lines.
* Anchored VWAPs (daily bars) from the channel anchor, the top, and earnings.
* Moving-average thesis: in a log-linear trend with slope b per bar, an N-bar
  SMA trails price by ~ b*(N-1)/2 in log space -> it is a parallel line.
"""
import numpy as np
import pandas as pd
from scipy.stats import norm

from common import load_bars


def bvc(df):
    dp = np.log(df.close).diff()
    sig = dp.rolling(78 * 5, min_periods=50).std()  # 5 sessions of 5m bars
    buy = pd.Series(norm.cdf(dp / sig), index=df.index).fillna(0.5)
    d = df.assign(buy=buy * df.volume, sell=(1 - buy) * df.volume)
    d["delta"] = d.buy - d.sell
    d["cvd"] = d.delta.cumsum()
    return d


def volume_profile(df, bins=120):
    tp = (df.high + df.low + df.close) / 3
    edges = np.geomspace(df.low.min(), df.high.max(), bins + 1)
    vol, _ = np.histogram(tp, bins=edges, weights=df.volume)
    centers = np.sqrt(edges[:-1] * edges[1:])
    poc = centers[vol.argmax()]
    order = np.argsort(vol)[::-1]
    keep = order[: np.searchsorted(np.cumsum(vol[order]), 0.7 * vol.sum()) + 1]
    return centers, vol, poc, centers[keep].min(), centers[keep].max()


def blocks(df, k=4.0):
    tod = df.index.strftime("%H:%M")
    lv = np.log(df.volume.replace(0, np.nan))
    med = lv.groupby(tod).transform("median")
    mad = (lv - med).abs().groupby(tod).transform("median") * 1.4826
    z = (lv - med) / mad
    b = df[z > k].assign(z=z[z > k])
    return b


def anchored_vwap(daily, start):
    d = daily[daily.index >= start]
    tp = (d.high + d.low + d.close) / 3
    return (tp * d.volume).cumsum() / d.volume.cumsum()


def ma_lag_check(daily, ch, ns=(20, 50, 100)):
    """Observed vs predicted log gap between price-channel mid and SMA_N."""
    t = np.arange(len(daily), dtype=float)
    mid = pd.Series(ch.mid(t), index=daily.index)
    res = {}
    for n in ns:
        sma = np.log(daily.close.rolling(n).mean())
        gap = (sma - mid).iloc[ch.start + n:]
        res[n] = {"pred_offset_vs_mid": float(-ch.b * (n - 1) / 2),
                  "obs_mean": float(gap.mean()), "obs_sd": float(gap.std()),
                  "lower_offset": float(ch.lo), "upper_offset": float(ch.hi)}
    return res


def summary():
    m5 = bvc(load_bars("MU", "5m"))
    centers, vol, poc, val, vah = volume_profile(m5)
    day = m5.groupby(m5.index.date).agg(ret=("close", "last"), delta=("delta", "sum"), v=("volume", "sum"))
    day["ret"] = np.log(day.ret).diff()
    b = blocks(m5)
    return {
        "bars": len(m5), "from": str(m5.index[0]), "to": str(m5.index[-1]),
        "poc": float(poc), "value_area": (float(val), float(vah)),
        "corr_daily_delta_ret": float(day[["ret", "delta"]].corr().iloc[0, 1]),
        "cvd_60d_shares": float(m5.cvd.iloc[-1]),
        "cvd_last_5d_shares": float(m5.delta[m5.index >= m5.index[-1].normalize() - pd.Timedelta(days=7)].sum()),
        "n_blocks": len(b),
        "block_prices": b.close.round(0).value_counts().head(8).to_dict(),
        "block_net_delta": float(b.delta.sum()),
    }, m5, (centers, vol), b


if __name__ == "__main__":
    import json
    from channels import detect
    s, *_ = summary()
    print(json.dumps(s, indent=1, default=str))
    daily = load_bars("MU")
    print(json.dumps(ma_lag_check(daily, detect(daily, q=0.15)), indent=1))
