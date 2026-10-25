"""Pre-top profiles of the channel's corrections (README.md, method fixed at 534277a).
Usage: python dossier.py <etfs folder> <long folder>  -> out/profile.csv, out/dossier.json, out/daily.csv"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
AG = HERE.parent
MICRO = AG.parent / "microstructure" / "out"
CH0, CH1 = pd.Timestamp("2022-10-13"), pd.Timestamp("2026-10-23")
MAJOR = ["2023-07-31", "2025-02-19", "2026-01-27"]
MINOR = ["2024-03-28", "2024-07-16", "2025-10-28"]
PANEL = ["AAPL", "MSFT", "AMZN", "GOOGL", "META", "NVDA", "ADBE", "AMAT", "AMD", "BA", "CAT", "COST", "CSCO", "DIS", "GE", "IBM", "INTC", "JNJ",
         "JPM", "KO", "LLY", "MCD", "MMM", "MRK", "MU", "ORCL", "PEP", "PFE", "PG", "QCOM", "T", "TXN", "UNH", "WMT", "XOM", "HD", "CVX",
         "BAC", "C", "WFC", "VZ"]
GROUPS = {
    "leadership / rotation": ["semis vs SPY (20d)", "AAPL stock-specific (20d)", "AAPL-S&P correlation (20d)", "equal weight vs SPY (20d)",
                              "small caps vs SPY (20d)", "defensives vs SPY (20d)"],
    "breadth": ["share of panel above 50-day", "avg pairwise correlation"],
    "dealers / flows": ["GEX percentile", "DIX percentile", "SPY dealer gamma percentile"],
    "volatility structure": ["VIX percentile", "VIX / VIX3M", "VVIX percentile", "SKEW percentile", "spot-vol correlation (20d)"],
    "cross-asset": ["bonds TLT (20d)", "dollar UUP (20d)", "bitcoin (20d)", "gold (20d)", "credit HYG vs IEF (20d)", "banks KRE vs SPY (20d)"],
    "stretch": ["S&P vs 50-day average", "S&P return (20d)"]}


def close(folder, name):
    d = json.loads((Path(folder) / f"{name}.json").read_text())["chart"]["result"][0]
    idx = pd.to_datetime(d["timestamp"], unit="s", utc=True).tz_convert("America/New_York").normalize().tz_localize(None)
    s = pd.Series(d["indicators"]["quote"][0]["close"], index=idx, dtype=float).dropna()
    s = s[~s.index.duplicated(keep="last")].sort_index()
    return s[s > 0]


def pct(s, n=252):
    return s.rolling(n, min_periods=120).apply(lambda w: (w[:-1] < w[-1]).mean(), raw=True)


def build(etfs, long):
    spx = close(etfs, "%5EGSPC")
    spx = spx[spx.index >= "2020-06-01"]
    idx = spx.index
    c = lambda n, f=etfs: close(f, n).reindex(idx).ffill()
    lr = lambda s, n=20: np.log(s).diff(n)
    rs = np.log(spx).diff()
    spy, smh = c("SPY"), c("SMH")
    aapl = c("AAPL")
    ra = np.log(aapl).diff()
    rm = (rs - 0.065 * ra.fillna(0)) / (1 - 0.065)
    beta = (ra.rolling(252, min_periods=200).cov(rm) / rm.rolling(252, min_periods=200).var()).shift(1)
    I = pd.DataFrame(index=idx)
    I["semis vs SPY (20d)"] = lr(smh / spy)
    I["AAPL stock-specific (20d)"] = (ra - beta * rm).rolling(20).sum()
    I["AAPL-S&P correlation (20d)"] = ra.rolling(20).corr(rm)
    I["equal weight vs SPY (20d)"] = lr(c("RSP") / spy)
    I["small caps vs SPY (20d)"] = lr(c("IWM") / spy)
    I["defensives vs SPY (20d)"] = lr(c("XLP") / spy)
    P = pd.DataFrame({s: close(long, s).reindex(idx).ffill() for s in PANEL})
    I["share of panel above 50-day"] = (P > P.rolling(50).mean()).mean(axis=1)
    dd = pd.read_csv(AG / "2026-10-25-aapl-decoupling" / "out" / "daily.csv", index_col=0, parse_dates=True)
    I["avg pairwise correlation"] = dd["avg pairwise corr"].reindex(idx)
    dix = pd.read_csv(Path(etfs) / "DIX.csv", parse_dates=["date"]).set_index("date")
    dix = dix[~dix.index.duplicated()].reindex(idx)
    I["GEX percentile"] = pct(dix.gex)
    I["DIX percentile"] = pct(dix.dix)
    g = pd.read_csv(MICRO / "td_gamma_SPY.csv", parse_dates=["date"]).set_index("date").gex_classic
    I["SPY dealer gamma percentile"] = pct(g).reindex(idx)
    vix, vix3m = c("%5EVIX"), c("%5EVIX3M")
    I["VIX percentile"] = pct(vix)
    I["VIX / VIX3M"] = vix / vix3m
    I["VVIX percentile"] = pct(c("%5EVVIX"))
    I["SKEW percentile"] = pct(c("%5ESKEW"))
    I["spot-vol correlation (20d)"] = vix.diff().rolling(20).corr(rs)
    I["bonds TLT (20d)"] = lr(c("TLT"))
    I["dollar UUP (20d)"] = lr(c("UUP"))
    I["bitcoin (20d)"] = lr(c("BTC-USD"))
    I["gold (20d)"] = lr(c("GLD"))
    I["credit HYG vs IEF (20d)"] = lr(c("HYG") / c("IEF"))
    I["banks KRE vs SPY (20d)"] = lr(c("KRE") / spy)
    I["S&P vs 50-day average"] = spx / spx.rolling(50).mean() - 1
    I["S&P return (20d)"] = lr(spx)
    dist = spx / spx.rolling(252, min_periods=60).max() - 1
    return I, spx, dist


def main(etfs, long):
    OUT.mkdir(exist_ok=True)
    I, spx, dist = build(etfs, long)
    idx = I.index
    ch = (idx >= CH0) & (idx <= CH1)
    ref = ch & (dist >= -0.03).to_numpy()
    mu, sd = I[ref].mean(), I[ref].std()
    m10 = I.rolling(10, min_periods=7).mean()
    Z = (m10 - mu) / sd
    events = MAJOR + MINOR
    prof = pd.DataFrame({e: Z.loc[pd.Timestamp(e)] for e in events})
    prof["today (Oct 12-23)"] = Z.iloc[-1]
    hi = spx[idx >= "2026-08-01"].idxmax()
    prof[f"recent high ({hi.date()})"] = Z.loc[hi]
    rows = []
    for k in I.columns:
        v = prof.loc[k, events].to_numpy()
        maj = v[:3]
        sgn = 0
        for sg in (1, -1):
            if np.all(sg * maj >= 0.5) and np.sum(sg * v >= 0.5) >= 5:
                sgn = sg
        rows.append({"indicator": k, "group": next(gname for gname, ks in GROUPS.items() if k in ks), "lines up": sgn,
                     "majors same sign |z|>=0.5": int(max(np.sum(maj >= 0.5), np.sum(maj <= -0.5))),
                     "events same sign |z|>=0.5": int(max(np.sum(v >= 0.5), np.sum(v <= -0.5))),
                     "mean z (6 events)": float(np.nanmean(v)), "today z": float(prof.loc[k, "today (Oct 12-23)"]),
                     "normal near-high mean": float(mu[k]), "today raw (10d mean)": float(m10[k].iloc[-1])})
    R = pd.DataFrame(rows)
    up = R[R["lines up"] != 0].indicator.tolist()
    res = {"lined up": {r.indicator: {"direction": "high" if r["lines up"] > 0 else "low", "mean z": r["mean z (6 events)"], "today z": r["today z"]}
                        for _, r in R[R["lines up"] != 0].iterrows()},
           "near misses (3 of 3 majors, 4 of 6)": R[(R["majors same sign |z|>=0.5"] == 3) & (R["events same sign |z|>=0.5"] == 4)].indicator.tolist(),
           "recent high": str(hi.date()), "S&P distance to 252d high today %": float(100 * dist.iloc[-1])}
    if up:
        tmpl = prof.loc[up, events].mean(axis=1).to_numpy()
        Zu = Z[up]
        sim = (Zu.to_numpy() @ tmpl) / (np.linalg.norm(Zu.to_numpy(), axis=1) * np.linalg.norm(tmpl))
        sim = pd.Series(sim, index=idx)
        base = sim[ref].dropna()
        res["similarity today"] = float(sim.iloc[-1])
        res["similarity today, percentile among channel near-high days"] = float((base < sim.iloc[-1]).mean())
        res["share of channel near-high days with similarity >= today"] = float((base >= sim.iloc[-1]).mean())
        top_days = [pd.Timestamp(e) for e in events]
        res["similarity at each event"] = {e: float(sim.loc[pd.Timestamp(e)]) for e in events}
        I["similarity"] = sim
    prof.round(3).to_csv(OUT / "profile.csv")
    R.round(4).to_csv(OUT / "lineup.csv", index=False)
    I.assign(dist=dist).to_csv(OUT / "daily.csv")
    (OUT / "dossier.json").write_text(json.dumps(res, indent=1, default=float))
    return prof, R, res


if __name__ == "__main__":
    prof, R, res = main(*sys.argv[1:3])
    pd.set_option("display.width", 250)
    print(prof.round(2).to_string())
    print(R[["indicator", "lines up", "majors same sign |z|>=0.5", "events same sign |z|>=0.5", "mean z (6 events)", "today z"]].round(2).to_string())
    print(json.dumps(res, indent=1, default=float))
