"""Ex-ante volatility and average correlation, from daily bars, as known at each month end and each Friday.

  data/vol_monthly.pkl     per stock and month: sig_m = std of daily log returns over the trailing 126 sessions x sqrt(21)
  out/avgcorr.csv          average pairwise correlation of daily returns across the stock universe (tech + non-tech),
                           trailing 63 sessions, at month ends and at Fridays
  out/sp_vol_weekly.csv    S&P 500 daily-return vol over the trailing 126 sessions x sqrt(5), at Fridays
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
PREV = HERE.parent / "2026-10-15-channel-reversion-macro"
sys.path.insert(0, str(PREV))
import build_panel as BP          # noqa: E402
import fetch_data as FD           # noqa: E402
from build import STOCKS as NONTECH  # noqa: E402

DATA, OUT = HERE / "data", HERE / "out"


def daily_returns():
    cols = {}
    for base, syms in ((PREV / "data", FD.STOCKS), (DATA, NONTECH)):
        BP.DATA = base
        for s in syms:
            if (base / "yahoo" / f"{s}.json").exists():
                d = BP.load_yahoo(s)
                cols[s] = np.log(d.adjclose).diff()
    return pd.DataFrame(cols).sort_index()


def avg_corr(R, dates, win=63, min_names=20):
    out = {}
    idx = R.index.to_numpy("datetime64[ns]")
    for dt in dates:
        j = np.searchsorted(idx, np.datetime64(dt), side="right")
        if j < win:
            continue
        X = R.iloc[j - win:j]
        X = X.loc[:, X.notna().all() & (X.std() > 0)]
        if X.shape[1] < min_names:
            continue
        Z = (X - X.mean()) / X.std()
        n = Z.shape[1]
        s = Z.sum(axis=1)
        out[dt] = float((s.var() - n) / (n * (n - 1)))
    return pd.Series(out)


def main():
    R = daily_returns()
    rows = []
    for s in R.columns:
        r = R[s].dropna()
        sig = r.rolling(126, min_periods=100).std() * np.sqrt(21)
        me = sig.resample("ME").last()
        rows.append(pd.DataFrame({"symbol": s, "month": me.index, "sig_m": me.to_numpy()}))
    pd.concat(rows).dropna().to_pickle(DATA / "vol_monthly.pkl")

    months = pd.date_range("1975-01-31", R.index[-1] + pd.offsets.MonthEnd(0), freq="ME")
    fridays = pd.date_range("1975-01-03", R.index[-1] + pd.Timedelta(days=6), freq="W-FRI")
    ac = pd.concat({"monthly": avg_corr(R, months), "weekly": avg_corr(R, fridays)}, axis=1, sort=True)
    ac.index.name = "date"
    ac.to_csv(OUT / "avgcorr.csv", float_format="%.5f")

    BP.DATA = DATA
    spx = BP.load_yahoo("GSPC_long").close
    v = np.log(spx).diff().rolling(126, min_periods=100).std() * np.sqrt(5)
    v = v.resample("W-FRI").last().rename("sig_w").to_frame()
    v.index.name = "Date"
    v.to_csv(OUT / "sp_vol_weekly.csv", float_format="%.6f")
    print("vol rows", sum(len(x) for x in rows), "| avgcorr monthly", ac.monthly.notna().sum(),
          "from", ac.monthly.first_valid_index().date(), "| weekly", ac.weekly.notna().sum())


if __name__ == "__main__":
    main()
