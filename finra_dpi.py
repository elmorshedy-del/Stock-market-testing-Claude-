"""Per-stock dark-pool index (DPI) from FINRA's free daily short-sale volume files.

FINRA publishes off-exchange (TRF) volume and the part of it reported as short
sales, per symbol per day. Most off-exchange short volume is market makers
selling short to fill buy orders, so a high short share = buying pressure.
SqueezeMetrics' DIX is the dollar-weighted DPI of S&P 500 members; here DPI is
computed per stock (TSLA, MSFT, MU, ...).

Consolidated files (CNMSshvolYYYYMMDD.txt) exist from Aug 2018; cached per day
for the tickers in KEEP under data/finra/ (gitignored).

Usage: python finra_dpi.py fetch [start]     # incremental download
       python finra_dpi.py test  [SYM ...]   # DPI vs forward moves/bursts
"""
import sys
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd
from scipy.stats import binom

from common import DATA, load_bars
from stock_now import burst_days

URL = "https://cdn.finra.org/equity/regsho/daily/CNMSshvol{:%Y%m%d}.txt"
KEEP = {"TSLA", "MSFT", "MU", "SPY", "QQQ", "NVDA", "AAPL", "AMD", "META", "AMZN", "GOOGL"}
DIR = DATA / "finra"


def fetch_day(d):
    path = DIR / f"{d:%Y%m%d}.csv"
    if path.exists():
        return d, "cached"
    try:
        txt = urlopen(Request(URL.format(d), headers={"User-Agent": "Mozilla/5.0"}), timeout=30).read().decode()
    except Exception as e:                                   # holidays and pre-2018 dates are 403/404
        return d, f"skip {str(e)[:40]}"
    rows = [ln for ln in txt.splitlines()[1:] if ln.split("|")[1:2] and ln.split("|")[1] in KEEP]
    path.write_text("date|symbol|short|short_exempt|total|market\n" + "\n".join(rows) + "\n")
    return d, "ok"


def fetch(start="2018-08-01"):
    DIR.mkdir(parents=True, exist_ok=True)
    days = pd.bdate_range(start, pd.Timestamp.today().normalize() - pd.Timedelta(days=1))
    with ThreadPoolExecutor(8) as ex:
        res = list(ex.map(fetch_day, days))
    print({k: sum(1 for _, s in res if s.startswith(k)) for k in ("ok", "cached", "skip")})


def load():
    parts = [pd.read_csv(p, sep="|") for p in sorted(DIR.glob("*.csv"))]
    d = pd.concat(parts)
    d["date"] = pd.to_datetime(d.date.astype(str))
    d["dpi"] = d.short / d.total
    return d.pivot(index="date", columns="symbol", values="dpi"), d.pivot(index="date", columns="symbol", values="total")


def frame(sym, dpi):
    b = load_bars(sym)
    c = b.close
    x = pd.DataFrame(index=c.index)
    x["dpi"] = dpi[sym].reindex(c.index)
    x["dpi5"] = x.dpi.rolling(5).mean()
    x["dpi_pct"] = x.dpi5.rolling(252, min_periods=120).rank(pct=True)
    lc = np.log(c)
    for h in (5, 10, 20):
        x[f"fwd{h}"] = lc.shift(-h) - lc
    up, dn = burst_days(c, 1), burst_days(c, -1)
    x["up_next10"] = pd.Series(up, index=c.index)[::-1].rolling(10, min_periods=1).max()[::-1].shift(-1)
    x["dn_next10"] = pd.Series(dn, index=c.index)[::-1].rolling(10, min_periods=1).max()[::-1].shift(-1)
    x["ret20_past"] = lc - lc.shift(20)
    return x.dropna(subset=["dpi_pct", "fwd20"])


def test(sym, dpi, start="2019-08-01", seed=5):
    x = frame(sym, dpi)
    x = x[x.index >= start]
    x["tercile"] = pd.qcut(x.dpi_pct, 3, labels=["low DPI", "mid", "high DPI"])
    tab = x.groupby("tercile", observed=True).agg(days=("fwd10", "size"), fwd5_pct=("fwd5", lambda s: 100 * s.mean()),
                                                  fwd10_pct=("fwd10", lambda s: 100 * s.mean()),
                                                  fwd20_pct=("fwd20", lambda s: 100 * s.mean()),
                                                  p_up_burst_10d=("up_next10", "mean"), p_dn_burst_10d=("dn_next10", "mean"))
    # circular-shift null for the high-minus-low 20d return spread (keeps autocorrelation of both series)
    rng = np.random.default_rng(seed)
    hi = (x.tercile == "high DPI").to_numpy()
    lo = (x.tercile == "low DPI").to_numpy()
    f20 = x.fwd20.to_numpy()
    obs = f20[hi].mean() - f20[lo].mean()
    null = []
    for _ in range(2000):
        s = rng.integers(60, len(x) - 60)
        h2, l2 = np.roll(hi, s), np.roll(lo, s)
        null.append(f20[h2].mean() - f20[l2].mean())
    p = float(np.mean(np.array(null) >= obs))
    return tab, obs, p, x


if __name__ == "__main__":
    pd.set_option("display.width", 200)
    cmd = sys.argv[1] if len(sys.argv) > 1 else "test"
    if cmd == "fetch":
        fetch(*sys.argv[2:3])
    else:
        dpi, vol = load()
        print(f"FINRA days {len(dpi)}: {dpi.index[0].date()} .. {dpi.index[-1].date()}")
        for sym in sys.argv[2:] or ["TSLA", "MSFT", "MU", "SPY", "QQQ"]:
            tab, obs, p, x = test(sym, dpi)
            print(f"\n{sym}: DPI (5d mean) percentile vs trailing year, 2019-08+")
            print(tab.round(3).to_string())
            print(f"   high-minus-low DPI 20d fwd return {100 * obs:+.2f} pts, circular-shift null p={p:.3f}")
            cur = dpi[sym].dropna()
            print(f"   latest DPI {cur.iloc[-1]:.3f} on {cur.index[-1].date()}, 5d mean {cur.iloc[-5:].mean():.3f}, "
                  f"pct vs trailing year {cur.rolling(5).mean().iloc[-252:].rank(pct=True).iloc[-1]:.2f}")
