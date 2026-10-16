"""Weekly S&P 500 feature table and outcomes, every value as known at that Friday's close.

build(cutoff=None) -> DataFrame indexed by Friday. With a cutoff, every raw input is truncated at the cutoff first,
so verify_mv.py can check that no feature on or before the cutoff changes (no look-ahead).

Layers (columns are prefixed):
  V_  volatility baseline   VIX, 20- and 126-day realized vol
  M_  slow macro            Fed funds 52w change, 10y 26w change, curve, dollar, M2, CPI, margin debt, Fed liquidity,
                            TIPS, credit, margin credit, Chicago Fed NFCI and its risk/credit/leverage parts
  O_  options/flow/vol      VIX/VIX3M, VIX9D/VIX, VVIX, SKEW, VIX minus realized vol, Cboe put/call (total, equity,
                            index; 10-day means), S&P dealer gamma (GEX) and dark-pool index (DIX)
  R_  momentum and RSI      RSI(14) daily/weekly/monthly, 4/13/26/52-week momentum, 12-1 momentum, weekly MACD
                            histogram, distance from the 40-week average, breadth, RSI bearish divergence
  S_  stretch               3-year weekly channel position and R^2, drawdown from the 52-week high, average correlation
  ERA_ regime flags         zero-commission era (from 2019-10-04), daily-0DTE era (from 2022-05-13)
Outcomes: Y_CORR (10% fall within 13 weeks), Y_BEAR (20% fall within 52 weeks), Y_CHAN (touch of the 3-year
channel's lower line within 26 weeks, valid channels only); NaN where unresolved.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
R1 = HERE.parent / "2026-10-15-channel-reversion-macro"
R2 = HERE.parent / "2026-10-15-channel-reversion-round2"
sys.path.insert(0, str(R1))
import build_panel as BP  # noqa: E402

DATA, OUT = HERE / "data", HERE / "out"
ERA_ZC, ERA_0DTE = pd.Timestamp("2019-10-04"), pd.Timestamp("2022-05-13")


def ycol(base, sym, col="adjclose"):
    BP.DATA = base
    return BP.load_yahoo(sym)[col]


def asof(series, idx, lag_days=0):
    s = series.dropna().sort_index()
    pos = np.searchsorted(s.index.to_numpy("datetime64[ns]"),
                          (idx - pd.Timedelta(days=lag_days)).to_numpy("datetime64[ns]"), side="right") - 1
    return pd.Series(np.where(pos >= 0, s.to_numpy(float)[np.clip(pos, 0, None)], np.nan), index=idx)


def rsi(close, n=14):
    d = close.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn)


def cboe_pc():
    rows = []
    for name in ("totalpc", "equitypc", "indexpc"):
        df = pd.read_csv(DATA / "cboe" / f"{name}.csv", skiprows=2)
        df.columns = [c.strip() for c in df.columns]
        df["DATE"] = pd.to_datetime(df["DATE"].astype(str).str.strip(), format="mixed")
        rows.append(df.set_index("DATE")["P/C Ratio"].astype(float).rename(name))
    arch = pd.concat(rows, axis=1)
    rec = {}
    for f in sorted((DATA / "cboe" / "daily").glob("*.json")):
        d = json.loads(f.read_text())
        r = {x["name"]: float(x["value"]) for x in d["ratios"]}
        rec[pd.Timestamp(f.stem)] = {"totalpc": r.get("TOTAL PUT/CALL RATIO"), "equitypc": r.get("EQUITY PUT/CALL RATIO"),
                                     "indexpc": r.get("INDEX PUT/CALL RATIO")}
    new = pd.DataFrame(rec).T
    pc = pd.concat([arch[arch.index < new.index.min()], new]).sort_index()
    return pc[~pc.index.duplicated(keep="last")].astype(float)


def breadth_daily():
    sys.path.insert(0, str(R2))
    import fetch_data as FD
    from build import STOCKS as NONTECH
    cols = {}
    for base, syms in ((R1 / "data", FD.STOCKS), (R2 / "data", NONTECH)):
        BP.DATA = base
        for s in syms:
            if (base / "yahoo" / f"{s}.json").exists():
                cols[s] = BP.load_yahoo(s).adjclose
    px = pd.DataFrame(cols).sort_index()
    sma = px.rolling(200, min_periods=200).mean()
    above = (px > sma).astype(float).where(sma.notna())
    n = above.notna().sum(axis=1)
    return (above.sum(axis=1) / n.replace(0, np.nan)).where(n >= 30)


def build(cutoff=None):
    cut = pd.Timestamp(cutoff) if cutoff is not None else None

    def trunc(s):
        return s[s.index <= cut] if cut is not None else s

    BP.DATA = R2 / "data"
    spd = trunc(BP.load_yahoo("GSPC_long"))
    close, low = spd.close, spd.low
    last_day = close.index[-1]
    wk = close.resample("W-FRI").last().dropna()
    idx = wk.index
    day_of = close.index.to_series().resample("W-FRI").last().reindex(idx)
    f = pd.DataFrame(index=idx)
    lr = np.log(close).diff()

    # V: volatility baseline
    f["V_VIX"] = asof(trunc(ycol(R1 / "data", "^VIX")), idx)
    f["V_RV20"] = asof(lr.rolling(20).std() * np.sqrt(252), idx)
    f["V_RV126"] = asof(lr.rolling(126).std() * np.sqrt(252), idx)

    # M: slow macro (reuses round 2's weekly known-at table; values there are as-of lookups, see r2_verify W2)
    mw = pd.read_csv(R2 / "out" / "sp_macro_weekly.csv", parse_dates=["week"], index_col="week")
    mw = mw[mw.index <= cut] if cut is not None else mw
    for c in ("FF_HIKE", "Y10_UP", "CURVE_FLAT", "USD_UP", "M2_SLOW", "MARGIN_FROTH", "LIQ_DRAIN", "TIPS_UP",
              "CREDIT_WIDEN", "MARGIN_CREDIT"):
        f["M_" + c] = mw[c].reindex(idx)
    macro_m = pd.read_csv(R1 / "out" / "macro_monthly.csv", parse_dates=["month"], index_col="month").cpi_yoy
    f["M_CPI_YOY"] = asof(trunc(macro_m.dropna()), idx)          # month index = month the print became known
    nf = pd.read_csv(DATA / "nfci.csv")
    nf["d"] = pd.to_datetime(nf.Friday_of_Week, format="%m/%d/%Y")
    nf = nf.set_index("d")
    for c, name in (("NFCI", "NFCI"), ("Risk", "NFCI_RISK"), ("Credit", "NFCI_CREDIT"), ("Leverage", "NFCI_LEV")):
        s = trunc(nf[c].astype(float))
        f["M_" + name] = asof(s, idx, 7)                         # published the following week
    f["M_NFCI_CHG13"] = f.M_NFCI - f.M_NFCI.shift(13)

    # O: options / flow / volatility structure
    vix = trunc(ycol(R1 / "data", "^VIX"))
    vix3m = trunc(ycol(R2 / "data", "VIX3M"))
    vix9d = trunc(ycol(DATA, "VIX9D"))
    f["O_VIX_TERM"] = asof(vix / vix3m, idx)
    f["O_VIX9D_RATIO"] = asof(vix9d / vix, idx)
    f["O_VVIX"] = asof(trunc(ycol(DATA, "VVIX")), idx)
    f["O_SKEW"] = asof(trunc(ycol(DATA, "SKEW")), idx)
    f["O_VRP"] = f.V_VIX - 100 * f.V_RV20
    pc = trunc(cboe_pc()).rolling(10, min_periods=8).mean()
    for c in ("totalpc", "equitypc", "indexpc"):
        f["O_PC_" + c.replace("pc", "").upper()] = asof(pc[c], idx)
    dix = pd.read_csv(R1 / "data" / "DIX.csv", parse_dates=["date"]).set_index("date")
    dix = trunc(dix)
    f["O_GEX"] = asof(dix.gex.rolling(5).mean() / 1e9, idx)
    f["O_DIX"] = asof(dix.dix.rolling(5).mean(), idx)

    # R: momentum and RSI
    f["R_RSI_D"] = asof(rsi(close), idx)
    f["R_RSI_W"] = rsi(wk).reindex(idx)
    mclose = close.resample("ME").last()
    rm = []
    for t, c in wk.items():
        m = mclose[mclose.index < t.to_period("M").to_timestamp()]          # completed months before this one
        s = pd.concat([m.iloc[-60:], pd.Series([c], index=[t])])
        rm.append(rsi(s).iloc[-1] if len(s) > 15 else np.nan)
    f["R_RSI_M"] = rm
    for n in (4, 13, 26, 52):
        f[f"R_MOM{n}"] = np.log(wk / wk.shift(n))
    f["R_MOM12_1"] = np.log(wk.shift(4) / wk.shift(52))
    ema12, ema26 = wk.ewm(span=12, adjust=False).mean(), wk.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    f["R_MACD_H"] = (macd - macd.ewm(span=9, adjust=False).mean()) / wk
    sma40 = wk.rolling(40).mean()
    f["R_DIST_SMA40"] = wk / sma40 - 1
    br = breadth_daily()
    f["R_BREADTH"] = asof(trunc(br), idx)
    rw = f.R_RSI_W
    hi26 = wk.rolling(26).max()
    f["R_RSI_DIV"] = ((wk >= 0.99 * hi26) & (rw <= rw.shift(1).rolling(26).max() - 10)).astype(float).where(rw.notna())

    # S: stretch
    spch = pd.read_pickle(R2 / "data" / "sp_channels.pkl")
    c156 = spch[spch.W == 156].set_index("week")
    if cut is not None:      # the channel row at t uses bars <= t only (r2_verify W1); drop rows after the cutoff
        c156 = c156[c156.index <= cut]
    f["S_CHAN_Z"] = c156.z.reindex(idx).clip(-3, 3)
    f["S_CHAN_R2"] = c156.r2.reindex(idx)
    f["S_DD52"] = wk / wk.rolling(52).max() - 1
    ac = pd.read_csv(R2 / "out" / "avgcorr.csv", parse_dates=["date"], index_col="date").weekly.dropna()
    f["S_AVGCORR"] = asof(trunc(ac), idx)

    f["ERA_ZC"] = (idx >= ERA_ZC).astype(float)
    f["ERA_0DTE"] = (idx >= ERA_0DTE).astype(float)

    # outcomes (use only days after the Friday's last trading day)
    lows = low.where(low > 0, close)
    dates = close.index.to_numpy("datetime64[ns]")
    lv, cv = lows.to_numpy(float), close.to_numpy(float)
    out = {"Y_CORR": [], "Y_BEAR": []}
    for d in day_of.to_numpy("datetime64[ns]"):
        i = np.searchsorted(dates, d)
        c0 = cv[i]
        for name, days, thr in (("Y_CORR", 91, -0.10), ("Y_BEAR", 364, -0.20)):
            j = np.searchsorted(dates, d + np.timedelta64(days, "D"), side="right")
            seg = lv[i + 1:j]
            hit = len(seg) and (seg.min() / c0 - 1) <= thr
            resolved = hit or (d + np.timedelta64(days, "D") <= np.datetime64(last_day))
            out[name].append(float(hit) if resolved else np.nan)
    f["Y_CORR"], f["Y_BEAR"] = out["Y_CORR"], out["Y_BEAR"]
    hit = c156.t_rev.reindex(idx) <= 26
    res = hit | (c156.n_fwd.reindex(idx) >= 26)
    f["Y_CHAN"] = np.where(res & c156.valid.reindex(idx).fillna(False), hit.astype(float), np.nan)
    f["last_day"] = day_of
    f["partial"] = idx > last_day
    return f


LAYERS = {
    "V": lambda c: c.startswith("V_"),
    "M": lambda c: c.startswith("M_"),
    "O": lambda c: c.startswith("O_"),
    "R": lambda c: c.startswith("R_"),
    "S": lambda c: c.startswith("S_"),
}
RAW_SCALED = {"R_RSI_D", "R_RSI_W", "R_RSI_M", "S_CHAN_Z", "S_CHAN_R2", "S_DD52", "R_RSI_DIV", "ERA_ZC", "ERA_0DTE"}


def transform(f, win=260, minp=104):
    """Model inputs: trailing-percentile (centred) for most features; natural scale for bounded ones."""
    sys.path.insert(0, str(R1))
    import tests as T
    X = pd.DataFrame(index=f.index)
    for c in f.columns:
        if not (c[:2] in ("V_", "M_", "O_", "R_", "S_") or c.startswith("ERA_")):
            continue
        if c in RAW_SCALED:
            v = f[c]
            if c.startswith("R_RSI_") and c != "R_RSI_DIV":
                v = (v - 50) / 50
            X[c] = v
        else:
            X[c] = T.trailing_pct(f[c], win, minp) - 0.5
    return X


if __name__ == "__main__":
    f = build()
    f.to_pickle(DATA / "features_raw.pkl")
    X = transform(f)
    X.to_pickle(DATA / "features_X.pkl")
    cov = pd.DataFrame({"first": X.apply(lambda s: s.first_valid_index()), "n": X.notna().sum()})
    cov.to_csv(OUT / "feature_coverage.csv")
    print(f.index[0].date(), "->", f.index[-1].date(), "| features", X.shape[1])
    print(cov.sort_values("first").to_string())
    for y in ("Y_CORR", "Y_BEAR", "Y_CHAN"):
        s = f.loc["1992":, y]
        print(y, "resolved weeks", int(s.notna().sum()))
