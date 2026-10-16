"""S&P 500 zoomed in: weekly bars back to 1928, weekly ex-ante channels, and a weekly table of signals' raw values
as known at each Friday close.

Writes data/sp_weekly.pkl (bars), data/sp_channels.pkl (W = 104, 156, 260 weeks), out/sp_macro_weekly.csv.

Known-at rules (Friday close t): daily market series (S&P, VIX, VIX3M, dollar, HYG, IEF, S&P GEX/DIX, TIPS) use the
last value on or before t; H.15 daily rates the last business day on or before t; H.4.1 the last Wednesday at least
2 days before t; monthly series (M2, margin debt, margin credit, CPI) become known at the end of the following month.
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
PREV = HERE.parent / "2026-10-15-channel-reversion-macro"
sys.path.insert(0, str(PREV))
import build_panel as BP          # noqa: E402
import channels_panel as CP       # noqa: E402
import fetch_data as FD           # noqa: E402

DATA, OUT = HERE / "data", HERE / "out"
PDATA = PREV / "data"
WEEKS = (104, 156, 260)


def yahoo_long(sym, start_epoch, name):
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?period1={start_epoch}"
           f"&period2={int(time.time())}&interval=1d&includePrePost=false&events=div%2Csplit")
    FD.curl(url, DATA / "yahoo" / f"{name}.json", refresh=True)


def weekly(d, today):
    w = d.resample("W-FRI").agg({"high": "max", "low": "min", "close": "last", "adjclose": "last",
                                 "volume": "sum"}).dropna(subset=["close"])
    w["partial"] = w.index > today          # unfinished week
    return w


def asof(series, idx, lag_days=0):
    s = series.dropna().sort_index()
    pos = np.searchsorted(s.index.to_numpy("datetime64[ns]"),
                          (idx - pd.Timedelta(days=lag_days)).to_numpy("datetime64[ns]"), side="right") - 1
    out = np.where(pos >= 0, s.to_numpy(float)[np.clip(pos, 0, None)], np.nan)
    return pd.Series(out, index=idx)


def monthly_known_next_month_end(s_month_end, idx):
    """A monthly value for month m becomes usable at the end of month m+1."""
    known = s_month_end.copy()
    known.index = known.index + pd.offsets.MonthEnd(1)
    return asof(known, idx)


def main():
    BP.DATA = DATA
    (DATA / "yahoo").mkdir(parents=True, exist_ok=True)
    yahoo_long("%5EGSPC", -1325635200, "GSPC_long")       # from 1928
    yahoo_long("%5EVIX3M", 0, "VIX3M")
    d = BP.load_yahoo("GSPC_long")
    today = d.index[-1]
    wk = weekly(d, today)
    wk.to_pickle(DATA / "sp_weekly.pkl")
    frames = [CP.frame_for("^GSPC", wk, W) for W in WEEKS]
    ch = pd.concat(frames)
    ch["growth_yr"] = np.exp(52 * ch.b) - 1
    ch.rename(columns={"month": "week"}, inplace=True)
    ch.to_pickle(DATA / "sp_channels.pkl")

    idx = wk.index
    m = pd.DataFrame(index=idx)
    BP.DATA = PDATA
    r = BP.fed_series("H15", ["RIFSPFF_N.B", "RIFLGFCY10_N.B", "RIFLGFCM03_N.B"])
    h41 = BP.fed_series("H41", ["RESPPMA_N.WW", "RESPPLLDT_N.WW", "RESPPLLRD_N.WW"])
    ff, y10, y3m = (asof(r[k], idx) for k in ("RIFSPFF_N.B", "RIFLGFCY10_N.B", "RIFLGFCM03_N.B"))
    m["FF_HIKE"] = ff - asof(r["RIFSPFF_N.B"], idx, 364)
    m["FAST_HIKE"] = (m.FF_HIKE >= 1.5).astype(float).where(m.FF_HIKE.notna())
    m["Y10_UP"] = y10 - asof(r["RIFLGFCY10_N.B"], idx, 182)
    m["CURVE_FLAT"] = -(y10 - y3m)

    def yclose(sym, base=PDATA):
        BP.DATA = base
        return BP.load_yahoo(sym).adjclose
    dxy = yclose("DX-Y.NYB")
    m["USD_UP"] = np.log(asof(dxy, idx) / asof(dxy, idx, 182))
    macro = pd.read_csv(PREV / "out" / "macro_monthly.csv", parse_dates=["month"], index_col="month")
    # macro_monthly already stores M2 and margin YoY at the month they became known (shifted one month); undo the
    # shift to recover the data month, then apply the weekly known-at rule
    m2 = macro.m2_yoy.shift(-1)
    mg = macro.margin_yoy.shift(-1)
    m["M2_SLOW"] = -monthly_known_next_month_end(m2, idx)
    m["MARGIN_FROTH"] = monthly_known_next_month_end(mg, idx)
    w = pd.DataFrame({"a": h41["RESPPMA_N.WW"], "t": h41["RESPPLLDT_N.WW"], "r": h41["RESPPLLRD_N.WW"]}).dropna()
    nl = (w.a - w.t - w.r) / 1000
    m["LIQ_DRAIN"] = -np.log(asof(nl, idx, 2) / asof(nl, idx, 2 + 182))
    tips = pd.concat([pd.read_csv(f, parse_dates=["Date"]) for f in sorted((PDATA / "treasury_real").glob("*.csv"))])
    tips = tips.set_index("Date")["10 YR"].astype(float).sort_index()
    m["TIPS_UP"] = asof(tips, idx) - asof(tips, idx, 182)
    hyg, ief = yclose("HYG"), yclose("IEF")
    m["CREDIT_WIDEN"] = -(np.log(asof(hyg, idx) / asof(hyg, idx, 182)) - np.log(asof(ief, idx) / asof(ief, idx, 182)))
    dix = pd.read_csv(PDATA / "DIX.csv", parse_dates=["date"]).set_index("date")
    m["GEX_LOW"] = -asof(dix.gex.rolling(5).mean(), idx) / 1e9
    m["DIX_LOW"] = -asof(dix.dix.rolling(5).mean(), idx)
    vix = yclose("^VIX")
    m["VIX_HIGH"] = asof(vix, idx)
    vix3m = yclose("VIX3M", DATA)
    m["VIX_INVERT"] = asof(vix, idx) / asof(vix3m, idx)
    fin = pd.read_excel(PDATA / "finra_margin.xlsx")
    fin["d"] = pd.to_datetime(fin.iloc[:, 0].astype(str)) + pd.offsets.MonthEnd(0)
    credit = fin.set_index("d").iloc[:, 3].astype(float).sort_index()
    spx_m = d.close.resample("ME").last()
    m["MARGIN_CREDIT"] = monthly_known_next_month_end(np.log(credit / spx_m.reindex(credit.index)), idx)
    sma52 = wk.close.rolling(52).mean()
    m["TECH_MA"] = (wk.close < sma52).astype(float).where(sma52.notna())
    m.index.name = "week"
    m.to_csv(OUT / "sp_macro_weekly.csv", float_format="%.5f")
    print("S&P weekly bars", len(wk), wk.index[0].date(), "->", wk.index[-1].date(), "| channel rows", len(ch))
    print(m.notna().idxmax().astype(str).to_string())


if __name__ == "__main__":
    main()
