"""Pass 3 (protocol in README): correction onset from near-high weeks, 2011-2026."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd

H = Path(__file__).resolve().parent; D = H / "data"
def y(k): s = pd.read_csv(D / f"Y_{k}.csv", index_col=0, parse_dates=True).iloc[:, 0]; return s[~s.index.duplicated()].sort_index()
def f(k): s = pd.read_csv(D / f"F_{k}.csv", index_col=0, parse_dates=True).iloc[:, 0]; return s[~s.index.duplicated()].sort_index()
NAMES = {"F1": "Stretch above the 200-day average", "F2": "Rally speed, 13 weeks", "F3": "10-year yield, 8-week change (bp)",
         "F4": "Stock–bond correlation, 63 days", "F5": "VIX level", "F6": "VIX 20-day change", "F7": "VVIX", "F8": "SKEW index",
         "F9": "Credit lag (HYG − SPY, 8 weeks)", "F10": "Breadth (RSP/SPY, 13-week change)", "F11": "Dealer gamma (GEX) percentile",
         "F12": "GEX percentile, 4-week change", "F13": "DIX, 5-day average", "F14": "Dollar, 8-week change", "F15": "Gold–S&P correlation, 63 days",
         "F16": "Excess earnings yield"}
HINDSIGHT = {"F3", "F15"}

def build():
    P = y("SPX"); idx = P.index; al = lambda s: s.reindex(idx, method="ffill")
    lr = np.log(P).diff(); sd = lr.rolling(63).std()
    t10 = al(f("DGS10")); yd = t10 / 100; dur = (1 - (1 + yd / 2) ** -20) / yd; br = -dur.shift(1) * yd.diff() + yd.shift(1) / 252
    dix = pd.read_csv(D / "DIX.csv", parse_dates=["date"]).set_index("date"); gex = al(dix.gex); dixv = al(dix.dix)
    gpct = gex.rolling(252, min_periods=120).apply(lambda w: (w[:-1] < w[-1]).mean() if len(w) > 1 else np.nan, raw=True)
    core = f("CPILFESL"); core.index = core.index + pd.offsets.MonthEnd(0) + pd.offsets.MonthEnd(1); core_yy = 100 * f("CPILFESL").pct_change(12)
    core_yy.index = core_yy.index + pd.offsets.MonthEnd(0) + pd.offsets.MonthEnd(1)
    cape = pd.read_csv(D / "cape_multpl.csv", index_col=0, parse_dates=True).iloc[:, 0]; cape = cape[cape.index.day == 1]
    cape.index = cape.index + pd.offsets.MonthEnd(0) + pd.offsets.MonthEnd(1)
    spy, rsp, hyg = al(y("SPY")), al(y("RSP")), al(y("HYG")); vix = al(f("VIXCLS"))
    F = pd.DataFrame({
        "F1": np.log(P / P.rolling(200).mean()) / sd,
        "F2": np.log(P / P.shift(65)) / (sd * np.sqrt(65)),
        "F3": 100 * (t10 - t10.shift(40)),
        "F4": lr.rolling(63).corr(br),
        "F5": vix, "F6": np.log(vix / vix.shift(20)), "F7": al(y("VVIX")), "F8": al(y("SKEW")),
        "F9": np.log(hyg / hyg.shift(40)) - np.log(spy / spy.shift(40)),
        "F10": np.log(rsp / spy) - np.log(rsp / spy).shift(65),
        "F11": gpct, "F12": gpct - gpct.shift(20), "F13": dixv.rolling(5).mean(),
        "F14": np.log(al(y("DXY")) / al(y("DXY")).shift(40)),
        "F15": lr.rolling(63).corr(np.log(al(y("GOLDF"))).diff()),
        "F16": 100 / al(cape) - (t10 - al(core_yy)),
    }, index=idx)
    last = P.groupby(P.index.to_period("W-FRI")).apply(lambda s: s.index[-1])
    W = F.loc[last.values].copy(); W.index = pd.DatetimeIndex(last.values)
    pos = idx.get_indexer(W.index); arr = P.values
    hi252 = P.rolling(252, min_periods=200).max()
    W["near_high"] = (P.loc[W.index] >= 0.97 * hi252.loc[W.index]).values
    W["price"] = P.loc[W.index].values
    def lab(i, n, thr):   # outcome known if the window is complete, or if the fall has already happened inside a partial window
        if i + n < len(arr): return float(arr[i + 1:i + n + 1].min() / arr[i] - 1 <= thr)
        if i + 1 < len(arr) and arr[i + 1:].min() / arr[i] - 1 <= thr: return 1.0
        return np.nan
    C10 = [lab(i, 65, -0.10) for i in pos]; C7 = [lab(i, 40, -0.07) for i in pos]
    W["C10"] = pd.array(C10, dtype="float"); W["C7"] = pd.array(C7, dtype="float")
    return W.loc["2011-11-01":]

def auc(x, c):
    x = np.asarray(x); c = np.asarray(c).astype(bool); r = pd.Series(x).rank().values
    n1 = c.sum(); n0 = (~c).sum()
    return (r[c].sum() - n1 * (n1 + 1) / 2) / (n1 * n0) if n1 and n0 else np.nan

def episodes(Wn, tg, gap=8):
    ev = Wn.index[Wn[tg] == 1]
    if len(ev) == 0: return []
    groups, cur = [], [ev[0]]
    for d in ev[1:]:
        if (d - cur[-1]).days > gap * 7: groups.append(cur); cur = [d]
        else: cur.append(d)
    groups.append(cur); return groups

def lens1(W, n_shift=1000, seed=3):
    rng = np.random.default_rng(seed); rows = []
    for tg in ("C10", "C7"):
        full = W[tg].values; n = len(full); valid = ~np.isnan(full)
        nh = W.near_high.values & valid
        Wn = W[nh]; eps = episodes(Wn, tg)
        shifts = rng.integers(26, n - 26, size=n_shift)
        for fe in NAMES:
            x = W[fe].values; m = nh & ~np.isnan(x)
            a = auc(x[m], full[m])
            null = []
            for k in shifts:
                cs = np.roll(np.where(valid, full, np.nan), k); mm = m & ~np.isnan(cs)
                null.append(auc(x[mm], cs[mm]))
            null = np.array(null); p = (1 + np.sum(np.abs(null - 0.5) >= abs(a - 0.5))) / (1 + n_shift)
            agree = 0; tot = 0
            for g in eps:
                e = W.loc[g, fe].mean()
                lo, hi = g[0] - pd.Timedelta(weeks=52), g[-1] + pd.Timedelta(weeks=52)
                ctrl = Wn[(Wn.index >= lo) & (Wn.index <= hi) & (Wn[tg] == 0)][fe].mean()
                if pd.notna(e) and pd.notna(ctrl):
                    tot += 1; agree += int(np.sign(e - ctrl) == np.sign(a - 0.5))
            rows.append({"target": tg, "var": fe, "name": NAMES[fe], "auc": a, "p": p, "n_weeks": int(m.sum()), "n_event_weeks": int(np.nansum(full[m])),
                         "episodes_agree": f"{agree}/{tot}", "hindsight": fe in HINDSIGHT})
    R = pd.DataFrame(rows).sort_values("p").reset_index(drop=True); M = len(R)
    R["bh_ok"] = False; k = [i for i in range(M) if R.p.iloc[i] <= 0.10 * (i + 1) / M]
    if k: R.loc[:max(k), "bh_ok"] = True
    return R

if __name__ == "__main__":
    W = build(); W.to_csv(H / "out" / "weekly.csv")
    for tg in ("C10", "C7"):
        nh = W[W.near_high & W[tg].notna()]; eps = episodes(nh, tg)
        print(f"{tg}: near-high weeks {len(nh)}, event weeks {int(nh[tg].sum())} (base rate {nh[tg].mean():.1%}), episodes {len(eps)}:",
              [f"{g[0].date()}→{g[-1].date()} ({len(g)}w)" for g in eps])
    R = lens1(W); R.to_csv(H / "out" / "lens1.csv", index=False)
    pd.set_option("display.width", 200)
    print(R[["target", "name", "auc", "p", "bh_ok", "episodes_agree", "hindsight", "n_weeks", "n_event_weeks"]].round(3).to_string(index=False))


# ---------------- lens 2 and lens 3 ----------------
from sklearn.linear_model import LogisticRegression
def fit_predict(Xtr, ytr, Xte):
    mu, sd = Xtr.mean(), Xtr.std().replace(0, 1)
    m = LogisticRegression(C=0.5, max_iter=2000).fit((Xtr - mu) / sd, ytr)
    return m.predict_proba((Xte - mu) / sd)[:, 1], m.predict_proba((Xtr - mu) / sd)[:, 1]

def choose(Wtr, tg, passed):
    if passed: return passed
    a = {fe: abs(auc(Wtr[fe].values, Wtr[tg].values) - 0.5) for fe in NAMES if Wtr[fe].notna().mean() > 0.9}
    return sorted(a, key=a.get, reverse=True)[:4]

def lens2(W, tg, passed, scheme, y_override=None):
    Wn = W[W.near_high].copy()
    if y_override is not None: Wn[tg] = y_override
    Wn = Wn[Wn[tg].notna()]
    years = sorted(set(Wn.index.year)); test_years = [yr for yr in years if (scheme == "loyo") or yr >= 2015]
    P, Y, I, TH, CH = [], [], [], [], []
    for yr in test_years:
        a, b = pd.Timestamp(f"{yr}-01-01"), pd.Timestamp(f"{yr + 1}-01-01")
        te = (Wn.index >= a) & (Wn.index < b)
        if scheme == "loyo": tr = (Wn.index < a - pd.Timedelta(weeks=13)) | (Wn.index >= b + pd.Timedelta(weeks=13))
        else: tr = Wn.index < a - pd.Timedelta(weeks=13)
        Wtr = Wn[tr]
        if te.sum() == 0 or Wtr[tg].sum() < 3: continue
        cols = choose(Wtr, tg, passed)
        Xtr = Wtr[cols].fillna(Wtr[cols].median()); Xte = Wn.loc[te, cols].fillna(Wtr[cols].median())
        p, ptr = fit_predict(Xtr, Wtr[tg], Xte)
        P.append(p); Y.append(Wn.loc[te, tg].values); I.append(Wn.index[te]); TH.append(np.full(te.sum(), np.quantile(ptr, 0.80))); CH.append([",".join(cols)] * te.sum())
    p, yv = np.concatenate(P), np.concatenate(Y)
    base = np.concatenate([np.full(len(y_), np.nan) for y_ in Y])
    # base rate from the training side of each fold is approximately the full-sample rate here; use expanding/other-years rate
    br = Wn[tg].mean(); bs = 1 - np.mean((p - yv) ** 2) / np.mean((br - yv) ** 2)
    return {"auc": float(auc(p, yv)), "brier_skill": float(bs), "n": int(len(yv)), "events": int(yv.sum())}, pd.DataFrame(
        {"date": np.concatenate(I), "p": p, "y": yv, "thr": np.concatenate(TH), "vars": np.concatenate(CH)})

def lens2_null(W, tg, passed, scheme, n=200, seed=5):
    rng = np.random.default_rng(seed); full = W[tg].values; nn = len(full); out = []
    nh = W.near_high.values
    for k in rng.integers(26, nn - 26, size=n):
        ys = np.roll(full, k)[nh]
        r, _ = lens2(W, tg, passed, scheme, y_override=ys); out.append(r["auc"])
    return np.array(out)
