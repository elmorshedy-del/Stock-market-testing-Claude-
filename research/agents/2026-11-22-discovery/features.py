"""Stage 2 + 4 of DISCOVERY.md: point-in-time weekly panel, the systematic feature library, and the targets."""
from pathlib import Path
import numpy as np, pandas as pd

H = Path(__file__).resolve().parent; D = H / "data"
LOCK = pd.Timestamp("2020-01-01")
def y(k): s = pd.read_csv(D / f"Y_{k}.csv", index_col=0, parse_dates=True).iloc[:, 0]; return s[~s.index.duplicated()].sort_index()
def f(k): s = pd.read_csv(D / f"F_{k}.csv", index_col=0, parse_dates=True).iloc[:, 0]; return s[~s.index.duplicated()].sort_index()
def monthly_lagged(s, lag=1):
    s = s.copy(); s.index = s.index + pd.offsets.MonthEnd(0) + pd.offsets.MonthEnd(lag); return s   # usable from the end of the following month

def base_weekly():
    wk = lambda s: s.resample("W-FRI").last()
    spx_d = y("SPX")
    core = f("CPILFESL"); core_yy = 100 * core.pct_change(12)
    cape = pd.read_csv(D / "cape_multpl.csv", index_col=0, parse_dates=True).iloc[:, 0]; cape = cape[cape.index.day == 1]
    B = pd.DataFrame({
        "SPX": wk(spx_d), "VIX": wk(f("VIXCLS")), "US10Y": wk(f("DGS10")), "US2Y": wk(f("DGS2")), "US3M": wk(f("DGS3MO")),
        "CREDIT": wk(f("BAA10Y")), "DXY": wk(y("DXY")), "USDJPY": wk(f("DEXJPUS")), "OIL": wk(f("DCOILWTICO")).clip(lower=1),
        "GOLD": wk(y("GOLDF")), "NIKKEI": wk(y("NIKKEI")),
        "NFCI": wk(f("NFCI")).shift(1), "NFCI_LEV": wk(f("NFCILEVERAGE")).shift(1), "NFCI_CRED": wk(f("NFCICREDIT")).shift(1), "NFCI_RISK": wk(f("NFCIRISK")).shift(1),
    })
    B["CURVE"] = B.US10Y - B.US3M
    B["CORE_YY"] = monthly_lagged(core_yy).reindex(B.index, method="ffill")
    B["REAL10"] = B.US10Y - B.CORE_YY
    B["CAPE"] = monthly_lagged(cape).reindex(B.index, method="ffill")
    B["EXCESS_EY"] = 100 / B.CAPE - B.REAL10
    return B.loc["1965-01-01":], spx_d

PRICE = ["SPX", "DXY", "USDJPY", "OIL", "GOLD", "NIKKEI"]
LEVEL = ["VIX", "US10Y", "US2Y", "CURVE", "CREDIT", "NFCI", "NFCI_LEV", "NFCI_CRED", "NFCI_RISK", "REAL10", "CAPE", "EXCESS_EY"]
HS = [1, 4, 13, 52]

def bond_ret(yld):
    yd = yld / 100; dur = (1 - (1 + yd / 2) ** -20) / yd
    return -dur.shift(1) * yd.diff() + yd.shift(1) / 52

def build():
    B, spx_d = base_weekly(); F = {}
    for k in PRICE + LEVEL:
        x = np.log(B[k]) if k in PRICE else B[k]
        d1 = x.diff(); sd = d1.rolling(156, min_periods=104).std()
        for h in HS:
            ch = x.diff(h); F[f"{k}|chg{h}w"] = ch; F[f"{k}|speed{h}w"] = ch / (sd * np.sqrt(h))
        F[f"{k}|accel4w"] = x.diff(4) - x.diff(4).shift(4)
        F[f"{k}|z3y"] = (x - x.rolling(156, min_periods=104).mean()) / x.rolling(156, min_periods=104).std()
        if k in LEVEL: F[f"{k}|level"] = x
        if k in PRICE: F[f"{k}|from52wHigh"] = x - x.rolling(52, min_periods=40).max()
    # co-movement with the S&P
    R = pd.DataFrame({"SPX": np.log(B.SPX).diff(), "BONDS": bond_ret(B.US10Y), "GOLD": np.log(B.GOLD).diff(), "DXY": np.log(B.DXY).diff(),
                      "YEN": -np.log(B.USDJPY).diff(), "OIL": np.log(B.OIL).diff(), "CREDIT": -B.CREDIT.diff(), "NIKKEI": np.log(B.NIKKEI).diff()})
    for k in R.columns.drop("SPX"):
        for w in (13, 52):
            F[f"corr(SPX,{k})|{w}w"] = R.SPX.rolling(w, min_periods=int(0.8 * w)).corr(R[k])
        F[f"corr(SPX,{k})|52w chg13w"] = F[f"corr(SPX,{k})|52w"].diff(13)
    # system: share of cross-asset variance in one common factor (absorption ratio), 52-week window, 7 assets available since 1986
    A = R[["SPX", "BONDS", "DXY", "YEN", "OIL", "CREDIT", "NIKKEI"]]
    ar = pd.Series(np.nan, index=A.index)
    for i in range(52, len(A)):
        w = A.iloc[i - 52:i].dropna()
        if len(w) >= 45:
            ev = np.linalg.eigvalsh(np.corrcoef(w.values.T)); ar.iloc[i - 1] = ev[-1] / ev.sum()
    F["absorption|52w"] = ar; F["absorption|chg13w"] = ar.diff(13)
    # S&P realized volatility from daily data, sampled at the Friday close
    lr = np.log(spx_d).diff()
    for n in (20, 63, 252):
        F[f"SPXvol|{n}d"] = (lr.rolling(n).std() * np.sqrt(252)).resample("W-FRI").last()
    F["SPXvol|ratio20/252"] = F["SPXvol|20d"] / F["SPXvol|252d"]
    F["VIX-minus-realized20d"] = B.VIX / 100 - F["SPXvol|20d"]
    X = pd.DataFrame(F).loc["1970-01-01":]
    # targets from daily closes, anchored at each Friday close
    px = spx_d; fr = px.resample("W-FRI").last(); idx = fr.index
    pos = px.index.get_indexer(px.resample("W-FRI").apply(lambda s: s.index[-1] if len(s) else pd.NaT).dropna())
    T = pd.DataFrame(index=idx)
    last_day = px.resample("W-FRI").apply(lambda s: s.index[-1] if len(s) else pd.NaT)
    rows = {}
    arr = px.values; lra = np.diff(np.log(arr), prepend=np.nan)
    for wkend, d in last_day.dropna().items():
        i = px.index.get_loc(d)
        r = {}
        if i + 20 < len(arr):
            r["vol4"] = np.log(np.std(lra[i + 1:i + 21], ddof=1) * np.sqrt(252)); r["ret4"] = np.log(arr[i + 20] / arr[i]); r["end4"] = px.index[i + 20]
        if i + 65 < len(arr):
            r["mdd13"] = arr[i + 1:i + 66].min() / arr[i] - 1; r["ret13"] = np.log(arr[i + 65] / arr[i]); r["end13"] = px.index[i + 65]
        r["bench_vol4"] = np.log(np.std(lra[i - 19:i + 1], ddof=1) * np.sqrt(252)) if i >= 20 else np.nan
        rows[wkend] = r
    T = pd.DataFrame(rows).T; T.index = pd.to_datetime(T.index)
    for c in ["vol4", "ret4", "mdd13", "ret13", "bench_vol4"]: T[c] = T[c].astype(float)
    T["crash13"] = (T.mdd13 <= -0.10).astype(float).where(T.mdd13.notna())
    return X, T, B

if __name__ == "__main__":
    X, T, B = build()
    X.to_parquet(H / "data" / "features.parquet"); T.to_parquet(H / "data" / "targets.parquet")
    print("features:", X.shape[1], "| weeks:", X.shape[0], X.index[0].date(), "→", X.index[-1].date())
    disc = X.loc["1990-01-01":"2019-12-31"]
    cov = disc.notna().mean().sort_values()
    print("coverage in 1990-2019 (lowest 8):", cov.head(8).round(2).to_dict())
    print("targets:", T.loc["1990":"2019"].describe().T[["count", "mean", "std"]].round(3).to_string())
    print("crash13 base rate 1990-2019:", round(T.loc["1990":"2019", "crash13"].mean(), 3))
